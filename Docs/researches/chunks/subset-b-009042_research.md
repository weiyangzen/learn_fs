# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 226498-234635

## Scope and Purpose

This chunk covers a late slice of SQLite's amalgamated extension code. It begins in the tail of the RBU VFS implementation, includes the complete `dbstat` and `sqlite_dbpage` virtual table modules, then enters most of the session extension through changeset generation, iteration, apply, changegroup merge, and the main rebase transformation loop. The range ends inside `sessionRebase()` after assigning an owned output buffer, before the local cleanup and public `sqlite3rebaser_*` wrappers in the next lines.

The code is compiled conditionally. RBU requires `!SQLITE_CORE || SQLITE_ENABLE_RBU`; `dbstat` and `dbpage` require their feature flags or test builds and no virtual-table omission; the session module requires both `SQLITE_ENABLE_SESSION` and `SQLITE_ENABLE_PREUPDATE_HOOK`.

Operationally, this chunk exposes low-level database introspection and replication/synchronization primitives:

- RBU VFS wrappers register and destroy a VFS that redirects selected file operations during resumable bulk update.
- `dbstat` scans btree pages and reports per-page or aggregate space usage.
- `sqlite_dbpage` reads and writes raw database pages through the pager.
- The session extension records table changes through preupdate hooks, serializes changesets/patchsets, parses and inverts changesets, applies changes with conflict handling, merges multiple changesets, and starts rebase support.

## RBU VFS Tail

The visible RBU section finishes VFS delegation and lifecycle APIs:

- `rbuVfsAccess()` has special handling for `SQLITE_ACCESS_EXISTS` during `RBU_STAGE_OAL`. It finds the main database wrapper with `rbuFindMaindb()`, detects whether SQLite is checking for the real WAL file while the RBU VFS wants an `*-oal` file, and either returns `SQLITE_CANTOPEN` or synthesizes existence from `rbuVfsFileSize()`.
- `rbuVfsFullPathname()`, dynamic library hooks, randomness, sleep, and current-time hooks are direct pass-throughs to `pRealVfs`.
- `rbuVfsGetLastError()` is a no-op returning 0.
- `sqlite3rbu_create_vfs()` allocates an `rbu_vfs`, copies a `sqlite3_vfs` template, points it at a parent VFS, sizes `szOsFile` to include `rbu_file` plus the parent file object, allocates a recursive mutex, and registers the new VFS as non-default.
- `sqlite3rbu_destroy_vfs()` only frees VFS objects whose `xOpen` is `rbuVfsOpen`, preventing accidental destruction of unrelated VFS registrations.
- `sqlite3rbu_temp_size_limit()` and `sqlite3rbu_temp_size()` expose per-RBU temporary storage accounting.

This code depends on earlier RBU types and functions outside the chunk, especially `rbu_vfs`, `rbu_file`, `sqlite3rbu`, `rbuVfsOpen()`, `rbuVfsDelete()`, `rbuVfsFileSize()`, `rbuFindMaindb()`, and the RBU stage constants.

## DBSTAT Virtual Table

`dbstat` implements a virtual table with schema:

`name, path, pageno, pagetype, ncell, payload, unused, mx_payload, pgoffset, pgsize, schema HIDDEN, aggregate HIDDEN`.

Important types:

- `StatCell` stores per-cell local payload size, child page number, overflow-page list, final overflow bytes, and overflow iteration cursor.
- `StatPage` stores copied page bytes, page number, btree path, parsed flags, cell count, unused bytes, parsed cells, right-child page, and maximum payload.
- `StatCursor` maintains the root-page statement, EOF/aggregate state, active schema, a fixed stack of 32 `StatPage` frames, and the current column values.
- `StatTable` stores the owning `sqlite3*` and default schema index.

Important APIs and methods:

