# sources/storage-engines/sqlite/ext/fts5 subset-b-008739 research

Work item `subset-b-008739` covers the FTS5 virtual table front end, storage layer, Tcl test harness, and two test-only auxiliary virtual/function modules.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_main.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_main.c

## Purpose

`fts5_main.c` is the primary SQLite virtual table module implementation for FTS5. It registers the `fts5` module, wires SQLite virtual table callbacks to the FTS5 config, expression, index, storage, tokenizer, vocab, and auxiliary-function subsystems, and exposes the public `fts5_api`/`Fts5ExtensionApi` surfaces used by extensions. It owns query planning, cursor lifecycle, MATCH execution, rank sorting, column materialization, update handling, transaction/savepoint callbacks, extension API dispatch, tokenizer registration, and SQL helper functions such as `fts5()`, `fts5_source_id()`, `fts5_locale()`, and `fts5_insttoken()`.

## Important APIs, types, and functions

Key types are `Fts5Global`, `Fts5FullTable`, `Fts5Cursor`, `Fts5Sorter`, `Fts5Auxiliary`, `Fts5TokenizerModule`, and `Fts5Auxdata`. `Fts5Global` is connection-scoped state: the public `fts5_api`, registered tokenizers, registered auxiliary functions, open cursor list, and the randomized locale blob header. `Fts5FullTable` extends the public `Fts5Table` with `Fts5Storage`, connection global state, sorted-query cursor state, and debug transaction bookkeeping. `Fts5Cursor` carries a virtual-table cursor plan, rowid bounds, expression tree, content statement, sorter, rank function state, auxiliary data, and cached match-instance arrays.

Module setup is centered on `fts5Init()`, which creates the `sqlite3_module`, initializes index/expression/aux/tokenizer/vocab subsystems, registers SQL functions, and installs the module destructor. `sqlite3_fts_init()`, `sqlite3_fts5_init()`, or `sqlite3Fts5Init()` call it depending on loadable-extension versus core builds. `fts5InitVtab()`, `fts5CreateMethod()`, and `fts5ConnectMethod()` parse table options, load tokenizers, open index/storage handles, declare the virtual schema, load config, and set virtual-table safety flags.

Query planning is handled by `fts5BestIndexMethod()`, which encodes MATCH/rank/rowid/LIKE/GLOB constraints into `idxStr`, stores ORDER BY flags in `idxNum`, estimates cost/rows, and marks rowid equality as unique. Runtime query setup is in `fts5FilterMethod()`: it decodes `idxStr`, extracts locale-wrapped MATCH text, builds or combines `Fts5Expr` objects, applies rowid bounds, chooses scan/rowid/MATCH/sorted/special plans, and opens content statements or expression iterators. Cursor movement is split across `fts5CursorFirst()`, `fts5CursorFirstSorted()`, `fts5SorterNext()`, `fts5CursorReseek()`, and `fts5NextMethod()`.

Writes enter through `fts5UpdateMethod()`, with helpers `fts5SpecialInsert()`, `fts5SpecialDelete()`, `fts5StorageInsert()`, and `fts5ContentlessUpdate()`. Transaction entry points are `fts5BeginMethod()`, `fts5SyncMethod()`, `fts5CommitMethod()`, `fts5RollbackMethod()`, `fts5SavepointMethod()`, `fts5ReleaseMethod()`, and `fts5RollbackToMethod()`. `sqlite3Fts5FlushToDisk()` trips cursors and delegates persistence to storage.

The extension API is the static `sFts5Api` object. It maps xUserData, xColumnCount, xRowCount, xColumnTotalSize, xTokenize/xTokenize_v2, xPhraseCount, xPhraseSize, xInstCount, xInst, xRowid, xColumnText, xColumnSize, xQueryPhrase, xSetAuxdata/xGetAuxdata, phrase iterators, xQueryToken, xInstToken, and xColumnLocale onto cursor and storage internals. Auxiliary SQL dispatch uses `fts5CreateAux()`, `fts5FindFunctionMethod()`, `fts5ApiCallback()`, and `fts5ApiInvoke()`. Tokenizer registration uses `fts5CreateTokenizer()`, `fts5CreateTokenizer_v2()`, `fts5FindTokenizer()`, `fts5FindTokenizer_v2()`, `fts5LoadTokenizer()`, and wrapper adapters between v1 and v2 tokenizer APIs.

