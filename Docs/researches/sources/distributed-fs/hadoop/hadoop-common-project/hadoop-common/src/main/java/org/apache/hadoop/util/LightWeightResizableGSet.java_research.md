# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightResizableGSet.java

## Purpose

`LightWeightResizableGSet` adds synchronized access and table growth to `LightWeightGSet`, resizing when element count exceeds a configurable load-factor threshold.

## Important APIs, Types, And Functions

Constructors accept initial capacity and optional load factor, with defaults of 16 and 0.75. It synchronizes `put()`, `get()`, `remove()`, `size()`, `getIterator(Consumer<Iterator<E>>)` and resizing helpers `resize()` and `expandIfNecessary()`.

## Control Flow, State, And Persistence

Construction rounds capacity, initializes `hash_mask`, threshold, and buckets. `put()` delegates to the parent insertion then expands if `size > threshold` and below max capacity. `resize()` allocates a new bucket array and relinks every existing `LinkedElement` into its new bucket. State is inherited hash table plus capacity/load-factor fields; no persistence.

## Dependencies And Integration Points

It depends on `LightWeightGSet`, `HadoopIllegalArgumentException`, Java `Consumer`, and iterators. It is appropriate where the low-memory linked-element representation is desired but initial cardinality is uncertain.

## Risks And Test Signals

Returning iteration through a consumer under synchronization controls concurrent access, but callers must not retain and use the iterator after the synchronized callback if they need safety. Tests should cover constructor validation, expansion boundaries, rehash correctness, synchronized get/remove, iterator callback behavior, and max-capacity behavior.
