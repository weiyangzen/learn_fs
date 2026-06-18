# sources/storage-engines/foundationdb/contrib/sqlite/sqlite3.amalgamation.c lines 105143-110689

## Scope And Purpose

This chunk covers four adjacent areas of the FoundationDB vendored SQLite amalgamation:

- the tail of FTS3 `fts3_snippet.c`, including NEAR doclist trimming, `snippet()`, `offsets()`, and `matchinfo()`;
- the R-tree virtual table module implementation, including node persistence tables, query planning/filtering, insert/delete, split/reinsert, and module registration;
- the ICU extension and ICU-backed FTS3 tokenizer;
- a FoundationDB-added `tryReadEveryDbPage()` diagnostic/integrity helper that scans every database page through the pager read path.

The code is mostly optional feature code behind `SQLITE_ENABLE_FTS3`, `SQLITE_ENABLE_RTREE`, and `SQLITE_ENABLE_ICU`, except the final page-scanning helper, which is exported in the local `sqlite3.h` and reaches into SQLite pager/btree internals.

## Important APIs, Types, And Functions

FTS3 snippet and matchinfo code centers on `Fts3Cursor`, `Fts3Table`, `Fts3Expr`, `Fts3Phrase`, `SnippetIter`, `SnippetPhrase`, `SnippetFragment`, `MatchInfo`, `LcsIterator`, `TermOffset`, and `TermOffsetCtx`. Important functions include `fts3ExprNearTrim()`, `fts3ExprLoadDoclists()`, `fts3BestSnippet()`, `fts3SnippetText()`, `sqlite3Fts3Snippet()`, `sqlite3Fts3Offsets()`, `fts3MatchinfoValues()`, `fts3GetMatchinfo()`, and `sqlite3Fts3Matchinfo()`.

The FTS3 helpers use `sqlite3Fts3ExprLoadDoclist()`, `sqlite3Fts3ExprLoadFtDoclist()`, `sqlite3Fts3FindPositions()`, `sqlite3Fts3GetVarint()`, `fts3GetDeltaPosition()`, `sqlite3Fts3SelectDoctotal()`, `sqlite3Fts3SelectDocsize()`, tokenizer module callbacks, SQLite scalar result APIs, and `sqlite3Fts3SegmentsClose()`.

The R-tree module defines `Rtree`, `RtreeCursor`, `RtreeNode`, `RtreeCell`, `RtreeConstraint`, `RtreeMatchArg`, `RtreeGeomCallback`, and `RtreeCoord`. Its virtual table entry points are wired through `rtreeModule`: `rtreeCreate`, `rtreeConnect`, `rtreeBestIndex`, `rtreeDisconnect`, `rtreeDestroy`, `rtreeOpen`, `rtreeClose`, `rtreeFilter`, `rtreeNext`, `rtreeEof`, `rtreeColumn`, `rtreeRowid`, `rtreeUpdate`, and `rtreeRename`. Public registration APIs include `sqlite3RtreeInit()` and `sqlite3_rtree_geometry_callback()`.

R-tree internal helpers include serialization functions `readInt16()`, `readCoord()`, `readInt64()`, `writeInt16()`, `writeCoord()`, `writeInt64()`, node cache/refcount helpers `nodeAcquire()`, `nodeWrite()`, `nodeRelease()`, `nodeHashLookup()`, `nodeHashInsert()`, `nodeHashDelete()`, scan helpers `testRtreeCell()`, `testRtreeEntry()`, `descendToCell()`, and write-path helpers `ChooseLeaf()`, `AdjustTree()`, `SplitNode()`, `Reinsert()`, `rtreeInsertCell()`, `deleteCell()`, `removeNode()`, `fixLeafParent()`, and `fixBoundingBox()`.

The ICU extension registers SQL functions through `sqlite3IcuInit()`: `regexp`, `lower`, `upper`, `like`, and `icu_load_collation`. It uses ICU APIs such as `uregex_open()`, `uregex_setText()`, `uregex_matches()`, `u_strToUpper()`, `u_strToLower()`, `ucol_open()`, `ucol_strcoll()`, and UTF iteration/folding macros. The FTS3 ICU tokenizer exports `sqlite3Fts3IcuTokenizerModule()` and implements tokenizer callbacks `icuCreate()`, `icuDestroy()`, `icuOpen()`, `icuClose()`, and `icuNext()` around ICU `UBreakIterator`.

