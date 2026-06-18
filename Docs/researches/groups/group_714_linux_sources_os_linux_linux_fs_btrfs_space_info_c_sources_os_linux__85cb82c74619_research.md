# Group Research: group_714_linux_sources_os_linux_linux_fs_btrfs_space_info_c_sources_os_linux__85cb82c74619

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/space-info.c -->
# File Research: sources/os/linux/linux/fs/btrfs/space-info.c

## Scope And Role

`space-info.c` implements Btrfs logical space accounting, reservation admission, ENOSPC ticketing, async reclaim, preemptive metadata reclaim, data reclaim, zoned reclaim hooks, and periodic block-group reclaim policy.

The file is the core bridge between high-level reservations and lower-level block group/chunk allocation. It manages `struct btrfs_space_info` instances for system, metadata, data, mixed data+metadata, and remap-tree space types, and it coordinates reclaim by running delayed items, delayed refs, delalloc writeback, ordered extent waits, delayed iputs, transaction commits, chunk allocation, zone reset, and zone reclaim.

A long introductory comment describes the reservation model:

- `space_info` is the arbiter for total usable logical space.
- `block_rsv` objects are reservation buckets accounted mostly through `bytes_may_use`.
- Reservation helpers charge `bytes_may_use`, then allocation and extent insertion move bytes through `bytes_reserved` and `bytes_used`.
- When immediate reservation fails, requesters create tickets and either wait for async reclaim or run priority reclaim inline.
- Metadata can overcommit against unallocated chunk space; data reservations do not overcommit.

## Main Data Structures

`struct reserve_ticket` is the per-waiter reservation object:

- `bytes`: remaining requested bytes.
- `error`: failure code, commonly `-ENOSPC`, `-EINTR`, or filesystem abort error.
- `steal`: whether the ticket may steal from the global reserve.
- `list`: links into `space_info->tickets` or `space_info->priority_tickets`.
- `wait`: wait queue for normal ticket waiters.
- `lock`: protects ticket state during wakeups and interruption.

`struct btrfs_space_info` is defined in `space-info.h`; this file initializes and mutates its counters, ticket lists, block-group lists, reclaim flags, and sysfs-visible reclaim counters.

## Space Info Creation And Initialization

`calc_chunk_size()` chooses default chunk size:

- Zoned filesystems use `fs_info->zone_size`.
- Data uses `BTRFS_MAX_DATA_CHUNK_SIZE`.
- System and metadata-remap use `32 MiB`.
- Metadata uses `1 GiB` on filesystems larger than `50 GiB`, otherwise `256 MiB`.

`init_space_info()` initializes block-group lists, locks, ticket lists, reclaim defaults, chunk size, flags, and zoned default reclaim threshold.

`create_space_info()` allocates a primary `btrfs_space_info`, optionally adds a zoned sub-group, registers sysfs entries, links it into `fs_info->space_info`, and stores `fs_info->data_sinfo` for data space.

`create_space_info_sub_group()` creates a child space info for zoned data relocation or treelog accounting. The implementation currently allows one sub-group slot per primary space info.

`btrfs_init_space_info()` creates:

- System space.
- Either mixed data+metadata space or separate metadata and data spaces.
- Metadata-remap space when `BTRFS_FEATURE_INCOMPAT_REMAP_TREE` is enabled.

`btrfs_add_bg_to_space_info()` folds a block group into its space info counters, including total/disk totals, used bytes, readonly super bytes, zone unusable bytes, and block-group list membership by RAID index. It also tries to grant waiting tickets after new capacity is visible.

`btrfs_find_space_info()` searches by masked block-group type flags and returns the first matching space info.

## Reservation Admission

`reserve_bytes()` is the central reservation routine used by both metadata and data wrappers.

The normal fast path checks:

- Current `btrfs_space_info_used(..., true)`.
- Whether pending tickets should block bypass.
- Whether `used + orig_bytes <= total_bytes`.
- For metadata, whether `can_overcommit()` allows the reservation based on unallocated chunk space.

If successful, it increments `bytes_may_use`.

The emergency path, `BTRFS_RESERVE_FLUSH_EMERGENCY`, ignores current `bytes_may_use` and admits only if actual used space plus the request fits in total bytes. This is intentionally dangerous but allowed for internal reservation pessimism failures.

When reservation fails and ticketing is allowed, `reserve_bytes()` creates a stack ticket, increments `space_info->reclaim_size`, and links the ticket into either:

- `space_info->tickets` for normal async reclaim modes.
- `space_info->priority_tickets` for inline priority reclaim modes.

Normal tickets queue either `async_reclaim_work` or `async_data_reclaim_work`. Metadata fast-path successes may also trigger `preempt_reclaim_work` when reservation pressure is high.

`btrfs_reserve_metadata_bytes()` wraps `reserve_bytes()` and emits ENOSPC trace/debug dumps on failure.

`btrfs_reserve_data_bytes()` restricts callers to data-safe flush modes, wraps `reserve_bytes()`, and emits ENOSPC diagnostics.

## Ticket Granting And Failure

`btrfs_try_granting_tickets()` runs under `space_info->lock`. It grants priority tickets first, then normal tickets. A ticket is granted if the requested bytes fit in currently allocated space or, for metadata, can be overcommitted. Granting increments `bytes_may_use`, removes and wakes the ticket, and advances `tickets_id`.

`remove_ticket()` unlinks a ticket, subtracts its remaining bytes from `reclaim_size`, sets error or success, and wakes waiters.

`wait_reserve_ticket()` waits killably for normal tickets. On fatal signal it removes the ticket while holding `space_info->lock` to avoid leaking a later granted `bytes_may_use` reservation.

`handle_reserve_ticket()` dispatches by flush mode:

- Normal metadata/data flushing waits for async reclaim.
- `BTRFS_RESERVE_FLUSH_LIMIT` and `BTRFS_RESERVE_FLUSH_EVICT` run priority metadata reclaim.
- `BTRFS_RESERVE_FLUSH_FREE_SPACE_INODE` runs priority data reclaim.
- It asserts that successful tickets do not also carry errors.

`maybe_fail_all_tickets()` is used after reclaim exhaustion. It repeatedly fails or grants tickets until progress stops, optionally stealing from the global reserve for eligible tickets, and handles transaction-abort error propagation.

`steal_from_global_rsv()` lets selected tickets consume global block reserve bytes if at least 10% of the global reserve remains beyond the requested bytes.

## Overcommit And Available Space Calculation

