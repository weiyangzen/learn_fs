# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 242625-251111

## Scope

This chunk covers a large slice of SQLite FTS5 internals inside the amalgamated `sqlite3.c` vendored under WiredTiger test third-party sources. It starts near the end of the FTS5 expression parser/evaluator support code, then covers the in-memory FTS5 hash accumulator and the opening/middle of the low-level FTS5 index backend. It ends just after `sqlite3Fts5IndexOpen()` begins `sqlite3Fts5IndexClose()` cleanup.

The main subsystems in this range are:

- FTS5 expression-tree construction helpers, debug/test expression-printing UDFs, phrase/position-list introspection, and position-list population for `detail=column` and `detail=none` tables.
- The in-memory `Fts5Hash` table that accumulates term-to-doclist updates before flushing them into level-0 index segments.
- The FTS5 `%_data` and `%_idx` storage format definitions, rowid packing macros, structure-record decode/write logic, segment metadata, page writers, doclist-index writers, tombstone arrays, segment iterators, and multi-segment merge iterators.
- Index read paths that seek segments by term, scan hash or disk segments, merge duplicate rowids, filter by column sets, skip tombstones/deleted entries, and expose current rowid/position-list outputs.
- Index write paths that flush hash contents to new segments, write leaf pages and `%_idx` btree separators, maintain doclist-index records, split large position lists across pages, and perform automerge/crisismerge/optimize work.
- Secure-delete and contentless-delete support, including tombstone-aware merge selection and physical removal of term/rowid entries from existing segment pages.
- Prefix-query setup and tokendata mapping for `xInstToken()` support.
- Public-ish FTS5 index lifecycle entry points for begin-write, sync, rollback, reinit, open, optimize, and merge operations.

Within WiredTiger this is third-party SQLite code used by tests or embedded tooling, not WiredTiger storage engine implementation. Its behavior still matters because any test binary using this amalgamation inherits SQLite FTS5 indexing, merge, and query semantics exactly.

## Purpose

The purpose of this chunk is to bridge FTS5 query expressions and tokenized document updates to the persistent full-text index stored in SQLite shadow tables. The expression support maps parsed MATCH terms and phrases to rowid/position-list state. The hash layer batches index updates in memory. The index layer serializes those updates into SQLite `%_data` segment pages, maintains `%_idx` accelerators, reads and merges segment iterators for queries, and incrementally compacts segments over time.

The code is performance-critical and corruption-facing. It manipulates compact varint encodings, page headers, prefix-compressed terms, delta-encoded rowids, position-list payloads, and reference-counted in-memory structures. It also supports multiple FTS5 detail modes (`full`, `columns`, `none`), prefix indexes, tokendata mode, secure-delete mode, contentless-delete tombstones, reverse rowid scans, and column-restricted queries.

## Important APIs, Types, and Functions

### Expression Helpers

The chunk begins after `fts5ExprAssignXNext()` has selected per-node iterator callbacks. `fts5ExprAddChildren()` flattens adjacent `AND` or `OR` nodes so expression trees avoid unnecessary nesting, while preserving `NOT` binary shape. `fts5ParsePhraseToAnd()` rewrites trigram LIKE/GLOB phrases into an `AND` tree when `bPhraseToAnd` is set, turning a phrase such as `abc + def + ghi` into independent term nodes.

`sqlite3Fts5ParseNode()` is the main expression node allocator for `FTS5_STRING`, `FTS5_AND`, `FTS5_OR`, and `FTS5_NOT`. It handles null child elision, phrase-to-AND rewrites, term-node simplification, `detail!=full` query restrictions, phrase/node back-pointers, EOF marking for empty phrases, and maximum expression-depth enforcement. `sqlite3Fts5ParseImplicitAnd()` combines adjacent terms during parsing and includes special handling for EOF placeholder nodes so empty-string terms do not leave invalid phrase-array entries behind.

Under `SQLITE_TEST` or `SQLITE_FTS5_DEBUG`, `fts5ExprTermPrint()`, `fts5ExprPrintTcl()`, `fts5ExprPrint()`, and `fts5ExprFunction()` implement debug scalar functions `fts5_expr()`, `fts5_expr_tcl()`, `fts5_isalnum()`, and `fts5_fold()`. These parse expressions using a synthetic FTS5 config and render them in human-readable or Tcl-readable form. `sqlite3Fts5ExprInit()` registers those debug-only UDFs and references parser trace/fallback symbols to avoid unused warnings.

