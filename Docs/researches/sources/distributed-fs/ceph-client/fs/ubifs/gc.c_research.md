# sources/distributed-fs/ceph-client/fs/ubifs/gc.c

## Purpose

`gc.c` implements UBIFS out-of-place garbage collection for main-area logical eraseblocks (LEBs). It treats data LEBs and index LEBs differently: data LEB GC copies still-live data, inode, directory-entry, and xattr-entry nodes to the GC journal head and updates the TNC to point at the new locations; index LEB GC marks index nodes dirty in the TNC and defers physical reuse until a subsequent commit has made recovery safe. The file also manages the GC journal head, retained GC LEB state, and the list of index LEBs that were logically freed but cannot yet be unmapped.

## Important APIs, Types, And Functions

The externally used entry points are `ubifs_garbage_collect_leb()`, `ubifs_garbage_collect()`, `ubifs_gc_start_commit()`, `ubifs_gc_end_commit()`, `ubifs_destroy_idx_gc()`, and `ubifs_get_idx_gc_leb()`. Internally, `switch_gc_head()` turns `c->gc_lnum` into a bud on journal head `GCHD`, `sort_nodes()` filters obsolete scanned nodes and orders live nodes for better read locality, `move_node()` writes one node to the GC head and replaces its TNC location, `move_nodes()` drains live nodes into the GC head, and `gc_sync_wbufs()` flushes other journal heads before old LEBs are unmapped.

The file uses `struct ubifs_scan_leb` and `struct ubifs_scan_node` from the scan layer, `struct ubifs_lprops` from the LPT/lprops layer, `struct ubifs_wbuf` from the I/O layer, and `struct ubifs_gced_idx_leb` entries on `c->idx_gc`. The important return protocol distinguishes `LEB_FREED`, `LEB_RETAINED`, and `LEB_FREED_IDX`, plus negative errors such as `-EAGAIN`, `-ENOSPC`, `-EROFS`, and media or allocation failures.

## Control Flow

The main GC loop in `ubifs_garbage_collect()` runs under the commit lock and the GC write-buffer mutex. It first refuses to proceed if a commit is already needed, then repeatedly asks lprops for a dirty or empty/freeable LEB with `ubifs_find_dirty_leb()`. Each selected LEB is passed to `ubifs_garbage_collect_leb()`. A ready freed LEB is returned to the caller by number; a retained LEB becomes `c->gc_lnum`; a freed index LEB only becomes usable after commit, so the loop may continue until soft/hard iteration limits request commit or report no progress.

For a data LEB, `ubifs_garbage_collect_leb()` scans the whole LEB, calls `move_nodes()`, synchronizes non-GC write buffers so obsoleting writes are stable, updates lprops to fully free/clean state, updates `c->gced_lnum` and `c->gc_seq` with memory barriers for TNC race handling, and either retains the LEB as the next GC head or unmaps it. `move_nodes()` sorts live data nodes by inode/block and non-data nodes by inode/hash/size, writes what fits into the GC head, emits authentication nodes when needed, and switches the GC head when necessary.

For an index LEB, `ubifs_garbage_collect_leb()` reads each index node key and level, calls `ubifs_dirty_idx_node()` so the TNC will rewrite it, records the LEB on `c->idx_gc`, and changes lprops to free-space accounting with index status cleaned and `idx_gc_cnt` incremented. `ubifs_gc_start_commit()` unmaps immediately freeable non-index LEBs, marks already-GCed index LEBs as eligible for post-commit unmap, and moves freeable dirty index LEBs to `c->idx_gc`. `ubifs_gc_end_commit()` finally unmaps eligible index LEBs and updates lprops to clear `LPROPS_TAKEN`.

## State And Persistence Behavior

GC is tied to persistent safety. Data nodes are never discarded until their replacements are written to the GC journal head and TNC entries have been replaced. Other write buffers are synchronized before unmapping a freeable/data LEB because they may contain nodes that obsolete content in the LEB being collected. Index LEBs are not physically released until commit has made the new index state durable, preserving recovery from old index nodes after an unclean unmount.

The main mutable state is `c->gc_lnum`, `c->jheads[GCHD].wbuf`, `c->idx_gc`, `c->idx_gc_cnt`, lprops free/dirty/index/taken flags, and TNC node locations. Authentication state is updated through `ubifs_shash_update()` on moved nodes and by writing `UBIFS_AUTH_NODE` records to the GC head; the auth node itself is accounted as dirty with `ubifs_add_dirt()`.

## Dependencies And Integration Points

This file integrates with the lprops allocator (`ubifs_find_dirty_leb()`, `ubifs_change_one_lp()`, `ubifs_return_leb()`), log/journal management (`ubifs_add_bud_to_log()`), write-buffer I/O (`ubifs_wbuf_sync_nolock()`, `ubifs_wbuf_seek_nolock()`, `ubifs_wbuf_write_nolock()`), raw UBI operations (`ubifs_leb_unmap()`), scanning (`ubifs_scan()`), key helpers (`key_type()`, `key_inum()`, `key_block()`, `key_hash()`, `key_read()`), TNC mutation (`ubifs_tnc_has_node()`, `ubifs_tnc_replace()`, `ubifs_dirty_idx_node()`), and commit orchestration.

## Risks And Edge Cases

The riskiest paths are partial-progress failures after live nodes have moved, handling `-EAGAIN` without losing a taken lprops entry, and the ordering between write-buffer synchronization, lprops changes, TNC replacement, and LEB unmap. The soft and hard LEB limits defend against pathological no-progress loops, but callers still must handle repeated `-EAGAIN` when nearly full or under tight journal limits. Authentication adds another fitting constraint because `ubifs_auth_node_sz(c)` is subtracted from available GC-head space. The `c->gced_lnum`/`c->gc_seq` barrier protocol is a race-sensitive integration with TNC lookups.

## Test Signals

Useful test signals include GC under low-space workloads, repeated commit-required GC loops, data LEBs containing mixed live/obsolete nodes, index LEB GC followed by power-cut recovery, authenticated mounts, write-buffer error injection, and debug checks such as node order checks, lprops checks, and TNC consistency checks. Expected behavior is that freed LEBs are returned only when safe, index GC is completed after commit, and media write/unmap failures switch UBIFS read-only through the lower I/O path.
