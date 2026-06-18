# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IdentityHashStore.java

## Purpose

`IdentityHashStore` is a compact identity-based key/value store. Keys are compared with `==` rather than `equals()`, making it useful for object-identity tracking.

## Important APIs, Types, And Functions

The class stores alternating key/value entries in an `Object[]`. Important APIs are the constructor, `put(K,V)`, `get(K)`, `remove(K)`, `numElements()`, `capacity()`, `isEmpty()`, `visitAll(Visitor<K,V>)`, and the `Visitor` callback interface. Internal helpers compute identity hashes, probe open-addressed slots, and reallocate on growth.

## Control Flow, State, And Persistence

Insert probes by identity hash until it finds a free slot; inserting the same key multiple times creates multiple mappings rather than replacing. Lookups scan the full probe cycle for the first identical key. Remove clears the found entry without compacting clusters, relying on full-cycle lookup rather than stopping at empty slots. State is in-memory array contents, size, and capacity; there is no synchronization or persistence.

## Dependencies And Integration Points

It depends mainly on Java arrays and `Preconditions`. It integrates with low-level Hadoop code that needs identity semantics without the overhead or behavior of ordinary maps.

## Risks And Test Signals

Open addressing is sensitive to deletion and duplicate-key behavior. Tests should cover identity-distinct equal objects, null-key rejection on put, duplicate inserts of the same key, collision clusters, removal followed by lookup of later clustered entries, expansion, and `visitAll()` traversal.
