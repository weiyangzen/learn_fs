# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 259630-262899

## Scope

This chunk is the end of SQLite's amalgamated FTS5 implementation and the beginning/end of two auxiliary virtual table extensions. It starts inside the tail of FTS5 tokenizer code, then covers the complete built-in Porter tokenizer wrapper, trigram tokenizer, generated Unicode folding/category tables, FTS5 varint helpers, the `fts5vocab` virtual table module, the `sqlite_stmt` virtual table module, and the final `sqlite3_sourceid()` export.

The code is compiled conditionally as part of `sqlite3.c`: the FTS5 portion is guarded by the surrounding `!defined(SQLITE_CORE) || defined(SQLITE_ENABLE_FTS5)` block, and the statement virtual table is guarded by `!defined(SQLITE_CORE) || defined(SQLITE_ENABLE_STMTVTAB)` plus `!SQLITE_OMIT_VIRTUALTABLE`.

## Purpose

The FTS5 tokenizer code provides built-in tokenization services for full text search:

- The Porter tokenizer wraps an underlying tokenizer, usually `unicode61`, and stems each token before passing it to FTS5.
- The trigram tokenizer emits overlapping three-codepoint tokens for substring-oriented indexing and can advertise LIKE/GLOB pattern support.
- The Unicode helpers fold case, optionally remove diacritics, classify Unicode codepoints, and derive ASCII token-character tables for the `unicode61` tokenizer.

The varint helpers serialize and deserialize SQLite-style variable-length integers for FTS5 internal index records.

The `fts5vocab` module exposes an existing FTS5 index through virtual tables with `col`, `row`, or `instance` views. It reads FTS5 index iterators directly and converts term/doc/position-list data into SQL-visible rows.

The `sqlite_stmt` module exposes prepared statements on a connection as an eponymous virtual table, reporting SQL text and statement status counters.

## Important APIs, Types, and Functions

### Porter tokenizer

- `FTS5_PORTER_MAX_TOKEN` limits tokens subject to stemming to 64 bytes. Larger or very short tokens are passed through unchanged.
- `PorterTokenizer` stores the v2 tokenizer interface copied from the wrapped tokenizer, the wrapped `Fts5Tokenizer`, and a reusable stemming buffer.
- `fts5PorterCreate()` resolves the base tokenizer with `fts5_api.xFindTokenizer_v2()`, defaults to `unicode61`, forwards remaining arguments to the base tokenizer, and copies the tokenizer v2 method table.
- `fts5PorterDelete()` delegates destruction to the wrapped tokenizer's `xDelete()` before freeing its own object.
- `PorterContext` carries the caller's token callback and buffer through the wrapper.
- `fts5PorterCb()` implements the actual stemming pipeline and forwards either the stemmed token or the original token.
- Generated rule functions `fts5PorterStep1B()`, `fts5PorterStep1B2()`, `fts5PorterStep2()`, `fts5PorterStep3()`, and `fts5PorterStep4()` apply suffix rewrites. Hand-written helpers implement Step 1A, Step 1C, Step 5a, and Step 5b.
- Condition helpers `fts5Porter_MGt0()`, `fts5Porter_MGt1()`, `fts5Porter_MEq1()`, `fts5Porter_Ostar()`, `fts5Porter_Vowel()`, and `fts5Porter_MGt1_and_S_or_T()` implement Porter algorithm predicates over a mutable byte buffer.

### Trigram tokenizer and tokenizer registration

- `TrigramTokenizer` contains `bFold` and `iFoldParam`, controlling case folding and diacritic removal.
- `fts5TriCreate()` parses option pairs: `case_sensitive` must be `0` or `1`, and `remove_diacritics` must be `0`, `1`, or `2`. Diacritic removal is rejected when `case_sensitive=1`.
- `fts5TriTokenize()` reads UTF-8 codepoints, optionally folds/removes diacritics via `sqlite3Fts5UnicodeFold()`, skips folded-away diacritic marks, and emits overlapping 3-character tokens with input byte offsets.
- `sqlite3Fts5TokenizerPattern()` identifies trigram tokenizer support for pattern pushdown: folded trigrams support LIKE, case-sensitive trigrams support GLOB, and diacritic-removing trigrams do not advertise pattern support.
- `sqlite3Fts5TokenizerPreload()` detects tokenizer configs whose first argument is `trigram`, so planning can load the tokenizer before `xBestIndex()`.
- `sqlite3Fts5TokenizerInit()` registers `unicode61`, `ascii`, `trigram`, and the v2 `porter` tokenizer with the `fts5_api`.

### Unicode helpers

