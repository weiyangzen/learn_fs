# subset-b-008735 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_write.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_write.c

## Purpose
`fts3_write.c` is the write-side and segment-maintenance implementation for SQLite FTS3/FTS4 virtual tables. It handles `xUpdate()` inserts, deletes, updates, special maintenance commands, pending-term accumulation, full and incremental segment merges, segment b-tree construction, docsize/stat maintenance, integrity checking, and some segment-reader helpers also used by query code in `fts3.c`.

The file is compiled when FTS3 is enabled. It is tightly coupled to the FTS shadow-table schema: `%_content`, `%_segments`, `%_segdir`, `%_docsize`, and `%_stat`.

## Important APIs, Types, And Functions
Core transient types are `PendingList`, `Fts3DeferredToken`, `Fts3SegReader`, `SegmentWriter`, and `SegmentNode`. Incremental merge adds `Blob`, `NodeReader`, `NodeWriter`, and `IncrmergeWriter`.

Statement plumbing is centralized in `sqlite3Fts3PrepareStmt()`, `fts3SqlStmt()`, and `fts3SqlExec()`. `fts3SqlStmt()` maps `SQL_*` constants to cached prepared statements for all shadow-table operations and binds optional parameters.

Update entry points include `sqlite3Fts3UpdateMethod()`, `fts3InsertData()`, `fts3InsertTerms()`, `fts3DeleteTerms()`, `fts3DeleteByRowid()`, `fts3DeleteAll()`, `fts3InsertDocsize()`, and `fts3UpdateDocTotals()`. `fts3SpecialInsert()` dispatches hidden-column commands: `optimize`, `rebuild`, `integrity-check`, `merge=A,B`, `automerge=X`, and `flush`, plus debug/test commands.

Pending-term and doclist construction flows through `fts3PendingTermsDocid()`, `fts3PendingTermsAdd()`, `fts3PendingTermsAddOne()`, `fts3PendingListAppend()`, and `sqlite3Fts3PendingTermsFlush()`. These functions tokenize content, populate per-index hash tables, and flush pending lists into segment b-trees.

