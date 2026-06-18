# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/DummyErasureEncoder.java

Purpose: high-level encoder for the dummy codec, used to isolate non-codec overhead.

Important APIs and control flow: `prepareEncodingStep()` creates a `DummyRawEncoder`, selects data input blocks and parity output blocks, and wraps them in `ErasureEncodingStep`.

State and persistence: no cached raw encoder; no persistence.

Dependencies and integration: extends `ErasureEncoder` and delegates to `DummyRawEncoder`.

Risks and test signals: useful for pipeline/performance tests, but not data-correctness tests. Verify it creates step shapes consistent with real encoders.
