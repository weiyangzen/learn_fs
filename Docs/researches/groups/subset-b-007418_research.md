# subset-b-007418

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSClient.java

## Purpose
`DFSClient` is the private HDFS client core used by `DistributedFileSystem` to talk to the NameNode through `ClientProtocol` and to DataNodes through the data-transfer path. It is the main façade for file creation, append, open, metadata operations, snapshots, cache directives, encryption zones, erasure coding administration, ACLs, xattrs, delegation tokens, checksums, dead-node tracking, and client-side read/write statistics.

## Important APIs, Types, and Functions
The class implements `Closeable`, `RemotePeerFactory`, `DataEncryptionKeyFactory`, and `KeyProviderTokenIssuer`. Its key collaborators are `ClientProtocol namenode`, `DfsClientConf`, `LeaseRenewer`, `ClientContext`, `SaslDataTransferClient`, `DFSInputStream`, `DFSStripedInputStream`, `DFSOutputStream`, `DFSHedgedReadMetrics`, and a cached `DataEncryptionKey`.

Construction flows through `DFSClient(URI, ClientProtocol, Configuration, FileSystem.Statistics)`, which builds the client config, obtains or accepts a NameNode proxy, computes local bind addresses, prepares default read/write `CachingStrategy`, initializes shared hedged and striped read pools, and constructs the SASL data-transfer client. Public filesystem APIs are mostly traced wrappers over `ClientProtocol`: `getLocatedBlocks`, `create`, `primitiveCreate`, `append`, `setReplication`, `rename`, `truncate`, `delete`, `listPaths`, `getFileInfo`, `mkdirs`, `setPermission`, snapshots, cache pools/directives, ACL/xattr methods, encryption-zone methods, erasure-coding methods, `listOpenFiles`, `msync`, and inotify stream creation. Data path helpers include `openInternal`, `createWrappedInputStream`, `createWrappedOutputStream`, `newConnectedPeer`, `connectToDN`, and `inferChecksumTypeByReading`.

## Control Flow
The constructor chooses among three NameNode proxy paths: a lossy proxy for configured HA tests, an injected `ClientProtocol` for tests, or a normal `NameNodeProxiesClient` proxy for production. Most public methods start with `checkOpen()`, enter a `TraceScope`, call one NameNode RPC, and unwrap expected `RemoteException` subclasses into stable client-facing exceptions.

Read open calls fetch initial `LocatedBlocks` and choose `DFSStripedInputStream` when the file carries an erasure-coding policy, otherwise `DFSInputStream`. Write create calls mask permissions, call `DFSOutputStream.newStreamForCreate`, and immediately register the stream with the lease renewer through `beginFileLease`. Append calls perform a retry loop around `namenode.append` for short-lived `RetriableException`s, create an append stream from the returned last block/status, then begin lease renewal.

Close and lease renewal are coupled. `renewLease` renews the NameNode lease for the current client and namespaces and aborts all open files if the hard lease limit has elapsed. `close()` closes all open output streams, marks the client stopped, unreferences `ClientContext` unless disabled for tests, and stops the NameNode proxy.

## State and Persistence
Most durable filesystem state lives in the NameNode or DataNodes, not in this object. Local mutable state includes `clientRunning`, `lastLeaseRenewal`, `filesBeingWritten`, cached `FsServerDefaults`, cached `DataEncryptionKey`, default caching strategies, local interface addresses, and `ClientContext` references. `filesBeingWritten` is synchronized and drives lease renewer lifecycle. `serverDefaults` is refreshed after `serverDefaultsValidityPeriod`; `encryptionKey` is refreshed when absent or expired. Hedged-read metrics and hedged/striped thread pools are static and therefore shared process-wide across clients.

## Dependencies and Integration Points
`DFSClient` integrates with NameNode RPC through `ClientProtocol`, data-transfer protocol through `Peer`, `Sender`, `BlockReaderFactory`-related callers, `DFSUtilClient.connectToDN`, and SASL helpers. It integrates with KMS through `HdfsKMSUtil` and `KeyProviderCache`, with tracing through `FsTracer`, with HA and delegation-token renewal through `HAUtilClient`, `NameNodeProxiesClient`, and the nested `Renewer`, and with read-side health management through `DeadNodeDetector` and `LocatedBlocksRefresher` stored in `ClientContext`. `DistributedFileSystem` and `WebHdfsFileSystem` sit above it and also use `DFSOpsCountStatistics` for operation counters.

