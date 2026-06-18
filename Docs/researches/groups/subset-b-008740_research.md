# subset-b-008740 Research

This grouped report covers the requested SQLite extension source files. Each section is delimited with the exact source path markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_tokenize.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_tokenize.c

## Purpose
`fts5_tokenize.c` implements and registers FTS5 built-in tokenizers: `unicode61`, `ascii`, `trigram`, and the v2 `porter` tokenizer wrapper. It turns SQL tokenizer declarations into `Fts5Tokenizer` instances, folds text, handles token/separator customization, emits tokens through FTS5 callbacks, and reports pattern support for trigram-backed LIKE/GLOB acceleration.

## Important APIs, Types, And Functions
The exported integration points are `sqlite3Fts5TokenizerInit()`, `sqlite3Fts5TokenizerPattern()`, and `sqlite3Fts5TokenizerPreload()`. `sqlite3Fts5TokenizerInit()` registers tokenizer modules with the `fts5_api`; `sqlite3Fts5TokenizerPattern()` identifies trigram pattern capability; `sqlite3Fts5TokenizerPreload()` detects configurations that must instantiate trigram tokenizers before planning.

Important tokenizer state types are `AsciiTokenizer`, `Unicode61Tokenizer`, `PorterTokenizer`, `PorterContext`, and `TrigramTokenizer`. ASCII stores a 128-byte token-character table. Unicode stores ASCII token flags, a reusable folding buffer, diacritic mode, sorted non-ASCII exceptions, and Unicode category flags. Porter wraps another tokenizer and stems callback tokens. Trigram stores case-fold and diacritic-fold flags.

Creation/destruction functions include `fts5AsciiCreate/Delete`, `fts5UnicodeCreate/Delete`, `fts5PorterCreate/Delete`, and `fts5TriCreate/Delete`. Tokenization functions include `fts5AsciiTokenize()`, `fts5UnicodeTokenize()`, `fts5PorterTokenize()`, and `fts5TriTokenize()`.

## Control Flow
Registration builds an array of built-in tokenizer structs for `unicode61`, `ascii`, and `trigram`, calls `xCreateTokenizer()` for each, then registers `porter` with the v2 tokenizer interface so it can pass the extra locale arguments supported by v2 tokenizers.

ASCII tokenization skips ASCII separators, treats all non-ASCII bytes as token bytes, lowercases only ASCII A-Z, grows a scratch token buffer as needed, and calls `xToken()` with byte offsets from the original input.

Unicode tokenization parses UTF-8 using local copies of SQLite UTF-8 macros when outside the amalgamation. It skips separators by consulting Unicode category tables from `fts5_unicode2.c`, then folds token codepoints with `sqlite3Fts5UnicodeFold()`. Diacritical modifier codepoints are allowed inside tokens and may fold to zero when removal is enabled. The output buffer is retained on the tokenizer and grown in place.

Porter tokenization finds and creates a base tokenizer, usually `unicode61`, then wraps its `xTokenize()` callback with `fts5PorterCb()`. The callback copies short tokens into a fixed buffer and applies generated Porter stemming steps before forwarding the stemmed token and original offsets. Tokens shorter than 3 bytes or longer than `FTS5_PORTER_MAX_TOKEN` pass through.

Trigram tokenization reads three folded non-zero Unicode characters into a small buffer, emits overlapping 3-character tokens, then slides the UTF-8 buffer one character at a time. Token offsets span from the first character of the trigram to the next character start.

## State And Persistence
All state is per-tokenizer instance and heap-owned by SQLite. There is no direct disk persistence. Effects become persistent only through FTS5 callers that store emitted tokens in an index. Unicode tokenizer folding buffers are retained between calls, making allocation amortized but instance-local. Porter retains the base tokenizer instance and its own fixed stemming buffer.

## Dependencies And Integration Points
The file depends on `fts5Int.h`, FTS5 tokenizer APIs, SQLite allocation/string utilities, FTS5 internal constants such as `FTS5_PATTERN_LIKE`, and Unicode helper functions from `fts5_unicode2.c`. Token callbacks integrate with FTS5 indexing, querying, auxiliary functions, and query planning for trigram LIKE/GLOB.

## Risks
UTF-8 boundary handling and byte offsets are critical because FTS5 stores offsets for phrase and snippet features. Unicode category, exception, and diacritic options can change token boundaries, so regressions are user visible. The ASCII tokenizer intentionally treats non-ASCII bytes as token characters, which is simple but can surprise callers expecting Unicode semantics. Porter stemming operates on byte tokens and assumes lowercased ASCII-like input; non-English or long tokens bypass or stem poorly. Trigram `remove_diacritics` is rejected when `case_sensitive=1`, an option combination that tests should preserve.

