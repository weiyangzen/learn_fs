# sources/distributed-fs/ceph-client/fs/ext4/mballoc-test.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/mballoc-test.c` is a KUnit test module for ext4 multiblock allocation internals. It builds a synthetic ext4 superblock, stubs the block bitmap and group descriptor accessors used by mballoc, initializes the real mballoc backend, and verifies allocation, freeing, bitmap marking, buddy generation, and buddy mutation behavior over several block-size and cluster-layout configurations. The source was read as a complete 1003-line file.

## Important APIs, Types, and Functions

The local test harness types are `struct mbt_grp_ctx`, which owns a fake block bitmap buffer head, fake group descriptor, and descriptor buffer head for one block group; `struct mbt_ctx`, which holds an array of group contexts; `struct mbt_ext4_super_block`, which embeds a fake on-disk superblock, `struct ext4_sb_info`, and test context; and `struct mbt_ext4_block_layout`, which parameterizes block size, cluster bits, blocks per group, group count, and descriptor size.

Harness setup and teardown functions include `mbt_alloc_inode()`, `mbt_free_inode()`, `mbt_kill_sb()`, `mbt_mb_init()`, `mbt_mb_release()`, `mbt_ext4_alloc_super_block()`, `mbt_ext4_free_super_block()`, `mbt_init_sb_layout()`, `mbt_grp_ctx_init()`, `mbt_grp_ctx_release()`, `mbt_ctx_init()`, `mbt_ctx_release()`, `mbt_kunit_init()`, and `mbt_kunit_exit()`.

Static-stub replacements are `ext4_read_block_bitmap_nowait_stub()`, `ext4_wait_block_bitmap_stub()`, `ext4_get_group_desc_stub()`, and `ext4_mb_mark_context_stub()`. They redirect mballoc internals to the synthetic bitmaps and descriptors.

Test helpers include `mbt_ctx_mark_used()`, `mbt_ctx_bitmap()`, `mbt_generate_test_ranges()`, `validate_free_blocks_simple()`, `test_free_blocks_simple_range()`, `test_mark_diskspace_used_range()`, `mbt_generate_buddy()`, `mbt_validate_group_info()`, `do_test_generate_buddy()`, `test_mb_mark_used_range()`, and `test_mb_free_blocks_range()`. KUnit cases are `test_new_blocks_simple()`, `test_free_blocks_simple()`, `test_mb_generate_buddy()`, `test_mb_mark_used()`, `test_mb_free_blocks()`, `test_mark_diskspace_used()`, and slow case `test_mb_mark_used_cost()`.

## Control Flow

KUnit enters through `mbt_test_suite`, which names the suite `ext4_mballoc_test`, supplies `mbt_kunit_init()` and `mbt_kunit_exit()`, and registers parameterized test cases across `mbt_test_layouts`. `KUNIT_ARRAY_PARAM()` creates layout parameters for 1 KiB, 4 KiB, and 64 KiB block sizes, all with `cluster_bits = 3`, four groups, 8192 blocks per group, and 64-byte group descriptors.

`mbt_kunit_init()` allocates a superblock through `sget()`, embeds ext4 private state in `struct mbt_ext4_super_block`, initializes blockgroup locks and layout fields, allocates per-group fake bitmaps/descriptors, activates KUnit static stubs for bitmap and descriptor access, calls `mbt_mb_init()` to run the real `ext4_mb_init()`, initializes free and dirty cluster counters, and stores the superblock in `test->priv`.

`mbt_ctx_init()` sets each fake group bitmap to contain all valid clusters free and all beyond-end bits used, initializes free-cluster counts in the fake descriptor, and marks the first cluster of group zero used so simple allocation does not choose a block that fails ext4 superblock block-validity checks. `mbt_kunit_exit()` reverses setup by releasing counters, mballoc state, fake block device and queue, per-group bitmap memory, blockgroup lock state, and the synthetic superblock.

The simple allocation test calls `ext4_mb_new_blocks_simple_test()` repeatedly: first expecting the goal block, then the next cluster after the goal, then the first cluster in a later group after the goal group is full, then an earlier group after later groups are full, and finally an allocation failure after all groups are full.

Freeing and marking tests generate random non-overlapping ranges within equal slices of a group. `test_free_blocks_simple()` first marks every cluster used, frees a range through `ext4_free_blocks_simple_test()`, and validates only that range became free in the goal group. `test_mark_diskspace_used()` calls `ext4_mb_mark_diskspace_used_test()` for each generated range and checks the fake bitmap has exactly that contiguous used range.

