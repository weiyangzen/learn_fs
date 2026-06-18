# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECChunk.java

Purpose: wraps a `ByteBuffer` slice or byte array as the chunk-level data unit passed to raw erasure coders.

Important APIs and control flow: constructors wrap whole buffers/arrays or slice a `ByteBuffer` using offset/length. `toBuffers()` converts nullable `ECChunk[]` to nullable `ByteBuffer[]`. `toBytesArray()` copies remaining bytes without changing the original buffer position via mark/reset. `allZero` is a metadata flag for optimized handling.

State and persistence: stores one `ByteBuffer` and mutable `allZero`; underlying buffer content is external mutable state. No persistence.

Dependencies and integration: used by `ErasureCodingStep.performCoding()`, `ErasureEncodingStep`, `ErasureDecodingStep`, and HH-XOR steps to bridge block/chunk abstractions to raw byte-buffer coders.

Risks and test signals: test array-backed/direct buffers, slices, null conversion, mark/reset behavior, and all-zero propagation. Buffer position/limit semantics are critical because raw coders often advance positions.