## Control flow

Creation/connect allocates `Fts5FullTable`, parses config, opens the index and storage subsystems, declares the virtual table, and loads the config cookie. Query planning first scans constraints for MATCH-like clauses, rank MATCH, rowid equality/ranges, and tokenizer-supported LIKE/GLOB pattern matches. `xFilter` then converts those encoded constraints into either a full text expression, a special internal query (`MATCH '*reads'` or `MATCH '*id'`), a rowid lookup, or a content scan.

Normal MATCH execution initializes an `Fts5Expr` iterator against `Fts5Index` and advances it row by row. Content is lazy: cursor flags such as `FTS5CSR_REQUIRE_CONTENT`, `FTS5CSR_REQUIRE_DOCSIZE`, `FTS5CSR_REQUIRE_INST`, and `FTS5CSR_REQUIRE_POSLIST` indicate which derived row data must be loaded or recomputed. `xColumn` fetches the table-name hidden column as a cursor id, evaluates rank through the configured auxiliary function, or seeks into storage for user columns. For `ORDER BY rank`, `fts5CursorFirstSorted()` prepares a recursive SELECT over the same virtual table that materializes `(rowid, rank)` sorted by rank; the outer cursor then reads pre-sorted rows and position-list blobs from a `Fts5Sorter`.

Updates branch by operation shape: delete has one argument, insert has a NULL old rowid, update has integer old/new rowids, and special inserts use the hidden table-name column. Regular writes call storage to delete old index/content/docsize rows and insert new content/index/docsize rows. Contentless tables restrict UPDATE and DELETE unless `contentless_delete=1` semantics permit the operation; updates that touch only unindexed columns can be content-only operations for contentless-unindexed tables.

## State and persistence behavior

Persistent data is not written directly by this file; it is delegated to `fts5_storage.c` and `fts5_index.c`. This file controls when pending index state is flushed, reset, or invalidated. `xSync`, savepoint creation, and some release paths flush pending terms and totals through `sqlite3Fts5FlushToDisk()`. Rollback and rollback-to discard cached index/storage state and reset config page-size state. `fts5TripCursors()` marks active MATCH cursors for reseek before writes or flushes so reads do not continue on stale index iterators.

Locale state is transiently stored in `Fts5Config.t.pLocale/nLocale` around tokenization. `fts5_locale()` returns a blob with a connection-randomized header, locale text, a nul separator, and text; `sqlite3Fts5IsLocaleValue()` and `sqlite3Fts5DecodeLocaleValue()` identify and unpack these values only for the owning `Fts5Global` header. `fts5_insttoken()` marks a query value with a subtype that enables prefix token retention for xInstToken.

Auxiliary data is cursor-scoped and auxiliary-function-scoped via `Fts5Auxdata`; destructors run when the cursor is reset or closed. Tokenizer and auxiliary registrations are connection-scoped and freed by `fts5ModuleDestroy()`.

## Dependencies and integration points

This file depends on `fts5Int.h` internals and calls into config (`sqlite3Fts5Config*`), index (`sqlite3Fts5Index*`), storage (`sqlite3Fts5Storage*`), expression (`sqlite3Fts5Expr*`), tokenizer (`sqlite3Fts5Tokenize`, tokenizer init/pattern helpers), aux (`sqlite3Fts5AuxInit`), and vocab (`sqlite3Fts5VocabInit`) modules. It integrates tightly with SQLite virtual table APIs: `sqlite3_create_module_v2`, `sqlite3_vtab_config`, `sqlite3_index_info`, `xFindFunction`, `sqlite3_overload_function`, subtypes, pointer binding, and shadow-table naming/integrity callbacks.

