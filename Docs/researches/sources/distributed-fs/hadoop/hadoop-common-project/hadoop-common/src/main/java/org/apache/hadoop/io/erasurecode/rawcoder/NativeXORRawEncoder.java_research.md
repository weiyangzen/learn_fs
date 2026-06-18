# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawEncoder.java

Purpose: JNI-backed XOR raw encoder using Intel ISA-L.

Important APIs/types/functions: static native-code check, constructor/native `initImpl`, `performEncodeImpl()`, `release()`, native `encodeImpl()` and `destroyImpl()`.

Control flow: construction initializes native state under encoder write lock. Public encode calls in `AbstractNativeRawEncoder` validate native state, capture buffer offsets, and delegate to this class's JNI method. Release destroys the native coder under lock.

State and persistence: native pointer is object-scoped in the superclass.

Dependencies and integration: created by `NativeXORRawErasureCoderFactory`; participates in the same raw encoder API as Java XOR and inherits direct-buffer preference.

Risks: native dependency and heap-call conversion overhead. Tests should validate direct path, array fallback copy-back, release/closed behavior, and output parity equivalence with Java XOR for varied data lengths including non-8-byte multiples.
