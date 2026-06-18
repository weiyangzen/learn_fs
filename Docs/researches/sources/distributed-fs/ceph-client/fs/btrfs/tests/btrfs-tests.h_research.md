# sources/distributed-fs/ceph-client/fs/btrfs/tests/btrfs-tests.h

## Purpose

`btrfs-tests.h` is the shared declaration and logging header for Btrfs sanity tests. It exposes the top-level test runner, individual test entry points, dummy object helpers, and no-op fallbacks when sanity tests are disabled.

## Important APIs, Types, And Functions

- `btrfs_run_sanity_tests()` is declared as a real runner when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled and as an inline zero-return no-op otherwise.
- `test_msg()` and `test_err()` wrap `pr_info()`/`pr_err()` with a Btrfs selftest prefix; `test_err()` includes file and line.
- Allocation error enum values identify shared failure classes such as fs_info, root, extent buffer, path, inode, block group, extent map, chunk map, I/O context, and transaction.
- Individual entry points include extent buffer, free-space cache, extent I/O, inode, qgroup, free-space tree, raid stripe tree, extent map, delayed refs, chunk allocation, and zoned tests.
- Dummy helpers allocate/free inodes, `fs_info`, roots, block groups, transactions, and devices.
- `DEFINE_FREE()` wrappers provide cleanup support for dummy `fs_info` and block groups.

## Control Flow

The header uses `#ifdef CONFIG_BTRFS_FS_RUN_SANITY_TESTS` as its main switch. Enabled builds get declarations for test code compiled elsewhere; disabled builds get only a stub runner. Zoned tests have a second configuration split: `btrfs_test_zoned()` is real only under `CONFIG_BLK_DEV_ZONED`, otherwise it returns success.

## State And Persistence Behavior

The header declares helpers that manage in-memory dummy state. It contains no persistent state, but its cleanup wrappers encode ownership expectations for dummy `fs_info` and block groups.

## Dependencies And Integration Points

It depends on basic kernel types and cleanup helpers, forward declares Btrfs transaction/root types, and is included by all Btrfs test files in this subset. It is also the ABI between normal Btrfs initialization code and the optional sanity-test runner.

## Risks

Configuration guards must match the compilation of the test implementation files. Adding a new test requires adding a prototype here and wiring it into `btrfs_run_sanity_tests()`. Incorrect dummy helper ownership can cause leaks or double frees across test files.

## Test Signals

The header defines the common logging and error vocabulary used by all selftests, so consistent `test_msg()`, `test_err()`, and `test_std_err()` output is the main diagnostic signal.
