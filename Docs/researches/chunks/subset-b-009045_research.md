# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 251112-259629

## Scope

This chunk covers the tail of the FTS5 index implementation, the main FTS5 virtual-table module, most of the FTS5 storage layer, and the start of the built-in tokenizer implementations in the SQLite amalgamation vendored under WiredTiger tests. It begins after earlier FTS5 index setup/destruction code and ends partway through `fts5UnicodeTokenize()`, so several types and helpers are defined in neighboring chunks.

## Purpose

The code implements the runtime machinery for SQLite FTS5 tables:

- Writing tokens and prefix tokens into the FTS index.
- Opening and advancing term/rowid iterators, including `tokendata=1` token mapping for `xInstToken()`.
- Maintaining contentless-delete tombstone hash tables in segment metadata.
- Running index and storage integrity checks.
- Registering FTS5 debug helpers, the `fts5` virtual table module, extension APIs, tokenizers, and scalar functions.
- Managing FTS5 virtual table queries, updates, transactions, savepoints, ranking, locale-aware text extraction, shadow storage tables, docsize/totals records, and rebuild/optimize/merge commands.
- Starting the ASCII and Unicode tokenizer implementations used by FTS5 indexing and querying.

## Important Types And State

- `Fts5Index` is the index backend handle. This chunk uses its persistent error field `p->rc`, `pHash`, `iWriteRowid`, `bDelete`, `pConfig`, `pStruct`, `nRead`, `nContentlessDelete`, and structure/version state.
- `Fts5Iter`, `Fts5IndexIter`, `Fts5SegIter`, `Fts5TokenDataIter`, and `Fts5TokenDataMap` model index scans. A normal iterator owns segment iterators; a `tokendata=1` wrapper iterator has `nSeg==0` and merges multiple child iterators through `pTokenDataIter`.
- `Fts5Structure`, `Fts5StructureLevel`, and `Fts5StructureSegment` describe on-disk FTS segment layout, including leaf page ranges, origin ranges, tombstone page counts, and tombstone entry counts.
- `Fts5Global` is per-database module state. It owns the public `fts5_api`, registered auxiliary functions, tokenizer modules, default tokenizer, open cursor list, cursor-id allocator, and the per-connection randomized locale blob header.
- `Fts5FullTable` extends the public `Fts5Table` with `Fts5Storage`, global context, sort cursor state, savepoint tracking, and debug transaction state.
- `Fts5Cursor` is the virtual table cursor. It tracks query plan, rowid bounds, content lookup statement, expression tree, optional rank sorter, cache flags, rank function/arguments, auxiliary data, and cached phrase-instance arrays.
- `Fts5Storage` owns shadow-table prepared statements, cached totals (`nTotalRow`, `aTotalSize`), saved-row statement state for updates using `sqlite3_value_nochange()`, and references to `Fts5Config` and `Fts5Index`.
- `AsciiTokenizer`, `Unicode61Tokenizer`, and `Fts5TokenizerModule` hold tokenizer configuration and bridge v1/v2 tokenizer APIs.

Persistent state is stored in FTS5 shadow tables:

- `%_data` stores segment pages, averages, structure, and tombstone pages.
- `%_idx` stores segment b-tree split keys and doclist-index markers.
- `%_config` stores configuration key/value records, including version.
- `%_docsize` stores per-row token counts and, for `contentless_delete=1`, origin values.
- `%_content` stores content for normal or unindexed-content modes.

## Index Write And Query Flow

`sqlite3Fts5IndexCharlenToBytelen()` and `fts5IndexCharlen()` count UTF-8 character boundaries for prefix indexing. `sqlite3Fts5IndexWrite()` writes the main token record through `sqlite3Fts5HashWrite()` and then writes configured prefix-index entries after translating prefix character counts to byte lengths. Delete calls are represented by negative `iCol` and must match `p->bDelete`.

`sqlite3Fts5IndexQuery()` is the primary index query entry point. It builds an encoded term with a leading index selector byte, chooses between main index, exact prefix index, prefix scan, or `tokendata=1` special handling, opens a multi-iterator, and closes index readers on error. Prefix queries may be satisfied by a configured prefix index or by scanning main-index terms, with debug-only `FTS5INDEX_QUERY_TEST_NOIDX` exercising the scan path.

