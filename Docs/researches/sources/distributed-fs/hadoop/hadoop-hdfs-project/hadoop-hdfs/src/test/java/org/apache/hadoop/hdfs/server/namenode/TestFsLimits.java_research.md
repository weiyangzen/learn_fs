<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsLimits.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsLimits.java

Purpose: `TestFsLimits` unit-tests NameNode namespace limits for maximum path component length and maximum directory item count, including mkdir and rename paths, disabled limits during edit-log loading, invalid configured limits, reserved `.snapshot` directory handling, and exception messages containing the correct parent directory.

Important APIs, types, and functions: it uses `DFS_NAMENODE_MAX_COMPONENT_LENGTH_KEY`, `DFS_NAMENODE_MAX_DIRECTORY_ITEMS_KEY`, `FSNamesystem.mkdirs`, `FSNamesystem.renameTo`, `Options.Rename`, `FSLimitException.PathComponentTooLongException`, `FSLimitException.MaxDirectoryItemsExceededException`, `HdfsConstants.DOT_SNAPSHOT_DIR`, mocked `FSImage`/`FSEditLog`, `NameNode.initMetrics`, and helper methods `getMockNamesystem`, `lazyInitFSDirectory`, `mkdirs`, `rename`, `deprecatedRename`, `mkdirCheckParentDirectory`, `renameCheckParentDirectory`, and `verify`.

Control flow: setup creates a fresh config with a NameNode directory URI, initializes metrics, and resets static `fs`/`fsIsReady`. Tests set limit values before the first operation, causing `lazyInitFSDirectory` to construct an FSNamesystem with those settings. Mkir and rename helpers execute the operation, catch any throwable, compare the generated exception class with the expected class, and return error text when needed. Rename coverage includes both modern `renameTo` with `Rename[]` and deprecated overload. `testDuringEditLogs` sets `fsIsReady=false`, proving component and directory limits are skipped while image/edit logs are loading except for reserved `.snapshot` validation.

State and persistence behavior: no disk persistence beyond configuration of a name-dir URI. The state under test is an in-memory FSNamesystem namespace and its image-loaded flag, which gates whether limits apply.

Dependencies and integration points: depends on FSNamesystem namespace mutation methods, reserved snapshot name validation, NameNode metrics setup, and exception message formatting.

Risks and edge cases: static fields (`conf`, `fs`, `fsIsReady`) make ordering safe only because `@BeforeEach` resets them. Helpers catch `Throwable`, which may hide assertion errors inside operations if expected is set incorrectly, though the class comparison usually exposes mismatches. Parent-directory verification tokenizes on whitespace, so formatting changes can affect it.

Test signals: expected exception class for overlong components, too many directory items, invalid limit values, reserved `.snapshot`; successful operations under limits; rename-specific failures at destination parent; limits disabled while `fsIsReady=false`; and error messages containing exact parent directory tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFsLimits.java -->
