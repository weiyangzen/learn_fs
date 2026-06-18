# sources/storage-engines/sqlite/src/sqlite.h.in lines 10717-11389

## Scope

This chunk covers the final public API declarations and preprocessor cleanup in `sqlite.h.in`. It starts in the prepared-statement scan-status documentation and then declares APIs for scan counters, mid-transaction pager cache flushing, pre-update hooks, OS error reporting, WAL snapshot handles, database serialization/deserialization, `carray()` parameter binding, and closing platform/header guards. The file is a generated-header template, so this range is API contract and documentation rather than implementation logic.

## Purpose

- Expose optional statement scan-status inspection for prepared statements compiled with `SQLITE_ENABLE_STMT_SCANSTATUS`.
- Provide `sqlite3_db_cacheflush()` as an explicit way to push dirty pager-cache pages to disk during a write transaction without ending the transaction.
- Define the optional pre-update hook API family behind `SQLITE_ENABLE_PREUPDATE_HOOK` for observing row changes before they occur and for reading old/new column values during the callback.
- Expose `sqlite3_system_errno()` so callers can retrieve the platform-specific low-level cause of the most recent file-open or I/O failure.
- Define the opaque `sqlite3_snapshot` handle and its lifecycle for opening historical WAL read transactions.
- Expose database image serialization and deserialization APIs when `SQLITE_OMIT_DESERIALIZE` is not used.
- Expose `sqlite3_carray_bind_v2()` and the legacy-compatible `sqlite3_carray_bind()` wrapper for binding host arrays into the `carray()` table-valued function.
- Restore header state at the end of the generated SQLite C API header: undo the no-floating-point `double` macro, apply WASI defaults, close the C++ `extern "C"` block, and leave the final include-guard close for `mksqlite3.tcl`.

## Important APIs, Types, And Constants

