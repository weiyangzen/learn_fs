# subset-b-007422 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderLocalLegacy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderLocalLegacy.java

## Purpose
`BlockReaderLocalLegacy` is the legacy HDFS short-circuit block reader. When a DFS client runs on the same host as a DataNode, it bypasses the DataNode data-transfer protocol by asking the DataNode for local block and metadata file paths, then reading those files directly through `FileInputStream`. It exists for the older HDFS-2246 path-based short-circuit mechanism and is private to the HDFS client implementation.

## Important APIs, types, and functions
The class implements `BlockReader`, including `read(byte[], int, int)`, `read(ByteBuffer)`, `skip`, `close`, `readAll`, `readFully`, `available`, `isShortCircuit`, `getClientMmap`, `getDataChecksum`, and `getNetworkDistance`. `newBlockReader(...)` is the factory that resolves `BlockLocalPathInfo`, opens the block and metadata streams, chooses checksum or no-checksum mode, and constructs the reader. `LocalDatanodeInfo` stores one `ClientDatanodeProtocol` proxy and an LRU synchronized cache of up to 10,000 `ExtendedBlock -> BlockLocalPathInfo` entries per local DataNode IPC port. `getBlockPathInfo(...)` performs the `ClientDatanodeProtocol#getBlockLocalPathInfo` RPC and skips caching for transient storage. `getSlowReadBufferNumChunks`, `fillBuffer`, `doByteBufferRead`, `fillSlowReadBuffer`, and `writeSlice` implement checksum-aware local reading.

## Control flow
Reader creation first looks up cached path info by block and local DataNode IPC port. On a miss, it obtains the current `UserGroupInformation`, creates or reuses a DataNode RPC proxy, and requests block/meta paths with the block token. It then opens the local block file and, unless checksums are skipped by configuration or transient storage, opens the metadata file and reads the `DataChecksum` from `BlockMetadataHeader`. Construction skips the data and checksum streams to the checksum chunk containing the requested start offset and allocates direct buffers from `DirectBufferPool`.

For checksummed reads, `read(ByteBuffer)` drains any residual slow buffer, reads aligned full chunks directly into the caller buffer, verifies chunk checksums, then falls back to a slow staged read for unaligned tail or initial offset bytes. `read(byte[],...)` always stages through `slowReadBuff` in checksum mode. `skip` advances within buffered data when possible, reads through small gaps to keep data and checksum streams synchronized, and for larger gaps skips both streams to a checksum boundary before reading the intra-chunk remainder. `close` closes streams and returns pooled buffers.

## State and persistence behavior
Instance state tracks data/checksum streams, checksum metadata, the original start offset, block id, filename for diagnostics, checksum chunk sizes, offset within the current chunk, optional skip buffer, and two pooled direct buffers. Static state includes the per-DataNode `localDatanodeInfoMap` and a shared `DirectBufferPool`. Path cache entries are process-local only and are invalidated when opening the cached local path fails. Transient replicas are deliberately not cached because eviction can move the replica path without a client notification channel.

## Dependencies and integration points
This class integrates `DFSClient` block-reader creation with `ClientDatanodeProtocol`, `BlockLocalPathInfo`, `ExtendedBlock`, `BlockTokenIdentifier`, `DfsClientConf.ShortCircuitConf`, `StorageType`, `DataChecksum`, `BlockMetadataHeader`, `DirectBufferPool`, and Hadoop IO utilities. It delegates `readAll` and `readFully` to `BlockReaderUtil`. Its `ClientDatanodeProtocol` proxy is created through `DFSUtilClient.createClientDatanodeProtocolProxy` under the client `UserGroupInformation`.

## Risks and test signals
Correctness depends on maintaining data and checksum stream alignment across unaligned reads and skips. Important tests should cover start offsets inside checksum chunks, reads shorter than a chunk, `ByteBuffer` position/limit restoration, EOF while honoring `offsetFromChunkBoundary`, metadata checksum verification failure, skip across buffered and unbuffered ranges, transient storage cache bypass, cached path invalidation after local file disappearance, and cleanup of pooled buffers on constructor failures. Security and integration tests should cover Kerberos/token-protected `getBlockLocalPathInfo` and the legacy permission requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderLocalLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderRemote.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderRemote.java

## Purpose
`BlockReaderRemote` is the packet-protocol HDFS block reader used when reading from a DataNode over a `Peer` connection. It sends an `OP_READ_BLOCK` request, consumes DataTransferProtocol packets, verifies checksums when requested, and optionally returns the connection to `PeerCache` after a clean read-status response.

## Important APIs, types, and functions
The class implements `BlockReader`. `newBlockReader(...)` sends the read request through `Sender.readBlock`, parses `BlockOpResponseProto`, extracts `ReadOpChecksumInfoProto`, validates the first chunk offset, and creates the reader. `read(byte[],...)` and `read(ByteBuffer)` expose bytes from `curDataSlice`. `readNextPacket()` receives a packet with `PacketReceiver`, validates its `PacketHeader`, verifies chunk checksums, skips prefix bytes before `startOffset`, and when the requested byte count is satisfied reads the trailing empty packet and sends `CHECKSUM_OK` or `SUCCESS`. `sendReadResult` and static `writeReadResult` serialize `ClientReadStatusProto`. `checkSuccess` delegates block operation status validation to `DataTransferProtoUtil`.

## Control flow
Creation wraps the peer output stream in a buffered `DataOutputStream`, sends a read-block operation containing the block, token, client name, start offset, requested length, checksum flag, and caching strategy, then reads the server response from the peer input stream. During reads, if no current data slice remains and more transfer bytes are needed, the reader pulls the next packet. Each packet advances `lastSeqNo`, reduces `bytesNeededToFinish`, verifies checksums against the packet checksum slice and offset, and positions the data slice so callers only see requested bytes. At the logical end of the read, the reader consumes the mandatory zero-length last packet before sending the final status. `skip` advances over already received packet data and reads more packets as needed.

## State and persistence behavior
Persistent state is only connection/session state: the `Peer`, `DatanodeID`, optional `PeerCache`, `PacketReceiver`, current packet data slice, checksum parameters, current sequence number, start offset, remaining bytes to finish, and whether the final status has been sent. `close` closes packet resources, clears checksum/start state, and returns the peer to the cache only if a status code was successfully sent; otherwise it closes the peer to avoid reusing a connection in an uncertain protocol state.

## Dependencies and integration points
It depends on `Peer`, `PeerCache`, DataTransferProtocol classes (`Sender`, `PacketHeader`, `PacketReceiver`, protobuf status/checksum messages), `DataChecksum`, `ExtendedBlock`, block tokens, `CachingStrategy`, and HDFS client remote-buffer configuration. It is consumed by `DFSInputStream` block-reader selection logic and is the remote counterpart to short-circuit readers.

## Risks and test signals
Key risks are packet sequence/header validation, correct handling of padded bytes before `startOffset`, checksum error offset reporting, draining the trailing empty packet, and peer-cache reuse only after a clean final status. Tests should include successful checksum and no-checksum reads, mid-chunk start offsets, packet boundary reads, short skips, malformed packet headers, invalid first chunk offsets, DataNode error responses, send-status failures, and verifying that failed or incomplete reads close rather than cache peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderRemote.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderUtil.java