The local page scan API is `tryReadEveryDbPage(sqlite3 *db, Pgno start, Pgno *pBadPage, int *pBadPageType, int *pBadPageZero)`. It depends on `sqlite3BtreePager()`, `sqlite3BtreeLastPage()`, internal `readDbPage()`, pointer-map macros `PTRMAP_PAGENO`/`PTRMAP_PTROFFSET`, `PENDING_BYTE`, `PGHDR_ZERO_COPY`, and `unpinZeroCopy()`.

## Control Flow

`fts3ExprNearTrim()` starts with a phrase node whose doclist has just been loaded and walks leftward through parent NEAR operators while the phrase is the right child. For each adjacent phrase group it finds the left phrase and calls `sqlite3Fts3ExprNearTrim()` so loaded doclists are pruned to NEAR-compatible positions.

`fts3ExprLoadDoclists()` iterates matchable phrase nodes with `fts3ExprIterate()`, skips NOT-right-hand subtrees, increments phrase/token counts, lazily loads phrase doclists, marks expressions loaded, and then applies NEAR trimming. Snippet, offsets, LCS, and hits calculations share this loader to ensure doclists are available before reading encoded position lists.

Snippet selection first builds a per-phrase `SnippetIter` for one column. `fts3BestSnippet()` scans candidate token windows, scores each candidate with a large bonus for phrases not yet covered by earlier fragments, and records the best fragment. `sqlite3Fts3Snippet()` tries one through four fragments, optionally across all columns, until the covered phrase bitmask equals the seen phrase bitmask or the fragment limit is reached. `fts3SnippetText()` then re-tokenizes the actual column text, may shift the window forward with `fts3SnippetShift()`, appends ellipses, and wraps highlighted tokens with caller-provided markers.

`sqlite3Fts3Offsets()` loads doclists, allocates one `TermOffset` iterator per query token, initializes those iterators for each column, tokenizes the stored column text, and appends `column term start length` tuples for matched terms. It treats tokenizer exhaustion before expected positions as corruption and returns an SQLite error through the scalar function context.

`sqlite3Fts3Matchinfo()` validates the requested format string or uses the default, returns an empty blob for expression-less cursors, and delegates to `fts3GetMatchinfo()`. `fts3GetMatchinfo()` caches the matchinfo array and format string on the cursor, computes phrase count and output size, and populates global fields once per query while recomputing row-local fields only when `isMatchinfoNeeded` is set. `fts3MatchinfoValues()` handles each format character: phrase/column/document counts, average lengths from `%_stat`, row lengths from `%_docsize`, LCS by synchronized position-list iterators, and hits through global and local callbacks.

R-tree scans are planned by `rtreeBestIndex()`. A rowid equality constraint uses strategy 1; coordinate constraints and MATCH geometry constraints use strategy 2 with a compact two-byte-per-constraint `idxStr`. `rtreeFilter()` configures the cursor from this strategy, deserializes geometry blobs when needed, acquires the root node for scans, and descends to the first leaf cell satisfying all constraints. `rtreeNext()` continues depth-first traversal, ascending via parent pointers when a node is exhausted.

R-tree writes run through `rtreeUpdate()`. Deletes locate the leaf through `%_rowid`, remove the cell, condense underfull nodes, shrink the root when it has a single child, and reinsert removed node contents. Inserts validate min/max coordinate ordering, choose or allocate a rowid, select a leaf using `ChooseLeaf()`, then call `rtreeInsertCell()`. Overflow either splits the node or, for the configured R*-tree variant, performs one reinsertion before splitting. Split assignment defaults to `splitNodeStartree()`, which sorts cells by dimension, evaluates margin/overlap/area, and writes left/right nodes and mapping tables.

ICU SQL functions are ordinary scalar functions. `icuLikeFunc()` validates pattern length and optional single-character escape, then runs a recursive Unicode-aware LIKE matcher. `icuRegexpFunc()` caches compiled ICU regex objects with SQLite auxdata keyed to the pattern argument. `icuCaseFunc16()` converts input through ICU upper/lower routines and returns UTF-16 text. `icuLoadCollation()` opens a `UCollator` for a locale and registers it as a SQLite UTF-16 collation.

