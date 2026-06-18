# subset-b-007486 research

Grouped research report for the Hadoop HDFS server/common, block alias map, SPS, and DataNode block-pool files in subset B. Each section preserves the source path in the title and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Util.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Util.java

Purpose: `Util` is a private HDFS server helper class for storage URI normalization, NameNode image download, journal-node address resolution, DataNode file-I/O profiling decisions, and basic block-pool usage statistics. It centralizes support code used by storage and image transfer paths rather than modeling one runtime service.

Important APIs and functions: `stringAsURI`, `fileAsURI`, and `stringCollectionAsURIs` normalize configuration strings into canonical URI lists. `doGetUrl` opens an authenticated `HttpURLConnection`, validates an HTTP 200 response, requires `Content-Length`, reads optional `X-MD5-Digest` and image filename headers, and delegates to `receiveFile`. `receiveFile` streams a remote fsimage/edits payload to all target local files, optionally computes MD5, throttles reads, fsyncs every output, checks the advertised size, and removes partial files on failure. `getAddressesList` parses semicolon-separated authorities and optionally expands journal hosts through `DomainNameResolver`; `getLoggerAddresses` removes excluded addresses. `isDiskStatsEnabled` is a logging helper for the file I/O sampling percentage. `getBlockPoolUsedPercentStdDev` computes the standard deviation of block pool usage from `StorageReport[]`.

Control flow and state: most methods are stateless, but static initialization creates a default `URLConnectionFactory`, captures whether SPNEGO is enabled from `UserGroupInformation`, and fixes the I/O buffer size from configuration. The image download flow is deliberately defensive: open connection, set timeout, validate response and headers, stream data to every usable output, close and force files in `finally`, then validate size and checksum. A failed output path is reported through `StorageErrorReporter` when the destination storage supports it; the download continues if at least one output stream is usable.

Persistence and dependencies: persistence is limited to writing downloaded files and deleting partial targets. The class depends on Hadoop security, HDFS config keys, `ImageServlet` headers, `StorageReport`, `DataTransferThrottler`, journal DNS resolution, and `MD5Hash`.

Integration points: NameNode image transfer code and storage recovery paths call `doGetUrl`/`receiveFile`. Journal manager code uses the address helpers for quorum journal URIs. DataNode diagnostics use the profiling and usage-deviation helpers.

Risks and test signals: callers must pass accurate advertised sizes and must handle partial writes across multiple storage directories. `receiveFile` overwrites existing paths and only deletes files on incomplete receive, size mismatch, or checksum mismatch. `getAddressesList` can throw `UnknownHostException` when resolution is enabled and no records are returned. Useful tests exercise missing `Content-Length`, digest mismatch, multi-output partial failure, directory targets requiring image filename headers, unresolved journal hosts, and empty storage-report arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/Util.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/BlockAliasMap.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/BlockAliasMap.java

Purpose: `BlockAliasMap<T extends BlockAlias>` defines the unstable public abstraction used by PROVIDED storage to map HDFS `Block` identifiers to external storage aliases such as `FileRegion`.

Important APIs and types: `Reader<U>` is an `Iterable` and `Closeable` with a `resolve(Block)` lookup method and marker `Options`. `Writer<U>` is a `Closeable` with `store(U)` and marker `Options`. `ImmutableIterator` supplies a base iterator that always rejects `remove`. The top-level API exposes `getReader(opts, blockPoolID)`, `getWriter(opts, blockPoolID)`, `refresh()`, and `close()`.

Control flow and state: this file has no concrete storage state. Implementations decide how to bind a reader or writer to a block pool and whether `refresh` has meaning. The abstract contract allows `getReader` to return null when no reader can be created, although concrete implementations often throw instead.

Persistence and dependencies: the contract depends on `Block`, `BlockAlias`, and Java `Optional`/`Iterator`/`Closeable`. Persistence semantics are left to implementations such as LevelDB, text files, or RPC-backed alias maps.