## Test Signals
Relevant tests should cover tokenizer option parsing, invalid odd argument counts, tokenchars/separators overrides, Unicode category strings, diacritic modes 0/1/2, malformed UTF-8, offset correctness, Porter expected stems, trigram LIKE/GLOB planning, and `SQLITE_DONE` callback normalization to `SQLITE_OK`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_tokenize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_unicode2.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_unicode2.c

## Purpose
`fts5_unicode2.c` is a machine-generated Unicode classification and folding support module for FTS5 tokenization. It provides case folding, optional diacritic removal, Unicode general-category parsing, codepoint category lookup, and ASCII token table derivation for configured category sets.

## Important APIs, Types, And Functions
Public functions are `sqlite3Fts5UnicodeIsdiacritic()`, `sqlite3Fts5UnicodeFold()`, `sqlite3Fts5UnicodeCatParse()`, `sqlite3Fts5UnicodeCategory()`, and `sqlite3Fts5UnicodeAscii()`. The private `fts5_remove_diacritic()` maps many lower-case Latin codepoints with diacritics back to ASCII base characters, with a simple/complex mode controlled by the tokenizer's `remove_diacritics` option.

The large static arrays `aFts5UnicodeBlock`, `aFts5UnicodeMap`, and `aFts5UnicodeData` encode compressed category ranges. The case-folding table in `sqlite3Fts5UnicodeFold()` encodes ranges and offsets generated from Unicode data.

## Control Flow
`sqlite3Fts5UnicodeFold()` first handles ASCII uppercase quickly. For BMP codepoints it binary-searches the generated folding range table, applies the encoded offset when the range and parity rule match, then optionally calls `fts5_remove_diacritic()`. For one higher-plane range it folds by adding 40. Other codepoints pass through.

`sqlite3Fts5UnicodeCategory()` rejects codepoints outside the supported 20-bit range, locates the relevant block and map range by binary search, checks the range length encoded in `aFts5UnicodeData`, and returns a 5-bit category id. Category 30 is special-cased for alternating lowercase/uppercase letter ranges.

`sqlite3Fts5UnicodeCatParse()` parses two-character category expressions such as `L*`, `Nd`, or `Co` into a 32-byte category mask. `sqlite3Fts5UnicodeAscii()` uses the same generated range data to fill a 128-entry ASCII token-character table from a category mask and always clears NUL.

## State And Persistence
The module is stateless and read-only. All tables are static constant data in process memory. It does not allocate memory, mutate global state, or persist results. Its outputs feed tokenizer instance state and ultimately affect persistent FTS5 index contents when tokenizers use it.

## Dependencies And Integration Points
The file includes only `<assert.h>` and relies on SQLite/FTS5 typedefs (`u8`, `u16`, `u32`) supplied by amalgamation context or prior declarations. It is consumed by `fts5_tokenize.c` for Unicode category checks, folding, diacritic handling, and ASCII token table initialization.

## Risks
The file is marked machine-generated; manual edits risk desynchronizing compressed tables from generator expectations. Unicode version drift can affect classification and folding compatibility with newer standards. Diacritic removal is not full Unicode normalization and only maps supported lower-case characters; callers must not assume canonical equivalence. Bounds are encoded compactly, so off-by-one errors would affect many tokenizer decisions.

## Test Signals
Tests should compare folding and category lookup for ASCII, Latin-1, Greek, Cyrillic, combining marks 768-817, private-use/category edge cases, unsupported high codepoints, and configured category strings. FTS5 tokenizer tests using `unicode61 categories` and `remove_diacritics` are the best integration signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_unicode2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_varint.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_varint.c

## Purpose
`fts5_varint.c` implements FTS5 variable-length integer serialization and deserialization. FTS5 uses this format heavily in index pages, doclists, position lists, and other compact on-disk/in-memory structures.

## Important APIs, Types, And Functions
The main APIs are `sqlite3Fts5GetVarint32()`, `sqlite3Fts5GetVarint()`, `sqlite3Fts5PutVarint()`, and `sqlite3Fts5GetVarintLen()`. `sqlite3Fts5GetVarint32()` is a 32-bit fast path with unrolled 1-, 2-, and 3-byte decoding and fallback to the 64-bit decoder. `sqlite3Fts5GetVarint()` decodes 1-9 byte 64-bit varints. `sqlite3Fts5PutVarint()` writes 1- or 2-byte values inline and delegates larger values to `fts5PutVarint64()`.