- `statConnect()` resolves the optional schema argument, declares the virtual table, marks it `SQLITE_VTAB_DIRECTONLY`, and stores the default database index.
- `statBestIndex()` recognizes equality constraints on `schema`, `name`, and `aggregate`, refuses unusable constraints so the module remains right-most in joins, advertises natural `(name, path)` ordering, and sets `SQLITE_INDEX_SCAN_HEX`.
- `statOpen()`, `statClose()`, `statResetCsr()`, `statClearPage()`, and `statClearCells()` manage cursor and page/cell allocations.
- `getLocalPayload()` implements SQLite btree local-payload sizing for table leaves versus index/interior pages.
- `statDecodePage()` parses a copied btree page, validates page flags and freeblock chains, decodes cells, calculates unused bytes, local payload, maximum payload, child links, and overflow chains by reading overflow pages through the pager.
- `statGetPage()` obtains a pager page and copies it into a malloc buffer padded by `DBSTAT_PAGE_PADDING_BYTES` to tolerate small overreads while inspecting corrupt pages.
- `statSizeAndOffset()` calculates page size and file offset. It first tries ZIPVFS file-control opcode `230440`, then falls back to normal page-size arithmetic.
- `statNext()` is the main traversal state machine. It steps a root-page query, pushes child pages on `aPage[]`, walks cells and right children depth-first, emits overflow pages as separate rows, or accumulates the whole btree in aggregate mode.
- `statFilter()` builds a query over `sqlite_schema`, optionally constrains by table/index name, optionally orders by name, and starts traversal.
- `statColumn()` returns per-page values or aggregate values depending on `isAgg`.
- `sqlite3DbstatRegister()` registers module name `dbstat`.

Control flow is btree-oriented. `statFilter()` selects root pages, `statNext()` loads a root and decodes a page, then repeatedly emits the current page, its overflow pages, and descendants. In aggregate mode, it suppresses per-page rows and keeps walking until the current btree is exhausted, then returns one accumulated row.

State is cursor-local and read-only against database contents. It uses pager snapshots so WAL/uncommitted pager-visible state is reflected consistently with SQLite internals. Corrupt page structures generally clear parsed cells and label the page as `corrupted` instead of always failing, but impossible traversal depth returns `SQLITE_CORRUPT_BKPT`.

## SQLITE_DBPAGE Virtual Table

`sqlite_dbpage` is an eponymous virtual table for raw page access:

`pgno INTEGER PRIMARY KEY, data BLOB, schema HIDDEN`.

Important types and APIs:

- `DbpageCursor` tracks the current page number, max page number, pager, page-1 reference, schema index, and page size.
- `DbpageTable` stores the database handle plus pending truncate state (`iDbTrunc`, `pgnoTrunc`).
- `dbpageConnect()` declares the table, marks it `SQLITE_VTAB_DIRECTONLY` and `SQLITE_VTAB_USES_ALL_SCHEMAS`.
- `dbpageBestIndex()` plans schema and page-number equality constraints, with unique scan flags for `pgno=?`.
- `dbpageFilter()` resolves the schema, initializes pager/page-size information, bounds scans to one page if `pgno=?`, and pins page 1.
- `dbpageColumn()` returns `pgno`, a transient copy of page data, or schema name. It treats the pending-byte page as a zero blob because asking the pager for it is corrupt.
- `dbpageUpdate()` supports raw page replacement and extension through pager write calls. It rejects writes in defensive mode, rejects deletes, requires BLOB page data exactly equal to the page size, and interprets `INSERT(pgno, NULL)` for `pgno>1` as a pending truncate to `pgno-1`.
- `dbpageBeginTrans()` begins write transactions on all attached btrees because the updated schema may be supplied per row.
- `dbpageSync()` applies a pending truncate just before commit with `sqlite3PagerTruncateImage()`.
- `dbpageRollbackTo()` cancels pending truncation.
- `sqlite3DbpageRegister()` registers module name `sqlite_dbpage`.

This module is intentionally dangerous. It integrates directly with `Btree`, `Pager`, and `DbPage`; it can overwrite raw database pages and truncate the database image. The defensive-mode guard and direct-only virtual table configuration are important safety boundaries.

## Session Core Data Model

The session module begins with stream sizing constants and core structs:

- `sqlite3_session` owns the database handle, attached schema name, recording flags, auto-attach/filter settings, implicit-rowid-PK support, error state, memory accounting, optional max-changeset-size accounting, zero-blob value for `sqlite_stat1`, linked sessions on the same database, attached `SessionTable` list, and a `SessionHook`.
- `SessionHook` abstracts preupdate/diff access through `xOld`, `xNew`, `xCount`, and `xDepth`.
- `SessionBuffer` is a growable byte buffer for SQL strings, records, changesets, rebase blobs, and deferred constraint blobs.
- `SessionInput` abstracts fixed-buffer and streaming input, including current/next offsets and stream-discard policy.
- `sqlite3_changeset_iter` stores the current input stream, decoded table header, patchset/invert/skip-empty flags, current operation, table metadata, old/new value arrays, and optional conflict row statement.
- `SessionTable` stores table metadata, column/default/PK arrays, hidden-column mapping, rowid-PK/stat1 flags, hash-table buckets of `SessionChange`, and default-value statement.
- `SessionChange` stores one accumulated row change: operation, indirect flag, number of serialized fields, maximum output size estimate, serialized old/PK record bytes, and hash-chain link.

The on-disk/over-the-wire record format is explicitly architecture-independent: one type byte per field, varint lengths for text/blob, and big-endian 8-byte integer/float payloads. Changesets use `T` table headers and old/new records; patchsets use `P` headers and omit values not needed for conflict-free application; rebase blobs use table headers plus per-conflict insert/delete records and replace/omit flags.

## Serialization, Hashing, and Table Metadata

Important helper families:

- Varint and endian helpers: `sessionVarintPut()`, `sessionVarintLen()`, `sessionVarintGet()`, `sessionGetI64()`, and `sessionPutI64()`.
- Value serialization: `sessionSerializeValue()`, `sessionAppendValue()`, `sessionAppendCol()`, `sessionReadRecord()`, `sessionSerialLen()`, and `sessionValueSetStr()`.
- Buffer growth and SQL/string construction: `sessionBufferGrow()`, `sessionAppendStr()`, `sessionAppendPrintf()`, `sessionAppendByte()`, `sessionAppendVarint()`, `sessionAppendBlob()`, `sessionAppendInteger()`, and `sessionAppendIdent()`.
- PK hashing/comparison: `sessionPreupdateHash()`, `sessionChangeHash()`, `sessionChangeEqual()`, and `sessionPreupdateEqual()`.
- Record merge/update helpers: `sessionMergeRecord()`, `sessionMergeValue()`, `sessionMergeUpdate()`, `sessionSkipRecord()`, `sessionAppendRecordMerge()`, and `sessionAppendPartialUpdate()`.
- Table introspection: `sessionTableInfo()` reads `PRAGMA table_xinfo()` or synthesizes `sqlite_stat1` metadata; `sessionInitTable()` initializes `SessionTable`; `sessionReinitTable()` detects compatible schema growth; `sessionPrepareDfltStmt()`, `sessionUpdateOneChange()`, and `sessionUpdateChanges()` extend older change records with defaults after `ALTER TABLE ADD COLUMN`.

The hash table key is the row primary key. Tables without primary keys are ignored, unless implicit rowid-PK mode is enabled before attaching tables. `sqlite_stat1` is special: the module treats `(tbl, idx)` as a logical primary key and maps NULL `idx` values to a zero-length blob internally so serialized PK matching remains possible.

## Recording Changes

Session recording is built around SQLite's preupdate hook:

- `sqlite3session_create()` allocates a session, installs `xPreUpdate` as the database preupdate hook, and links the new session into the hook's linked list.
- `sqlite3session_delete()` removes the session from that linked list, restores the hook to the next session if needed, frees the zero blob, tables, changes, and the session object.
- `sqlite3session_attach()` either enables auto-attach (`zName==NULL`) or adds a named table to the session's ordered table list.
- `sqlite3session_table_filter()` configures an auto-attach filter.
- `sqlite3session_enable()` and `sqlite3session_indirect()` toggle recording and indirect-change marking under the database mutex.
- `sqlite3session_isempty()`, `sqlite3session_memory_used()`, `sqlite3session_object_config()`, and `sqlite3session_changeset_size()` expose state and configuration.

