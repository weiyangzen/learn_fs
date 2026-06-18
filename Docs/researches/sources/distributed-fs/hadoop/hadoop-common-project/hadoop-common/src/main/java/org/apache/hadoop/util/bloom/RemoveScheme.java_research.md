# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/RemoveScheme.java

Purpose: `RemoveScheme` defines constants for selective-clearing strategies used by `RetouchedBloomFilter`.

Important APIs/types/functions: constants are `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.

Control flow: no executable code; consumers switch on the short constants.

State and persistence behavior: static constants only.

Dependencies and integration points: implemented by `RetouchedBloomFilter` to select which bit to clear for known false positives.

Risks: as an interface of constants, any implementing class exposes these names. Invalid short values are handled by `RetouchedBloomFilter` with `AssertionError`.

Test signals: retouched filter tests should exercise each scheme and invalid values.
