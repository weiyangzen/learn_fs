# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/PermissionChecker.java

## Purpose
`PermissionChecker` defines the authorization checks used by the file-system master against locked inode paths. It abstracts parent permission, direct permission, superuser checks, effective permission lookup, and set-attribute authorization.

## Important APIs, types, and functions
Methods are `checkParentPermission(Mode.Bits, LockedInodePath)`, `checkPermission(Mode.Bits, LockedInodePath)`, `checkSuperUser()`, `getPermission(LockedInodePath)`, and `checkSetAttributePermission(LockedInodePath, boolean, boolean, boolean)`.

## Control flow
Implementations inspect the current user, path inode metadata, owners/groups, ACLs, and requested mode bits. Parent checks fall back to the closest existing ancestor for missing paths and pass for invalid paths or root-like paths per interface comments.

## State and persistence behavior
The interface itself is stateless. Implementations read inode permission state and security context but do not normally mutate metadata.

## Dependencies and integration points
It depends on `LockedInodePath`, `Mode.Bits`, `AccessControlException`, and `InvalidPathException`. `DefaultFileSystemMaster` uses a concrete implementation to guard create, delete, rename, set-attribute, access-check, and listing operations.

## Risks
Interface comments define permissive behavior for invalid paths; implementations must match this exactly to avoid breaking create-on-missing-path flows. Set-attribute checks combine superuser, owner, and write requirements and are easy to weaken accidentally. Internal APIs in `FileSystemMaster` still note missing permission checks.

## Test signals
`PermissionCheckerTest` and file-system master permission tests should cover owner/group/other bits, ACLs, superuser/group membership, parent fallback, invalid paths, and set-attribute combinations.