Integration points: DataNode PROVIDED storage, fsimage-generation utilities, and alias-map service clients use this contract to resolve block IDs to external file offsets.

Risks and test signals: because the API is marked unstable, callers should not assume a common option type or refresh behavior. Tests should verify implementation-specific close semantics, unsupported remove behavior, empty lookups, and block-pool scoping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/BlockAliasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/InMemoryLevelDBAliasMapClient.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/InMemoryLevelDBAliasMapClient.java

Purpose: this private client adapts the RPC protocol of `InMemoryAliasMapServer` to the `BlockAliasMap<FileRegion>` API. It is used by DataNodes and fs2img-like tools to read and write PROVIDED `FileRegion` records backed by the server-side in-memory/LevelDB alias map.

Important APIs and types: the outer class is `Configurable` and initializes protocol translators through `InMemoryAliasMapProtocolClientSideTranslatorPB.init(conf)`. `LevelDbReader.resolve` calls `aliasMap.read(block)` and maps a returned `ProvidedStorageLocation` into `FileRegion`. Its iterator pages through `aliasMap.list(marker)` using `InMemoryAliasMap.IterationResult`. `LevelDbWriter.store` writes block and provided location pairs through `aliasMap.write`.

Control flow and state: `setConf` replaces the local collection of alias-map proxies. `getAliasMap(blockPoolID)` requires a non-null block pool id, asks each proxy for `getBlockPoolId`, and returns the matching one or throws. Reader iteration is lazy and batch-oriented: first batch starts at an empty marker; when the current batch is exhausted and a next marker is present, it fetches the next batch and recurses to return the first item.

Persistence and dependencies: this class does not persist locally. It depends on RPC proxies and server-side alias map persistence. `close` stops every proxy with `RPC.stopProxy`; reader and writer close methods are no-ops because the proxy lifecycle belongs to the client.

Integration points: it bridges `BlockAliasMap` consumers with `InMemoryAliasMapProtocol`, `ProvidedStorageLocation`, and protobuf client translators.

Risks and test signals: `getAliasMap` logs and ignores IO failures while checking proxy block-pool ids, then throws if no match is found. Iterator IOExceptions are wrapped in `RuntimeException`, which can surprise callers expecting checked IO. Tests should cover multiple block pools, missing block-pool id, empty list batches, marker pagination, proxy shutdown, and failed protocol calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/InMemoryLevelDBAliasMapClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/LevelDBFileRegionAliasMap.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/LevelDBFileRegionAliasMap.java

Purpose: `LevelDBFileRegionAliasMap` is a LevelDB-backed `BlockAliasMap<FileRegion>` implementation for PROVIDED storage block-to-file-region mappings.

Important APIs and types: `LevelDBOptions` is both reader and writer options plus `Configurable`; it reads `DFS_PROVIDED_ALIASMAP_LEVELDB_PATH`. `getReader` and `getWriter` validate or default options and open a DB under the configured path, optionally nested by `blockPoolID`. `LevelDBReader.resolve` serializes a `Block` key, gets the value, deserializes it as `ProvidedStorageLocation`, and returns a `FileRegion`. `FRIterator` scans a `DBIterator`, deserializing every key/value pair. `LevelDBWriter.store` serializes the block key and provided-location value into LevelDB.

Control flow and state: `createDB` enforces a non-empty path, sets `createIfMissing` based on reader versus writer, creates the block-pool subdirectory for writers, and opens the DB with the JNI factory. The outer `close` and `refresh` are no-ops because readers and writers own DB handles.

Persistence and dependencies: persistence is local LevelDB data under `DFS_PROVIDED_ALIASMAP_LEVELDB_PATH` or a block-pool child directory. The wire/storage format reuses `InMemoryAliasMap` protobuf byte helpers.

Integration points: this implementation can be selected where a concrete `BlockAliasMap` is configured for PROVIDED storage. It integrates with Hadoop `Configuration`, `FileRegion`, and LevelDB JNI.

