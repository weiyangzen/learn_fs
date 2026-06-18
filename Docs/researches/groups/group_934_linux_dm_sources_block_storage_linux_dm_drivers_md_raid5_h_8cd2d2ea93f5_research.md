# Group Research: group_934_linux_dm_sources_block_storage_linux_dm_drivers_md_raid5_h_8cd2d2ea93f5

Scope: `Docs/research_subset_a.md` / `sources/block-storage/linux-dm`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid5.h

## Purpose
Internal header for the Linux MD RAID4/5/6 personality. It defines the stripe cache data model, per-stripe and per-device state flags, RAID5/RAID6 layout constants, worker/cache/journal bookkeeping, and exported helper prototypes used by the RAID5 implementation files.

## Main Definitions
- `enum check_states`: parity check and repair state machine, covering idle, P check, Q check, dual P/Q check, check result, repair compute run, and repair compute result.
- `enum reconstruct_states`: write/reshape reconstruction state machine for prexor drain, drain/write, expand, and their result phases.
- `struct stripe_head`: central per-stripe cache object. It records stripe identity, parity/Q disk indexes, generation, state flags, refcount, locks, worker group, batching, log/PPL state, r5c journal membership, partial parity page, async operation targets/results, optional page packing metadata, and the flexible `dev[]` array of per-disk `struct r5dev`.
- `struct r5dev`: per-device member inside a stripe, including normal and replacement bios/vectors, cache/original pages, page offset, bio queues (`toread`, `read`, `towrite`, `written`), target sector, device flags, log checksum, and write hint.
- `struct stripe_head_state`: transient state summary built by `handle_stripe()`, including sync/expand/replace state, counts for locked/uptodate/read/write/failed/written devices, compute/fill/drain needs, failed device indexes, parity failure flags, operation request bits, blocked rdev, bad-block handling, log failure, and extra-page wait state.
- `enum r5dev_flags`: per-device stripe flags for cache validity and I/O (`R5_UPTODATE`, `R5_LOCKED`, `R5_DOUBLE_LOCKED`, `R5_OVERWRITE`), requested actions (`R5_Wantread`, `R5_Wantwrite`, `R5_Wantcompute`, `R5_Wantfill`, `R5_Wantdrain`, `R5_WantReplace`), error/recovery state, replacement handling, discard, skip-copy, journal residency, and write-back prexor original-page freshness.
- Stripe state enum: per-stripe flags such as `STRIPE_ACTIVE`, `STRIPE_HANDLE`, `STRIPE_SYNCING`, `STRIPE_INSYNC`, `STRIPE_PREREAD_ACTIVE`, `STRIPE_DELAYED`, `STRIPE_EXPANDING`, `STRIPE_FULL_WRITE`, `STRIPE_BIOFILL_RUN`, `STRIPE_COMPUTE_RUN`, `STRIPE_BATCH_READY`, `STRIPE_LOG_TRAPPED`, and r5c caching/list/prefetch states.
- Operation and policy enums: `STRIPE_OP_*` request bits for biofill, compute, prexor, biodrain, reconstruct, check, and partial parity; parity RMW preferences; and syndrome source selection modes.
- `struct disk_info`: per-array disk slot with original rdev, replacement rdev, and an extra prexor page.
- `struct r5worker` / `struct r5worker_group`: workqueue execution structures for handling stripes and maintaining per-hash-lock temporary inactive lists.
- `enum r5c_journal_mode` and `enum r5_cache_state`: write-through/write-back journal mode and stripe-cache/log pressure state bits.
- `struct r5pending_data`: pending bio batch keyed by stripe sector.
- `struct r5conf`: array-level RAID5/6 configuration and runtime state, including stripe hash locks/table, MD device pointer, layout/chunk/degraded parameters, stripe cache bounds, reshape metadata, stripe queues, aligned-read retry tracking, preread and full-write counters, slab cache, quiesce/recovery state, per-CPU scratch pages, inactive/released stripe pools, r5c full/partial stripe lists, wait queues, shrinker, disk table, bioset, takeover thread, worker groups, log state, and pending-bio batching state.

## Important Behavior and Contracts
- The opening comments document the stripe cache buffer lifecycle: `R5_UPTODATE` and `R5_LOCKED` encode empty, want, dirty, and clean states; completion paths transition want/dirty buffers back to clean or empty, sometimes outside `STRIPE_ACTIVE`.
- `STRIPE_INSYNC` distinguishes a clean reconstructed block from a block that has actually been written to the spare or parity device during rebuild/resync.
- Stripe list membership is tied to `atomic_t count` and `STRIPE_HANDLE`: zero-ref stripes with handle work go to the handle list, while zero-ref stripes without handle work go to inactive lists.
- Stripe operations are designed around async_tx offload. The comments describe ordering constraints among parity checks, writes, and compute-block operations so destructive parity checks and dependent writes do not run concurrently.
- Plugging/preread handling delays stripes that need preread so more writes can be gathered for the same stripe, with `STRIPE_PREREAD_ACTIVE`, delayed/hold queues, and unplug promotion controlling write throughput.
- `disk_info.rdev` may be cleared asynchronously by disk removal. Safe access requires `mddev->reconfig_mutex`, known resync/recovery/reshape context, or RCU plus incrementing `rdev->nr_pending`.
- `NR_STRIPE_HASH_LOCKS` is fixed at 8 and explicitly constrained below 64 because code can take all hash locks, making lock nesting depth a practical limit.
- `RAID5_STRIPE_SIZE`, `RAID5_STRIPE_SHIFT`, and `RAID5_STRIPE_SECTORS` abstract the normal `PAGE_SIZE == 4096` case from configurations that pack multiple logical stripes per page.
- `r5_next_bio()` walks stripe/device bio lists only while the next bio remains within the current stripe-device sector range, preventing traversal into a bio segment belonging to another device.
- RAID layout constants cover classic rotating parity RAID5 layouts, non-rotating RAID4-style parity layouts, DDF RAID6 layouts, and RAID6 variants aligned with RAID5 layouts for simpler RAID5-to-RAID6 conversion.
- `algorithm_valid_raid5()`, `algorithm_valid_raid6()`, and `algorithm_is_DDF()` encode the accepted layout ranges used by the implementation.

## Exported Interface
- `md_raid5_kick_device()`
- `raid5_set_cache_size()`
- `raid5_compute_blocknr()`
- `raid5_release_stripe()`
- `raid5_compute_sector()`
- `raid5_get_active_stripe()`
- `raid5_calc_degraded()`
- `r5c_journal_mode_set()`

## Dependencies
Includes Linux RAID XOR support, DMA engine/async infrastructure, and local locks. The types it exposes are coupled to MD core structures (`struct mddev`, `struct md_rdev`, `struct md_thread`), block-layer bios/pages, kernel lists/hash lists/llists, spinlocks, atomics, wait queues, shrinkers, percpu storage, RAID5 cache/log code (`r5l_*`, r5c), and partial parity log state.

## Role in Repository
This header is the private contract for `drivers/md/raid5*` implementation code. It does not perform I/O itself; it defines the shared in-memory model and constants that let the RAID5 personality coordinate stripe cache lookup, request attachment, parity computation, degraded/replacement operation, reshape, journaling/write-back cache, batching, and worker scheduling.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5.h -->