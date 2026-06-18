# subset-b-007487 research

Work item `subset-b-007487` covers six DataNode-side HDFS classes under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode`. The files form a local block I/O cluster: receiving and committing writes, sending reads, recovering replicas after client or DataNode failure, scheduling background block verification, carrying partial-chunk checksum state, and centralizing the DataNode configuration values used by those paths.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockReceiver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockReceiver.java

## Purpose

`BlockReceiver` is the DataNode write-side data-transfer component. It receives HDFS data packets for one `ExtendedBlock`, writes block bytes and metadata checksums into a local `ReplicaInPipeline`, optionally mirrors the packets to a downstream DataNode, and coordinates upstream acknowledgements through an inner `PacketResponder`. It is used by client writes, append/recovery writes, DataNode-to-DataNode replication, replace-block, and block-transfer setup stages.

## Important APIs, types, and functions

- `BlockReceiver(...)` constructs the receiver, creates or recovers the target replica according to `BlockConstructionStage`, opens `ReplicaOutputStreams`, initializes client and disk `DataChecksum` instances, writes the metadata header for newly created replicas, and configures cache/sync behavior from `DNConf` and `CachingStrategy`.
- `receiveBlock(...)` is the outer receive loop. It starts `PacketResponder` for client pipelines, repeatedly calls `receivePacket()`, finalizes or converts replicas for DataNode-originated transfers, and handles restart/OOB cleanup behavior.
- `receivePacket()` parses one `PacketHeader`, validates offsets and lengths, mirrors the packet downstream, verifies or translates checksums, writes block data and metadata, handles hsync/sync-block requests, enqueues ack records, sends replace-block progress responses, and applies throttling.
- `flushOrSync(boolean isSync, long seqno)` flushes data and checksum streams and optionally fsyncs files and the replica directory. It records fsync/flush metrics and slow-I/O warnings.
- `PacketResponder` is an inner `Runnable`/`Closeable` that owns the ack queue. It reads downstream `PipelineAck`s, waits for locally persisted packets, finalizes client-written blocks on the last packet, builds local ack headers, relays OOB restart acks, and updates `bytesAcked`.
- `verifyChunks`, `translateChunks`, `computePartialChunkCrc`, and `adjustCrcFilePosition` implement checksum handling, including partial-chunk recovery where on-disk data already contains part of the chunk.
- `manageWriterOsCache` applies `sync_file_range` and `posix_fadvise(DONTNEED)` behavior behind large writes.

## Control flow

Construction selects the replica lifecycle path first. DataNode-originated replication/move creates a temporary replica. Client stages create RBW, recover RBW, append, recover append, or create temporary transfer replicas. The constructor then opens streams, compares requested and disk checksum policies, records whether checksum translation is needed, and writes a checksum metadata header for new replicas.

`receiveBlock` installs downstream/upstream streams and starts `PacketResponder` only for client-originated non-transfer pipelines. The receive thread remains responsible for reading data packets, writing local disk state, and forwarding packet bytes to the mirror. The responder thread remains responsible for downstream ack reads and upstream ack writes. On normal completion, the receive path closes the responder queue and, for replication/transfer paths rather than client writes, finalizes or converts the replica itself. Client-write finalization happens in `PacketResponder.finalizeBlock` after the last packet is durably handled and before the last ack is returned.

`receivePacket` is ordered to preserve pipeline semantics: header validation and replica byte visibility update happen first; packets are forwarded to the mirror before local disk writes; checksum verification is skipped for middle DataNodes on normal client pipelines unless this node is last, the sender is another DataNode, or checksum translation is required; local data and checksums are written only for bytes beyond `bytesOnDisk`; sync packets enqueue acks after fsync; non-sync packets may enqueue earlier when checksum verification can be delegated to downstream. The last packet returns `-1` to stop the loop.

The ack responder loop reads downstream acks when present, matches them with the head of `ackQueue`, computes local and downstream ack timing, finalizes the block when the packet is marked last, sends a combined `PipelineAck` upstream, and removes the ack queue head. Mirror read/write errors set `mirrorError`, allowing upstream to learn that the downstream leg failed while this DataNode keeps enough local state to let pipeline recovery decide fault attribution.

## State and persistence behavior

Persistent state is the local replica data file, checksum metadata file, optional restart metadata file, and finalization state in `FsDatasetSpi`. `replicaInfo.setNumBytes` advances visible in-pipeline length, `setLastChecksumAndDataLen` stores the last checksum and data length for concurrent reads and append recovery, and `setBytesAcked` tracks the highest offset successfully acknowledged upstream. `syncOnClose`, sync-block packets, and directory fsync flags determine when file data, checksum metadata, and parent directory entries are forced to stable storage.

The class carefully manages reserved space and volume references: constructor failures release reserved bytes and clean partial replication blocks; `releaseAnyRemainingReservedSpace` is a defensive close-time cleanup; `claimReplicaHandler` transfers ownership so finalization can keep the volume reference while `BlockReceiver.close()` nulls the normal field.

For DataNode restart, incomplete client pipelines can write restart metadata with an expiry time and send an OOB restart ack so clients can reconnect without treating the DataNode as corrupt. For replace-block operations, periodic `IN_PROGRESS` responses prevent caller socket timeouts while throttling slows transfer.

## Dependencies and integration points

`BlockReceiver` is tightly integrated with `DataNode`, `FsDatasetSpi`, `ReplicaInPipeline`, `ReplicaOutputStreams`, `PacketReceiver`, `PacketHeader`, `PipelineAck`, `BlockMetadataHeader`, `DataTransferThrottler`, `DataNodeFaultInjector`, `DataNodePeerMetrics`, `DNConf`, and HDFS protocol classes such as `ExtendedBlock`, `DatanodeInfo`, and `BlockConstructionStage`. It feeds DataNode metrics for packets, bytes written, slow disk writes, slow mirror writes, fsyncs, slow acks, and peer downstream latency. It also reports corrupt remote source blocks to the NameNode when checksum errors are detected during DataNode-originated writes.

## Risks and edge cases

The highest-risk logic is partial chunk handling during recovery or append. It must reconcile `bytesOnDisk`, packet offsets, chunk boundaries, prior checksum bytes, and client-provided checksum buffers without corrupting the metadata file. Pipeline error handling is also subtle: mirror failures should notify upstream without prematurely blaming the current node, while checksum errors reported by downstream deliberately self-terminate the sender/responder. Thread coordination relies on `ackQueue` monitor discipline, responder interruption, join timeouts, and `running` state; regressions here can produce stuck xceivers or lost final acks. Slow disk or downstream writes affect pipeline health and are explicitly logged and metered.

## Test signals

Useful tests should exercise create, append, recovery, transfer RBW/finalized, replacement, checksum translation, missing checksums for transient storage, partial-chunk append recovery, sync-block/hsync behavior, restart OOB acks, downstream ack mismatch, mirror failure, checksum mismatch, slow-I/O fault injection, and responder join timeout paths. Existing hooks such as `DataNodeFaultInjector`, `@VisibleForTesting` cache constants, and metrics counters are clear signals that behavior is covered by targeted unit and integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockReceiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockRecoveryWorker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockRecoveryWorker.java

## Purpose

`BlockRecoveryWorker` executes NameNode-issued block recovery commands on a DataNode. It coordinates with peer DataNodes through `InterDatanodeProtocol`, chooses recoverable replicas, updates replicas under recovery to a new generation stamp and length, and commits the synchronized result back to the active NameNode. It supports both contiguous replicated blocks and erasure-coded striped block groups.

## Important APIs, types, and functions

- `recoverBlocks(String who, Collection<RecoveringBlock> blocks)` starts a `Daemon` that processes recovery commands and maintains the DataNode block recovery worker metric.
- `BlockRecord` binds a `DatanodeID`, `InterDatanodeProtocol` proxy, `ReplicaRecoveryInfo`, and returned storage ID. `updateReplicaUnderRecovery` calls the remote or local DataNode to truncate/update the replica.
- `RecoveryTaskContiguous.recover()` asks each target DataNode to `initReplicaRecovery`, filters invalid generation stamps, zero-length replicas, and weak replica states, then calls `syncBlock`.
- `RecoveryTaskContiguous.syncBlock(...)` selects the best replica state, computes the recovered length, updates participating replicas, and calls `commitBlockSynchronization`.
- `RecoveryTaskStriped.recover()` maps internal block IDs to the longest valid replica, computes a safe block-group length, truncates internal blocks that can participate, and commits a block-group synchronization result.
- `getActiveNamenodeForBP`, `getDatanodeID`, and `callInitReplicaRecovery` isolate block-pool service lookup and RemoteException unwrapping.

## Control flow

The daemon iterates each `RecoveringBlock`, logs the command, branches by `isStriped()`, and catches per-block `IOException`s so one failed recovery does not stop the remaining batch.

For contiguous blocks, recovery probes all listed locations. A local target uses the in-process DataNode as `InterDatanodeProtocol`; remote targets use a proxy configured with `DNConf.socketTimeout` and `connectToDnViaHostname`. A replica is considered a candidate when its generation stamp is at least the block generation stamp and its length is positive. Only replicas whose original state is `RWR` or better join the synchronization list. If all probes fail, or candidates exist but none are recoverable, recovery fails.

`syncBlock` commits deletion when no non-empty replicas are available. Otherwise it finds the best state: finalized replicas dominate and must agree on length; RBW/RWR recovery uses the minimum length across replicas in the best state. Truncate recovery overrides the computed length with `rBlock.getNewBlock().getNumBytes()`. Each participating DataNode is asked to update its replica under recovery to the recovery generation stamp, new block ID, and new length. At least one success is required before the NameNode is notified with the successful DataNode and storage IDs.

For striped blocks, the worker validates that at least the number of data units are available, probes internal block replicas, keeps the longest replica per internal block, computes a safe block-group length through `StripedBlockUtil.getSafeLength`, and truncates internal blocks whose current length can satisfy the safe length. It commits either deletion when the safe length is zero or a block-group update with arrays indexed by internal block index.

## State and persistence behavior

The worker does not persist local state directly. Persistence occurs through peer `updateReplicaUnderRecovery` calls, which change replica generation stamp, block ID, length, and state in each DataNode dataset, and through `commitBlockSynchronization`, which updates NameNode metadata. `BlockRecord.storageID` is populated only after successful replica update and is sent to the NameNode to bind recovered locations to storage volumes.

Recovery IDs are treated as new generation stamps. The code aborts if a peer reports `RecoveryInProgressException`, preventing overlapping recoveries with conflicting generation stamps. For striped block groups, the safe length policy deliberately prefers truncation to a length that can be represented by enough internal blocks; TODO comments state that parity regeneration for partial stripes is not implemented here.

## Dependencies and integration points

This class depends on `DataNode`, `BPOfferService`, active NameNode translator `DatanodeProtocolClientSideTranslatorPB`, `InterDatanodeProtocol`, `ReplicaRecoveryInfo`, `RecoveringBlock`, `RecoveringStripedBlock`, `ErasureCodingPolicy`, `StripedBlockUtil`, and `HdfsServerConstants.ReplicaState`. It integrates with DataNode metrics and logging, and relies on `DNConf` for inter-DataNode proxy behavior.

## Risks and edge cases

Contiguous recovery must avoid committing a length that loses finalized data or extends beyond a valid replica. The finalized-length consistency check is critical because conflicting finalized replicas imply deeper corruption. Striped recovery is more limited: it chooses the longest duplicate internal replica, truncates to a safe length, and explicitly leaves decode/encode parity repair TODOs, so changes here can affect erasure-coded file correctness. A partial failure after some `updateReplicaUnderRecovery` calls but before NameNode commit causes recovery to be retried with updated peer state, so idempotence and generation-stamp validation are important.

## Test signals

Tests should cover no replicas, all DataNodes failing, in-progress recovery abort, finalized length disagreement, RBW/RWR min-length selection, truncate recovery with a new block, partial participant failure, active NameNode lookup failure, and striped safe-length computation with missing and zero-length internal blocks. The `@VisibleForTesting getSafeLength` method and fault-injector delay point are direct hooks for deterministic tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockRecoveryWorker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockScanner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockScanner.java

## Purpose

`BlockScanner` is the DataNode-level coordinator for periodic on-disk block verification. It owns one `VolumeScanner` per storage volume, configures scan rate/staleness/cursor behavior, starts and stops scanner threads as volumes appear or disappear, marks suspicious blocks for prompt rescans, and exposes scanner statistics through an HTTP servlet.

## Important APIs, types, and functions

- `BlockScanner(DataNode, Configuration)` builds a cached `Conf`, initializes scanner shutdown join timeout, and logs whether scanning is enabled.
- `Conf` reads scanner-specific configuration: bytes per second, scan period, max staleness, cursor save interval, skip-recent-accessed flag, and optional test-only `ScanResultHandler`.
- `isEnabled()` gates all scanner creation and suspect-block handling on positive scan period and positive target bytes/sec.
- `addVolumeScanner(FsVolumeReference)` creates and starts a `VolumeScanner`, stores it by storage ID, and keeps or releases the volume reference according to success.
- `removeVolumeScanner`, `removeAllVolumeScanners`, `enableBlockPoolId`, and `disableBlockPoolId` manage scanner lifecycle and block-pool participation.
- `markSuspectBlock(String storageId, ExtendedBlock block)` forwards urgent scan requests to the matching volume scanner.
- `Servlet.doGet` emits plain text scanner statistics from the DataNode web UI.

## Control flow

The constructor snapshots configuration. When the DataNode registers or adds a storage volume, `addVolumeScanner` checks `isEnabled`, rejects duplicate storage IDs, constructs `VolumeScanner(conf, datanode, ref)`, starts the thread, and records it in the `TreeMap`. If scanner creation fails or scanning is disabled, it closes the `FsVolumeReference` so the volume is not leaked.

Removal is synchronized. Single-volume removal shuts down the scanner, removes it from the map, and joins for five minutes. Full shutdown first broadcasts `shutdown()` to all scanners, then joins each using the configurable `joinVolumeScannersTimeOutMs`, then clears the map. Block-pool enable/disable events are broadcast to all active volume scanners.

`markSuspectBlock` is a fast path from other DataNode components, such as read failures in `BlockSender`, to prioritize a likely-corrupt block. It is intentionally best-effort: disabled scanners or missing volume scanners are logged and ignored.

## State and persistence behavior

`BlockScanner` itself keeps only in-memory state: `TreeMap<String, VolumeScanner> scanners`, current `Conf`, and join timeout. Persistent scanner cursors and result handling are delegated to `VolumeScanner`; `Conf.cursorSaveMs` and `maxStalenessMs` are passed down but not persisted here. Synchronization on public lifecycle methods serializes mutations to the scanner map.

## Dependencies and integration points

The class integrates with `DataNode`, `VolumeScanner`, `FsVolumeReference`, `FsVolumeSpi`, `ExtendedBlock`, servlet context attribute `datanode`, `DFSConfigKeys`, and Guava `Uninterruptibles`. It is a downstream consumer of corruption signals from block transfer code, and an upstream coordinator for per-volume verification workers.

## Risks and edge cases

Resource ownership is the main local risk: `FsVolumeReference` must be closed when a scanner is not retained, and scanner threads must not block DataNode shutdown indefinitely. Disabled scanner configuration is represented by negative or zero scan periods or zero throughput; callers must tolerate no-op add/remove/suspect paths. Duplicate storage IDs are logged as errors and ignored, which is safer than running two scanners over the same volume but may hide volume identity bugs.

## Test signals

Tests should validate configuration edge cases, especially scan period zero compatibility behavior, disabled scanner behavior, duplicate add handling, reference cleanup on add failure, block-pool broadcast, suspect-block routing, shutdown timeout behavior, and servlet output for enabled and disabled scanner states. `Conf.allowUnitTestSettings` and internal config keys provide explicit test hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockSender.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockSender.java

## Purpose

`BlockSender` is the DataNode read-side data-transfer component. It reads a block and its metadata checksums from the local dataset and streams them as HDFS data packets to a client or another DataNode. It enforces byte-range and checksum chunk alignment, optionally verifies checksums while reading, can use zero-copy `transferTo` for socket sends, manages read-ahead/drop-behind cache behavior, and marks blocks suspect when disk-like read/send failures appear.

## Important APIs, types, and functions

- `BlockSender(...)` validates and snapshots the target replica, opens metadata and block input streams, selects checksum behavior, computes aligned offsets, captures the last partial chunk checksum for RBW/finalized replicas, and creates `ReplicaInputStreams`.
- `sendBlock(DataOutputStream, OutputStream, DataTransferThrottler)` wraps `doSendBlock` in a tracing scope.
- `doSendBlock(...)` computes packet buffer sizes, selects normal copy or `transferTo`, repeatedly calls `sendPacket`, sends the terminating empty packet, records client trace logs, and closes streams.
- `sendPacket(...)` writes a `PacketHeader`, reads checksum bytes, optionally substitutes an in-memory last-partial checksum, reads data or transfers it directly from the file channel, verifies checksums if requested, writes to the output stream, throttles, and returns data bytes sent.
- `readChecksum` handles missing or unreadable checksum data, filling zeros only when `corruptChecksumOk` is true.
- `verifyChecksum` recomputes and compares checksums chunk by chunk, throwing `ChecksumException` with the failed offset.
- `manageOsCache`, `isLongRead`, and `close` coordinate readahead and `posix_fadvise(DONTNEED)` cache dropping.

## Control flow

The constructor first captures the replica under a dataset read lock and checks generation stamp compatibility. RBW replicas may wait briefly for the requested minimum visible length and provide an in-memory last checksum. Finalized replicas lazily load the last partial chunk checksum so a concurrent append cannot race with a stale metadata checksum. The constructor obtains a volume reference, opens metadata if checksum sending or verification is needed, falls back to NULL checksums when allowed, validates requested offset/length against the bytes safely readable, aligns the read start and end to checksum chunk boundaries, skips checksum metadata to the aligned offset, and opens the block data stream at the same offset.

The send loop chooses `transferTo` only when configured, checksum verification is off, the base stream is a `SocketOutputStream`, and the data stream is a `FileInputStream`. In normal mode the packet buffer holds header, checksums, and data. In transferTo mode it holds only header and checksum data, then delegates file bytes to `FileIoProvider.transferToSocketFully`. After all data reaches `endOffset`, an empty packet marks end-of-block/range and `sentEntireByteRange` becomes true unless the thread was interrupted.

Exception handling distinguishes client socket behavior from likely disk corruption. Broken pipe and connection reset are treated as expected client disconnects. EIO-style messages become `DiskFileCorruptException`; other non-timeout send exceptions mark the block suspect through `BlockScanner`.

## State and persistence behavior

`BlockSender` does not mutate block contents. Its persistent interaction is indirect: suspected corrupt reads can trigger scanner work through `datanode.getBlockScanner().markSuspectBlock`, and `invalidateMissingBlock` is called when metadata is unexpectedly absent. It owns a `FsVolumeReference` for the duration of the transfer to prevent volume removal, closes metadata/data streams on completion, and cancels outstanding readahead.

Mutable transfer state includes `offset`, `endOffset`, `seqno`, `blockInPosition`, `sentEntireByteRange`, `lastChunkChecksum`, `curReadahead`, and `lastCacheDropOffset`. `lastChunkChecksum` is specifically a consistency bridge from write-side mutable replicas to read-side packet construction.

## Dependencies and integration points

The class depends on `DataNode`, `FsDatasetSpi`, `Replica`, `ReplicaInPipeline`, `FinalizedReplica`, `ReplicaInputStreams`, `FsVolumeReference`, `LengthInputStream`, `BlockMetadataHeader`, `DataChecksum`, `PacketHeader`, `DataTransferThrottler`, `SocketOutputStream`, `FileIoProvider`, `BlockScanner`, `DNConf`, and HTrace/FsTracer. It consumes `DNConf.transferToAllowed`, `readaheadLength`, and drop-cache settings.

## Risks and edge cases

Read alignment is subtle: requested ranges may begin or end mid-chunk, but packets must carry whole checksum chunks when checksums are sent. Metadata files can be missing, too short, or have unrealistic chunk sizes; the constructor tries to preserve historical behavior while still rejecting corrupt headers. The last partial chunk checksum path exists because concurrent append or RBW writes can overwrite metadata after the sender opens; losing that ordering can produce false checksum failures. The EIO detection uses message-prefix parsing because some NIO paths do not expose stronger exception types; this is fragile but intentionally documented in the code.

## Test signals

Tests should cover aligned and unaligned byte ranges, `length < 0`, RBW visible-length waits, finalized last-partial checksum loading, missing/corrupt metadata with `corruptChecksumOk` true and false, NULL checksums, normal copy versus transferTo, checksum verification failures, socket timeout versus disk EIO classification, block scanner suspect marking, interruption before final packet, and cache/readahead behavior for short and long reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/BlockSender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ChunkChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ChunkChecksum.java

## Purpose

`ChunkChecksum` is a small immutable holder for the checksum bytes of the last checksum chunk and the data length at which that checksum applies. It lets write-side or replica state hand a coherent partial-chunk checksum to `BlockSender`.

## Important APIs, types, and functions

- `ChunkChecksum(long dataLength, byte[] checksum)` stores the visible data length and checksum bytes. The checksum may be `null` when unavailable.
- `getDataLength()` returns the block length associated with the checksum.
- `getChecksum()` returns the raw checksum byte array.

## Control flow

The class has no internal branching. `BlockSender` consumes it during construction to determine the safe readable end offset and during the last data packet to overwrite the last checksum read from disk with the current in-memory checksum when needed.

## State and persistence behavior

The holder is immutable by field reference, but it does not defensively copy the checksum array. Callers must treat the byte array as stable or avoid mutating it after construction. It does not perform I/O or persistence.

## Dependencies and integration points

`ChunkChecksum` is in the DataNode package and is used by `ReplicaInPipeline.getLastChecksumAndDataLen`, `FinalizedReplica.getLastPartialChunkChecksum`, and `BlockSender`. It represents the contract between mutable replica write state and packetized read state.

## Risks and edge cases

Because `getChecksum()` exposes the backing array, accidental mutation could corrupt the checksum substituted into a read packet. A null checksum is a valid signal and must be handled by consumers by falling back to on-disk or NULL-checksum behavior. The `dataLength` must match the checksum's logical chunk end; inconsistent producer state can make `BlockSender` reject otherwise valid requested ranges.

## Test signals

Tests are mostly integration-level: RBW and finalized partial-chunk reads should verify that the last packet uses the current partial checksum and that null checksum values do not crash the sender. A focused unit test could assert simple accessor behavior, but correctness is mainly proven through `BlockSender` and replica tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ChunkChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DNConf.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DNConf.java

## Purpose

`DNConf` is the DataNode startup/runtime configuration snapshot. It reads Hadoop `Configuration` keys into typed fields used by data transfer, block reports, cache reports, volume handling, security, persistent memory cache, slow-I/O logging, peer/disk statistics, and shutdown/restart behavior. Several fields remain mutable through setters for tests or live reconfiguration hooks.

## Important APIs, types, and functions

- `DNConf(Configurable dn)` reads all configuration values from `dn.getConf()` and normalizes units and invariants.
- Public getters expose transfer encryption, socket timeouts, SASL/trusted-channel helpers, buffer sizes, TCP no-delay, lifeline intervals, memory locking, persistent memory directories, process-command thresholds, report intervals, and slow-I/O thresholds.
- Package-private setters update block report interval, cache report interval, split threshold, initial block report delay, and peer stats.
- Public setters update file I/O profiling sampling, outlier report interval, and DataNode slow-I/O warning threshold.
- `initBlockReportDelay()` clamps the initial block report delay to zero if it is negative or greater than/equal to the block report interval.

## Control flow

Construction is linear but includes several important normalizations. Lifeline interval defaults to three heartbeats and is forced to exceed the heartbeat interval. Restart replica expiry is converted from seconds to milliseconds. Block-pool ready timeout is read as seconds. Disk stats are derived from file-I/O profiling sampling percentage through `Util.isDiskStatsEnabled`. Configured data directories are counted to support tolerated-volume-failure checks. Security helpers are initialized through `TrustedChannelResolver` and `DataTransferSaslUtil`.

The mutable setters enforce simple invariants with `Preconditions`: report intervals must be positive, split threshold must be non-negative, and slow-I/O warning threshold must be positive. Some setters also write back into the underlying `Configuration` before recomputing derived fields, such as initial block report delay and outlier report interval.

## State and persistence behavior

Most fields are final startup snapshots. Operational fields that can change after construction are `volatile`, including report intervals, peer/disk stats flags, outlier interval, cache report interval, initial block report delay, and slow-I/O threshold. `DNConf` does not persist state outside the wrapped `Configuration`, but a few setters mutate the configuration object so subsequent reads see updated raw values.

## Dependencies and integration points

`DNConf` integrates with nearly every DataNode subsystem. `BlockReceiver` consumes socket timeout, restart replica expiry, sync-on-close, drop-cache/sync-behind-write flags, slow-I/O thresholds, xceiver stop timeout, peer stats, and lazy-persist policy. `BlockSender` consumes transferTo, readahead, drop-cache-read settings, and socket-related behavior. `BlockRecoveryWorker` consumes socket timeout and hostname proxy preference. Other DataNode services consume block/cache report intervals, heartbeat/lifeline timing, security fields, locked memory, persistent memory cache settings, volume-failure tolerances, max IPC data length, and NameNode compatibility minimums.

## Risks and edge cases

The class centralizes unit conversions, so mistakes can create cluster-wide timing bugs. Lifeline and block-report delay clamping prevents invalid operator settings from breaking DataNode liveness/report scheduling. Because many fields are final snapshots, changing Hadoop configuration after startup has no effect unless a setter exists and is called. Public mutable setters must maintain the same invariants as constructor-derived values or downstream code may observe invalid volatile state.

## Test signals

Tests should cover default construction, explicit socket/cache/security/report settings, lifeline clamping when configured less than heartbeat, initial block report delay clamping, unit conversions, data directory counting, disk stats sampling toggles, persistent memory config, setter precondition failures, and downstream consumers such as `BlockSender` and `BlockReceiver` observing updated slow-I/O/report settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/DNConf.java -->
