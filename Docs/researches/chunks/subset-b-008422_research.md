# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.h lines 5492-6410

## Scope And Purpose

This chunk is the tail of FoundationDB's vendored SQLite public header. It declares connection and prepared-statement status APIs, the legacy application-defined page-cache interface, online backup APIs, shared-cache unlock notification, string comparison and error logging helpers, WAL hooks and checkpoint APIs, checkpoint mode constants, the R-Tree geometry callback extension header, and a FoundationDB-specific database-page scan helper.

The header is mostly API contract, not implementation. It defines how embedders and extensions observe SQLite memory/query behavior, replace the pager cache, copy live databases, respond to shared-cache lock contention, manage WAL growth, register R-Tree geometry predicates, and scan every database page for codec/corruption diagnostics.

## Important APIs, Types, And Functions

`sqlite3_db_status(sqlite3*, int op, int *pCur, int *pHiwtr, int resetFlg)` reports database-connection counters. The `SQLITE_DBSTATUS_*` verbs in this range cover lookaside slots used, lookaside hit/miss counters, pager cache heap usage, schema heap usage, and prepared-statement heap/lookaside usage. `SQLITE_DBSTATUS_MAX` is `6`.

`sqlite3_stmt_status(sqlite3_stmt*, int op, int resetFlg)` reports per-prepared-statement counters. The exposed verbs are `SQLITE_STMTSTATUS_FULLSCAN_STEP`, `SQLITE_STMTSTATUS_SORT`, and `SQLITE_STMTSTATUS_AUTOINDEX`, used to detect full scans, sort work, and transient automatic index inserts.

`sqlite3_pcache` is an opaque custom page-cache handle. `sqlite3_pcache_methods` is the legacy page-cache vtable registered through `sqlite3_config(SQLITE_CONFIG_PCACHE, ...)`. Its callbacks are `xInit`, `xShutdown`, `xCreate`, `xCachesize`, `xPagecount`, `xFetch`, `xUnpin`, `xRekey`, `xTruncate`, and `xDestroy`, with `pArg` copied into SQLite global configuration.

