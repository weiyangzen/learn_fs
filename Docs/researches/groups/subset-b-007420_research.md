# Research: subset-b-007420

This grouped report covers the Hadoop HDFS client files assigned to `subset-b-007420`. Each section preserves the original source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DeadNodeDetector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DeadNodeDetector.java

## Purpose
`DeadNodeDetector` is a client-side daemon that proactively probes DataNodes considered suspect or dead by `DFSInputStream` instances sharing the same DFS client context. Its output is a shared `deadNodes` map keyed by DataNode UUID, letting multiple input streams avoid repeatedly selecting unhealthy replicas while still removing nodes that later respond successfully.

## Important APIs, Types, And Functions
The class extends `Daemon` and exposes `addNodeToDetect(DFSInputStream, DatanodeInfo)`, `isDeadNode(DatanodeInfo)`, `clearAndGetDetectedDeadNodes()`, `removeNodeFromDeadNodeDetector(DFSInputStream, DatanodeInfo)`, `shutdown()`, testing hooks for scheduler disabling and queue injection, and queue accessors. Internal types include `ProbeType` (`CHECK_DEAD`, `CHECK_SUSPECT`), state enum `INIT`, `CHECK_DEAD`, `IDLE`, `ERROR`, `UniqueQueue<T>` for de-duplicated scheduling, `Probe` for RPC liveness checks, and `ProbeScheduler` for periodic queue draining.

## Control Flow
Construction copies configuration, initializes concurrent maps and fixed daemon thread pools, creates dead/suspect probe queues, reads detection intervals and timeouts, and starts scheduler threads unless tests disable them. `work()` loops until interrupted, refreshes/prunes the shared dead-node set, then transitions from `INIT` to `CHECK_DEAD` to `IDLE`. `checkDeadNodes()` queues currently known dead nodes for re-probe. Separate scheduler threads repeatedly call `scheduleProbe()` for dead or suspect queues, which drains each `UniqueQueue`, avoids duplicate probes via `probeInProg`, and submits `Probe` tasks.

Each `Probe` creates a `ClientDatanodeProtocol` proxy, submits `getDatanodeInfo()` to a bounded RPC pool, waits for `probeConnectionTimeoutMs`, cancels the future, and calls `probeCallBack()`. Successful dead probes remove the node from global and per-stream dead/suspect tracking. Successful suspect probes remove the node from all stream-local local-dead sets. Failed suspect probes promote the node into `deadNodes`; failed dead probes leave it dead.

## State And Persistence Behavior
All state is in-memory and scoped to one client context: `deadNodes`, `suspectAndDeadNodes`, `probeInProg`, two queues, scheduler threads, and pools. `suspectAndDeadNodes` maps live `DFSInputStream` objects to their suspect/dead DataNodes and is used to prune `deadNodes` when no stream still references a node. No durable persistence exists.

## Dependencies And Integration Points
It integrates with `DFSInputStream` for local-dead-node removal, `DFSUtilClient.createClientDatanodeProtocolProxy()` for DataNode RPC, `ClientDatanodeProtocol.getDatanodeInfo()` for liveness, HDFS client config keys for intervals and pool sizes, `SubjectInheritingThread` for scheduler identity, and `Daemon.DaemonFactory` for worker pools.

## Risks And Edge Cases
The code synchronizes map mutations around `suspectAndDeadNodes`, but it removes entries from `ConcurrentHashMap` while iterating, so behavior relies on weakly consistent iteration. `UniqueQueue.poll()` removes `null` from its set if the queue is empty, which is harmless but worth noting. Timeout paths call `future.cancel(true)`, but an underlying stuck DataNode RPC may still consume resources until the RPC layer reacts. Shutdown interrupts and joins scheduler/daemon threads, but only calls `shutdown()` on executor services, not `shutdownNow()`. Liveness depends on DataNode UUID stability.

## Test Signals
Useful tests should cover duplicate queue suppression, suspect promotion to dead on probe failure, dead removal on successful re-probe, pruning when streams unregister nodes, scheduler disabling for deterministic unit tests, interruption/shutdown, and timeouts that do not block subsequent probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DeadNodeDetector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DistributedFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DistributedFileSystem.java

## Purpose
`DistributedFileSystem` is the public Hadoop `FileSystem` implementation for the `hdfs://` scheme. It translates generic filesystem APIs and HDFS-specific extension APIs into `DFSClient` calls, while handling path qualification, symlink resolution, operation statistics, delegation-token service identity, snapshots, encryption zones, erasure coding, storage policies, cache administration, ACLs, xattrs, trash-root selection, and builders for HDFS output streams.

