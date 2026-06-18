
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestDecodingValidator.java

Purpose: Parameterized tests for `DecodingValidator`, ensuring decoded outputs can be independently validated across RS, native RS, XOR, and native XOR raw decoders.

Important APIs and types: Extends `TestRawCoderBase`; uses `DecodingValidator.validate()`, `getNewValidIndexes()`, `getNewErasedIndex()`, `InvalidDecodingException`, `CoderUtil.getValidIndexes()`, and JUnit parameter sources. Native cases are gated by `ErasureCodeNative.isNativeCodeLoaded()`.

Control flow: For each factory/layout/erasure set, it encodes data, erases chunks, decodes with least required inputs, restores marks, clones inputs and outputs, validates, then asserts input positions advance, recovered chunks and erased indexes are unchanged, and validator-selected indexes are consistent. A bad-decoding test pollutes recovered output and expects `InvalidDecodingException`.

State and persistence: Reuses an optional validator around a decoder and all chunk data is in memory.

Dependencies and integration points: Validates the safety layer that can detect silent decoder corruption.

Risks: Native parameter cases are skipped without native libraries. An empty non-parameter `testIdempotentReleases()` shadows the inherited test name but does nothing.

Test signals: Strong signal for validator correctness, immutability of caller data, and failure detection on polluted output.
