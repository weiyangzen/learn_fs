# sources/storage-engines/sqlite/ext/fts5/fts5_index.c lines 8346-9560

## Scope

This chunk covers the end of the FTS5 index integrity-check implementation and the test/debug helpers registered by `sqlite3Fts5IndexInit()`. It starts inside the debug-only `fts5TestTerm()` query cross-check, then covers segment/page-index integrity validation, full index checksum validation, `fts5_decode()` and `fts5_decode_none()` record decoders, `fts5_rowid()`, the `fts5_structure` table-valued function, and `sqlite3Fts5IndexReset()`.

The code is split between production integrity checking and diagnostics compiled only with `SQLITE_TEST` or `SQLITE_FTS5_DEBUG`. Normal builds still include the integrity-check entry point and reset logic, while the scalar/table-valued debugging aids are registered as no-ops outside those debug/test feature gates.

## Purpose

- Validate that FTS5 on-disk segment metadata, `%_idx` entries, leaf page contents, doclist-index records, and index checksums agree with each other.
- Compare the checksum of actual index contents with the checksum expected by the storage layer during FTS5 integrity checks.
- In `SQLITE_DEBUG` builds, run additional expensive self-checks that compare forward and reverse query results, prefix-index results against no-index scans, and doclist-index forward/reverse iteration.
- Provide human-readable decoding of FTS5 `%_data` records for tests and debugging through `fts5_decode()` and `fts5_decode_none()`.
- Provide `fts5_rowid('segment', segid, pgno)` so tests can compute segment-data rowids without duplicating internal rowid packing rules.
- Expose serialized FTS5 structure records through the debug-only `fts5_structure` virtual table, including segment id, level, merge state, leaf range, contentless-delete origins, and tombstone counts.
- Invalidate the cached `Fts5Structure` if `PRAGMA data_version` changed since it was read.

## Important APIs, Types, And Functions

- `fts5TestTerm()` is debug-only. For each term transition during a linear integrity scan, it queries the previous term and verifies ASC/DESC checksum parity. For prefix indexes it can also compare indexed prefix results against `FTS5INDEX_QUERY_TEST_NOIDX` scans when pending hash data is empty and the term bytes are valid UTF-8.
- `fts5IndexIntegrityCheckEmpty()` verifies that leaf pages in a gap exist, have no terms, and optionally have no first-rowid pointer. It is used to validate empty pages between `%_idx` split-key entries and doclist-index-covered ranges.
- `fts5IntegrityCheckPgidx()` reconstructs each term referenced by a leaf page-index (`pgidx`), checks that offsets stay inside the leaf body, verifies prefix-compressed term reconstruction bounds, and enforces strictly increasing term order.
- `fts5IndexIntegrityCheckSegment()` validates a single `Fts5StructureSegment`. It scans `%_idx` rows for the segment, reads each referenced leaf, verifies split-key ordering, validates the leaf `pgidx`, checks empty leaves between indexed leaves, and validates doclist-index entries when present.
- `sqlite3Fts5IndexIntegrityCheck()` is the public index-layer integrity API used by FTS5 storage. It loads the current `Fts5Structure`, checks every segment, scans all terms and rowids with a multi-iterator, computes `sqlite3Fts5IndexEntryCksum()` values, and optionally compares the result with the caller-provided checksum.
- `fts5DecodeRowid()` unpacks `%_data` rowid bits into tombstone flag, segment id, doclist-index flag, tree height, and page number. `fts5DebugRowid()` formats those components.
- `fts5DecodeStructure()` and `fts5DebugStructure()` decode a serialized `Fts5Structure` blob and print levels, merge counts, segment ids, leaf ranges, and origin ranges.
- `fts5DecodeAverages()`, `fts5DecodePoslist()`, `fts5DecodeDoclist()`, and `fts5DecodeRowidList()` decode specific `%_data` payload formats into textual output.
- `fts5DecodeFunction()` implements both `fts5_decode()` and `fts5_decode_none()`. It pads a copy of the input blob, decodes by rowid kind, and dispatches to structure, averages, doclist-index, tombstone-hash, detail=none leaf, or normal/detail leaf decoding.
- `fts5RowidFunction()` implements `fts5_rowid()`, currently supporting only the `"segment"` subject.
- `Fts5StructVtab` and `Fts5StructVcsr` implement the `fts5_structure` virtual table cursor over a decoded structure blob supplied through the hidden `struct` column.
- `sqlite3Fts5IndexInit()` registers debug/test SQL helpers: `fts5_decode`, `fts5_decode_none`, `fts5_rowid`, and the `fts5_structure` module.
- `sqlite3Fts5IndexReset()` compares `fts5IndexDataVersion(p)` with `p->iStructVersion` and calls `fts5StructureInvalidate()` on mismatch.

## Control Flow

`sqlite3Fts5IndexIntegrityCheck()` first calls `fts5StructureRead()`. If no structure can be loaded, it returns the existing `Fts5Index.rc` through `fts5IndexReturn()`. Otherwise it walks every level and segment in the structure and calls `fts5IndexIntegrityCheckSegment()` for each one.

