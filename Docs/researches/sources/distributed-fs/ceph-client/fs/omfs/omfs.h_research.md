# sources/distributed-fs/ceph-client/fs/omfs/omfs.h

Purpose: provides OMFS in-memory superblock state, cluster-to-block conversion, and cross-file function declarations shared by bitmap, directory, file, and inode code.

Important APIs and types: `struct omfs_sb_info` stores total blocks, bitmap/root inode locations, block and system-block sizes, mirror count, cluster size, block shift, in-memory bitmap array, bitmap lock, and mount uid/gid/masks. `clus_to_blk` scales OMFS cluster/block numbers to VFS block numbers using `s_block_shift`. `OMFS_SB` retrieves private superblock state. Declarations cover allocation, directory operations, file operations, block reading, inode allocation/loading, and sync.

Control flow: no active control flow beyond inline conversion/accessor helpers. The declared APIs define module boundaries: bitmap allocation is used by inode and file code; directory helpers initialize inode blocks; file helpers provide address-space operations; inode helpers own superblock and inode lifecycle.

State and persistence behavior: this header defines in-memory mount state only. Persistent structures come from `omfs_fs.h`, included here. `s_imap` mirrors allocation state from disk and is protected by `s_bitmap_lock`.

Dependencies and integration points: includes Linux module/fs headers and `omfs_fs.h`. It is the central internal contract among all OMFS translation units. The declarations `omfs_reserve_block` and `omfs_find_empty_block` are present but not implemented or used in this source set, likely stale prototypes.

Risks: `clus_to_blk` assumes `s_block_shift` was correctly derived from compatible power-of-two sizes at mount. Callers assume `OMFS_SB(sb)` is valid after mount setup. Stale extern declarations can mislead future maintainers or hide missing cleanup when refactoring.

Test signals: compile with sparse/W=1 for unused or stale prototypes, mount images with different system/data block-size ratios, allocation and mapping tests that verify `clus_to_blk`, and teardown tests confirming `s_imap` ownership.
