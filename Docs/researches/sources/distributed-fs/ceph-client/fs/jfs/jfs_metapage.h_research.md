# sources/distributed-fs/ceph-client/fs/jfs/jfs_metapage.h

## Purpose
`jfs_metapage.h` declares the metapage abstraction used for all JFS metadata I/O and journaling coordination. It exposes the metapage structure, state bits, allocation/read helpers, release/write helpers, journal home-location ordering helpers, and extent invalidation macros.

## Important APIs, types, and functions
The central type is `struct metapage`, whose leading fields mirror `struct logsyncblk` for membership on `jfs_log.synclist`. Public APIs include `metapage_init()`, `metapage_exit()`, `__get_metapage()`, `release_metapage()`, `grab_metapage()`, `force_metapage()`, `hold_metapage()`, `put_metapage()`, `__invalidate_metapages()`, and `jfs_metapage_aops`. Convenience macros `read_metapage()` and `get_metapage()` select read-existing versus create/new behavior. Inline helpers include `write_metapage()`, `flush_metapage()`, `discard_metapage()`, `metapage_nohomeok()`, `metapage_wait_for_io()`, `_metapage_homeok()`, and `metapage_homeok()`.

## Control flow
Callers fetch metadata with `read_metapage()` or `get_metapage()`, modify `mp->data` under the metapage lock, then either release clean, mark dirty via `write_metapage()`, force synchronous write via `flush_metapage()`, or discard invalidated metadata via `discard_metapage()`. Transaction code calls `metapage_nohomeok()` when a metadata page is journal-protected and `_metapage_homeok()`/`metapage_homeok()` after the commit reaches stable storage.

## State and persistence behavior
`META_dirty` controls home writeback, `META_sync` requests synchronous write on release, `META_discard` suppresses stale writes for invalidated extents, `META_forcewrite` bypasses normal no-home blocking, and `META_io` tracks writeback in progress. `nohomeok` is a counter, not a boolean, allowing nested transaction holds. The `log`, `lsn`, `clsn`, and `synclist` fields bind metapages to journal sync-point advancement.

## Dependencies and integration points
The header depends on `linux/pagemap.h`, JFS transaction IDs (`lid_t`), extent helpers (`addressPXD`, `lengthPXD`, `addressDXD`, `addressXAD`), and `struct jfs_log`. It is used by inode, directory, extent-tree, allocation-map, mount, transaction, and log code wherever metadata pages are read, modified, invalidated, or flushed.

## Risks
Callers must pair holds/releases carefully or the metapage can remain locked, pinned, or no-home-blocked. `metapage_nohomeok()` waits for folio writeback while holding folio state and increments a counter that must eventually be decremented. The invalidation macros operate on block extents; incorrect extent lengths or addresses can discard unrelated metadata or leave stale pages dirty.

## Test signals
Useful tests exercise dirty release, synchronous flush, discard, nested no-home sections, wait-for-I/O serialization, and invalidation through PXD/DXD/XAD macros. Debugging should watch metapage refcounts, `nohomeok`, and `META_io` transitions during transaction commit and unmount.
