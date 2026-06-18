# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 96989-105142

## Scope And Purpose

This chunk covers a large contiguous part of SQLite's FTS3/FTS4 implementation in the FoundationDB-contrib SQLite amalgamation. It begins in the position-list phrase merge helper, then implements FTS3 doclist merging and query evaluation, the `fts3`/`fts4` virtual-table method table, tokenizer registration, the `fts4aux` statistics virtual table, the MATCH-expression parser, FTS3's standalone hash table, the simple and porter tokenizers, most of the FTS3 write/segment merge machinery, deferred-token handling, `xUpdate`/`optimize`, and the opening definitions for snippet, offsets, and matchinfo processing.

The central theme is the full-text index lifecycle: parse a MATCH expression, tokenize input text, read and merge compressed doclists from pending terms and `%_segments`/`%_segdir`, evaluate boolean/phrase/NEAR constraints, expose auxiliary SQL functions and `fts4aux`, and update persistent FTS shadow tables on INSERT/UPDATE/DELETE/optimize.

## Important APIs, Types, And Functions

`fts3PoslistPhraseMerge()`, completed at the start of this chunk, and `fts3PoslistNearMerge()` operate on FTS3 position lists. They compare column-aware delta-encoded token positions, preserve or discard left/right positions depending on caller needs, and implement phrase and bidirectional NEAR matching.

`fts3DoclistMerge()` is the main compressed doclist combiner. It supports `MERGE_OR`, `MERGE_POS_OR`, `MERGE_AND`, `MERGE_NOT`, `MERGE_PHRASE`, `MERGE_POS_PHRASE`, `MERGE_NEAR`, and `MERGE_POS_NEAR`. It reads delta-varint docids from two sorted input doclists, writes delta-varint output to a caller-provided buffer, and optionally counts result documents.

`TermSelect` plus `fts3TermSelectCb()`, `fts3TermSelectMerge()`, `sqlite3Fts3SegReaderCursor()`, `fts3TermSegReaderCursor()`, and `fts3TermSelect()` retrieve all segment doclists for a term or prefix. They combine pending terms with on-disk segment readers, configure `Fts3SegFilter`, optionally apply column filters and position requirements, and merge multiple matching segment doclists into one result.

`fts3PhraseSelect()`, `fts3EvalExpr()`, `fts3NearMerge()`, and `sqlite3Fts3ExprNearTrim()` evaluate phrase and expression nodes. Phrase evaluation may process tokens in cheapest-first order during `xFilter()`, defer common tokens, merge multi-token phrases by position distance, and retain positions for NEAR, snippet, offsets, or matchinfo consumers.

`fts3FilterMethod()`, `fts3NextMethod()`, `fts3EofMethod()`, `fts3RowidMethod()`, `fts3ColumnMethod()`, `fts3UpdateMethod()`, transaction hooks, `fts3FindFunctionMethod()`, and `fts3RenameMethod()` form the `fts3Module` `sqlite3_module`. `sqlite3Fts3Init()` registers the `fts3` and `fts4` modules, initializes tokenizer hash state, registers `fts4aux`, and overloads `snippet`, `offsets`, `matchinfo`, and `optimize`.

`Fts3auxTable` and `Fts3auxCursor` implement the `fts4aux` virtual table with schema `term, col, documents, occurrences`. Its cursor reuses FTS segment readers and computes per-term aggregate and per-column document/occurrence counts by decoding position-bearing doclists.

The parser section defines `ParseContext`, `getNextToken()`, `getNextString()`, `getNextNode()`, `insertBinaryOperator()`, `fts3ExprParse()`, `sqlite3Fts3ExprParse()`, and `sqlite3Fts3ExprFree()`. It handles legacy and parenthesized FTS3 syntax, column qualifiers, quoted phrases, prefix tokens, implicit AND, OR/AND/NOT/NEAR precedence, and `NEAR/N` distance arguments.

