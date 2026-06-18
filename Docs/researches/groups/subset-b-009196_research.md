# subset-b-009196 Research

Grouped research for the requested Syncthing ignore, locations, and model files. Each section is source-tree-aligned and wrapped for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignore_test.go -->
# sources/sync-backup/syncthing/lib/ignore/ignore_test.go

## Purpose
Exercises the ignore matcher contract: pattern parsing, include expansion, negation, deletable flags, case handling, cache reload behavior, hash stability, line preservation, path-root semantics, skipped-directory decisions, special characters, international wildcards, and escape-directive parsing.

## Important APIs, Types, and Functions
`newTestFS` builds a fake filesystem with `.stignore` and included files. Tests drive `New`, `Load`, `Parse`, `Match`, `Patterns`, `Lines`, `Hash`, `WriteIgnores`, `parseLine`, and `allowsSkippingIgnoredDirs`. `escapeTest`, `backslashTests`, `pipeTests`, and override test tables encode platform-sensitive escaping semantics. Benchmarks cover cached and uncached `Match`.

## Control Flow
Most tests create a fake filesystem, load or parse ignore text, then assert `ignoreresult.R` flags for representative paths. Include tests validate recursive include expansion and missing include errors. Cache tests mutate ignore files and mtimes, reload matchers, and check whether cached match results survive or are invalidated. Escape tests generate pattern variants with `#escape=` before, after, duplicated, invalid, and included lines, then route through `testEscape`.

## State and Persistence Behavior
The tests persist ignore files in the fake filesystem, including file content and modification timestamps, to validate cache keys and reload invalidation. Matcher state inspected includes parsed patterns, original lines, cached match count, and hash values. No production state is written outside fake filesystems.

## Dependencies and Integration Points
Depends on Syncthing `fs`, `osutil`, `rand`, `build`, and `ignoreresult`. The behaviors tested are consumed by scanner and folder code that must know whether paths are ignored, deletable, case-folded, or safe to skip while walking directories.

## Risks
Coverage is broad but primarily table-driven unit behavior; it relies on fake filesystem timestamp manipulation to model cache invalidation. Several paths are platform-gated, so Windows and Darwin behaviors need platform CI. `TestBadPatterns` is skipped, signaling known incomplete validation coverage for malformed glob/include parsing.

## Test Signals
Signals include regression tests for historical issues 3164, 3174, 3639, 3674, 4680, 4689, 4901, and 5009; benchmark coverage for cache performance; and extensive escape directive matrices that protect compatibility across default backslash and pipe escape modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult.go -->
# sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult.go

## Purpose
Defines the compact ignore-match result type used by the ignore package without creating import cycles. It encodes whether a path is ignored, deletable, matched case-insensitively, or allows directory traversal to be skipped.

## Important APIs, Types, and Functions
`type R uint8` stores bit flags. Public constants are `NotIgnored`, platform-defined `Ignored`, `IgnoredDeletable`, and `IgnoreAndSkip`. Methods are `IsIgnored`, `IsDeletable`, `IsCaseFolded`, `CanSkipDir`, `ToggleIgnored`, `WithDeletable`, `WithFoldCase`, `WithSkipDir`, and `String`.

## Control Flow
All methods are direct bit tests or bit mutations. `IsDeletable` and `CanSkipDir` intentionally require the ignored bit in addition to their own flag bits, so orphaned modifier bits do not produce operational behavior.

## State and Persistence Behavior
No mutable or persistent state exists. Values are copied by value and used as return values from matcher calls.

## Dependencies and Integration Points
This package is imported by ignore matching code and downstream consumers such as folder scanning and deletion logic. Platform files define the meaning of the `Ignored` constant to apply default case folding on case-insensitive platforms.

## Risks
The type is intentionally tiny, so misuse risk comes from callers setting modifier bits without `ignoreBit`. The helper methods guard reads, but direct bit comparisons outside this package could bypass that contract. `String` is diagnostic only and should not be parsed as a stable wire format.

## Test Signals
`ignoreresult_test.go` verifies `CanSkipDir` requires an ignored result. Wider flag behavior is indirectly exercised by ignore matcher tests for deletable, case-insensitive, and skip-directory behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_foldcase.go -->
# sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_foldcase.go

## Purpose
Supplies the platform-specific default ignored result for case-insensitive filesystems and operating systems.

## Important APIs, Types, and Functions
Defines `const Ignored = ignoreBit | foldCaseBit` behind the `windows || darwin || ios` build tag.

## Control Flow
There is no runtime control flow. The Go build selects this file on Windows, Darwin, and iOS, causing plain ignored matches to also report `IsCaseFolded`.

## State and Persistence Behavior
No state or persistence. The constant affects matcher return values at compile time.

