# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestProvidedReplicaImpl.java

Purpose: This unit test validates `ProvidedReplica` read behavior for finalized replicas backed by byte ranges in an external local file.

Important APIs/types/functions: `FinalizedProvidedReplica`, `ProvidedReplica.blockDataExists`, `getBlockURI`, `getDataInputStream`, `getBlockDataLength`, `BoundedInputStream`, `ReadableByteChannel`, and `FileSystemTestHelper`.

Control flow: Setup creates a deterministic local backing file if missing, divides it into 128 KiB provided replicas, and records one `FinalizedProvidedReplica` per range. The test iterates replicas, asserts backing data exists and the block URI matches, then compares each replica stream against the corresponding slice of the local file. After deleting the file, it asserts every replica reports missing backing data.

State and persistence behavior: The test creates and deletes a real local file under the test root. Replica objects hold URI, offset, length, generation stamp, and configuration but no HDFS DataNode cluster state.

Dependencies and integration points: It covers the provided-storage replica abstraction, Java stream/channel reads, range-bounded comparison, and local filesystem URI handling.

Risks and test signals: Signals are byte-for-byte equality, URI equality, and `blockDataExists` before/after deletion. Risks include leftover local files, slow byte-by-byte file creation, and limited coverage of nonzero seek offsets beyond stream start.