`calc_effective_data_chunk_size()` estimates a data chunk size for overcommit and reclaim heuristics, using the data space-info chunk size directly on zoned filesystems and otherwise capping to 10% of device writable bytes and `1 GiB`.

`calc_available_free_space()` estimates how much unallocated physical capacity can support metadata overcommit. It:

- Uses per-profile availability if present, otherwise `free_chunk_space`.
- Divides for mirrored/duplicated profiles.
- Reserves one effective data chunk to avoid data allocations consuming all metadata headroom.
- Allows larger overcommit when not using full flush modes.
- Aligns down to zone size on zoned filesystems.

`can_overcommit()` rejects data/mixed data space and delegates to `check_can_overcommit()` for metadata-like spaces.

`btrfs_can_overcommit()` is the exported lock-held check using current `space_info` usage.

## Reclaim State Machine

`flush_space()` maps `enum btrfs_flush_state` to concrete reclaim actions:

- Run delayed items.
- Flush delalloc, with optional ordered-extent waits.
- Run delayed refs.
- Allocate chunks, optionally forced.
- Run zoned reclaim and unused block-group deletion.
- Run delayed iputs.
- Commit current transaction.
- Reset unused zones.

It traces every flush attempt with result and preemptive/normal context.

`shrink_delalloc()` starts delalloc writeback across roots, waits for async compressed delalloc workers to establish ordered extents, optionally waits for ordered extents, and loops up to three times unless doing preemptive one-shot reclaim.

`do_async_reclaim_metadata_space()` is the normal metadata ticket flusher. It progresses through flush states from delayed items through transaction commit or zone reset. It resets to the first state when tickets are granted, skips full delalloc and forced chunk allocation on early cycles, and fails tickets after repeated no-progress commit cycles.

`btrfs_async_reclaim_metadata_space()` runs metadata reclaim for the primary metadata space and any zoned metadata sub-group.

`do_async_reclaim_data_space()` first tries forced chunk allocation until the data space is marked full, then cycles through data states: full delalloc, delayed iputs, transaction commit, zoned reclaim, zone reset, and forced chunk allocation. It fails tickets only when full and no state makes progress.

`btrfs_async_reclaim_data_space()` runs data reclaim for `fs_info->data_sinfo` and its sub-group.

`btrfs_init_async_reclaim_work()` wires the metadata, data, and preemptive reclaim work items.

## Preemptive Metadata Reclaim

`need_preemptive_reclaim()` decides whether background metadata reclaim should run before tasks block on tickets. It avoids reclaim when tickets already exist, the filesystem is effectively full, the pressure is only global reserve, pressure is too small, the filesystem is closing, or remounting is active.

It compares reclaimable pressure against a clamp-scaled threshold based on available metadata headroom. The `clamp` field can tighten thresholds from `1/2` down to `1/256`.

`btrfs_preempt_reclaim_metadata_space()` chooses the dominant reclaim source:

- Delalloc reservations.
- Pinned bytes, via transaction commit.
- Delayed inode block reserve.
- Delayed refs block reserve.

It reclaims one quarter of the selected amount per loop and relaxes `clamp` if one loop was enough.

`maybe_clamp_preempt()` tightens `clamp` when delalloc is growing faster than ordered extents and normal ticketing had to be used.

## Periodic And Dynamic Block-Group Reclaim

`calc_unalloc_target()` sets a target of ten effective data chunks of unallocated space.

`calc_dynamic_reclaim_threshold()` computes a reclaim threshold based on how far unallocated space is below the target, while backing off if there is not enough unused allocated data space to make relocation useful.

`btrfs_calc_reclaim_threshold()` returns either the dynamic threshold or the fixed `bg_reclaim_threshold`.

`is_reclaim_urgent()` treats unallocated space below one effective data chunk as urgent.

`do_reclaim_sweep()` scans block groups for a RAID index, uses the threshold to select underused groups, increments `reclaim_mark`, and calls `btrfs_mark_bg_to_reclaim()` for candidates. Urgent mode can make a second pass to take fresher groups if no stale groups qualified.

`btrfs_space_info_update_reclaimable()` tracks net reclaimable byte changes and marks periodic reclaim ready once at least one data chunk worth of space has become reclaimable.

`btrfs_set_periodic_reclaim_ready()` toggles periodic reclaim readiness and resets accumulated reclaimable bytes when clearing.

`btrfs_reclaim_sweep()` runs periodic reclaim across eligible non-system space infos and all RAID indexes.

## Diagnostics And Stat Helpers

`btrfs_dump_space_info()` logs current counters, global block reserves, block-group counters, free-space details, and aggregate availability.

`btrfs_dump_space_info_for_trans_abort()` logs all space infos and global reserves after ENOSPC-related transaction aborts.

`btrfs_account_ro_block_groups_free_space()` computes unused bytes inside readonly block groups, scaled by RAID factor, for `statfs` accounting.

`btrfs_return_free_space()` preferentially refills the global reserve from returned free space, then tries to grant tickets.

## Concurrency And Locking

`space_info->lock` protects counters, ticket lists, reclaim size, `flush`, `full`, and periodic reclaim fields. Many helpers assert the lock is held.

`groups_sem` protects block-group list traversal and modification.

Ticket state has its own spinlock because waiters and reclaimers race on ticket completion.

Workqueues run async reclaim outside reservation callers, while priority reclaim can run inline for contexts that cannot wait on normal async tickets.

Transaction state is handled carefully: several flush paths use `btrfs_join_transaction_nostart()`, while commit paths assert `current->journal_info == NULL` to avoid deadlock.

## Integration Points

This file depends heavily on:

- `block-group.c` for block-group availability, reclaim marking, chunk allocation, unused group deletion, and zone resets.
- `transaction.c` for delayed refs and commits.
- `ordered-data.c` and delalloc paths for flushing dirty file data.
- `zoned.c` for zone reset/reclaim behavior.
- `sysfs.c` for space-info sysfs registration.
- `super.c` indirectly through mount options such as `ENOSPC_DEBUG` and zoned/free-space settings.

## Risks And Edge Cases

Reservation correctness depends on every counter transition preserving invariants among `bytes_may_use`, `bytes_reserved`, `bytes_used`, `bytes_pinned`, readonly bytes, and zone-unusable bytes.

Ticket interruption is delicate: if a killed task is not removed before reclaim grants it, `bytes_may_use` can leak. `wait_reserve_ticket()` explicitly guards this.

Priority tickets can bypass normal tickets, but only relative to the priority list. Normal no-flush reservations intentionally do not jump existing normal tickets.

