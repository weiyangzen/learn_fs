# Group Research: group_961_linux_stable_sources_os_linux_linux_stable_fs_btrfs_volumes_c_6459a0dfad14

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/volumes.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/volumes.c

## Purpose

`volumes.c` is the Btrfs multi-device, chunk, RAID profile, balance, and logical-to-physical mapping core. It owns the in-memory device registry, block device scanning/open/close, seed/sprout handling, device add/remove/grow/shrink, chunk allocation/removal, balance relocation, chunk-map lookup, I/O stripe mapping, degraded-mount checks, persistent device stats, and mount-time verification of chunk/device-extent consistency.

The file was read completely: 8,868 lines.

## Main Data And Policy Tables

The central RAID policy table is `btrfs_raid_array[]`, indexed by `enum btrfs_raid_types`. It defines each profile’s stripe geometry, min/max device counts, redundancy, parity count, allocation increment, on-disk block-group flag, printable name, and minimum-device error code. Helpers such as `btrfs_bg_flags_to_raid_index()`, `btrfs_bg_type_to_raid_name()`, `btrfs_nr_parity_stripes()`, `btrfs_bg_type_to_factor()`, and `btrfs_describe_block_groups()` expose these profile properties to allocation, balance, sysfs/ioctl reporting, and error messages.

The global `fs_uuids` list, protected by `uuid_mutex`, tracks discovered `btrfs_fs_devices` sets. Per-filesystem `device_list_mutex`, `chunk_mutex`, `balance_mutex`, and RCU protect different layers of device and chunk mutation. The file documents lock ordering and exclusive operations up front: balance, add, remove, replace, and resize cannot run concurrently.

## Device Discovery And Lifetime

Device discovery starts with `btrfs_scan_one_device()`, which opens a block device read-only, reads the primary superblock with `btrfs_read_disk_super()`, and registers it through `device_list_add()` unless it is a single non-seed device that can be skipped outside mount. Registration handles metadata UUIDs, temporary fsids for single-device same-fsid collisions, stale-device cleanup, generation ordering, path replacement, missing-device revival, and mounted-device duplicate rejection.

Opening and closing are split between `btrfs_open_devices()`, `open_fs_devices()`, `btrfs_open_one_device()`, `btrfs_close_devices()`, and `btrfs_close_one_device()`. Opening validates devid/UUID against the disk superblock, sets writeability, tracks rotating/discardable properties, installs block-device pointers, and initializes read policy. Closing syncs writable devices, invalidates block devices, clears write/missing/replace state, destroys zoned metadata, releases allocation-state trees, and resets transient flush-failure state so a later mount can retry.

`btrfs_free_stale_devices()` and `btrfs_forget_devices()` remove unmounted stale device records. `btrfs_free_extra_devids()` prunes scanned devices that were not found in filesystem metadata after the chunk tree is read.

## Device Operations

`btrfs_init_new_device()` implements device add. It opens the target for write, checks zoned compatibility and minimum size, allocates a `btrfs_device`, initializes zone info, starts a transaction, links the device into allocation/device lists, updates superblock total bytes and device count, adds sysfs state, inserts a chunk-tree device item, and commits. For seeding filesystems it performs sprout setup: clones seed devices, generates a new fsid, creates initial writable metadata/system chunks through `init_first_rw_device()`, stores seed generations, updates sysfs fsid, and relocates system chunks.

`btrfs_rm_device()` removes a device after checking extent-tree-v2 support, RAID minimum-device constraints, active swapfile pins, replace-target state, and writable-device availability. It shrinks the device to zero, removes its device item, removes it from lists and sysfs, updates superblock device count, scratches old superblocks, returns the block-device file to the caller for final release, and frees private seed device sets when needed.

Resize paths are `btrfs_grow_device()` and `btrfs_shrink_device()`. Growing updates total bytes, free chunk space, per-profile availability, and the on-disk device item. Shrinking first adjusts in-memory size, commits pending chunk allocations if necessary, relocates all dev extents beyond the new size, clears allocation-state bits past the end, writes the new disk size, and rolls back in-memory counters on failure.

Device replace cleanup is handled by `btrfs_rm_dev_replace_remove_srcdev()`, `btrfs_rm_dev_replace_free_srcdev()`, and `btrfs_destroy_dev_replace_tgtdev()`, which carefully update list counts, active superblock device, sysfs, and RCU lifetime.