The hash section defines the FTS3-local `Fts3Hash` operations: `sqlite3Fts3HashInit()`, `sqlite3Fts3HashClear()`, `sqlite3Fts3HashFindElem()`, `sqlite3Fts3HashFind()`, and `sqlite3Fts3HashInsert()`. It supports string or binary keys, optional key copies, bucket rehashing, and a global insertion-order list.

The tokenizer sections implement `porterTokenizerModule` and `simpleTokenizerModule`. The porter tokenizer scans non-delimiter runs, case-folds ASCII, applies a Porter stemmer for short alphabetic words, and falls back to truncating/copying for unsuitable terms. The simple tokenizer lowercases ASCII and treats configured or default non-alphanumeric ASCII bytes as delimiters.

The write section defines persistent indexing structures and helpers: `PendingList`, `Fts3DeferredToken`, `Fts3SegReader`, `SegmentWriter`, and `SegmentNode`; SQL statement ids for shadow-table operations; `fts3SqlStmt()`, `fts3SqlExec()`, `sqlite3Fts3ReadLock()`, `sqlite3Fts3AllSegdirs()`, pending-list append/add helpers, `fts3InsertTerms()`, `fts3InsertData()`, `fts3DeleteAll()`, `fts3DeleteTerms()`, segment readers/writers, `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, `sqlite3Fts3SegReaderFinish()`, `fts3SegmentMerge()`, `sqlite3Fts3PendingTermsFlush()`, docsize/stat encoders, `sqlite3Fts3UpdateMethod()`, and `sqlite3Fts3Optimize()`.

The snippet opening defines matchinfo format flags (`p`, `c`, `n`, `a`, `l`, `s`, `x`), `LoadDoclistCtx`, `SnippetIter`, `SnippetPhrase`, `SnippetFragment`, `MatchInfo`, `StrBuffer`, `fts3GetDeltaPosition()`, and `fts3ExprIterate()`. The actual snippet/matchinfo algorithms continue after this chunk.

## Control Flow

Query execution starts in `fts3FilterMethod()`. For full-text searches, it parses the MATCH argument with `sqlite3Fts3ExprParse()`, obtains a content-table read lock, evaluates the expression into a docid doclist with `fts3EvalExpr()`, closes any segment blob handle, prepares a content-row lookup statement, and calls `fts3NextMethod()`. Full scans prepare a `%_content` scan; docid lookups bind one rowid.

`fts3EvalExpr()` recursively evaluates expression trees. Phrase nodes call `fts3PhraseSelect()`. OR allocates a combined output and uses `MERGE_OR`; AND and NOT merge bare docid lists in-place; NEAR first forces position-bearing phrase lists, then calls `fts3NearMerge()`. In filter mode, AND subexpressions are costed through segment-reader cost estimates and processed cheapest first. If the next token/subexpression appears more expensive than the already narrowed doclist, the evaluator marks tokens deferred and returns a superset.

Deferred evaluation runs in `fts3NextMethod()` through `fts3EvalDeferred()`. If a filter-time result was a superset, the current content row is sought, deferred doclists are rebuilt for that single row by retokenizing its columns in `sqlite3Fts3CacheDeferredDoclists()`, and `fts3EvalExpr()` is rerun in `FTS3_EVAL_NEXT` mode to decide whether to accept the row.

Term selection creates a `Fts3SegReaderCursor` over pending terms and/or `%_segdir` rows. `sqlite3Fts3SegReaderCursor()` optionally adds a pending-terms reader, scans selected segment-directory rows, narrows leaf ranges with `fts3SelectLeaf()` for bounded term searches, and allocates one `Fts3SegReader` per segment. `sqlite3Fts3SegReaderStart()` advances each reader to the filter term and sorts readers by term/age. `sqlite3Fts3SegReaderStep()` groups readers on the same term, merges their doclists by docid, applies column filtering and position stripping as requested, and returns `SQLITE_ROW` for each merged term.

The parser is hand-written. `getNextNode()` tokenizes operators, parentheses, quoted strings, and single tokens. `fts3ExprParse()` repeatedly inserts phrase and operator nodes into a tree using `insertBinaryOperator()`, adds implicit AND nodes when adjacent phrases occur, handles legacy `-token` as NOT branches, rejects NEAR operands that are not phrases, and reports mismatched parentheses from the public wrapper.

Updates flow through `sqlite3Fts3UpdateMethod()`. Deletes or updates first check whether removing the row empties the table. If so, all FTS shadow tables and pending terms are cleared. Otherwise the old row is tokenized with column `-1` to append delete markers into pending terms, content/docsize rows are deleted, and document totals are decremented. Inserts write `%_content`, advance or flush pending terms if docids are out of order or memory is high, tokenize inserted columns into pending lists, optionally write `%_docsize`, and update `%_stat` totals.

Pending terms are flushed by `sqlite3Fts3PendingTermsFlush()`, which calls `fts3SegmentMerge()` with `FTS3_SEGCURSOR_PENDING`. Segment merging opens readers for the requested level or all levels, streams merged term/doclists through `sqlite3Fts3SegReaderStep()`, feeds them to `fts3SegWriterAdd()`, deletes old `%_segments`/`%_segdir` rows or clears pending terms, and writes the replacement segment with `fts3SegWriterFlush()`.

Segment writing batches prefix-compressed term/doclist records into leaf blocks of `p->nNodeSize`. When a leaf fills, `fts3SegWriterAdd()` writes it to `%_segments` and inserts a separator term into an in-memory `SegmentNode` tree. `fts3NodeWrite()` later writes interior nodes bottom-up into `%_segments`, except for the root, which is stored inline in the `%_segdir.root` blob. Single-leaf segments store the whole root directly in `%_segdir`.

The `fts4aux` cursor starts with `fts3auxFilterMethod()`, configures an exact or range scan filter, opens a segment reader cursor, then uses `fts3auxNextMethod()` to parse each term's merged position doclist. A small state machine counts document boundaries, column markers, and positions into `aStat[0]` for all columns and `aStat[i+1]` for individual columns, yielding one row for `*` plus one row per column that has documents.

## State And Persistence Behavior

FTS3 persistent state lives in shadow tables. `%_content` stores row text by docid, `%_segments` stores segment b-tree blocks keyed by blockid, `%_segdir` stores segment metadata and inline roots, `%_docsize` stores per-row encoded column token counts when enabled, and `%_stat` stores record 0 with total rows, per-column token totals, and total byte size when enabled.

Pending indexing state is in `Fts3Table.pendingTerms`, a hash from term bytes to `PendingList`. A `PendingList` stores delta-encoded docids, column markers, positions, and zero terminators in memory until flush. `p->iPrevDocid` and `p->nPendingData` enforce monotonically increasing pending docids and trigger flushes when docids go backwards or pending data exceeds `nMaxPendingData`.

Doclists and position lists are compact binary formats. Docids are stored as delta varints. Position-list entries encode position deltas plus two; `0x00` terminates a doclist entry's positions, and `0x01` introduces a new column number. Many functions mutate cursor pointers in-place while reading these lists, so ownership and pointer advancement are part of the API contract.

Segment readers may own heap-allocated node buffers, point at inline root-node memory immediately after the reader object, or iterate directly over pending-term hash entries. `sqlite3Fts3ReadBlock()` reuses `Fts3Table.pSegments`, an open incremental blob handle on `%_segments.block`; callers that can return to SQLite user code close it with `sqlite3Fts3SegmentsClose()` to release locks.

Segment writers accumulate transient leaf buffers and an in-memory interior tree before persisting blocks. On successful flush, durable changes are `%_segments` inserts and a `%_segdir` insert. Merges delete obsolete segment blocks and directory rows only after the replacement writer has collected merged term data, but the surrounding SQLite transaction provides atomicity.

Deferred token state is cursor-local. `sqlite3Fts3DeferToken()` links `Fts3DeferredToken` objects from phrase tokens to `Fts3Cursor.pDeferred`; `sqlite3Fts3CacheDeferredDoclists()` materializes row-local pending lists for the current row; `sqlite3Fts3FreeDeferredDoclists()` clears cached lists and loaded expression doclists; `sqlite3Fts3FreeDeferredTokens()` frees the token records.

Auxiliary functions receive the active FTS cursor through the hidden column whose name matches the table. `fts3ColumnMethod()` returns a blob containing the `Fts3Cursor *`; `fts3FunctionArg()` validates and extracts it for `snippet`, `offsets`, `matchinfo`, and `optimize`.

Tokenizer registration state is connection-local in an `Fts3Hash` stored as module auxiliary data. `sqlite3Fts3InitHashTable()` exposes it through the `fts3_tokenizer()` scalar function, and `hashDestroy()` frees it when the module is destroyed.

## Dependencies And Integration Points

This code depends heavily on SQLite core virtual-table APIs (`sqlite3_module`, `xFilter`, `xNext`, `xColumn`, `xUpdate`, `sqlite3_create_module_v2`, `sqlite3_overload_function`), SQL statement APIs, incremental blob APIs, SQLite memory allocation, `sqlite3_value`/`sqlite3_context`, and the FTS tokenizer interface (`sqlite3_tokenizer_module`).

The read/query path integrates with earlier FTS3 structures and helpers defined outside this range, including `Fts3Table`, `Fts3Cursor`, `Fts3Expr`, `Fts3Phrase`, `Fts3PhraseToken`, `Fts3SegReaderCursor`, `Fts3SegFilter`, `fts3BestIndexMethod()`, `fts3ConnectMethod()`, `fts3OpenMethod()`, `fts3CursorSeek()`, `fts3SelectLeaf()`, varint helpers, and position-list helpers.

The write path integrates with the FTS shadow schema created by table construction code outside this chunk. SQL templates in `fts3SqlStmt()` assume exact shadow table names (`%_content`, `%_segments`, `%_segdir`, `%_docsize`, `%_stat`) and exact column layouts. `fts3RenameMethod()` mirrors those names when the virtual table is renamed.

`sqlite3Fts3Init()` is the public initialization point for built-in or loadable FTS3. It registers `fts4aux` before registering `fts3`/`fts4`, installs the built-in `simple`, `porter`, and optional ICU tokenizers, optionally registers parser/tokenizer test functions under `SQLITE_TEST`, and shares one tokenizer hash between `fts3` and `fts4`.

The snippet/matchinfo opening connects the query evaluator to later auxiliary-function code. `sqlite3Fts3ExprLoadDoclist()`, `sqlite3Fts3ExprLoadFtDoclist()`, `sqlite3Fts3FindPositions()`, and `fts3ExprIterate()` are used by snippet, offsets, and matchinfo code to load phrase doclists, trim NEAR groups, and find positions for the current row/column.

Shared-cache locking is addressed through `sqlite3Fts3ReadLock()`, which intentionally reads `%_content` before segment tables so concurrent writers see expected lock behavior. This is important because FTS3 failures during commit can roll back a whole transaction.

## Risks And Edge Cases

The code trusts compressed doclist invariants in many hot paths. Some segment-reader paths return `SQLITE_CORRUPT` for malformed node prefix/suffix lengths or doclist terminators, but in-memory pending lists and merge helpers rely on internal generation correctness and asserts. Corrupt shadow-table blobs can still exercise pointer-heavy varint loops.

`fts3DoclistMerge()` requires the caller to provide a sufficiently large output buffer. Most call sites allocate `nLeft+nRight+1`, but in-place AND/NOT merging writes into the left buffer. Future changes that alter output-size assumptions would risk overwrite or truncated results.

Deferred-token optimization intentionally allows `xFilter()` to return a superset. Correctness then depends on `fts3NextMethod()` always calling `fts3EvalDeferred()` before accepting rows and on `sqlite3Fts3CacheDeferredDoclists()` reproducing tokenizer behavior exactly for the content row.

The tokenizer API stores and returns raw C pointers as SQL blobs through `fts3_tokenizer()` and the hidden FTS cursor column. This is a legacy extension mechanism and is process-local, ABI-sensitive, and unsafe to persist or expose across trust boundaries.

`sqlite3Fts3InitTokenizer()` mutates a copy of the tokenizer specification in place while dequoting tokens. It assumes `sqlite3Fts3NextToken()` finds at least one token; malformed or empty tokenizer strings need coverage because `z[n] = '\0'` follows immediately.

The porter tokenizer is ASCII-centric. Non-ASCII bytes are token characters but not case-folded or stemmed in the same way as ASCII words, and custom simple-tokenizer delimiters reject UTF-8 delimiter bytes. Index compatibility depends on using the same tokenizer configuration at query and insert time.

Segment merge and optimize operations can be expensive and write many shadow-table rows. `sqlite3Fts3Optimize()` wraps the merge in a savepoint and rolls back on error, but the special insert path `INSERT INTO tbl(tbl) VALUES('optimize')` maps `SQLITE_DONE` to success and clears pending terms only on non-DONE merge results.

`fts3SpecialInsert()` has a likely typo in the test-only `maxpending=` branch: it checks `nVal>11` but calls `sqlite3_strnicmp(zVal, "maxpending=", 9)` and reads `&zVal[11]`. Test-only tuning commands should verify the intended prefix length.

`fts3SegmentMerge()` asserts `pWriter` after streaming terms. If a segment cursor exists but all terms are empty/ignored, an assert build could fail; non-assert builds would call `fts3SegWriterFlush()` with NULL if not otherwise prevented by cursor behavior.

Several cleanup paths depend on closing reusable resources. Virtual-table methods that indirectly call `sqlite3Fts3ReadBlock()` must close `p->pSegments` before returning to user code, or they may hold blob locks longer than intended.

## Test Signals

Expression parser tests should cover legacy and parenthesized modes, implicit AND, OR precedence differences, explicit AND/NOT, legacy `-token`, `NEAR` and `NEAR/N`, invalid NEAR operands, mismatched parentheses, column qualifiers, quoted phrases, prefix `*`, malformed quotes, and tokenizer errors. Under `SQLITE_TEST`, `fts3_exprtest()` provides a direct parse-tree signal.

Query tests should exercise term, prefix, phrase, OR, AND, NOT, and NEAR searches across multiple columns and multiple segment levels, including cases that require position lists, column filters, doclist stripping, and segment/pending-term merging. They should compare results before and after pending-term flushes and segment optimization.

Deferred-evaluation tests should create high-frequency terms that trigger deferral, then verify `xFilter()` superset behavior is refined correctly by `xNext()` for phrase and boolean queries, including snippets/matchinfo after deferred doclists are cached.

Write-path tests should cover insert, update with same docid, update with changed docid, delete, deleting the last row, rowid/docid conflict handling, pending flush on out-of-order docid, pending flush on size threshold, `%_docsize` and `%_stat` maintenance, and rollback clearing pending terms.

Segment tests should force multi-leaf segments with small test node sizes, level overflow at `FTS3_MERGE_COUNT`, optimize-all merges, inline-root segments, prefix-compressed separator terms, corrupted segment node blobs, and `sqlite3Fts3SegReaderCost()` with and without `%_stat`.

Auxiliary-function tests should validate `snippet()`, `offsets()`, `matchinfo()` argument validation and cursor seeking, plus `optimize()` text/error results. `fts4aux` tests should verify exact, range, and full scans; `ORDER BY term ASC` planning; `*` aggregate rows; per-column document and occurrence counts; and stop-term behavior.

Tokenizer tests should check simple-tokenizer delimiter configuration, ASCII case folding, non-ASCII token inclusion, porter stemming rules, long-word fallback/truncation, digit handling, tokenizer lookup/registration through `fts3_tokenizer()`, and the `SQLITE_TEST` tokenizer test helpers when available.
