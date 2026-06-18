# sources/distributed-fs/ceph-client/fs/btrfs/tests/btrfs-tests.c

## Purpose

`btrfs-tests.c` is the shared harness for Btrfs in-kernel sanity tests enabled by `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`. It provides a pseudo filesystem mount, dummy Btrfs allocation helpers, transaction initializers, and the top-level `btrfs_run_sanity_tests()` dispatcher.

## Important APIs, Types, And Functions

- `test_mnt` stores the pseudo filesystem mount used for test inode allocation.
- `test_error[]` maps shared allocation failure indexes from `btrfs-tests.h` to log strings.
- `btrfs_test_init_fs_context()`, `test_type`, `btrfs_init_test_fs()`, and `btrfs_destroy_test_fs()` register, mount, unmount, and unregister the pseudo filesystem.
- `btrfs_new_test_inode()` allocates a regular inode from `test_mnt` and initializes Btrfs inode number and ownership.
- `btrfs_alloc_dummy_fs_info()` and `btrfs_free_dummy_fs_info()` build and tear down a minimal `btrfs_fs_info` with `fs_devices`, `super_copy`, buffer tree, checksum sizing, and dummy state.
- `btrfs_alloc_dummy_device()` creates a `btrfs_device`, initializes its `alloc_state`, and links it to `fs_info->fs_devices->devices`.
- `btrfs_alloc_dummy_block_group()` and `btrfs_free_dummy_block_group()` create block group/free-space-control scaffolding.
- `btrfs_init_dummy_transaction()` and `btrfs_init_dummy_trans()` initialize enough delayed-ref and transaction handle state for tests.
- `btrfs_run_sanity_tests()` runs all registered sanity tests across supported sectorsize/nodesize combinations, then extent-map and zoned tests.

## Control Flow

`btrfs_run_sanity_tests()` registers and mounts the pseudo filesystem first. It then loops through `test_sectorsize[]` and powers-of-two nodesizes up to `BTRFS_MAX_METADATA_BLOCKSIZE`, running free-space cache, extent buffer, extent I/O, inode, qgroup, free-space tree, raid-stripe-tree, delayed-ref, and chunk-allocation tests. After the nodesize loop, it runs extent-map tests and zoned tests, then unmounts and unregisters the pseudo filesystem.

Dummy allocators are intentionally minimal but initialize the fields used by production helpers. Cleanup releases extent buffers from `fs_info->buffer_tree`, mapping trees, devices, qgroup config, fs roots, superblock copy, and leak debug checks.

## State And Persistence Behavior

All state is in-memory test state. `btrfs_alloc_dummy_fs_info()` sets `BTRFS_FS_STATE_DUMMY_FS_INFO`, installs the dummy `fs_info` into the pseudo superblock, and configures sizes and checksum metadata. No disk persistence occurs. Cleanup is strict because production helpers may populate xarrays, mapping trees, roots, qgroups, and extent buffers.

## Dependencies And Integration Points

This harness integrates with Linux pseudo filesystems, VFS inode allocation, Btrfs inode allocation/destruction, free-space cache/tree, transactions, volumes, qgroups, block groups, and disk-io helpers. Every test file in this subset depends on these helpers through `btrfs-tests.h`.

## Risks

The dummy objects are intentionally incomplete, so tests must only call production paths whose dependencies are initialized. Missing cleanup can leak extent buffers, roots, devices, or qgroup config and make later tests unreliable. The harness stops on first failure inside the sectorsize/nodesize loop, so one failing test can hide later failures.

## Test Signals

The top-level test signal is a zero return from `btrfs_run_sanity_tests()`. Each subtest logs its name through `test_msg()` and returns negative errno-like failures. Allocation failures use shared `test_std_err()` messages to identify the missing dummy object class.
