# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 186321-194031

## Scope

This chunk begins at the tail of SQLite UTF-16 open handling, then covers public connection APIs from collation registration through compile-option diagnostics, the optional unlock-notify implementation, and the start of the FTS3/FTS4 module. The FTS portion includes the large format overview for varints, doclists, segment leaves, segment interior nodes, and segment directory tables; the private FTS3 header surface; tokenizer and hash-table interfaces; the FTS3 virtual table constructor and module methods; doclist/position-list merge helpers; segment-reader setup; cursor filtering and row retrieval; transaction/savepoint hooks; overloaded FTS SQL functions; module initialization; and the beginning of full-text query phrase evaluation through token-cost collection setup.

The code is part of SQLite's amalgamated source vendored under WiredTiger tests. It is not WiredTiger storage-engine code, but it provides a complete embedded SQLite implementation used by the test tree.

## Purpose

The first part exposes SQLite core public APIs and helper glue around database handles. It registers collations and collation-needed callbacks, stores per-connection client data, reports autocommit and errors, returns table column metadata, forwards file-control operations to pager/VFS objects, implements test-control verbs, builds URI filename memory layouts for VFS use, exposes attached database names and filenames, supports WAL snapshots when enabled, and reports compile-time options.

The unlock-notify section implements the `sqlite3_unlock_notify()` API for shared-cache locking. It tracks blocked connections in a global list protected by the static main mutex, detects deadlocks, groups callbacks by callback function, and invokes callbacks when blocking transactions end.

The FTS3/FTS4 section implements a virtual table module for full-text search. It defines how FTS doclists and segment btrees are encoded, parses `CREATE VIRTUAL TABLE ... USING fts3/fts4(...)` arguments, creates or connects to shadow tables, selects query plans for rowid lookup, MATCH lookup, or full scan, scans segment indexes, merges term doclists into phrase/prefix/OR/NEAR results, exposes snippet/offsets/matchinfo/optimize functions, registers built-in tokenizers, and starts per-query phrase readers with either full in-memory doclists or incremental doclist loading.

## Important APIs, Types, and Functions

