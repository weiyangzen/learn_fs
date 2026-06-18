
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestXORCoder.java

Purpose: Tests block-level XOR erasure coding for a 10 data, 1 parity layout.

Important APIs and types: Uses `XORErasureEncoder`, `XORErasureDecoder`, inherited `TestErasureCoderBase`, and JUnit timeout coverage.

Control flow: `setup()` sets coder classes, 10 data units, 1 parity unit, and 10 chunks per block. One test erases the parity block with heap buffers and repeats to validate reuse. Another erases data block 5 and alternates direct and heap buffers across repeated calls.

State and persistence: All data is generated in memory by the inherited harness. Encoder and decoder reuse is intentional inside repeated calls.

Dependencies and integration points: Validates the block-level XOR coder facade above raw XOR coding primitives.

Risks: XOR can recover only one missing unit; the test matrix is appropriately narrow but does not cover invalid multi-erasure paths at the block level.

Test signals: Confirms parity reconstruction, data reconstruction, and mixed ByteBuffer compatibility for XOR block coders.
