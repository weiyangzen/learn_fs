# subset-b-008733 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3.c

## Purpose
`fts3.c` is the central SQLite FTS3/FTS4 virtual-table implementation unit. It registers the `fts3` and `fts4` modules, parses virtual-table constructor options, declares the virtual table schema, creates and drops shadow tables, implements most read-side virtual-table methods, exposes the overloaded `snippet()`, `offsets()`, `matchinfo()`, and `optimize()` functions, and drives full-text query evaluation over FTS segment b-trees and doclists.

The file also documents and implements core FTS3 encodings: FTS3 little-endian varints, doclists, position lists, segment leaf/interior/root nodes, segment directories, merge-level behavior, and delete/update replacement semantics. Write-side mutation and low-level segment IO are mostly implemented in other FTS3 files, but this file owns the query planner interface, query cursor lifecycle, doclist merging, expression traversal, and extension initialization.

## Important APIs, Types, And Functions
The extension entry points are `sqlite3Fts3Init(sqlite3 *db)` and, for loadable builds, `sqlite3_fts3_init()`. `sqlite3Fts3Init()` registers `fts4aux`, built-in tokenizers, the tokenizer helper table, overloaded scalar functions, the `fts3` and `fts4` virtual-table modules, and the tokenize virtual table.

The `fts3Module` `sqlite3_module` table wires SQLite callbacks to local implementations: `fts3CreateMethod`, `fts3ConnectMethod`, `fts3BestIndexMethod`, `fts3OpenMethod`, `fts3CloseMethod`, `fts3FilterMethod`, `fts3NextMethod`, `fts3EofMethod`, `fts3ColumnMethod`, `fts3RowidMethod`, transaction callbacks, `fts3FindFunctionMethod`, `fts3RenameMethod`, `fts3ShadowName`, and `fts3IntegrityMethod`.

Constructor parsing is centered on `fts3InitVtab()`. It handles tokenizer arguments, FTS4-only options such as `matchinfo=fts3`, `prefix=`, `compress=`, `uncompress=`, `order=`, `content=`, `languageid=`, and `notindexed=`, builds the `Fts3Table` allocation, initializes pending-term hash tables for main and prefix indexes, prepares read/write expression lists, optionally creates shadow tables, and declares the vtab schema.

Utility APIs exported to sibling FTS3 files include `sqlite3Fts3PutVarint()`, `sqlite3Fts3GetVarint()`, `sqlite3Fts3GetVarintU()`, `sqlite3Fts3GetVarintBounded()`, `sqlite3Fts3GetVarint32()`, `sqlite3Fts3VarintLen()`, `sqlite3Fts3Dequote()`, `sqlite3Fts3ErrMsg()`, `sqlite3Fts3ReadInt()`, `sqlite3Fts3CreateStatTable()`, `sqlite3Fts3DoclistPrev()`, `sqlite3Fts3FirstFilter()`, `sqlite3Fts3EvalTestDeferred()`, `sqlite3Fts3EvalPhraseStats()`, `sqlite3Fts3EvalPhrasePoslist()`, `sqlite3Fts3MsrCancel()`, and `sqlite3Fts3EvalPhraseCleanup()`.

Segment-reader integration is exposed through `sqlite3Fts3SegReaderCursor()`. Internally, `fts3SegReaderCursor()` adds pending-term and persisted segment readers, uses `fts3SelectLeaf()` and `fts3ScanInteriorNode()` to narrow b-tree leaf ranges, and appends readers into `Fts3MultiSegReader`. `fts3TermSegReaderCursor()` chooses prefix-index readers when possible, falling back to the main index for exact or prefix scans.

Doclist and position-list manipulation is implemented by helpers such as `fts3PoslistCopy()`, `fts3ColumnlistCopy()`, `fts3ReadNextPos()`, `fts3PoslistMerge()`, `fts3PoslistPhraseMerge()`, `fts3PoslistNearMerge()`, `fts3DoclistOrMerge()`, `fts3DoclistPhraseMerge()`, `fts3TermSelectMerge()`, and `fts3TermSelectFinishMerge()`. These routines are the backbone of OR, phrase, prefix, and NEAR matching.

