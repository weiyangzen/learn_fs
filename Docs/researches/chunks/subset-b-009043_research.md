# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 234636-242624

## Purpose

This chunk bridges the end of SQLite's session extension rebaser implementation into the beginning and early middle of the FTS5 amalgamated module. In the vendored SQLite source used by WiredTiger tests, it covers:

- The public `sqlite3rebaser_*()` API and `sqlite3session_config()` tail from `sqlite3session.c`.
- The FTS5 public extension header (`fts5.h`): auxiliary-function APIs, tokenizer APIs, synonym semantics, and the `fts5_api` registration surface.
- The FTS5 internal interface header (`fts5Int.h`): shared types, constants, and prototypes connecting config, buffer, index, hash, storage, expression, tokenizer, vocab, and unicode modules.
- The generated Lemon parser for FTS5 MATCH expressions.
- Built-in FTS5 auxiliary functions: `highlight()`, `snippet()`, `bm25()`, and `fts5_get_locale()`.
- Shared FTS5 buffer, position-list, malloc/string, and term-set helpers.
- FTS5 table configuration parsing and loading from `%_config`.
- The first large section of the FTS5 expression engine: MATCH tokenization/parsing, phrase/NEAR/column-set structures, iterator initialization, rowid set logic for TERM/STRING/AND/OR/NOT nodes, and parser construction of phrases and colsets.

This is not WiredTiger storage-engine code directly. It is a third-party SQLite amalgamation under `test/3rdparty`, so its main role in this repository is preserving SQLite behavior for tests or tools that compile this copy.

## Important APIs, Types, and Functions

Session/rebaser tail:

- `sqlite3rebaser_create()` allocates and zeroes a `sqlite3_rebaser`.
- `sqlite3rebaser_configure()` reads a rebase changeset with `sqlite3changeset_start()` and folds it into `p->grp` with `sessionChangesetToHash()`.
- `sqlite3rebaser_rebase()` and `sqlite3rebaser_rebase_strm()` run `sessionRebase()` over memory-backed or streaming changeset input.
- `sqlite3rebaser_delete()` releases table metadata, record buffers, and the rebaser itself.
- `sqlite3session_config()` currently handles `SQLITE_SESSION_CONFIG_STRMSIZE`, updating and returning `sessions_strm_chunk_size`; unknown operations return `SQLITE_MISUSE`.

FTS5 public extension API:

- `Fts5ExtensionApi` is the auxiliary-function callback table. It exposes query/row metadata (`xColumnCount`, `xRowCount`, `xColumnTotalSize`, `xColumnSize`, `xColumnText`, `xRowid`), match detail APIs (`xPhraseCount`, `xPhraseSize`, `xInstCount`, `xInst`, phrase iterators), query re-execution (`xQueryPhrase`), auxdata (`xSetAuxdata`, `xGetAuxdata`), token access (`xQueryToken`, `xInstToken`), locale lookup (`xColumnLocale`), and locale-aware tokenization (`xTokenize_v2`).
- `Fts5PhraseIter` stores opaque position-list iteration pointers for phrase/column iteration APIs.
- `fts5_extension_function` is the ABI for custom FTS5 auxiliary functions.
- `fts5_tokenizer_v2` is the modern tokenizer ABI, including locale parameters in `xTokenize()`. `fts5_tokenizer` is the older ABI without locale support.
- `FTS5_TOKENIZE_QUERY`, `FTS5_TOKENIZE_PREFIX`, `FTS5_TOKENIZE_DOCUMENT`, `FTS5_TOKENIZE_AUX`, and `FTS5_TOKEN_COLOCATED` define tokenizer request and synonym-output flags.
- `fts5_api` registers or looks up tokenizers and auxiliary functions, including v2 tokenizer variants.

FTS5 internal shared types and constants:

- `Fts5Config` captures parsed `CREATE VIRTUAL TABLE` options and loaded `%_config` values: database/table names, columns, unindexed flags, prefix indexes, content mode, content rowid, columnsize, tokendata, locale, detail mode, tokenizer config, rank config, automerge/crisismerge/usermerge/hashsize/page-size settings, secure-delete, delete-merge, and prefix-insttoken.
- `Fts5TokenizerConfig` stores the tokenizer object/API, tokenizer arguments, trigram pattern mode, and current locale.
- `Fts5Colset` is an ordered set of searchable columns used by expression evaluation and index queries.
- `Fts5Buffer` is the module's growable byte buffer used by config SQL strings, position lists, and serialized data.
- `Fts5PoslistReader`, `Fts5PoslistWriter`, and `Fts5LookaheadReader` decode and encode FTS5 position lists.
- `Fts5IndexIter` exposes an index iterator's current rowid, position-list blob, size, and EOF flag.
- `Fts5Table` binds the virtual table shell to an `Fts5Config` and `Fts5Index`.
- `Fts5Expr`, `Fts5ExprNode`, `Fts5ExprTerm`, `Fts5ExprPhrase`, `Fts5ExprNearset`, and `Fts5Parse` define parsed MATCH expressions and their runtime iterator state.

Key FTS5 helper functions in this chunk:

- Parser entry points: `sqlite3Fts5ExprNew()`, `sqlite3Fts5ExprPattern()`, `sqlite3Fts5ExprAnd()`, `sqlite3Fts5ExprFree()`, `sqlite3Fts5ExprClonePhrase()`.
- Expression iteration: `sqlite3Fts5ExprFirst()`, `sqlite3Fts5ExprNext()`, `sqlite3Fts5ExprEof()`, `sqlite3Fts5ExprRowid()`, `fts5ExprNodeFirst()`, `fts5ExprNodeNext_TERM()`, `fts5ExprNodeNext_STRING()`, `fts5ExprNodeNext_OR()`, `fts5ExprNodeNext_AND()`, `fts5ExprNodeNext_NOT()`.
- Phrase and NEAR matching: `fts5ExprPhraseIsMatch()`, `fts5ExprNearIsMatch()`, `fts5ExprNearTest()`, `fts5ExprNearInitAll()`, `fts5ExprSynonymList()`, `fts5ExprSynonymRowid()`, `fts5ExprSynonymAdvanceto()`.
- Parse actions/helpers: `fts5ExprGetToken()`, `sqlite3Fts5ParseTerm()`, `fts5ParseTokenize()`, `sqlite3Fts5ParseNearset()`, `sqlite3Fts5ParseSetCaret()`, `sqlite3Fts5ParseNear()`, `sqlite3Fts5ParseSetDistance()`, `sqlite3Fts5ParseColset()`, `sqlite3Fts5ParseColsetInvert()`, `sqlite3Fts5ParseSetColset()`.
- Config parsing/loading: `sqlite3Fts5ConfigParse()`, `fts5ConfigParseSpecial()`, `fts5ConfigParseColumn()`, `fts5ConfigMakeExprlist()`, `sqlite3Fts5ConfigDeclareVtab()`, `sqlite3Fts5Tokenize()`, `sqlite3Fts5ConfigParseRank()`, `sqlite3Fts5ConfigSetValue()`, `sqlite3Fts5ConfigLoad()`, `sqlite3Fts5ConfigErrmsg()`, `sqlite3Fts5ConfigFree()`.
- Built-ins: `fts5HighlightFunction()`, `fts5SnippetFunction()`, `fts5Bm25Function()`, `fts5GetLocaleFunction()`, and `sqlite3Fts5AuxInit()`.
- Buffer/poslist utilities: `sqlite3Fts5BufferSize()`, `sqlite3Fts5BufferAppendVarint()`, `sqlite3Fts5BufferAppendBlob()`, `sqlite3Fts5BufferAppendString()`, `sqlite3Fts5BufferAppendPrintf()`, `sqlite3Fts5Mprintf()`, `sqlite3Fts5BufferFree()`, `sqlite3Fts5BufferSet()`, `sqlite3Fts5PoslistNext64()`, `sqlite3Fts5PoslistReaderInit()`, `sqlite3Fts5PoslistWriterAppend()`, `sqlite3Fts5PoslistSafeAppend()`, `sqlite3Fts5MallocZero()`, and `sqlite3Fts5Strndup()`.
- Term-set integrity support: `sqlite3Fts5TermsetNew()`, `sqlite3Fts5TermsetAdd()`, and `sqlite3Fts5TermsetFree()`.