## Risks
The class has broad surface area, so exception translation drift is a regression risk when new NameNode exceptions are introduced. Static hedged and striped read pools mean the first client configuration can influence later clients in the same JVM. Lease renewal correctness depends on synchronized updates to `filesBeingWritten`; missed `endFileLease` or close failures can leave leases active until recovery. Cached server defaults and encryption keys improve performance but can be stale during NameNode/KMS transitions. Dead-node and block-refresh behavior depends on shared `ClientContext`, so close/unreference and test-only disabling need careful coverage. The global `DFSClientFaultInjector` can leak between tests if not restored.

## Test Signals
Relevant tests include `TestPread` for hedged-read behavior and metrics, `TestRead` and `TestDFSInputStream` for read retry/fault injection paths, `TestDeadNodeDetection` for shared dead-node detector lifecycle, `TestLocatedBlocksRefresher` and `TestDFSInputStreamBlockLocations` for block refresh behavior, `TestDFSInotifyEventInputStream` for inotify exposure through `getInotifyEventStream`, `TestDistributedFileSystem` for closed-client checks and operation statistics, and token/encryption tests such as `TestSaslDataTransferExpiredBlockToken`. Lease and pipeline recovery paths use `DFSClientFaultInjector` in `TestClientProtocolForPipelineRecovery`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSClientFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSClientFaultInjector.java

## Purpose
`DFSClientFaultInjector` is a private, visible-for-testing singleton that provides no-op production hooks for injecting failures or delays into HDFS client read, write, lease, packet, and block-reader paths.

## Important APIs, Types, and Functions
The class exposes static `get()` and `set()` for replacing the singleton, plus a public static `AtomicLong exceptionNum` used by tests. Hook methods include `corruptPacket`, `uncorruptPacket`, `failPacket`, `startFetchFromDatanode`, `fetchFromDatanodeException`, `readFromDatanodeDelay`, `skipRollingRestartWait`, `sleepBeforeHedgedGet`, `delayWhenRenewLeaseTimeout`, `onCreateBlockReader`, `failCreateBlockReader`, and `failWhenReadWithStrategy`.

## Control Flow
Production execution calls these methods at predefined points and gets default no-op or `false` behavior. Tests replace the singleton with a subclass or Mockito mock, then force behavior such as invalid block-token failures, delayed hedged reads, packet corruption, block-reader creation failures, or lease-renewal timing changes. Because all hooks are methods on one global instance, a test must restore the old injector after use.

## State and Persistence
The only persistent state is process-local: the static singleton and `exceptionNum`. There is no synchronization around `set()`, so safe use assumes tests serialize or restore it carefully. No filesystem or NameNode state is stored here.

## Dependencies and Integration Points
Call sites include `DFSPacket` packet corruption/failure paths, `DFSInputStream` block-reader creation and datanode read paths, `DFSStripedInputStream` striped reader hooks, `BlockReaderFactory` read strategy hooks, and `LeaseRenewer` timeout delay hooks. The method signatures depend on `LocatedBlock` and `InvalidBlockTokenException` so tests can emulate data-transfer token failures precisely.

## Risks
The global mutable singleton is easy to leak across tests and can make concurrent tests interfere with each other. Adding a new production hook without a default no-op would make tests brittle. Hook methods that throw checked exceptions must preserve the exact production exception type expected by retry logic; otherwise tests can validate unrealistic paths.

## Test Signals
`TestPread`, `TestRead`, `TestDFSInputStream`, `TestDFSStripedInputStream`, `TestClientProtocolForPipelineRecovery`, `TestCrcCorruption`, `TestDFSClientRetries`, and `TestPipelineCloseRecoveryByteArrayLeak` all replace or mock this injector. Coverage signals should include restoration of the previous singleton in `finally` blocks and assertions that injected delays/failures drive the intended retry, hedged-read, or recovery branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSClientFaultInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSHedgedReadMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSHedgedReadMetrics.java

## Purpose
`DFSHedgedReadMetrics` is a small private metrics holder for HDFS client hedged reads. It tracks how often a hedged read is launched, how often a hedged request wins, and how often the hedged-read executor rejects work and runs it in the caller thread.

## Important APIs, Types, and Functions
The class contains three public `LongAdder` fields: `hedgedReadOps`, `hedgedReadOpsWin`, and `hedgedReadOpsInCurThread`. It exposes increment methods `incHedgedReadOps`, `incHedgedReadOpsInCurThread`, and `incHedgedReadWins`, plus getters returning `long` snapshots.