Expression accessors include `sqlite3Fts5ExprPhraseCount()`, `sqlite3Fts5ExprPhraseSize()`, `sqlite3Fts5ExprPoslist()`, `sqlite3Fts5ExprPhraseCollist()`, `sqlite3Fts5ExprQueryToken()`, `sqlite3Fts5ExprInstToken()`, and `sqlite3Fts5ExprClearTokens()`. They expose phrase counts, phrase terms, current position/collist data, query-token bytes, original instance-token bytes for tokendata/prefix cases, and per-term token-data caches.

For `detail=columns` and `detail=none`, the expression layer may rebuild position lists by retokenizing row text. `sqlite3Fts5ExprClearPoslists()` allocates `Fts5PoslistPopulator` state and clears or marks phrase misses. `sqlite3Fts5ExprPopulatePoslists()` configures per-phrase column eligibility and calls `sqlite3Fts5Tokenize()` with `fts5ExprPopulatePoslistsCb()`, which matches document tokens against expression terms/synonyms/prefixes, appends encoded offsets, and optionally records tokendata back into index iterators. `sqlite3Fts5ExprCheckPoslists()` then recursively validates `AND`, `OR`, and `NOT` nodes against populated lists.

### In-Memory FTS5 Hash

`Fts5Hash` and `Fts5HashEntry` implement the pending update table. A hash entry stores the key and current doclist in one allocation: the key is a one-byte index identifier followed by term bytes, and the data area contains delta-encoded rowids and position-list encodings similar to on-disk doclists.

Key functions:

- `sqlite3Fts5HashNew()`, `sqlite3Fts5HashFree()`, and `sqlite3Fts5HashClear()` allocate, free, and empty the hash. The object updates the caller's byte counter through `pnByte`.
- `fts5HashKey()`, `fts5HashKey2()`, and `fts5HashResize()` hash term keys and double slot count when the load factor approaches 0.5.
- `sqlite3Fts5HashWrite()` appends a token occurrence or delete marker. It creates or grows `Fts5HashEntry` allocations, starts new rowid records, handles `detail=full`, `detail=columns`, and `detail=none` encodings, tracks column/position ordering, and updates delete/content flags.
- `fts5HashAddPoslistSize()` finalizes the pending position-list size field. This may rewrite a reserved one-byte field into a multi-byte varint and shifts following bytes.
- `fts5HashEntryMerge()` and `fts5HashEntrySort()` produce sorted scan lists for flushes and prefix scans without removing entries from hash buckets.
- `sqlite3Fts5HashQuery()`, `sqlite3Fts5HashScanInit()`, `sqlite3Fts5HashScanNext()`, `sqlite3Fts5HashScanEof()`, and `sqlite3Fts5HashScanEntry()` expose point lookups or ordered scans of pending doclists to the segment iterator layer.

A notable state transition is that hash scans finalize position-list size fields, after which those entries are no longer safely appendable. `fts5SegIterHashInit()` clears `Fts5Index.bDelete` after scan initialization to avoid appending to finalized delete-related data.

### FTS5 Index Storage Structures

The index backend defines the `%_data` table record classes and rowid layout. `FTS5_AVERAGES_ROWID` and `FTS5_STRUCTURE_ROWID` identify global records. `FTS5_SEGMENT_ROWID()`, `FTS5_DLIDX_ROWID()`, and `FTS5_TOMBSTONE_ROWID()` pack segment id, doclist-index bit, height, and page number into shadow-table rowids using `fts5_dri()`.

Core types introduced here include:

- `Fts5Data`: an owned `%_data` blob plus `nn` and `szLeaf`.
- `Fts5Index`: the backend handle, holding config, prepared statements, pending hash, reader blob, cached structure, flush/error state, data-version, and counters.
- `Fts5Structure`, `Fts5StructureLevel`, and `Fts5StructureSegment`: in-memory decoded structure records. V2 structures add contentless-delete origin counters, tombstone page counts, tombstone entry counts, and segment entry counts.
- `Fts5PageWriter`, `Fts5DlidxWriter`, and `Fts5SegWriter`: segment output builders for leaf pages, doclist-index pages, separator terms, and `%_idx` rows.
- `Fts5SegIter`, `Fts5DlidxIter`, and `Fts5Iter`: single-segment, doclist-index, and multi-segment iterators.
- `Fts5TombstoneArray`: lazily loaded, reference-counted tombstone hash pages for contentless-delete filtering.
- `Fts5DoclistIter`, `PrefixMerger`, `Fts5TokenDataMap`, and `Fts5TokenDataIter`: helper structures for prefix-query doclist construction and tokendata instance-token lookup.

