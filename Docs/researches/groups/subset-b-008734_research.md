# subset-b-008734 research

Grouped research for SQLite FTS3/FTS4 sources under `sources/storage-engines/sqlite/ext/fts3`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_expr.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_expr.c

## Purpose

Implements the hand-written parser for FTS3/FTS4 `MATCH` query strings. It converts user query text into `Fts3Expr` trees containing phrase nodes and boolean/proximity operators, with legacy syntax support and optional parenthesized syntax controlled by `sqlite3_fts3_enable_parentheses` or `SQLITE_ENABLE_FTS3_PARENTHESIS`.

## Important APIs, types, and functions

`ParseContext` carries the tokenizer, language id, column names, default column, FTS4 feature flag, error context, and parenthesis nesting state. Public entry points are `sqlite3Fts3ExprParse()`, `sqlite3Fts3ExprFree()`, `sqlite3Fts3OpenTokenizer()`, and `sqlite3Fts3MallocZero()`. Parser internals include `getNextToken()`, `getNextString()`, `getNextNode()`, `fts3ExprParse()`, `insertBinaryOperator()`, `fts3ExprBalance()`, and `fts3ExprCheckDepth()`. Under `SQLITE_TEST`, `sqlite3Fts3ExprInitTestInterface()` registers `fts3_exprtest` and `fts3_exprtest_rebalance`.

## Control flow

Parsing repeatedly asks `getNextNode()` for the next keyword, parenthesized subexpression, quoted phrase, or tokenizer-normalized token. `getNextNode()` recognizes `OR`, `AND`, `NOT`, and `NEAR[/N]`, handles column prefixes for unquoted terms, and recurses into `fts3ExprParse()` for parentheses. `fts3ExprParse()` inserts implicit `AND` nodes, handles legacy unary `-` as a deferred `NOT` branch, rejects illegal NEAR operands, and uses precedence-aware insertion to build a tree. The public wrapper then balances `AND`/`OR` trees and enforces `SQLITE_FTS3_MAX_EXPR_DEPTH`.

## State and persistence

The file creates transient heap-owned expression trees. Phrase allocations combine `Fts3Expr`, `Fts3Phrase`, phrase-token metadata, and token text in one block where possible. No database state is persisted, but parsed expressions are later attached to `Fts3Cursor` evaluation state and freed by non-recursive traversal to avoid stack overflow.

## Dependencies and integration points

Depends on `fts3Int.h`, tokenizer modules through `sqlite3_tokenizer_module`, FTS phrase/evaluation cleanup via `sqlite3Fts3EvalPhraseCleanup()`, varint parsing for NEAR distances via `sqlite3Fts3ReadInt()`, and error formatting via `sqlite3Fts3ErrMsg()`. Integration is central to `MATCH` execution, snippet/matchinfo phrase iteration, and FTS4 first-token `^` syntax.

## Risks and test signals

Risks include tokenizer callbacks consuming quote/parenthesis delimiters, expression-depth denial of service, OOM during two-pass phrase allocation, mismatched parenthesis state, precedence differences between legacy and parenthesized modes, and non-phrase operands around `NEAR`. Test signals are `fts3_exprtest`, rebalance tests, malformed MATCH error strings, max-depth failures, prefix and column-qualified token cases, legacy `-term` behavior, and parenthesized `AND`/`NOT` syntax coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_expr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_hash.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_hash.c

## Purpose

Provides the standalone hash-table implementation used by FTS3, mainly for tokenizer module registration and lookup. It is derived from SQLite's generic hash table but scoped to FTS and supports string or binary keys.

## Important APIs, types, and functions

Public functions are `sqlite3Fts3HashInit()`, `sqlite3Fts3HashClear()`, `sqlite3Fts3HashFindElem()`, `sqlite3Fts3HashFind()`, and `sqlite3Fts3HashInsert()`. Internal helpers include `fts3StrHash()`, `fts3BinHash()`, key comparators, `ftsHashFunction()`, `ftsCompareFunction()`, `fts3Rehash()`, `fts3HashInsertElement()`, `fts3FindElementByHash()`, and `fts3RemoveElementByHash()`.

