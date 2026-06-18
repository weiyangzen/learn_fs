# sources/distributed-fs/ceph-client/fs/btrfs/tests/raid-stripe-tree-tests.c

## Purpose
`raid-stripe-tree-tests.c` is a Btrfs selftest suite for the RAID stripe tree feature. It verifies that RAID stripe extents can be inserted, looked up, overwritten, truncated, punched, and deleted while preserving logical-to-physical stripe mappings for a two-device RAID1 test layout.

## Important APIs, Types, And Functions
The suite uses `struct btrfs_io_context` plus per-device `struct btrfs_io_stripe` entries as input to `btrfs_insert_one_raid_extent()`. It checks mappings through `btrfs_get_raid_extent_offset()` and removes ranges through `btrfs_delete_raid_extent()`. `btrfs_device_by_devid()` is a local lookup helper over `fs_devices->devices`.

Scenario functions cover one behavior each: `test_simple_create_delete()`, `test_create_update_delete()`, `test_tail_delete()`, `test_front_delete()`, `test_front_delete_prev_item()`, `test_punch_hole()`, `test_punch_hole_3extents()`, and `test_delete_two_extents()`. `run_test()` builds an isolated dummy filesystem and transaction for each scenario, and `btrfs_test_raid_stripe_tree()` runs the scenario table.

## Control Flow
Each scenario allocates a `btrfs_io_context`, fills two stripes with devices 0 and 1, chooses `RST_TEST_RAID1_TYPE`, and inserts one or more logical ranges. Lookups select device 0 and assert the physical address and returned length. Deletion scenarios then call `btrfs_delete_raid_extent()` over exact, front, tail, middle, or cross-item ranges, followed by lookup assertions for retained fragments and `-ENODATA` assertions for holes.

`run_test()` allocates a dummy fs, creates a dummy stripe root with `BTRFS_FEATURE_INCOMPAT_RAID_STRIPE_TREE`, installs an empty leaf, allocates two dummy devices, initializes a dummy transaction, runs the selected scenario, and frees the dummy root and fs. This per-test isolation prevents leftover stripe extents from affecting later cases.

## State And Persistence Behavior
State is held in the dummy stripe root btree and dummy device list. The tests mutate the RAID stripe tree through production insert and delete helpers, but no disk IO is performed. Logical ranges are generally anchored at 1 MiB, with device 1 physical addresses offset by 1 GiB to make copy selection visible.

## Dependencies And Integration Points
The suite integrates with `fs.h`, `disk-io.h`, `transaction.h`, `volumes.h`, and `raid-stripe-tree.h`. It validates the RAID stripe tree implementation behind the higher-level volume mapping code, especially the contract that lookups return the correct physical address and maximum contiguous length for a requested logical offset.

## Risks And Edge Cases
The strongest coverage is around range surgery. Tests verify deletion of two complete extents while leaving a third intact; punching a hole in one extent into two fragments; punching a 2 MiB hole across three 1 MiB extents; front deletion that shifts item starts; tail deletion that shrinks length; and cross-item deletion where the deletion starts in one item and ends in the next. Because all tests use RAID1 with two devices, they do not validate RAID0/10 profile-specific stripe math. Several cases also rely on exact size constants, so future stripe tree item coalescing behavior could require careful expectation updates.

## Test Signals
The suite signals success by exact lookup behavior after every mutation: retained fragments must return expected physical offsets and lengths, deleted regions must return `-ENODATA`, and cleanup deletes remaining extents. `btrfs_test_raid_stripe_tree()` reports the failing function pointer with `%ps`, which is useful for locating the failed scenario in kernel selftest output.
