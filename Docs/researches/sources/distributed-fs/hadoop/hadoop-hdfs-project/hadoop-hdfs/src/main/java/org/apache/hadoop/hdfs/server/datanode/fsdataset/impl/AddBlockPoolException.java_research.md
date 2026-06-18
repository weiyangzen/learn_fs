# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/AddBlockPoolException.java

Purpose: runtime exception used to aggregate IO failures encountered while adding or scanning block pools across multiple volumes.

Important APIs/types/functions: constructors accept an existing `Map<FsVolumeSpi, IOException>` or create a new `ConcurrentHashMap`. `mergeException` merges another aggregate while preserving the first exception per volume. `hasExceptions` reports whether failures exist. `getFailingVolumes` exposes the volume-to-exception map. `toString` includes the map.

Control flow: block-pool initialization code can collect failures per volume and throw or merge them after parallel work. When merging, later errors for the same volume are discarded because the first is likely causal.

State and persistence: in-memory map only. No suppressed exceptions are attached to the Java throwable; details live in the map.

Dependencies and integration points: depends on `FsVolumeSpi` and `IOException`. Integrated with `FsDatasetImpl`/volume startup paths that need to distinguish unhealthy data directories.

Risks: extends `RuntimeException`, so callers may miss it if expecting checked IO failures. The exposed map is mutable. `toString` quality depends on volume and exception string forms. Merging over key sets assumes stable `FsVolumeSpi` identity/equality.

Test signals: empty aggregate, constructor with prefilled map, merge preserves original per-volume exception, duplicate-volume merge behavior, and caller handling of `hasExceptions`.
