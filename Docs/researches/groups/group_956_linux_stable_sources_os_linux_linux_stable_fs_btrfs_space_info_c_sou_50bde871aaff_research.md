# Group Research: group_956_linux_stable_sources_os_linux_linux_stable_fs_btrfs_space_info_c_sou_50bde871aaff

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux-stable`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/space-info.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/space-info.c

This file implements Btrfs space accounting, reservation admission, ENOSPC ticketing, async reclaim, preemptive metadata reclaim, and block-group reclaim threshold logic.

Key responsibilities:
- Initializes `btrfs_space_info` objects for SYSTEM, METADATA, DATA, mixed DATA+METADATA, and metadata remap profiles via `btrfs_init_space_info()`.
- Creates zoned-mode subgroups for data relocation and tree-log space with sysfs entries.
- Accounts block groups into a space-info through `btrfs_add_bg_to_space_info()`, updating logical totals, disk totals, used bytes, readonly bytes, superblock reservation bytes, and zone-unusable bytes.
- Provides lookup and state clearing helpers: `btrfs_find_space_info()` and `btrfs_clear_space_info_full()`.

Reservation model:
- `reserve_bytes()` is the central allocator admission path for both metadata and data reservations.
- Fast path grants reservations by increasing `bytes_may_use` if current usage plus requested bytes fits `total_bytes`, or if metadata overcommit is allowed.
- Metadata overcommit is deliberately disabled for data and mixed block group space.
- `BTRFS_RESERVE_FLUSH_EMERGENCY` bypasses normal `bytes_may_use` accounting pressure and admits only if actual non-`may_use` space can fit the request.
- Public wrappers are `btrfs_reserve_metadata_bytes()` and `btrfs_reserve_data_bytes()`.

Ticketing and ENOSPC handling:
- Failed reservations may create a stack-local `reserve_ticket` and enqueue it on `priority_tickets` or normal `tickets`.
- `btrfs_try_granting_tickets()` grants priority tickets before normal tickets, maintaining `reclaim_size` and `tickets_id`.
- `remove_ticket()` handles list removal, error assignment, successful completion, and wakeups.
- Normal waiters use `wait_reserve_ticket()` with killable waits; interrupted waits remove their own ticket to avoid leaked `bytes_may_use`.
- `maybe_fail_all_tickets()` fails tickets after reclaim has exhausted useful progress, optionally stealing from the global block reserve for allowed flush modes.

Flush and reclaim machinery:
- `flush_space()` maps `enum btrfs_flush_state` to concrete reclaim actions:
  - delayed inode item flushing,
  - delayed ref running,
  - delalloc writeout and ordered extent waiting,
  - chunk allocation,
  - delayed iputs,
  - transaction commit,
  - zoned block-group reclaim,
  - zoned reset of unused block groups.
- Metadata async reclaim starts at delayed items and advances through increasingly expensive states until tickets are satisfied or failed.
- Data async reclaim first tries forced chunk allocation while the space-info is not full, then runs full delalloc, delayed iputs, transaction commit, zoned reclaim/reset, and forced chunk allocation.
- Priority reclaim paths perform bounded synchronous flushing for callers that cannot wait on the normal async worker.

Preemptive reclaim:
- `need_preemptive_reclaim()` decides whether background metadata flushing should start before callers block on tickets.
- It avoids competing with active ticket reclaim, avoids running when the fs is closing or remounting, accounts for the global reserve, and scales aggressiveness through `space_info->clamp`.
- `btrfs_preempt_reclaim_metadata_space()` chooses what to flush based on the dominant reclaimable pool: delalloc, pinned bytes, delayed items, or delayed refs.

Chunk/free-space calculations:
- `calc_chunk_size()` chooses default chunk sizes based on zoned mode, block group type, total writable bytes, and metadata/data/system profile.
- `calc_effective_data_chunk_size()` bounds data chunk assumptions to 10% of writable device space or 1 GiB, except zoned mode where zone size is used directly.
- `calc_available_free_space()` estimates metadata overcommit capacity from unallocated chunk space or per-profile availability and reserves headroom for future data chunks.

Block-group reclaim:
- Dynamic reclaim tries to protect unallocated space by comparing free chunk space to a target of ten effective data chunks.
- `btrfs_calc_reclaim_threshold()` chooses either dynamic threshold or configured `bg_reclaim_threshold`.
- `btrfs_reclaim_sweep()` scans non-system space-infos and marks underused block groups for reclaim when periodic reclaim is ready.
- `btrfs_space_info_update_reclaimable()` sets periodic reclaim readiness after enough net reclaimable bytes accumulate.
- Urgent reclaim allows fresh block groups to be considered when unallocated space is below one effective data chunk.

Diagnostics and accounting helpers:
- `btrfs_dump_space_info()` prints aggregate space-info state, global block reserves, per-block-group availability, and free-space details.
- `btrfs_dump_space_info_for_trans_abort()` dumps all space-infos during transaction abort diagnostics.
- `btrfs_account_ro_block_groups_free_space()` reports unused readonly block group space for `df`-style accounting.
- `btrfs_return_free_space()` first refills the global reserve when possible, then grants pending tickets.

Concurrency and invariants:
- `space_info->lock` protects byte counters, ticket lists, reclaim flags, and reclaim counters.
- `groups_sem` protects block-group lists by RAID index.
- Ticket internals use their own spinlock and waitqueue.
- Reservation code asserts that transaction-holding callers do not use flush modes that can commit transactions and deadlock.
- The implementation relies on monotonic `tickets_id` to detect progress across reclaim cycles.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/space-info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/space-info.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/space-info.h

This header defines Btrfs space-info data structures, reservation flush policy enums, reclaim state ordering, byte-counter helpers, and exported APIs for reservation and reclaim.

Major definitions:
- `enum btrfs_reserve_flush_enum` describes caller-permitted reclaim strength:
  - no flushing,
  - limited flushing,
  - eviction-oriented flushing,
  - data flushing,
  - free-space-inode data flushing,
  - full flushing,
  - full flushing with global-reserve stealing,
  - emergency reservation.
- `enum btrfs_flush_state` orders reclaim stages used by async metadata reclaim. The numeric order is semantically important.
- `enum btrfs_space_info_sub_group` defines primary, data relocation, and tree-log subgroup identifiers.
- `BTRFS_SPACE_INFO_SUB_GROUP_MAX` is currently `1`, so each primary space-info can have one subgroup slot.

`struct btrfs_space_info`:
- Represents allocation state for a logical space class such as DATA, METADATA, SYSTEM, or mixed DATA+METADATA.
- Tracks logical counters:
  - `total_bytes`,
  - `bytes_used`,
  - `bytes_pinned`,
  - `bytes_reserved`,
  - `bytes_may_use`,
  - `bytes_readonly`,
  - `bytes_zone_unusable`.
- Tracks disk-accounting counters:
  - `disk_used`,
  - `disk_total`.
- Stores allocation/reclaim state:
  - `full`,
  - `chunk_alloc`,
  - `flush`,
  - `force_alloc`,
  - `reclaim_size`,
  - `tickets_id`,
  - `clamp`,
  - `chunk_size`.
- Holds ticket queues:
  - `priority_tickets`,
  - `tickets`.
- Holds block-group lists by RAID type under `groups_sem`.
- Exposes reclaim stats and policy:
  - `reclaim_count`,
  - `reclaim_bytes`,
  - `reclaim_errors`,
  - `dynamic_reclaim`,
  - `periodic_reclaim`,
  - `periodic_reclaim_ready`,
  - `reclaimable_bytes`.

Important inline helpers:
- `btrfs_mixed_space_info()` detects mixed DATA+METADATA space.
- `DECLARE_SPACE_INFO_UPDATE()` generates guarded counter update helpers with tracing and underflow detection.
- Generated helpers cover:
  - `bytes_may_use`,
  - `bytes_pinned`,
  - `bytes_zone_unusable`.
- `btrfs_space_info_used()` sums used, reserved, pinned, readonly, zone-unusable, and optionally `bytes_may_use`.
- `btrfs_space_info_free_bytes_may_use()` subtracts from `bytes_may_use` and immediately tries to grant tickets.
- `btrfs_space_info_type_str()` maps exact block group type flags to display strings.

Exported API surface:
- Initialization and lookup:
  - `btrfs_init_space_info()`,
  - `btrfs_add_bg_to_space_info()`,
  - `btrfs_update_space_info_chunk_size()`,
  - `btrfs_find_space_info()`,
  - `btrfs_clear_space_info_full()`.
- Reservation:
  - `btrfs_reserve_metadata_bytes()`,
  - `btrfs_reserve_data_bytes()`,
  - `btrfs_can_overcommit()`,
  - `btrfs_try_granting_tickets()`.
- Diagnostics:
  - `btrfs_dump_space_info()`,
  - `btrfs_dump_space_info_for_trans_abort()`.
- Reclaim:
  - `btrfs_init_async_reclaim_work()`,
  - `btrfs_account_ro_block_groups_free_space()`,
  - `btrfs_space_info_update_reclaimable()`,
  - `btrfs_set_periodic_reclaim_ready()`,
  - `btrfs_calc_reclaim_threshold()`,
  - `btrfs_reclaim_sweep()`,
  - `btrfs_return_free_space()`.

Concurrency assumptions:
- Byte counter helpers assert `space_info->lock` is held.
- Block-group list traversal is coordinated with `groups_sem`.
- The header exposes only policy and accounting interfaces; the reclaim state machine is implemented in `space-info.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/space-info.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/subpage.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/subpage.c

