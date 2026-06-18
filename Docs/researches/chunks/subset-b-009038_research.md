# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 194032-202197

## Scope

This chunk covers a dense section of SQLite's vendored FTS3/FTS4 implementation. It begins inside the FTS query evaluator's deferred-token cost analysis and result iteration logic, completes `fts3.c`, then includes `fts3_aux.c`, `fts3_expr.c`, `fts3_hash.c`, `fts3_porter.c`, `fts3_tokenizer.c`, `fts3_tokenizer1.c`, `fts3_tokenize_vtab.c`, and the opening of `fts3_write.c`.

The executable surface spans query matching, NEAR filtering, matchinfo statistics, fts4aux term-stat virtual tables, MATCH-expression parsing, tokenizer registry and tokenizer implementations, tokenizer-inspection virtual tables, pending-term accumulation, segment directory SQL statement management, segment readers, and initial segment-writing helpers.

## Purpose

The first section finishes FTS query evaluation. It decides when expensive token doclists can be deferred, starts segment readers for each query token, advances expression trees through candidate docids, verifies deferred terms and NEAR constraints against loaded row text, maintains phrase position lists, and gathers phrase statistics for `matchinfo()`.

The `fts3_aux.c` section implements the `fts4aux` virtual table. It exposes index vocabulary statistics as rows with `term`, `col`, `documents`, `occurrences`, and hidden `languageid`, using FTS segment readers to scan term doclists and count per-column document and occurrence totals.

The `fts3_expr.c` section is the hand-written parser for the right-hand side of the FTS `MATCH` operator. It supports legacy syntax and optional parenthesized syntax, recognizes phrases, column-qualified tokens, quoted strings, `OR`, `AND`, `NOT`, `NEAR[/N]`, prefix tokens, first-token markers, implicit AND, legacy unary minus, expression balancing, depth checks, and parser test functions.

The `fts3_hash.c` section provides the FTS-local hash table used for tokenizer registries and pending-term maps. It supports string or binary keys, optional key copying, lookup, insertion, replacement, deletion, rehashing, and full cleanup.

The tokenizer sections implement the built-in Porter stemmer tokenizer, the generic tokenizer registry SQL function, the built-in simple tokenizer, and the `fts3tokenize` virtual table used to inspect tokenization output.

The `fts3_write.c` opening defines the data structures and SQL statement cache used by FTS writes and segment maintenance. It starts the logic for pending doclists, language/prefix/level mapping, shadow-table access, block reads, segment readers, and segment writer construction.

## Important APIs, Types, and Functions

- Query evaluation and deferred matching:
  - `fts3EvalAverageDocsize()` reads `%_stat` doctotal data and estimates average document size in pages for deferred-token cost decisions.
  - `fts3EvalSelectDeferred()` chooses tokens in an AND/NEAR cluster to defer based on doclist overflow pages, phrase constraints, estimated row counts, and average document size.
  - `fts3EvalStart()` allocates token readers, performs FTS4 deferred-token selection, and starts readers.
  - `fts3EvalNextRow()` advances `Fts3Expr` trees for PHRASE, AND, OR, NOT, and NEAR nodes in docid order, while intentionally treating NEAR as AND and ignoring deferred tokens at this stage.
  - `sqlite3Fts3EvalTestDeferred()` loads current row content, builds deferred token doclists, evaluates the full expression including NEAR, and frees deferred doclists.
  - `fts3EvalNext()` is the core xNext-style loop for a full-text cursor, repeatedly skipping candidate rows that fail deferred or NEAR checks and enforcing `iMinDocid`/`iMaxDocid`.
  - `sqlite3Fts3EvalPhraseStats()` and `sqlite3Fts3EvalPhrasePoslist()` provide matchinfo/snippet/offset consumers with phrase occurrence totals and per-column position lists.
  - `sqlite3Fts3EvalPhraseCleanup()`, `sqlite3Fts3MsrCancel()`, and `sqlite3_fts3_init()` handle phrase cleanup, multi-segment-reader cancellation, and extension initialization.

