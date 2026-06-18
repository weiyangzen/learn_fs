# sources/distributed-fs/ceph-client/fs/ufs/inode.c

## Purpose
`inode.c` implements UFS block mapping, address-space operations, inode read/writeback for UFS1 and UFS2, eviction, truncation, and setattr. It is the bridge between VFS pagecache I/O and UFS direct/indirect fragment allocation.

## Important APIs, types, and functions
Exported objects/functions are `ufs_aops`, `ufs_prepare_chunk`, `ufs_iget`, `ufs_write_inode`, `ufs_sync_inode`, `ufs_evict_inode`, `ufs_setattr`, and `ufs_file_inode_operations`. Key internals include `ufs_block_to_path`, `ufs_frag_map`, `ufs_extend_tail`, `ufs_inode_getfrag`, `ufs_inode_getblock`, `ufs_getfrag_block`, `ufs_set_inode_ops`, `ufs1_read_inode`, `ufs2_read_inode`, `ufs1_update_inode`, `ufs2_update_inode`, `ufs_update_inode`, `ufs_trunc_direct`, `free_full_branch`, `free_branch_tail`, `ufs_alloc_lastblock`, `ufs_truncate_blocks`, and `ufs_truncate`.

## Control flow
Read mapping computes a direct/single/double/triple-indirect path, follows pointers under `meta_lock` sequence protection, and maps physical fragments. Write mapping serializes creation with `truncate_mutex`, extends short direct tails when needed, allocates direct or indirect fragment runs via `ufs_new_fragments`, marks new buffers, and updates inode dirty state. Address-space operations call these paths for read folio, writepages, write begin/end, and bmap.

Inode read validates inode number, reads the inode block, decodes UFS1 or UFS2 fields, copies block pointers or fast symlink data, initializes last-fragment and ops. Writeback encodes inode fields back, clearing deleted inodes. Eviction truncates data for unlinked files, writes the cleared inode, then frees the inode bitmap. Truncation allocates the final partial block if needed, truncates pagecache, frees direct and indirect branches beyond EOF, updates `i_lastfrag`, times, and dirty state.

## State and persistence
Persistent state includes inode mode/link/uid/gid/size/times/blocks/generation/flags, direct and indirect block pointers, fast symlink bytes, device numbers, allocated fragments, and freed branch blocks. Runtime state includes `i_lastfrag`, `i_dir_start_lookup`, `meta_lock`, `truncate_mutex`, pagecache buffers, and mapping ops.

## Dependencies and integration points
It depends on `balloc.c` for block allocation/freeing, `util.h` for pointer/endian/device helpers, `dir.c` for directory chunk preparation, `file.c` operations, namei operation tables, buffer-head/pagecache APIs, and UFS superblock geometry/format flags.

## Risks and test signals
Risks include direct/indirect path arithmetic overflow, stale reads during concurrent pointer updates, tail-fragment growth and relocation bugs, missing `s_sbbase` in read/write asymmetry, truncation leaks or double frees, UFS1/UFS2 field mismatch, and fast-symlink versus block-backed symlink confusion. Test signals include sparse reads, direct/single/double/triple indirect writes, truncate up/down at fragment and block boundaries, fast and long symlinks, UFS1/UFS2 inode round trips, eviction of unlinked open files, and fsck after write/truncate workloads.