- `fts5_remove_diacritic()` maps many lowercase diacritic codepoints to ASCII letters using generated `aDia[]` and `aChar[]` tables. The `bComplex` argument controls whether complex mappings marked with the high bit are allowed.
- `sqlite3Fts5UnicodeIsdiacritic()` recognizes combining diacritical marks in the 768-817 range using bitmasks.
- `sqlite3Fts5UnicodeFold()` lowercases ASCII, many BMP ranges from generated case-folding tables, one non-BMP range, and optionally removes diacritics.
- `sqlite3Fts5UnicodeCatParse()` parses two-letter Unicode category selectors such as `Ll`, `Nd`, `P*`, or `L*` into a 32-entry category mask array.
- `aFts5UnicodeBlock`, `aFts5UnicodeMap`, and `aFts5UnicodeData` are generated compressed Unicode category tables.
- `sqlite3Fts5UnicodeCategory()` binary-searches the generated maps to return a compact category code for a codepoint under `1<<20`.
- `sqlite3Fts5UnicodeAscii()` populates a 128-byte ASCII token-character table from a category mask.

### FTS5 varints

- `sqlite3Fts5GetVarint32()` decodes one-, two-, and three-byte varints inline, falling back to `sqlite3Fts5GetVarint()` for larger encodings, then masks to 31 bits.
- `sqlite3Fts5GetVarint()` decodes 64-bit varints in one to nine bytes, with hand-unrolled cases and precomputed masks `SLOT_2_0` and `SLOT_4_2_0`.
- `fts5PutVarint64()` is the noinline slow path for serializing values larger than 14 bits.
- `sqlite3Fts5PutVarint()` fast-paths one- and two-byte writes and delegates larger values.
- `sqlite3Fts5GetVarintLen()` returns the encoded length for values known to be at least 128.

### fts5vocab virtual table

- `Fts5VocabTable` is the vtab object. It stores the target FTS5 table/database names, database handle, `Fts5Global`, vocabulary type, and a recursion guard `bBusy`.
- `Fts5VocabCursor` is the cursor object. It owns the lock-holding statement, `Fts5Table`, index iterator, referenced FTS5 structure, optional upper-bound term, selected columns mask, per-column count/doc arrays, rowid, current term buffer, and instance-position state.
- `FTS5_VOCAB_COL`, `FTS5_VOCAB_ROW`, and `FTS5_VOCAB_INSTANCE` select output schema and iteration behavior.
- `fts5VocabTableType()` dequotes and validates `col`, `row`, or `instance`.
- `fts5VocabInitVtab()` implements both create/connect. It validates arguments, declares the schema, allocates one object containing both table and database names, dequotes identifiers, and stores global state.
- `fts5VocabBestIndexMethod()` recognizes term equality and range constraints, records them in `idxNum`, assigns argument indexes, estimates cost, and consumes ascending `ORDER BY term`.
- `fts5VocabOpenMethod()` resolves the target FTS5 table by preparing a synthetic `MATCH '*id'` query, stepping it to obtain a cursor id, translating that id through `sqlite3Fts5TableFromCsrid()`, flushing pending FTS5 data to disk, and allocating per-column count arrays.
- `fts5VocabFilterMethod()` resets cursor state, extracts term equality/lower/upper constraints, starts an `sqlite3Fts5IndexQuery()`, references the current FTS5 structure for change detection, and positions the cursor.
- `fts5VocabNextMethod()` advances through terms and rowids, accumulates document and occurrence counts from position lists, respects `detail=full`, `detail=columns`, and `detail=none`, and handles the `col`, `row`, and `instance` table variants.
- `fts5VocabColumnMethod()` materializes SQL-visible values for term, column name, document counts, instance rowids, and offsets.
- `sqlite3Fts5VocabInit()` registers the module as `fts5vocab` with `sqlite3_create_module_v2()`.

### sqlite_stmt virtual table

- `StmtRow` stores a snapshot row: rowid, SQL text, integer columns, and next pointer.
- `stmt_vtab` stores the owning `sqlite3*`; `stmt_cursor` stores the same connection and current linked-list row.
- `stmtConnect()` declares schema `sql,ncol,ro,busy,nscan,nsort,naidx,nstep,reprep,run,mem` and stores the connection.
- `stmtFilter()` snapshots all prepared statements reachable from `sqlite3_next_stmt()`, copies SQL text, and reads statement counters using `sqlite3_stmt_status()`.
- `stmtNext()`, `stmtColumn()`, `stmtRowid()`, and `stmtEof()` scan the linked-list snapshot.
- `sqlite3StmtVtabInit()` registers the `sqlite_stmt` module.
- `sqlite3_stmt_init()` is the extension entry point when built outside `SQLITE_CORE`.
- `sqlite3_sourceid()` returns the amalgamation's `SQLITE_SOURCE_ID`.

## Control Flow