Endian helpers (`fts5PutU16()`, `fts5GetU16()`, `fts5GetU32()`, `fts5GetU64()`, `fts5PutU32()`, `fts5PutU64()`), buffer append macros, leaf header macros, and constants such as `FTS5_DATA_PADDING`, `FTS5_DATA_ZERO_PADDING`, `FTS5_WORK_UNIT`, `FTS5_OPT_WORK_UNIT`, and `FTS5_MIN_DLIDX_SIZE` define the low-level binary contract.

### Data IO and Structure Records

`fts5DataRead()` uses a reusable read-only `sqlite3_blob` handle to read records from `%_data`. It reopens the blob for a requested rowid, maps `SQLITE_ERROR` to `FTS5_CORRUPT`, allocates padded `Fts5Data`, reads the blob, and initializes `szLeaf`. `fts5LeafRead()` adds leaf sanity checks. `fts5DataWrite()`, `fts5DataDelete()`, and `fts5DataRemoveSegment()` write/replace data rows, delete rowid ranges, remove segment/tombstone records, and clean corresponding `%_idx` rows.

`fts5IndexPrepareStmt()` prepares persistent statements with `SQLITE_PREPARE_NO_VTAB` and maps missing/modified shadow tables to corruption. `fts5IndexCloseReader()` closes the blob reader and records close errors in `Fts5Index.rc`.

`fts5StructureDecode()` parses the structure record, including legacy and `FTS5_STRUCTURE_V2` formats. It validates level/segment counts, merge counts, segment page ranges, V2 tombstone/origin metadata, and total segment count. `fts5StructureWrite()` serializes the structure with the current configuration cookie and V2 extension fields when needed. `fts5StructureRead()`, `fts5StructureReadUncached()`, `fts5IndexDataVersion()`, and `fts5StructureInvalidate()` implement a cached structure object keyed by SQLite `PRAGMA data_version`.

Reference and copy-on-write helpers (`fts5StructureRef()`, `fts5StructureRelease()`, `sqlite3Fts5StructureRef()`, `sqlite3Fts5StructureRelease()`, `sqlite3Fts5StructureTest()`, and `fts5StructureMakeWritable()`) allow callers to hold structure snapshots safely while merge/write logic edits writable copies.

Structure editing and merge policy helpers include `fts5StructureAddLevel()`, `fts5StructureExtendLevel()`, `fts5StructurePromoteTo()`, `fts5StructurePromote()`, `fts5AllocateSegid()`, `fts5IndexDiscardData()`, `fts5IndexFindDeleteMerge()`, `fts5IndexMerge()`, `fts5IndexAutomerge()`, `fts5IndexCrisismerge()`, `fts5IndexOptimizeStruct()`, `sqlite3Fts5IndexOptimize()`, and `sqlite3Fts5IndexMerge()`.

### Segment and Doclist Iterators

Doclist-index iteration is handled by `fts5DlidxLvlNext()`, `fts5DlidxIterNextR()`, `fts5DlidxIterNext()`, `fts5DlidxIterFirst()`, `fts5DlidxIterEof()`, `fts5DlidxIterLast()`, `fts5DlidxLvlPrev()`, `fts5DlidxIterPrevR()`, `fts5DlidxIterPrev()`, `fts5DlidxIterFree()`, `fts5DlidxIterInit()`, `fts5DlidxIterRowid()`, and `fts5DlidxIterPgno()`. These traverse one or more levels of doclist-index pages and are used to skip directly to pages likely to contain a target rowid.

Single-segment iteration is initialized by `fts5SegIterInit()` for full scans, `fts5SegIterSeekInit()` for term lookups, `fts5SegIterNextInit()` for finding the next term after a token, and `fts5SegIterHashInit()` for pending in-memory hash data. `fts5SegIterSetNext()` chooses between forward, reverse, and `detail=none` next callbacks.

