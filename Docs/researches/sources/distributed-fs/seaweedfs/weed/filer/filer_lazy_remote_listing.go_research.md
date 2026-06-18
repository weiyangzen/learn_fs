<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_listing.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_listing.go

## Purpose
Populates local directory metadata from a remote storage listing when a mounted directory has an enabled listing cache TTL.

## Important APIs and Types
`xattrRemoteListingSyncedAt` stores last listing sync time. `lazyListContextKey` prevents recursion. `maybeLazyListFromRemote` performs TTL-gated remote listing and persistence. `updateDirectoryListingSyncedAt` records the cache timestamp on the directory entry.

## Control Flow and State
The function skips recursive contexts, missing remote storage, unmapped paths, and mounts with `ListingCacheTtlSeconds <= 0`. It reads the local directory xattr directly from the store; if fresh, it returns. It then singleflights by directory, maps the path to remote, lists remote children, skips local-only entries, updates existing remote-backed entries while preserving local chunks/attrs, creates missing entries, and updates the synced-at xattr.

## Persistence Behavior
Writes or updates filer metadata only. Directory timestamps and remote file sizes/mtimes are stored locally; file content remains remote. Listing errors are logged and swallowed.

## Dependencies and Integration Points
Called at the start of directory listing in `filer.go`. Integrates with remote storage client `ListDirectory`, `CreateEntry`, direct store updates, xattrs, and lazy fetch recursion guards.

## Risks
Stale remote deletions are not removed from local metadata in this code. Existing local-only entries are deliberately preserved, which can mask remote changes with the same name. Errors are swallowed, so callers cannot distinguish stale from fresh listings. `context.WithoutCancel` preserves work after callers leave.

## Test Signals
Tests cover population, disabled TTL, TTL cache skip, not-under-mount, preserving local-only entries, merging remote-backed entries while preserving local fields, and recursion guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_lazy_remote_listing.go -->
