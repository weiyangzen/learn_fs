# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameCache.java

## Purpose
Unit test for `NameCache` dictionary promotion, lookup reuse, lookup count accounting, initialization, and reset behavior.

## Important APIs, Types, and Functions
- Uses `NameCache<String>` with use threshold 2.
- Exercises `put`, `initialized`, `size`, `reset`, and `getLookupCount`.
- Helper `verifyNameReuse` checks whether a later `put` returns an interned cached value or `null`.

## Control Flow
- Adds "matching" names twice so they reach the threshold and are promoted.
- Adds "notMatching" names once so they remain below threshold.
- Calls `initialized`, verifies promoted names are reused and dictionary size matches, then verifies below-threshold names are not reused.
- Resets, reinitializes, and verifies none of the names are reused.

## State and Persistence Behavior
- Pure in-memory dictionary/cache state.
- `lookupCount` increments only when an initialized dictionary hit occurs.

## Dependencies and Integration Points
- Tests only `NameCache`; no NameNode or filesystem integration.

## Risks and Edge Cases
- Uses object identity (`s == cache.put(s)`) to assert reuse during threshold promotion.
- Does not test concurrency, non-string keys, or memory pressure behavior.

## Test Signals
- Clear unit signal for promotion threshold, initialized lookup semantics, cache size, and reset clearing.