Risks and test signals: `LevelDBReader.resolve` does not explicitly handle a null value from `db.get`; the protobuf deserializer must tolerate or reject it. `iterator()` returns null if `db` is null, which violates normal `Iterable` expectations. Tests should cover missing configured path, reader against absent DB, writer directory creation, block-pool-specific DB paths, serialization round trips, iterator close behavior, and corrupt key/value bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/LevelDBFileRegionAliasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TextFileRegionAliasMap.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TextFileRegionAliasMap.java

Purpose: `TextFileRegionAliasMap` stores and reads `FileRegion` aliases as delimited UTF-8 text files, optionally compressed, with one block-pool-specific file per block pool.

Important APIs and types: `ReaderOptions` configures read file path and delimiter from `DFS_PROVIDED_ALIASMAP_TEXT_READ_FILE` and delimiter keys. `WriterOptions` configures output directory, delimiter, and optional codec from the write-dir and codec keys. `createReader` converts `LocalFileSystem` to raw local FS, discovers compression by file extension, derives `blocks_<blockPoolID>.csv[.codec]`, and returns `TextReader`. `createWriter` creates the output stream and wraps it with the codec if configured. `TextReader.resolve` linearly scans the iterator for a matching `Block`. `TextWriter.store` writes `blockId,path,offset,length,generationStamp[,base64Nonce]`.

Control flow and state: readers keep a synchronized `IdentityHashMap` from iterators to open `BufferedReader`s so `close` can close all active iterators. Each iterator prefetches one pending `FileRegion`; EOF removes the reader from the map. Writer state is a single `Writer` and delimiter. `refresh` throws unsupported.

Persistence and dependencies: persistence is text files in Hadoop `FileSystem`, raw local FS when applicable, and optional Hadoop compression codecs. Nonces are Base64 encoded only when non-empty. The parsed block pool id is inferred from the filename prefix `blocks_`.

Integration points: this implementation is useful for import/export tooling and PROVIDED storage bootstrap where human-readable alias maps are easier than LevelDB. It relies on HDFS config keys, `Path`, `CompressionCodecFactory`, `FileRegion`, and `ProvidedStorageLocation`.

Risks and test signals: delimiter parsing uses `String.split(delim)`, so regex metacharacters and delimiters in paths are risky. `blockPoolIDFromFileName` assumes a `blocks_` prefix. `resolve` is O(n). `getWriter` falls back to the outer `conf` in one branch, which must be set. Tests should cover compressed and uncompressed files, nonce round trip, invalid line field counts, special delimiters, multiple live iterators, close error aggregation, and filename/block-pool mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TextFileRegionAliasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/package-info.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/package-info.java

Purpose: package metadata states that the alias-map package maps PROVIDED HDFS blocks to data in remote storage systems.

Important APIs and types: no runtime types are declared here. It applies `@InterfaceAudience.Public` and `@InterfaceStability.Unstable` to the package.

Control flow, state, and persistence: none. This is documentation and annotation metadata only.

Dependencies and integration points: imports Hadoop classification annotations and scopes the public unstable API for `BlockAliasMap` and its implementations.

Risks and test signals: no executable behavior. Review signal is consistency between this package contract and concrete alias-map APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockDispatcher.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockDispatcher.java

Purpose: `BlockDispatcher` performs a single Storage Policy Satisfier block-replica movement by connecting to a target DataNode and issuing a DataTransferProtocol `replaceBlock` request.

Important APIs and functions: the constructor captures socket timeout, I/O buffer size, and whether to connect to DataNodes by hostname. `moveBlock` takes `BlockMovingInfo`, SASL client, `ExtendedBlock`, socket, data-encryption-key factory, and access token. `sendRequest` wraps `Sender.replaceBlock`; `receiveResponse` consumes `IN_PROGRESS` responses until a terminal response and validates it through `DataTransferProtoUtil.checkBlockOpStatus`. `newSocket` is visible for testing.

