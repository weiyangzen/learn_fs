# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawDecoder.java

Purpose: JNI-backed Reed-Solomon raw decoder using Intel ISA-L.

Important APIs/types/functions: static native-code load check, constructor calling native `initImpl`, `performDecodeImpl()`, `release()`, `preferDirectBuffer()`, native `decodeImpl()` and `destroyImpl()`.

Control flow: class loading verifies native erasure code availability. Construction initializes a native coder under the write lock inherited from `AbstractNativeRawDecoder`. Decode calls enter the base native class, which captures ByteBuffer offsets and delegates to `performDecodeImpl`; this class forwards to JNI. `release()` destroys native state under the write lock.

State and persistence: native coder pointer lives in the superclass private field and is owned for the Java object lifetime. No durable state.

Dependencies and integration: depends on `ErasureCodeNative`, `ErasureCoderOptions`, and `AbstractNativeRawDecoder`; produced by `NativeRSRawErasureCoderFactory`.

Risks: unavailable native libraries fail at class load/construction; using after `release()` raises `IOException` in the base class. Tests should cover native availability gating, direct-buffer preference, release idempotency expectations, decode correctness against Java RS, and array-call conversion through direct buffers.