Full-text evaluation uses `fts3EvalStart()`, `fts3EvalAllocateReaders()`, `fts3EvalStartReaders()`, `fts3EvalPhraseStart()`, `fts3EvalPhraseLoad()`, `fts3EvalPhraseNext()`, `fts3EvalNextRow()`, `sqlite3Fts3EvalTestDeferred()`, `fts3EvalNearTest()`, and `fts3EvalNext()`. Matchinfo statistics are gathered through `fts3EvalGatherStats()`, `fts3EvalUpdateCounts()`, and `sqlite3Fts3EvalPhraseStats()`.

## Control Flow
Module initialization starts in `sqlite3Fts3Init()`: initialize optional tokenizer modules, register `fts4aux`, create a reference-counted tokenizer hash, insert tokenizer modules, install test hooks when enabled, register overloaded functions, then create `fts3`, `fts4`, and tokenize virtual-table modules. The `hashDestroy()` callback decrements and finally clears the shared tokenizer hash.

`CREATE VIRTUAL TABLE ... USING fts3/fts4` flows through `fts3CreateMethod()` into `fts3InitVtab(isCreate=1)`. The initializer parses module arguments, resolves external content columns if `content=` is used without explicit columns, creates a default `content` column if none are supplied, initializes the requested tokenizer or the `simple` tokenizer, parses prefix indexes, allocates one contiguous `Fts3Table` object, builds shadow-table SQL fragments, creates `%_content`, `%_segments`, `%_segdir`, and optional `%_docsize`/`%_stat`, records page size, and calls `sqlite3_declare_vtab()`. `xConnect` follows the same path without creating shadow tables and marks legacy non-FTS4 `%_stat` detection as unknown.

Query planning enters `fts3BestIndexMethod()`. It prefers `docid`/`rowid` equality, then usable `MATCH`, then full content scan. It also records hidden `languageid` and docid range constraints in high `idxNum` bits and can consume rowid ordering in either direction. If a usable `MATCH` is unavailable but present, it returns a very high estimated cost so SQLite avoids a plan that would later fail.

Query execution starts with `fts3FilterMethod()`. It clears any reused cursor, decodes `idxNum`, records docid bounds and requested order, and either prepares a content scan statement, prepares a seek statement for direct docid lookup, or parses the `MATCH` expression with `sqlite3Fts3ExprParse()` and calls `fts3EvalStart()`. `fts3NextMethod()` then advances either the prepared SQLite statement or the FTS expression evaluator. For full-text matches, rows initially carry only docid/position-list state; `fts3ColumnMethod()` lazily calls `fts3CursorSeek()` when user column values or snippet-like functions need the underlying content row.

Full-text startup allocates a `Fts3MultiSegReader` for each query token, optionally estimates token costs and defers expensive common tokens for FTS4, and starts each phrase either as an incremental phrase iterator or by fully loading and merging token doclists. Prefix queries may use configured prefix indexes when their length matches, may scan a longer prefix index plus the main term, or may scan the main index directly.

Expression iteration is recursive. `fts3EvalNextRow()` advances phrase, AND, NEAR, OR, and NOT nodes in docid order. For AND/NEAR, child iterators are synchronized to the same docid; NEAR is initially treated like AND. OR chooses the smaller next docid and advances duplicates on both sides. NOT advances the right side far enough to exclude matching left-side docids. `sqlite3Fts3EvalTestDeferred()` then seeks and tokenizes the current content row for deferred tokens and runs `fts3EvalTestExpr()` plus `fts3EvalNearTest()` to reject false positives and trim NEAR position lists for snippet/offset/matchinfo correctness.