- fts4aux virtual table:
  - `Fts3auxTable` stores the virtual table base plus a minimal `Fts3Table` handle for the target FTS table.
  - `Fts3auxCursor` embeds an `Fts3MultiSegReader`, `Fts3SegFilter`, term stop key, language id, rowid, current column, and dynamic per-column stats.
  - `fts3auxConnectMethod()` parses constructor arguments, declares `CREATE TABLE x(term, col, documents, occurrences, languageid HIDDEN)`, and builds a lightweight FTS table descriptor.
  - `fts3auxBestIndexMethod()` recognizes term equality/range constraints and hidden `languageid` equality, marks `ORDER BY term ASC` as consumed, and sets estimated costs.
  - `fts3auxFilterMethod()` initializes a segment-reader cursor for exact or range term scans.
  - `fts3auxNextMethod()` advances term rows and decodes doclists into total and per-column document/occurrence counters.
  - `sqlite3Fts3InitAux()` registers the `fts4aux` module.

- MATCH expression parser:
  - `ParseContext` carries tokenizer, language id, FTS table column names, default column, FTS4 syntax flag, parser nesting depth, and legacy unary-minus state.
  - `sqlite3Fts3OpenTokenizer()` opens tokenizer cursors and applies tokenizer `xLanguageid()` when supported.
  - `getNextToken()` parses a single token expression, including prefix `*`, legacy `-`, and FTS4 first-token `^`.
  - `getNextString()` tokenizes quoted phrases into one allocation containing `Fts3Expr`, `Fts3Phrase`, token array, and token text.
  - `getNextNode()` recognizes operators, quoted strings, parentheses, column prefixes, and regular tokens.
  - `fts3ExprParse()` constructs the expression tree, inserts implicit AND nodes, enforces NEAR operands as phrases, and handles legacy NOT branches.
  - `fts3ExprBalance()` and `fts3ExprCheckDepth()` rebalance AND/OR trees and enforce `SQLITE_FTS3_MAX_EXPR_DEPTH`.
  - `sqlite3Fts3ExprParse()` is the exported parser entry point and generates error messages.
  - `sqlite3Fts3ExprFree()` frees expression trees iteratively to avoid stack overflow.
  - Under `SQLITE_TEST`, `fts3_exprtest` and `fts3_exprtest_rebalance` expose parser output as SQL functions.

- FTS hash and tokenizer registry:
  - `sqlite3Fts3HashInit()`, `sqlite3Fts3HashClear()`, `sqlite3Fts3HashFindElem()`, `sqlite3Fts3HashFind()`, and `sqlite3Fts3HashInsert()` provide the FTS hash-table API.
  - `fts3TokenizerFunc()` implements the scalar `fts3_tokenizer()` registry accessor. Two-argument writes require either `SQLITE_DBCONFIG_ENABLE_FTS3_TOKENIZER` or a bound pointer blob; reads also gate pointer-blob return.
  - `sqlite3Fts3NextToken()` and `sqlite3Fts3InitTokenizer()` parse tokenizer specifications, dequote names/arguments, look up tokenizer modules, and call module `xCreate()`.
  - `sqlite3Fts3InitHashTable()` registers the tokenizer SQL functions and test helpers.

