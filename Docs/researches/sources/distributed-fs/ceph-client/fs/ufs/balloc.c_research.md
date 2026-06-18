# sources/distributed-fs/ceph-client/fs/ufs/balloc.c

## Purpose
`balloc.c` implements UFS fragment and block allocation/freeing, including cylinder-group bitmap updates, fragment accounting, cluster accounting, partial-fragment growth, page-cache block-number migration, and free-space search heuristics.

## Important APIs, types, and functions
Public functions are `ufs_free_fragments`, `ufs_free_blocks`, and `ufs_new_fragments`. Key internals are `adjust_free_blocks`, `ufs_change_blocknr`, `ufs_clear_frags`, `try_add_frags`, `ufs_add_fragments`, `ufs_alloc_fragments`, `ufs_alloccg_block`, `ubh_scanc`, `ufs_bitmap_search`, `ufs_clusteracct`, and fragment search tables.

## Control flow
Free paths lock `s_lock`, locate the cylinder group, validate magic and bit state, set free bits, update fragment/block summaries, mark super/cylinder buffers dirty, and optionally sync. Allocation first enforces root-reserved space, chooses a preferred cylinder group from goal or parent inode, tries direct allocation in that group, then quadratic and linear fallback. Partial tail growth first tries adjacent fragments; if unavailable, it allocates a new block/fragment run, moves dirty page-cache buffer mappings from old blocks to new blocks, frees old fragments, and updates inode block pointers under `meta_lock`.

## State and persistence
Persistent state includes UFS free bitmaps, cylinder group summaries, superblock summary totals, inode `i_blocks`, inode block pointers, allocation rotors, cluster summaries, and dirty superblock state. Runtime state includes page-cache buffer mappings and allocation goals.

## Dependencies and integration points
It depends on `ufs_load_cylinder`, `util.h` bitmap/endian helpers, `UFS_I(inode)->meta_lock`, buffer-head I/O, capabilities for reserved blocks, and inode mapping operations in `inode.c`.

## Risks and test signals
Risks include bitmap/summary counter divergence, incorrect fragment reassembly, 32-bit `i_blocks` overflow guarded by `try_add_frags`, page-cache aliasing during block moves, and weak coverage because write support is experimental. Test signals include allocating direct and indirect blocks, growing short tails, ENOSPC with/without `CAP_SYS_RESOURCE`, freeing whole blocks across cylinder group boundaries, synchronous mounts, and fsck comparison after write workloads.