The ICU tokenizer allocates a cursor containing a folded UTF-16 copy of UTF-8 input plus offset mapping back to byte positions. `icuOpen()` builds that representation and opens a word break iterator. `icuNext()` skips whitespace-like break ranges, converts the current token back to UTF-8 into a reusable buffer, and returns token bytes, byte offsets, and monotonically increasing token position.

`tryReadEveryDbPage()` obtains the main database btree and pager, calculates the last page and the page containing SQLite's pending byte, then loops from `start` through the last page, skipping the pending-byte page. For each page it constructs a stack `PgHdr`, points it at a malloc buffer, and calls `readDbPage()` without inserting the page into the normal page cache. On the first non-OK return it records `*pBadPage` and stops. For `SQLITE_CORRUPT`, it also checks whether the read buffer is all zeroes and tries to read the relevant pointer-map page to report the expected bad page type.

## State And Persistence Behavior

FTS3 state is mostly cursor-local. Doclists become cached on `Fts3Expr` nodes, `isLoaded` prevents duplicate loads, NEAR trimming mutates loaded doclists, `Fts3Cursor.aMatchinfo`/`zMatchinfo` cache the current matchinfo format and array, and snippet/offset string builders own transient SQLite-allocated buffers returned as SQL results. `sqlite3Fts3SegmentsClose()` is called after snippet, offsets, and matchinfo calculations to close FTS segment readers.

R-tree state is persisted in three ordinary SQLite tables: `%_node`, `%_rowid`, and `%_parent`. Node blobs contain depth/cell counts and serialized rowid-or-child plus coordinate cells. `Rtree` keeps prepared statements for these tables and a small in-memory hash of live `RtreeNode` objects. Dirty nodes are written by `nodeWrite()` when their reference count drops to zero; newly allocated nodes receive rowids from `%_node` insertions. Parent and rowid mapping tables are updated separately during insert, split, delete, condense, and reinsert operations.

R-tree schema lifecycle is handled by virtual table callbacks. `rtreeSqlInit()` creates backing tables for `xCreate` and prepares all read/write/delete statements for both create and connect. `rtreeDestroy()` drops all three backing tables. `rtreeRename()` renames all backing tables to match the virtual table name. `rtreeRelease()` finalizes prepared statements and frees the virtual table object once no cursor/update path holds it busy.

ICU extension state consists of registered SQLite functions/collations and per-call/per-pattern allocations. Regex objects are cached through auxdata and closed by `icuRegexpDelete()`. ICU collators are owned by SQLite collation destructors. The FTS3 ICU tokenizer stores locale on the tokenizer object, and each tokenizer cursor owns its break iterator, UTF-16 copy, offset array, and UTF-8 output buffer.

`tryReadEveryDbPage()` is read-oriented and does not intentionally mutate database contents. It does allocate one page-sized heap buffer and may receive zero-copy page memory from `readDbPage()` when the pager is read-only and using WAL; in that case it calls `unpinZeroCopy()` for both the tested page and optional pointer-map page. It reports corruption details through output parameters but does not persist diagnostics.

## Dependencies And Integration Points

The FTS3 functions integrate with SQLite's virtual table/scalar-function path and depend on FTS3 expression parsing, segment/doclist loading, deferred token handling, tokenizer modules, `%_stat`, and `%_docsize`. They are called by SQL auxiliary functions exposed by FTS3 tables and rely on the current row statement (`pCsr->pStmt`) to retrieve original column text.

The R-tree module integrates with SQLite's virtual table API, query planner (`sqlite3_index_info`), scalar function registration, ordinary SQL backing tables, prepared statement APIs, and extension loading. Geometry callbacks bridge user C callbacks into SQL by returning an opaque blob with a magic value, callback pointer, context, and double parameters; MATCH constraints later deserialize that blob for scan filtering.

The ICU extension integrates with SQLite function/collation registration and the external ICU library. Its compile-time availability depends on `SQLITE_ENABLE_ICU`, while the ICU tokenizer also depends on `SQLITE_ENABLE_FTS3`. The tokenizer module pointer returned by `sqlite3Fts3IcuTokenizerModule()` is consumed by FTS3 tokenizer registration code elsewhere in the amalgamation.

The page scan helper is a local integration point between FoundationDB's SQLite API surface and SQLite pager internals. The public prototype appears in the vendored `sqlite3.h`, but the implementation directly creates `PgHdr` objects and uses internal pager/btree state, pointer map calculations, and the local zero-copy VFS extension hooks.

