# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLightWeightGSet.java

Purpose: verifies iterator removal behavior for `LightWeightGSet`, Hadoop's linked-element hash set.

Important APIs and types: `LightWeightGSet<K,E>`, `LightWeightGSet.LinkedElement`, `put`, `iterator`, `Iterator.remove`, and `size`. `TestElement` stores an integer value and the bucket-chain `next` pointer required by the collection.

Control flow: deterministic random input is inserted into a set of capacity 16. `testRemoveAllViaIterator` walks the iterator and removes every element, then expects size zero. `testRemoveSomeViaIterator` first sums all values, computes a threshold, removes elements above that threshold during iteration, then iterates again to verify all remaining values satisfy the predicate.

State and persistence: state is in-memory bucket chains and iterator cursor/removal state. No external persistence or global state is used.

Dependencies and integration points: tests the `LinkedElement` callback contract used by many Hadoop lightweight collections and caches.

Risks: iterator removal can skip elements, corrupt chain links, fail when removing bucket heads, or leave the size counter wrong. Test signals include complete removal to zero and predicate validation after selective removals under a timeout.
