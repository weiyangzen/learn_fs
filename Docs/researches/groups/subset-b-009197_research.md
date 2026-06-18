# subset-b-009197 research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendrecv_test.go -->
## sources/sync-backup/syncthing/lib/model/folder_sendrecv_test.go

Purpose: this file is a focused regression and behavior test suite for the `sendReceiveFolder` pull path. It exercises block selection, local block reuse, temp-file reuse, copier/puller/finisher handoff, deletion behavior, ownership propagation, sparse zero-block handling, case-conflict behavior, and cleanup of progress state after failures. The tests are package-internal, so they call unexported helpers such as `handleFile`, `copierRoutine`, `pullerRoutine`, `finisherRoutine`, `performFinish`, `handleDir`, `handleSymlink`, `deleteDir`, `deleteFile`, `deleteDirOnDisk`, `renameFile`, `blockDiff`, and `scanSubdirs`.

Important fixtures and helpers: `blocks` provides deterministic `protocol.BlockInfo` values, including the all-zero block used by sparse-file tests. `prepareTmpFile` copies `testdata/tmpfile` into a folder filesystem and pushes its mtime into the future, letting temp reuse logic be tested. `diffTestData`, `setupFile`, and `createEmptyFileInfo` create protocol file metadata for block-diff and conflict tests. `setupSendReceiveFolder` builds a test model, immediately stops services, extracts the `sendReceiveFolder`, initializes `tempPullErrors`, and optionally seeds local index state through `updateLocalsFromScanning`. `cleanupSharedPullerState` and `startCopier` are concurrency helpers for tests that manually wire the pull pipeline.

Control flow covered: `TestHandleFile` and `TestHandleFileWithTemp` verify that required blocks are sent to the copy path and that blocks already present in an existing temp file are not redundantly copied or pulled. `TestCopierFinder` runs `copierRoutine` and validates that reused local blocks are written into the temp file while missing blocks are emitted to the pull channel. `TestDeregisterOnFailInCopy` and `TestDeregisterOnFailInPull` force failures mid-pipeline and then confirm that finisher cleanup deregisters progress, drains queue state, closes writers, and emits exactly one `ItemFinished` event. Several tests drive deletion and finish logic directly to cover ignored directories, symlink boundaries, unscanned directories, and case-only filesystem conflicts.

State and persistence behavior: most tests interact with the fake or configured folder filesystem, the model database, the pull queue, the progress emitter, temp pull error map, and event logger. `TestCopierCleanup` is the strongest database signal: it updates local FileInfo block lists and confirms obsolete block hashes disappear from the local block map while new hashes are discoverable. Deletion tests check that disk operations and `dbUpdateJob` emissions are separated correctly: a safe delete may enqueue a DB update, while ambiguous ignored or unscanned state schedules scans instead.

Dependencies and integration points: the suite uses `config`, `fs`, `ignore`, `protocol`, `scanner`, `events`, `build`, and `itererr` from Syncthing plus Go concurrency primitives. Tests are sensitive to platform behavior: symlink tests skip on Windows, owner-copy tests skip on Windows, and Windows-specific unsupported symlink replacement is covered by `TestPullSymlinkOverExistingWindows`. The tests integrate with the real scanner hash logic, fake filesystem ownership APIs, the model event bus, and protocol version vectors.

Risks: many tests are concurrency-sensitive and rely on timeouts, channels, and manual cleanup. Failure to close channels or file writers can deadlock or leak goroutines. Case-only rename behavior differs by filesystem case sensitivity, so tests allow either a direct DB update on case-sensitive systems or an expected case-conflict error path. Sparse zero-block behavior is subtle: a reused temp file or disabled sparse support must force zero bytes to be written, while a clean sparse hole can skip writes safely. Ignored delete handling is high risk because deleting behind symlinks or through ignored child directories could remove data outside the intended tree.

Test signals: this file is itself the test signal for send/receive behavior. It covers positive block-copy behavior, failure cleanup idempotency, blockmap cleanup, conflict creation for file-to-dir and file-to-symlink replacement, symlink boundary safety, context cancellation, zero block materialization, unscanned directory safety, case conflicts, unsupported Windows symlinks, and ignored child directory delete protection.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendrecv_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendrecv_unix.go -->
## sources/sync-backup/syncthing/lib/model/folder_sendrecv_unix.go

