# subset-b-009191 Research

Grouped research for the Syncthing SQLite database, typed KV wrapper, and selected generated protobuf surfaces. Each file section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_global_test.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_global_test.go

## Purpose
This test file exercises global-version selection and "need" calculations in the SQLite backend. It verifies how local and remote file rows interact when versions differ, files are deleted, ignored, invalid, or absent, and when devices or file rows are dropped.

## Important APIs and Control Flow
Tests drive the public `DB` API: `Open`, `Update`, `AllNeededGlobalFiles`, `CountNeed`, `CountGlobal`, `GetGlobalFile`, `DropAllFiles`, `DropDevice`, and `DropFilesNamed`. `TestNeed` sets local and remote vectors to prove local need and remote need are symmetric but not identical. `testDropWithDropper` abstracts three drop paths and asserts global recalculation after removing a winning remote row. The later tests focus on deleted globals, ignored local rows, remote invalid flags, missing deleted rows, pagination, symlink/directory need accounting, and a regression where a delete after a conflict must become global.

## State and Persistence Behavior
Each test creates a temporary SQLite database and writes file state into per-folder databases. The assertions depend on `folderdb_update.go` setting `FlagLocalGlobal` and `FlagLocalNeeded`, and on `folderdb_global.go` querying those flags correctly. Deleted files contribute to deleted counts rather than bytes; directories use synthetic size semantics from update code.

## Dependencies and Integration Points
The file uses `config.PullOrder*`, `protocol.FileInfo`, `protocol.Vector`, and helper constructors in `db_test.go`. It is the main behavioral test signal for `recalcGlobalForFile`, remote need SQL, count summarization, and public folder-device drop methods.

## Risks and Test Signals
The risk surface is subtle conflict resolution: invalid or ignored rows must not become needed or counted as valid globals, while delete rows must still win when their version vector does. Pagination tests ensure `LIMIT/OFFSET` are appended safely to need queries. The "deleted after conflict" regression captures a real-world global-selection bug and should be preserved around vector serialization or comparison changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_global_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_indexid_test.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_indexid_test.go

## Purpose
This test file validates per-folder, per-device index ID behavior. Index IDs identify a device's index stream and are persisted in the folder database `indexids` table.

## Important APIs and Control Flow
`TestIndexIDs` opens a temporary DB, then runs parallel subtests for local and remote devices. For `protocol.LocalDeviceID`, `GetIndexID` must lazily generate a nonzero ID, persist it, and return the same value on later calls. A separate folder must receive a different local ID. For a remote device, `GetIndexID` must return zero until `SetIndexID` stores an explicit value, after which it must be retrieved exactly.

## State and Persistence Behavior
The tests cover the distinction in `folderDB.GetIndexID`: local devices create state under `updateLock`, while non-local devices are read-only unless set explicitly. The folder wrapper creates folder DBs on `GetIndexID`, so even an ID lookup can create per-folder persistent state.

## Dependencies and Integration Points
The file depends on `protocol.NewIndexID`, `protocol.IndexID`, and the public `DB` methods that delegate to `folderdb_indexid.go` through `db_folderdb.go`.

## Risks and Test Signals
The test guards against accidental remote ID generation, local ID instability, and cross-folder reuse. It does not assert sequence preservation, which is covered in broader database tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_indexid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_kv.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_kv.go

## Purpose
This file implements the low-level SQLite-backed `db.KV` operations on `baseDB`, providing a simple `kv` table for metadata and typed wrappers.

## Important APIs and Control Flow
`GetKV` selects a byte value by key and wraps any SQL error. `PutKV` and `DeleteKV` acquire `baseDB.updateLock` before mutating `kv` with `INSERT OR REPLACE` or `DELETE`. `PrefixKV` returns an `iter.Seq[db.KeyValue]` plus error function. With an empty prefix it scans all key/value rows; otherwise it uses `prefixEnd(prefix)` to construct a lexicographic half-open range.

## State and Persistence Behavior
State lives in the common `kv` table present in both main and folder databases. Values are opaque byte slices; namespaces and typed encodings are layered by `internal/db/typed.go`. Iterators close SQL rows when iteration exits and defer row-scan errors to the returned error function.

## Dependencies and Integration Points
This file depends on `sqlx.Rows`, `db.KeyValue`, `baseDB.stmt`, `baseDB.updateLock`, `wrap`, and `prefixEnd` from `util.go`. It supports service metadata such as maintenance timestamps and folder metadata such as `folderID`.

## Risks and Test Signals
The prefix range relies on binary-collated string ordering and a non-empty prefix. `GetKV` intentionally surfaces `sql.ErrNoRows`; typed callers convert that to a missing-value result. Tests in `typed_test.go` indirectly exercise put/get/delete behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_local_test.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_local_test.go