Transaction flow uses `fts3BeginMethod()` to reset per-transaction counters and detect `%_stat`, `fts3SyncMethod()` to flush pending terms to segments and possibly run auto incremental merge, `fts3CommitMethod()` as a post-sync assertion/no-op, and `fts3RollbackMethod()`/`fts3RollbackToMethod()` to discard pending in-memory terms. `fts3SavepointMethod()` forces a flush by issuing a special insert into the virtual table unless the table is suppressing recursive savepoint behavior during rename.

## State And Persistence Behavior
Persistent FTS state lives in shadow tables named from the virtual table: `%_content` unless `content=` makes the table external-content, `%_segments`, `%_segdir`, optional FTS4 `%_docsize`, and optional `%_stat`. Segment data is an append/merge-oriented collection of immutable b-tree-like structures, and `%_segdir` stores roots and block ranges. Deletes and updates are represented by newer doclist entries that supersede older entries during query-time and merge-time doclist merging.

In-memory table state in `Fts3Table` includes tokenizer ownership, table/database names, column metadata, notindexed flags, content/languageid settings, prepared statement caches, page and node-size estimates, pending-term hash tables for each index, merge counters, an optional reusable seek statement, and a shared `%_segments` blob handle managed by sibling write/segment code. `fts3DisconnectMethod()` finalizes cached statements, closes tokenizer state, and frees allocated strings; `fts3DestroyMethod()` first drops shadow tables.

Cursor state in `Fts3Cursor` includes search strategy, EOF/seek flags, current statement, parsed query expression, language id, deferred token list, doclist buffers, docid bounds, direction, matchinfo state, average-row-size estimates, and current docid. The content row is not always loaded when a match is found; `isRequireSeek` delays `%_content` lookup until a column or auxiliary function needs it.

Doclists are delta-varint encoded and include position lists per document unless a bare docid list is explicitly used. Position lists use `POS_COLUMN` and `POS_END` sentinels and encode positions as delta-plus-two values. Much of the file assumes zero padding (`FTS3_BUFFER_PADDING`) after doclist buffers to simplify varint/terminator scans safely.

## Dependencies
This file depends on `fts3Int.h`, `fts3.h`, SQLite core/extension APIs, tokenizer modules, tokenizer/hash helpers, expression parsing, snippet/matchinfo helpers, write-side FTS3 functions, segment-reader implementations, and optional ICU/unicode/test modules. Key sibling APIs include `sqlite3Fts3UpdateMethod()`, `sqlite3Fts3PendingTermsFlush()`, `sqlite3Fts3PendingTermsClear()`, `sqlite3Fts3Optimize()`, segment-reader creation/stepping/freeing, `%_stat`/`%_docsize` selectors, deferred-token cache APIs, tokenizer initialization, and integrity checking.

Compile-time switches strongly shape behavior: `SQLITE_CORE`, `SQLITE_ENABLE_FTS3`, `SQLITE_ENABLE_FTS4`, `SQLITE_DISABLE_FTS4_DEFERRED`, `SQLITE_DISABLE_FTS3_UNICODE`, `SQLITE_ENABLE_ICU`, `SQLITE_TEST`, and `SQLITE_DEBUG`. The file includes debug-only corruption assertion plumbing through `sqlite3_fts3_may_be_corrupt` and `sqlite3Fts3Corrupt()`.

## Integration Points
SQLite integrates this file through the virtual-table API and extension initialization API. The hidden table-name column passes a typed `Fts3Cursor` pointer to overloaded functions; `snippet()`, `offsets()`, `matchinfo()`, and `optimize()` validate that pointer with `sqlite3_value_pointer(..., "fts3cursor")` before operating on the current match.

The write path is delegated to `sqlite3Fts3UpdateMethod()` and segment maintenance functions in sibling files, but this file decides when pending terms are flushed, when auto incremental merge is attempted, when savepoints force flushes, and how rename/drop operations affect shadow tables. Integrity checks call `sqlite3Fts3IntegrityCheck()` and translate failures into SQLite `integrity_check` diagnostics.