Purpose: this non-Windows implementation provides `(*sendReceiveFolder).syncOwnership` for Unix-like platforms. It applies owner and group metadata from `protocol.FileInfo.Platform.Unix` to an on-disk path through the folder's mtime-aware filesystem wrapper.

Important API: `syncOwnership(file *protocol.FileInfo, path string) error` is the only function. It returns nil when no Unix platform ownership data is present. When metadata exists, it converts numeric UID and GID to strings, optionally resolves `OwnerName` and `GroupName` through `os/user`, and calls `f.mtimefs.Lchown(path, uid, gid)`. The use of `Lchown` is important because ownership updates must apply to the path itself rather than following symlinks.

Control flow: the function first checks `file.Platform.Unix == nil` and exits early. It initializes fallback owner and group strings from `UID` and `GID`. If owner or group names are populated, it attempts a name lookup; successful lookups with non-empty IDs replace the numeric fallback. Lookup failures are intentionally ignored, preserving the numeric identifiers from the remote metadata. Finally, the resolved string IDs are passed to the filesystem layer.

State and persistence behavior: there is no in-memory state. The only persistent effect is filesystem metadata mutation through `mtimefs.Lchown`. The code does not update database state directly; any index update or scan reconciliation happens elsewhere in the send/receive pipeline.

Dependencies and integration points: it depends on Go's `os/user` package, `strconv`, and Syncthing's `protocol.PlatformData`. Its primary integration point is the `sendReceiveFolder` platform-data application path. It also relies on the configured filesystem implementation supporting `Lchown`; fake filesystems in tests can emulate ownership, while real filesystems may require privileges.

Risks: user and group name resolution is host-local and may not match the source device. The numeric fallback is necessary for portability but may still fail if the process lacks permission. Because lookup errors are swallowed, troubleshooting depends on the eventual `Lchown` error. The path must already be safely resolved by callers; this function deliberately uses link-aware ownership mutation but does not perform path validation.

Test signals: ownership behavior is indirectly covered by send/receive tests such as parent-owner copy tests and by platform-data tests that ensure `setPlatformData` can run against a filesystem. Direct Unix owner-name resolution edge cases are not tested here.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendrecv_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendrecv_windows.go -->
## sources/sync-backup/syncthing/lib/model/folder_sendrecv_windows.go

Purpose: this Windows implementation provides ownership synchronization for `sendReceiveFolder` and helper functions for resolving Windows user or group names into IDs accepted by the filesystem `Lchown` abstraction.

Important APIs: `syncOwnership(file *protocol.FileInfo, path string) error` applies `protocol.FileInfo.Platform.Windows.OwnerName` when present. `lookupUserAndGroup(name string, group bool) (string, string, error)` resolves either a user ID or group ID and leaves the other field blank, matching `Lchown` expectations. `lookupWithoutDomain(name string, lookup func(string) (string, error)) (string, error)` retries qualified names without the `DOMAIN\` prefix.

Control flow: `syncOwnership` exits when Windows platform data or owner name is missing. It logs the requested owner and group flag, resolves the principal using `lookupUserAndGroup`, logs the resolved IDs, and calls `f.mtimefs.Lchown(path, usid, gsid)`. If the platform metadata marks the owner as a group, group lookup is used; otherwise user lookup is used. The lookup helper tries the full name first and then, only for a two-part backslash-qualified name, retries the user or group portion after the backslash.

State and persistence behavior: the function has no database state. Its persistent effect is an ownership change on the filesystem object. Failed lookups stop before filesystem mutation and return contextual errors such as `lookup user <name>` or `lookup group <name>`.

Dependencies and integration points: it uses Go `os/user`, `strings`, `fmt`, Syncthing logging, `protocol.PlatformData`, and the folder's `mtimefs`. It integrates with the same platform-data application path as the Unix implementation, but must bridge Windows account naming conventions to the filesystem interface.

Risks: Windows account names can include domains, local machine prefixes, groups, and localized names. The retry logic only handles exactly one backslash separator, so unusual forms may fail. The function returns lookup errors instead of silently falling back, unlike the Unix version; this stricter behavior can surface as pull errors. Correctness also depends on the filesystem backend interpreting blank user or group fields the same way the function expects.

Test signals: direct tests for `lookupUserAndGroup` are not present in this subset. Windows send/receive coverage exists for symlink-over-existing-file behavior, but ownership resolution relies mainly on platform-specific runtime coverage and fake filesystem behavior elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_sendrecv_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_summary.go -->
## sources/sync-backup/syncthing/lib/model/folder_summary.go

Purpose: this file implements the `FolderSummaryService`, which listens to model and protocol events, batches folders needing recalculation, computes API-compatible folder summaries, emits `FolderSummary` and `FolderCompletion` events, and updates folder summary metrics.

Important APIs and types: `FolderSummaryService` combines `suture.Service` with `Summary(folder string) (*FolderSummary, error)`. `NewFolderSummaryService` constructs a supervised service with two children: `listenForUpdates` and `calculateSummaries`. `FolderSummary` is the externally serialized API shape, preserving legacy fields such as `PullErrors`, `Invalid`, and `Version`. `FolderSummaryEventData` wraps a folder ID and summary for event logging.

Summary control flow: `Summary` gathers model data through `FolderErrors`, `GlobalSize`, `LocalSize`, `NeedSize`, `ReceiveOnlySize`, `Sequence`, and `RemoteSequences`. It tolerates paused or not-running folders by returning an empty-compatible summary rather than an error, preserving API behavior. It adjusts needed deletes for `IgnoreDelete`, subtracts completed progress bytes from need bytes, clamps negative need bytes to zero, fills receive-only changed counters only for receive-only or receive-encrypted folders, computes in-sync files and bytes, attaches current folder state and state error, detects meaningful ignore patterns by ignoring comment lines beginning with `//`, and attaches watch errors.

