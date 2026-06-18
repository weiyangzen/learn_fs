# sources/distributed-fs/ceph-client/fs/ext4/resize.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/resize.c` implements online growth of mounted ext4 filesystems. It validates resize requests, initializes metadata for new block groups and flex groups, updates group descriptor tables and backups, manages the resize inode or conversion to `meta_bg`, extends the final partial group, and publishes new groups to in-memory allocation structures and the on-disk superblock. The source was read as a complete 2192-line file.

## Important APIs, Types, and Functions

Public entry points include `ext4_resize_begin()`, `ext4_resize_end()`, `ext4_group_add()`, `ext4_group_extend()`, `ext4_resize_fs()`, `ext4_kvfree_array_rcu()`, and `ext4_list_backups()`. The key planning type is `struct ext4_new_flex_group_data`, which wraps an array of `struct ext4_new_group_data`, group flags, resize allocation capacity, and count.

Important helpers include `verify_group_input()`, `alloc_flex_gd()`, `ext4_alloc_group_tables()`, `setup_new_flex_group_blocks()`, `verify_reserved_gdb()`, `add_new_gdb()`, `add_new_gdb_meta_bg()`, `reserve_backup_gdb()`, `update_backups()`, `ext4_add_new_descs()`, `ext4_set_bitmap_checksums()`, `ext4_setup_new_descs()`, `ext4_update_super()`, `ext4_flex_group_add()`, `ext4_setup_next_flex_gd()`, `ext4_group_extend_no_check()`, `ext4_convert_meta_bg()`, and bitmap helpers such as `set_flexbg_block_bitmap()`.

## Control Flow

`ext4_resize_begin()` enforces `CAP_SYS_RESOURCE`, checks resize-inode consistency, rejects resizing from a backup superblock, refuses filesystems mounted with errors or `sparse_super2`, and sets `EXT4_FLAGS_RESIZING`. `ext4_resize_end()` clears the flag and optionally refreshes overhead accounting.

`ext4_resize_fs()` is the main grow-to-size path. It first verifies the target block exists on the device and trims bigalloc requests to a cluster boundary. It rejects shrink, no-op, and inode-count overflow cases, computes old/new group and descriptor counts, opens the resize inode when needed, and may convert to `meta_bg` if descriptor growth cannot use resize-inode reservations. It ensures the last group has enough room for required metadata, extends the current last group if only partial capacity remains, allocates flex group and multiblock allocator arrays, then repeatedly plans the next flex group, allocates its metadata block locations, and commits it through `ext4_flex_group_add()`.

`ext4_flex_group_add()` initializes new metadata blocks in one transaction series before exposing the group: backup superblocks/GDTs, inode tables, block bitmaps, inode bitmaps, and bitmap bits for group tables. It then journals superblock access, adds any needed group descriptor blocks, writes descriptors, adds in-memory groupinfo, updates superblock counts and allocation counters, and finally updates backup superblocks and GDT copies. `ext4_group_add()` is the older single-group interface and wraps the same flex-add machinery after validating user-provided group layout. `ext4_group_extend()` only extends the current last group without adding descriptors.

## State and Persistence Behavior

Persistent state includes `s_blocks_count`, free block and inode counters, total inode count, reserved block count, overhead clusters, feature flags (`resize_inode`, `meta_bg`), `s_first_meta_bg`, `s_reserved_gdt_blocks`, group descriptor blocks, backup superblocks/GDTs, block and inode bitmaps, inode tables, resize inode block pointers and `i_blocks`, and group descriptor checksums. In-memory state includes `s_groups_count`, `s_blockfile_groups`, RCU-protected `s_group_desc` arrays, flex group counters, multiblock allocator groupinfo, free cluster and inode percpu counters, and the resizing flag.

The code uses write memory barriers before publishing `s_groups_count`, with comments specifying that readers must pair with read barriers before consuming dependent group data. Replacement group descriptor arrays are freed through RCU via `ext4_kvfree_array_rcu()`.

## Dependencies and Integration Points

This file depends on ext4 superblock and group descriptor formats, JBD2 resize transactions, block bitmap manipulation, inode table zeroing, backup-super selection, resize inode layout, metadata checksums, RCU array publication, multiblock allocator setup, flex_bg accounting, bigalloc cluster math, feature flags, and block-device reads/zeroout. It integrates with ioctl/remount resize paths, mount feature validation, allocator visibility, and backup metadata used by e2fsck.

## Risks and Edge Cases

Online resize cannot roll back arbitrary metadata once journaled, so most helpers validate inputs and allocate memory before mutating on-disk structures. Group geometry must avoid overlaps among bitmaps, inode tables, GDTs, and data space. Descriptor growth must distinguish reserved-GDT resize-inode mode from `meta_bg` mode and convert only when safe. Backup update failure is nonfatal for the resize but marks the filesystem not valid to force fsck. Publishing `s_groups_count` before descriptors and counters are ready would expose invalid allocation space, hence the ordering barriers.

Other edge cases include sparse backup group sequences, non-sparse filesystems reaching descriptor boundaries, bigalloc cluster alignment, partial final groups, inode count overflow, block count overflow, resize inode corruption, memory allocation failures for large flex groups, journal credit exhaustion requiring restarts, and resizing attempts on filesystems with errors or unsupported `sparse_super2`.

## Test Signals

Tests should cover online growth within the last group, adding one group, adding many flex groups, descriptor block boundary crossings, reserved-GDT consumption, conversion to `meta_bg`, bigalloc growth, metadata checksum filesystems, flex_bg accounting, backup superblock/GDT updates, ENOSPC or EIO reading target last block, journal credit batching, and fault injection during bitmap/table/descriptor initialization. Signals include mount logs for resize progress, updated `s_groups_count`, allocator visibility of new groups, valid group descriptor checksums, fsck-clean backup metadata, and forced-fsck state when backup updates fail.