## Dependencies and Integration Points
Used by `ignoreresult.go` constants such as `IgnoredDeletable` and `IgnoreAndSkip`, and by ignore matcher code that starts from `ignoreresult.Ignored`.

## Risks
The correctness boundary is build-tag selection. If a platform has case-sensitive matching despite these OS defaults, callers may get folded behavior unless they use explicit ignore flags or platform-specific logic.

## Test Signals
`ignore_test.go` includes platform-gated case-insensitivity tests that should pass on Windows and Darwin builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_foldcase.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_nofoldcase.go -->
# sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_nofoldcase.go

## Purpose
Supplies the platform-specific default ignored result for platforms where ignore matching should not automatically be case-folded.

## Important APIs, Types, and Functions
Defines `const Ignored = ignoreBit` behind the `!windows && !darwin && !ios` build tag.

## Control Flow
No runtime control flow. The Go build selects this file on non-Windows, non-Darwin, non-iOS platforms.

## State and Persistence Behavior
No state or persistence. The constant only influences compiled matcher behavior.

## Dependencies and Integration Points
Complements `ignoreresult_foldcase.go` and feeds constants in `ignoreresult.go`. Ignore matcher tests on Unix-like case-sensitive builds expect uppercase and lowercase names to remain distinct unless patterns request `(?i)`.

## Risks
The default assumes OS-level case sensitivity. Mounted case-insensitive filesystems on Unix-like platforms may still need explicit case-insensitive ignore patterns.

## Test Signals
`TestCaseSensitivity` in `ignore_test.go` checks that non-Windows/non-Darwin builds do not match different case by default.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_nofoldcase.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_test.go -->
# sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_test.go

## Purpose
Verifies the semantic contract of the skip-directory result flag.

## Important APIs, Types, and Functions
`TestFlagCanSkipDir` constructs `ignoreresult.R` values including zero, `NotIgnored`, `NotIgnored.WithSkipDir`, `Ignored`, and `IgnoreAndSkip`.

## Control Flow
The test iterates table rows and compares `CanSkipDir()` with the expected boolean, reporting mismatches with the result string.

## State and Persistence Behavior
No state, persistence, filesystem, or network behavior.

## Dependencies and Integration Points
Imports `github.com/syncthing/syncthing/lib/ignore/ignoreresult` as an external test package, which validates the public API as callers see it.

## Risks
The test covers one important invariant but does not directly test `IsDeletable`, `IsCaseFolded`, mutator methods, or `String`; those are left to indirect ignore matcher tests.

## Test Signals
Protects callers that use `Match(...).CanSkipDir()` as a single check instead of separately checking `IsIgnored`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/locations/locations.go -->
# sources/sync-backup/syncthing/lib/locations/locations.go

## Purpose
Centralizes Syncthing runtime path selection for config, certificates, database, logs, GUI assets, default folder, and lock files. It also computes platform defaults and expands timestamped log paths.

## Important APIs, Types, and Functions
`LocationEnum` and `BaseDirEnum` enumerate keys. Public functions are `Set`, `SetBaseDir`, `Get`, `GetBaseDir`, `ListExpandedPaths`, `PrettyPaths`, and `GetTimestamped`. Internal helpers include `expandLocations`, platform default functions, `unixConfigDir`, `unixDataDir`, `userHomeDir`, `getTimestampedAt`, and `fileExists`.

## Control Flow
`init` resolves user home, config base, and data base, populates `baseDirs`, then expands templates into `locations`. `Set` validates location keys and stores an absolute cleaned override, except `"-"`. `SetBaseDir` validates base keys, absolutizes the path, updates `baseDirs`, and recomputes all template-derived locations. Unix default selection prefers existing legacy config or database paths, then absolute `XDG_STATE_HOME`, then `~/.local/state/syncthing`.

## State and Persistence Behavior
The package keeps process-global mutable maps `baseDirs` and `locations`. It does not write files, but it probes existence with `os.Lstat` and reads environment variables. Timestamp expansion is computed on demand without mutating stored templates.

## Dependencies and Integration Points
Uses `build` platform flags, `fs.ExpandTilde`, `filepath`, `os`, and `time`. Model health checks use `locations.Get(locations.Database)` to verify database disk free space; command-line and startup code can override paths through this package.

## Risks
Global mutable maps are not guarded by locks, so path overrides are expected during startup, not concurrent runtime mutation. Environment handling intentionally preserves historical behavior for relative XDG config/data variables, which can surprise strict XDG consumers. `init` panics on expansion failure.

## Test Signals
`locations_test.go` validates Unix config/data fallback order and timestamp substitution. Platform-specific Windows/Darwin defaults are not exercised in this listed test file.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/locations/locations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/locations/locations_test.go -->
# sources/sync-backup/syncthing/lib/locations/locations_test.go

## Purpose
Tests Unix location defaulting and timestamped path formatting.

