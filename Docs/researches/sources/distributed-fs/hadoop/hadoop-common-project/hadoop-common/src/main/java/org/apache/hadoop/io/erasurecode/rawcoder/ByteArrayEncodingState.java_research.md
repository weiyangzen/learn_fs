# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteArrayEncodingState.java

Purpose: package-private encode-call state for byte-array raw erasure encoders. It normalizes `byte[][]` inputs/outputs into a shared `EncodingState` contract with `inputOffsets`, `outputOffsets`, and `encodeLength`.

Important APIs/types/functions: public-call constructor, converted-state constructor, `convertToByteBufferState()`, and `checkBuffers(byte[][])`.

Control flow: the public constructor finds the first valid input, uses its array length as the encode length, validates input/output counts against the encoder options, ensures every input and output is non-null and exactly that length, then initializes zero offsets. `convertToByteBufferState()` clones each input range into a direct buffer and allocates direct output buffers, enabling native encoders to serve array callers.

State and persistence: per-call only. It does not move caller positions because byte arrays have no cursor; offsets are either zero for direct public calls or inherited from a heap `ByteBuffer` conversion.

Dependencies and integration: consumed by `RawErasureEncoder`, Java RS/XOR implementations, legacy RS, dummy coder, and native base classes.

Risks: array callers cannot encode slices without coming through `ByteBuffer`; native conversion allocates and copies, which is intentionally logged as inefficient elsewhere. Tests should check length validation, non-null enforcement, direct conversion copy-back through native adapters, and zero-length early-return behavior in `RawErasureEncoder`.
