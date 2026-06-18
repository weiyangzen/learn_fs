# sources/distributed-fs/ceph-client/fs/gfs2/rgrp.c

## Purpose
`rgrp.c` implements GFS2 resource group discovery, bitmap interpretation, block allocation, block freeing, multi-block reservations, rindex refresh, FITRIM/discard, and resource-group consistency checks. It is the allocator core for data, metadata, dinodes, xattr blocks, and inode deletion cleanup.

## Important APIs, Types, And Functions
The internal `struct gfs2_rbm` identifies a bitmap position by resource group, bitmap-block index, and bitmap-relative offset. `struct gfs2_extent` records the best candidate free extent during scanning. Exported entry points include `gfs2_rindex_update`, `gfs2_blk2rgrpd`, `gfs2_rgrp_go_instantiate`, `gfs2_inplace_reserve`, `gfs2_alloc_blocks`, `__gfs2_free_blocks`, `gfs2_free_meta`, `gfs2_unlink_di`, `gfs2_free_di`, `gfs2_check_blk_type`, `gfs2_rlist_*`, `gfs2_rgrp_send_discards`, and `gfs2_fitrim`.

The bitmap helpers `gfs2_setbit`, `gfs2_testbit`, `gfs2_bit_search`, `gfs2_bitfit`, `gfs2_rbm_from_block`, `gfs2_rbm_add`, and `gfs2_rbm_find` translate between on-disk two-bit block states and filesystem block numbers. Reservation helpers (`rs_cmp`, `rs_insert`, `gfs2_rs_deltree`, `rg_mblk_search`, `gfs2_reservation_check_and_update`) maintain an rbtree of reserved block ranges per resource group.

## Control Flow
Resource groups are discovered by reading the rindex inode through `gfs2_rindex_update` -> `gfs2_ri_update` -> `read_rindex_entry`. Each entry allocates a `gfs2_rgrpd`, computes per-bitmap-block descriptors, obtains an rgrp glock, and inserts the descriptor into `sd_rindex_tree`. `set_rgrp_preferences` spreads preferred rgrps across journals to reduce cluster lock contention.

Allocation starts with `gfs2_inplace_reserve`. It chooses a starting rgrp from the inode goal or existing reservation, skips busy or non-preferred groups in early passes, acquires the rgrp glock, optionally refreshes from the lock value block, searches or creates a reservation, reclaims unlinked dinodes if needed, and falls back to `min_target` after log flush. `gfs2_alloc_blocks` then searches the reservation or rgrp bitmap, updates bitmap bits, reservation accounting, rgrp header/LVB, statfs, quota, inode goal, and revoke state.

Freeing uses `rgblk_free` to clone bitmap bytes before modifying states, then updates rgrp counts and journal state through `__gfs2_free_blocks`, `gfs2_free_meta`, `gfs2_unlink_di`, and `gfs2_free_di`. FITRIM walks rgrps under exclusive rgrp glocks, sends discards for free extents, and marks rgrps trimmed in a transaction.

## State And Persistence
Persistent state is in rindex entries, rgrp header blocks, rgrp bitmap blocks, and optionally rgrp LVBs. In-memory state includes `sd_rindex_tree`, `rd_bits`, `rd_free`, `rd_free_clone`, `rd_reserved`, `rd_requested`, `rd_rstree`, `rd_extfail_pt`, `rd_last_alloc`, and flags such as `GFS2_RDF_CHECK`, `GFS2_RGF_TRIMMED`, and `GFS2_RDF_ERROR`. Bitmap clone buffers delay reuse of newly freed blocks until the clone is discarded. All on-disk rgrp/bitmap updates are added to GFS2 transactions before mutation.

## Dependencies And Integration Points
This file is tightly coupled to glocks (`glock.h`, `glops.h`), metadata I/O, transactions, logging/revokes, quota, statfs, inode update paths, directory delete verification, tracepoints, and Linux block discard APIs. xattr and file deallocation paths rely on `gfs2_rlist_*`, `gfs2_inplace_reserve`, `gfs2_alloc_blocks`, and `gfs2_free_meta`.

## Risks And Edge Cases
Important risks are bitmap/rgrp count divergence, reservation-tree overlap, allocation under stale LVB state, wraparound in bitmap scans, rindex growth races, discard errors disabling mount-time discard, and unlinked dinode cleanup racing with inode cache state. Error paths often mark the rgrp readonly until unmount or withdraw the filesystem, so false positives are high-impact but protect metadata integrity.

## Test Signals
Useful signals include allocation/free tracepoints (`gfs2_block_alloc`, `gfs2_rs`), statfs consistency after allocations and frees, fsck clean runs after stress, FITRIM return ranges, ENOSPC behavior with fragmented rgrps, xfstests covering unlink/recreate and quota accounting, and multi-node allocation contention tests with rgrp LVB enabled and disabled.
