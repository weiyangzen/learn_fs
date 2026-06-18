# Group Research: group_962_linux_stable_sources_os_linux_linux_stable_fs_btrfs_volumes_h_source_c9b54c72c3c5

Scope source: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/volumes.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/volumes.h

## Purpose

`volumes.h` is the shared declaration surface for Btrfs multi-device, chunk mapping, RAID profile, device statistics, device lookup, and block-to-device IO mapping code. It defines the core in-memory structures used by `volumes.c`, zoned support, device replace, scrub, balance, and lower-level bio submission.

## Main Concepts

- Defines Btrfs stripe constants: `BTRFS_STRIPE_LEN`, shift, and mask.
- Converts on-disk block group profile bits to internal `enum btrfs_raid_types` with compile-time static assertions.
- Defines `struct btrfs_device`, the per-device runtime state:
  - backing block device/file pointers
  - size accounting: total, disk total, used bytes, committed sizes
  - device identity: devid, uuid, devt, name
  - state bits for writable, missing, replace target, flush failures, discovered item
  - zoned info pointer
  - scrub, sysfs, statistics, allocation-state tracking
- Defines `struct btrfs_fs_devices`, the filesystem-level device set:
  - fsid and metadata_uuid handling
  - device counts, missing/open/rw devices
  - device lists and seed list
  - mount-hold lifecycle counters
  - mount/device capability flags
  - sysfs kobjects
  - chunk allocation and mirrored read policy
  - per-profile available-space cache
- Defines IO mapping structures:
  - `struct btrfs_io_stripe`
  - `struct btrfs_discard_stripe`
  - `struct btrfs_io_context`
  - `struct btrfs_chunk_map`
- Defines balancing and device lookup helper structures.
- Declares major exported routines for device scanning/opening/closing, chunk creation/removal, block mapping, balance, stats, device replace cleanup, chunk-map lookup, superblock reads, and per-profile availability.

## Important Details

- 64-bit device counters get generated getters/setters. On 32-bit SMP, seqcount protects torn reads. On 32-bit preemptible builds, preemption is disabled around direct access.
- `BTRFS_RAID_SINGLE` is special because it has no on-disk profile bit.
- `BTRFS_MAX_DEVS` and `BTRFS_MAX_DEVS_SYS_CHUNK` derive maximum stripe counts from item/system-chunk array capacity.
- `struct btrfs_io_context` carries both logical mapping and device-replace duplication state. RAID56 has special full-stripe metadata and replace-source tracking.
- `btrfs_free_chunk_map()` is refcounted and asserts the RB node is detached before freeing.
- Device stat helpers update `dev_stats_ccnt` with memory barriers so transaction-time stat persistence sees ordered values.
- `btrfs_get_per_profile_avail()` reads the cached profile estimate under `per_profile_lock` and treats `U64_MAX` as unavailable.
- `btrfs_op()` maps write and zone-append bios to `BTRFS_MAP_WRITE`, reads to `BTRFS_MAP_READ`, and warns on unexpected bio ops.

## Dependencies

This header depends on Linux block-device, bio, atomic, list, mutex, kobject, refcount, completion, rbtree, and UAPI Btrfs tree definitions. It also includes Btrfs-local `messages.h`, `extent-io-tree.h`, and `fs.h`.

## Research Notes

This file is architectural glue. Changes here affect many Btrfs subsystems because the structures encode shared invariants for device state, chunk mapping, RAID behavior, zoned support, and device statistics. The static assertions around RAID indexes and stripe size are especially important because they guard assumptions shared with on-disk formats and mapping code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/volumes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/xattr.c

## Purpose

`xattr.c` implements Btrfs extended attribute get, set, remove, list, VFS xattr handlers, Btrfs property xattrs, and inode security-label initialization.

## Main Functions

- `btrfs_getxattr()`
  - Looks up a `BTRFS_XATTR_ITEM_KEY` dir item by inode/object id and name.
  - Returns the value size when caller passes size 0.
  - Copies packed dir-item xattr data from the leaf into the caller buffer.
  - Returns `-ENODATA`, `-ERANGE`, or lookup errors as appropriate.

