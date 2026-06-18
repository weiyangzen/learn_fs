# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteBufferEncodingState.java

Purpose: per-call encoding state for `ByteBuffer` inputs/outputs. It records the logical slice length, homogeneous direct/heap mode, and buffer arrays for low-level encoders.

Important APIs/types/functions: main constructor, converted-state constructor, `convertToByteArrayState()`, and `checkBuffers(ByteBuffer[])`.

Control flow: the main constructor uses the first valid input to set `encodeLength` and `usingDirectBuffer`, validates input/output counts through `EncodingState`, then rejects null buffers, mismatched `remaining()`, or mixed directness. Heap buffers can be converted to byte arrays by capturing array offsets at current positions.

State and persistence: per-call only. It does not itself advance positions; `RawErasureEncoder` snapshots and advances non-null input positions after encoding.

Dependencies and integration: used by all encoder implementations through `RawErasureEncoder.encode(ByteBuffer[], ...)`; native encoders prefer direct mode, while Java encoders can serve both direct and heap.

Risks: the conversion path assumes array-backed heap buffers; direct buffers use native/ByteBuffer code. Output positions are not restored or flipped by this class, so integration tests should verify caller-visible cursor semantics in `RawErasureEncoder`, length validation, directness homogeneity, and heap-array offsets for sliced buffers.
