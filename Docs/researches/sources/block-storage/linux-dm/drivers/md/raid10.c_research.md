# File Research: sources/block-storage/linux-dm/drivers/md/raid10.c

## Purpose

`raid10.c` implements the Linux MD RAID10 personality: a striped mirror layout with configurable near copies, far copies, offset copies, and far-set placement. It registers an `md_personality` named `raid10` and provides the full lifecycle surface used by MD core: request submission, status, error handling, hot add/remove, spare activation, sync/recovery, reshape, resize, takeover from RAID0, quiesce, and module init/exit.

The file includes shared RAID1/RAID10 helpers from `raid1-10.c` and relies heavily on MD core structures from `md.h`, bitmap helpers from `md-bitmap.h`, RAID0 takeover metadata from `raid0.h`, and its local private structures from `raid10.h`.

## Main Data And State

The central runtime object is `struct r10conf`, allocated by `setup_conf()` and stored in `mddev->private`. It owns the active geometry (`geo`), previous geometry during reshape (`prev`), mirror slots, retry queues, pending write lists, barrier counters, resync pools, a temporary page for correction, and clustered resync window bounds.

Per-request state is `struct r10bio`. Normal read/write requests allocate it from `conf->r10bio_pool`; sync/recovery/reshape requests allocate larger buffers from `conf->r10buf_pool`. Each `r10bio` records the virtual sector, sector count, state bits, master bio, read slot, and a flexible `devs[]` array mapping each copy to a physical device number and sector.

State bits in `r10bio->state` drive the async continuation logic in `raid10d()`: normal read retry (`R10BIO_ReadError`), normal write error or bad-block cleanup (`R10BIO_WriteError`, `R10BIO_MadeGood`), sync (`R10BIO_IsSync`), recovery (`R10BIO_IsRecover`), reshape (`R10BIO_IsReshape`), degraded writes, previous-layout I/O during reshape, failfast, and discard.

## Layout Mapping

`__raid10_find_phys()` maps a virtual sector to all physical copy locations for a supplied geometry. It handles:

- `near_copies`: adjacent RAID0-style copies.
- `far_copies`: additional copies at a stride.
- `far_offset`: far copies offset by adjacent stripes instead of a large stride.
- `far_set_size`: optional grouping that confines far-copy shifts inside device sets, including the final uneven set.

`raid10_find_phys()` selects either current or previous geometry depending on reshape progress and `mddev->reshape_backwards`, setting `R10BIO_Previous` when using the old layout. `raid10_find_virt()` performs the reverse mapping from physical sector/device to virtual sector, mainly for recovery where work is driven by physical addresses.

`raid10_size()` computes array sectors from member sectors, far copies, and near copies. `calc_sectors()` computes usable per-device sectors and far-copy stride. `setup_geo()` decodes MD layout bits into geometry, validates chunk size and copy count, and supports original, old "improved but buggy", and fixed far-set layouts.

## Normal Read Path

`raid10_make_request()` is the personality entry point. It handles prefush through MD, calls `md_write_start()`, attempts optimized discard handling, splits bios that cross chunk boundaries when necessary, and dispatches to `__make_request()`.

For reads, `raid10_read_request()` first passes `regular_request_wait()` to respect barriers and reshape boundaries. It then calls `read_balance()` to choose a readable mirror. `read_balance()`:

- Computes copy locations.
- Avoids blocked copies, faulty devices, devices not yet recovered far enough, and known bad blocks.
- Avoids balancing across active resync windows or clustered resync regions.
- Chooses non-rotational devices by lowest pending count, far-copy layouts by lowest address, and near layouts by estimated head distance.
- Sets failfast only when alternative readable copies exist.

The selected read is submitted as a cloned bio with `raid10_end_read_request()` as completion. Successful completion marks `R10BIO_Uptodate` and ends the master bio. Failed reads are retried unless no remaining mirror can preserve availability; retry work is queued to `raid10d()`.

## Normal Write Path

`raid10_write_request()` waits for clustered resync conflicts, normal barriers, reshape metadata safety, and blocked devices. It maps all copies, pins selected `rdev`s under RCU, avoids faulty devices, limits the write length around bad-block ranges, optionally splits the bio, starts the bitmap write, and submits one cloned write per live main or replacement device via `raid10_write_one_disk()`.

