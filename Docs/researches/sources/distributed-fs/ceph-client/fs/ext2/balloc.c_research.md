# sources/distributed-fs/ceph-client/fs/ext2/balloc.c

Purpose: Implements ext2 block bitmap validation, allocation, freeing, reservation-window management, free block counting, and sparse-superblock group descriptor accounting.

Important APIs/types/functions: Public helpers include `ext2_get_group_desc`, `ext2_new_blocks`, `ext2_free_blocks`, `ext2_data_block_valid`, `ext2_count_free_blocks`, `ext2_bg_has_super`, `ext2_bg_num_gdb`, `ext2_init_block_alloc_info`, `ext2_discard_reservation`, and `ext2_rsv_window_add`. Internal control centers are `read_block_bitmap`, `ext2_valid_block_bitmap`, `group_adjust_blocks`, `ext2_try_to_allocate`, `ext2_try_to_allocate_with_rsv`, `alloc_new_reservation`, `find_next_reservable_window`, and `ext2_has_free_blocks`.

Control flow: Allocation starts with quota reservation, optional inode reservation-window selection, reserved-block availability checks, and a goal group derived from the requested physical goal. It tries the goal group, then all groups, skipping empty or reservation-poor groups. Within a group it reads and validates the bitmap, optionally creates or extends a reservation window in the filesystem-wide red-black tree, finds free bits, and atomically sets contiguous bits. If reservations cause apparent ENOSPC, it retries without reservations. On success it rejects system-zone overlap, updates group descriptor counts, percpu free-block counter, quota, bitmap dirty state, and returns the first physical block plus actual count.

State and persistence behavior: Persistent state includes block bitmaps and group descriptor free-block counts; in-memory state includes percpu counters and reservation RB tree. Freeing validates the data zone, splits frees across group boundaries, refuses system-zone frees, atomically clears bitmap bits, dirties/syncs buffers on synchronous mounts, adjusts group/percpu counters, returns quota, and marks the inode dirty.

Dependencies and integration points: Used by `inode.c` block mapping and truncation. Depends on buffer heads, quota, capability checks for reserved blocks, per-blockgroup locks, superblock mount options, and ext2 group geometry from `ext2.h`.

Risks: Bitmap/group descriptor inconsistencies can allocate or free metadata blocks if validations regress. Reservation tree locking is split from bitmap locking and must avoid overlapping windows. Counter updates must match actual bits changed, including already-clear/already-set races. The `ext2_data_block_valid` check excludes first data block and superblock overlap but metadata-zone checks happen separately.

Test signals: xfstests allocation/free under fragmentation; ENOSPC with reserved blocks and unprivileged users; reservation on/off and `EXT2_IOC_SETRSVSZ`; corruption tests for bad block bitmap, freeing system zones, and cross-group frees; synchronous mount bitmap persistence; sparse-superblock group accounting.