Control flow and state: the dispatcher is mostly immutable. `moveBlock` connects to the target xfer address, sets read timeout to `socketTimeout * 5`, performs SASL negotiation, sends the replace request naming the source DataNode and target storage type, waits for terminal response, and returns success. One `InvalidEncryptionKeyException` is retried after clearing the encryption key and creating a new socket. `BlockPinningException` is treated as success because pinned blocks should not be retried.

Persistence and dependencies: no local persistence. It affects block placement by asking a target DataNode to copy/replace a replica. Dependencies include DataTransferProtocol `Sender`, SASL/encryption token machinery, `BlockStorageMovementCommand.BlockMovingInfo`, `StorageType`, and network utilities.

Integration points: SPS mover tasks use this class to satisfy storage policies and report `BlockMovementStatus` to tracking code.

Risks and test signals: socket ownership is transferred to the method and always closed. Retry is limited to one encryption-key refresh. Treating pinning as success is intentional but can mask policy non-compliance if callers expect a physical move. Tests should mock successful terminal response, repeated `IN_PROGRESS`, encryption key retry, block pinning, protocol failure status, socket timeout, and hostname versus IP target selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementAttemptFinished.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementAttemptFinished.java

Purpose: immutable value object describing the result of one SPS block movement attempt.

Important APIs and types: constructor captures `Block`, source `DatanodeInfo`, target `DatanodeInfo`, target `StorageType`, and `BlockMovementStatus`. Getters expose block, target datanode, target type, and status; source is included only in `toString`.

Control flow, state, and persistence: no behavior beyond construction and formatting. State is final and not persisted by this class.

Dependencies and integration points: used as the result type for `CompletionService<BlockMovementAttemptFinished>` consumed by `BlockStorageMovementTracker` and passed to `BlocksMovementsStatusHandler`.

Risks and test signals: the missing source getter may matter to consumers that need source details after completion. Tests are simple construction/getter/toString checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementAttemptFinished.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementStatus.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementStatus.java

Purpose: enum of SPS DataNode block-storage movement outcomes.

Important APIs and types: two statuses are defined: `DN_BLK_STORAGE_MOVEMENT_SUCCESS(0)` and `DN_BLK_STORAGE_MOVEMENT_FAILURE(-1)`. Package-private `getStatusCode` returns the numeric code.

Control flow, state, and persistence: enum constants are static immutable values. No persistence is performed here.

Dependencies and integration points: used by `BlockDispatcher` and movement result objects; TODO notes future finer-grained failure categories.

Risks and test signals: failure detail is coarse, so diagnostics must come from logs or higher-level exceptions. Tests should confirm code values if protocol serialization or metrics depend on them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockMovementStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockStorageMovementTracker.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockStorageMovementTracker.java

Purpose: runnable tracker that drains completed SPS movement futures and forwards successful result objects to a status handler.

Important APIs and functions: constructor takes a `CompletionService<BlockMovementAttemptFinished>` and optional `BlocksMovementsStatusHandler`. `run` loops on `completionService.take()`, calls `future.get()`, logs the result, and invokes `handler.handle(result)` while still running. `stopTracking` flips a volatile `running` flag.

Control flow and state: `running` controls the outer loop and suppresses handler callbacks after stop. `take()` blocks until interrupted or a future completes. Interrupted exceptions are logged only when still running; execution exceptions are logged with a TODO for retry handling.

Persistence and dependencies: no persistence. Depends on Java concurrency, SPS result/handler types, and logging.

Integration points: movement executor services use this as a companion thread to decouple movement task completion from SPS policy state updates.

Risks and test signals: `stopTracking` alone does not unblock `take`; callers must interrupt the tracker thread for prompt shutdown. Failed futures are logged but not converted to failure status objects. Tests should cover handler invocation, null handler, stop plus interrupt, and `ExecutionException` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlockStorageMovementTracker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlocksMovementsStatusHandler.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlocksMovementsStatusHandler.java

Purpose: callback interface for collecting or processing completed SPS block movement attempts.

