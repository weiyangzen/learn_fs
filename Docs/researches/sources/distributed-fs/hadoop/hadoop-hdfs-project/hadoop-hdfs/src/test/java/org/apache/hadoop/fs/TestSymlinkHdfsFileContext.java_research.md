<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileContext.java

Purpose: Runs the HDFS symlink base tests through a FileContext wrapper and adds AbstractFileSystem-specific link behavior.
Important APIs/types/functions: `TestSymlinkHdfsFileContext` extends `TestSymlinkHdfs`; `testSetup()` creates `FileContextTestWrapper`; `testAccessLinkFromAbstractFileSystem()` verifies AFS does not resolve links implicitly.
Control flow: Before all tests, the subclass binds FileContext to the shared cluster URI and installs the wrapper. The added test creates a file/link and calls `AbstractFileSystem.open(link)`, expecting `UnresolvedLinkException`.
State and persistence behavior: Uses the shared static cluster/DFS/WebHDFS state from the base class plus a static FileContext.
Dependencies and integration points: Integrates HDFS FileContext symlink behavior, AbstractFileSystem API, and inherited `SymlinkBaseTest` cases.
Risks and edge cases: Depends on base class `beforeClassSetup()` ordering. The AFS test must distinguish direct AFS behavior from FileContext's higher-level resolution.
Test signals: Signals are inherited symlink tests plus `UnresolvedLinkException` from raw AFS open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileContext.java -->
