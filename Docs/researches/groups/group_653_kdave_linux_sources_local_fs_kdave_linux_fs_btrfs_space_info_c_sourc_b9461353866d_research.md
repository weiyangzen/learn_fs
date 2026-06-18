# Group Research: group_653_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_space_info_c_sourc_b9461353866d

Scope verified against `Docs/research_subset_a.md`. All six listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/space-info.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/space-info.c

Read coverage: complete file, 2258 lines.

This file implements Btrfs space reservation, ENOSPC ticketing, async reclaim, preemptive metadata reclaim, data-space reclaim, and periodic block-group reclaim. It is the implementation backing `space-info.h`.

Main responsibilities:
- Initializes `btrfs_space_info` instances for system, metadata, data, mixed data+metadata, and remap-tree block-group classes.
- Tracks block-group totals, used bytes, disk totals, readonly bytes, zone-unusable bytes, and reclaim state.
- Implements metadata overcommit policy with `calc_available_free_space()`, `btrfs_can_overcommit()`, and reserve-time checks.
- Implements reservation tickets with FIFO-style normal tickets and separate priority tickets.
- Drives flushing through ordered states: delayed items, delayed refs, delalloc, chunk allocation, delayed iputs, transaction commit, zoned reset, and zoned reclaim.
- Exposes diagnostics through `btrfs_dump_space_info()` and transaction-abort dump helpers.
- Implements dynamic and periodic block-group reclaim thresholds.

Important flows:
- `btrfs_init_space_info()` creates initial space-info objects based on superblock incompat features.
- `btrfs_add_bg_to_space_info()` accounts a block group into its space info and links it by RAID index.
- `reserve_bytes()` is the central reservation engine. It checks current usage, pending tickets, overcommit eligibility, emergency reservation rules, ticket creation, async work triggering, and preemptive reclaim triggering.
- `btrfs_reserve_metadata_bytes()` and `btrfs_reserve_data_bytes()` are the public metadata/data entry points.
- `btrfs_try_granting_tickets()` grants priority tickets first, then normal tickets, updating `bytes_may_use`.
- `do_async_reclaim_metadata_space()` advances the metadata reclaim state machine until tickets are served or failed.
- `do_async_reclaim_data_space()` tries forced data chunk allocation, then escalates through data reclaim states.
- `btrfs_reclaim_sweep()` scans reclaim-ready space infos and marks low-utilization block groups for relocation.

Concurrency and invariants:
- `space_info->lock` protects core counters, ticket lists, reclaim flags, and reclaim threshold state.
- `groups_sem` protects block-group list traversal and mutation.
- Ticket wait state has its own spinlock and waitqueue.
- Reservation paths assert that transaction-holding callers do not use flush modes that may commit and deadlock.
- Counter update helpers from the header trace changes and guard underflow.

Integration points:
- Uses transaction, delayed inode, delayed ref, ordered extent, chunk allocator, block-group, zoned, free-space-cache, and sysfs subsystems.
- Work items initialized by `btrfs_init_async_reclaim_work()` are stored in `btrfs_fs_info`.
- `super.c` consumes readonly block-group accounting through `btrfs_account_ro_block_groups_free_space()` for `statfs`.

Risk notes:
- Reservation correctness depends on strict lock ordering and ticket removal semantics; interrupted waits explicitly remove tickets to avoid `bytes_may_use` leaks.
- Metadata overcommit is intentionally conservative and disabled for mixed/data space infos.
- Zoned mode changes reclaim termination and chunk sizing; regressions here can surface as false ENOSPC or overcommit.
- Dynamic reclaim threshold math intentionally uses approximations and overflow-aware percentage calculation.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/space-info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/space-info.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/space-info.h

Read coverage: complete file, 344 lines.

This header defines the Btrfs space-info reservation and reclaim interface.

