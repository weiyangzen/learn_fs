# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StoragePolicySummary.java

## Purpose

`StoragePolicySummary.java` aggregates actual block storage-type allocations against each block's specified storage policy and renders a human-readable compliance summary. The source was read as a complete 260-line file.

## Important APIs, Types, and Functions

The class owns `storageComboCounts`, `storagePolicies`, and `totalBlocks`. Key methods are constructor, `add`, `sortByComparator`, `toString`, and `getStoragePolicy`. The nested `StorageTypeAllocation` stores sorted `StorageType[]`, specified and actual `BlockStoragePolicy`, formats descriptors, checks `policyMatches`, and implements equality/hash code.

## Control Flow

Callers add each block's storage type array and specified policy. `add` wraps the pair in `StorageTypeAllocation`, increments the count, and computes the matching actual policy for first-time combinations. `getStoragePolicy` sorts each candidate policy's storage types and matches it as a prefix, allowing extra replicas of the final storage type. `toString` sorts combinations by block count descending and emits separate compliant and non-compliant tables with percentages.

## State and Persistence Behavior

The summary is transient report state. It mutates input storage arrays by sorting them inside `StorageTypeAllocation`, so callers should not rely on the original ordering after calling `add`.

## Dependencies and Integration Points

It integrates with `BlockStoragePolicy`, `StorageType`, and NameNode reporting paths that inspect block placement and storage policy compliance.

## Risks and Edge Cases

`totalBlocks` can be zero if `toString` is called before any `add`, producing no rows but avoiding division because the loop is empty. Mutating the passed `StorageType[]` is a subtle side effect. Actual policy matching depends on sorted order and duplicate handling; changes to policy semantics need matching updates here.

## Test Signals

Tests should cover compliant and non-compliant mixes, duplicate storage types, extra replicas matching the last policy type, unknown actual policy, sorted output by count, percentage formatting, equality/hash behavior, and caller-visible mutation expectations.