- Collation APIs: `sqlite3_create_collation()`, `sqlite3_create_collation_v2()`, `sqlite3_create_collation16()`, `sqlite3_collation_needed()`, and `sqlite3_collation_needed16()` install comparison callbacks or factories under the connection mutex. The v2 form accepts an `xDel` destructor.
- Client-data APIs: `sqlite3_get_clientdata()` and `sqlite3_set_clientdata()` manage a linked list of `DbClientData` entries on `sqlite3.pDbData`, keyed by name and protected by `db->mutex`.
- Connection and diagnostics APIs: `sqlite3_get_autocommit()`, `sqlite3_extended_result_codes()`, `sqlite3_sleep()`, `sqlite3_global_recover()`, `sqlite3_thread_cleanup()`, `sqlite3_compileoption_used()`, and `sqlite3_compileoption_get()`.
- Error breakpoint helpers: `sqlite3ReportError()`, `sqlite3CorruptError()`, `sqlite3MisuseError()`, `sqlite3CantopenError()`, and debug-only OOM/corrupt-page variants log the error class and source line through `sqlite3_log()`.
- Schema metadata API: `sqlite3_table_column_metadata()` loads schema state, locates a table and column, handles rowid aliases, and returns declared type, collation, NOT NULL, primary-key, and autoincrement attributes.
- File-control and filename APIs: `sqlite3_file_control()`, `sqlite3_create_filename()`, `sqlite3_free_filename()`, `sqlite3_uri_parameter()`, `sqlite3_uri_key()`, `sqlite3_uri_boolean()`, `sqlite3_uri_int64()`, `sqlite3_filename_database()`, `sqlite3_filename_journal()`, `sqlite3_filename_wal()`, `sqlite3_db_name()`, `sqlite3_db_filename()`, `sqlite3_db_readonly()`, and private `sqlite3DbNameToBtree()`.
- Snapshot APIs under `SQLITE_ENABLE_SNAPSHOT`: `sqlite3_snapshot_get()`, `sqlite3_snapshot_open()`, `sqlite3_snapshot_recover()`, and `sqlite3_snapshot_free()` coordinate WAL snapshot handles with btree/pager transactions.
- `sqlite3_test_control()` verbs in this range include PRNG save/restore/seed, foreign-key no-action override, Bitvec tests, fault hooks, benign malloc hooks, pending-byte override, assert status, always/never corruption flags, localtime faulting, internal-function flags, extra schema checks, seek-count reporting, sort/count-of-view/optimization toggles, log-est conversion, byte-order probing, assertion of a pending byte invariant, FTS3 corruption test mode, tune parameters, SQL keyword counters, parser-coverage callbacks, parse-out handoff, and JSON self-check toggles where compiled in.
- Unlock-notify state and functions: static `sqlite3BlockedList`, `checkListProperties()`, `removeFromBlockedList()`, `addToBlockedList()`, `enterMutex()`, `leaveMutex()`, `sqlite3_unlock_notify()`, `sqlite3ConnectionBlocked()`, `sqlite3ConnectionUnlocked()`, and `sqlite3ConnectionClosed()`.
- FTS tokenizer interfaces: `sqlite3_tokenizer_module`, `sqlite3_tokenizer`, and `sqlite3_tokenizer_cursor` define tokenizer construction, destruction, open/close, token iteration, optional language-ID callbacks, and test counters.
- FTS hash interfaces: `Fts3Hash`, `Fts3HashElem`, `sqlite3Fts3HashInit()`, `sqlite3Fts3HashInsert()`, `sqlite3Fts3HashFind()`, `sqlite3Fts3HashFindElem()`, and `sqlite3Fts3HashClear()` back tokenizer/module lookup.
- Core FTS types: `Fts3Table`, `Fts3Cursor`, `Fts3Doclist`, `Fts3PhraseToken`, `Fts3Phrase`, `Fts3Expr`, `Fts3SegFilter`, `Fts3MultiSegReader`, `Fts3HashWrapper`, `TermSelect`, `TokenDoclist`, and the opening `Fts3TokenAndCost`.
- FTS table construction helpers: `sqlite3Fts3Dequote()`, `fts3CreateTables()`, `fts3DatabasePageSize()`, `fts3IsSpecialColumn()`, `fts3QuoteId()`, `fts3ReadExprList()`, `fts3WriteExprList()`, `sqlite3Fts3ReadInt()`, `fts3GobbleInt()`, `fts3PrefixParameter()`, `fts3ContentColumns()`, and `fts3InitVtab()`.
- FTS virtual table module methods: `fts3CreateMethod()`, `fts3ConnectMethod()`, `fts3BestIndexMethod()`, `fts3OpenMethod()`, `fts3CloseMethod()`, `fts3FilterMethod()`, `fts3NextMethod()`, `fts3EofMethod()`, `fts3ColumnMethod()`, `fts3RowidMethod()`, `fts3UpdateMethod()`, `fts3SyncMethod()`, `fts3BeginMethod()`, `fts3CommitMethod()`, `fts3RollbackMethod()`, `fts3RenameMethod()`, `fts3SavepointMethod()`, `fts3ReleaseMethod()`, `fts3RollbackToMethod()`, `fts3ShadowName()`, and `fts3IntegrityMethod()`.
- FTS varint and doclist primitives: `sqlite3Fts3PutVarint()`, `sqlite3Fts3GetVarintU()`, `sqlite3Fts3GetVarint()`, `sqlite3Fts3GetVarintBounded()`, `sqlite3Fts3GetVarint32()`, `sqlite3Fts3VarintLen()`, `fts3GetDeltaVarint()`, `fts3GetReverseVarint()`, `fts3PutDeltaVarint()`, `fts3GetDeltaVarint3()`, and `fts3PutDeltaVarint3()`.
- FTS position/doclist merge helpers: `fts3PoslistCopy()`, `fts3ColumnlistCopy()`, `fts3ReadNextPos()`, `fts3PutColNumber()`, `fts3PoslistMerge()`, `fts3PoslistPhraseMerge()`, `fts3PoslistNearMerge()`, `fts3DoclistOrMerge()`, `fts3DoclistPhraseMerge()`, `sqlite3Fts3FirstFilter()`, `fts3TermSelectMerge()`, `fts3TermSelectFinishMerge()`, `fts3DoclistCountDocids()`, `sqlite3Fts3DoclistPrev()`, and `sqlite3Fts3DoclistNext()`.
- FTS segment and term selection: `fts3ScanInteriorNode()`, `fts3SelectLeaf()`, `fts3SegReaderCursorAppend()`, `fts3SegReaderCursor()`, `sqlite3Fts3SegReaderCursor()`, `fts3SegReaderCursorAddZero()`, `fts3TermSegReaderCursor()`, `fts3SegReaderCursorFree()`, and `fts3TermSelect()`.
- FTS overloaded SQL functions: `fts3FunctionArg()`, `fts3SnippetFunc()`, `fts3OffsetsFunc()`, `fts3OptimizeFunc()`, `fts3MatchinfoFunc()`, and `fts3FindFunctionMethod()`.
- FTS module initialization: `sqlite3Fts3Init()` registers auxiliary FTS objects, tokenizers (`simple`, `porter`, `unicode61`, optional `icu`), overloaded scalar functions, `fts3`, `fts4`, and tokenizer virtual-table support. `hashDestroy()` reference-counts shared tokenizer hash storage.
- FTS query evaluation setup: `fts3EvalAllocateReaders()`, `fts3EvalPhraseMergeToken()`, `fts3EvalPhraseLoad()`, `fts3EvalDeferredPhrase()`, `fts3EvalPhraseStart()`, `fts3EvalDlPhraseNext()`, `incrPhraseTokenNext()`, `fts3EvalIncrPhraseNext()`, `fts3EvalPhraseNext()`, `fts3EvalStartReaders()`, and the initial `fts3EvalTokenCosts()`.