## Control Flow
Decoding checks the high bit of each byte to determine continuation. The 64-bit decoder is highly unrolled and uses precomputed masks (`SLOT_2_0`, `SLOT_4_2_0`) to avoid repeated expressions and compiler issues. The ninth byte stores eight payload bits and terminates the sequence.

Encoding writes low 7-bit chunks in reverse for normal values, clearing the continuation bit on the final low-order byte before reversing into the output buffer. Values needing the full 64-bit range use nine bytes with the last byte storing eight bits.

`sqlite3Fts5GetVarintLen()` computes the byte length for a `u32` value known by assertion to be at least 128, returning 2 through 5.

## State And Persistence
The module has no state. It directly reads and writes caller-provided buffers. Its encoding defines persistent FTS5 binary format, so compatibility with existing index bytes is mandatory.

## Dependencies And Integration Points
The file includes `fts5Int.h` for SQLite integer types, `SQLITE_NOINLINE`, and assertions. It is integrated throughout FTS5 index, doclist, position-list, and vocabulary code. `fts5_vocab.c` relies on related fast varint/poslist helpers to count positions.

## Risks
The decoders assume the caller supplies enough bytes for a valid varint; truncated or corrupt buffers are handled by higher-level FTS5 corruption checks, not by local bounds checks. Any encoding change would break on-disk FTS5 compatibility. The 32-bit decoder masks fallback values to 31 bits, so callers must use the correct API for expected ranges. The unrolled logic is performance-sensitive and easy to regress with seemingly harmless edits.

## Test Signals
Test round-trips for boundary values at 1, 2, 3, 4, 5, and 9 byte thresholds: 0x7f, 0x80, 0x3fff, 0x4000, 0x1fffff, 0x200000, 0xfffffff, 0x10000000, and high 64-bit values. FTS5 index corruption tests and rebuild/optimize tests also validate real-world decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_varint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_vocab.c -->
# sources/storage-engines/sqlite/ext/fts5/fts5_vocab.c

## Purpose
`fts5_vocab.c` implements the read-only `fts5vocab` virtual table module. It exposes the contents of an existing FTS5 index in three schemas: `row` for per-term totals, `col` for per-term/per-column totals, and `instance` for every term occurrence.

## Important APIs, Types, And Functions
The exported initializer is `sqlite3Fts5VocabInit(Fts5Global *pGlobal, sqlite3 *db)`, which registers the `fts5vocab` module. `Fts5VocabTable` stores virtual table configuration: target FTS5 database/table name, connection, global registry, table type, and a recursion guard. `Fts5VocabCursor` stores the underlying FTS5 table pointer, statement holding the table cursor id, FTS5 index iterator, structure reference, term bounds, rowid, term buffer, counts, and instance position state.

Virtual table methods are implemented by `fts5VocabCreate/Connect`, `fts5VocabBestIndexMethod`, `fts5VocabOpenMethod`, `fts5VocabFilterMethod`, `fts5VocabNextMethod`, `fts5VocabColumnMethod`, `fts5VocabRowidMethod`, and cleanup methods.

## Control Flow
Connect/create parses arguments, supports a TEMP-table form that names a separate target database, dequotes database/table/type strings, declares the schema matching `col`, `row`, or `instance`, and stores target metadata in one allocation.

`xBestIndex` recognizes usable constraints on the `term` column: equality, lower bound, and upper bound. It encodes selected constraints and the low 8 bits of `colUsed` into `idxNum`, assigns argv indexes, estimates equality as cheaper, and consumes `ORDER BY term ASC`.

`xOpen` prevents recursive definition, runs an FTS5 `MATCH '*id'` query to obtain the live FTS5 cursor id, resolves it to `Fts5Table`, flushes pending data to disk, allocates a cursor and per-column count arrays, and holds the prepared statement to keep the FTS5 table object available.

`xFilter` resets cursor state, decodes term constraints, copies an upper-bound term if present, opens an FTS5 index scan, saves a structure reference, and primes either the first instance row or the first aggregate row. `xNext` verifies the structure has not changed, advances rowid, then either walks instances or aggregates all rows for the current term into doc/count arrays before moving to the next term. `xColumn` formats results according to table type and detail mode.

