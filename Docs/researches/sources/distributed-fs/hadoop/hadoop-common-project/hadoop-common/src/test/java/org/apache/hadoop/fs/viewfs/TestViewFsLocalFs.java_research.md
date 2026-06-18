# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsLocalFs.java

Purpose: concrete `ViewFsBaseTest` subclass that runs the generic `FileContext` viewfs suite against the local filesystem.

Important APIs and types: `ViewFsBaseTest`, `FileContext.getLocalFSFileContext`, JUnit `BeforeEach` and `AfterEach`.

Control flow: setup assigns `fcTarget` to the local FS `FileContext` and then delegates to the base setup, which creates target directories, mount links, and the `fcView` viewfs context. Teardown simply delegates to the base class, which deletes the test root.

State and persistence: all file operations are inherited from the base test and occur under the local test root managed by `FileContextTestHelper`.

Dependencies and integration: this is the local concrete runner for `ViewFsBaseTest`, validating `FileContext` APIs rather than `FileSystem` APIs. It covers create, mkdir, delete, rename, ACL/xattr failures on internal dirs, block locations, link status, checksums, server defaults, and optimized list delegation inherited from the base.

Risks and test signals: failures generally originate in shared `ViewFsBaseTest` logic but can also indicate local `FileContext` initialization or cleanup behavior changed.