- `btrfs_setxattr()`
  - Requires an active transaction.
  - Enforces `BTRFS_MAX_XATTR_SIZE`.
  - Treats `value == NULL` as removal.
  - Honors `XATTR_CREATE` and `XATTR_REPLACE`.
  - Handles packed xattrs in a single item, including atomic replacement.
  - Updates inode runtime flags: sets `BTRFS_INODE_COPY_EVERYTHING` and clears `BTRFS_INODE_NO_XATTRS` on success.

- `btrfs_setxattr_trans()`
  - Starts a transaction unless one already exists in `current->journal_info`.
  - The existing-transaction path supports security modules setting xattrs during inode creation.
  - Updates inode version, ctime, and inode item after successful xattr update.

- `btrfs_listxattr()`
  - Iterates all xattr keys for the inode.
  - Walks packed `struct btrfs_dir_item` records inside each item.
  - Computes required buffer size or copies null-terminated names.
  - Returns `-ERANGE` when the caller buffer is too small.

- VFS handlers:
  - security, trusted, user, and Btrfs property namespaces are registered in `btrfs_xattr_handlers`.
  - security capability lookups use `BTRFS_INODE_NO_CAP_XATTR` as a negative cache.
  - `btrfs.*` xattrs route through property validation and `btrfs_set_prop()`.

- `btrfs_xattr_security_init()`
  - Calls `security_inode_init_security()` with `btrfs_initxattrs()`.
  - `btrfs_initxattrs()` builds full `security.*` names and writes them in a NOFS allocation context.

## Important Details

- Xattrs are stored using Btrfs dir-item packing: `struct btrfs_dir_item`, name bytes, then value bytes.
- Replacement is designed to be atomic from readers’ perspective, particularly for ACLs.
- When replacing an xattr packed with other xattrs in the same item, the code deletes only the matching dir name and then extends the item for the new value.
- Read-only roots reject set operations with `-EROFS`.
- Property xattrs can be ignored by `btrfs_ignore_prop()` after validation.
- Transaction abort is triggered when inode update fails after xattr/property mutation.

## Dependencies

This file depends on VFS xattr/security APIs, POSIX ACL xattr names, inode versioning, Btrfs transaction handling, dir-item helpers, tree locking, property validation, inode update, and extent-buffer accessors.

## Research Notes

This implementation is tightly coupled to Btrfs dir-item packing and transaction semantics. The main invariants are maximum xattr item size, correct create/replace/remove error behavior, atomic replacement visibility, and keeping inode metadata/runtime flags synchronized after successful changes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/xattr.h

## Purpose

`xattr.h` declares the Btrfs xattr API used by inode, security, and VFS integration code.

## Exports

- `btrfs_xattr_handlers`
  - VFS handler table for security, trusted, user, and Btrfs property xattrs.
- `btrfs_getxattr()`
  - Retrieve one xattr by full name.
- `btrfs_setxattr()`
  - Set/remove one xattr under an existing transaction.
- `btrfs_setxattr_trans()`
  - Set/remove one xattr while managing transaction start/end when needed.
- `btrfs_listxattr()`
  - List all xattr names on a dentry inode.
- `btrfs_xattr_security_init()`
  - Initialize security xattrs during inode creation.

## Dependencies

The header forward-declares `dentry`, `inode`, `qstr`, `xattr_handler`, and `btrfs_trans_handle`, and includes only `linux/types.h`.

## Research Notes

This is intentionally small and stable. It exposes only the xattr operations needed outside `xattr.c`, while hiding dir-item packing and handler implementation details.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/zlib.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/zlib.c

## Purpose

`zlib.c` implements the Btrfs zlib compression backend: workspace allocation, bio compression, compressed bio decompression, and single-folio decompression.

## Main Structures

- `struct workspace`
  - zlib `z_stream`
  - workspace input/output buffer
  - buffer size
  - list node for Btrfs compression workspace pooling
  - selected compression level

## Main Functions

- `zlib_get_workspace()`
  - Gets a generic Btrfs zlib workspace and records the requested level.
- `zlib_alloc_workspace()`
  - Allocates zlib deflate/inflate workspace memory.
  - Allocates a buffer sized for sectorsize or a larger s390 DFLTCC-friendly buffer.