Main contents:
- `enum btrfs_reserve_flush_enum` defines caller flush permissions, from no-flush and limited flush through full flush, global-reserve stealing, and emergency reservation.
- `enum btrfs_flush_state` defines reclaim state ordering used by async metadata reclaim.
- `enum btrfs_space_info_sub_group` defines primary and zoned subgroups for data relocation and tree-log separation.
- `struct btrfs_space_info` stores logical/disk accounting, block-group lists, tickets, reclaim counters, sysfs kobjects, zoned unusable bytes, chunk sizing, and periodic reclaim state.

Important inline helpers:
- `btrfs_mixed_space_info()` detects mixed data+metadata space infos.
- `DECLARE_SPACE_INFO_UPDATE()` generates traced, underflow-checked update helpers for `bytes_may_use`, `bytes_pinned`, and `bytes_zone_unusable`.
- `btrfs_space_info_used()` sums used, reserved, pinned, readonly, zone-unusable, and optionally may-use bytes under lock.
- `btrfs_space_info_free_bytes_may_use()` releases may-use bytes and immediately retries ticket granting.
- `btrfs_space_info_type_str()` maps flags to user-readable type strings.

Exported API:
- Initialization and lookup: `btrfs_init_space_info()`, `btrfs_find_space_info()`.
- Block-group accounting: `btrfs_add_bg_to_space_info()`, `btrfs_update_space_info_chunk_size()`.
- Reservation: `btrfs_reserve_metadata_bytes()`, `btrfs_reserve_data_bytes()`, `btrfs_try_granting_tickets()`, `btrfs_can_overcommit()`.
- Diagnostics and reclaim: `btrfs_dump_space_info()`, `btrfs_dump_space_info_for_trans_abort()`, `btrfs_reclaim_sweep()`, `btrfs_calc_reclaim_threshold()`.
- Reclaim readiness: `btrfs_space_info_update_reclaimable()`, `btrfs_set_periodic_reclaim_ready()`, `btrfs_return_free_space()`.

Risk notes:
- Callers must hold `space_info->lock` for inline accounting helpers that assert lock ownership.
- Flush enum selection is a deadlock boundary: transaction-holding paths must avoid commit-capable flush modes.
- `BTRFS_SPACE_INFO_SUB_GROUP_MAX` is currently `1`, so subgroup users assume a single slot.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/space-info.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/subpage.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/subpage.c

Read coverage: complete file, 828 lines.

This file implements Btrfs subpage folio state: tracking sector-level uptodate, dirty, writeback, ordered, checked, and locked bits when filesystem sector size is smaller than folio/page size.

Main responsibilities:
- Allocates and attaches `struct btrfs_folio_state` as folio private data for metadata or data folios.
- Maintains packed per-sector bitmaps for page state flags.
- Provides subpage-aware set, clear, test, clamp, and metadata wrappers.
- Bridges normal folio flags and subpage bitmaps so non-subpage filesystems use standard folio operations.
- Manages subpage locking for compressed async delalloc and multi-sector folios.
- Provides debug dumping and dirty bitmap extraction.

Important flows:
- `btrfs_attach_folio_state()` attaches private state only when subpage handling is needed.
- `btrfs_alloc_folio_state()` sizes the bitmap array as `bitmap_count * blocks_per_folio`.
- `btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` protect metadata extent-buffer lifetime against folio-private detachment races.
- `btrfs_folio_set_lock()`, `btrfs_folio_end_lock()`, and `btrfs_folio_end_lock_bitmap()` maintain subpage lock counts and unlock the folio only after the last locked sector clears.
- Explicit implementations handle uptodate, dirty, writeback, ordered, and checked state.
- `IMPLEMENT_BTRFS_PAGE_OPS()` generates regular, clamped, and metadata wrappers for each tracked state.
- `btrfs_meta_folio_clear_and_test_dirty()` tells metadata writeback whether clearing an extent buffer made the whole folio clean.
- `btrfs_folio_assert_not_dirty()` and `btrfs_subpage_dump_bitmap()` support assert/debug diagnostics.