The final line in this assigned range is the opening of `fts5ExprAssignXNext()`. Its switch body and downstream parse-node construction continue in the following chunk.

## Control Flow

The session rebaser path is short and linear. A rebaser is allocated zero-filled, configured by converting a rebase changeset into a hash/group representation, then used to transform an input changeset through `sessionRebase()`. The streaming variant substitutes `sqlite3changeset_start_strm()` and an output callback. All iterator paths finalize the changeset iterator when initialization succeeded.

FTS5 module initialization begins by exposing the public extension ABI, then declaring internal cross-module contracts. The code in this chunk is organized by amalgamated source file: public API declarations, internal declarations, generated parser code, built-in auxiliary functions, generic helpers, config parsing, and expression evaluation.

The generated Lemon parser takes tokens from `fts5ExprGetToken()` and reduces them into expression nodes, nearsets, phrases, colsets, and prefix flags. Important grammar actions include:

- `expr AND expr`, `expr OR expr`, and `expr NOT expr` reduce into internal expression nodes via `sqlite3Fts5ParseNode()`.
- Adjacent `exprlist cnearset` reduces through `sqlite3Fts5ParseImplicitAnd()`.
- `colset : expr` or `colset : nearset` applies a column filter through `sqlite3Fts5ParseSetColset()`.
- `NEAR(...)` validates the `NEAR` keyword, parses optional distance, and stores it on a nearset.
- `phrase PLUS STRING star_opt` appends a tokenized term to an existing phrase.
- `STRING star_opt` creates a new phrase, optionally marking its final term as a prefix query.

`sqlite3Fts5ExprNew()` owns MATCH expression compilation. It allocates a Lemon parser, feeds tokens until `FTS5_EOF` or parse error, applies an implicit left-hand-column filter when `iCol` names a real table column, and wraps the parse tree and phrase array into an `Fts5Expr`.

`sqlite3Fts5ExprPattern()` is a special trigram-tokenizer path for LIKE/GLOB planning. It extracts literal spans of at least three UTF-8 characters from the pattern, quotes them into a generated MATCH expression, and compiles that expression as a superset filter. For reduced-detail tables it may force phrase-to-AND behavior or disable the column filter.

Expression iteration is tree-driven:

- `sqlite3Fts5ExprFirst()` binds an `Fts5Index`, records rowid order, initializes all expression-node iterators with `fts5ExprNodeFirst()`, optionally seeks to `iFirst`, then skips `bNomatch` pseudo-matches.
- `sqlite3Fts5ExprNext()` advances the root with its `xNext` method until a real match or EOF, then enforces the caller's rowid boundary.
- TERM nodes use a single index iterator and can point phrase position lists directly at index iterator data in `detail=full`.
- STRING nodes coordinate multiple term iterators, synonyms, phrase adjacency, first-token constraints, NEAR distance, and column filters before admitting a row.
- OR nodes choose the earliest child in iteration order, preferring real matches over `bNomatch` rows for equal rowids.
- AND nodes repeatedly advance lagging children until all children land on the same rowid, carrying child `bNomatch` state.
- NOT nodes advance the right child to the left child's rowid and skip left-side rows suppressed by a matching right side.

The auxiliary functions run through the `Fts5ExtensionApi` rather than direct internal structures. `highlight()` obtains column text, locale, and coalesced match instances, then re-tokenizes the column to splice open/close markers around token ranges. `snippet()` scores possible windows around phrase instances and sentence starts, then reuses the highlight callback over the chosen window. `bm25()` lazily allocates per-query data in FTS5 auxdata, computes row count, total token count, per-phrase document frequency through `xQueryPhrase()`, then scores each row using per-column weights. `fts5_get_locale()` validates a single integer column argument and returns `xColumnLocale()` output.

