# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc_btree.c

## Purpose
This file implements the XFS free-space btree operations for the by-block-number tree (bnobt) and by-count tree (cntbt). It defines cursor behavior, root updates, block allocation/free via the AGFL, key/record comparisons, verifiers, btree operation tables, staged-btree commit support, max record/level calculations, and cursor cache lifecycle.

## Important APIs and Functions
- Cursor constructors `xfs_bnobt_init_cursor` and `xfs_cntbt_init_cursor` allocate btree cursors, hold the perag group, attach AGF buffers, and set levels from AGF roots.
- `xfs_allocbt_set_root` updates AGF root/level fields and perag cached btree levels for either tree.
- `xfs_allocbt_alloc_block` gets new btree blocks from the AGFL, increments `m_allocbt_blks`, and marks busy extents reusable.
- `xfs_allocbt_free_block` returns btree blocks to the AGFL, decrements `m_allocbt_blks`, and records busy extents with discard skipped.
- Comparison helpers implement bnobt ordering by startblock and cntbt ordering by blockcount then startblock.
- `xfs_allocbt_verify`, read/write verifiers, and `xfs_bnobt_buf_ops`/`xfs_cntbt_buf_ops` validate magic, CRC, AG block headers, levels, and record capacity.
- `xfs_bnobt_ops` and `xfs_cntbt_ops` provide the generic btree core callbacks.
- `xfs_allocbt_commit_staged_btree` installs a rebuilt staged root into AGF and commits the fake root.
- `xfs_allocbt_maxrecs`, `xfs_allocbt_maxlevels_ondisk`, `xfs_allocbt_calc_size`, and cursor cache init/destroy support geometry and memory sizing.

## Control Flow
Allocator code creates bnobt/cntbt cursors and uses generic btree operations through the callback tables. When the btree core splits or joins blocks, allocation and free callbacks move blocks to/from AGFL and update global in-core allocbt block counters. Root changes update both persistent AGF fields and perag cached levels. Verifiers run on buffer read/write to reject corrupt btree blocks before use or persistence.

## State and Persistence Behavior
Persistent state includes free-space btree blocks, AGF root pointers and levels, and buffer checksums. In-core state includes btree cursors, held perag group references, cached btree levels, and the mount-wide `m_allocbt_blks` counter. Staged btrees support online repair/rebuild before atomically installing new roots.

## Dependencies and Integration Points
This file integrates with the generic XFS btree engine, AGFL allocator functions in `xfs_alloc.c`, busy extent tracking, health/sick masks, tracepoints, online repair staging, buffer verification, and perag/group references.

## Risks and Edge Cases
Verifier level checks must tolerate growfs/log-recovery contexts where perag state is unavailable, and online repair contexts where alternate repair heights may be valid. Misordered keys or wrong high-key construction breaks allocation searches. AGFL allocation failure must return `stat = 0` rather than corrupting the tree. Incorrect root updates desynchronize AGF from perag caches.

## Test Signals
Tests should cover bnobt/cntbt cursor operations, btree split/join with AGFL pressure, online repair staged root commit, corrupt magic/CRC/level/order records, growfs initialization contexts without attached perag, allocator behavior after btree block reuse, and slab cache lifecycle at module init/exit.