## Purpose
This test file validates local file, blocklist, block index, and remote sequence behavior in the SQLite backend.

## Important APIs and Control Flow
`TestBlocks` checks block-hash lookup for local files. `TestBlocksDeleted` verifies that replacing a local file's blocks removes old block hits through file-row replacement and deferred block filtering. `TestDropBlockIndex`, `TestPopulateBlockIndex`, and `TestPopulateBlockIndexSkipsRemoteFiles` exercise optional block index maintenance. `TestSkipBlockIndexOnUpdate` proves file blocklists remain retrievable even when `db.WithSkipBlockIndex` avoids populating `blocks`. `TestRemoteSequence` asserts `RemoteSequences` tracks highest remote sequence per device.

## State and Persistence Behavior
The tests distinguish `blocklists` storage from `blocks` index rows. FileInfo retrieval reconstructs blocks from stored blocklists, while `AllLocalBlocksWithHash` uses the `blocks` table filtered through live local `files` rows. Remote files may store blocklists but are not inserted into the local block index.

## Dependencies and Integration Points
The tests use public `DB` methods, `itererr.Collect`, `protocol.DeviceID`, `protocol.LocalDeviceID`, and helper file/block generators from `db_test.go`. They directly exercise `folderdb_update.go` block insertion and `folderdb_local.go` block queries.

## Risks and Test Signals
Important risks are stale block hits after file replacement, rebuilding the block index from blocklists, and preserving file retrieval when indexing is skipped. The tests also confirm no-op behavior when dropping an empty or nonexistent block index.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_local_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_mtimes_test.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_mtimes_test.go

## Purpose
This test file covers folder-scoped modified-time pair persistence. Syncthing stores both on-disk and virtual mtimes for a file name.

## Important APIs and Control Flow
`TestMtimePairs` opens a temporary DB, writes a pair using `PutMtime(folder, name, ondisk, virtual)`, reads it through `GetMtime`, deletes it with `DeleteMtime`, and verifies reads return zero times after deletion.

## State and Persistence Behavior
The test exercises the `mtimes` table in the folder DB. Times are stored as Unix nanoseconds by `folderDB.PutMtime` and reconstructed with `time.Unix(0, nanos)`. `PutMtime` creates the folder DB if needed; `DeleteMtime` and `GetMtime` are tolerant of missing rows.

## Dependencies and Integration Points
The file uses the public `DB` wrapper methods in `db_folderdb.go`, which delegate to `folderdb_mtimes.go`, and Go's `time` package.

## Risks and Test Signals
The main risk is lossy or mismatched time serialization. The test truncates one value to second precision and uses a nanosecond offset for the other, giving coverage for both simple and subsecond values. It does not cover cross-platform path normalization.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_mtimes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_open.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_open.go

## Purpose
This file defines the top-level SQLite `DB` type and open/close lifecycle for Syncthing's SQLite database backend.

## Important APIs and Types
`DB` embeds `*baseDB` for the main database and tracks `pathBase`, `deleteRetention`, an RW-locked `folderDBs` map, and a `folderDBOpener`. `Option` and `WithDeleteRetention` configure deleted-file retention, clamping positive durations to at least 24 hours. `Open` configures WAL, optimization, incremental vacuum, and the main application ID, runs schema/migrations, cleans dropped folder files, and opens existing folder DBs. `OpenForMigration` uses unsafe high-throughput pragmas for bulk migration inserts. `Close` closes all folder DBs then the main DB. `initTmpDir` sets `SQLITE_TMPDIR` on non-Windows/non-Darwin systems when unset.

## State and Persistence Behavior
The main database lives at `main.db` under the supplied directory; folder databases live next to it and are tracked from the main `folders` table. Opening can mutate state by creating directories, initializing schemas, cleaning orphaned folder files, and migrating folder DBs.

## Dependencies and Integration Points
The file integrates with `openBase`, SQL schema assets, `db.DB`, `folderDB`, `slog`, and `build` OS flags. `Open` is the entry point for almost every test in this subset.

## Risks and Test Signals
Risks include accidentally running migration pragmas in normal operation, temp-dir setup after SQLite initialization, and partial folder DB open failure after the main DB opens. `db_test.go` includes path-special-character coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_open.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_open_cgo.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_open_cgo.go

## Purpose
This build-tagged file selects the cgo SQLite driver.

## Important APIs and Control Flow
Under `//go:build cgo`, it imports `github.com/mattn/go-sqlite3` for side-effect driver registration and sets `dbDriver = "sqlite3"`. `commonOptions` enables foreign keys, recursive triggers, synchronous mode, and immediate transaction locking using go-sqlite3 DSN parameters.