Event control flow: `listenForUpdates` subscribes to local and remote index updates, state changes, remote and local download progress, device connection, cluster config, and folder watch state changes. `processUpdate` marks specific folders dirty, all folders shared with a connected or configured device dirty, or sends an immediate refresh when a folder transitions from syncing or sync-preparing to idle. The immediate send is nonblocking so event handling does not stall. `calculateSummaries` pumps every two seconds plus a backoff proportional to calculation time, drains the dirty-folder set, and also handles immediate folder refreshes.

State and persistence behavior: service state is in-memory: a mutex-protected `folders` dirty set and an `immediate` channel. It does not persist summary state to the database; it reads persisted model counts and sequences and emits events/metrics. Metrics are updated in `sendSummary` for global, local, and need scopes. Folder completion events are generated per configured remote device, excluding the local device ID.

Dependencies and integration points: this service sits between `config.Wrapper`, the `Model` interface, `events.Logger`, the suture service tree, `svcutil`, database count types, protocol device IDs, and Prometheus metrics declared in `metrics.go`. It feeds GUI/API consumers through the event stream and metric consumers through gauges.

Risks: event data is type-asserted, so mismatched event payloads panic. Dirty-folder batching trades freshness for bounded CPU use; long summary calculations extend the next pump interval. `sendSummary` indexes `c.cfg.Folders()[folder]`, so folder removal or stale event ordering can be risky if configuration lookup assumptions change. Need byte adjustment depends on progress accounting not exceeding current need; the clamp prevents negative external values but may hide transient accounting races.

Test signals: this subset includes the generated `FolderSummaryService` mock but no direct tests for summary event batching. Existing behavior is indirectly covered by model and API tests that use the service or mock the `Model` methods it calls.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_summary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_test.go -->
## sources/sync-backup/syncthing/lib/model/folder_test.go

Purpose: this test file covers folder-level utility behavior, primarily scan subdirectory normalization through `unifySubs` and platform-data application through `sendReceiveFolder.setPlatformData`.

Important types and helpers: `unifySubsCase` describes input subdirectories, paths known to exist in the database, and expected normalized output. `unifySubsCases` returns platform-adjusted cases, converting slash separators on Windows. The tests use `messagediff` for readable output differences and `slices.Contains` to implement a fake existence predicate.

Control flow covered by `TestUnifySubs`: trailing slash cleanup, deterministic sorting, subsumption of child paths by parent paths, interpreting `nil`, empty input, or explicit empty string as full-folder scan, preserving unknown children when a known parent exists, distinguishing true path prefixes from lexical prefixes such as `usr/lib` vs `usr/libexec`, preserving special files `.stfolder` and `.stignore`, falling back to scanning a known parent when an unknown path cannot be trusted, and cleaning absolute paths into folder-relative paths.

