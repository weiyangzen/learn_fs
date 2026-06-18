# File Research: sources/block-storage/linux-dm/drivers/md/dm-zoned-reclaim.c

## Scope

This file implements background reclaim for the dm-zoned target. Reclaim frees cache/random zones and buffer zones by copying still-valid blocks to other zones, merging validity metadata, remapping chunks, and flushing metadata, with throttling based on free-zone pressure and target idleness.

## Public And Internal APIs Covered

- Lifecycle/control: `dmz_ctr_reclaim()`, `dmz_dtr_reclaim()`, `dmz_suspend_reclaim()`, `dmz_resume_reclaim()`.
- Scheduling/accounting: `dmz_reclaim_bio_acc()`, `dmz_schedule_reclaim()`.
- Work function: `dmz_reclaim_work()`.
- Copy/reclaim helpers: `dmz_reclaim_copy()`, `dmz_reclaim_align_wp()`, `dmz_reclaim_buf()`, `dmz_reclaim_seq_data()`, `dmz_reclaim_rnd_data()`, `dmz_reclaim_empty()`, `dmz_do_reclaim()`.
- Policy helpers: `dmz_reclaim_percentage()`, `dmz_should_reclaim()`, `dmz_target_idle()`.
- `dm_kcopyd` completion: `dmz_reclaim_kcopy_end()`.

## Control Flow And Behavior

- `dmz_ctr_reclaim()` allocates one reclaim context for a device index, creates a throttled `dm_kcopyd` client, creates an ordered reclaim workqueue, and queues immediate reclaim work.
- Reclaim is considered idle after 10 seconds without target bio accounting. When idle, reclaim can run broadly; when busy, it starts only if unmapped cache/random zones fall below low-watermark pressure.
- `dmz_reclaim_work()` exits if a device is dying, computes free-zone percentage, configures kcopyd throttle, runs one reclaim attempt, checks devices after non-interrupt errors, and reschedules if reclaim is still needed.
- `dmz_do_reclaim()` asks metadata for a reclaim-locked candidate. Empty random/cache zones are freed directly. Weighted random/cache data zones are copied to a free sequential or fallback random zone. Buffered sequential zones either merge buffer into data or data into buffer depending on valid-block positions.
- `dmz_reclaim_copy()` iterates valid extents from the source zone, optionally zero-fills holes to advance a sequential destination's write pointer, submits synchronous `dm_kcopyd` copies, checks for dying devices, and honors reclaim termination requests.
- `dmz_reclaim_buf()` copies a buffer zone back into its sequential data zone at/after the data write pointer, merges valid blocks, invalidates/frees the buffer, and clears the reclaim lock.
- `dmz_reclaim_seq_data()` copies a sequential data zone into its buffer zone, merges valid blocks, frees the old data zone, and remaps the chunk to the buffer zone.
- `dmz_reclaim_rnd_data()` allocates a free sequential zone, or a random/cache fallback when cache zones exist, copies valid blocks, copies validity metadata, frees the old data zone, and remaps the chunk.
- Successful reclaim flushes metadata before reporting success.

## State And Data Structures

- `struct dmz_reclaim` stores metadata, delayed work/workqueue, kcopyd client/throttle/error, device index, state flags, and last access time.
- `DMZ_RECLAIM_KCOPY` marks an in-flight kcopyd operation and is waited on via bit wait queues.
- Watermark constants control policy: idle period, low free-zone percentage, and high free-zone percentage.

## Dependencies

- dm-zoned metadata APIs for zone selection, validity bitmap operations, map/unmap/free, flush locking, and free-zone counts.
- `dm_kcopyd` for copying valid extents between zones.
- Block APIs for zeroout when aligning sequential-zone write pointers.
- Kernel delayed workqueues, bit wait/wakeup, jiffies timing, and module infrastructure.

## Risks And Invariants

- Reclaim must hold metadata/map/flush locks in the right order around metadata mutations and release the zone reclaim lock exactly once.
- Sequential destinations require writes at the write pointer; holes are zeroed so later copied extents remain sequential.
- Candidate zones may become active or be requested to terminate; active/reclaim state prevents data movement under live I/O.
- Valid-block bitmap merge/copy must happen only after data copying succeeds, and metadata must be flushed before reclaimed zones are considered safely reusable.
- If free sequential zones are exhausted, reclaim may need to reclaim a buffered sequential zone first to make future random-zone reclaim possible.
