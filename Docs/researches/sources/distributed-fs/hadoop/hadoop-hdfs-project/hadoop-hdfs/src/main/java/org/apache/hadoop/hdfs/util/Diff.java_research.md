<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Diff.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Diff.java

## Purpose
`Diff` represents changes between a previous sorted element list and a current sorted element list using two sorted lists: created elements and deleted elements. It supports create/delete/modify, undo, lookup in previous/current views, applying diffs, and combining posterior diffs.

## APIs and Types
`Element<K>` supplies comparable keyed elements. `Processor<E>` handles overwritten/deleted elements during combine. `Container<E>` wraps a determinate lookup result that may be null. `UndoInfo<E>` stores data for undoing delete/modify. Public methods expose created/deleted lists, mutation operations, undo operations, previous/current accessors, apply-to-previous/current transforms, combination, and `toString`.

## Control Flow
Mutations binary-search sorted created/deleted lists. `create` inserts into created. `delete` removes a newly created element or inserts into deleted. `modify` replaces a created element or records old in deleted and new in created. `accessPrevious` and `accessCurrent` swap list roles to determine if a key is known present/absent. `apply2Previous` subtracts deleted from previous, then merges created. `apply2Current` reverses the operation. `combinePosterior` merges another diff by replaying create, delete, or modify cases in sorted order.

## State and Persistence
State is two lazily allocated sorted `List<E>` fields. No persistence or synchronization. Correctness relies on object identity in some remove/contains paths and sorted list invariants.

## Dependencies and Integration
It depends on Java collections and Hadoop `Preconditions`. It is a core utility for snapshot/diff-like namespace state handling where compact reversible list changes are needed.

## Risks
Callers must provide elements whose `compareTo(K)` and `getKey()` remain stable. Undo methods are explicitly undefined unless called for the immediately corresponding previous operation with returned `UndoInfo`. Some code paths use negative binary-search insertion points in `remove`, which is correct for undo insertion-point semantics but brittle if list state changed. The class is not thread-safe and can throw `AssertionError`/`Preconditions` on invariant violations.

## Test Signals
Tests should cover all documented state cases, sorted insertion/removal, create-delete cancellation, delete-create replacement, repeated modify, undo for each operation, access previous/current known-present/known-absent/unknown cases, apply round trips, combinePosterior with a deleted processor, and invariant violation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/Diff.java -->
