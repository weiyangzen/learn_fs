# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFileSystemPermission.java

Purpose: validates local filesystem permission, umask, rename permission preservation, and group ownership behavior.

Important APIs/types/functions: `LocalFileSystem`, `FsPermission`, config key `FS_PERMISSIONS_UMASK_KEY`, `mkdirs`, `create` with explicit permission, `setPermission`, `setOwner`, `getFileStatus`, `Shell.getGroupsCommand`, and helper `getPermission`.

Control flow/state/persistence: tests run only on non-Windows. They create files/directories under a temp prefix, set umasks, assert default and explicit permissions after umask application, rename files/directories and verify permissions survive, set permissions to none/all, set group ownership to the current user's groups when available, and update umask at runtime to ensure newly created dirs observe the changed value. Cleanup deletes created paths and resets umask in the runtime test.

Dependencies/integration points: depends on Unix permission semantics, shell group command output, and local FS status loading.

Risks/test signals: catches stale umask caching, permission loss during rename, incorrect create/mkdir permission masking, and `setOwner` group failures. Platform sensitivity is explicitly guarded by assumptions.