## Important APIs, Types, and Functions
`TestUnixConfigDir`, `TestUnixDataDir`, and `TestGetTimestamped` call internal helpers `unixConfigDir`, `unixDataDir`, and `getTimestampedAt`.

## Control Flow
The Unix tests define table rows with user home, XDG variables, simulated existing files, and expected directories. Each row injects a `fileExists` closure backed by `slices.Contains`. The timestamp test fixes a UTC time and checks the basename of `PanicLog`.

## State and Persistence Behavior
No filesystem writes occur. Tests simulate existence entirely in memory. `TestGetTimestamped` reads the package global `locations` map initialized by `init`.

## Dependencies and Integration Points
Build-tagged `!windows`, so these tests validate Unix-like behavior only. They protect upgrade paths from legacy `.config/syncthing` and old LevelDB database locations to current state directory rules.

## Risks
The tests do not cover relative XDG state rejection directly for every branch, Windows/Darwin paths, `Set`, `SetBaseDir`, or concurrent global mutation. They also assume initialized templates include `%{timestamp}` for `PanicLog`.

## Test Signals
Strong signal on migration-sensitive precedence: existing config wins over new state defaults, existing database can keep data colocated with config or legacy XDG data, and timestamp formatting uses `YYYYMMDD-HHMMSS`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/locations/locations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/blockpullreorderer.go -->
# sources/sync-backup/syncthing/lib/model/blockpullreorderer.go

## Purpose
Chooses the order in which file blocks are requested during pulling, supporting in-order, random, and standard multi-device distribution strategies.

## Important APIs, Types, and Functions
`blockPullReorderer` exposes `Reorder`. `newBlockPullReorderer` selects by `config.BlockPullOrder`. Implementations are `inOrderBlockPullReorderer`, `randomOrderBlockPullReorderer`, and `standardBlockPullReorderer`. `chunk` splits block slices into approximately equal contiguous parts.

## Control Flow
In-order returns the original slice. Random shuffles the input slice in place. Standard builds a sorted list of all device IDs plus the local ID, records the local device index, splits blocks into one chunk per device, emits the local chunk first when present, then shuffles and appends remaining chunks.

## State and Persistence Behavior
No persistence. Standard reorderer stores local index, device count, and a shuffle function for tests. Random and standard can mutate ordering of provided block slices or returned slices.

## Dependencies and Integration Points
Used by `sendReceiveFolder.handleFile` before copy/pull scheduling. Depends on `config`, `protocol.DeviceID`, `slices`, and Syncthing `rand`.

## Risks
Ordering is a performance and distribution concern, not correctness; however in-place shuffling can surprise callers if they reuse the original slice. Standard mode panics if the local ID is not found after construction, which should be impossible because it appends that ID itself.

## Test Signals
`blockpullreorderer_test.go` verifies chunk boundaries, in-order identity, and deterministic standard ordering with shuffle disabled.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/blockpullreorderer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/blockpullreorderer_test.go -->
# sources/sync-backup/syncthing/lib/model/blockpullreorderer_test.go

## Purpose
Validates block chunking and reorderer behavior used by the pull pipeline.

## Important APIs, Types, and Functions
Tests target `chunk`, `inOrderBlockPullReorderer.Reorder`, and `standardBlockPullReorderer.Reorder`. `someBlocks` is a small fixture of `protocol.BlockInfo` offsets.

## Control Flow
`Test_chunk` table-checks partition counts including more parts than blocks and nil input. `Test_inOrderBlockPullReorderer_Reorder` checks identity. `Test_standardBlockPullReorderer_Reorder` sorts known device IDs, disables shuffling, and checks the local chunk is moved to the front for different local device positions.

## State and Persistence Behavior
No persistent state. The standard reorderer test mutates the reorderer's `shuffle` field to a no-op for deterministic assertions.

## Dependencies and Integration Points
Uses package-level test device IDs from the model test suite and `protocol.BlockInfo`. Protects `folder_sendrecv.go` block scheduling behavior.

## Risks
Random order behavior is not statistically tested. The tests cover offset ordering, not real block hashes or copy/download side effects.

## Test Signals
Regression signal for even chunking, nil/empty inputs, and stable standard ordering when there are fewer blocks than devices or multiple blocks per selected chunk.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/blockpullreorderer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/debug.go -->
# sources/sync-backup/syncthing/lib/model/debug.go

## Purpose
Defines the package logger adapter used by model code.

## Important APIs, Types, and Functions
Declares package variable `l = slogutil.NewAdapter("The root hub")`.

## Control Flow
No runtime control flow beyond package initialization.

## State and Persistence Behavior
Holds a package-global logging adapter. No persistence or domain state.

## Dependencies and Integration Points
Depends on `internal/slogutil`. Older model code and tests use `l.Debugf`, `l.Debugln`, and related adapter methods alongside newer structured `slog` loggers.

