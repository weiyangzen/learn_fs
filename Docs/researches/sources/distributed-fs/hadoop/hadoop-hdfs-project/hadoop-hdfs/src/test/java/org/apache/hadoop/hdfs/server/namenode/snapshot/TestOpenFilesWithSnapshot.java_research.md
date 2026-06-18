# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOpenFilesWithSnapshot.java

Purpose: Slow integration suite for snapshot capture of open files, including aborted streams, deletion, rename, checksum stability, mixed capture-open-files config, and NameNode restart/checkpoint behavior.

Important APIs/types/functions: enables `DFS_NAMENODE_SNAPSHOT_CAPTURE_OPENFILES`. Helpers include `doWriteAndAbort`, `createFile`, `writeToStream` with `hsync(UPDATE_LENGTH)`, `createSnapshot`, `verifyFileSize`, and `restartNameNode` that triggers block reports, saves namespace, and restarts. Uses `DFSOutputStream`, `HdfsDataOutputStream`, `NamenodeProtocols.addBlock`, `FileChecksum`, and `SubjectInheritingThread`.

Control flow: early tests create under-construction files, abort streams, snapshot, delete files/parents, and restart/read snapshot files. Multiple-snapshot tests delete newer snapshots and restart with/without checkpoint. Point-in-time tests keep several files open under and outside snap roots, write between snapshots, and verify snapshot lengths freeze only when configured. Deletion tests delete open live files and snapshots in different orders while preserving remaining snapshot references. A writer-thread stress test deletes snapshots while appending. Checksum test proves old snapshot checksums survive truncate/append of current file. Mixed-config test toggles capture behavior and verifies old/new snapshot length semantics.

State and persistence behavior: strong persistence coverage through saveNamespace and NameNode restarts. Open file state is captured at hsync/update-length boundaries and represented as immutable snapshot copies when capture is enabled.

Dependencies and integration points: integrates append pipeline, block reports, leases/open file capture, snapshot deletion, truncation, checksums, NameNode RPC, and thread subject inheritance.

Risks and test signals: excellent regression coverage but slow and sometimes coarse where success is "restart does not fail". The writer stress loop is timing-sensitive and can be expensive.