Important APIs and types: single method `handle(BlockMovementAttemptFinished moveAttemptFinishedBlk)`.

Control flow, state, and persistence: no implementation; state and persistence are owned by implementors.

Dependencies and integration points: consumed by `BlockStorageMovementTracker`, implemented by SPS coordination code that needs movement completion events.

Risks and test signals: implementors need to be thread-safe because callbacks happen on the tracker thread. Tests belong with implementations and should validate failure/status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/BlocksMovementsStatusHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/package-info.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/package-info.java

Purpose: package metadata documents common block movement classes for Storage Policy Satisfier functionality.

Important APIs and types: no runtime API is declared here. Package annotations mark it private and unstable.

Control flow, state, and persistence: none.

Dependencies and integration points: imports Hadoop classification annotations and applies them to the `org.apache.hadoop.hdfs.server.common.sps` package.

Risks and test signals: no executable behavior. Review signal is alignment with SPS class visibility and stability expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/sps/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPOfferService.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPOfferService.java

Purpose: `BPOfferService` represents one DataNode service for a block pool or nameservice. It owns one `BPServiceActor` per NameNode in that nameservice, coordinates registration state shared across actors, tracks which NameNode is active, and routes NameNode commands and DataNode block notifications.

Important APIs and functions: construction creates actors for configured NN and lifeline addresses. `refreshNNList` adds actors for new NNs and stops actors for removed NNs. `verifyAndSetNamespaceInfo` checks namespace/block-pool consistency and initializes the DataNode block pool on the first successful handshake. `registrationSucceeded` verifies registration consistency, records `DatanodeRegistration`, notifies the DataNode, and installs block-token keys. `notifyNamenodeReceivedBlock`, `notifyNamenodeReceivingBlock`, and `notifyNamenodeDeletedBlock` enqueue incremental block reports on every actor. `processCommandFromActor` handles `DNA_REGISTER` immediately, then dispatches other commands to `processCommandFromActive` or `processCommandFromStandby`.

Control flow and state: the class uses a read/write lock around namespace, registration, and active-actor state. `bpId` is cached volatile for low-contention access. Active NameNode tracking uses heartbeat HA state plus transaction id: a new active claim is accepted only if its txid is newer than `lastActiveClaimTxId`; stale active claims are ignored to reduce split-brain damage. Active commands trigger transfers, invalidations, cache/uncache, finalize, recovery, token updates, balancer bandwidth updates, and erasure-coding reconstruction. Standby commands are ignored except token updates, which are accepted without updating the current key.

Persistence and dependencies: persistence is indirect through `DataNode` and `FSDataset` operations: block invalidation, cache state, trash and rolling-upgrade markers, token secret managers, and block-pool shutdown/initialization. Dependencies include HA status, `DatanodeProtocol` command types, `ReceivedDeletedBlockInfo`, storage reports, and DataNode workers.

Integration points: `BlockPoolManager` starts/stops and refreshes BPOS instances. `BPServiceActor` calls back for namespace verification, registration, heartbeat active-state updates, command processing, and shutdown. DataNode client/data-transfer paths call notification methods to report block lifecycle changes.

Risks and test signals: lock ordering matters because actors call back while service state changes. `refreshNNList` starts new actors before adding them to the CopyOnWrite list. Active-state correctness depends on monotonically increasing txids. Commands from standby are mostly dropped, so HA state transitions must be processed before command routing. Tests should cover namespace mismatch, active failover with txid ordering, standby token update, bad block reporting fanout, refresh add/remove, rolling upgrade status, and active-only command effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPOfferService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActor.java

Purpose: `BPServiceActor` is the per-NameNode DataNode thread that performs version handshake, registration, heartbeats, block reports, cache reports, lifelines, incremental block reports, and NameNode command processing for one `BPOfferService`.