- Built-in tokenizers and tokenizer virtual table:
  - `porter_tokenizer` and `porter_tokenizer_cursor` implement a Porter stemmer tokenizer. `porter_stemmer()` lowercases ASCII terms, falls back for short/long/non-ASCII terms, and applies the standard Porter steps on reversed ASCII buffers.
  - `sqlite3Fts3PorterTokenizerModule()` returns the Porter tokenizer module.
  - `simple_tokenizer` and `simple_tokenizer_cursor` implement ASCII delimiter-based tokenization with lowercasing.
  - `sqlite3Fts3SimpleTokenizerModule()` returns the simple tokenizer module.
  - `Fts3tokTable` and `Fts3tokCursor` implement the `fts3tokenize` virtual table.
  - `fts3tokConnectMethod()` resolves and creates the configured tokenizer, defaulting to `simple`.
  - `fts3tokBestIndexMethod()` requires an `input = ?` constraint for cheap scans.
  - `fts3tokFilterMethod()` opens a tokenizer cursor over the supplied input, and `fts3tokColumnMethod()` returns input, token, byte offsets, and token position.
  - `sqlite3Fts3InitTok()` registers `fts3tokenize` with `sqlite3_create_module_v2()`.

- FTS write and segment primitives:
  - `PendingList`, `Fts3DeferredToken`, `Fts3SegReader`, `SegmentWriter`, and `SegmentNode` define pending doclists, deferred-token state, segment iterators, segment builders, and interior b-tree nodes.
  - `fts3SqlStmt()` caches prepared statements for FTS shadow-table operations, including `%_content`, `%_segments`, `%_segdir`, `%_docsize`, and `%_stat`.
  - `sqlite3Fts3SelectDoctotal()` and `sqlite3Fts3SelectDocsize()` expose validated `%_stat` and `%_docsize` lookups.
  - `fts3Writelock()` forces an early write lock on `%_segdir` before pending writes.
  - `getAbsoluteLevel()` maps language id, prefix-index id, and relative segment level into the absolute `%_segdir.level` namespace.
  - `sqlite3Fts3AllSegdirs()` prepares segment-directory scans for a specific level or all levels for one language/index.
  - `fts3PendingListAppendVarint()`, `fts3PendingListAppend()`, `fts3PendingTermsAddOne()`, `fts3PendingTermsAdd()`, `fts3PendingTermsDocid()`, and `sqlite3Fts3PendingTermsClear()` manage in-memory pending term doclists before flush.
  - `fts3InsertTerms()`, `fts3InsertData()`, `fts3DeleteAll()`, and `fts3DeleteTerms()` begin the insert/delete paths for FTS rows and shadow-table state.
  - `sqlite3Fts3ReadBlock()`, `sqlite3Fts3SegmentsClose()`, `fts3SegReaderIncrRead()`, `fts3SegReaderRequire()`, and `fts3SegReaderNext()` load segment blocks, including incremental reads for large nodes.
  - `sqlite3Fts3MsrOvfl()` estimates segment doclist overflow pages; `sqlite3Fts3SegReaderNew()`, `sqlite3Fts3SegReaderPending()`, `fts3SegReaderFirstDocid()`, and `fts3SegReaderNextDocid()` create and advance segment readers.
  - `fts3SegReaderSort()`, `fts3WriteSegment()`, `sqlite3Fts3MaxLevel()`, `fts3WriteSegdir()`, `fts3PrefixCompress()`, `fts3NodeAddTerm()`, `fts3NodeWrite()`, `fts3SegWriterAdd()`, and `fts3SegWriterFlush()` begin the segment-building and persistence path.

## Control Flow and Data Flow

FTS query execution begins with a parsed `Fts3Expr` tree and token readers. `fts3EvalStart()` allocates readers, optionally estimates token costs for FTS4, defers expensive tokens, and starts all remaining readers. `fts3EvalNext()` then calls `fts3EvalNextRow()` to advance the expression tree to the next candidate docid. AND/NEAR nodes merge left and right docid streams, OR nodes pick the earlier stream, NOT nodes keep the left stream while skipping matching right docids, and phrase nodes advance through phrase doclists. Candidate rows are then verified by `sqlite3Fts3EvalTestDeferred()`, which seeks the content row when necessary, builds deferred doclists, checks the full expression recursively, trims NEAR position lists, and skips false candidates.