## State and Persistence Behavior
The file itself holds no runtime state, but its constants affect every `openBase` DSN in cgo builds. Foreign key and recursive trigger behavior are foundational to folder DB cascades and count triggers.

## Dependencies and Integration Points
It is consumed by `basedb.go` when opening `sqlx` connections. It is mutually exclusive with `db_open_nocgo.go`.

## Risks and Test Signals
The risk is DSN divergence between cgo and modernc builds. Any option mismatch can change transaction locking or trigger behavior. Database tests should be run under both build modes when touching these constants.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_open_cgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_open_nocgo.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_open_nocgo.go

## Purpose
This build-tagged file selects the pure-Go SQLite driver for non-cgo, non-wazero builds.

## Important APIs and Control Flow
Under `//go:build !cgo && !wazero`, it side-effect imports `modernc.org/sqlite`, sets `dbDriver = "sqlite"`, and uses `_pragma` DSN options for foreign keys, recursive triggers, synchronous mode, and immediate transaction locking. Its `init` function records the `modernc-sqlite` build tag through `build.AddTag`.

## State and Persistence Behavior
The constants shape all SQLite connections in this build mode. The driver choice also affects behavior around URI parsing, locking, and pragma support.

## Dependencies and Integration Points
It integrates with `basedb.go` connection setup and Syncthing build metadata. It is mutually exclusive with the cgo driver file.

## Risks and Test Signals
The main risk is semantic drift from the cgo driver. The test suite's path special-character, concurrency, foreign-key, trigger, and migration behaviors are relevant for both driver variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_open_nocgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_prepared.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_prepared.go

## Purpose
This file provides transaction-scoped prepared-statement caching for SQLite update paths.

## Important APIs and Control Flow
`txPreparedStmts` embeds `*sqlx.Tx` and keeps a `map[string]*sqlx.Stmt`. `Preparex` lazily creates the map, returns a cached statement for repeated identical SQL text, or prepares and stores a new statement with wrapped errors. `Commit` and `Rollback` close all cached statements before delegating to the underlying transaction.

## State and Persistence Behavior
The only state is in-memory and scoped to one transaction. It reduces repeated statement preparation in update and recalculation loops, especially `folderDB.Update`, `recalcGlobalForFile`, block insertion, and folder-wide recalculation.

## Dependencies and Integration Points
The file depends on `sqlx.Tx`, `sqlx.Stmt`, and `wrap`. `folderdb_update.go` is the primary caller.

## Risks and Test Signals
Because statement cache keys are raw query strings, whitespace or dynamic SQL changes create separate prepared statements. Closing errors are ignored. Correctness depends on always using `Commit` or `Rollback` on the wrapper, not directly on `Tx`, after statements have been cached.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_prepared.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_service.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_service.go

## Purpose
This file implements periodic SQLite maintenance and garbage collection for main and folder databases.

## Important APIs and Control Flow
`DB.Service` returns a `Service` with a maintenance interval, typed metadata namespace, and manual-start channel. `Serve` schedules the next run from `dbsvc/lastMaint`, accepts manual starts through `StartMaintenance`, runs `periodic`, reports manual completion, and stores the last maintenance time. `periodic` tidies the main DB under `updateLock`, then iterates folders. For each folder it compares current local sequence to `dbsvc/lastSuccessfulGCSeq`; unchanged folders skip garbage collection. Changed folders run old-deleted cleanup, unused name/version cleanup, blocklist/block cleanup, and tidy under the folder update lock.

## State and Persistence Behavior
Maintenance writes typed KV metadata, runs `ANALYZE`, `PRAGMA optimize`, incremental vacuum, journal size limits, and WAL truncate checkpoints. It deletes old deleted file rows based on `deleteRetention`, orphaned `file_names` and `file_versions`, and unreferenced `blocklists` and `blocks`.

## Dependencies and Integration Points
The service integrates with `db.Typed`, `forEachFolder`, `folderDB.GetDeviceSequence`, SQLite pragmas, and the folder schema's foreign-key relationships. `blobRange`, `randomBlobRanges`, `blobRanges`, and `intToBlob` partition blob keyspace for bounded GC work.

## Risks and Test Signals
Block GC temporarily disables foreign keys on one connection and manually deletes in randomized blob ranges with a five-minute per-table cap, so interruption can leave garbage for a later run but must not delete referenced rows. `db_service_test.go` checks range SQL generation; `db_test.go` validates blocklist GC after deleting a file.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_service_test.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_service_test.go

## Purpose
This test file validates deterministic blob-range SQL generation used by database maintenance garbage collection.

## Important APIs and Control Flow
`TestBlobRange` calls `blobRanges(7)`, formats each range with `blobRange.SQL("hash")`, and compares the output against expected open/closed half-open ranges over three-byte prefixes.