## State And Persistence
The virtual table persists only its SQL schema entry. All scanning state is cursor-local. It reads persistent FTS5 index data after flushing pending in-memory content. A structure reference is held so concurrent index changes can be detected via `sqlite3Fts5StructureTest()`.

## Dependencies And Integration Points
The module depends on FTS5 internals: `Fts5Global`, `Fts5Table`, `Fts5Index`, index iterators, poslist decoders, structure reference APIs, table lookup by cursor id, and `sqlite3_create_module_v2()`. It is exposed as the SQL module `fts5vocab`.

## Risks
`fts5vocab` is tightly coupled to FTS5 internal cursor-id lookup and index iterator formats. Detail modes affect available columns: `detail=none` cannot provide real instance offsets and column names. Count logic must detect invalid column ids as `FTS5_CORRUPT`. Term upper-bound comparison is bytewise and must remain consistent with FTS5 term ordering. The recursion guard avoids resolving a vocab table against itself.

## Test Signals
Tests should create FTS5 tables with all three detail modes, multiple columns, deletes/flushes, term equality/range constraints, ORDER BY term, and all vocab table types. Corruption tests should exercise out-of-range column ids and structure changes during scans. Planner tests should verify `term` constraints are pushed into `xFilter`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5_vocab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5parse.y -->
# sources/storage-engines/sqlite/ext/fts5/fts5parse.y

## Purpose
`fts5parse.y` is the Lemon grammar for FTS5 query expressions. It describes how tokens from the FTS5 expression tokenizer become expression nodes, nearsets, phrases, column filters, implicit ANDs, prefixes, and NEAR groups.

## Important APIs, Types, And Functions
The generated parser is named `sqlite3Fts5Parser` and receives an `Fts5Parse *pParse` extra argument. Semantic values include `Fts5Token`, `Fts5ExprNode *`, `Fts5ExprNearset *`, `Fts5ExprPhrase *`, and `Fts5Colset *`.

Grammar actions call parser-construction helpers including `sqlite3Fts5ParseFinished()`, `sqlite3Fts5ParseError()`, `sqlite3Fts5ParseNode()`, `sqlite3Fts5ParseImplicitAnd()`, `sqlite3Fts5ParseColset()`, `sqlite3Fts5ParseColsetInvert()`, `sqlite3Fts5ParseSetColset()`, `sqlite3Fts5ParseNearset()`, `sqlite3Fts5ParseNear()`, `sqlite3Fts5ParseSetDistance()`, `sqlite3Fts5ParseSetCaret()`, and `sqlite3Fts5ParseTerm()`.

## Control Flow
The grammar starts at `input ::= expr`, then finalizes the parse tree. Boolean precedence is declared as OR, AND, NOT, TERM, COLON. Explicit `AND`, `OR`, and `NOT` create corresponding expression nodes. Adjacent cnearsets are combined using `sqlite3Fts5ParseImplicitAnd()`.

Column filters parse as single strings, braced lists, or inverted forms with `MINUS`; filters may apply to parenthesized expressions or individual nearsets. Nearsets may be a single phrase, a caret-anchored phrase, or `NEAR(...)` with optional distance. Phrases are sequences of string terms joined by `+`, and a trailing `*` sets prefix matching for the preceding term.

Syntax and stack overflow handlers report errors through `Fts5Parse`. Destructors free partially built nodes, nearsets, phrases, and column sets when parse reductions are discarded.

## State And Persistence
The grammar itself has no persistent state. Generated parser stack state is transient for one query parse. Successful parsing produces an FTS5 expression tree consumed by query execution; failures record messages in `Fts5Parse`.

## Dependencies And Integration Points
The file includes `fts5Int.h` and generated `fts5parse.h`. It depends on Lemon code generation and FTS5 expression-construction helpers implemented elsewhere. Query syntax accepted here directly defines SQL `MATCH` expression semantics.

## Risks
Grammar precedence determines user-visible behavior for mixed boolean and phrase expressions. Destructor correctness matters for parse-error memory safety. Column-filter inversion and nested column filters must remain consistent with documented FTS5 syntax. `YYNOERRORRECOVERY` disables recovery, so the first syntax error is terminal and error messages must be useful.

## Test Signals
Parser tests should cover boolean precedence, implicit AND, parentheses, `NOT`, column filters and inverted filters, braced column lists, caret anchor, NEAR with and without distance, `+` phrase concatenation, prefix `*`, syntax errors, and stack overflow or deeply nested expressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/fts5/fts5parse.y -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/icu/icu.c -->
# sources/storage-engines/sqlite/ext/icu/icu.c

