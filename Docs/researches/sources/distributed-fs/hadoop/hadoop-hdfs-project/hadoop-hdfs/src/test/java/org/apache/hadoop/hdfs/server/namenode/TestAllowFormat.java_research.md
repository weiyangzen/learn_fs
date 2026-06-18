<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAllowFormat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAllowFormat.java

Purpose: tests NameNode format behavior controlled by `dfs.namenode.support.allow.format` and verifies non-file shared edits directories are ignored by local format handling.

Important APIs/types/functions: uses `NameNode.format()`, `MiniDFSCluster`, `DFS_NAMENODE_NAME_DIR_KEY`, `DFS_DATANODE_DATA_DIR_KEY`, `DFS_NAMENODE_CHECKPOINT_DIR_KEY`, `DFS_NAMENODE_SUPPORT_ALLOW_FORMAT_KEY`, HA setup through `HATestUtil`, and `DummyJournalManager`.

Control flow: `@BeforeAll` prepares multiple name directories, pre-creating one empty dir to guard against unwanted prompts, configures data/checkpoint dirs, and sets a default HDFS URI. `testAllowFormat()` formats through MiniDFSCluster startup, shuts down, asserts manual format fails when allow-format is false, then succeeds when true. `testFormatShouldBeIgnoredForNonFileBasedDirs()` configures HA shared edits with a `dummy://` URI and verifies `NameNode.format()` handles it without trying file-directory formatting.

State and persistence: creates and deletes local DFS base directories and NameNode storage metadata. The second test exercises configuration parsing more than persistent shared-edits state.

Dependencies and integration points: covers NameNode storage formatting, MiniDFSCluster directory-management flags, HA shared edits config, non-file journal plugins, and test directory cleanup.

Risks and test signals: risks are accidental formatting despite disabled config, hanging on prompts for empty dirs, or treating non-file shared edits as local paths. Signals are expected `IOException` text and successful format calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAllowFormat.java -->
