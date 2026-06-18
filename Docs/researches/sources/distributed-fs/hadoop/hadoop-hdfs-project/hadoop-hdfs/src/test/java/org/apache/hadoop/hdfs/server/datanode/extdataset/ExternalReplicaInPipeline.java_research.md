# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalReplicaInPipeline.java

Purpose: This external-package `ReplicaInPipeline` stub verifies that write-pipeline replica contracts can be implemented by a third-party dataset.

Important APIs/types/functions: `ReplicaInPipeline`, `ReplicaOutputStreams`, `ChunkChecksum`, `DataChecksum`, `ReplicaState.FINALIZED`, writer-management methods, byte-ack/length methods, and `FsVolumeSpi`.

Control flow: Mutators no-op, metrics return zero, `getLastChecksumAndDataLen` returns a zero/null checksum, `createStreams` returns `ReplicaOutputStreams` with null streams and the requested checksum, and writer methods return false or no-op.

State and persistence behavior: No bytes, writer thread, checksum, or storage UUID are retained. It does not create data or metadata files.

Dependencies and integration points: It is used by `ExternalDatasetImpl` methods that create temporary, RBW, append, and recovery handlers, and instantiated directly by `TestExternalDataset`.

Risks and test signals: Signal is type construction and accessibility of pipeline APIs. It provides no behavioral safety for real write pipelines because stream fields are null and state changes are ignored.