## State and Persistence Behavior
No database is opened. The test covers the SQL fragments used by `garbageCollectBlocklistsAndBlocksLocked` to partition deletes over `blocks.hash` or `blocklists.blocklist_hash`.

## Dependencies and Integration Points
The test uses `bytes.Buffer`, `fmt.Fprintln`, and `strings.TrimSpace`. It directly exercises `blobRanges`, `blobRange.SQL`, and indirectly `intToBlob` in `db_service.go`.

## Risks and Test Signals
The risk is malformed SQL ranges that overlap, leave gaps, or produce unbounded deletes. The test confirms the first range has only an upper bound, middle ranges have both bounds, and the last range has only a lower bound.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_stats.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_stats.go

## Purpose
This file exposes SQLite table-size statistics for the main database and child folder databases.

## Important APIs and Types
`DatabaseStatistics` is a JSON-oriented tree with database name, optional folder ID, table stats, total stats, and child databases. `TableStatistics` holds table/index name, total size, and unused bytes. `DB.Statistics` reads stats for the main `baseDB`, then calls `forEachFolder` and appends one child entry per folder. `baseDB.tableStats` queries the SQLite `dbstat` virtual table with `aggregate=true`, orders by name, and sums table sizes.

## State and Persistence Behavior
The code is read-only, but requires SQLite to have the `dbstat` virtual table available. Results reflect current database pages and unused page bytes after any maintenance/vacuum state.

## Dependencies and Integration Points
It depends on `baseDB.stmt`, `folderDB.tableStats`, and `forEachFolder`. The statistics shape is likely consumed by diagnostics or API layers.

## Risks and Test Signals
Missing `dbstat` support or driver differences can make `Statistics` fail. There are no direct tests in this subset, so changes should be validated against both drivers and with at least one opened folder DB.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_test.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_test.go

## Purpose
This is the broad integration test suite for the SQLite backend. It validates schema initialization, local/global/need APIs, folder and device drops, concurrency, block GC, path handling, error wrapping, and helper constructors.

## Important APIs and Control Flow
`TestBasics` builds a mixed local/remote folder and then subtests schema version, `GetDeviceFile`, `GetGlobalFile`, local/global/need iterators, counts, folder/device listing, sequences, prefix queries, and sequence-ordered local iteration. Other tests cover prefix range behavior with literal `*`, availability lists, dropping files/folders/devices, reset of device sequence on `DropAllFiles`, `DropFolderDevice`, concurrent updates, updating while iterating needed files, matching files by blocklist hash, blocklist garbage collection, large file block insertion, `wrap` formatting, vector ordering regressions, special path names, and block insertion after syncing a remote file locally.

## State and Persistence Behavior
Tests create temporary main and folder SQLite databases, insert `protocol.FileInfo` rows, rely on triggers for counts, and inspect internal tables for blocklist and block counts. They verify folder isolation, device isolation, sequence persistence, global flag recalculation, and deferred block garbage collection.

## Dependencies and Integration Points
The file depends on `internal/db`, `itererr`, `timeutil`, `build`, `config`, `protocol`, and helpers `genFile`, `genDir`, `genBlocks`, `genBlockHash`, `mustCollect`, and `fiNames`. It is the strongest test signal spanning `db_folderdb.go`, `folderdb_*`, `db_service.go`, and `util.go`.

## Risks and Test Signals
This file protects high-risk behavior: concurrent writes through `updateLock`, iterator/read interaction with updates, huge blocklists chunked below SQLite variable limits, URI-like filesystem paths, and historical vector-ordering bugs. The tests intentionally inspect internal tables in a few places, making them sensitive but useful for persistence regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_update.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/db_update.go

## Purpose
This file implements top-level database update and housekeeping methods that operate around folder database lifecycle rather than individual file rows.

## Important APIs and Control Flow
`DropFolder` locks the folder map and main update lock, deletes the folder row from the main `folders` table, closes and removes the open folder DB file plus WAL/SHM side files, and removes it from the cache. `ListFolders` reads folder IDs ordered by ID. `cleanDroppedFolders` compares on-disk `folder.*` files with `folders.database_name` values and removes orphaned files. `startFolderDatabases` opens all listed folders to apply migrations. `wrap` annotates errors with the caller function name and optional context strings.

## State and Persistence Behavior
`DropFolder` mutates both the main DB and filesystem. `cleanDroppedFolders` can delete files during startup if their basename does not match any live database name prefix. `startFolderDatabases` may migrate or initialize folder DBs as a side effect.

## Dependencies and Integration Points
The file uses `os`, `filepath`, `slices`, `strings`, logging helpers, and the folder DB cache initialized in `db_open.go`. `wrap` is used throughout the SQLite package.