Segment integrity checking scans `%_idx` with `SELECT segid, term, (pgno>>1), (pgno&1) ... ORDER BY 1, 2`. For each usable split-key row, it reads the corresponding leaf from `%_data`. A non-empty leaf must have a first term greater than or equal to the split key, a rowid pointer before the first term, and a valid page-index. A secure-delete special case allows the very first segment page to remain represented in `%_idx` even if it has been reduced to an empty four-byte leaf. Gaps before each indexed leaf are checked as termless leaves. If the `%_idx` row advertises a doclist-index, the code iterates it, verifies rowid-less intermediate leaves, and confirms each advertised leaf contains the expected first rowid, with relaxed comparisons for secure-delete pages that may have had rowids removed.

After structural validation, `sqlite3Fts5IndexIntegrityCheck()` scans all index entries with `fts5MultiIterNew(... FTS5INDEX_QUERY_NOOUTPUT ...)`. For `detail=none`, non-empty entries contribute one checksum item per rowid. For other detail modes, the code materializes the current position list, appends zero padding, iterates positions with `sqlite3Fts5PoslistNext64()`, and adds one checksum item per column/token offset. If `bUseCksum` is true and the computed checksum differs from the storage-layer checksum, it reports an FTS5 corruption error for the table.

In debug builds, the linear scan also calls `fts5TestTerm()` whenever the term changes. That helper queries the previous term normally and in descending order, then for prefix indexes optionally queries with the prefix index disabled. The accumulated query checksum must match the linear-scan checksum at the same point. This gives coverage for query paths that a pure linear scan would not exercise.

The decode path starts in `fts5DecodeFunction()`. It copies the SQL blob argument into a newly allocated buffer with `FTS5_DATA_ZERO_PADDING` bytes of trailing zeros, decodes the rowid, appends a formatted rowid prefix, then selects a decoding strategy. Doclist-index rows are stepped with `fts5DlidxLvlNext()`. Tombstone hash pages print element counts and non-zero slots. Segment id zero rows decode as averages or structure records. Detail=none leaf pages decode rowid lists and prefix-compressed terms. Normal leaf pages decode any leading poslist/doclist tail, then use the page-index to find each term/doclist boundary.

The `fts5_structure` virtual table requires an equality constraint on hidden column `struct`. `xFilter` decodes that blob into an `Fts5Structure`, initializes the cursor before the first segment, and calls `xNext`. `xNext` advances segment then level, releasing the decoded structure at EOF. `xColumn` maps cursor state to level, segment ordinal, merge flag, segid, leaf range, origin range, tombstone page count, tombstone entry count, and segment entry count.

## State And Persistence Behavior

The integrity-check functions do not intentionally mutate index contents. They read `%_data`, `%_idx`, and the serialized structure record, and mutate only in-memory error/check state:

- `Fts5Index.rc` carries corruption, OOM, SQL, and finalize errors through helper calls.
- `sqlite3Fts5ConfigErrmsg()` records table-specific corruption messages for rowid/blob failures and checksum mismatches.
- Temporary `Fts5Buffer` instances hold reconstructed terms, position lists, decoded output, and previous-term state.
- `Fts5Data` pages read from `%_data` are reference-count-neutral local objects released after each check or decode.
- `Fts5DlidxIter` and `Fts5Iter` instances are transient iterators over doclist-index pages and merged segment contents.
- `Fts5StructVcsr.pStruct` owns a decoded structure while the debug virtual table cursor is active and releases it at EOF or close.

Persistent storage assumptions are central to the checks. `%_idx.pgno` packs a leaf page number and doclist-index flag; `%_data` segment rowids are built by `FTS5_SEGMENT_ROWID()` and unpacked by `fts5DecodeRowid()` in debug tools; leaf bodies store rowid offsets, page-index offsets, term data, doclists, and optional doclist-index references; secure-delete and contentless-delete modes allow tombstone metadata and removed entries that make some exact equality checks intentionally looser.

`sqlite3Fts5IndexReset()` is the only routine here that changes cached index state in normal operation. It reads the database data-version and invalidates `p->pStruct` if another connection or operation changed the underlying table since the structure was cached.

## Dependencies And Integration Points

