# Group Research: group_658_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_volumes_c_485cf4cde9cd

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/kdave-linux` is included in subset A. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/volumes.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/volumes.c

## Purpose

`volumes.c` is the central Btrfs volume, device, chunk, balance, and logical-to-physical mapping implementation. It manages global scanned-device registration, mount-time device opening, seed/sprout filesystems, device add/remove/resize, chunk allocation and removal, balance relocation, RAID profile metadata, runtime chunk maps, block I/O mapping, discard mapping, device statistics, device/chunk-tree verification, and zoned repair relocation.

## Public Interfaces

Important implemented interfaces include RAID/profile helpers, global device scanning, device open/close, device add/remove/grow/shrink, device replace helpers, chunk map lookup/allocation/removal, balance/resume/recover/pause/cancel, I/O mapping, discard mapping, mount-time chunk/device loading, degraded mount checks, device stats, and zoned repair helpers.

## Major Behavior

The file defines `btrfs_raid_array[]`, the table of Btrfs RAID profile properties: minimum devices, device increments, copies, parity, tolerated failures, names, flags, and error codes. This table drives profile validation, stripe geometry, logical capacity, copy counts, degraded tolerance, and user-visible names.

Device registration is built around the global `fs_uuids` list protected by `uuid_mutex`. Scan-time code reads superblocks, handles temp-fsid cases, updates device paths, rejects mounted duplicates, and removes stale unmounted records. Device names are RCU-protected.

Mount open/close code verifies devid/UUID matches, tracks latest generation, writeability, discard and rotational status, open/rw counts, and block devices. Close paths flush/invalidate writable devices, reset transient state, release zone info, and keep or free `fs_devices` depending on reuse.

Seed and sprout handling lets a read-only seed filesystem become part of a writable filesystem by cloning seed state, splicing devices into a private seed list, assigning a new fsid, recording seed generations, adding the first writable metadata/system chunks, and relocating system chunks after device initialization.

Device extent allocation searches the committed device tree and adjusts holes for pending chunk allocations in `device->alloc_state`. Zoned filesystems additionally require allocatable, empty, zone-aligned ranges. This prevents double allocation during open transactions.

Device removal validates extent-tree-v2 support, RAID minimum devices, swapfile pins, replace-target state, and last-writable-device status. It removes the device from allocation, shrinks it to zero by relocating extents, deletes the device item, cancels scrub, detaches list state, scratches old superblocks, and defers final block-device release to the caller.

Chunk removal is staged: delete device extents and update device used-space accounting first, then under `chunk_mutex` update device items, remove the `CHUNK_ITEM`, delete system chunk array entries, and remove the block group. If system metadata reservation hits `-ENOSPC`, it allocates a system chunk and retries once.

Balance persists intent as a temporary item, validates conversion profiles, rejects mixed data/metadata mismatches, requires force when reducing metadata/system redundancy, and supports pause, cancel, async resume, and mount-time recovery. The relocation engine first counts matching chunks, then relocates filtered chunks by type, profile, usage, devid, physical range, virtual range, stripe count, soft-convert target, and limits.

Chunk allocation is profile-driven through `struct alloc_chunk_ctl`. Regular allocation limits chunk and stripe size by space-info policy, 1 GiB stripe size, and 10% writable-space heuristics. Zoned allocation uses zone-sized stripes and stricter metadata/system sizing. Allocation installs an in-memory chunk map, creates a block group, updates device bytes used, sets RAID incompat bits, and later persists chunk/device extent items.

The mapping tree is an rb-tree of refcounted `btrfs_chunk_map` objects protected by `mapping_tree_lock`. Maps are inserted with device allocation bits set and removed with bits cleared.

`btrfs_map_block()` translates logical ranges into physical stripes for SINGLE, DUP, RAID0, RAID1/1C3/1C4, RAID10, RAID5, and RAID6. It handles stripe-boundary length limits, RAID56 full-stripe mapping, read mirror selection, single-device fast paths, RAID stripe tree remapping, and device-replace write duplication.

Mount-time loading reads the system chunk array, then walks the chunk tree to load device and chunk items. It handles seed devices, degraded missing-device placeholders, device geometry/accounting, runtime chunk maps, and free chunk space. Post-load verification checks degraded writeability, dev-extent/chunk consistency, device boundaries, zone alignment, and stale registered devices.

Device statistics are loaded from and persisted to the device tree. Commit-time stat flushing uses a cheap RCU pre-scan before taking `device_list_mutex`, reducing transaction-commit blocking when no counters changed.

Zoned repair starts a background relocation task for a failed block group, guarded by balance exclusivity and a per-block-group relocating flag.

## Dependencies and Integration

`volumes.c` integrates with disk I/O, extent tree, block groups, transactions, RAID56, device replace, sysfs, tree checker/accessors, space info, discard, zoned support, UUID tree, ioctl balance formatting, relocation, scrub, superblock helpers, and the RAID stripe tree. It also uses Linux block-device APIs, page cache, VFS path lookup, kthreads, RCU, rbtrees, atomics, percpu counters, and lockdep.

## Concurrency and Safety Notes

Key locks are `uuid_mutex`, `device_list_mutex`, `chunk_mutex`, `balance_mutex`, and `reclaim_bgs_lock`. Lock ordering is carefully documented because chunk allocation/removal, device replace finalization, COW, mount-time loading, and block-device open/close can otherwise deadlock.

RCU protects device list/name readers; detached devices call `synchronize_rcu()` before free. Chunk maps are refcounted and must be released by callers.

High-risk areas are RAID geometry arithmetic, device-replace duplication, RAID56 full-stripe boundaries, zoned alignment and empty-zone checks, seed/sprout fsid transitions, degraded mount policy, balance pause/cancel lifetime, transaction abort handling during chunk/device metadata updates, and commit-time stat/device-size synchronization.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/volumes.c -->