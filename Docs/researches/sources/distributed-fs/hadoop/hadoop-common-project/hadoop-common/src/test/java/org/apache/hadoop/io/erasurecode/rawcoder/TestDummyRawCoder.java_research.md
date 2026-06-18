
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestDummyRawCoder.java

Purpose: Tests the dummy raw erasure coder, whose expected behavior is to produce zero-filled parity and recovered chunks rather than real erasure recovery.

Important APIs and types: Extends `TestRawCoderBase`, selects `DummyRawErasureCoderFactory`, uses `ECChunk`, `ByteBuffer.wrap()`, inherited buffer allocation, and zero chunk bytes from `TestCoderBase`.

Control flow: Setup selects the dummy factory, disables dumps, and sets the base chunk size. Two tests prepare 6x3 layouts with data-only and data-plus-parity erasures, then run a custom `testCoding()`: encode generated data, compare parity chunks against zero chunks, erase inputs, decode, and compare recovered chunks against zero chunks.

State and persistence: All data is in memory. The custom test marks data chunks before encode and restores them before decode.

Dependencies and integration points: Provides coverage for the no-op raw coder used by benchmark and testing paths.

Risks: It intentionally does not validate reconstruction of original bytes. `getEmptyChunks()` wraps the same zero byte array repeatedly, so mutation by a coder would couple expected chunks.

Test signals: Confirms dummy coder output contract for direct and heap buffers.
