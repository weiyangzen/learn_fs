# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNestedEncryptionZones.java

Purpose: Tests nested HDFS encryption zone behavior, including persistence across edit logs and fsimage, rename restrictions between zones, root-directory zone behavior, and trash placement for nested zones.

Important APIs and functions: Setup configures a Java key store provider, creates encryption keys with `DFSTestUtil.createKey`, and uses `DistributedFileSystem.createEncryptionZone`. Helpers `initTopEZDirAndNestedEZDir`, `verifyEncryption`, and `renameChildrenOfEZ` create zones/files and assert encryption behavior. Trash behavior is checked through `FileSystem.getTrashRoot`, `FsShell`, and `ToolRunner`.

Control flow: The main nested-zone test creates a top and nested zone, verifies file encryption and raw file inequality, restarts NameNodes to load edit logs, checkpoints and restarts to load fsimage, then tests allowed and forbidden renames. It rejects moving a separate zone into an existing zone, allows renaming the top zone root, and allows renaming the nested zone within the same top zone. The root-zone test creates the top zone at `/`, validates rename restrictions, then verifies trash roots for top and nested zone files and confirms shell delete moves files into the correct per-zone trash.

State and persistence behavior: Encryption zone definitions, keys, file contents, and rename changes are persisted through edits and fsimage. Raw path comparisons validate ciphertext differs between zones. Trash paths are namespace state under each encryption zone's trash root.

Dependencies and integration points: Integrates NameNode encryption zone manager, key provider configuration, delegation token key use, raw reserved paths, safe mode and saveNamespace, FsShell trash, UGI current user, and HDFS rename validation.

Risks: JKS provider flushing requires setting the client provider to the NameNode provider. Rename rejection checks use exception message substrings. Trash behavior depends on configured trash interval and current user naming.

Test signals: Passing means nested zones reload after restart/checkpoint, encrypted status stays true, plaintext comparisons match while raw ciphertext differs, illegal cross-zone moves fail, legal zone-root renames succeed, and trash roots are zone-local.
