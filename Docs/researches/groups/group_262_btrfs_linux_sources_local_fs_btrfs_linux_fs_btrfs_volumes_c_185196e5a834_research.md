# Group Research: group_262_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_volumes_c_185196e5a834

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/local-fs/btrfs-linux/fs/btrfs/volumes.c` (8,868 lines, 249,427 bytes)

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/volumes.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/volumes.c

This file implements Btrfs volume management: global filesystem/device registration, device open/close and mount-time assembly, device add/remove/resize, seeding and sprout handling, balance and chunk relocation orchestration, chunk allocation and chunk-map lifetime, logical-to-physical mapping for all profiles, mount-time chunk/device tree reconstruction, persistent device statistics, device extent verification, and zoned/repair mapping helpers.

Primary responsibilities:
- Defines RAID profile attributes in `btrfs_raid_array[]`, including device constraints, copy/parity counts, tolerated failures, names, and block-group flags.
- Maintains the global `fs_uuids` registry under `uuid_mutex` and per-filesystem device lists under `device_list_mutex`.
- Scans and registers block devices from superblocks, handles stale registrations, duplicate paths, temp-fsid single-device cases, metadata UUIDs, missing devices, and seed devices.
- Opens, closes, clones, frees, and resets `btrfs_fs_devices` and `btrfs_device` objects.
- Adds, removes, grows, and shrinks devices while keeping superblock totals, chunk tree device items, sysfs entries, allocation lists, writable-device counts, and free chunk space coherent.
- Implements balance state persistence/recovery/cancel/pause and the main balance loop over chunk items.
- Allocates and removes chunks, device extents, chunk items, system chunk array entries, block groups, and in-memory chunk maps.
- Converts logical block ranges into physical device stripes for single, DUP, RAID0, RAID1/1C3/1C4, RAID10, RAID5, and RAID6, including dev-replace duplication and read-mirror selection.
- Rebuilds the in-memory device/chunk mapping tree from on-disk device items, chunk items, and the superblock system chunk array during mount.
- Verifies chunk-to-device-extent consistency before writable use.

Core data and locking model:
- `uuid_mutex` protects the global `fs_uuids` list, high-level `fs_devices` counters, seeding/sprout structure changes, device registration, and mount/open/close assembly.
- `fs_devices->device_list_mutex` protects updates to `fs_devices->devices`, with RCU used for read-only traversals in selected paths.
- `fs_info->chunk_mutex` serializes chunk allocation/removal, device allocation state bits, per-profile availability updates, system chunk array changes, and transaction post-commit device update list membership.
- `fs_info->mapping_tree_lock` protects the rb-tree of `btrfs_chunk_map` records. Each chunk map carries its own refcount; callers acquiring maps must release them with `btrfs_free_chunk_map()`.
- `fs_info->balance_mutex`, `balance_lock`, `balance_pause_req`, `balance_cancel_req`, and exclusive-op state coordinate balance lifecycle.
- Device path strings use RCU (`device->name`), allowing path replacement without invalidating concurrent readers.

RAID/profile helpers:
- `btrfs_bg_flags_to_raid_index()`, `btrfs_bg_type_to_raid_name()`, `btrfs_nr_parity_stripes()`, `btrfs_bg_type_to_factor()`, and `btrfs_describe_block_groups()` translate block-group flags to RAID attributes and user/debug text.
- `alloc_profile_is_valid()` validates that allocation profiles contain only one reduced profile bit.
- `validate_convert_profile()` enforces balance conversion targets against profiles allowed by currently writable device count.
- `btrfs_check_raid_min_devices()` verifies that removing a device would not violate any active profile’s minimum device count.

Device registry and scanning:
- `alloc_fs_devices()` creates an unlinked `btrfs_fs_devices` object and initializes device, allocation, seed, and fs-list heads.
- `device_list_add()` is the central registration path after a superblock is read. It finds or creates the `fs_devices` object, handles metadata UUIDs, temp-fsid single-device mounts, duplicate generation handling, missing-device path replacement, stale path replacement, and `fs_devices->total_devices`.
- `find_fsid_by_device()` resolves fsid-vs-devt conflicts for temp-fsid support while rejecting unsupported multi-device or seeding cases.
- `btrfs_scan_one_device()` performs non-exclusive read-only scanning, optionally skips ordinary single non-seed devices outside mount context, registers multi-device/seed devices, and frees stale records for the same device number.
- `btrfs_free_stale_devices()` removes unmounted, unheld stale devices and frees empty `fs_devices` records.
- `btrfs_forget_devices()` exposes stale-device removal by `dev_t`.
- `btrfs_get_dev_args_from_path()` reads a device superblock and fills lookup arguments for ioctl/device operations; `"missing"` is handled as a special selector.
- `btrfs_find_device_by_devspec()` resolves a device either by devid or by reading the path’s superblock.

Device open/close lifecycle:
- `btrfs_get_bdev_and_sb()` opens a block device, optionally sets the Btrfs block size, invalidates cache, and reads a disk superblock.
- `btrfs_open_one_device()` validates devid and device UUID against the on-disk superblock, sets writable/seeding/rotational/discardable state, updates `devt`, opens the bdev, and links writable devices into `alloc_list`.
- `open_fs_devices()` opens all devices in one `fs_devices`, selects `latest_dev`, initializes read policy, and counts open/writable devices.
- `btrfs_open_devices()` sorts devices by devid and supports nested opens by incrementing `fs_devices->opened`.
- `btrfs_close_one_device()`, `close_fs_devices()`, and `btrfs_close_devices()` flush/invalidate writable bdevs, reset per-mount state, destroy zone info, remove allocation-list membership, close seed device lists, and free single-device stale records where possible.
- `btrfs_free_extra_devids()` removes scanned devices that were not found in the filesystem metadata after reading the system/chunk trees.

Seeding and sprout handling:
- `btrfs_init_sprout()` creates a private seed-device copy and preserves the original seed fs_devices in `fs_uuids`.
- `btrfs_setup_sprout()` moves existing seed devices into a private seed list, generates a new fsid/metadata UUID for the sprouted writable filesystem, and clears the seeding super flag.
- `btrfs_finish_sprout()` records expected seed-device generation in device items.
- `btrfs_init_new_device()` handles the special add-device path for seeding filesystems: it locks `s_umount` and `uuid_mutex`, initializes sprout state, creates first writable metadata/system chunks through `init_first_rw_device()`, relocates system chunks after commit, and updates sysfs fsid state.
- `open_seed_devices()` opens or constructs private seed fs_devices when device items reference a different fsid during mount.

Device add/remove/resize:
- `btrfs_init_new_device()` adds a new writable device to a mounted filesystem. It validates zone compatibility and size, initializes `btrfs_device`, adds it to device and allocation lists, updates super totals and `free_chunk_space`, creates sysfs state, inserts the chunk-tree device item, commits, forgets stale registrations for the same devt, and updates device ctime/mtime for blkid/udev.
- `btrfs_rm_device()` removes a device after checking extent-tree-v2 unsupported state, RAID minimums, swapfile pins, replace target state, and last-writable-device constraints. It relocates/shrinks all extents off the device, removes the device item, detaches it from lists, adjusts super `num_devices`, scratches old superblocks, and returns the bdev file to the caller for final release.
- `btrfs_grow_device()` increases a writable device size, updates super `total_bytes`, `total_rw_bytes`, free chunk space, disk/total bytes, post-commit device update list, and the on-disk device item.
- `btrfs_shrink_device()` reduces a device size by first lowering in-memory capacity, committing pending allocations if necessary, relocating any device extents beyond the new boundary, clearing allocation state bits beyond the new size, updating disk size and super totals, and rolling back in-memory totals if any step fails.
- Device replace integration includes `btrfs_rm_dev_replace_remove_srcdev()`, `btrfs_rm_dev_replace_free_srcdev()`, and `btrfs_destroy_dev_replace_tgtdev()`, which remove or destroy source/target devices while preserving device-list and active-bdev invariants.

Device extents and free-space search:
- `find_free_dev_extent()` scans the committed device tree for holes on a device, accounts for pending chunk allocations in `device->alloc_state`, skips reserved ranges, and applies zoned constraints through `dev_extent_hole_check_zoned()`.
- `btrfs_first_pending_extent()` and `btrfs_find_hole_in_pending_extents()` filter candidate holes against in-memory pending allocations.
- `btrfs_free_dev_extent()` deletes a device extent item and marks the transaction as having freed block groups.
- `btrfs_remove_dev_extents()` deletes all device extents belonging to a chunk map, updates each device’s bytes-used count and free chunk space, and queues device-size updates for transaction commit.

Chunk removal and relocation integration:
- `btrfs_find_chunk_map_nolock()`, `btrfs_find_chunk_map()`, and `btrfs_get_chunk_map()` look up chunk maps in the in-memory rb-tree, including overlap lookups used by iteration.
- `btrfs_remove_chunk()` removes a chunk in phases: delete device extents, lock `chunk_mutex`, reserve system metadata, update device items, delete the chunk item, optionally allocate a replacement system chunk on `-ENOSPC`, delete the superblock system chunk array entry for system chunks, update per-profile availability, release reserved chunk metadata, and remove the block group.
- `btrfs_relocate_chunk()` runs block-group relocation, handles remap-tree relocation completion specially, and then calls `btrfs_relocate_chunk_finish()` to delete the old chunk.
- `btrfs_relocate_sys_chunks()` relocates all system chunks, retrying once for `-ENOSPC`.
- `btrfs_may_alloc_data_chunk()` forces an empty data chunk before relocating the only data chunk so balance/shrink does not accidentally lose the desired data profile.

Balance:
- Balance parameters are persisted with `insert_balance_item()` and removed with `del_balance_item()`.
- `btrfs_recover_balance()` reconstructs `balance_ctl` from the temporary balance item at mount and leaves the exclusive operation paused for user or rw-remount action.
- `btrfs_balance()` validates mixed data/metadata requirements, target profiles, device count constraints, and redundancy-reduction rules, persists the balance item, publishes `fs_info->balance_ctl`, runs `__btrfs_balance()`, and handles pause/cancel/completion cleanup.
- `__btrfs_balance()` first counts expected chunks, then walks chunk items backward, applies filters, optionally reserves an extra data chunk, relocates matching chunks, tracks `-ENOSPC`, and separately processes `METADATA_REMAP` chunks through the remap tree.
- Filters include profile, usage/usage range, devid, physical device range, logical range, stripe count, soft-convert, and limit/limit range.
- `balance_remap_chunks()` makes remap block groups read-only, COWs the remap tree, and marks unused block groups for later cleanup where applicable.
- `btrfs_pause_balance()`, `btrfs_cancel_balance()`, and `btrfs_resume_balance_async()` coordinate state transitions with wait queues and exclusive-op state.

Chunk allocation:
- `btrfs_update_per_profile_avail()` estimates allocatable space per RAID profile using virtual chunk allocation, except zoned filesystems where it reports `U64_MAX` because availability depends on zone constraints.
- `init_alloc_chunk_ctl()` derives allocation geometry from `btrfs_raid_array[]` and policy-specific constraints.
- `gather_device_info()` enumerates writable allocation candidates, checks metadata membership and replace-target state, finds a usable device hole, and sorts devices by max and total availability.
- `decide_stripe_size_regular()` and `decide_stripe_size_zoned()` compute stripe count, stripe size, and logical chunk size while respecting max chunk size, system chunk device caps, RAID increments, stripe alignment, and zone size.
- `btrfs_create_chunk()` validates the requested profile, initializes allocation control, gathers device info, decides stripe geometry, allocates a `btrfs_chunk_map`, adds it to the mapping tree, creates the block group, updates device bytes-used, decreases free chunk space, sets RAID incompat flags, and updates per-profile availability.
- `btrfs_chunk_alloc_add_chunk_item()` persists a newly created chunk: updates device items, builds the on-disk chunk item stripes, inserts it into the chunk tree, marks the block group as having its chunk item inserted, and copies system chunks into the superblock system chunk array.
- `init_first_rw_device()` creates initial metadata and system chunks during sprout setup before full block-group item insertion is possible.

Chunk map lifecycle:
- `btrfs_alloc_chunk_map()` allocates variable-sized chunk maps with a refcount and cleared rb node.
- `btrfs_add_chunk_map()` inserts a map into the mapping tree, marks corresponding device allocation state as `CHUNK_ALLOCATED`, and clears `CHUNK_TRIMMED`.
- `btrfs_remove_chunk_map()` removes a map from the rb-tree, clears device allocation state, and drops the tree reference.
- `btrfs_mapping_tree_free()` releases all maps at teardown.
- `chunk_map_device_set_bits()` and `btrfs_chunk_map_device_clear_bits()` update each stripe’s `device->alloc_state` range.

Logical-to-physical mapping:
- `btrfs_map_block()` is the central mapper. It looks up the chunk map, applies remap-tree translation when the chunk is marked remapped, clamps length to chunk/stripe/full-stripe boundaries, chooses the correct profile mapper, handles dev-replace synchronization, optionally returns a stack `btrfs_io_stripe` for single-device I/O, or allocates a `btrfs_io_context`.
- `map_blocks_raid0()`, `map_blocks_raid1()`, `map_blocks_dup()`, `map_blocks_raid10()`, `map_blocks_raid56_read()`, `map_blocks_raid56_write()`, and `map_blocks_single()` implement per-profile stripe index, stripe number, mirror number, and returned-stripe count calculations.
- RAID56 writes and repair-style mappings return full stripes ordered as data stripes followed by parity, with `full_stripe_logical` recorded for RAID56 parity code.
- `handle_ops_on_dev_replace()` duplicates non-read writes from a replace source stripe to the target device, increases tolerated write errors for the extra stripe, and handles DUP read-mirror queries specially.
- `find_live_mirror()` selects a readable RAID1/RAID10 mirror based on read policy, avoids missing devices, and prefers avoiding the device-replace source when configured.
- Experimental read policies include fixed devid preference and round-robin based on total read sectors and minimum contiguous read size.
- `btrfs_map_discard()` maps discard ranges to physical stripes for non-RAID56 profiles, accounting for RAID0/RAID10 stripe distribution and mirrored/DUP full-stripe discard behavior.
- `btrfs_map_repair_block()` maps read-repair or scrub repair writes to exactly one target stripe; for RAID56 it reduces the full-stripe mapping to the data stripe containing the logical address.

Mount-time reconstruction:
- `btrfs_read_sys_array()` parses the superblock system chunk array through dummy extent-buffer accessors and seeds system chunk maps before the chunk tree is readable.
- `btrfs_read_chunk_tree()` walks device items and chunk items at mount, with chunk-tree locking skipped because the filesystem is not yet open. It reads all device items before chunk items, opens seed devices as needed, constructs missing-device placeholders when degraded mount is allowed, fills device fields, and validates super `num_devices` and total byte accounting.
- `read_one_dev()` validates and fills a `btrfs_device` from a chunk-tree device item, moves missing seed devices to the right fs_devices list, enforces seed generation, checks bdev capacity, marks `ITEM_FOUND` and `IN_FS_METADATA`, and contributes writable free space.
- `read_one_chunk()` constructs a `btrfs_chunk_map` from a chunk item, validates 32-bit metadata address limits when relevant, resolves each stripe’s device or missing placeholder, sets `IN_FS_METADATA`, calculates stripe size, and inserts the map.
- `btrfs_init_devices_late()` attaches `fs_info` to all devices after roots/devices are available and initializes zone info for seed devices.
- `btrfs_check_rw_degradable()` verifies that every chunk has no more missing/flush-failed stripes than its profile tolerates before writable degraded mount.
- `btrfs_verify_dev_items()` detects registered devices that were not found in chunk-tree device items and advises unregistering them before mount.

Persistent device stats:
- `btrfs_init_dev_stats()` and `btrfs_device_init_dev_stats()` load per-device persistent error counters from the device tree or initialize them to zero.
- `btrfs_run_dev_stats()` writes changed stats during transaction commit. It first scans with RCU to avoid taking `device_list_mutex` in the common no-update case, then uses memory barriers paired with stat updates before writing on-disk items.
- `btrfs_get_dev_stats()` serves ioctl reads and optional reset of device stats.
- `btrfs_dev_stat_inc_and_print()` and `btrfs_dev_stat_print_on_load()` report write/read/flush/corruption/generation error counters.
- `btrfs_commit_device_sizes()` finalizes delayed per-device size/bytes-used updates during transaction commit.

Verification and repair helpers:
- `btrfs_verify_dev_extents()` walks the device tree and verifies every device extent has a corresponding chunk stripe, does not overlap the previous extent on the same device, stays within device boundaries, and respects zone alignment. It then confirms every chunk stripe was matched by a device extent.
- `verify_one_dev_extent()` checks chunk existence, expected stripe length, reserved-space warnings, device lookup, physical bounds, and zone alignment.
- `verify_chunk_dev_extent_mapping()` checks that each chunk map’s `verified_stripes` count equals `num_stripes`.
- `btrfs_pinned_by_swapfile()` checks whether a block group or device is pinned by an active swapfile and is used to reject unsafe removal/relocation.
- `btrfs_repair_one_zone()` schedules zoned block-group relocation repair after I/O failure, but avoids repair attempts in degraded mode.
- `relocating_repair_kthread()` runs zoned repair relocation under super write guard, exclusive balance operation, and `reclaim_bgs_lock`.

Cross-file relationships:
- `disk-io.c` and mount code depend on scanning/opening devices, reading system chunks, reading the chunk tree, verifying device extents, and later closing/freeing device state.
- `ioctl.c` drives user-visible device add/remove/resize, balance, cancel/pause/resume, stats, and device lookup flows that enter this file.
- `transaction.c` invokes delayed device-size and device-stat commit hooks.
- `block-group.c` and `extent-tree.c` interact with `btrfs_create_chunk()`, block-group creation/removal, allocation profiles, free chunk space, and chunk metadata reservation.
- `relocation.c` performs the heavy relocation work called by `btrfs_relocate_chunk()` and provides remap-tree translation used by mapping/discard paths.
- `raid56.c` consumes `btrfs_io_context` geometry from `btrfs_map_block()` for full-stripe parity write/recovery/scrub handling.
- `dev-replace.c` relies on device-list/chunk-mutex ordering and the replacement stripe duplication logic in mapping.
- `zoned.c` supplies zone compatibility, zone hole selection, empty-zone enforcement, superblock log-zone reset, and zone repair behavior.
- `scrub.c` uses mapping, missing-device handling, device stats, replace state, and relocation pause/continue integration.
- `sysfs.c` receives device add/remove/sprout updates.

Important invariants and risks:
- Device-list mutations during mount/close are protected by `uuid_mutex`; runtime list changes require `device_list_mutex`, and many read paths rely on RCU assumptions documented in the file.
- Chunk tree updates, device item updates for chunk changes, system chunk array modifications, and device allocation-state changes must occur under `chunk_mutex` to avoid allocation/removal/device-replace races.
- Device extent allocation searches the committed device tree and separately accounts for pending in-memory chunk allocations; this prevents double allocation but means newly freed extents in the current transaction are not seen as reusable.
- Device shrink first changes in-memory size so concurrent allocation stops using the truncated range, then relocates out-of-range extents, and must roll back totals on failure.
- Removing a chunk has a deliberate lock split: device extent deletion avoids `chunk_mutex` because COWing the device tree may allocate metadata chunks, while chunk item deletion later requires `chunk_mutex`.
- `btrfs_map_block()` must keep returned lengths within chunk, stripe, or RAID56 full-stripe boundaries; callers rely on this to split bios correctly.
- RAID56 mirror semantics differ from mirrored profiles: mirror 1 means rebuild from parity plus data, and RAID6 mirror numbers above 2 intentionally mark additional stripes as failed for retry reconstruction.
- Device replace can make allocated `bioc` stripe capacity larger than the real chunk stripe count. Consumers must honor `replace_nr_stripes`, `replace_stripe_src`, and `bioc->num_stripes`.
- Seed/sprout handling depends on preserving original seed `fs_devices` records in `fs_uuids` while moving mounted seed devices into private lists.
- Balance pause leaves `balance_ctl` and the on-disk balance item intact; cancel/completion deletes the item and finishes the exclusive operation.
- Persistent device-stat updates rely on memory ordering between counter updates and on-disk serialization during transaction commit.
- Mount-time writable safety depends on both chunk-tree device items and device extents matching the in-memory maps; corruption reports usually return `-EUCLEAN`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/volumes.c -->