Config parsing is also staged. `sqlite3Fts5ConfigParse()` allocates a config object, pre-allocates column/unindexed arrays, parses each virtual-table argument as either an option (`name=value`) or a column declaration, applies option-specific validators, enforces cross-option constraints, fills default content table/rowid names, and builds `zContentExprlist`. `sqlite3Fts5ConfigLoad()` later reads runtime options from `%_config`, applies defaults before scanning rows, validates the FTS5 file-format version, and stores an `iCookie` snapshot.

## State and Persistence Behavior

The rebaser stores persistent-in-object state in `sqlite3_rebaser.grp`: configured table records and a reusable record buffer. `sqlite3rebaser_configure()` can be called more than once, merging changeset conflict/rebase data into that group until `sqlite3rebaser_delete()` frees it.

FTS5 configuration state is split between parse-time virtual-table schema options and persisted `%_config` table values. Parse-time options determine columns, content mode, tokenizer arguments, prefix indexes, locale/tokendata/detail behavior, content rowid, and generated content select lists. `%_config` values determine mutable runtime/index settings such as page size, automerge, usermerge, crisismerge, hashsize, rank function, secure-delete, delete-merge, and insttoken behavior. `sqlite3Fts5ConfigLoad()` resets defaults before loading persisted values, so missing keys use compile-time defaults.

FTS5 content persistence is represented in this chunk by names and SQL fragments, not by the table creation code itself. `zContent` may identify `%_content`, `%_docsize`, an external content table, or no content table depending on `content=`, `columnsize=`, and contentless options. `zContentExprlist` is built as a SQL expression list selecting rowid and columns from alias `T`, with `NULL` placeholders for non-stored columns and locale columns when appropriate.

Expression state is mostly in-memory and iterator-local:

- Each `Fts5ExprTerm` owns token text, prefix/first flags, optional synonym list, and an `Fts5IndexIter`.
- Each `Fts5ExprPhrase` owns a current-row position-list buffer unless it can alias index iterator data for simple TERM matches.
- Each `Fts5ExprNearset` owns phrase pointers, a NEAR distance, and optional colset.
- Each `Fts5ExprNode` owns rowid/EOF/nomatch state plus its child pointers or nearset.
- `Fts5Expr` owns the parse root and phrase pointer array.

Position lists are delta-varint encoded with column markers. `sqlite3Fts5PoslistNext64()` decodes entries into `(column << 32) + offset`, treating certain malformed records as EOF/corruption-tolerant stop points. Writers preserve sorted order and column transitions through `sqlite3Fts5PoslistSafeAppend()`.

Auxiliary-function state may persist for the duration of one MATCH query through FTS5 auxdata. `bm25()` uses `xGetAuxdata()`/`xSetAuxdata()` to cache `Fts5Bm25Data`, including IDF values and reusable frequency storage. `highlight()` and `snippet()` allocate only per-call buffers and free them before returning.

Memory ownership is explicit throughout. Parse helpers transfer phrase/nearset ownership into expression nodes, free both old and new objects on OOM where appropriate, and close term iterators in `fts5ExprPhraseFree()`. Config teardown deletes tokenizer instances with the matching v1/v2 `xDelete()` API, then frees all strings and arrays.

## Dependencies and Integration Points

This code integrates with several SQLite subsystems:

- Session extension internals: `sqlite3_changeset_iter`, `sqlite3changeset_start()`, `sqlite3changeset_start_strm()`, `sqlite3changeset_finalize()`, `sessionChangesetToHash()`, `sessionRebase()`, `sessionDeleteTable()`, and session-global stream chunk sizing.
- SQLite public memory and value APIs: `sqlite3_malloc*()`, `sqlite3_realloc*()`, `sqlite3_free()`, `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_value_*()`, `sqlite3_result_*()`, and SQLite result/error codes.
- SQLite virtual table API: `sqlite3_declare_vtab()` is used by `sqlite3Fts5ConfigDeclareVtab()` to declare visible columns plus hidden table-name and rank columns.
- FTS5 index module: expression evaluation opens and advances index iterators with `sqlite3Fts5IndexQuery()`, `sqlite3Fts5IterNext()`, `sqlite3Fts5IterNextFrom()`, `sqlite3Fts5IterClose()`, and optionally `sqlite3Fts5IterToken()`.
- FTS5 storage module: declared prototypes connect config and expression behavior to `%_content`, `%_docsize`, `%_config`, rebuild, optimize, merge, reset, and integrity operations implemented later in the amalgamation.
- FTS5 tokenizer module: config parsing stores tokenizer arguments, while `sqlite3Fts5Tokenize()` loads the tokenizer lazily and dispatches through either legacy `fts5_tokenizer` or `fts5_tokenizer_v2` with locale.
- FTS5 hash/index/write path: constants and prototypes define how document tokens are written, hashed, scanned, and queried, though implementations mostly appear outside this chunk.
- Generated Lemon parser mechanics: the hand-written expression code depends on `sqlite3Fts5ParserAlloc()`, `sqlite3Fts5Parser()`, and `sqlite3Fts5ParserFree()` from the generated parser in this same range.
- Optional build flags: `SQLITE_ENABLE_FTS5`, `SQLITE_CORE`, `NDEBUG`, `SQLITE_DEBUG`, `SQLITE_COVERAGE_TEST`, `SQLITE_MUTATION_TEST`, `SQLITE_OMIT_AUXILIARY_SAFETY_CHECKS`, and `SQLITE_FTS5_MAX_EXPR_DEPTH` affect declarations, assertions, parser tracing, and safety macros.

For WiredTiger, the practical integration point is build/test linkage against this vendored amalgamation. Local changes here would be high risk because they can silently change SQLite's FTS5 query semantics or extension ABI.

## Risks and Edge Cases

- The chunk crosses source-file boundaries. The first few lines belong to `sqlite3session.c`; the rest begins `fts5.c`. Research and future edits must not assume one coherent subsystem across the entire slice.
- The assigned range ends at the start of `fts5ExprAssignXNext()`, so parse-node finalization and later expression APIs are incomplete here and continue in the next chunk.
- FTS5 ABI structures are public. Reordering or changing `Fts5ExtensionApi`, `fts5_tokenizer_v2`, `fts5_tokenizer`, or `fts5_api` fields would break extensions.
- The tokenizer contract is subtle. `FTS5_TOKEN_COLOCATED` must not be returned for the first token and drives synonym handling differently for query and document tokenization. Prefix and tokendata behavior depend on exact `nQueryTerm` versus `nFullTerm` handling.
- In `fts5ParseTokenize()`, tokendata mode computes `nQueryTerm` with `strlen()` after setting `pTerm`/`pSyn` text. This intentionally treats embedded zero bytes as a query-term boundary, while `nFullTerm` retains full tokenizer output.
- `sqlite3Fts5ExprNew()` must clean up parser output correctly across parse errors, OOM, and implicit colset allocation. Leaking `apPhrase`, double-freeing phrase ownership, or keeping `sParse.pExpr` after error would be serious.
- Column filters are disallowed for `detail=none`. `sqlite3Fts5ParseSetColset()` converts such attempts into parse errors; changing this would alter documented query behavior.
- `fts5ParseSetColset()` intersects nested colsets. If the intersection becomes empty, it rewrites the node to `FTS5_EOF` and clears `xNext`, which affects later iterator initialization.
- The config parser accepts abbreviations through prefix comparisons in option and enum parsing. Ambiguous or partial option names can be accepted or rejected based on matching behavior; this is observable SQL syntax.
- `contentless_delete=1` is accepted only for contentless tables and rejected with `columnsize=0`. `contentless_unindexed=1` also requires contentless mode. These cross-option validations are user-visible.
- `fts5ConfigSkipLiteral()` validates only a constrained subset of SQL literal syntax for config/rank parsing. Accepted values here determine what can be stored in rank arguments and tokenizer directives.
- `sqlite3Fts5ConfigLoad()` rejects unknown file format versions unless they match current or secure-delete format versions. This protects against reading newer FTS5 data with older code.
- Position-list decoding deliberately stops on some corrupt encodings instead of reading past bounds. Assertion-only `assert_nc()` conditions distinguish trusted invariants from corruption-sensitive invariants.
- Simple TERM nodes alias position-list data owned by the index iterator in `detail=full`, while more complex expressions synthesize buffers. Lifetime changes around iterator advancement can invalidate those aliases.
- `detail!=full` paths do not have full position information. `fts5ExprNearTest()` reduces matching to presence checks, and auxiliary APIs are documented as slower or less informative for such tables.
- `highlight()` and `snippet()` rely on tokenizer byte offsets to splice original column text. Tokenizers that return inconsistent offsets can produce malformed output.
- `snippet()` scoring allocates an `aSeen` array sized by phrase count and a sentence-start array that grows by doubling. OOM must propagate through SQLite result errors.
- `bm25()` asserts row count is positive after `xRowCount()` succeeds and caches IDF values in auxdata. Edge behavior for empty tables is normally avoided because the function runs only for matched rows.
- `fts5ExprNodeNext_STRING()` has special synonym advancement logic for `iFrom` seeks and descending order. Comparator mistakes can skip rows or loop indefinitely.
- The generated Lemon parser uses a fixed stack depth of 100 unless configured otherwise, while `SQLITE_FTS5_MAX_EXPR_DEPTH` guards expression tree depth later. Parser stack overflow and deep expression handling are distinct concerns.