## Risks and edge cases

High-risk areas are recursive virtual-table use for rank sorting, cursor reseek after writes, locale blob identification tied to connection-local random headers, and `idxStr` encoding/decoding consistency between `xBestIndex` and `xFilter`. Contentless/contentless-delete rules are subtle and must preserve index correctness without stored content. `sqlite3_value_nochange()` handling depends on storage saved-row behavior to preserve unmodified values and locales. Detail modes other than `full` require reconstructing position lists from content, which is impossible for contentless tables and therefore returns empty lists. Corruption handling deliberately converts missing content rows, malformed position/docsize state, and impossible column positions into `FTS5_CORRUPT` paths.

## Test signals

The file has extensive assert-based transaction-state checks under `SQLITE_DEBUG`, special test/debug directives such as `prefix-index`, public integrity plumbing via `xIntegrity`, and SQL helper functions that are exercised by Tcl and FTS5 extension tests. `SQLITE_FTS5_ENABLE_TEST_MI` can register the test `matchinfo()` implementation. The companion Tcl/test files in this work item exercise the extension API, tokenizer v1/v2 bridging, locale propagation, matchinfo compatibility, tokenization output, corruption toggles, and dropping corrupt FTS5 tables.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_storage.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_storage.c

## Purpose

`fts5_storage.c` is the persistence layer that sits between the FTS5 virtual table front end and the index subsystem. It owns shadow-table SQL, content/docsize/config table creation and maintenance, totals/averages persistence, content insertion/deletion, rebuild, optimize/merge/reset wrappers, integrity checking against stored content, statement caching, and special handling for contentless and locale-aware tables.

## Important APIs, types, and functions

The central type is `Fts5Storage`, containing `Fts5Config`, `Fts5Index`, cached totals (`nTotalRow`, `aTotalSize`, `bTotalsValid`), a saved lookup statement for UPDATE no-change values (`pSavedRow`), and a small prepared-statement cache. Statement ids cover scans, lookups, content insert/replace/delete, docsize replace/delete/lookup, config replacement, and unrestricted scan.

Public entry points include `sqlite3Fts5StorageOpen()`, `sqlite3Fts5StorageClose()`, `sqlite3Fts5DropAll()`, `sqlite3Fts5StorageRename()`, `sqlite3Fts5CreateTable()`, `sqlite3Fts5StorageDelete()`, `sqlite3Fts5StorageDeleteAll()`, `sqlite3Fts5StorageRebuild()`, `sqlite3Fts5StorageOptimize()`, `sqlite3Fts5StorageMerge()`, `sqlite3Fts5StorageReset()`, `sqlite3Fts5StorageContentInsert()`, `sqlite3Fts5StorageIndexInsert()`, `sqlite3Fts5StorageIntegrity()`, `sqlite3Fts5StorageStmt()`, `sqlite3Fts5StorageStmtRelease()`, `sqlite3Fts5StorageDocsize()`, `sqlite3Fts5StorageSize()`, `sqlite3Fts5StorageRowCount()`, `sqlite3Fts5StorageSync()`, `sqlite3Fts5StorageRollback()`, and `sqlite3Fts5StorageConfigValue()`.

Important internal helpers are `fts5StorageGetStmt()` for lazy SQL preparation, `fts5StorageInsertCallback()` for writing token positions to the index during tokenization, `sqlite3Fts5StorageFindDeleteRow()` and `sqlite3Fts5StorageReleaseDeleteRow()` for saved-row update handling, `fts5StorageDeleteFromIndex()`, `fts5StorageContentlessDelete()`, `fts5StorageInsertDocsize()`, `fts5StorageLoadTotals()`, `fts5StorageSaveTotals()`, `fts5StorageNewRowid()`, and the integrity-check callback/termset code.

## Control flow

