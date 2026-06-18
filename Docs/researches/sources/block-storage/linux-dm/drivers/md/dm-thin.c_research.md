# File Research: sources/block-storage/linux-dm/drivers/md/dm-thin.c

## Purpose
Implements the device-mapper `thin-pool` and `thin` targets. The pool target owns metadata, data-device allocation, snapshots, commit policy, discard handling, space exhaustion behavior, and lifecycle coordination. The thin target maps read/write bios through pool metadata, provisions blocks on demand, breaks snapshot sharing, and exposes per-thin status and limits.

## Main Interfaces
- Pool target operations: `pool_ctr()`, `pool_dtr()`, `pool_map()`, `pool_preresume()`, `pool_resume()`, `pool_presuspend()`, `pool_postsuspend()`, `pool_message()`, `pool_status()`, `pool_iterate_devices()`, and `pool_io_hints()`.
- Thin target operations: `thin_ctr()`, `thin_dtr()`, `thin_map()`, `thin_endio()`, `thin_preresume()`, `thin_presuspend()`, `thin_postsuspend()`, `thin_status()`, `thin_iterate_devices()`, and `thin_io_hints()`.
- Core IO path: `thin_bio_map()`, `process_bio()`, `process_cell()`, `provision_block()`, `process_shared_bio()`, `break_sharing()`, `process_deferred_bios()`, and `do_worker()`.
- Metadata and allocation path: `commit()`, `alloc_data_block()`, `metadata_operation_failed()`, `abort_transaction()`, `maybe_resize_data_dev()`, and `maybe_resize_metadata_dev()`.
- Pool control messages: `create_thin`, `create_snap`, `delete`, `set_transaction_id`, `reserve_metadata_snap`, and `release_metadata_snap`.

## Control Flow
Thin bios are first normalized by `thin_map()` and sent to `thin_bio_map()`. Flushes and discards are deferred to the pool worker; normal bios try a nonblocking metadata lookup while holding a virtual bio-prison cell to avoid races with discard. If a block is mapped and unshared, the bio is remapped directly to the pool data device. If lookup blocks, the block is unmapped, or the mapping is shared, the cell is queued to the ordered pool workqueue.

The worker drains prepared mapping/discard lists, then processes deferred cells and bios for each active thin. Unmapped writes allocate a data block and either zero it, copy data from an external origin, or complete a full-block overwrite directly with a hooked endio. Shared writes allocate a new data block, quiesce shared reads through a deferred set, copy old data with kcopyd, insert the new mapping, and then release detained bios. Reads from unmapped thin blocks return zeroes or read from an external origin if configured.

Pool metadata commits are batched. Bios that require a commit, such as flush/FUA after metadata changes, are held in `deferred_flush_bios` or `deferred_flush_completions`; `process_deferred_bios()` commits once and then issues or completes the accumulated bios. A periodic delayed worker wakes the pool to limit uncommitted transaction age.

Discard handling is mode- and feature-dependent. Without passdown, mapped ranges are removed after all IO quiesces. With passdown, the code removes mappings, temporarily increments data-block references to prevent reallocation races, issues discard bios to unshared physical ranges, then decrements references after passdown completes.

## State And Synchronization
The global `dm_thin_pool_table` maps pool mapped devices and metadata devices to shared `struct pool` objects under a mutex. Each pool has an ordered workqueue, bio prison, kcopyd client, metadata handle, deferred sets for shared reads and all IO, prepared mapping/discard lists, active thin list, and callback function pointers selected by pool mode.

`struct thin_c` tracks its pool, opened thin metadata device, optional external origin, deferred bios, retry-on-resume bios, deferred prison cells, sorted bio tree, and an RCU-visible active-thin list node. Active thin iteration uses RCU plus a refcount/completion pair so destruction waits for worker iteration to finish.

The pool mode state machine controls write, out-of-data-space, out-of-metadata-space, read-only, and fail behavior. Mode transitions swap IO callbacks, adjust metadata read/write state, cancel or schedule no-space timeouts, and send table events. Metadata failures abort the current transaction, set `needs_check`, and degrade the pool to read-only or fail mode.

## Integration Points
The file depends heavily on `dm-thin-metadata.h` for persistent metadata operations, `dm-bio-prison-v1` for per-block serialization, `dm_deferred_set` for quiescing, and `dm-kcopyd` for zero/copy operations. It registers two DM targets, `thin-pool` and `thin`, with the device-mapper core and uses DM target messages/status/table events for user-space control.

## Notable Behaviors
- Thin snapshots are implemented by metadata tree sharing; data sharing is broken lazily on write using timestamp/shared-state metadata.
- Pool data block size must be between 64 KiB and 1 GiB, and thin device ids are limited to 24 bits.
- `error_if_no_space` controls whether out-of-data-space IO is failed immediately or queued until resume; queued IO can later be forced to `BLK_STS_NOSPC` by the no-space timeout.
- Metadata pre-commit flushes the data device before committing metadata so newly inserted mappings survive crashes.
- Read-only pool modes still service reads and may return zeroes or origin data for unmapped blocks, but writes that need provisioning are failed or queued according to mode.
- `check_at_most_once`-style behavior is not here; thin instead sorts deferred bios/cells by sector to improve locality before processing.

## Risks And Review Focus
- Bio-prison cell ownership is subtle; every path must release, defer, requeue, or error cells exactly once.
- Discard passdown depends on temporary reference increments and shared-status double checks to avoid discarding blocks still referenced by other thins.
- Mode transitions update many function pointers; inconsistent callback state would change IO semantics under error conditions.
- Metadata error handling deliberately aborts transactions and sets `needs_check`; recovery paths should preserve that conservative behavior.
- Suspend/resume ordering matters: pool resume requeues bios and resumes active thins before clearing the pool suspended flag.
