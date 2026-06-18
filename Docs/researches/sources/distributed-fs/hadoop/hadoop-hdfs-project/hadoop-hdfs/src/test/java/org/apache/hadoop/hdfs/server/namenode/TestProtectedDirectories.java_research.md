# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestProtectedDirectories.java

Purpose: Verifies `fs.protected.directories` and protected subdirectory behavior for delete, trash, rename, runtime reconfiguration, path normalization, canonicalization, root handling, and invalid configured paths.

Important APIs and types: `setupTestCase` configures `FS_PROTECTED_DIRECTORIES`, starts a NameNode-only MiniDFSCluster, and creates protected/unprotected paths. `TestMatrixEntry` stores expected delete/rename outcomes. Tests call `FileSystem.delete`, `Trash.moveToAppropriateTrash`, `FileSystem.rename`, `NameNode.reconfigureProperty`, `FSDirectory.parseProtectedDirectories`, `FSDirectory.normalizePaths`, and `FSDirectory.getProtectedDirectories`.

Control flow: Matrix builders describe many layouts: empty/non-empty protected dirs, nested protected and unprotected trees, disjoint trees, string-prefix edge cases, trailing separators, and protected subdirectory mode. Delete, trash, and rename tests iterate sorted paths and compare actual success to matrix expectations, also checking failed delete leaves file counts unchanged. Reconfigure test changes protected directories at runtime and then resets to default. Normalization tests parse redundant slashes, trailing slashes, `..`, root, schemes, and reserved paths.

State and persistence behavior: Protected directory configuration is held in NameNode/FSDirectory runtime state and can be reconfigured. Namespace directories are created for each matrix case but not persisted across cluster instances.

Dependencies and integration points: Integrates CommonConfigurationKeys, DFS protected subdirectory enablement, MiniDFSCluster, FSDirectory policy parsing, HDFS delete/rename authorization, Trash behavior, AccessControlException handling, Guava-compatible collection helpers, and AssertJ assertions.

Risks: Matrix expectations are dense and path-order dependent. `testMoveProtectedSubDirsToTrash` compares `moveToTrash` with a second call to itself, which can mask expected-matrix intent and may be a weak assertion. Path canonicalization behavior is security-sensitive, especially for prefixes and reserved paths.

Test signals: Passing means protected paths and ancestors with protected children resist destructive operations when expected, trash follows the same access policy, runtime reconfiguration updates FSDirectory and config, and parser normalization rejects invalid paths while preserving root.