## Important APIs, Types, And Functions
Core lifecycle and identity methods include `initialize()`, `initDFSClient()`, `getScheme()`, `getUri()`, `getWorkingDirectory()`, `setWorkingDirectory()`, `getHomeDirectory()`, `getPathName()`, `close()`, `getClient()`, and `canonicalizeUri()`. Standard filesystem operations include `open()`, `create()`, `append()`, `rename()`, `delete()`, `truncate()`, `listStatus()`, `listLocatedStatus()`, `listStatusIterator()`, `batchedListStatusIterator()`, `mkdirs()`, `getFileStatus()`, `getFileChecksum()`, permissions, owners, times, ACLs, xattrs, and access checks.

HDFS-only surfaces include lease recovery, safe mode, namespace save/roll, datanode and block health reports, storage policies, snapshots and snapshot diff listing, cache directives/pools, encryption zones and re-encryption status, KMS token issuer methods, erasure coding policy management, inotify streams, open-file listing, slow DataNode reports, `getLocatedBlocks()`, and `getEnclosingRoot()`. Inner classes `DirListingIterator`, `PartialListingIterator`, `SnapshotDiffReportListingIterator`, and `HdfsDataOutputStreamBuilder` implement incremental listing, batched listing, snapshot diff iteration, and create/append builder behavior.

## Control Flow
`initialize()` validates that the URI has a host, creates a `DFSClient`, stores a normalized scheme/authority URI, sets the working directory to the HDFS home directory, and registers `DFSOpsCountStatistics`. Most public methods increment `FileSystem.Statistics` plus `DFSOpsCountStatistics`, call `fixRelativePart()`, and resolve symlinks through `FileSystemLinkResolver`. The resolver's `doCall()` path invokes `DFSClient` directly with `getPathName()`, while `next()` delegates to the target filesystem or rejects cross-filesystem symlinks for HDFS-only operations.

Create and append methods funnel into `DFSClient.create()`/`append()` and wrap `DFSOutputStream` through `safelyCreateWrappedOutputStream()`, closing the inner stream if wrapping fails. Directory listing either fetches all batches into an array (`listStatusInternal`) or exposes lazy iterators that request further `DirectoryListing`/`BatchedDirectoryListing` batches only when needed. Snapshot diff remote iteration repeatedly calls `dfs.getSnapshotDiffReportListing()` using returned cursor state.

## State And Persistence Behavior
Instance state is limited to `workingDir`, normalized `uri`, `DFSClient dfs`, `verifyChecksum`, and `DFSOpsCountStatistics`. File metadata, blocks, snapshots, encryption zones, cache directives, quotas, and policies are persisted by NameNode/DataNode services behind `DFSClient`, not by this facade. Some method calls change durable HDFS namespace state, while builder options such as favored nodes are request-time hints and are not persisted.

## Dependencies And Integration Points
The class depends heavily on `DFSClient`, HDFS protocol records, `FileSystemLinkResolver`, `FSLinkResolver`, `GlobalStorageStatistics`, `HAUtilClient`, `DfsPathCapabilities`, KMS/KeyProvider interfaces, snapshot/cache/EC/storage-policy protocol classes, and Hadoop security tokens. It is the integration point used by user code, MapReduce, HBase, `HdfsAdmin`, trash handling, and higher-level filesystem APIs.

## Risks And Edge Cases
The file is a broad facade, so regressions often come from inconsistent symlink semantics, missing statistics increments, or mismatches between generic `FileSystem` contracts and HDFS-only behavior. Some `next()` branches intentionally reject non-DFS symlink targets; tests need to lock those failure modes. Trash-root selection swallows several IO failures and falls back to the user's normal trash root, so operational errors may only be logged. Snapshot and encryption trash provisioning must handle existing `.Trash` paths that are files or have wrong permissions. `HdfsDataOutputStreamBuilder` must reject missing create/append flags and avoid conflicting EC replication settings. `createPathHandle()` enforces HDFS status type, non-directory/non-symlink inputs, matching authority, and requested data/location constraints.

## Test Signals
High-value tests include symlink resolution for each operation family, lazy and batched listing cursor behavior, safe stream cleanup on wrap failure, create/append builder flags and HDFS-specific options, path handle validation, trash-root selection across normal, EZ, and snapshottable directories, snapshot diff pagination, ACL/xattr delegation, EC/storage policy calls, HA logical URI canonicalization, statistics counters, and close semantics for open output streams and the underlying `DFSClient`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DistributedFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ExceptionLastSeen.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ExceptionLastSeen.java

