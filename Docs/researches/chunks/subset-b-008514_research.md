# sources/storage-engines/lmdb/libraries/liblmdb/mdb.c lines 1-8938

## Scope

This chunk covers the opening 8938 lines of LMDB's main C implementation. It includes platform abstraction, on-disk and in-memory core types, page allocation and copy-on-write machinery, transaction begin/end/commit up to metadata publication, environment open/map/lock/close setup, comparison routines, page lookup/search, read cursor traversal, and the first half of `_mdb_cursor_put()`. The chunk ends while `_mdb_cursor_put()` is still handling same-size sub-cursor overwrite logic, so the rest of put, page split/merge/rebalance, delete, DBI APIs, copy/dump/load, reader check, and final cleanup routines continue in later chunks.

This file is not a thin wrapper around LMDB. The visible range carries local extensions around `MDB_RPAGE_CACHE`, `MDB_REMAP_CHUNKS`, page encryption/checksums, `mdb_txn_prepare()`, `mdb_env_rollback()`, `MDB_PREVSNAPSHOT`, and nested read-only child transaction accounting.

## Purpose

`mdb.c` implements Lightning MDB's memory-mapped B+tree storage engine. The code in this range establishes the central invariants used by the rest of the file:

- Database contents are a pair of alternating meta pages followed by page-numbered B+tree, overflow, and freelist pages.
- Readers are lock-free for data access and publish only their snapshot transaction ID in a shared reader table.
- Exactly one writer holds the writer mutex, performs copy-on-write page updates, persists dirty pages, and publishes a new snapshot by writing the next meta page.
- Free pages are reclaimed only after all older readers are gone, using the FreeDB plus `me_pghead`, `me_pglast`, `mt_free_pgs`, loose pages, and spill lists.
- Cursors hold a stack from root to leaf and are the main interface for searching, traversal, reads, and writes.

The environment setup code maps data and lock files, validates meta/lock formats, initializes a new database when no meta pages exist, and configures platform-specific shared locking. The read path searches B+trees by binary search in branch/leaf pages, follows overflow nodes, and supports sorted duplicate sub-pages/sub-databases. The write path starts here with dirty-page allocation, page touching, freelist saving, page flushing, and the early `put` cases that create roots, convert duplicates, and overwrite existing data.

## Important APIs, Types, And Functions

Public or externally visible APIs in this chunk include:

- `mdb_version()` and `mdb_strerror()` for library version and error text.
- `mdb_cmp()` and `mdb_dcmp()` dispatching per-DB key/data comparators.
- `mdb_txn_begin()`, `mdb_txn_renew()`, `mdb_txn_reset()`, `mdb_txn_abort()`, `mdb_txn_commit()`, `mdb_txn_prepare()`, `mdb_txn_env()`, `mdb_txn_id()`, and `mdb_txn_flags()`.
- `mdb_env_create()`, `mdb_env_open()`, `mdb_env_close()`, `mdb_env_sync()`, `mdb_env_sync0()`, `mdb_env_set_mapsize()`, `mdb_env_set_maxdbs()`, `mdb_env_set_maxreaders()`, `mdb_env_get_maxreaders()`, and `mdb_env_rollback()`.
- `mdb_get()` and `mdb_cursor_get()` for read access. The lower-level cursor open/close/put/delete APIs are declared or partially implemented here but continue later.

Core persistent layout and state types:

- `MDB_page_header`, `MDB_page`, and `MDB_page2` define page headers, page flags, key-index arrays, overflow page count storage, and 2-byte-aligned access helpers.
- `MDB_node` represents branch/leaf entries, including data size, key size, flags for overflow/subdata/dups, and encoded child page numbers.
- `MDB_db` is the per-B+tree root/stat record persisted in meta pages and named DB records.
- `MDB_meta` stores magic/version, map address/size, FreeDB/MainDB records, page size, environment flags, last page, and committed txnid.
- `MDB_reader`, `MDB_txninfo`, and lock-format macros define the shared reader table and lock-file compatibility signature.
- `MDB_txn` tracks parent/child relationships, txn/work IDs, dirty/free/spill/loose pages, DB records, DBI validity flags, cursor lists, reader slot, and optional remapped-page caches.
- `MDB_cursor` and `MDB_xcursor` track B+tree position and duplicate-data sub-cursors.
- `MDB_env` owns file handles, mapped data/lock regions, meta pointers, preallocated writer transaction, DBI tables, page caches, free/dirty lists, locks, optional encryption/checksum callbacks, and user/assert contexts.

Important internal routines in this range:

