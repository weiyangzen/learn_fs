# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/UfsSyncChecker.java

## Purpose
`UfsSyncChecker` checks whether persisted Alluxio directory metadata contains all direct children present in the corresponding UFS directory. It supports safe recursive UFS deletion by marking directories in sync only when UFS content is represented in Alluxio.

## Important APIs, types, and functions
The constructor stores `MountTable` and `ReadOnlyInodeStore`. `checkDirectory(InodeDirectory, AlluxioURI)` compares sorted UFS and Alluxio child names and records synced directories. `isDirectoryInSync(AlluxioURI)` queries the recorded result. Private `getChildrenInUFS` recursively lists UFS and caches listings by UFS URI; `trimIndirect` removes indirect descendants from recursive listing results.

## Control flow
`checkDirectory` requires a persisted directory, obtains UFS children, filters temporary names, sorts both sides, and advances through UFS children when a matching Alluxio child is found. If every UFS child is matched, the directory is recorded as synced. Otherwise ancestor synced markers are invalidated until a mount point boundary, and a debug message records the unmatched UFS child.

## State and persistence behavior
The checker is per-operation in-memory state. It caches recursive UFS listing arrays and synced directory markers. It does not mutate Alluxio or UFS state.

## Dependencies and integration points
It integrates with `SafeUfsDeleter`, `MountTable`, `ReadOnlyInodeStore`, UFS resources, `ListOptions.recursive`, `UfsStatus`, and path normalization utilities.

## Risks
The comparison checks that all UFS direct children are present in Alluxio, but extra Alluxio children do not make the directory unsafe. Recursive UFS listings are cached under the listed URI and reused for descendants, so path prefix trimming must be exact. Temporary-file filtering must match UFS temporary naming conventions. The class is not thread-safe.

## Test signals
Tests should cover matching/missing children, temporary files, directories with trailing separators, recursive listing reuse, mount-point ancestor invalidation, empty or null UFS listings, and extra Alluxio-only children.
