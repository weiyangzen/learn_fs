# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/protocol/DatanodeStorageReport.java

Purpose: `DatanodeStorageReport` groups a `DatanodeInfo` with that DataNode's per-storage `StorageReport[]`.

Important APIs/types/functions: constructor sets both final fields; getters return the datanode info and storage report array.

Control flow: produced by NameNode/reporting APIs when clients or admin commands request storage-level cluster state.

State and persistence behavior: shallowly immutable; the array reference is final but contents can be mutated by callers.

Dependencies and integration points: depends on HDFS `DatanodeInfo` and local `StorageReport`. Integrates with storage reports, balancing, and admin diagnostics.

Risks and test signals: array exposure can allow external mutation. Tests should verify consumers handle empty arrays and multiple storage reports per DataNode.
