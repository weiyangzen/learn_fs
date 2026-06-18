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
