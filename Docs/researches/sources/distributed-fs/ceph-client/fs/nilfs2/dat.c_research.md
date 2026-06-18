# sources/distributed-fs/ceph-client/fs/nilfs2/dat.c

## Purpose
`dat.c` implements the NILFS disk address translation metadata file. It maps virtual block numbers to physical block numbers and checkpoint lifetimes, allocates/frees virtual entries through the persistent allocator, supports copy-on-write updates during log construction, and provides shadow-map behavior needed by GC and recovery-safe translation.

## Important APIs and functions
- `struct nilfs_dat_info` embeds generic metadata state, a persistent allocator cache, and a shadow map.
- Prepare/commit/abort helpers include `nilfs_dat_prepare_alloc()`, `nilfs_dat_commit_alloc()`, `nilfs_dat_abort_alloc()`, `nilfs_dat_prepare_start()`, `nilfs_dat_commit_start()`, `nilfs_dat_prepare_end()`, `nilfs_dat_commit_end()`, `nilfs_dat_abort_end()`, `nilfs_dat_prepare_update()`, `nilfs_dat_commit_update()`, and `nilfs_dat_abort_update()`.
- `nilfs_dat_mark_dirty()` dirties the entry block containing a virtual block number.
- `nilfs_dat_freev()` frees arrays of virtual block numbers.
- `nilfs_dat_move()` changes the physical block for an existing virtual block, freezing the old buffer before exposing uncommitted movement.
- `nilfs_dat_translate()` resolves a virtual block number to a physical block number, using a frozen buffer for non-GC readers when the live entry is redirected.
- `nilfs_dat_get_vinfo()` returns lifetime and block-number information for arrays of `nilfs_vinfo`.
- `nilfs_dat_read()` initializes and reads the DAT inode, allocator cache, shadow map, btnode cache, and raw inode.

## Control flow
Allocation first reserves a palloc entry, then gets/creates the entry block. Commit initializes a full lifetime `[NILFS_CNO_MIN, NILFS_CNO_MAX)` with no physical block yet, commits the allocator entry, marks the entry block dirty, and marks DAT dirty. Starting a block write records the current checkpoint number and physical block. Ending a lifetime validates start <= current checkpoint, optionally prepares allocator free if the physical block is still zero, and sets `de_end` either to the current checkpoint or to `de_start` for dead entries.

Updates compose end of the old virtual entry and allocation of a new one. B-tree and direct propagation use this to preserve log-structured copy-on-write semantics: old virtual addresses remain valid for older checkpoints while new writes receive new virtual entries.

`nilfs_dat_move()` handles cleaner movement. Before changing `de_blocknr`, it freezes the entry buffer into the metadata shadow map and marks the live buffer redirected. `nilfs_dat_translate()` returns frozen data for normal readers while GC is not active, avoiding exposure of an uncommitted new block number.

## State and persistence behavior
Each `struct nilfs_dat_entry` stores `de_start`, `de_end`, and `de_blocknr`. The palloc bitmap/descriptors track allocated virtual block entries. DAT itself is a metadata inode with bmap and B-tree node cache. Shadow-map state is in-memory but protects consistency until segment construction either commits or restores metadata pages.

## Dependencies and integration points
DAT depends on `mdt.c` for metadata blocks and shadow maps, `alloc.c` persistent allocation, `btnode.c` for DAT bmap node caches, and bmap users in `direct.c`, `btree.c`, `inode.c`, `gcinode.c`, and `ioctl.c`. `nilfs_get_block()` takes the DAT metadata semaphore during lookups so virtual translations are stable.

## Risks and invariants
Virtual block entries with `de_blocknr == 0` cannot translate. Start checkpoint must not exceed current checkpoint. A free commit without palloc descriptor/bitmap buffers indicates duplicate virtual block use. Failing to use frozen buffers during `nilfs_dat_move()` could expose uncommitted GC movement. Update prepare paths must abort both old and new requests on failure.

## Test signals
Exercise virtual block allocation/start/end/update, translate of live and dead entries, GC move with redirected/frozen buffers, free arrays from cleanerd, `GET_VINFO`, corruption cases with invalid lifetimes or zero block numbers, and mount-time validation of DAT entry size.