Open optionally creates shadow tables. Normal/contentless-unindexed tables get a `%_content` table with rowid, stored content columns, optional unindexed-only content columns, and optional locale columns for indexed columns. Tables with `columnsize=1` get `%_docsize`; contentless-delete tables add an `origin` column. All tables get `%_config`, initialized with the FTS5 version.

Inserts are split into content and index phases. `sqlite3Fts5StorageContentInsert()` writes or replaces `%_content` for normal/unindexed-content tables, decodes `fts5_locale()` blobs into text plus locale side columns, and reads unchanged UPDATE values from `pSavedRow`. For external or pure contentless tables it only chooses or allocates a rowid. `sqlite3Fts5StorageIndexInsert()` loads totals, begins an index write, tokenizes each indexed column with the current locale, writes each token through `sqlite3Fts5IndexWrite()`, accumulates per-column sizes into a varint `%_docsize` blob, updates totals, and stores docsize.

Deletes load totals, begin a delete index write, remove terms using either supplied values or a content lookup, decrement totals, write contentless-delete tombstones when applicable, then delete docsize and content rows. Rebuild clears index/docsize/unindexed content state, scans the content source, retokenizes every indexed column, rewrites docsize, and saves totals. Sync saves cached totals and calls index sync while preserving `last_insert_rowid`.

## State and persistence behavior

Persistent state is stored in FTS5 shadow tables `%_data`, `%_idx`, `%_config`, `%_docsize`, and sometimes `%_content`. `%_data`/`%_idx` are primarily maintained by the index subsystem, but this layer drops, clears, reinitializes, and syncs them. `%_config` stores version and runtime config values; changing a config value also increments the index cookie. `%_docsize` stores a varint array of per-column token counts, plus `origin` for contentless-delete. Totals are cached in memory during write transactions and serialized into the index averages record on sync.

`pSavedRow` is important for UPDATE semantics. When a row is being updated, FTS5 may need original content values for columns whose SQLite argument is `sqlite3_value_nochange()`, especially to preserve locale metadata. The storage layer keeps the lookup statement stepped on the old row until the subsequent content/index insert finishes, then resets it.

## Dependencies and integration points

This file depends on `fts5Int.h`, SQLite prepared statements and SQL execution, `sqlite3Fts5Tokenize()`, locale helpers from `fts5_main.c`, and many `sqlite3Fts5Index*` calls. It is called directly by `fts5_main.c` virtual table methods and indirectly by extension APIs such as xColumnSize, xColumnTotalSize, and xRowCount. It relies on `Fts5Config` generated SQL fragments such as `zContentExprlist`, `zContent`, `zContentRowid`, column counts, locale flags, content mode, and unindexed-column maps.

## Risks and edge cases

Prepared statement construction is mode-dependent and must match shadow-table schemas exactly. A missing internal shadow table is translated to `SQLITE_CORRUPT` for internal statements, while missing external content has different behavior. Totals can become corrupt if deletes see absent rows or docsize blobs decode incorrectly. Contentless-delete behavior depends on a valid origin from `%_docsize`. `columnsize=0` prevents automatic rowid allocation for external/contentless inserts. Locale storage is split between encoded values for external content and side columns for normal content, so UPDATE no-change paths must keep text and locale synchronized.

## Test signals

Primary test signals are `integrity-check` special inserts and SQLite `xIntegrity`, both of which call `sqlite3Fts5StorageIntegrity()`. The integrity path retokenizes content, verifies docsize counts, recomputes expected index checksums including prefixes and detail modes, checks content/docsize row counts, validates totals, and delegates final checksum comparison to the index layer. Rebuild, optimize, merge, delete-all, contentless-delete, locale, nochange UPDATE, and columnsize variations are all visible through this module.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_tcl.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_tcl.c

## Purpose

`fts5_tcl.c` is test-only Tcl glue compiled under `SQLITE_TEST` and `SQLITE_ENABLE_FTS5`. It exposes FTS5 internals and extension APIs to SQLite's Tcl test suite. It lets tests obtain an `fts5_api` pointer from a Tcl database command, register Tcl-implemented auxiliary functions and tokenizers, invoke tokenizer APIs, inspect tokenizer locale state, toggle debug corruption assumptions, register additional test modules, and perform special test utilities such as dropping corrupt FTS5 tables.