Important iterator helpers include:

- `fts5SegIterNextPage()`, `fts5SegIterLoadTerm()`, `fts5SegIterLoadRowid()`, `fts5SegIterLoadNPos()`, and `fts5GetPoslistSize()` decode leaf pages, terms, rowids, delete flags, and position-list sizes.
- `fts5LeafSeek()` finds a term on a leaf using prefix-compressed terms and page indexes.
- `fts5SegIterLoadDlidx()`, `fts5SegIterReverse()`, `fts5SegIterReverseInitPage()`, and `fts5SegIterReverseNewPage()` support descending rowid scans of a single term.
- `fts5SegIterNext()`, `fts5SegIterNext_None()`, and `fts5SegIterNext_Reverse()` advance iterators through regular, `detail=none`, and reverse encodings.
- `fts5SegIterNextFrom()` uses doclist-index pages to advance an oneterm iterator to or past a target rowid.
- `fts5SegIterClear()` frees term buffers, leaf buffers, next-leaf prefetch, tombstone arrays, doclist iterators, and reverse offset arrays.

Multi-segment iteration uses a tournament tree in `Fts5Iter.aFirst`. `fts5MultiIterAlloc()` sizes the iterator to a power-of-two segment count. `fts5MultiIterDoCompare()`, `fts5MultiIterAdvanced()`, `fts5MultiIterAdvanceRowid()`, `fts5MultiIterSetEof()`, and `fts5MultiIterFinishSetup()` maintain the winner tree, detect duplicate term/rowid entries from lower-priority segments, and choose the visible current entry. `fts5MultiIterNext()`, `fts5MultiIterNext2()`, `fts5MultiIterNextFrom()`, `fts5MultiIterEof()`, `fts5MultiIterRowid()`, and `fts5MultiIterTerm()` expose traversal operations.

Delete/tombstone filtering is split by mode. Ordinary delete markers are zero-length or flagged position lists, detected by `fts5MultiIterIsEmpty()`. Contentless-delete tombstones are checked by `fts5MultiIterIsDeleted()` using `Fts5TombstoneArray` and `fts5IndexTombstoneQuery()`.

### Position-List Outputs and Column Filtering

`fts5ChunkIterate()` streams a position list to a callback, following overflow onto subsequent segment pages when required. `fts5SegiterPoslist()` copies or filters position-list data into an output buffer. `fts5PoslistCallback()`, `fts5PoslistFilterCallback()`, and `fts5PoslistOffsetsCallback()` implement raw copy, `detail=full` column filtering, and `detail=columns` offset filtering.

`fts5IndexExtractColset()` can avoid copying when a single-column filter corresponds to a contiguous subset of a full position list. Output callbacks selected by `fts5IterSetOutputCb()` populate `Fts5IndexIter.base` fields for different configurations:

- `fts5IterSetOutputs_None()` for `detail=none`.
- `fts5IterSetOutputs_Nocolset()` for full/columns detail with no filter.
- `fts5IterSetOutputs_ZeroColset()` for an empty column set.
- `fts5IterSetOutputs_Col()` and `fts5IterSetOutputs_Col100()` for `detail=columns`.
- `fts5IterSetOutputs_Full()` for `detail=full` with column restrictions.

### Segment Writing, Flush, and Merge

Segment output starts with `fts5WriteInit()`, which prepares the `%_idx` writer, initializes a leaf page buffer with a four-byte header, allocates page/pgidx buffers, and ensures doclist-index writer storage. `fts5WriteAppendTerm()` writes prefix-compressed terms and page-index entries, and records split keys through `fts5WriteBtreeTerm()` when a new leaf starts. `fts5WriteAppendRowid()` writes first or delta rowids and updates the doclist-index via `fts5WriteDlidxAppend()`. `fts5WriteAppendPoslistData()` streams large position lists across page boundaries without splitting varints.

`fts5WriteFlushLeaf()` finalizes `szLeaf`, appends pgidx data if the page contains terms, writes the leaf row to `%_data`, resets page buffers, and increments leaf counters. `fts5WriteBtreeNoTerm()`, `fts5WriteFlushDlidx()`, `fts5WriteDlidxClear()`, `fts5WriteDlidxGrow()`, `fts5DlidxExtractFirstRowid()`, and `fts5WriteFlushBtree()` maintain optional doclist-index pages and `%_idx` entries for large doclists. `fts5WriteFinish()` flushes final pages, writes btree separators, frees writer buffers, and reports leaf count.

