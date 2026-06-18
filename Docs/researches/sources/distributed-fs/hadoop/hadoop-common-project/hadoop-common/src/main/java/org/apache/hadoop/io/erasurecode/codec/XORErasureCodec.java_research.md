# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/codec/XORErasureCodec.java

Purpose: concrete high-level XOR erasure codec.

Important APIs and control flow: constructor delegates to `ErasureCodec` and asserts the schema has exactly one parity unit. `createEncoder()` returns `XORErasureEncoder`; `createDecoder()` returns `XORErasureDecoder`.

State and persistence: no additional fields.

Dependencies and integration: selected by `CodecUtil` for `xor` schemas and bridges to XOR high-level coders.

Risks and test signals: test one-parity schema enforcement with assertions enabled and upper-layer validation with assertions disabled. XOR recovery can only tolerate one erased block, enforced more directly by grouping/recovery decisions.
