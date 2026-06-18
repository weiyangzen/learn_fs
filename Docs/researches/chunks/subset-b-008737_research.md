# sources/storage-engines/sqlite/ext/fts5/fts5_index.c lines 1-8345

## Scope And Purpose

This chunk contains most of SQLite FTS5's low-level index storage engine. It implements read, write, query, merge, delete, contentless-delete, secure-delete, prefix-query, tokendata, and the beginning of integrity-check support for the `%_data` and `%_idx` backing tables owned by an FTS5 virtual table.

The top-level contract is described in the opening comments: `%_data(id INTEGER PRIMARY KEY, block BLOB)` stores structure records, averages, segment leaf pages, doclist-index pages, and contentless-delete tombstone hash pages. `%_idx(segid, term, pgno, PRIMARY KEY(segid, term))` stores term-to-segment-page routing entries used to seek directly into segment b-trees. Other FTS5 code calls this module through APIs declared in `fts5Int.h`; this file owns the binary formats and most of the state transitions that make the FTS index durable and queryable.

The requested chunk ends inside the debug/integrity-check section, after `fts5TestTerm()` has begun but before the rest of integrity-check and debug decoding helpers. The final per-file research should merge this with later chunks for the rest of `fts5_index.c`.

## Storage Format

The file defines fixed rowids for singleton records:

- `FTS5_AVERAGES_ROWID` stores the row count and total token counts per column.
- `FTS5_STRUCTURE_ROWID` stores the segment hierarchy and merge state.

Segment leaves, doclist-index pages, and tombstone pages use rowids composed from segment id, doclist-index flag, tree height, and page number. The important macros are `FTS5_SEGMENT_ROWID()`, `FTS5_DLIDX_ROWID()`, and `FTS5_TOMBSTONE_ROWID()`. The tombstone rowid macro offsets segment ids by `1<<16` so contentless-delete hash pages live outside normal segment/data rowid ranges.

The structure record has a legacy format and a V2 format identified by `FTS5_STRUCTURE_V2`. V2 is used by `contentless_delete=1` tables and extends each segment with origin range, number of tombstone pages, counted tombstone entries, and segment entry count. `fts5StructureDecode()` and `fts5StructureWrite()` are the authoritative serializer/deserializer pair.

Segment leaf pages begin with a 4-byte header: first-rowid offset and leaf-body size. The leaf body contains prefix-compressed terms, delta-encoded doclists, and position lists. The footer is a page index of term offsets. Doclists may span leaf pages; when they do, termless pages and first-rowid header offsets allow forward and reverse iteration without loading entire doclists. Large spanning doclists may also have doclist-index b-trees that copy first rowids for termless pages and support seeks within a doclist.

Contentless-delete tombstones are stored as per-segment open-addressed hash pages. The page header records key size, rowid-zero flag, and entry count. Slots are either 4-byte or 8-byte big-endian rowids. Query and rebuild paths are `fts5IndexTombstoneQuery()`, `fts5IndexTombstoneAddToPage()`, `fts5IndexTombstoneRehash()`, and `fts5IndexTombstoneRebuild()`.

## Important Types

`Fts5Index` is the module handle. It stores the virtual-table config, `%_data` table name, in-memory `Fts5Hash`, pending write counters, error state, prepared statements, read-only blob handle, cached structure pointer, and data-version used to identify cached structure freshness.

`Fts5Structure`, `Fts5StructureLevel`, and `Fts5StructureSegment` model the persistent segment tree. Levels contain oldest-to-newest segment arrays and `nMerge` tracks incremental merge inputs. Segments carry leaf page ranges, segment ids, and V2 contentless-delete metadata.

`Fts5Data` wraps a raw `%_data` blob plus its total size and leaf-body size. Reads pad allocation with zero bytes so varint and corruption handling can avoid unsafe overreads.

`Fts5SegIter` iterates through a single segment or in-memory hash doclist. It tracks current leaf page, term, rowid, position-list offset/size, doclist-index iterator, reverse-iteration offsets, and lazily loaded tombstone pages.

