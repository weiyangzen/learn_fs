# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureCoder.java

Purpose: common interface for high-level erasure encoders and decoders that calculate coding steps over `ECBlockGroup`.

Important APIs and control flow: exposes data/parity counts, `ErasureCoderOptions`, `calculateCoding(ECBlockGroup)`, direct-buffer preference, and `release()`. Implementations are also Hadoop `Configurable`.

State and persistence: interface only; lifecycle contract requires implementations to release raw coder resources.

Dependencies and integration: used by codec classes and higher-level EC managers to decouple block group planning from raw chunk computation.

Risks and test signals: implementation tests should ensure `calculateCoding()` returns valid step input/output block arrays and that `release()` closes cached native/raw resources.