`BenchmarkUnifySubs` repeatedly runs the same cases to track allocation and performance behavior. This matters because subdirectory scan requests can be a frequent control path when file watchers or users request partial rescans.

`TestSetPlatformData` creates a fake filesystem, writes a temp file, constructs a `protocol.FileInfo` whose `Name` intentionally does not match the target path, sets permissions, modified time, and xattrs for Linux, Darwin, FreeBSD, and NetBSD, and calls `setPlatformData` with `SyncXattrs` enabled. The intent is to ensure platform metadata is applied to the explicit path argument and does not accidentally depend on `FileInfo.Name`.

State and persistence behavior: `TestUnifySubs` is pure, using only a fake database-existence callback. `TestSetPlatformData` mutates a fake filesystem and validates no error from xattr/permission/time application. No model database is used directly.

Dependencies and integration points: tests exercise `config.DefaultMarkerName`, `config.XattrFilter`, `fs.NewFilesystem`, `protocol.PlatformData`, scanner-compatible file metadata, build platform detection, and `sendReceiveFolder`'s embedded `folder` configuration. The xattr test is a cross-platform compatibility signal for the platform-specific send/receive files.

Risks: `unifySubs` must avoid overscanning too broadly while never missing necessary paths; special marker and ignore files are exceptions to normal existence logic. Platform-data application must not trust remote file names for local path selection. Coverage is strong for representative normalization cases but not exhaustive for all path-cleaning edge cases or every platform xattr implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folderstate.go -->
## sources/sync-backup/syncthing/lib/model/folderstate.go

Purpose: this file defines folder state enums, remote folder state enums, and `stateTracker`, the concurrency-safe state transition helper that logs state changes and updates metrics.

Important APIs and types: `folderState` values include idle, scanning, scan-waiting, sync-waiting, sync-preparing, syncing, cleaning, clean-waiting, error, and starting. `folderState.String` maps values to the external event/API strings. `remoteFolderState` represents unknown, not sharing, paused, and valid remote folder states; it implements `String` and `MarshalText` for textual serialization. `stateTracker` stores folder ID, event logger, mutex, current state, current error, and last-changed timestamp. `newStateTracker`, `setState`, `getState`, and `setError` are the main functions.

Control flow: `setState` is for non-error states only and panics if called with `FolderError`, forcing callers to use `setError` for error transitions. It no-ops if the new state equals the current state. Otherwise it builds `StateChanged` event data containing folder, from, to, and optional duration since the previous change; logs a debug message; updates current state and truncates the changed timestamp to whole seconds; emits the event; and updates `metricFolderState` in a deferred call. `setError` handles both entering an error state and clearing back to idle. It emits warn/info logs for visible error transitions, includes the error string when present, updates `s.err`, and logs a `StateChanged` event.

State and persistence behavior: all state is in-memory and protected by a mutex. The persistent/external effects are event log entries and metric gauge values. The timestamp truncation stabilizes externally visible times to second precision. The current error is retained until cleared through `setError(nil)`.

Dependencies and integration points: it depends on `events.Logger`, structured logging through `log/slog` and `slogutil`, and the `metricFolderState` gauge from `metrics.go`. Folder summary code consumes model state strings and changed times, while GUI/API consumers receive `StateChanged` events. Remote folder state text marshaling is used when remote sharing status is serialized.

Risks: the initial zero value of `folderState` is idle and `changed` starts zero, so first transition duration is omitted. Calling `setState(FolderError)` panics by design and is a sharp API boundary. Metrics are updated after the state mutation through `defer`; if event logging ever blocks or panics, metric freshness could be affected. `setError(nil)` always transitions to idle, which is correct for current semantics but would be risky if clearing an error should resume a prior non-idle state.

Test signals: direct tests are not in this subset. Indirect signals appear in folder summary event handling, which reacts to state transitions into idle from syncing or sync-preparing, and in any model tests that inspect folder state strings or errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/folderstate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/indexhandler.go -->
## sources/sync-backup/syncthing/lib/model/indexhandler.go

