# sources/distributed-fs/ceph-client/fs/btrfs/tests/zoned-tests.c

## Purpose
`zoned-tests.c` is a table-driven Btrfs selftest for loading zoned block group allocation state from per-stripe write pointers. It focuses on `btrfs_load_block_group_by_raid_type()` behavior across SINGLE, DUP, RAID1, RAID0, and RAID10 profiles, including conventional zones, missing devices, degraded mounts, partially written stripes, and invalid write pointer layouts.

## Important APIs, Types, And Functions
The key local type is `struct load_zone_info_test_vector`, which declares raid profile, stripe count, per-stripe allocation offsets, last allocation pointer, block group length, degraded mode, expected return, and expected allocation offset. The local `struct zone_info` mirrors the fields consumed by the loader: physical, capacity, and alloc offset. `test_load_zone_info()` builds a dummy block group, chunk map, zone info array, and active bitmap, then calls `btrfs_load_block_group_by_raid_type()`.

Special sentinel offsets model device states: `WP_MISSING_DEV` for a missing device and `WP_CONVENTIONAL` for a conventional zone. `HALF_STRIPE_LEN` expresses partial-stripe progress.

## Control Flow
`btrfs_test_zoned()` allocates a dummy fs info and loops over `load_zone_info_tests[]`. Each vector sets up a chunk map with `map->type`, `map->num_stripes`, and RAID10 `sub_stripes = 2` when needed. Active bits are set for sequential zones with an allocation offset inside `ZONE_SIZE`. The test toggles the mount `DEGRADED` option based on the vector, invokes the loader, compares the returned errno with `expected_result`, and for success compares `bg->alloc_offset` with `expected_alloc_offset`.

## State And Persistence Behavior
The test is purely in memory. Persistent zoned state is modeled by zone write pointers and `last_alloc`; loader output is represented by the dummy block group's `alloc_offset`. The active bitmap models zones with outstanding sequential allocations. Mount option state is mutated on the dummy `fs_info->mount_opt` to exercise degraded recovery rules.

## Dependencies And Integration Points
The file depends on Btrfs test helpers, `space-info.h`, `volumes.h`, and `zoned.h`. It directly covers zoned integration between chunk-map RAID geometry and block group allocation recovery. The vectors encode how the zoned allocator expects mirrored profiles to agree on write pointers, striped profiles to preserve stripe order, and conventional zones to be reconciled through `last_alloc`.

## Risks And Edge Cases
Important negative cases include mismatched mirrored write pointers, partial missing devices for nonrecoverable profiles, `last_alloc` greater than the sequential write pointer, disordered RAID0 or RAID10 stripes, stripes too far apart, and too many partial writes. Positive degraded behavior is limited to RAID1-style recovery where the available mirror can define the allocation pointer. Conventional-zone cases are sensitive because the loader must infer a consistent logical allocation point from incomplete physical write-pointer data.

## Test Signals
The table intentionally expects some loader errors, and the entry point announces that error messages are expected. A vector fails only when the return code differs from `expected_result` or a successful call produces the wrong block group `alloc_offset`. This makes the file a compact regression matrix for zoned allocation recovery.
