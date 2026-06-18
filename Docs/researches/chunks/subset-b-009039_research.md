# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 202198-210096

Chunk `subset-b-009039` covers the tail of SQLite FTS3/FTS4 write-side segment maintenance, the FTS3 `snippet()`, `offsets()`, and `matchinfo()` helper implementation, the built-in unicode tokenizer and unicode folding tables, and the opening portion of the JSON/JSONB implementation. This is amalgamated third-party SQLite code embedded under WiredTiger tests, so the code is not a WiredTiger storage engine component directly, but it is part of the vendored SQLite test dependency surface.

## Purpose

The first section continues the FTS3 segment reader and writer machinery. It merges sorted segment b-trees, flushes pending terms, optimizes or rebuilds indexes, performs incremental merge work, updates `%_segdir`, `%_segments`, `%_stat`, `%_docsize`, and `%_content`, and exposes special virtual-table commands such as `optimize`, `rebuild`, `integrity-check`, `merge=`, `automerge=`, and `flush`.

The second section implements FTS3 query presentation functions. `sqlite3Fts3Snippet()` selects and renders text fragments with highlighted hits, `sqlite3Fts3Offsets()` returns token offsets for matching terms in the current row, and `sqlite3Fts3Matchinfo()` returns packed `u32` statistics for ranking and query analysis.

The third section implements the `unicode` FTS tokenizer and unicode helper tables. It tokenizes UTF-8 text into folded, optionally diacritic-stripped tokens, with configurable `tokenchars=` and `separators=` exceptions.

The last section begins SQLite's JSON support. It defines JSONB element type codes, parse/string/cache data structures, text escaping helpers, JSON5 whitespace handling, JSON text-to-JSONB conversion, JSONB validation, and initial JSONB-to-text rendering.

## Important APIs, Types, and Functions

FTS segment iteration and merging:

- `sqlite3Fts3SegReaderStart()` and `fts3SegReaderStart()` initialize a `Fts3MultiSegReader` against an optional `Fts3SegFilter`, seeking each segment to the requested term or prefix.
- `sqlite3Fts3MsrIncrStart()` starts an incremental doclist reader for one term, initializes docid positions for matching segment readers, and sorts by docid order according to `Fts3Table.bDescIdx`.
- `sqlite3Fts3MsrIncrRestart()` resets an incremental reader so a later normal segment-reader step can rebuild the full doclist.
- `sqlite3Fts3SegReaderStep()` is the central merge step. It advances segment readers, groups equal terms, merges doclists, applies column filters, honors `FTS3_SEGMENT_IGNORE_EMPTY`, `FTS3_SEGMENT_REQUIRE_POS`, `FTS3_SEGMENT_PREFIX`, `FTS3_SEGMENT_SCAN`, and `FTS3_SEGMENT_FIRST`, and returns `SQLITE_ROW` for each merged term.
- `sqlite3Fts3SegReaderFinish()` frees all segment readers and buffers in a multi-segment cursor.
- `fts3SegmentMerge()` merges pending, one level, or all levels into a new segment using `SegmentWriter`, deletes old segdir rows, flushes the writer, and may promote small higher-level segments.
- `sqlite3Fts3PendingTermsFlush()`, `sqlite3Fts3Optimize()`, `fts3DoOptimize()`, and `fts3DoRebuild()` are the high-level maintenance operations for pending-term flush, full optimize, and rebuild.

Incremental merge support:

- `Blob`, `NodeWriter`, `NodeReader`, and `IncrmergeWriter` model appendable segment construction and node traversal.
- `nodeReaderInit()`, `nodeReaderNext()`, and `nodeReaderRelease()` parse prefix-compressed segment b-tree nodes.
- `fts3IncrmergeWriter()` allocates an appendable output segment by reserving block ranges in `%_segments` and placing a zero-length marker at `end_block`.
- `fts3IncrmergeLoad()` reopens an appendable segment if the next input key sorts after the segment's last key.
- `fts3IncrmergeAppend()`, `fts3IncrmergePush()`, and `fts3IncrmergeRelease()` append leaf terms/doclists, maintain internal nodes, flush blocks, and write a new `%_segdir` record.
- `fts3IncrmergeChomp()`, `fts3TruncateSegment()`, `fts3TruncateNode()`, `fts3RemoveSegdirEntry()`, and `fts3RepackSegdirLevel()` delete or truncate input segments after partial merge progress.
- `sqlite3Fts3Incrmerge()` coordinates repeated incremental merge passes with `%_stat` merge hints via `fts3IncrmergeHintLoad()`, `fts3IncrmergeHintPush()`, `fts3IncrmergeHintPop()`, and `fts3IncrmergeHintStore()`.

FTS update and integrity APIs:

- `sqlite3Fts3UpdateMethod()` is the virtual table `xUpdate` implementation. It handles special command inserts, delete/update/insert paths, conflict handling, `%_content` writes, pending term indexing, docsize writes, and FTS4 doc-total updates.
- `fts3DeleteByRowid()` removes an existing row from the index and subsidiary tables, with a full cleanup path if the table becomes empty.
- `sqlite3Fts3IntegrityCheck()` and `fts3DoIntegrityCheck()` compare a checksum calculated from the FTS index with a checksum calculated by re-tokenizing content rows.
- `fts3SpecialInsert()` dispatches user commands embedded as `INSERT INTO tbl(tbl) VALUES(...)`.

Snippet, offsets, and matchinfo:

- Matchinfo format flags are defined as `p`, `c`, `n`, `a`, `l`, `s`, `x`, `y`, and `b`, with default `"pcx"`.
- `MatchinfoBuffer` caches global matchinfo data with two in-object output slots, reference bits, and fallback heap allocation when both slots are in use.
- `sqlite3Fts3ExprIterate()` walks phrase nodes, excluding the right side of `NOT`.
- `fts3BestSnippet()`, `fts3SnippetNextCandidate()`, `fts3SnippetDetails()`, `fts3SnippetShift()`, and `fts3SnippetText()` select and render highlighted snippet fragments.
- `sqlite3Fts3Offsets()` uses `TermOffset` iterators and tokenization of the current row text to render `"column term start length"` entries.
- `fts3MatchinfoValues()` populates the matchinfo result for global and row-local statistics, delegating to phrase stats, local hit counts, LCS computation, doc totals, and docsize reads.
- `sqlite3Fts3Matchinfo()` applies the default format and closes FTS segment resources after result generation.

Unicode tokenizer:

- `unicode_tokenizer` stores diacritic mode plus sorted exception codepoints.
- `unicode_cursor` stores the input buffer, current byte offset, token index, and reusable output token buffer.
- `unicodeCreate()` parses `remove_diacritics=0|1|2`, `tokenchars=...`, and `separators=...`.
- `unicodeNext()` scans UTF-8, skips separators, folds case through `sqlite3FtsUnicodeFold()`, strips diacritics when configured, and returns token text plus byte offsets and token position.
- `sqlite3Fts3UnicodeTokenizer()` exposes the `sqlite3_tokenizer_module`.
- `sqlite3FtsUnicodeIsalnum()`, `sqlite3FtsUnicodeIsdiacritic()`, `sqlite3FtsUnicodeFold()`, and `remove_diacritic()` implement generated unicode classification and folding tables.

JSON and JSONB startup:

- JSONB type codes `JSONB_NULL` through `JSONB_OBJECT` define binary JSON element tags.
- `JsonCache` caches up to four text-to-JSONB parse translations in `sqlite3_get_auxdata()`.
- `JsonString` is a string accumulator backed by inline space first and `sqlite3RCStr` when it grows.
- `JsonParse` owns or references JSONB blobs, original JSON text, edit state, parse error state, nesting depth, and reference count.
- `jsonCacheInsert()` and `jsonCacheSearch()` manage an LRU parse cache.
- `jsonAppendString()`, `jsonAppendSqlValue()`, `jsonReturnString()`, and `jsonReturnStringAsBlob()` serialize SQL values or generated JSON strings as text JSON or JSONB.
- `json5Whitespace()` recognizes JSON5 whitespace and comments.
- `jsonBlobAppendNode()`, `jsonBlobChangePayloadSize()`, and `jsonbPayloadSize()` encode and decode JSONB node headers.
- `jsonbValidityCheck()` recursively validates JSONB elements, primitive payload syntax, array children, object key/value pairing, and maximum nesting depth.
- `jsonTranslateTextToBlob()` is a recursive descent parser from JSON/JSON5 text to SQLite JSONB; `jsonConvertTextToBlob()` wraps it for complete-input parsing.
- `jsonTranslateBlobToText()` begins rendering JSONB back to canonical JSON text.

## Control Flow

FTS segment reads use a sorted array of `Fts3SegReader` objects. `sqlite3Fts3SegReaderStep()` advances the first `nAdvance` readers, resorts, checks EOF and term filters, identifies all readers on the same term, and either returns a single doclist directly or merges multiple doclists into `Fts3MultiSegReader.aBuffer`. During merging it decodes first docids, sorts readers by current docid, coalesces duplicate docids, applies column filters, checks ascending or descending docid order, and writes varint deltas and optional position lists.

Full segment merge starts by constructing a multi-segment cursor for a level or all segments, selecting a destination absolute level and index, scanning merged terms with `sqlite3Fts3SegReaderStep()`, writing each term/doclist through `fts3SegWriterAdd()`, deleting old segment directory rows, flushing the writer, then optionally promoting small segments into the new level.