`fts4aux` depends on this file's segment-reader and varint/doclist helpers. Snippet and matchinfo code depend on the evaluator's position-list state, deferred-token handling, and `sqlite3Fts3EvalPhrasePoslist()`/`sqlite3Fts3EvalPhraseStats()` interfaces.

## Risks And Edge Cases
The main correctness risk is malformed on-disk FTS data. The file performs many corruption checks for impossible prefix lengths, b-tree heights, child ordering, invalid column markers, missing content rows, and inconsistent restart positions, but several low-level doclist scans still rely on padding and format invariants. Corruption handling must consistently return `SQLITE_CORRUPT_VTAB` or related codes without overreading.

Virtual-table recursion is guarded by `Fts3Table.bLock`; missing or misplaced lock increments around internal SQL can lead to recursive use errors or planner failures. External-content tables deliberately disable deferred-token optimization because index and content rows may not be synchronized.

Prefix and descending-order indexes make doclist sizing and merge logic subtle. The code adds varint padding in several output allocations because descending deltas or negative first docids can require larger encodings after merge. Changing docid ordering, position-list trimming, or OR/NEAR restart behavior can silently break snippets, offsets, and matchinfo even if rowid result sets look correct.

`fts3InitVtab()` has many constructor option interactions: `content=` suppresses compression hooks, `compress` and `uncompress` must appear together, `notindexed=` must match a column, and `languageid=` may remove a column imported from an external content table. Memory ownership crosses tokenizer objects, option strings, copied column arrays, and one large `Fts3Table` allocation; error paths must preserve those ownership rules.

## Test Signals
Good behavioral tests should cover FTS3 and FTS4 creation, connect, rename, drop, shadow-table creation, external-content tables, prefix indexes, `languageid=`, `notindexed=`, `order=desc`, `matchinfo=fts3`, compression/uncompression option validation, and tokenizer selection. Query tests should include docid lookup, full scans with rowid ranges, MATCH on all columns and a single column, phrase queries, prefix queries with and without prefix indexes, NEAR chains, AND/OR/NOT trees, first-token `^` filters, deferred-token cases, and descending output.

Persistence tests should verify pending-term flushing on commit/savepoint, rollback clearing, auto incremental merge triggers, optimize results, integrity-check diagnostics, and corruption handling for malformed segment roots/doclists/column markers. Auxiliary-function tests should validate `snippet()`, `offsets()`, and `matchinfo()` after OR/NEAR/deferred queries, because those depend on the evaluator retaining and trimming correct per-row position lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3.h -->
# sources/storage-engines/sqlite/ext/fts3/fts3.h

## Purpose
`fts3.h` is the small public header for code that links against SQLite's FTS3 extension. It exposes the single initialization function needed to register the FTS3/FTS4 extension with a database connection.

## Important APIs, Types, And Functions
The only declared API is `int sqlite3Fts3Init(sqlite3 *db);`. Callers pass an open SQLite connection, and the implementation in `fts3.c` registers the FTS3/FTS4 modules, tokenizers, auxiliary modules, and overloaded functions on that connection.

The header includes `sqlite3.h` so the `sqlite3` connection type and SQLite result codes are visible. It wraps the declaration in `extern "C"` when included from C++ so C++ clients can link against the C implementation.

## Control Flow
There is no runtime control flow in this header. It is included by extension or core build units that need the declaration. Loadable-extension builds ultimately call `sqlite3_fts3_init()` in `fts3.c`, which initializes the SQLite extension API table and delegates to `sqlite3Fts3Init()`.

## State And Persistence Behavior
The header owns no state and writes no data. The function it declares mutates the supplied SQLite connection by registering modules and functions. Persistent FTS shadow tables are created later only when users create FTS virtual tables.

## Dependencies
The direct dependency is `sqlite3.h`. The declared function depends at link time on the FTS3 implementation and its sibling tokenizer, expression, snippet, auxiliary, and write modules.

