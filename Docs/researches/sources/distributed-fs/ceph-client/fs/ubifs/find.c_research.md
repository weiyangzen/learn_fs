# sources/distributed-fs/ceph-client/fs/ubifs/find.c

## Purpose
`find.c` selects logical eraseblocks for UBIFS allocation, garbage collection, and index commit work. It searches lprops heaps/lists first, falls back to LPT scans when necessary, marks chosen LEBs as taken, and maintains the dirty-index LEB list used by in-the-gaps index commit.

## Important APIs, Types, and Functions
- `struct scan_data` carries scan criteria and the selected LEB number.
- `valuable()` decides whether lprops found during scans should be cached in memory.
- Dirty-space selection: `scan_for_dirty_cb()`, `scan_for_dirty()`, and `ubifs_find_dirty_leb()`.
- Data free-space selection: `scan_for_free_cb()`, `do_find_free_space()`, and `ubifs_find_free_space()`.
- Index free-LEB selection: `scan_for_idx_cb()`, `scan_for_leb_for_idx()`, and `ubifs_find_free_leb_for_idx()`.
- Dirty-index reuse: `cmp_dirty_idx()`, `ubifs_save_dirty_idx_lnums()`, `scan_dirty_idx_cb()`, `find_dirty_idx_leb()`, `get_idx_gc_leb()`, `find_dirtiest_idx_leb()`, and `ubifs_find_dirty_idx_leb()`.

## Control Flow
Dirty GC selection optionally tries empty/freeable LEBs when the caller allows it and index reservations are safe. It then compares the dirty and dirty-index heaps, preferring the LEB with most free+dirty space while avoiding reserved index LEBs. If heaps and in-memory lists fail, it scans the LPT from `c->lscan_lnum`, adds valuable lprops to memory, and returns a matching LEB. The selected lprops is updated with `LPROPS_TAKEN`.

Free-space selection calculates whether empty LEBs may be consumed without violating minimum index reservations. It may temporarily increments `taken_empty_lebs` under `space_lock` before dropping the lock, then looks for empty, free, dirty-heap, uncategorized, or scanned LPT candidates. Empty or freeable LEBs selected for writing are unmapped before use.

Index allocation only accepts empty/freeable LEBs because commit assumes empty index LEBs and cannot trust free tails after unclean unmount. It marks selected LEBs as both `LPROPS_TAKEN` and `LPROPS_INDEX`, then unmaps them; on unmap failure it clears those flags.

Dirty-index reuse snapshots the dirty-index heap at commit start, sorts by dirty+free space, converts pointers to LEB numbers, then later tries those saved LEBs, a full dirty-index scan, and finally trivial index-GC LEBs.

## State and Persistence Behavior
The file mutates in-memory and on-flash lprops through `ubifs_change_lp()` and `ubifs_change_one_lp()`, updates `c->lscan_lnum`, manipulates `taken_empty_lebs`, consumes `c->dirty_idx`, and may unmap UBI LEBs. Its choices affect persistent allocation layout, GC behavior, commit index placement, and space budgeting accuracy.

## Dependencies and Integration Points
It depends on the LPT/lprops subsystem, lprops category heaps/lists, budgeting counters in `c->bi` and `c->lst`, UBI unmap through UBIFS wrappers, `space_lock`, and index GC helpers. It is used by journal reservation/allocation, garbage collection, and commit/TNC index writing.

## Risks and Edge Cases
- Index reservation logic must avoid stealing LEBs needed for commit; errors can cause later `-ENOSPC` or commit failure.
- `taken_empty_lebs` is adjusted optimistically while locks are dropped; every error path must undo it.
- LPT scanning is skipped when all pnodes are already loaded, so heap/list categorization accuracy matters.
- Free+dirty LEBs are excluded for normal data allocation because they may be unmapped or contain obsolete data still referenced by write buffers.
- Dirty-index saved arrays store LEB numbers cast through `void *`, so users must remember the array no longer contains lprops pointers after `ubifs_save_dirty_idx_lnums()`.

## Test Signals
Exercise GC dirty LEB selection with and without `pick_free`, index reservation pressure, empty/freeable/free/dirty/uncategorized category transitions, LPT scan fallback, unmap failure rollback, dirty-index commit reuse, trivial index GC fallback, and low-space races involving `taken_empty_lebs`.