## Purpose
`icu.c` integrates ICU with SQLite. Depending on build macros, it registers ICU-backed `regexp`, `upper`, `lower`, `like`, and `icu_load_collation` SQL functions, and exposes the loadable extension entry point `sqlite3_icu_init()`.

## Important APIs, Types, And Functions
The primary initializer is `sqlite3IcuInit(sqlite3 *db)`. For loadable builds, `sqlite3_icu_init()` calls it after `SQLITE_EXTENSION_INIT2()`. SQL functions are implemented by `icuRegexpFunc()`, `icuCaseFunc16()`, `icuLikeFunc()`, and `icuLoadCollation()`. Support functions include `icuLikeCompare()`, `icuRegexpDelete()`, `icuCollationColl()`, `icuCollationDel()`, and `icuFunctionError()`.

ICU APIs used include `uregex_open`, `uregex_setText`, `uregex_matches`, `uregex_close`, `u_strToUpper`, `u_strToLower`, `u_foldCase`, `ucol_open`, `ucol_setStrength`, `ucol_strcoll`, and `ucol_close`.

## Control Flow
`sqlite3IcuInit()` iterates a static scalar-function table and calls `sqlite3_create_function()` for each enabled function. Collation loading is always available when the file is compiled in; regexp/case/LIKE are included when not core-only or when ICU support is enabled.

`icuLikeFunc()` validates optional ESCAPE as one UTF-8 character, bounds the pattern length, then calls recursive `icuLikeCompare()`, which handles `%`, `_`, escapes, and case folding per Unicode codepoint.

`icuRegexpFunc()` caches a compiled `URegularExpression` in SQLite auxdata for the pattern argument, sets the current string text, runs a full match with `uregex_matches()`, clears the text pointer, and returns 1 or 0.

`icuCaseFunc16()` converts UTF-16 input using ICU upper/lower mapping, optionally with a locale. It tries once with the input-sized output buffer, then retries after `U_BUFFER_OVERFLOW_ERROR` with ICU's required size.

`icuLoadCollation()` opens an ICU collator for a locale, optionally applies a strength string, and registers an SQLite UTF-16 collation with a destructor that closes the collator.

## State And Persistence
Registered SQL functions and collations are per-connection state. Regex auxdata caches compiled patterns for a statement execution and is destroyed by SQLite. Collators live until the collation is replaced or the connection closes. No database file format is changed, but user schemas can persist collation names that require this extension to be loaded later.

## Dependencies And Integration Points
The module depends on ICU headers and libraries plus SQLite extension/core APIs. It uses `SQLITE_DETERMINISTIC`, `SQLITE_INNOCUOUS`, and `SQLITE_DIRECTONLY` flags. `sqliteicu.h` exposes `sqlite3IcuInit()` to statically linked applications.

## Risks
LIKE uses recursion for `%` matching, so the pattern length guard is important for worst-case behavior. ICU version changes can alter case mapping, regex, or collation results. `icu_load_collation()` is direct-only to limit schema-trigger abuse; changing flags would affect security posture. Locale-specific case mapping can surprise callers expecting SQLite ASCII semantics. Collation names persisted in schemas become load-order dependencies.

## Test Signals
Tests should cover Unicode LIKE folding, ESCAPE validation, pattern length errors, NULL propagation, regex cache reuse and invalid patterns, locale-specific upper/lower behavior such as Turkish I, collation loading with valid and invalid strength names, extension loading, and builds with/without `SQLITE_ENABLE_ICU`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/icu/icu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/icu/sqliteicu.h -->
# sources/storage-engines/sqlite/ext/icu/sqliteicu.h

## Purpose
`sqliteicu.h` is the public header for applications that link the ICU extension directly instead of loading it dynamically. It declares the `sqlite3IcuInit()` initialization function.

## Important APIs, Types, And Functions
The single exported declaration is `int sqlite3IcuInit(sqlite3 *db);`. The header includes `sqlite3.h` and wraps the declaration in `extern "C"` for C++ callers.

## Control Flow
There is no runtime control flow in the header. Consumers include it, then call `sqlite3IcuInit(db)` on a live SQLite connection to register ICU functions and collation support.

## State And Persistence
The header owns no state. The called initializer creates per-connection SQLite functions and collations as implemented in `icu.c`.