- `sqlite3_stmt_scanstatus(sqlite3_stmt *pStmt, int idx, int iScanStatusOp, void *pOut)` returns one scan-status metric for a query-plan loop. It is documented as equivalent to `sqlite3_stmt_scanstatus_v2()` with `flags==0`.
- `sqlite3_stmt_scanstatus_v2(sqlite3_stmt *pStmt, int idx, int iScanStatusOp, int flags, void *pOut)` extends scan status to optionally cover all `EXPLAIN QUERY PLAN` elements, not only loop elements. `idx==-1` may target whole-query statistics for supported metrics. Out-of-range `idx` returns non-zero and leaves `*pOut` unchanged.
- `SQLITE_SCANSTAT_COMPLEX` is the only scan-status flag in this chunk. When set, indexes address all complex plan elements reported by `EXPLAIN QUERY PLAN`; when clear, indexes address only `SCAN...` and `SEARCH...` loop elements.
- `sqlite3_stmt_scanstatus_reset(sqlite3_stmt*)` zeros scan-status event counters for a prepared statement.
- `sqlite3_db_cacheflush(sqlite3*)` flushes dirty pager-cache pages for all schemas on a connection, including `main`, `temp`, and attached databases, subject to page-use and locking constraints.
- `sqlite3_preupdate_hook(sqlite3 *db, xPreUpdate, void *pArg)` installs or clears a single pre-update callback per database connection. It returns the previous callback context pointer.
- `sqlite3_preupdate_old(sqlite3*, int, sqlite3_value**)` and `sqlite3_preupdate_new(sqlite3*, int, sqlite3_value**)` expose old/new protected values for the current pre-update event. Valid call sites depend on the operation: old values are valid for `UPDATE`/`DELETE`, new values for `INSERT`/`UPDATE`.
- `sqlite3_preupdate_count(sqlite3*)` returns the column count for the row being changed.
- `sqlite3_preupdate_depth(sqlite3*)` reports trigger nesting depth for the current change, with direct top-level changes at depth 0.
- `sqlite3_preupdate_blobwrite(sqlite3*)` distinguishes `sqlite3_blob_write()`-driven pre-update events from normal deletes by returning the written blob column index, or `-1` otherwise.
- `sqlite3_system_errno(sqlite3*)` returns an OS-dependent error number associated with the most recent I/O or open failure, for example a Unix `errno` after `SQLITE_CANTOPEN`.
- `sqlite3_snapshot` is an opaque 48-byte public struct. The hidden byte array deliberately prevents callers from depending on the internal WAL header layout while keeping the ABI-sized object visible.
- `sqlite3_snapshot_get(sqlite3 *db, const char *zSchema, sqlite3_snapshot **ppSnapshot)` allocates a snapshot handle for the current read view of a WAL-mode schema. The caller must free successful handles with `sqlite3_snapshot_free()`.
- `sqlite3_snapshot_open(sqlite3 *db, const char *zSchema, sqlite3_snapshot *pSnapshot)` starts or repositions a read transaction so it reads from a historical snapshot instead of the newest database state.
- `sqlite3_snapshot_free(sqlite3_snapshot*)` destroys a snapshot handle allocated by `sqlite3_snapshot_get()`.
- `sqlite3_snapshot_cmp(sqlite3_snapshot *p1, sqlite3_snapshot *p2)` compares snapshot age for two handles associated with the same database file and current WAL generation.
- `sqlite3_snapshot_recover(sqlite3 *db, const char *zDb)` scans a persistent WAL file to make older valid frames available to `sqlite3_snapshot_open()`.
- `sqlite3_serialize(sqlite3 *db, const char *zSchema, sqlite3_int64 *piSize, unsigned int mFlags)` returns a byte image for a database schema. Without `SQLITE_SERIALIZE_NOCOPY`, it returns a caller-owned allocation from `sqlite3_malloc64()`.
- `SQLITE_SERIALIZE_NOCOPY` requests a direct pointer to SQLite's contiguous in-memory representation, when one exists, and avoids allocating a copy.
- `sqlite3_deserialize(sqlite3 *db, const char *zSchema, unsigned char *pData, sqlite3_int64 szDb, sqlite3_int64 szBuf, unsigned mFlags)` replaces a schema with an in-memory database backed by the supplied serialized bytes.
- `SQLITE_DESERIALIZE_FREEONCLOSE`, `SQLITE_DESERIALIZE_RESIZEABLE`, and `SQLITE_DESERIALIZE_READONLY` control ownership, growth, and mutability of the deserialized database buffer.
- `sqlite3_carray_bind_v2(sqlite3_stmt *pStmt, int i, void *aData, int nData, int mFlags, void (*xDel)(void*), void *pDel)` binds an array to the first argument of a `carray()` table-valued function invocation.
- `sqlite3_carray_bind(...)` is a compatibility wrapper equivalent to the v2 form with the destructor argument `D` set to the array pointer `P`.
- `SQLITE_CARRAY_INT32`, `SQLITE_CARRAY_INT64`, `SQLITE_CARRAY_DOUBLE`, `SQLITE_CARRAY_TEXT`, and `SQLITE_CARRAY_BLOB` identify the element layout passed to `carray()`. The unprefixed `CARRAY_*` aliases preserve legacy compatibility.

## Control Flow And Contracts

Scan-status callers prepare and execute a statement, then query `sqlite3_stmt_scanstatus_v2()` by metric and query-plan element index. With `SQLITE_SCANSTAT_COMPLEX` clear, the index space is filtered to loop-like plan nodes. With the flag set, it is aligned to all plan elements for which SQLite stored scan-status metadata. The API writes a type-specific value into `pOut`: counters are integer-like, estimates are `double`, and plan/name data are string pointers. `sqlite3_stmt_scanstatus_reset()` clears the accumulated execution and cycle counters without changing the statement program.

`sqlite3_db_cacheflush()` runs against a database connection, not a single schema. It only has useful flushing work when a write transaction is open. The flush loop skips dirty pages currently in use by active cursors and page 1, and it may acquire additional database locks before writing pages. If a needed lock is busy and cannot be obtained after the busy handler, that database is skipped and the routine continues with other schemas. A pure lock-skipped result returns `SQLITE_BUSY`; I/O, allocation, or other errors abort the operation immediately with that error code.