## Control flow

Initialization records key class and ownership policy. Lookup computes a raw hash and masks it by the power-of-two bucket count. Insert first searches for an existing element; if found it updates data or removes the element when `data==NULL`. New inserts lazily allocate eight buckets and double the table when the element count reaches the bucket count. Rehash rebuilds bucket chains while preserving the global doubly linked element list.

## State and persistence

The table owns bucket arrays, element nodes, and optionally key copies. It stores only in-memory process state and persists nothing to SQLite tables. `sqlite3Fts3HashClear()` returns the table to an empty state and frees copied keys.

## Dependencies and integration points

Depends on SQLite memory routines through `fts3Int.h` and the declarations in `fts3_hash.h`. The tokenizer subsystem initializes a string/copy-key hash and stores `sqlite3_tokenizer_module *` values keyed by tokenizer names. Test and virtual-table code also uses the hash to resolve tokenizer names.

## Risks and test signals

OOM semantics are subtle: insert returns the input `data` if allocation fails, which callers must treat as failure. String keys use byte-counted `strncmp()` with case-sensitive matching, so callers must pass consistent `nKey` values including the nul byte for tokenizer names. Removal must keep both bucket chains and the global list valid. Test signals come from tokenizer registration/query tests, repeated insert/delete/clear cycles, OOM paths, and hash iteration macros.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_hash.h -->
# sources/storage-engines/sqlite/ext/fts3/fts3_hash.h

## Purpose

Declares the FTS3 standalone hash-table API and the concrete `Fts3Hash` and `Fts3HashElem` layouts. The file is intentionally not fully opaque because iteration and accessor operations are implemented as macros.

## Important APIs, types, and functions

`Fts3Hash` stores key mode, key-copy policy, element count, the first element in a global list, bucket count, and bucket array. `Fts3HashElem` stores global-list links, user data, key pointer, and key length. Key classes are `FTS3_HASH_STRING` and `FTS3_HASH_BINARY`. Declared operations are `sqlite3Fts3HashInit()`, `sqlite3Fts3HashInsert()`, `sqlite3Fts3HashFind()`, `sqlite3Fts3HashClear()`, and `sqlite3Fts3HashFindElem()`, with shorthand aliases and iteration macros.

## Control flow

Clients initialize a stack or embedded `Fts3Hash`, insert keyed data, find by key, optionally iterate using `fts3HashFirst()` and `fts3HashNext()`, and clear when done. Deletion is expressed by inserting `NULL` data for a key.

## State and persistence

The header defines in-memory state only. Ownership of keys is controlled by `copyKey`; ownership of `data` always remains with the caller unless a higher-level subsystem adds its own policy.

## Dependencies and integration points

The implementation lives in `fts3_hash.c`. `fts3_tokenizer.c`, `fts3_tokenize_vtab.c`, expression test setup, and FTS module initialization use this API to publish and resolve tokenizer implementations.

## Risks and test signals

Because structure fields are visible, misuse can corrupt internal invariants. Macro iteration assumes the table is not mutated unsafely while walking it. Tests that register tokenizers, query unknown tokenizers, clear module state, and run under OOM are the practical signals for this header/API contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_icu.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_icu.c

## Purpose

Implements the optional ICU-backed FTS3 tokenizer, compiled only with `SQLITE_ENABLE_ICU`. It uses ICU word-boundary analysis and Unicode case folding to tokenize multilingual input.

## Important APIs, types, and functions

`IcuTokenizer` stores the base tokenizer and optional locale string. `IcuCursor` stores an ICU `UBreakIterator`, UTF-16 input copy, UTF-8 offset map, output buffer, and token counter. Tokenizer callbacks are `icuCreate()`, `icuDestroy()`, `icuOpen()`, `icuClose()`, and `icuNext()`. `sqlite3Fts3IcuTokenizerModule()` returns the static module.