This file implements Btrfs subpage folio state handling for cases where filesystem sector size or metadata node size is smaller than the kernel folio/page size.

Purpose:
- Tracks per-sector state inside a folio using `struct btrfs_folio_state`.
- Supports separate bitmap state for uptodate, dirty, writeback, ordered, checked, and locked sectors.
- Bridges normal folio-level flags with subpage-aware operations.

Folio state lifecycle:
- `btrfs_attach_folio_state()` attaches subpage private state only when needed:
  - metadata requires subpage support when nodesize is smaller than `PAGE_SIZE`,
  - data requires subpage support when sectorsize is smaller than folio size.
- `btrfs_detach_folio_state()` detaches and frees the private state when the folio no longer needs it.
- `btrfs_alloc_folio_state()` sizes the bitmap array as `btrfs_bitmap_nr_max * sectors_per_folio`, initializes the spinlock, and initializes either metadata `eb_refs` or data `nr_locked`.

Metadata extent-buffer references:
- `btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` protect subpage metadata folio state from being detached while extent buffers are being created or destroyed.
- These helpers require the mapping private lock and only operate when metadata subpage mode is active.

Range validation and clamping:
- `btrfs_subpage_assert()` verifies private state exists, start/length are sector-aligned, and mapped folio ranges fit within the folio.
- `subpage_calc_start_bit()` maps a byte range and bitmap kind to a starting bit offset.
- `btrfs_subpage_clamp_range()` safely truncates arbitrary data ranges to the portion covered by the current folio.