- `zlib_free_workspace()`
  - Frees zlib workspace memory, temporary buffer, and wrapper object.
- `need_special_buffer()`
  - Detects when s390 hardware zlib acceleration benefits from a 4-page staging buffer.
- `copy_data_into_buffer()`
  - Copies filemap data into the workspace buffer for DFLTCC acceleration.
- `zlib_compress_bio()`
  - Compresses file data into a compressed bio.
  - Maps input folios or uses the workspace staging buffer.
  - Allocates compressed output folios.
  - Aborts with `-E2BIG` if compressed output is not beneficial or cannot fit.
- `zlib_decompress_bio()`
  - Inflates compressed bio folios into target pages using `btrfs_decompress_buf2page()`.
  - Supports raw deflate optimization by inspecting the zlib header and skipping Adler32 when safe.
- `zlib_decompress()`
  - Inflates a small compressed buffer into one destination folio.
  - Zero-fills any missing output on failure/short decompression.
- `btrfs_zlib_compress`
  - Advertises min, max, and default zlib compression levels.

## Important Details

- Compression uses `Z_SYNC_FLUSH` while feeding input and `Z_FINISH` to complete the stream.
- The backend gives up early if the compressed stream grows beyond the original data.
- Output folios are added directly to the compressed bio as they fill.
- Decompression validates that the expected output length was produced; otherwise it returns `-EIO`.
- NOFS-sensitive allocation appears through the broader compression path; this backend uses `GFP_NOFS` for compressed folios.
- Folio mappings are paired carefully with `kunmap_local()` and `folio_put()`.

## Dependencies

This file depends on Linux zlib/zutil APIs, folio/page-cache helpers, bio helpers, and Btrfs compression helpers from `compression.h`, inode metadata from `btrfs_inode.h`, filesystem sizing from `fs.h`, and subpage support.

## Research Notes

The zlib backend is conservative: it prioritizes correctness, bounded output, and hardware-aware buffering. Key failure modes are allocation failure, zlib stream errors, compressed output larger than input, and short decompression.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/zlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/zoned.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/zoned.c

## Purpose

`zoned.c` implements Btrfs zoned block device support. It discovers and caches zone geometry, validates zoned mount constraints, manages superblock log zones, tracks active zones, recovers block-group write pointers, enforces sequential write placement, coordinates zone append completion, finishes zones, reserves active-zone budget for metadata/system use, and supports zoned block-group reclaim/reset.

## Major Areas

### Zone Discovery and Device State

- `btrfs_get_dev_zone_info_all_devices()` loads zone information for all devices during mount.
- `btrfs_get_dev_zone_info()` allocates and populates `struct btrfs_zoned_device_info`.
  - Supports true zoned devices and regular devices with emulated conventional zones.
  - Validates zone size bounds: 4 MiB minimum and 8 GiB maximum.
  - Builds bitmaps for sequential zones, empty zones, and active zones.
  - Tracks `max_active_zones` and initializes `active_zones_left`.
  - Optionally creates a zone cache for real zoned devices.
  - Validates superblock log zone state.
- `btrfs_destroy_dev_zone_info()` and `btrfs_clone_dev_zone_info()` manage zone-info lifecycle.

### Zoned Mode Validation

- `btrfs_check_zoned_mode()` rejects zoned devices unless the filesystem has the zoned incompat flag.
- In zoned mode, all devices must have the same zone size.
- Queue limits are stacked from zoned block devices.
- Mixed block groups are rejected.
- `fs_info->zone_size`, `max_zone_append_size`, `max_extent_size`, and chunk allocation policy are configured.
- `btrfs_check_mountopts_zoned()` rejects space cache v1 and NODATACOW, and disables async discard.

### Superblock Log Zones

- Zoned devices store superblocks in log zone pairs at primary, 512 GiB, and 4 TiB mirror positions.
- `sb_write_pointer()` interprets the two-zone log state and chooses the current write pointer or latest full-zone superblock.
- `btrfs_sb_log_location_bdev()` and `btrfs_sb_log_location()` locate read/write superblock positions.
- `btrfs_advance_sb_log()` advances cached superblock log write pointers and finishes full zones.
- `btrfs_reset_sb_log_zones()` resets a mirror’s superblock log zone pair.