Purpose: this file implements per-device/per-folder index exchange. An `indexHandler` sends local file index data to a protocol connection, receives remote index and index updates into the database, tracks delta-index sequence state, handles pause/resume, and reports anomalies. `indexHandlerRegistry` manages handler lifecycle across folder configuration, remote cluster config, and pause/removal changes.

Important types: `indexHandler` stores the protocol connection, download state, folder ID, receive-encrypted flag, event logger, two sequence cursors, a pause condition variable, database, and folder runner. `localPrevSequence` is the highest local sequence seen while iterating the database and may skip holes. `sentPrevSequence` is the highest sequence actually sent to the peer and must not skip holes because it is used in protocol correctness checks. `indexHandlerRegistry` owns a service map of active handlers, pending cluster start info, current folder runner/config state, and shared dependencies.

Construction control flow: `newIndexHandler` reads local index ID and sequence, compares peer-provided local knowledge to determine whether delta updates can start at a remote max sequence or must restart from zero, and compares the peer's announced remote index ID with the database. Missing or changed remote index IDs cause `DropAllFiles` for that device, and changed IDs are persisted through `SetIndexID`. It then initializes both sequence cursors to the selected start sequence.

Send control flow: `Serve` sends one initial index after waiting for unpaused state, subscribes to local index updates and device disconnects, and then loops. If the local database sequence is not ahead of `localPrevSequence`, it waits on context, event, or a minute ticker. When new data exists, `sendIndexTo` iterates `AllLocalFilesBySequence` from `localPrevSequence + 1`, batches with `NewFileInfoBatch`, sends the first batch as `Index` when starting from zero and later batches as `IndexUpdate`, and delays 250 ms after each send to coalesce changes. Batching allows a final delete to stay with a preceding add to preserve rename semantics. It validates nondecreasing database sequence behavior and reports anomalies as failures.

Receive control flow: `ReceiveIndex` finds the active handler under registry lock and delegates to `receive`. `receive` rejects paused handlers, schedules a pull when done, forgets download progress for files present in the update, drops all remote files on a full index, validates `prevSequence`, per-file sequence bounds, monotonicity, and `lastSequence`, updates the database, verifies the resulting device sequence, and logs `RemoteIndexUpdated` with item count and sequence.

State and persistence behavior: local and sent sequence cursors are in-memory per connection. Persistent state changes happen through database index ID reads/writes, `DropAllFiles`, remote file `Update`, and device sequence reads. Download progress is updated with forget records for regular files. Registry state controls active services and pending start info but does not persist.

Dependencies and integration points: the handler integrates protocol messages (`Index`, `IndexUpdate`), the database, config folder types, event logging, download progress state, service supervision, and runner scheduling. `prepareFileInfoForIndex` clears versions for receive-only changed files so they cannot win globally and subtracts encryption trailer size before announcing sizes. Receive-encrypted folders skip locally changed receive-only file infos entirely to avoid sending unencrypted metadata to peers.

Risks: sequence correctness is critical; mixing `localPrevSequence` and `sentPrevSequence` incorrectly can break delta indexes or skip data. Error handling in registry `startLocked` callers is currently ignored in some paths with comments, so start failures may be only logged elsewhere. `receive` defers `runner.SchedulePull`; this assumes runner is non-nil whenever not paused. Event payload and database anomalies are reported but not always fatal on receive. The registry holds its mutex while calling `is.receive`, which performs database work and scheduling; changing that could affect concurrency.

Test signals: `indexhandler_test.go` stresses concurrent protocol index updates through `FileInfoBatch`. Other tests outside this subset likely cover cluster config and database behavior. This file logs anomalies through `events.Failure`, making runtime event streams an important diagnostic signal for sequence bugs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/indexhandler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/indexhandler_test.go -->
## sources/sync-backup/syncthing/lib/model/indexhandler_test.go

Purpose: this test file verifies that large numbers of index update messages can be sent through Syncthing protocol connections using `model.NewFileInfoBatch` without message loss or race detector failures.

Important test: `TestIndexhandlerConcurrency` creates two connected protocol endpoints using paired `io.Pipe` readers and writers. It uses generated `mocks.Model` instances as protocol model callbacks, starts both connections, exchanges empty cluster config and initial index messages for folder `foo`, and then sends 500 batches of 1000 files each from one side to the other.