Segment readers and writers include `sqlite3Fts3ReadBlock()`, `sqlite3Fts3SegmentsClose()`, `sqlite3Fts3SegReaderNew()`, `sqlite3Fts3SegReaderPending()`, `fts3SegReaderNext()`, `fts3SegReaderFirstDocid()`, `fts3SegReaderNextDocid()`, `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, and `sqlite3Fts3SegReaderFinish()`. Writer functions include `fts3SegWriterAdd()`, `fts3SegWriterFlush()`, `fts3NodeAddTerm()`, `fts3NodeWrite()`, `fts3WriteSegment()`, and `fts3WriteSegdir()`.

Merge and maintenance APIs include `fts3SegmentMerge()`, `fts3AllocateSegdirIdx()`, `fts3PromoteSegments()`, `sqlite3Fts3Incrmerge()`, `fts3IncrmergeWriter()`, `fts3IncrmergeAppend()`, `fts3IncrmergeChomp()`, `fts3IncrmergeHintLoad()`, `fts3IncrmergeHintStore()`, `fts3DoOptimize()`, `fts3DoRebuild()`, `sqlite3Fts3Optimize()`, and `sqlite3Fts3IntegrityCheck()`.

## Control Flow
Normal insert/update/delete work enters through `sqlite3Fts3UpdateMethod()`. Special hidden-column inserts are intercepted first. Otherwise the method allocates document-size delta arrays, obtains a write lock on `%_segdir`, handles rowid conflict behavior, deletes any old row, inserts the new content row if needed, tokenizes indexed columns into pending-term hashes, writes `%_docsize`, updates `%_stat` totals for FTS4, closes any open segment blob handle, and returns the accumulated SQLite status.

Pending terms are ordered by docid/language/index constraints. `fts3PendingTermsDocid()` flushes if docids go backwards, delete/insert ordering would become ambiguous, language id changes, or the pending memory budget is exceeded. `sqlite3Fts3PendingTermsFlush()` calls `fts3SegmentMerge()` with `FTS3_SEGCURSOR_PENDING` for every main/prefix index, then clears the pending hashes.

Segment writing is prefix-compressed. Leaf nodes contain a height byte, term prefix/suffix varints, term suffix bytes, doclist size, and doclist bytes. `SegmentWriter` writes full leaf nodes to `%_segments`, builds an in-memory interior `SegmentNode` tree, and finally writes a `%_segdir` row with root data. Small segments can live entirely in `%_segdir.root`; larger segments use `%_segments` blocks for leaves and interior nodes.

Segment reading advances a collection of `Fts3SegReader` objects over pending hashes or persisted segment b-trees. `sqlite3Fts3SegReaderStep()` sorts readers by term, merges identical-term doclists, applies column filtering and prefix/exact/scan filters, and emits either a direct doclist pointer or a merged buffer. Incremental doclist reading uses `sqlite3_blob` handles and chunk thresholds to avoid loading large nodes unless necessary.

Full merge (`fts3SegmentMerge()`) opens readers over a level or all levels, emits merged doclists into a new `SegmentWriter`, deletes obsolete segment blocks and segdir entries, flushes the writer to the next level, and may promote smaller higher-level segments down to the new level for balance. `fts3DoOptimize()` flushes pending data and merges every language/index combination into one segment where possible.

Incremental merge (`sqlite3Fts3Incrmerge()`) repeatedly selects a level with enough segments or resumes a stored hint from `%_stat`. It opens the oldest segments, creates or appends to an appendable output segment, writes only a bounded number of leaf pages, then either deletes fully consumed input segments or truncates partially consumed ones so already copied terms are not duplicated. Hints store unfinished `(absolute-level, input-count)` pairs as varints in `%_stat`.

Integrity checking computes a checksum by scanning the FTS index and another checksum by tokenizing the content rows, including prefix indexes and language ids. A mismatch produces `FTS_CORRUPT_VTAB` through `fts3DoIntegrityCheck()` or `*pbOk = 0` through `sqlite3Fts3IntegrityCheck()`.

## State And Persistence Behavior
In-memory state includes cached prepared statements in `Fts3Table.aStmt`, pending-term hash tables in each `Fts3Index`, pending byte counters, last docid/language/delete metadata, reusable `%_segments` blob handles, query/merge buffers, and deferred-token doclists on cursors.

Persistent state is stored in FTS shadow tables. `%_content` stores user column content unless the table is external-content/contentless. `%_segments` stores segment blocks keyed by blockid, including NULL block markers used to reserve appendable incremental-merge space. `%_segdir` maps absolute levels and indexes to segment block ranges and root blobs. `%_docsize` stores per-row token counts. `%_stat` stores total document statistics, incremental-merge hints, and automerge settings.

Absolute segment levels encode language id, main/prefix index id, and relative level: `((iLangid * nIndex + iIndex) * FTS3_SEGDIR_MAXLEVEL) + iLevel`. This encoding is fundamental to merges, language filtering, and prefix-index separation.

The code carefully closes `p->pSegments` before returning to SQLite callers so blob handles do not hold database locks longer than a virtual-table method. Many functions propagate `SQLITE_NOMEM`, IO errors, or `FTS_CORRUPT_VTAB` and leave transaction rollback to SQLite.

## Dependencies
The file depends on `fts3Int.h`, SQLite core APIs, tokenizer APIs, varint/doclist helpers from the FTS3 subsystem, FTS hash-table helpers, and build-time macros such as `SQLITE_ENABLE_FTS3`, `SQLITE_TEST`, `SQLITE_DISABLE_FTS4_DEFERRED`, `FTS3_LOG_MERGES`, and debug/assertion macros.

Important integration points outside this file include FTS3 table setup/destruction code, query evaluation in `fts3.c`, tokenizer modules, FTS4 stat/docsize helpers, and tests that exercise special inserts and corruption handling.

## Risks And Edge Cases
The largest risk is corruption handling in compact binary formats. Segment nodes, doclists, root blobs, varints, and `%_segdir.end_block` text/int dual encoding are all parsed manually. The code adds padding and many bounds checks, but malformed databases still exercise subtle integer, prefix-compression, and incremental-read paths.

Merge logic is stateful and persistent. Incorrect idx repacking, segment truncation, appendable block reservation, promotion, or hint handling can create duplicate terms, lost terms, leaked segment blocks, or future corruption. The `p->bIgnoreSavepoint` window in segdir repacking is also a delicate integration point with SQLite savepoint behavior.

External-content tables alter assumptions: content rows may not be stored in `%_content`, emptiness cannot be inferred the same way, and rebuild/integrity depend on reading the external source. Rowid/docid alias conflicts and `ON CONFLICT REPLACE` handling are another important edge.

Tokenizer behavior is trusted for non-negative positions and non-empty tokens. Tokenizers returning invalid positions or tokens cause `SQLITE_ERROR`; tokenizer OOM/IO errors propagate.

## Test Signals
High-value tests include insert/update/delete with explicit rowid and docid aliases; REPLACE conflict handling; external-content rebuilds; language-id isolation; prefix indexes; `order=desc`; docsize/stat correctness; pending flush at memory and docid ordering boundaries; optimize and full merge; incremental merge continuation across transactions; automerge persistence; corrupt node/doclist/root/end-block inputs; deferred-token query behavior; and integrity-check mismatch detection.

Existing signals are likely in SQLite FTS3/FTS4 test suites, `fts3.test`, corruption tests, incremental merge tests, optimize/rebuild/integrity command tests, and coverage tooling such as `ext/fts3/tool/fts3cov.sh`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/tool/fts3cov.sh -->
# sources/storage-engines/sqlite/ext/fts3/tool/fts3cov.sh

## Purpose
`fts3cov.sh` is a small developer coverage helper for the SQLite FTS3 extension. It runs the FTS3 Tcl test suite under `testfixture`, then prints branch-coverage summaries from `gcov` for each C file under `ext/fts3`.

## Important APIs, Types, And Functions
This is a POSIX shell script, not a library. It uses:

`set -e` to stop on unhandled command failures.

`srcdir=\`dirname $(dirname $(dirname $(dirname $0)))\`` to derive the SQLite source root from the script path.

