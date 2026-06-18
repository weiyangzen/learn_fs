# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/XORErasureEncoder.java

Purpose: high-level XOR encoder that creates parity with a raw XOR encoder.

Important APIs and control flow: `prepareEncodingStep()` creates a raw XOR encoder through `CodecUtil`, selects data blocks and parity output blocks, and returns `ErasureEncodingStep`.

State and persistence: no cached raw encoder; no persistence.

Dependencies and integration: extends `ErasureEncoder` and delegates to configured raw XOR encoder.

Risks and test signals: test parity generation, raw coder fallback, and resource release via step `finish()`. Repeated step creation creates repeated raw encoders, unlike RS/HH-XOR cached implementations.
