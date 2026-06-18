# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawDecoder.java

Purpose: JNI-backed XOR raw decoder using Intel ISA-L.

Important APIs/types/functions: native load check, constructor/native `initImpl`, `performDecodeImpl()`, `release()`, native `decodeImpl()` and `destroyImpl()`.

Control flow: construction initializes native XOR state under `decoderLock`. Decode requests flow through `AbstractNativeRawDecoder`, including offset capture and closed-state checking, then call JNI with inputs, erased indexes, outputs, and offsets. Release destroys native state under write lock.

State and persistence: native coder state is object-scoped; no durable state.

Dependencies and integration: depends on `ErasureCodeNative`, `ErasureCoderOptions`, and native base decoder; factory is `NativeXORRawErasureCoderFactory`.

Risks: this class does not override `preferDirectBuffer()`, but inherits `true` from `AbstractNativeRawDecoder`. Tests should cover one-erasure XOR decode semantics, native availability, release behavior, direct/heap conversion, and parity with `XORRawDecoder`.
