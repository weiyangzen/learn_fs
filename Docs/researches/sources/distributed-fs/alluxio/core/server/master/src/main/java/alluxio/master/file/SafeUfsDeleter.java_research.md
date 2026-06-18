# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/SafeUfsDeleter.java

## Purpose
`SafeUfsDeleter` deletes persisted UFS entries for a subtree while avoiding recursive UFS deletes when Alluxio metadata is not known to be in sync with UFS contents.

## Important APIs, types, and functions
The constructor receives `MountTable`, inode store, the subtree inode list, and `DeletePOptions`. It may build a `UfsSyncChecker` and precheck persisted directories. `delete(AlluxioURI, Inode)` performs individual file deletes, recursive directory deletes only when safe, or rejects unsafe directory deletes. `isRecursiveDeleteSafe` checks whether a path is inside the deletion root and either unchecked or marked in sync.

## Control flow
Construction uses the first inode pair as deletion root. Unless delete is unchecked or Alluxio-only, it checks each persisted non-mount directory against UFS. During deletion, if the parent will be recursively deleted safely, the child is skipped. Files are deleted individually. Directories are recursively deleted only if that directory is safe; otherwise an IOException asks the user to sync UFS or delete unchecked.

## State and persistence behavior
The class holds the mount table, root path, and optional sync checker for one delete operation. It mutates external UFS state through `UnderFileSystem.deleteExistingFile` and `deleteExistingDirectory`. It does not mutate Alluxio inode state itself.

## Dependencies and integration points
It integrates delete internals in `DefaultFileSystemMaster`, `UfsSyncChecker`, `MountTable`, UFS resources, inode store, delete options, and mount-point detection.

## Risks
Recursive delete safety depends on accurate precomputed sync checks. Mount points are intentionally excluded from recursive directory checks to preserve mounted directories. Partial UFS recursive delete failures are noted as a TODO. Root-path prefix checks use string prefix matching, so path normalization must remain strict enough to avoid false containment.

## Test signals
Delete integration tests should cover unchecked deletes, Alluxio-only deletes, recursive safe/unsafe directories, mount points, missing UFS files/directories, and partial UFS failure behavior. Unit tests for `UfsSyncChecker` feed into confidence here.