## Control Flow
`DFSClient` owns one static instance and exposes it through `getHedgedReadMetrics()`. `DFSInputStream.hedgedFetchBlockByteRange` increments `hedgedReadOps` when the first positional read exceeds the hedged-read threshold and a parallel attempt is launched. It increments `hedgedReadOpsWin` when one hedged future completes and the remaining futures are canceled. `DFSClient` increments `hedgedReadOpsInCurThread` from the hedged-read thread pool rejection handler when executor saturation causes caller-runs fallback.

## State and Persistence
All counters are in-memory process metrics. `LongAdder` makes concurrent increments cheap and thread-safe, but the counters are not persisted and are shared through the static `DFSClient` metric instance. Tests can reset the public adders directly.

## Dependencies and Integration Points
The main integration points are `DFSClient.initThreadsNumForHedgedReads`, `DFSInputStream.hedgedFetchBlockByteRange`, `DistributedFileSystem.getHedgedReadMetrics`, and tests in `TestPread`. The class intentionally avoids Hadoop metrics-system dependencies and is directly accessible to client-side consumers such as HBase.

## Risks
Because fields are public, external code and tests can reset or mutate counters at any time. Since the `DFSClient` instance is static, metrics combine all clients in the JVM and do not distinguish files, clusters, users, or nameservices. `LongAdder.longValue()` is a weakly consistent snapshot under concurrent updates, which is acceptable for metrics but not for exact accounting.

## Test Signals
`TestPread` resets the adders and verifies hedged-read launches, wins, and caller-thread fallback under delayed reads and constrained pools. Good regression tests should assert counter changes only around controlled hedged-read scenarios and should avoid assuming global counters start at zero unless they reset them first.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSHedgedReadMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSInotifyEventInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSInotifyEventInputStream.java

## Purpose
`DFSInotifyEventInputStream` is the client-side stream for reading HDFS edit-log-derived inotify event batches from the NameNode. It is public but unstable and explicitly not intended to be shared by multiple threads.

## Important APIs, Types, and Functions
The stream holds a `ClientProtocol namenode`, current iterator of `EventBatch`, `lastReadTxid`, `syncTxid`, random backoff generator, and `Tracer`. Constructors either start from the NameNode current edit-log txid or from a caller-supplied last-read txid. Public methods are `poll()`, `poll(long, TimeUnit)`, `take()`, and `getTxidsBehindEstimate()`.

## Control Flow
`poll()` opens an `inotifyPoll` trace scope. If `lastReadTxid` is `-1`, it initializes from `namenode.getCurrentEditLogTxid()` and returns null. When the current batch iterator is empty, it calls `namenode.getEditsFromTxid(lastReadTxid + 1)`. If the NameNode returns edits, it updates `syncTxid`, replaces the iterator, advances `lastReadTxid` to the returned last txid, and throws `MissingEventsException` if the first returned txid does not immediately follow the previous one. It then returns the next converted event batch or null when no edit op converted to an event.

`poll(timeout)` repeatedly calls `poll()` with exponential sleep starting at 10 ms until an event arrives or the timeout expires. `take()` repeats indefinitely and sleeps for a randomized interval between `nextWaitMin` and `2 * nextWaitMin`, doubling up to a 60 second minimum window to avoid synchronized client polling.

## State and Persistence
The stream persists only its in-memory cursor (`lastReadTxid`) and lag estimate basis (`syncTxid`). The NameNode edit log is the durable source. `getTxidsBehindEstimate()` returns `-1` until at least one successful event fetch supplied a synced txid; otherwise it returns `syncTxid - lastReadTxid`.

## Dependencies and Integration Points
`DFSClient.getInotifyEventStream()` and `DistributedFileSystem.getInotifyEventStream()` construct this class. It depends on `ClientProtocol.getCurrentEditLogTxid` and `getEditsFromTxid`, inotify model classes `EventBatch`, `EventBatchList`, and `MissingEventsException`, and Hadoop tracing/time utilities.

## Risks
The class is not synchronized, so concurrent callers can corrupt iterator and txid state. Timeout waits can exceed the requested timeout by one NameNode RPC duration. If a client falls behind far enough that edit-log data is no longer available, `MissingEventsException` is expected and callers must decide how to resynchronize. The lag estimate is approximate and only updates after successful edit reads, so it should not be treated as exact monitoring data.