## Purpose
`ExceptionLastSeen` is a small package-private synchronization helper used by HDFS write-path classes such as `DataStreamer` and `DFSOutputStream` to remember the latest failure and rethrow it from later control points.

## Important APIs, Types, And Functions
The class stores one `IOException thrown`. `get()` returns the current value, `set(Throwable)` records an `IOException` directly or wraps any other `Throwable` in an `IOException`, `clear()` removes it, `check(boolean resetToNull)` throws the stored exception and optionally clears it first, and `throwException4Close()` throws the stored exception if present or otherwise throws `ClosedChannelException`.

## Control Flow
Producers call `set()` when a background streamer or output stream encounters an error. Foreground operations call `check()` to fail promptly using the earlier exception. Close paths call `throwException4Close()` to prefer a real prior error and fall back to closed-channel semantics.

## State And Persistence Behavior
The helper has only in-memory state. Every accessor and mutator is synchronized on the instance, providing simple visibility and atomicity for background/foreground write-path coordination.

## Dependencies And Integration Points
It depends only on `IOException` and `ClosedChannelException`, but its semantic integration is with asynchronous HDFS output components that need to bridge background failures to user-facing calls.

## Risks And Edge Cases
`set()` asserts non-null but assertions are usually disabled at runtime; a null argument would be wrapped as `new IOException((Throwable) null)`. `check(false)` leaves the exception sticky, so repeated callers will observe the same failure. `throwException4Close()` always throws.

## Test Signals
Tests should cover wrapping non-IO throwables, optional reset behavior, sticky errors, `clear()`, and close behavior with and without a prior stored exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ExceptionLastSeen.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ExtendedBlockId.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ExtendedBlockId.java

## Purpose
`ExtendedBlockId` is an immutable key for identifying an HDFS block by the pair of block ID and block pool ID. It is useful wherever a stable map/set key is needed without carrying the full mutable `ExtendedBlock` object.

## Important APIs, Types, And Functions
The final public class exposes `fromExtendedBlock(ExtendedBlock)`, a constructor accepting `long blockId` and `String bpId`, getters for both fields, and overrides for `equals()`, `hashCode()`, and `toString()`. Equality requires the same runtime class and identical block ID and pool ID.

## Control Flow
There is no complex flow. Callers either build an instance directly or extract it from an `ExtendedBlock`; Java collections then use the Apache Commons `EqualsBuilder` and `HashCodeBuilder` implementations.

## State And Persistence Behavior
Both fields are final and no mutation is available. No durable persistence exists; the `toString()` shape is `blockId_bpId` and should be treated as diagnostic rather than a parser contract unless callers explicitly rely on it.

## Dependencies And Integration Points
It depends on `org.apache.hadoop.hdfs.protocol.ExtendedBlock` and Apache Commons Lang builder utilities. It integrates with block caches or maps that need a compact identity key across block pools.

## Risks And Edge Cases
The constructor does not validate `bpId`; a null pool ID is accepted and handled by the builder utilities. Equality rejects subclasses by class equality rather than `instanceof`, which is consistent with final class behavior.

## Test Signals
Tests should verify conversion from `ExtendedBlock`, equality and hash behavior for same/different block IDs and pool IDs, null pool IDs if supported by callers, and the diagnostic string format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ExtendedBlockId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/FileChecksumHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/FileChecksumHelper.java

## Purpose
`FileChecksumHelper` contains package-private strategy classes that compute HDFS file checksums for replicated and striped files. It supports legacy MD5-of-block-CRC checksums and composite CRC checksums, using NameNode block locations and DataNode checksum RPCs.

## Important APIs, Types, And Functions
The abstract `FileChecksumComputer` owns common input and accumulated state: source path, requested length, `DFSClient`, `ClientProtocol`, `ChecksumCombineMode`, derived `BlockChecksumType`, `DataOutputBuffer`, located blocks, remaining length, checksum properties, and retry bookkeeping. Its main methods are `compute()`, `checksumBlocks()`, `makeFinalResult()`, `makeMd5CrcResult()`, `makeCompositeCrcResult()`, `refetchBlocks()`, `extractChecksumProperties()`, and `populateBlockChecksumBuf()`.

`ReplicatedFileChecksumComputer` iterates individual replicated `LocatedBlock`s and issues `Sender.blockChecksum()`. `StripedFileNonStripedChecksumComputer` iterates `LocatedStripedBlock` block groups, builds `StripedBlockInfo`, and issues `Sender.blockGroupChecksum()`.

