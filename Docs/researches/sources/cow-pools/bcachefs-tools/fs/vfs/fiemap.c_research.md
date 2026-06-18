# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/fiemap.c

Purpose: implements bcachefs `fiemap` support, translating extent btree records plus dirty pagecache state into `FIEMAP_EXTENT_*` records for userspace.

Key behavior:
- `bch2_fill_extent()` emits fiemap extents for direct data, inline data, reservations, reflinks, unwritten extents, compressed data, and unaligned mappings.
- `bch2_next_fiemap_pagecache_extent()` scans pagecache over btree holes and synthesizes delayed-allocation extents for dirty cached data.
- `bch2_next_fiemap_extent()` merges pagecache-delalloc state with extent btree mappings, resolves `KEY_TYPE_reflink_p` through indirect extent lookup, and trims keys to the requested range.
- `bch2_fiemap()` prepares the request, walks sector ranges, delays emission by one extent so the final record can be marked `FIEMAP_EXTENT_LAST`, and normalizes errors through `bch2_err_class()`.

Important interactions:
- Depends on `vfs/pagecache.c` seek helpers to detect dirty cached data in holes.
- Uses btree transactions and restarts; blocking pagecache scans are done through `drop_locks_do()` to avoid sleeping on folio locks while holding btree locks.
- The code explicitly notes fiemap mappings are not stable because bcachefs can relocate data in the background.