For `tokendata=1`, `fts5SetupTokendataIter()` scans all terms sharing a token-data prefix and appends one iterator per matching term. `fts5IterSetOutputsTokendata()` merges child iterators by lowest rowid, optionally merges multiple position lists, and builds maps from rowid/position back to the child term iterator. `sqlite3Fts5IterToken()` then uses that map to answer `xInstToken()` lookups, either from the exact child term or from prefix-token storage built by `fts5SetupPrefixIterTokendata()` / `sqlite3Fts5IndexIterWriteTokendata()`.

Iterator APIs in this chunk include `sqlite3Fts5IterNext()`, `sqlite3Fts5IterNextScan()`, `sqlite3Fts5IterNextFrom()`, `sqlite3Fts5IterTerm()`, `sqlite3Fts5IndexIterClearTokendata()`, and `sqlite3Fts5IterClose()`. They delegate to normal multi-iterator movement or tokendata merge movement based on whether `nSeg==0`.

## Tombstones And Contentless Deletes

`sqlite3Fts5IndexContentlessDelete()` loads the structure and finds all segments whose origin range contains the deleted row origin. The first matching segment increments `nEntryTombstone`; all matching segments receive the rowid in their tombstone hash via `fts5IndexTombstoneAdd()`.

Tombstones are persisted as hash-table pages in `%_data` using `FTS5_TOMBSTONE_ROWID(segid,page)`. `fts5IndexTombstoneAddToPage()` handles 4-byte or 8-byte keys, a special rowid-zero flag, open-addressed insertion, and half-full refusal unless forced. `fts5IndexTombstoneRebuild()` and `fts5IndexTombstoneRehash()` grow or rebuild the table when a page is full or the key width must expand from 4 to 8 bytes. Successful rebuild writes all pages and updates `pSeg->nPgTombstone` plus the structure record.

Risks here are data-structure correctness and corruption detection: bad page sizing, key-width mismatches, origin-range errors, or missed structure writes could leave deletes invisible to queries. The code mitigates with rebuild retries, explicit `FTS5_CORRUPT` paths elsewhere, and decode/debug tooling.

## Integrity And Debug Tooling

The integrity-check section computes checksums with `sqlite3Fts5IndexEntryCksum()`. Debug-only helpers compare forward and reverse doclist-index traversal (`fts5TestDlidxReverse()`), query terms in ascending and descending order (`fts5QueryCksum()`), validate UTF-8 prefixes (`fts5TestUtf8()`), and compare prefix-index results against main-index scans (`fts5TestTerm()`).

`fts5IndexIntegrityCheckSegment()` verifies `%_idx` entries against segment leaves, checks split-key ordering, page indexes, empty pages, doclist-index pointers, and secure-delete edge cases. `sqlite3Fts5IndexIntegrityCheck()` walks all segments, scans all terms to build a checksum, and compares it with a checksum derived from content when requested.

Under `SQLITE_TEST` or `SQLITE_FTS5_DEBUG`, this chunk registers:

- `fts5_decode(rowid, blob)` and `fts5_decode_none()` for human-readable decoding of structure, averages, segment leaves, doclist indexes, tombstone pages, and rowid lists.
- `fts5_rowid('segment', segid, pgno)` for deriving segment rowids.
- `fts5_structure(struct)` as a table-valued view over decoded `Fts5Structure` records.

These are important test signals for corruption triage because they expose the exact encoded storage records that normal queries consume.

## Virtual Table Module And Query Planning

`fts5InitVtab()` implements both `xCreate` and `xConnect`: parse configuration, load tokenizer if needed, open index and storage subsystems, declare the virtual-table schema, load configuration, and enable constraint support/innocuous mode. `fts5FreeVtab()`, `fts5DisconnectMethod()`, and `fts5DestroyMethod()` close index, storage, config, and shadow tables.

`fts5BestIndexMethod()` builds an `idxStr` program and `idxNum` flags for `xFilter()`. It recognizes table-column MATCH, rank MATCH, column-specific MATCH, LIKE/GLOB pattern support when the tokenizer advertises it, rowid equality/ranges, and `ORDER BY rank` or `ORDER BY rowid`. It rejects unusable MATCH constraints, suppresses duplicate rank/equality constraints, marks rowid equality scans unique, blocks recursively defined content tables through `pConfig->bLock`, and estimates costs based on match and rowid constraint combinations.