Overcommit is intentionally metadata-only; mixed data+metadata profiles are treated as data and cannot overcommit.

Zoned filesystems replace some normal final reclaim states with zone reset/reclaim behavior and require zone-size alignment in available-space calculations.

## Testing Signals

Useful tests should cover:

- Immediate metadata and data reservation success.
- Metadata overcommit with and without unallocated chunk space.
- Ticket queuing, grant ordering, interruption, and ENOSPC failure.
- Priority reclaim modes and global-reserve stealing.
- Async metadata reclaim progress through delayed items, delayed refs, delalloc, chunk allocation, and commit.
- Async data reclaim when data space is full.
- Preemptive reclaim clamp changes under buffered write pressure.
- Zoned reclaim and reset states.
- Periodic reclaim threshold and urgent reclaim behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/space-info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/space-info.h -->
# File Research: sources/os/linux/linux/fs/btrfs/space-info.h

## Scope And Role

`space-info.h` declares the public Btrfs space-info data model and reservation/reclaim API. It is the shared contract for logical space accounting, reservation flushing levels, reclaim state ordering, block-group membership, ticket lists, sysfs-visible reclaim counters, and helper updates for major counters.

The implementation is primarily in `space-info.c`, while many other Btrfs subsystems use this header to reserve, release, inspect, and reclaim filesystem space.

## Reservation Flush Modes

`enum btrfs_reserve_flush_enum` describes how much reclaim a caller may perform when a reservation cannot be admitted immediately.

Important modes:

- `BTRFS_RESERVE_NO_FLUSH`: fail quickly; used when flushing could deadlock or blocking is not allowed.
- `BTRFS_RESERVE_FLUSH_LIMIT`: run limited metadata reclaim, mainly delayed inode items and chunk allocation.
- `BTRFS_RESERVE_FLUSH_EVICT`: broader reclaim for eviction contexts.
- `BTRFS_RESERVE_FLUSH_DATA`: data reservation flushing, interruptible by fatal signals.
- `BTRFS_RESERVE_FLUSH_FREE_SPACE_INODE`: special data-space reclaim path for free-space inode work.
- `BTRFS_RESERVE_FLUSH_ALL`: full normal metadata reclaim.
- `BTRFS_RESERVE_FLUSH_ALL_STEAL`: full reclaim plus possible global reserve stealing.
- `BTRFS_RESERVE_FLUSH_EMERGENCY`: bypasses normal `bytes_may_use` pressure and admits if actual used space fits.

The comments document deadlock-sensitive contexts, especially transaction-handle holders.

## Reclaim States

`enum btrfs_flush_state` gives the ordered state machine used by metadata reclaim:

- Delayed inode item flushing.
- Delayed reference flushing.
- Delalloc flushing and ordered-extent waiting.
- Chunk allocation, including forced allocation.
- Delayed iputs.
- Transaction commit.
- Zoned reset and reclaim states.

The enum order is intentionally meaningful for `btrfs_async_reclaim_metadata_space()`.

## Space-Info Sub-Groups

`enum btrfs_space_info_sub_group` names:

- `BTRFS_SUB_GROUP_PRIMARY`
- `BTRFS_SUB_GROUP_DATA_RELOC`
- `BTRFS_SUB_GROUP_TREELOG`

`BTRFS_SPACE_INFO_SUB_GROUP_MAX` is `1`, so each primary space info currently has one sub-group slot. The implementation uses that slot for zoned data relocation under data space or treelog under metadata space.

## Main Type: `struct btrfs_space_info`

`struct btrfs_space_info` represents one logical allocation class.

Core identity and hierarchy:

- `fs_info`: owning filesystem.
- `parent`: parent primary space info for sub-groups.
- `sub_group[]`: child space-info slots.
- `subgroup_id`: primary, data relocation, or treelog.
- `flags`: block-group type flags.

Counters:

- `total_bytes`: logical bytes in this space class.
- `bytes_used`: bytes committed to extents.
- `bytes_pinned`: bytes freed but unavailable until transaction completion.
- `bytes_reserved`: bytes reserved by allocator for current allocations.
- `bytes_may_use`: optimistic reservations for delalloc and metadata work.
- `bytes_readonly`: bytes unavailable because block groups are readonly.
- `bytes_zone_unusable`: zoned-mode unusable bytes until zone reset.
- `disk_used` and `disk_total`: physical-disk accounting with mirrors/parity factors.

Allocation and reclaim state:

- `max_extent_size`: allocator ENOSPC hint.
- `chunk_size`: default chunk allocation size.
- `bg_reclaim_threshold`: fixed block-group reclaim threshold.
- `clamp`: preemptive reclaim threshold divisor shift.
- `full`: no more chunks can be allocated for this space.
- `chunk_alloc`: chunk allocation in progress.
- `flush`: async reclaim in progress.
- `force_alloc`: forced chunk allocation state.

Lists and synchronization:

- `lock`: protects counters, flags, reclaim state, tickets, and readonly block-group list.
- `groups_sem`: protects block-group lists by RAID type.
- `list`: links into `fs_info->space_info`.
- `ro_bgs`: readonly block groups.
- `priority_tickets` and `tickets`: reservation wait queues.
- `block_groups[BTRFS_NR_RAID_TYPES]`: block groups partitioned by RAID profile.

Ticket/reclaim metadata:

- `reclaim_size`: bytes needed for pending tickets.
- `tickets_id`: monotonic progress counter.
- `reclaim_count`, `reclaim_bytes`, `reclaim_errors`: sysfs-visible reclaim metrics.
- `dynamic_reclaim`, `periodic_reclaim`, `periodic_reclaim_ready`, `reclaimable_bytes`: background reclaim policy state.

Sysfs state:

- `kobj`
- `block_group_kobjs[]`

## Inline Helpers

`btrfs_mixed_space_info()` detects mixed data+metadata space infos.

`DECLARE_SPACE_INFO_UPDATE()` generates lock-held update helpers with tracing and underflow checks for:

- `bytes_may_use`
- `bytes_pinned`
- `bytes_zone_unusable`

`btrfs_space_info_used()` sums used, reserved, pinned, readonly, zone-unusable, and optionally may-use bytes. Callers must hold `space_info->lock`.

`btrfs_space_info_free_bytes_may_use()` subtracts may-use bytes and tries to grant tickets under the space-info lock.

`btrfs_space_info_type_str()` converts exact type combinations to `"SYSTEM"`, `"DATA+METADATA"`, `"DATA"`, `"METADATA"`, or `"UNKNOWN"`.