## Control flow

Creation copies the optional locale. Opening a cursor converts UTF-8 input to folded UTF-16 code units using ICU `U8_NEXT`, `u_foldCase()`, and `U16_APPEND`, while recording original UTF-8 byte offsets. It then opens an ICU word break iterator over the UTF-16 buffer. `icuNext()` advances to the next non-whitespace word boundary range, converts that UTF-16 token back to UTF-8 with `u_strToUTF8()`, grows the output buffer if needed, and returns token text and original byte offsets.

## State and persistence

All state is per-tokenizer or per-cursor heap state. No SQLite tables are modified. The cursor owns the break iterator, UTF-16 input, offset array, and UTF-8 output buffer until `icuClose()`.

## Dependencies and integration points

Depends on ICU headers `ubrk.h`, `ucol.h`, `ustring.h`, `utf16.h`, and the common FTS tokenizer ABI from `fts3_tokenizer.h`. It integrates through tokenizer registration in FTS module setup and can be used by expression parsing, indexing, snippet generation, and offsets wherever a tokenizer is required.

## Risks and test signals

Build risk is high because this code is excluded unless ICU support is enabled. Runtime risks include invalid UTF-8 conversion to replacement characters, ICU status failures, offset mapping around supplementary codepoints, whitespace-only boundary ranges, and allocation loops around `u_strToUTF8()`. Signals are tokenizer tests with locale arguments, multilingual text, folded case, byte-offset assertions, and ICU-enabled build coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_icu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_porter.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_porter.c

## Purpose

Implements the built-in Porter stemming tokenizer. It tokenizes ASCII-like words, folds ASCII case, and stems English terms for FTS matching while leaving unsupported or long tokens to a copy/truncation fallback.

## Important APIs, types, and functions

`porter_tokenizer` is the tokenizer instance and `porter_tokenizer_cursor` tracks input, offsets, token index, and reusable output buffer. Tokenizer callbacks are `porterCreate()`, `porterDestroy()`, `porterOpen()`, `porterClose()`, and `porterNext()`. Stemming helpers include `isConsonant()`, `isVowel()`, `m_gt_0()`, `m_eq_1()`, `m_gt_1()`, `hasVowel()`, `doubleConsonant()`, `star_oh()`, `stem()`, `copy_stemmer()`, and `porter_stemmer()`. `sqlite3Fts3PorterTokenizerModule()` exports the module.

## Control flow

`porterNext()` scans past delimiters, collects a token, grows `zToken` as needed, and passes the raw token to `porter_stemmer()`. The stemmer reverses lower-case ASCII letters into a fixed buffer, applies Porter steps 1a through 5b using reversed suffix matching, then reverses the stem back. Tokens that are too short, too long, contain digits, or contain non-ASCII letters fall back to case-folded copying and possible truncation.

## State and persistence

State is transient tokenizer/cursor memory only. Index persistence is indirect: because indexed terms are stemmed, changing this algorithm or delimiter rules would require reindexing existing FTS data.

## Dependencies and integration points

Uses the FTS tokenizer ABI and SQLite allocation APIs. It is registered as a tokenizer module and is consumed by FTS table creation, query parsing, indexing, snippets, offsets, and `fts3tokenize`.

## Risks and test signals

Risks include English-specific stemming surprises, fixed-size reverse buffer boundaries, inconsistent handling of high-bit UTF-8 bytes as token characters but not stemmable letters, and term-collision effects from fallback truncation. Test signals are known Porter stem output, offset preservation after stemming, delimiter behavior, long-token truncation, non-ASCII fallback, and tokenizer-module lifecycle tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_porter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_snippet.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_snippet.c

## Purpose

Implements FTS3/FTS4 auxiliary result functions `snippet()`, `offsets()`, and `matchinfo()`, plus shared phrase iteration and matchinfo-buffer caching. It turns expression evaluation doclists and row text into user-visible highlight snippets, byte offsets, and ranking/statistics blobs.