`Fts5Iter` is the merged iterator returned to higher layers. It contains a power-of-two array of `Fts5SegIter` objects and a tournament tree (`aFirst`) that selects the next term/rowid across all segments. It also owns output buffers and optional `Fts5Colset` filtering.

`Fts5SegWriter`, `Fts5PageWriter`, and `Fts5DlidxWriter` write segment leaves, page footers, `%_idx` entries, and doclist-index b-trees.

`Fts5TokenDataIter` and `Fts5TokenDataMap` support `tokendata=1` and `xInstToken()` by mapping rowid/position pairs back to the token term that produced them.

`Fts5TombstoneArray` is a reference-counted, lazily populated array of tombstone hash pages shared across related segment iterators.

## Data Access And Structure Management

`fts5DataRead()` is the central `%_data` reader. It reuses a read-only incremental blob handle when possible, reopens it for the requested rowid, treats `SQLITE_ERROR` from blob open/reopen as virtual-table corruption, allocates padded `Fts5Data`, reads the blob, sets `szLeaf`, increments `nRead`, and stores failures in `Fts5Index.rc`. `fts5LeafRead()` adds leaf-specific validation that `szLeaf` is within bounds.

`fts5DataWrite()` uses a cached `REPLACE INTO %_data(id, block)` statement. `fts5DataDelete()` deletes rowid ranges. `fts5DataRemoveSegment()` deletes all normal leaf/doclist-index records for a segment, deletes tombstone pages if present, and removes `%_idx` rows for the segment.

`fts5IndexPrepareStmt()` centralizes persistent prepared-statement creation and treats missing or altered backing tables as corruption when prepare returns `SQLITE_ERROR`.

`fts5StructureRead()` caches the decoded structure object, keyed by `PRAGMA data_version`, and `fts5StructureInvalidate()` drops the cache after writes or rollback. Structure objects are reference-counted because iterators and mutation paths may share them; `fts5StructureMakeWritable()` clones when a shared structure must be edited.

Structure promotion and merge planning are handled by `fts5StructurePromoteTo()`, `fts5StructurePromote()`, `fts5IndexMerge()`, `fts5IndexAutomerge()`, and `fts5IndexCrisismerge()`. Promotion keeps very small or newly large segments from remaining on poorly chosen levels, while automerge and crisismerge bound the number of segments accumulated by writes.

## Segment And Multi-Iterator Control Flow

Single-segment iteration starts with `fts5SegIterInit()` for full scans, `fts5SegIterSeekInit()` for exact/GE seeks, `fts5SegIterNextInit()` for tokendata continuation, or `fts5SegIterHashInit()` for in-memory hash contents. The iterator chooses its `xNext` function based on reverse mode and `detail=none`.

Forward iteration is split between `fts5SegIterNext()` and `fts5SegIterNext_None()`. They advance within a doclist, cross leaf-page boundaries, decode new terms, decode rowid deltas, and set position-list output state. `fts5SegIterLoadTerm()`, `fts5SegIterLoadRowid()`, and `fts5SegIterLoadNPos()` are the core decoders.

Reverse iteration uses `fts5SegIterReverse()`, `fts5SegIterReverseInitPage()`, and `fts5SegIterReverseNewPage()` to locate the last rowid in a doclist, build rowid-offset tables for the current page, and walk backward through pages. If a doclist-index exists, `fts5SegIterNextFrom()` can jump closer to a requested rowid before scanning.

Doclist-index iteration is implemented by `Fts5DlidxIter` and helpers from `fts5DlidxLvlNext()` through `fts5DlidxIterPgno()`. These functions traverse single or multi-level doclist-index b-trees in forward or reverse order and expose leaf page/first-rowid pairs to segment iterators.

`fts5MultiIterNew()` allocates and initializes a merged iterator over all structure segments and optionally the in-memory hash. `fts5MultiIterFinishSetup()` builds a tournament tree over sub-iterators. `fts5MultiIterNext()` advances the winner, skips duplicate lower-priority entries, applies delete-marker and tombstone filtering, and sets public output fields. `fts5MultiIterNext2()` is a lighter variant for prefix scans that need to know when a new term might have started.