The pre-update hook registration is connection-local. Registering a callback overwrites the old callback, and registering a NULL callback disables it. The callback fires before real table changes for `INSERT`, `UPDATE`, and `DELETE`, but not for virtual table updates or system tables such as `sqlite_sequence` and `sqlite_stat1`. During the callback, the caller can ask for operation metadata, rowids, column counts, old/new column values, and trigger depth. The auxiliary routines are callback-scoped; using them outside the matching callback or with a different connection is explicitly undefined.

Pre-update rowid arguments have operation-specific meaning. For rowid-table `UPDATE` and `DELETE`, `iKey1` is the original rowid. For rowid-table `INSERT` and `UPDATE`, `iKey2` is the final rowid. For `WITHOUT ROWID` tables, and for rowid cases where the operation does not provide the corresponding old or new rowid, the value is undefined. `sqlite3_blob_write()` is documented as invoking the hook with `SQLITE_DELETE` because the new values are not available at that point; `sqlite3_preupdate_blobwrite()` is the disambiguation signal.

Snapshot control flow is WAL-specific. A caller must turn off autocommit with an explicit transaction before calling `sqlite3_snapshot_get()` or `sqlite3_snapshot_open()`. Snapshot get may automatically open a read transaction on the named schema if none exists, then returns a heap-allocated handle representing the current WAL read mark. Snapshot open either starts a read transaction on the requested snapshot or upgrades an existing read transaction, but an existing read transaction requires no active statements. If the snapshot has been overwritten by checkpointing, `sqlite3_snapshot_open()` returns `SQLITE_ERROR_SNAPSHOT`.

Snapshot recovery is a special repair/discovery path for persistent WAL files left on disk after all connections closed. Without recovery, a new connection may only be able to open the last WAL transaction through the snapshot API. `sqlite3_snapshot_recover()` scans the WAL for the named database and makes all valid snapshots visible to later `sqlite3_snapshot_open()` calls. It fails if a read transaction is already open or the database is not in WAL mode.

Serialization reads a database image and returns its byte representation. For ordinary on-disk databases, the image is equivalent to the database file. For in-memory and temp databases, it is the database image that would be written by a backup. The no-copy mode only succeeds when SQLite is already using a contiguous memory image for that schema, usually after deserialization. If no-copy succeeds, the pointer stays valid and unchanged until the next write on the connection or connection close, and applications must not modify it.

Deserialization disconnects the named schema and reopens it as an in-memory database using the caller-supplied buffer. `szDb` is the database image size and `szBuf` is the total available buffer size; `szBuf` must be at least `szDb`. If the buffer is larger and the database is not read-only, SQLite may append page-sized content up to `szBuf`. With `SQLITE_DESERIALIZE_RESIZEABLE`, SQLite may grow the buffer with `sqlite3_realloc64()`, but the docs constrain that flag to buffers also owned by SQLite through `SQLITE_DESERIALIZE_FREEONCLOSE`.

`carray()` binding stores a typed array pointer or copy on a prepared-statement parameter. The parameter index must be the first argument to the `carray()` table-valued function. Destructor handling follows SQLite's binding conventions with an extension: a custom destructor is invoked with the separate `pDel` argument in the v2 form, and it is invoked even if binding fails. `SQLITE_STATIC` means SQLite does not own the data. `SQLITE_TRANSIENT` means SQLite copies the array before returning and does not call the caller's destructor.

## State And Persistence Behavior

