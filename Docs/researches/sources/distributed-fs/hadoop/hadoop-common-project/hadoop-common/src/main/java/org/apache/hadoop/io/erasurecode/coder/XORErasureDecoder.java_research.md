# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/XORErasureDecoder.java

Purpose: high-level XOR decoder for recovering one missing data or parity block.

Important APIs and control flow: `prepareDecodingStep()` creates a raw XOR decoder through `CodecUtil`, builds default input blocks and erased indexes, uses an overridden `getOutputBlocks()` that orders erased parity blocks before data blocks, and returns `ErasureDecodingStep`.

State and persistence: no cached raw decoder; each step creates one. No persistence.

Dependencies and integration: extends `ErasureDecoder`, uses `ErasureCodeConstants.XOR_CODEC_NAME`, and delegates math to raw XOR decoder.

Risks and test signals: test one-erasure recovery, parity-before-data output ordering, and upper-layer rejection of multiple erasures. Comments contain typos but signal that recoverability is checked above this class.