## Control Flow
Construction chooses `MD5CRC` or `COMPOSITE_CRC` based on `ChecksumCombineMode`, initializes remaining length, and adopts provided located blocks. `compute()` returns the historical empty-file checksum for no blocks; otherwise it delegates block traversal to the subclass and builds the final checksum. Replicated traversal adjusts the last block length to the requested remaining range, tries each DataNode location until one succeeds, and retries one time per block on invalid block token by refetching block locations or on invalid encryption key by clearing the cached data encryption key. Striped traversal uses similar retry logic per block group and passes requested byte length for the group.

## State And Persistence Behavior
All computation state is per-object and in-memory. It mutates the `ExtendedBlock` byte length for partial last-block checksum requests, accumulates raw per-block checksum bytes in `blockChecksumBuf`, and may refresh block tokens/locations from the client. It does not persist results beyond returning a `FileChecksum`.

## Dependencies And Integration Points
It integrates with `DFSClient` for block locations, DataNode connections, timeouts, encryption-key clearing, and checksum inference; `ClientProtocol` for NameNode context; DataTransfer protocol `Sender`; `PBHelperClient`; `DataTransferProtoUtil`; checksum classes such as `MD5MD5CRC32GzipFileChecksum`, `MD5MD5CRC32CastagnoliFileChecksum`, `CompositeCrcFileChecksum`; and erasure coding records including `ErasureCodingPolicy`, `LocatedStripedBlock`, and `StripedBlockInfo`.

## Risks And Edge Cases
Mixed CRC types are allowed only for MD5MD5CRC mode by marking type `MIXED`; composite CRC rejects mixed types. Composite mode tolerates differing bytes-per-CRC with a warning but preserves the first value. Empty files always return the legacy gzip checksum shape, regardless of combine mode. The buffer uses `DataOutputBuffer.getData()`, which may be larger than written bytes; code reads by expected index. Retrying decrements the loop index and depends on `lastRetriedIndex` to prevent infinite retry. Partial checksums and snapshot paths alter `remaining`, so off-by-one errors would change final digest compatibility.

## Test Signals
Tests should cover empty files, one-block and multi-block replicated files, partial length checksums, token refetch retry, encryption-key retry, all DataNodes failing, composite CRC composition and last-block length, mixed CRC behavior, striped block group checksums, and older DataNode replies without explicit CRC type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/FileChecksumHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HAUtilClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HAUtilClient.java

## Purpose
`HAUtilClient` provides client-side helpers for HDFS high availability logical URIs and delegation-token service names. It lets clients distinguish logical nameservices from physical NameNode addresses and clone HA delegation tokens for concrete NameNode endpoints.

## Important APIs, Types, And Functions
Key methods are `isLogicalUri(Configuration, URI)`, `isClientFailoverConfigured(Configuration, URI)`, `buildTokenServiceForLogicalUri(URI, String)`, `buildTokenServicePrefixForLogicalUri(String)`, `getServiceUriFromToken(String, Token<?>)`, `isTokenForLogicalUri(Token<?>)`, and `cloneDelegationTokenForLogicalUri(UserGroupInformation, URI, Collection<InetSocketAddress>)`.

## Control Flow
Logical URI detection compares the URI host against configured nameservice IDs. Failover configuration checks for the per-host failover proxy provider key. Token-service construction prefixes the scheme-specific logical host with the HA delegation-token prefix. Token URI parsing strips that prefix if present and constructs a filesystem URI. Token cloning selects a logical HA token from the user's credentials, privately clones it for every physical NameNode address using `SecurityUtil.buildTokenService()`, and stores each clone under an alias designed to keep physical clones from normal credential propagation.

## State And Persistence Behavior
The class has no mutable persistent state beyond a static `DelegationTokenSelector`. `cloneDelegationTokenForLogicalUri()` mutates the supplied `UserGroupInformation` credentials by adding private alias tokens.

## Dependencies And Integration Points
It depends on `DFSUtilClient` nameservice discovery, `HdfsClientConfigKeys.Failover`, `HdfsConstants.HA_DT_SERVICE_PREFIX`, `DelegationTokenSelector`, `UserGroupInformation`, and Hadoop token service utilities. `DistributedFileSystem` uses it to avoid DNS canonicalization for logical URIs, and proxy creation uses its token-service helpers.

## Risks And Edge Cases
URI host matching means malformed or hostless URIs are not logical. Cloning only happens when a logical token is already present; missing tokens are only logged. The alias string includes `//` plus the physical token service, so consumers must use the same private alias convention.