NEAR handling is deliberately two-phase. During docid iteration it behaves like AND so that candidate selection can use ordinary docid stream merging. After a row is selected, `fts3EvalNearTest()` walks the NEAR chain, allocates temporary workspace proportional to the involved position lists, and calls `fts3EvalNearTrim()` from both sides to leave only positions that satisfy each NEAR distance. If a NEAR branch fails, its phrase position lists are invalidated so `snippet()`, `offsets()`, and `matchinfo()` do not report highlights from an unmatched NEAR clause.

Phrase statistics are gathered lazily. When `sqlite3Fts3EvalPhraseStats()` needs aggregate occurrence/row counts, `fts3EvalGatherStats()` finds the enclosing NEAR/deferred root, allocates `aMI[]` arrays for phrases, restarts iteration without incremental shortcuts, counts current-row position lists across all matching rows, then restores the cursor and expression root to the original docid. Fully deferred phrases outside NEAR use a conservative synthetic count equal to the table document count.

`fts4aux` scans index terms through a multi-segment reader. `xBestIndex` records whether the scan is exact, lower-bound, upper-bound, or range, plus optional language id. `xFilter` builds an `Fts3SegFilter` with position lists required, starts the reader, and calls `xNext`. `xNext` decodes each term's doclist as a small state machine: docid, initial column-0 or column switch, positions, and next docid separators. It accumulates row counts and occurrence counts for the aggregate `*` row and per-column rows, then emits only columns with nonzero document counts.

The parser uses tokenizer output rather than raw string splitting for terms. `getNextNode()` first strips whitespace and recognizes operators/parentheses/quoted phrases; otherwise it finds optional `column:` prefixes and delegates to `getNextToken()`. `fts3ExprParse()` maintains the previous node and current root, inserts implicit AND operators when two phrases are adjacent, threads operator precedence through `insertBinaryOperator()`, and returns `SQLITE_DONE` internally at end-of-input or close-parenthesis. Public parsing then balances large AND/OR trees to avoid deep recursion in later evaluation.

Pending-write flow starts when an insert or delete sets the active docid with `fts3PendingTermsDocid()`. `fts3PendingTermsAdd()` tokenizes each indexed column, appends docid/column/position varints to the main pending hash, and also adds configured prefix-index entries. Delete entries use column `-1` to encode deletion doclists. Pending data flushes when docids arrive out of order, language id changes, a delete/insert ordering constraint requires it, or the pending memory budget is exceeded.

Segment-reader flow handles three storage sources: pending hashes, root-only segments stored entirely in `%_segdir.root`, and multi-block segments in `%_segments`. `fts3SegReaderNext()` copies pending lists for hash entries, or reads leaf blocks from `%_segments`, optionally retaining a blob handle for incremental chunk loads. It decodes prefix-compressed terms and doclist sizes, validates bounds and terminators, and exposes the current term/doclist to multi-segment readers.

Segment-writer flow builds prefix-compressed leaf blocks and an in-memory interior tree. `fts3SegWriterAdd()` appends term/doclist records until a leaf exceeds node size, writes full leaves to `%_segments`, adds separator terms to `SegmentNode`, and tracks `nLeafData`. `fts3SegWriterFlush()` writes the final leaf and interior nodes, then writes one `%_segdir` record whose root is either the whole segment for root-only segments or the top interior node for multi-block segments.

## State and Persistence Behavior

`Fts3Cursor` state is mutated heavily during evaluation: `iPrevId`, `isEof`, `isRequireSeek`, `isMatchinfoNeeded`, `nDoc`, `nRowAvg`, deferred-token lists, and phrase doclists are all updated as query iteration progresses. Position lists may be edited in place by NEAR trimming and invalidated between rows.

`Fts3Phrase` owns loaded doclists (`aAll`), current-row position lists (`pList`, `nList`, `bFreeList`), incremental-reader flags, OR-position cache fields, and per-phrase matchinfo arrays. Cleanup must free both doclist buffers and token segment cursors.