### Allocation Zone Selection and Reset

- `btrfs_find_allocatable_zones()` searches for empty sequential zones and avoids both zoned superblock log zones and regular superblock offsets.
- `btrfs_reset_device_zone()` resets device zones, marks them empty, and clears active-zone accounting.
- `btrfs_ensure_empty_zones()` validates allocation targets and forcibly resets non-empty sequential zones that should be free.

### Block Group Write Pointer Recovery

- `calculate_alloc_pointer()` derives an allocation pointer for conventional-zone block groups from the highest existing extent.
- `btrfs_load_zone_info()` reads each mapped device zone and derives physical position, capacity, active state, and allocation offset.
- Per-profile loaders validate and combine zone write pointers:
  - `btrfs_load_block_group_single()`
  - `btrfs_load_block_group_dup()`
  - `btrfs_load_block_group_raid1()`
  - `btrfs_load_block_group_raid0()`
  - `btrfs_load_block_group_raid10()`
- `btrfs_load_block_group_by_raid_type()` dispatches by profile and rejects unsupported RAID5/RAID6.
- `btrfs_load_block_group_zone_info()` attaches the chunk map, initializes `alloc_offset`, `zone_capacity`, `meta_write_pointer`, active-list membership, and sequential-zone flags.

Important profile constraints:
- Zoned data DUP/RAID profiles require raid-stripe-tree support.
- Mirrored profiles must have matching write pointer offsets unless degraded behavior allows missing devices.
- RAID0/RAID10 loaders reconstruct logical allocation progress from per-stripe write pointers and reject stripe disorder or multiple partial stripes.

### Sequential Data and Metadata IO

- `btrfs_calc_zone_unusable()` computes unusable space from written-but-free and capacity-shortfall regions.
- `btrfs_use_zone_append()` enables `REQ_OP_ZONE_APPEND` for normal data writes in sequential-zone block groups, excluding data relocation.
- `btrfs_record_physical_zoned()` adjusts checksum logical addresses after zone append returns the actual physical write location.
- `btrfs_finish_ordered_zoned()` splits or rewrites ordered extents when zone append caused physically non-contiguous placement.
- `btrfs_check_meta_write_pointer()` enforces metadata/system writes at `meta_write_pointer`, handles active metadata/system block-group pivoting, and returns `0`, `-EAGAIN`, or `-EBUSY`.

### Device Replace and Zone Pointer Sync

- `btrfs_zoned_issue_zeroout()` zeroes sequential-zone ranges.
- `btrfs_sync_zone_write_pointer()` advances a replacement target zone write pointer by zero-filling from the target position to the source zone write pointer.

### Active Zone Management and Zone Finish

- `btrfs_zone_activate()` activates a block group and its underlying zones while respecting per-device active-zone limits and reserved metadata/system capacity.
- `do_zone_finish()` finishes an active block group, waits for outstanding writes when needed, updates block-group allocation state to full, finishes device zones, clears special block-group references, and removes the group from the active list.
- `btrfs_zone_finish()` is the public wrapper.
- `btrfs_can_activate_zone()` checks whether active-zone budget exists for new allocation.
- `btrfs_zone_finish_endio()` finishes a block group when IO reaches the final allocatable range.
- `btrfs_schedule_zone_finish_bg()` schedules asynchronous zone finish after the last metadata extent buffer writes.

### Relocation, Reclaim, and Stats

- `btrfs_zoned_reserve_data_reloc_bg()` reserves or creates a data relocation block group and moves it into the relocation space-info subgroup.
- `btrfs_zoned_release_data_reloc_bg()` releases the relocation flag once all relocation extents are written.
- `btrfs_zone_finish_one_bg()` chooses an active data block group with least remaining space and finishes it.
- `btrfs_zoned_activate_one_bg()` tries to activate a metadata/system block group, optionally finishing another group first.
- `btrfs_check_active_zone_reservation()` reserves active-zone slots for metadata, tree-log, and system block groups.
- `btrfs_reset_unused_block_groups()` resets fully zone-unusable unused block groups so they can be reused without deleting/recreating chunks.
- `btrfs_show_zoned_stats()` emits active block group, reclaim, relocation, tree-log, and per-active-zone statistics.

