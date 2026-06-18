# sources/distributed-fs/ceph-client/fs/ubifs/tnc_commit.c

## Purpose
`tnc_commit.c` implements the TNC-specific portion of UBIFS commit. It selects dirty znodes, assigns new on-flash positions, optionally reuses holes left by obsolete index nodes, writes new index nodes, updates index-head state, and frees obsolete in-memory znodes after commit. Its core invariant is that the old committed index remains intact until the new committed index is durably written.

## Important APIs, Types, And Functions
`ubifs_tnc_start_commit()` is the start-commit entry point. It checks the TNC, builds the circular dirty-znode commit list with `get_znodes_to_commit()`, allocates empty index LEBs via `alloc_idx_lebs()`, lays out dirty znodes through `layout_commit()`, updates budgeting/index-size state, destroys previous old-index records, returns the new root zbranch, and saves dirty index LEB numbers.

Layout helpers include `layout_in_empty_space()`, `layout_in_gaps()`, `layout_leb_in_gaps()`, `fill_gap()`, `is_idx_node_in_use()`, and `get_leb_cnt()`. `make_idx_node()` materializes an index node into a gap and updates parent/root zbranches and hashes under the TNC mutex. `write_index()` writes nodes placed in empty space and clears dirty/COW flags with memory barriers. `ubifs_tnc_end_commit()` returns temporary gap LEBs, writes the index, frees obsolete znodes, frees allocated LEB arrays, and clears `c->cnext`.

## Control Flow
Start commit locks `c->tnc_mutex`, finds all dirty znodes in a deterministic dirty traversal, marks them `COW_ZNODE`, and chains them through `cnext`. It estimates required empty LEBs and asks lprops for index LEBs. If insufficient empty space exists, it scans dirty index LEBs and fills gaps where obsolete index nodes can be safely overwritten. Remaining nodes are assigned to empty index-head space or newly allocated index LEBs. Lprops and index size accounting are updated before the wider commit proceeds.

End commit first clears `LPROPS_TAKEN` from in-gap LEBs. `write_index()` then rebuilds each index node in the commit buffer, updates branch hashes in both commit-parent and live-parent views, verifies the planned location matches the actual write position, clears `DIRTY_ZNODE` before `COW_ZNODE`, writes aligned buffers to flash, and advances `c->ihead_lnum`/`c->ihead_offs`. Finally, under `tnc_mutex`, obsolete znodes are freed and non-obsolete committed znodes are returned to clean-count accounting.

## State And Persistence
Persistent outputs are new UBIFS index nodes written to index LEBs and the root zbranch later recorded by the broader commit machinery. Temporary in-memory commit state includes `c->cnext`, `c->enext`, `c->ilebs`, `c->ileb_cnt`, `c->ileb_nxt`, `c->gap_lebs`, `c->calc_idx_sz`, and debug new-index-head positions. Lprops state is updated for free/dirty/taken/index flags. The old-index RB-tree from `tnc.c` is consumed to avoid overwriting nodes still needed for recovery.

## Dependencies And Integration Points
This file uses scanner output from `scan.c` to inspect index LEB gaps, TNC old-index lookup from `tnc.c`, lprops allocation and accounting APIs, UBIFS node preparation/hash helpers, index node sizing helpers, debug check hooks, and write APIs (`ubifs_leb_change`, `ubifs_leb_write`). The broader `commit.c` calls `ubifs_tnc_start_commit()` and `ubifs_tnc_end_commit()` around master/log commit work.

## Risks And Edge Cases
Power-cut safety depends on not overwriting old-index nodes that are still part of the last committed index. The in-the-gaps method must correctly distinguish obsolete, dirty-old, and clean-in-use index nodes. `c->lst.idx_lebs` can grow while selecting dirty index LEBs, so `gap_lebs` may need dynamic enlargement. Dirty/clean znode counters are intentionally updated at different phases; temporary negative clean counts must be tolerated by the shrinker. Clearing dirty/COW flags without the required ordering can cause redundant copies or missed copy-on-write during concurrent TNC mutations.

## Test Signals
Signals include commits with no dirty znodes, commits fitting in current index head, commits needing new empty index LEBs, forced `-ENOSPC` into in-the-gaps layout, gap filling around clean in-use and dirty old nodes, LEB accounting after no nodes fit a selected gap, commit failure before end-commit cleanup, dirty/clean znode counter balance, index-head consistency checks, power-cut recovery using the old index, and debug mode forcing in-the-gaps behavior.