Writes are queued through a plug callback (`raid10_unplug()`) or `conf->pending_bio_list`; `flush_pending_writes()` flushes bitmap writes before submitting queued bios. `raid10_end_write_request()` tracks errors per main or replacement device, sets `WriteErrorSeen`/`WantReplacement`, can fail fast devices, records made-good blocks, and completes through `one_write_done()`. `close_write()` ends bitmap and MD write accounting only after mirrored write completion.

`handle_write_completed()` is the process-context cleanup path for write errors and bad-block updates. For normal writes it clears made-good bad-block records, narrows write failures to bad-block granularity via `narrow_write_error()`, may fail devices, and only completes master bios after metadata changes are safe.

## Discard Path

`raid10_handle_discard()` optimizes large aligned discard requests when reshape is not active. It waits on the barrier, aligns the discard to full stripe-size regions, splits unaligned head/tail bios back through the normal path, then emits discard ranges to each live main and replacement device. Far layouts may require multiple `r10bio` objects linked through the first one. Discard completion ignores device discard errors from the upper layer perspective and uses `raid_end_discard_bio()` to unwind linked requests.

Small, reshape-overlapping, or unsupported discards return `-EAGAIN` so the regular write path handles them conservatively.

## Barriers, Freezing, And Retry Thread

The file implements its own barrier protocol around `conf->nr_pending`, `nr_waiting`, `nr_queued`, and `barrier`.

- Normal I/O calls `wait_barrier()` and later `allow_barrier()`.
- Background sync/recovery/reshape calls `raise_barrier()` and later `lower_barrier()`.
- `freeze_array()`/`unfreeze_array()` temporarily block new I/O while read or write error correction runs synchronously.

`raid10d()` is the MD thread callback. It checks recovery, drains delayed end-io completions after superblock updates, flushes pending writes, then consumes `retry_list`. Depending on `r10bio` flags it dispatches to write cleanup, reshape continuation, sync writeback, recovery writeback, or read-error repair.

## Error Handling

`raid10_error()` fails an `rdev` unless doing so would make required data unavailable and `fail_last_dev` is false. It clears `In_sync`, increments `mddev->degraded`, marks recovery interrupted, blocks and faults the rdev, and requests a superblock update.

Read-error handling is two-stage. IRQ completion queues the failed read. `handle_read_error()` freezes the array when possible and calls `fix_read_error()`, which tries page-sized reads from alternate mirrors, writes corrected data back, verifies it, updates corrected error counters, and records bad blocks or fails devices as needed. `check_decay_read_errors()` decays per-device read-error counts over time before threshold checks.

Recovery read errors use `fix_recovery_read_error()`, which retries page-sized reads and writes, records bad blocks on source and destination devices, and aborts recovery when bad-block recording cannot preserve correctness.

## Resync And Recovery

`init_resync()` creates the resync buffer mempool, noting whether replacements exist. `raid10_alloc_init_r10buf()` resets pooled bios before reuse.

`raid10_sync_request()` is the MD sync callback and handles both logical resync and physical recovery:

- It skips full rebuilds when a clean array with no bitmap and no requested recovery can be safely trusted.
- It closes sync state and bitmap accounting at the end or abort path.
- For `MD_RECOVERY_RESHAPE`, it delegates to `reshape_request()`.
- For recovery, it walks physical sectors and creates one linked `r10bio` per out-of-sync or replacement target, maps to a readable virtual copy, reads from a good mirror, and schedules writes to main and replacement devices.
- For resync, it reads all available copies for a virtual stripe, compares pages, counts mismatches, and writes corrected data to out-of-date copies or replacements unless running check-only mode.

`sync_request_write()` treats the lowest successful read copy as authoritative for resync. It writes mismatched or unreadable copies and replacement devices, using bad-block and failfast handling. `recovery_request_write()` writes recovered data to the target main/replacement device after a successful recovery read.

Clustered MD support broadcasts resync windows through `md_cluster_ops->resync_info_update()` and suppresses conflicting normal I/O with `area_resyncing()`.

## Disk Add, Remove, Spare Activation

`raid10_add_disk()` places a new `md_rdev` into a missing mirror slot or as a replacement for a device marked `WantReplacement`, with constraints around recovery state and availability. It stacks queue limits and may force full sync.