- Scan-status counters are statement-local runtime state attached to the VDBE program. Resetting them does not change database contents.
- `sqlite3_db_cacheflush()` affects pager-cache dirty state and database files, but it does not commit or roll back the active transaction. Pages written mid-transaction remain part of the transaction's normal durability and rollback/WAL semantics.
- Pre-update hook registration is mutable connection state. The callback context pointer is stored on the `sqlite3` handle and the previous pointer is returned when replacing it.
- Pre-update old/new `sqlite3_value` pointers are protected and temporary. They are destroyed when the pre-update callback returns and should not be retained.
- `sqlite3_system_errno()` exposes low-level connection error state stored by VFS/open paths; the value is platform-specific and meaningful only for recent open/I/O failures.
- Snapshot handles are heap objects whose public type is opaque. They encode WAL-index header state and remain useful only while their WAL generation and frames are still available.
- Snapshot validity depends on WAL persistence and checkpoint behavior. A checkpoint can make a historical snapshot unavailable, and WAL deletion/restart invalidates comparisons for older handles.
- Serialized database buffers returned without `SQLITE_SERIALIZE_NOCOPY` are caller-owned and must be freed with SQLite's allocator. No-copy buffers remain SQLite-owned.
- Deserialized buffers may become SQLite-owned, caller-owned, fixed-size, resizable, or read-only depending on flags. Applications must not modify or invalidate the buffer while the connection uses it.
- `carray()` bindings are prepared-statement parameter state. Data lifetime is governed by `SQLITE_STATIC`, `SQLITE_TRANSIENT`, or the custom destructor installed through `sqlite3_carray_bind_v2()`.
- The final `#undef double` restores the C token after earlier floating-point omission support. The WASI block forces `SQLITE_WASI`, disables loadable extensions by default, and defaults `SQLITE_THREADSAFE` to 0 if the caller has not set it.

## Dependencies And Integration Points

- `sqlite3_stmt_scanstatus*()` depends on the scan-status option and VDBE instrumentation in `vdbeapi.c`. It integrates with earlier scan-status constants and with `EXPLAIN QUERY PLAN` output.
- Scan-status cycle reporting depends on opcode execution counters and cycle accounting, including `SQLITE_SCANSTAT_NCYCLE` and the bytecode virtual table's `nexec` and `ncycle` columns referenced by the header comments.
- `sqlite3_db_cacheflush()` integrates with the pager layer for each attached schema and with the busy-handler mechanism used by the connection's locking code.
- The pre-update hook declarations depend on `SQLITE_ENABLE_PREUPDATE_HOOK`. Registration state lives on the `sqlite3` connection object, and value retrieval is tied to the internal update/delete/insert execution path.
- Pre-update callbacks use operation constants `SQLITE_INSERT`, `SQLITE_DELETE`, and `SQLITE_UPDATE` declared earlier in the public header. They expose `sqlite3_value` objects with protected lifetime rules.
- `sqlite3_system_errno()` is coupled to VFS implementations that preserve OS error numbers through failed opens and I/O operations. On Unix this maps naturally to `errno`; other VFSes define their own meaning.
- Snapshot APIs require `SQLITE_ENABLE_SNAPSHOT` and non-`SQLITE_OMIT_WAL` internals. Public functions in `main.c` call btree and pager snapshot helpers, which delegate to WAL functions such as `sqlite3WalSnapshotGet()`, `sqlite3WalSnapshotOpen()`, and snapshot comparison/check logic.
- Snapshot handles are documented in `sqlite.h.in` as 48 bytes because the WAL implementation currently stores `WalIndexHdr`-shaped data behind the opaque public type. Consumers must treat it as opaque despite the visible size.
- `sqlite3_serialize()` and `sqlite3_deserialize()` are omitted under `SQLITE_OMIT_DESERIALIZE`. Implementations live in the in-memory database/VFS path and interact with btree, pager, schema selection, and file-control hooks.
- Serialization and deserialization integrate with backup semantics, page-size/page-count logic, SQLite memory allocation (`sqlite3_malloc64()`, `sqlite3_free()`, `sqlite3_realloc64()`), and schema attachment rules.
- `sqlite3_deserialize()` cannot target `temp` and the docs warn that WAL-mode input database images are not supported as deserialized databases unless bytes 18 and 19 are changed to rollback-mode file-format values before the call.
- `sqlite3_carray_bind*()` depends on the `carray.c` table-valued function module and on `sqlite3_bind_pointer()` using the `"carray-bind"` pointer type. Extension access is exposed through `sqlite3ext.h` and `loadext.c`.
- `SQLITE_CARRAY_BLOB` uses `struct iovec`, so callers need the platform-visible iovec definition expected by the carray implementation.
- The WASI defaults affect extension loading and threading for the generated header on WebAssembly System Interface targets.
- The final comment notes that `mksqlite3.tcl` appends the closing `#endif` for `SQLITE3_H`, confirming this file is a template input to SQLite's amalgamation/header generation pipeline.

