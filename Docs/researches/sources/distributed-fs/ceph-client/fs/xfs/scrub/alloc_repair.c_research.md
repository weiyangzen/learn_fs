# sources/distributed-fs/ceph-client/fs/xfs/scrub/alloc_repair.c

## Purpose
This file repairs the bnobt and cntbt simultaneously. It reconstructs free-space records by scanning reverse mappings for gaps and OWN_AG metadata, stages new free-space btrees with the newbt framework, updates AGF counters, and reaps blocks from the old allocation btrees.

## Important APIs, types, and functions
`struct xrep_abt` holds the repair state: bitmaps for old allocbt blocks and non-allocbt OWN_AG blocks, staged new bnobt/cntbt builders, an `xfarray` of free records, cursor position, free block counters, and longest extent. `xrep_setup_ag_allocbt` flushes busy extents before repair. `xrep_abt_find_freespace` scans rmapbt and AGFL data. `xrep_abt_reserve_space` reserves free extents for new btree blocks through an iterative geometry calculation. `xrep_abt_build_new_trees` sorts, reserves, bulk-loads cntbt and bnobt, commits staged roots, and resets AGF counters. `xrep_allocbt` is the repair entry point, and `xrep_revalidate_allocbt` re-scrubs both trees.

## Control flow and state
Repair requires rmapbt. It first ensures the busy extent list is empty to avoid double-use of blocks. Rmap walking records gaps as free records, records OWN_AG blocks as possible old allocbt blocks, and records rmapbt path blocks plus AGFL entries as blocks that must not be released. After subtracting the not-allocbt bitmap, remaining OWN_AG blocks are candidates for old bnobt/cntbt blocks. Free records are sorted by length to reserve btree blocks efficiently, may be shrunk or removed to satisfy staged btree reservations, then are sorted appropriately for cntbt and bnobt bulk loading.

## Persistence and integration
The new trees are installed via staged btree commit helpers, AGF fields `agf_btreeblks`, `agf_freeblks`, and `agf_longest` are logged, perag btree heights are reinitialized, and transaction rolls make new roots durable before old blocks are reaped. Rmap updates and free of unused reservations use deferred operations.

## Risks and test signals
The repair depends on rmap correctness and must handle reflink-overlapping rmap records. Reservation logic can consume free records and alter sorting, making off-by-one and ENOSPC behavior important. Tests should include maximally fragmented AGs, no-space repairs, reflink overlap gaps, AGFL-owned OWN_AG subtraction, stale btree block reaping, btree height changes that exercise alternate verifier heights, busy extent refusal, and revalidation of both trees after repair.