`fts5TrimSegments()` updates input segments after partial incremental merges. `fts5MergeChunkCallback()` copies position-list chunks into a segment writer during merge. `fts5IndexMergeLevel()` merges input segments from a level into a higher-level segment, writes non-deleted doclists, removes fully merged old segments, trims partially consumed segments, updates structure metadata, and decrements remaining work-page budget. `fts5IndexMerge()` chooses ongoing merge levels, levels with too many segments, or contentless-delete tombstone-heavy levels.

`fts5FlushOneHash()` is the central pending-data flush path. It reads and invalidates the current structure, allocates a segment id, scans sorted hash entries, writes each term/doclist into a new level-0 segment, performs secure-delete physical removal when configured, appends the new segment to level 0, promotes segments when appropriate, runs automerge and crisismerge, writes the updated structure, and releases it. `fts5IndexFlush()` calls this when pending data or contentless-delete work exists and preserves `flushRc` if a failed flush must be retried/reported.

### Secure Delete and Contentless Delete

Secure-delete code physically removes token traces instead of just appending delete markers. `fts5SecureDeleteIdxEntry()` deletes `%_idx` separator entries for pages whose last term was removed. `fts5SecureDeleteOverflow()` rewrites pages that held overflow portions of a deleted position list, shifting leaf bodies and pgidx data. `fts5DoSecureDelete()` removes the current rowid/position-list entry from a segment page, adjusts following rowid deltas, removes entire terms when their last rowid disappears, updates page headers and footers, and handles cases where the doclist spans multiple pages. `fts5FlushSecureDelete()` ensures the FTS5 version is upgraded to secure-delete format, seeks the target term/rowid in existing segments with hash skipped, and calls `fts5DoSecureDelete()`.

Contentless-delete state is stored in V2 structure records through segment origins, tombstone page counts, tombstone entry counts, and entry counts. `fts5IndexFindDeleteMerge()` selects merge candidates when tombstones exceed the configured delete-merge percentage. Query iterators lazily load tombstone pages and suppress tombstoned rowids.

### Prefix Query and Tokendata Setup

`fts5VisitEntries()` scans all index entries matching a full token or prefix and invokes a callback for each visible rowid entry. It uses a no-output multi-iterator initially, then selects output callbacks and filters by column set.

Prefix query setup accumulates a synthetic doclist from all terms with the requested prefix. `fts5DoclistIterNext()`, `fts5DoclistIterInit()`, `fts5MergeRowidLists()`, `fts5MergePrefixLists()`, `fts5PrefixMergerInsertByRowid()`, `fts5PrefixMergerInsertByPosition()`, `fts5AppendRowid()`, `fts5AppendPoslist()`, and `prefixIterSetupCb()` merge rowid-only or full position-list doclists while preserving rowid order and merged positions. `fts5SetupPrefixIter()` chooses the merge strategy based on detail mode, optionally combines main-index and prefix-index data, builds an in-memory `Fts5Data` doclist, and returns an `Fts5Iter` over it.

Tokendata support adds `Fts5TokenDataMap` and `Fts5TokenDataIter`. `prefixIterSetupTokendataCb()` records rowid/position-to-term mappings for prefix queries. `fts5TokendataIterAppendMap()`, `fts5TokendataMerge()`, `fts5TokendataIterSortMap()`, and `fts5TokendataIterDelete()` allocate, sort, and free these mappings. These structures support APIs that need to recover the original matched token for an instance.

### Lifecycle Entry Points

The chunk ends with higher-level index lifecycle functions:

- `sqlite3Fts5IndexBeginWrite()` allocates the hash table on demand, flushes if rowid ordering or hash-size limits require it, sets write rowid/delete mode, and increments pending-row counts for inserts.
- `sqlite3Fts5IndexSync()` flushes pending data and closes the blob reader.
- `sqlite3Fts5IndexRollback()` closes readers, discards pending hash data, invalidates cached structures, and returns the backend to a clean state.
- `sqlite3Fts5IndexReinit()` initializes empty `%_data` storage with averages and structure records, including initial contentless-delete origin state.
- `sqlite3Fts5IndexOpen()` allocates `Fts5Index`, creates `%_data` and `%_idx` shadow tables when requested, and reinitializes them.
- `sqlite3Fts5IndexClose()` begins at the end of the chunk and starts finalizing prepared statements after invalidating cached structure state.