## Important Invariants

- Zoned filesystems cannot use mixed block groups, NODATACOW, or space cache v1.
- Block group length and allocation targets must be aligned to zone size.
- Sequential zones must be written in order; metadata uses `meta_write_pointer`, while data can use zone append.
- Active-zone limits are tracked per device and can reserve capacity for metadata/system needs.
- Superblock log zones are special allocation exclusions.
- Missing/failing devices are represented during write-pointer recovery, but unrecoverable mismatches become mount-time errors or make block groups unallocatable.
- Zone finish transitions an active block group to full and clears active accounting on underlying device zones.

## Dependencies

This file depends on Linux zoned block APIs, zone management operations, queue limits, Btrfs chunk maps, block groups, device replace, transactions, sysfs, ordered extents, extent buffers, raid-stripe-tree assumptions, and filesystem-wide lock ordering.

## Research Notes

`zoned.c` is a central policy implementation for making Btrfs copy-on-write allocation compatible with sequential-write devices. The code bridges physical zone constraints with logical Btrfs block groups. Most complexity comes from recovering write pointers across RAID profiles, preserving metadata ordering, handling zone append relocation of physical writes, and managing scarce active-zone resources.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/zoned.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/zoned.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/zoned.h

## Purpose

`zoned.h` declares the Btrfs zoned-mode API and provides no-op fallbacks when `CONFIG_BLK_DEV_ZONED` is disabled. It also defines the per-device zoned metadata structure and lightweight helpers used throughout Btrfs.

## Main Structure

- `struct btrfs_zoned_device_info`
  - `zone_size` and `zone_size_shift`
  - `nr_zones`
  - `max_active_zones`
  - `reserved_active_zones`
  - `active_zones_left`
  - bitmaps for sequential, empty, and active zones
  - optional `zone_cache`
  - cached superblock log zones

## Exported Zoned APIs

When zoned block support is enabled, the header declares functions for:

- device zone info load/clone/destroy
- zoned mode and mount option checks
- superblock log location, advancement, and reset
- allocatable-zone search
- zone reset and empty-zone validation
- block-group zone info loading and unusable-space calculation
- zone append decision and physical-position recording
- metadata write-pointer validation
- zeroout and dev-replace write-pointer synchronization
- active-zone activation/finish/accounting
- data relocation block-group reservation/release
- zone cache freeing
- reclaim decisions
- unused block-group reset
- zoned stats display

## Disabled-Config Behavior

When `CONFIG_BLK_DEV_ZONED` is disabled:

- Most APIs become no-ops or return regular filesystem behavior.
- `btrfs_check_zoned_mode()` rejects a filesystem that is actually marked zoned with `-EOPNOTSUPP`.
- Zone append is disabled.
- zone reset/zeroout/sync helpers return unsupported where appropriate.
- activation/finish helpers act as if all block groups are active and finishable.

## Inline Helpers

- `btrfs_dev_is_sequential()` checks if a device position is in a sequential zone.
- `btrfs_dev_is_empty_zone()` checks the empty-zone bitmap, treating non-zoned devices as empty.
- `btrfs_dev_set_empty_zone_bit()`, `btrfs_dev_set_zone_empty()`, and `btrfs_dev_clear_zone_empty()` update empty-zone state.
- `btrfs_check_device_zone_type()` allows regular devices in zoned filesystems via emulation, but rejects host-managed zoned devices for non-zoned filesystems.
- `btrfs_check_super_location()` ensures superblocks on zoned devices are not placed in sequential-write-required zones.
- `btrfs_can_zone_reset()` validates sequential-zone and alignment requirements for resets.
- `btrfs_zoned_meta_io_lock()` and unlock gate metadata IO serialization only in zoned mode.
- `btrfs_clear_treelog_bg()` clears the tracked tree-log block group.
- `btrfs_zoned_data_reloc_lock()` and unlock serialize zoned data relocation IO.
- `btrfs_zoned_bg_is_full()` checks whether allocation reached zone capacity.