- Page memory and copy-on-write: `mdb_page_malloc()`, `mdb_page_free()`, `mdb_dpage_free()`, `mdb_dlist_free()`, `mdb_page_loose()`, `mdb_page_alloc()`, `mdb_page_unspill()`, and `mdb_page_touch()`.
- Dirty-page pressure and persistence: `mdb_pages_xkeep()`, `mdb_page_spill()`, `mdb_freelist_save()`, `mdb_page_flush()`, `mdb_env_sync0()`, and `mdb_env_write_meta()`.
- Transaction lifecycle: `mdb_txn_renew0()`, `mdb_cursor_shadow()`, `mdb_cursors_close()`, `mdb_dbis_update()`, `mdb_txn_end()`, `_mdb_txn_abort()`, and `_mdb_txn_commit()`.
- Environment lifecycle: `mdb_env_read_header()`, `mdb_env_init_meta0()`, `mdb_env_init_meta()`, `mdb_env_pick_meta()`, `mdb_env_map()`, `mdb_fname_init()`, `mdb_fopen()`, `mdb_env_open2()`, `mdb_env_setup_locks()`, `mdb_env_share_locks()`, `mdb_env_excl_lock()`, `mdb_env_close_active()`, and `mdb_env_close()`.
- Search/read cursor path: `mdb_node_search()`, `mdb_cursor_push()`, `mdb_cursor_pop()`, `mdb_page_get()`, `mdb_page_search_root()`, `mdb_page_search_lowest()`, `mdb_page_search()`, `mdb_node_read()`, `mdb_cursor_sibling()`, `mdb_cursor_next()`, `mdb_cursor_prev()`, `mdb_cursor_set()`, `mdb_cursor_first()`, and `mdb_cursor_last()`.
- Optional remapped read-page/encryption/checksum path: `mdb_rpage_get()`, `mdb_rpage_encsum()`, `mdb_page_encrypt()`, `mdb_rpage_decrypt()`, `mdb_rpage_dispose()`, `mdb_page_set_checksum()`, and `mdb_page_chk_checksum()`.
- The partial write cursor path: `mdb_cursor_touch()`, `mdb_subdb_adjust()`, and `_mdb_cursor_put()` through existing-node overwrite handling.

## Control Flow

Environment open starts with `mdb_env_create()`, optional setters, then `mdb_env_open()`. Open validates flags, derives data/lock filenames, allocates dirty/free/DBI state, sets up lockfile/shared locks unless disabled, opens the data file, reads or initializes meta pages in `mdb_env_open2()`, maps the file with `mdb_env_map()`, verifies encryption/checksum compatibility, computes page limits, opens the synchronous meta fd, downgrades exclusive lock to shared, and preallocates `me_txn0` for write transactions. On failure, `mdb_env_close_active()` unwinds only resources marked by `MDB_ENV_ACTIVE`.

Read transaction begin flows through `mdb_txn_begin()` to `mdb_txn_renew0()`. With locks enabled, a reader slot is found or reused, the process liveness lock is set, `mr_txnid` is sampled from `mti_txnid`, and the transaction copies the matching meta DB records. Without a lock table, the current picked meta page provides the snapshot. `mdb_txn_reset()` clears `mr_txnid` but can keep a `MDB_NOTLS` slot; `mdb_txn_abort()` with slot mode can fully release it.

Write transaction begin acquires `me_wmutex`, increments the latest txnid, initializes `mt_workid`, dirty/free lists, loose/spill state, DB tables, and `env->me_txn`. Nested write transactions clone parent DB state, save the parent's `MDB_pgstate`, copy `me_pghead` when needed, shadow parent cursors, and merge back into the parent on successful nested commit. Nested read-only transactions under a writer share parent dirty/free state and update `mt_rdonly_child_count` under `mt_child_mutex`.

Commit of a top-level writer follows a strict durability sequence. `_mdb_txn_commit()` closes cursors, writes dirty named DB records into the main DB, saves freelist changes into the FreeDB, flushes dirty pages via `mdb_page_flush()`, optionally syncs data via `mdb_env_sync0()`, optionally leaves the transaction in `MDB_TXN_PREPARE`, then publishes the snapshot with `mdb_env_write_meta()`. Only after the meta page is written is `mti_txnid` advanced for new readers. On failure, the transaction abort path frees dirty memory, restores state, releases locks, and marks fatal environment state when meta write failure makes the map unsafe.

Page reads use `mdb_page_get()`: first check the current transaction and ancestors for dirty-page aliases, then spilled pages, then the mapped file or remapped-page cache. Searches use `mdb_page_search()` to refresh stale named DB roots, load the root page, optionally touch pages for modification, and descend through branch pages in `mdb_page_search_root()` using `mdb_node_search()`. Cursor traversal walks duplicate xcursor state first, then increments/decrements leaf indices and recursively moves to sibling pages through branch parents.

