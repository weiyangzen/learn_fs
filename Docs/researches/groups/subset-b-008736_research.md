# subset-b-008736 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5Int.h -->
# sources/storage-engines/sqlite/ext/fts5/fts5Int.h

## Purpose
`fts5Int.h` is the private coordination header for SQLite FTS5. It defines the shared scalar aliases, portability macros, constants, opaque type declarations, core structs, and cross-module function prototypes used by the FTS5 virtual table implementation. It is not a public API header; it binds together config parsing, buffer/poslist helpers, index access, virtual table storage, expression evaluation, hash accumulation, tokenizers, auxiliary functions, vocabulary tables, and Unicode helpers.

## Important APIs, types, and constants
- Basic aliases `u8`, `u16`, `u32`, `u64`, `i16`, and `i64` are provided for non-amalgamation builds, along with `ArraySize`, `ALWAYS`, `NEVER`, `MIN`, `MAX`, `FLEXARRAY`, and `UNUSED_PARAM` helpers.
- Limits and defaults include `FTS5_MAX_TOKEN_SIZE` at 32768 bytes, `FTS5_MAX_PREFIX_INDEXES` at 31, `FTS5_MAX_SEGMENT` at 2000, `FTS5_DEFAULT_NEARDIST` at 10, and `FTS5_DEFAULT_RANK` as `bm25`.
- `Fts5Config` is the central table configuration object. It stores database/table identity, column names, unindexed column flags, tokenizer state, prefix indexes, content mode, detail mode, locale/tokendata flags, config-table values such as page size and merge settings, rank function configuration, and error-message plumbing.
- `Fts5TokenizerConfig` abstracts tokenizer v1/v2 state, arguments, pattern mode, and current locale.
- `Fts5Buffer`, `Fts5PoslistReader`, `Fts5PoslistWriter`, and `Fts5Termset` define the shared buffer and position-list utilities implemented in `fts5_buffer.c`.
- `Fts5Index`, `Fts5IndexIter`, query flags, and write/read/sync/merge/integrity prototypes define the contract to `fts5_index.c`.
- `Fts5Table` maps the SQLite virtual table object to an FTS5 config and index.
- `Fts5Hash` prototypes define the transient term hash used before flushing postings to `%_data`.
- `Fts5Storage` prototypes define the persistence contract for `%_content`, `%_docsize`, `%_config`, and related rebuild/merge operations.
- `Fts5Expr`, `Fts5ExprNode`, `Fts5ExprPhrase`, `Fts5ExprNearset`, `Fts5Token`, and parse callbacks define the query-expression parse/evaluation boundary.
- Tokenizer, auxiliary, vocab, and Unicode prototypes make this header the single internal dispatch surface for module initialization.

## Control flow and integration
The header is organized by module interface. `fts5_main.c` and storage code parse a table declaration with `sqlite3Fts5ConfigParse()`, declare a virtual table schema, load tokenizers, open storage/index handles, and use `sqlite3Fts5IndexWrite()` plus `sqlite3Fts5Storage...()` functions for DML. Query planning builds `Fts5Expr` objects with `sqlite3Fts5ExprNew()` or `sqlite3Fts5ExprPattern()`, then iterates them through `sqlite3Fts5ExprFirst()`, `sqlite3Fts5ExprNext()`, `sqlite3Fts5ExprEof()`, and `sqlite3Fts5ExprRowid()`. Auxiliary functions access phrase counts, position lists, query tokens, and inst-token data through the expression APIs declared here.

## State and persistence behavior
This header does not persist state itself, but it defines all structs that carry persistent-table metadata and transient query/index state. `Fts5Config` mirrors both `CREATE VIRTUAL TABLE` options and runtime values loaded from `%_config`. The index/storage APIs declared here are responsible for writing postings, averages, config values, content rows, docsize rows, deletes, merges, rollbacks, and integrity checks. The hash and buffer APIs define transient in-memory state that is flushed or discarded by index sync/rollback paths.

## Dependencies
It includes `fts5.h` and `sqlite3ext.h`, then uses SQLite extension APIs, SQLite allocation APIs, varints, statements, virtual-table structs, and tokenizer/extension-function types. Build-time dependencies include generated parser and Unicode modules through prototypes elsewhere. Non-amalgamation builds receive local fallback typedefs and macros normally provided by SQLite internal headers.