## Public API

Initialization and lookup:

- `btrfs_init_space_info()`
- `btrfs_add_bg_to_space_info()`
- `btrfs_update_space_info_chunk_size()`
- `btrfs_find_space_info()`
- `btrfs_clear_space_info_full()`

Diagnostics:

- `btrfs_dump_space_info()`
- `btrfs_dump_space_info_for_trans_abort()`

Reservation:

- `btrfs_reserve_metadata_bytes()`
- `btrfs_reserve_data_bytes()`
- `btrfs_try_granting_tickets()`
- `btrfs_can_overcommit()`

Reclaim:

- `btrfs_init_async_reclaim_work()`
- `btrfs_account_ro_block_groups_free_space()`
- `btrfs_space_info_update_reclaimable()`
- `btrfs_set_periodic_reclaim_ready()`
- `btrfs_calc_reclaim_threshold()`
- `btrfs_reclaim_sweep()`
- `btrfs_return_free_space()`

## Concurrency Notes

Most counter helpers require `space_info->lock`. The generated update helpers assert lock ownership and trace both logical counter updates and space reservation events.

Block-group list traversal requires `groups_sem`, while readonly block-group list accounting uses `space_info->lock` plus individual block-group locks.

Ticket list manipulation is lock-protected and coordinated with per-ticket locks in `space-info.c`.

## Integration Points

This header includes `trace/events/btrfs.h`, `linux/kobject.h`, wait queues, rwsems, spinlocks, and `volumes.h`. Its struct fields are used across reservation code, block-group management, sysfs allocation reporting, statfs, chunk allocation, and zoned reclaim.

## Risks And Edge Cases

The counter-update macro clamps underflow to zero after warning; callers should still treat underflow as a bug.

`btrfs_space_info_type_str()` switches on exact `flags`, so remap-tree or sub-group flags not matching listed combinations report `"UNKNOWN"`.

`BTRFS_SPACE_INFO_SUB_GROUP_MAX` being `1` means future additional sub-groups require ABI/code updates, not just enum additions.

## Testing Signals

Tests should validate:

- Underflow detection in generated update helpers.
- Correct `btrfs_space_info_used()` sums with and without `bytes_may_use`.
- Mixed profile detection.
- Type-string reporting for system, data, metadata, and mixed space.
- Ticket granting after may-use release.
- Reclaim threshold toggles through dynamic and periodic reclaim fields.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/space-info.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/subpage.c -->
# File Research: sources/os/linux/linux/fs/btrfs/subpage.c

## Scope And Role

`subpage.c` implements Btrfs support for filesystems whose sector size is smaller than the memory folio size. In that mode a single folio can contain multiple filesystem sectors or multiple metadata tree blocks, so normal folio flags are too coarse.

The file attaches a `struct btrfs_folio_state` to folios and maintains per-sector bitmaps for:

- Uptodate.
- Dirty.
- Writeback.
- Ordered.
- Checked.
- Locked.

The helpers provide both strict subpage operations and wrapper operations that fall back to normal folio flags on non-subpage filesystems.

## Design Overview

The opening comment describes subpage constraints and behavior:

- Historically focused on 64 KiB page size.
- Metadata read supports subpage granularity.
- Metadata writeback can still operate at folio scope but submits dirty extent buffers inside the folio.
- Metadata cannot rely solely on folio locking because multiple tree blocks may share one folio; it relies on io-tree locking for concurrency.
- Both data and metadata use `btrfs_folio_state` to track per-sector state.

## Folio State Allocation And Lifetime

`btrfs_attach_folio_state()` attaches private subpage state when needed. It skips attachment if:

- The folio already has private data.
- Metadata is not subpage.
- Data does not have sector size smaller than folio size.

For metadata it asserts the folio is not large. For mapped folios it asserts the folio is locked.

`btrfs_detach_folio_state()` detaches and frees the state if the folio is private and the requested folio type is actually subpage.

`btrfs_alloc_folio_state()` allocates enough bitmap storage for `btrfs_bitmap_nr_max * blocks_per_folio`, initializes the spinlock, and initializes either:

- `eb_refs` for metadata.
- `nr_locked` for data.

`btrfs_free_folio_state()` is an inline free in the header.

## Metadata Extent-Buffer References

`btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` protect metadata folio state lifetime during extent-buffer allocation/free races.

They operate only when metadata is subpage and require `folio->mapping->i_private_lock`. The counter prevents detaching folio private state while an extent buffer sharing the folio is still being created or torn down.

## Range Validation And Bitmap Layout

`btrfs_subpage_assert()` verifies:

- Folio private state exists.
- `start` and `len` are sector-aligned.
- For mapped folios, the range lies inside the folio.

`subpage_calc_start_bit()` computes the starting bit for a named bitmap by combining:

- Sector offset inside the folio.
- Bitmap number multiplied by blocks per folio.

`btrfs_subpage_clamp_range()` truncates an arbitrary range to the portion inside a folio. If the folio is outside the range, it sets length to zero so callers can safely no-op.

`subpage_test_bitmap_all_set()` and `subpage_test_bitmap_all_zero()` test full-bitmap state for deciding when the coarse folio flag can be set or cleared.

## Subpage Lock Tracking

`btrfs_folio_set_lock()` records subpage-locked sectors inside a folio that was already locked by regular folio locking. It asserts the target bits were clear, sets locked bits, and increments `nr_locked`.

`btrfs_folio_end_lock()` releases subpage locks for a range and unlocks the folio only when the last subpage lock is cleared. It falls back to `folio_unlock()` for non-subpage folios or plain-locked subpage folios with `nr_locked == 0`.

`btrfs_folio_end_lock_bitmap()` clears locked sectors from a caller-provided bitmap and unlocks when the last tracked subpage lock is gone.

`btrfs_subpage_end_and_test_lock()` is the internal locked-bitmap clearing helper. It handles special compression/writeback paths where the folio was locked without subpage locked bits.

## Per-State Operations

Manual implementations handle flags whose coarse folio semantics need special care.

`btrfs_subpage_set_uptodate()` sets range bits and marks the whole folio uptodate only when all sectors are uptodate.

`btrfs_subpage_clear_uptodate()` clears range bits and clears the folio uptodate flag unconditionally.

`btrfs_subpage_set_dirty()` sets dirty bits and marks the folio dirty.

`btrfs_subpage_clear_and_test_dirty()` clears dirty bits and returns true if no dirty bits remain. Callers must clear the folio dirty flag themselves when appropriate.

