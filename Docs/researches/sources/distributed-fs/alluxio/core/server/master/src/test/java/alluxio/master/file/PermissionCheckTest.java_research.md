# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PermissionCheckTest.java

## Purpose
End-to-end FileSystemMaster permission tests with authorization enabled. The suite validates how create, mkdir, rename, delete, read/list/status, attribute changes, complete/free, ACL-style owner/group/mode updates, and explicit access checks behave for owner, group, other, superuser, and supergroup users.

## Important APIs/types/functions
- Configures `SECURITY_GROUP_MAPPING_CLASS`, permission supergroup, and root UFS via `ConfigurationRule`.
- Uses `AuthenticatedUserRule` to run individual file master calls as different users.
- `FakeUserGroupsMapping` maps admin/user1/user2/user3/user4 to deterministic groups.
- `before()` constructs `MasterRegistry`, `MetricsMaster`, block master, and file master with `TestUserState`, starts services, and calls `createDirAndFileForTest`.
- Helper methods wrap each operation: `verifyCreateFile`, `verifyCreateDirectory`, `verifyRename`, `verifyDelete`, `verifyRead`, `verifyGetFileId`, `verifyGetFileInfoOrList`, `verifySetState`, `verifyCompleteFile`, `verifyFree`, `verifySetAcl`, and `verifyAccess`.

## Control flow
- Shared fixture creates `/testDir`, `/testDir/file`, and `/testFile` with controlled owners/groups/modes.
- Each test switches the authenticated user, executes one master operation, and checks either result metadata or expected exception message.
- Negative tests use `ExpectedException` and `ExceptionMessage.PERMISSION_DENIED` with a constructed `user/access/path/failed-at` message.
- Umask-specific tests temporarily change `SECURITY_AUTHORIZATION_PERMISSION_UMASK` to create unreadable or non-executable paths.
- Recursive `setAttribute` tests verify child metadata changes after owner/group/mode updates.

## State and persistence behavior
- The file master runs against a temporary root UFS and a noop journal system.
- Permission state is inode owner/group/mode plus global auth config and group mapping cache.
- Tests reset group mapping cache and reload configuration in teardown, important because group mapping and authorization settings are process-global.

## Dependencies and integration points
- Exercises FileSystemMaster public methods and their contexts, security utilities that derive owner/group from authenticated user, group mapping service cache, and exception-message contracts.
- Integrates with block and metrics masters through a real `MasterRegistry`.

## Risks and edge cases
- The class is large and relies on shared mutable namespace; test order must not matter because each test rebuilds the master.
- `getRootInode()` appears unused and may be legacy helper drift.
- Exact exception-message assertions are useful but brittle if wording changes.
- Some comments in delete/free tests mention the wrong user/path, but assertions encode the intended behavior.

## Test signals
- Very strong regression signal for FileSystemMaster authorization enforcement at API boundaries.
- Covers both allow and deny paths, including supergroup bypass, owner-only ACL updates, execute requirement for directory listing, recursive attributes, and missing-file access checks.