## Risks and edge cases
- Because this is the internal ABI across FTS5 modules, changes to struct layout or prototype semantics can silently break multiple C files.
- `Fts5Config` contains ownership-sensitive pointers: tokenizer objects, `azCol`, `abUnindexed`, prefix arrays, SQL fragments, and rank strings must be freed consistently by `sqlite3Fts5ConfigFree()`.
- `FTS5_CURRENT_VERSION` and `FTS5_CURRENT_VERSION_SECUREDELETE` gate file-format compatibility; mismatched changes can produce unreadable indexes or bad upgrade behavior.
- Query flags share one bit namespace between public index-query behavior and internal skip/no-output behavior; collisions are explicitly avoided by this header.
- Detail modes, content modes, locale, tokendata, and contentless-delete options strongly affect downstream invariants. Callers must check the defined constants instead of assuming full-detail, content-bearing tables.

## Test signals
Useful tests should cover non-amalgamation builds, configuration combinations, tokenizer v1/v2 loading, detail modes, prefix-index limits, secure-delete format loading, contentless-delete/contentless-unindexed paths, expression parsing and iteration APIs, hash write/query/scan APIs, storage rollback/sync, and auxiliary APIs that depend on expression metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5Int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_aux.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_aux.c

## Purpose
`fts5_aux.c` registers and implements FTS5 built-in auxiliary functions: `snippet`, `highlight`, `bm25`, and `fts5_get_locale`. These functions run at query time against an `Fts5Context` using the `Fts5ExtensionApi`, so they are consumers of the expression/index/storage layer rather than direct index writers.

## Important APIs and functions
- `sqlite3Fts5AuxInit()` registers the built-ins through `fts5_api.xCreateFunction()`.
- `CInstIter`, `fts5CInstIterInit()`, and `fts5CInstIterNext()` iterate coalesced phrase instances for a single column. Overlapping matches are merged into one start/end range for highlighting.
- `HighlightContext`, `fts5HighlightAppend()`, `fts5HighlightCb()`, and `fts5HighlightFunction()` implement `highlight(col, open, close)`.
- `Fts5SFinder`, `fts5SentenceFinderCb()`, `fts5SnippetScore()`, and `fts5SnippetFunction()` implement snippet range selection, sentence-boundary preference, and highlighted excerpt rendering.
- `Fts5Bm25Data`, `fts5Bm25GetData()`, and `fts5Bm25Function()` compute BM25 ranking and cache per-query IDF/average-length data with `xGetAuxdata()`/`xSetAuxdata()`.
- `fts5GetLocaleFunction()` exposes the stored locale for a requested column through `xColumnLocale()`.

## Control flow
`highlight()` validates that it has three arguments, reads the target column text with `xColumnText()`, initializes a coalesced instance iterator from `xInstCount()`/`xInst()`, fetches the column locale, and re-tokenizes the column with `xTokenize_v2()`. The tokenizer callback copies original byte ranges into an output string while opening and closing the requested markers around matching token ranges. Out-of-range columns return an empty string rather than an error.

`snippet()` validates five arguments, clamps the requested token count to 0..64, and scans either one column or all columns. For each candidate match instance it scores a window by favoring new query phrases heavily and repeated phrases lightly. It also tokenizes columns to find likely sentence starts after punctuation, adding a bonus for windows aligned to a sentence or document start. Once the best column/start are chosen, it reuses the highlight callback in a bounded range and adds ellipses before or after omitted text.

`bm25()` first materializes query-wide data. It asks for total row count and total token count, then for each phrase runs `xQueryPhrase()` with `fts5CountCb()` to count matching rows and compute IDF. Per row, it counts phrase instances with optional per-column weights from function arguments, gets document length with `xColumnSize(-1)`, and returns the negative BM25 score so SQLite's ascending sort ranks better matches first.

`fts5_get_locale()` requires exactly one integer column index, checks range, then returns the locale bytes for that column.

## State and persistence behavior
No database state is persisted by this file. It reads current-row content, phrase-instance metadata, column sizes, row counts, and locales from the extension API. The only retained state is BM25 auxdata, scoped to the current query and destroyed with `sqlite3_free`. Highlight/snippet strings and sentence arrays are transient allocations freed before return.