## Important APIs, types, and functions

`f5tDbPointer()` extracts a `sqlite3*` from the Tcl SQLite command object using the leading layout of `SqliteDb`. `f5tDbAndApi()` prepares `SELECT fts5(?1)`, binds an `fts5_api_ptr`, and retrieves the FTS5 API. `F5tFunction`, `F5tApi`, and `F5tAuxData` support Tcl auxiliary functions and API subcommands.

`xF5tApi()` implements test wrappers for extension APIs: xColumnCount, xRowCount, xColumnTotalSize, xTokenize, xPhraseCount, xPhraseSize, xInstCount, xInst, xRowid, xColumnText, xColumnSize, xQueryPhrase, xSetAuxdata/xGetAuxdata including integer variants, phrase and phrase-column iteration, xQueryToken, xInstToken, and xColumnLocale. `xF5tFunction()` adapts an FTS5 auxiliary callback into a Tcl script invocation and returns Tcl results as SQLite values. `f5tCreateFunction()` registers such scripts through `fts5_api.xCreateFunction`.

Tokenizer test support includes `f5tTokenize()` for direct tokenization through a named tokenizer, `f5tCreateTokenizer()` for Tcl-defined tokenizers, `f5tTokenizerCreate()`, `f5tTokenizerTokenize_v2()`, `f5tTokenizerTokenize()`, `f5tTokenizerReturn()` (`sqlite3_fts5_token`), and `f5tTokenizerLocale()` (`sqlite3_fts5_locale`). Tokenizers may be v1 or v2, wrap a parent tokenizer, and expose locale values passed by core FTS5.

Additional commands include `sqlite3_fts5_may_be_corrupt`, `sqlite3_fts5_token_hash`, `sqlite3_fts5_register_matchinfo`, `sqlite3_fts5_register_fts5tokenize`, `sqlite3_fts5_register_origintext`, `sqlite3_fts5_drop_corrupt_table`, and `sqlite3_fts5_register_str`.

## Control flow

`Fts5tcl_Init()` creates Tcl commands and shares a `F5tTokenizerContext` with tokenizer-related commands. Auxiliary function registration stores the Tcl script and registers `xF5tFunction()` with FTS5. When SQLite invokes the auxiliary function, a temporary Tcl command representing the live `Fts5ExtensionApi` context is created, the user script is evaluated with that command and trailing SQL arguments, and the temporary command is deleted.

Tokenizer registration evaluates an instance-creation Tcl script during `xCreate`; that script returns the per-instance tokenization script. During tokenization, `f5tTokenizerReallyTokenize()` installs callback state in `F5tTokenizerContext`, appends the FTS5 tokenization mode and input text to the instance script, evaluates it, and expects the script to call `sqlite3_fts5_token` to emit tokens. If a parent tokenizer is configured, its tokens are fed back through `f5tTokenizeCallback()` so the Tcl script can transform parent tokens rather than raw input.

## State and persistence behavior

This file has no persistent database state of its own except for registered SQL functions, tokenizers, and virtual table modules attached to the database connection. Tcl object reference counts guard registered scripts and auxdata objects. Tokenizer context state is transient and only valid during a tokenizer callback; commands reject use outside that active callback. The debug `sqlite3_fts5_may_be_corrupt` command reads or mutates the global debug flag only in debug builds.

`sqlite3_fts5_drop_corrupt_table()` temporarily disables defensive mode, rewrites enough shadow-table state to make a corrupt FTS5 table droppable, drops it, and restores defensive mode. The `str()` test function returns a non-nul-terminated text buffer to exercise SQLite/FTS5 text-size handling.

## Dependencies and integration points

