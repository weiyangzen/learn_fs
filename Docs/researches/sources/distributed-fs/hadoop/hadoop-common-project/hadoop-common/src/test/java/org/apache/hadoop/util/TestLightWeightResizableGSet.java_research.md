# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightResizableGSet.java

Purpose: tests `LightWeightResizableGSet`, the resizable variant of Hadoop's lightweight linked-element set, under large insert/update/remove workloads.

Important APIs and types: `LightWeightResizableGSet<K,E>`, `LinkedElement`, `put`, `get`, `contains`, `remove`, `values`, `clear`, `iterator`, and random `TestKey`/`TestElement` helpers.

Control flow: `testBasicOperations` generates 65,536 unique long keys, inserts all elements, validates size and retrieval, creates replacement elements with the same keys and new data, inserts them as updates, verifies values changed without size growth, checks `values()`, and removes every key. `testRemoveAll` validates both `clear()` and iterator-based removal after repopulating the set.

State and persistence: all state is in-memory hash table capacity, linked bucket nodes, and element `next` pointers. Test data uniqueness is maintained by a `HashSet<Long>`.

Dependencies and integration points: uses AssertJ assertions and SLF4J logging; validates the collection contract relied on by memory-sensitive Hadoop structures.

Risks: resizing can lose entries, replacement can inflate size, `values()` can omit elements, iterator removal can corrupt buckets, and clear can leave stale linked nodes. Test signals cover large cardinality, key-equality lookup with separate key objects, and full removal checks.