## Dependencies and integration points
The file depends on the FTS5 extension API version having `xTokenize_v2()` and `xColumnLocale()` for locale-aware tokenization. It uses SQLite result/error APIs, SQLite allocation APIs, `math.h` for `log()`, and phrase/instance metadata generated by the expression evaluator. It integrates with tokenizer locale support added in the config/main layers and with `xInst()`/`xInstCount()` position data populated from the expression/index layers.

## Risks and edge cases
- Output construction uses repeated `sqlite3_mprintf("%z...")`, which is simple but can be costly for large highlighted text.
- `snippet()` allocates `aSeen` using `nPhrase`; zero-phrase or malformed expression behavior depends on upstream guarantees.
- `bm25()` asserts that row count is positive after `xRowCount()`. Empty-table behavior must be handled by the caller/API contract.
- `xInst()` offsets are treated as trusted except for a corruption check in `snippet()` where `io>nDocsize` yields `FTS5_CORRUPT`.
- Locale-aware tokenization means highlight/snippet correctness depends on the same tokenizer and locale being used for indexing and query-time rendering.
- Argument validation differs by function: out-of-range `highlight()` returns empty text, while `fts5_get_locale()` returns `SQLITE_RANGE`.

## Test signals
Tests should cover overlapping phrase highlights, colocated tokens, prefix/synonym query instances, range-limited snippets, sentence-boundary scoring, all-column snippets with `iCol=-1`, NULL marker/ellipsis arguments, column weight arguments for `bm25`, empty and very short documents, locale-enabled tables, invalid argument counts/types, and corruption paths for impossible instance offsets.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_buffer.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_buffer.c

## Purpose
`fts5_buffer.c` implements small shared utilities used throughout FTS5: growable byte buffers, big-endian integer helpers, varint position-list readers/writers, allocation helpers, bareword classification, and a fixed-bucket term set used by integrity checking.

## Important APIs and functions
- `sqlite3Fts5BufferSize()` grows `Fts5Buffer` allocations exponentially from 64 bytes.
- `sqlite3Fts5BufferAppendVarint()`, `sqlite3Fts5BufferAppendBlob()`, `sqlite3Fts5BufferAppendString()`, `sqlite3Fts5BufferAppendPrintf()`, and `sqlite3Fts5BufferSet()` build byte/string buffers with shared `int *pRc` error propagation.
- `sqlite3Fts5Mprintf()` is a small `sqlite3_vmprintf()` wrapper that respects an existing error code.
- `sqlite3Fts5Put32()` and `sqlite3Fts5Get32()` encode/decode big-endian 32-bit integers for FTS5 record fields.
- `sqlite3Fts5PoslistNext64()`, `sqlite3Fts5PoslistReaderInit()`, and `sqlite3Fts5PoslistReaderNext()` decode FTS5 position-list streams into `(column << 32) + offset` values.
- `sqlite3Fts5PoslistSafeAppend()` and `sqlite3Fts5PoslistWriterAppend()` encode monotonically increasing positions, including column-change markers.
- `sqlite3Fts5MallocZero()` and `sqlite3Fts5Strndup()` centralize allocation and error-code handling.
- `sqlite3Fts5IsBareword()` classifies expression/config bareword characters.
- `sqlite3Fts5TermsetNew()`, `sqlite3Fts5TermsetAdd()`, and `sqlite3Fts5TermsetFree()` implement a duplicate-detection set keyed by index id plus term bytes.

## Control flow
Buffer append functions first ensure capacity, then append bytes and update `n`. String and printf appenders write a trailing NUL byte but keep it outside the logical length. Position-list decoding reads varint deltas. A value of 1 denotes a column change followed by column number and first offset; values greater than 1 are offset deltas plus 2. A value of 0 is treated as a terminator boundary. Encoding mirrors this by writing column markers when the high column bits change and offset deltas otherwise.

The term set uses the same checksum style as `fts5_hash.c` so collision-oriented tests can exercise both paths. On add, it checks an existing bucket for matching `iIdx`, term length, and bytes; if absent, it allocates one object containing the entry and term payload.

## State and persistence behavior
This file only manages transient memory. `Fts5Buffer` retains allocation capacity until freed or reused with `sqlite3Fts5BufferZero()`. Position-list helpers read/write serialized posting-list fragments that are later embedded in hash entries or index pages. `Fts5Termset` is in-memory only and is freed after integrity-check use.

