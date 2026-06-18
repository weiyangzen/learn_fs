# Group Research: group_257_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_space_info_c_sourc_9ddf0f41d408

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/btrfs-linux`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/space-info.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/space-info.c

This file implements Btrfs space-info initialization, logical/disk byte accounting, metadata/data reservation tickets, ENOSPC reclaim state machines, preemptive metadata flushing, zoned reclaim/reset integration, and periodic block group reclaim policy.

Core responsibilities:
- Create `struct btrfs_space_info` objects for SYSTEM, METADATA, DATA, mixed DATA+METADATA, and optional METADATA_REMAP spaces.
- Maintain aggregate counters when block groups are attached: logical total/used/reserved/may-use/pinned/readonly/zone-unusable and mirrored disk totals.
- Decide when metadata reservations may overcommit unallocated chunk space.
- Queue reservation tickets when immediate reservation is impossible, then grant or fail them as reclaim makes progress.
- Run normal async reclaim, priority reclaim, data reclaim, and preemptive metadata reclaim.
- Compute automatic block group reclaim thresholds and schedule reclaim sweeps.

Initialization and space lookup:
- `calc_chunk_size()` chooses default chunk size: zone size for zoned filesystems, 1G or 256M metadata chunks depending on filesystem size, 32M system/remap chunks, and max-sized data chunks.
- `init_space_info()` initializes locks, block-group lists, ticket lists, sysfs-visible defaults, chunk size, subgroup id, and zoned reclaim threshold.
- `create_space_info()` allocates the primary space info, creates zoned subgroups for data relocation or tree-log metadata where needed, adds sysfs nodes, links the object into `fs_info->space_info`, and records `fs_info->data_sinfo`.
- `btrfs_init_space_info()` creates the set of space infos according to superblock incompat features such as mixed block groups and remap tree.
- `btrfs_find_space_info()` matches requested block-group type flags against the mounted filesystem's space-info list.
- `btrfs_clear_space_info_full()` clears `full` after adding capacity.

Reservation ticket model:
- `struct reserve_ticket` carries requested bytes, error, global-reserve-steal permission, list node, waitqueue, and a private lock.
- `reserve_bytes()` is the central reservation path used by metadata and data reservations.
- Immediate success adds bytes to `bytes_may_use` when current used space plus request fits total bytes or, for metadata only, `can_overcommit()` allows it.
- `BTRFS_RESERVE_FLUSH_EMERGENCY` ignores `bytes_may_use` when necessary and fits only against real allocated space.
- Normal flushers append to `space_info->tickets` and queue async reclaim work; priority flushers append to `priority_tickets` and perform their own limited reclaim.
- `remove_ticket()` removes a ticket from its list, adjusts `reclaim_size`, sets success or error state, and wakes waiters.
- `btrfs_try_granting_tickets()` grants priority tickets before normal tickets and updates `tickets_id` whenever a ticket is satisfied.
- `wait_reserve_ticket()` handles fatal-signal interruption by removing the ticket under `space_info->lock` to avoid leaking reserved `bytes_may_use`.
- `handle_reserve_ticket()` selects wait, priority metadata reclaim, priority data reclaim, or evict-style reclaim according to `enum btrfs_reserve_flush_enum`.

Overcommit and free-space calculation:
- `calc_effective_data_chunk_size()` derives the conservative data chunk size used to protect metadata overcommit from immediate data consumption.
- `calc_available_free_space()` estimates unallocated space available to metadata/system chunks, honoring per-profile availability when available, mirroring factors, data chunk reservation headroom, flush aggressiveness, and zone-size alignment on zoned filesystems.
- `check_can_overcommit()` tests whether allocated used bytes plus requested bytes fit allocated bytes plus computed unallocated allowance.
- `can_overcommit()` and `btrfs_can_overcommit()` reject overcommit for DATA or mixed DATA+METADATA space and only apply the logic to metadata/system-style reservations.

Flush state machine:
- `flush_space()` dispatches individual `enum btrfs_flush_state` actions:
  - delayed inode items with bounded or full count,
  - delalloc flushing and ordered-extent waiting,
  - delayed refs with bounded or full count,
  - normal or forced chunk allocation,
  - zoned block group reclaim or unused-zone reset,
  - delayed iputs,
  - current transaction commit.
- `shrink_delalloc()` starts delalloc writeback, waits for async delalloc submission to catch up, optionally waits for ordered extents, and loops while tickets still need space.
- `btrfs_calc_reclaim_metadata_size()` uses `reclaim_size`, current used bytes, and available overcommit room to decide how much metadata pressure to apply.
- `do_async_reclaim_metadata_space()` walks the metadata flush sequence, skips full delalloc and forced chunk allocation on the first cycle to avoid over-flushing/underutilized chunks, commits or resets zones at the end, and fails tickets after repeated nonprogress.
- `do_async_reclaim_data_space()` first tries forced data chunk allocation until the space info is full, then cycles through data-specific states: full delalloc, delayed iputs, transaction commit, zoned reclaim/reset, and forced chunk allocation.
- `btrfs_async_reclaim_metadata_space()` and `btrfs_async_reclaim_data_space()` run primary space infos and their zoned subgroups.

Priority and preemptive reclaim:
- `priority_flush_states` perform delayed item flushing, zone reset, and chunk allocation for limited high-priority metadata reservations.
- `evict_flush_states` are broader and include delayed refs, delalloc, chunk allocation, transaction commit, and zone reset.
- `priority_reclaim_metadata_space()` flushes the configured state list, then either fails the ticket, steals from global reserve when allowed, or returns filesystem abort errors.
- `priority_reclaim_data_space()` tries forced chunk allocation until the data space info is marked full, then fails the ticket.
- `need_preemptive_reclaim()` determines whether background metadata reclaim should start before writers block on tickets, considering global reserve, fullness, bytes pinned/may-use, ordered vs delalloc balance, and a dynamic `clamp` divisor.
- `btrfs_preempt_reclaim_metadata_space()` picks the largest reclaimable source among delalloc, pinned bytes, delayed items, and delayed refs, reclaims one quarter of that pressure, and adjusts the clamp if only one loop was needed.
- `maybe_clamp_preempt()` tightens preemptive reclaim thresholds when queued tickets prove background reclaim is falling behind buffered writers.

Ticket failure and global reserve:
- `steal_from_global_rsv()` can satisfy selected tickets from the global block reserve if the reserve belongs to the same space info and retains at least 10% of its target size.
- `maybe_fail_all_tickets()` runs when reclaim made no progress after repeated cycles. It can fail tickets with `-ENOSPC` or filesystem abort error, tries global-reserve stealing, and re-runs ticket granting so smaller later tickets can still proceed.
- `btrfs_dump_space_info()` and `btrfs_dump_space_info_for_trans_abort()` provide ENOSPC diagnostics for space infos, global block reserves, block groups, and free-space cache state.

Block group reclaim:
- `btrfs_account_ro_block_groups_free_space()` reports unused space inside readonly block groups, including RAID mirror factors, for `statfs`.
- `calc_unalloc_target()` targets ten effective data chunks of unallocated space.
- `calc_dynamic_reclaim_threshold()` raises reclaim intensity as unallocated chunk space falls below that target and backs off when the space info lacks enough unused allocated space to relocate.
- `btrfs_calc_reclaim_threshold()` selects either dynamic threshold or fixed `bg_reclaim_threshold`.
- `is_reclaim_urgent()` treats the filesystem as urgent when unallocated space is less than one effective data chunk.
- `do_reclaim_sweep()` scans block groups by RAID profile, marks groups below threshold that have aged at least one pass, and in urgent mode may do a second pass that accepts fresh candidates.
- `btrfs_reclaim_sweep()` runs periodic reclaim for eligible non-system space infos.
- `btrfs_space_info_update_reclaimable()` and `btrfs_set_periodic_reclaim_ready()` track net reclaimable bytes and arm/disarm cleaner-thread reclaim.

Cross-file relationships:
- `space-info.h` declares the structures, flush enums, counter helpers, and exported API implemented here.
- `block-group.c`, `extent-tree.c`, `delalloc-space.c`, `transaction.c`, and allocator paths update space-info counters and call reservation helpers.
- `super.c` uses `btrfs_account_ro_block_groups_free_space()` for `statfs` and cancels async reclaim work during readonly remount.
- `sysfs.c` exposes space-info objects and reclaim counters.
- `zoned.c` supplies reclaim, reset, and zoned-mode policy used by the flush states and subgroup setup.
- `free-space-cache.c` is used for diagnostic dumping of per-block-group free space.

Important invariants and risks:
- `space_info->lock` protects byte counters, ticket lists, `reclaim_size`, `tickets_id`, and reclaim-ready state.
- `groups_sem` protects block-group list traversal and insertion.
- Metadata overcommit must reserve one effective data chunk of unallocated space so data allocation cannot consume all metadata headroom.
- Normal reservation flush modes that can commit transactions are forbidden when `current->journal_info` is set.
- Ticket grant order is priority tickets first, then normal tickets; skipped or interrupted tickets must be removed before they can be granted.
- `bytes_may_use` is the reservation handoff point: reservations add it, extent allocation moves it to `bytes_reserved`, and block-group updates move reserved bytes to used bytes.
- Zoned mode changes several endpoints: chunk size is zone size, available overcommit is zone-aligned, data/metadata subgroups exist, and final reclaim may reset zones rather than only committing transactions.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/space-info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/space-info.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/space-info.h

This header defines Btrfs space-info state, reservation flush policies, reclaim states, subgroup identifiers, counter update helpers, and the public API for space reservation and reclaim.

Reservation flush policies:
- `BTRFS_RESERVE_NO_FLUSH` fails quickly and is used where flushing would block or deadlock, such as active transaction handles, nowait writes, and transaction attach/start cases that rely on existing reserves.
- `BTRFS_RESERVE_FLUSH_LIMIT` can run delayed inode items and allocate a chunk.
- `BTRFS_RESERVE_FLUSH_EVICT` can run delayed items, delayed refs, delalloc/ordered extents, chunk allocation, and transaction commit.
- `BTRFS_RESERVE_FLUSH_DATA`, `BTRFS_RESERVE_FLUSH_FREE_SPACE_INODE`, and `BTRFS_RESERVE_FLUSH_ALL` use broader reclaim; data/all waits are fatal-signal interruptible.
- `BTRFS_RESERVE_FLUSH_ALL_STEAL` is like full flushing but may steal from the global block reserve.
- `BTRFS_RESERVE_FLUSH_EMERGENCY` is reserved for `btrfs_use_block_rsv()` fallback when pessimistic reservation sizing was insufficient.

Reclaim state ordering:
- `enum btrfs_flush_state` orders metadata async reclaim states from delayed item flushing through delayed refs, delalloc, chunk allocation, delayed iputs, transaction commit, zone reset, and zoned block group reclaim.
- The numeric order is significant for `space-info.c`'s reclaim state machine.

`struct btrfs_space_info`:
- Points to `fs_info`, optional parent, and at most one zoned subgroup.
- Tracks logical counters: `total_bytes`, `bytes_used`, `bytes_pinned`, `bytes_reserved`, `bytes_may_use`, `bytes_readonly`, and `bytes_zone_unusable`.
- Tracks allocator state: `max_extent_size`, `chunk_size`, `bg_reclaim_threshold`, `clamp`, `full`, `chunk_alloc`, `flush`, and `force_alloc`.
- Tracks mirrored disk accounting with `disk_used` and `disk_total`.
- Owns lists for readonly block groups, priority tickets, normal tickets, and per-RAID block groups.
- Maintains `reclaim_size` and `tickets_id` for ticket-driven reclaim progress.
- Provides sysfs kobjects for the space info and its block-group profile directories.
- Maintains reclaim statistics: `reclaim_count`, `reclaim_bytes`, and `reclaim_errors`.
- Controls automatic block-group reclaim through `dynamic_reclaim`, `periodic_reclaim`, `periodic_reclaim_ready`, and `reclaimable_bytes`.

Subgroups:
- `BTRFS_SUB_GROUP_PRIMARY` identifies ordinary space infos.
- `BTRFS_SUB_GROUP_DATA_RELOC` and `BTRFS_SUB_GROUP_TREELOG` are used for zoned-mode data relocation and tree-log metadata.
- `BTRFS_SPACE_INFO_SUB_GROUP_MAX` is currently one, so each primary can have at most one subgroup.

Inline helpers:
- `btrfs_mixed_space_info()` detects combined DATA+METADATA space.
- `DECLARE_SPACE_INFO_UPDATE()` generates locked counter update helpers with tracepoints and underflow protection.
- Generated helpers update `bytes_may_use`, `bytes_pinned`, and `bytes_zone_unusable`.
- `btrfs_space_info_used()` sums used, reserved, pinned, readonly, zone-unusable, and optionally may-use bytes.
- `btrfs_space_info_free_bytes_may_use()` subtracts may-use bytes and immediately tries to grant waiting tickets.
- `btrfs_space_info_type_str()` maps common space-info flags to SYSTEM, DATA+METADATA, DATA, METADATA, or UNKNOWN.

Exported API:
- Initialization and lookup: `btrfs_init_space_info()`, `btrfs_add_bg_to_space_info()`, `btrfs_update_space_info_chunk_size()`, `btrfs_find_space_info()`, `btrfs_clear_space_info_full()`.
- Diagnostics: `btrfs_dump_space_info()` and `btrfs_dump_space_info_for_trans_abort()`.
- Reservations: `btrfs_reserve_metadata_bytes()`, `btrfs_reserve_data_bytes()`, `btrfs_try_granting_tickets()`, and `btrfs_can_overcommit()`.
- Reclaim work: `btrfs_init_async_reclaim_work()`, `btrfs_space_info_update_reclaimable()`, `btrfs_set_periodic_reclaim_ready()`, `btrfs_calc_reclaim_threshold()`, `btrfs_reclaim_sweep()`, and `btrfs_return_free_space()`.
- Reporting: `btrfs_account_ro_block_groups_free_space()`.

Cross-file relationships:
- Implemented by `space-info.c`.
- Included by allocation, transaction, block reserve, delalloc, block-group, sysfs, and superblock code.
- Includes `volumes.h` because space infos organize block groups by RAID profile and use Btrfs block-group flags.

Important invariants:
- Callers of generated update helpers and `btrfs_space_info_used()` must hold `space_info->lock`.
- `bytes_may_use` is reservation accounting, not actual allocated extent use.
- `bytes_zone_unusable` is a first-class used component for zoned filesystems until zone reset makes it reusable.
- The header's enum order and public flush semantics are part of the contract with `space-info.c`; changing them changes reclaim behavior.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/space-info.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/subpage.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/subpage.c

This file implements subpage support for cases where Btrfs sectors or metadata nodes are smaller than the kernel folio/page size. It attaches a `btrfs_folio_state` to folios and tracks per-sector state bits for uptodate, dirty, writeback, ordered, checked, and locked ranges.

Context and limitations:
- The file documents current subpage constraints: 64K page-size focus, metadata read/write support, and metadata not crossing a 64K page boundary.
- Metadata reads can operate on only the target tree block inside a folio.
- Metadata writeback still works at full-folio granularity but submits only dirty extent buffers inside that folio.
- Metadata locking relies on `io_tree` locking rather than folio locking to avoid deadlocks and excessive serialization among multiple tree blocks in one page.

Folio private-state lifecycle:
- `btrfs_attach_folio_state()` attaches private state only when the folio is actually subpage for the requested metadata/data type and does nothing when private state already exists.
- `btrfs_detach_folio_state()` detaches and frees state only for matching subpage metadata/data cases.
- `btrfs_alloc_folio_state()` allocates a flexible bitmap large enough for all state lanes across `fsize / sectorsize` sectors, initializes the lock, and initializes either `eb_refs` for metadata or `nr_locked` for data.
- `btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` protect metadata folio private state from being detached while extent buffers are being inserted or removed; callers must hold the mapping's `i_private_lock`.

Bitmap indexing and range handling:
- `btrfs_subpage_assert()` validates private state, sectorsize alignment, length alignment, and mapped-folio range containment.
- `subpage_calc_start_bit()` maps a byte range plus bitmap lane name to the starting bit in the packed bitmap.
- `btrfs_subpage_clamp_range()` intersects a caller range with the folio bounds and permits zero-length results for callers that walk folios beyond the logical target range.
- `subpage_test_bitmap_all_set()` and `subpage_test_bitmap_all_zero()` test whole-lane state for a folio.

Lock handling:
- `btrfs_subpage_end_and_test_lock()` clears the locked bits for a range, decrements `nr_locked`, and returns whether this was the final subpage lock.
- `btrfs_folio_end_lock()` handles non-subpage folios, plain `folio_lock()` cases with no subpage locked bits, and subpage range unlock cases.
- `btrfs_folio_end_lock_bitmap()` clears locked bits described by a sector bitmap and unlocks the folio only when all subpage locks are gone.
- `btrfs_folio_set_lock()` populates locked bits for a range on an already locked folio, mainly for async delalloc/compression paths that start from normal folio locking.

State operations:
- `btrfs_subpage_set_uptodate()` sets range bits and marks the whole folio uptodate only when all sectors are uptodate.
- `btrfs_subpage_clear_uptodate()` clears range bits and clears the folio uptodate flag.
- `btrfs_subpage_set_dirty()` sets range dirty bits and marks the folio dirty.
- `btrfs_subpage_clear_and_test_dirty()` clears range dirty bits and returns true when the folio has no dirty subpage sectors left.
- `btrfs_subpage_clear_dirty()` clears the folio dirty-for-IO state only when the last dirty subpage range was cleared.
- `btrfs_subpage_set_writeback()` sets range writeback bits and starts folio writeback; it preserves the writeback TOWRITE tag when the folio remains dirty so `WB_SYNC_ALL` does not miss it.
- `btrfs_subpage_clear_writeback()` clears range writeback bits and ends folio writeback when no writeback sectors remain.
- Ordered and checked helpers mirror this pattern, setting/clearing folio-level ordered/checked flags based on whole-lane state.

Generated helper families:
- `IMPLEMENT_BTRFS_SUBPAGE_TEST_OP()` creates all-set range tests for each bitmap lane.
- `IMPLEMENT_BTRFS_PAGE_OPS()` creates:
  - `btrfs_folio_set/clear/test_*()` for data folios that may or may not be subpage,
  - `btrfs_folio_clamp_set/clear/test_*()` for data folio operations where the requested range may exceed folio bounds,
  - `btrfs_meta_folio_set/clear/test_*()` for metadata extent-buffer ranges.
- Generated helpers fall back to normal folio operations when `fs_info` is absent in selftests or when the folio is not subpage.

Diagnostics and assertions:
- `btrfs_folio_assert_not_dirty()` asserts both folio dirty state and subpage dirty bits are clear, dumping the dirty bitmap on mismatch.
- `btrfs_subpage_dump_bitmap()` dumps all subpage bitmap lanes plus the base folio for debugging.
- `btrfs_get_subpage_dirty_bitmap()` reads the current dirty lane into a caller-supplied bitmap.
- `btrfs_meta_folio_clear_and_test_dirty()` clears metadata dirty state and returns whether the folio-level dirty flag was also cleared.

Cross-file relationships:
- `subpage.h` declares the bitmap layout, `btrfs_folio_state`, and all generated helper prototypes.
- Extent buffer and metadata I/O paths use the metadata helpers for tree blocks smaller than page size.
- Data writeback, compression, delalloc, and extent I/O paths use data folio and clamp helpers to bridge byte ranges to subpage sector state.
- `messages.h` provides warning output for bitmap dumps; `btrfs_inode.h` provides data-inode assertions used by the header.

Important invariants and risks:
- Subpage bitmap operations require an attached `btrfs_folio_state`; callers must attach private state before using subpage helpers.
- Start and length must be sectorsize-aligned.
- Metadata subpage currently assumes non-large folios.
- Folio-level flags summarize per-sector state but are deliberately conservative: uptodate/checked require all sectors, while dirty/writeback/ordered remain set while any sector is active.
- The locked bitmap and `nr_locked` allow one folio to represent multiple independently locked subranges; clearing the folio lock too early would break async delalloc and compression ordering.
- Writeback tag preservation in `btrfs_subpage_set_writeback()` is necessary for sync writeback correctness on dirty subpage folios.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/subpage.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/subpage.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/subpage.h

This header defines Btrfs subpage folio state and declares the helper API used by data and metadata paths when filesystem sectors or metadata nodes are smaller than the kernel folio size.

Bitmap layout:
- Packed bitmap lanes are ordered by lowercase enum values because macros use those names to generate function names.
- Lanes are:
  - `uptodate`,
  - `dirty`,
  - `writeback`,
  - `ordered`,
  - `checked`,
  - `locked`,
  - `max`.
- Each lane contains one bit per sector inside the folio.
- Comments note that ordered and checked are deprecated COW-fixup flags and that locked/writeback behavior is tied to async delalloc/compression lifecycle constraints.

`struct btrfs_folio_state`:
- Attached to `folio->private` for both data and metadata inodes when subpage state is needed.
- Contains a spinlock protecting bitmap lanes.
- Uses a union:
  - metadata uses `atomic_t eb_refs` to prevent premature detach while extent buffers refer to the folio,
  - data uses `atomic_t nr_locked` to count locked sectors inside the folio.
- Ends with a flexible `unsigned long bitmaps[]` sized by `btrfs_alloc_folio_state()`.

Subpage detection:
- `btrfs_meta_is_subpage()` returns true when `nodesize < PAGE_SIZE`; this works for metadata even for dummy extent-buffer folios without mappings.
- `btrfs_is_subpage()` returns true when `fs_info->sectorsize < folio_size(folio)` and asserts mapped folios belong to data inodes.

Lifecycle API:
- `btrfs_attach_folio_state()` and `btrfs_detach_folio_state()` manage folio private state.
- `btrfs_alloc_folio_state()` and `btrfs_free_folio_state()` allocate/free the private state.
- `btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` manage metadata extent-buffer references.

Lock API:
- `btrfs_folio_end_lock()` ends a byte-range subpage lock and unlocks the folio only when all subpage locks are gone.
- `btrfs_folio_set_lock()` marks a range locked on an already locked folio.
- `btrfs_folio_end_lock_bitmap()` clears locked sectors from a caller-provided bitmap.

Generated state APIs:
- `DECLARE_BTRFS_SUBPAGE_OPS(name)` declares subpage, data-folio, clamped-data-folio, and metadata-folio helpers for each state lane.
- The header declares full helper families for `uptodate`, `dirty`, `writeback`, `ordered`, and `checked`.
- Data helpers expect ranges inside one folio unless using the `clamp` variants.
- Metadata helpers use extent-buffer start/length and have no clamp variants because metadata folios are either subpage nodesize ranges or ordinary folios.

Other helpers:
- `btrfs_folio_clamp_finish_io()` is an error-cleanup helper that clears dirty, starts writeback, then clears writeback for a clamped range.
- `btrfs_subpage_clear_and_test_dirty()` clears dirty bits and reports whether this was the last dirty range.
- `btrfs_folio_assert_not_dirty()` verifies folio and subpage dirty state.
- `btrfs_meta_folio_clear_and_test_dirty()` handles metadata dirty clearing.
- `btrfs_get_subpage_dirty_bitmap()` exposes dirty-sector bitmap state to callers.
- `btrfs_subpage_dump_bitmap()` is a cold diagnostic dump helper.

Cross-file relationships:
- Implemented by `subpage.c`.
- Used by extent I/O, metadata extent-buffer, writeback, delalloc, and compression paths that cannot rely solely on folio-level flags.
- Includes `btrfs_inode.h` for `is_data_inode()` assertions in `btrfs_is_subpage()`.

Important invariants:
- Subpage metadata detection depends on nodesize, not mapping, because dummy extent-buffer folios can be unmapped.
- The bitmap lane order is part of the macro-generated ABI inside this translation unit pair.
- Per-sector state must remain synchronized with folio-level summary flags to preserve page-cache and writeback semantics.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/subpage.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/super.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/super.c

This file implements Btrfs VFS superblock integration: filesystem type registration, new mount API context handling, mount option parsing and reporting, subvolume mounting, remount transitions, `statfs`, sync/freeze/unfreeze, `/dev/btrfs-control` ioctls, super operations, shrinker hooks, device removal handling, and module init/exit sequencing.

Mount context and option parsing:
- `struct btrfs_fs_context` stores mount-time context: subvolume name/objectid, inline extent limit, commit interval, metadata ratio, thread pool size, mount option bits, compression type/level, and refcount.
- `btrfs_fs_parameters` describes supported new-mount-API parameters, including ACL, compression, COW/checksum, device scan, discard, free-space cache, subvolume selection, rescue options, and debug options.
- `btrfs_parse_compress()` accepts bare `compress`, typed compression, optional zlib/zstd levels, `compress-force`, and `no`/`none`; enabling compression clears NODATACOW/NODATASUM.
- `btrfs_parse_param()` maps parsed options to context bits and values, scans `device=`, handles rescue aliases/deprecations, validates thread pool size, maps `subvolid=0` to the top-level subvolume, and gates ACL support on `CONFIG_BTRFS_FS_POSIX_ACL`.
- Debug-only options include fragmentation, reference verification, and reference tracking under `CONFIG_BTRFS_DEBUG`.

Option validation and defaults:
- `btrfs_check_options()` rejects rescue/log-replay-ignore options on read-write mounts, prevents disabling the free-space tree when required by on-disk features, delegates zoned option validation, and warns about deprecated space cache v1.
- `btrfs_set_free_space_cache_settings()` reconciles mount options with on-disk free-space-cache state, forces free-space tree for sectorsize/page-size mismatch, clears v1 cache on zoned filesystems, and auto-selects v1 or v2 when the user did not specify a policy.
- `set_device_specific_options()` enables SSD optimizations for non-rotational devices unless disabled and auto-enables async discard on discard-capable non-zoned devices unless discard was explicitly configured.
- `btrfs_clear_oneshot_options()` clears mount-only options that should not persist across remount display/state.
- `btrfs_emit_options()` logs option transitions and current compression/max-inline settings.
- `btrfs_show_options()` emits `/proc/mounts` options including compression, rescue options, cache mode, discard, ACL, subvolume id, and resolved subvolume path.

Mount and subvolume flow:
- `btrfs_init_fs_context()` allocates the Btrfs fs context, installs operations, initializes defaults for new mounts, copies current info for reconfigure, and sets POSIX ACL/I_VERSION flags.
- `btrfs_dup_fs_context()` shares the private context between original and duplicated fs contexts while transferring `source` ownership to the duplicate used for the real superblock mount.
- `btrfs_get_tree_subvol()` allocates a preliminary `btrfs_fs_info`, duplicates the fs context, mounts or finds the real superblock through `btrfs_get_tree_super()`, handles compatibility reconfiguration for ro/rw subvolume mounts, creates a vfsmount, and switches `fc->root` to the requested subvolume dentry.
- `btrfs_get_tree_super()` scans the source device, safely pins `fs_devices` around `sget_fc()`, reuses existing superblocks when available, opens devices for first mounts, applies device-specific options, fills the superblock, and returns a root dentry.
- `btrfs_fill_super()` initializes VFS superblock operations/export/xattr/verity fields, sets up the backing device info, calls `open_ctree()`, emits options, creates the root inode dentry, and marks the superblock active.
- `mount_subvol()` resolves default subvolume objectid when needed, converts subvolid to a path, calls `mount_subtree()`, verifies the resulting inode is a subvolume inode, and checks subvolid/path consistency to catch rename races.
- `btrfs_get_subvol_name_from_objectid()` walks root backrefs and inode refs backwards to reconstruct an absolute subvolume path.
- `get_default_subvol_objectid()` looks up the `default` dir item in the tree of tree roots.

Remount/reconfigure:
- `btrfs_reconfigure()` synchronizes the filesystem, marks remounting, validates options/features, copies context to fs_info, handles thread-pool resizing, manages free-space-tree transition constraints, performs ro/rw transitions, updates POSIX ACL masks, emits option changes, wakes the transaction thread, runs cleanup, and clears remounting state.
- `btrfs_reconfigure_for_mount()` preserves compatibility for subvolume mounts that need to turn an existing read-only superblock back to read-write.
- `btrfs_remount_rw()` rejects remount after fatal errors, no writable devices, non-degradable device sets, or pending log replay; then runs pre-rw mount setup, clears readonly state, marks the fs open, and resumes discard.
- `btrfs_remount_ro()` cancels async reclaim work, cleans discard, waits for UUID scan, marks readonly, deletes unused block groups, waits for cleaner state, runs delayed iputs, suspends dev-replace/scrub/balance/qgroup work, and commits the super.
- `btrfs_remount_begin()` and `btrfs_remount_cleanup()` handle autodefrag shutdown, discard async toggles, and space-cache v1 active-state changes.
- `btrfs_resize_thread_pool()` updates Btrfs worker pools and relevant kernel workqueue max-active values.

Sync, statfs, and VFS operations:
- `btrfs_sync_fs()` flushes btree inode pages for non-wait sync, waits ordered roots for wait sync, attaches to or starts a transaction when needed, and commits it.
- `btrfs_calc_avail_data_space()` simulates the chunk allocator over devices sorted by free bytes to estimate additional data space available for `statfs`.
- `btrfs_statfs()` reports blocks/free/available space, accounts RAID profile factors, readonly block group free space, global block reserve, metadata exhaustion heuristics, sectorsize, name length, and a stable fsid mixed with subvolume root id.
- `btrfs_show_devname()` reports the latest device path under RCU.
- `btrfs_show_stats()` emits zoned stats for zoned filesystems.
- `btrfs_super_ops` wires Btrfs into VFS operations for inode lifecycle, put_super, sync, options, devname, statfs, freeze/unfreeze, shrinker object count/free, stats, block-device removal, and shutdown.

Freeze, unfreeze, and device safety:
- `btrfs_freeze()` sets `BTRFS_FS_FROZEN` and commits the current transaction.
- `check_dev_super()` rereads each present device's primary superblock while frozen, verifies checksum type, checksum, superblock validity, and committed generation.
- `btrfs_unfreeze()` checks all devices for unexpected modification, handles errors by forcing filesystem error/readonly state, then clears frozen state while still returning success to the VFS so thaw can finish.
- `btrfs_remove_bdev()` handles lower block-device removal notifications by marking the matching Btrfs device missing, updating writable/missing counts, checking whether read-write degraded operation remains possible, and setting DEGRADED when continuing.
- `btrfs_shutdown()` forces filesystem shutdown.

Control device and module lifecycle:
- `/dev/btrfs-control` is registered as a misc device with `btrfs_ctl_fops`.
- `btrfs_control_ioctl()` requires `CAP_SYS_ADMIN` and supports device scan, forget device, devices-ready query, and supported-feature query.
- `btrfs_interface_init()`/`btrfs_interface_exit()` register and unregister the control device.
- `btrfs_print_mod_info()` prints module feature flags such as experimental, debug, assert, zoned, fsverity, and read policy.
- `mod_init_seq` orders initialization of properties, sysfs, compression, caches, direct I/O, transactions, ctree, free-space caches, extent state/buffer caches, biosets, extent maps, optional read policy, ordered data, delayed inode/ref infrastructure, backrefs, control interface, sanity tests, and filesystem registration.
- `btrfs_exit_btrfs_fs()` unwinds successfully initialized components in reverse order; `exit_btrfs_fs()` also cleans up filesystem UUID tracking.
- `late_initcall(init_btrfs_fs)` registers the filesystem late in boot, and `module_exit(exit_btrfs_fs)` handles module unload.

Cross-file relationships:
- `disk-io.c` provides `open_ctree()`/`close_ctree()` and filesystem initialization/teardown internals.
- `transaction.c`, `ordered-data.c`, `delayed-inode.c`, `dev-replace.c`, `scrub.c`, `qgroup.c`, `discard.c`, and `block-group.c` are coordinated during sync, remount, freeze, and readonly transitions.
- `space-info.c` supplies readonly block group accounting and async reclaim work that this file cancels on readonly remount.
- `volumes.c` provides device scan/open/forget, degraded checks, device lookup, and allocator profile information.
- `compression.c` provides compression type/level parsing and display.
- `zoned.c` validates zoned mount options and reports zoned stats.
- `ioctl.c` supplies ioctl feature reporting and volume-argument path validation for the control device.

Important invariants and risks:
- The Btrfs subvolume mount path deliberately uses a duplicated fs context and a temporary mount because VFS superblock state and mount read-only state are distinct but must remain compatible with legacy mount behavior.
- `uuid_mutex` must not be held across `sget_fc()`; the code pins `fs_devices` to bridge that lifetime gap.
- Rescue options that bypass normal replay/checking are read-only only.
- Read-write remount is forbidden after filesystem error, insufficient writable devices, non-degradable device loss, or unreplayed tree log.
- Freeze/unfreeze superblock generation checks protect against hibernation or external modification while frozen.
- `statfs` availability is intentionally pessimistic and zeroes `f_bavail` when metadata is effectively exhausted.
- Module init uses a table-driven sequence so partial initialization failures unwind only completed stages.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/super.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/super.h

This header exposes the small public interface from `super.c` needed by other Btrfs code and defines inline helpers for accessing Btrfs filesystem state from a VFS superblock.

Declared API:
- `btrfs_check_options()` validates mount option bits against filesystem state and requested superblock flags.
- `btrfs_sync_fs()` is the Btrfs sync-super operation and can also be called directly by internal code.
- `btrfs_get_subvol_name_from_objectid()` resolves a subvolume root objectid to a path string.
- `btrfs_set_free_space_cache_settings()` initializes free-space-cache/free-space-tree mount policy from on-disk state and mount options.

Inline helpers:
- `btrfs_sb()` returns `sb->s_fs_info` as `struct btrfs_fs_info *`.
- `btrfs_set_sb_rdonly()` sets VFS `SB_RDONLY` and Btrfs `BTRFS_FS_STATE_RO`.
- `btrfs_clear_sb_rdonly()` clears both the VFS readonly flag and the Btrfs readonly state bit.

Cross-file relationships:
- Implemented by `super.c`.
- Included by mount, disk I/O, transaction, and filesystem-state code that needs access to `btrfs_fs_info` or needs to coordinate VFS readonly state with Btrfs internal state.
- Includes `fs.h` for `BTRFS_FS_STATE_RO` and the `btrfs_fs_info` state-bit definitions.

Important invariants:
- Readonly transitions must update both `sb->s_flags` and `fs_info->fs_state`; callers should use the inline helpers rather than setting one side manually.
- `btrfs_sb()` assumes `s_fs_info` has already been initialized with a valid Btrfs filesystem info object.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/super.h -->