<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_delete_entry.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_delete_entry.go

## Purpose
Coordinates deletion of filer metadata, associated chunks, remote objects, hard link metadata, and bucket collections.

## Important APIs and Types
`DeleteEntryMetaAndData` is the public deletion entry point. `doBatchDeleteFolderMetaAndData` recursively deletes directory children. `doDeleteEntryMetaAndData` deletes a single entry. `DoDeleteCollection` asks the master to delete a collection. `maybeDeleteHardLinks` removes hard-link KV records. Callback types `OnChunksFunc` and `OnHardLinkIdsFunc` allow child traversal to collect cleanup work.

## Control Flow and State
Deletion loads the entry, honors `ifNotModifiedAfter`, detects buckets, recursively deletes children when needed, deletes the entry itself, then schedules chunk deletion unless hard links still reference data. Folder deletion pages through children, rejects non-recursive non-empty deletes, optionally deletes remote child objects, sends metadata notifications, collects chunks, deletes all folder children from the store, and notifies for the directory.

## Persistence Behavior
Metadata removal is synchronous through the store. Chunk deletion is asynchronous via `DeleteChunks`. Remote object deletion occurs before local metadata deletion for local-origin events. Bucket deletion calls the master collection-delete RPC.

## Dependencies and Integration Points
Uses `FindEntry`, `ListDirectoryEntries`, `Store.DeleteFolderChildren`, `Store.DeleteOneEntry`, `maybeDeleteFromRemote`, `NotifyUpdateEvent`, hard-link KV cleanup, and master collection deletion.

## Risks
Remote deletion happens before local metadata deletion, so a later local store failure can leave remote data removed but metadata still present. Recursive delete error handling depends on `ignoreRecursiveError`. Hard-link deletion has a noted collection limitation. Bucket deletion relies on `IsBucket` and store bucket-drop capability.

## Test Signals
Remote deletion behavior and failure ordering are covered by `filer_lazy_remote_test.go`. Generic non-empty folder and hard-link edge cases are less directly covered in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_delete_entry.go -->