## Dependencies and integration points
The implementation depends on `fts5Int.h`, SQLite allocation APIs, SQLite varint helpers declared in the header, and `assert_nc()` for corrupt-record-tolerant checks. It is used by config SQL assembly, expression phrase/NEAR evaluation, hash doclist construction, index page construction, auxiliary rendering, and integrity checks.

## Risks and edge cases
- Many functions are no-ops once `*pRc` is non-OK, so callers must initialize and inspect the shared error code correctly.
- `sqlite3Fts5BufferAppendString()` decrements `n` after appending `nStr+1`; it assumes the append happened or the buffer state remains valid under the error-code convention.
- `sqlite3Fts5PoslistSafeAppend()` silently ignores out-of-order positions. Callers must supply positions in nondecreasing order or matches disappear.
- `sqlite3Fts5PoslistNext64()` stops on corrupt records such as a column marker with an invalid first offset; callers must treat EOF plus `iPos=-1` as possible corruption depending on context.
- `sqlite3Fts5IsBareword()` indexes the ASCII table with `(int)t`; this relies on the high-bit early return for non-ASCII bytes.

## Test signals
Tests should exercise buffer growth, OOM propagation, NUL-terminated string append semantics, big-endian integer round trips, poslist encode/decode across columns and offsets, corrupt poslist boundaries, zero-length input, bareword parsing for ASCII and high-bit bytes, termset duplicate detection, and collision-heavy termset buckets.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_config.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_config.c

## Purpose
`fts5_config.c` parses FTS5 virtual-table declarations, manages `Fts5Config` lifetime, declares the SQLite virtual table schema, tokenizes text through the configured tokenizer, parses rank specifications, applies `%_config` values, and loads persistent configuration from the `%_config` shadow table.

## Important APIs and functions
- `sqlite3Fts5ConfigParse()` builds an `Fts5Config` from xCreate/xConnect arguments.
- `sqlite3Fts5ConfigFree()` releases tokenizer instances, tokenizer args, names, columns, prefix arrays, rank strings, content SQL fragments, and the config object.
- `sqlite3Fts5ConfigDeclareVtab()` constructs the hidden-column virtual-table schema.
- `sqlite3Fts5Tokenize()` lazily loads the tokenizer and dispatches to tokenizer v1 or v2, passing locale to v2.
- `sqlite3Fts5ConfigParseRank()` validates strings like `bm25(1.0, 'x')` and splits function name from literal arguments.
- `sqlite3Fts5ConfigSetValue()` applies one runtime config key such as `pgsz`, `hashsize`, `automerge`, `usermerge`, `crisismerge`, `deletemerge`, `rank`, `secure-delete`, or `insttoken`.
- `sqlite3Fts5ConfigLoad()` reads `%_config`, installs defaults, validates file-format version, and records the cookie.
- `sqlite3Fts5ConfigErrmsg()` routes formatted errors to `sqlite3_vtab.zErrmsg` when available.

## Control flow
Declaration parsing tokenizes each CREATE VIRTUAL TABLE argument into either a column definition or an option assignment. `fts5ConfigGobbleWord()` accepts quoted identifiers and barewords. Option assignments go to `fts5ConfigParseSpecial()`, which handles prefix lists, tokenizer argument tokenization, content modes, content-rowid, boolean options, detail mode, locale, and tokendata. Column arguments go to `fts5ConfigParseColumn()`, which rejects reserved `rank` and `rowid` names and records optional `UNINDEXED`.

After scanning arguments, `sqlite3Fts5ConfigParse()` enforces cross-option constraints: `contentless_delete=1` requires contentless tables and is incompatible with `columnsize=0`; `contentless_unindexed=1` requires contentless tables. It then synthesizes the default content table target if no `content=` was specified: normal tables use `%_content`; contentless tables with docsize enabled use `%_docsize`; contentless-unindexed tables may switch to `FTS5_CONTENT_UNINDEXED`. Finally it defaults `content_rowid` to `rowid` and builds `zContentExprlist`, which is the select-list fragment used to retrieve rowid, column values, and optional locale columns.

Runtime loading first resets defaults for page size, merge settings, hash size, and delete merge, then scans `%_config`. All keys other than `version` are applied through `sqlite3Fts5ConfigSetValue()`. File-format version must match `FTS5_CURRENT_VERSION` or `FTS5_CURRENT_VERSION_SECUREDELETE`.