## Risks
Global logger naming is broad and shared across the package, so log attribution relies on surrounding fields or messages. It is not test-isolated.

## Test Signals
No direct tests; usage is indirectly compiled throughout the model package.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/deviceactivity.go -->
# sources/sync-backup/syncthing/lib/model/deviceactivity.go

## Purpose
Tracks in-flight block requests per remote device and selects the least busy source for new pulls.

## Important APIs, Types, and Functions
`deviceActivity` owns a `map[protocol.DeviceID]int` protected by a mutex. `newDeviceActivity` constructs it. `leastBusy`, `using`, and `done` read or adjust per-device counters.

## Control Flow
`leastBusy` scans an availability slice and returns the index with the lowest current usage count, defaulting to `-1` for empty input. `using` increments the selected device count before a request, and `done` decrements it afterward.

## State and Persistence Behavior
State is in-memory only and process-global in `folder_sendrecv.go` as `activity`. Counters are not persisted and can go negative if `done` is called without matching `using`.

## Dependencies and Integration Points
Depends on `protocol.DeviceID` and the model `Availability` type. `sendReceiveFolder.pullBlock` uses it to spread block requests across available peers.

## Risks
Tie-breaking is order-dependent and favors the first equally idle candidate. The code does not delete zero counters or guard underflow. The global instance means activity spans all folders, which is intentional for balancing but can cross-couple unrelated syncs.

## Test Signals
`deviceactivity_test.go` checks least-busy rotation through increments and decrements across three devices.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/deviceactivity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/deviceactivity_test.go -->
# sources/sync-backup/syncthing/lib/model/deviceactivity_test.go

## Purpose
Tests least-busy selection and counter updates for device request activity.

## Important APIs, Types, and Functions
`TestDeviceActivity` constructs three `Availability` values and exercises `newDeviceActivity`, `leastBusy`, `using`, and `done`.

## Control Flow
The test verifies initial first-device preference, increments selected devices to move preference to the next least-used device, then decrements devices and checks preference changes back.

## State and Persistence Behavior
Only in-memory counters in a fresh `deviceActivity` are mutated. No database, filesystem, or network state.

## Dependencies and Integration Points
Uses `protocol.DeviceID` and model `Availability`, mirroring the puller’s device candidate list.

## Risks
The test is single-threaded, so it does not exercise mutex behavior under concurrent pulls. It also does not cover empty availability returning `-1` or underflow.

## Test Signals
Provides deterministic behavioral coverage for tie-breaking and counter-based balancing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/deviceactivity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/devicedownloadstate.go -->
# sources/sync-backup/syncthing/lib/model/devicedownloadstate.go

## Purpose
Tracks which blocks a remote device has downloaded into temporary files, enabling other devices to request already-downloaded temporary blocks and display remote progress.

## Important APIs, Types, and Functions
`deviceFolderFileDownloadState` stores block indexes, version, and block size per file. `deviceFolderDownloadState` manages files for one folder with `Has`, `Update`, `BytesDownloaded`, and `GetBlockCounts`. `deviceDownloadState` wraps all folders for a device with folder-scoped `Update`, `Has`, `GetBlockCounts`, `BytesDownloaded`, and `newDeviceDownloadState`.

## Control Flow
Updates are append or forget events. Append creates file state, replaces it if the version changes, or appends block indexes for the same version. Forget deletes only when the version matches. Queries first check nil receiver and folder/file existence, then require exact version equality.

## State and Persistence Behavior
All state is in-memory and guarded by RW mutexes. It is not persisted; it mirrors live `DownloadProgress` protocol messages. `BytesDownloaded` estimates using the advertised block size, falling back to `protocol.MinBlockSize`.

## Dependencies and Integration Points
Depends on `protocol.FileDownloadProgressUpdate` and `protocol.Vector`. Integrated with connection download progress handling and block availability from temporary files.

## Risks
Repeated append updates can duplicate block indexes, inflating counts and bytes if senders repeat data. Folder creation in `Update` uses a read-then-write pattern that could race if two goroutines create the same folder simultaneously, although subsequent map assignment is locked. Returned maps are snapshots.

## Test Signals
`devicedownloadstate_test.go` verifies append, replacement by version, forget semantics, and multi-file behavior. Byte-count and concurrent behavior are not directly tested there.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/devicedownloadstate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/devicedownloadstate_test.go -->
# sources/sync-backup/syncthing/lib/model/devicedownloadstate_test.go

## Purpose
Validates device download progress state transitions across versions, appends, forgets, and multiple files.

## Important APIs, Types, and Functions
`TestDeviceDownloadState` builds `protocol.FileDownloadProgressUpdate` fixtures for two versions of `f1` and one version of `f2`, then drives `newDeviceDownloadState`, `Update`, and `Has`.

