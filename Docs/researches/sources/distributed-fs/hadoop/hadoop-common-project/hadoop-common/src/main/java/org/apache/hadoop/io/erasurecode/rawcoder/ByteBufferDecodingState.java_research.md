# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteBufferDecodingState.java

Purpose: per-call decoding state for `ByteBuffer` inputs, including erased indexes, output buffers, direct/heap mode, and the common `decodeLength`.

Important APIs/types/functions: main constructor, converted-state constructor, `convertToByteArrayState()`, `checkInputBuffers()`, and `checkOutputBuffers()`.

Control flow: the constructor selects the first non-null input to infer `decodeLength` and directness, validates array sizes and recoverability through `DecodingState`, then checks every non-null input has matching `remaining()` and buffer type. Outputs must be non-null, same `remaining()`, and same directness. Heap buffers can be converted to arrays by recording `arrayOffset() + position()` for each buffer.

State and persistence: per-call only. It captures cursor-relative ranges, and `RawErasureDecoder` later advances non-null input positions by `decodeLength`; output positions are managed by caller/coder behavior.

Dependencies and integration: central for `RawErasureDecoder.decode(ByteBuffer[], ...)`, ECChunk decoding, Java coders, and native JNI coders.

Risks: `convertToByteArrayState()` assumes heap buffers expose backing arrays; this is safe because callers with direct buffers bypass conversion, but read-only or non-array heap buffers would fail if accepted. Tests should cover direct/heap mixing rejection, enough valid inputs, output length mismatch, null outputs, and position/array-offset preservation.