## State and persistence behavior
`Fts5Config` stores both declaration-time state and persistent shadow-table settings. Declaration-time state is in memory but determines which shadow tables and SQL fragments are used. `%_config` values are persistent and are loaded into fields such as `pgsz`, `nAutomerge`, `nUsermerge`, `nCrisisMerge`, `nHashSize`, `zRank`, `zRankArgs`, `bSecureDelete`, `nDeleteMerge`, and `bPrefixInsttoken`. Tokenizer instances are loaded lazily and cached in `pConfig->t`.

## Dependencies and integration points
The file depends on the buffer helpers for SQL assembly, allocation helpers from `fts5_buffer.c`, tokenizer loading from `fts5_main.c`/`fts5_tokenizer.c`, SQLite SQL preparation/stepping/finalization APIs, SQLite value APIs, and constants from `fts5Int.h`. Storage and index modules consume the resulting config for table names, content modes, merge parameters, tokenizer behavior, locale behavior, and file-format validation.

## Risks and edge cases
- Option matching is prefix-based through `sqlite3_strnicmp(name, zCmd, nCmd)`, so ambiguous abbreviations are rejected only in enum parsing, not all option paths.
- Tokenizer directive parsing accepts only space as config whitespace in helper routines, whereas expression parsing accepts tabs/newlines too.
- `fts5ConfigGobbleWord()` allocates a full input-length copy for each word, which is simple but may be wasteful for long malformed inputs.
- Rank parsing only accepts SQL literals in the argument list; expressions are intentionally rejected.
- Cross-option rules are important for contentless tables. Missing tests here can create configurations that later storage/index code cannot satisfy.
- File-format validation reports a rebuild hint. Incorrect version constants or secure-delete transitions can make existing indexes unreadable.

## Test signals
Tests should cover quoted and bare column names, reserved column/table names, malformed quotes, prefix range/limit errors, duplicate tokenizer/content/content_rowid directives, contentless-delete constraints, contentless-unindexed behavior with unindexed columns, locale-enabled expression lists, tokenizer v1/v2 dispatch, rank parsing with literals and malformed expressions, `%_config` defaults and bounds, secure-delete version loading, and invalid config version error messaging.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_expr.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_expr.c

## Purpose
`fts5_expr.c` parses MATCH expressions into an FTS5 expression tree, initializes index iterators for terms and prefixes, evaluates boolean/phrase/NEAR/column-constrained matches, exposes phrase position lists to auxiliary APIs, supports trigram LIKE/GLOB pattern acceleration, and registers debug/test scalar functions for expression rendering and Unicode helpers.

## Important APIs, types, and functions
- `Fts5Expr` owns the root node, config pointer, index pointer, rowid direction, and phrase array.
- `Fts5ExprNode` represents AND, OR, NOT, STRING/NEAR, TERM, or empty-match nodes. Each node stores EOF/nomatch state, current rowid, tree height, child pointers, and an `xNext` method.
- `Fts5ExprTerm` stores term bytes, query length versus full tokendata length, prefix/first-token flags, an index iterator, and synonym chain.
- `Fts5ExprPhrase` stores ordered terms and the current phrase poslist. `Fts5ExprNearset` groups phrases under a NEAR distance and optional column set.
- `sqlite3Fts5ExprNew()` tokenizes expression syntax, drives the Lemon parser, applies implicit LHS column filters, and returns an expression.
- `sqlite3Fts5ExprPattern()` converts trigram LIKE/GLOB patterns into a MATCH expression matching a superset of rows.
- `sqlite3Fts5ExprFirst()`, `sqlite3Fts5ExprNext()`, `sqlite3Fts5ExprEof()`, and `sqlite3Fts5ExprRowid()` provide the row iteration API.
- Parser callbacks such as `sqlite3Fts5ParseTerm()`, `sqlite3Fts5ParseNearset()`, `sqlite3Fts5ParseNode()`, `sqlite3Fts5ParseImplicitAnd()`, and colset functions are called by generated parser code.
- Auxiliary-facing APIs include phrase count/size, poslist access, collist access, cloned phrase expressions, query token access, inst-token lookup, poslist population for low-detail tables, and token-map clearing.

## Control flow
The lexer `fts5ExprGetToken()` recognizes operators, braces, parentheses, quoted strings, barewords, prefix markers, and special keywords. `sqlite3Fts5ExprNew()` feeds tokens into the generated parser, then optionally wraps the whole expression in a one-column colset if the MATCH left-hand side is a user column. Node construction assigns specialized `xNext` methods and flattens compatible AND/OR children, while enforcing maximum expression depth.