## Control Flow
Each table row applies a sequence of updates to a fresh state, then iterates expected present and absent block indexes. Scenarios cover append accumulation, matching-version forget, nonmatching forget no-op, version replacement, delete then append, and multi-file isolation.

## State and Persistence Behavior
Only in-memory state is created per table row. No persisted database or filesystem state.

## Dependencies and Integration Points
Uses `protocol.Vector` and `protocol.FileDownloadProgressUpdate`, matching messages sent over Syncthing connections.

## Risks
Does not test `BytesDownloaded`, `GetBlockCounts`, nil receiver behavior, folder isolation beyond one folder name, or concurrent access.

## Test Signals
Strong signal that block availability is version-scoped and stale progress is cleared when remote devices switch file versions.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/devicedownloadstate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/doc.go -->
# sources/sync-backup/syncthing/lib/model/doc.go

## Purpose
Provides the package documentation declaration for `model`.

## Important APIs, Types, and Functions
Contains the package comment: model implements folder abstraction and file pulling mechanisms.

## Control Flow
No executable control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Used by Go documentation tooling as the package overview for model.

## Risks
The comment is intentionally brief and does not describe major concepts such as folder modes, database integration, pull queues, or scanner/watch behavior.

## Test Signals
No direct tests; compilation ensures the package declaration is valid.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/fakeconns_test.go -->
# sources/sync-backup/syncthing/lib/model/fakeconns_test.go

## Purpose
Provides mocked protocol connections for model tests, including file advertisement, request data, deletion, update, and download progress capture.

## Important APIs, Types, and Functions
`downloadProgressMessage` records folder updates. `newFakeConnection` creates a `protocolmocks.Connection` wrapper. `fakeConnection` stores files, file data, folder ID, model reference, and close state. Helpers include `setIndexFn`, `DownloadProgress`, `addFileLocked`, `addFile`, `updateFile`, `deleteFile`, `sendIndexUpdate`, and `addFakeConn`.

## Control Flow
The fake connection returns bytes from `fileData` for protocol requests, reports stable IDs, and on close calls `model.Closed` once. File helpers build `protocol.FileInfo` with scanner blocks, monotonically increasing sequences, versions based on the fake device short ID, and type-specific metadata. `addFakeConn` attaches the fake to a `testModel` and sends cluster config.

## State and Persistence Behavior
All fake state is in memory, protected by a mutex for file mutations. It does not persist files to disk; file content lives in `fileData`. Sequence timestamps use `timeutil.StrictlyMonotonicNanos`.

## Dependencies and Integration Points
Depends on protocol mocks, scanner block generation, rand IDs, and the model test harness. It integrates with `Model.IndexUpdate`, `AddConnection`, and `ClusterConfig`.

## Risks
Mocks omit many real connection behaviors, such as streaming errors, latency, authentication, and partial request failures, unless tests override mock functions. `DownloadProgress` appends without locking.

## Test Signals
This is test infrastructure; its effectiveness is visible in folder, puller, and receive-only tests that need controllable remote devices.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/fakeconns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/fileinfobatch.go -->
# sources/sync-backup/syncthing/lib/model/fileinfobatch.go

## Purpose
Batches `protocol.FileInfo` slices for database updates or index messages, limiting batch size by serialized bytes and item count.

## Important APIs, Types, and Functions
Constants `MaxBatchSizeBytes` and `MaxBatchSizeFiles` define flush thresholds. `FileInfoBatch` stores pending infos, byte size, flush function, and sticky error. Methods include `NewFileInfoBatch`, `SetFlushFunc`, `Append`, `Full`, `FlushIfFull`, `Flush`, `Reset`, and `Size`.

## Control Flow
`Append` initializes capacity, appends a file, and adds protobuf wire size. `Full` checks both thresholds. `FlushIfFull` delegates to `Flush` only when full. `Flush` no-ops on empty, calls the flush function, stores any error as sticky, and resets on success. After an error, `Append` panics and flush attempts return the same error until `Reset`.

## State and Persistence Behavior
State is in-memory only. Persistence side effects are delegated to the caller-provided flush function, commonly database updates or protocol sends.

## Dependencies and Integration Points
Uses `protocol.FileInfo.ToWire(true)` and `google.golang.org/protobuf/proto.Size`. Used heavily by folder scanning, pulling, send-only override, and receive-only revert code to control database update sizes.

## Risks
Not concurrency-safe. A nil flush function will panic if `Flush` is called with data. Sticky error semantics require callers to reset explicitly before reuse.

## Test Signals
`fileinfobatch_test.go` covers sticky error behavior and reset recovery, but not threshold calculation, protobuf sizing, or nil flush behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/fileinfobatch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/fileinfobatch_test.go -->
# sources/sync-backup/syncthing/lib/model/fileinfobatch_test.go

## Purpose
Tests `FileInfoBatch` behavior when the flush function returns an error.

