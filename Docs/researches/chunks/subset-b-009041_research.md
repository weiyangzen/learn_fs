# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 218441-226497

## Scope

This chunk covers the tail of SQLite's R-tree/geopoly extension, the optional ICU extension and FTS3 ICU tokenizer, and the start through most of the Resumable Bulk Update (RBU) extension implementation. It begins inside `geopolyBBox()` cleanup and continues through Geopoly predicates, Geopoly virtual-table methods, R-tree callback registration, ICU scalar/collation/tokenizer functions, the RBU public header embedded in the amalgamation, RBU handle/object-iterator/state machinery, RBU update/vacuum stepping, RBU state persistence, and the first RBU VFS shim methods through the beginning of `rbuVfsAccess()`.

The range is enabled only under the surrounding compile-time options in the amalgamation: R-tree/Geopoly code is gated by SQLite R-tree/Geopoly options, ICU code by `SQLITE_ENABLE_ICU`/`SQLITE_ENABLE_ICU_COLLATIONS`, FTS3 ICU tokenizer by `SQLITE_ENABLE_FTS3` plus ICU, and RBU by `SQLITE_ENABLE_RBU` or non-core extension builds.

## Purpose

- Finish Geopoly support by exposing SQL geometry functions, aggregate bounding-box calculation, polygon overlap/containment algorithms, and the `geopoly` virtual-table module layered on SQLite's R-tree implementation.
- Register R-tree virtual-table modules (`rtree`, `rtree_i32`) and public R-tree MATCH callback APIs that wrap application geometry/query callbacks into pointer results consumed by R-tree scans.
- Provide ICU-backed SQLite functions for Unicode-aware `LIKE`, `REGEXP`, `upper()`, `lower()`, runtime collation loading, and an FTS3 tokenizer that uses ICU word boundaries.
- Define the public RBU API and implement the early/mid RBU engine: opening handles, stepping resumable updates, applying update rows in sorted b-tree order, creating imposter tables, maintaining resumable state, moving OAL to WAL, running incremental checkpoints, and wrapping VFS methods so RBU can intercept WAL, SHM, locking, and temporary-file behavior.

## Important APIs, Types, And Functions

### Geopoly And R-tree

- `geopolyBBoxFunc()`, `geopolyBBoxStep()`, and `geopolyBBoxFinal()` implement scalar `geopoly_bbox()` and aggregate `geopoly_group_bbox()`, using `GeoBBox` aggregate context to accumulate min/max coordinates and returning a serialized Geopoly blob.
- `pointBeneathLine()` and `geopolyContainsPointFunc()` implement point-in-polygon testing using a ray-crossing count. Boundary hits return SQL integer `1`; interior points return `2`; outside returns `0`.
- `GeoEvent`, `GeoSegment`, `GeoOverlap`, `geopolyAddOneSegment()`, `geopolySortEventsByX()`, `geopolySortSegmentsByYAndC()`, and `geopolyOverlap()` implement a sweep-line style overlap classifier for two polygons. Results distinguish disjoint, overlap, containment by either side, and equality.
- `geopolyWithinFunc()` maps `geopolyOverlap()` classifications into the SQL `geopoly_within()` contract, while `geopolyOverlapFunc()` returns the full classifier.
- `geopolyInit()`, `geopolyCreate()`, and `geopolyConnect()` allocate and initialize an `Rtree` object configured for 2D float coordinates plus `_shape` as an auxiliary not-null column, declare the virtual table schema, initialize node size, and connect underlying R-tree storage tables.
- `geopolyFilter()` converts Geopoly rowid, overlap, and within query plans into R-tree cursor/search constraints. For overlap/within plans it computes the query polygon bounding box and installs four `RtreeConstraint` entries.
- `geopolyBestIndex()` selects direct rowid lookup, R-tree-assisted `geopoly_overlap()`/`geopoly_within()`, or full scan, and advertises cost/row estimates and constraint usage to SQLite.
- `geopolyColumn()` reads `_shape` and auxiliary columns using the R-tree auxiliary read statement and caches the aux row for the cursor.
- `geopolyUpdate()` translates virtual-table inserts/updates/deletes into R-tree cell changes plus auxiliary table updates, including text-to-blob polygon normalization and conflict behavior for duplicate rowids.
- `geopolyFindFunction()` overloads `geopoly_overlap()` and `geopoly_within()` so the virtual-table planner can see function constraints.
- `geopolyModule` wires the Geopoly module to R-tree cursor, transaction, rename, shadow-name, and integrity implementations where possible.
- `sqlite3_geopoly_init()` registers Geopoly scalar/aggregate SQL functions and the `geopoly` module. `sqlite3RtreeInit()` registers R-tree diagnostic functions, `rtree`, `rtree_i32`, and optionally Geopoly.
- `geomCallback()`, `sqlite3_rtree_geometry_callback()`, and `sqlite3_rtree_query_callback()` expose R-tree MATCH extension APIs. They allocate `RtreeGeomCallback`/`RtreeMatchArg` state, duplicate SQL parameters, and return a typed pointer result named `"RtreeMatchArg"`.