`Fts3auxCursor` persists the active term scan and its per-column `aStat` array across virtual-table calls. `fts3auxFilterMethod()` explicitly finalizes old segment readers and frees old term/stop/stat allocations before reusing a cursor.

Parser expression trees use single-allocation layouts for phrase nodes and token text where possible. `sqlite3Fts3ExprFree()` is iterative because hostile or generated MATCH expressions may be large enough for recursive free to overflow the C stack.

The FTS hash table owns buckets, elements, and optionally copied keys. In replacement mode it returns old user data to the caller; in delete mode it frees the element and copied key but not caller-owned data. When element count reaches zero it clears buckets as well.

Tokenizer instances and cursors are module-owned but follow the FTS tokenizer ABI. Cursors retain input pointers or copied input buffers and dynamically resized token buffers. The `fts3tokenize` virtual table stores one tokenizer instance per virtual table and one tokenizer cursor per scan.

The write section is the first durable-storage-heavy part of the chunk. Prepared statements are cached in `Fts3Table.aStmt[]`; shadow-table changes target `%_content`, `%_segments`, `%_segdir`, `%_docsize`, and `%_stat`. Pending lists are in-memory until flushed; segment blocks are durable rows in `%_segments`; segment directory metadata is durable in `%_segdir`; doctotal/docsize metadata is durable in `%_stat` and `%_docsize`.

`sqlite3Fts3ReadBlock()` may leave a reusable `sqlite3_blob` handle in `Fts3Table.pSegments`, so callers that reach user-visible virtual-table boundaries must call `sqlite3Fts3SegmentsClose()` to avoid holding locks longer than expected.

## Dependencies and Integration Points

This code depends on SQLite core APIs for memory allocation, prepared statements, virtual table callbacks, SQL scalar functions, blobs, result values, database configuration, and error propagation. It also depends on FTS-internal doclist helpers, segment reader helpers, tokenizer interfaces, varint helpers, `Fts3Table`, `Fts3Cursor`, `Fts3Expr`, `Fts3Phrase`, `Fts3MultiSegReader`, and related macros defined earlier in the amalgamation.

The query evaluator integrates with SQLite's virtual table scan callbacks through FTS cursor state. It supplies phrase position data to `snippet()`, `offsets()`, and `matchinfo()` code outside this chunk, and it uses FTS write/segment helpers to read term doclists.

The tokenizer registry is shared by table creation, MATCH parsing, tokenizer test helpers, and `fts3tokenize`. `sqlite3Fts3InitHashTable()` installs SQL access to the hash table using `SQLITE_DIRECTONLY`, and later initialization code registers built-in modules such as `simple` and `porter`.

`fts4aux` and `fts3tokenize` are read-only virtual tables. They plug into the core virtual table module ABI but are diagnostic/introspection surfaces over existing FTS tables or tokenizer modules, not standalone persistent tables.

The write section links FTS xUpdate paths to shadow-table persistence. It also supplies segment-reader APIs used by query evaluation, so read and write subsystems are intentionally coupled around segment formats, prefix compression, doclist varints, and `%_segdir` metadata.

In this repository, the file is vendored under WiredTiger's third-party SQLite test tree. The relevant integration concern is preserving upstream SQLite behavior for tests that exercise SQLite as embedded code; WiredTiger code should not depend on these private FTS internals directly.

## Risks and Edge Cases