## Risks and Test Signals
Filesystem deletion is the main risk, especially name-prefix matching and WAL/SHM cleanup. `db_test.go` covers `DropFolder` behavior and `TestErrorWrap`; startup cleanup has less direct coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/db_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/debug.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/debug.go

## Purpose
This file registers the SQLite database package with Syncthing's structured logging utilities.

## Important APIs and Control Flow
The package-level `init` calls `slogutil.RegisterPackage("SQLite database")`.

## State and Persistence Behavior
It has no database or filesystem persistence. Its only state effect is process-global logging package registration during package initialization.

## Dependencies and Integration Points
It depends on `internal/slogutil`. The debug and service files emit structured logs that benefit from this package registration.

## Risks and Test Signals
The risk is minimal. Removing or renaming the registration could affect log filtering or diagnostics, but not database correctness. There are no direct tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_counts.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_counts.go

## Purpose
This file computes aggregate file counts and byte totals from the per-folder SQLite database.

## Important APIs and Control Flow
`countsRow` mirrors rows from the materialized `counts` table. `CountLocal` selects counts for a specific device excluding ignored rows. `CountNeed` dispatches to local or remote need-count SQL. `CountGlobal` selects rows marked `FlagLocalGlobal` and not invalid. `CountReceiveOnlyChanged` selects receive-only rows. `needSizeLocal` sums rows with `FlagLocalNeeded`. `needSizeRemote` mirrors remote need-list semantics using two grouped queries: valid non-deleted globals absent at the remote's same version, and valid deleted globals where the remote still has a valid non-deleted row. `summarizeCounts` converts rows into `db.Counts`.

## State and Persistence Behavior
The code is read-only and depends on count triggers in the folder schema staying synchronized with `files`. Deleted rows increment `Counts.Deleted`; files, directories, and symlinks increment separate counters and bytes.

## Dependencies and Integration Points
It depends on `db.Counts`, `protocol.FileInfoType`, `protocol.FlagLocal`, template constants from `baseDB.tplInput`, and SQL written by `folderdb_update.go`.

## Risks and Test Signals
The risk is divergence between count SQL and iterator SQL, especially remote deleted needs. `db_global_test.go` and `db_test.go` compare counts with need/global iterators across ignored, invalid, deleted, symlink, and directory cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_counts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_global.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_global.go

## Purpose
This file implements global-file and need-list queries inside a single folder database.

## Important APIs and Control Flow
`GetGlobalFile` normalizes the name, selects the row marked `FlagLocalGlobal`, joins fileinfo and optional blocklist bytes, and reconstructs a `protocol.FileInfo`. `GetGlobalAvailability` finds remote devices holding the same version as the current global row. `AllGlobalFiles` and `AllGlobalFilesPrefix` stream global metadata ordered by name, using `prefixEnd` for prefix ranges. `AllNeededGlobalFiles` converts `config.PullOrder` to SQL ordering and appends limit/offset, then delegates to local or remote need queries. Local need selects rows with `FlagLocalNeeded` and not ignored. Remote need selects valid non-deleted global rows not present on the remote at the same version plus valid deleted globals when the remote has any valid non-deleted row for that name.

## State and Persistence Behavior
The file is read-only but depends on `folderdb_update.go` maintaining global and need flags. FileInfo rows are reconstructed from protobuf payloads plus optional external blocklists.

## Dependencies and Integration Points
It integrates with `config.PullOrder`, `protocol.DeviceID`, `db.FileMetadata`, `itererr.Map`, `indirectFI`, and filename normalization/native conversion.

## Risks and Test Signals
Dynamic `ORDER BY`, `LIMIT`, and `OFFSET` strings are built from controlled enum/int inputs, not user SQL. The main risk is remote need semantics around deleted or invalid rows. `db_global_test.go` is the primary coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_global.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_indexid.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_indexid.go

## Purpose
This file manages per-device index IDs and per-device sequence tracking in a folder database.

## Important APIs and Control Flow
`GetIndexID` first tries a read-only join over `indexids` and `devices`. If absent for a remote device, it returns zero. If absent for the local device, it takes `updateLock`, rechecks, generates `protocol.NewIndexID`, and inserts it with the current max local file sequence. `SetIndexID` ensures a device row and stores a supplied ID with sequence zero. `DropAllIndexIDs` clears all IDs. `GetDeviceSequence` returns the stored sequence or zero for missing/null values. `RemoteSequences` streams non-local device sequence rows and parses device IDs. `indexIDFromHex` and `indexIDToHex` convert protocol IDs to/from database strings.

## State and Persistence Behavior
State lives in the `indexids` table keyed by `device_idx`; `files` inserts update sequence through schema behavior. The local lazy insert preserves current local max sequence to avoid resetting an existing file stream.

## Dependencies and Integration Points
The file depends on `protocol.IndexID`, `protocol.DeviceID`, `iterStructs`, `itererr.Zip`, and `deviceIdxLocked`.