### ICU And FTS3 ICU

- `icuFunctionError()` formats ICU API failures into SQLite scalar-function errors.
- `icuLikeCompare()` and `icuLikeFunc()` implement Unicode case-folding `LIKE`, including `%`, `_`, and optional single-character ESCAPE handling. `SQLITE_MAX_LIKE_PATTERN_LENGTH` limits recursive pattern complexity.
- `icuRegexpFunc()` caches compiled `URegularExpression` objects with SQLite auxdata and runs `uregex_matches()` over UTF-16 input.
- `icuCaseFunc16()` implements one- and two-argument `upper()`/`lower()` using ICU `u_strToUpper()`/`u_strToLower()`, reallocating if ICU reports buffer overflow.
- `icuLoadCollation()`, `icuCollationColl()`, and `icuCollationDel()` open ICU collators, optionally apply a named strength, register UTF-16 SQLite collations, and close collators on destruction.
- `sqlite3IcuInit()` registers ICU SQL functions, and `sqlite3_icu_init()` exposes extension entry-point registration for non-core builds.
- `IcuTokenizer` and `IcuCursor` hold the FTS3 tokenizer locale, UTF-16 input copy, UTF-8 offsets, break iterator, output token buffer, and token index.
- `icuCreate()`, `icuOpen()`, `icuNext()`, `icuClose()`, `icuDestroy()`, and `sqlite3Fts3IcuTokenizerModule()` implement an FTS3 tokenizer module using ICU word breaks and case folding.

### RBU Public API And Core State

- The embedded `sqlite3rbu.h` declares public APIs: `sqlite3rbu_open()`, `sqlite3rbu_vacuum()`, `sqlite3rbu_step()`, `sqlite3rbu_savestate()`, `sqlite3rbu_close()`, `sqlite3rbu_progress()`, `sqlite3rbu_bp_progress()`, `sqlite3rbu_state()`, `sqlite3rbu_db()`, `sqlite3rbu_rename_handler()`, `sqlite3rbu_create_vfs()`, and `sqlite3rbu_destroy_vfs()`.
- `RbuState` mirrors persisted `rbu_state` rows such as stage, table, data table, index, row offset, progress, WAL checksum, database cookie, OAL size, and phase-one estimate.
- `RbuObjIter` tracks the current target table/index, source `data_xxx` table, target table columns/types/PK flags/indexed flags, prepared SELECT/INSERT/DELETE/UPDATE statements, imposter-table metadata, and per-table cleanup state.
- `sqlite3rbu` is the main handle. It owns target/RBU database handles, filenames, state database name, error state, progress counters, object iterator, private VFS name, target file descriptors, checkpoint frame list, temp-space accounting, and vacuum-specific state.
- `rbu_vfs` and `rbu_file` implement the RBU VFS wrapper and per-file shim state, including real VFS/file pointers, target/RBU links, open flags, database header cookie/write-version, WAL filename/file association, heap SHM pages, delete-on-close name, and linked-list membership.
- Stage constants distinguish OAL construction, OAL-to-WAL move, checkpoint capture, checkpoint copy, and done states. Operation constants distinguish row insert/delete/replace/update and index insert/delete.

## Control Flow

Geopoly scalar functions first normalize SQL values into `GeoPoly` blobs using helpers defined earlier in the file, then run geometry-specific calculations and return either blobs or integers. The overlap algorithm constructs one event list per non-vertical polygon segment, sorts events by X coordinate, maintains an active Y-sorted segment list, detects crossings between segments from opposite polygons, and records coverage masks to classify containment/equality/disjoint states.