Important APIs and types: `retrieveNamespaceInfo` loops on `versionRequest` and validates NameNode version. `connectToNNAndHandshake` creates the NN proxy, retrieves namespace info, initializes block-pool locking, asks BPOS to verify/init storage, updates thread name, and calls `register`. `register` creates DataNode registration, retries `registerDatanode`, records returned registration, notifies BPOS, resets full block-report lease, and schedules initial FBR. `sendHeartBeat` sends storage, cache, transfer, volume-failure, slow-peer, and slow-disk state to the NN. `blockReport` flushes IBRs, builds per-storage block reports, sends either one combined RPC or one RPC per storage based on split threshold, and schedules the next report. `cacheReport` sends cached block ids periodically. `offerService` is the main periodic loop. Nested `LifelineSender` sends lightweight lifeline RPCs after registration. Nested `Scheduler` manages heartbeat, lifeline, block-report, and outlier-report times. Nested `CommandProcessingThread` asynchronously processes queued `DatanodeCommand`s.

Control flow and state: lifecycle begins in `run`, repeatedly trying handshake/registration until the BPOS policy says initialization should stop. Once running, `offerService` checks due timers, sends heartbeat, captures full block-report lease id, updates BPOS active-state before command enqueue, handles rolling upgrade status only for ACTIVE NNs, sends IBRs, sends full block reports when leased or forced, sends cache reports, then waits until the next heartbeat or IBR. Commands are processed off-thread, with `KeyUpdateCommand` inserted at the head of the queue. `bpThreadQueue` is a separate retry queue for `BPServiceActorAction` objects such as error or bad-block reports; failed actions are requeued.

Persistence and dependencies: persistence is indirect through FSDataset block/cache reports, registration state, block-pool locks, rolling-upgrade marker actions via BPOS, and metrics. It depends on DataNode configuration, NameNode and lifeline protocol translators, `IncrementalBlockReportManager`, `BlockReportContext`, slow-report types, token/key commands, and Hadoop subject-inheriting threads.

Integration points: BPOS owns actor lifecycle and command routing. DataNode storage provides block, cache, and storage reports. NameNode RPC protocols consume registration, heartbeat, block report, cache report, and bad-block operations. Tests use visible methods to trigger heartbeats, block reports, lifelines, and injected protocol proxies.

Risks and test signals: the actor has multiple threads (`bpThread`, lifeline thread, command processing thread) and volatile/shared state. `stopTracking` equivalents require interrupts to break waits. FBR lease handling must reset on invalid leases and registration. Command queue metrics must remain balanced when queues are cleared or interrupted. Tests should cover initial registration retry, NameNode restart/reregister, heartbeat-triggered active transition before command processing, split block reports, invalid lease reset, lifeline delay until registration, command queue ordering for key updates, and forced IBR/FBR triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActorAction.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActorAction.java

Purpose: small action interface used by `BPOfferService` to enqueue NameNode-reporting work onto a `BPServiceActor`.

Important APIs and types: `reportTo(DatanodeProtocolClientSideTranslatorPB bpNamenode, DatanodeRegistration bpRegistration)` performs the action against the actor's current NameNode proxy and registration and may throw `BPServiceActorActionException`.

Control flow and state: the interface has no state. `BPServiceActor.processQueueMessages` copies and clears the pending action list, invokes `reportTo`, and requeues actions that throw the custom exception.

Persistence and dependencies: persistence is owned by implementations such as bad-block or error-report actions. Dependencies are the DataNode protocol translator and registration.

Integration points: BPOS enqueues actions for every actor when reporting errors or bad blocks.

Risks and test signals: implementations should define equality carefully because the actor queue suppresses duplicates with `contains`. Tests should cover retry behavior when `reportTo` throws.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActorAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActorActionException.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActorActionException.java

Purpose: checked exception indicating a queued `BPServiceActorAction` failed and should be retried by the actor action queue.

Important APIs and types: extends `IOException`, defines `serialVersionUID`, and provides message-only and message-plus-cause constructors.

Control flow and state: no additional state. `BPServiceActor` catches this specific type, logs it, and re-enqueues the failed action.

Persistence and dependencies: no persistence; depends only on `IOException`.