The file depends on Tcl, `tclsqlite.h`, `fts5.h`, SQLite C APIs, the FTS5 public extension API, and the test registration functions from `fts5_test_mi.c` and `fts5_test_tok.c`. It mirrors portions of the SQLite test harness internals by assuming the leading field of `SqliteDb` is `sqlite3 *db`. It is not built for release configurations.

## Risks and edge cases

The code intentionally bridges lifetimes across SQLite callbacks and Tcl command evaluation, making reference counts and destructor paths important. Temporary API Tcl commands hold stack `F5tApi` objects and must not outlive the callback. The tokenizer context is shared and restored around nested tokenization, so parent tokenizer recursion must preserve previous callback state. Error-code conversion from Tcl results to SQLite codes is deliberately narrow. The corrupt-drop utility mutates shadow tables and defensive mode and must remain test-only.

## Test signals

This file is itself a test surface. It enables direct assertions about extension API return values, auxdata destructor behavior, tokenizer callback flags, v1/v2 tokenizer compatibility, locale propagation to tokenizers and xColumnLocale, `xQueryToken`/`xInstToken`, content corruption handling, and auxiliary registration. The commands registered in `Fts5tcl_Init()` are the main Tcl-level probes for FTS5 behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_tcl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_test_mi.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_test_mi.c

## Purpose

`fts5_test_mi.c` is a test-only FTS5 auxiliary function that emulates the older FTS3/FTS4 `matchinfo()` function on top of the FTS5 extension API. It is used to validate FTS5 auxiliary APIs and to provide compatibility-style test data, not as release production code.

## Important APIs, types, and functions

`Fts5MatchinfoCtx` stores table column count, phrase count, the requested flag string, output integer count, and the output `u32` array. `fts5_api_from_db()` retrieves `fts5_api` through `SELECT fts5(?1)`. `fts5MatchinfoFlagsize()` maps each supported flag (`p`, `c`, `x`, `y`, `b`, `n`, `a`, `l`, `s`) to the number of 32-bit integers emitted. `fts5MatchinfoIter()` walks the flag string and invokes either global or local filler callbacks.

`fts5MatchinfoGlobalCb()` fills query/table-wide values such as phrase count, column count, per-phrase global hit/doc counts through `xQueryPhrase`, row count, and average column lengths. `fts5MatchinfoLocalCb()` fills current-row values such as phrase-column bitmaps, local hit counts, column lengths, and longest phrase-sequence lengths. `fts5MatchinfoFunc()` is the registered auxiliary callback. `sqlite3Fts5TestRegisterMatchinfoAPI()` and `sqlite3Fts5TestRegisterMatchinfo()` register the function via `fts5_api.xCreateFunction`.

## Control flow

On first invocation for a cursor, `fts5MatchinfoFunc()` reads the optional flag string (default `pcx`), retrieves cached auxdata, and if needed allocates a new `Fts5MatchinfoCtx` with enough space for all output integers and a copy of the flag string. Context creation computes global fields once using the extension API. Each row invocation then recomputes local fields, returns the `u32` array as a blob, and caches the context as FTS5 auxdata so subsequent rows for the same cursor and flag string reuse global work.

## State and persistence behavior

There is no persistent database state. State is per-cursor auxiliary data owned by FTS5 and destroyed with `sqlite3_free`. The global part of the matchinfo output is cached in the same allocation as local output storage; local fields are overwritten for each row.

## Dependencies and integration points

The file depends only on `fts5.h`, SQLite APIs, and the FTS5 extension API version 2 or newer. It exercises `xColumnCount`, `xPhraseCount`, `xQueryPhrase`, `xPhraseFirst`, `xPhraseNext`, `xRowCount`, `xColumnTotalSize`, `xPhraseFirstColumn`, `xPhraseNextColumn`, `xColumnSize`, `xInstCount`, `xInst`, and `xPhraseSize`.

## Risks and edge cases

