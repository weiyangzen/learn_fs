# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestFcPermissionsLocalFs.java

Purpose: Runs the generic `FileContextPermissionBase` suite against a local viewfs `FileContext`.

Important APIs/types/functions: `FileContextPermissionBase`, `getFileContext`, `ViewFsTestSetup.setupForViewFsLocalFs`, and `ViewFsTestSetup.tearDownForViewFsLocalFs`.

Control flow: `setUp` delegates to the base class, which calls this class's `getFileContext` override to obtain a viewfs-local `FileContext`. `tearDown` delegates to base cleanup and then removes the viewfs-local setup.

State/persistence: Local filesystem permission test state is managed by inherited helpers and viewfs setup.

Dependencies/integration: Validates viewfs local mounts against the standard FileContext permission contract.

Risks: Permission tests may be platform-sensitive, especially on filesystems without POSIX permission enforcement. This adapter contains no direct assertions.

Test signals: Inherited permission assertions execute against the viewfs local context returned by `getFileContext`.
