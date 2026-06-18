# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MountTable.java

## Purpose
`MountTable` tracks Alluxio mount points and resolves between Alluxio namespace paths and underlying file-system URIs. It owns journaled mount-table state, UFS client registration, mount validation, read-only checks, mount id generation, and path sync cache access.

## Important APIs, Types, and Functions
Core APIs include `add()`, `addValidated()`, `validateMountPoint()`, `delete()`, `update()`, `getMountPoint()`, `getMountTable()`, `containsMountPoint()`, `findChildrenMountPoints()`, `isMountPoint()`, `reverseResolve()`, `resolve()`, `checkUnderWritableMountPoint()`, `getMountInfo()`, `getUfsClient()`, `getUfsSyncPathCache()`, and `createUnusedMountId()`. Nested `Resolution` exposes resolved UFS URI, UFS client/resource acquisition, shared flag, and mount id. Nested `ReverseResolution` exposes the resolved Alluxio URI and mount info. Nested `State` implements the journaled mount table.

## Control Flow, State, and Persistence
`MountTable` uses a `ReentrantReadWriteLock`. Add validates under the write lock, rejects duplicate Alluxio mount paths, rejects UFS mount paths that are prefix/suffix-related to existing mounts with the same scheme/authority, and checks that the new Alluxio mount path does not shadow an existing path in the parent UFS. Successful adds journal an `AddMountPointEntry`, and `State.applyAddMountPoint()` inserts `MountInfo` and registers the UFS mount with `UfsManager`.

Delete rejects root unmount, optionally blocks unmount if nested mount points exist, removes the UFS mount, and journals `DeleteMountPointEntry`; replay also removes through `State.applyDeleteMountPoint()`. `update()` deletes then re-adds a mount with new options/mount id, attempting to restore the old mount if re-add fails. `resolve()` finds the longest matching mount point, obtains a UFS client by mount id, lets UFS resolve the relative path, and returns a `Resolution`. Journal iteration emits add entries for non-root mounts only; root is considered initial state.

## Dependencies and Integration Points
The class integrates with `UfsManager`, `UnderFileSystem`, `UnderFileSystemConfiguration`, `MountInfo`, mount proto options, metrics counters for sync, `PathUtils`, `Journaled`, and `UfsSyncPathCache`. `InodeTree.syncPersistDirectory()` and `LazyUfsBlockLocationCache` use mount resolution to reach UFS paths.

## Risks
Validation performs live UFS `exists()` checks, so mount operations depend on UFS availability and permissions. `delete()` removes the UFS manager mount before applying/journaling the delete entry; if journaling fails, runtime state and durable state can diverge. `update()` nests delete/add calls under the write lock; this works with the reentrant write lock but broadens the critical section and performs UFS work while locked. `reverseResolve()` is linear over all mounts and can be expensive for many mount points.

## Test Signals
Tests should cover duplicate mount rejection, UFS prefix/suffix conflict detection, shadowing detection, root unmount rejection, nested mount checks, update rollback, longest-prefix resolution, reverse resolution, read-only write checks, mount id uniqueness, journal replay of add/delete, and checkpoint/journal iterator exclusion of root.