Incremental merge is quota based. `sqlite3Fts3Incrmerge()` loads a merge hint, finds a level with enough segments, optionally overrides that level from the hint, opens readers on the oldest segments, starts a filtered merge, appends term/doclist pairs until its leaf-page work quota is reached, then either deletes fully consumed segments or truncates partially consumed input segments at the current term. If input remains, it pushes a hint for the next call. Output segments may be appendable across calls, using reserved block space and persisted `end_block` size metadata.

`sqlite3Fts3UpdateMethod()` first detects special-command inserts and exits through command handlers. Normal updates allocate docsize delta arrays, acquire a write lock, handle rowid conflict policy, delete the old row for delete/update, insert the new content row for insert/update, index terms into pending terms, write `%_docsize` if enabled, and update FTS4 `%_stat` document totals.

Snippet flow is query-position-list driven first, text-tokenizer driven second. `fts3BestSnippet()` loads phrase doclists, finds per-column positions, scores candidate token windows by phrase coverage, and records a fragment. `sqlite3Fts3Snippet()` tries one to four fragments until all seen phrases are covered. `fts3SnippetText()` then retokenizes the row column, shifts the fragment for better surrounding context, emits ellipses and original intervening text, and wraps highlighted tokens.

Matchinfo flow caches global data per cursor/format. `fts3GetMatchinfo()` validates the format string and allocates `MatchinfoBuffer` on first use, computes global fields once, then allocates an output slot for each call and fills row-local fields. `fts3MatchinfoValues()` advances the output pointer after each directive according to `fts3MatchinfoSize()`.

The unicode tokenizer flow is linear over UTF-8 bytes. It skips non-token characters, accumulates token characters and trailing diacritics, expands a reusable output buffer, folds each codepoint, optionally drops standalone diacritic effects, and returns `SQLITE_DONE` at input end.

JSON parsing flow appends placeholder JSONB array/object nodes with maximum possible payload, recursively parses children, then patches payload length with `jsonBlobChangePayloadSize()`. Primitive parsing selects canonical or JSON5-specific JSONB types. Top-level conversion verifies trailing input is only accepted whitespace/comments, and optional debug self-check validates the generated JSONB tree.

## State and Persistence Behavior

FTS persistent state is stored in SQLite shadow tables:

- `%_segments` stores segment b-tree blocks by block id. Incremental merge uses zero-length entries as appendable segment reservation markers.
- `%_segdir` stores segment metadata: level, index, start block, leaves-end block, end block plus optional leaf-data byte count, and root node.
- `%_stat` stores FTS4 document totals, automerge settings, and incremental merge hints.
- `%_docsize` stores per-column token counts for each document as a varint blob.
- `%_content` stores row content for non-external-content tables.

In-memory FTS state includes pending term hashes, segment-reader buffers, incremental writer node buffers, deferred token lists on `Fts3Cursor`, and `MatchinfoBuffer` caches tied to the cursor. Most helpers follow SQLite's prepared-statement reuse pattern through `fts3SqlStmt()` and clear/reuse statements with `sqlite3_reset()`.

JSON persistent state is not written directly in this chunk, but values are returned as SQLite text or BLOB results. Parse cache state is attached to the SQL function context via auxdata and is invalidated by SQLite when appropriate. `JsonParse` reference counting (`nJPRef`) protects cached parse objects while allowing result strings and parse blobs to share RCStr-managed memory.

## Dependencies and Integration Points

This code depends heavily on internal SQLite and FTS3 infrastructure defined elsewhere in the amalgamation: `Fts3Table`, `Fts3Cursor`, `Fts3Expr`, `Fts3Phrase`, `Fts3PhraseToken`, `Fts3MultiSegReader`, `Fts3SegReader`, `Fts3SegFilter`, tokenizer modules, SQL statement identifiers such as `SQL_SELECT_LEVEL`, and helpers such as `fts3SqlStmt()`, `fts3WriteSegment()`, `fts3WriteSegdir()`, `sqlite3Fts3ReadBlock()`, `fts3DeleteSegment()`, `fts3PendingTermsAdd()`, `fts3InsertTerms()`, `sqlite3Fts3EvalPhrasePoslist()`, and `sqlite3Fts3EvalPhraseStats()`.

The FTS virtual table integration points are `sqlite3Fts3UpdateMethod()`, `sqlite3Fts3Optimize()`, `sqlite3Fts3Snippet()`, `sqlite3Fts3Offsets()`, `sqlite3Fts3Matchinfo()`, deferred-token helpers, and `sqlite3Fts3UnicodeTokenizer()`. They interact with SQLite's `sqlite3_context`, `sqlite3_value`, `sqlite3_stmt`, vtab conflict policy, savepoints, SQL result APIs, and tokenizer API.