## Test Signals
`TestDFSInotifyEventInputStream` covers event delivery across filesystem operations, restart/upgrade cases use `TestDFSUpgradeFromImage`, and `TestDFSInotifyEventInputStreamKerberized` covers secure clusters. `TestDistributedFileSystem` verifies closed-client behavior for inotify stream creation. Important assertions include txid ordering, missing-event behavior, timeout/take behavior, and Kerberos access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSInotifyEventInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSInputStream.java

## Purpose
`DFSInputStream` is the replicated-file HDFS input stream. It resolves file blocks through `DFSClient`, chooses DataNodes, builds `BlockReader`s, performs sequential and positional reads, handles retry/token/encryption refresh, reports checksum failures, tracks read statistics, supports zero-copy reads, and participates in dead-node detection and located-block refresh.

## Important APIs, Types, and Functions
The class extends `FSInputStream` and implements `ByteBufferReadable`, `ByteBufferPositionedReadable`, `CanSetDropBehind`, `CanSetReadahead`, `CanUnbuffer`, `HasEnhancedByteBufferAccess`, and `StreamCapabilities`. Key state is split between synchronized stateful-read fields (`currentNode`, `currentLocatedBlock`, `pos`, `blockEnd`, `blockReader`) and `infoLock`-protected shared fields (`locatedBlocks`, `lastBlockBeingWrittenLength`, `fileEncryptionInfo`, `cachingStrategy`, `lastRefreshedBlocksAt`). It also keeps per-stream `ReadStatistics`, local dead nodes, failure count, and tracked zero-copy buffers.

Important methods include `openInfo`, `fetchAndCheckLocatedBlocks`, `getLastBlockLength`, `readBlockLength`, `getBlockAt`, `fetchBlockAt`, `getBlockRange`, `blockSeekTo`, `getBlockReader`, `readWithStrategy`, `pread`, `fetchBlockByteRange`, `actualGetFromOneDataNode`, `hedgedFetchBlockByteRange`, `reportCheckSumFailure`, `seek`, `seekToNewSource`, zero-copy `read(ByteBufferPool, int, EnumSet<ReadOption>)`, `releaseBuffer`, and `refreshBlockLocations`.

## Control Flow
Construction stores the provided initial `LocatedBlocks`, applies the default read caching strategy, and calls `openInfo(false)`. `openInfo` ensures block metadata is current and, for an under-construction last block, asks DataNodes for visible replica length with bounded retries. `fetchAndCheckLocatedBlocks` rejects block-list changes compared with an existing list.

Sequential reads call `readWithStrategy`, which checks client/stream state, registers for block refresh if needed, seeks to a block when the cursor is past `blockEnd` or no current node exists, reads through the current `BlockReader`, advances `pos`, updates read statistics, and reports checksum failures. On failures it retries the current node once for transient read errors, otherwise marks nodes dead and seeks a new source.

Positioned reads call `pread`, clamp length to EOF, map the range to `LocatedBlock`s, and read each block either through normal `fetchBlockByteRange` or through `hedgedFetchBlockByteRange` when hedged reads are enabled and the block is not striped. Hedged reads submit one read, wait for the configured threshold, submit reads to other DataNodes if needed, accept the first successful future, and cancel the rest without interrupting running HDFS reads.

`blockSeekTo` resolves the target block, chooses a valid DataNode, and constructs a `BlockReader`. It refreshes an encryption key once for `InvalidEncryptionKeyException`, refetches a block token once for token failures, and otherwise marks failed nodes dead before trying another. Zero-copy reads try `BlockReader.getClientMmap` when short-circuit mmap is enabled, fall back to pooled ByteBuffer reads, and require callers to return buffers through `releaseBuffer`.

## State and Persistence
The stream owns only client-side mutable read state; file data and block metadata persist in HDFS. `locatedBlocks` is a cache refreshed by explicit fetches or by `LocatedBlocksRefresher`. Dead nodes are tracked locally and can be merged with `DFSClient`'s shared `DeadNodeDetector`. `extendedReadBuffers` tracks outstanding buffers by identity so `close()` can warn about leaks and `releaseBuffer()` can return pooled buffers or close mmaps. Caching strategy changes close the current block reader so new settings take effect.

