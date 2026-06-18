<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_buckets.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_buckets.go

## Purpose
Provides bucket detection for filer entries.

## Important APIs and Functions
`IsBucket(entry *Entry) bool` returns true for directory entries whose parent path equals `f.DirBucketsPath` and whose directory name does not start with `.`.

## Control Flow and State
The function checks directory mode, splits `FullPath` into parent and name, compares to configured bucket root, and excludes hidden/system bucket-like names.

## Persistence Behavior
No persistence. It influences whether other code treats a directory deletion as collection deletion or bucket event handling.

## Dependencies and Integration Points
Used by deletion (`DeleteEntryMetaAndData`) to detect collection/bucket deletion, by rename checks, and by metadata event bucket notifications. Depends on `Entry.IsDirectory` and `util.FullPath.DirAndName`.

## Risks
Correctness depends entirely on `DirBucketsPath` being configured consistently. Hidden directories under bucket root are intentionally not buckets.

## Test Signals
Indirectly tested by remote deletion and bucket event tests; no dedicated table for edge names, root paths, or nil entries in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_buckets.go -->