## Important APIs, types, and functions

Public entry points are `sqlite3Fts3Snippet()`, `sqlite3Fts3Offsets()`, `sqlite3Fts3Matchinfo()`, `sqlite3Fts3ExprIterate()`, and `sqlite3Fts3MIBufferFree()`. Key types include `LoadDoclistCtx`, `SnippetIter`, `SnippetPhrase`, `SnippetFragment`, `MatchInfo`, `MatchinfoBuffer`, `StrBuffer`, `LcsIterator`, `TermOffset`, and `TermOffsetCtx`. Important helpers include `fts3BestSnippet()`, `fts3SnippetText()`, `fts3SnippetShift()`, `fts3MatchinfoValues()`, `fts3GetMatchinfo()`, `fts3MatchinfoLcs()`, `fts3ExprLHitGather()`, and `fts3ColumnlistCount()`.

## Control flow

Phrase iteration skips the right side of `NOT` expressions. Snippet generation loads phrase doclists, gathers per-column position lists, scores candidate token windows by phrase coverage and hit count, expands up to four fragments, then retokenizes row text to emit highlighted text and ellipses. Offsets count query terms, initializes position iterators per column, retokenizes stored column text, and appends `column term start length` tuples. Matchinfo validates the format string, allocates or reuses a cached two-slot buffer, computes global fields once per query, and fills row-local fields for each current row.

## State and persistence

Most state is per-call heap memory, but `Fts3Cursor.pMIBuffer`, `nPhrase`, and `isMatchinfoNeeded` cache matchinfo state across rows. The code reads persisted FTS segment/doclist data, `%_docsize`, `%_stat`/doctotal records, and content columns through the current cursor statement, but does not write persistent state.

## Dependencies and integration points

Depends heavily on FTS evaluation APIs from `fts3Int.h`: `sqlite3Fts3EvalPhrasePoslist()`, `sqlite3Fts3EvalPhraseStats()`, `sqlite3Fts3EvalTestDeferred()`, `sqlite3Fts3SegmentsClose()`, `sqlite3Fts3SelectDoctotal()`, `sqlite3Fts3SelectDocsize()`, `sqlite3Fts3MsrCancel()`, and FTS varint helpers. It uses the table tokenizer to map token positions back to source byte offsets.

## Risks and test signals

Risks include corrupt doclists causing invalid varint walks, matchinfo format restrictions differing between FTS3 and FTS4, deferred-token approximations, stale cached global matchinfo after format changes, tokenizer offset mismatches, snippet masks limited to 64 tokens/phrases modulo 64, and contentless-table offset corruption detection. Test signals include exact `snippet()`, `offsets()`, and `matchinfo()` outputs, `pcx` default behavior, `l`, `a`, `n`, `s`, `x`, `y`, and `b` flags, deferred-token queries, NULL columns, corrupt-index tests, and multi-column/multi-fragment snippets.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_snippet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_term.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_term.c

## Purpose

Defines the test-only `fts4term` virtual table module, which exposes raw full-text index terms and their docid/column/position occurrences. It is not production FTS code and is compiled under `SQLITE_TEST`.

## Important APIs, types, and functions

`Fts3termTable` stores a synthetic `Fts3Table` and index number. `Fts3termCursor` embeds `Fts3MultiSegReader`, `Fts3SegFilter`, EOF state, doclist pointer, rowid, docid, column, and position. Virtual-table callbacks are `fts3termConnectMethod()`, `fts3termDisconnectMethod()`, `fts3termBestIndexMethod()`, `fts3termOpenMethod()`, `fts3termCloseMethod()`, `fts3termFilterMethod()`, `fts3termNextMethod()`, `fts3termEofMethod()`, `fts3termColumnMethod()`, and `fts3termRowidMethod()`. `sqlite3Fts3InitTerm()` registers the module as `fts4term`.

## Control flow