Lock handling:
- `btrfs_folio_set_lock()` marks per-sector locked bits for a range already protected by the ordinary folio lock.
- `btrfs_folio_end_lock()` clears subpage lock bits and unlocks the folio only when the last subpage lock is gone.
- `btrfs_folio_end_lock_bitmap()` clears locked bits from a caller-provided bitmap.
- The implementation handles folios locked by plain `folio_lock()` with no subpage lock bits by simply unlocking the folio.

Bitmap operations:
- Direct subpage setters/clearers/testers are implemented for:
  - uptodate,
  - dirty,
  - writeback,
  - ordered,
  - checked.
- Uptodate and checked mark the whole folio flag only when all subpage bits are set.
- Clearing uptodate or checked clears the whole folio flag.
- Dirty marking sets subpage dirty bits and marks the folio dirty.
- `btrfs_subpage_clear_and_test_dirty()` returns whether clearing a range made the full dirty bitmap empty.
- Writeback handling starts folio writeback only when needed and ends folio writeback when all subpage writeback bits are clear.
- `btrfs_subpage_set_writeback()` preserves writeback indexing semantics for still-dirty folios so `WB_SYNC_ALL` writeback does not miss remaining dirty data.

Macro-generated API families:
- `IMPLEMENT_BTRFS_SUBPAGE_TEST_OP()` generates direct subpage test functions.
- `IMPLEMENT_BTRFS_PAGE_OPS()` generates:
  - `btrfs_folio_set_*`,
  - `btrfs_folio_clear_*`,
  - `btrfs_folio_test_*`,
  - clamped data-folio variants,
  - metadata extent-buffer variants.