## Purpose
`BlockReaderUtil` centralizes simple helper behavior shared by local, remote, and external `BlockReader` implementations.

## Important APIs, types, and functions
`readAll(BlockReader, byte[], int, int)` repeatedly calls `BlockReader.read` until it has filled the requested length, sees EOF, or gets a non-positive read result. It returns EOF or the number of bytes actually read. `readFully(BlockReader, byte[], int, int)` loops until the requested length is read and throws `IOException` on premature EOF.

## Control flow
Both helpers use the `BlockReader` byte-array read path. `readAll` preserves partial-read semantics by returning already-read bytes if EOF follows a partial read. `readFully` treats any negative return before satisfying `len` as a hard error.

## State and persistence behavior
The class is stateless and package-private. It does not persist data or modify reader state beyond consuming bytes through the provided reader.

## Dependencies and integration points
It depends only on the `BlockReader` interface and `IOException`. It is called by `BlockReaderLocalLegacy`, `BlockReaderRemote`, and `ExternalBlockReader` to keep `readAll`/`readFully` semantics consistent.

## Risks and test signals
The main test signals are EOF behavior with zero bytes read versus after a partial read, propagation of reader exceptions, and ensuring no infinite loop if an implementation returns `0` while progress is expected. Callers rely on underlying readers to follow Hadoop read semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/CorruptFileBlockIterator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/CorruptFileBlockIterator.java

## Purpose
`CorruptFileBlockIterator` adapts `DFSClient.listCorruptFileBlocks` into a `RemoteIterator<Path>` for `DistributedFileSystem` and `Hdfs` callers.

## Important APIs, types, and functions
The constructor stores the `DFSClient`, converts the requested `Path` to a URI path string, and preloads the first result. `hasNext()` checks whether `nextPath` is populated. `next()` returns the current path and advances the iterator or throws `NoSuchElementException` when exhausted. `getCallsMade()` exposes the number of DFSClient RPC calls for debugging/tests.

## Control flow
`loadNext()` fetches a new `CorruptFileBlocks` batch when no batch exists or the current batch has been consumed. It updates `files`, `cookie`, `fileIdx`, and `callsMade`, then either converts the next string to a `Path` or marks exhaustion with `nextPath = null`. The cookie is passed back to the NameNode for paginated continuation.

## State and persistence behavior
State is in-memory iterator state: current file-name array, index, continuation cookie, next path, and call count. It persists nothing locally.

## Dependencies and integration points
It depends on `DFSClient`, `CorruptFileBlocks`, Hadoop `Path`, and `RemoteIterator`. It is part of the client-side public filesystem listing path for corrupt block reports.

## Risks and test signals
Tests should cover empty first response, multiple batches, cookie continuation, `NoSuchElementException` after exhaustion, path string/URI conversion, and call-count behavior. A risk is that an empty response is interpreted as completion; the NameNode contract must guarantee that no later batch is reachable after an empty file list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/CorruptFileBlockIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/DfsClientConf.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/DfsClientConf.java

## Purpose
`DfsClientConf` is the immutable-ish configuration snapshot used by `DFSClient` and related HDFS client components. It reads Hadoop `Configuration` keys once, normalizes values, validates critical bounds, and exposes typed getters for retry, failover, read, write, checksum, socket, short-circuit, hedged-read, striped-read, dead-node, lease, and pluggable replica-accessor behavior.

## Important APIs, types, and functions
The constructor loads all client settings from `HdfsClientConfigKeys` and common Hadoop keys. `getChecksumOptFromConf`, `getChecksumType`, `getChecksumCombineModeFromConf`, and `createChecksum` build checksum options and validate effective checksum types. `loadWriteByteArrayManagerConf` optionally builds a `ByteArrayManager.Conf`. `loadReplicaAccessorBuilderClasses` loads configured `ReplicaAccessorBuilder` classes with the thread context class loader and logs failed loads. The nested `ShortCircuitConf` captures socket cache, domain socket, legacy block reader, local-read, metrics sampling, buffer/cache sizes, mmap, stale-threshold, shared-memory watcher, domain-socket disable interval, and key-provider cache expiry settings.

## Control flow
Construction reads primitive values, derives some defaults from other values such as `prefetchSize = 10 * defaultBlockSize`, converts duration units where required, validates positive striped read threadpool size, bounds `DFS_CLIENT_SHORT_CIRCUIT_NUM` to 1 through 5, and creates `ShortCircuitConf`. `ShortCircuitConf` normalizes short-circuit metrics sampling: values <= 0 disable metrics, values > 100 clamp to 100, and otherwise enable sampling with the provided percentage. Invalid checksum type or combine mode strings are logged and replaced with defaults.

## State and persistence behavior
All fields are client-process configuration state; no disk persistence happens here. Most fields are final. `ShortCircuitConf` stores final values and reports them with `confAsString`. The class may hold loaded class references for replica accessor builders. Invalid configured classes are skipped after logging, so the resulting list may be partial.

## Dependencies and integration points
It integrates deeply with `DFSClient`, block readers, output streams, hedged and striped readers, socket/peer caches, lease renewal, checksum computation, and external replica accessors. Dependencies include `Configuration`, `Client.getRpcTimeout`, `FsPermission`, `ChecksumOpt`, `ChecksumCombineMode`, `DataChecksum`, `ByteArrayManager`, `ReplicaAccessorBuilder`, and many `HdfsClientConfigKeys`.

## Risks and test signals
Important risks include silent fallback for bad checksum names, class-loading failures reducing external-accessor coverage, configuration bounds that must match documentation, and relative units for lease hard-limit seconds converted to milliseconds. Tests should cover default loading, invalid checksum/combine mode fallback, checksum creation failure, replica accessor class loading success/failure, short-circuit metrics sampling normalization, domain socket disable interval validation, short-circuit client count bounds, positive striped threadpool validation, and compatibility of getters with `DFSClient` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/DfsClientConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/ExternalBlockReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/ExternalBlockReader.java

## Purpose
`ExternalBlockReader` adapts a pluggable `ReplicaAccessor` into the standard HDFS `BlockReader` interface, allowing custom replica-reading implementations to participate in normal DFS input stream reads.

## Important APIs, types, and functions
The constructor receives a `ReplicaAccessor`, visible replica length, and start offset. `read(byte[],...)` and `read(ByteBuffer)` call the accessor at the current `pos` and advance `pos` only on non-negative reads. `skip` advances forward without exceeding `visibleLength`. `available` returns remaining bytes capped to `Integer.MAX_VALUE`. `isShortCircuit` and `getNetworkDistance` delegate to the accessor. `readFully` and `readAll` delegate to `BlockReaderUtil`.

## Control flow
Reads are positional through the accessor rather than stream-position based. EOF is propagated directly if the accessor returns a negative value. Skips do not invoke the accessor and cannot move backward. `close` closes the accessor.

## State and persistence behavior
State consists of the accessor, visible length, and mutable current position. The class persists nothing and exposes no checksum or zero-copy mmap support (`getDataChecksum` and `getClientMmap` return null).