`btrfs_subpage_clear_dirty()` clears dirty bits and clears the folio dirty-for-IO flag when the last dirty bit is gone.

`btrfs_subpage_set_writeback()` sets writeback bits and starts folio writeback if needed. It preserves the TOWRITE tag when the folio remains dirty so `WB_SYNC_ALL` does not miss still-dirty folios.

`btrfs_subpage_clear_writeback()` clears writeback bits and ends folio writeback when all writeback bits are gone.

`btrfs_subpage_set_ordered()` and `btrfs_subpage_clear_ordered()` maintain ordered bits and the coarse ordered folio flag.

`btrfs_subpage_set_checked()` marks the folio checked only when all checked bits are set.

`btrfs_subpage_clear_checked()` clears checked bits and clears the coarse checked flag.

`IMPLEMENT_BTRFS_SUBPAGE_TEST_OP()` generates range test helpers for uptodate, dirty, writeback, ordered, and checked.

## Folio Wrapper Operations

`IMPLEMENT_BTRFS_PAGE_OPS()` generates a full family of helpers for each state:

- `btrfs_folio_set_*`
- `btrfs_folio_clear_*`
- `btrfs_folio_test_*`
- `btrfs_folio_clamp_set_*`
- `btrfs_folio_clamp_clear_*`
- `btrfs_folio_clamp_test_*`
- `btrfs_meta_folio_set_*`
- `btrfs_meta_folio_clear_*`
- `btrfs_meta_folio_test_*`

These wrappers use normal folio operations when there is no `fs_info` or when the folio is not subpage, which also supports existing selftests that pass minimal filesystem state.

For metadata helpers, the range is derived from the `extent_buffer` start and length.

## Dirty Assertions And Metadata Dirty Clearing

`btrfs_folio_assert_not_dirty()` is active under `CONFIG_BTRFS_ASSERT`. It checks both the coarse folio dirty flag and the subpage dirty bits, dumping dirty bitmaps when an unexpected dirty range is found.

`btrfs_meta_folio_clear_and_test_dirty()` clears metadata dirty bits for an extent buffer and clears the folio dirty-for-IO flag when the last dirty subpage range is gone. Non-subpage metadata clears the folio directly and returns true.

## Bitmap Debugging And Export

`GET_SUBPAGE_BITMAP()` reads one named bitmap into an `unsigned long`.

`SUBPAGE_DUMP_BITMAP()` logs one named bitmap.

`btrfs_subpage_dump_bitmap()` dumps all subpage bitmaps plus the underlying page for debugging.

`btrfs_get_subpage_dirty_bitmap()` exports the dirty bitmap for callers that need to inspect dirty sectors.

## Concurrency And Locking

`btrfs_folio_state->lock` protects bitmap mutation and reads. Many operations use `spin_lock_irqsave()` because they may interact with writeback or completion contexts.

`nr_locked` is atomic but still updated under the bitmap lock when tied to bitmap changes.

Metadata `eb_refs` is atomic and additionally protected by `i_private_lock` at call sites to coordinate folio-private lifetime.

Folio coarse flags are updated only when subpage bitmap state reaches all-set or all-zero thresholds.

## Integration Points

This file is used by extent I/O, metadata extent-buffer handling, delalloc/writeback paths, compression paths, and COW fixup/ordered extent state management. The public declarations live in `subpage.h`.

It depends on folio APIs, bitmap APIs, Btrfs inode helpers, extent-buffer metadata, and filesystem sector-size fields.

## Risks And Edge Cases

Zero-length clamped ranges are intentionally accepted by subpage helpers.

Subpage state must be attached before bitmap helpers run; assertions catch missing private state.

Misbalanced subpage lock setting/ending can leave a folio locked or unlock it too early. The code asserts `nr_locked` bounds against cleared bits.

Dirty/writeback interactions are subtle because folio-level dirty and writeback flags aggregate multiple sector bits.

The generated wrapper functions rely on correct `btrfs_is_subpage()` and `btrfs_meta_is_subpage()` decisions.

## Testing Signals

Useful tests should cover:

- Sector-sized dirty/uptodate/writeback/ordered/checked transitions inside one folio.
- Coarse folio flag transitions when all bits become set or clear.
- Subpage lock reference counting with overlapping ranges and bitmap unlock.
- Metadata folios with multiple extent buffers.
- Dirty assertion failure diagnostics.
- Clamp helpers for ranges partially or wholly outside a folio.
- Non-subpage fallback behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/subpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/subpage.h -->
# File Research: sources/os/linux/linux/fs/btrfs/subpage.h

## Scope And Role

`subpage.h` declares the Btrfs subpage folio-state data model and helper API. It supports filesystems whose sector size or metadata node size is smaller than `PAGE_SIZE`, allowing per-sector state tracking within a single folio.

The implementation is in `subpage.c`; callers across extent I/O, metadata, delalloc, and writeback use this header to attach state and manipulate range-level flags.

## Bitmap Layout

The anonymous enum defines bitmap indexes used to build function names and offset into `btrfs_folio_state->bitmaps`:

- `btrfs_bitmap_nr_uptodate`
- `btrfs_bitmap_nr_dirty`
- `btrfs_bitmap_nr_writeback`
- `btrfs_bitmap_nr_ordered`
- `btrfs_bitmap_nr_checked`
- `btrfs_bitmap_nr_locked`
- `btrfs_bitmap_nr_max`

The comments note that ordered and checked are deprecated COW-fixup flags, while locked is currently needed for async delalloc/compression range handling.

All state bitmaps are packed into one flexible array, grouped by bitmap type and indexed by sector within the folio.

## Main Type: `struct btrfs_folio_state`

`struct btrfs_folio_state` is attached to `folio->private` for subpage data and metadata folios.

It contains:

- `lock`: protects bitmap access.
- A union:
  - `eb_refs`: metadata extent-buffer reference count, managed under mapping private lock.
  - `nr_locked`: data subpage locked-sector count.
- `bitmaps[]`: flexible bitmap storage for all per-sector state classes.

`enum btrfs_folio_type` distinguishes metadata and data allocation/attachment behavior.

## Subpage Detection

`btrfs_meta_is_subpage()` returns true when `fs_info->nodesize < PAGE_SIZE`. Metadata subpage handling depends on node size rather than folio size because metadata folios are not allocated larger than node size.

`btrfs_is_subpage()` returns true when `fs_info->sectorsize < folio_size(folio)`. For mapped data folios, it asserts the host inode is a Btrfs data inode.