## Test Signals
Tests should cover nameservice-host detection, configured failover provider detection, logical service string shape by scheme, parsing logical and physical token services, and cloning behavior for multiple NameNodes with and without a source HA token.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HAUtilClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsConfiguration.java

## Purpose
`HdfsConfiguration` is the HDFS-specific `Configuration` subclass responsible for registering HDFS default resources and deprecated key mappings in the correct order.

## Important APIs, Types, And Functions
It has constructors mirroring `Configuration`, a static initializer, `init()`, `addDeprecatedKeys()`, and a `main()` that dumps deprecated keys. `init()` is intentionally empty and exists to trigger class loading.

## Control Flow
When the class loads, it calls `addDeprecatedKeys()` and then adds `hdfs-default.xml`, `hdfs-rbf-default.xml`, `hdfs-site.xml`, and `hdfs-rbf-site.xml` as default resources. The deprecation list maps older HDFS keys such as `dfs.http.address`, `dfs.socket.timeout`, `dfs.block.size`, and `dfs.encryption.key.provider.uri` to current client/server key constants.

## State And Persistence Behavior
Class loading mutates global `Configuration` static registries for default resources and deprecation deltas. Instances are ordinary mutable `Configuration` objects. No repository or external persistent state is written.

## Dependencies And Integration Points
It depends on `HdfsClientConfigKeys`, `DeprecatedKeys`, and core Hadoop configuration classes. Many HDFS client classes call `HdfsConfiguration.init()` in static blocks to ensure defaults and key translations are registered before configuration lookup.

## Risks And Edge Cases
The static initializer runs once per classloader, so tests that depend on isolated deprecation state need classloader isolation or cleanup. Ordering matters: deprecations must be registered before defaults are loaded. Missing new deprecated mappings can silently break compatibility for old configuration files.

## Test Signals
Tests should verify class-loading through `init()`, presence of expected HDFS resources, old-to-new key translation for representative keys, constructor behavior with and without defaults, and `main()` dump execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsKMSUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsKMSUtil.java

## Purpose
`HdfsKMSUtil` centralizes HDFS client key-provider and encryption stream helper logic. It resolves KMS provider URIs, validates crypto metadata, obtains codecs, decrypts encrypted data encryption keys, and wraps encrypted file input streams.

## Important APIs, Types, And Functions
Public methods include `createKeyProvider(Configuration)`, `getCryptoProtocolVersion(FileEncryptionInfo)`, `getCryptoCodec(Configuration, FileEncryptionInfo)`, `getKeyProviderUri(UserGroupInformation, URI, String, Configuration)`, `getKeyProvider(KeyProviderTokenIssuer, Configuration)`, `getKeyProviderMapKey(URI)`, and `createWrappedInputStream(InputStream, KeyProvider, FileEncryptionInfo, Configuration)`. Package-visible `decryptEncryptedDataEncryptionKey()` performs the KMS decrypt.

## Control Flow
Provider creation delegates to `KMSUtil` using `hadoop.security.key.provider.path`. Provider URI resolution first checks the UGI credentials secret keyed by the NameNode URI, then optionally accepts the NameNode-provided default KMS URI unless configured to ignore it, then falls back to local configuration. A resolved URI is cached back into credentials. Encrypted stream wrapping validates protocol support, resolves a `CryptoCodec` for the cipher suite, decrypts the EDEK through `KeyProviderCryptoExtension`, and returns a `CryptoInputStream` over the original input.

## State And Persistence Behavior
The utility has static configuration-key state and writes resolved provider URI bytes into the supplied UGI credentials. It does not persist keys or decrypted material beyond returned objects.

## Dependencies And Integration Points
It integrates with HDFS file encryption metadata (`FileEncryptionInfo`), Hadoop KMS utilities, `KeyProvider`, `KeyProviderTokenIssuer`, UGI credentials, `CryptoCodec`, `CryptoInputStream`, and HDFS `DFSUtilClient` byte/string helpers. `DFSClient` and `DistributedFileSystem` use these paths when opening encrypted files and collecting additional token issuers.

## Risks And Edge Cases
If the NameNode reports an empty KMS URI, the method falls back rather than using it. Unsupported crypto protocol versions, unknown cipher suites, missing codec classes, missing key providers, and decrypt failures are all surfaced as `IOException`. Caching provider URI in credentials means stale KMS URI data can persist for the UGI lifetime.

## Test Signals
Tests should cover credential override, NameNode default URI, ignore-NN-default configuration, local fallback, null result when no URI exists, unsupported protocol/cipher handling, missing codec errors, decrypt success/failure, and credential map key shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsKMSUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/KeyProviderCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/KeyProviderCache.java

