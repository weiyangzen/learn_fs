# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestFSMainOperationsLocalFileSystem.java

Purpose: Adapts the generic `FSMainOperationsBaseTest` suite to a `ViewFileSystem` mounted over the local filesystem.

Important APIs/types/functions: `FSMainOperationsBaseTest`, `ViewFileSystemTestSetup.setupForViewFileSystem`, `ViewFileSystemTestSetup.createConfig`, `ViewFileSystemTestSetup.tearDown`, `FileSystem.getLocal`, and overridden `createFileSystem`, `setUp`, `tearDown`.

Control flow: `setUp` obtains the local target filesystem and invokes the base setup. `createFileSystem` builds a viewfs configuration and returns a view filesystem mounted for the base test's use. `tearDown` runs base cleanup and removes the viewfs/local test setup.

State/persistence: Uses local filesystem test state managed by the base class and `ViewFileSystemTestSetup`; `fcTarget` holds the raw local FS.

Dependencies/integration: This is a bridge test that runs inherited main filesystem operation tests against `ViewFileSystem`, validating viewfs compatibility with the common `FileSystem` contract.

Risks: The class itself has no direct test methods; behavior depends entirely on inherited tests. Failures may originate in base test assumptions or setup helper mount configuration.

Test signals: Inherited `FSMainOperationsBaseTest` assertions execute against the viewfs-backed filesystem.