`xPreUpdate()` iterates all sessions attached to the connection, filters by enabled state and schema, auto-attaches tables if configured, and calls `sessionPreupdateOneChange()`. For UPDATE, it records both the old row (`SQLITE_UPDATE`) and the new PK identity (`SQLITE_INSERT`) so rowid/PK changes are represented correctly.

`sessionPreupdateOneChange()` initializes table metadata, handles schema growth, grows the per-table hash table, computes the PK hash from old or new values, ignores rows with NULL primary-key columns, finds any existing `SessionChange`, and either creates a serialized baseline record or updates direct/indirect and size-estimate metadata. It carefully separates fatal OOM from non-fatal hash-growth failures and propagates hard errors through `pSession->rc`.

## Diff and Changeset Generation

`sqlite3session_diff()` compares a table in the session database against the same table in another attached database. It installs `SessionDiffCtx` hooks over SELECT statements, checks that source and target schemas/PK layouts match, then records inserts, deletes, and modified rows using generated SQL:

- `sessionExprComparePK()` builds equality predicates for primary keys.
- `sessionExprCompareOther()` builds non-PK difference predicates.
- `sessionSelectFindNew()` and `sessionDiffFindNew()` find rows present in one database and not the other.
- `sessionAllCols()` and `sessionDiffFindModified()` join matching PK rows and record value differences.

`sessionGenerateChangeset()` produces changesets or patchsets. It wraps generation in a `SAVEPOINT changeset`, revalidates table schema, emits table headers with `sessionAppendTableHdr()`, prepares a PK lookup with `sessionSelectStmt()`, binds primary keys with `sessionSelectBind()`, then emits:

- `SQLITE_INSERT` with current full row values when the row still exists and the original op was insert.
- `SQLITE_UPDATE` through `sessionAppendUpdate()` when original values differ from current values.
- `SQLITE_DELETE` through `sessionAppendDelete()` when a previously existing row no longer exists.

Streaming variants call `xOutput` whenever the buffer exceeds `sessions_strm_chunk_size`. Non-streaming variants return an allocated buffer owned by the caller.

Public generation APIs in this chunk include `sqlite3session_changeset()`, `sqlite3session_changeset_strm()`, `sqlite3session_patchset()`, and `sqlite3session_patchset_strm()`.

## Changeset Iteration and Inversion

Iterator creation is centralized in `sessionChangesetStart()`, used by fixed-buffer and streaming public APIs:

- `sqlite3changeset_start()`
- `sqlite3changeset_start_v2()` with `SQLITE_CHANGESETSTART_INVERT`
- `sqlite3changeset_start_strm()`
- `sqlite3changeset_start_v2_strm()`

Input buffering is handled by `sessionInputBuffer()` and `sessionDiscardData()`. Streaming input keeps enough bytes buffered for the current table header or record, while `bNoDiscard` preserves record bytes for callers that need raw slices.

`sessionChangesetNextOne()` is the parser state machine. It reads `T` or `P` table headers, validates operation bytes, decodes old/new records or buffers raw record bytes, supports inverted iteration, shifts patchset UPDATE PK fields into old-value slots, and normalizes questionable changeset UPDATE records that include old non-PK values without corresponding new values. `sessionChangesetNext()` optionally skips empty UPDATEs.

Public iterator APIs include:

- `sqlite3changeset_next()`
- `sqlite3changeset_op()`
- `sqlite3changeset_pk()`
- `sqlite3changeset_old()`
- `sqlite3changeset_new()`
- `sqlite3changeset_conflict()`
- `sqlite3changeset_fk_conflicts()`
- `sqlite3changeset_finalize()`

`sessionChangesetInvert()` constructs an inverse changeset. INSERT and DELETE swap operation codes while preserving records. UPDATE reads old/new records, writes a new old record made from PK columns plus original new non-PK values, then writes a new new record from original old non-PK values with PK columns undefined. Public inversion APIs are `sqlite3changeset_invert()` and `sqlite3changeset_invert_strm()`.

## Applying Changesets

The apply path centers on `SessionApplyCtx`, which stores prepared statements, target schema metadata, cached UPDATE statements, deferred constraint buffers, optional rebase output, and flags for `sqlite_stat1`, deferred constraints, inverted constraint replay, rowid-PK mode, and no-op ignoring.