## Dependencies and integration points
It depends on `ReplicaAccessor`, `BlockReader`, `ClientMmap`, `ReadOption`, `DataChecksum`, and `BlockReaderUtil`. It is configured indirectly by `DfsClientConf` replica accessor builder classes and used when external replica access is selected.

## Risks and test signals
Tests should cover positional advancement, EOF without position advancement, skip clamping at visible length, large remaining length in `available`, accessor close propagation, direct `ByteBuffer` reads, and integration with `readFully`/`readAll`. A functional risk is that checksum and mmap are unsupported, so callers must tolerate null checksum and no zero-copy path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/ExternalBlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/LeaseRenewer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/LeaseRenewer.java

## Purpose
`LeaseRenewer` is the shared background renewer used by `DFSClient` instances that have files open for create or append. It ensures the NameNode sees periodic lease renewals so it does not treat the writer as failed and recover or reassign the lease.

## Important APIs, types, and functions
`getInstance(authority, ugi, dfsc)` returns a shared renewer for a NameNode authority and user, then registers the client. `remove(LeaseRenewer)` removes a renewer from the factory. `put(DFSClient)` starts or refreshes the daemon if the client is running. `closeClient(DFSClient)` unregisters a client and starts the empty grace period. `interruptAndJoin()` stops the daemon for tests/shutdown. `renew()` deduplicates clients by sorted client name and calls `DFSClient.renewLease`. The nested `Factory` and `Factory.Key` maintain the global `(authority, UGI) -> LeaseRenewer` map.

## Control flow
Adding a client updates the renewal period to the shortest half-RPC-timeout among registered clients. `put` starts a new `Daemon` when no daemon is running or the current one has expired, increments `currentId`, and uses `isLSRunning` to avoid multiple simultaneous daemons in one renewer. The daemon loop sleeps for `sleepPeriod`, renews when elapsed time reaches `renewal`, and exits if its id is stale, the renewer expired after being empty beyond `gracePeriod`, or the thread is interrupted. On `SocketTimeoutException`, it removes the renewer and closes all files being written with abort semantics; other `IOException`s log and retry later.

## State and persistence behavior
State is process-local: registered `DFSClient` list, renewal/grace/sleep timings, daemon reference, `currentId`, empty timestamp, factory key, instantiation trace for trace logging, and the static factory map. There is no disk persistence; the durable state being protected is the NameNode lease table.

## Dependencies and integration points
It depends on `DFSClient` methods (`getConf`, `getClientName`, `isClientRunning`, `renewLease`, `closeAllFilesBeingWritten`), `UserGroupInformation`, `HdfsConstants.LEASE_SOFTLIMIT_PERIOD`, `Daemon`, `Time`, `DFSClientFaultInjector`, and Hadoop exceptions/logging. It is called from DFSClient write lifecycle paths.

## Risks and test signals
Concurrency is the main risk: shared factory access, client list mutation, daemon id staleness, `AtomicBoolean` behavior, and empty grace expiry all interact. Tests should cover one renewer per authority/user, duplicate client registration, renewal period recalculation after client removal, daemon expiry and replacement, timeout abort behavior, `IOException` retry behavior, non-running client removal, trace logging, and close/interruption. The `isLSRunning` flag is set when a daemon starts and is not reset in this class, so tests should verify intended interaction with factory removal and creation of fresh renewers after daemon exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/LeaseRenewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/SnapshotDiffReportGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/SnapshotDiffReportGenerator.java

## Purpose
`SnapshotDiffReportGenerator` converts NameNode snapshot diff listing entries into the end-user `SnapshotDiffReport`. It summarizes where changes occurred and classifies them as modify, create, delete, or rename.

## Important APIs, types, and functions
`INODE_COMPARATOR` lexicographically compares `DiffReportListingEntry` source paths as byte-component arrays, handling a special null-root sentinel. `RenameEntry` pairs reference-created and reference-deleted entries by file id. `ChildrenDiff` stores per-directory created and deleted lists. The constructor receives snapshot names/root, direction flag, and modified/created/deleted listing entries. `generateReportList()` builds `dirDiffMap` and `renameMap`. `generateReport()` creates the final `SnapshotDiffReport`. The private `generateReport(DiffReportListingEntry)` expands a modified directory's child changes.

## Control flow
Generation sorts modified entries first. It groups created and deleted entries by parent directory id, using `ChunkedArrayList` for created/deleted lists, and records rename metadata for reference entries. The final report emits a `MODIFY` entry for each modified item, and for modified reference directories with child diffs, emits child create/delete/rename entries. Direction is controlled by `isFromEarlier`: when false, create/delete and rename source/target are reversed to represent a newer-to-older comparison.

## State and persistence behavior
State is in-memory maps and lists for one report generation. The method mutates `mlist` by sorting it and fills `dirDiffMap`/`renameMap`. No persistent state is written.

## Dependencies and integration points
It depends on `SnapshotDiffReport`, `SnapshotDiffReportListing.DiffReportListingEntry`, `DiffReportEntry`, `DiffType`, Guava `SignedBytes.lexicographicalComparator`, and Hadoop `ChunkedArrayList`. It is used by the HDFS client after receiving snapshot diff listing data from the NameNode.

## Risks and test signals
Tests should cover lexicographic ordering, null-root sentinel ordering, grouping multiple creates/deletes under one directory, rename pairing by file id, reference modified directories, direction reversal with `isFromEarlier=false`, empty lists, and repeated calls to `generateReport` on the same instance. A risk is that created-reference handling only sets the target when a target already exists, so rename pairing behavior depends on listing semantics and should be regression-tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/SnapshotDiffReportGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/BlockReaderIoProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/BlockReaderIoProvider.java

## Purpose
`BlockReaderIoProvider` wraps short-circuit local block `FileChannel` reads with optional sampled latency recording.

## Important APIs, types, and functions
The constructor accepts nullable `ShortCircuitConf`, `BlockReaderLocalMetrics`, and `Timer`; it enables sampling only when configuration exists and short-circuit metrics are enabled. `read(FileChannel, ByteBuffer, long)` performs the actual positional channel read and, for sampled calls, measures elapsed monotonic time and calls `addLatency`. `addLatency` records latency and logs one warning per provider if a sampled read exceeds 1000 ms.

## Control flow
Sampling compares a random integer in `[0, Integer.MAX_VALUE)` against a precomputed range derived from the configured sampling percentage. Unsampled reads call `FileChannel.read` directly. Sampled reads measure before and after the read and update rolling metrics.

## State and persistence behavior
State includes the metrics object, enabled flag, sample threshold, timer, and a boolean suppressing repeated slow-read warnings. Metrics are exported through Hadoop metrics, but this class itself persists nothing.

## Dependencies and integration points
It depends on `DfsClientConf.ShortCircuitConf`, `BlockReaderLocalMetrics`, `Timer`, `FileChannel`, `ByteBuffer`, and `ThreadLocalRandom`. It is used by the newer `BlockReaderLocal` short-circuit implementation, not the legacy reader in this subset.