Integration points: action implementations throw it to request retry instead of dropping a report.

Risks and test signals: because retry is unbounded at the queue layer, persistent failures can repeat indefinitely. Tests should verify cause preservation and actor requeue behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BPServiceActorActionException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockChecksumHelper.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockChecksumHelper.java

Purpose: `BlockChecksumHelper` contains DataNode-side checksum computers for replicated blocks and erasure-coded block groups, supporting both legacy `MD5CRC` and newer `COMPOSITE_CRC` block checksum types.

Important APIs and types: `AbstractBlockChecksumComputer` stores DataNode, checksum options, output bytes, bytes-per-CRC, CRC type, CRC count, and checksum size. `BlockChecksumComputer` adds replicated-block state: block, request length, metadata stream, checksum stream, visible length, partial-block flag, and metadata header parsing. `ReplicatedBlockChecksumComputer.compute` reads metadata then dispatches to MD5-of-CRCs or composite CRC. `BlockGroupNonStripedChecksumComputer` computes a group checksum for striped blocks by contacting live internal-block DataNodes or reconstructing missing/failed internal blocks.

Control flow and state: replicated MD5CRC digests the metadata CRC stream, recalculating the final partial CRC from block data when the requested length cuts through a checksum chunk. Replicated COMPOSITE_CRC composes CRCs across full chunks plus a final partial chunk, using existing metadata when the visible block already contains the partial chunk and recomputing from data for shorter requests. For striped groups, the computer builds a map of live block indices to DataNodes and tokens, iterates data units in logical order, records byte offsets for each child checksum, reads child checksums via DataTransferProtocol, reconstructs missing or failed blocks through erasure-coding reconstructor classes, and finally digests or reassembles cell-level CRCs in logical file order.

Persistence and dependencies: no new persistence is written. It reads local block metadata and block data streams and may make remote checksum RPCs to other DataNodes. Dependencies include DataTransferProtocol `Sender`, `BlockChecksumOptions`, `CrcComposer`, `CrcUtil`, `DataChecksum`, EC policy/reconstruction classes, tokens, and `StripedBlockUtil`.

Integration points: DataNode checksum operation handlers instantiate these computers to answer block checksum requests for replicated and striped files. It also integrates with the EC worker when reconstruction is needed for unavailable internal blocks.

Risks and test signals: checksum semantics differ for partial chunks, full visible blocks, mixed CRC types, and composite CRC. `blockGroup.setNumBytes` is temporarily mutated when constructing internal blocks and must be restored. COMPOSITE_CRC rejects mixed underlying CRC types. Remote child checksum failures fall back to reconstruction, but reconstruction failures abort. Tests should cover partial replicated MD5 and composite CRC, final partial chunk from metadata versus data, striped group missing block reconstruction, mixed CRC type behavior, requested length shorter than group length, and child DataNode protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockChecksumHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolManager.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolManager.java

Purpose: `BlockPoolManager` owns all `BPOfferService` instances in a DataNode, keyed by nameservice and block-pool id, and handles dynamic NameNode/nameservice refresh.

Important APIs and functions: `addBlockPool` adds a registered BPOS to the block-pool map. `getAllNamenodeThreads`, `get`, `remove`, `startAll`, `shutDownAll`, and `joinAll` control BPOS lifecycle. `refreshNamenodes` loads NameNode service and lifeline RPC addresses from configuration and delegates to `doRefreshNamenodes`. `createBPOS` is extracted for tests. `isSlownodeByBlockPoolId` and `isSlownode` aggregate slow-node state from BPOS instances.

Control flow and state: maps and the offer-service list are synchronized for structural changes, while the list itself is a `CopyOnWriteArrayList` for safe iteration. `doRefreshNamenodes` computes nameservices to add, remove, and refresh. It creates BPOS objects for added services under the manager lock, starts all services as the login user, stops removed services outside the manager lock so actor callbacks can call `remove`, and refreshes NN lists for existing services as the login user.

