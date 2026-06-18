
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestHHErasureCoderBase.java

Purpose: Specializes the block-level harness for Hitchhiker-style coders that process multiple sub-packets per coding step.

Important APIs and types: Extends `TestErasureCoderBase`, adds `subPacketSize`, and overrides `performCodingStep(ErasureCodingStep)`. It works with `ECBlock`, `ECChunk`, and `ErasureCodingStep.performCoding()`.

Control flow: For each block chunk index advanced by `subPacketSize`, the override flattens chunks for all input blocks across each sub-packet into a single input array, allocates matching output chunks, writes them back into output blocks, then invokes `performCoding()` once per sub-packet group. The step is finished after all grouped chunks are processed.

State and persistence: Uses inherited block/chunk state and mutable `subPacketSize`, defaulting to 2. No persistent state exists.

Dependencies and integration points: Provides the test execution model for `HHXORErasureEncoder` and `HHXORErasureDecoder`, whose steps expect sub-packeted input and output arrays.

Risks: `numChunksInBlock` must be a multiple of `subPacketSize`; otherwise chunk indexing would overrun. IOException is converted to test failure.

Test signals: Validates that Hitchhiker steps handle batched sub-packet buffer ordering.