## Free-Space And Chunk Allocation

Device extent allocation uses `find_free_dev_extent()`, which scans the committed device tree for holes, then validates candidates against pending chunk allocations in `device->alloc_state`. `btrfs_first_pending_extent()` and `btrfs_find_hole_in_pending_extents()` prevent double allocation against chunks allocated in the current transaction but not yet visible in the committed dev tree. Zoned allocation adds `dev_extent_hole_check_zoned()`, requiring zone-aligned, allocatable, empty ranges.

Chunk allocation is driven by `btrfs_create_chunk()`. It initializes an `alloc_chunk_ctl` from RAID attributes and regular/zoned policy, gathers candidate writable devices with usable holes, sorts by largest available space, rounds device count to the profile increment, decides stripe and chunk sizes, allocates a `btrfs_chunk_map`, inserts it into the mapping tree, creates a block group, updates device bytes-used, adjusts free chunk space, sets RAID incompat flags, and refreshes per-profile availability.

`btrfs_chunk_alloc_add_chunk_item()` persists a newly created chunk into the chunk tree and, for system chunks, the superblock system chunk array. It updates all participating device items and writes stripe devid/offset/UUID data into the chunk item. The function is deliberately tied to `chunk_mutex` to avoid races with chunk-tree updates, superblock system array updates, and device replace finalization.

`btrfs_update_per_profile_avail()` estimates allocatable bytes for each RAID profile using virtual chunks on non-zoned filesystems. Zoned filesystems currently set per-profile availability to `U64_MAX` because the simple estimation model is not accurate there.

## Chunk Removal, Relocation, And Balance

`btrfs_remove_chunk()` removes a logical chunk by deleting device extents, updating device bytes-used, deleting the chunk item, removing the system-array entry if needed, refreshing per-profile availability, releasing reserved chunk metadata, and removing the associated block group. It retries system chunk allocation when deletion needs system metadata space and the existing system block groups cannot satisfy it.

Relocation is exposed through `btrfs_relocate_chunk()`, which pauses scrub, relocates the block group, and either finishes via `btrfs_remove_chunk()` or leaves metadata-remap chunks to remap-tree logic. `btrfs_relocate_sys_chunks()` scans system chunks backwards and relocates them, retrying once on ENOSPC.

Balance state is persisted in a `BTRFS_BALANCE_OBJECTID` temporary item via `insert_balance_item()` and removed by `del_balance_item()`. `btrfs_recover_balance()` reconstructs paused balance control at mount. `btrfs_balance()` validates mixed data/metadata constraints, conversion targets, device counts, and redundancy reductions; starts the exclusive operation; runs `__btrfs_balance()`; handles pause/cancel/error reporting; updates ioctl output; and resets state when not paused.

`__btrfs_balance()` does a counting pass and an execution pass over chunk items in reverse order. It applies profile, usage, devid, physical range, virtual range, stripe-count, soft-convert, and limit filters through `should_balance_chunk()`. Matching chunks are relocated, active swapfile chunks are skipped, ENOSPC is accumulated, and metadata-remap chunks are processed later through `balance_remap_chunks()` after CoWing the remap tree.

## Mapping Tree And Logical-To-Physical I/O

The mapping tree is an rb-tree of refcounted `btrfs_chunk_map` objects protected by `mapping_tree_lock`. `btrfs_add_chunk_map()` inserts a map and marks participating device ranges `CHUNK_ALLOCATED`; `btrfs_remove_chunk_map()` removes it and clears allocation bits; `btrfs_find_chunk_map()` and `btrfs_get_chunk_map()` resolve logical ranges and validate coverage.

`btrfs_map_block()` is the main logical-to-physical mapper. It resolves remapped chunks, bounds I/O length at chunk, stripe, or RAID56 full-stripe boundaries, determines whether RAID stripe tree offsets are needed, locks device-replace state, and maps according to profile:

- RAID0 and single distribute by stripe number.
- RAID1/RAID1C3/RAID1C4 select a live mirror for reads and all mirrors for writes.
- DUP maps duplicate stripes, with read mirror selection.
- RAID10 maps within sub-stripe mirror groups.
- RAID5/RAID6 reads map direct data stripes; writes and repair/rebuild map full stripe sets with data stripes ordered before parity.

