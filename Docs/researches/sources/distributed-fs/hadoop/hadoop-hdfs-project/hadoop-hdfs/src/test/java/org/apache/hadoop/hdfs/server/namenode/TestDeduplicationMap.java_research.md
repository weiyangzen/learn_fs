# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeduplicationMap.java

Purpose: Unit test for `FSImageFormatProtobuf.SaverContext.DeduplicationMap`, confirming stable numeric IDs for repeated values during protobuf fsimage save.

Important APIs/types/functions: Uses `DeduplicationMap.newMap()` and `getId(T)`.

Control flow: Creates a map, requests IDs for `"1"`, `"2"`, and `"3"`, then requests the same values again. The first pass should allocate monotonically increasing IDs starting at 1; the second pass should return the same IDs.

State and persistence behavior: The state is in-memory deduplication metadata used during image serialization. No filesystem or NameNode state is involved.

Dependencies and integration points: Production integration is fsimage protobuf saving, where repeated values are represented by stable compact IDs.

Risks: A regression could allocate duplicate IDs or reassign existing values, corrupting references in serialized images.

Test signals: Six equality checks validate ID allocation and reuse.