## Risks And Edge Cases

- `sqlite3_stmt_scanstatus_v2()` has undefined behavior if `iScanStatusOp` is not a valid scan-status option unless API armor catches it. Callers must pass a correctly typed `pOut` for the requested metric.
- The `SQLITE_SCANSTAT_COMPLEX` flag changes the meaning of `idx`. Tooling that mixes complex and non-complex indexing can silently ask for different plan elements.
- `idx==-1` is only documented as "may retrieve" whole-query statistics. Code should not assume all scan-status operations support whole-query values.
- Scan-status APIs exist only in builds with `SQLITE_ENABLE_STMT_SCANSTATUS`; applications and extensions need compile-time or runtime feature handling before linking against them.
- `sqlite3_db_cacheflush()` does not update `sqlite3_errcode()` or `sqlite3_errmsg()`. Callers relying on connection error state after a failure may report stale diagnostics.
- Cache flushing can return `SQLITE_BUSY` after partially flushing other attached databases. This creates observable partial progress without transaction completion.
- Pre-update auxiliary functions are explicitly undefined outside the callback or with the wrong connection. Misuse can expose invalid temporary values.
- Pre-update hooks do not fire for virtual tables or system tables, so audit/replication code using this hook alone can miss changes.
- Rowid callback arguments are undefined for several valid operation/table combinations, especially `WITHOUT ROWID` tables. Consumers must branch on table kind and operation instead of assuming values are meaningful.
- `sqlite3_blob_write()` appears as a `SQLITE_DELETE` pre-update event, which can confuse delete-tracking code unless it checks `sqlite3_preupdate_blobwrite()`.
- Snapshot APIs require non-autocommit transaction state. Calling them in SQLite's default autocommit mode returns `SQLITE_ERROR` and, for `snapshot_get()`, the docs leave read-transaction side effects undefined for some failure cases.
- `sqlite3_snapshot_get()` cannot create a snapshot until at least one transaction has been written to the current WAL file. Fresh WAL-mode databases with no WAL file are a documented failure case.
- Snapshot handles can be invalidated by writers or checkpointers depending on whether `sqlite3_snapshot_get()` opened the read transaction itself or reused an existing one.
- `sqlite3_snapshot_open()` requires the connection to know that the schema is in WAL mode. A newly opened connection may need a harmless read such as `PRAGMA application_id` before snapshot APIs work.
- Snapshot comparison is undefined for handles from different database files or from before the last WAL deletion/restart.
- `sqlite3_snapshot_recover()` is only for WAL files that persist across connection shutdown or abnormal process exit. It fails when a read transaction is open and should not be used as a general snapshot open retry.
- `sqlite3_serialize()` may return NULL for allocation failure, invalid schema, no no-copy contiguous representation, or other preparation/step failures. Callers need to inspect `piSize` and context, not only the pointer.
- `SQLITE_SERIALIZE_NOCOPY` returns SQLite-owned memory that becomes invalid after the next write or connection close. Modifying it is forbidden.
- `sqlite3_deserialize()` accepts potentially malformed database bytes and warns that SQLite may read slightly past `szDb`; untrusted inputs should include the recommended extra padding and still be treated as database parser attack surface.
- Deserialization fails with `SQLITE_BUSY` when the schema has an active read transaction or backup operation. Calling code must coordinate with readers and backups before replacing a schema.
- `SQLITE_DESERIALIZE_RESIZEABLE` without `SQLITE_DESERIALIZE_FREEONCLOSE` violates the documented ownership model and risks reallocating memory that SQLite does not own.
- Deserialized WAL-mode images will produce `SQLITE_CANTOPEN` when used unless the caller rewrites the database header file-format version bytes to rollback mode.
- `sqlite3_carray_bind_v2()` invokes custom destructors even on bind failure. Callers must not free the same data again after receiving an error.
- With `SQLITE_STATIC`, array memory must remain valid until SQLite finishes using the bound parameter. This includes the array of pointers for text and the `struct iovec` array and pointed-to blob memory for blob arrays.
- `SQLITE_TRANSIENT` copying can be expensive for large text/blob arrays and can fail with `SQLITE_NOMEM`; code must not assume binding is cheap.
- The unprefixed `CARRAY_*` constants can collide with application symbols, but they are intentionally retained for compatibility.
- WASI defaults may surprise embedders that expect loadable extensions or SQLite mutexes unless they explicitly define `SQLITE_OMIT_LOAD_EXTENSION`/`SQLITE_THREADSAFE` differently before including/building SQLite.

