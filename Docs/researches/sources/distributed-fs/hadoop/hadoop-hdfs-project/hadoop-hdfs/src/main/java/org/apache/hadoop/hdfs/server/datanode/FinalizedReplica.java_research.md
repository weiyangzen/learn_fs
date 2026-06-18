# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FinalizedReplica.java

Purpose: `FinalizedReplica` describes a fully written local block replica. It extends `LocalReplica`, exposes all bytes as visible, and carries cached metadata for finalized-read and recovery-adjacent workflows.

Important APIs: constructors accept block fields or `Block` objects plus volume/directory and optional last partial chunk checksum. Overrides return `ReplicaState.FINALIZED`, `getVisibleLength == getNumBytes`, `getBytesOnDisk == getNumBytes`, and unsupported recovery/original methods. `getMetadataLength` caches the metadata length on first call. `loadLastPartialChunkChecksum` asks the volume to compute/load the last partial chunk checksum.

Control flow and state: the object is mostly immutable block identity/location inherited from `LocalReplica`, with mutable `lastPartialChunkChecksum` and cached `metaLength`. It does not perform writes except checksum cache loading; file IO is inherited through local replica methods.

Dependencies and integration points: it depends on `LocalReplica`, `Block`, `FsVolumeSpi`, `ReplicaState`, and `ReplicaRecoveryInfo`. Block readers, scanners, and dataset maps use it as the normal finalized local replica representation.

Risks: `metaLength` is cached and not invalidated; this is correct for finalized metadata but would be stale if callers mutate metadata after finalization. Recovery APIs throw, so recovery code must convert to another replica state before setting recovery IDs. The checksum byte array is stored by reference, so callers should avoid mutating it after setting.

Test signals: verify finalized state/length values, metadata length caching, copy constructor checksum preservation, last partial checksum loading from volume, unsupported recovery methods, and inherited local file path behavior.