## Risks and test signals
Tests should cover disabled metrics with null config, 0/100 sampling behavior, latency recording, warning suppression after the first slow read, exception propagation from `FileChannel.read`, and deterministic timer injection. The range computation intentionally scales by sampling percentage; extreme values are normalized upstream in `ShortCircuitConf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/BlockReaderIoProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/BlockReaderLocalMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/BlockReaderLocalMetrics.java

## Purpose
`BlockReaderLocalMetrics` registers and maintains rolling average latency metrics for short-circuit local reads.

## Important APIs, types, and functions
`create()` obtains the default Hadoop `MetricsSystem`, constructs a metrics instance, and registers it under `HdfsShortCircuitReads`. `addShortCircuitReadLatency(long)` adds a sample to `MutableRollingAverages` with value name `ShortCircuitLocalReads`. `collectThreadLocalStates()` flushes thread-local metric state. `getShortCircuitReadRollingAverages()` exposes the metric for tests.

## Control flow
The class relies on Hadoop metrics annotations to initialize and export `shortCircuitReadRollingAverages`. Callers add samples as reads complete; metrics system collection later publishes rolling averages.

## State and persistence behavior
State is the mutable rolling-average metric object registered with the process metrics system. No files are written.

## Dependencies and integration points
It depends on Hadoop Metrics2 annotations, `DefaultMetricsSystem`, `MetricsSystem`, and `MutableRollingAverages`. `BlockReaderIoProvider` records into this class.

## Risks and test signals
Tests should verify metric registration name, value name, latency sample accumulation, thread-local collection, and behavior if `create()` is called multiple times in the same metrics system. Operationally, metric cardinality is low, but registration conflicts can be a risk in repeated unit-test setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/BlockReaderLocalMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/package-info.java

## Purpose
This package-info documents the `org.apache.hadoop.hdfs.client.impl.metrics` package as support for tracking Block Reader Local latencies.

## Important APIs, types, and functions
It declares package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Evolving`, indicating internal HDFS client metrics APIs that may still change.

## Control flow
There is no executable control flow.

## State and persistence behavior
There is no runtime state or persistence.

## Dependencies and integration points
It imports Hadoop classification annotations and applies them to the metrics package containing `BlockReaderIoProvider` and `BlockReaderLocalMetrics`.

## Risks and test signals
Test signal is limited to API classification and package documentation. Build or javadoc checks should ensure annotations resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/package-info.java

## Purpose
This package-info declares the `org.apache.hadoop.hdfs.client.impl` package for internal HDFS client implementation classes.

## Important APIs, types, and functions
It contains only the package declaration and license header. No package-level annotations are present.

## Control flow
There is no executable control flow.

## State and persistence behavior
There is no runtime state or persistence.

## Dependencies and integration points
The package contains block readers, client configuration, lease renewal, corrupt block iteration, external block reader adaptation, and snapshot diff generation. This file itself introduces no dependencies.

## Risks and test signals
Only build/package consistency matters. Tests are not applicable beyond compilation and javadoc packaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/package-info.java

## Purpose
This package-info documents `org.apache.hadoop.hdfs.client` as the package providing administrative APIs for HDFS.

## Important APIs, types, and functions
It applies `@InterfaceAudience.Public` and `@InterfaceStability.Evolving` to the package, indicating public but evolving HDFS client APIs.

## Control flow
There is no executable control flow.

## State and persistence behavior
There is no runtime state or persistence.

## Dependencies and integration points
It imports Hadoop classification annotations and classifies the surrounding client API package, which includes public client-side administrative types.

## Risks and test signals
Build and javadoc checks should verify annotation resolution. API compatibility review should consider the package-level public/evolving contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/Event.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/Event.java

## Purpose
`Event` defines the public unstable data model emitted by HDFS inotify. It represents edit-log-derived filesystem changes such as create, close, append, rename, metadata update, unlink, and truncate.

## Important APIs, types, and functions
The base class stores an `EventType` enum. Nested event classes include `CloseEvent`, `CreateEvent`, `MetadataUpdateEvent`, `RenameEvent`, `AppendEvent`, `UnlinkEvent`, and `TruncateEvent`. `CreateEvent` has an `INodeType` enum and builder for file/directory/symlink creation fields including owner, group, permissions, symlink target, overwrite flag, default block size, and optional erasure-coded flag. `MetadataUpdateEvent` has `MetadataType` values for times, replication, owner, permissions, ACLs, and xAttrs, also using a builder. Rename, append, and unlink use builders; close and truncate use direct constructors.

## Control flow
There is little behavior beyond construction, getters, and `toString`. Builders accumulate optional fields and create immutable-in-practice event instances. `MetadataUpdateEvent.toString` conditionally includes fields based on `metadataType`. Create string formatting conditionally includes symlink target.

## State and persistence behavior
Each event instance stores event payload fields in memory. Lists for ACLs and xAttrs are referenced directly rather than defensively copied. There is no persistence here; events are serialized/deserialized elsewhere from edit-log/inotify RPC data.

## Dependencies and integration points
It depends on Hadoop permissions (`FsPermission`, `AclEntry`), `XAttr`, Java `Optional`, and classification annotations. It is consumed by HDFS inotify streams and event batches, exposing user-visible event metadata.

## Risks and test signals
Tests should cover every event type, builder field propagation, optional erasure-coded absence/presence, symlink-only target semantics, metadata-specific `toString`, ACL/xAttr null handling, timestamp/file-size getters, and public unstable compatibility. Because fields are mutable references and not final, callers should not assume deep immutability of ACL/xAttr lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/Event.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/EventBatch.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/EventBatch.java

## Purpose
`EventBatch` groups all inotify `Event` objects that occurred under the same NameNode transaction ID.

## Important APIs, types, and functions
The constructor accepts a `txid` and `Event[]`. `getTxid()` returns the transaction id, and `getEvents()` returns the event array.

## Control flow
There is no behavior beyond construction and getters.

## State and persistence behavior
The class stores the event array reference directly and has no persistence. It is a client-side transport/value object.

## Dependencies and integration points
It depends on `Event` and classification annotations. It is contained in `EventBatchList` and delivered by the inotify stream to clients.

## Risks and test signals
Tests should verify txid/event preservation, empty event arrays, and caller expectations around array mutability. Inotify ordering relies on batches being processed by txid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/EventBatch.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/EventBatchList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/EventBatchList.java

## Purpose
`EventBatchList` is the private HDFS client container for a page of inotify event batches plus transaction-id range metadata.

## Important APIs, types, and functions
The constructor stores a `List<EventBatch>`, `firstTxid`, `lastTxid`, and `syncTxid`. Getters expose the batch list and transaction ids.

## Control flow
There is no executable behavior beyond getters.

## State and persistence behavior
State is the referenced batch list and txid metadata. `firstTxid` identifies the first observed txid, `lastTxid` the last read txid, and `syncTxid` the latest NameNode synced txid. No local persistence occurs.

## Dependencies and integration points
It depends on `EventBatch` and is used by client inotify polling to determine event progress, lag, and whether gaps may have occurred after edit-log cleanup.

## Risks and test signals
Tests should cover empty batch pages, txid metadata consistency, lag calculations using `syncTxid`, and gap detection when `firstTxid` is higher than the requested next txid. The list reference is not copied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/EventBatchList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/MissingEventsException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/MissingEventsException.java

## Purpose
`MissingEventsException` signals that an inotify client expected the next event batch to start at one transaction id but the NameNode returned a later transaction id, usually because intervening edits were removed during checkpointing.