Persistence and dependencies: no direct persistence. It drives runtime connections to NameNodes and delegates storage registration to BPOS/DataNode. Dependencies include `DFSUtil` address parsing, `DFSConfigKeys`, `UserGroupInformation`, Guava-like collection helpers, and DataNode logging.

Integration points: DataNode uses this manager during startup and `refreshNamenodes`. BPOfferService calls back to `remove` when the last actor shuts down and to `addBlockPool` after successful block-pool registration elsewhere in the DataNode flow.

Risks and test signals: refresh sequencing is sensitive: newly added services are started while holding the manager lock, removed services are stopped later, and existing services refresh their actor lists. Null lifeline maps are tolerated. Tests should cover adding/removing nameservices, refreshing NN addresses inside a nameservice, map cleanup for never-registered BPOS, login-user `doAs` failures, and slow-node aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolSliceStorage.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolSliceStorage.java

Purpose: `BlockPoolSliceStorage` manages the on-disk storage slice for one block pool on a DataNode. It formats block-pool storage, recovers interrupted transitions, upgrades layout, rolls back, finalizes snapshots, manages rolling-upgrade trash, and writes block-pool VERSION properties.

Important APIs and functions: constructors bind storage info and block-pool id. `recoverTransitionRead` and `loadBpStorageDirectories` analyze a `StorageLocation`, format if needed, recover transient states, run layout transitions, and add successful `StorageDirectory` objects. `format` clears and initializes block-pool storage. `setPropertiesFromFields` and `setFieldsFromProperties` persist and load `layoutVersion`, `namespaceID`, `blockpoolID`, and `cTime`. `doTransition` decides rollback, trash restore, regular startup, upgrade, or fatal newer-state mismatch. `doUpgrade` renames `current` to `previous.tmp`, hardlinks finalized/RBW blocks into a new current directory, writes new properties, and renames to `previous`. `doRollback` swaps `previous` back to `current`. `doFinalize` renames `previous` to `finalized.tmp` and deletes it asynchronously. Trash helpers map block paths between `current` and `trash`. Rolling-upgrade marker helpers create and clear marker files and trigger finalize.

Control flow and state: block-pool id is validated against VERSION files and namespace info. PROVIDED storage bypasses normal transitions. Startup rollback first prefers a `previous` snapshot; when no previous exists it restores block files from trash. Upgrades restore trash first when moving to a newer layout, clean obsolete detach directories, remove stale previous directories, and preserve block data through hardlinks. Rolling-upgrade marker state is cached in static concurrent sets to avoid filesystem checks on every heartbeat response.

Persistence and dependencies: this file directly mutates the DataNode disk layout under `<storage>/current/<bpid>`, including `current`, `previous`, `previous.tmp`, `removed.tmp`, `finalized.tmp`, `trash`, and `RollingUpgradeInProgress`. It writes VERSION files and uses hardlinks to avoid copying block data. Dependencies include `Storage`, `StorageDirectory`, `NamespaceInfo`, `DataNodeLayoutVersion`, `DataStorage`, `FileUtil`, `HardLink`, `StorageType`, and layout feature flags.

Integration points: DataNode block-pool initialization calls recovery/transition logic after the BPOS handshake supplies namespace info. Rolling upgrade status from `BPOfferService` and FSDataset enables trash and marker operations. Replica deletion paths call `getTrashDirectory`; rollback paths call restore helpers.

Risks and test signals: disk transitions are high risk because interrupted rename/delete operations must be recoverable. Regex-based path mapping assumes block-pool id path shape and can mis-map unusual paths. Static marker caches are shared across instances. Trash is disallowed when `previous` exists to avoid mixing rollback mechanisms. Tests should cover format, normal startup, namespace/block-pool mismatch, upgrade hardlink layout, rollback eligibility, trash restore with no overwrite of larger current files, finalize async deletion, rolling-upgrade marker creation/clear, PROVIDED storage skip, and path mapping for current/trash directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockPoolSliceStorage.java -->