Control flow: the receiving mock installs `IndexUpdateCalls` to verify every received filename matches the expected batch and index position (`f<batch>-<file>`), increments received entry and batch counters, and marks a waitgroup item done. The sender builds a `FileInfoBatch` with a flush function that calls `c1.IndexUpdate`. For each batch, the test appends 1000 `protocol.FileInfo` values with block hashes, adds one waitgroup item, and flushes. It waits for all receiver callbacks before closing connections and checking sent vs received counts.

State and persistence behavior: there is no database persistence. The state under test is protocol connection state, batch buffering, callback invocation counts, waitgroup synchronization, and transport ordering over pipes.

Dependencies and integration points: it depends on `protocol.NewConnection`, generated protocol mocks, generated model mocks, `testutil.NoopCloser`, and the public `model.NewFileInfoBatch` helper. It exercises real protocol serialization/deserialization and callback dispatch rather than only unit-level batch logic.

Risks: this is a high-volume concurrency test and can expose races when run with `go test -race`. Without the waitgroup, connection close can race with the final outgoing message, so the test explicitly waits for the receiving side to observe all expected batches before closing. The test assumes each `IndexUpdate` contains exactly `files` entries and indexes directly into `idxUp.Files[j]`; a short malformed message would panic or fail loudly.

Test signals: the primary signal is equality between `sentEntries` and `recvdEntries`, plus per-file name order validation and race detector cleanliness. It does not validate index handler database sequence logic directly; it validates the lower-level protocol and batch transport path that index sending relies on.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/indexhandler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/metrics.go -->
## sources/sync-backup/syncthing/lib/model/metrics.go

Purpose: this file declares Prometheus metrics for the model package's folder state, folder summary counts, pull and scan activity, processed bytes, and conflict counts. It also provides `registerFolderMetrics` to pre-create labeled time series for a folder.

Important metrics: `metricFolderState` is a gauge labeled by folder. `metricFolderSummary` is a gauge labeled by folder, scope, and type; the promlinter warning is suppressed because one vector intentionally carries several summary dimensions. Pull and scan counters track total iterations and total seconds per folder. `metricFolderProcessedBytesTotal` tracks bytes by folder and source, with sources `network`, `local_origin`, `local_other`, and `skipped`. `metricFolderConflictsTotal` counts conflicts per folder.

Control flow: package initialization registers metrics through `promauto`, so importing the model package registers collectors globally. `registerFolderMetrics(folderID string)` touches each relevant label combination so counters and gauges exist even before nonzero activity. It initializes state, pulls, pull seconds, scans, scan seconds, processed byte sources, and conflicts. Folder summary scope/type combinations are updated in `folder_summary.go` when a summary is sent rather than pre-created here.

State and persistence behavior: metric state lives in Prometheus collector objects in process memory. It is not persisted by this file. Values are mutated by other model code during state transitions, scans, pulls, summaries, and conflict handling.

Dependencies and integration points: depends on `github.com/prometheus/client_golang/prometheus` and `promauto`. `folderstate.go` writes `metricFolderState`, `folder_summary.go` writes `metricFolderSummary`, and send/receive or scan paths update the counters. External integration is through Prometheus scraping and any API exposing registered metrics.

Risks: global `promauto` registration can panic on duplicate metric names if package-level registration is repeated in unusual test setups. Label cardinality is bounded by folder IDs and a small fixed set of scopes/types/sources, but folder churn can still grow metric series over process lifetime. Because folder summary uses a multi-dimensional generic gauge, consumers must interpret labels correctly.

Test signals: no direct tests in this subset. Runtime validation comes from metric scrape output and tests around state transitions, pulls, scans, and summaries that update the metrics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/mocks/folderSummaryService.go -->
## sources/sync-backup/syncthing/lib/model/mocks/folderSummaryService.go

Purpose: this generated counterfeiter fake implements `model.FolderSummaryService` for tests. It lets tests stub service behavior, set default or per-call returns, inspect call counts and arguments, and retrieve a consolidated invocation map.

Important API surface: the fake has `Serve` and `Summary` methods matching the real interface. For each method it exposes `Calls` to install a stub, `CallCount`, `ArgsForCall`, `Returns`, and `ReturnsOnCall`. It also exposes `Invocations` for all recorded calls. The compile-time assertion `var _ model.FolderSummaryService = new(FolderSummaryService)` guarantees interface compatibility.