## Dependencies and Integration Points
The stream depends on `DFSClient` for configuration, NameNode block locations, data-transfer peer creation, stats, dead-node detector, block refresher, and checksum failure reporting. Data-node access goes through `BlockReaderFactory`, `ClientDatanodeProtocol` for visible length, `Token<BlockTokenIdentifier>`, `CachingStrategy`, `StorageType`, and `DFSUtilClient` helpers. Higher-level users receive it through `DFSClient.open` unless erasure coding selects `DFSStripedInputStream`.

## Risks
Lock ordering is delicate: comments require avoiding acquisition of `this` while holding `infoLock`, and block refresh can re-enter seek logic. `deadNodes` uses a concurrent map as a temporary parallel-access mitigation, so positioned reads and sequential reads still need careful concurrency testing. Hedged reads allocate per-attempt ByteBuffers and cancel without interruption, which avoids noisy partial-read errors but can leave background reads running briefly. Stale block tokens, encryption keys, or located blocks must be refreshed exactly once per failure class before failing over. Zero-copy callers that forget `releaseBuffer` can retain mmap resources until close. Under-construction block length handling depends on DataNode reports and retry timing.

## Test Signals
`TestPread` exercises positional reads, hedged reads, delayed reads, metrics, and fault injection. `TestRead`, `TestDFSInputStream`, and `TestDFSInputStreamBlockLocations` cover read retry behavior, block-location refresh, and local/remote block decisions. `TestLocatedBlocksRefresher` covers refresher registration/deregistration. `TestDeadNodeDetection` validates local and shared dead-node handling. Checksum and corruption paths are covered by `TestCrcCorruption`; token refresh and SASL interactions are covered by data-transfer token tests such as `TestSaslDataTransferExpiredBlockToken`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSOpsCountStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSOpsCountStatistics.java

## Purpose
`DFSOpsCountStatistics` is the HDFS implementation of `StorageStatistics` for counting how many times each distributed filesystem operation is issued by HDFS clients.

## Important APIs, Types, and Functions
The nested `OpType` enum defines the tracked operations and their stable string symbols, such as `op_create`, `op_open`, `op_get_file_status`, snapshot operations, cache operations, xattr operations, storage policy operations, erasure-coding operations, and quota operations. `OpType.fromSymbol` maps a symbol back to an enum through a static `HashMap`. The class name exported to global storage statistics is `DFSOpsCountStatistics`. Counters are held in an `EnumMap<OpType, LongAdder>`.

The public surface is `incrementOpCounter(OpType)`, `getScheme()`, `getLongStatistics()`, `getLong(String)`, `isTracked(String)`, and `reset()`. The private `LongIterator` adapts the enum map entries to `StorageStatistics.LongStatistic`.

## Control Flow
Construction initializes one `LongAdder` per enum value. Filesystem front-ends call `incrementOpCounter` immediately around operations. Consumers iterate `getLongStatistics()` to see all counters, call `getLong(symbol)` for a single counter, or call `isTracked(symbol)` to validate a key. `reset()` resets every `LongAdder`.

## State and Persistence
All state is in-memory and thread-safe through `LongAdder`. Counters are process-local and reset when the `StorageStatistics` instance is reset or the JVM exits. There is no persistence to HDFS, logs, or metrics files in this class.

## Dependencies and Integration Points
The class extends `org.apache.hadoop.fs.StorageStatistics` and reports the HDFS scheme through `HdfsConstants.HDFS_URI_SCHEME`. `DistributedFileSystem` and `WebHdfsFileSystem` obtain/register this statistic in `GlobalStorageStatistics` and increment matching `OpType`s for their public filesystem methods. External callers can inspect it through Hadoop filesystem statistics APIs.

## Risks
Every new user-visible DFS operation needs a matching enum value and increments in all relevant filesystem front-ends; otherwise statistics silently undercount. Symbol strings are external-facing and must remain unique and stable. `LongAdder` snapshots are weakly consistent under concurrent updates, suitable for metrics but not exact transactional accounting. The enum contains historical spelling/casing in symbols such as `op_set_storagePolicy` and `op_set_quota_bystoragetype`, so cleanup refactors could break consumers.

## Test Signals
`TestDFSOpsCountStatistics` verifies symbol uniqueness, iteration across all enum values, `getLong`, `isTracked`, `reset`, and concurrent increments. `TestDistributedFileSystem` and WebHDFS tests assert that higher-level operations increment selected counters in integrated filesystem flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSOpsCountStatistics.java -->
