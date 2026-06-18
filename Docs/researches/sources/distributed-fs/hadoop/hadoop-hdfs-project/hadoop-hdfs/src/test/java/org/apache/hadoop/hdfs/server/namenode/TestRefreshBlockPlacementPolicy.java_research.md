# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRefreshBlockPlacementPolicy.java

Purpose: Verifies that NameNode block placement policy implementations can be dynamically refreshed from custom configured classes back to defaults for both replicated and erasure-coded placement.

Important APIs and functions: `MockBlockPlacementPolicy` extends `BlockPlacementPolicyDefault` and increments a static `counter` in `chooseTarget`. `setup()` configures both `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` and `DFS_BLOCK_PLACEMENT_EC_CLASSNAME_KEY` to this mock, then starts a 9-DN cluster. Tests call `NameNode.reconfigurePropertyImpl` with `null` to reset.

Control flow: `verifyRefreshPolicy()` creates a file and confirms the mock counter increases, invokes the supplied refresh function, deletes and recreates the file, then verifies the counter does not change, proving the default policy is active. `testRefreshEcPolicy` first creates an EC directory and enables default EC placement on it.

State and persistence behavior: Runtime state is the active BlockManager placement policy instance and the static invocation counter. The reconfiguration is in-memory for the running NameNode and is not persisted by this test.

Dependencies and integration points: Integrates dynamic reconfiguration, `BlockPlacementPolicyDefault`, replicated and EC placement config keys, `DistributedFileSystem.create`, and NameNode block target selection.

Risks: Static `counter` is shared across tests and relies on relative increments. Use of Java `assert` for the first counter check depends on assertions being enabled; the final `assertEquals` is the stronger JUnit signal.

Test signals: The counter increases before refresh and remains unchanged after refresh for both replicated and EC file creation.
