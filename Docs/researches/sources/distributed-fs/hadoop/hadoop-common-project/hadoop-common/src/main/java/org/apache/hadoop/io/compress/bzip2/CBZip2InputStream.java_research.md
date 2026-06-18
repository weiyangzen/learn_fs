
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CBZip2InputStream.java

## Purpose
`CBZip2InputStream` is Hadoop's pure-Java bzip2 decompressor, adapted from Apache Ant and enhanced for Hadoop split processing. It expects the leading `BZ` bytes to be handled by the caller.

## Important APIs and Types
It extends `InputStream` and implements `BZip2Constants`. Public/visible APIs include constructors with `READ_MODE`, `read`, `skipToNextMarker`, visible `skipToNextBlockMarker`, `numberOfBytesTillNextMarker`, `getProcessedByteCount`, `updateReportedByteCount`, `close`, and CRC error reporting. Internal `STATE` drives decompression phases, and nested `Data` holds large per-block arrays.

## Control Flow
In `CONTINUOUS` mode, the constructor initializes stream headers unless lazy initialization is needed for empty input. In `BYBLOCK` mode, it scans to the next block delimiter and then initializes one block. `read(byte[], int, int)` emits decompressed bytes until the buffer fills or the internal state returns end-of-block/end-of-stream; in BYBLOCK mode it returns `END_OF_BLOCK` after a block so `BZip2Codec` can update compressed positions. Decoding reads Huffman tables, move-to-front data, reconstructs the Burrows-Wheeler transform, applies randomized or non-randomized output setup, and validates CRCs.

## State and Persistence
State includes bit buffer/live bits, raw and reported compressed byte counters, current block metadata, CRCs, current output character/state-machine variables, and large block decode arrays (`ll8`, `tt`, Huffman tables, selectors). Closing nulls data and the input stream. No durable state is written.

## Dependencies and Integration
Used by `BZip2Codec.BZip2CompressionInputStream` for pure-Java normal and split reads. Test utilities use `numberOfBytesTillNextMarker` and block marker scanning to validate split offsets.

## Risks
Instances are not thread-safe and allocate several MB per max-size block. Marker scanning works at bit granularity and must maintain byte counters exactly for split correctness. CRC errors are fatal. Public mutable constants from `BZip2Constants` can affect randomized block handling. Lazy initialization based on `available()` can be sensitive to unusual input stream implementations.

## Test Signals
`TestBZip2Codec` validates BYBLOCK and CONTINUOUS behavior through `BZip2Codec`. `BZip2Utils` and bzip2 text writer tests exercise block marker offsets. Corruption/CRC behavior should be covered when modifying decode paths.
