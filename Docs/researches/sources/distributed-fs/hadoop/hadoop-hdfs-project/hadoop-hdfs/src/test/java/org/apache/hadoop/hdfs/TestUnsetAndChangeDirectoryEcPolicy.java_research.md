# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestUnsetAndChangeDirectoryEcPolicy.java

Purpose: Tests setting, unsetting, changing, inheriting, and persisting erasure-coding policies on directories and root, plus invalid path/file cases.

Important APIs and types: `DistributedFileSystem.setErasureCodingPolicy`, `unsetErasureCodingPolicy`, `getErasureCodingPolicy`, `DFSTestUtil.enableAllECPolicies`, `SystemErasureCodingPolicies`, `NoECPolicySetException`, `ErasureCodeNative`, `NativeRSRawErasureCoderFactory`, and `cluster.restartNameNode`.

Control flow: Setup creates a cluster with `dataBlocks + parityBlocks` datanodes, EC block size, no reconstruction max streams, optional native RS coder config, and all EC policies enabled. Tests cover unsetting absent EC policy, creating EC files before unset and replicated files after unset, nested child policy override then fallback to parent policy, root policy unset/change, replicated files with different replication factors after unset, nonexistent path failures, disallowing set/unset on files, and edit-log persistence of root unset across restart.

State and persistence behavior: EC policy xattrs/metadata live in NameNode namespace and are inherited at file creation time. Existing EC files retain their policy after directory policy changes. `testUnsetEcPolicyInEditLog` confirms unset operation persists via edit log.

Dependencies and integration points: Integrates EC policy management, system policies, native coder configuration, file creation under EC directories, root path behavior, exceptions, and NameNode restart/edit-log replay.

Risks and test signals: Some tests delete root recursively after root-policy cases, so isolation relies on fresh MiniDFSCluster per test. Passing signals EC directory policy semantics and persistence are correct for inheritance and invalid operations.