Control flow: each fake method locks its method-specific mutex, records arguments, captures the current stub and configured return values, records the invocation in the shared map, unlocks, and then calls the stub if present. If no stub is set, a per-call return overrides the default return; otherwise the default return is used. This lock-then-unlock-before-stub pattern avoids holding fake internals locked while user test code executes.

State and persistence behavior: all state is in-memory test state: argument slices, return structs, per-call return maps, stubs, and invocation records. There is no persistence. The invocation map copy returned by `Invocations` copies the map but not the nested slices, which is standard for these generated fakes but means callers should treat it as observational test data rather than mutable isolated state.

Dependencies and integration points: it imports `context`, `sync`, and the real `model` package. Tests that need a `FolderSummaryService` can use this fake without starting a suture service. It is generated from the `go:generate` directive in `folder_summary.go`.

Risks: because it is generated, manual edits would be overwritten. Default zero returns can hide missing test setup unless tests assert call counts or configure explicit returns. The fake is concurrency-aware for its own bookkeeping, but returned pointers such as `*model.FolderSummary` are not deep-copied.

Test signals: there are no tests for the fake itself. Its correctness signal is successful compilation against `model.FolderSummaryService` and the behavior of tests that depend on call recording.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/mocks/folderSummaryService.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/mocks/model.go -->
## sources/sync-backup/syncthing/lib/model/mocks/model.go

Purpose: this generated counterfeiter fake implements the large `model.Model` interface for unit and protocol tests. It provides method stubs, call recording, default returns, per-call returns, and argument inspection for model operations spanning connections, folder/file indexes, ignore handling, scans, requests, statistics, state, and usage reporting.

Important API surface: the fake covers connection lifecycle (`AddConnection`, `Closed`, `ConnectedTo`, `OnHello`, `ClusterConfig`), protocol data paths (`Index`, `IndexUpdate`, `DownloadProgress`, `Request`), file/index queries (`AllGlobalFiles`, `LocalFiles`, `LocalFilesSequenced`, `CurrentFolderFile`, `CurrentGlobalFile`, `NeedFolderFiles`, `RemoteNeedFolderFiles`), summary dependencies (`FolderErrors`, `GlobalSize`, `LocalSize`, `NeedSize`, `ReceiveOnlySize`, `FolderProgressBytesCompleted`, `Sequence`, `RemoteSequences`, `State`, `CurrentIgnores`, `WatchError`, `Completion`), scan and ignore controls, version restore/reset/revert/override, pending device/folder APIs, and stats/reporting APIs. The final assertion ensures it satisfies `model.Model`.

Control flow pattern: every method follows the counterfeiter template. It locks a method-specific mutex, records argument values, snapshots the configured stub and returns, records a shared invocation entry, unlocks, and either calls the stub, returns a per-call override, or returns defaults. Void methods call only stubs after recording. Methods accepting mutable slices such as `RequestGlobal`, `ScanFolderSubdirs`, and `SetIgnores` copy slice arguments before storing them, preventing later caller mutation from corrupting recorded arguments.

State and persistence behavior: state is entirely in-memory test bookkeeping. There is no database or filesystem behavior unless a test provides a stub. Return maps, slices, iterators, and pointers are generally returned as configured, without deep copies. The fake uses separate mutexes per method plus an invocation mutex, so tests can safely record calls from multiple goroutines, as seen in protocol concurrency tests.

Dependencies and integration points: imports include `context`, `iter`, `net`, `sync`, `time`, Syncthing `db`, `model`, `protocol`, `stats`, `contract`, and `versioner`. It is used by protocol/model tests to satisfy callback interfaces without starting a real model. In this subset, `indexhandler_test.go` uses it as the protocol connection model on both sides.

Risks: generated fakes can mask behavior because default zero values may be valid-looking. Tests must configure stubs or assert invocations when behavior matters. Some recorded return values and invocation maps are shallow copies, so concurrent mutation by test code can still race outside the fake's locks. The file is large and generated; interface changes require regeneration rather than hand edits.

Test signals: this file's main signal is compilation against `model.Model`. Behavior is exercised indirectly by tests that install callbacks, especially `IndexUpdateCalls` in the index handler concurrency test. The slice-copying methods provide better argument inspection signals for mutable byte/string slices.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/mocks/model.go -->