## Important APIs, types, and functions
It extends `Exception`, stores `expectedTxid` and `actualTxid`, provides a no-arg constructor and a constructor for both ids, getters, and a detailed `toString`.

## Control flow
The exception carries txid metadata and formats a diagnostic string. No other behavior exists.

## State and persistence behavior
State is the two long txid values. There is no persistence.

## Dependencies and integration points
It is public/evolving in the HDFS inotify package and consumed by inotify stream clients as a signal that they cannot reconstruct a gap from available edit logs.

## Risks and test signals
Tests should verify txid preservation, default constructor values, serialization compatibility via `serialVersionUID`, and message clarity. Client code should handle this as a data-loss/gap condition rather than a transient retry alone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/inotify/MissingEventsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/BasicInetPeer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/BasicInetPeer.java

## Purpose
`BasicInetPeer` adapts a regular Java `Socket` without an associated channel to the HDFS `Peer` interface.

## Important APIs, types, and functions
The constructor captures the socket, its input/output streams, and whether the socket address is local. `getInputStreamChannel()` returns null because the socket has no channel. Read timeout, receive buffer, TCP_NODELAY, close, address string, stream, locality, domain socket, and security methods implement `Peer`.

## Control flow
Operations mostly delegate to the underlying socket and cached streams. `setWriteTimeout` is intentionally a no-op because blocking Java socket writes cannot have a timeout without NIO.

## State and persistence behavior
State is the socket, cached streams, and local flag. Closing closes the socket. No persistence occurs.

## Dependencies and integration points
It depends on `Socket` and `DomainSocket` types and implements `Peer` for DataNode data-transfer clients that cannot use NIO channels.

## Risks and test signals
Tests should cover null channel behavior, no-op write timeout, address-string behavior before/after connection, local detection, stream reuse, close idempotence, and `hasSecureChannel=false`. Callers needing write timeouts should use `NioInetPeer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/BasicInetPeer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/DomainPeer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/DomainPeer.java

## Purpose
`DomainPeer` adapts a UNIX domain socket to the HDFS `Peer` interface for local DataNode communication.

## Important APIs, types, and functions
The constructor stores the `DomainSocket`, streams, and channel. Read/write timeout and receive buffer methods use domain-socket attributes. Address methods return `unix:<path>` and `<local>`. `isLocal()` always returns true, `getTcpNoDelay()` returns false, `getDomainSocket()` returns the underlying socket, and `hasSecureChannel()` returns true.

## Control flow
All I/O properties delegate to the domain socket. `close` closes the domain socket. Security is treated as local secure communication based on domain socket path permission controls.

## State and persistence behavior
State is the domain socket and cached stream/channel handles. No persistence occurs.

## Dependencies and integration points
It depends on Hadoop `DomainSocket` and implements `Peer` for local short-circuit/domain-socket data paths and peer caches.

## Risks and test signals
Tests should cover timeout attributes, receive buffer attribute, close/open status, path-based address strings, local/secure flags, and channel availability. Security assumptions depend on correct domain socket path permission validation outside this class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/DomainPeer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/EncryptedPeer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/EncryptedPeer.java

## Purpose
`EncryptedPeer` wraps an existing `Peer` with encrypted input/output streams from an `IOStreamPair`, while preserving peer metadata and timeout behavior through delegation.

## Important APIs, types, and functions
The constructor stores the enclosed peer, encrypted streams, and an encrypted channel if the input stream implements `ReadableByteChannel`. Timeout, receive-buffer, TCP_NODELAY, close-state, address, locality, and domain-socket methods delegate to the enclosed peer. `getInputStream` and `getOutputStream` return encrypted streams. `hasSecureChannel()` always returns true.

## Control flow
Close attempts to close the encrypted input, then encrypted output, then the enclosed peer in nested finally blocks. Other methods are direct delegation or stream access.

## State and persistence behavior
State is a wrapper around the enclosed peer and encrypted stream pair. No persistence occurs.

## Dependencies and integration points
It depends on `Peer`, `IOStreamPair`, `DomainSocket`, and Java stream/channel types. It is used by HDFS data-transfer encryption layers to keep the rest of the block-reader pipeline using `Peer`.

## Risks and test signals
Tests should verify encrypted stream use, close ordering under exceptions, channel null/non-null behavior depending on stream type, delegated timeout/address/locality behavior, `hasSecureChannel=true`, and no accidental exposure of unencrypted enclosed streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/EncryptedPeer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/NioInetPeer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/NioInetPeer.java

## Purpose
`NioInetPeer` adapts a socket with a channel to `Peer` using Hadoop `SocketInputStream` and `SocketOutputStream`, enabling simulated blocking I/O with read and write timeouts.

## Important APIs, types, and functions
The constructor creates NIO-backed socket streams from the socket channel and records locality. `getInputStreamChannel()` returns the input stream because it is a `ReadableByteChannel`. Timeout methods set timeouts on the Hadoop socket streams. Other methods expose buffer, TCP_NODELAY, addresses, streams, locality, null domain socket, insecure channel, and close behavior.

## Control flow
Close closes the input stream and then the output stream in a finally block; closing either stream also closes the socket. Reads/writes happen through the wrapped Hadoop streams.

## State and persistence behavior
State is the socket, NIO-backed streams, and local flag. No persistence occurs.

## Dependencies and integration points
It depends on Hadoop `SocketInputStream`, `SocketOutputStream`, `Peer`, and Java sockets. It is the preferred TCP peer when timeout-capable writes and channel-based packet reads are needed.

## Risks and test signals
Tests should cover timeout updates, channel availability, close behavior when input close fails, address strings, local detection, and `hasSecureChannel=false`. The constructor requires a socket channel; callers must not pass a socket without one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/NioInetPeer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/Peer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/Peer.java

## Purpose
`Peer` is the HDFS client abstraction for a DataNode connection, hiding whether the transport is a regular socket, NIO socket, UNIX domain socket, or encrypted wrapper.

## Important APIs, types, and functions
The interface exposes input channel, read/write timeout setters, receive buffer size, TCP_NODELAY, close state, close, remote/local address strings, input/output streams, locality, optional `DomainSocket`, and `hasSecureChannel`.

## Control flow
As an interface it has no executable flow. Implementations define how timeout, close, and stream semantics are realized for each transport.

## State and persistence behavior
No state exists in the interface. Implementations own transport resources.

## Dependencies and integration points
It extends `Closeable` and references Java stream/channel types plus Hadoop `DomainSocket`. `BlockReaderRemote`, peer caches, data-transfer encryption, and domain-socket short-circuit paths depend on this abstraction.

## Risks and test signals
Interface-level tests should verify all implementations satisfy close idempotence, stream lifetime until peer close, timeout behavior documented for basic sockets, locality/security flags, and optional channel/domain socket nullability. Callers must handle a null input channel for `BasicInetPeer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/net/Peer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AclException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AclException.java

## Purpose
`AclException` is an HDFS private `IOException` subclass for failures while manipulating ACLs.

## Important APIs, types, and functions
It provides constructors for a message and for a message plus cause.

## Control flow
There is no behavior beyond exception construction.