## Risks And Edge Cases

The FTS3 code relies on compact delta/varint encoded position-list formats. Incorrect pointer advancement can corrupt matchinfo, snippets, or offsets. The bitmask approach for snippets uses `u64`, so phrase/token positions beyond the mask width are inherently risky. Deferred tokens require fallback doclist loading for global hits; phrases composed entirely of deferred tokens substitute document-count values because full index stats are unavailable.

`fts3SnippetShift()` opens a tokenizer on a substring and assumes tokenizer positions can be used to determine how far a snippet may shift. Tokenizer errors propagate, but subtle tokenizer offset differences can change displayed snippets without affecting match results.

`sqlite3Fts3Offsets()` returns `SQLITE_CORRUPT` if the stored document text token stream cannot satisfy positions advertised by the index. That is a useful integrity signal but can also surface from tokenizer incompatibility after table creation.

R-tree node integrity checks are partial. `nodeAcquire()` validates root depth and node cell count, but many invariants depend on consistent `%_node`, `%_rowid`, and `%_parent` rows. Parent-chain repair guards against loops, and missing parent data becomes `SQLITE_CORRUPT`. Any bug in split/reinsert/mapping updates can leave durable backing tables inconsistent.

R-tree coordinate handling is sensitive to type mode. `rtree` stores coordinates as 32-bit floats; `rtree_i32` stores 32-bit integers. Inserts reject min greater than max but do not otherwise normalize values. Floating-point equality constraints and area/overlap comparisons can be precision-sensitive.

`deserializeGeometry()` checks blob shape and magic before installing a MATCH callback, but the blob contains callback pointers and context produced by a registered SQL function. This is safe only inside the same process/address space and is not a portable persisted representation.

ICU `icuCaseFunc16()` allocates `nInput * 2 + 2` bytes and calls ICU conversion once. If ICU reports a capacity issue for unusual expansions, this code reports an ICU error instead of retrying with the required size. The error path also does not free `zOutput` before returning, so failures here risk a leak. `icuLikeCompare()` is recursive for `%` matching; the pattern length guard limits but does not eliminate worst-case matching cost.

The ICU tokenizer's offset mapping is delicate because it case-folds UTF-8 into UTF-16 and then maps token boundaries back to byte offsets. Invalid or unusual UTF-8 and multi-code-unit folding can stress the `U8_NEXT`/`U16_APPEND` path and token offset correctness.

`tryReadEveryDbPage()` has several sharp edges: it assumes `db->aDb[0].pBt` is initialized and notes a TODO for clients that have not opened/read the database; it uses `malloc()` without checking for `NULL`; it dereferences output pointers without validation; and it calls `readDbPage()` without explicitly acquiring locks in this function, relying on caller/database state to satisfy pager preconditions. On corruption it reuses the page buffer for pointer-map reads, so the all-zero check must happen before that reuse, as it currently does.

## Test Signals

Relevant FTS3 tests should exercise `snippet()`, `offsets()`, and `matchinfo()` over phrase, multi-token phrase, NEAR, NOT, deferred-token, NULL-column, multi-column, and tokenizer edge cases. Integrity-oriented tests should verify that index/document-tokenizer mismatch produces corruption from `offsets()` and that cached matchinfo is invalidated when format strings change.

R-tree signals include virtual table create/connect/drop/rename, rowid lookup strategy, coordinate range scans, MATCH geometry callbacks, insert/update/delete, duplicate rowid rejection, min/max coordinate constraints, node split and root growth, underfull-node condense and root shrink, and persistence across reconnect. Corruption tests should cover malformed node blobs, missing parent or rowid mappings, parent loops, and invalid root depth.

ICU tests should cover Unicode case folding in `LIKE`, single-character ESCAPE validation, regex cache reuse and invalid patterns, locale-specific upper/lower behavior, loading and using ICU collations, and FTS3 ICU tokenizer token boundaries and byte offsets for multi-byte text.

The local page scan helper can be tested by opening a database through the FoundationDB SQLite build, calling `tryReadEveryDbPage()` from page 1 and non-1 starts, verifying that the pending-byte page is skipped, injecting or simulating read/corruption errors, checking `pBadPage`, `pBadPageType`, and `pBadPageZero`, and running under a VFS path that exercises `xReadZeroCopy`/`xReleaseZeroCopy` to confirm no pinned pages leak.