`fts5FilterMethod()` decodes `idxStr`, extracts locale-wrapped expressions with `fts5ExtractExprText()`, handles `fts5_insttoken()` subtype requests, builds combined FTS expressions, handles pattern expressions, sets rowid bounds according to sort order, loads index configuration, and selects one of:

- `FTS5_PLAN_MATCH` for normal MATCH.
- `FTS5_PLAN_SORTED_MATCH` plus an internal `FTS5_PLAN_SOURCE` cursor for `ORDER BY rank`.
- `FTS5_PLAN_SPECIAL` for internal `MATCH '*reads'` and `MATCH '*id'`.
- `FTS5_PLAN_ROWID` or `FTS5_PLAN_SCAN` using storage statements.

Cursor movement uses `fts5NextMethod()`, `fts5CursorFirst()`, `fts5SorterNext()`, and `fts5CursorReseek()`. Writes call `fts5TripCursors()` to mark active MATCH cursors for reseek so readers do not continue using stale index iterator state.

## Cursor Columns, Rank, And Extension API

`fts5ColumnMethod()` returns user columns, the hidden table-name column (cursor id), or the hidden rank column. For rank sorting, `fts5PoslistBlob()` serializes phrase position lists for internal source cursors. For ordinary rank evaluation, `fts5FindRankFunction()` resolves the configured auxiliary rank function and optional parsed rank arguments.

The extension API table `sFts5Api` is version 4 in this chunk and exposes user data, column count/text/size/locale, row count, column total size, tokenization with and without locale, phrase metadata, instance enumeration, phrase iterators, query-token, instance-token, auxiliary data, and phrase subquery support. `fts5ApiCallback()` looks up a cursor id and invokes the registered auxiliary function with the current cursor context.

Position-list and instance APIs are lazy. `fts5CsrPoslist()` returns index-provided position lists for `detail=full`, or repopulates them by retokenizing row content for lower-detail modes when content is available. `fts5CacheInstArray()` merges phrase position readers into sorted `(phrase,column,offset)` triples and flags corrupt column numbers. `fts5ApiInstToken()` depends on the tokendata mapping implemented earlier in the chunk.

Locale support flows through `fts5_locale()`, `sqlite3Fts5IsLocaleValue()`, `sqlite3Fts5DecodeLocaleValue()`, `sqlite3Fts5SetLocale()`, `fts5TextFromStmt()`, and `fts5ApiColumnLocale()`. The randomized per-connection header in `Fts5Global.aLocaleHdr` identifies internal locale blobs while reducing accidental collision with user blobs.

## Updates, Transactions, And Special Commands

`fts5UpdateMethod()` handles virtual-table insert, update, delete, and special insert directives. It loads config if needed, sets error-message routing, trips open cursors, validates `fts5_locale()` usage against `locale=1`, honors conflict mode for normal/contentless-delete tables, and distinguishes:

- `DELETE` by rowid.
- `INSERT`, including `REPLACE` conflict handling.
- `UPDATE` with unchanged rowid.
- `UPDATE` with modified rowid, carefully detecting conflicts before irreversible changes.
- Special insert directives: `delete-all`, `rebuild`, `optimize`, `merge`, `integrity-check`, debug `prefix-index`, `flush`, and config key/value updates.
- Special contentless delete command for contentless external/content tables without `contentless_delete=1`.

`fts5ContentlessUpdate()` enforces contentless update rules: updating only unindexed columns can be content-only; otherwise, `contentless_delete=1` requires all indexed columns to be modified, not a subset.

Transaction callbacks are thin but important. `xSync` flushes pending index/storage state to disk, `xCommit` is a no-op after sync, `xRollback` discards pending storage/index state and resets page-size config, `xSavepoint` flushes and tracks the active savepoint, `xRelease` may flush when releasing below the last flushed savepoint, and `xRollbackTo` trips cursors and rolls back pending storage when needed. Debug builds track expected transaction state with `fts5CheckTransactionState()`.

## Module Registration

`fts5Init()` creates `Fts5Global`, initializes the public `fts5_api` methods, randomizes the locale header, registers the `fts5` module with `sqlite3_create_module_v2()`, initializes index debug helpers, expression support, built-in auxiliaries, tokenizers, vocab support, and scalar functions:

- `fts5(pointer)` returns the API pointer.
- `fts5_source_id()` returns the FTS5 source id string.
- `fts5_locale(locale,text)` wraps text with locale metadata.
- `fts5_insttoken(expr)` returns its argument with a subtype requesting prefix instance-token support.