Buddy tests construct expected buddy and group-info state independently with `mbt_generate_buddy()`, then compare it with ext4 internals. `test_mb_generate_buddy()` checks `ext4_mb_generate_buddy_test()` from arbitrary bitmap ranges. `test_mb_mark_used()` loads a real `struct ext4_buddy`, applies `mb_mark_used_test()`, updates the independent bitmap, regenerates expected buddy data, and compares both buddy bytes and group counters. `test_mb_free_blocks()` starts from a fully used group, frees ranges with `mb_free_blocks_test()`, and performs the same comparison. `test_mb_mark_used_cost()` repeats random mark/free cycles 100000 times and logs elapsed jiffies for a slow performance signal.

## State and Persistence Behavior

All state is in-memory KUnit fixture state; the module does not mount or write a real filesystem. The synthetic `struct super_block` has enough fields populated for ext4 mballoc to operate: block size, group geometry, cluster ratio, descriptor sizing, `s_es`, blockgroup lock, inode list, super operations, fake block device, request queue, buddy cache, and percpu counters.

Fake persistent metadata is represented by in-memory block bitmaps and group descriptors in `mbt_grp_ctx`. Stubs return these objects to real ext4 mballoc code, so tests observe mutations through bitmap bits, descriptor free-cluster counts, and `struct ext4_group_info` buddy counters. `mbt_mb_init()` and `mbt_mb_release()` create and destroy real mballoc backend state, including the buddy cache inode and counters.

Random test ranges are transient and generated separately per test iteration. Several helper paths explicitly skip zero-length ranges because the tested production functions warn or BUG on zero lengths, so the test avoids invalid inputs rather than asserting their handling.

## Dependencies and Integration Points

The file depends on KUnit, KUnit static stubs, Linux random helpers, ext4 core declarations from `ext4.h`, and mballoc declarations from `mballoc.h`. It is tightly integrated with test-only symbols exposed by the mballoc implementation, including `ext4_mb_new_blocks_simple_test()`, `ext4_free_blocks_simple_test()`, `ext4_mb_mark_diskspace_used_test()`, `ext4_mb_generate_buddy_test()`, `ext4_mb_load_buddy_test()`, `ext4_mb_unload_buddy_test()`, `mb_mark_used_test()`, `mb_free_blocks_test()`, `mb_find_next_zero_bit_test()`, `mb_find_next_bit_test()`, and bit manipulation helpers.

Static stubbing lets the suite reuse production mballoc behavior while replacing filesystem I/O dependencies. `ext4_read_block_bitmap_nowait_stub()` hands out a referenced fake buffer head, `ext4_wait_block_bitmap_stub()` marks it uptodate and verified, `ext4_get_group_desc_stub()` exposes the fake descriptor, and `ext4_mb_mark_context_stub()` applies direct bitmap mutations for mark-context calls.

The test module registers with `kunit_test_suites()` and declares `MODULE_LICENSE("GPL")`, so it is built and run as a kernel KUnit suite when the relevant ext4 test configuration is enabled.

## Risks and Edge Cases

The harness deliberately models only the subset of ext4 state needed by mballoc. That keeps the tests fast, but it risks diverging from real mount-time state if mballoc starts depending on additional superblock, block-device, journal, or group-descriptor fields. Stub behavior must stay aligned with production helper side effects, especially buffer-head reference ownership, uptodate/verified flags, and group descriptor updates.

Random range generation increases coverage but can reduce reproducibility unless the KUnit random seed is captured by the broader test runner. Zero-length ranges are skipped because production helpers expect non-zero lengths in some paths; this means invalid-length handling is not tested here. Tests that compare raw buddy memory depend on stable buddy layout and offsets for each block size and cluster geometry.

The 64 KiB block-size layout is skipped for buddy-cache load/mutation tests when block size exceeds `PAGE_SIZE`, because the buddy cache assumes a page contains at least one block. That skip is intentional but leaves those paths covered only for smaller layouts on systems with smaller page sizes. The slow cost test loops 100000 times and logs timing rather than asserting a threshold, so it is a performance observation rather than a regression gate.

## Test Signals

Primary success signals are KUnit assertions comparing expected block numbers, allocation errors, exact bitmap transitions, buddy-buffer byte equality, and `struct ext4_group_info` counters such as `bb_first_free`, `bb_fragments`, `bb_free`, `bb_largest_free_order`, and `bb_counters[]`. The suite covers allocation preference around goal groups, fallback before and after a goal group, no-space failure, freeing exact ranges, diskspace marking, buddy generation, mark-used mutation, free-block mutation, and a slow mark-used cost path.

Useful failure diagnostics come from assertion messages that print expected and found blocks or counter indexes. Additional validation should run the suite under different page sizes and with KASAN/KCSAN or fault injection for allocation failures in setup paths, because this file has detailed cleanup paths for partial superblock, group-context, mballoc, and percpu-counter initialization.