The merge tree treats segment ordering as priority: newer segments shadow older entries with the same term/rowid. `fts5MultiIterIsEmpty()` detects delete markers with empty position lists, and `fts5MultiIterIsDeleted()` checks contentless-delete tombstones.

## Position Lists, Column Filters, Prefix Queries, And Tokendata

`fts5ChunkIterate()` streams a position list that may span leaf pages to a callback. `fts5SegiterPoslist()` uses it to either copy a full position list or filter it by a column set. Output callbacks handle `detail=full`, `detail=columns`, and `detail=none` differences.

`fts5IterSetOutputCb()` chooses one of several output callbacks: no output, detail-none row count behavior, direct no-colset output, zero-colset output, full-detail filtering, or optimized detail-column filtering for <=100 columns.

Prefix queries are not always satisfied by a dedicated prefix index. `sqlite3Fts5IndexQuery()` selects a prefix index when one has matching character length, can use the next-longer prefix index plus the main index for some cases, or falls back to scanning main-index terms. `fts5VisitEntries()` provides the generic term-range visitor used by prefix setup. `fts5SetupPrefixIter()` merges all matching term doclists into a synthetic doclist and wraps it with `fts5MultiIterNew2()`.

Prefix doclist merging uses `fts5MergeRowidLists()` for `detail=none` and `fts5MergePrefixLists()` for full/column detail. The latter merges duplicate rowids and sorted position lists, carefully preserving varint encoding and allocating padding for corrupt-input detection.

`tokendata=1` handling is more complex because multiple indexed terms may correspond to a single query token. `fts5SetupTokendataIter()` builds a set of iterators, one for each indexed term matching the token-data prefix form. `fts5IterSetOutputsTokendata()` merges row outputs across those iterators and, for full detail, accumulates maps from row positions to term iterators. `sqlite3Fts5IterToken()`, `sqlite3Fts5IndexIterClearTokendata()`, and `sqlite3Fts5IndexIterWriteTokendata()` expose or populate the token maps used by `xInstToken()`.

## Write, Flush, Merge, And Delete Behavior

Writes enter through `sqlite3Fts5IndexBeginWrite()` and `sqlite3Fts5IndexWrite()`. `BeginWrite` ensures the in-memory hash exists and flushes it if rowid order changes, a delete follows an insert for the same rowid, or the hash exceeds `nHashSize`. `IndexWrite` writes the token to the main index and to configured prefix indexes using index prefix bytes starting at `FTS5_MAIN_PREFIX`.

`fts5IndexFlush()` flushes pending hash data or pending contentless deletes by calling `fts5FlushOneHash()`. The flush path scans hash terms in order, writes a new level-0 segment through `Fts5SegWriter`, updates structure metadata, promotes segments as needed, runs automerge and crisismerge, writes the structure record, and clears the hash on success.

Segment writing is assembled from `fts5WriteInit()`, `fts5WriteAppendTerm()`, `fts5WriteAppendRowid()`, `fts5WriteAppendPoslistData()`, `fts5WriteFlushLeaf()`, `fts5WriteFlushBtree()`, and `fts5WriteFinish()`. These functions maintain leaf headers, page-index footers, prefix-compressed terms, delta rowids, position-list splitting at varint boundaries, doclist-index pages, and `%_idx` split keys.

Incremental merge is handled by `fts5IndexMergeLevel()`. It opens a multi-iterator across input segments, writes a merged output segment, drops annihilated delete markers when allowed, preserves delete markers when necessary, trims partially consumed input segments if the work budget runs out, and deletes fully consumed segments from `%_data` and `%_idx`. `fts5TrimSegments()` rewrites the first remaining page of partially merged inputs so future merge steps resume correctly.