## Control Flow and State Behavior

The normal write path starts when table-level FTS5 code calls `sqlite3Fts5IndexBeginWrite()` for a rowid. Token writes are accumulated in `Fts5Hash` through `sqlite3Fts5HashWrite()` elsewhere in the amalgamation. The hash preserves rowid order assumptions and tracks memory through `nPendingData`. When rowid order changes, a delete/insert conflict occurs, or the hash exceeds `nHashSize`, `fts5IndexFlush()` writes pending entries to disk.

Flush control flow is:

1. Read and invalidate the cached structure.
2. If hash is non-empty, allocate a free segment id.
3. Initialize `Fts5SegWriter` and scan hash entries in term order.
4. For each term, either append its doclist directly if it fits or iterate rowid/poslist records and split them across leaves.
5. In secure-delete mode, delete markers may trigger in-place edits of existing segments instead of writing new delete entries.
6. Finish the writer, append a level-0 segment if pages were produced, update V2 origin/entry metadata when needed, promote small segments, run automerge/crisismerge, write the structure, and clear hash state.

The query path builds one or more `Fts5SegIter` objects from the pending hash and from every relevant disk segment in the current structure. Each segment iterator decodes its current term, rowid, delete flag, and position list. `Fts5Iter` merges them using `aFirst[]`, with lower array indexes representing higher-priority/newer sources. Duplicate term/rowid entries from older segments are advanced or skipped. Empty delete entries and contentless-delete tombstones are filtered before output callbacks expose rowid and position-list data.

Persistent state lives mainly in SQLite shadow tables:

- `%_data` stores the averages record, structure record, segment leaf pages, doclist-index pages, and tombstone hash pages.
- `%_idx` stores per-segment term-to-page separators and flags indicating whether a doclist-index exists.
- `%_config` may be updated by secure-delete upgrade code to set the FTS5 version.

In-memory state includes:

- Pending term/doclist data in `Fts5Hash`.
- Cached `Fts5Structure` snapshots with reference counts and `data_version`.
- Reusable prepared statements for `%_data`, `%_idx`, and config access.
- A reusable blob reader, invalidated on rollback/sync/close.
- Segment iterator buffers, next-leaf prefetch, doclist-index iterators, reverse rowid offset arrays, and tombstone arrays.
- Writer buffers for leaf page body, page index, previous term, doclist-index levels, and pending `%_idx` term.

Error propagation is centralized through `Fts5Index.rc`. Most helpers are no-ops when `rc` is already non-OK. Corruption-facing decoders set `FTS5_CORRUPT` or `SQLITE_CORRUPT_VTAB`; allocation failures set `SQLITE_NOMEM`; public entry points usually return through `fts5IndexReturn()`, which resets `p->rc` to `SQLITE_OK` after reporting it.

## Dependencies and Integration Points

This code depends on SQLite internals defined earlier or later in the amalgamation:

- FTS5 parser/config/expression types such as `Fts5Parse`, `Fts5Expr`, `Fts5ExprNode`, `Fts5ExprNearset`, `Fts5ExprPhrase`, `Fts5ExprTerm`, `Fts5Colset`, `Fts5Config`, `Fts5Global`, and `Fts5Buffer`.
- SQLite core allocation, varint, buffer, and string helpers including `sqlite3_malloc64()`, `sqlite3_realloc64()`, `sqlite3_free()`, `sqlite3Fts5MallocZero()`, `sqlite3Fts5BufferSize()`, `fts5BufferAppendVarint()`, `fts5BufferAppendBlob()`, `sqlite3Fts5PutVarint()`, `sqlite3Fts5GetVarint()`, `fts5GetVarint32()`, and `fts5FastGetVarint32()`.
- SQLite SQL APIs for shadow-table IO: `sqlite3_prepare_v3()`, `sqlite3_bind_*()`, `sqlite3_step()`, `sqlite3_reset()`, `sqlite3_finalize()`, `sqlite3_blob_open()`, `sqlite3_blob_reopen()`, `sqlite3_blob_read()`, and `sqlite3_blob_close()`.
- FTS5 tokenizer and Unicode helpers used by expression debug and poslist population: `sqlite3Fts5Tokenize()`, `sqlite3Fts5UnicodeCatParse()`, `sqlite3Fts5UnicodeCategory()`, and `sqlite3Fts5UnicodeFold()`.
- FTS5 index APIs outside this chunk, such as token writes, query entry points, iterator close/free wrappers, averages handling, tombstone creation, and table-level virtual table methods.