The JSON code depends on SQLite core allocation, RCStr, auxdata, SQL value/result APIs, charset macros (`SQLITE_ASCII`/`SQLITE_EBCDIC`), numeric formatting, identifier checks, and JSON-related flags supplied as SQL function user data. This chunk introduces core helpers that later JSON functions use for `json()`, `jsonb()`, `json_extract()`, mutation functions, and aggregate construction.

## Risks and Edge Cases

- Segment/doclist corruption is detected through ordering checks, prefix-compression sanity checks, malformed varints, out-of-range child pointers, invalid node heights, bad JSONB sizes, and maximum nesting-depth limits. Many failures map to `FTS_CORRUPT_VTAB` or `SQLITE_CORRUPT_VTAB`.
- `sqlite3Fts3SegReaderStep()` has multiple behavioral modes controlled by flags; regressions here can affect term lookup, prefix scans, column-filtered queries, phrase queries, and optimize/merge output.
- Descending index mode (`bDescIdx`) reverses docid delta expectations. Incorrect comparison or delta encoding can corrupt doclists.
- Incremental merge is persistence-sensitive. Appendable segment reservation, negative `nLeafData` markers during partial merge, merge hints, and segment truncation/repacking must stay consistent across interrupted calls.
- `fts3IncrmergeHintPop()` assumes a well-formed varint tail; corrupt hints intentionally return `FTS_CORRUPT_VTAB`.
- `fts3UpdateDocTotals()` saturates counters to zero on underflow-like cases rather than allowing unsigned wrap. Any change to docsize accounting can affect FTS4 ranking and `matchinfo()`.
- Snippet and offsets retokenize stored text and assume tokenizer position/offset behavior matches indexing. External-content tables can return content that no longer matches the index; some offset EOF cases only become corruption for non-external-content tables.
- Matchinfo buffers use custom ownership callbacks and reference bits. Returning one of the two in-buffer slots requires `fts3MIBufferFree()` to derive the owning object from a stored offset.
- The unicode tokenizer has subtle compatibility behavior around diacritic removal mode `2`, exception inversion, and UTF-8 invalid codepoint handling. Generated unicode tables should be treated as data, not hand-maintained logic.
- JSON parsing accepts JSON5 extensions but canonical output remains JSON. The text parser uses negative internal return codes for delimiters; error-location handling depends on preserving `pParse->iErr`.
- JSONB validation is intentionally structural and not a complete semantic guarantee for all malformed blobs; later rendering may still produce errors or odd output from malformed JSONB.
- JSON string and blob builders rely on careful capacity checks with `u32`/`u64` sizes. OOM flags on `JsonString` and `JsonParse` must be propagated before using partially built buffers.

## Test Signals

Useful behavioral signals for this chunk include:

- FTS3/FTS4 tests that insert, update, delete, rebuild, optimize, flush pending terms, and run `merge=A,B` and `automerge=X`.
- Queries over tables with multiple segment levels, prefix indexes, descending docid indexes, column filters, empty doclists, and external content.
- Integrity-check tests that compare index checksums to content re-tokenization across multiple language ids and prefix indexes.
- Snippet tests for multi-column tables, multi-phrase queries, `NOT` subtrees, negative and positive token counts, NULL columns, punctuation preservation, and fragment ellipsis placement.
- Offsets tests that verify byte offsets from tokenizer output and behavior when incremental doclists must be cancelled.
- Matchinfo tests for all format flags (`pcnalxybs`), FTS3 versus FTS4 restrictions, deferred tokens, docsize/doc-total availability, and global cache reuse across rows.
- Unicode tokenizer tests for UTF-8 decoding, case folding, diacritic stripping modes, custom token/separator exceptions, malformed UTF-8 replacement, and byte offset reporting.
- JSON tests for canonical JSON, JSON5 whitespace/comments/strings/numbers, nesting-depth failure, malformed JSONB, JSONB header length forms, string escaping, SQL BLOB rejection in JSON text builders, and auxdata cache reuse.

## Chunk Boundaries and Cross-References

This chunk begins mid-function after earlier FTS3 segment-reader setup code, so helpers like `fts3SegReaderNext()`, `fts3SegReaderTermCmp()`, `fts3SegReaderSort()`, `fts3SegReaderFirstDocid()`, and the FTS SQL statement enum are defined before the chunk. It ends inside `jsonTranslateBlobToText()`, so JSONB-to-text rendering, path lookup, JSON SQL function entry points, JSON aggregate code, and registration logic continue in later chunks.