## Important APIs, Types, and Functions
`TestFileInfoBatchError` uses `NewFileInfoBatch`, `Append`, `Flush`, and `Reset`.

## Control Flow
The test first flushes successfully, then sets the flush function to return a sentinel error. It verifies the error is returned, subsequent `Flush` calls return the same error without calling the flush function again, and `Reset` clears the sticky error and pending list.

## State and Persistence Behavior
Only in-memory counters and errors are used. No database or filesystem persistence.

## Dependencies and Integration Points
Uses `protocol.FileInfo` as the batched payload type and `errors.New` for the sentinel failure.

## Risks
Does not test batch full thresholds, `FlushIfFull`, `Size`, `SetFlushFunc`, append-after-error panic, or empty flush behavior.

## Test Signals
Protects a key failure contract used by folder scanner and puller batching: once a database flush fails, callers see a stable failure until reset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/fileinfobatch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder.go -->
# sources/sync-backup/syncthing/lib/model/folder.go

## Purpose
Implements the shared folder service: lifecycle, scanning, pull scheduling, health checks, watcher management, error tracking, local database updates, and forced rescans. Specialized folder modes embed this base.

## Important APIs, Types, and Functions
Core types are `folder`, `syncRequest`, `puller`, `scanBatch`, and `cFiler`. Public-like service methods include `Serve`, `Scan`, `ScheduleScan`, `DelayScan`, `SchedulePull`, `ScheduleForceRescan`, `Errors`, `WatchError`, `Override`, `Revert`, `BringToFront`, and `Jobs`. Key internals include `pull`, `scanSubdirs`, `scanSubdirsChangedAndNew`, `scanSubdirsDeletedAndIgnored`, `findRename`, watcher routines, `updateLocals`, and `unifySubs`.

## Control Flow
`Serve` sets startup state, reconciles block index, optionally starts the watcher, then runs a select loop over context cancellation, pull scheduling, pull retry backoff, initial scan completion, forced rescans, scan timers, synchronous requests, watcher events, watcher restarts, and version cleanup. `scanSubdirs` reloads ignores, takes the IO limiter, normalizes subdirs, scans changed/new files, flushes updates, then walks database prefixes to mark deleted or newly ignored items. `pull` waits for initial scan, checks need count and health, reloads ignores, takes IO when needed, delegates to the mode-specific puller, and schedules exponential retry on failure.

## State and Persistence Behavior
The folder holds timers, channels, state tracker, local/pull error slices, forced-rescan map, watcher state, stats reference, and mutable ignore matcher. Persistent state is in Syncthing DB through `db.Update`, `DropFilesNamed`, block index population/drop, folder stats, and local index events. Filesystem state is read through scanners and watchers; version cleanup may mutate versioned files via the configured versioner.

## Dependencies and Integration Points
Integrates with `config.FolderConfiguration`, `db.DB`, `fs.Filesystem`, `ignore.Matcher`, `scanner`, `events`, `stats`, `locations`, `watchaggregator`, `versioner`, and semaphores. It is the base for send-receive, send-only, receive-only, and receive-encrypted modes.

## Risks
This file has high concurrency complexity: timers must be stopped/drained correctly, buffered scheduling channels coalesce events, and watcher goroutines interact with scans. Global path health, ignore reloads, and DB updates can fail mid-scan. `updateLocals` ignores return values in some callers, and global mutable folder state requires sequencing through `doInSync`.

## Test Signals
Direct tests are not in this file, but many model tests exercise scanning, receive-only behavior, fake connections, and pull scheduling. Additional focused tests would help for `unifySubs`, watcher restart errors, forced rescan, and deleted/ignored database reconciliation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_recvenc.go -->
# sources/sync-backup/syncthing/lib/model/folder_recvenc.go

## Purpose
Implements receive-encrypted folder mode by extending send-receive behavior while treating local unexpected plaintext/encrypted items as receive-only changes that can be reverted.

## Important APIs, Types, and Functions
Registers `newReceiveEncryptedFolder` for `config.FolderTypeReceiveEncrypted`. `receiveEncryptedFolder` embeds `*sendReceiveFolder`, sets `localFlags` to `protocol.FlagLocalReceiveOnly`, and implements `Revert`, `revert`, and `revertHandleDirs`.

## Control Flow
`Revert` executes synchronously in the folder service loop. `revert` scans all local files, selects receive-only-changed non-deleted items, queues directories separately, removes non-directories from disk, marks them deleted with zero version while preserving receive-only local flag, flushes batched DB updates, then schedules a pull. Directory handling sorts deepest-first, deletes via send-receive directory deletion helpers, and schedules scans.

## State and Persistence Behavior
Updates local DB entries through `updateLocalsFromScanning`; deletes unexpected files and directories from the folder filesystem. It intentionally keeps `FlagLocalReceiveOnly` on deleted items so they are not advertised as normal valid changes.

