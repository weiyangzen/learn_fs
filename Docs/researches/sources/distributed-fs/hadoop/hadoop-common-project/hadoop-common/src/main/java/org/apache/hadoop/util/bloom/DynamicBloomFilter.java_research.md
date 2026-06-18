# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/DynamicBloomFilter.java

Purpose: `DynamicBloomFilter` grows by adding rows of standard Bloom filters once the active row reaches a configured record threshold.

Important APIs/types/functions: constructor accepts vector size, hash count/type, and per-row threshold `nr`. `add(Key)` inserts into the active row or creates a new row. `membershipTest(Key)` checks each row. `and`, `or`, `xor`, `not`, `toString`, `write`, and `readFields` operate across the row matrix. Private `addRow` and `getActiveStandardBF` manage matrix growth.

Control flow: insert obtains the last row when `currentNbRecord < nr`; otherwise it appends a new `BloomFilter`, resets `currentNbRecord`, inserts, then increments. Membership returns true if any row matches. Logical operations require another `DynamicBloomFilter` with same vector size, hash count, row count, and `nr`, then delegate row-by-row.

State and persistence behavior: stores `nr`, `currentNbRecord`, and an array of mutable `BloomFilter` rows. Writable state serializes inherited metadata, threshold, current record count, row count, and each row.

Dependencies and integration points: extends `Filter` and composes `BloomFilter`.

Risks: `membershipTest(null)` returns true, unlike other Bloom implementations that throw on null; this can hide caller bugs. `currentNbRecord` tracks only the latest row and does not deduplicate keys, so repeated adds drive growth. Logical operations require identical row counts, limiting combining independently grown filters. Not thread-safe.

Test signals: tests should cover row growth at threshold, null membership behavior, serialization preserving rows/current count, and compatibility checks for logical operations.
