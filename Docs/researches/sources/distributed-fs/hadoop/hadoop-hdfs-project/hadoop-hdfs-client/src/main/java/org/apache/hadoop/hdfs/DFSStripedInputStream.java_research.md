# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSStripedInputStream.java

## Purpose

`DFSStripedInputStream` is the HDFS client input stream for erasure-coded striped files. It extends `DFSInputStream` with block-group addressing, per-internal-block readers, stripe buffering, erasure-code decoding, and striped read statistics.

## Important APIs, Types, and Functions

The constructor records the erasure-coding policy, data/parity counts, cell size, group size, decoder, block-reader array, and striped read-statistics type. Buffer helpers include `resetCurStripeBuffer`, `getParityBuffer`, `getCurStripeBuf`, `getBufferPool`, and `getStripedReadsThreadPool`. Position/read methods include `blockSeekTo`, `seek`, `readWithStrategy`, `readOneStripe`, `copyToTargetBuf`, `fetchBlockByteRange`, and `refreshLocatedBlock`. Cleanup and unsupported APIs include `close`, `closeCurrentBlockReaders`, `closeReader`, `unbuffer`, `read(ByteBufferPool,...)`, and `releaseBuffer`.

## Control Flow

Sequential reads call `readWithStrategy`. If the current position is outside the current block group or a retry is needed, `blockSeekTo` refreshes block location state and clears existing internal readers. The stream computes a stripe range from the position, divides it through `StripedBlockUtil`, parses the `LocatedStripedBlock` into internal `LocatedBlock`s, and uses `StatefulStripeReader` to read or reconstruct the aligned stripe into `curStripeBuf`. Data is then copied from the stripe buffer into the caller strategy until the requested range or block end is satisfied. Positional reads use `PositionStripeReader` and independent temporary reader state. Failed block-reader setup can refetch encryption keys, refetch block tokens/locations, and mark dead nodes before retrying.

## State and Persistence Behavior

The class keeps only client-side runtime state: `blockReaders`, `curStripeBuf`, `parityBuf`, `curStripeRange`, decoder, and a concurrent set of datanode UUIDs already warned about for lost-block logging. Buffers are borrowed from a static `ElasticByteBufferPool` and returned on `close` or `unbuffer`; the decoder is released on close. There is no direct NameNode persistence beyond inherited block-location fetching and corruption reporting through `DFSInputStream`.

## Dependencies and Integration Points

It integrates with `DFSInputStream`, `DFSClient` striped-read thread pools and statistics, `StripeReader`, `StatefulStripeReader`, `PositionStripeReader`, `StripedBlockUtil`, `LocatedStripedBlock`, `ErasureCodingPolicy`, `RawErasureDecoder`, `CodecUtil`, `DFSUtilClient.CorruptedBlocks`, and block-reader token/encryption refresh paths. It updates both regular read statistics and EC-specific file-system read stats.

## Risks and Edge Cases

Stripe math must handle arbitrary positions, partial final block groups, and current-file-length changes for incomplete last blocks. `seek` can reuse `curStripeBuf` only when the target remains within `curStripeRange`; otherwise it invalidates `blockEnd`. Reconstruction depends on enough data/parity units and correctly sized direct or heap buffers according to decoder preference. The method explicitly does not implement enhanced zero-copy byte-buffer reads because online EC reconstruction may be required. Corruption reporting happens in `finally`, so callers may see reports after successful retries as well as checksum failures.

## Test Signals

Tests should cover sequential reads across cell and stripe boundaries, seeks within and outside the cached stripe, positional reads spanning multiple stripes, missing data block reconstruction from parity, token/encryption-key refetch, final partial stripes, corrupt-block reporting, lost-node warning de-duplication, `unbuffer` buffer release, unsupported enhanced byte-buffer access, and read-statistics updates for local/remote/short-circuit striped reads.