Concurrency and invariants:
- `btrfs_folio_state->lock` protects bitmap operations.
- Data folios use `nr_locked`; metadata folios use `eb_refs` in the same union.
- Metadata subpage support asserts non-large folios.
- Range operations assert sector alignment and single-folio containment, except clamp helpers intentionally trim ranges.
- Writeback start preserves the `TOWRITE` tag when the folio remains dirty to avoid sync writeback ordering bugs.

Integration points:
- Used by extent buffer, extent IO, delalloc, metadata writeback, and data folio code.
- Depends on `btrfs_blocks_per_folio()`, folio flags, extent buffer ranges, and `is_data_inode()` assertions.

Risk notes:
- Bitmap/folio flag synchronization is subtle; a missed clear can leave folios permanently dirty/writeback/ordered.
- Lock count handling must remain consistent with bitmap bits or folio unlock can happen too early or never happen.
- Metadata subpage behavior intentionally avoids page locking as the sole metadata lock to prevent deadlocks among tree blocks sharing a folio.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/subpage.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/subpage.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/subpage.h

Read coverage: complete file, 212 lines.

This header declares Btrfs subpage folio-state types and helper APIs.

Main contents:
- Bitmap index enum for `uptodate`, `dirty`, `writeback`, `ordered`, `checked`, and `locked`.
- `struct btrfs_folio_state`, containing a spinlock, either metadata `eb_refs` or data `nr_locked`, and flexible packed bitmap storage.
- `enum btrfs_folio_type` distinguishes metadata and data users.
- Inline detection helpers:
  - `btrfs_meta_is_subpage()` checks `nodesize < PAGE_SIZE`.
  - `btrfs_is_subpage()` checks `sectorsize < folio_size(folio)` and asserts data inode mapping when present.

Declared API:
- Attach/detach/allocation: `btrfs_attach_folio_state()`, `btrfs_detach_folio_state()`, `btrfs_alloc_folio_state()`, `btrfs_free_folio_state()`.
- Metadata extent-buffer refs: `btrfs_folio_inc_eb_refs()`, `btrfs_folio_dec_eb_refs()`.
- Lock handling: `btrfs_folio_set_lock()`, `btrfs_folio_end_lock()`, `btrfs_folio_end_lock_bitmap()`.
- Macro-generated state APIs for subpage, regular folio, clamped folio, and metadata folio operations.
- Cleanup/debug helpers: `btrfs_folio_clamp_finish_io()`, dirty clear/test helpers, dirty assertions, dirty bitmap extraction, and bitmap dump.

Design notes:
- The header documents the naming split:
  - `btrfs_subpage_*()` assumes subpage private state and a range inside one folio.
  - `btrfs_folio_*()` handles either subpage or normal folio.
  - `btrfs_folio_clamp_*()` trims larger ranges to a folio.
  - `btrfs_meta_folio_*()` is for metadata extent buffers.

Risk notes:
- Callers must choose the correct helper family; passing a cross-folio range to non-clamp helpers violates assumptions.
- Ordered and checked flags are documented as deprecated COW-fixup state.
- The locked bitmap is tied to async delalloc/compression lifetime and is explicitly marked as needing future rework.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/subpage.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/super.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/super.c

Read coverage: complete file, 2711 lines.

This file implements the Btrfs Linux filesystem registration, mount/fs_context parsing, superblock operations, remount handling, statfs reporting, `/dev/btrfs-control`, freeze/unfreeze checks, and module init/exit sequencing.

Main responsibilities:
- Defines `btrfs_fs_context` and parses mount parameters through the new mount API.
- Validates option combinations, rescue options, zoned constraints, free-space-cache constraints, compression settings, and readonly-only recovery options.
- Opens/scans devices, creates or reuses superblocks, fills the superblock, and mounts the selected subvolume.
- Supports subvolume mounts with differing mount read-only/read-write state via internal reconfigure compatibility logic.
- Implements `sync_fs`, `show_options`, `statfs`, freeze/unfreeze, device removal notification, shrinker callbacks, and shutdown.
- Registers the `btrfs` filesystem type and `/dev/btrfs-control` misc device.
- Runs ordered subsystem initialization and reverse cleanup for the module.

