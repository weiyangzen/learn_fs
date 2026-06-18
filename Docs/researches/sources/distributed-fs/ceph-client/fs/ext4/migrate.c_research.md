# sources/distributed-fs/ceph-client/fs/ext4/migrate.c

## Purpose
`migrate.c` implements conversion between ext4's legacy indirect block mapping and extent-based mapping. `ext4_ext_migrate()` converts an indirect-mapped regular file to extents by building an equivalent extent tree in a temporary inode, swapping the original inode's `i_data`, and freeing old indirect metadata. `ext4_ind_migrate()` performs the limited reverse conversion from a simple extent file to direct `i_data[]` block pointers.

## Important APIs, Types, And Functions
`struct migrate_struct` tracks the current contiguous logical-to-physical run. Forward migration helpers are `update_extent_range()`, `finish_range()`, `update_ind_extent_range()`, `update_dind_extent_range()`, and `update_tind_extent_range()`. Cleanup and swap helpers include `free_dind_blocks()`, `free_tind_blocks()`, `free_ind_block()`, `ext4_ext_swap_inode_data()`, `free_ext_idx()`, and `free_ext_block()`. Public functions are `ext4_ext_migrate()` and `ext4_ind_migrate()`.

## Control Flow
`ext4_ext_migrate()` rejects unsupported inodes, takes writepages serialization, creates a hidden temporary inode, gives it the source inode checksum seed, initializes an extent tree, and sets `EXT4_STATE_EXT_MIGRATE`. It scans direct, indirect, double-indirect, and triple-indirect mappings, coalescing contiguous physical/logical runs into extents inserted into the temporary inode. On success, `ext4_ext_swap_inode_data()` verifies the migrate flag, sets `EXT4_INODE_EXTENTS`, copies the temporary extent tree into the original inode, adjusts `i_blocks`, frees old indirect metadata, and marks the inode dirty. On failure it frees temporary extent metadata and resets the temporary inode before dropping it.

`ext4_ind_migrate()` rejects unsupported filesystems, non-extent inodes, and bigalloc. It forces delayed allocation blocks out, disables fast commit for the transaction, validates the extent tree, and only accepts an empty tree or a single depth-zero extent that fits inside direct blocks. It clears the extent flag, zeros `i_data`, writes direct physical block pointers, and dirties the inode.

## State And Persistence Behavior
Both migrations are journaled as `EXT4_HT_MIGRATE` and mark fast commit ineligible. Forward migration uses the temporary inode as a durable staging area and uses `EXT4_STATE_EXT_MIGRATE` as the race detector for concurrent block allocation. Old indirect metadata is freed with metadata/forget flags; temporary extent metadata is recursively freed on failure. The checksum seed transfer is required so extent metadata remains valid after `i_data` is copied to the source inode.

## Dependencies And Integration Points
The file depends on `ext4_jbd2.h`, `ext4_extents.h`, extent insertion/checking APIs, journal credit helpers, inode creation, quota-aware allocation, `ext4_free_blocks()`, buffer reads, writeback serialization, delayed allocation flushing, checksum seeds, and fast-commit ineligibility marking.

## Risks And Edge Cases
Risks include races with mmap or other block allocation, incorrect logical advancement through sparse indirect trees, journal credit exhaustion during repeated extent insertion/freeing, incomplete cleanup of temporary extent metadata, checksum-seed mismatch, and callers expecting general reverse migration even though only simple direct-range extent files are supported.

## Test Signals
Tests should cover direct-only files, sparse indirect files, fragmented and contiguous runs, single/double/triple indirect coverage, insertion/free failures, concurrent allocation returning `-EAGAIN`, checksum-enabled filesystems, quota behavior, temp-inode cleanup, reverse migration for empty and one-extent direct files, and reverse rejection for bigalloc, depth, multiple extents, or extents beyond direct blocks.
