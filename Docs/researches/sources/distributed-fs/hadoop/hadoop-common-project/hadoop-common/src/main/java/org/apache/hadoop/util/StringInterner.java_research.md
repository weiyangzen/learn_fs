# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StringInterner.java

Purpose: `StringInterner` centralizes string interning choices for Hadoop callers. It exposes a strong Guava interner for values that should be retained and a JVM-backed `String.intern()` path for weak-style canonicalization that does not keep a separate Hadoop strong map.

Important APIs/types/functions: `strongIntern(String)` returns `null` for `null` and otherwise stores the canonical value in `STRONG_INTERNER`. `weakIntern(String)` returns `null` for `null` and otherwise calls `sample.intern()`. `internStringsInArray(String[])` mutates the input array in place by weak-interning every element and returns the same array.

Control flow: all public methods are small null-guarded wrappers. The array method loops linearly over indices and delegates per element to `weakIntern`, so `null` array elements survive as `null`.

State and persistence behavior: the only persistent process state is static `STRONG_INTERNER`, which retains every strongly interned string until class unloading. Weak interning delegates lifetime and canonical storage to the JVM string pool.

Dependencies and integration points: depends on Hadoop third-party Guava `Interner`/`Interners` and Hadoop audience/stability annotations. It is useful for configuration keys, paths, and repeated identifiers across Hadoop components.

Risks: `strongIntern` can create unbounded process memory retention if fed high-cardinality or user-controlled values. `internStringsInArray` mutates caller-owned arrays and does not check the array itself for `null`. `weakIntern` uses JVM global string-pool semantics, so behavior depends on the runtime rather than Hadoop-owned pruning.

Test signals: useful tests should assert null preservation, array mutation, object identity for duplicate values, and memory-sensitive callers should prefer weak interning for unbounded domains.
