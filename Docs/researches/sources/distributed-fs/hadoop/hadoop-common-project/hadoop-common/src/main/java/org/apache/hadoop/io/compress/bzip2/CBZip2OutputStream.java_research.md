
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CBZip2OutputStream.java

## Purpose
`CBZip2OutputStream` is Hadoop's pure-Java bzip2 compressor, adapted from Apache Ant. It writes bzip2 data after the caller has emitted the leading `BZ` magic bytes.

## Important APIs and Types
It extends `OutputStream` and implements `BZip2Constants`. Public APIs include constructors, `chooseBlockSize`, `write`, `finish`, `close`, `flush`, `getBlockSize`, and visible `getAllowableBlockSize`. Internals implement run-length encoding, block sorting, move-to-front transform, Huffman table generation, bit output, CRCs, randomization fallback, and nested `Data` arrays.

## Control Flow
Construction validates block size, allocates block data, writes the `h` format byte and block-size digit, and initializes the first block. Writes accumulate runs and encode them into the block; when the block reaches its allowable size, the current block is ended and a new block starts. `finish()` flushes any pending run, ends the block, writes the end-of-stream marker and combined CRC, then releases state. Compression flow is RLE -> block sort/BWT -> MTF generation -> Huffman table selection/refinement -> bitstream emission.

## State and Persistence
State includes current block index, original pointer, block size, bit buffer/live bits, CRCs, run tracking, sort work limits, block randomization flag, output stream, and memory-intensive arrays (`block`, `fmap`, `sfmap/quadrant`, frequency tables, selectors, heaps, sort stacks). Finish/close null out `out` and `data`.

## Dependencies and Integration
Used by `BZip2Codec.BZip2CompressionOutputStream` and bzip2 test utilities. It depends on `CRC`, `BZip2Constants`, and Hadoop `IOUtils` for close handling.

## Risks
Instances are not thread-safe and can allocate around 8.5 MB for 900k compression blocks. The `finalize()` method calls `finish()`, which is legacy and should not be relied on for resource management. Sorting is performance-sensitive and contains heavily unrolled code; small changes can affect compression ratio, speed, or correctness. The caller must write the `BZ` header separately.

## Test Signals
`TestBZip2Codec`, `BZip2TextFileWriter`, and stream reuse tests exercise valid stream generation, block boundaries, reset handling, and interoperability with `CBZip2InputStream`.