## Lifecycle API

- `btrfs_attach_folio_state()`
- `btrfs_detach_folio_state()`
- `btrfs_alloc_folio_state()`
- `btrfs_free_folio_state()`

These allocate, attach, detach, and free the per-folio bitmap state.

Metadata extent-buffer reference helpers:

- `btrfs_folio_inc_eb_refs()`
- `btrfs_folio_dec_eb_refs()`

Lock tracking helpers:

- `btrfs_folio_end_lock()`
- `btrfs_folio_set_lock()`
- `btrfs_folio_end_lock_bitmap()`

## Generated Operation API

`DECLARE_BTRFS_SUBPAGE_OPS(name)` declares, for each state name:

- Strict subpage range operations:
  - `btrfs_subpage_set_name()`
  - `btrfs_subpage_clear_name()`
  - `btrfs_subpage_test_name()`
- Data folio wrapper operations:
  - `btrfs_folio_set_name()`
  - `btrfs_folio_clear_name()`
  - `btrfs_folio_test_name()`
- Clamped data folio wrapper operations:
  - `btrfs_folio_clamp_set_name()`
  - `btrfs_folio_clamp_clear_name()`
  - `btrfs_folio_clamp_test_name()`
- Metadata extent-buffer operations:
  - `btrfs_meta_folio_set_name()`
  - `btrfs_meta_folio_clear_name()`
  - `btrfs_meta_folio_test_name()`

The macro is instantiated for:

- `uptodate`
- `dirty`
- `writeback`
- `ordered`
- `checked`

The comments define expected usage:

- `btrfs_subpage_*()` assumes a subpage folio and a range inside one folio.
- `btrfs_folio_*()` handles both subpage and regular folios, but range must be inside one folio.
- `btrfs_folio_clamp_*()` truncates ranges to folio boundaries.
- Metadata should use `btrfs_meta_folio_*()` helpers, not clamped data helpers.

## Additional Helpers

`btrfs_folio_clamp_finish_io()` is an inline cleanup helper that clears dirty, sets writeback, and clears writeback for an error/finish path over a clamped range.

Dirty and diagnostics API:

- `btrfs_subpage_clear_and_test_dirty()`
- `btrfs_folio_assert_not_dirty()`
- `btrfs_meta_folio_clear_and_test_dirty()`
- `btrfs_get_subpage_dirty_bitmap()`
- `btrfs_subpage_dump_bitmap()`

## Concurrency Notes

The header documents that metadata `eb_refs` is tied to `private_lock` and protects whether `btrfs_folio_state` can be detached.

Data `nr_locked` tracks how many sectors in a folio are subpage-locked.

The bitmap layout is sized at allocation time based on `fsize >> fs_info->sectorsize_bits`.

## Integration Points

This header includes `btrfs_inode.h` for inode assertions and depends on `struct extent_buffer` declarations available through included Btrfs headers.

It is a shared contract for metadata pages, data folios, extent I/O, COW fixup state, ordered extent state, and writeback state.

## Risks And Edge Cases

The helper families are easy to misuse if a caller passes a range crossing multiple folios to non-clamp functions.

Metadata and data use the same state structure but different union fields. Passing the wrong `enum btrfs_folio_type` can corrupt logical interpretation.

The ordered and checked bits are marked deprecated but remain part of the ABI within this source file.

The locked bitmap exists for async delalloc/compression behavior and cannot be removed until that lifecycle is reworked.

## Testing Signals

Tests should validate:

- Allocation size for multiple sector counts per folio.
- Metadata vs data union initialization.
- Subpage detection for nodesize and sectorsize combinations.
- Generated helper behavior for all declared state classes.
- Clamp finish-IO behavior on partial folio ranges.
- Dirty bitmap export and debug dump paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/subpage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/super.c -->
# File Research: sources/os/linux/linux/fs/btrfs/super.c

## Scope And Role

`super.c` implements Btrfs integration with the Linux VFS superblock and filesystem-type APIs. It covers mount option parsing, fs_context lifecycle, initial mount, subvolume mounting, remount/reconfigure, sync, statfs, freeze/unfreeze, device control ioctls, superblock operations, shrinker hooks, block-device removal handling, module initialization, and module teardown.

It is the primary Btrfs entry point from the kernel VFS and module loader.

## Filesystem Context And Mount Options

`struct btrfs_fs_context` stores parsed mount state:

- `subvol_name`
- `subvol_objectid`
- `max_inline`
- `commit_interval`
- `metadata_ratio`
- `thread_pool_size`
- `mount_opt`
- `compress_type`
- `compress_level`
- `refs`

The option tables define accepted parameters for ACLs, compression, subvolumes, devices, discard, fatal error behavior, free-space cache, SSD options, rescue modes, ENOSPC debug, and debug-only fragmentation/reference verification options.

`btrfs_parse_param()` uses the new mount API parser and maps parsed options into `btrfs_fs_context`. It handles interactions such as:

- Compression clears `NODATACOW` and `NODATASUM`.
- `nodatacow` disables compression and data checksums.
- `ssd_spread` implies `ssd`.
- `discard=sync` and `discard=async` are mutually exclusive.
- `space_cache=v1` and `space_cache=v2` select old cache or free-space tree.
- Rescue options are grouped under `rescue=`.
- Deprecated `usebackuproot` and compatibility `norecovery` map to rescue-style flags.

`btrfs_parse_compress()` parses zlib/lzo/zstd compression and optional levels, including force-compress handling.

## Option Validation And Defaults

`btrfs_check_options()` rejects rescue options that require read-only mounts, prevents disabling free-space-tree when required by on-disk features, delegates zoned mount-option validation, and warns about deprecated space cache v1 on normal mounts.

`btrfs_set_free_space_cache_settings()` derives runtime free-space cache settings from on-disk state and mount options. It forces free-space tree when sector size differs from page size and clears old space cache on zoned filesystems.

`set_device_specific_options()` auto-enables SSD optimization on non-rotational devices and auto-enables async discard on discardable non-zoned devices unless discard was explicitly configured or disabled.

`btrfs_clear_oneshot_options()` removes mount-only flags such as backup-root use and cache-clearing after mount/remount processing.

`btrfs_emit_options()` logs newly enabled/disabled options and compression changes.

## Subvolume Resolution And Mounting

`btrfs_get_subvol_name_from_objectid()` reconstructs a subvolume path by walking root backrefs in the root tree and inode refs in parent filesystem trees until it reaches the top-level subvolume. It returns a `PATH_MAX`-bounded allocated path.