- Non-subpage and selftest paths fall back to ordinary folio flag operations.

Assertions and diagnostics:
- `btrfs_folio_assert_not_dirty()` checks both folio dirty state and subpage dirty bitmap state under `CONFIG_BTRFS_ASSERT`.
- `btrfs_subpage_dump_bitmap()` dumps all subpage bitmaps for a folio and includes `dump_page()` output.
- `btrfs_get_subpage_dirty_bitmap()` exports the dirty bitmap for callers that need to submit or inspect dirty subranges.

Concurrency:
- Per-folio bitmap operations are protected by `btrfs_folio_state.lock`.
- `nr_locked` is atomic because multiple subpage lock ranges can coexist.
- Metadata `eb_refs` is atomic but must be manipulated under the mapping private lock.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/subpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/subpage.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/subpage.h

This header declares Btrfs subpage support types and helper APIs.

Core concept:
- When Btrfs sector size or metadata node size is smaller than a folio, a single folio can contain multiple independently tracked Btrfs sectors or tree blocks.
- `struct btrfs_folio_state` stores per-sector bitmaps in `folio->private`.

Bitmap layout:
- `btrfs_bitmap_nr_uptodate`,
- `btrfs_bitmap_nr_dirty`,
- `btrfs_bitmap_nr_writeback`,
- `btrfs_bitmap_nr_ordered`,
- `btrfs_bitmap_nr_checked`,
- `btrfs_bitmap_nr_locked`,
- `btrfs_bitmap_nr_max`.

State object:
- `struct btrfs_folio_state` contains:
  - `lock` for bitmap protection,
  - metadata-only `eb_refs`,
  - data-only `nr_locked`,
  - flexible bitmap storage.
- `enum btrfs_folio_type` distinguishes metadata and data users.

Subpage detection:
- `btrfs_meta_is_subpage()` returns true when `nodesize < PAGE_SIZE`.
- `btrfs_is_subpage()` returns true when `sectorsize < folio_size(folio)` and asserts mapped folios belong to data inodes.

Declared lifecycle APIs:
- `btrfs_attach_folio_state()`,
- `btrfs_detach_folio_state()`,
- `btrfs_alloc_folio_state()`,
- `btrfs_free_folio_state()`.

Metadata extent-buffer reference APIs:
- `btrfs_folio_inc_eb_refs()`,
- `btrfs_folio_dec_eb_refs()`.

Lock APIs:
- `btrfs_folio_end_lock()`,
- `btrfs_folio_set_lock()`,
- `btrfs_folio_end_lock_bitmap()`.

Generated bitmap operation declarations:
- `DECLARE_BTRFS_SUBPAGE_OPS(name)` declares subpage, folio, clamped folio, and metadata folio variants.
- Operations are declared for:
  - uptodate,
  - dirty,
  - writeback,
  - ordered,
  - checked.

Additional helpers:
- `btrfs_folio_clamp_finish_io()` clears dirty, sets writeback, then clears writeback for error cleanup.
- `btrfs_subpage_clear_and_test_dirty()` clears dirty bits and reports whether the whole folio is now clean.
- `btrfs_folio_assert_not_dirty()` verifies folio and bitmap cleanliness.
- `btrfs_meta_folio_clear_and_test_dirty()` is the metadata extent-buffer dirty-clear helper.
- `btrfs_get_subpage_dirty_bitmap()` retrieves dirty bitmap state.
- `btrfs_subpage_dump_bitmap()` provides cold-path diagnostics.