Ordinary delete operations are represented as delete markers in doclists and resolved during merge. Secure-delete mode is different: `fts5FlushSecureDelete()` upgrades the table version to `FTS5_CURRENT_VERSION_SECUREDELETE` if needed, seeks the existing term/rowid, and calls `fts5DoSecureDelete()` to rewrite existing segment leaf pages so the term occurrence is physically removed. `fts5SecureDeleteOverflow()` removes overflow position-list bytes from following pages, and `fts5SecureDeleteIdxEntry()` removes `%_idx` entries when secure deletion removes the last term from a leaf.

Contentless-delete mode uses V2 structure records and tombstone hash pages instead of editing segment contents immediately. `sqlite3Fts5IndexContentlessDelete()` finds segments whose origin range covers the deleted origin, increments counted tombstones once, and calls `fts5IndexTombstoneAdd()` for each matching segment. Tombstone additions may rewrite one hash page or rebuild the hash with more pages or a larger key size. Later reads skip tombstoned rowids, and `fts5IndexFindDeleteMerge()` can choose levels for delete-driven merge work when tombstone density exceeds the `deletemerge` threshold.

## Public APIs In This Chunk

Key external functions implemented in this span include:

- `sqlite3Fts5IndexOpen()`, `sqlite3Fts5IndexClose()`, and `sqlite3Fts5IndexReinit()` for lifecycle and backing table initialization.
- `sqlite3Fts5IndexBeginWrite()`, `sqlite3Fts5IndexWrite()`, `sqlite3Fts5IndexSync()`, and `sqlite3Fts5IndexRollback()` for write transactions.
- `sqlite3Fts5IndexQuery()`, `sqlite3Fts5IterNext()`, `sqlite3Fts5IterNextScan()`, `sqlite3Fts5IterNextFrom()`, `sqlite3Fts5IterTerm()`, `sqlite3Fts5IterToken()`, `sqlite3Fts5IterClose()`, and tokendata helpers for query iteration.
- `sqlite3Fts5IndexOptimize()` and `sqlite3Fts5IndexMerge()` for explicit maintenance commands.
- `sqlite3Fts5IndexGetAverages()` and `sqlite3Fts5IndexSetAverages()` for the averages record.
- `sqlite3Fts5IndexSetCookie()`, `sqlite3Fts5IndexLoadConfig()`, `sqlite3Fts5IndexGetOrigin()`, `sqlite3Fts5IndexReads()`, and `sqlite3Fts5IndexContentlessDelete()` for metadata, diagnostics, and special table modes.
- `sqlite3Fts5IndexEntryCksum()` and the beginning of debug-only integrity helpers.

## Dependencies And Integration Points

This file depends heavily on internal FTS5 services declared in `fts5Int.h`: configuration loading and error reporting, `Fts5Hash`, `Fts5Buffer`, varint helpers, position-list readers/writers, memory helpers, and query flags such as `FTS5INDEX_QUERY_PREFIX`, `FTS5INDEX_QUERY_DESC`, `FTS5INDEX_QUERY_SCAN`, and `FTS5INDEX_QUERY_SKIPEMPTY`.

It integrates with SQLite core through incremental blob I/O, prepared statements, `sqlite3_step/reset/finalize`, `sqlite3_mprintf`, `sqlite3_malloc64/realloc64/free`, `PRAGMA data_version`, and SQLite result codes. It also assumes the FTS5 virtual table layer has created `%_data`, `%_idx`, and `%_config` tables and that tokenizer/front-end code calls writes in acceptable rowid order.

The FTS query layer consumes `Fts5IndexIter` outputs (`iRowid`, `pData`, `nData`, `bEof`) and may call term/token helpers for vocab and `xInstToken()` behavior. The maintenance command layer calls optimize/merge APIs. Integrity-check code later in the file calls checksumming helpers and reissues index queries through this same public interface.

## State And Persistence Behavior

Persistent state is stored in `%_data`, `%_idx`, and `%_config`. `%_data` contains all binary blobs for structure, averages, segment leaves, doclist-index pages, and tombstone hash pages. `%_idx` is a routing index for term seeks. `%_config` is touched by secure-delete upgrade logic to persist the index version.