Important flows:
- `btrfs_parse_param()` handles all user mount options and stores them in `btrfs_fs_context`.
- `btrfs_check_options()` enforces readonly-only rescue flags, free-space-tree constraints, zoned options, and deprecation warnings.
- `btrfs_set_free_space_cache_settings()` derives v1/v2 free-space cache behavior from mount options and on-disk features; it forces free-space-tree for subpage sector/page mismatch.
- `btrfs_get_tree_subvol()` allocates temporary `fs_info`, duplicates fs_context, mounts the whole filesystem, reconfigures if needed, then mounts the selected subvolume subtree.
- `btrfs_fill_super()` sets VFS superblock callbacks, opens the ctree, emits options, and installs the root inode/dentry.
- `btrfs_reconfigure()` applies remount options, handles RO/RW transitions, resizes worker pools, reconciles free-space-tree option state, and restores old context on failure.
- `btrfs_statfs()` combines allocated data/metadata free space, readonly block-group adjustments, simulated data allocation availability, global reserve accounting, and subvolume-specific fsid.
- `btrfs_freeze()` commits current transactions; `btrfs_unfreeze()` rereads device superblocks to detect unexpected external modification before clearing frozen state.
- `init_btrfs_fs()` walks `mod_init_seq`; failed initialization unwinds initialized components in reverse.

Concurrency and lifetime:
- Device scanning/opening is coordinated under `uuid_mutex`, but `sget_fc()` is called without holding it to avoid lock-order inversion.
- Existing superblock reuse leaves the temporary fs_context-owned `fs_info` for later cleanup.
- Remount-to-readonly cancels reclaim work, cleans discard state, waits for cleaner/uuid/qgroup/scrub/balance activity, and commits the superblock.
- Freeze/unfreeze assumes the filesystem remains frozen while validating device superblocks.

Integration points:
- Includes and coordinates most Btrfs subsystems: disk-io, transactions, compression, dev replace, free-space cache/tree, qgroups, scrub, raid56, zoned mode, verity, ioctl, sysfs, and space-info.
- Exports functions declared in `super.h`: option checking, sync, subvolume-name lookup, and free-space-cache settings.

Risk notes:
- Mount option interactions are compatibility-sensitive ABI: compression vs nodatacow/nodatasum, rescue aliases, deprecated options, and old/new mount API readonly semantics.
- Subvolume mount handling relies on careful fs_context duplication and ownership transfer.
- `statfs` availability is approximate by design and must remain pessimistic when metadata is exhausted.
- Unfreeze validation deliberately returns success after marking the filesystem errored so VFS can unfreeze safely.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/super.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/super.h

Read coverage: complete file, 38 lines.

This small header exposes Btrfs superblock-facing helpers and declarations used outside `super.c`.

Declared API:
- `btrfs_check_options()` validates mount option state against filesystem features and mount flags.
- `btrfs_sync_fs()` implements the VFS sync callback.
- `btrfs_get_subvol_name_from_objectid()` resolves a subvolume objectid into a path-like name.
- `btrfs_set_free_space_cache_settings()` derives free-space-cache mount behavior after mount options and on-disk feature state are known.

Inline helpers:
- `btrfs_sb()` returns `struct btrfs_fs_info *` from `super_block->s_fs_info`.
- `btrfs_set_sb_rdonly()` sets `SB_RDONLY` and `BTRFS_FS_STATE_RO`.
- `btrfs_clear_sb_rdonly()` clears both the VFS readonly flag and Btrfs readonly state bit.

Integration notes:
- The readonly helpers are used by remount code to keep VFS superblock flags and Btrfs internal state synchronized.
- This header is a narrow bridge between generic VFS superblock code and Btrfs `fs_info` state.

Risk notes:
- Readonly state must be updated through these paired helpers where possible; setting only the VFS flag or only the Btrfs state bit can desynchronize mount behavior.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/super.h -->