Design notes:
- The header explicitly separates direct subpage helpers from folio helpers and clamped data-folio helpers.
- Metadata callers are expected to use `btrfs_meta_folio_*()` helpers rather than clamp variants.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/subpage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/super.c

This file implements Btrfs VFS superblock integration, mount option parsing, fs-context operations, subvolume mounting, remount handling, statfs accounting, control-device ioctls, freeze/unfreeze behavior, superblock operations, filesystem registration, and module init/exit sequencing.

Mount context and options:
- `struct btrfs_fs_context` stores parsed mount state before it is copied into `btrfs_fs_info`.
- `btrfs_fs_parameters[]` defines the new mount API parameter table for options such as compression, discard, space cache, rescue modes, subvolume selection, degraded mounts, thread pool size, and debugging options.
- `btrfs_parse_param()` maps parsed options into mount flags and context fields.
- Compression parsing supports `zlib`, `lzo`, `zstd`, optional levels where supported, `compress-force`, and disabling compression with `no` or `none`.
- Rescue options include backup root, no log replay, ignoring bad roots, ignoring data or metadata checksums, ignoring super flags, and `rescue=all`.
- Deprecated compatibility options such as `usebackuproot` and `norecovery` are preserved with warnings or compatibility messages.

Option validation and defaults:
- `btrfs_check_options()` rejects writeable mounts with read-only-only rescue options and prevents invalid free-space-tree combinations.
- It delegates zoned-specific mount option validation to `btrfs_check_mountopts_zoned()`.
- `btrfs_set_free_space_cache_settings()` chooses free-space-cache behavior from explicit options, on-disk feature state, page/sector size constraints, and zoned mode.
- `set_device_specific_options()` auto-enables SSD optimizations and async discard when devices support it and the user did not override it.
- One-shot options such as backup root and clear cache are cleared after mount/remount processing.

Subvolume naming and selection:
- `btrfs_get_subvol_name_from_objectid()` reconstructs a subvolume path by walking root backrefs in the root tree and inode refs in filesystem trees.
- `get_default_subvol_objectid()` resolves the default subvolume from the root directory’s `default` item, falling back to the top-level subvolume.
- `mount_subvol()` mounts a selected subvolume path, verifies the root inode is a subvolume inode, and checks that `subvolid` matches when supplied.

Superblock fill and sync:
- `btrfs_fill_super()` initializes VFS superblock fields, sets operations, export ops, xattrs, verity ops when enabled, backing device info, opens the Btrfs tree, emits options, and creates the root dentry.
- `btrfs_sync_fs()` flushes btree inode mapping for non-wait syncs, waits ordered roots for wait syncs, attaches or starts a transaction if needed, and commits it.

Show options:
- `btrfs_show_options()` emits the effective mount options for `/proc/mounts`, including compression, rescue flags, discard mode, ACL state, space cache state, subvolume id, and subvolume path.
- `print_rescue_option()` formats multiple rescue flags under a single `rescue=` option group.

Remount/reconfigure:
- `btrfs_reconfigure()` implements fs-context reconfiguration and remount behavior.
- It preserves mount options during bind-style subvolume reconfiguration, syncs the filesystem, sets remounting state, validates options and features, resizes worker pools, transitions read-only/read-write state, emits changed options, wakes the transaction thread, and cleans up one-shot state.
- `btrfs_remount_rw()` prevents writeable remount after fs error, without writeable devices, when not degradable enough, or when log replay would be required.
- `btrfs_remount_ro()` cancels reclaim work, stops discard, waits for UUID rescan, sets readonly state, deletes unused block groups, waits for cleaner work, runs delayed iputs, suspends dev-replace, cancels scrub, pauses balance, waits qgroup rescan, and commits the superblock.
- `btrfs_remount_begin()` and `btrfs_remount_cleanup()` coordinate autodefrag, discard, and space-cache side effects.

