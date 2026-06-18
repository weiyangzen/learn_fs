<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightLinkedSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightLinkedSet.java

## Purpose
`LightWeightLinkedSet` extends `LightWeightHashSet` with an all-element doubly linked list so iteration and polling follow insertion order.

## APIs and Types
It adds `DoubleLinkedElement<T>` with before/after pointers, tracks `head`, `tail`, and a bookmark iterator. Public additions include `pollFirst`, ordered overrides of `pollN`, `pollAll`, `toArray`, `iterator`, `clear`, `getBookmark`, and `resetBookmark`.

## Control Flow
Adds use the superclass bucket lookup but allocate `DoubleLinkedElement`, prepend to the bucket, append to the insertion-order list, and adjust bookmark if needed. Removal delegates bucket unlinking to the superclass override path, then unlinks from the doubly linked list and advances bookmark if the removed element was next. Ordered poll methods repeatedly remove from `head`. Iterators walk `after` pointers and are fail-fast; iterator removal is unsupported.

## State and Persistence
State is inherited hash table plus ordered linked-list pointers and bookmark iterator state. No persistence or synchronization.

## Dependencies and Integration
It depends on `LightWeightHashSet` internals and Java iterator exceptions. It is used where low overhead and stable insertion-order traversal/polling are needed.

## Risks
It is tightly coupled to superclass `removeElem` returning the exact linked element. Bookmark state is mutated by `getBookmark`, which may be surprising. Iterator remove is unsupported even though the superclass iterator supports it. Like the superclass, it does not null-terminate oversized arrays.

## Test Signals
Tests should cover insertion-order iteration, duplicate handling, remove head/tail/middle, pollFirst, pollN ordering, pollAll ordering and clear, bookmark progression/removal/reset, fail-fast iteration, and resizing while preserving order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/LightWeightLinkedSet.java -->