Porter tokenization is a wrapper around another tokenizer. `fts5PorterTokenize()` builds a `PorterContext` and calls the wrapped tokenizer's `xTokenize()`, substituting `fts5PorterCb()` as the callback. For each emitted token, `fts5PorterCb()` copies eligible tokens into the local buffer, runs Porter steps in sequence, and calls the original callback with the resulting stem. Tokens shorter than 3 bytes or longer than `FTS5_PORTER_MAX_TOKEN` bypass stemming.

Trigram tokenization is a sliding window over UTF-8 codepoints. `fts5TriTokenize()` fills a three-codepoint buffer, records byte offsets for each codepoint, emits the current trigram, then removes the first codepoint and appends the next folded codepoint. Combining marks that fold to zero are skipped. End-of-input stops after the last complete trigram has been emitted.

Unicode classification and folding are table-driven. Folding lowercases ASCII directly; for BMP characters it binary-searches generated case-fold ranges, computes the lower-case mapping by offset, and optionally passes the result through diacritic removal. Category lookup similarly binary-searches block/map arrays and decodes packed category/range data.

FTS5 varint decoding uses fast-path unrolled branches. The first clear high bit determines the number of bytes. The 32-bit routine inlines the common first three cases and calls the 64-bit routine only for rare longer encodings. The put routine serializes from least significant groups into a temporary buffer for the general case, then reverses into output.

`fts5vocab` query execution starts with virtual table connect/create, where the target FTS5 table name and type are captured. Opening a cursor resolves the live FTS5 table by using an internal MATCH query and cursor id lookup, then flushes pending index changes. Filtering starts an index scan for equality, lower-bound, or full scan. The next method groups consecutive index rows with the same term for `row` and `col` modes, while `instance` mode walks individual position-list entries.

`sqlite_stmt` execution snapshots state at filter time. The cursor owns a linked list of `StmtRow` objects created by walking `sqlite3_next_stmt()`. Subsequent `xNext()` calls free consumed rows, so the output is stable for the scan and cleanup is incremental.

## State and Persistence Behavior

The tokenizer objects are per-tokenizer-instance heap allocations. `PorterTokenizer` owns the wrapped tokenizer instance and a reusable buffer; `TrigramTokenizer` owns only option flags. Neither persists data to disk.

Unicode tables are static read-only generated data embedded in the amalgamation. They are process-local constants and have no runtime persistence.

The FTS5 varint functions operate on caller-provided memory and do not own state.

`fts5vocab` is read-only but observes persistent FTS5 index state. `fts5VocabOpenMethod()` explicitly calls `sqlite3Fts5FlushToDisk()` after resolving the target FTS5 table, so pending in-memory FTS5 changes are flushed before vocabulary scanning. The cursor also stores a referenced FTS5 structure pointer and `fts5VocabNextMethod()` calls `sqlite3Fts5StructureTest()` before advancing, detecting index structure changes while the scan is active. The `pStmt` member is kept open to hold the target table/cursor relationship for the lifetime of the vocab cursor.

`sqlite_stmt` is read-only and snapshots transient prepared-statement metadata into heap rows. Counters are read without reset by passing zero to `sqlite3_stmt_status()`. The snapshot rows are freed as the scan advances or when the cursor closes.

## Dependencies and Integration Points

This chunk depends heavily on surrounding SQLite and FTS5 internals:

- SQLite allocator and utility APIs: `sqlite3_malloc`, `sqlite3_malloc64`, `sqlite3_free`, `sqlite3_mprintf`, `sqlite3_stricmp`, `sqlite3_declare_vtab`, `sqlite3_create_module`, `sqlite3_create_module_v2`, `sqlite3_prepare_v2`, `sqlite3_step`, `sqlite3_finalize`, `sqlite3_value_text`, `sqlite3_value_bytes`, and result APIs.
- FTS5 tokenizer APIs: `fts5_api`, `fts5_tokenizer`, `fts5_tokenizer_v2`, `Fts5Tokenizer`, `Fts5TokenizerConfig`, and the `xCreateTokenizer`/`xCreateTokenizer_v2` registration path.
- FTS5 internals: `Fts5Global`, `Fts5Table`, `Fts5Index`, `Fts5IndexIter`, `Fts5Buffer`, `Fts5Config`, `sqlite3Fts5IndexQuery()`, `sqlite3Fts5IterNextScan()`, `sqlite3Fts5IterTerm()`, `sqlite3Fts5IterEof()`, `sqlite3Fts5StructureRef()`, `sqlite3Fts5StructureRelease()`, `sqlite3Fts5StructureTest()`, `sqlite3Fts5BufferSet()`, `sqlite3Fts5BufferFree()`, and `sqlite3Fts5FlushToDisk()`.
- UTF-8 and FTS5 macros: `READ_UTF8`, `WRITE_UTF8`, `FTS5_SKIP_UTF8`, `FTS5_POS2COLUMN`, `FTS5_POS2OFFSET`, `MIN`, `ArraySize`, `UNUSED_PARAM`, and `UNUSED_PARAM2`.
- Statement inspection APIs: `sqlite3_next_stmt`, `sqlite3_sql`, `sqlite3_column_count`, `sqlite3_stmt_readonly`, `sqlite3_stmt_busy`, and `sqlite3_stmt_status`.

