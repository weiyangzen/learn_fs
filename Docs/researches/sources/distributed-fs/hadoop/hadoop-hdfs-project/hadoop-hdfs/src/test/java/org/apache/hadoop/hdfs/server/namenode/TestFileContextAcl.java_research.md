<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextAcl.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextAcl.java

Purpose: `TestFileContextAcl` reruns the shared HDFS ACL base test suite through the `FileContext` API surface rather than the ordinary `DistributedFileSystem` ACL methods, proving both client APIs reach equivalent NameNode ACL behavior.

Important APIs, types, and functions: it extends `FSAclBaseTest`, initializes `conf` and `startCluster` in `@BeforeAll`, overrides `createFileSystem`, and defines `FileContextFS extends DistributedFileSystem`. `FileContextFS.initialize` calls `super.initialize` and creates a `FileContext`, while ACL methods (`modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `getAclStatus`) delegate to `FileContext`.

Control flow: the inherited base tests call `createFileSystem`; this class returns a `DistributedFileSystem` facade whose ACL operations are routed through `FileContext`. Non-ACL filesystem operations still use the superclass `DistributedFileSystem` behavior, limiting this adapter to the API boundary under test.

State and persistence behavior: persistence and namespace state are controlled by the inherited base tests and shared mini cluster. This class adds no storage behavior; it verifies that FileContext-driven ACL mutations/readbacks affect the same HDFS namespace state.

Dependencies and integration points: depends on `FSAclBaseTest` for coverage, cluster lifecycle, and assertions; `FileContext.getFileContext(conf)` for the alternate API; and HDFS ACL NameNode operations.

Risks and edge cases: because only ACL methods are overridden, any inherited test that performs a non-ACL operation still goes through `DistributedFileSystem`, which is intended but means this is not a full FileContext filesystem facade. Coverage is tied entirely to the base class; changes there can expand or break this adapter.

Test signals: all inherited ACL tests must pass while ACL calls are delegated through `FileContext`, indicating API parity for ACL operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextAcl.java -->