## Integration Points
SQLite core builds may call `sqlite3Fts3Init()` directly during extension initialization. External embedders or loadable extension code can include this header to register FTS3 support on a specific connection without relying on private internal headers.

## Risks And Edge Cases
The header intentionally exposes only initialization. It does not expose tokenizer registration helpers, FTS table structures, or evaluator internals. Consumers that need deeper behavior must use SQLite SQL APIs or internal headers, not this public header.

The main integration risk is build mismatch: including this header without linking the FTS3 implementation produces unresolved symbols, and calling the initializer in a build where FTS3 is omitted will not be available.

## Test Signals
Compilation tests should verify that C and C++ translation units can include the header. Runtime smoke tests should call `sqlite3Fts3Init()` on a database connection and then successfully execute `CREATE VIRTUAL TABLE t USING fts3(...)` or `fts4(...)`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3Int.h -->
# sources/storage-engines/sqlite/ext/fts3/fts3Int.h

## Purpose
`fts3Int.h` is the private shared interface for SQLite's FTS3/FTS4 implementation. It normalizes compile-time feature flags, defines portable helper macros and scalar types for non-amalgamation builds, declares the core FTS table/cursor/expression/doclist/segment structures, and publishes cross-file prototypes used by the FTS3 tokenizer, expression parser, snippet/matchinfo code, write path, segment readers, auxiliary tables, and integrity checker.

## Important APIs, Types, And Functions
The header defines build and format constants such as `SQLITE_FTS3_MAX_EXPR_DEPTH`, `FTS3_MERGE_COUNT`, `FTS3_MAX_PENDING_DATA`, `FTS3_VARINT_MAX`, `FTS3_BUFFER_PADDING`, `FTS3_SEGDIR_MAXLEVEL`, `POS_COLUMN`, and `POS_END`. It also aliases `SQLITE_ENABLE_FTS4` to `SQLITE_ENABLE_FTS3` and disables FTS when virtual tables are omitted.

`Fts3Table` is the connection-level virtual-table object. It embeds `sqlite3_vtab`, database/table names, column metadata, notindexed flags, tokenizer pointer, external-content and languageid settings, statement caches, FTS3/FTS4 mode flags, page/node sizes, segment blob state, savepoint state, prefix-index definitions, pending-term hash tables, pending-data counters, previous-docid/langid tracking, and debug transaction fields.

`Fts3Cursor` is the per-query cursor object. It embeds `sqlite3_vtab_cursor` and tracks search strategy, EOF/seek flags, active SQLite statement, parsed expression tree, language id, deferred tokens, current doclist pointers, ordering, evaluation mode, row-size estimates, document counts, docid range constraints, and matchinfo buffer state.

The expression model is `Fts3Expr`, `Fts3Phrase`, and `Fts3PhraseToken`. Phrase tokens store parsed token text, prefix/first-position flags, and evaluation-time deferred-token or segment-reader state. Phrases cache merged doclists and OR-position state. Expression nodes form trees with types `FTSQUERY_NEAR`, `FTSQUERY_NOT`, `FTSQUERY_AND`, `FTSQUERY_OR`, and `FTSQUERY_PHRASE`.

Segment-reader contracts are represented by `Fts3SegFilter` and `Fts3MultiSegReader`. Filter flags include `FTS3_SEGMENT_REQUIRE_POS`, `FTS3_SEGMENT_IGNORE_EMPTY`, `FTS3_SEGMENT_COLUMN_FILTER`, `FTS3_SEGMENT_PREFIX`, `FTS3_SEGMENT_SCAN`, and `FTS3_SEGMENT_FIRST`. Special segment levels `FTS3_SEGCURSOR_PENDING` and `FTS3_SEGCURSOR_ALL` select pending terms or all persisted segments.

The prototype groups define the private FTS3 subsystem API: write/update and segment maintenance (`sqlite3Fts3UpdateMethod()`, pending flush/clear, optimize, reader creation/free, block reads, stat/docsize selectors, incremental merge), deferred-token helpers, segment-reader stepping, prepared-statement helper, varint/doclist/evaluator helpers from `fts3.c`, tokenizer initialization, snippet/offsets/matchinfo APIs, expression parsing/freeing, tokenize-vtab registration, unicode helpers, expression iteration, and integrity checking.