Writes use `mdb_cursor_touch()` to copy-on-write every page in the cursor stack. `mdb_page_touch()` allocates a new page for old snapshots, reuses/unspills pages that this transaction spilled, or copies parent-dirty pages into a child transaction, then updates parent branch pointers or DB roots and retargets other tracked cursors. `_mdb_cursor_put()` begins by validating flags/sizes, locating the insertion point, spilling if dirty-room pressure is high, creating a new root if needed, touching the cursor path, and then handling duplicate conversion, sub-page/sub-DB promotion, and existing overflow/same-size overwrite cases. The function continues beyond this chunk.

## State And Persistence Behavior

The durable database image is governed by `MDB_meta`: page size, map size, two core DB roots, last used page, and committed txnid. There are two meta pages, and transaction `N` writes meta slot `N & 1`. Readers choose a stable snapshot from a meta page or the lock table txnid; writers make all data pages durable before publishing the new meta.

MVCC safety depends on `MDB_reader.mr_txnid` and `mdb_find_oldest()`. A writer reads all active reader slots to decide which FreeDB records are old enough to reclaim. Stale or conservative reader data only delays reuse. Stale dead readers are later handled by reader-check code outside this chunk.

Freelist state is split across durable and transient structures. Durable FreeDB records map old txnids to IDLs of freed page numbers. During a writer, `env->me_pghead` accumulates reusable pages loaded from old FreeDB records, `env->me_pglast` records how far the FreeDB was consumed, `txn->mt_free_pgs` records pages freed by this transaction, and `txn->mt_loose_pgs` caches single dirty pages reusable within the same transaction. `mdb_freelist_save()` repeatedly reserves and fills FreeDB records until the freelist representation stabilizes.

Dirty page state differs by mode. Without `MDB_WRITEMAP`, dirty pages are malloc-backed and tracked in sorted `mt_u.dirty_list`; commit writes them to the data file and frees/reuses the memory. With `MDB_WRITEMAP`, writes update mapped pages directly, `mt_dirty_room` is mostly a dummy guard, and sync behavior relies on `msync`/`FlushViewOfFile` plus metadata ordering. Spilled pages are dirty pages flushed early to avoid `MDB_TXN_FULL`; `mt_spill_pgs` marks them as clean-but-owned so later writes can unspill or avoid parent conflicts.

The optional remapped page cache maps only meta pages initially and maps read chunks on demand into `mt_rpages` and `me_rpages`. This changes LMDB's usual data-pointer lifetime guarantee: comments explicitly state that returned data may be unmapped after cursor movement or subsequent operations, so callers must copy data if it must survive later operations in the same transaction.

Encryption/checksum state is configured in `MDB_env` callbacks and sizes. Dirty pages get checksums and optional encryption before flushing. Read chunks are decrypted lazily into `menc`, tracked by `muse` bitmasks, optionally checksum-verified, and zeroed before decrypted buffers are freed. The meta page stores an encryption flag and the initial meta setup stores checksum size in the tail of page 0.

## Dependencies And Integration Points

This file depends directly on `lmdb.h` for public types, flags, error codes, callback signatures, and API declarations, and on `midl.h` for sorted IDL/ID2L/ID3L page-list operations. It integrates with POSIX or Windows primitives for `mmap`/`NtMapViewOfSection`, file open/read/write/sync/truncate, process-shared mutexes or named semaphores/System V semaphores, TLS keys, process liveness locks, and cache flush behavior on MIPS.

The code is tightly coupled to LMDB's page layout: `PAGEHDRSZ`, `NODEPTR`, `NODEDATA`, `NODEPGNO`, `LEAF2KEY`, `OVPAGES`, and `MDB_db` sizes must remain compatible with existing database files. Lock-file compatibility is similarly encoded in `MDB_LOCK_FORMAT`, which reflects mutex type, reader layout, pid/thread sizes, cacheline, and txnid width.

Higher-level APIs later in the file build on the functions in this chunk. `mdb_put()`, `mdb_cursor_put()`, delete/drop, DBI open/stat/flags, environment copy/incremental dump/load, and reader-list/check all depend on these transaction, page, cursor, and environment primitives. The partial `_mdb_cursor_put()` in this range calls forward-declared helpers such as `mdb_page_new()`, `mdb_node_del()`, `mdb_update_key()`, `mdb_node_add()`, `mdb_page_split()`, and xcursor initializers that are completed later in the file.

## Risks And Edge Cases