Connect expects the target FTS table name and optional index number, declares schema `term, docid, col, pos`, and builds enough `Fts3Table` metadata to read segment tables. Filtering initializes a full segment scan requiring positions. `fts3termNextMethod()` steps segment readers term by term and decodes the current doclist: docid deltas, column markers, and position deltas are translated to output columns.

## State and persistence

The module owns no persistent table. It reads existing FTS segment state through the synthetic table object and maintains cursor-local decoded position state. Disconnect finalizes prepared statements and frees synthetic metadata.

## Dependencies and integration points

Depends on segment-reader APIs such as `sqlite3Fts3SegReaderCursor()`, `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, `sqlite3Fts3SegReaderFinish()`, `sqlite3Fts3SegmentsClose()`, and FTS varint decoding. It integrates with the SQLite virtual-table API and the Tcl/SQLite test suite.

## Risks and test signals

Risks include malformed doclists, incorrect synthetic `Fts3Table` fields, index-number mismatches for prefix indexes, and exposing implementation ordering assumptions. Test signals are ordered `term, docid, col, pos` scans, prefix-index constructor arguments, segment-reader cleanup, and corrupt-index behavior under debug tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_term.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_test.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_test.c

## Purpose

Provides Tcl-only FTS3/FTS4 test helpers. It validates NEAR matching logic, exposes knobs for incremental doclist loading, returns a version-1 tokenizer for language-id tests, tests FTS varints, and toggles debug corruption assertions.

## Important APIs, types, and functions

NEAR test structures are `NearDocument`, `NearToken`, and `NearPhrase`, with helpers `nm_phrase_match()`, `nm_near_chain()`, and `nm_match_count()`. Tcl commands include `fts3_near_match_cmd()`, `fts3_configure_incr_load_cmd()`, `fts3_test_tokenizer_cmd()`, `fts3_test_varint_cmd()`, and `fts3_may_be_corrupt()`. The test tokenizer uses `test_tokenizer`, `test_tokenizer_cursor`, and callbacks including `testTokenizerLanguage()`. `Sqlitetestfts3_Init()` registers all commands.

## Control flow

`fts3_near_match` parses document and expression Tcl lists, builds phrase arrays, and checks phrase occurrences plus forward/reverse NEAR chains. The incremental-load command returns current global tuning values and optionally overwrites them. The test tokenizer emits alphabetic ASCII tokens, lowercasing for even language ids, preserving case for odd ids, and returning an error for language ids >=100. Varint testing round-trips values through FTS varint encoders/decoders.

## State and persistence

No database state is persisted. The file mutates test-only globals `test_fts3_node_chunksize`, `test_fts3_node_chunk_threshold`, and, under debug, `sqlite3_fts3_may_be_corrupt`. Tcl allocations are command-local, and tokenizer cursor buffers are heap-owned.

## Dependencies and integration points

Depends on `tclsqlite.h`, `fts3Int.h`, SQLite FTS varint helpers, and the tokenizer ABI. It integrates only into testfixture builds with `SQLITE_TEST` and FTS3/FTS4 enabled.

## Risks and test signals

Risks are mostly test-harness drift: NEAR semantics here must match production evaluation, tokenizer language-id behavior must exercise `xLanguageid`, and global tuning changes must be restored by tests. Signals are Tcl command results, phrase-count variable output, varint round-trip failures, language-id error propagation, and debug corruption assertion toggling.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_tokenize_vtab.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_tokenize_vtab.c

## Purpose

Implements the `fts3tokenize` virtual table, a diagnostic table-valued interface that tokenizes an input string with a selected FTS3 tokenizer and returns one row per token.

## Important APIs, types, and functions

`Fts3tokTable` stores the tokenizer module and tokenizer instance. `Fts3tokCursor` stores copied input text, tokenizer cursor, current rowid, token text, byte offsets, and token position. Important helpers are `fts3tokQueryTokenizer()` and `fts3tokDequoteArray()`. Virtual-table callbacks include connect/create, disconnect/destroy, best-index, open, reset/close, filter, next, eof, column, and rowid. `sqlite3Fts3InitTok()` registers module name `fts3tokenize`.

## Control flow

Connect declares schema `input, token, start, end, position`, dequotes tokenizer arguments, resolves the tokenizer in the shared hash, and creates a tokenizer instance. Best-index strongly prefers an equality constraint on `input`. Filter copies the bound input into nul-terminated memory, opens a tokenizer cursor, and immediately advances to the first token. Next calls tokenizer `xNext()` and resets cursor state on `SQLITE_DONE`.

## State and persistence

The virtual table has no persistent backing storage. Table state owns one tokenizer instance for the vtab lifetime. Cursor state owns input copies and tokenizer cursors for each scan.

## Dependencies and integration points

Depends on `Fts3Hash` tokenizer registry, `sqlite3Fts3Dequote()`, tokenizer modules, and SQLite virtual-table APIs. It is registered from FTS initialization and shares tokenizer implementations with real FTS tables.

## Risks and test signals

Risks include forgetting the required `input = ?` constraint, tokenizer lifetime leaks, dequoting argument mismatches with `CREATE VIRTUAL TABLE`, and incorrect byte offsets for tokenizers with Unicode behavior. Test signals are `SELECT * FROM fts3tokenize(...) WHERE input=?` rows, default `simple` tokenizer behavior, tokenizer-argument quoting, unknown tokenizer errors, EOF/reset behavior, and planner use of the equality constraint.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_tokenize_vtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer.c

## Purpose

Implements generic tokenizer registration, tokenizer-spec parsing, and SQL access to the tokenizer hash via `fts3_tokenizer()`. It is the bridge between FTS table definitions, tokenizer modules, and optional extension/test registration.

## Important APIs, types, and functions

Public/internal entry points include `sqlite3Fts3InitTokenizer()`, `sqlite3Fts3InitHashTable()`, `sqlite3Fts3IsIdChar()`, and `sqlite3Fts3NextToken()`. The scalar function implementation is `fts3TokenizerFunc()`. Test-only helpers include `testFunc()`, `registerTokenizer()`, `queryTokenizer()`, and `intTestFunc()`.

## Control flow

`sqlite3Fts3InitTokenizer()` copies the tokenizer specification string, extracts and dequotes the tokenizer name with `sqlite3Fts3NextToken()`, looks up the module in `Fts3Hash`, parses remaining dequoted arguments, calls module `xCreate()`, and sets the tokenizer's module pointer. `fts3TokenizerFunc()` either looks up a tokenizer pointer by name or stores a supplied pointer blob, subject to `SQLITE_DBCONFIG_ENABLE_FTS3_TOKENIZER` or bound-parameter safety checks. `sqlite3Fts3InitHashTable()` registers one- and two-argument SQL functions and test functions.

## State and persistence

The shared tokenizer hash is in-memory per database/FTS initialization. Created tokenizer instances are heap objects owned by FTS table or caller lifecycle. No persistent state is written, but tokenizer choice affects persisted index terms, so changes require reindexing.

## Dependencies and integration points

Depends on `Fts3Hash`, tokenizer ABI, `sqlite3Fts3Dequote()`, `sqlite3Fts3ErrMsg()`, SQLite scalar-function APIs, and DB config `SQLITE_DBCONFIG_ENABLE_FTS3_TOKENIZER`. The expression parser, indexer, snippet/offset logic, `fts3tokenize`, and tests all call through this setup.

## Risks and test signals

The pointer-returning SQL function is intentionally guarded because exposing raw pointers is unsafe. Other risks include tokenizer-spec parsing around quoted identifiers, argument allocation failures, unknown tokenizer errors, and module `xCreate()` returning success without a tokenizer. Test signals are tokenizer registration/query tests, disabled `fts3_tokenizer()` behavior, bound-parameter exceptions, tokenizer test output, and internal README example validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer.h -->
# sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer.h

## Purpose

Defines the stable FTS3 tokenizer ABI used by built-in tokenizers, optional external tokenizers, and FTS query/index/snippet code.

## Important APIs, types, and functions

Declares `sqlite3_tokenizer_module`, `sqlite3_tokenizer`, and `sqlite3_tokenizer_cursor`. Module callbacks are `xCreate`, `xDestroy`, `xOpen`, `xClose`, `xNext`, and version-1 `xLanguageid`. The base tokenizer stores `pModule`; the base cursor stores `pTokenizer`. The header also declares test helper symbols `fts3_global_term_cnt()` and `fts3_term_cnt()`.

## Control flow

An FTS table resolves a module, calls `xCreate()` with tokenizer arguments, and later opens cursors with `xOpen()` for specific input buffers. `xNext()` returns normalized token text, byte offsets in the original input, and token position until `SQLITE_DONE`. If `iVersion>=1`, FTS may call `xLanguageid()` after opening the cursor.

## State and persistence

The ABI itself stores no data beyond base struct pointers. Tokenizer implementations extend the structs with private state. The normalized tokens produced through this interface are persisted indirectly in FTS indexes and used for query normalization.

## Dependencies and integration points

Includes `sqlite3.h` for result codes and integer types. Implemented by `fts3_tokenizer1.c`, `fts3_porter.c`, `fts3_unicode.c`, `fts3_icu.c`, and test tokenizers. Consumed by parser, index writer, snippet/offset code, `fts3tokenize`, and tokenizer registration.

## Risks and test signals

The ABI requires input buffers to remain valid until `xClose()` and returned token buffers to remain valid only until next `xNext()` or close. Incorrect offsets break snippets and offsets. Version negotiation for `xLanguageid()` must be respected. Test signals are lifecycle tests, tokenizer output tests, language-id behavior, and offset-sensitive snippets.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer1.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer1.c

## Purpose

Implements the built-in `simple` tokenizer. It splits text on ASCII delimiters, lowercases ASCII uppercase letters, and leaves non-delimiter bytes otherwise unchanged.

## Important APIs, types, and functions

`simple_tokenizer` stores the base tokenizer and a 128-byte delimiter table. `simple_tokenizer_cursor` tracks input pointer, byte length, offset, token index, reusable token buffer, and buffer size. Tokenizer callbacks are `simpleCreate()`, `simpleDestroy()`, `simpleOpen()`, `simpleClose()`, and `simpleNext()`. `sqlite3Fts3SimpleTokenizerModule()` exports the module.

## Control flow

Creation either marks caller-supplied ASCII delimiters from the second tokenizer argument or defaults all non-alphanumeric ASCII bytes to delimiters. Open records the input buffer and length. `simpleNext()` skips delimiters, scans the next non-delimiter byte span, grows its output buffer, ASCII-folds the token into that buffer, and returns byte offsets and increasing token positions.

## State and persistence

Tokenizer delimiter configuration is per tokenizer instance. Cursor token buffers are transient. Persisted index terms depend on delimiter configuration and case folding, so changing tokenizer arguments after indexing requires reindexing.

## Dependencies and integration points

Uses the common tokenizer ABI and SQLite allocation. It is the default tokenizer for many FTS3 paths and is also used by tokenizer tests and `fts3tokenize`.

## Risks and test signals

Risks include lack of UTF-8-aware case folding, unsupported high-bit delimiter arguments, embedded nul or byte-length assumptions, and index incompatibility if delimiter rules change. Test signals are token boundary output, ASCII lowercasing, custom delimiter rejection for UTF-8 bytes, offsets, and default tokenizer behavior when no tokenizer is specified.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_tokenizer1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_unicode.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_unicode.c

## Purpose

Implements the built-in `unicode61`-style tokenizer for FTS3/FTS4 when Unicode tokenization is not disabled. It performs UTF-8 decoding, Unicode alphanumeric classification, case folding, optional diacritic removal, and configurable token/separator exceptions.

## Important APIs, types, and functions

`unicode_tokenizer` stores diacritic-removal mode and sorted exception codepoints. `unicode_cursor` stores input bytes, current offset, token index, and reusable UTF-8 output buffer. Key functions are `unicodeCreate()`, `unicodeDestroy()`, `unicodeOpen()`, `unicodeClose()`, `unicodeNext()`, `unicodeAddExceptions()`, `unicodeIsException()`, `unicodeIsAlnum()`, and `sqlite3Fts3UnicodeTokenizer()`.

## Control flow

Creation parses arguments `remove_diacritics=0/1/2`, `tokenchars=...`, and `separators=...`, building a sorted exception list that inverts the generated Unicode alnum classifier. `unicodeNext()` scans to the next token character, then reads token characters and combining diacritics with `READ_UTF8`, folds each codepoint through `sqlite3FtsUnicodeFold()`, optionally drops standalone diacritics, writes UTF-8 with `WRITE_UTF8`, and returns original byte offsets.

## State and persistence

Tokenizer options are per table tokenizer instance. Cursor state and buffers are transient. Persisted FTS index terms depend on Unicode tables, diacritic mode, and exception arguments.

## Dependencies and integration points

Depends on generated helpers in `fts3_unicode2.c`: `sqlite3FtsUnicodeIsalnum()`, `sqlite3FtsUnicodeIsdiacritic()`, and `sqlite3FtsUnicodeFold()`. Uses the tokenizer ABI and SQLite memory routines. It integrates as a tokenizer module for indexing, querying, snippets, offsets, and `fts3tokenize`.

## Risks and test signals

Risks include invalid UTF-8 handling, changes to generated Unicode tables, duplicate exception insertion, ignoring standalone diacritic exceptions, buffer growth failures, and byte-offset correctness for multibyte input. Test signals are Unicode token boundaries, case folding, diacritic modes 0/1/2, tokenchars/separators options, malformed UTF-8, and snippet/offset behavior over multibyte text.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_unicode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_unicode2.c -->
# sources/storage-engines/sqlite/ext/fts3/fts3_unicode2.c

## Purpose

Contains machine-generated Unicode classification, diacritic, and case-folding tables used by the Unicode tokenizer. The file explicitly says not to edit it by hand.

## Important APIs, types, and functions

Public functions are `sqlite3FtsUnicodeIsalnum()`, `sqlite3FtsUnicodeIsdiacritic()`, and `sqlite3FtsUnicodeFold()`. Internal `remove_diacritic()` maps many Latin lowercase diacritic codepoints to ASCII base letters. The implementation uses compact range tables and binary searches.

## Control flow

`sqlite3FtsUnicodeIsalnum()` handles ASCII with bitmasks and non-ASCII by finding the last generated non-alnum range not greater than the target codepoint. `sqlite3FtsUnicodeIsdiacritic()` checks a compact mask for combining marks U+0300 through U+0331. `sqlite3FtsUnicodeFold()` first applies ASCII or generated Unicode lowercase mappings, handles a supplementary Deseret range, and then optionally calls `remove_diacritic()`. Diacritic mode 2 enables mappings marked complex that mode 1 preserves.

## State and persistence

The file has only static read-only tables. It persists nothing directly, but table contents determine normalized tokens stored in FTS indexes. Regenerating against a different Unicode database can change query/index compatibility.

## Dependencies and integration points

Compiled when Unicode FTS3 support is enabled. Consumed by `fts3_unicode.c` for token boundary classification, combining-mark treatment, and token normalization. Generated from Unicode data files under the `unicode/` directory according to comments and tool scripts.

## Risks and test signals

Risks include stale generated data, binary-search boundary mistakes, differing behavior for complex diacritic mappings, undefined behavior for negative codepoints, and index drift if tables change. Test signals are generated-table conformance tests, known fold/diacritic examples, ASCII fast-path coverage, combining-diacritic handling, and tokenizer regression tests over multilingual samples.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts3/fts3_unicode2.c -->