## Control Flow
This header does not execute code, but it defines the cross-module flow of the FTS subsystem. SQLite vtab callbacks in `fts3.c` allocate and populate `Fts3Table`/`Fts3Cursor`; write-side code updates pending-term hashes and segment tables; segment-reader code fills `Fts3MultiSegReader` objects; expression-parser code produces `Fts3Expr` trees; evaluator code traverses phrases and segment readers; snippet/matchinfo code consumes evaluator state through the declared APIs.

Conditional compilation shapes that flow. If FTS4 deferred tokens are disabled, deferred-token functions become no-op macros. If unicode support is disabled, unicode tokenizer helpers disappear. Test builds expose expression test interfaces and debug knobs. Non-amalgamation builds define SQLite-style scalar typedefs and macros that the amalgamation would normally provide.

## State And Persistence Behavior
`Fts3Table` is the primary in-memory owner for persistent FTS metadata and transient transaction state. It records which shadow tables exist, which prefix indexes are configured, how large pending-term buffers may grow before being flushed, and which language id the pending terms belong to. Its statement cache and segment blob handle are connection-local resources, not persisted state.

Persistent state is represented indirectly through the constants and APIs in this header: `%_segments` and `%_segdir` hold segment b-trees; `%_content` holds table content unless an external content table is configured; `%_docsize` and `%_stat` hold FTS4 size/statistics metadata. `FTS3_MERGE_COUNT`, `FTS3_SEGDIR_MAXLEVEL`, and pending-data limits constrain how in-memory terms become persistent segments and how those segments are merged.

`Fts3Cursor`, `Fts3Expr`, `Fts3Phrase`, `Fts3Doclist`, and `Fts3MultiSegReader` are transient query/evaluation state. They hold pointers into malloced buffers, segment-reader outputs, prepared statements, and deferred-token caches, so ownership cleanup must be coordinated between evaluator, cursor close, and expression free routines.

## Dependencies
The header depends on SQLite public or extension headers (`sqlite3.h`, optionally `sqlite3ext.h`), tokenizer definitions in `fts3_tokenizer.h`, FTS hash support in `fts3_hash.h`, and standard C headers. It also relies on SQLite compile-time feature macros and, outside the amalgamation, provides fallback definitions for `ALWAYS`, `NEVER`, `TESTONLY`, `FLEXARRAY`, integer typedefs, and fallthrough annotations.

## Integration Points
Every major FTS3 source file includes this header to share private structures and prototypes. It is the contract between the virtual-table front end (`fts3.c`), write path (`fts3_write.c`), tokenizers, expression parser, snippet/matchinfo module, auxiliary term table, unicode helpers, and test hooks.

For SQLite integration, the header preserves extension vs core behavior with `SQLITE_EXTENSION_INIT3` and feature guards. For FTS4 integration, it makes FTS4 an extension of the FTS3 implementation by enabling FTS3 whenever FTS4 is requested and by carrying FTS4-specific table fields such as `bFts4`, `bHasDocsize`, `bHasStat`, prefix indexes, and language id state.

## Risks And Edge Cases
Because this header exposes private structure layouts across many `.c` files, layout changes have a broad blast radius. Fields such as `Fts3Cursor.pStmt`, phrase doclist pointers, deferred-token pointers, and segment-reader buffers have implicit ownership rules that are not enforced by the type system.

Compile-time feature combinations are risky. Disabling virtual tables undefines FTS, disabling deferred tokens changes evaluator behavior through macros, and non-amalgamation builds rely on local definitions matching SQLite core semantics. Any mismatch in `SQLITE_CORE`, `SQLITE_ENABLE_FTS3`, or `SQLITE_ENABLE_FTS4` can produce missing symbols or inconsistent module registration.