`get_default_subvol_objectid()` looks up the `"default"` dir item under `btrfs_super_root_dir()` and falls back to `BTRFS_FS_TREE_OBJECTID` if not found.

`mount_subvol()` resolves the requested or default subvolume, calls `mount_subtree()`, verifies that the resulting root inode is a subvolume inode, and checks that a requested objectid matches the mounted root.

`btrfs_get_tree_subvol()` creates a temporary `btrfs_fs_info`, duplicates the fs_context for mounting the whole filesystem, then creates a vfsmount and switches `fc->root` to the requested subvolume dentry.

A long comment explains the historical complexity of allowing different read-only/read-write states per Btrfs subvolume mount, especially the ambiguity between mount read-only and superblock read-only in the old mount API and compatibility expectations with modern mount tooling.

## Superblock Filling And Sync

`btrfs_fill_super()` initializes the VFS superblock:

- Sets max file size, magic, super operations, dentry ops, export ops, verity ops, xattrs, time granularity, and cgroup/writeback flags.
- Sets up backing device info.
- Calls `open_ctree()` to open the filesystem.
- Emits mount options.
- Loads the root inode and creates `sb->s_root`.
- Marks the superblock active.

`btrfs_put_super()` logs the last unmount and calls `close_ctree()`.

`btrfs_sync_fs()` handles `sync_fs`:

- Non-waiting sync flushes btree inode mapping.
- Waiting sync waits ordered roots, attaches to or starts a transaction when needed, handles frozen filesystems carefully, and commits the transaction.

## Remount And Reconfigure

`btrfs_info_to_ctx()` and `btrfs_ctx_to_info()` copy mount option state between `btrfs_fs_info` and `btrfs_fs_context`.

`btrfs_reconfigure()` handles remounts and mount reconfiguration. It:

- Saves old context.
- For mount reconfiguration, preserves existing mount options except ro/rw/subvolume changes.
- Syncs the filesystem.
- Marks `BTRFS_FS_STATE_REMOUNTING`.
- Validates options and feature compatibility.
- Applies new context.
- Handles autodefrag cleanup, thread-pool resizing, and free-space-tree transition restrictions.
- Switches read-write to read-only or read-only to read-write when requested.
- Updates ACL masks, emits option logs, wakes the transaction thread, runs cleanup, clears one-shot options, and clears remounting state.
- Restores old context on later failure.

`btrfs_remount_rw()` rejects remounting read-write after filesystem error, without writable devices, without enough devices for the RAID profile, or when tree-log replay would be required. It then runs pre-RW setup, clears read-only state, marks the filesystem open, and resumes discard.

`btrfs_remount_ro()` cancels reclaim workers, cleans discard, waits for UUID rescan, sets read-only state, deletes unused block groups, waits for cleaner state, runs delayed iputs, suspends device replace, cancels scrub, pauses balance, waits for qgroup rescan, and commits the superblock.

`btrfs_remount_begin()` and `btrfs_remount_cleanup()` handle autodefrag wait/cleanup, discard toggle handling, and old space-cache state toggles.

## Mounting The Superblock

`btrfs_get_tree_super()` scans the source device, locates/holds `fs_devices`, calls `sget_fc()`, and either reuses an existing superblock or opens devices and fills a new one.

For a new mount it:

- Opens devices with mode derived from requested read-only/read-write flags.
- Rejects read-write mount without writable devices.
- Applies device-specific options.
- Sets `sb->s_id`.
- Renames shrinker debugfs entry.
- Calls `btrfs_fill_super()`.

For an existing superblock it drops the temporary fs_devices hold and leaves read-only mismatches to later reconfiguration.

`btrfs_fc_test_super()` matches superblocks by `fs_devices`.

`btrfs_get_tree()` delegates to subvolume mounting.

`btrfs_kill_super()` kills the anonymous superblock and frees `fs_info`.

`btrfs_free_fs_context()` frees duplicated context state and any temporary `fs_info`.

`btrfs_dup_fs_context()` shares the Btrfs fs-private context by refcount and transfers the source string to the duplicate context.

`btrfs_init_fs_context()` initializes defaults, hooks `btrfs_fs_context_ops`, and sets default ACL and inode-version flags.

`btrfs_fs_type` registers the filesystem as `"btrfs"` with device requirement, binary mount data, idmapped mounts, and mtime-granularity support.

## `statfs` And Space Reporting

`btrfs_calc_avail_data_space()` simulates chunk allocation availability across open devices. It filters usable devices, accounts for RAID profile stripe requirements, sorts devices by available bytes, and accumulates allocatable data space.

`btrfs_statfs()` reports filesystem space. It:

- Aggregates data free space, metadata free space, and total disk-used bytes from all space infos.
- Accounts readonly block groups through `btrfs_account_ro_block_groups_free_space()`.
- Applies RAID factor scaling.
- Subtracts the global block reserve from free blocks.
- Adds simulated unallocated data chunk space.
- Sets `f_bavail` to zero if metadata space is exhausted and the global reserve cannot fit.
- Fills magic, block size, name length, and fsid values, including subvolume root id to disambiguate subvolume mounts.

## Freeze, Unfreeze, And Superblock Integrity

`btrfs_freeze()` marks the filesystem frozen and commits the current transaction.

`check_dev_super()` reads the primary superblock from a device while frozen and verifies checksum type, checksum, structural validity, and transaction generation against the committed transaction.

`btrfs_unfreeze()` checks every present device superblock for unexpected modification, reports filesystem error if any device changed, clears frozen state, and returns success so VFS can thaw even if the filesystem was forced read-only.

## Control Device And Device Events

`btrfs_control_open()` initializes control file private data.

`btrfs_control_ioctl()` implements `/dev/btrfs-control` ioctls, restricted to `CAP_SYS_ADMIN`:

- `BTRFS_IOC_SCAN_DEV`
- `BTRFS_IOC_FORGET_DEV`
- `BTRFS_IOC_DEVICES_READY`
- `BTRFS_IOC_GET_SUPPORTED_FEATURES`

It copies and validates user volume args, scans devices under `uuid_mutex`, forgets devices by path/devt, reports readiness, or returns supported feature data.

`btrfs_remove_bdev()` handles block-device disappearance. It finds the Btrfs device, marks it missing, updates writable/missing counters, checks whether the filesystem can remain read-write in degraded mode, and either returns `-EIO` or sets the degraded mount option.

`btrfs_shutdown()` forces filesystem shutdown.

