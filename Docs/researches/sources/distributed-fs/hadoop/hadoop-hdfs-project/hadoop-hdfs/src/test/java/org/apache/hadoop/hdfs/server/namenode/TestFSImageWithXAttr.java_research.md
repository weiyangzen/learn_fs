<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithXAttr.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithXAttr.java

Purpose: `TestFSImageWithXAttr` verifies that extended attributes survive NameNode restart through both edit-log replay and fsimage checkpoint persistence, including create, replace, null-value storage, empty byte-array retrieval, and removal.

Important APIs, types, and functions: the test enables `DFS_NAMENODE_XATTRS_ENABLED_KEY`, uses `MiniDFSCluster`, `DistributedFileSystem`, `XAttrSetFlag.CREATE/REPLACE`, `SafeModeAction`, and `Map<String, byte[]>` returned by `getXAttrs`. The shared `testXAttr(boolean persistNamespace)` is invoked by `testPersistXAttr` and `testXAttrEditLog`; `restart` optionally checkpoints through safe mode.

Control flow: setup creates a one-DataNode cluster with XAttrs enabled. The test creates `/p`, sets three XAttrs (`user.a1`, `user.a2`, and `user.a3` with null value), restarts by the selected persistence lane, asserts all three names and byte values, replaces `user.a1`, restarts again, asserts the replacement while preserving others, removes all XAttrs, restarts again, and expects an empty result map.

State and persistence behavior: it exercises inode XAttr storage, edit-log operations for set/replace/remove, fsimage serialization of XAttrFeature, and conversion of null values to the empty byte-array form returned by `getXAttrs`.

Dependencies and integration points: depends on NameNode XAttr configuration, HDFS client XAttr APIs, safe mode checkpointing, cluster restart, and byte-array equality assertions.

Risks and edge cases: exact map size checks catch duplicates and missed removals, while `assertArrayEquals` catches value corruption. The class-level shared cluster can retain `/p` state between methods if a prior method fails. The null-vs-empty value behavior is subtle and should remain intentionally documented because `name3` is set with `null` but asserted as `{}`.

Test signals: paired fsimage/edit-log tests, byte-level assertions for all values, replace-after-restart, and remove-after-restart are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImageWithXAttr.java -->