## Control Flow and Contracts

Public SQLite APIs generally follow a pattern of API-armor checks, entering `db->mutex`, delegating to private helpers, converting the result through `sqlite3ApiExit()` where appropriate, and leaving the mutex. `sqlite3_table_column_metadata()` additionally enters all btrees while loading schema state and leaves them before setting error state and outputs.

`sqlite3_file_control()` resolves a database name to a `Btree`, enters that btree, maps several common opcodes directly to pager data (`SQLITE_FCNTL_FILE_POINTER`, `VFS_POINTER`, `JOURNAL_POINTER`, `DATA_VERSION`, `RESERVE_BYTES`, `RESET_CACHE`), and forwards all other opcodes to `sqlite3OsFileControl()`. It preserves the busy-handler recursion count across the VFS call.

URI filename helpers depend on a precise memory layout: four zero bytes precede the database filename, URI key/value pairs follow the database filename, then journal and WAL filenames follow. `databaseName()` scans backward to find the four-zero sentinel. Passing arbitrary strings to these APIs violates that contract and can corrupt memory.

Unlock notify is a three-state list protocol over `sqlite3.pBlockingConnection`, `pUnlockConnection`, `xUnlockNotify`, and `pUnlockArg`. Registering a callback cancels the prior one, invokes immediately if no blocker remains, detects cycles by following `pUnlockConnection`, or inserts the connection into `sqlite3BlockedList` grouped by callback function. Unlocking a connection clears blockers, batches callback arguments for each callback function, grows the argument array under benign-malloc markers, and falls back to smaller callback batches if allocation fails.

FTS virtual table creation routes both xCreate and xConnect through `fts3InitVtab()`. It parses tokenizer arguments, FTS4 `key=value` options, content-table columns, prefix indexes, compression/uncompression functions, `order=desc`, language ID, and not-indexed columns. It allocates `Fts3Table` as one contiguous object containing column pointers, prefix-index metadata, not-indexed flags, table/database names, and column-name copies.

`fts3BestIndexMethod()` selects among full scan, docid lookup, and MATCH search. MATCH constraints on user columns override rowid lookup to avoid planner shapes that leave MATCH unusable. The method encodes language-ID and docid range constraints in high bits of `idxNum`, assigns argv positions, advertises rowid ordering when possible, and marks docid equality unique on newer SQLite versions.

`fts3FilterMethod()` decodes `idxNum`, clears any previous cursor state, sets docid bounds and scan direction, parses MATCH expressions through the tokenizer, starts FTS expression evaluation, closes segment readers, prepares content-table SELECTs for full scans or docid lookups, and advances to the first row via `fts3NextMethod()`.

FTS content access is lazy for full-text matches. MATCH evaluation identifies the next matching docid and sets `isRequireSeek`; user-column reads, snippet, offsets, and matchinfo call `fts3CursorSeek()` to prepare or reuse a rowid lookup statement and fetch the content row only when needed.

FTS segment lookup descends segment interior nodes using prefix-compressed terms. `fts3ScanInteriorNode()` reconstructs terms, validates prefix/suffix bounds, and identifies child block ranges. `fts3SelectLeaf()` recursively loads interior blocks until it narrows to leaf block IDs that may contain the target term or prefix.

