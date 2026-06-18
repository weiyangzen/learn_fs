<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestResolveHdfsSymlink.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestResolveHdfsSymlink.java

Purpose: Tests FileContext and DFSClient behavior around HDFS symlink resolution to other filesystems and delegation token APIs.
Important APIs/types/functions: `TestResolveHdfsSymlink`, `testFcResolveAfs()`, `testFcDelegationToken()`, `testLinkTargetNonSymlink()`, and `testLinkTargetNonExistent()`.
Control flow: Setup starts HDFS with delegation tokens always enabled. Tests create a local file, create an HDFS symlink to the local root, resolve abstract filesystems for a path through the link, obtain/renew/cancel HDFS delegation tokens, and assert DFSClient link-target errors for non-symlink and missing paths.
State and persistence behavior: State includes the MiniDFSCluster, local test file, HDFS symlink, and issued delegation token. Cleanup deletes the non-symlink file and shuts down the cluster.
Dependencies and integration points: Integrates `FileContext.resolveAbstractFileSystems`, local FS, HDFS symlinks, `DFSClient.getLinkTarget`, and HDFS delegation token renewal/cancellation.
Risks and edge cases: Cross-filesystem symlink resolution depends on FileContext URI construction. Token tests assume at least one token is returned. Some created symlink/local paths are not explicitly cleaned before cluster teardown.
Test signals: Signals are exactly two resolved AFS instances, successful token renew/cancel, error text for non-symlink, and `FileNotFoundException` text for missing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestResolveHdfsSymlink.java -->
