# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureDecoder.java

Purpose: abstract high-level decoder base implementing `ErasureCoder` for recovery calculations.

Important APIs and control flow: constructor stores counts/options. `calculateCoding()` delegates to subclass `prepareDecodingStep()`. Default `getInputBlocks()` concatenates data and parity blocks. Default `getOutputBlocks()` returns all erased data blocks followed by erased parity blocks. `getErasedIndexes()` computes indexes in the concatenated input array. `preferDirectBuffer()` defaults false and `release()` is no-op.

State and persistence: final count/options fields; configuration inherited from `Configured`. No persistence.

Dependencies and integration: base for RS, XOR, HH-XOR, and dummy decoders. It defines the block ordering contract passed to raw decoders.

Risks and test signals: test erased-index ordering, zero-erasure behavior, data/parity output ordering, and subclass overrides such as XOR. Block ordering mismatches will corrupt recovery.