Doclist and position-list logic assumes FTS3 encoding: docids are varint deltas ordered ascending or descending, position lists terminate with `POS_END` (`0`), column switches use `POS_COLUMN` (`1`), and actual positions are delta encoded with `+2`. The merge helpers preserve these encodings while computing OR, exact phrase, NEAR, first-position, prefix, and incremental phrase results.

`fts3TermSelect()` configures a segment filter, iterates merged segment readers, and merges all returned doclists through `TermSelect`. Prefix searches can combine many term doclists pair-wise to limit memory growth. Exact phrases load each token's term doclist and repeatedly apply `fts3DoclistPhraseMerge()` based on token distance.

Phrase evaluation can be full or incremental. `fts3EvalPhraseStart()` chooses incremental loading only when the scan direction matches index order, the phrase has at most four tokens, no incompatible prefix or first-token constraints exist, and at least one token has an incremental segment reader. Otherwise it materializes the full phrase doclist in memory.

Incremental phrase advancement walks each token iterator until all non-ignored tokens agree on one docid, then merges position lists to prove the phrase occurs in that row. Deferred FTS4 tokens are resolved later against row-local deferred token lists and intersected with undeferred phrase positions.

## State and Persistence Behavior

Core connection state mutated here includes collation hashes and callbacks, per-connection client data, `db->autoCommit`, `db->errMask`, `db->pDbData`, collation-needed callbacks, busy-handler counters during file-control, snapshot pager state, test-control global flags, and compile-option readout.

`sqlite3_set_clientdata()` owns destructor calls for replaced or removed values. If allocation of a new entry fails, it calls the destructor for the incoming data before returning `SQLITE_NOMEM`.

Snapshot APIs are transaction-sensitive. They require autocommit to be disabled, reject write transactions, temporarily manipulate pager snapshot state, and may begin or commit read transactions to validate or open snapshot handles.

Unlock-notify state is process-global for the blocked list and connection-local for each wait relationship. All list mutation is protected by `SQLITE_MUTEX_STATIC_MAIN`; each public registration also holds the target connection mutex.

FTS3/FTS4 durable state is stored in shadow tables. Internal-content tables create `%_content`, `%_segments`, `%_segdir`, optional `%_docsize`, and optional `%_stat`. External-content FTS4 tables skip `%_content` and derive columns from the external table when not specified. Destroy and rename methods drop or rename the matching shadow tables.

`Fts3Table` persists across virtual table connections. It owns prepared statements, generated read/write expression strings, tokenizer instance, tokenizer hash references, pending-term hash tables for each prefix index, cached segment metadata, page-size/node-size settings, autoincremental merge settings, transaction/savepoint debug state, and options such as FTS4, docsize/stat presence, descending docid order, external content, language ID, and not-indexed columns.

`Fts3Cursor` persists for a virtual table scan. It owns the prepared content statement, parsed MATCH expression tree, generated doclist buffers, current docid, bounds, scan direction, language ID, deferred tokens, and matchinfo buffer. `fts3ClearCursor()` finalizes or caches statements, frees doclists and expressions, and zeroes all fields past the base cursor.

FTS write state is buffered in pending terms until xSync, savepoint flushing, or explicit flush paths. xSync flushes pending terms, may launch automatic incremental merge based on newly added leaves and max segment level, closes segment caches, and restores the connection's last-insert-rowid.

Transaction hooks keep FTS buffers coherent with SQLite transaction boundaries. xBegin resets merge accounting and resolves legacy `%_stat` presence. xCommit expects pending terms already flushed. xRollback and xRollbackTo clear pending terms when their savepoint boundary requires it. xSavepoint forces a flush by executing an internal `INSERT INTO fts_table(fts_table) VALUES('flush')` command unless savepoint handling is temporarily ignored during rename.

FTS expression state is split between parse-time fields (`Fts3PhraseToken.z/n/isPrefix/bFirst`, `Fts3Phrase.nToken/iColumn`, `Fts3Expr` tree shape) and evaluation fields (`pSegcsr`, `pDeferred`, `doclist`, `bIncr`, `iDoclistToken`, `iDocid`, `bEof`, `bStart`, `bDeferred`, `aMI`).

## Dependencies and Integration Points

The core API section depends on SQLite connection mutexes, schema loading, btree locks, pager/VFS interfaces, UTF conversion, collation lookup, value allocation, SQLite memory allocation, error propagation, WAL snapshot functions, compile-option generation, and optional API armor.