## Dependencies

The header depends on Linux block/zoned block definitions, atomics, spinlocks, mutexes, seq_file, and Btrfs local headers for messages, volumes, disk IO, block groups, and inode helpers.

## Research Notes

This header is the compatibility boundary for zoned support. It lets most call sites use zoned helpers unconditionally while preserving clean behavior in kernels built without zoned block support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/zoned.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/zstd.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/zstd.c

## Purpose

`zstd.c` implements the Btrfs zstd compression backend, including zstd parameter limiting, per-level workspace management, delayed workspace reclaim, bio compression, compressed bio decompression, and single-folio decompression.

## Main Constants

- `ZSTD_BTRFS_MAX_WINDOWLOG` limits the zstd window to 128 KiB.
- `ZSTD_BTRFS_MAX_INPUT` is derived from the max window.
- Supported levels range from `-15` to `15`.
- Default level is `3`.
- Workspace reclaim timeout is `307 * HZ`, intentionally offset from typical transaction timing.

## Workspace Management

- `struct workspace`
  - compression memory buffer and size
  - sectorsize temporary output buffer
  - actual workspace level and requested level
  - last-used timestamp
  - idle/LRU list nodes
  - zstd input/output buffers
  - cached zstd parameters

- `struct zstd_workspace_manager`
  - spinlock
  - global LRU list
  - per-level idle workspace lists
  - bitmap of active levels
  - wait queue
  - reclaim timer

- `zstd_calc_ws_mem_sizes()`
  - Computes monotonic workspace memory requirements so higher-level workspaces can satisfy lower-level requests.
  - Negative fast levels share level-1 sizing.

- `zstd_alloc_workspace_manager()`
  - Initializes manager state and preallocates a max-level workspace when possible.

- `zstd_get_workspace()`
  - Finds an idle workspace at the requested level or higher.
  - Allocates a new workspace under NOFS context.
  - If allocation fails, waits for a max-level workspace to become available.

- `zstd_put_workspace()`
  - Returns a workspace to idle lists.
  - Updates LRU state only for same-level use.
  - Keeps one max-level workspace protected for forward progress.
  - Wakes waiters when max-level workspace returns.

- `zstd_reclaim_timer_fn()`
  - Frees idle workspaces that have aged past the reclaim interval.

## Compression and Decompression

- `zstd_get_btrfs_parameters()` clamps zstd window size to Btrfs’s maximum.
- `zstd_compress_bio()`
  - Initializes a zstd compression stream for the requested level and input length.
  - Maps file folios as input.
  - Writes compressed output into allocated compressed folios.
  - Aborts with `-E2BIG` if compression is not beneficial or output reaches input size.
- `zstd_decompress_bio()`
  - Streams compressed bio folios into the workspace buffer.
  - Copies decompressed ranges into target pages via `btrfs_decompress_buf2page()`.
  - Detects zstd stream errors and short/missing input.
- `zstd_decompress()`
  - Decompresses one small buffer into a destination folio.
  - Zero-fills missing output and returns `-EIO` on short output or stream error.
- `btrfs_zstd_compress`
  - Advertises min, max, and default zstd levels.

## Important Details

- The workspace manager deliberately allows larger workspaces to satisfy smaller-level requests.
- The LRU timestamp is not refreshed when a larger workspace temporarily serves a lower-level request, allowing future reclaim in favor of better-sized workspaces.
- The max-level workspace acts as a forward-progress reserve under memory pressure.
- Compression and decompression maintain local folio mappings and release them on all exit paths.
- Like the zlib backend, this code rejects compressed output that is not smaller than input.

## Dependencies

This file depends on Linux zstd APIs, bitmap/list/timer/waitqueue primitives, folio and bio helpers, Btrfs compression helpers, inode/root metadata, and superblock-to-fs-info accessors.

## Research Notes

`zstd.c` has more internal resource-management logic than `zlib.c` because zstd workspace size varies substantially by compression level. The core behavior is still the standard Btrfs compression backend contract: allocate reusable workspaces, compress filemap input into compressed bios, decompress bios to pages, and fail safely on expansion or malformed streams.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/zstd.c -->