# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitCache.java

## Purpose
`TestShortCircuitCache` verifies the DFSClient short-circuit read cache and its shared-memory coordination with DataNodes. It covers cache creation, invalid configurations, fetch-or-create reuse, expiry, eviction, time- and shared-memory-based staleness, shared-memory slot allocation/release, DataNode registry cleanup on failure, file descriptor request edge cases, domain socket closure across one or multiple DataNodes, and DataNode restart cleanup.

## Important APIs, Types, And Functions
The tests directly construct `ShortCircuitCache`, `ShortCircuitReplica`, `ShortCircuitReplicaInfo`, `ExtendedBlockId`, `DfsClientShmManager`, `DfsClientShm`, `ShortCircuitShm.Slot`, and `ShortCircuitRegistry`. `TestFileDescriptorPair` creates paired data and metadata files, including a `BlockMetadataHeader` with NULL checksum, and supplies `FileInputStream` pairs to cache replicas. `SimpleReplicaCreator` implements `ShortCircuitCache.ShortCircuitReplicaCreator` for deterministic cache insertions. Cluster tests use `MiniDFSCluster`, `DistributedFileSystem`, `BlockReaderFactory`, `BlockReaderTestUtil`, `DomainSocket`, `DomainPeer`, `TemporarySocketDirectory`, `PeerCache`, `DfsClientConf`, and Mockito fault injection.

The central cache APIs under test are `fetchOrCreate`, `unref`, `accept(CacheVisitor)`, `allocShmSlot`, `scheduleSlotReleaser`, `getDfsClientShmManager().visit`, and DataNode-side `ShortCircuitRegistry.registerSlot`/visitor queries. Failure-injector classes override `BlockReaderFactory.FailureInjector` hooks for request-file-descriptor failure and receipt-verification capability.

## Control Flow
Pure cache tests create local file descriptor pairs, call `fetchOrCreate` with block IDs, assert the same `ShortCircuitReplicaInfo` is reused while referenced or evictable, unref replicas, and then force expiry or eviction by time and capacity. Shared-memory tests create a short-circuit-enabled MiniDFSCluster with a domain socket path, use a domain peer to allocate slots, inspect the client-side shared-memory manager, and verify scheduled release eventually drains the segment and slot counts.

Failure and regression tests drive real short-circuit reads through `DFSTestUtil.readFileBuffer`, inject DataNode or BlockReaderFactory failures, and then assert the DataNode `ShortCircuitRegistry` has the expected segment/slot counts. Domain socket closure tests manually allocate/register slots and release them in different orders to make sure shutdown of one DataNode or one segment does not prematurely close unrelated shared memory. `testDNRestart` restarts the DataNode after slot allocation and ensures stale slots can be released without leaving registry or client manager state behind.

## State And Persistence Behavior
The key state is in-memory but backed by OS resources: file descriptors, domain sockets, memory-mapped/shared-memory segments, short-circuit replica reference counts, evictable maps, failed-load maps, and DataNode registry slot tables. Temporary data/meta files and temporary socket directories are local filesystem state cleaned by each test. MiniDFSCluster files provide real HDFS blocks whose local replicas are exposed through short-circuit reads. Tests explicitly check that invalidated slots are marked stale, registry counts fall to zero after release/failure, and cache eviction keeps only the newest eligible replicas.

## Dependencies And Integration Points
This suite integrates DFSClient short-circuit read code with DataNode xceiver behavior, domain sockets, shared memory, `BlockReaderFactory`, `PeerCache`, `ClientContext`, and DataNode-side `ShortCircuitRegistry`. It depends on native domain socket support and skips via `assumeTrue` when the domain socket library is unavailable. Mockito is used for `ClientContext`, `PeerCache`, `DomainSocket`, `ShortCircuitCache`, and `DataNodeFaultInjector` edge cases.

## Risks And Edge Cases
The tests guard against file descriptor leaks, stale shared-memory slots, incorrect retry behavior on `RetriableException`, NPEs when native file descriptor creation fails because of ulimit/native limitations, and cleanup failures when DataNode short-circuit shared-memory response fails. Timing sleeps and async `GenericTestUtils.waitFor` calls make some checks sensitive to scheduler delays. Some tests disable TCP reads for testing, so failure to perform short-circuit IO must surface as explicit non-TCP-read failures rather than silent fallback.

## Test Signals
Signals include exact cache reuse identity, creator callbacks being or not being invoked, visitor-observed segment/slot counts, valid/invalid slot flags, zero registry and manager counts after cleanup, expected exception text when forced short-circuit reads fail, and Mockito verification of retry/failure paths. Successful reads after clearing a failure injector confirm that the path map and registry recover.
