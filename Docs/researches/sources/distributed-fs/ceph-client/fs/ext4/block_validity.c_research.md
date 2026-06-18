# sources/distributed-fs/ceph-client/fs/ext4/block_validity.c

## Purpose

`fs/ext4/block_validity.c` builds and queries an RCU-protected red-black tree of ext4 filesystem metadata block ranges, called system zones, so file data block references cannot overlap superblocks, group descriptors, bitmaps, inode tables, or journal inode blocks. It is a defense against metadata overwrite caused by corrupted block maps or logic bugs.

## Important APIs, types, and functions

- `struct ext4_system_zone` stores one protected range: start block, count, and owning inode number for special reserved-inode ranges.
- `ext4_init_system_zone()` and `ext4_exit_system_zone()` manage the kmem cache.
- `add_system_zone()` inserts a non-overlapping range into an rb-tree and merges adjacent ranges with the same inode owner.
- `ext4_setup_system_zone()` builds a complete tree for a mounted superblock from every group's base metadata, block bitmap, inode bitmap, inode table, and optional journal inode blocks, then publishes it with `rcu_assign_pointer()`.
- `ext4_release_system_zone()` clears the published pointer and frees the old tree after an RCU grace period.
- `ext4_protect_reserved_inode()` maps a reserved inode such as the journal inode and adds its extents as allowed-only-for-that-inode zones.
- `ext4_sb_block_valid()` checks a block range against filesystem bounds and the system zone tree; if an inode is supplied, overlap is allowed only when the zone owner matches the inode number.
- `ext4_inode_block_valid()` wraps the superblock-level check for an inode.
- `ext4_check_blockref()` validates an array of 32-bit block references and reports corruption through `ext4_error_inode()`.

## Control flow

Mount or remount setup allocates a new `ext4_system_blocks`, iterates groups, and adds protected metadata ranges. Overlaps during construction are corruption unless they can be merged as contiguous same-owner ranges. Journal inode protection maps the journal file through `ext4_map_blocks()` and inserts each mapped extent tagged with the journal inode number. Only after successful construction is the tree published. Readers use `rcu_read_lock()`, walk the rb-tree by range comparisons, and return invalid on any overlap except permitted same-inode reserved zones.

## State and persistence behavior

The rb-tree is in-memory derived state; it is not persisted. Its inputs are persistent ext4 geometry and journal inode extents. The tree pointer in `ext4_sb_info->s_system_blks` is protected by `sb->s_umount` for updates and RCU for readers. Persistent corruption is reported but not repaired here.

## Dependencies and integration points

The file depends on ext4 geometry helpers from allocation code, group descriptor access, journal inode lookup, inode block mapping, rb-tree APIs, RCU, slab cache management, and ext4 error reporting. Indirect block and extent validation code can call `ext4_check_blockref()` or `ext4_inode_block_valid()` before trusting disk block references.

## Risks and edge cases

System-zone construction must cover all metadata placements, including sparse/meta_bg geometry and journal inode extents. Overlapping metadata ranges generally signal corruption and abort setup. RCU publication is essential: remount can disable block validity while readers still walk the old tree. The range check guards against start block before first data block, arithmetic wraparound, and ending beyond filesystem size.

## Test signals

Mount with block validity enabled/disabled, create images with overlapping bitmap/table/super ranges, corrupt indirect block references to metadata blocks, validate journal inode exceptions, test remount toggling under concurrent reads, run with sparse_super/meta_bg/bigalloc layouts, and inject allocation failures during tree construction.
