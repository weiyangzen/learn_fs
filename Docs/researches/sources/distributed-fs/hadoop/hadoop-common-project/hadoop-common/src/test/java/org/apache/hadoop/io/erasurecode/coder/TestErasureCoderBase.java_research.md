
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestErasureCoderBase.java

Purpose: Shared block-level erasure coder harness that simulates `ECBlockGroup` encoding and decoding without HDFS block IO.

Important APIs and types: Extends `TestCoderBase`. Defines `TestBlock extends ECBlock`, `testCoding()`, `performCodingStep()`, `prepareBlockGroupForEncoding()`, `backupAndEraseBlocks()`, `createEncoder()`, and `createDecoder()`. It reflects constructors accepting `ErasureCoderOptions`.

Control flow: Concrete tests set encoder and decoder classes, then `testCoding()` runs direct or heap buffers over three chunk sizes. It creates data and parity blocks, calculates an encoding step, iterates chunks through `performCoding()`, clones data, erases configured blocks, calculates a decoding step, performs it, and compares recovered blocks with backups.

State and persistence: Caches encoder and decoder instances for reuse checks. `TestBlock` stores an in-memory `ECChunk[]`; erasure is represented by nulling chunks and marking the block erased.

Dependencies and integration points: Exercises block-level `ErasureCoder`, `ErasureCodingStep`, `ECBlock`, and `ECBlockGroup` abstractions that sit above raw coders.

Risks: Reflection hides constructor errors until runtime. Reusing coder instances intentionally stresses shared internal buffers.

Test signals: Covers variable chunk sizes, direct/heap buffers, data/parity erasures, and block-group step integration.