## Test Signals

- Build with `SQLITE_ENABLE_STMT_SCANSTATUS` and verify `sqlite3_stmt_scanstatus()` matches `sqlite3_stmt_scanstatus_v2(..., flags=0, ...)` for loop nodes.
- Exercise `SQLITE_SCANSTAT_COMPLEX` with plans containing non-loop `EXPLAIN QUERY PLAN` elements and verify index mapping differs from loop-only mode.
- Query valid and out-of-range scan-status indexes and confirm out-of-range calls return non-zero without mutating the output buffer.
- Reset scan status after statement execution and verify execution/cycle counters return to zero while statement execution remains valid.
- Run `sqlite3_db_cacheflush()` during write transactions with multiple attached schemas, with active cursors pinning dirty pages, and with a busy lock on one schema to verify partial flush plus `SQLITE_BUSY`.
- Verify cache-flush I/O or allocation failure returns immediately and does not rely on `sqlite3_errmsg()` being updated.
- Build with `SQLITE_ENABLE_PREUPDATE_HOOK` and cover callback registration replacement, disabling with NULL, returned previous context pointer, and operation metadata for insert/update/delete.
- Test pre-update value access for `UPDATE`, `DELETE`, and `INSERT`, including invalid old/new access patterns guarded in test builds.
- Cover trigger depth reporting for direct changes, top-level triggers, and nested triggers.
- Verify the hook excludes virtual tables and system tables, and separately cover `sqlite3_blob_write()` producing a delete-like callback with `sqlite3_preupdate_blobwrite()` returning the blob column.
- For snapshots, test failure in autocommit mode, failure on rollback-journal databases, failure before any WAL transaction exists, and success after a WAL write inside an explicit transaction.
- Test `sqlite3_snapshot_open()` with active statements on the target schema, invalid schema names, invalid snapshot data, and snapshots overwritten by checkpoint returning `SQLITE_ERROR_SNAPSHOT`.
- Test `sqlite3_snapshot_cmp()` for older/same/newer snapshots in the same WAL generation and avoid asserting behavior across WAL deletion or different database files.
- Test `sqlite3_snapshot_recover()` on a persistent WAL containing multiple transactions after reopening the database, and verify failure with an already-open read transaction.
- Test `sqlite3_serialize()` on on-disk, in-memory, temp, empty, and attached databases; verify size reporting, caller ownership, and NULL results under no-copy mode without a contiguous memory image.
- Test no-copy serialization after `sqlite3_deserialize()` and verify pointer stability until the next write and invalidation after write/close.
- Test `sqlite3_deserialize()` with fixed-size, resizable, read-only, and free-on-close buffers; include `szBuf==szDb`, extra capacity, growth past capacity, and failure cleanup behavior when `FREEONCLOSE` is set.
- Verify deserialization rejects `"temp"`, returns `SQLITE_BUSY` during active reads/backups, and fails or reports `SQLITE_CANTOPEN` for WAL-mode images unless header bytes are adjusted.
- Test `sqlite3_carray_bind_v2()` for all five element types, including text NULL entries and blob `struct iovec` entries.
- Test `carray()` destructor behavior for custom destructor success, custom destructor failure, `SQLITE_STATIC`, `SQLITE_TRANSIENT`, and the wrapper equivalence of `sqlite3_carray_bind()`.
- Build with `SQLITE_OMIT_FLOATING_POINT` and confirm the header's temporary `double` macro is undefined by the end of the header.
- Build for `__wasi__` and confirm the generated configuration defines `SQLITE_WASI`, omits loadable extensions by default, and defaults to single-threaded mode unless overridden.
