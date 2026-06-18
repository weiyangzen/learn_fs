# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/ErasureEncoder.java

Purpose: abstract high-level encoder base implementing `ErasureCoder` for parity generation.

Important APIs and control flow: constructor stores counts/options. `calculateCoding()` delegates to subclass `prepareEncodingStep()`. `getInputBlocks()` returns data blocks; `getOutputBlocks()` returns parity blocks. Direct-buffer preference defaults false and `release()` defaults no-op.

State and persistence: final data/parity counts and options; Hadoop configuration from `Configured`. No persistence.

Dependencies and integration: base for RS, XOR, HH-XOR, and dummy encoders. It defines the normal data-to-parity block mapping for encoding steps.

Risks and test signals: test block array selection and count propagation. Subclasses with cached raw encoders should override `release()` as RS and HH-XOR do.
