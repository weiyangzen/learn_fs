# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestReferenceCountMap.java

Purpose: verifies `ReferenceCountMap` counting and thread-safe behavior using `AclFeature` instances.

Important APIs/types/functions: `ReferenceCountMap.put`, `remove`, `getReferenceCount`, `getUniqueElementsSize`, inner `PutThread`, inner `RemoveThread`, `SubjectInheritingThread`.

Control flow: the single-thread test inserts two ACL features, repeats insertions to raise counts, removes once, and checks remaining counts and unique element size. The concurrent test starts two put threads, each adding both features 10000 times, joins them, verifies count `2 * LOOP_COUNTER`, then starts one remove thread that removes both features 10000 times and verifies counts drop to `LOOP_COUNTER`.

State and persistence behavior: in-memory counters only. The two `AclFeature` objects are shared across threads as fields.

Dependencies and integration points: models NameNode feature deduplication/reference counting, especially ACL feature sharing. `SubjectInheritingThread` preserves security subject context in Hadoop test infrastructure.

Risks: concurrent test only overlaps put-put, then remove after joins; it does not test simultaneous put/remove interleavings. It assumes `AclFeature` equality/hash behavior based on contained int arrays.

Test signals: count increments, decrements without removing unique entries too early, unique element cardinality, and concurrent add/remove totals.
