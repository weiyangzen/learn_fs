# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/PermissionCheckerTest.java

## Purpose
Focused unit tests for `DefaultPermissionChecker` against a manually constructed `InodeTree`. It validates POSIX-style owner/group/other permission selection, parent/ancestor permission checks, superuser/supergroup bypass, invalid-path behavior, and effective permission calculation.

## Important APIs/types/functions
- Builds static `InodeTree`, `InodeStore`, `MountTable`, `InodeLockManager`, block master, and metrics master in `beforeClass`.
- `FakeUserGroupsMapping` provides deterministic single and multi-group membership.
- `createAndSetPermission` locks paths with `LockPattern.WRITE_EDGE`, creates inodes, then writes owner/group/mode directly into the inode store.
- `checkPermission` calls `PermissionChecker.checkPermission`; `checkParentOrAncestorPermission` calls `checkParentPermission`; `getPermission` validates `PermissionChecker.getPermission`.

## Control flow
- Class-level setup initializes root as admin/admin/0755 and creates `/testDir/file`, `/testFile`, and `/testWeirdFile`.
- Tests set `AuthenticatedClientUser` directly, lock the relevant inode path, and invoke permission checker methods.
- Weird mode `0157` is used to prove there is no fallback from owner to group/other or group to other when a more specific class lacks bits.
- Parent and ancestor tests use a partially missing path to ensure checks stop at the existing ancestor.

## State and persistence behavior
- Inode metadata is in a heap/metastore-backed tree and is modified directly after creation.
- Uses `NoopJournalContext`, so journal persistence is not the concern; lock correctness and checker semantics are.
- Global auth configuration and group mapping cache are changed at class setup and reset at teardown.

## Dependencies and integration points
- Integrates core inode tree locking, inode store mutation, group mapping, authenticated client user state, and permission exception formatting.
- Uses mocked UFS manager/mount info because permission checking only needs inode namespace context.

## Risks and edge cases
- Static fixture means inode state is shared across tests; current tests are read-only after setup.
- Direct inode mutation bypasses higher-level FileSystemMaster behavior, so this complements but does not replace `PermissionCheckTest`.
- Exact denial message assertions are brittle but pin user-facing diagnostics.

## Test signals
- Strong signal for the low-level permission algorithm, especially specific-class bit selection and supergroup bypass.
- Regression indicators: owner/group/other fallback changes, parent checks using the wrong ancestor, or `getPermission` returning non-POSIX effective bits.