## Super Operations And Shrinker Hooks

`btrfs_super_ops` provides VFS callbacks:

- inode drop/evict/allocation/destruction/free
- `put_super`
- `sync_fs`
- mount option and device-name display
- `statfs`
- freeze/unfreeze
- cached object counting/freeing
- stats display
- block device removal
- shutdown

`btrfs_show_options()` emits mount options for `/proc/mounts`, including subvolid and reconstructed subvolume path.

`btrfs_show_devname()` prints the latest device name under RCU.

`btrfs_nr_cached_objects()` reports evictable extent maps to the shrinker.

`btrfs_free_cached_objects()` asks extent-map code to free cached objects and returns zero because freeing is asynchronous.

`btrfs_show_stats()` currently emits zoned stats for zoned filesystems.

## Module Initialization And Exit

`btrfs_ctl_fops` and `btrfs_misc` register `/dev/btrfs-control`.

`btrfs_print_mod_info()` prints compile-time feature status such as experimental, debug, assert, zoned, and fsverity support.

`mod_init_seq[]` centralizes initialization and cleanup order for properties, sysfs, compression, caches, DIO, transactions, ctree, free space, extent state, extent buffers, biosets, extent maps, optional read policy, ordered data, delayed inode, auto defrag, delayed refs, prelim refs, control device, sanity tests, and filesystem registration.

`init_btrfs_fs()` runs the sequence and unwinds on failure.

`btrfs_exit_btrfs_fs()` unwinds successful init steps in reverse order.

`exit_btrfs_fs()` also cleans filesystem UUID state.

The module uses `late_initcall(init_btrfs_fs)` and `module_exit(exit_btrfs_fs)`.

## Concurrency And Locking

Mount-time device discovery and device state changes use `uuid_mutex` and device-list locks.

Subvolume mount compatibility paths coordinate with `s_umount`.

Remount paths set `BTRFS_FS_STATE_REMOUNTING` to inform other subsystems, including space reclaim.

Read-only transition cancels reclaim workers and coordinates with cleaner, scrub, balance, device replace, delayed iputs, UUID rescan, and qgroup rescan.

Freeze/unfreeze relies on the filesystem being frozen to safely inspect device superblocks without device-list locking.

RCU protects latest-device name display.

## Integration Points

`super.c` integrates almost every Btrfs subsystem:

- `disk-io` for `open_ctree()` and `close_ctree()`.
- Transaction, delayed refs, delayed inode, and ordered-data subsystems for sync/remount.
- Space-info and block-group code for statfs and reclaim worker shutdown.
- Device/volume scanning and degraded checks.
- Free-space cache/tree, discard, zoned mode, scrub, qgroup, balance, and dev-replace.
- Compression, verity, xattr, export, inode, and dentry operations.
- Sysfs, module init, miscdevice control, and tracepoints.

## Risks And Edge Cases

Mount option interactions are dense: compression, datacow, datasum, space cache, rescue mode, discard, and ACL behavior all have cross-effects.

Subvolume mounting must preserve old ABI behavior around read-only flags while using the new mount API.

`statfs` is necessarily approximate for mixed RAID profiles and metadata exhaustion thresholds.

Remount read-only has many asynchronous subsystems to quiesce; missing one can leave open transactions or post-RO writes.

Device disappearance handling must distinguish tolerable degraded operation from losing read-write viability.

Freeze/unfreeze protects against external modification after hibernation-like scenarios by validating device superblocks.

## Testing Signals

Useful tests should cover:

- Mount option parsing, negation, aliases, and invalid values.
- Compression type/level parsing.
- Rescue options requiring read-only mounts.
- Free-space cache v1/v2 compatibility and forced free-space tree for subpage sectors.
- Subvolume mounting by name, objectid, default subvolume, and mismatch cases.
- Remount ro/rw transitions, especially degraded and log-replay cases.
- `statfs` under metadata exhaustion, readonly block groups, and multiple RAID profiles.
- `/dev/btrfs-control` ioctls and permission checks.
- Freeze/unfreeze superblock modification detection.
- Device removal degraded/read-write viability handling.
- Module init unwind on intermediate failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/super.h -->
# File Research: sources/os/linux/linux/fs/btrfs/super.h

## Scope And Role

`super.h` is the small public header for Btrfs superblock-facing helpers and declarations. It exposes selected functions from `super.c` and inline helpers for converting and changing VFS superblock read-only state.

## Public Declarations

Declared functions:

- `btrfs_check_options()`: validates mount option combinations against filesystem state and requested superblock flags.
- `btrfs_sync_fs()`: VFS `sync_fs` implementation.
- `btrfs_get_subvol_name_from_objectid()`: reconstructs a subvolume path from a root objectid.
- `btrfs_set_free_space_cache_settings()`: derives free-space cache/free-space-tree settings during mount.

Forward declarations:

- `struct super_block`
- `struct btrfs_fs_info`

The header includes `linux/types.h`, `linux/fs.h`, and Btrfs `fs.h`.

## Inline Helpers

`btrfs_sb()` returns `sb->s_fs_info` as `struct btrfs_fs_info *`.

`btrfs_set_sb_rdonly()` sets VFS `SB_RDONLY` and Btrfs `BTRFS_FS_STATE_RO`.

`btrfs_clear_sb_rdonly()` clears both the VFS read-only flag and the Btrfs internal read-only state bit.

These helpers ensure VFS and Btrfs internal read-only state are updated together.

## Integration Points

This header is used by Btrfs files that need superblock conversion, read-only state changes, sync invocation, option validation, or free-space cache setup without depending on the full `super.c` implementation details.

## Concurrency And State Notes

The read-only helpers do not perform locking themselves. Callers must invoke them in contexts where superblock and filesystem state transitions are serialized, such as mount/remount paths.

`btrfs_sb()` assumes `s_fs_info` has been initialized to a valid `btrfs_fs_info`.

## Risks And Edge Cases

Any caller bypassing `btrfs_set_sb_rdonly()` or `btrfs_clear_sb_rdonly()` can desynchronize `SB_RDONLY` from `BTRFS_FS_STATE_RO`.

The declarations expose functions implemented in `super.c`, so signature drift would break cross-file build consistency.

## Testing Signals

Tests should cover:

- Read-only remount paths setting both VFS and Btrfs state.
- Read-write remount paths clearing both state bits.
- Callers of `btrfs_check_options()` rejecting invalid read-write rescue combinations.
- Subvolume name reconstruction through `btrfs_get_subvol_name_from_objectid()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/super.h -->