Geopoly virtual-table execution follows the SQLite module lifecycle. `geopolyInit()` constructs an `Rtree`-backed virtual table with one required `_shape` auxiliary column and optional user columns. `geopolyBestIndex()` recognizes rowid and overloaded function constraints. `geopolyFilter()` resets the cursor, turns the chosen strategy into either a leaf lookup or a root R-tree scan with bounding-box constraints, then uses shared R-tree search code to reach candidate leaves. `geopolyUpdate()` rejects writes while nodes are referenced, computes new bounding boxes when shape/rowid changes, deletes old R-tree entries as needed, inserts new R-tree cells, and updates auxiliary row storage.

ICU scalar functions are invoked like normal SQLite functions. `icuLikeFunc()` validates ESCAPE and pattern length before recursing through UTF-8 codepoints. `icuRegexpFunc()` compiles/caches the pattern on argument 0 auxdata, sets the input text, matches, clears the regex text, and returns `1` or `0`. Collation loading is direct: open a `UCollator`, validate optional strength, then transfer ownership to SQLite via `sqlite3_create_collation_v2()`.

The ICU tokenizer lifecycle allocates tokenizer/cursor objects, converts input UTF-8 to folded UTF-16 while preserving original byte offsets, opens an ICU word break iterator, and returns successive non-whitespace word spans converted back to UTF-8.

RBU starts in `sqlite3rbu_open()` or `sqlite3rbu_vacuum()`, both delegating to `openRbuHandle()`. Handle open creates a private RBU VFS, opens target/RBU/state databases, creates or loads `rbu_state`, checks WAL-mode and cookie constraints, initializes phase-one progress estimation from `rbu_count`, starts transactions, and positions `RbuObjIter` at the saved table/index/row if resuming.

During `RBU_STAGE_OAL`, `sqlite3rbu_step()` repeatedly prepares work for the current object via `rbuObjIterPrepareAll()`, advances the source SELECT one row, increments progress, and calls `rbuStep()`. `rbuStep()` decodes `rbu_control` through `rbuStepType()`, then performs delete/insert/replace/index operations with `rbuStepOneOp()` or update operations through cached dynamic `UPDATE` statements from `rbuGetUpdateStmt()`. When a table has indexed columns, temporary triggers populate `rbu_tmp_xxx` with old/new index keys so auxiliary index b-trees can be updated in sorted order.

Object preparation is SQL-generation heavy. `rbuObjIterCacheTableInfo()` discovers target table shape, validates source columns, checks `rbu_rowid` requirements, and marks indexed columns. `rbuCreateImposterTable()` and `rbuCreateImposterTable2()` use `SQLITE_TESTCTRL_IMPOSTER` to create writable aliases for target b-trees and external primary-key indexes. `rbuObjIterGetIndexCols()`, `rbuObjIterGetWhere()`, `rbuObjIterGetSetlist()`, and related helpers generate quoted column lists, PK predicates, index key projections, bind lists, and update SET clauses.

After phase one finishes, RBU saves `RBU_STAGE_MOVE`, increments the schema cookie, commits both DB handles, and moves to `RBU_STAGE_MOVE`. `rbuMoveOalFile()` closes and reopens handles, obtains an exclusive lock, renames `*-oal` to `*-wal` through the registered rename callback, reopens in normal WAL mode, and sets up checkpointing.

Checkpoint setup runs a restart checkpoint in special capture mode so the VFS records WAL frame-to-database-page mappings instead of doing IO. `RBU_STAGE_CKPT` copies frames with `rbuCheckpointFrame()` in sector-aligned groups, syncs the database, updates WAL shared-memory backfill state, and finishes with `SQLITE_DONE`. `sqlite3rbu_savestate()` and `sqlite3rbu_close()` commit/sync as needed and persist resumable state with `rbuSaveState()`.

The RBU VFS methods in this chunk wrap the underlying VFS. `rbuVfsOpen()` substitutes `*-oal` for `*-wal` while building OAL, associates WAL and main DB file handles, optionally opens `rbu_memory=1` targets as delete-on-close temp DBs, and installs RBU IO methods. `rbuVfsRead()`/`rbuVfsWrite()` capture page header cookie/write-version, synthesize the first vacuum target page when needed, track OAL size, track temp file size, and record checkpoint frame/page mappings in capture mode. Lock/SHM methods block unsafe exclusive/checkpoint behavior and substitute heap SHM pages during OAL construction.

