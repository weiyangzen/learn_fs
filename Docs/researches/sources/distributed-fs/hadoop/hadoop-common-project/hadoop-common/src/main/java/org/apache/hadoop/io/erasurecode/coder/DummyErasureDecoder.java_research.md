# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/DummyErasureDecoder.java

Purpose: high-level decoder for the dummy codec, intended for tests and performance isolation.

Important APIs and control flow: `prepareDecodingStep()` creates a `DummyRawDecoder`, builds input blocks via base decoder logic, calculates erased indexes, selects output blocks, and returns `ErasureDecodingStep`.

State and persistence: no cached raw decoder; each coding step creates a new dummy raw decoder. No persistence.

Dependencies and integration: extends `ErasureDecoder` and uses `DummyRawDecoder`, `ECBlockGroup`, and `ErasureDecodingStep`.

Risks and test signals: verify erased-index ordering and output-block selection match base decoder behavior. It should not be used to validate data correctness because it performs no real reconstruction.