## State and persistence behavior
State is standard exception message/cause plus `serialVersionUID`. No persistence occurs.

## Dependencies and integration points
It depends on `IOException` and Hadoop classification annotations. It is thrown by ACL-related HDFS protocol/client/server code.

## Risks and test signals
Tests should verify message/cause propagation and serialization compatibility if used across RPC boundaries. Behavioral risk is low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AclException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AddErasureCodingPolicyResponse.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AddErasureCodingPolicyResponse.java

## Purpose
`AddErasureCodingPolicyResponse` represents the per-policy result of adding an erasure coding policy.

## Important APIs, types, and functions
Constructors create success responses from an `ErasureCodingPolicy` or failure responses from an error string or `HadoopIllegalArgumentException`. Getters expose success, policy, and error message. `toString`, `equals`, and `hashCode` include policy, success flag, and error message.

## Control flow
Construction sets `succeed` based on constructor choice. `toString` branches between success and failure text.

## State and persistence behavior
State is the policy reference, boolean success flag, and optional error string. No local persistence occurs; objects are protocol values.

## Dependencies and integration points
It depends on `ErasureCodingPolicy`, `HadoopIllegalArgumentException`, and Apache Commons builders. It is used by erasure coding admin APIs and RPC responses.

## Risks and test signals
Tests should cover success/failure constructors, null or present error messages, equality/hash consistency, and string output. A failure response still carries a policy, so callers should not infer null policy on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AddErasureCodingPolicyResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AlreadyBeingCreatedException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AlreadyBeingCreatedException.java

## Purpose
`AlreadyBeingCreatedException` signals that a create request targeted a file that is already open for creation and not yet closed.

## Important APIs, types, and functions
It extends `IOException`, has a stable `serialVersionUID`, and exposes a single message constructor.

## Control flow
There is no behavior beyond exception construction.

## State and persistence behavior
State is the exception message. No local persistence occurs.

## Dependencies and integration points
It is private/evolving HDFS protocol exception used by create/lease-related NameNode and client paths.

## Risks and test signals
Tests should verify message propagation and caller handling in create/append conflict paths. RPC exception mapping should preserve the type where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/AlreadyBeingCreatedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BatchedDirectoryListing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BatchedDirectoryListing.java

## Purpose
`BatchedDirectoryListing` is an internal struct for partial batched directory listing responses between HDFS client and NameNode.

## Important APIs, types, and functions
The constructor stores an array of `HdfsPartialListing`, a `hasMore` flag, and a `startAfter` continuation byte array. Getters expose each field. `toString` uses `ToStringBuilder`.

## Control flow
There is no behavior beyond field access.

## State and persistence behavior
State is the referenced listing array, pagination flag, and continuation key. No local persistence occurs.

## Dependencies and integration points
It depends on `HdfsPartialListing`, Apache Commons `ToStringBuilder`, and HDFS client/NameNode batched listing APIs.

## Risks and test signals
Tests should cover empty and multi-entry listing arrays, continuation behavior with `hasMore`, byte-array preservation, and string diagnostics. Arrays are not defensively copied, so mutability should be considered by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BatchedDirectoryListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/Block.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/Block.java

## Purpose
`Block` is the core HDFS block identity/value type, carrying block id, length, and generation stamp. Its equality, hash, and ordering are intentionally based only on block id, while helper methods support stricter id-plus-generation comparison.

## Important APIs, types, and functions
Static constants define block file prefix and metadata extension. Regex patterns parse block and meta filenames. Static helpers include `isBlockFilename`, `filename2id`, `isMetaFilename`, `metaToBlockFile`, `getGenerationStamp`, `getBlockId`, `toString(Block)`, and `matchingIdAndGenStamp`. Instance APIs include constructors from ids, another block, or a block file; setters/getters; `getBlockName`; `appendStringTo`; Writable `write/readFields`; id-only `writeId/readId`; `compareTo`; `equals`; and `hashCode`.

## Control flow
Writable serialization writes block id, byte length, and generation stamp, and deserialization rejects negative `numBytes`. Filename parsing returns 0 or the grandfather generation stamp when patterns do not match. `compareTo`, `equals`, and `hashCode` ignore length and generation stamp, matching the class contract.

## State and persistence behavior
State is mutable block id, number of bytes, and generation stamp. The class participates in Hadoop Writable serialization and is registered in `WritableFactories`, so it crosses RPC/storage serialization boundaries.

## Dependencies and integration points
It depends on `Writable`, `WritableFactories`, regex utilities, `HdfsConstants`, and Java `File`. It is foundational across HDFS protocol, NameNode metadata, DataNode storage, block readers, and block reports.

## Risks and test signals
Critical tests should verify filename regexes including negative ids and metadata generation stamps, Writable round trip and negative-size rejection, equality/hash ignoring generation stamp, `matchingIdAndGenStamp` strict comparison, and compatibility of `writeId/readId`. Callers must avoid using `equals` when generation stamp matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/Block.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockChecksumOptions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockChecksumOptions.java

## Purpose
`BlockChecksumOptions` carries options controlling how lower-level chunk checksums are combined into a block-level checksum.

## Important APIs, types, and functions
Constructors accept a `BlockChecksumType` and optional stripe length. Getters expose type and stripe length. `toString` formats both fields.

## Control flow
There is no behavior beyond construction and formatting.

## State and persistence behavior
State is final checksum type and stripe length. No local persistence occurs.

## Dependencies and integration points
It depends on `BlockChecksumType` and is used by HDFS block checksum APIs, especially when composite CRCs or striped checksum behavior are requested.

## Risks and test signals
Tests should cover default stripe length of 0, explicit stripe lengths, string formatting, and caller validation for unsupported combinations. The class does not validate stripe length itself.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockChecksumOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockChecksumType.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockChecksumType.java

## Purpose
`BlockChecksumType` enumerates supported algorithms for computing block-level checksums from chunk checksums or CRCs.

## Important APIs, types, and functions
Values are `MD5CRC`, representing an MD5 digest over chunk CRCs, and `COMPOSITE_CRC`, representing chunk-independent CRC computation, optionally striped.

## Control flow
There is no executable behavior beyond enum value use.

## State and persistence behavior
Enum constants are stable protocol values. No local persistence occurs in this file.

## Dependencies and integration points
It is used by `BlockChecksumOptions` and HDFS checksum request/response paths.

## Risks and test signals
Tests should verify serialization/protobuf mappings elsewhere and behavior for each checksum type. Adding enum values requires compatibility review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockChecksumType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockLocalPathInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockLocalPathInfo.java

## Purpose
`BlockLocalPathInfo` carries the local filesystem paths for a block data file and its metadata file on a DataNode.

## Important APIs, types, and functions
The constructor stores an `ExtendedBlock`, block file path, and metadata file path. `getBlockPath`, `getBlock`, and `getMetaPath` expose those values.

## Control flow
There is no behavior beyond construction and getters.

## State and persistence behavior
State is the block reference and two path strings. The path strings are initialized to empty defaults but set by the constructor. No local persistence occurs here.

## Dependencies and integration points
It depends on `ExtendedBlock` and is returned by `ClientDatanodeProtocol#getBlockLocalPathInfo`. `BlockReaderLocalLegacy` consumes it to open local block and checksum files.

