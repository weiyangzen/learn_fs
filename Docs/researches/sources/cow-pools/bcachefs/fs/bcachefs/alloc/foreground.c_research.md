# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/foreground.c

Core foreground bucket/sector allocator implementation. It manages open buckets, write points, device selection, allocation retries, EC stripe allocation, partial bucket reuse, allocator waiting, and allocator diagnostics.

Main responsibilities:
- Maintain open bucket handles and their hash table.
- Allocate buckets from either `BTREE_ID_freespace` or the early alloc-btree scan path before freespace is initialized.
- Avoid superblock buckets, nouse buckets, open buckets, nocow-locked buckets, and buckets whose empty journal sequence is not safely flushed.
- Schedule discard, GC generation cleanup, copygc, and cached bucket invalidation when allocation pressure indicates they can help.
- Choose devices with a weighted fair queue style `dev_stripe_state`, biased toward devices with more free space.
- Allocate enough effective durability to satisfy requested replicas, with special handling for zero-durability cache devices and erasure-coded buckets.
- Reuse write point open buckets and partial open buckets before allocating new buckets.
- Resize the number of active write points according to stranded space pressure.
- Stop/drop open buckets during device removal, EC shutdown, or filesystem shutdown.
- Render detailed allocator, open-bucket, write-point, device, and stuck-wait diagnostics.
- Filter allocator wait wakeups using per-device `alloc_wake_counter` snapshots.

Important control flow:
- `bch2_bucket_alloc_trans()` allocates one bucket from `req->ca`, possibly sleeping on open-bucket or free-space waitlists.
- `bch2_bucket_alloc_set_trans()` walks sorted candidate devices and accumulates bucket replicas.
- `bch2_alloc_sectors_req()` is the high-level allocator path: finds a write point, computes eligible devices, reuses open buckets, tries EC stripe allocation or normal bucket allocation, falls back from target-only to all devices when allowed, and aligns final sector availability.
- `bucket_alloc_from_stripe()` pulls buckets from partially constructed EC stripes.
- `writepoint_find()` hashes inode/write streams to write points, grows or recycles write points as needed.
- `__bch2_wait_on_allocator()` waits with timeout diagnostics and re-parks on unrelated fs-wide wakeups.

Concurrency:
- Open bucket freelist/hash/partial arrays are protected by `allocator.freelist_lock`.
- Individual open buckets have their own spinlock and atomic pin count.
- Write points are mutex-protected.
- Write point hash mutations use `write_points_hash_lock` and RCU hlist operations.
- Allocation waiters use closure waitlists plus per-device wake counters to avoid retry storms from unrelated device wakes.

Failure and fallback behavior:
- Returns rich bcachefs error codes for no buckets, insufficient devices, blocked allocation, open bucket exhaustion, EC failure, and no progress.
- Can reduce write point count and retry after blocked allocation/open-bucket failures.
- Copygc watermark writes avoid deadlocking copygc against its own free-space wait.
- Btree allocations are not allowed to degrade in the copygc bailout case because under-replicated btree writes can force emergency read-only.

Dependencies:
- Alloc/background/check/discard/disk group helpers, btree iter/update/check, copygc, EC creation/init, nocow locking, data write types, journal state, counters, time stats, and device/member state.
