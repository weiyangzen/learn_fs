# sources/distributed-fs/ceph-client/fs/ubifs/lprops.c

## Purpose

`lprops.c` manages UBIFS logical eraseblock properties and their fast lookup categories. Lprops record per-LEB free space, dirty space, flags such as index/taken/category, and aggregate space statistics. This file keeps category heaps/lists consistent so higher layers can quickly find empty LEBs, freeable LEBs, LEBs with free space, dirty data LEBs for GC, and dirty/freeable index LEBs.

## Important APIs, Types, And Functions

Category maintenance APIs include `ubifs_add_to_cat()`, `ubifs_replace_cat()`, `ubifs_ensure_cat()`, `ubifs_categorize_lprops()`, `ubifs_change_lp()`, `ubifs_change_one_lp()`, `ubifs_update_one_lp()`, `ubifs_read_one_lp()`, and `ubifs_get_lp_stats()`. Fast lookup APIs include `ubifs_fast_find_free()`, `ubifs_fast_find_empty()`, `ubifs_fast_find_freeable()`, and `ubifs_fast_find_frdi_idx()`. Debug validators include `dbg_check_cats()`, `dbg_check_heap()`, and `dbg_check_lprops()`.

Internal heap functions are `get_heap_comp_val()`, `move_up_lpt_heap()`, `adjust_lpt_heap()`, `add_to_lpt_heap()`, `remove_from_lpt_heap()`, and `lpt_heap_replace()`. They operate on `struct ubifs_lpt_heap` arrays and `struct ubifs_lprops::hpos`.

## Control Flow

`ubifs_categorize_lprops()` is the category policy. Taken LEBs are uncategorized. Fully free LEBs go to `LPROPS_EMPTY`. LEBs whose free plus dirty equals the full LEB size go to `LPROPS_FREEABLE` for data or `LPROPS_FRDI_IDX` for index. Index LEBs with enough reclaimable space go to `LPROPS_DIRTY_IDX`. Data LEBs with dirty space above the dead watermark and greater than free space go to `LPROPS_DIRTY`; otherwise LEBs with free space go to `LPROPS_FREE`; the rest are uncategorized.

`ubifs_change_lp()` is the central mutator. It ensures the lprops pnode is dirty/COW-safe, updates aggregate stats under `space_lock`, aligns free/dirty values to 8 bytes, adjusts empty/index/taken counters, removes and recalculates dead/dark/used accounting for non-index LEBs, recategorizes the LEB, updates `c->idx_gc_cnt`, and returns the possibly copied lprops pointer. Wrapper functions acquire/release lprops locking and look up by LEB number.

Heaps are bounded. If a category heap is full, `add_to_lpt_heap()` may replace a weaker bottom-half candidate; otherwise the new LEB becomes uncategorized. `ubifs_ensure_cat()` gives uncategorized LEBs another chance to enter a useful category when callers encounter them. Fast find helpers assume `c->lp_mutex` is held and return the top/list-head lprops for their category without scanning.

## State And Persistence Behavior

Lprops are persisted through the LPT, but this file manages the in-memory categorized view and aggregate `c->lst` counters used by budgeting, GC, and free-space allocation. Copy-on-write LPT behavior means a lprops pointer can change during `ubifs_change_lp()`, especially around commit. Dark and dead space accounting models unusable tail space so budgeting does not overpromise writes that may not fit future nodes.

## Dependencies And Integration Points

The file is used by journal reservation to find free space, GC to choose dirty/freeable LEBs, commit to update index/data LEB status, budgeting to read aggregate stats, and debug validation to compare lprops against actual media and TNC reachability. It depends on LPT lookup/scan functions, UBIFS scan, TNC node-existence checks, write-buffer sync during debug media scans, and global locks `lp_mutex` and `space_lock`.

## Risks And Edge Cases

Category and aggregate counter drift is the primary risk. A LEB must not appear in multiple categories, heaps must preserve `hpos`, and `freeable_cnt`, `idx_gc_cnt`, `empty_lebs`, `idx_lebs`, and total free/dirty/used/dead/dark counters must match actual lprops. Unclean unmounts complicate debug scans because empty/freeable LEBs may contain stale garbage and index LEB free space may differ due to in-the-gaps commit behavior. Heap overflow intentionally degrades to uncategorized, so callers must handle misses from fast helpers.

## Test Signals

Good signals include lprops mutation under GC, commit, journal allocation, and index GC; category heap overflow; transitions among empty/free/freeable/dirty/index/taken states; debug `dbg_check_lprops()` after syncing write buffers; power-cut recovery with stale empty/freeable LEB content; and budget/free-space tests that compare aggregate counters to scanned media.