## Dependencies And Integration Points
It depends on the SQLite public header and the compiled ICU extension object. It is the static-link counterpart to the loadable `sqlite3_icu_init()` entry point.

## Risks
The header has no include guard, so repeated direct inclusion relies on the declaration being identical and harmless. Consumers must link ICU and the extension object or get unresolved symbols. ABI compatibility follows SQLite's `sqlite3 *` and the compiled extension.

## Test Signals
Build tests should include this header from C and C++ translation units, statically link `icu.c`, call `sqlite3IcuInit()`, and verify registered functions such as `regexp`, `lower`, and `icu_load_collation`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/icu/sqliteicu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/intck/sqlite3intck.c -->
# sources/storage-engines/sqlite/ext/intck/sqlite3intck.c

## Purpose
`sqlite3intck.c` implements the incremental integrity-check extension declared by `sqlite3intck.h`. It checks tables and indexes using generated SQL, reports corruption messages without treating corruption as an API error, and allows the check to be paused by ending its read transaction and later resumed from a saved key.

## Important APIs, Types, And Functions
The public API functions are `sqlite3_intck_open()`, `sqlite3_intck_close()`, `sqlite3_intck_step()`, `sqlite3_intck_message()`, `sqlite3_intck_error()`, `sqlite3_intck_unlock()`, and `sqlite3_intck_test_sql()`.

The opaque `sqlite3_intck` struct stores the SQLite handle, database name, current object name, current prepared check statement, restart key text, key column count, corruption message, corrupt-schema flag, error code/message, and the test SQL buffer.

Important private helpers are `intckPrepare()`, `intckPrepareFmt()`, `intckFinalize()`, `intckStep()`, `intckExec()`, `intckMprintf()`, `intckSaveKey()`, `intckFindObject()`, `intckParseCreateIndex()`, `intckGetAutoIndex()`, `intckIsIndex()`, and `intckCheckObjectSql()`.

## Control Flow
Opening allocates the handle, copies the database name (default `main`), and registers a helper SQL function `parse_create_index()` used by generated SQL. Closing finalizes the active statement, unregisters the helper function, frees current object/key/message/test SQL/error strings, and frees the handle.

`sqlite3_intck_step()` clears the previous message, finds the next object if no statement is active, builds object-specific SQL with `intckCheckObjectSql()`, prepares it, then steps one row. The generated SELECT returns rows whose first column is a corruption message or NULL. When a statement finishes, it finalizes it and moves to the next object on the next step. `SQLITE_CORRUPT` while reading schema or scanning an object is converted to a corruption message and normal progress, not a terminal API error.

`intckCheckObjectSql()` disables `PRAGMA automatic_index` while generating checks, decides whether the object is an index, builds a CTE-heavy SQL statement, and restores automatic indexes afterward. For table checks it verifies that required index entries exist. For index checks it verifies that index entries correspond to table rows. It handles WITHOUT ROWID primary keys, partial indexes, expression indexes by parsing CREATE INDEX SQL, collations, and restart WHERE clauses.

`sqlite3_intck_unlock()` saves the current vector key with `intckSaveKey()`, finalizes the active statement to close the read transaction, and leaves the handle ready to regenerate SQL with a resume condition. `sqlite3_intck_test_sql()` returns generated SQL for a named object or current object without running it.

## State And Persistence
The checker maintains transient heap state and one active prepared statement. Its read transaction is held while `pCheck` is active and released by finishing or unlocking. It mutates connection-local function registration for `parse_create_index()` and temporarily toggles `PRAGMA automatic_index`. It does not write database content.

## Dependencies And Integration Points
The module uses public SQLite APIs, `sqlite3intck.h`, and SQLite SQL pragmas (`sqlite_schema`, `pragma_index_list`, `pragma_index_xinfo`, `PRAGMA automatic_index`). The test bridge in `test_intck.c` exposes it to the SQLite Tcl test harness.

## Risks
Generated SQL is complex and must quote identifiers correctly; expression and partial index parsing is intentionally lightweight and can miss exotic syntax. The handle documentation forbids other use of the database connection while active because the module changes helper functions and transaction state. Disabling/restoring `automatic_index` must be robust if errors occur. Restart keys for indexes with DESC and NULL handling are subtle. The close routine unregisters `parse_create_index` with arity 1 even though open registered arity 2, which is a suspicious mismatch worth test attention.

