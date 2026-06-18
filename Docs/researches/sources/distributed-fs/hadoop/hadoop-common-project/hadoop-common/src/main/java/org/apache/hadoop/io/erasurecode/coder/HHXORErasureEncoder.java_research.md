# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureEncoder.java

Purpose: high-level Hitchhiker-XOR encoder that composes RS raw encoding with XOR raw encoding.

Important APIs and control flow: lazily creates cached RS and XOR raw encoders through `CodecUtil`; `prepareEncodingStep()` selects data/parity blocks and returns `HHXORErasureEncodingStep`; `release()` releases both cached encoders.

State and persistence: caches raw encoder references in memory. No persistence.

Dependencies and integration: extends `ErasureEncoder`, uses RS and XOR raw coders, and creates the HH-XOR-specific encoding step.

Risks and test signals: test raw coder fallback for both codecs, repeated coding step creation with cached encoders, and release idempotence. Configuration must support both RS and XOR raw coders.