## Purpose
`KeyProviderCache` caches `KeyProvider` instances by URI for HDFS clients, closes providers when evicted, and invalidates all providers during shutdown.

## Important APIs, Types, And Functions
The constructor accepts an expiry in milliseconds and creates a Guava cache with `expireAfterAccess`. `get(Configuration, URI)` returns a cached provider or creates one with `KMSUtil.createKeyProviderFromUri()`. `invalidateCache()` is a testing-visible synchronized invalidation hook. `setKeyProvider(Configuration, KeyProvider)` injects a provider under the configured URI for tests. `KeyProviderCacheFinalizer` is the shutdown hook. `createKeyProviderURI()` parses the configured provider path for test injection.

## Control Flow
Construction installs a removal listener that closes evicted providers and registers a shutdown hook unless shutdown is already in progress. `get()` returns null for a null server URI; otherwise it uses `cache.get()` with a `Callable` provider factory and logs/returns null on creation errors. Evictions and invalidation trigger provider close through the listener.

## State And Persistence Behavior
State is an in-memory cache from `URI` to `KeyProvider`. The cache lifetime is process-local, entries expire after access, and shutdown invalidates everything. No durable state is written.

## Dependencies And Integration Points
It depends on Hadoop's relocated Guava cache, `KMSUtil`, `ShutdownHookManager`, `FileSystem.SHUTDOWN_HOOK_PRIORITY`, and `CommonConfigurationKeysPublic.HADOOP_SECURITY_KEY_PROVIDER_PATH`. HDFS clients use it to avoid recreating KMS providers for the same URI.

## Risks And Edge Cases
`get()` swallows all provider creation exceptions and returns null, so callers must handle missing providers. The removal listener catches `Throwable` while closing providers, which prevents eviction failures from propagating. `setKeyProvider()` asserts that the configured URI exists; with assertions disabled, a null URI could be passed to `cache.put()` and fail.

## Test Signals
Tests should cover provider reuse, expiry-triggered close, explicit invalidation, null URI behavior, malformed configured URI for test injection, shutdown hook invalidation, and creation failure returning null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/KeyProviderCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/LocatedBlocksRefresher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/LocatedBlocksRefresher.java

## Purpose
`LocatedBlocksRefresher` is a client-context daemon that periodically refreshes cached `LocatedBlocks` in registered `DFSInputStream`s. It is intended for streams with dead nodes or lacking local replicas and is disabled unless the configured interval is enabled by the surrounding client configuration.

## Important APIs, Types, And Functions
The daemon exposes `addInputStream()`, `removeInputStream()`, `isInputStreamTracked()`, `shutdown()`, `getRunCount()`, `getRefreshCount()`, and `getInterval()`. Internal helpers include `waitForInterval()` and synchronized `getInputStreams()`.

## Control Flow
Construction reads the refresh interval and thread count, derives a thread-name prefix from the client context, creates a fixed daemon thread pool, and names the main daemon thread. `work()` sleeps for `interval` plus +/-10% jitter, snapshots registered streams from a weak set, and submits one refresh task per stream. A `Phaser` waits for all tasks. Each task checks the stream is still tracked and calls `DFSInputStream.refreshBlockLocations(addressCache)`, sharing an address cache for the whole pass. Run and refresh counters are updated after each pass.

## State And Persistence Behavior
State is in-memory: weakly referenced registered input streams, interval/jitter, executor, counters, and per-run address cache. `WeakHashMap` prevents the refresher from keeping abandoned streams alive. No durable persistence exists.

## Dependencies And Integration Points
It depends on `DFSInputStream.refreshBlockLocations()`, `DfsClientConf.getLocatedBlocksRefresherInterval()`, HDFS client config for thread count, `Daemon.DaemonFactory`, `Phaser`, `ThreadLocalRandom`, and `Time`. It integrates with read-path block location and dead-node recovery behavior.

## Risks And Edge Cases
`ThreadLocalRandom.current().nextLong(-jitter, jitter)` requires a positive bound range; a zero interval produces zero jitter and would be invalid if the daemon were started. The registered set is synchronized, but weak references can disappear between passes. `shutdown()` interrupts the main thread and shuts down the pool without awaiting or forcing worker termination.

## Test Signals
Tests should cover registration/removal, weak-reference behavior if practical, jittered wait interruption, refresh counting, skipped removed streams, shared address cache use, thread naming, and shutdown of main and worker threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/LocatedBlocksRefresher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/NameNodeProxiesClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/NameNodeProxiesClient.java