Statement construction and binding helpers:

- `sessionUpdateFind()` builds and caches UPDATE statements keyed by a bitmask of modified columns; cache size is limited by `SESSION_UPDATE_CACHE_SZ`.
- `sessionUpdateFree()` releases cached UPDATE statements.
- `sessionDeleteRow()` builds DELETE SQL using PK predicates plus optional non-PK data checks.
- `sessionSelectRow()` reuses `sessionSelectStmt()` for target-row lookup.
- `sessionInsertRow()` builds INSERT SQL over all target columns.
- `sessionStat1Sql()` prepares special SQL that maps zero-length-blob sentinel values back to NULL `idx`.
- `sessionBindValue()`, `sessionBindRow()`, and `sessionSeekToRow()` bind changeset values and seek target rows.

Conflict and retry flow:

- `sessionConflictHandler()` invokes the user callback with `SQLITE_CHANGESET_DATA`, `NOTFOUND`, `CONFLICT`, or `CONSTRAINT` depending on operation outcome and whether a matching PK row exists. It can defer constraint conflicts into `constraints`, reject invalid callback returns, and append rebase records through `sessionRebaseAdd()`.
- `sessionApplyOneOp()` attempts DELETE, UPDATE, or INSERT. It detects no-row changes as data/notfound conflicts and constraint failures as conflict/constraint cases.
- `sessionApplyOneWithRetry()` handles `SQLITE_CHANGESET_REPLACE`: retrying UPDATE/DELETE while ignoring data mismatches, or deleting a conflicting row in a `SAVEPOINT replace_op` before retrying INSERT.
- `sessionRetryConstraints()` replays deferred constraint changes until no progress is made or all succeed.
- `sessionChangesetApply()` runs the overall apply transaction. It optionally creates `SAVEPOINT changeset_apply`, enables deferred foreign keys, groups work by table, invokes the table filter, validates target schema and PK compatibility, prepares statements, applies each operation, retries deferred constraints, checks remaining foreign-key violations through the conflict handler, releases or rolls back the savepoint, returns optional rebase data, and restores `SQLITE_FkNoAction` state if requested.

Public apply APIs include `sqlite3changeset_apply_v2()`, `sqlite3changeset_apply()`, `sqlite3changeset_apply_v2_strm()`, and `sqlite3changeset_apply_strm()`.

## Changegroup and Rebase Logic

`sqlite3_changegroup` accumulates multiple changesets or patchsets into per-table hash tables and later serializes a merged result. It stores error state, patchset/changeset mode, a table list, a scratch record buffer, and optional schema database information for extending older records.

Important APIs and merge helpers:

- `sqlite3changegroup_new()` allocates an empty group.
- `sqlite3changegroup_schema()` attaches schema context for compatibility with changesets generated before added columns.
- `sqlite3changegroup_add()` and `sqlite3changegroup_add_strm()` parse input into the group.
- `sqlite3changegroup_add_change()` adds the current iterator entry.
- `sqlite3changegroup_output()` and `sqlite3changegroup_output_strm()` serialize accumulated changes.
- `sqlite3changegroup_delete()` frees all tables, records, schema strings, and scratch buffers.
- `sqlite3changeset_concat()` and `sqlite3changeset_concat_strm()` are convenience wrappers around a changegroup.
- `sessionChangesetFindTable()` finds/creates compatible `SessionTable` objects for incoming changes.
- `sessionChangesetExtendRecord()` appends default or undefined fields when combining changesets with fewer columns than the schema-aware group table.
- `sessionOneChangeToHash()` locates existing changes by PK, removes them, merges them, and reinserts the merged result.
- `sessionChangeMerge()` implements the operation-combination matrix: insert+update stays insert, insert+delete cancels out, update+update merges, update+delete becomes delete, delete+insert becomes update, and unsupported duplicate/out-of-order combinations discard the second operation. In rebase mode, it also uses `0xFF` markers for replaced fields.

`sqlite3_rebaser` is introduced as a wrapper around a `sqlite3_changegroup`. The visible `sessionRebase()` function rebases a local changeset against rebase records already loaded into that group:

- It iterates input changes with raw record access and detects new table headers.
- Patchsets are rejected for rebasing.
- If no rebase record matches the row, it copies the original operation and record.
- If a matching remote rebase change exists, it transforms local INSERT/UPDATE/DELETE according to the remote operation and whether the remote change was indirect.
- It can drop operations made obsolete by remote changes, convert INSERT into UPDATE, convert UPDATE into INSERT, or rewrite old/new records with `sessionAppendPartialUpdate()` and `sessionAppendRecordMerge()`.
- The chunk ends while `sessionRebase()` is transferring `sOut.aBuf` into `*ppOut`/`*pnOut`; cleanup and public `sqlite3rebaser_*` functions are in the following source lines.

## State and Persistence Behavior

RBU VFS state is persisted in the registered VFS object, its parent pointer, mutex, and per-file wrappers. The temp-size limit and current temp usage live on each `sqlite3rbu` handle.

`dbstat` state is transient cursor state. It copies page contents into cursor-owned buffers and frees parsed cell/overflow allocations as pages are popped from the traversal stack. It does not mutate the database.

`sqlite_dbpage` read state is transient, but write state persists through pager writes and commit-time truncation. `pgnoTrunc` is intentionally held on the virtual table object until `xSync` or rollback-to clears it.

Session state is persistent for the lifetime of the `sqlite3_session`: attached table metadata, change hash tables, memory accounting, max-size estimate, and error state remain until deletion or until changesets are generated. Generated changesets, patchsets, rebase blobs, and changegroup outputs are allocated buffers that the public API expects callers to free with SQLite allocation routines. Apply state is temporary and transaction-scoped, protected by savepoints and database mutexes.

Schema changes are handled conservatively. Added non-PK columns may be tolerated by extending existing records with default or undefined values. PK layout changes, removed columns, rowid-PK mode changes, or incompatible table definitions produce `SQLITE_SCHEMA`.

## Dependencies and Integration Points

This chunk depends heavily on SQLite internal APIs:

- Virtual table APIs: `sqlite3_module`, `sqlite3_vtab_config()`, `sqlite3_declare_vtab()`, `sqlite3_create_module()`, `sqlite3_index_info`, and xBestIndex/xFilter/xColumn/xUpdate contracts.
- Pager/btree internals: `Btree`, `Pager`, `DbPage`, `sqlite3BtreePager()`, `sqlite3PagerGet()`, `sqlite3PagerWrite()`, `sqlite3PagerUnref()`, `sqlite3BtreeGetPageSize()`, `sqlite3BtreeLastPage()`, `sqlite3BtreeBeginTrans()`, and related mutex enter/leave calls.
- Preupdate hooks: `sqlite3_preupdate_hook()`, `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, and `sqlite3_preupdate_blobwrite()`.
- VDBE/value internals: `sqlite3_value`, `sqlite3ValueNew()`, `sqlite3ValueSetStr()`, `sqlite3ValueFree()`, `sqlite3VdbeMemSetInt64()`, and `sqlite3VdbeMemSetDouble()`.
- SQL compiler/runtime APIs: `sqlite3_prepare_v2()`, `sqlite3_prepare()`, `sqlite3_step()`, `sqlite3_reset()`, `sqlite3_finalize()`, `sqlite3_bind_*()`, `sqlite3_column_*()`, `sqlite3_exec()`, and `sqlite3_db_status()`.
- Core utility APIs: SQLite malloc/realloc/free, `sqlite3_mprintf()`, `sqlite3_str`, varint helpers, identifier quoting through `%w`, and mutex APIs.

Integration points include command-line/diagnostic use of `dbstat`, privileged raw-page tooling through `sqlite_dbpage`, application-level replication/synchronization through the session extension, conflict handlers supplied by callers of changeset apply, and optional streaming callbacks for large changesets.

## Risks and Edge Cases

- The chunk starts inside `rbuVfsAccess()`, so preceding RBU open/delete/file-wrapper logic must be reconciled with earlier chunks.
- The chunk ends inside `sessionRebase()`, so the final cleanup and public rebaser wrapper APIs must be reconciled with the next chunk.
- `dbstat` uses a fixed 32-entry page stack. Extremely deep or corrupt btrees can trigger `SQLITE_CORRUPT_BKPT`.
- `dbstat` intentionally tolerates some corrupt page content by reporting `pagetype='corrupted'`; consumers should not interpret every row as proof of healthy btree structure.
- `statDecodePage()` reads overflow chains through the pager. Bad overflow pointers surface as pager errors or corrupt-state behavior.
- `sqlite_dbpage` can corrupt databases by writing arbitrary page images. `SQLITE_Defensive`, direct-only registration, page-size checks, and transaction boundaries are essential controls.
- `dbpageUpdate()` begins write transactions on all attached databases because schema is row data; this can increase lock scope.
- Changes for rows with NULL primary-key values are ignored by the session module because they cannot be matched reliably.
- Tables without primary keys are ignored unless implicit rowid-PK mode is enabled before tables are attached.
- `sqlite_stat1` requires special NULL/sentinel handling; mistakes there would break apply/merge behavior for statistics rows.
- Record parsing is defensive against negative/oversized lengths and malformed table headers, returning `SQLITE_CORRUPT_BKPT`.
- Streaming input discards old data unless `bNoDiscard` is set. Code paths that retain raw record pointers must enable no-discard behavior.
- Conflict callback return values are strictly validated. Returning `REPLACE` in unsupported contexts becomes `SQLITE_MISUSE`.
- Apply temporarily changes foreign-key behavior and can defer constraint conflicts. Failure paths must roll back savepoints and restore flags to avoid leaking changed connection state.
- Changeset concatenation order matters because the merge matrix is directional.
- Size and memory accounting rely on `sqlite3_msize()` and can diverge if allocations are not made through the session wrappers.

## Test Signals

Useful validation signals for this chunk:

- RBU VFS tests that create/destroy custom VFS names, use a parent VFS, enter OAL stage, and verify WAL/OAL access redirection and temp-size limits.
- `dbstat` tests over normal tables, indexes, overflow payloads, empty databases, aggregate mode, `schema=?`, `name=?`, `ORDER BY name,path`, attached databases, ZIPVFS file-control behavior, and deliberately corrupt btree pages.
- `sqlite_dbpage` tests for full scan, `pgno=?`, attached schema selection, pending-byte page reads, exact page-size BLOB writes, defensive-mode write rejection, NULL insert truncation, rollback cancellation, and commit-time truncation.
- Session recording tests for attach, auto-attach filters, enable/disable, indirect changes, UPDATE with changed PK, DELETE/INSERT cancellation, rowid implicit-PK mode, tables without PK, NULL PK values, and schema changes after recording starts.
- Changeset/patchset generation tests for inserts, deletes, updates, no-op updates, large streaming output, `sqlite_stat1`, UTF-8 conversion OOM paths, and max changeset size accounting.
- Iterator tests for fixed-buffer and streaming input, corrupt headers, corrupt record lengths, inversion flag behavior, patchset UPDATE PK movement, `old/new/op/pk/conflict/fk_conflicts` API misuse cases, and finalize error propagation.
- Apply tests for DATA, NOTFOUND, CONFLICT, CONSTRAINT, and FOREIGN_KEY conflict callbacks; `OMIT`, `ABORT`, and `REPLACE` outcomes; deferred constraints; no-op ignore; invert apply; no-savepoint mode; rebase output; schema mismatch logging; and `SQLITE_CHANGESETAPPLY_FKNOACTION`.
- Changegroup and concat tests for all merge matrix cases, patchset versus changeset mismatch, schema-aware extension of old records, streaming add/output, adding a single iterator change, and order preservation by table.
- Rebase tests for local INSERT/UPDATE/DELETE against remote insert/delete/update rebase records, indirect versus direct remote records, partial update field removal, generated empty updates, patchset rejection, and streaming threshold output.

## Cross-Chunk Notes

This is one chunk of the amalgamated `sqlite3.c` file. Adjacent chunks are needed to recover the start of `rbuVfsAccess()` and the definitions of RBU structures used here, plus the cleanup tail of `sessionRebase()` and public `sqlite3rebaser_*` APIs immediately after line 234635.
