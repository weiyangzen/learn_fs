# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawEncoder.java

Purpose: JNI-backed Reed-Solomon raw encoder using Intel ISA-L.

Important APIs/types/functions: static `ErasureCodeNative.checkNativeCodeLoaded()`, constructor/native `initImpl`, `performEncodeImpl()`, `release()`, `preferDirectBuffer()`, native `encodeImpl()` and `destroyImpl()`.

Control flow: constructor initializes native RS state under the encoder write lock. Public encode calls use `AbstractNativeRawEncoder`, which rejects closed native state, gathers input/output offsets, and calls this class's JNI delegate. `release()` destroys native resources under the write lock.

State and persistence: native coder state persists for the encoder object lifetime only.

Dependencies and integration: created by `NativeRSRawErasureCoderFactory`; integrates with the same `RawErasureEncoder` API and prefers direct buffers for performance.

Risks: native library/configuration dependence and JNI resource lifecycle dominate. Array inputs are converted and copied, so tests should cover direct-buffer fast path, heap-array fallback copy-back, release behavior, and parity equivalence with `RSRawEncoder` for representative schemas.