- Deferred-token decisions rely on `%_stat` doctotal data. Missing, empty, or malformed doctotal blobs produce `FTS_CORRUPT_VTAB`; external-content tables disable deferred-token optimization because index and content table consistency is not guaranteed.
- NEAR evaluation edits position lists in place and may zero unused tails. Consumers that assume position lists are immutable after doclist load would report wrong offsets or corrupt iteration.
- `sqlite3Fts3EvalPhrasePoslist()` has special OR-tree handling because the current phrase may have moved past `iPrevId` or the tree may be EOF while a descendant still has an earlier entry. It may force incremental phrases to load full doclists.
- Expression parsing is intentionally syntax-mode dependent. Legacy mode gives OR higher precedence than implicit AND and supports unary `-`; parenthesis mode enables AND/NOT and parentheses but replaces the unary-minus behavior.
- Quoted phrases cannot be column-qualified in this implementation. Only single tokens receive the `column:` prefix handling in `getNextNode()`.
- Parser depth and balancing are security-sensitive. Missing depth checks or broken balancing could allow stack exhaustion from crafted MATCH strings.
- Hash insertion has unusual return semantics: when allocation fails, it returns the new data pointer and may leave the table unchanged. Callers must compare against the inserted pointer where needed.
- The `fts3_tokenizer()` pointer interface is sensitive. The code gates registration and pointer return through database config or bound values to reduce unsafe SQL-level pointer exposure.
- The Porter tokenizer stems only ASCII alphabetic terms. Non-ASCII, digit-containing long tokens, too-short tokens, or too-long tokens fall back to copy/truncate behavior, so token equivalence is not Unicode-aware.
- The simple tokenizer explicitly rejects UTF-8 delimiter configuration and lowercases only ASCII letters.
- `fts3tokBestIndexMethod()` makes unconstrained scans prohibitively expensive and `fts3tokFilterMethod()` returns `SQLITE_ERROR` if no `input = ?` constraint is supplied.
- Pending doclists assume nondecreasing docids within a language id and flush on ordering changes. Incorrect docid ordering or missed flushes would corrupt delta-encoded doclists.
- Segment node and doclist readers rely on padding (`FTS3_NODE_PADDING`) to safely read varints near corrupt node boundaries, but still must validate suffix lengths, doclist sizes, and final terminators.
- `sqlite3Fts3ReadBlock()` reuses blob handles for performance; failing to close them at virtual-table API boundaries can hold database locks.
- Segment writer code treats non-increasing term order as corruption because prefix compression requires strictly increasing terms.

## Test Signals

Useful validation signals for this chunk include:

- FTS3/FTS4 MATCH tests for phrase, prefix, column-qualified, OR, AND, NOT, legacy unary minus, implicit AND, and `NEAR/N` queries in both ascending and descending docid modes.
- Deferred-token tests with FTS4, external-content tables, doctotal corruption, very common terms, multi-token phrases, and NEAR expressions.
- `snippet()`, `offsets()`, and `matchinfo()` tests involving OR branches, unmatched NEAR subexpressions, deferred phrases, and all-deferred phrases.
- `fts4aux` tests for exact term lookup, term range scans, hidden `languageid`, `ORDER BY term ASC`, aggregate `*` rows, per-column rows, and corrupt doclist handling.
- Parser tests using `fts3_exprtest` and `fts3_exprtest_rebalance` under `SQLITE_TEST`, including malformed quotes, mismatched parentheses, maximum depth, NEAR with non-phrase operands, token names that prefix keywords such as `ORacle`, `^` first-token syntax, and tokenizer errors.
- Hash-table tests for string and binary keys, copy-key and non-copy-key modes, insertion, replacement, deletion by NULL data, rehashing, zero-entry clear, and allocation failure.
- Tokenizer tests for `simple`, `porter`, tokenizer arguments, custom tokenizer registration through bound blobs, disabled pointer access, `fts3_tokenizer_internal_test()`, and tokenizer SQL errors.
- `fts3tokenize` virtual-table tests requiring `input = ?`, verifying token text, byte offsets, position values, tokenizer arguments, default tokenizer selection, and cursor reuse.
- Write-path tests for inserts, deletes, delete-all, external-content tables, language id changes, prefix indexes, notindexed columns, pending data flush thresholds, rowid/docid conflict handling, docsize/doctotal validation, and empty-table detection.
- Segment tests for root-only segments, multi-block segments, incremental block reads, descending pending doclists, segment sorting by term/docid/age, corrupt suffix/doclist bounds, blob-handle closure, and segment directory level allocation.
