# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestParallelImageWrite.java

Purpose: Verifies DFS namespace integrity and identical fsimage files across multiple NameNode image directories when images are written in parallel during restart and saveNamespace.

Important APIs and functions: `testRestartDFS` creates files with `DFSTestUtil`, restarts MiniDFSCluster without formatting, forces checkpoint-on-startup with `DFS_NAMENODE_CHECKPOINT_TXNS_KEY`, calls `saveNamespace`, and compares metadata. Static helper `checkImages` inspects `NNStorage`, image `StorageDirectory` instances, and `FSImageTestUtil` hash/equality helpers.

Control flow: The test starts a formatted cluster, records the configured number of NameNode name dirs, creates 200 files under `/srcdat`, records root and directory status, mutates root owner and directory group, and shuts down. It restarts without formatting, confirms files and metadata persisted, checks that all image dirs contain identical newest images, mutates the namespace by cleanup/recreate, enters safe mode, saves namespace, rechecks image equality, and verifies the fsimage hash changed after namespace mutation.

State and persistence behavior: This is a persistence-focused test. It validates namespace metadata in fsimage files across restarts and explicit saveNamespace, and checks all image storage directories have non-empty identical images.

Dependencies and integration points: Uses MiniDFSCluster, FSNamesystem, FSImage/NNStorage, name dir configuration, DFSTestUtil, safe mode RPC, and FSImageTestUtil MD5 comparisons ignoring transaction id.

Risks: Requires more than one image directory in MiniDFSCluster. Hash comparison ignores txid but still assumes deterministic image contents across directories. The test writes many files and can be IO-sensitive.

Test signals: Passing means file tree and metadata survive restart, every image directory remains active, parallel image files are identical, newest images match, and a later namespace save produces a different image hash.
