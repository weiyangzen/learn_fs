
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderBase.java

Purpose: Shared XOR raw-coder matrix for one-parity recovery and negative cases.

Important APIs and types: Extends `TestRawCoderBase` and defines tests using `prepare()`, `testCodingDoMixAndTwice()`, `testCodingWithErasingTooMany()`, `testCodingWithBadInput()`, and `testCodingWithBadOutput()`.

Control flow: Positive tests cover 10 data plus 1 parity with erased data index 0, erased parity index 0, and erased data index 5. The too-many-erasure test removes one data and one parity unit and expects failure. The bad-input/output test corrupts buffers around data index 5 and expects failures.

State and persistence: Uses inherited mutable erased indexes, chunk data, coders, and direct/heap buffer modes.

Dependencies and integration points: Inherited by Java XOR, native XOR, and intended Java/native interoperability wrappers.

Risks: XOR's single-parity contract means this base should stay limited to one recoverable erasure in positive tests. Random corruption can affect exact failure location.

Test signals: Covers single-erasure XOR recovery, error handling, and mixed ByteBuffer operation.
