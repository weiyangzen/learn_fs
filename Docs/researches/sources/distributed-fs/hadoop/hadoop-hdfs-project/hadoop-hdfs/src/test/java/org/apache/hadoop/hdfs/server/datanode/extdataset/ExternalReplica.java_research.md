# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalReplica.java

Purpose: This minimal external `Replica` implementation exists to verify that third-party code can implement the DataNode replica contract outside the DataNode package.

Important APIs/types/functions: `Replica`, `ReplicaState.FINALIZED`, `FsVolumeSpi`, and replica identity/length methods such as `getBlockId`, `getGenerationStamp`, `getNumBytes`, `getVisibleLength`, `getStorageUuid`, and `getVolume`.

Control flow: Every method returns a neutral placeholder: zero IDs/lengths, `FINALIZED` state, `null` storage/volume, and non-transient storage false.

State and persistence behavior: The class stores no fields and represents no actual block file. It is a compile-time stub, not a meaningful replica implementation.

Dependencies and integration points: It is returned by `ExternalDatasetImpl.getReplica` and instantiated in `TestExternalDataset`, ensuring the `Replica` interface remains externally implementable.

Risks and test signals: Signal is successful construction and compilation. Risk is mistaking this for behavioral coverage; it does not validate actual replica data, lifecycle transitions, or storage identity.