## State And Persistence Behavior

Geopoly state is stored as R-tree rows plus an auxiliary `_shape` column. `_shape` text values may be normalized to Geopoly blob format on write. Bounding boxes are persisted in the underlying R-tree coordinate storage, while `_shape` and user auxiliary columns are persisted through R-tree auxiliary tables.

ICU functions and tokenizer state are per-call/per-cursor in memory. ICU collations persist only as registrations on the SQLite connection; compiled regex objects are cached for the lifetime SQLite assigns to auxdata.

RBU has substantial persistent state:

- The RBU input database supplies `data_xxx` tables and optional `rbu_count`.
- `rbu_state` is created in the RBU DB or attached state DB and stores the resumable cursor: stage, table, data table, index, row offset, progress, WAL checksum, database change-counter cookie, OAL size, and phase-one estimate.
- During phase one, writes go to an OAL file (`<database>-oal`) rather than a normal WAL. The target database remains readable by non-RBU clients in rollback-mode semantics until the OAL is moved.
- The move stage renames OAL to WAL under exclusive lock, making the update visible through normal WAL recovery semantics.
- The checkpoint stage copies WAL frames into the database incrementally, saving progress so interruption can resume.
- RBU vacuum mode builds a new target-like database, copies schema and selected pragmas, uses a state database for resumability, and may synthesize file header state while the target temp database is initially empty.

RBU also persists safety decisions in the database header and WAL/shm state. It compares the target database cookie loaded from page 1 against `RBU_STATE_COOKIE` to detect modifications during an RBU update, and compares the saved WAL-index checksum against the current checksum before resuming a checkpoint.

## Dependencies And Integration Points

- Geopoly integrates with the R-tree module's `Rtree`, `RtreeCursor`, `RtreeNode`, search-point queues, SQL statement cache, node management, and transaction helpers defined earlier in `sqlite3.c`.
- Virtual-table integration depends on SQLite module callbacks, `sqlite3_vtab_config()`, `sqlite3_declare_vtab()`, `sqlite3_index_info`, constraint-overload APIs, and `sqlite3_vtab_nochange()`.
- R-tree callback APIs integrate with application-defined `sqlite3_rtree_geometry` and `sqlite3_rtree_query_info` callbacks using typed pointer results and SQLite function destructors.
- ICU integration depends on ICU headers/APIs: `uregex_*`, `u_strToUpper()`, `u_strToLower()`, `u_foldCase()`, `ucol_*`, `ubrk_*`, and UTF macros such as `U8_NEXT`, `U16_APPEND`, and `U16_NEXT`.
- FTS3 ICU tokenizer integrates with the legacy `sqlite3_tokenizer_module` interface.
- RBU integrates tightly with SQLite core internals: file controls (`SQLITE_FCNTL_RBU`, `SQLITE_FCNTL_RBUCNT`, VFS pointer, file pointer, ZIPVFS), `SQLITE_TESTCTRL_IMPOSTER`, SQLite schema pragmas, WAL locks and shared-memory layout, DB header offsets, VFS IO method tables, `sqlite_schema`, temporary triggers, and transaction handling.
- RBU has optional platform integration for WinCE rename via `MoveFileW()` and zipvfs via special file controls. The default rename path uses C `rename()`.

## Risks And Edge Cases