`raid10_remove_disk()` removes a non-sync or faulty rdev when no pending references exist. If a replacement exists after removing the main rdev, it promotes the replacement to `rdev` with memory barriers so readers never observe both pointers absent.

`raid10_spare_active()` marks fully recovered rdevs or replacements `In_sync`, promotes replacements, faults replaced old devices so they are removed, updates degradation count, and notifies sysfs.

## Reshape And Resize

Reshape is supported only for near/offset-style layouts, not classic far layouts. `raid10_check_reshape()` validates the new geometry, copy count, array-size alignment, current availability, and allocates an expanded mirror table when adding disks.

`raid10_start_reshape()` commits new geometry, swaps in the new mirror array, validates data-offset separation to avoid overwrite, resizes bitmaps, adds spares for new disks, recalculates degradation against old and new geometries, sets recovery bits, and starts `md_do_sync` as the reshape thread.

`reshape_request()` copies data chunk by chunk between old and new layouts. It maintains `reshape_progress` and `reshape_safe`, periodically persists metadata checkpoints, raises barriers, reads from the previous layout, prepares writes to the new layout, and updates clustered resync windows. `reshape_request_write()` handles read completion, falls back to `handle_reshape_read_error()` for alternate reads, and submits all new-layout writes. `end_reshape()` finalizes geometry after successful reshape, and `raid10_finish_reshape()` commits layout/chunk/delta fields and handles disk-count changes.

`raid10_resize()` supports resizing near and offset arrays, rejects far arrays without offset, resizes bitmap and array sectors, updates recovery checkpoint for expansion, and recalculates device sectors.

## Startup, Teardown, And Personality Registration

`setup_conf()` allocates `r10conf`, mirrors, temporary page, bio pools, split bioset, prior/current geometry, barrier state, and a private thread. `raid10_run()` binds existing rdevs into mirror slots, validates clustered restrictions, configures queue discard and I/O hints, checks enough mirrors exist, computes degradation, registers integrity, handles resumed reshape, and exposes array size.

`raid10_free()` releases pools, pages, mirror arrays, bioset, and config. `raid10_quiesce()` raises or lowers the barrier. `raid10_takeover()` supports takeover from a single-zone RAID0 by doubling disks and using a near=2/far=1 layout.

The file ends with `raid10_personality`, `raid_init()`, `raid_exit()`, and module metadata/aliases.

## Dependencies And Integration Points

Key external dependencies include MD core request/accounting/recovery APIs (`md_write_start`, `md_done_sync`, `md_check_recovery`, `md_register_thread`, `md_error`, `md_update_sb` indirectly), bitmap APIs, bad-block APIs, block-layer bio split/clone/submit APIs, RCU-protected `md_rdev` pointer access, sysfs notifications, queue limit configuration, clustered MD callbacks, and trace remap events.

The implementation assumes MD core serializes configuration changes with `reconfig_mutex` in the places documented by `raid10.h`. Runtime paths must use RCU and `nr_pending` carefully because mirror `rdev` pointers can be cleared asynchronously.

## Notable Risks And Invariants

- `conf->barrier` and `conf->nr_pending` must remain balanced; lost `allow_barrier()`/`lower_barrier()` calls can hang the array.
- `rdev` pointer access relies on RCU plus `nr_pending`, or on reshape/recovery/configuration contexts where the header documents it as safe.
- Reshape safety depends on correctly persisted `reshape_position`, `reshape_safe`, and `offset_diff`; wrong values can overwrite data not yet copied.
- Bad-block handling intentionally limits bio sizes and may split writes around problematic sectors; callers must preserve master bio chaining.
- Replacement promotion in `raid10_remove_disk()` uses memory barriers to avoid transient no-device observations.
- Several reshape error paths contain FIXME comments for bad-block recording; reshape read/write error handling is less complete than normal resync/recovery.
- The file uses BUG/WARN assertions for impossible state transitions, especially in mapping, recovery, and discard handling.

## Testing Signals

Useful coverage would include near/far/offset/far-set mapping round trips, read balancing under bad blocks and replacements, write error paths with bad-block logs, discard alignment and far-copy multi-r10bio handling, recovery with replacements, clustered resync windows, and forward/backward reshape with metadata checkpoint interruption/restart.
