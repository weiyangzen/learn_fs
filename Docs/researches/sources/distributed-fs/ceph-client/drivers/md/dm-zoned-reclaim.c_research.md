# sources/distributed-fs/ceph-client/drivers/md/dm-zoned-reclaim.c

## Purpose

`dm-zoned-reclaim.c` implements background reclaim for `dm-zoned`. It keeps enough random/cache zones free by moving valid blocks between data, buffer, random/cache, and sequential zones, then updating metadata and flushing it after successful remaps.

## Important APIs, Types, and Functions

`struct dmz_reclaim` stores metadata, delayed work/workqueue, a `dm_kcopyd` client and throttle, device index, copy-error state, flags, and last target access time. Public entry points are `dmz_ctr_reclaim()`, `dmz_dtr_reclaim()`, `dmz_suspend_reclaim()`, `dmz_resume_reclaim()`, `dmz_reclaim_bio_acc()`, and `dmz_schedule_reclaim()`. Core helpers are `dmz_reclaim_copy()`, `dmz_reclaim_align_wp()`, `dmz_reclaim_buf()`, `dmz_reclaim_seq_data()`, `dmz_reclaim_rnd_data()`, `dmz_reclaim_empty()`, `dmz_do_reclaim()`, and `dmz_should_reclaim()`.

## Control Flow

The constructor creates a kcopyd client and ordered workqueue, then queues reclaim. `dmz_reclaim_work()` checks device health, calculates the free random/cache percentage, and either reschedules or runs reclaim with throttling based on idle state and pressure. `dmz_do_reclaim()` chooses a candidate from metadata, then frees empty zones, moves random/cache data to a free sequential zone, merges buffer data into sequential data, or merges sequential data into its buffer depending on valid-block placement.

## State and Persistence Behavior

Data is moved through `dm_kcopyd_copy()`. Sequential destination holes are zeroed to align the write pointer. Metadata changes are made through bitmap copy/merge, invalidation, unmap/free/map calls, and a final `dmz_flush_metadata()` on success. Reclaim is interruptible by foreground I/O through `DMZ_RECLAIM_TERMINATE`.

## Dependencies and Integration Points

It depends on metadata for all zone selection and remapping, `dm-kcopyd` for copying, and the block layer for zeroout. The target updates access time, exposes an explicit `reclaim` message, and suspends/resumes reclaim.

## Risks and Test Signals

Key risks are sequential write ordering, interruption cleanup, no-free-zone pressure, copy success followed by metadata flush failure, and asymmetric cache policy in multi-device setups. Test low free-zone thresholds, idle reclaim, racing foreground I/O, empty-zone reclaim, random-to-sequential migration, both buffered sequential merge directions, and manual reclaim messages.