## Risks and test signals
Tests should verify path preservation, empty/null path handling as supplied by the DataNode, and integration with legacy short-circuit reads. Security risk is external: exposing paths is only safe under DataNode-side authorization and Kerberos/token checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockLocalPathInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockStoragePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockStoragePolicy.java

## Purpose
`BlockStoragePolicy` describes preferred and fallback storage media for block replicas, including creation fallback, replication fallback, and copy-on-create policy behavior.

## Important APIs, types, and functions
Constructors set a 4-bit id, name, preferred `StorageType[]`, creation fallbacks, replication fallbacks, and optional `copyOnCreateFile`. `chooseStorageTypes(short)` returns desired non-transient storage types for a replication factor. Overloads subtract already chosen types and handle unavailable storage by replacing with creation or replication fallbacks. `chooseExcess` identifies storage types to delete. `getCreationFallback`, `getReplicationFallback`, `equals`, `hashCode`, `toString`, and `BlockStoragePolicySpi` getters expose policy metadata.

## Control flow
Storage selection starts from preferred types, skips transient types for usage-accounting accuracy, repeats the last non-transient type if more replicas are needed, subtracts already chosen types with `diff`, replaces unavailable types from the appropriate fallback list, removes excess after fallback replacement, and logs if not enough storage types remain to satisfy expected replicas.

## State and persistence behavior
State is policy metadata and arrays. The only mutable field is `copyOnCreateFile`, though it is set only by constructors. Equality and hash use policy id only, making id uniqueness critical.

## Dependencies and integration points
It implements `BlockStoragePolicySpi` and depends on `StorageType`, `EnumSet`, and logging. It is used by NameNode/block placement and exposed through filesystem storage policy APIs.

## Risks and test signals
Tests should cover transient storage exclusion, replication larger than preferred list, chosen/excess subtraction with duplicates, fallback selection for new blocks versus replication, unavailable fallback exhaustion warnings, equality by id, copy-on-create flag, and array mutation risks through returned arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockStoragePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockType.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockType.java

## Purpose
`BlockType` classifies HDFS blocks as replicated contiguous blocks or erasure-coded striped blocks.

## Important APIs, types, and functions
Enum values are `CONTIGUOUS` and `STRIPED`. `fromBlockId(long)` uses the highest bit of the block id to identify striped blocks. `BLOCK_ID_MASK` and `BLOCK_ID_MASK_STRIPED` define the current bit mask.

## Control flow
`fromBlockId` masks the id and returns `STRIPED` if the striped bit is set, otherwise `CONTIGUOUS`.

## State and persistence behavior
Enum constants and bit masks are static protocol conventions. No local persistence occurs.

## Dependencies and integration points
It is used by block-management and protocol code to interpret block ids for replicated versus erasure-coded layouts.

## Risks and test signals
Tests should cover high-bit set/unset ids, legacy random ids that may make conversion unreliable, and future extension compatibility if additional high bits are claimed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/BlockType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveEntry.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveEntry.java

## Purpose
`CacheDirectiveEntry` pairs a cache directive's configuration with its runtime statistics for list responses.

## Important APIs, types, and functions
The constructor stores `CacheDirectiveInfo` and `CacheDirectiveStats`. Getters expose both.

## Control flow
There is no behavior beyond construction and getters.

## State and persistence behavior
State is two final references. No local persistence occurs.

## Dependencies and integration points
It is public/evolving and used by `CacheDirectiveIterator` and NameNode cache directive list RPCs.

## Risks and test signals
Tests should verify info/stats preservation and behavior with null values if RPC layers permit them. The object does not enforce invariants between requested directive fields and reported stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveInfo.java

## Purpose
`CacheDirectiveInfo` describes a path-based cache directive for HDFS centralized cache management. Its fields are nullable so the same type can represent create, modify, filter, and list payloads.

## Important APIs, types, and functions
The nested `Builder` supports id, path, replication, pool, and expiration setters plus copy-construction. `Expiration` represents relative or absolute expiration, has `NEVER`, `MAX_RELATIVE_EXPIRY_MS`, factory methods `newRelative`, `newAbsolute(Date)`, `newAbsolute(long)`, and accessors for raw millis, absolute date, and absolute millis. The outer class exposes getters, `equals`, `hashCode`, and a compact `toString` that includes only non-null fields.

## Control flow
Builder methods return `this` for chaining and `build()` creates a new info object. Relative expiration validates that the duration does not exceed `Long.MAX_VALUE / 4` to avoid overflow. `getAbsoluteMillis` converts relative expirations using the local current time; `toString` uses human-readable duration or ISO date formatting.

## State and persistence behavior
State is final directive fields. `Expiration` is immutable. No local persistence happens here, but objects are serialized in RPC/edit-log-related cache directive paths.

## Dependencies and integration points
It depends on Hadoop `Path`, `DFSUtilClient` formatting helpers, Apache Commons equality/hash builders, and Hadoop preconditions. It is consumed by cache directive create/modify/list APIs and by `CacheDirectiveIterator` filters.

## Risks and test signals
Tests should cover nullable partial directives, builder copy semantics, relative/absolute expiration formatting, `NEVER`, overflow validation, equality/hash with nulls, `toString` field omission, and time-sensitive behavior of relative expiration conversion. Client/server clocks matter because the server-side clock is authoritative for actual expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveIterator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveIterator.java

## Purpose
`CacheDirectiveIterator` is a `BatchedRemoteIterator` over HDFS cache directives, with tracing and a compatibility fallback for older NameNodes that cannot filter by directive id.

## Important APIs, types, and functions
The constructor takes a `ClientProtocol`, `CacheDirectiveInfo` filter, and `Tracer`, starting iteration at previous id `0L`. `makeRequest(Long)` calls `namenode.listCacheDirectives`. `elementToPrevKey` returns the entry id for pagination. `removeIdFromFilter` clears the id from a filter. The nested `SingleEntry` wraps exactly one matching entry as a `BatchedEntries` result.

## Control flow
Each batch request runs inside a trace scope named `listCacheDirectives`. If the server throws an `IOException` containing `"Filtering by ID is unsupported"`, the iterator removes the id filter, requests a page starting at `id - 1`, scans for the requested id, and returns a single-entry result. If the id is not found, it throws a `RemoteException` wrapping `InvalidRequestException`.

## State and persistence behavior
State is the current mutable filter, NameNode proxy, and tracer. The filter may be changed after compatibility fallback. No local persistence occurs.

## Dependencies and integration points
It depends on `BatchedRemoteIterator`, `ClientProtocol`, tracing, `RemoteException`, `InvalidRequestException`, and `CacheDirectiveEntry`. It is used by HDFS cache directive list APIs and must handle failover/retry semantics inherited from `BatchedRemoteIterator`.

## Risks and test signals
Tests should cover normal pagination, trace-scope creation, prev-key extraction, compatibility fallback with matching id, fallback with missing id, brittle ordering assumption around `id - 1`, exception propagation for unrelated IO failures, and null-entry precondition behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveStats.java

## Purpose
`CacheDirectiveStats` reports runtime cache progress for a single cache directive.