Integration points inside SQLite include MATCH expression parsing, FTS5 virtual table updates, query execution, phrase APIs, `xQueryToken()`/`xInstToken()`, optimize/merge special commands, rollback/sync hooks, and shadow-table creation. For the repository, the integration is indirect: WiredTiger tests that embed this SQLite amalgamation may exercise FTS5 behavior, but this code should generally be treated as vendored SQLite source.

## Risks

- The binary formats are compact and hand-decoded. Off-by-one errors in `szLeaf`, pgidx offsets, rowid offsets, position-list sizes, or varint boundaries can cause corruption reports, bad query results, or unsafe memory reads.
- Hash entries are append-oriented until scans finalize position-list size fields. Appending after `fts5HashAddPoslistSize()` has rewritten an entry would corrupt pending doclists, so the `bDelete`/scan interaction is fragile.
- Detail modes use different encodings. `detail=none` uses special zero-byte delete/content markers, `detail=columns` stores column lists, and `detail=full` stores full positions. Code paths that assume the wrong mode will misread doclists.
- Rowid ordering is assumed in many write paths. `sqlite3Fts5IndexBeginWrite()` must flush when rowids move backward or delete/insert ordering would make a hash entry unappendable.
- Segment merge priority determines visible results. Bugs in `fts5MultiIterDoCompare()`, duplicate advancement, tombstone filtering, or empty-delete skipping can resurrect deleted rows or hide live rows.
- Secure-delete physically rewrites pages and `%_idx` rows. It must update rowid deltas, page headers, term footers, overflow pages, and separator entries consistently; a small mistake can damage an entire segment.
- Structure-record V2 support adds compatibility risk. Origin counters, tombstone metadata, and version upgrade writes must remain synchronized with `contentless_delete` and secure-delete behavior.
- Blob-reader caching interacts with savepoints and rollback. `SQLITE_ABORT` from `sqlite3_blob_reopen()` is deliberately handled by reopening later; missing invalidation would read stale or invalid shadow-table pages.
- Prefix-query materialization can allocate large temporary doclists and tokendata maps. Incorrect merge buffering or map sorting affects prefix MATCH results and `xInstToken()` output.
- This is amalgamated third-party code. Local modifications are hard to maintain unless they come from the exact upstream SQLite version expected by the test suite.

## Test and Validation Signals

Useful test signals for this chunk include:

- FTS5 MATCH queries over inserted, deleted, and updated rows, including `AND`, `OR`, `NOT`, implicit `AND`, empty phrases, NEAR/phrase restrictions, trigram LIKE/GLOB phrase-to-AND rewrites, and column filters.
- Tables using `detail=full`, `detail=columns`, and `detail=none`, with phrase APIs and position/collist access checked where supported.
- Prefix index queries, both with and without `tokendata=1`, including `xInstToken()` expectations for prefix matches.
- Update workloads that force hash flushes because of rowid order changes, pending hash size, deletes followed by inserts for the same rowid, and explicit sync/rollback boundaries.
- Optimize and merge commands, automerge thresholds, crisismerge thresholds, and incremental merge continuation after partial work.
- Contentless-delete tables with tombstone-heavy levels and configured `deletemerge`, verifying that tombstoned rowids are hidden and later merge work compacts them.
- Secure-delete mode tests that remove all instances of a term and verify `%_data`/`%_idx` no longer retain the term, including entries spanning overflow leaf pages.
- Corruption tests for malformed `%_data` leaves, invalid structure records, bad page offsets, out-of-range segment metadata, and truncated doclists.
- Debug/test builds exercising `fts5_expr()`, `fts5_expr_tcl()`, `fts5_isalnum()`, `fts5_fold()`, `assert()` invariants, and `FTS5_CORRUPT` paths.

No tests were run for this research chunk; this document is based on static reading of `sqlite3.c` lines 242625-251111.
