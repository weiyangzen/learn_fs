# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/StripedBlockUtil.java

## Purpose

`StripedBlockUtil` is the HDFS erasure-coded striped block mapping utility. It translates logical byte ranges in a block group into internal-block offsets, aligned read stripes, chunk buffers, and zero-fill markers used by striped reads and recovery/decoding paths. It also constructs per-internal-block `LocatedBlock`/`ExtendedBlock` views from a `LocatedStripedBlock`.

## Important APIs, Types, And Functions

Key entry points are `parseStripedBlockGroup`, `constructInternalBlock`, `getInternalBlockLength`, `getSafeLength`, `offsetInBlkToOffsetInBG`, `divideOneStripe`, `divideByteRangeIntoStripes`, `spaceConsumedByStripedBlock`, `getNextCompletedStripedRead`, `checkBlocks`, and `getBlockIndex`. Important nested types are `BlockReadStats`, `StripingCell`, `AlignedStripe`, `VerticalRange`, `StripingChunk`, `ChunkByteBuffer`, `StripingChunkReadResult`, and `StripeRange`.

## Control Flow

Block-group parsing indexes returned striped locations by block index and constructs internal blocks with adjusted block IDs and lengths. Range division maps a logical request to `StripingCell`s, derives per-internal-block `VerticalRange`s, merges range boundaries into aligned stripes, maps destination `ByteBuffer` slices into requested chunks, and marks data chunks beyond short internal block length as `ALLZERO`. Async read completion pulls `Future<BlockReadStats>` from a `CompletionService` and normalizes success, failure, cancellation, and timeout into `StripingChunkReadResult`.

## State And Persistence

The class is stateless apart from mutable objects it returns. `StripingChunk` state flags model in-memory read progress only. `ChunkByteBuffer` holds `ByteBuffer` slices over caller buffers and can copy decoded data back. There is no persistence; correctness depends on stable block IDs, generation stamps, EC policy width, cell size, and block-group length supplied by HDFS metadata.

## Dependencies And Integration Points

It integrates with `LocatedStripedBlock`, `LocatedBlock`, `ExtendedBlock`, `ErasureCodingPolicy`, `DFSStripedOutputStream` cell layout, block tokens, storage IDs/types, datanode locations, async read executors, and HDFS striped reader/decoder code.

## Risks

Most risks are off-by-one or boundary errors: inclusive logical ranges are converted to half-open buffer ranges, last partial cells affect parity fetch spans, and block-group length can split a stripe. `spaceConsumedByStripedBlock` uses a parity index based on internal length symmetry and should be regression-tested for partial final stripes. `getBlockIndex` masks only low four bits, so it assumes the encoded internal index range remains within that contract.

## Test Signals

Useful tests cover full and partial stripes, single-stripe reads, reads crossing cell and stripe boundaries, partial final block groups, all-zero chunk preparation, async read success/failure/cancel/timeout, block token/location propagation, `checkBlocks` mismatch exceptions, safe length calculation, and parity space accounting for multiple EC policies.