`statfs` accounting:
- `btrfs_calc_avail_data_space()` simulates data chunk allocation across devices sorted by maximum available space and RAID profile constraints.
- `btrfs_statfs()` reports total blocks, free blocks, available blocks, block size, name length, and fsid.
- It accounts for global block reserve, readonly block group free space, RAID profile factors, mixed metadata/data mode, and metadata exhaustion heuristics.

Mount API and subvolume mount mechanics:
- `btrfs_get_tree_super()` scans the source device, finds or creates a VFS superblock with `sget_fc()`, opens devices for first mounts, fills the superblock, and reuses existing superblocks for subsequent mounts.
- `btrfs_get_tree_subvol()` creates a duplicated fs context for the real superblock mount, then mounts the requested subvolume as the caller’s root.
- `btrfs_reconfigure_for_mount()` preserves compatibility for per-subvolume ro/rw behavior by converting a reused read-only superblock back to read-write when needed.
- `btrfs_dup_fs_context()` shares the Btrfs fs context across duplicated fs contexts and transfers `source` ownership carefully.
- `btrfs_free_fs_context()` releases partially initialized fs-info and refcounted mount context state.

Filesystem type and control device:
- `btrfs_fs_type` registers Btrfs with the VFS using fs-context operations and flags requiring a block device, binary mount data, idmapped mounts, and multigrain timestamps.
- `/dev/btrfs-control` is registered as a misc device.
- `btrfs_control_ioctl()` supports:
  - scanning a device,
  - forgetting devices,
  - checking whether devices are ready,
  - returning supported feature flags.
- Control ioctls require `CAP_SYS_ADMIN`.

Freeze/unfreeze and device integrity:
- `btrfs_freeze()` marks the fs frozen and commits the current transaction.
- `btrfs_unfreeze()` checks every device’s primary superblock for checksum, superblock validity, checksum type, fsid validity, and generation consistency before clearing frozen state.
- `check_dev_super()` performs the per-device validation and returns `-EUCLEAN` on detected unexpected modification.

Super operations:
- `btrfs_super_ops` wires Btrfs into VFS operations for inode eviction, sync, option display, device name display, inode allocation/destruction, statfs, freeze/unfreeze, shrinker callbacks, zoned stats, block-device removal, and shutdown.
- `btrfs_remove_bdev()` marks a removed block device missing, updates writable device accounting, checks degradability, and either continues degraded or fails read-write operation.
- `btrfs_shutdown()` forces filesystem shutdown.
- Shrinker callbacks count and free cached extent maps.

Module initialization:
- `mod_init_seq[]` defines ordered init/exit pairs for properties, sysfs, compression, caches, direct I/O, transactions, ctree, free-space cache, extent states, extent buffers, biosets, extent maps, ordered data, delayed inode/ref infrastructure, auto defrag, preliminary refs, control interface, sanity tests, and filesystem registration.
- `init_btrfs_fs()` runs the sequence and unwinds already initialized steps on failure.
- `exit_btrfs_fs()` reverses initialized steps and cleans up filesystem UUID state.
- Module metadata declares Btrfs description and GPL license.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/super.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/super.h

This header exposes a small Btrfs superblock-facing API used by other Btrfs files.

Declared functions:
- `btrfs_check_options()` validates parsed mount options against filesystem state and target superblock flags.
- `btrfs_sync_fs()` is the VFS sync implementation exported for use outside `super.c`.
- `btrfs_get_subvol_name_from_objectid()` resolves a subvolume objectid to a path-like subvolume name.
- `btrfs_set_free_space_cache_settings()` initializes effective free-space-cache mount behavior from on-disk state and mount options.

Inline helpers:
- `btrfs_sb()` returns `sb->s_fs_info` as `struct btrfs_fs_info *`.
- `btrfs_set_sb_rdonly()` sets `SB_RDONLY` and the Btrfs internal `BTRFS_FS_STATE_RO` bit.
- `btrfs_clear_sb_rdonly()` clears both the VFS read-only flag and the Btrfs internal read-only state bit.

Role:
- Keeps common superblock helpers available without exposing the full mount implementation in `super.c`.
- Maintains consistency between VFS `sb->s_flags` and Btrfs `fs_state` read-only tracking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/super.h -->