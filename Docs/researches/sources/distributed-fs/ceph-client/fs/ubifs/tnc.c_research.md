# sources/distributed-fs/ceph-client/fs/ubifs/tnc.c

## Purpose
`tnc.c` implements the UBIFS Tree Node Cache, the in-memory cache and mutation layer for UBIFS indexing B-tree nodes. It handles lookup, insertion, replacement, removal, range deletion, hash-collision resolution, leaf-node caching, GC race handling, old-index tracking for recovery, and debug validation. It is the main authority for mapping UBIFS keys to on-flash node locations.

## Important APIs, Types, And Functions
Old-index tracking uses `insert_old_idx()`, `insert_old_idx_znode()`, `ins_clr_old_idx_znode()`, and `destroy_old_idx()` to preserve references to index nodes that belonged to the last committed index but may no longer be discoverable by key. Copy-on-write and dirtying are handled by `copy_znode()`, `dirty_cow_znode()`, `dirty_cow_bottom_up()`, `replace_znode()`, and `add_idx_dirt()`.

Lookup primitives include `ubifs_lookup_level0()`, `lookup_level0_dirty()`, `tnc_next()`, `tnc_prev()`, `get_znode()`, `ubifs_tnc_locate()`, `ubifs_tnc_lookup_nm()`, `ubifs_tnc_lookup_dh()`, and `ubifs_tnc_next_ent()`. Hash-collision helpers are `matches_name()`, `resolve_collision()`, `fallible_matches_name()`, `fallible_resolve_collision()`, `resolve_collision_directly()`, `search_dh_cookie()`, and `do_lookup_dh()`. Leaf node caching is managed by `lnc_add()`, `lnc_add_directly()`, `lnc_free()`, and `tnc_read_hashed_node()`.

Mutation APIs are `ubifs_tnc_add()`, `ubifs_tnc_add_nm()`, `ubifs_tnc_replace()`, `ubifs_tnc_remove()`, `ubifs_tnc_remove_nm()`, `ubifs_tnc_remove_dh()`, `ubifs_tnc_remove_range()`, and `ubifs_tnc_remove_ino()`. Bulk read APIs are `ubifs_tnc_get_bu_keys()` and `ubifs_tnc_bulk_read()`. GC/debug integration includes `ubifs_tnc_has_node()`, `ubifs_dirty_idx_node()`, `is_idx_node_in_tnc()`, and `dbg_check_inode_size()`. Cleanup is `ubifs_tnc_close()`.

## Control Flow
Lookups acquire `c->tnc_mutex`, lazily load missing znodes from flash via `ubifs_load_znode()`, binary-search zbranches, and descend to level 0. Non-hashed unique keys can often drop `tnc_mutex` before reading the leaf node, then retry safely if GC may have moved the LEB. Hashed dent/xent keys keep the mutex while resolving collisions by comparing names or double-hash cookies and may use the leaf-node cache.

Mutations use `lookup_level0_dirty()` to load and dirty the path from root to leaf. Dirtying respects in-progress commits: if a znode has `COW_ZNODE`, it is copied, the old instance is marked obsolete, and old on-flash positions are recorded. Insertions split full znodes, possibly splitting the root and correcting parent lower-bound keys. Deletions remove zbranches, add obsolete leaf space to lprops dirt, collapse empty znodes, and may reduce tree height. Range and inode removal repeatedly find and delete all keys in the requested range, including xattr entries and xattr inodes.

Bulk read first collects consecutive data-node zbranches for one inode in one LEB, respecting buffer length, holes, page-boundary coverage, and `UBIFS_MAX_BULK_READ`. The actual bulk read then reads one contiguous media range, checks for a GC race with `maybe_leb_gced()`, and validates every data node.

## State And Persistence
TNC state is memory-resident but mirrors persistent index nodes. Zbranches hold keys, LEB/offset/length, hash, optional child znode pointer, and optional cached leaf pointer. Dirty znodes represent index updates that must be committed by `tnc_commit.c`. `c->old_idx` protects the last committed index from being overwritten before a new commit completes. `c->dirty_zn_cnt`, `c->clean_zn_cnt`, and global `ubifs_clean_zn_cnt` feed budgeting and shrinker behavior. Lprops dirt is updated when old leaf or index locations become obsolete.

## Dependencies And Integration Points
This file depends on key encoding/comparison helpers, IO helpers, write-buffer reads, CRC/hash validation, lprops dirt accounting, TNC znode loading from `tnc_misc.c`, commit behavior from `tnc_commit.c`, GC sequence tracking, replay mode semantics, fscrypt names, journal callers that add/remove nodes, GC callers that replace moved nodes, directory/xattr code that uses name lookups, and debug code. The shrinker reclaims clean znodes created and counted by this file.

## Risks And Edge Cases
Hash collisions are the dominant lookup edge case: parent boundary keys can point to adjacent znodes with equivalent hashed keys, so lookups often need to scan left and right. Replay can encounter dangling branches after GC, so fallible lookup paths must distinguish missing media from hard IO failures. GC can move a leaf after `tnc_mutex` is dropped; sequence checks and retry-under-lock avoid returning stale data. Commit copy-on-write requires precise ordering of `DIRTY_ZNODE`, `COW_ZNODE`, obsolete flags, old-index records, and clean counters. Tree split/collapse bugs can break parent keys and make old index nodes unrecoverable after power loss.

## Test Signals
Signals include unique-key lookup/add/remove, dent/xent hash-collision lookup and removal, double-hash cookie lookup/removal, replay with dangling branches, insertion split/root split behavior, deletion collapse/root collapse behavior, range and inode removal including xattrs, GC replacement by exact location, stale read retry after GC sequence changes, bulk-read grouping and `-EAGAIN`, dirty/clean counter balance, old-index RB-tree cleanup, shrinker interaction, and `dbg_check_tnc()`/`dbg_check_inode_size()` failures under debug builds.