## Risks and Test Signals
Hex conversion and local lazy creation are critical. Remote IDs must not be created accidentally. `db_indexid_test.go`, `db_local_test.go`, and `db_test.go` cover ID persistence and sequences.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_indexid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_local.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_local.go

## Purpose
This file implements folder-local file retrieval, local iterators, block lookup, device listing, and human-readable debug output.

## Important APIs and Control Flow
`GetDeviceFile` normalizes a filename, joins `fileinfos`, `files`, `blocklists`, `devices`, and `file_names`, and reconstructs a `protocol.FileInfo`. `AllLocalFiles`, `AllLocalFilesBySequence`, and `AllLocalFilesWithPrefix` stream fileinfos for one device, optionally sequence-ordered or prefix-bounded. `AllLocalFilesWithBlocksHash` returns metadata for local files with a matching blocklist hash. `AllLocalBlocksWithHash` joins through live local `files` rows to filter out garbage-collected/deferred block rows. `ListDevicesForFolder` reports remote devices with positive counts. `DebugCounts` and `DebugFilePattern` print tabular diagnostic data with shortened device IDs, type names, versions, and blocklist hashes.

## State and Persistence Behavior
The code is mostly read-only, relying on stored protobuf fileinfos and blocklists. Debug methods expose internal persisted state but do not mutate it.

## Dependencies and Integration Points
It uses `db.FileMetadata`, `db.BlockMapEntry`, `indirectFI`, `dbVector`, filename normalization/native conversion, `tabwriter`, and `protocol.DeviceIDFromString`.

## Risks and Test Signals
Iterator error handling and row closing are important for long scans. Block lookup must avoid stale rows after file replacement. `db_local_test.go` and `db_test.go` provide coverage for file, prefix, sequence, block, and device-list behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_mtimes.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_mtimes.go

## Purpose
This file persists per-file modified-time mapping pairs for a folder database.

## Important APIs and Control Flow
`GetMtime` selects `ondisk` and `virtual` nanosecond values by name and returns zero times on any error or missing row. `PutMtime` locks updates and `INSERT OR REPLACE`s the pair. `DeleteMtime` locks updates and deletes by name.

## State and Persistence Behavior
State lives in the folder DB `mtimes` table. Times are stored as `time.Time.UnixNano()` values and reconstructed with `time.Unix(0, value)`. Missing data is deliberately represented as zero times without an error path in `GetMtime`.

## Dependencies and Integration Points
The public wrappers in `db_folderdb.go` create or fetch folder DBs and delegate here. The scanner and filesystem layers likely use this to reconcile timestamp precision or virtual mtimes.

## Risks and Test Signals
Silent zero-time fallback can hide SQL errors, but keeps the API simple. `db_mtimes_test.go` covers write/read/delete round trips.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_mtimes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_open.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_open.go

## Purpose
This file defines the per-folder database type and opens folder-specific SQLite databases.

## Important APIs and Types
`folderDB` embeds `*baseDB` and stores `folderID`, `localDeviceIdx`, and `deleteRetention`. `openFolderDB` configures normal folder pragmas, common and folder schemas/migrations, opens the base DB, writes `folderID` to KV, creates/touches the local device row, and stores `LocalDeviceIdx` in template input. `openFolderDBForMigration` uses unsafe bulk-insert pragmas, one connection, and no migrations. `deviceIdxLocked` upserts a device string into `devices` and returns its numeric `idx`.

## State and Persistence Behavior
Opening creates or migrates the folder database file, initializes common tables, ensures the local device row exists, and records folder identity in KV. Device indexes become stable internal foreign keys for files, counts, and index IDs.

## Dependencies and Integration Points
It integrates with `openBase`, schema assets, application IDs, `protocol.LocalDeviceID`, and `folderDB` methods that use `{{.LocalDeviceIdx}}` in SQL templates.

## Risks and Test Signals
Device index stability matters because lower device indexes influence conflict tie-breaking. Bulk migration mode must not be used for normal operation. Most tests cover this indirectly through every folder operation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_open.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_update.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/folderdb_update.go

## Purpose
This file contains the core write path for per-folder file index state, including file insertion/replacement, blocklist persistence, block index maintenance, global/need recalculation, drop operations, and WAL checkpoint pacing.

## Important APIs and Control Flow
`Update` locks the folder, ensures a device index, starts a transaction with cached prepared statements, normalizes names, computes block hashes, applies synthetic directory size, records remote sequence values, deduplicates file names and version strings, inserts/replaces file rows, stores external blocklists, optionally inserts local block rows, marshals `FileInfo` protobufs, and calls `recalcGlobalForFile` for each changed name. It rejects duplicate remote sequence numbers in one update batch. Drop methods remove devices or file rows and recalculate affected global state. `DropBlockIndex` deletes all block rows and vacuums; `PopulateBlockIndex` rebuilds from local file blocklists. `insertBlocksLocked` chunks inserts in batches of 1000 to avoid SQLite variable limits.