## Purpose
`NameNodeProxiesClient` creates client-side NameNode RPC proxies for `ClientProtocol` and related HA protocols. It hides the differences between direct non-HA NameNode addresses and logical HA nameservices with failover proxy providers.

## Important APIs, Types, And Functions
`ProxyAndInfo<PROXYTYPE>` bundles a proxy, delegation-token service, and address. Factory methods include `createProxyWithClientProtocol()`, `createProxyWithLossyRetryHandler()`, `createFailoverProxyProvider()`, `getFailoverProxyProviderClass()`, `createHAProxy()`, `createNonHAProxyWithClientProtocol()`, and `createProxyWithAlignmentContext()`.

## Control Flow
`createProxyWithClientProtocol()` attempts to build a failover proxy provider. Without one, it resolves the physical NameNode address, builds a token service, and creates a non-HA protobuf RPC translator, optionally wrapped in a retry proxy. With a provider, it creates an HA retry proxy using failover-on-network-exception retry policy and logical or physical token service depending on provider behavior.

`createFailoverProxyProvider()` loads the configured provider class, invokes its `(Configuration, URI, Class, HAProxyFactory)` constructor, wraps legacy providers, validates that logical URIs do not specify non-default ports, and propagates the fallback-to-simple-auth flag. `createProxyWithAlignmentContext()` selects `ClientGSIContext` for router observer reads when requested, sets the protobuf RPC engine, obtains the protobuf proxy with default retry policy, and wraps it in `ClientNamenodeProtocolTranslatorPB`.

## State And Persistence Behavior
The class is stateless. It creates dynamic proxies, retry handlers, RPC protocol proxies, and translator objects; any connection state is owned by Hadoop IPC and failover providers.

## Dependencies And Integration Points
It integrates with `DFSClient`, HA failover provider classes, `ClientHAProxyFactory`, `RetryProxy`, `RetryPolicies`, `RetryUtils`, `RPC`, `ProtobufRpcEngine2`, `ClientNamenodeProtocolPB`, `ClientNamenodeProtocolTranslatorPB`, `SecurityUtil`, `HAUtilClient`, `UserGroupInformation`, and optional `AlignmentContext`.

## Risks And Edge Cases
Reflection failures are wrapped as `IOException`, preserving nested IO causes. Logical URIs with explicit non-default ports are rejected. Lossy retry proxies are HA-only and return null otherwise. Empty `methodNameToPolicyMap` in non-HA retry wrapping means default policy controls all calls. Observer-read alignment context is enabled only when no context was supplied.

## Test Signals
Tests should cover non-HA proxy creation, HA provider creation and token service shape, legacy provider wrapping, configured provider class-not-found handling, logical URI port rejection, fallback-to-simple-auth propagation, lossy retry handler creation, and alignment context selection for router observer reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/NameNodeProxiesClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/PeerCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/PeerCache.java

## Purpose
`PeerCache` caches idle DataNode `Peer` connections for HDFS reads, keyed by DataNode identity and whether the peer uses a domain socket. It reduces connection setup overhead while expiring old or closed peers.

## Important APIs, Types, And Functions
Public methods are `get(DatanodeID, boolean)`, `put(DatanodeID, Peer)`, and `size()`, with testing-visible `clear()` and `close()`. Internal `Key` combines `DatanodeID` and domain-socket flag. Internal `Value` stores a `Peer` and insertion time. The expiry daemon runs `PeerCache.run()`, and eviction helpers are `evictExpired()` and `evictOldest()`.

## Control Flow
A cache with capacity zero is disabled. `put()` rejects nulls, closes peers immediately when disabled or when the peer is already closed, starts the expiry daemon lazily, evicts the oldest entry when at capacity, and inserts a new value. `get()` removes entries for the requested key in insertion order until it finds one that is not expired and not closed; expired peers are closed and skipped. The daemon periodically evicts expired global oldest entries and clears all peers when interrupted.

## State And Persistence Behavior
State is an in-memory `LinkedListMultimap<Key, Value>` and optional daemon thread. No socket survives process exit; `clear()` and `close()` close all cached peers.

## Dependencies And Integration Points
It depends on `Peer`, `DatanodeID`, Hadoop relocated Guava `LinkedListMultimap`, `IOUtilsClient.cleanupWithLogger()`, `Daemon`, and monotonic time. It integrates with the DFS read path where block readers borrow and return DataNode connections.

