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
