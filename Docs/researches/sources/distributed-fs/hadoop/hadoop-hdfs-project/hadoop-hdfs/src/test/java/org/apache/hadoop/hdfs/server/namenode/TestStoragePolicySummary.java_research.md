# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStoragePolicySummary.java

## Purpose

`TestStoragePolicySummary` verifies aggregation, canonical formatting, policy matching annotations, and descending-count sorting for `StoragePolicySummary`.

## Important APIs, Types, and Functions

The test uses `BlockStoragePolicySuite.createDefaultSuite`, `BlockStoragePolicy` instances for `HOT`, `WARM`, and `COLD`, `StorageType` arrays, `StoragePolicySummary.add`, `StoragePolicySummary.sortByComparator`, and `StorageTypeAllocation.toString`.

## Control Flow

Each test adds synthetic block storage allocations under specified policies, converts the internal `storageComboCounts` map into an ordered string map, and compares exact expected strings and counts. Scenarios cover repeated HOT counts, equivalent WARM allocations in different storage-type order, mismatches between specified and actual policy, and sorting by descending count.

## State and Persistence Behavior

State is the in-memory summary map from `StorageTypeAllocation` to occurrence count. There is no persistence, but the output format is CLI/report-facing behavior.

## Dependencies and Integration Points

This tests NameNode reporting around block storage policy summaries. It depends on default policy definitions and the textual representation used to explain whether actual storage types match the requested policy.

## Risks and Edge Cases

Incorrect canonicalization can double-count equivalent allocations with different input ordering. Incorrect matching can hide policy violations. Sorting instability can change user-visible reports.

## Test Signals

Signals include exact strings such as `HOT|DISK:3(HOT)` and `COLD|DISK:1,ARCHIVE:2(WARM)`, expected map sizes, expected counts, and ordered string output for descending count.