## Dependencies and Integration Points
Depends on send-receive deletion helpers, `itererr`, `FileInfoBatch`, `protocol`, and folder service synchronization. Receive-encrypted scanning in `folder.go` uses `scanner.WalkWithoutHashing`, making this revert path part of encrypted-folder local cleanup.

## Risks
Deletion is destructive for unexpected local items. Errors are recorded as scan errors but the routine continues. Directory deletion runs alongside a pull scanner goroutine; scan channel sends must be drained until closed.

## Test Signals
No direct listed tests for receive-encrypted revert. Receive-only tests cover similar revert concepts, but encrypted-specific virtual parent and trailer behavior require separate coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_recvenc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_recvonly.go -->
# sources/sync-backup/syncthing/lib/model/folder_recvonly.go

## Purpose
Implements receive-only folder mode, where local changes are tracked but not propagated, and user-triggered revert resets or deletes local changes to return to global state.

## Important APIs, Types, and Functions
Registers `newReceiveOnlyFolder` for `config.FolderTypeReceiveOnly`. `receiveOnlyFolder` embeds `*sendReceiveFolder`, sets `localFlags` to `protocol.FlagLocalReceiveOnly`, and implements `Revert`/`revert`. `deleteQueue` batches deletions, especially directories, with `handle` and `flush`.

## Control Flow
`revert` runs in the folder loop, starts a pull scanner routine, iterates all local files, and ignores entries without receive-only local changes. It clears the receive-only flag, compares with the global file, deletes unexpected local-only items, merges equivalent global entries, or resets versions to zero so the next pull wins without conflict. Directory deletes are queued and processed deepest-first after file updates, then deleted directories are appended as deleted DB entries.

## State and Persistence Behavior
Mutates local database through `updateLocalsFromScanning`, removes files/directories from disk when local-only, clears local flags, and schedules a pull so missing global content is downloaded. No remote index should be advanced by receive-only changes because local flags are converted when advertised.

## Dependencies and Integration Points
Depends on `sendReceiveFolder` pull/delete helpers, `itererr`, `FileInfoBatch`, `events`, `ignore.Matcher`, and `protocol.FileInfo` comparison rules. Model API calls `Revert` for receive-only folders.

## Risks
Revert is intentionally destructive for unexpected local items. Ignored but non-deletable items are skipped. Some `FlushIfFull` calls ignore returned errors inside the loop, which may delay error reporting until final flush. Correctness depends on subtle `FileInfoComparison` flags for ownership and xattrs.

## Test Signals
`folder_recvonly_test.go` extensively covers deletion of unexpected files, reset-to-need behavior, undoing local changes, remote drop handling, remote adoption of identical changes, own-ID version regression, and avoiding conflict loops.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_recvonly.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_recvonly_test.go -->
# sources/sync-backup/syncthing/lib/model/folder_recvonly_test.go

## Purpose
Regression and behavior tests for receive-only folder local-change tracking and revert semantics.

## Important APIs, Types, and Functions
Tests include `TestRecvOnlyRevertDeletes`, `TestRecvOnlyRevertNeeds`, `TestRecvOnlyUndoChanges`, `TestRecvOnlyDeletedRemoteDrop`, `TestRecvOnlyRemoteUndoChanges`, `TestRecvOnlyRevertOwnID`, and `TestRecvOnlyLocalChangeDoesNotCauseConflict`. Helpers are `setupKnownFiles` and `setupROFolder`.

## Control Flow
Each test constructs a receive-only model, fake remote connection, and fake filesystem content. They send remote indexes, scan local state, mutate files or remote state, call `m.Revert` or direct pull, then assert global, local, need, and receive-only sizes or file existence. The own-ID test subscribes to local index updates and waits for a non-deleted equivalent file after revert.

## State and Persistence Behavior
Tests use the model database and fake filesystem to exercise real local index updates, scan results, deletion on disk, and event emission. Remote state is simulated via fake connection index updates.

## Dependencies and Integration Points
Uses the model test harness, config wrappers, `addFakeConn`, scanner blocks, events, and filesystem helpers. It validates receive-only integration across scanner, DB global/local views, puller, and revert API.

## Risks
The tests are integration-heavy and can be timing-sensitive where they wait on events. They focus on receive-only, not receive-encrypted. Assertions are mostly size-based, so some metadata details may be unverified.

## Test Signals
Strong coverage for user-visible receive-only invariants: local changes are detected but not needed, revert makes old global data needed again, equivalent remote changes clear receive-only state, and repeated local edits do not produce conflict pulls.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_recvonly_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendonly.go -->
# sources/sync-backup/syncthing/lib/model/folder_sendonly.go

## Purpose
Implements send-only folder behavior: never downloads file content, but can merge metadata-only differences and allow the local side to override global state.