## Test Signals

Useful test signals visible in this chunk include:

- Public API error paths: `sqlite3rebaser_create()` returning `SQLITE_NOMEM`, `sqlite3session_config()` returning `SQLITE_MISUSE`, rebase iterator start/finalize behavior, and streaming versus non-streaming rebase equivalence.
- FTS5 extension ABI tests: registering custom auxiliary functions/tokenizers, v1/v2 tokenizer lookup compatibility, locale propagation, synonym handling with `FTS5_TOKEN_COLOCATED`, prefix query behavior, and tokendata token boundaries.
- Built-in auxiliary tests: `highlight()` argument count, out-of-range column behavior, overlapping phrase coalescing, locale-aware retokenization, `snippet()` ellipsis/window selection, sentence-start bonus scoring, `bm25()` weighting and auxdata caching, and `fts5_get_locale()` argument validation.
- Config parser tests: duplicate `tokenize=`, `content=`, and `content_rowid=` directives; malformed boolean options; invalid/too-many prefix indexes; reserved column/table names (`rank`, `rowid`); invalid `detail=` values; contentless option incompatibilities; default `%_content` versus `%_docsize` selection; and SQL declaration of hidden columns.
- `%_config` loading tests: defaults for missing keys, valid ranges for `pgsz`, `hashsize`, `automerge`, `usermerge`, `crisismerge`, `deletemerge`, `secure-delete`, and `insttoken`; invalid rank specs; invalid file-format version error text.
- MATCH parser tests: unterminated quoted strings, bareword syntax errors, implicit AND, explicit AND/OR/NOT, `NEAR()` spelling and distance parsing, prefix `*`, caret first-token constraints, column filters, inverse colsets, empty quoted phrases, phrase concatenation with `+`, and `detail=none` column-query rejection.
- Expression iterator tests: ascending and descending rowid order, `iFirst`/`iLast` boundaries, TERM fast path, multi-term phrase adjacency, synonym merging, NEAR trimming, AND/OR/NOT row alignment, `bNomatch` propagation, EOF propagation, and prefix-index selection flags.
- Debug/test instrumentation: `assert()`, `assert_nc()`, `ALWAYS()`/`NEVER()`, parser trace hooks under non-`NDEBUG`, and generated-parser coverage tables provide signals for internal invariant and coverage testing.
