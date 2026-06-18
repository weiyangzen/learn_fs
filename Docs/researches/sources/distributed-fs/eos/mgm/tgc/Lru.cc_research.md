# sources/distributed-fs/eos/mgm/tgc/Lru.cc

## Purpose
`Lru.cc` implements the in-memory least-recently-used queue used by tape-GC to choose old disk replicas for eviction.

## Important APIs, Types, And Functions
Implemented methods include constructor validation, `fileAccessed()`, private `newFileHasBeenAccessed()` and `queuedFileHasBeenAccessed()`, `fileDeletedFromNamespace()`, `empty()`, `size()`, `getAndPopFidOfLeastUsedFile()`, `maxQueueSizeExceeded()`, and `toJson()`.

## Control Flow
`fileAccessed()` checks the fid-to-list map. New files are pushed to the front unless max size is already reached, in which case the overflow latch is set. Existing files are erased from their current list position and reinserted at the front. `getAndPopFidOfLeastUsedFile()` removes the back list entry and clears the overflow latch. `toJson()` writes size and fids from MRU to LRU, checking output length after each fid and at the end.

## State And Persistence
State is in-memory and not internally synchronized: max size, overflow latch, `std::list` queue, and hopscotch map from file ID to list iterator. Persistence is indirect only through JSON diagnostics.

## Dependencies And Integration Points
The implementation uses `MaxLenExceeded`, `IFileMD::id_t`, EOS Murmur3 hashing, and `tsl::hopscotch_map`. `TapeGc` owns an `Lru` and `MultiSpaceTapeGc` populates it from QuarkDB through `fileAccessed()` calls.

## Risks And Edge Cases
No mutex is present; callers must serialize access. When full, new fids are ignored rather than evicting an old entry, so max-size pressure can make the queue stale until pops occur. JSON output changes the stream to hex and zero-fill without restoring flags, which can affect later writes to the same stream. `toJson()` can exceed maxLen before throwing by design.

## Test Signals
Existing `LruTests` cover constructor errors, empty pop, ordering, deletion, max-size latch, JSON formatting, maxLen errors, and disabled performance. Additional concurrency tests would need external synchronization expectations.