- Geopoly geometry predicates compare floating-point coordinates for exact equality in several places. Boundary, equality, crossing, and containment classifications may be sensitive to precision, degenerate polygons, repeated points, and near-collinear segments.
- `geopolyOverlap()` ignores vertical segments when building the sweep-line event set. Other point-in-polygon code handles vertical boundaries, but overlap classification depends on the algorithm's assumptions about polygon representation and coverage masks.
- `geopolyUpdate()` blocks writes when R-tree nodes are referenced, but callers may still observe `SQLITE_LOCKED_VTAB` in read/write concurrency patterns involving active cursors.
- Geopoly text-to-blob normalization during aux writes means invalid text shapes can fail either bounding-box computation or conversion and produce virtual-table errors.
- ICU `LIKE` uses recursive matching for `%`, bounded by pattern length but still potentially expensive on adversarial patterns near the configured maximum.
- `icuRegexpFunc()` caches compiled patterns as auxdata, so correctness depends on SQLite invalidating auxdata when the pattern changes; ICU errors are surfaced as SQL errors.
- ICU tokenizer offset handling depends on the UTF-8 to folded UTF-16 conversion preserving meaningful token boundaries after case folding; unusual Unicode case-fold expansions or invalid input can produce conversion errors.
- RBU uses extensive dynamic SQL against schema names and `PRAGMA` output. Most identifiers are quoted with `%w`/`%Q`, but logic is still sensitive to unusual schemas, expression indexes, partial indexes, generated/hidden columns, and virtual-table behavior.
- RBU relies on imposter tables through `SQLITE_TESTCTRL_IMPOSTER`, a powerful internal test-control interface. Incorrect rootpage, schema, PK, or collation reconstruction can corrupt target b-trees.
- RBU state commits are not fully atomic with OAL/WAL side effects. The comments explicitly note possible inconsistency after power loss, usually surfacing as constraint errors or restart from saved state.
- RBU refuses targets already in WAL mode during OAL construction and uses VFS tricks to detect/deny WAL presence. Damaged headers, stacked VFSes, or zipvfs setup mistakes can produce hard errors.
- Checkpoint resume is invalidated if another writer appends to WAL, detected by WAL-index checksum mismatch. That avoids unsafe continuation but can mark the operation done rather than continuing the old checkpoint.
- The RBU VFS mutates the WAL filename buffer in `rbuVfsOpen()` by changing the suffix from `-wal` to `-oal`; this assumes SQLite-owned filename buffers are writable and formatted as expected in this code path.
- Locking behavior intentionally blocks exclusive locks before done to prevent automatic checkpointing at close. This can surprise integrations expecting ordinary SQLite close/checkpoint behavior.
- RBU temp-space accounting only applies to delete-on-close files associated with the RBU handle; other temporary allocations or lower VFS behavior may not be reflected in `szTemp`.

## Test Signals

- Geopoly SQL tests should cover `geopoly_bbox()`, `geopoly_group_bbox()`, `geopoly_contains_point()`, `geopoly_overlap()`, `geopoly_within()`, rowid lookup, overlap/within indexed queries, inserts/updates/deletes of `_shape`, malformed polygons, rowid conflicts, and concurrent cursor/write locking.
- R-tree callback tests should register geometry and query callbacks, pass multiple SQL parameter types, verify MATCH receives duplicated parameters, and verify destructor paths.
- ICU tests should exercise Unicode `LIKE` with `%`, `_`, ESCAPE, long pattern rejection, `REGEXP` success/failure and invalid regex errors, locale-sensitive upper/lower behavior, collation loading with valid/invalid strengths, and extension init paths.
- FTS3 ICU tokenizer tests should cover locale-specific word breaks, UTF-8 offset reporting, whitespace skipping, empty/null input, invalid UTF sequences, and buffer growth when converting tokens back to UTF-8.
- RBU open/step/close tests should cover fresh updates, resume after `sqlite3rbu_savestate()`, resume after `sqlite3rbu_close()`, empty updates, update databases with `dataN_table` ordering, and malformed `rbu_control` values.
- RBU table-shape tests should include rowid tables, explicit integer primary keys, external primary keys, WITHOUT ROWID tables, virtual tables, required/prohibited `rbu_rowid`, missing columns, not-null/PK enforcement, expression indexes, partial indexes, unique indexes, and descending PK/index columns.
- RBU operation tests should cover insert, delete, replace, update masks with `x`, no-op `.`, `d` delta, and `f` fossil delta; IPK NULL insert mismatch; non-existing delete/update rows; and index b-tree maintenance via `rbu_tmp_xxx` triggers.
- RBU persistence tests should interrupt in OAL, MOVE, and CKPT stages, verify `rbu_state` fields, verify database cookie mismatch detection, verify OAL size continuation, verify WAL checksum mismatch behavior, and confirm progress APIs return sensible phase-one/phase-two values.
- RBU VFS tests should cover `*-wal` to `*-oal` substitution, heap SHM in OAL stage, denied WAL-mode targets, exclusive checkpoint URI behavior, zipvfs stack detection, temp-size limits, sector-size grouping during checkpoint, 8.3 filename suffix shortening, custom rename handlers, and cleanup of private VFS/file lists.