## State and Persistence Behavior
Persistent state spans `devices`, `file_names`, `file_versions`, `files`, `fileinfos`, `blocklists`, `blocks`, `indexids`, counts triggers, and WAL checkpoints. `recalcGlobalForFile` sorts all rows for a name by vector, invalid state, modified time, and device index, marks exactly one global row, and sets local need unless local already has the global/equivalent version or the global is invalid.

## Dependencies and Integration Points
The file depends on `protocol.FileInfo`, `db.UpdateOptions`, `dbproto.BlockList`, protobuf marshaling, `txPreparedStmts`, `dbVector`, `iterStructs`, and SQL template constants.

## Risks and Test Signals
This is the highest-risk file in the subset. Regressions can corrupt global state, need state, block lookup, sequences, or conflict resolution. Tests in `db_test.go`, `db_global_test.go`, and `db_local_test.go` cover concurrency, block-index rebuild, deleted conflict wins, large files, skipped block indexing, and drops.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/folderdb_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/util.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/util.go

## Purpose
This file provides shared SQLite utility types for row iteration, version-vector SQL conversion, indirect FileInfo reconstruction, and prefix range construction.

## Important APIs and Control Flow
`iterStructs[T]` converts `sqlx.Rows` into a Go iterator, `StructScan`s each row into `T`, optionally calls `cleanup()`, closes rows on exit, and exposes scan/row errors through a returned function. `dbVector` implements `driver.Valuer` and `sql.Scanner` for `protocol.Vector` strings and sorts counters after scanning to repair older serialization ordering. `indirectFI.FileInfo` unmarshals a stored BEP `FileInfo`, optionally unmarshals an external `dbproto.BlockList` into its `Blocks`, converts the name to native format, and returns a `protocol.FileInfo`. `prefixEnd` increments the final non-0xff byte to make a lexicographic exclusive upper bound.

## State and Persistence Behavior
The file itself is stateless, but defines how version vectors and FileInfo payloads are serialized/deserialized from persisted database columns.

## Dependencies and Integration Points
It depends on `sqlx`, `database/sql/driver`, generated `bep` and `dbproto`, `proto`, `osutil`, and `protocol`. It is used by nearly all folder query files.

## Risks and Test Signals
`prefixEnd` panics on empty prefixes and does not handle all-0xff overflow specially. `dbVector.Scan` expects strings only. `util_test.go` covers vector round trip; prefix behavior is heavily exercised through database prefix tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/util_test.go -->
# sources/sync-backup/syncthing/internal/db/sqlite/util_test.go

## Purpose
This file tests `dbVector`, the SQLite conversion wrapper for `protocol.Vector`.

## Important APIs and Control Flow
`TestDbvector` creates a vector with two counters, wraps it as `dbVector`, calls `Value`, scans that value into another `dbVector`, and asserts the resulting vector equals the original.

## State and Persistence Behavior
The test does not open a database. It validates the serialization format that is stored in the `file_versions.version` column and later scanned back during global conflict resolution.

## Dependencies and Integration Points
It depends on `protocol.Vector`, `protocol.Counter`, and the `dbVector.Value`/`Scan` methods in `util.go`.

## Risks and Test Signals
This test catches basic scan/value breakage but not the older unsorted-counter repair path except indirectly if equality requires canonical ordering. `db_test.go` adds regression coverage for strange deleted-global behavior tied to vector ordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/sqlite/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/typed.go -->
# sources/sync-backup/syncthing/internal/db/typed.go

## Purpose
This file implements a typed, namespaced wrapper over a byte-oriented `db.KV` store.

## Important APIs and Control Flow
`Typed` stores a `KV` and namespace prefix. `NewMiscDB` uses the `misc` namespace; `NewTyped` accepts any prefix. `PutInt64` stores big-endian uint64 bytes; `Int64` reads and converts them back. `PutTime` and `Time` use `time.Time` binary marshaling. `PutString`/`String`, `PutBytes`/`Bytes`, and `PutBool`/`Bool` store simple byte encodings. `Delete` removes a prefixed key. `filterNotFound` converts `sql.ErrNoRows` into nil so missing keys return `ok=false` without an error.

## State and Persistence Behavior
All values are persisted in the underlying `KV` using keys formatted as `prefix + "/" + key`. Existing values are overwritten regardless of prior type. `Bool` stores true as `0x0` and false as `0x1`, which is unusual but internally consistent.