Unlock notify integrates with shared-cache btree locking. Other code calls `sqlite3ConnectionBlocked()` when an operation is blocked by another connection, `sqlite3ConnectionUnlocked()` when a transaction releases locks, and `sqlite3ConnectionClosed()` during connection teardown.

FTS3 depends on many SQLite subsystems: virtual table APIs, SQL preparation/execution, tokenizer modules, module registration/destructors, SQLite memory allocation, varint utilities, btree/pager page-size pragmas, schema metadata, integrity checking, overloaded scalar functions, extension initialization, and test-only hooks.

The FTS shadow tables integrate with the ordinary SQL engine. Constructors issue `CREATE TABLE` for shadow storage; read paths prepare SELECTs against `%_content` or external content tables; savepoint flushes execute SQL against the virtual table itself; rename/destroy use ordinary DDL.

Segment readers are implemented by later/other FTS routines declared in `fts3Int.h`, including `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, `sqlite3Fts3SegReaderFinish()`, `sqlite3Fts3SegReaderNew()`, `sqlite3Fts3SegReaderPending()`, `sqlite3Fts3AllSegdirs()`, `sqlite3Fts3ReadBlock()`, `sqlite3Fts3MsrIncrStart()`, `sqlite3Fts3MsrIncrNext()`, and `sqlite3Fts3MsrOvfl()`.

Deferred-token support integrates with FTS4 deferred token caches through `sqlite3Fts3DeferToken()`, `sqlite3Fts3CacheDeferredDoclists()`, `sqlite3Fts3DeferredTokenList()`, and cleanup helpers. When `SQLITE_DISABLE_FTS4_DEFERRED` is defined, these paths compile to no-ops or are omitted.

Snippet, offsets, matchinfo, and optimize integrate through the special hidden table-name column: `fts3ColumnMethod()` returns a typed pointer to the active cursor, and overloaded SQL functions retrieve it with `sqlite3_value_pointer(..., "fts3cursor")`.

Within WiredTiger, the integration concern is vendored SQLite test behavior: compile flags, FTS availability, tokenizer selection, corruption handling, and fault/test controls can affect SQLite-backed test scenarios even though WiredTiger does not call these internal functions directly.

## Risks and Edge Cases

- Most public APIs rely on connection mutex discipline. Missing mutex entry or exit would expose connection-local state such as collation callbacks, client data, error state, and attached database metadata to races.
- `sqlite3_get_clientdata()` and `sqlite3_set_clientdata()` do not include API-armor checks in this chunk. Null `db` or `zName` misuse would dereference through the connection or call `strcmp()` on a null pointer.
- `sqlite3_table_column_metadata()` treats views as not found, has special rowid alias behavior, and sets output parameters even on errors. Callers must not assume output pointers are untouched after failure.
- `sqlite3_file_control()` trusts `pArg` to match the opcode. Incorrect pointer types for built-in opcodes cause memory corruption at the caller boundary.
- Filename helper APIs require pager-created or `sqlite3_create_filename()`-created strings. `databaseName()` scans backward and cannot validate arbitrary input safely.
- Snapshot APIs contain subtle database index tests (`iDb==0 || iDb>1`) and transaction-state requirements. Invalid database names leave `rc` as `SQLITE_ERROR`; write transactions reject snapshot operations.
- `sqlite3_test_control()` is intentionally broad and can mutate global flags, PRNG seeding, pending-byte layout, parser coverage callbacks, and debug behavior. It is not a stable application-control plane.
- Unlock-notify callback invocation happens while the static main mutex is still held in this implementation path. Callback behavior must avoid operations that would deadlock on mutex ordering.
- Unlock-notify deadlock detection only follows registered unlock wait chains. Incorrect maintenance of `pUnlockConnection` or list grouping would either miss deadlocks or report false `SQLITE_LOCKED`.
- FTS constructor parsing has many option interactions. `content=` disables compression functions; missing only one of `compress=` or `uncompress=` is an error; unknown FTS4 options are errors; `prefix=` parsing can silently drop zero entries; and unresolved `notindexed=` names become constructor errors.
- FTS3 varint encoding differs from SQLite core varints: it is little-endian and can be up to 10 bytes. Reusing core varint assumptions here would corrupt doclists and segment nodes.
- Segment interior scanning validates prefix/suffix lengths, zero suffixes, and height descent. Corrupt segment blobs must return `FTS_CORRUPT_VTAB` rather than overread or loop indefinitely.
- Position-list merge code is pointer-heavy and often edits buffers in place. Padding (`FTS3_BUFFER_PADDING`, `FTS3_VARINT_MAX`) is essential, especially with descending docids where output varints may grow.
- `fts3TermSelectMerge()` sometimes stores a borrowed `aDoclist` pointer from a segment reader in `TermSelect` for pairwise merging. Later merges must not free borrowed buffers unless they were replaced by allocated merge output.
- `fts3CursorSeek()` treats a missing `%_content` row as corruption only for internal-content FTS tables. External-content tables may legitimately miss rows or reflect external table state differently.
- `p->bLock` prevents recursive virtual table operations while preparing or stepping internal SQL. Incorrect increments would either block legitimate operations or permit reentry into the same virtual table.
- xSavepoint flushes pending terms by executing SQL against the FTS table. `bIgnoreSavepoint` is required to prevent recursive savepoint behavior during this internal flush and during rename.
- Incremental phrase loading is limited to short phrases and compatible segment readers. A mistaken `bLookup` setting can cause the evaluator to assume it can incrementally merge doclists that actually require full materialization.
- Deferred-token phrase handling replaces or frees `doclist.pList` based on `bFreeList`. Ownership mistakes here would leak, double-free, or leave the phrase pointing at freed memory.

## Test Signals

Useful validation signals for this chunk include:

- Core API tests for collation registration/destructor behavior, UTF-16 collation names, collation-needed callbacks, client-data replacement/removal destructor calls, autocommit reporting, and extended result-code masking.
- Metadata tests for ordinary columns, rowid aliases, integer primary keys, AUTOINCREMENT, views, missing tables/columns, attached database names, and schema-load errors.
- VFS/file-control tests covering file pointer, VFS pointer, journal pointer, data version, reserve bytes, reset cache, unknown op forwarding, and busy-handler recursion preservation.
- URI filename tests using `sqlite3_create_filename()` and VFS xOpen filenames to validate parameter lookup, boolean/int64 parsing, key enumeration, and database/journal/WAL extraction.
- WAL snapshot tests for get/open/recover/free across autocommit-disabled read transactions, write transaction rejection, invalid database names, active statements, and stale snapshot handling.
- Unlock-notify tests for immediate callback, cancellation, callback replacement, deadlock detection, grouped callback batching, connection close cleanup, malloc-failure fallback during callback array growth, and shared-cache blocked/unlocked transitions.
- FTS virtual table constructor tests for FTS3 vs FTS4, tokenizer selection, prefix indexes, `matchinfo=fts3`, `compress`/`uncompress`, `order=desc`, external `content=`, `languageid=`, `notindexed=`, default column creation, and invalid option diagnostics.
- Shadow-table tests for create, destroy, rename, xShadowName recognition, and external-content behavior where `%_content` is not owned by FTS.
- Query planner tests for MATCH constraints, unusable MATCH constraints, rowid/docid equality and ranges, language-ID constraints, order-by consumption in ascending and descending scans, and estimated row/cost behavior.
- Cursor tests for full scans, docid lookup, MATCH lookup, lazy content seeking, EOF cleanup, rowid/column/langid hidden columns, and content corruption detection.
- FTS doclist tests for varint read/write, bounded varint reads, ascending and descending docid deltas, reverse iteration, OR merge, exact phrase merge, NEAR merge, prefix term merge, first-token filtering, and zero-padding after NEAR trimming.
- Segment-reader tests for pending terms plus persistent segments, prefix-index selection, root-only segments, interior-node leaf narrowing, corrupt interior node detection, and segment cursor cleanup.
- Transaction tests for pending-term flush on xSync and xSavepoint, rollback clearing, rollback-to savepoint boundaries, automatic incremental merge thresholds, last-insert-rowid restoration, and legacy `%_stat` discovery.
- Overloaded function tests for `snippet()`, `offsets()`, `matchinfo()`, and `optimize()` argument validation, cursor pointer extraction, lazy seek behavior, and result/error codes.
- FTS initialization tests for tokenizer hash registration/destruction, built-in tokenizer availability, optional unicode/ICU paths, `fts3_tokenizer` virtual table setup, test-only expression interfaces, and module registration for both `fts3` and `fts4`.
- Deferred and incremental evaluation tests for all-deferred phrases, mixed deferred/undeferred phrases, short phrases eligible for incremental loading, prefix tokens without prefix indexes, `^first` tokens, descending-order scans, and OOM during temporary position-list allocation.
