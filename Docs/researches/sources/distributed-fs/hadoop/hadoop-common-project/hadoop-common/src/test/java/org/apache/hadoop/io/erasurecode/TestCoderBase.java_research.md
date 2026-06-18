
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCoderBase.java

Purpose: Provides shared test utilities for both block-level and raw erasure coder tests, especially ByteBuffer allocation, chunk generation, erasure simulation, cloning, comparison, and diagnostics.

Important APIs and types: Defines `prepare()`, `setChunkSize()`, `prepareBufferAllocator()`, `prepareDataChunksForEncoding()`, `prepareParityChunksForEncoding()`, `prepareOutputChunksForDecoding()`, `backupAndEraseChunks()`, `cloneChunksWithData()`, `compareAndVerify()`, `markChunks()`, `restoreChunksFromMark()`, and corruption helpers. It uses `ECChunk`, `BufferAllocator.SimpleBufferAllocator`, `SlicedBufferAllocator`, `Configuration`, and `DumpUtil`.

Control flow: Tests call `prepare()` to set data/parity counts, erased indexes, configuration, and fixed-data mode. Encoding inputs and decoding outputs are generated with alternating zero-offset and nonzero-position buffers. Erased chunks are backed up, nulled in the input arrays, then later compared against recovered chunks.

State and persistence: Holds mutable per-test settings such as chunk size, allocator, direct-buffer mode, fixed data, erased indexes, and `allowChangeInputs`. No durable state exists, but static `Random` and fixed-data generator affect reproducibility.

Dependencies and integration points: Used by `TestErasureCoderBase`, `TestRawCoderBase`, and decoder validation tests.

Risks: Alternating buffer offsets catches position/limit bugs, but random data and static generator state make failures less deterministic unless fixed data is enabled. Corruption helpers choose random chunks.

Test signals: Enables broad checks for direct versus heap buffers, input mutation, erased index translation, and output equality.
