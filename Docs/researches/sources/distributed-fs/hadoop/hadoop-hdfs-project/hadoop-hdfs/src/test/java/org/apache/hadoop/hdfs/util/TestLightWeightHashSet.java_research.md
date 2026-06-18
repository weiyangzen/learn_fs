# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestLightWeightHashSet.java

Purpose: behavioral and capacity tests for `LightWeightHashSet`, Hadoop's compact hash-set implementation.

Important APIs/types/functions: constructors with capacity/load factors, `add`, `addAll`, `contains`, `containsAll`, `remove`, `removeAll`, iterator removal, `pollAll`, `pollN`, `pollToArray`, `clear`, `toArray`, `getCapacity`, `getElement`.

Control flow: `setUp` creates 100 random integers and a default-capacity set. Tests cover empty iteration, single/multiple insertion, duplicate rejection, membership, removal by value and iterator, polling all or bounded subsets, array polling with undersized/exact/zero arrays, clearing, load-factor expansion/shrinkage, bulk remove/contains/toArray, and canonical element lookup. `TestObject` deliberately creates a distinct object equal to an inserted value to verify `getElement` returns the stored instance.

State and persistence behavior: in-memory only. Random integer data is seeded with `Time.now`, so element values vary, but assertions are set-membership based rather than fixed-order based.

Dependencies and integration points: uses SLF4J logging and Hadoop `Time`; validates collection semantics expected by HDFS internals that use memory-sensitive sets.

Risks: random duplicates in the input list could make `assertTrue(set.add(i))` fail if `rand.nextInt()` repeats, though probability is low. Capacity assertions encode power-of-two and load-factor implementation details.

Test signals: Java collection contract coverage, iterator remove safety, poll-drains-remove semantics, dynamic resizing, and canonical-object retrieval.
