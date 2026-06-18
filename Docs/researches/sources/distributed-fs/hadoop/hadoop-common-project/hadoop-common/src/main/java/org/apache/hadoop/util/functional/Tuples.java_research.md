# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/functional/Tuples.java

`Tuples` provides a tiny public tuple facility without adding a third-party tuple dependency. The exposed API is `pair(K, V)`, returning a `Map.Entry<K, V>`.

The returned implementation is private immutable `Tuple<K,V>`. It stores final `key` and `value`, returns them through `getKey()` and `getValue()`, rejects mutation through `setValue()` with `UnsupportedOperationException`, formats as `(key, value)`, and implements value equality/hash code using `Objects.equals()` and `Objects.hash()`. There is no mutable state, persistence, synchronization, or external resource behavior.

Dependencies are Java `Map.Entry`, `Objects`, and Hadoop `InterfaceStability.Unstable`. Integration is as a lightweight API return/container type where callers need a pair without coupling Hadoop APIs to external libraries or newer Java tuple-like constructs. Risks are mostly API expectations: because it is returned as `Map.Entry`, some callers may expect `setValue()` to work; equality requires the same private `Tuple` class rather than accepting arbitrary `Map.Entry` implementations, so equality is not fully interface-polymorphic. Test signals are likely indirect through users of `pair()`; this file has no dedicated test surfaced in the scanned subset.