- Meta write ordering is the primary corruption boundary. If data pages or the freelist are not durable before `mm_txnid` is advanced, readers can observe a snapshot that points at missing or stale pages.
- `MDB_NOSYNC`, `MDB_NOMETASYNC`, `MDB_MAPASYNC`, `MDB_WRITEMAP`, Windows write-through handles, and broken Linux `fdatasync` workarounds create platform-specific durability modes that must be tested separately.
- Reader table correctness is concurrency-sensitive. Slot publication order, TLS destructor behavior, `MDB_NOTLS` ownership, pid liveness locks, robust mutex recovery, and stale readers all affect page reuse safety.
- `mt_workid` and page `mp_txnid` are central to nested transaction copy-on-write. Bugs in `IS_MUTABLE`, `IS_WRITABLE`, `IS_DIRTY_NW`, workid rewind, or parent dirty-list merging can corrupt parent/child isolation.
- Freelist saving is intentionally iterative because writing the FreeDB can allocate or free pages. Off-by-one errors in reserved IDL records, `me_pghead`, `me_pglast`, loose-page squashing, or FreeDB cursor deletes can leak pages or double-allocate pages.
- Spilled page handling is subtle. Spilling must not include active cursor pages, DB roots, loose pages, or pages already spilled in ancestors; unspill and nested commit must keep spill lists and dirty lists consistent.
- `MDB_RPAGE_CACHE` weakens ordinary LMDB pointer lifetime assumptions and introduces shared/local reference-count purging. Missing unrefs can leak mappings; premature purge can invalidate returned data; overflow remapping around chunk boundaries is especially risky.
- Encryption/checksum support must preserve unencrypted page-number/txnid header fields, handle authentication tail sizes consistently, zero decrypted pages on disposal, and keep checksum size compatible with existing files.
- `mdb_env_set_mapsize()` after open requires no active transactions. Remapping at a fixed address can fail with `MDB_ADDR_BUSY`, and map sizes below committed data are rounded up.
- The chunk ends mid-`_mdb_cursor_put()`, so write-path conclusions here are incomplete without later logic for node shrinking, new node insertion, overflow allocation, page split, cursor fixups, and public put wrappers.

## Test Signals

Useful validation signals for this chunk include:

- Core LMDB tests covering create/open/close, read-only open, `MDB_NOSUBDIR`, `MDB_NOLOCK`, lock-file reuse, max readers, max DBs, map resize, fixed map behavior, and invalid/corrupt meta handling.
- Transaction tests for read snapshot stability across concurrent writers, writer serialization, nested write commit/abort, nested read-only transactions under a writer, reset/renew behavior, `MDB_NOTLS`, and failed transaction blocking.
- Durability/crash tests that kill the process around dirty-page flush, freelist save, data sync, meta write, and `MDB_NOSYNC`/`MDB_NOMETASYNC` combinations, then reopen and verify the chosen meta page and B+tree roots.
- Freelist stress with long-lived readers, many small deletes/inserts, overflow page churn, dirty-list pressure forcing spill/unspill, and nested transactions modifying pages also touched by parents.
- Cursor read tests for `MDB_SET`, `MDB_SET_RANGE`, `MDB_GET_BOTH`, duplicate and fixed-duplicate databases, first/last/next/prev traversal, multiple-value fetches, empty DBs, leaf2 pages, and overflow values.
- Environment lock tests across processes, including stale process/thread cleanup, robust mutex owner-dead recovery, POSIX semaphore and System V semaphore builds, Windows named mutex/TLS callback behavior, and read-only filesystem lock omission.
- Remapped-page-cache tests with `MDB_REMAP_CHUNKS`, overflow pages crossing chunk boundaries, cursor movement after returned data, transaction close purge, map-full/txn-full cache thresholds, and read-only tail chunk mapping.
- Encryption/checksum tests for new and existing environments, mismatch detection, checksum failure reporting, encrypted overflow pages, dirty-page flush encryption, decrypted-buffer zeroing, and interactions with remapped chunks.
- Error-path tests for `MDB_MAP_FULL`, `MDB_TXN_FULL`, `MDB_PAGE_NOTFOUND`, `MDB_CORRUPTED`, `MDB_BAD_DBI`, `MDB_BAD_TXN`, `MDB_SHORT_WRITE`, `MDB_CRYPTO_FAIL`, and `MDB_BAD_CHECKSUM`.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-008514`. It covers `mdb.c` lines 1-8938 and stops in the middle of `_mdb_cursor_put()`. The final per-file research should merge this with subsequent chunks to complete the write path, delete/rebalance/split logic, public cursor/DBI/environment maintenance APIs, copy/dump/load helpers, reader cleanup, and final mutex-failure recovery code.
