# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/RetouchedBloomFilter.java

Purpose: `RetouchedBloomFilter` extends `BloomFilter` with false-positive tracking and selective bit clearing to remove selected false positives while accepting introduced false negatives.

Important APIs/types/functions: `add(Key)` records keys in `keyVector` for every hashed bit. `addFalsePositive` overloads record known false positives in `fpVector`. `selectiveClearing(Key, short)` chooses a bit using `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, or `RATIO` and clears it. Helpers include `randomRemove`, `minimumFnRemove`, `maximumFpRemove`, `ratioRemove`, `clearBit`, `removeKey`, `computeRatio`, `getWeight`, and `createVector`. Writable methods persist base bits plus false-positive vectors, key vectors, and ratios.

Control flow: insertion sets bits and appends the key to per-position synchronized lists. False-positive insertion appends to `fpVector` positions but does not set bits. Selective clearing verifies the target currently tests as a member, hashes it, selects an index according to weighted lists, then clears the bit and removes affected keys/false positives from all their hashed lists.

State and persistence behavior: inherited `BitSet` plus arrays of synchronized `List<Key>` for recorded keys and false positives, a ratio array, and lazily initialized `Random`. Serialization writes every list and ratio after the base Bloom filter state.

Dependencies and integration points: extends `BloomFilter` and implements `RemoveScheme`; uses `Key` weights to estimate false-negative/false-positive tradeoffs.

Risks: `randomRemove` returns an index in `[0, nbHash)`, not a hashed bit position, while other schemes return positions from the hashed vector; this means random clearing can clear an unrelated low-index bit. The synchronized lists are not used with external synchronization during iteration/removal, so compound operations are not thread-safe. Stored `Key` objects are mutable, which can corrupt list removal semantics. Serialization can be large because it stores per-bit key lists.

Test signals: tests should cover all selective schemes, especially random index semantics, list cleanup after clearing, serialization with populated vectors, null handling, and false-negative tradeoffs after clearing.