The implementation documents behavioral differences from FTS4: FTS5 uses matchable phrases from the matching expression subtree, and global `x` counts ignore NEAR constraints while current-row counts observe them. Output sizes can grow with `nCol * nPhrase`, so allocation size and flag validation are important. The `s` flag's longest-sequence logic assumes ordered instance data from `xInst`. If the table has no rows, average-length output is zeroed to avoid divide-by-zero.

## Test signals

This module is a direct test signal for extension API correctness. Failures in phrase iteration, column-size accounting, row counts, auxdata caching, or instance ordering show up as mismatched `matchinfo()` blobs in Tcl tests. It can be registered through the Tcl command in `fts5_tcl.c` or compiled in via `SQLITE_FTS5_ENABLE_TEST_MI`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_test_mi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_test_tok.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_test_tok.c

## Purpose

`fts5_test_tok.c` is a test-only virtual table module named `fts5tokenize`. It exposes the output of any registered FTS5 tokenizer as rows so tests can assert token text, byte offsets, and token positions. The virtual table schema is `input HIDDEN, token, start, end, position`, and queries are expected to constrain `input = <string>`.

## Important APIs, types, and functions

`Fts5tokTable` stores the selected tokenizer API and tokenizer instance. `Fts5tokCursor` stores the input string and an in-memory array of `Fts5tokRow` results. `fts5tokDequote()` and `fts5tokDequoteArray()` copy and dequote module arguments from `CREATE VIRTUAL TABLE`. `fts5tokConnectMethod()` declares the schema, locates the tokenizer through `fts5_api.xFindTokenizer`, and creates the tokenizer instance. `fts5tokBestIndexMethod()` accepts only usable equality constraints on the hidden `input` column.

Runtime callbacks are `fts5tokOpenMethod()`, `fts5tokResetCursor()`, `fts5tokCloseMethod()`, `fts5tokFilterMethod()`, `fts5tokCb()`, `fts5tokNextMethod()`, `fts5tokEofMethod()`, `fts5tokColumnMethod()`, and `fts5tokRowidMethod()`. `sqlite3Fts5TestRegisterTok()` registers the module with `sqlite3_create_module`.

## Control flow

Creation/connect dequotes tokenizer arguments, resolves the tokenizer module, and creates a tokenizer instance. `xBestIndex` marks `input = ?` as required and cheap; without it the module leaves a high-cost unusable plan. `xFilter` clears previous cursor rows, copies the input text, invokes the tokenizer once, and collects every emitted token in `fts5tokCb()`. The callback grows the row array geometrically, copies token text, records start/end byte offsets, and advances the position counter only for non-colocated tokens. Cursor iteration then simply walks the precomputed row array.

## State and persistence behavior

The module has no persistent database representation. The tokenizer instance is table-scoped and freed by disconnect/destroy. Token rows are cursor-scoped heap allocations freed on reset/close. Rowids are 1-based positions in the output array rather than source token positions; the `position` column stores tokenizer position semantics including colocated-token handling.

## Dependencies and integration points

This file is built only when both `SQLITE_TEST` and `SQLITE_ENABLE_FTS5` are defined. It depends on `fts5.h`, SQLite virtual table APIs, and an `fts5_api` pointer supplied as module client data by `sqlite3Fts5TestRegisterTok()`. It is registered from the Tcl harness in `fts5_tcl.c`.

## Risks and edge cases

The module materializes all tokens before returning the first row, so very large input strings can allocate large row arrays. It copies token text into nul-terminated strings even though token bytes are length-delimited by the tokenizer, which is acceptable for tests but can obscure embedded nul behavior. `xFilter` returns `SQLITE_ERROR` if the hidden input equality constraint is not provided. Argument dequoting is simple and designed for SQLite module arguments, not general SQL parsing.

## Test signals

This module is a focused tokenizer probe. It verifies tokenizer selection, argument parsing, byte offsets, end offsets, colocated-token position behavior, and compatibility of FTS5 tokenizers with virtual table scan planning. It complements the Tcl tokenizer wrappers by exposing tokenizer output through SQL rows.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_test_tok.c -->