`sqlite3_backup` is an opaque state object for online backups. `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, `sqlite3_backup_remaining()`, and `sqlite3_backup_pagecount()` copy pages from one database connection/database name to another in bounded steps.

`sqlite3_unlock_notify()` registers or cancels a shared-cache unlock callback for a blocked connection. The callback receives a bundled array of context pointers when multiple blocked connections share the same callback function.

`sqlite3_strnicmp()` exposes SQLite's case-insensitive UTF-8 identifier comparison. `sqlite3_log()` writes formatted messages to the process-wide `SQLITE_CONFIG_LOG` callback without dynamic allocation.

`sqlite3_wal_hook()` registers one WAL commit callback per database handle. `sqlite3_wal_autocheckpoint()` installs SQLite's default hook that checkpoints when the WAL reaches a frame threshold. `sqlite3_wal_checkpoint()` is the passive checkpoint wrapper, while `sqlite3_wal_checkpoint_v2()` supports `SQLITE_CHECKPOINT_PASSIVE`, `SQLITE_CHECKPOINT_FULL`, and `SQLITE_CHECKPOINT_RESTART` and can report total/log checkpointed frame counts.

`sqlite3_rtree_geometry_callback()` registers a SQL scalar function that returns an R-Tree MATCH blob. The callback receives `sqlite3_rtree_geometry`, which carries the application context, SQL parameters as doubles, and optional user data/destructor fields.

`tryReadEveryDbPage(sqlite3 *db, Pgno start, Pgno *pBadPage, int *pBadPageType, int *pBadPageZero)` is a local FoundationDB addition after the upstream R-Tree header. It scans physical database pages from `start` through the last page without caching each page, reports the first error page, and on `SQLITE_CORRUPT` attempts to report pointer-map page type and whether the bad page was all zero bytes.

## Control Flow

Status collection is synchronous and read-only from the caller's perspective. The implementation of `sqlite3_db_status()` enters the database mutex, switches on the verb, reads lookaside, pager, schema, or statement memory state, optionally resets high-water values, and returns `SQLITE_OK` or an error for unsupported verbs. `sqlite3_stmt_status()` reads the VDBE statement counter array and optionally zeroes the selected counter.

The custom page-cache path starts during global SQLite configuration. SQLite copies the provided `sqlite3_pcache_methods` into global config, calls `xInit()` once per effective initialization, creates cache instances with `xCreate(szPage, bPurgeable)`, fetches pages with `xFetch(key, createFlag)`, returns pages with `xUnpin(discard)`, updates keys with `xRekey()`, drops page ranges with `xTruncate()`, and finally calls `xDestroy()` for each cache plus `xShutdown()` at process shutdown.

Backup flow is explicitly staged: `sqlite3_backup_init()` validates distinct source/destination connections, resolves source and destination btrees, sets destination page size constraints, and increments the source backup count. Each `sqlite3_backup_step()` opens or reuses a destination write transaction, opens a source read transaction as needed, copies up to `nPage` source pages into destination pages while skipping the pending-byte page, updates remaining/pagecount fields, and returns `SQLITE_OK`, `SQLITE_DONE`, `SQLITE_BUSY`, `SQLITE_LOCKED`, or a fatal error. Completion updates the destination schema version, handles page-size/truncation details, syncs and commits. `sqlite3_backup_finish()` detaches the object from the source pager, rolls back any still-open destination transaction, writes the destination handle error code, and frees the backup object.

Unlock-notify flow is shared-cache-specific. When a statement or prepare operation records a blocking connection, a later `sqlite3_unlock_notify()` either invokes the callback immediately if no blocker remains, detects dependency cycles and returns `SQLITE_LOCKED`, or links the blocked connection into a global blocked list. When a blocking transaction ends, SQLite walks the list, clears blocking references, bundles callbacks with matching function pointers, invokes them, and removes now-unblocked entries.

WAL hook flow is per connection. `sqlite3_wal_hook()` stores callback and context under the database mutex and returns the previous context. `sqlite3_wal_autocheckpoint()` replaces any existing hook with the default checkpoint hook when `N > 0`, or clears it otherwise. `sqlite3_wal_checkpoint_v2()` validates the mode, resolves a specific attached database name or all databases, initializes output counts to `-1`, and dispatches to the checkpoint implementation under the database mutex.

R-Tree geometry registration creates an ordinary SQLite scalar function. When SQL calls that function, SQLite builds a blob containing the geometry callback pointer, context, and numeric parameters. The R-Tree MATCH operator later interprets the blob and calls the registered geometry predicate for candidate bounding boxes.

`tryReadEveryDbPage()` obtains database 0's btree and pager, computes `lastPage` and the pending-byte page to skip, allocates one page buffer, constructs a lightweight `PgHdr`, and calls the internal `readDbPage()` for each page. On corruption it scans the buffer for all-zero content and, if possible, reads the pointer-map page to classify the bad page before returning the failing page number and error code.

## State And Persistence Behavior

The status APIs expose transient connection and statement state. Lookaside counters live on the `sqlite3` handle, VDBE counters live on the prepared statement, pager memory totals are summed from attached btrees, and schema/statement memory values are approximations. Reset flags mutate only high-water or counter fields, not database content.

The page-cache interface owns volatile cache state supplied by an application. SQLite treats returned pages as page-sized, 8-byte-aligned memory with SQLite-private extra bytes included in `szPage`. Cache keys are one-based page numbers. `xFetch()` pins a page, `xUnpin()` unpins without reference counting, `xRekey()` changes page identity, and `xTruncate()` discards pages at or beyond a limit. A non-purgeable cache, used for in-memory databases, should never retain unpinned pages.

Online backup mutates the destination database persistently. It holds a destination write transaction across the backup operation, briefly read-locks the source during step calls, copies page bytes through pager/btree layers, updates the destination schema cookie, truncates/syncs the destination file for page-size differences, and rolls back destination writes if abandoned before `SQLITE_DONE`. The source can change between steps; external changes may restart copied work, while changes on the same source connection update already-copied destination pages through pager backup callbacks.

Unlock-notify state is connection-local plus a process-global blocked-connection list protected by SQLite mutexes. At most one callback registration is active per blocked connection. Callback contexts are not durable and callbacks are invoked from the SQLite call that releases the blocking transaction.

WAL hook and auto-checkpoint state is stored on the `sqlite3` connection as a function pointer plus context. WAL checkpointing writes persistent database pages from the WAL back into the database file and may reset WAL reuse state depending on mode and reader positions. Passive checkpoints avoid waiting; full and restart checkpoints may invoke the busy handler and block writers while running.

R-Tree geometry callback state is connection-local SQL function registration state. `sqlite3_create_function_v2()` owns a small heap context and frees it through the supplied destructor. Per-call MATCH blobs are transient SQL values freed by SQLite.

`tryReadEveryDbPage()` is intended as diagnostic read-only scanning, but it bypasses the normal page cache path by using `readDbPage()` with a scratch `PgHdr`. It does allocate a raw `malloc()` page buffer and reads pointer-map pages on corruption. Its observable state is output parameters and possible pager/codec side effects from direct page reads.

## Dependencies And Integration Points

This header depends on core opaque SQLite types declared earlier in `sqlite3.h`: `sqlite3`, `sqlite3_stmt`, `sqlite3_file`, error codes, database names, shared-cache behavior, WAL mode, and `SQLITE_API`. The local `tryReadEveryDbPage()` declaration also depends on internal `Pgno`, so it is not a pure upstream public API boundary.

`sqlite3_db_status()` integrates with the shell's `.stats` reporting in `contrib/sqlite/shell.c`, where lookaside, pager heap, schema heap, statement heap, fullscan, sort, and autoindex counters are printed. The implementation reaches into lookaside accounting, btree/pager memory accounting, schema memory, and VDBE statement counters.

`sqlite3_pcache_methods` integrates with `sqlite3_config(SQLITE_CONFIG_PCACHE)` and `SQLITE_CONFIG_GETPCACHE`; the copied vtable is stored in `sqlite3GlobalConfig.pcache`. The pager/page-cache subsystem is the main consumer. Incorrect custom cache behavior can affect every btree and pager operation in the process.

The backup APIs integrate with the shell `.backup` and `.restore` commands, pager backup callback lists, btree transactions, page-size metadata, journal/WAL mode checks, busy handlers, and destination schema invalidation. Backup is also exposed to loadable extensions through `sqlite3ext.h`.

Unlock notification integrates with shared-cache lock bookkeeping, `sqlite3_step()`, `sqlite3_prepare()`, and `sqlite3_close()` paths that can release blocking transactions. It is compiled only when `SQLITE_ENABLE_UNLOCK_NOTIFY` is enabled but is declared in the public header.

WAL APIs integrate with pager WAL commit, `PRAGMA wal_autocheckpoint`, `PRAGMA wal_checkpoint`, the busy-handler interface, attached database lookup, and VFS locking/shm behavior. `sqlite3_wal_hook()` and `sqlite3_wal_autocheckpoint()` replace each other because both use the single per-handle WAL callback slot.

The R-Tree callback declaration integrates with the optional R-Tree extension implementation in the same amalgamation. It uses SQLite scalar-function registration as the SQL-level bridge between application geometry code and virtual-table MATCH evaluation.

`tryReadEveryDbPage()` integrates directly with internal pager, btree, pointer-map, and optional pager-codec behavior in `sqlite3.amalgamation.c`. This is likely FoundationDB-specific validation support for detecting unreadable/corrupt database pages and classifying codec failures.

## Risks And Edge Cases

Applications must check `sqlite3_db_status()` return codes because verbs may be unsupported or discontinued. `sqlite3_stmt_status()` in this older SQLite version indexes `aCounter[op-1]` directly, so invalid statement status verbs are a misuse risk rather than a gracefully rejected query.

Custom page-cache implementations are high risk. They must be thread-safe except for `xInit()` and `xShutdown()`, return correctly aligned buffers of the exact `szPage`, preserve page contents for cache hits, avoid reference counting, handle `createFlag` semantics, discard replacement keys in `xRekey()`, and tolerate SQLite evicting or truncating pinned pages as documented. A bug here can corrupt pager state globally.

Backup callers must not use the destination connection, or any same-process shared cache for the destination file, between `sqlite3_backup_init()` and `sqlite3_backup_finish()`. SQLite documents that it does not fully detect such misuse, and it may deadlock or malfunction. Fatal backup errors such as I/O errors, OOM, and read-only page-size constraints should not be retried; `SQLITE_BUSY` and `SQLITE_LOCKED` can be retried.

Backup with page-size mismatch is constrained. WAL destinations and in-memory destinations reject mismatched source/destination page sizes with `SQLITE_READONLY`. The implementation has special truncation and pending-byte handling for page-size changes, so tests should cover both smaller-to-larger and larger-to-smaller page-size copies.

Unlock-notify callbacks are non-reentrant. Calling arbitrary SQLite APIs from inside the callback can crash or deadlock. The DROP TABLE/DROP INDEX same-connection `SQLITE_LOCKED` case has no true blocking connection and can cause immediate callback loops unless callers inspect the extended error code.

WAL hook callbacks run after commit has occurred. Returning an error propagates to the statement even though the commit is already durable, so callers must avoid treating hook failure as a rollback signal. Auto-checkpoint registration overwrites custom hooks and vice versa, which can silently disable one mechanism.

`sqlite3_wal_checkpoint_v2()` has mode-specific blocking behavior. Passive checkpoints never invoke the busy handler; full and restart may wait for writers/readers but fall back to passive progress and return `SQLITE_BUSY` if the busy handler stops waiting. Output counts may be set even on non-OK returns, and are undefined when checkpointing all attached databases.

`sqlite3_log()` truncates long messages and requires a non-null format string. It avoids dynamic allocation to reduce deadlock risk, so callers should not expect full diagnostic payloads for very long formatted messages.

R-Tree geometry callbacks receive coordinates and parameters as doubles and may carry callback-managed `pUser` state. Bad destructor handling or persistence of callback blobs outside the originating process/connection would be unsafe.

`tryReadEveryDbPage()` has local-code risks: the declaration exposes internal `Pgno` in `sqlite3.h`; the implementation uses raw `malloc()` rather than SQLite allocators and must free on all paths; it assumes `db->aDb[0].pBt` and pager state are initialized despite a TODO noting the client may not have initialized the database; output parameters must be valid; pointer-map classification is unavailable or unreliable for non-auto-vacuum databases or if the pointer-map page is also unreadable.

## Test Signals

Status tests should call `sqlite3_db_status()` for each `SQLITE_DBSTATUS_*` verb before and after preparing statements, using lookaside memory, attaching databases, and resetting high-water counters. Statement tests should execute queries that force full scans, sorts, and automatic indexes, then verify `sqlite3_stmt_status()` values and reset behavior.

Page-cache tests should register a custom `sqlite3_pcache_methods` implementation that logs callback order and validates `xInit`/`xShutdown`, `xCreate` arguments, `xFetch` create flags, one-shot `xUnpin`, `xRekey` replacement, and `xTruncate` discard behavior under normal queries, cache pressure, in-memory databases, and shutdown.

Backup tests should cover complete and incremental backups, `nPage < 0`, live source writes between steps, busy/locked retry paths, distinct-connection enforcement, destination read-only errors, WAL and in-memory page-size mismatch errors, abandon/finish rollback, remaining/pagecount updates, and shell `.backup`/`.restore` behavior.

Unlock-notify tests require shared-cache builds. They should create blocked readers/writers, register callbacks, verify immediate callback when blockers are already gone, replacement/cancellation semantics, bundled callback arguments, direct and indirect deadlock detection, and the DROP TABLE/DROP INDEX extended-error-code exception.

WAL tests should verify custom WAL hook invocation after commits, replacement between hooks and auto-checkpoint, default auto-checkpoint threshold behavior, disabled auto-checkpoint with `N <= 0`, passive/full/restart checkpoint return codes, `pnLog`/`pnCkpt` values, attached database name errors, non-WAL no-op behavior, and busy-handler interactions with concurrent readers/writers.

R-Tree tests should register a geometry callback, execute `MATCH` predicates with parameter lists, verify callback context and coordinate arrays, validate destructor cleanup, and exercise OOM during geometry blob allocation.

`tryReadEveryDbPage()` tests should scan a healthy database from page 1 and a later start page, skip the pending-byte page, inject or create unreadable/corrupt pages, verify `pBadPage`, `pBadPageZero`, and `pBadPageType`, cover codec-corruption paths if a codec is enabled, and call it before ordinary schema initialization to confirm or fix the TODO behavior.