## Test Signals
Tests should compare results with `PRAGMA integrity_check` on normal databases, rowid and WITHOUT ROWID tables, expression indexes, partial indexes, descending indexes, NULL-containing keys, attached databases, corrupt schema reads, object scan corruption, repeated unlock/resume cycles, error-state behavior, and `sqlite3_intck_test_sql()` output. Tests should also verify `automatic_index` is restored.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/intck/sqlite3intck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/intck/sqlite3intck.h -->
# sources/storage-engines/sqlite/ext/intck/sqlite3intck.h

## Purpose
`sqlite3intck.h` declares the public C API for the incremental integrity-check extension. It documents the differences from `PRAGMA integrity_check`, the incremental stepping model, and transaction unlock behavior.

## Important APIs, Types, And Functions
The header defines opaque type `sqlite3_intck` and declares `sqlite3_intck_open()`, `sqlite3_intck_close()`, `sqlite3_intck_step()`, `sqlite3_intck_message()`, `sqlite3_intck_unlock()`, `sqlite3_intck_error()`, and `sqlite3_intck_test_sql()`.

`sqlite3_intck_open()` binds a checker to a database handle and schema name. `sqlite3_intck_step()` advances work and returns `SQLITE_OK`, `SQLITE_DONE`, or an error code. `sqlite3_intck_message()` reports corruption from the last successful step. `sqlite3_intck_unlock()` releases the read transaction. `sqlite3_intck_error()` maps final `SQLITE_DONE` to `SQLITE_OK` and exposes error text. `sqlite3_intck_test_sql()` is test-only SQL introspection.

## Control Flow
The documented usage pattern opens a handle, repeatedly calls `sqlite3_intck_step()` while it returns `SQLITE_OK`, reads any message after each step, calls `sqlite3_intck_error()` at the end, then closes. Callers may interleave `sqlite3_intck_unlock()` to break long checks into multiple transactions.

## State And Persistence
The header owns no state, but it documents that the implementation owns an ongoing check handle and may hold a read transaction. It warns callers not to use the same database handle until the check object is destroyed.

## Dependencies And Integration Points
It includes `sqlite3.h`, uses SQLite result codes, and supports C++ via `extern "C"`. It is consumed by the implementation and the Tcl test module.

## Risks
API misuse risks include using the database handle concurrently, reading messages after errors instead of after `SQLITE_OK`, continuing after an error state, or using the handle after close. The extension is explicitly less thorough than `PRAGMA integrity_check`, so callers must understand its coverage limits.

## Test Signals
Header-level tests should compile from C and C++, validate the documented open/step/message/error/close loop, exercise `unlock()`, and verify NULL/default database-name behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/intck/sqlite3intck.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/intck/test_intck.c -->
# sources/storage-engines/sqlite/ext/intck/test_intck.c

## Purpose
`test_intck.c` is a SQLite Tcl test harness extension for the incremental integrity-check API. It creates Tcl commands that wrap `sqlite3_intck` handles and provides a convenience command to run an entire check and return corruption messages as a Tcl list.

## Important APIs, Types, And Functions
The initializer is `Sqlitetestintck_Init(Tcl_Interp *interp)`, which registers Tcl commands `sqlite3_intck` and `test_do_intck`. `TestIntck` stores a single `sqlite3_intck *`.

`test_sqlite3_intck()` opens a checker for a Tcl SQLite connection and creates a unique object command such as `intck0`. `testIntckCmd()` implements subcommands `close`, `step`, `message`, `error`, `unlock`, and `test_sql`. `test_do_intck()` runs the whole checker and returns all corruption messages. `testIntckFree()` closes the underlying handle when the Tcl command is deleted.

## Control Flow
`sqlite3_intck DB DBNAME` resolves the SQLite pointer with `getDbPointer()`, maps empty DBNAME to default NULL, opens the intck handle, creates a unique Tcl command, and returns that command name. Subcommands call the corresponding C API and convert result codes with `sqlite3ErrName()`.

`test_do_intck DB DBNAME` opens a checker, loops while `sqlite3_intck_step()` returns `SQLITE_OK`, appends non-empty messages, then calls `sqlite3_intck_error()` to distinguish clean completion from API errors. It always closes the checker before returning.

## State And Persistence
The only persistent test state is the Tcl command and its `TestIntck` client data. The underlying intck state is implementation-owned. No database writes are performed by the test wrapper itself.

## Dependencies And Integration Points
The file depends on SQLite test harness headers and functions: `tclsqlite.h`, `getDbPointer()`, `sqlite3ErrName()`, Tcl object APIs, and `sqlite3intck.h`. It is not part of the production SQLite library.