`./testfixture $srcdir/test/fts3.test --output=fts3cov-out.txt` to run the FTS3 test suite and capture test output.

A `for` loop over ``ls $srcdir/ext/fts3/*.c`` to run `gcov -b` on each FTS3 C basename and filter the `Taken at least once` branch-coverage line through `grep` and `sed`.

## Control Flow
The script assumes it is launched from a build directory containing `./testfixture` and `.gcno/.gcda` files for the FTS3 C objects. It computes the source root, executes `test/fts3.test`, emits a blank line, then iterates over all FTS3 C files by basename. For each file it prints `<file>: ` and then appends the branch coverage percentage reported by `gcov -b`.

Because `set -e` is active, failure to run the test fixture, `gcov`, or the filtering pipeline can terminate the script.

## State And Persistence Behavior
The script writes `fts3cov-out.txt` in the current directory and relies on coverage data files created by prior or current test execution. It does not modify source files or SQLite databases intentionally. `gcov` may emit `.gcov` files as side effects in the working directory depending on toolchain behavior.

## Dependencies
Dependencies are `/bin/sh`, `dirname`, `ls`, `basename`, `gcov`, `grep`, `sed`, a coverage-instrumented SQLite build, and a working `testfixture` binary. The source tree must have `test/fts3.test` and `ext/fts3/*.c` relative to the computed root.

## Integration Points
It integrates with SQLite's Tcl test harness and GCC/gcov-style coverage workflow. It is specifically aimed at FTS3/FTS4 C sources and complements the main test suite by summarizing branch coverage after `fts3.test`.

## Risks And Edge Cases
The path calculation and unquoted command substitutions are brittle for paths containing whitespace. `echo -ne` is not portable across all `/bin/sh` implementations. The `ls | for` pattern can mishandle unusual filenames, though SQLite source filenames are stable and simple. The script assumes `gcov` can locate coverage notes by basename from the current directory; out-of-tree builds may need different `gcov` options.

## Test Signals
A useful validation is to run it from a coverage-enabled SQLite build directory and confirm `fts3cov-out.txt` is produced and each FTS3 C file prints a branch coverage percentage. Failures generally indicate missing testfixture, missing coverage instrumentation, wrong working directory, or gcov version/path mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/tool/fts3cov.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/tool/fts3view.c -->
# sources/storage-engines/sqlite/ext/fts3/tool/fts3view.c

## Purpose
`fts3view.c` is a standalone debugging and analysis utility for SQLite FTS3/FTS4 indexes. Linked against a SQLite build with `SQLITE_ENABLE_FTS4`, it opens a database, lists FTS3/4 tables, or inspects an FTS table's schema, statistics, vocabulary, segment layout, raw segment bytes, decoded segment nodes, decoded doclists, and largest segment blocks.

## Important APIs, Types, And Functions
Global command parsing state is `nExtra` and `azExtra`. `findOption()` consumes simple `--name` and `--name value` options from that array.

SQLite helpers are `prepare()` and `runSql()`. `prepare()` formats SQL with `sqlite3_vmprintf()`, prepares it, and exits on error. `runSql()` formats and executes SQL and returns the SQLite result code.

Inspection commands are implemented by `showSchema()`, `showStat()`, `showVocabulary()`, `showSegmentStats()`, `showSegdirMap()`, `showSegment()`, `showDoclist()`, and `listBigSegments()`.

Binary format helpers are `getVarint()`, `decodeSegment()`, `printBlob()`, `atoi64()`, `prepareToGetSegment()`, and `decodeDoclist()`. These decode the FTS3 segment-node and doclist formats enough to print human-readable diagnostics.

`main()` opens the database, lists FTS tables when only a database argument is supplied, or dispatches `big-segments`, `doclist`, `schema`, `segdir`, `segment`, `segment-stats`, `stat`, or `vocabulary`.

## Control Flow
With one argument, `main()` scans `sqlite_schema` for `*_segdir` tables and prints the corresponding virtual-table creation SQL. With table and command arguments, it dispatches to one command handler and returns.

`showVocabulary()` creates a temporary `fts4aux` table with a randomized name inside a transaction, computes document count, token totals, rare-token counts, and top tokens, then rolls back so the auxiliary table is discarded.

`showSegmentStats()` aggregates `%_segments` and `%_segdir` sizes, splits leaf versus interior/root segments, consults `PRAGMA page_size`, counts oversized leaf blocks, and prints per-relative-level summaries.

`showSegdirMap()` iterates `%_segdir` grouped by index and level, prints root rowids as `r<rowid>`, maps tree and leaf block ranges, and identifies NULL marker blocks used by appendable incremental-merge segments.

`showSegment()` selects either a `%_segdir.root` blob (`rN`) or a `%_segments.block` blob (`N`), then either hex-dumps it with `printBlob()` or parses it with `decodeSegment()`. `showDoclist()` selects a segment/root blob, slices by offset and size, and either dumps or decodes the doclist.

## State And Persistence Behavior
The program is mostly read-only. It opens the target database and runs SELECT/PRAGMA queries against schema and FTS shadow tables. The main exception is `showVocabulary()`, which creates an `fts4aux` virtual table inside `BEGIN` and ends with `ROLLBACK`, making it intentionally temporary.

All output is written to stdout/stderr. The utility exits with status 1 for usage errors, open failures, or prepare failures. It does not attempt to recover from malformed command arguments or corrupt FTS blobs beyond basic parsing.

## Dependencies
The file depends on the SQLite C API and standard C headers. Runtime use requires an SQLite library built with FTS4 support so `fts4aux` and FTS3/FTS4 shadow-table conventions exist. It assumes legacy shadow-table names `%_segments`, `%_segdir`, and `%_stat`.

## Integration Points
This is a tooling companion for the FTS3/FTS4 storage format implemented by files such as `fts3_write.c`. It understands the same segment-node prefix compression, doclist varints, `%_segdir` block ranges, `root` blobs, and appendable NULL marker conventions. It is useful for diagnosing merge behavior, segment bloat, vocabulary distribution, and corrupt or suspicious segment records.

## Risks And Edge Cases
This is diagnostic code and uses process exits for many errors. It builds SQL with `%q`/`%Q` escaping for table names in most places, but it assumes trusted local use. `decodeSegment()` has a fixed 1000-byte term buffer and exits if a term is too long. `getVarint()` is permissive and does not receive a buffer length, so corrupt blobs can cause misleading output or unsafe reads if used outside controlled debugging. `showVocabulary()` uses `sqlite3_mprintf("viewer_%llx", zTab, r)` with an extra unused argument, harmless in practice but a sign that this is not production-path code.

## Test Signals
Useful checks include running the tool against a database with no FTS tables, a simple FTS3 table, an FTS4 table with `%_stat`, a table with prefix indexes, a database after optimize/incremental merge, and known segment/doclist offsets. The `--raw` and decoded modes should agree on blob sizes and offsets. Building the tool against the SQLite amalgamation with `SQLITE_ENABLE_FTS4` is the first validation gate.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/tool/fts3view.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5.h -->
# sources/storage-engines/sqlite/ext/fts5/fts5.h

## Purpose
`fts5.h` declares the public extension interfaces for SQLite FTS5. It lets applications register custom auxiliary functions and custom tokenizers, and it defines the callback tables that FTS5 passes to those extensions at runtime.

The header is ABI-facing: it contains forward declarations, function-pointer typedefs, versioned API structs, tokenizer structs, and tokenization flags. It includes `sqlite3.h` and wraps declarations in `extern "C"` for C++ consumers.

## Important APIs, Types, And Functions
`fts5_extension_function` is the signature for auxiliary SQL functions registered with FTS5. It receives an `Fts5ExtensionApi`, an `Fts5Context`, a SQLite result context, and trailing SQL values.

`Fts5PhraseIter` is an opaque iterator payload used by phrase-instance and phrase-column iteration APIs. Applications allocate it but must not inspect or mutate the fields directly.

`Fts5ExtensionApi` is the auxiliary-function callback table. Version 4 includes row/column metadata (`xColumnCount`, `xRowCount`, `xColumnTotalSize`, `xColumnSize`, `xColumnText`, `xColumnLocale`), query metadata (`xPhraseCount`, `xPhraseSize`, `xQueryToken`), match-instance APIs (`xInstCount`, `xInst`, `xInstToken`, `xPhraseFirst`, `xPhraseNext`, `xPhraseFirstColumn`, `xPhraseNextColumn`), row identity (`xRowid`), tokenizer access (`xTokenize`, `xTokenize_v2`), phrase query execution (`xQueryPhrase`), and per-query auxiliary cache (`xSetAuxdata`, `xGetAuxdata`).

`Fts5Tokenizer` is an opaque tokenizer instance. `fts5_tokenizer_v2` is the preferred tokenizer module interface with `iVersion`, `xCreate`, `xDelete`, and locale-aware `xTokenize`. `fts5_tokenizer` is the legacy interface without `iVersion` and without locale arguments.

Tokenization flags are `FTS5_TOKENIZE_QUERY`, `FTS5_TOKENIZE_PREFIX`, `FTS5_TOKENIZE_DOCUMENT`, and `FTS5_TOKENIZE_AUX`. Token callback flags include `FTS5_TOKEN_COLOCATED` for synonyms at the same token position.

`fts5_api` is the registration/retrieval table. It supports `xCreateTokenizer`, `xFindTokenizer`, `xCreateFunction`, and version-3 additions `xCreateTokenizer_v2` and `xFindTokenizer_v2`.

## Control Flow
Extensions do not instantiate these structs directly except for tokenizer modules. At initialization time, an application obtains `fts5_api` from SQLite's FTS5 extension mechanism, then registers tokenizers or auxiliary functions. During MATCH queries or auxiliary function calls, FTS5 invokes the registered callbacks and supplies an `Fts5ExtensionApi` plus an `Fts5Context`.

Auxiliary functions call `Fts5ExtensionApi` methods to inspect the current row, current query, phrase instances, column text, tokenizer output, and cached per-query state. Some methods can trigger internal scans, especially phrase queries, instance enumeration on reduced-detail tables, and token retrieval for prefix matches.

Tokenizer control flow starts with `xCreate()` when FTS5 needs a tokenizer instance, then repeated `xTokenize()` calls for document indexing, query parsing, prefix query parsing, or auxiliary tokenization. The tokenizer reports tokens by invoking the provided `xToken()` callback in input order and returns either `SQLITE_OK`, the callback's error code, or another SQLite error code. `xDelete()` is called once for each successfully created tokenizer instance.

## State And Persistence Behavior
This header itself stores no state and writes no data. It defines contracts for FTS5-owned state and extension-owned state.

Auxiliary data managed by `xSetAuxdata()`/`xGetAuxdata()` is scoped to a single MATCH query and a single auxiliary function. Replacing or query cleanup invokes the registered destructor unless the value is cleared with `xGetAuxdata(..., bClear!=0)`.

Tokenizer instances are extension-owned objects returned by `xCreate()` and later destroyed by `xDelete()`. Tokenizers may maintain their own configuration and locale behavior, but token text passed to callbacks is consumed by FTS5 according to the callback contract.

Persistent FTS index contents are affected indirectly by tokenizer output during `FTS5_TOKENIZE_DOCUMENT`. Changing tokenizer normalization, synonym emission, locale handling, or colocated token behavior can change indexed terms and therefore query compatibility with existing databases.

## Dependencies
The only direct include is `sqlite3.h`. The API depends on SQLite result/value types, SQLite integer types, SQLite error codes, and FTS5's virtual-table/runtime implementation that fills these callback tables.

## Integration Points
Auxiliary functions integrate through `fts5_api.xCreateFunction()` and are later found through FTS5's virtual-table `xFindFunction()` path. Tokenizers integrate through `xCreateTokenizer()` or `xCreateTokenizer_v2()` and are referenced by FTS5 table definitions and tokenizer lookup APIs.

The header explicitly documents behavior for `detail=none`, `detail=column`, contentless tables, `columnsize=0`, `tokendata=1`, `fts5_locale()`, prefix-token instance lookup, `insttoken`, and synonym strategies. These are key compatibility points between extension code and FTS5 storage/query internals.

## Risks And Edge Cases
This is a C ABI contract, so struct versioning matters. Callers must check `iVersion` before using version-gated fields. Setting tokenizer methods to NULL is undefined behavior. Legacy and v2 tokenizer APIs differ in locale support and registration/retrieval ownership.

Several APIs return pointers to FTS5-owned buffers rather than copies. Extension code must treat returned column text, query tokens, instance tokens, and locale strings as transient and must not write through them. Range errors are reported as `SQLITE_RANGE` for invalid columns, phrase indexes, instance indexes, or token indexes.

Performance traps are prominent: `xInstCount`, `xInst`, phrase iteration, and token retrieval may be slow for `detail=none`, `detail=column`, contentless tables, and prefix-token queries unless `insttoken` support is enabled. Tokenizers that emit synonyms in both query and document modes can work but waste CPU or disk. Misusing `FTS5_TOKEN_COLOCATED` as the first token is an error.

## Test Signals
Good tests register an auxiliary function that exercises all available `Fts5ExtensionApi` methods by version, validates auxdata destructor behavior, checks range errors, and compares phrase/column iteration order. Tokenizer tests should cover legacy and v2 registration, locale propagation, all tokenization flags, callback error propagation, synonyms with `FTS5_TOKEN_COLOCATED`, prefix queries, `tokendata=1`, contentless tables, and reduced-detail tables.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5.h -->
