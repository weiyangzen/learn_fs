# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReplaceDatanodeOnFailure.java

Purpose: tests the default and configured `ReplaceDatanodeOnFailure` policies for client write pipelines, including active replacement with new DNs, append behavior with insufficient DNs, and best-effort replacement.

Important APIs and types: `ReplaceDatanodeOnFailure`, `Policy.ALWAYS`, `DataTransferProtocol.LOG`, `MiniDFSCluster`, `HdfsDataOutputStream`, `DatanodeInfo`, `GenericTestUtils.waitFor`, `SubjectInheritingThread`, `FSDataOutputStream`, and `FileStatus`.

Control flow: `testDefaultPolicy` exhaustively computes expected `satisfy` decisions for replication factors, existing pipeline sizes, append flags, and hflush flags. `testReplaceDatanodeOnFailure` starts writers, adds replacement DNs on another rack, stops an old DN, starts more writers, waits until all output streams report full replication, stops writers, and reads back content. `testAppend` validates that an empty file with replication 3 can be created on one DN and appended once, but a second append fails. `testBestEffort` enables always-replace without throwing on failure and verifies create/append can succeed with only one DN.

State and persistence behavior: exercises live pipeline composition, current block replication reporting, block placement across newly started DNs, and append state. Files are not persisted across cluster restart.

Dependencies and integration points: integrates client policy calculation, DataTransfer pipeline replacement, NameNode DataNode selection with load consideration disabled in one test, rack placement, and HDFS append semantics.

Risks and edge cases: the policy matrix is precise and catches semantic drift in default replacement conditions. Threaded writer tests are timing-sensitive and depend on replication reaching full count within 10 seconds. Append tests model under-provisioned clusters where logical file replication remains 3 even if physical availability is lower.

Test signals: boolean policy decisions match expected truth table, writer streams report replication 3, file contents match sequential writes, second append throws when replacement is not best effort, and best-effort append succeeds.
