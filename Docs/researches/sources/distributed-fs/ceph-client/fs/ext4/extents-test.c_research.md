# sources/distributed-fs/ceph-client/fs/ext4/extents-test.c

## Purpose
`extents-test.c` is a KUnit suite for ext4 extent split and conversion behavior. It targets `ext4_split_convert_extents()` directly through a test-only wrapper and indirectly through `ext4_map_query_blocks()` plus `ext4_map_create_blocks()`. The tests verify initialized-to-unwritten conversion, unwritten-to-initialized conversion, fallback zeroout behavior when extent insertion fails, and extent-status cache synchronization for high-level mapping paths.

## Important APIs, types, and fixtures
The test uses a minimal synthetic ext4 mount, inode, extent tree, extent-status tree, and data buffer. Constants `EXT_DATA_PBLK`, `EXT_DATA_LBLK`, and `EXT_DATA_LEN` create one three-block extent mapping logical block 10 to physical block 100. `struct kunit_ctx` holds the allocated `struct ext4_inode_info` and an in-memory data area used to model disk contents for zeroout tests.

`struct kunit_ext_test_param` drives all parameterized cases. It records a description, test type (`TEST_SPLIT_CONVERT` or `TEST_CREATE_BLOCKS`), initial unwritten state, split flags, target `struct ext4_map_blocks`, whether zeroout is disabled, expected extent states, whether this is a zeroout test, and expected data-buffer segments after zeroing. `struct kunit_ext_state` and `struct kunit_ext_data_state` express the expected tree and data results.

Static stubs replace selected ext4 internals: `__ext4_ext_dirty_stub()` suppresses real journal dirtying, `ext4_ext_insert_extent_stub()` returns `-ENOSPC` to force fallback zeroout, `ext4_ext_zeroout_stub()` and `ext4_issue_zeroout_stub()` zero the synthetic data buffer instead of issuing real block IO.

## Control flow
`extents_kunit_init()` creates a fake superblock with 4 KiB blocks, allocates `struct ext4_sb_info`, registers the extent status shrinker, allocates a mock ext4 inode, initializes its extent status tree and locks, marks it extent-enabled, allocates a three-block data buffer filled with `'X'`, and builds a depth-0 extent tree rooted in `i_data`. It inserts a matching extent status entry and activates the common static stubs.

`test_split_convert()` optionally activates the insert-failure stub for zeroout cases, finds the initial extent, verifies starting logical block, length, and unwritten state, populates a map from the current parameter, and dispatches either to `ext4_split_convert_extents_test()` or to `ext4_map_create_blocks_helper()`. The helper first calls `ext4_map_query_blocks()` to populate map details and then `ext4_map_create_blocks()` to perform split/conversion, avoiding the need to mock the full `ext4_map_blocks()` path.

After mutation, the test refinds the extent tree and iterates expected extents. For high-level create-blocks cases, it also looks up each extent in the extent-status cache and verifies containment, physical block alignment, and written/unwritten status. For zeroout cases, it verifies the synthetic data buffer has zeroes only in the expected unwritten portions and preserves `'X'` in ranges that should remain data.

The suite registers three parameter groups: direct split/convert cases, initialized-to-unwritten cases through `convert_initialized_extent()`, and unwritten handling cases through `ext4_ext_handle_unwritten_extents()`.

## State and persistence behavior
The test does not mount or persist a real filesystem. It models persistent extent metadata in `k_ei->i_data` and models disk data in `k_ctx.k_data`. The synthetic extent status tree is kept in memory and validated only for paths that should update it. Zeroout behavior is persistence-relevant even in this fake setup: the test ensures fallback conversion to one initialized extent does not leak stale data in ranges that remain logically unwritten.

Resource cleanup in `extents_kunit_exit()` unregisters the shrinker, deactivates the superblock, frees `sbi`, the mock inode, and the data buffer. Failure paths in init free partially allocated state and deactivate the superblock.

## Dependencies and integration points
The file depends on KUnit, KUnit static stubs, ext4 core headers, extents helpers, extent status APIs, superblock lifecycle helpers, and the KUnit-only exports declared in `ext4_extents.h` and `ext4.h`. It reaches into internal ext4 functions rather than public VFS behavior, so it is a focused unit test for extent algorithms.

## Risks and review notes
The test intentionally uses a minimal mock inode and superblock, so it may not catch bugs involving full journal handles, real block allocation, quota, locking, checksum tails, multi-level extent trees, or IO error handling. Static stubs can mask interactions with dirtying and block IO. Because the fixture creates only one depth-0 extent of length three, it has strong coverage of split shapes within a small extent but not broader tree balancing or large extent limits.

The global `k_ctx` means cases assume KUnit serializes suite state or invokes init/exit cleanly per case. Any future parallelization or additional shared state should avoid cross-test contamination.

## Test signals
The parameter tables cover two-extent and three-extent splits at the beginning, end, and middle of an extent; unwritten-to-written and written-to-unwritten transitions; direct split conversion; high-level create-block paths; endio and non-endio unwritten handling; forced `-ENOSPC` zeroout fallback; data preservation around zeroed ranges; and extent status cache consistency for high-level paths. These are strong regression signals for extent conversion correctness and stale-data avoidance.