## Dependencies and Integration Points
It depends on the `KV` interface, `database/sql`, `encoding/binary`, and `time`. SQLite `baseDB` implements the needed KV methods. The SQLite maintenance service stores timestamps and sequence markers through this wrapper.

## Risks and Test Signals
There is no length validation before reading fixed-width int or bool values, so corrupt or wrong-type values can panic. `typed_test.go` covers namespace isolation and several value types but not bool or bytes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/typed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/typed_test.go -->
# sources/sync-backup/syncthing/internal/db/typed_test.go

## Purpose
This test file validates the typed KV wrapper against the SQLite KV backend.

## Important APIs and Control Flow
`TestNamespacedInt` opens a temporary SQLite DB, constructs two `Typed` wrappers with prefixes `foo` and `bar`, and runs parallel subtests. The `Int` subtest verifies missing-key behavior, put/read, namespace isolation, and delete. The `Time` subtest verifies missing zero time and binary time round trip. The `String` subtest verifies missing empty string and string round trip.

## State and Persistence Behavior
The test writes to the SQLite common `kv` table through prefixed keys. It proves deleting a typed key removes only that prefixed key and that namespaces do not collide.

## Dependencies and Integration Points
The test imports `internal/db` and `internal/db/sqlite`, so it exercises the generic wrapper and the concrete SQLite `KV` implementation together.

## Risks and Test Signals
Parallel subtests share one database and different keys, so they provide light concurrency coverage. Missing direct coverage for bytes, bool, corrupt values, and `NewMiscDB` remains.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/db/typed_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/apiproto/tokenset.pb.go -->
# sources/sync-backup/syncthing/internal/gen/apiproto/tokenset.pb.go

## Purpose
This generated protobuf file defines the API-facing `TokenSet` message.

## Important APIs and Types
`TokenSet` is a generated message with one field, `Tokens map[string]int64`, documented as token string to expiry time in epoch nanoseconds. Standard generated methods include `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and `GetTokens`. The file also exposes `File_apiproto_tokenset_proto`, raw descriptor data, message info, Go type metadata, dependency indexes, and an init-time `protoimpl.TypeBuilder`.

## State and Persistence Behavior
Runtime state is message data plus protobuf reflection descriptor caches. The map values encode expiry timestamps as int64 nanoseconds; interpretation and validation are performed by callers, not this generated file.

## Dependencies and Integration Points
It depends on `google.golang.org/protobuf/reflect/protoreflect`, `runtime/protoimpl`, `reflect`, and `sync`. It is generated from `apiproto/tokenset.proto` and should not be hand-edited.

## Risks and Test Signals
Generated code risk is schema drift: callers depend on field number 1 and map key/value encoding remaining stable. There are no local tests in this subset; validation should be through protobuf regeneration and API token tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/apiproto/tokenset.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/bep/bep.pb.go -->
# sources/sync-backup/syncthing/internal/gen/bep/bep.pb.go

## Purpose
This generated protobuf file defines Syncthing's Block Exchange Protocol message and enum types used on the wire and in database serialization.

## Important APIs and Types
Enums include `MessageType`, `MessageCompression`, `Compression`, `FolderType`, `FolderStopReason`, `FileInfoType`, `ErrorCode`, and `FileDownloadProgressUpdateType`. Message structs include handshake/control messages (`Hello`, `Header`, `Ping`, `Close`), cluster configuration (`ClusterConfig`, `Folder`, `Device`), index exchange (`Index`, `IndexUpdate`, `FileInfo`, `BlockInfo`, `Vector`, `Counter`), platform metadata (`PlatformData`, `UnixData`, `WindowsData`, `XattrData`, `Xattr`), block transfer (`Request`, `Response`), and progress (`DownloadProgress`, `FileDownloadProgressUpdate`). Each generated type has standard protobuf reset/string/reflection/descriptor methods and nil-safe getters.

## State and Persistence Behavior
This file does not persist data directly, but its `FileInfo`, `BlockInfo`, and `Vector` wire shapes are persisted by the SQLite database as `fileinfos.fiprotobuf`, external blocklist protobufs, and version strings/conversions. Some fields are host-local implementation details (`local_flags`, `version_hash`, `encryption_trailer_size`) and are not intended for wire exchange despite being present in the generated struct.

## Dependencies and Integration Points
It depends on protobuf runtime/reflection packages. The SQLite code uses `bep.FileInfo` in `indirectFI.FileInfo` and `protocol.FileInfo.ToWire`/`FromDB`; protocol networking layers use the full message set.

## Risks and Test Signals
The file is generated and should not be manually edited. Changing proto field numbers, defaults, or local-only fields can break network compatibility or database decoding. SQLite tests indirectly cover `FileInfo` and `BlockInfo` persistence through update/retrieval and blocklist behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/internal/gen/bep/bep.pb.go -->