## Important APIs, types, and functions
The nested `Builder` sets bytes needed, bytes cached, files needed, files cached, and expired flag, then builds an immutable stats object. Getters expose all values. `toString` formats the counters and expiration state.

## Control flow
There is no behavior beyond builder chaining, construction, getters, and formatting.

## State and persistence behavior
State is final counter values and `hasExpired`. No local persistence occurs.

## Dependencies and integration points
It is public/evolving and paired with `CacheDirectiveInfo` inside `CacheDirectiveEntry` for cache directive list/status APIs.

## Risks and test signals
Tests should cover builder defaults of zero/false, all setters, string output, and large counter values. The builder does not reject negative values, so validation must occur upstream if needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CacheDirectiveStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolEntry.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolEntry.java

## Purpose
`CachePoolEntry` pairs cache pool configuration with runtime cache pool statistics for list responses.

## Important APIs, types, and functions
The constructor stores `CachePoolInfo` and `CachePoolStats`. Getters expose both.

## Control flow
There is no behavior beyond construction and getters.

## State and persistence behavior
State is two final references. No local persistence occurs.

## Dependencies and integration points
It is public/evolving and used by `CachePoolIterator` and NameNode cache pool listing RPCs.

## Risks and test signals
Tests should verify info/stats preservation and caller behavior if either reference is null. Invariants between pool limits and over-limit stats are enforced elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolInfo.java

## Purpose
`CachePoolInfo` describes a centralized cache pool, including ownership, permissions, byte limit, default replication, and maximum directive relative expiry. It is used in RPCs and can be stored in the edit log.

## Important APIs, types, and functions
Constants define unlimited limit, default limit, default replication, and relative-expiry-never. The constructor requires a pool name. Chainable setters/getters cover owner, group, mode, limit, default replication, and max relative expiry. `toString`, `equals`, and `hashCode` cover all fields. Static `validate(CachePoolInfo)` checks null info, non-negative limit/default replication, max relative expiry bounds, and valid pool name. `validateName` rejects null or empty names.

## Control flow
Setters mutate the same object and return it for chaining. Validation throws `InvalidRequestException` or `IOException` for invalid fields. Empty names are rejected because listing all pools starts from an empty previous key and an empty pool name would be ambiguous.

## State and persistence behavior
State is mutable pool metadata. The type is serializable through HDFS RPC/edit-log conversion layers, though this class itself has no serialization code.

## Dependencies and integration points
It depends on `FsPermission`, `InvalidRequestException`, `CacheDirectiveInfo.Expiration`, nullable annotations, and Apache Commons builders. It is used by cache pool create/modify/list APIs and `CachePoolEntry`.

## Risks and test signals
Tests should cover all validation failures, null optional fields for partial modification, equals/hash with nullable fields, string permission formatting, max expiry boundaries, unlimited limit, and default replication semantics. The negative replication check uses `< 0`, so zero is accepted by this class and must be interpreted by higher layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolIterator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolIterator.java

## Purpose
`CachePoolIterator` is a `BatchedRemoteIterator` over HDFS cache pools with tracing support.

## Important APIs, types, and functions
The constructor takes a `ClientProtocol` and `Tracer`, starting pagination with previous key `""`. `makeRequest(String)` calls `namenode.listCachePools(prevKey)` inside a trace scope named `listCachePools`. `elementToPrevKey(CachePoolEntry)` returns the pool name from entry info.

## Control flow
Iteration delegates each batch request to the NameNode. Pagination uses the last returned pool name as the next previous key, matching the cache pool listing contract.

## State and persistence behavior
State is the NameNode proxy and tracer. No local persistence occurs.

## Dependencies and integration points
It depends on `BatchedRemoteIterator`, `ClientProtocol`, `CachePoolEntry`, and Hadoop tracing. It is used by HDFS cache pool list APIs and participates in failover/retry behavior inherited from the iterator base.

## Risks and test signals
Tests should cover empty start key behavior, multiple batches, trace scope closing, prev-key extraction, exception propagation, and pool names sorted consistently with NameNode pagination. Empty pool names are disallowed by `CachePoolInfo.validateName`, supporting use of `""` as initial key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolStats.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolStats.java

## Purpose
`CachePoolStats` reports aggregate cache usage for a cache pool.

## Important APIs, types, and functions
The nested `Builder` sets bytes needed, bytes cached, bytes over limit, files needed, and files cached. `build()` creates the stats object. Getters expose each counter, and `toString` formats all counters.

## Control flow
There is no behavior beyond builder chaining, construction, getters, and formatting.

## State and persistence behavior
State is final aggregate counters. No local persistence occurs.

## Dependencies and integration points
It is public/evolving and paired with `CachePoolInfo` in `CachePoolEntry` for cache pool list/status APIs.

## Risks and test signals
Tests should cover builder defaults, all setter paths, large values, string output, and over-limit reporting. Negative values are not checked here, so producer-side validation is needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CachePoolStats.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ClientDatanodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ClientDatanodeProtocol.java

## Purpose
`ClientDatanodeProtocol` defines the private/evolving RPC contract from HDFS clients to DataNodes for replica visibility, local path discovery, DataNode administration, reconfiguration, block reports, volume reports, and disk balancer operations.

## Important APIs, types, and functions
The interface is annotated with `@KerberosInfo` for the DataNode principal config key and `@TokenInfo(BlockTokenSelector.class)` for block-token authentication. `versionID = 9L` is historical and no longer updated for protobuf protocol serialization. Methods include `getReplicaVisibleLength`, `refreshNamenodes`, `deleteBlockPool`, `getBlockLocalPathInfo`, `shutdownDatanode`, `evictWriters`, `getDatanodeInfo`, reconfiguration start/status/list methods, `triggerBlockReport`, `getBalancerBandwidth`, `getVolumeReport`, disk balancer submit/cancel/query, and `getDiskBalancerSetting`.

## Control flow
As an interface it contains no executable flow. Implementations on the DataNode side enforce authorization, token checks, and operation semantics. Clients call methods through RPC proxies, often via helper classes such as `DFSUtilClient`.

## State and persistence behavior
The interface owns no state. Implementations may mutate DataNode runtime state, disk balancer plans, block pool directories, configuration, and block reporting behavior. `getBlockLocalPathInfo` exposes local data/meta paths only when DataNode security/authorization requirements are met.

## Dependencies and integration points
It depends on HDFS protocol types (`ExtendedBlock`, `BlockLocalPathInfo`, `DatanodeLocalInfo`, `DatanodeVolumeInfo`), security tokens, `BlockReportOptions`, `ReconfigurationTaskStatus`, `DiskBalancerWorkStatus`, and client config keys. `BlockReaderLocalLegacy` uses `getBlockLocalPathInfo`; administration tools use the DataNode management methods.

## Risks and test signals
Tests should cover protobuf/wire compatibility for every method, Kerberos principal and block-token behavior, local path authorization, delete-block-pool force semantics, shutdown-for-upgrade behavior, reconfiguration status lifecycle, block report triggering, disk balancer plan validation/cancellation/status, and client behavior across DataNode restarts or unsupported methods. Interface changes require matching `ClientDatanodeProtocol.proto` updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ClientDatanodeProtocol.java -->
