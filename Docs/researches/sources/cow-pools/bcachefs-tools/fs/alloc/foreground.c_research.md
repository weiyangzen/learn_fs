# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/foreground.c

Core foreground bucket and sector allocator implementation. It manages open buckets, write points, allocation waits, device selection, replica placement, erasure-coded allocation, partial bucket reuse, allocator diagnostics, and shutdown/drop behavior.

Main responsibilities:
- Maintain open bucket handles, freelist, hash table, and partial open-bucket list.
- Allocate buckets from `BTREE_ID_freespace`, with an early alloc-btree scan path before freespace is initialized.
- Avoid superblock buckets, nouse buckets, open buckets, nocow-locked buckets, and buckets whose empty journal sequence is not flushed.
- Trigger discard, GC generation cleanup, copygc, and cached-bucket invalidation when allocation pressure indicates they may unblock allocation.
- Select devices through `dev_stripe_state`, a weighted fair virtual-time scheme biased toward devices with more free space.
- Allocate enough effective durability to satisfy requested replicas, including zero-durability cache-device handling.
- Reuse write-point open buckets and partial open buckets before allocating new buckets.
- Allocate from partially constructed erasure-code stripes when appropriate.
- Resize active write points based on stranded free-space pressure.
- Stop/drop open buckets for device removal, erasure-coding shutdown, or filesystem shutdown.
- Render allocator, open-bucket, write-point, device, request, and stuck-wait diagnostics.
- Filter allocator wait wakeups through per-device `alloc_wake_counter` snapshots.

Important control flow:
- `bch2_bucket_alloc_trans()` allocates a single bucket from `req->ca`, handling free-space pressure, copygc wakeups, discard wakeups, waitlist parking, and early/freespace allocation paths.
- `bch2_bucket_alloc_set_trans()` sorts candidate devices and attempts allocation until enough effective durability is accumulated.
- `bucket_alloc_from_stripe()` reuses buckets already attached to an EC stripe head.
- `bch2_alloc_sectors_req()` is the high-level allocator path: finds a write point, computes eligible devices from target/data type, reuses open buckets, tries partial buckets, EC stripe allocation, normal allocation, target fallback, EC fallback, and final alignment.
- `writepoint_find()` maps hashed write streams to write points, grows the write-point pool when possible, or recycles the oldest write point.
- `try_decrease_writepoints()` drops a write point when allocation stalls and stranded open-bucket space is too high.
- `__bch2_wait_on_allocator()` waits with timeout diagnostics and avoids full retries for unrelated fs-wide wakeups.

Concurrency:
- `allocator.freelist_lock` protects open bucket freelist/hash/partial arrays.
- Each open bucket has its own spinlock and atomic pin count.
- Write points are protected by per-write-point mutexes.
- Write point hash mutation uses `write_points_hash_lock` and RCU hlist operations.
- Allocation waiters use closure waitlists plus device wake-counter snapshots to reduce retry storms.

Failure and fallback behavior:
- Returns rich bcachefs error codes for no buckets, open-bucket exhaustion, blocked allocation, insufficient devices, no progress, and EC allocation failure.
- Can commit degraded allocation when at least one replica exists and waiting cannot make progress.
- Copygc watermark writes avoid deadlocking the freeing operation against its own wait.
- Btree writes avoid unsafe degradation in copygc bailout cases because under-replicated btree writes can force emergency read-only.

Dependencies:
- Alloc/background/check/discard/disk group helpers, btree iter/update/check APIs, copygc, EC create/init, nocow locking, write types, journal state, counters, time stats, and device/member state.