Doclist and segment constants are persistence-sensitive. Changing `POS_COLUMN`, `POS_END`, varint limits, segment level layout, or merge count assumptions can break compatibility with existing FTS indexes or corrupt query interpretation. `assert_fts3_nc()` also distinguishes debug assertions that are valid only for non-corrupt databases from checks that must survive hostile on-disk data.

## Test Signals
Useful tests should compile FTS3/FTS4 in core and loadable-extension configurations, with and without unicode, ICU, deferred tokens, debug, and amalgamation builds. Runtime tests should exercise all public prototypes through SQL-visible behavior: updates and pending-term flushes, segment reads and merges, tokenizer setup, expression parsing, snippet/offsets/matchinfo, fts4aux scans, prefix indexes, language ids, and integrity checks.

Structure-contract tests are indirect: memory sanitizer and corruption tests are important because this header defines many pointer-bearing objects and varint/doclist traversal contracts. Compatibility tests should verify that persisted FTS3/FTS4 indexes remain readable across builds using this header.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3Int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_aux.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_aux.c

## Purpose
`fts3_aux.c` implements the `fts4aux` virtual table module. `fts4aux` exposes term-level statistics for an existing FTS3/FTS4 table as a read-only table with columns `term`, `col`, `documents`, `occurrences`, and hidden `languageid`. It is an inspection/debug/statistics interface over the FTS segment index rather than a table with its own persistent storage.

## Important APIs, Types, And Functions
`Fts3auxTable` embeds `sqlite3_vtab` and owns a minimal `Fts3Table` instance used to address the target FTS table's segment tables. It does not create independent shadow tables.

`Fts3auxCursor` embeds `sqlite3_vtab_cursor` followed immediately by `Fts3MultiSegReader`, plus a `Fts3SegFilter`, optional stop term, language id, EOF flag, synthetic rowid, current column index, and an expandable `aStat` array. Each `aStat` entry stores per-term document and occurrence counts for all columns (`col='*'`) and individual columns.

The module schema is `CREATE TABLE x(term, col, documents, occurrences, languageid HIDDEN)`. `sqlite3Fts3InitAux(sqlite3 *db)` registers the module name `fts4aux` with SQLite.

The vtab callbacks are `fts3auxConnectMethod()` for both xCreate and xConnect, `fts3auxDisconnectMethod()` for xDisconnect/xDestroy, `fts3auxBestIndexMethod()`, `fts3auxOpenMethod()`, `fts3auxCloseMethod()`, `fts3auxFilterMethod()`, `fts3auxNextMethod()`, `fts3auxEofMethod()`, `fts3auxColumnMethod()`, and `fts3auxRowidMethod()`.

## Control Flow
`fts3auxConnectMethod()` accepts either `CREATE VIRTUAL TABLE aux USING fts4aux(fts_table)` or the temp-table form with an explicit target database and FTS table. It declares the fixed schema, allocates one block containing `Fts3auxTable`, a minimal `Fts3Table`, and copied database/table names, dequotes the target table name, sets `db`, `zDb`, `zName`, and `nIndex=1`, and returns the vtab object.

`fts3auxBestIndexMethod()` advertises that output is naturally ordered by `term ASC`, recognizes equality and range constraints on `term`, recognizes equality on hidden `languageid`, assigns argument indexes, and reduces estimated cost for constrained scans. Equality on `term` is cheapest; range scans are intermediate; unconstrained scans are expensive.

`fts3auxFilterMethod()` resets any reused cursor, interprets `idxNum` to pull `term=?`, `term>=?`, `term<=?`, and optional `languageid=?` values, builds a segment filter with required positions and empty-doclist filtering, enables scan mode for ranges, stores a lower-bound term and optional upper stop term, clamps negative language ids to zero, opens a segment-reader cursor over all segments for the target language, starts it, and advances once through `fts3auxNextMethod()`.