## Important APIs, Types, and Functions
Registers `newSendOnlyFolder` for `config.FolderTypeSendOnly`. `sendOnlyFolder` embeds `*folder`, implements `PullErrors`, `pull`, `Override`, and `override`.

## Control Flow
`pull` iterates needed global files alphabetically. Ignored files are invalidated locally, missing invalid/deleted entries can be accepted for accounting, and files equivalent to current local state except allowed metadata differences are merged into the local DB. `override` iterates needed globals, skips invalid local states, marks missing local files as deleted, or merges local versions with needed versions and updates the local version with the local short ID.

## State and Persistence Behavior
Writes local DB batches through `updateLocalsFromPulling` and `updateLocalsFromScanning`. It does not perform content IO during pull, and `PullErrors` always returns nil. Override changes local version vectors and sequence reset to force database sequencing.

## Dependencies and Integration Points
Depends on `itererr`, `FileInfoBatch`, `config`, `ignore`, `protocol`, and folder base scheduling. The base `folder.pull` treats send-only specially by not taking the IO limiter for content transfer.

## Risks
Send-only semantics are subtle: accepting metadata-only global entries must not hide real content differences. Override can propagate local deletions for missing files, so UI/API access should remain deliberate. `batch.Flush()` return in `pull` is not checked.

## Test Signals
No direct listed send-only tests in this subset. Behavior is likely covered elsewhere in model tests; this file would benefit from focused tests for metadata merge, ignored need invalidation, and override version vector updates.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendonly.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendrecv.go -->
# sources/sync-backup/syncthing/lib/model/folder_sendrecv.go

## Purpose
Implements the full send-receive puller: deciding needed work, creating/updating/deleting directories, files, and symlinks, reusing blocks, requesting remote blocks, finishing temp files, handling conflicts, batching DB updates, and tracking pull errors.

## Important APIs, Types, and Functions
Registers `newSendReceiveFolder` for `config.FolderTypeSendReceive`. Key types are `pullBlockState`, `copyBlocksState`, `dbUpdateType`, `dbUpdateJob`, `sendReceiveFolder`, and `FileError`. Major methods include `pull`, `pullerIteration`, `processNeeded`, `processDeletions`, `handleDir`, `checkParent`, `handleSymlink`, `deleteDir`, `deleteFileWithCurrent`, `renameFile`, `handleFile`, `reuseBlocks`, `copierRoutine`, `pullerRoutine`, `pullBlock`, `performFinish`, `finisherRoutine`, `dbUpdaterRoutine`, `pullScannerRoutine`, `moveForConflict`, `deleteDirOnDiskHandleChildren`, `scanIfItemChanged`, and `checkToBeDeleted`. Helpers include `blockDiff`, `populateOffsets`, `verifyBuffer`, `conflictName`, `isConflict`, and `existingConflicts`.

## Control Flow
`pull` runs up to three iterations until no changes or pull errors remain. Each `pullerIteration` starts DB updater, copier workers, a puller routine, and a finisher routine wired by channels. `processNeeded` classifies needed items: ignored/invalid entries become DB invalidations, deletions are deferred or executed, directories and symlinks are handled directly, files enter a job queue, and rename shortcuts are attempted by matching block hashes against pending deletions. File pulls build shared state, reuse temp blocks, reorder remaining blocks, copy from local/current/other-folder block indexes, request missing blocks from least-busy peers, then finish by setting metadata, replacing the target, and enqueueing DB updates.

## State and Persistence Behavior
Mutates filesystem contents through mkdir, chmod, xattrs/ownership, symlink creation, remove, rename/copy, versioner archive, temp file writes, sparse-file skips, and conflict-copy creation. Mutates DB through batched local updates, invalidations, deletions, block index reads, and local index events. In-memory state includes job queue, temp pull errors, global block stats, device activity, channels, wait groups, and per-file shared puller state.

## Dependencies and Integration Points
Integrates with model availability and `RequestGlobal`, `sharedPullerState`, job queue, scanner, protocol block/file metadata, fs/osutil operations, versioning, events, semaphores, config options, ignore matching, and database iterators. It is embedded by receive-only and receive-encrypted modes.

## Risks
This is high-risk synchronization code: channel ordering, context cancellation, partial temp files, DB batching, and filesystem race checks must align. Deletion logic intentionally refuses to remove changed or ignored content, but edge cases can cause repeated pull errors. Receive-encrypted skips hash verification locally. Some flush calls ignore return values. Global `blockStats` and `activity` couple work across folders.

## Test Signals
The listed subset has no direct send-receive test file, but block reorderer, device activity, fake connection, file batch, and receive-only tests cover important pieces. Additional tests should target rename shortcuts, conflict limits, directory delete error precedence, sparse zero blocks, receive-encrypted trailer shortcut, and cancellation paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendrecv.go -->