The module advertises `xShadowName` for `config`, `content`, `data`, `docsize`, and `idx` shadow tables, and `xIntegrity` delegates to storage integrity checking while producing user-facing corruption messages.

Loadable-extension entry points `sqlite3_fts_init()` and `sqlite3_fts5_init()` are present when not building into SQLite core; otherwise `sqlite3Fts5Init()` calls the same initializer.

## Storage Layer Flow

`fts5StorageGetStmt()` lazily prepares and caches statements for scans, lookups, content insert/replace/delete, docsize insert/delete/lookup, config replace, and full content scans. It builds SQL according to content mode, unindexed columns, locale columns, and contentless-delete origin columns. Internal shadow-table statement failures are converted to corruption for missing internal tables.

Creation and schema management:

- `sqlite3Fts5StorageOpen()` allocates storage state, creates `%_content` for normal/unindexed content modes, `%_docsize` if column sizes are enabled, `%_config`, and writes the initial version.
- `sqlite3Fts5DropAll()` drops FTS5 shadow tables.
- `sqlite3Fts5StorageRename()` flushes then renames shadow tables.
- `sqlite3Fts5CreateTable()` centralizes shadow table creation and error messages.

Insert/update/delete storage flow:

- `sqlite3Fts5StorageContentInsert()` writes content rows or allocates rowids for external/contentless tables through `%_docsize` when possible.
- `sqlite3Fts5StorageIndexInsert()` tokenizes indexed column values, writes terms to the index with `sqlite3Fts5IndexWrite()`, accumulates per-column token counts, updates totals, and writes `%_docsize`.
- `sqlite3Fts5StorageDelete()` begins a delete write, either adds contentless tombstones or tokenizes old content into delete markers, then removes `%_docsize` and `%_content` rows as appropriate.
- `sqlite3Fts5StorageFindDeleteRow()` and `sqlite3Fts5StorageReleaseDeleteRow()` manage the saved lookup statement used to preserve old values and locale metadata across rowid-changing updates and `sqlite3_value_nochange()` columns.

Totals and docsize behavior:

- `fts5StorageLoadTotals()` reads the averages record through the index.
- `fts5StorageSaveTotals()` serializes row count and per-column totals back to the averages record.
- `sqlite3Fts5StorageSync()` saves totals, syncs the index, and preserves `last_insert_rowid`.
- `sqlite3Fts5StorageDocsize()`, `sqlite3Fts5StorageSize()`, and `sqlite3Fts5StorageRowCount()` back extension APIs and corruption checks.

Maintenance operations:

- `sqlite3Fts5StorageDeleteAll()` deletes data/index/docsize/content rows and reinitializes the index.
- `sqlite3Fts5StorageRebuild()` scans content, retokenizes every indexed column, rebuilds index/docsize/totals, and respects locale metadata.
- `sqlite3Fts5StorageOptimize()`, `sqlite3Fts5StorageMerge()`, and `sqlite3Fts5StorageReset()` delegate to index maintenance/reset.
- `sqlite3Fts5StorageIntegrity()` recomputes checksums from content, verifies docsize and totals, validates shadow row counts, then delegates to `sqlite3Fts5IndexIntegrityCheck()`.

## Tokenizers In This Chunk

The ASCII tokenizer defines an ASCII alphanumeric token table plus `tokenchars` and `separators` exceptions. `fts5AsciiTokenize()` scans separator runs, folds ASCII uppercase to lowercase, grows a temporary fold buffer when needed, and calls the tokenizer callback for each token. Non-ASCII bytes are treated as token bytes by the ASCII tokenizer scan loop.

The Unicode tokenizer starts with UTF-8 read/write helpers when not using amalgamation-provided macros, `Unicode61Tokenizer` state, diacritic-removal constants, category parsing, exception insertion, deletion, creation, token-character testing, and the start of `fts5UnicodeTokenize()`. It supports `categories`, `remove_diacritics`, `tokenchars`, and `separators` options. The tokenizer uses Unicode category tables and a sorted exception list; non-ASCII tokenization and folding continue beyond this chunk.

## Dependencies And Integration Points

This chunk depends heavily on earlier and later FTS5 code in the same amalgamation:

- Index primitives: `fts5DataRead()`, `fts5DataWrite()`, `fts5StructureRead()`, `fts5StructureWrite()`, segment iterators, doclist-index iterators, buffer helpers, varint helpers, tombstone macros, rowid macros, and index sync/rollback/optimize/merge/reinit.
- Expression layer: `sqlite3Fts5ExprNew()`, `sqlite3Fts5ExprAnd()`, `sqlite3Fts5ExprFirst/Next()`, phrase and token APIs, poslist population, and pattern matching.
- Config layer: `sqlite3Fts5ConfigParse()`, `DeclareVtab`, `Load`, `SetValue`, rank parsing, tokenizer config, content mode, locale mode, unindexed columns, prefix indexes, and error routing.
- Tokenizer/Unicode helpers: `sqlite3Fts5Tokenize()`, `sqlite3Fts5TokenizerPattern()`, `sqlite3Fts5UnicodeCategory()`, `sqlite3Fts5UnicodeIsdiacritic()`, category parsing, and fold/remove-diacritic routines beyond this range.
- SQLite core APIs: virtual table callbacks, prepared statements, blobs, scalar functions, modules, value subtypes, `sqlite3_value_nochange()`, `sqlite3_vtab_config()`, `sqlite3_vtab_on_conflict()`, `sqlite3_randomness()`, and extension entry-point macros.

WiredTiger itself is not integrated directly here; the file is a vendored SQLite amalgamation used by tests. Behavioral changes in this chunk affect the embedded SQLite/FTS5 behavior available to those tests.

## Risks And Edge Cases

- `fts5BestIndexMethod()` manipulates `idxStr` while also using `iIdxStr`; this is intentional in SQLite code but brittle if modified without preserving pointer/index invariants.
- Locale blobs depend on a per-connection randomized header; stored values are interpreted only in contexts using the same `Fts5Global` header.
- Contentless-delete tombstones require origin metadata in `%_docsize`; missing or zero origins make deletes no-ops.
- Rank sorting prepares recursive SQL against the same virtual table and uses `pSortCsr` to avoid circular ownership and route source-cursor state; changes can easily reintroduce recursion or lifetime bugs.
- For `detail!=full`, instance and phrase position APIs may retokenize content. Contentless tables return empty position lists, so auxiliary functions must handle missing details.
- `sqlite3_value_nochange()` update handling relies on `pSavedRow` not being reset too early, especially with locale columns.
- Integrity checking can be expensive because it scans content and index structures and may retokenize all indexed columns.
- The storage statement cache temporarily transfers statements to cursors; release paths must return or finalize them to avoid leaks or use-after-reset behavior.
- Tokenizers resize fold buffers during tokenization; OOM must abort cleanly and convert `SQLITE_DONE` callback status back to `SQLITE_OK`.

## Test Signals

Good test coverage for this chunk includes:

- FTS5 MATCH queries with rowid bounds, ascending/descending rowid order, rank sorting, rank MATCH arguments, LIKE/GLOB pattern matching, and special `*reads`/`*id` queries.
- `tokendata=1` tables using `xInstToken()` and prefix inst-token paths, including multiple token-data terms mapping to the same rowid.
- Insert/update/delete cases for normal, external-content, contentless, `contentless_delete=1`, and `contentless_unindexed=1` tables, including REPLACE conflict handling and rowid-changing updates with no-change columns.
- Locale tests using `fts5_locale()`, `xColumnLocale()`, external content locale blobs, normal-content locale side columns, and rejection when `locale=1` is absent.
- Maintenance commands: `delete-all`, `rebuild`, `optimize`, `merge`, `flush`, config updates, and `integrity-check`.
- Corruption tests for missing shadow tables, bad `%_docsize` blobs, mismatched totals, broken `%_idx` split keys, bad doclist-index links, malformed tombstone pages, and stale structure cookies.
- Debug/test builds exercising `fts5_decode`, `fts5_decode_none`, `fts5_rowid`, `fts5_structure`, debug prefix-index comparisons, and doclist reverse checks.
- Tokenizer tests for ASCII `tokenchars`/`separators`, Unicode `categories`, `remove_diacritics`, non-ASCII exceptions, UTF-8 boundary handling, and callback early termination.

## Boundary Notes

The chunk starts after FTS5 index open/close setup code, so definitions for many index structs and helpers are outside this report. It ends inside `fts5UnicodeTokenize()`, before the Unicode tokenizer's full folding, diacritic-removal, callback, and registration logic. The final per-file synthesis should merge this report with adjacent chunks to describe complete FTS5 tokenizer behavior and whole-file SQLite integration.