- FTS5 storage calls `sqlite3Fts5IndexIntegrityCheck()` from `fts5_storage.c` after computing the expected checksum over logical table contents.
- Structure handling depends on `fts5StructureRead()`, `fts5StructureDecode()`, `fts5StructureRelease()`, and `fts5StructureInvalidate()` from earlier in `fts5_index.c`.
- Low-level page IO depends on `fts5DataRead()`, `fts5LeafRead()`, `fts5DataRelease()`, `FTS5_SEGMENT_ROWID()`, and `%_idx` SQL prepared through `fts5IndexPrepareStmt()`.
- Iterator integration uses `fts5MultiIterNew()`, `fts5MultiIterNext()`, `fts5MultiIterTerm()`, `fts5MultiIterRowid()`, `fts5MultiIterIsEmpty()`, `fts5SegiterPoslist()`, and `fts5MultiIterFree()`.
- Doclist-index checks and decoding use `fts5DlidxIterInit()`, `fts5DlidxIterNext()`, `fts5DlidxIterPrev()`, `fts5DlidxIterPgno()`, `fts5DlidxIterRowid()`, `fts5DlidxLvlNext()`, and `fts5DlidxIterFree()`.
- Position-list decoding depends on `sqlite3Fts5PoslistNext64()`, `sqlite3Fts5PoslistReaderInit()`, `sqlite3Fts5PoslistReaderNext()`, `FTS5_POS2COLUMN()`, and `FTS5_POS2OFFSET()`.
- SQLite SQL-function and virtual-table APIs are used directly: `sqlite3_create_function()`, `sqlite3_create_module()`, `sqlite3_value_*()`, `sqlite3_result_*()`, `sqlite3_declare_vtab()`, and `sqlite3_index_info`.
- Compile-time gates matter: `SQLITE_DEBUG` enables extra integrity self-tests; `SQLITE_TEST` or `SQLITE_FTS5_DEBUG` enables SQL-facing debug helpers.
- Tests under `ext/fts5/test` reference these helpers heavily, including `fts5rowid.test`, `fts5corrupt*.test`, `fts5fault1.test`, `fts5secure*.test`, and `fts5contentless*.test`.

## Risks And Edge Cases

- Integrity checking sits on a corruption boundary. Most parsing reads varints and offsets from on-disk blobs, so every offset check before using reconstructed terms, doclist ranges, or page-index entries matters.
- `fts5IntegrityCheckPgidx()` must keep the reconstructed previous term consistent with the compressed current term. A missed `nKeep` or `nByte` bound check could turn corrupt disk data into an out-of-bounds read.
- The doclist-index check has secure-delete exceptions. In secure-delete mode, removed rowids can make the first rowid greater than the doclist-index advertised rowid, while non-secure-delete still expects equality.
- `fts5IndexIntegrityCheckSegment()` contains a TODO for proving that no doclist index exists when `%_idx` does not advertise one. Corruption in stray doclist-index records may not be detected by this path.
- The final rightmost-leaf check is disabled with `#if 0`, so the current segment scan does not enforce that the last `%_idx` entry reaches `pSeg->pgnoLast`.
- Debug prefix self-tests are skipped when pending hash data exists, because the hash table supports only one scan query at a time. Bugs that require pending in-memory data may escape this extra debug comparison.
- `fts5TestUtf8()` gates no-index prefix comparisons, but it is deliberately a lightweight validator for test safety rather than a full text subsystem.
- `fts5DecodeFunction()` uses zero padding to reduce overread risk on corrupt records, but debug decoding still trusts many format details enough to be a diagnostic aid, not a hardened parser for untrusted blobs.
- The tombstone decoder reads `aBlob[0]` and `aBlob[1]` after allocation; malformed very-short blobs rely on SQLite value/blob behavior and padding assumptions, so tests should keep exercising corrupt tombstone inputs.
- `fts5structBestIndexMethod()` requires `struct=?`; without it the virtual table returns `SQLITE_CONSTRAINT`. Callers must supply the serialized structure blob explicitly.
- `sqlite3Fts5IndexReset()` assumes `p->iStructVersion` is non-zero when `p->pStruct` is cached. The assertion protects the cache-version contract in debug builds.

## Test Signals

- FTS5 `integrity-check` should pass for populated tables using `detail=full`, `detail=col`, and `detail=none`, with and without prefix indexes.
- Corruption tests should delete or corrupt `%_data` leaf pages, `%_idx` rows, page-index offsets, split keys, doclist-index pages, rowid pointers, and structure records, then verify `SQLITE_CORRUPT_VTAB` or table-specific corruption messages.
- Checksum tests should cover both `bUseCksum` enabled and disabled paths, including mismatches between logical storage checksums and physical index scan checksums.
- Debug builds should exercise ASC/DESC term query parity, prefix-index versus no-index parity, and doclist-index forward/reverse parity.
- Secure-delete tests should cover empty first leaf pages retained in `%_idx`, removed first rowids, detail=none/detail=col secure-delete tables, and version transitions.
- Contentless-delete tests should inspect `fts5_structure` columns for `loc1`, `loc2`, `npgtombstone`, `nentrytombstone`, and `nentry`.
- `fts5_decode()` tests should decode structure row `id=10`, averages records, normal segment leaves, doclist-index rows, tombstone hash pages, and malformed blobs without leaking memory.
- `fts5_decode_none()` tests should cover detail=none leaf pages, rowid-list delete markers, and prefix-compressed terms.
- `fts5_rowid()` tests should verify accepted `segment` calls and the documented error strings for no arguments, wrong arity, and unknown subject.
- Reset/cache tests should change underlying FTS5 data from another statement or connection, call `sqlite3Fts5IndexReset()`, and verify cached structure invalidation before subsequent reads.