The chunk is integrated into SQLite by module registration functions. `sqlite3Fts5TokenizerInit()` and `sqlite3Fts5VocabInit()` are called from the surrounding FTS5 initialization path; `sqlite3StmtVtabInit()` is called by core or extension initialization; `sqlite3_stmt_init()` is the external extension entry point for loadable builds.

## Risks and Edge Cases

- Porter stemming assumes lowercase ASCII-like token bytes from the base tokenizer. It operates byte-wise, not Unicode-aware. If a non-lowercase or multi-byte token reaches it, suffix rules may not behave linguistically, but the wrapper normally uses tokenizers that fold first.
- `fts5PorterCb()` uses a fixed buffer in `PorterTokenizer`; the max-token guard avoids overflow. Tokens over 64 bytes are not stemmed, so behavior differs for long terms.
- Many generated Porter step functions index `aBuf[nBuf-2]`; the caller only invokes them after the minimum token-length guard and prior transformations that maintain non-empty buffers.
- `fts5TriTokenize()` emits only complete three-codepoint windows. Inputs with fewer than three non-diacritic folded codepoints produce no tokens, which is intentional but important for MATCH behavior.
- Trigram options deliberately reject `remove_diacritics` with `case_sensitive=1`; changing this could break LIKE/GLOB pattern compatibility assumptions.
- Unicode folding/category data is generated. Table corruption or regeneration mismatches would affect token boundaries and index compatibility across SQLite versions.
- `sqlite3Fts5UnicodeCategory()` returns category 0 for codepoints at or above `1<<20`, so tokenization for very high codepoints is intentionally conservative in this table.
- Varint functions assume sufficient readable/writable bytes supplied by callers. They are low-level helpers without bounds parameters.
- `fts5vocab` depends on the internal `MATCH '*id'` mechanism and cursor-id lookup. If the target table cannot be resolved, it reports `no such fts5 table`.
- `fts5vocab` uses `bBusy` to prevent recursive resolution of the target table; recursive definitions return an error.
- `fts5vocab` count semantics vary with FTS5 detail mode. With `detail=none`, column names and offsets are not available, and instance iteration stops early.
- Position-list decoding can detect impossible column indexes and return `FTS5_CORRUPT`.
- `stmtFilter()` materializes all prepared statements at once. A connection with many large SQL strings can allocate noticeable memory during a scan.
- `sqlite_stmt` reports live statement status counters at snapshot time. Values may change after snapshot but before the caller reads all rows; the virtual table intentionally reports the snapshot, not a live view.

## Test Signals

Useful tests for this chunk include:

- FTS5 tokenizer creation tests for `porter`, with default `unicode61` and explicit wrapped tokenizer arguments.
- Porter stemming golden cases for Step 1A through Step 5, including pass-through behavior for tokens shorter than 3 bytes and longer than 64 bytes.
- Trigram tokenizer tests for ASCII text, UTF-8 multibyte text, folded case, diacritic removal, short input, and byte-offset correctness.
- Planner tests confirming `sqlite3Fts5TokenizerPattern()` enables LIKE for folded trigrams, GLOB for case-sensitive trigrams, and no pattern support when diacritic removal is active.
- Unicode folding/category tests against known codepoints, combining diacritic handling, ASCII table generation, and invalid/very high codepoints.
- FTS5 varint round-trip tests around 1-, 2-, 3-, 4-, 5-, and 9-byte boundaries, plus `sqlite3Fts5GetVarint32()` fallback paths.
- `fts5vocab` SQL tests for `col`, `row`, and `instance` schemas; term equality/range constraints; `ORDER BY term`; and all FTS5 detail modes.
- `fts5vocab` corruption or defensive tests for invalid position-list column values and index-structure changes during a cursor scan.
- `sqlite_stmt` tests that prepare several statements and verify SQL text, column counts, read-only flags, busy status, and statement counters exposed by the virtual table.
- Extension-build tests for `sqlite3_stmt_init()` and core-build tests for `sqlite3StmtVtabInit()` registration.

## Chunk Boundaries and Follow-up for Merge

The first lines of this chunk continue from earlier `unicode61` tokenization logic, so the merged per-file report should connect this chunk to the preceding tokenizer definitions and tokenizer config parsing. The FTS5 section ends here with `sqlite3Fts5VocabInit()` and the composite-file trailer. The following code starts and completes `stmt.c`, then closes the amalgamation with `sqlite3_sourceid()`.