## Risks And Edge Cases
All map operations are synchronized. Capacity must be positive with nonzero expiry; otherwise construction throws. `getInternal()` removes all candidates it inspects, including closed or expired peers. `evictExpired()` only checks the globally oldest entries, relying on insertion order. `close()` turns an interrupted join into a runtime exception.

## Test Signals
Tests should cover disabled behavior, insertion/retrieval by DataNode and domain flag, closed peer rejection, expiry cleanup, capacity eviction order, daemon startup laziness, clear/close closing all peers, and synchronization under concurrent get/put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/PeerCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/PositionStripeReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/PositionStripeReader.java

## Purpose
`PositionStripeReader` is a `StripeReader` implementation for positional reads of a complete aligned erasure-coded stripe. It prepares decoding inputs backed by one pooled `ByteBuffer`, fills missing data/parity chunks, decodes, and returns the buffer to the pool on close.

## Important APIs, Types, And Functions
The class overrides `prepareDecodeInputs()`, `prepareParityChunk(int)`, and `decode()`, and adds `initDecodeInputs(AlignedStripe)` and `close()`. It stores one `ByteBuffer codingBuffer`.

## Control Flow
`prepareDecodeInputs()` lazily allocates decode inputs by calling `initDecodeInputs()` once. `initDecodeInputs()` computes the span length in each block, allocates a buffer large enough for data plus parity chunks from `DFSStripedInputStream`'s buffer pool, creates `ECChunk` slices for data indexes, and attaches missing aligned-stripe data chunks to those buffers. `prepareParityChunk()` validates the index is parity and missing, creates an `ECChunk` at the parity offset in the same buffer, and stores a `StripingChunk`. `decode()` finalizes inputs and calls `decodeAndFillBuffer(true)`.

## State And Persistence Behavior
State is per-read and memory-only. `close()` nulls `decodeInputs` entries and returns `codingBuffer` to the DFS striped input stream buffer pool.

## Dependencies And Integration Points
It depends on `StripeReader`, `StripedBlockUtil.AlignedStripe`, `StripingChunk`, `ECChunk`, `RawErasureDecoder`, `DFSStripedInputStream`, HDFS corrupted-block tracking, and the erasure coding policy and target block metadata.

## Risks And Edge Cases
The single buffer is partitioned by offsets; wrong span or index calculations would corrupt adjacent chunks. `prepareParityChunk()` asserts parity index preconditions with `Preconditions.checkState()`. Forgetting `close()` leaks pooled buffers. `close()` does not call a superclass close in this file, so superclass ownership must be checked before changes.

## Test Signals
Tests should cover lazy allocation, data and parity chunk offset layout, decode with missing chunks, buffer pool return on close, direct versus heap buffer behavior through `useDirectBuffer()`, and repeated prepare/decode/close calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/PositionStripeReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReadStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReadStatistics.java

## Purpose
`ReadStatistics` tracks per-stream byte counters for HDFS reads, including total bytes, local bytes, short-circuit bytes, zero-copy bytes, block type, and erasure-coding decode time.

## Important APIs, Types, And Functions
The class exposes synchronized getters for total, local, short-circuit, zero-copy, remote bytes, block type, and EC decoding time. Mutators include `addRemoteBytes()`, `addLocalBytes()`, `addShortCircuitBytes()`, `addZeroCopyBytes()`, `addErasureCodingDecodingTime()`, package-private `setBlockType()`, and `clear()`. A copy constructor snapshots byte counters from another instance.

## Control Flow
Read-path code calls the appropriate add method based on how bytes were read. Each more-specific local path increments all broader counters: zero-copy also increments short-circuit, local, and total; short-circuit increments local and total; local increments total; remote increments only total. Remote bytes are derived as total minus local.

## State And Persistence Behavior
All state is in-memory and synchronized on the instance. `clear()` resets counters and EC decode time but leaves `blockType` unchanged after construction unless set elsewhere; the default block type starts as `CONTIGUOUS`.

## Dependencies And Integration Points
It depends on `BlockType` and integrates with `DFSInputStream`/`DFSStripedInputStream` statistics surfaces exposed to HDFS clients.

## Risks And Edge Cases
The copy constructor copies byte counters but not `blockType` or `totalEcDecodingTimeMillis`, so copies may lose EC state. No validation prevents negative increments. Since remote bytes are derived, counter corruption can produce negative remote values if local exceeds total.

## Test Signals
Tests should cover counter hierarchy for each add method, derived remote bytes, synchronization/copy behavior, `clear()` semantics, block-type setting, EC decode time accumulation, and negative increment handling if callers might pass invalid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReadStatistics.java -->