Iteration starts with `sqlite3Fts5ExprFirst()`. For each string/term node, `fts5ExprNearInitAll()` opens an `Fts5IndexIter` for every term and synonym via `sqlite3Fts5IndexQuery()`, using prefix and descending flags plus the node colset. TERM nodes can point directly at index-provided poslists. STRING nodes synchronize multiple term iterators to the same rowid, synthesize phrase poslists, merge synonym poslists, apply `^` first-token constraints, and trim NEAR matches.

Boolean nodes combine child iterators. OR selects the earliest rowid in iteration order, preferring real matches over `bNomatch` at equal rowid. AND advances lagging children until all rowids align; if any aligned child is only a structural/non-poslist match, the parent may become `bNomatch` and skip at the root. NOT advances the exclusion side to the include side and suppresses rows where the right child also matches. The public `First` and `Next` loops skip root `bNomatch` entries and enforce caller-provided rowid bounds.

Parsing terms uses `sqlite3Fts5Tokenize()` with `FTS5_TOKENIZE_QUERY` and optional prefix mode. Colocated tokenizer tokens become synonym chains. For `tokendata`, the query key length stops at the embedded NUL but the full term bytes remain available for token-return APIs. Detail modes restrict phrase/NEAR/column queries: without full detail, phrase and NEAR queries are rejected except for transformed trigram pattern cases.

## State and persistence behavior
This file is mostly transient query state. It owns expression nodes, phrases, synonym objects, poslist buffers, and index iterators. It reads persistent index data through `Fts5IndexIter` but does not write table state except for `sqlite3Fts5IndexIterWriteTokendata()` calls while populating token mappings for `xInstToken()` on prefix/tokendata queries. Debug/test scalar functions allocate temporary configs and expressions to print parse trees.

## Dependencies and integration points
The file depends on generated `fts5parse.h` and Lemon parser functions, `fts5_config.c` tokenizer and config APIs, `fts5_buffer.c` poslist/buffer helpers, `fts5_index.c` query/iterator/token-data APIs, Unicode helpers for debug/test functions, and SQLite allocation/UDF APIs. It is central to `fts5_main.c` query execution and to auxiliary functions that use phrase counts, position lists, instance tokens, and cloned phrase queries.

## Risks and edge cases
- Iterator direction is abstracted by `fts5RowidCmp()`; any direct numeric rowid comparison in this file must respect `bDesc` or DESC queries regress.
- Phrase and NEAR matching rewrite poslists in place. The logic relies on output positions being a subset of input positions.
- Synonym handling merges multiple poslists and skips duplicate positions; OOM during dynamic reader allocation must free temporary buffers correctly.
- `bNomatch` is subtle. Low-detail, column-filtered, AND, OR, and NOT paths can produce rows that satisfy term/doclist constraints but not final position semantics.
- Expression depth is capped by `SQLITE_FTS5_MAX_EXPR_DEPTH`; parser flattening reduces depth for repeated AND/OR but NOT remains binary.
- `sqlite3Fts5ExprPattern()` builds a superset expression for trigram patterns. Correct final LIKE/GLOB filtering must happen outside this file.
- Column filters are disallowed for `detail=none`; phrase/NEAR restrictions for `detail!=full` are enforced during node construction and pattern conversion.
- `sqlite3Fts5ExprClearTokens()` assumes iterators exist for every term; callers must only invoke it after iterator initialization.

## Test signals
Tests should cover tokenization of quoted strings and barewords, syntax errors, implicit AND, explicit AND/OR/NOT precedence, expression-depth limits, column sets and inverted colsets, missing columns, LHS column filters, prefix terms, synonyms/colocated tokens, `^` first-token phrases, phrase and NEAR poslist trimming, ascending and descending rowid iteration, rowid bounds, detail=none/detail=columns restrictions and poslist population, trigram LIKE/GLOB superset generation, tokendata embedded-NUL behavior, xQueryToken/xInstToken APIs, and debug expression printers under test builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_expr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_hash.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_hash.c

## Purpose
`fts5_hash.c` implements the in-memory term hash used by FTS5 index writes to accumulate `term -> doclist` content before flushing it to a level-0 segment. It stores postings compactly in per-term allocations and supports exact term lookup and sorted prefix/full scans for flush and query integration.

