# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WeakReferenceThreadMap.java

## Purpose
Thread-id keyed WeakReferenceMap convenience class for per-thread values without strong retention.

## Important APIs, Types, and Functions
getForCurrentThread(), removeForCurrentThread(), currentThreadId(), setForCurrentThread().

## Control Flow
Methods use current Thread.getId as key. setForCurrentThread avoids replacing when the existing weak reference resolves to the same object; otherwise it puts the new value and returns old.

## State and Persistence Behavior
Stores weak references in superclass; values may be GCd and referenceLost callback may run.

## Dependencies and Integration Points
Depends on org.apache.hadoop.util.WeakReferenceMap. Useful for thread-local-like caches with cleanup hooks.

## Risks and Test Signals
Risks are thread id reuse, GC timing, and non-null requirement on set. Tests should cover same-object set, replacement, remove, factory creation, and reference-lost callback.
