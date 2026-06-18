## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFcLocalFsPermission.java

Purpose: attaches the shared `FileContextPermissionBase` permission contract to the local `FileContext` implementation.

Important APIs/types/functions: `FileContextPermissionBase`, `FileContext.getLocalFSFileContext`, JUnit `@BeforeEach`/`@AfterEach`, and `UnsupportedFileSystemException`.

Control flow: the class delegates setup and teardown to the base class and overrides `getFileContext` to return the local FS context. The inherited base tests perform permission operations.

State and persistence: inherited tests create local files/directories and mutate permissions. This subclass has no additional state.

Dependencies/integration points: covers `FileContext` permission behavior for local filesystems, including the `FsPermission` path through the FileContext API rather than the older `FileSystem` API.

Risks and test signals: behavior depends on local OS permission support and user privileges. Windows or permissive filesystems may behave differently depending on assumptions in the base class. Failures point to local `FileContext` permission regression or environment limitations.