In-memory state is buffered in `Fts5Hash` until flush, with `nPendingData`, `nPendingRow`, `iWriteRowid`, and `bDelete` enforcing write ordering and flush thresholds. `flushRc` preserves flush errors while pending data remains. `nContentlessDelete` makes deletes contribute extra automerge work and is cleared on flush or discard.

The structure cache is explicitly invalidated around writes, rollback, reinit, and flush paths. Reference counting allows safe handoff to callers that need stable structure snapshots. Prepared statements and blob handles are cached for speed and closed/finalized at handle close or reader close.

Segment merge and secure-delete operations mutate existing persistent blobs in place, so corruption checks guard offsets, page bounds, rowid ordering, and footer consistency. Ordinary insert/delete writes append new segment data; automerge later rewrites merged segments and deletes obsolete ranges.

## Risks And Edge Cases

This code is high risk because it is both the FTS5 binary-format implementation and the query engine over that format.

- Corrupt or adversarial `%_data` blobs can produce invalid offsets, malformed varints, impossible page ranges, or overlapping segments. The code contains many `FTS5_CORRUPT_*` checks, but every decoder change needs careful bounds reasoning.
- `detail=none`, `detail=columns`, and `detail=full` use different position-list encodings and iteration paths. Fixes in one path may not apply to the others.
- Reverse iteration and `NextFrom()` depend on doclist-index metadata and per-page offset reconstruction. Off-by-one errors can silently skip or duplicate rowids.
- The tournament merge tree must preserve priority order across in-memory hash data and on-disk segments so newer delete markers or replacements shadow older entries.
- Prefix query fallback materializes a synthetic doclist. Large prefix ranges can be memory-intensive, and the merge code has special corruption padding to avoid overflow on malformed inputs.
- Secure-delete rewrites leaf bodies and footers in place, including overflow pages and `%_idx` entries. This path is especially sensitive to term/footer offset consistency.
- Contentless-delete tombstone hashes are rebuilt dynamically and use modulo page selection plus open addressing. Key-size upgrades, rowid zero, full pages, and counted tombstone metadata must stay synchronized with structure records.
- Structure V2 compatibility matters: legacy databases must remain readable, while contentless-delete tables require origin counters and tombstone metadata to persist accurately.
- Blob readers can be invalidated by savepoint rollback; `fts5DataRead()` handles `SQLITE_ABORT` by reopening, but transaction-bound state changes remain subtle.
- Segment id allocation assumes `FTS5_MAX_SEGMENT` and checks `%_idx` in debug builds only. Production correctness depends on structure records accurately listing all live segments.

## Test Signals

Useful validation signals for this chunk include:

- FTS5 insert/query/delete tests across `detail=full`, `detail=columns`, and `detail=none`, including prefix indexes and no-prefix-index fallback scans.
- Rowid ascending and descending query tests, especially `sqlite3Fts5IterNextFrom()` with large doclists that require doclist-index jumps.
- Prefix query tests with multiple matching terms, duplicate rowids, merged position lists, column filters, and `tokendata=1`/`xInstToken()` behavior.
- Maintenance tests for automerge, crisismerge, explicit `merge`, and `optimize`, verifying segment counts, `%_idx` entries, and query results before and after merges.
- Secure-delete tests that inspect database bytes or use debug helpers to confirm deleted tokens and `%_idx` entries are physically removed.
- Contentless-delete tests covering origin ranges, tombstone hash growth/rebuild, rowid zero, 4-byte to 8-byte key upgrades, deletemerge selection, and query filtering of tombstoned rows.
- Corruption tests that mutate structure records, leaf headers, page footers, doclist-index pages, and tombstone pages and expect `SQLITE_CORRUPT_VTAB` plus useful FTS5 error messages.
- Transaction tests for rollback/savepoint behavior, reader invalidation, flush error persistence, and structure cache invalidation.
- Integrity-check/debug builds that exercise `fts5TestDlidxReverse()`, query checksum comparisons, prefix-index cross-checking, and UTF-8 term validation. The remainder of the integrity-check implementation appears after this chunk and should be covered by the adjacent research document.
