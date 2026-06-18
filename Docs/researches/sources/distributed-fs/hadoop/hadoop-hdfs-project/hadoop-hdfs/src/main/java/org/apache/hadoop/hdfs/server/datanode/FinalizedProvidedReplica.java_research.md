# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FinalizedProvidedReplica.java

Purpose: `FinalizedProvidedReplica` represents a finalized HDFS block whose bytes are served from provided/external storage rather than local block files.

Important APIs: constructors accept direct file URI/offset/length/generation/path-handle fields, a `FileRegion`, or path prefix/suffix components. It overrides `getState` to `FINALIZED`, `getBytesOnDisk` and `getVisibleLength` to `getNumBytes`, and unsupported recovery/original-replica methods to throw `UnsupportedOperationException`.

Control flow and state: all location and access behavior is inherited from `ProvidedReplica`. The `FileRegion` constructor translates a provided storage location nonce into a `RawPathHandle`, preserving stable access to external storage. Since finalized replicas expose all bytes, visible length and bytes-on-disk are identical.

Dependencies and integration points: it depends on `ProvidedReplica`, `FileRegion`, `ProvidedStorageLocation`, `FsVolumeSpi`, `FileSystem`, `Path`, `PathHandle`, `RawPathHandle`, `Configuration`, and `ReplicaState`. Dataset code can treat it as a finalized `ReplicaInfo` while reads resolve through provided-storage mechanisms.

Risks: recovery mutation APIs are intentionally unsupported, so callers must not attempt append/recovery workflows on provided finalized replicas. Correctness depends on the external file, offset, length, generation stamp, and path handle remaining valid. Equality/hash behavior is inherited, so provided-location identity semantics come from `ProvidedReplica`.

Test signals: verify constructor field translation from `FileRegion`, `FINALIZED` state, visible/on-disk length equality, unsupported recovery APIs, and read integration against a provided `FileSystem`.
