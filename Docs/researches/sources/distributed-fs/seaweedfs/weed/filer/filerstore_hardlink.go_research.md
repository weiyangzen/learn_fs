<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_hardlink.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filerstore_hardlink.go

## Purpose
Implements hard-link metadata storage on top of the filer store wrapper's KV API.

## Important APIs and Functions
`handleUpdateToHardLinks` writes new hard-link state and removes old link state when an entry changes hard-link ID. `setHardLink` serializes attributes/chunks to KV under `HardLinkId`. `maybeReadHardLink` hydrates entry attributes/chunks from KV. `DeleteHardLink` decrements link count, updates ctime, rewrites KV, or deletes the KV record when count reaches zero.

## Control Flow and State
Directories are skipped. Insert/update writes shared blob when `HardLinkId` is set, then checks existing entry to remove an old hard-link record if ID changed. Reads transparently replace entry attributes/chunks from KV. Deletes skip hard-link counter changes when context `OP` is `MV`, preserving counts during moves.

## Persistence Behavior
Hard-link shared state persists in the default store KV namespace. Directory entries still persist separately with their `HardLinkId`; chunk metadata is shared via encoded blob.

## Dependencies and Integration Points
Called by `FilerStoreWrapper` insert/update/find/list/delete methods. Uses `Entry.EncodeAttributesAndChunks`, `DecodeAttributesAndChunks`, KV operations, and `ErrKvNotFound`.

## Risks
KV consistency is critical; if KV updates fail or are not transactional with entry updates, link counters and entry metadata can diverge. `maybeReadHardLink` returns errors but wrapper callers often ignore the returned error, potentially leaving partial entries. Context string key `OP` is untyped.

## Test Signals
No direct hard-link KV tests in this subset. Inode tests cover hard-link inode derivation only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filerstore_hardlink.go -->
