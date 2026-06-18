# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSFileContextMainOperations.java

Purpose: runs the generic `FileContextMainOperationsBaseTest` against local FS and adds local-specific checks for caching, corrupted-block support, working directory, and default file permission.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, `FileSystem.getLocal`, `FileContextTestHelper.createFile`, `FileContext.FILE_DEFAULT_PERM`, `fc.getUMask`, and inherited main-operation contract methods.

Control flow/state/persistence: setup creates a local file context and delegates to the base class. `getDefaultWorkingDirectory` caches the local FS working directory in a static field. `testFileContextNoCache` asserts separate local file context instances are not the same object. `listCorruptedBlocksSupported` returns false. `testDefaultFilePermission` creates a file and validates default permissions after umask.

Dependencies/integration points: bridges local FS through `FileContext`; depends on local default working directory and permission behavior.

Risks/test signals: catches unwanted `FileContext` instance caching, wrong default permission application, and incorrect exposure of corrupt-block APIs for local FS.
