# sources/distributed-fs/ceph-client/fs/btrfs/volumes.h

## Purpose

`volumes.h` is the central public contract for Btrfs multi-device and chunk-mapping behavior. It defines the in-memory device model, filesystem device set model, RAID profile attributes, chunk-map representation, IO mapping context, device lookup arguments, and exported operations for scanning, opening, resizing, balancing, replacing, mapping, and validating devices and chunks. Other Btrfs subsystems use this header to translate logical filesystem addresses into physical device stripes, track device state, and coordinate allocation policy, including zoned allocation policy through `BTRFS_CHUNK_ALLOC_ZONED`.

## Important APIs, Types, And Functions

Core constants include `BTRFS_STRIPE_LEN`, `BTRFS_MAX_DATA_CHUNK_SIZE`, `BTRFS_MAX_DISCARD_CHUNK_SIZE`, and the `BTRFS_DEV_STATE_*` bit indexes. The `BTRFS_BG_FLAG_TO_INDEX()` conversion and `enum btrfs_raid_types` map on-disk block-group profile bits to compact internal RAID indexes. Static assertions protect this on-disk-to-in-memory mapping.

`struct btrfs_device` represents one member device. Important fields include `devid`, UUID, `bdev_file`, `bdev`, `zone_info`, `dev_state`, size accounting (`total_bytes`, `disk_total_bytes`, `bytes_used`, `commit_*`), flush state, scrub state, dev stats, sysfs kobject state, allocation extent tree, and per-profile temporary accounting. The 64-bit size fields are accessed through generated `btrfs_device_get_*()` and `btrfs_device_set_*()` helpers; on 32-bit SMP they use `seqcount_t`, and on preemptible 32-bit they disable preemption.

`struct btrfs_fs_devices` groups all devices for one filesystem identity. It stores `fsid`, `metadata_uuid`, device counts, open/read-write counts, seed lists, mount/holding counters, sysfs roots, read policy, allocation policy, and per-profile availability estimates protected by `per_profile_lock`.

`struct btrfs_io_context` is the logical-to-physical mapping result used during bio submission. It records the map type, original bio, logical range, mirror number, stripe array, device-replace duplicate stripe data, RAID56 full-stripe metadata, and refcounting. `struct btrfs_chunk_map` is the persistent mapping tree node with logical start, length, stripe size, RAID type, stripe count, and physical stripe array. `btrfs_free_chunk_map()` releases it when refs drop to zero and asserts it is not still in the rb-tree.

Exported APIs include `btrfs_map_block()`, `btrfs_map_repair_block()`, `btrfs_map_discard()`, `btrfs_read_sys_array()`, `btrfs_read_chunk_tree()`, `btrfs_create_chunk()`, `btrfs_open_devices()`, `btrfs_scan_one_device()`, `btrfs_close_devices()`, `btrfs_rm_device()`, `btrfs_grow_device()`, `btrfs_shrink_device()`, `btrfs_init_new_device()`, balance control functions, dev-stat functions, chunk-map lookup/update helpers, superblock IO helpers, device extent verification, per-profile availability helpers, and pending extent helpers.

## Control Flow And Integration

Mount-time code scans devices into `btrfs_fs_devices`, opens them, reads superblocks and chunk trees, and constructs `btrfs_chunk_map` entries. IO submission calls `btrfs_map_block()` or repair/discard variants to translate logical ranges into `btrfs_io_context` stripes. Chunk allocation and deletion paths use the chunk creation/removal prototypes and update device size accounting. Balance, relocation, replace, scrub, sysfs, and zoned code all share the device/chunk objects defined here.

The header also routes bio operations through `btrfs_op()`, where writes and zone appends map to `BTRFS_MAP_WRITE` and reads map to `BTRFS_MAP_READ`. RAID helpers and exported `btrfs_bg_*` routines provide profile names, factors, parity counts, and indexes used by allocation, sysfs reporting, and zoned profile validation.

## State And Persistence Behavior

Device and chunk state spans memory and disk. `struct btrfs_device` tracks in-memory open state, runtime flags, IO stats, sysfs objects, and transaction-local size values, while `disk_total_bytes`, `commit_total_bytes`, and chunk/dev item update APIs connect the state to on-disk metadata. `struct btrfs_fs_devices` keeps global identity and membership state across mount, seed, temp-fsid, and metadata-uuid modes. Device stats are atomic and paired with `dev_stats_ccnt` barriers so `btrfs_run_dev_stats()` can persist coherent changes. Chunk maps mirror on-disk chunk tree items and drive all logical-to-physical persistence semantics.

## Dependencies

This header depends on Linux block, bio, list, mutex, refcount, completion, kobject, rbtree, sort, atomic, and UAPI Btrfs definitions. It includes Btrfs `messages.h`, `extent-io-tree.h`, and `fs.h`, and forward declares transaction, block-group, zoned-device, and space-info structures. It is consumed by volume management, disk IO, bio, scrub, sysfs, zoned, balance, device replace, and allocation code.

## Risks And Edge Cases

The RAID index mapping is tied to on-disk bits; incorrect changes would corrupt profile interpretation. Device size access needs the 32-bit ordering helpers to avoid torn reads. The `dev_state` bit contract is broad and must remain consistent across mount, replace, missing-device, flush, and sysfs paths. `btrfs_io_context` flexible-array sizing and refcounting are sensitive to stripe-count calculations, especially for device replace and RAID56. Device stats require correct memory barriers or transaction persistence can miss increments. UUID and holding counters require `uuid_mutex` as asserted by helper functions.

## Test Signals

High-value tests include mount and remount with single, multi-device, missing-device, seed, temp-fsid, and metadata-uuid configurations; logical-to-physical mapping for all supported RAID profiles; device add/remove/grow/shrink/replace; dev-stat increment/read/reset persistence; chunk-map lookup/removal refcount tests; balance and relocation tests; 32-bit or KCSAN coverage for size accessors; and zoned-mode integration where `zone_info` and zoned allocation policy are populated.