## Risks
If `getDbPointer()` fails after allocating `TestIntck`, the current code returns without freeing that allocation. The `error` subcommand builds a Tcl string with `zErr ? zErr : 0`; passing NULL as a string pointer relies on Tcl behavior and is riskier than using an empty string. The wrapper assumes the database handle is not used outside the check, matching the production API constraint.

## Test Signals
Tcl tests should cover lifecycle command creation/deletion, each subcommand, automatic cleanup, step/message behavior, unlock/resume, `test_sql` with explicit and current objects, full-run `test_do_intck`, open failures, and error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/intck/test_intck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/GNUmakefile -->
# sources/storage-engines/sqlite/ext/jni/GNUmakefile

## Purpose
`ext/jni/GNUmakefile` is a Linux-like bootstrap build for SQLite JNI bindings. It compiles selected Java sources, generates JNI headers, builds `libsqlite3-jni.so`, runs Java tests, builds a jar, generates javadocs, and assembles distribution zip files.

## Important Variables, Targets, And Rules
Key path variables include `JAVA_HOME`, `JDK_HOME`, `dir.top`, `dir.jni`, `dir.src`, `dir.src.c`, `dir.src.jni`, `dir.src.capi`, `dir.src.fts5`, `dir.bld`, and `dir.tests`. Build outputs are `sqlite3-jni.jar`, `src/c/sqlite3-jni.h`, `bld/libsqlite3-jni.so`, class files, javadocs, and dist zips.

Important feature toggles are `enable.fts5`, `enable.tester`, `opt.threadsafe`, `opt.fatal-oom`, `opt.debug`, `opt.metrics`, and `opt.extras`. `SQLITE_OPT` accumulates SQLite/JNI compile flags, including optional FTS5 and extra SQLite virtual tables/features.

Important targets include `all`, class compilation rules, `$(sqlite3.h)`, `$(sqlite3-jni.h)`, `$(package.dll)`, `test-one`, `test-sqllog`, `test-mt`, `test`, `tester`, `multitest`, `jar`, `run-jar`, `doc`, `clean`, `distclean`, `dist`, and `snapshot`.

## Control Flow
The default target builds `all`, which depends on Java class files and the shared library. Java sources are enumerated explicitly to avoid compiling in-progress files. `javac -h` emits JNI headers into the build directory. A generated list `sqlite3-jni.h.in` tracks expected JNI headers from CApi, SQLTester, and optionally FTS5 Java classes. The checked-in aggregate `sqlite3-jni.h` is refreshed by concatenating generated headers only when content changes.

The shared library rule compiles `sqlite3-jni.c` as a shared object with JDK include paths, SQLite include paths, and `SQLITE_OPT`. Tests run Java test classes with `-Djava.library.path=$(dir.bld.c)` and optional `-Xcheck:jni`. Jar packaging writes a sorted file list and creates an executable jar with Tester1 as entry point. Dist packaging copies source/build inputs into a versioned zip using the repository `version-info` tool.

## State And Persistence
The makefile writes build products under `ext/jni/bld`, Java `.class` files alongside sources, generated JNI headers, jar files, javadocs, and distribution archives. It can also update checked-in `src/c/sqlite3-jni.h`, with a warning if FTS5 was disabled. It does not use a separate out-of-tree build directory for class files.

## Dependencies And Integration Points
It depends on a JDK, `jar`, `java`, `javac`, `javadoc`, a C compiler, SQLite canonical `sqlite3.c`/`sqlite3.h`, JNI C sources under `src/c`, Java sources under `src/org/sqlite/jni`, optional test scripts, and top-level SQLite make targets such as `sqlite3.c` and `version-info`.

## Risks
The build assumes a Linux-like system and shared-library naming `libsqlite3-jni.so`. Java class outputs are in the source tree, increasing cleanup risk. `sqlite3-jni.h` is checked in and affected by `enable.fts5`, so accidental regeneration without FTS5 can strip APIs. The JDK include path wildcard is broad. The makefile is marked quick-and-dirty and uses `.NOTPARALLEL` only for selected generated headers, so unmodeled dependencies can matter.

## Test Signals
Build verification should run `make all`, `make test`, `make tester` when scripts exist, `make multitest` for thread/OOM variants, `make jar` plus `run-jar`, and `make clean/distclean`. FTS5-enabled and FTS5-disabled builds should compare generated `sqlite3-jni.h` behavior deliberately.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/jni/GNUmakefile -->
