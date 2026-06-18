<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestApplyingStoragePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestApplyingStoragePolicy.java

Purpose: Validates the user-visible `DistributedFileSystem` storage policy semantics for default, explicit, unset, and inherited policies on nested directories and files.

Important APIs, types, and functions: `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil.createFile`, `BlockStoragePolicySuite.createDefaultSuite`, `BlockStoragePolicy`, `setStoragePolicy`, `getStoragePolicy`, and `unsetStoragePolicy`. The tests compare against the default `HOT`, `WARM`, and `COLD` policies from the default suite.

Control flow: Each test starts a single-DataNode MiniDFSCluster in `clusterSetUp` and shuts it down in `clusterShutdown`. `testStoragePolicyByDefault` creates `/foo/bar/wow` and asserts all existing paths resolve to `HOT`; a missing path should throw `FileNotFoundException`. `testSetAndUnsetStoragePolicy` explicitly sets `WARM`, `COLD`, and `HOT` at different levels, verifies retrieval, unsets all three, and verifies fallback to `HOT`. `testNestedStoragePolicy` unsets from the leaf upward and checks nearest-ancestor inheritance. `testSetAndGetStoragePolicy` covers file and parent policy setting through the same DFS API.

State and persistence behavior: The tests manipulate in-memory NameNode metadata in a fresh cluster per method. They do not restart the NameNode, so edit-log/fsimage persistence is left to `TestBlockStoragePolicy`. The relevant state is the policy ID stored on inode metadata and the effective policy resolved from ancestors when an inode has no explicit policy.

Dependencies and integration points: Integrates the public DFS client API with the NameNode storage-policy manager and default policy suite. It also exercises exception translation for nonexistent paths.

Risks: The tests catch semantic regressions in inheritance but not physical block placement. They use broad `catch (Exception)` blocks and then `instanceof` checks, so unexpected exception subclasses could be less clearly diagnosed than `assertThrows`.

Test signals: Success means existing files and directories resolve to the expected explicit or inherited policy, missing paths consistently produce `FileNotFoundException`, and unsetting leaf/ancestor policies walks back through nearest ancestor and finally default `HOT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestApplyingStoragePolicy.java -->
