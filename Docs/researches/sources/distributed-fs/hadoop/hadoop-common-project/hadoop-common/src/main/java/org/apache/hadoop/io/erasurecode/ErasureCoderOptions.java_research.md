# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ErasureCoderOptions.java

Purpose: immutable raw/high-level coder options capturing data/parity unit counts and behavior flags.

Important APIs and control flow: constructors set `numDataUnits`, `numParityUnits`, computed `numAllUnits`, `allowChangeInputs`, and `allowVerboseDump`. Getters expose counts and flags.

State and persistence: final primitive fields only. No validation, persistence, or mutation.

Dependencies and integration: produced by `ErasureCodec` from `ECSchema` and passed into high-level and raw erasure coders.

Risks and test signals: test count propagation into raw coders and behavior when invalid counts are supplied. Since validation is external, factory tests should cover schema-to-options invariants.
