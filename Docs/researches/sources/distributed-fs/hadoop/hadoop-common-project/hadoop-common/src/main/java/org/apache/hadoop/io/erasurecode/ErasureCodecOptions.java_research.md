# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCodecOptions.java

Purpose: small options carrier for high-level erasure codecs, currently wrapping only an `ECSchema`.

Important APIs and control flow: constructor stores schema; `getSchema()` returns it. No validation or derived behavior.

State and persistence: one mutable-reference field; no persistence.

Dependencies and integration: passed into `ErasureCodec` constructors by `CodecUtil`, then used to derive `ErasureCoderOptions`.

Risks and test signals: test null-schema behavior at callers, because this class does not reject null. Future options should consider immutability and compatibility.
