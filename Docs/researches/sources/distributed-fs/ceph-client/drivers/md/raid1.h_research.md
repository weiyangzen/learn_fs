# sources/distributed-fs/ceph-client/drivers/md/raid1.h

## Purpose
`raid1.h` defines the private data structures and constants for the MD RAID1 personality. It documents the safe access rules for mirror rdev pointers, declares barrier-bucket sizing, and defines the per-array and per-I/O state that `raid1.c` uses for mirrored I/O, recovery, write-behind, and hotplug.

## Important APIs, Types, And Functions
`BARRIER_UNIT_SECTOR_BITS` and `BARRIER_UNIT_SECTOR_SIZE` define 64 MiB barrier units. `BARRIER_BUCKETS_NR_BITS` and `BARRIER_BUCKETS_NR` size the per-bucket atomic arrays to one page. `struct raid1_info` stores one mirror or replacement `md_rdev`, current head position, and sequential-read tracking fields. `struct r1conf` is the per-array configuration: MD device pointer, mirror array sized at `raid_disks * 2`, disk counts, locks, retry lists, pending write list, barrier waitqueue and counters, fullsync flag, r1bio/resync mempools, split bioset, temporary repair page, private thread pointer, and cluster sync window. `struct r1bio` is the variable-sized per-request object with completion counters, sector range, state bits, master bio, selected read disk, retry linkage, optional behind bio, and flexible array of target bios. `enum r1bio_state` names the per-I/O state bits. `sector_to_idx()` hashes a sector's barrier unit to a barrier bucket.

## Control Flow
The header itself only defines structures and the inline `sector_to_idx()`. Its comments define the concurrency contract for `raid1_info.rdev`: safe access requires `mddev->reconfig_mutex`, known recovery/resync context, or RCU plus an `nr_pending` reference. `raid1.c` follows this contract in setup, removal, request submission, recovery, and frozen-array sections.

## State And Persistence
All types are in-memory. They mirror persistent MD concepts such as degraded count, replacement devices, bad blocks, bitmap-backed write-behind, recovery windows, and in-sync/faulty rdev flags, but the actual persistence is owned by MD metadata and bitmap code. The flexible `r1bio->bios[]` array is allocated with room for originals plus replacements and can contain real bios or sentinel values from the shared RAID1/10 helper include.

## Dependencies And Integration Points
The header depends on MD/block-layer types such as `struct mddev`, `struct md_rdev`, `mempool_t`, `struct bio_set`, `struct bio`, `sector_t`, atomic counters, locks, lists, pages, wait queues, and `hash_long()`. It is directly included by `raid1.c`; MD core indirectly interacts with `r1conf` through `mddev->private`.

## Risks
The "do not put fields after bios[]" rule on `struct r1bio` is critical because the flexible array is allocated contiguously with the object. Barrier bucket sizing assumes `atomic_t` width and page size; changing these constants affects memory use and lock granularity. Misusing `sector_to_idx()` or the rdev pointer access rules can create barrier collisions, missed wakeups, or lifetime bugs. The mirror array stores replacements after the primary `raid_disks` slots, so index math must consistently use `raid_disks * 2`.

## Test Signals
Header behavior is covered indirectly by RAID1 build and all normal I/O, resync, hotplug, replacement, reshape, and quiesce tests. Debug builds with lockdep/KCSAN/KASAN are especially useful for validating the documented rdev access and flexible-array lifetime assumptions.