`fts3auxNextMethod()` first emits any remaining per-column rows for the current term whose document count is non-zero. Once columns are exhausted, it steps the multi-segment reader to the next term. For each doclist, it decodes the FTS3 doclist state machine: docid, optional column markers, and positions. It accumulates `aStat[0]` for all columns and `aStat[iCol+1]` for individual columns, then starts returning rows from `col='*'` onward. If a configured stop term is passed, it marks EOF.

`fts3auxColumnMethod()` returns the current term, column (`'*'` for aggregate or zero-based integer column index), document count, occurrence count, or current language id. `fts3auxCloseMethod()` closes segment resources and frees cursor buffers.

## State And Persistence Behavior
`fts4aux` has no persistent representation of its own. xCreate and xConnect are identical, and xDestroy and xDisconnect just release in-memory resources. The module reads the target FTS table's `%_segments`/`%_segdir` data through the common FTS3 segment-reader API.

Cursor state is transient. `aStat` grows as needed for terms whose doclists reference higher column numbers, and is zeroed for each new term. `iRowid` is a synthetic monotonically increasing rowid unrelated to the target FTS table rowids. `zStop` bounds range scans in memory after the segment reader begins at the lower bound.

The minimal embedded `Fts3Table` only contains the fields needed by segment-reader helpers and statement caches. `fts3auxDisconnectMethod()` finalizes any cached statements in that embedded object and frees `zSegmentsTbl`.

## Dependencies
The file depends on `fts3Int.h`, SQLite virtual-table APIs, string/assert helpers, and shared FTS3 functions: `sqlite3Fts3Dequote()`, `sqlite3Fts3ErrMsg()`, `sqlite3Fts3SegmentsClose()`, `sqlite3Fts3SegReaderFinish()`, `sqlite3Fts3SegReaderCursor()`, `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, and `sqlite3Fts3GetVarint()`.

It relies on FTS3 doclist encoding constants and `Fts3Table.nColumn` as discovered by segment-reader preparation. It is compiled only when FTS3 is available outside omitted/core-disabled configurations.

## Integration Points
`sqlite3Fts3Init()` calls `sqlite3Fts3InitAux()` during FTS3 initialization, so connections with FTS3 get the `fts4aux` module too. Users create an auxiliary virtual table pointing at an existing FTS table and query it with ordinary SQL. The module's hidden `languageid` column integrates with FTS4 language-id indexing.

The implementation shares the exact segment-reader path used by FTS queries. That makes `fts4aux` useful as a test and diagnostic view of the term index: it scans real index doclists and decodes position lists without going through expression parsing or content-table lookup.

## Risks And Edge Cases
The doclist decoder must reject malformed column markers. If a decoded column number is less than 1 or greater than `nColumn+1`, `fts3auxNextMethod()` returns `SQLITE_CORRUPT_VTAB`. The state machine also assumes valid FTS3 position-list encoding, so corruption tests should exercise truncated varints, bad column transitions, and malformed terminators.

Constructor argument handling is intentionally narrow. The two-table-name form is accepted only for temp-created aux tables that name a target database explicitly; other argument counts or database forms return an error message. A missing or stale target FTS table will surface later through segment-reader preparation rather than through a persistent aux schema check.

Range boundaries are byte-string comparisons over terms. The stop check marks EOF once the current term is greater than the upper bound or has the upper bound as a strict prefix-extension beyond it. Negative language ids are clamped to zero because SQLite's outer constraint check will reject returned rows for the original negative value.

## Test Signals
Tests should create FTS3/FTS4 tables, populate multiple columns and language ids, then verify `fts4aux` aggregate and per-column `documents`/`occurrences` counts. Query planner tests should cover unconstrained scans, `ORDER BY term ASC`, `term=?`, lower/upper range constraints, combined range constraints, and `languageid=?`.

Robustness tests should exercise empty indexes, deleted/updated rows, prefix-index tables, terms appearing in only some columns, malformed segment data, cursor reuse across filters, and cleanup paths that finalize cached statements and close segment readers.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_aux.c -->
