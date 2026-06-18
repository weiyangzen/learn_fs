# sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag_btree.c

## Purpose
`rcbag_btree.c` implements the in-memory btree operations used by `rcbag.c`. It defines record/key conversion, ordering, verification, cursor allocation, cache lifecycle, and record operations for refcount bag records.

## Important APIs, Types, And Functions
Public functions include `rcbagbt_mem_cursor`, `rcbagbt_mem_init`, `rcbagbt_maxrecs`, `rcbagbt_calc_size`, `rcbagbt_maxlevels_possible`, `rcbagbt_init_cur_cache`, `rcbagbt_destroy_cur_cache`, `rcbagbt_lookup_eq`, `rcbagbt_get_rec`, `rcbagbt_update`, and `rcbagbt_insert`. Internal btree ops include key/record init, comparisons, ordering checks, and buffer verification.

## Control Flow
The file defines `rcbagbt_mem_ops`, an `XFS_BTREE_TYPE_MEM` ops table backed by generic `xfbtree` block allocation, root setting, and cursor duplication. Cursor creation allocates an XFS btree cursor from a slab cache sized for the maximum possible height and attaches the target `xfbtree`. Record helpers populate `cur->bc_rec` and delegate lookup/insert/update to generic btree functions.

## State And Persistence Behavior
The btree stores records in memory buffers with XFS-like btree headers and verification but skips CRC checks for speed. The only global state is the cursor kmem cache. No on-disk filesystem metadata is written.

## Dependencies And Integration Points
It depends on `xfbtree`, `xfs_btree_mem`, buffer verification APIs, and the definitions in `rcbag_btree.h`. `rcbag.c` consumes its cursor and record helpers.

## Risks And Edge Cases
Incorrect ordering would break edge computation in `rcbag.c`. Max-level and max-record calculations must match the in-memory block size and header length. Verification rejects bad magic, v5 headers, too-high levels, and oversized record counts. The slab cache must be initialized before cursor allocation and destroyed at module shutdown.

## Test Signals
Tests should cover cursor cache lifecycle, insert/update/get/lookup behavior, ordering for equal startblock but different length records, maxlevels calculations for large record counts, and verifier rejection of malformed memory blocks.