For simple single-device mappings, it can fill a stack `btrfs_io_stripe` instead of allocating a `btrfs_io_context`. Otherwise it allocates a `bioc`, fills stripes, records mirror/full-stripe metadata, and duplicates non-read writes to the device-replace target when needed through `handle_ops_on_dev_replace()`.

Read mirror selection uses `find_live_mirror()`, defaulting to PID-based distribution and avoiding the source device of an active replace when possible. Experimental builds add devid-preferred and round-robin read policies.

`btrfs_map_discard()` maps discard ranges, excluding replace targets and rejecting RAID56. `btrfs_map_repair_block()` maps read-repair/scrub writes to a single target stripe, with special RAID56 handling through `map_raid56_repair_block()`.

## Mount-Time Chunk And Device Loading

`btrfs_read_sys_array()` reads system chunks from the superblock system chunk array using a dummy extent buffer. `btrfs_read_chunk_tree()` then scans the chunk tree at mount, first reading device items with `read_one_dev()` and then chunk items with `read_one_chunk()`. Device item loading handles seed fsids via `open_seed_devices()`, missing devices in degraded mode, generation checks for seed devices, device size sanity, writable free-space accounting, and `ITEM_FOUND`/`IN_FS_METADATA` state.

`read_one_chunk()` builds chunk maps from on-disk chunk items, rejects 32-bit metadata beyond addressable limits, fills stripes, resolves missing devices, marks participating devices as in metadata, and inserts maps into the mapping tree.

`btrfs_check_rw_degradable()` walks all chunk maps and verifies missing/failed devices do not exceed the profile’s tolerated barrier failures before allowing writable degraded operation.

## Device Stats And Verification

Persistent device stats are initialized by `btrfs_init_dev_stats()` and `btrfs_device_init_dev_stats()`, written during transaction commit by `btrfs_run_dev_stats()`, updated through `update_dev_stat_item()`, printed by `btrfs_dev_stat_inc_and_print()`/`btrfs_dev_stat_print_on_load()`, and exposed/reset via `btrfs_get_dev_stats()`. The commit path uses an RCU precheck and memory barriers around `dev_stats_ccnt` so healthy filesystems avoid blocking on `device_list_mutex` during transaction commit.

`btrfs_commit_device_sizes()` finalizes delayed device size/bytes-used updates during commit.

`btrfs_verify_dev_extents()` scans the device tree to ensure every dev extent maps to a chunk stripe, dev extents do not overlap, lengths match computed stripe lengths, extents stay within device boundaries, and zoned extents are zone-aligned. `verify_chunk_dev_extent_mapping()` then ensures every chunk stripe had a corresponding dev extent. `btrfs_verify_dev_items()` detects registered devices not represented by chunk-tree device items and tells users to forget stale devices before mount.

## Important Invariants

- `uuid_mutex` protects global filesystem-device registration and mount-time open/close assembly.
- `device_list_mutex` protects device-list mutation and some long read-side operations.
- `chunk_mutex` serializes chunk allocation/removal, device allocation-state updates, system chunk array updates, and device item updates that can race device replace.
- Chunk allocation must account for committed dev extents plus pending in-memory allocated ranges.
- Device replace target devices are excluded from normal allocation and receive duplicated writes only through replace-specific paths.
- Seed devices remain read-only; sprouting creates a new writable fsid and keeps seed device sets linked separately.
- Balance persists enough state to survive interruption and resume, but paused state keeps the exclusive operation owned by balance.
- RAID56 write mapping returns full stripe sets; repair mapping narrows those full maps back to the failing data stripe.
- Mount-time degraded acceptance is profile-aware and checks every loaded chunk map.

## Risk And Test Focus

High-risk areas are lock ordering among `uuid_mutex`, `device_list_mutex`, `chunk_mutex`, and transaction paths; allocation correctness with pending chunks; zoned hole validation; device replace duplication; seed/sprout fsid and generation handling; RAID56 full-stripe mapping; balance pause/cancel/resume persistence; and stale scanned-device handling.

Focused tests should cover multi-device mount with missing devices, degraded read-write admission, duplicate scan paths, metadata UUID and temp-fsid cases, add/remove/grow/shrink rollback, seed-to-sprout conversion, chunk allocation on regular and zoned devices, balance filters and resume, RAID0/1/10/5/6 mapping boundaries, discard mapping, repair mapping, device replace writes, persistent dev stats reset/writeback, and mount rejection for inconsistent dev extent/chunk mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/volumes.c -->