## Important APIs and functions
- `sqlite3Fts5HashNew()` allocates a hash with 1024 slots, stores a pointer to the caller's byte counter, and copies the table detail mode.
- `sqlite3Fts5HashFree()` and `sqlite3Fts5HashClear()` release all entries while preserving/freeing the hash object as appropriate.
- `sqlite3Fts5HashWrite()` appends one token occurrence or delete marker for a rowid/column/position/key byte plus token.
- `fts5HashAddPoslistSize()` finalizes the previous row's poslist-size or detail-none marker bytes.
- `fts5HashResize()` doubles slot count when load reaches 50 percent.
- `sqlite3Fts5HashQuery()` returns a malloced copy of a single term doclist, including a finalized copy of pending poslist-size bytes.
- `sqlite3Fts5HashScanInit()`, `sqlite3Fts5HashScanNext()`, `sqlite3Fts5HashScanEof()`, and `sqlite3Fts5HashScanEntry()` sort matching entries and iterate term/doclist pairs.
- `fts5HashEntrySort()` and `fts5HashEntryMerge()` implement a nonrecursive merge-bucket sort over existing hash entries.

## Control flow
Each `Fts5HashEntry` allocation contains the struct, key bytes, a NUL terminator for scan convenience, and doclist bytes. The key is a one-byte index discriminator (`bByte`) followed by token bytes, so main and prefix indexes occupy the same hash namespace without colliding. On first write, the entry stores the absolute rowid varint and reserves a byte for the current row's poslist-size field. Later writes for the same row append column markers and position deltas depending on detail mode. Writes for a new row finalize the previous row's poslist metadata, append a rowid delta, and reserve the next poslist-size field.

For `detail=full`, positions are encoded as column-change markers plus offset deltas. For `detail=columns`, the code treats the column as the position-like value and writes at most one value per new column. For `detail=none`, content and delete flags are represented without full position data. Delete writes set `bDel`; content writes in detail-none set `bContent`.

Exact query looks up the key by hash slot and copies only the doclist payload into a caller-owned buffer, using a faux entry inside that buffer so `fts5HashAddPoslistSize()` can finalize the copy without mutating the original entry. Scans sort pointers to existing entries by key, finalize entries in place when exposed, and return pointers into the entry allocation.

## State and persistence behavior
State is transient and memory-resident until index sync flushes it. The byte counter pointed to by `pnByte` is updated by net entry-data growth in `sqlite3Fts5HashWrite()`, allowing the index layer to decide when the hash is large enough to flush. The hash itself does not write to SQLite storage; it supplies serialized doclists to the index layer. `sqlite3Fts5HashClear()` resets all slots and entry count after flush or rollback.

## Dependencies and integration points
The file depends on `Fts5Config.eDetail`, SQLite allocation APIs, varint helpers, big-endian 32-bit helpers, and internal FTS5 constants. It integrates with `fts5_index.c` write paths, prefix-index handling via `bByte`, query paths that need unflushed terms, and flush paths that scan entries in sorted key order before constructing segment pages.

## Risks and edge cases
- The doclist format is intentionally similar but not identical to on-disk doclists. Flush/query code must account for hash-specific trailing poslist-size handling.
- `sqlite3Fts5HashWrite()` assumes rowids and columns arrive in valid order; debug assertions check monotonic columns, but release builds rely on callers.
- Reallocation updates the slot chain pointer manually. Bugs here can corrupt the hash chain or leave stale pointers.
- `fts5HashEntrySort()` uses a fixed 32-entry merge-slot array. It relies on the hash load/entry count staying within ranges where repeated merging does not overrun `ap`.
- Scan APIs expose pointers into hash entries and may finalize entries in place, so callers must not mutate/clear the hash during scan.
- Detail-none delete/content marker handling is compact and easy to misinterpret; tests need both delete-only and content-bearing rows.

## Test signals
Tests should cover first insert, repeated same-row positions, rowid deltas, column transitions, prefix-index discriminator bytes, hash resize, exact query before and after poslist finalization, sorted scan order, prefix scan filtering, detail=full/columns/none encodings, delete markers, byte-counter updates, clear/free behavior, collision-heavy terms, and interleaving unflushed hash results with persisted index reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_hash.c -->
