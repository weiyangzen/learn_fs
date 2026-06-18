# subset-b-009154 Research Report

Grouped code research for the Kopia robustness, test tooling, socket activation, packaging, and Docker files assigned to subset-b-009154. Each source file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/log.go -->
# sources/sync-backup/kopia/tests/robustness/engine/log.go

This file defines the robustness engine action log. `Log` holds all `LogEntry` records plus `ThisRunStartIdx`, and `LogEntry` captures `Time`, `Action`, command options, outputs, success state, and an error string. The formatting path is `LogEntry.String`, `formatTime`, `Log.StringThisRun`, and `Log.String`, which provide human-readable chronological diagnostics for all actions or only the current engine run.

The important API is append/find behavior: `AddEntry` appends a started action, `AddCompleted` mutates a started entry with completion state, and `FindLast`/`FindLastThisRun`/`findLastUntilIdx` find the most recent entry for an `ActionKey`. `setLogEntryCmdOpts` records action options deterministically enough for logs, while `Engine.logCompleted` ties engine action execution to stats persistence.

State is entirely in-memory until `metadata.go` serializes `EngineLog` into the configured metadata persister. Risks center on log entries being mutable after append, stringification losing structured error details, and callers needing to pass the same `LogEntry` pointer to completion. Test signals are indirect through engine robustness flows that depend on last snapshot/action lookup and persisted logs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/metadata.go -->
# sources/sync-backup/kopia/tests/robustness/engine/metadata.go

This file persists and restores engine metadata keys for action history, cumulative stats, and the snapshot ID index. The public surface is engine methods `saveLog`, `loadLog`, `saveStats`, `loadStats`, `saveSnapIDIndex`, and `loadSnapIDIndex`; each marshals or unmarshals JSON against `e.MetaStore`, which satisfies the robustness persister/store contract.

Control flow is uniform: save methods `json.Marshal` current engine state and call `Store`; load methods call `Load`, tolerate `robustness.ErrKeyNotFound` as an empty initial state, and decode JSON into engine fields. `loadLog` additionally sets `ThisRunStartIdx` to the pre-existing log length so later diagnostics can isolate the current run.

Persistence behavior depends on stable JSON encodings of `Log`, `Stats`, and `Checker.SnapIDIndex`. Integration points are `snapmeta.KopiaPersisterLight`, legacy `KopiaPersister`, and engine shutdown/init. Risks include corrupt JSON preventing startup, schema drift across test binary versions, and silent first-run behavior when metadata is missing. Test signals come from robustness tests that resume prior state and from snapmeta persister tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/stats.go -->
# sources/sync-backup/kopia/tests/robustness/engine/stats.go

This file tracks aggregate robustness engine counters and per-action runtime/error statistics. `Stats` stores start/end timestamps, total action counts, completed/error counts, and a map from `ActionKey` to `ActionStats`; `ActionStats` records count, total runtime, and error count. `Engine.Stats` combines current-run and cumulative statistics into a string for logs.

Important methods include `Stats.Stats`, `ActionStats.AverageRuntime`, `ActionStats.Record`, `statsUpdateCounters`, `statsIncrActionCountAndLog`, and `statsUpdatePerAction`. Control flow increments global counters when actions start and complete, logs progress every `statsLogFrequency`, records runtime from start timestamps, and updates cumulative state that `metadata.go` persists.

The state model separates current run stats from cumulative stats, using `clock.Now` for testable time. Dependencies are the engine action model and metadata persistence. Risks include divide-by-zero protection depending on count checks, log noise in long randomized tests, and inconsistent stats if an action entry is started but never completed due to process death. Signals are indirect through robustness logs and persisted stats restoration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/errors.go -->
# sources/sync-backup/kopia/tests/robustness/errors.go

This file centralizes sentinel errors used across the robustness framework. The sentinels distinguish expected test-control conditions (`ErrNoOp`, `ErrKeyNotFound`, `ErrInvalidOption`, `ErrCannotPerformIO`) from hard failures.

The key integration behavior is `errors.Is` matching. FIO file writers convert missing directories into `ErrNoOp`, metadata loaders treat `ErrKeyNotFound` as first-run absence, and tests intentionally mask `ErrNoOp` for delete/restore actions that cannot currently do useful work.

There is no persistence or internal control flow beyond error creation. Risks are semantic: wrapping code must preserve these sentinels, and adding new expected-action errors without using these sentinels can make randomized tests flaky. Test signals are scattered through robustness and multiclient tests that explicitly call `errors.Is` on these values.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/filewriter.go -->
# sources/sync-backup/kopia/tests/robustness/filewriter.go

This file defines the `robustness.FileWriter` interface used by the engine to mutate a source data tree. The interface exposes `DataDirectory`, `WriteRandomFiles`, `DeleteRandomSubdirectory`, `DeleteDirectoryContents`, and `DeleteEverything`, all context-aware where engine actions need cancellation/logging propagation.

Control flow is implemented by concrete adapters such as `fiofilewriter.FileWriter` and multiclient wrappers. Returned option maps are important because the engine logs effective randomized choices, enabling reproduction and audit of actions.

There is no state here, but the contract defines stateful behavior for file-system mutation. Risks are interface semantic drift: implementers must translate "no useful mutation" to `ErrNoOp`, must avoid deleting outside their data root, and must return meaningful effective options. Test signals come from FIO workload tests and robustness engine action tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/filewriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/fiofilewriter/fio_filewriter.go -->
# sources/sync-backup/kopia/tests/robustness/fiofilewriter/fio_filewriter.go

This file implements `robustness.FileWriter` using `tests/tools/fio.Runner`. It defines option keys for directory depth, file sizes, file counts, dedupe percentage, delete percentage, free-space limits, and per-action I/O limits, plus defaults for randomized robustness workloads.

`New` constructs a FIO runner. `WriteRandomFiles` chooses a random depth, file-size range, file count, dedupe percentage, and optional I/O limit, checks free space with `syscall.Statfs`, builds `fio.Options`, logs effective parameters, and delegates to `WriteFilesAtDepthRandomBranch`. Delete methods choose depths and delegate to `DeleteDirAtDepth` or `DeleteContentsAtDepth`, translating `fio.ErrNoDirFound` into `robustness.ErrNoOp`; `DeleteEverything` performs a 100% root-content delete.

State lives in the embedded runner and its temp data directory. Dependencies are FIO, Docker/local FIO environment variables, `maps`, `math/rand`, and robustness sentinels. Risks include invalid option ranges causing `rand.Intn` panics, integer narrowing for large sizes, platform-specific `Statfs`, and destructive deletes if runner roots are wrong. Tests exercise the lower FIO workload layer; robustness tests validate integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/fiofilewriter/fio_filewriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/client.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/client.go

This file creates lightweight client identities for multiclient robustness tests. `Client` contains a UUID-backed `ID` and a petname `Name`; context helpers attach a client to a `context.Context` under an unexported key.

The important APIs are `newClient`, `NewClientContext`, `NewClientContexts`, and `UnwrapContext`. Control flow is simple: tests create one or more client contexts, then multiclient file writers and snapshotters use `UnwrapContext` to select or lazily create per-client resources.

State is carried through context values rather than globals. Dependencies are `github.com/google/uuid` and `golang-petname`. Risks include nil clients when callers forget to wrap contexts, and context values being invisible to unrelated contexts. Test signals appear in multiclient harness `RunN` and snapshotter/filewriter wrappers that return `ErrKeyNotFound` on missing clients.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/filewriter.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/filewriter.go

This file multiplexes `robustness.FileWriter` instances by multiclient context. `MultiClientFileWriter` owns a map from client ID to concrete file writer, guarded by an `RWMutex`, and a factory `newFileWriterFn`.

The wrapper methods implement the `FileWriter` interface by calling `createOrGetFileWriter` and delegating `DataDirectory`, write, delete, and cleanup operations. If a context lacks a client, it logs and returns `robustness.ErrKeyNotFound`. Cleanup iterates all client writers, calls their cleanup hooks, and removes map entries.

State persists only for the test process lifetime: one FIO data root per client. Integration points are the multiclient harness and FIO writer. Risks include lazy-creation races: lookup happens under `RLock`, creation happens outside the write lock, so concurrent first use of the same client can duplicate work before the final map write. Tests cover behavior indirectly through concurrent multiclient robustness tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/filewriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/framework.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/framework.go

This file defines interfaces that decouple the multiclient framework from concrete Kopia and FIO implementations. `ClientSnapshotter` embeds `robustness.Snapshotter` and adds server-client lifecycle operations such as `ConnectClient`, `DisconnectClient`, and `ServerFingerprint`. `Server` adds repository/server control functions, and `FileWriter` embeds `robustness.FileWriter` with cleanup.

There is no executable control flow; the file establishes contracts consumed by `snapshotter.go`, `filewriter.go`, and `harness.go`. The interfaces allow `snapmeta.KopiaSnapshotter` to serve both server and client roles while allowing the harness to supply factories.

Risks are interface breadth and argument ordering: wrappers rely on exact semantics for server address, fingerprint, and user IDs. Test signals are multiclient integration tests that exercise server startup, client authorization, snapshot actions, GC, and cleanup through these interfaces.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/framework.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/harness.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/harness.go

This file assembles the multiclient robustness test harness. `TestHarness` owns repository paths, a temp base directory, multiclient FIO writer, multiclient Kopia snapshotter/server, lightweight metadata persister, and `engine.Engine`. `RepoPathPrefix` controls where shared test repositories live.

Initialization is a linear state machine in `init`: require `repo-path-prefix`, force `ENGINE_MODE=server`, create base dir, require FIO configuration, create snapshotter/server, connect/create the data repo, set cache limits, create metadata persister, connect/create metadata repo, and initialize the engine with repository sync enabled. `Run` and `RunN` run client contexts as parallel subtests and optionally clean up clients. `Cleanup` shuts down the engine, persister, server process, clients, file writers, and temp directory. `GetDirsToLog` collects repo/cache/data paths for storage reporting.

State is both process-local and persisted in shared Kopia repositories. Dependencies include `content.CachingOptions`, FIO/Kopia env vars, `snapmeta`, and `kopiarunner`. Risks include `os.Exit` in setup making failures abrupt, server SIGTERM cleanup races, tiny metadata cache values in bytes, and incomplete cache path collection if `cache info` fails. Signals are all multiclient tests and storage stats logging.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/harness.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/snapshotter.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/snapshotter.go

This file provides `MultiClientSnapshotter`, a `robustness.Snapshotter` implementation that starts one server repository and lazily creates per-client snapshotters. It stores a server adapter, client map, base dir, and client factory.

`ConnectOrCreateRepo` connects/creates the server repository and sets a global keep-latest policy plus compression. Snapshot, restore, compare, delete, and list operations call `createOrGetSnapshotter` to delegate by client context. `RunGC` intentionally runs on the server. `Cleanup` and `CleanupClient` disconnect clients, remove users from the server, clean client resources, and clean server resources. `createOrGetSnapshotter` authorizes the client, connects it with the server fingerprint, and registers it.

State includes long-lived server command, server fingerprint, per-client config dirs, and authorized users. Dependencies are `snapmeta.KopiaSnapshotter`, context client identities, and Kopia server ACL/user behavior. Risks include duplicate lazy creation under concurrent first use, leaked client temp dirs if authorization/connect fails after creation, and server user removal errors only being logged. Integration is central to multiclient tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/main_test.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/main_test.go

This file is the multiclient test package entry point. `TestMain` parses flags, creates a root client context, initializes a global `TestHarness`, exposes `eng` and `th` for individual tests, runs the suite, logs storage stats before and after cleanup, and exits with the test result.

Control flow ensures harness cleanup runs after `m.Run`, while storage stats are attempted around the lifecycle using `storagestats.LogStorageStats`. The global variables intentionally simplify test functions but couple all tests to one shared harness and repository state.

State persists across tests via shared data and metadata repositories under `repo-path-prefix`. Dependencies are the multiclient framework, robustness engine, and storage stats. Risks include global test order coupling, cleanup errors causing exit status 2, and stats logging failures being fatal around otherwise useful test results. Signals are the multiclient robustness test functions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/multiclient_test.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/multiclient_test.go

This file defines concurrent robustness scenarios against a shared Kopia server. Tests cover many small files, one large file, a broad directory tree, randomized small actions, direct maintenance/GC, and delete-random-snapshot behavior. Each scenario builds FIO options and calls `th.RunN` with client contexts.

Control flow for each client usually restores an existing snapshot into its data directory, performs deletes that tolerate `ErrNoOp`, writes files, snapshots, and restores/compares. `TestRandomizedSmall` loops until `rand-test-duration`, weighting actions through `engine.ActionOpts`. Helper functions mask expected `ErrNoOp` for restore/delete/random actions while asserting hard failures.

State is intentionally shared through the global engine, server repository, metadata repository, and per-client data dirs. Dependencies are `engine.ActionKey`, `fiofilewriter` option fields, `testlogging`, and `timetrack`. Risks include long runtimes, shared global engine concurrency assumptions, randomized non-reproducibility, and maintenance running directly against a repository with active server clients. Signals are the tests themselves.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/multiclient_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/storagestats/storage_stats.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/storagestats/storage_stats.go

This file logs disk usage snapshots for directories created by the multiclient framework. `DirectorySize` records a path and byte count; `LogStorageStats` collects sizes, JSON-encodes them, and writes a timestamped log file under a package-level path.

`collectDirectorySizes` iterates configured directories, `getSize` recursively walks each directory with `filepath.WalkDir` and sums non-directory sizes, and `getLogFilePath` lazily creates one shared log path in the current working directory. The client ID from the context is included in the filename.

State is the package-global `logFilePath`, so repeated calls overwrite the same file rather than creating before/after files. Dependencies are multiclient context identities and OS filesystem walking. Risks include a race on `logFilePath`, large repo walks slowing test setup/teardown, and failure on transient deleted paths. Test signals are manual/log artifacts rather than assertions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/storagestats/storage_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/options.go -->
# sources/sync-backup/kopia/tests/robustness/options.go

This file provides `GetOptAsIntOrDefault`, a small helper for parsing integer option maps used by engine actions and file writers. It returns the default for nil maps, missing keys, or parse failures.

Control flow is intentionally forgiving: callers do not receive parse errors, so invalid option values silently fall back to defaults. The helper is heavily integrated with `fiofilewriter` and robustness test option construction.

There is no state or persistence. Risk is hidden configuration mistakes, especially in randomized tests where default values can make an intended bounded action much larger. Test signals are indirect through option-driven robustness tests; no dedicated unit test is present in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/pathlock/path_lock.go -->
# sources/sync-backup/kopia/tests/robustness/pathlock/path_lock.go

This file implements path-scoped mutual exclusion for FIO filesystem operations. `Locker` returns an `Unlocker`; `pathLock` maintains a map from cleaned paths to lock channels plus a mutex. It rejects overlapping locks so a parent and child path cannot be modified concurrently.

`Lock` cleans paths and spins until `tryToLockPath` succeeds, incrementing `busyCounter` for test observability. `tryToLockPath` checks every currently locked path with `isInPath` in both directions, then creates a channel marker. `Unlock` closes/removes the channel. `isInPath` uses `filepath.Rel` and rejects paths that start with `..`.

State is process-local and synchronized by `sync.Mutex`; `busyCounter` is atomic for tests. Dependencies are filepath normalization and string prefix checks. Risks include busy waiting without context cancellation, path comparison edge cases with symlinks/case-insensitive filesystems, and panic potential from double unlock avoided only by ownership discipline. Tests cover basic, nonblocking, and race behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/pathlock/path_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/pathlock/path_lock_test.go -->
# sources/sync-backup/kopia/tests/robustness/pathlock/path_lock_test.go

This file validates the path-lock implementation. `TestPathLockBasic` checks same-path blocking, parent/child exclusion, sibling independence, and cleanup after unlock. `TestPathLockWithoutBlock` uses goroutines and `busyCounter` to verify locks do not spin when they should not conflict. `TestPathLockRace` runs randomized concurrent lock/unlock operations.

The tests exercise state transitions in the lock map, unlock behavior, and atomic busy instrumentation. They depend on `os.Getwd`, temporary path construction, `sync.WaitGroup`, and timed goroutine coordination.

Risks tested include deadlock, false conflicts, false non-conflicts, and data races. Residual risk remains around platform-specific path semantics and symlink resolution because tests use lexical paths. These tests are direct signals for concurrency safety in FIO workload mutation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/pathlock/path_lock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/persister.go -->
# sources/sync-backup/kopia/tests/robustness/persister.go

This file defines persistence contracts for robustness metadata. `Store` provides key/value `Store`, `Load`, and `Delete` methods. `Persister` embeds `Store` and adds repository lifecycle methods `LoadMetadata`, `FlushMetadata`, `GetPersistDir`, and `Cleanup`.

The engine uses the key/value operations for log, stats, and snapshot index metadata. Legacy implementations also use load/flush lifecycle methods to snapshot a whole metadata file; the lightweight persister makes those lifecycle hooks no-ops because it stores each key as a Kopia snapshot.

There is no internal state here. Risks are contract ambiguity between key/value persistence and whole-metadata persistence; implementations must define `ErrKeyNotFound` semantics consistently. Test signals are snapmeta persister tests and robustness engine init/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/persister.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/robustness_test/main_test.go -->
# sources/sync-backup/kopia/tests/robustness/robustness_test/main_test.go

This file is the single-client robustness test harness and `TestMain`. It builds data and metadata repository paths from `repo-path-prefix`, creates FIO writer, Kopia snapshotter, lightweight persister, engine, and an upgrader, restores a previous snapshot into the data directory, optionally upgrades repository format, runs tests, then cleans up.

Initialization is a linear set of boolean steps with skip behavior for missing FIO or `KOPIA_EXE`. `cleanup` shuts down engine metadata, clears upgrade env state, terminates a server command if present, removes temp directories, and cleans FIO/Kopia resources. Upgrade flow reads repository status JSON, runs `repository upgrade begin`, and logs previous/current content format versions.

State persists in shared repositories and in engine metadata; global `eng` is used by test functions. Dependencies are `snapmeta`, `fiofilewriter`, `kopiarunner`, and OS env flags. Risks include abrupt `os.Exit`, global state across tests, cleanup error masking except final check, and repository upgrade side effects. Signals are the single-client robustness tests and upgrade-specific test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/robustness_test/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/robustness_test/robustness_test.go -->
# sources/sync-backup/kopia/tests/robustness/robustness_test/robustness_test.go

This file defines single-client robustness scenarios. It mirrors the multiclient workloads at lower concurrency: many small files, one large file, directory-tree writes, and randomized small actions.

Each test creates FIO options, executes engine actions, tolerates expected `robustness.ErrNoOp` for deletes/restores where appropriate, and asserts snapshot/restore success. The randomized test builds weighted `engine.ActionOpts` and loops until `randomizedTestDur`.

State and persistence are provided by the global engine from `main_test.go`, which persists logs, stats, and snapshot metadata between runs. Dependencies are `engine`, `fiofilewriter`, `require`, and test logging. Risks include random long-running behavior, hidden option parse fallbacks, and coupling to previous repository contents. Test signals directly validate end-to-end backup/restore consistency under mutations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/robustness_test/robustness_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/index.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/index.go

This file defines `Index`, a map from index name to a set of keys. It supports `AddToIndex`, `RemoveFromIndex`, `GetKeys`, and `IsKeyInIndex`.

The structure is used by simple snapshot metadata stores to associate snapshot IDs or metadata keys with logical indexes. Control flow is straightforward set mutation: initialize a nested map on first add, delete keys from an index, return keys as an unordered slice, and check membership.

State is in-memory and JSON-serializable through map types when embedded in persisted metadata. Risks include nondeterministic key order from `GetKeys`, nil map panic if methods are called on a nil `Index` without initialization, and no automatic cleanup of empty index maps. Direct unit tests cover add/remove/get/membership behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/index_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/index_test.go

This file unit-tests the `Index` helper. `TestIndex` validates adding keys to indexes, checking membership, retrieving keys, and removing entries.

The test provides direct signals for the in-memory index set semantics used by snapshot metadata stores. It depends on `testify/require` and does not involve filesystem or Kopia state.

Residual risks not covered include concurrent access, JSON round-trip behavior when embedded in larger metadata, nil receiver/map initialization behavior, and deterministic ordering. The test is still a useful narrow guard for basic index correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector.go

This file holds shared Kopia CLI connection logic for snapshotter and legacy persister adapters. `kopiaConnector` stores a `kopiarunner.KopiaSnapshotter`, server command, server address, server fingerprint, and function hooks for repository initialization modes.

Initialization chooses behavior from env such as engine mode and S3 bucket settings. It can connect/create filesystem or S3 repositories, optionally through a Kopia server. Client/server helpers authorize clients and connect clients using fingerprints. Function fields let persisters override server initialization when they do not support server mode.

State includes process-local Kopia config directories, server process handles, and repository connection details. Dependencies are `kopiarunner`, `os/exec`, and env-driven mode selection. Risks include env misconfiguration, argument order mistakes for filesystem-with-server paths, server lifecycle leaks, and hidden coupling to default host/user constants. Tests use a stub connector to validate mode dispatch.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector_test.go

This file tests `kopiaConnector` mode dispatch with a `testConnector` stub. It configures connector function hooks, changes environment-like mode inputs, and verifies the expected filesystem/S3/server initialization path is called.

The control-flow signal is important because real connector methods launch Kopia commands and servers. The stub records which method was invoked, allowing tests to check dispatch without external binaries.

Risks covered are wrong mode routing and missing hook use. Risks not covered are actual Kopia command success, TLS fingerprint handling, server startup timing, and environment cleanup. Dependencies are `testify/require` and package-internal connector fields.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_connector_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister.go

This file implements the legacy whole-metadata `robustness.Persister` on top of Kopia snapshots. `KopiaPersister` embeds `Simple`, owns local metadata and persistence dirs, and reuses `kopiaConnector`.

`NewPersister` creates temp dirs, initializes the connector, and overrides server init hooks because this persister does not support server mode. `LoadMetadata` lists snapshots, restores the latest into the persistence dir, opens `metadata-store-latest`, and JSON-decodes it into `Simple`. `FlushMetadata` JSON-encodes `Simple` into that file and snapshots the persistence dir. Repo connection methods delegate to the connector/snapshotter.

State is both in-memory `Simple` metadata and the latest metadata snapshot in the metadata repository. Risks include relying on list order for latest snapshot, stale files in the persistence dir, temp file cleanup with ignored errors, and larger metadata snapshots than the key/value light persister. Tests are mostly legacy/integration; current harnesses prefer `KopiaPersisterLight`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light.go

This file implements a lighter key/value `robustness.Persister` using the in-process `tests/tools/kopiaclient.KopiaClient`. `KopiaPersisterLight` owns a Kopia client, a per-key in-process lock map, a condition variable, and a local base directory.

`ConnectOrCreateRepo` and `SetCacheLimits` use filesystem or S3 storage depending on `S3BucketNameEnvKey`. `Store`, `Load`, and `Delete` serialize access per key with `waitFor`/`doneWith`, then call `SnapshotCreate`, `SnapshotRestore`, or `SnapshotDelete`. Whole-metadata lifecycle methods are no-ops; `GetPersistDir` returns the temp persistence root and `Cleanup` removes it.

State persists as one or more Kopia snapshot manifests per metadata key. The condition variable prevents concurrent writes/deletes/loads for the same key but allows different keys concurrently. Risks include no context cancellation while waiting, `Signal` waking only one waiter, cleanup not closing a repo handle because handles are opened per operation, and S3 env reliance. Tests cover light persister behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light_test.go

This file tests the lightweight Kopia metadata persister. The tests create temp repositories, store/load/delete metadata keys, verify missing keys produce expected errors, and exercise repeated updates through Kopia snapshots.

The control-flow signal validates that the in-process Kopia client can initialize/connect, snapshot virtual files, restore latest values, and delete manifests for a key. It also indirectly validates per-key locking by using the public store/load/delete API, though not as a stress test.

Risks not fully covered include heavy concurrent same-key access, S3 storage, cache limit behavior, and process crash between metadata operations. Dependencies are `require`, temp filesystem storage, and robustness sentinel errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter.go

This file implements `robustness.Snapshotter` using Kopia CLI commands plus `fswalker` comparison. `KopiaSnapshotter` embeds `kopiaConnector` and owns a `WalkCompare` for data fingerprints.

`ConnectOrCreateRepo` connects/creates a repo and sets a permissive retention policy plus compression. Snapshot creation first gathers an fswalker fingerprint, runs `kopia snapshot create`, records timing stats, and returns snapshot ID plus fingerprint. Restore methods run `snapshot restore` and either gather a new fingerprint or compare against saved fingerprint data. Delete, GC, list, arbitrary `Run`, client authorization, server fingerprint, and cleanup delegate to the Kopia runner/connector. Upgrade helpers read repository status JSON and run repository format upgrade with env gating.

State includes Kopia config, server process/fingerprint, and no long-lived fswalker data beyond returned blobs. Dependencies are CLI JSON shape, `clock`, `fswalker`, and robustness stats types. Risks include CLI output parsing, restore target overwrite behavior, upgrade side effects, and filters hiding real metadata drift. Tests cover connector/snapshotter upgrade paths and end-to-end robustness.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter_upgrade_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter_upgrade_test.go

This file tests or gates the Kopia snapshotter repository-upgrade path. It exercises repository status retrieval and upgrade behavior under the robustness snapshotter wrapper, typically controlled by environment because upgrades are integration-heavy.

The main control-flow signal is that `KopiaSnapshotter.GetRepositoryStatus` can parse `repository status --json` and `UpgradeRepository` can execute the CLI upgrade command while setting and clearing `KOPIA_UPGRADE_LOCK_ENABLED`.

Risks include tests being skipped when `KOPIA_EXE` or upgrade env is absent, and real repository format changes being destructive or non-repeatable. Integration is with the single-client harness `TestMain`, which also contains upgrade logic.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter_upgrade_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/simple.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/simple.go

This file implements an in-memory metadata store. `Simple` stores key/value byte slices and an `Index`. It satisfies the robustness store behavior for tests and for the legacy Kopia persister before flushing whole metadata.

The important methods are constructor `NewSimple`, `Store`, `Load`, `Delete`, and index helper forwarding methods. `Load` returns `robustness.ErrKeyNotFound` for absent keys; `Store` copies or assigns values into the map; `Delete` removes keys.

State is JSON-serializable in-memory metadata. Risks include lack of synchronization for concurrent access, byte-slice aliasing depending on implementation details, and index consistency being caller-managed rather than automatic. Direct tests validate basic store/index behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/simple.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/simple_test.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/simple_test.go

This file tests `Simple` metadata storage. It validates storing and loading byte values, deleting keys, missing-key behavior, and index helper interaction.

The test is a direct signal for the legacy persister's in-memory state before JSON flush and restore. It depends on `testify/require` and robustness error sentinels.

Residual risks include concurrent access, JSON round trips through `KopiaPersister`, and mutation of returned byte slices. The test nevertheless protects the basic contract used by engine metadata save/load.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/simple_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapshotter.go -->
# sources/sync-backup/kopia/tests/robustness/snapshotter.go

This file defines the `robustness.Snapshotter` interface and snapshot creation stats. The interface covers repository connection, snapshot create/restore/restore-and-compare, delete, GC, list, arbitrary command execution, and cleanup as needed by the engine.

`CreateSnapshotStats` records snapshot start and end times. The engine uses these values for per-action logging/stats. Implementations include `snapmeta.KopiaSnapshotter` and `MultiClientSnapshotter`.

There is no state here, but this contract is the main integration point between engine actions and Kopia repositories. Risks are broad interface responsibilities, inconsistent implementation of no-op/errors, and optional methods like `Run`/`Cleanup` tying tests to Kopia-specific behavior. Test signals are full robustness and multiclient suites.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/socketactivation_test/server_wrap.sh -->
# sources/sync-backup/kopia/tests/socketactivation_test/server_wrap.sh

This tiny shell wrapper prepares environment for socket activation tests. It forwards to the Kopia server executable while setting activation-related variables such as `LISTEN_PID` as expected by systemd-style socket activation.

Control flow is a direct exec-style wrapper around server startup. Its integration point is `socketactivation_test.go`, which passes listener file descriptors through `CLIExeRunner.ExtraFiles` and relies on the wrapper to make those descriptors visible to the server process.

Risks are shell portability, argument forwarding, and environment correctness. Test signals are the socket activation integration tests that require `KOPIA_SERVER_EXE`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/socketactivation_test/server_wrap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/socketactivation_test/socketactivation_test.go -->
# sources/sync-backup/kopia/tests/socketactivation_test/socketactivation_test.go

This file tests Kopia server control socket activation. `TestServerControlSocketActivated` creates a repository and snapshot, opens a TCP listener on an ephemeral port, passes its file descriptor to the server process with `LISTEN_FDS=1`, waits for server stderr parsing to discover the base URL/control password, verifies status over the activated port, and shuts the server down.

`TestServerControlSocketActivatedTooManyFDs` passes two descriptors, expects server startup failure, and asynchronously scans stderr for the expected "too many activated sockets" message to avoid deadlock.

State includes external server process, listener file descriptors, and test CLI config. Dependencies are `KOPIA_SERVER_EXE`, `testenv.CLIExeRunner`, `testutil.ServerParameters`, and network timing. Risks include FD leaks, timing flakes around startup/shutdown, platform-specific activation semantics, and async stderr races. Tests are skipped when the server executable is absent.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/socketactivation_test/socketactivation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/stress_test/stress_test.go -->
# sources/sync-backup/kopia/tests/stress_test/stress_test.go

This file stress-tests Kopia content write/read behavior under concurrent managers. `TestStressBlockManager` is gated by `KOPIA_STRESS_TEST` and short mode, creates in-memory blob storage, configures content format options, and runs workers for 3 seconds locally or 30 seconds in CI.

`stressTestWithStorage` starts 16 parallel subtests. Each `stressWorker` repeatedly writes random byte slices, occasionally flushes or closes/reopens its manager, and verifies previously written content by content ID. The worker keeps a small rolling set of blocks to read back.

State is in-memory blob storage shared across workers plus per-worker write managers and random seeds. Dependencies include content manager internals, `blobtesting`, `format`, `encryption`, and `gather`. Risks include nondeterministic failure reproduction, hidden races only surfacing under stress, and runtime scaling in CI. Test signal is explicit but opt-in.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/stress_test/stress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testdirtree/testdirtree.go -->
# sources/sync-backup/kopia/tests/testdirtree/testdirtree.go

This file provides utilities for creating randomized directory trees for tests. It supports random hex or Unicode names, nested directories, random file contents, symlinks, configurable depth/count/size/name options, and counters for created objects and bytes.

Important APIs are `DirectoryTreeOptions`, `MaybeSimplifyFilesystem`, `DirectoryTreeCounters`, `MustCreateDirectoryTree`, `CreateDirectoryTree`, `MustCreateRandomFile`, and `CreateRandomFile`. Control flow recursively creates directories, then random files, then symlinks. File contents are generated from a `math/rand` source seeded with `clock.Now`.

State is filesystem output plus an atomic global name counter for uniqueness. Dependencies are Unicode normalization, platform complexity helpers, and test utilities. Risks include nondeterminism, symlink behavior on restricted platforms, ARM complexity reduction containing a likely assignment typo for `MaxSubdirsPerDirectory`, and cryptographic random errors ignored in name generation. Tests using this helper validate snapshot/restore edge cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testdirtree/testdirtree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_exe_runner.go -->
# sources/sync-backup/kopia/tests/testenv/cli_exe_runner.go

This file implements `CLIRunner` by launching an external Kopia executable. `CLIExeRunner` stores executable path, optional passthrough/debug fields, next stdin, extra file descriptors for socket activation, and log directory.

`Start` builds `exec.CommandContext` with `--log-dir`, merges environment variables, wires stdout/stderr pipes, optional stdin and `ExtraFiles`, starts the process, and returns readers plus wait/interrupt functions. Constructors resolve `KOPIA_EXE`, optionally use `kopia` under VS Code, unset `KOPIA_PASSWORD`, and create a temp log directory.

State is per-run process state and mutable `NextCommandStdin`/`ExtraFiles`. Dependencies are OS process APIs and test utilities. Risks include `ExtraFiles` persisting across starts unless caller clears it, process kill/signal errors ignored, and env leakage from `os.Environ`. Test signals include CLI integration and socket activation tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_exe_runner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_inproc_runner.go -->
# sources/sync-backup/kopia/tests/testenv/cli_inproc_runner.go

This file implements `CLIRunner` by invoking Kopia CLI subcommands in-process. `CLIInProcRunner` stores guarded next stdin and an optional `CustomizeApp` hook.

`Start` creates a new CLI app, enables dangerous commands, assigns a unique env prefix, applies customization, transfers one-shot stdin under a mutex, writes prefixed env vars, and calls `RunSubcommand`. `SetNextStdin` sets the next stdin. `NewInProcRunner` skips when external integration tests are preferred and registers an in-memory storage provider.

State is mostly per-command app state plus process environment variables with unique prefixes. Dependencies include kingpin and Kopia CLI internals. Risks include process-global env accumulation, in-process command side effects leaking between tests, and limited fidelity versus real process execution. Tests use it for faster CLI coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_inproc_runner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_test_env.go -->
# sources/sync-backup/kopia/tests/testenv/cli_test_env.go

This file defines `CLITest`, the high-level test environment for Kopia CLI tests. It owns a run context, temp repo/config directories, runner, fixed args, environment map, default repo-create flags, and log-output controls.

Core APIs run commands and assert outcomes: `RunAndExpectSuccess`, `RunAndExpectFailure`, `RunAndExpectSuccessWithErrOut`, `RunAndVerifyOutputLineCount`, `RunAndProcessStderr`, and async stderr variants. `Run` builds final args, starts the configured runner, concurrently reads stdout/stderr, waits, asserts expected success/failure, and returns lines. It also provides `TweakFile`, `SetLogOutput`, and `NotificationsSent`.

State includes per-test config/repo dirs and process env overrides such as `KOPIA_PASSWORD`. Dependencies are `testlogging`, `testutil`, notification capture, and runner implementations. Risks include scanner token limits for huge output, goroutine ordering around stderr processing, random file corruption on empty files, and broad logging of environment values. This file is a core integration-test utility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_test_env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/faketimeserver.go -->
# sources/sync-backup/kopia/tests/testenv/faketimeserver.go

This file implements a small HTTP handler that returns fake time information as JSON. `FakeTimeServer` wraps a `Now` function; `ServeHTTP` encodes the current fake time and a two-second validity duration.

The integration point is tests that need Kopia instances to synchronize to controllable time signals. `NewFakeTimeServer` constructs the handler, and the type satisfies `http.Handler`.

State is delegated to the provided `Now` callback. Risks include ignored JSON encode errors, no method/path validation, and tests needing to keep the callback concurrency-safe. Test signals come from time-dependent integration tests outside this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/faketimeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/storage_inmemory.go -->
# sources/sync-backup/kopia/tests/testenv/storage_inmemory.go

This file registers in-memory storage flags for in-process CLI tests. `storageInMemoryFlags` stores `repotesting.ReconnectableStorageOptions`, adds a required `--uuid` flag, and creates a reconnectable in-memory blob storage from those options.

Control flow is invoked through the custom storage provider installed by `NewInProcRunner`. On connect, it returns `blob.NewStorage` with `repotesting.ReconnectableStorageType` and the create/connect mode.

State is externalized in the reconnectable storage registry keyed by UUID. Dependencies are Kopia CLI storage provider APIs and blob testing support. Risks include UUID reuse causing unintended shared storage and in-memory-only behavior diverging from real backends. Test signal is in-process CLI repository creation/use.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/storage_inmemory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testingaction/main.go -->
# sources/sync-backup/kopia/tests/testingaction/main.go

This file implements a small command used by tests to simulate external actions. It parses flags for output files, delays, copied file specs, and input/output behavior, then writes/copies data accordingly.

Important functions are `main`, `writeFileTo`, `copyFiles`, and `copyFile`. Control flow can sleep, copy files described by a spec file, write named files to stdout/stderr, and copy byte streams. It uses scanner/line parsing for specs.

State is filesystem side effects and process stdout/stderr. Dependencies are standard I/O and flags only. Risks include broad file path access from spec input, scanner limits for long spec lines, and test hangs if delay values are large. Test signals are indirect from command/action integration tests that invoke this helper binary.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testingaction/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/config.go -->
# sources/sync-backup/kopia/tests/tools/fio/config.go

This file defines `Config` as a slice of FIO `Job` values and provides `Config.String` for rendering a human-readable fio-style configuration. It joins each job string with blank lines.

The string method is primarily diagnostic; actual runner execution converts configs directly to CLI arguments in `fio.go`. It integrates with debug logging when `Runner.Debug` is enabled.

There is no state. Risks are low, limited to formatting expectations in tests or logs. Unit tests for FIO config/run behavior validate the rendered structure indirectly and directly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/fio.go -->
# sources/sync-backup/kopia/tests/tools/fio/fio.go

This file wraps execution of FIO either as a local executable or Docker image. `Runner` stores executable details, data directories, global FIO config, debug flag, and a path locker. Environment keys select local FIO, Docker image, local data root, and host data root.

`NewRunner` creates a temp data dir, chooses local or Docker execution, builds global write options, initializes a no-op path locker, and validates setup by writing test files. `verifySetupWithTestWrites` writes a small random test workload and verifies count/size. `RunConfigs` and `argsFromConfigs` translate config/jobs/options to FIO CLI args. `Run` executes the command and captures stdout/stderr. `Cleanup` removes the local data dir.

State includes temp filesystem data and Docker volume mapping. Dependencies are FIO/Docker availability and `pathlock`. Risks include environment-driven skip/failure, local/container path mismatches, no command timeout, direct I/O assumptions, and validation doing real writes. Tests cover local/docker runner paths when env is configured.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/fio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/fio_test.go -->
# sources/sync-backup/kopia/tests/tools/fio/fio_test.go

This file tests FIO runner execution and config translation. It creates runners, runs direct args and config-based jobs, checks global config override behavior, and includes Docker-runner coverage when configured.

Control flow depends heavily on `TestMain` gating via FIO env vars. Tests verify that FIO writes produce expected files and that option overrides produce expected command behavior.

Risks covered include bad executable/image setup, config-to-args translation errors, and Docker volume mapping. Residual risks include platform-specific FIO engines and large robustness workload behavior. These tests are important prerequisites for robustness file writing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/fio_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/job.go -->
# sources/sync-backup/kopia/tests/tools/fio/job.go

This file defines a single FIO job. `Job` has a `Name` and `Options`; `Job.String` renders a fio config section with `[name]` followed by option lines.

The type is used inside `Config` for debug/log formatting and by `Runner.argsFromConfigs` to produce CLI flags. Option ordering is map-based, so string output order is nondeterministic unless tests account for it.

There is no state. Risks are formatting nondeterminism and divergence between string representation and CLI argument generation. FIO tests provide signals around job/config output and execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/main_test.go -->
# sources/sync-backup/kopia/tests/tools/fio/main_test.go

This file controls FIO test execution. `TestMain` checks `FIO_EXE` and `FIO_DOCKER_IMAGE` environment variables and exits/skips behavior appropriately for tests that require external FIO capability.

The integration purpose is to avoid failing normal test runs when FIO is unavailable, while enabling real I/O tests in configured environments.

State is only process environment. Risks include accidentally skipping coverage in CI if env is absent, or running destructive/heavy I/O tests when env points to an unexpected executable/image. Signals are all tests in the `fio` package.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/options.go -->
# sources/sync-backup/kopia/tests/tools/fio/options.go

This file defines FIO option builders. `Options` is a string map with `Merge` plus fluent methods for size, size ranges, I/O limits, file counts, file-size ranges, dedupe percentage, block size, fallocate mode, randrepeat, and directory.

Control flow is immutable-style: each builder returns a merged map, preserving the original input. `rangeOpt` swaps min/max if needed and formats `min-max`; `boolOpt` converts booleans to `1`/`0`.

There is no persistent state. Integration is broad: `fiofilewriter` uses these builders to construct randomized workloads, and `Runner` turns maps into CLI args. Risks include int narrowing from int64 to int, map iteration nondeterminism, and missing validation for unsupported FIO values. Unit tests cover workload/config option behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/workload.go -->
# sources/sync-backup/kopia/tests/tools/fio/workload.go

This file implements filesystem workload operations on top of `Runner`. It writes files at paths/depths, deletes directories, deletes probabilistic contents, traverses random existing directory trees, and creates missing branches as needed.

`WriteFiles` and depth variants lock the relevant path, create directories, translate local paths to FIO container paths, and run FIO configs. Delete methods use path locks and `operateAtDepth`, which recursively chooses shuffled directories until it finds a target or returns `ErrNoDirFound`. `writeFilesAtDepth` uses `branchDepth` to mix existing and newly-created paths. `pickRandSubdirPath` chooses a random child directory.

State is filesystem tree mutation under `Runner.LocalDataDir`; locking prevents conflicting operations when a real locker is installed. Risks include random traversal flakiness, no symlink boundary checks, deletion of root content through `DeleteContentsAtDepth`, and `rand.Intn(depth+1)` panics if callers pass negative depth. Workload tests cover writes/deletes/content deletion.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/workload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/workload_test.go -->
# sources/sync-backup/kopia/tests/tools/fio/workload_test.go

This file tests FIO workload helpers. It verifies writing files, writing at exact depths, deleting directories at depths, and deleting contents with probabilities of none/some/all. Helper functions walk the resulting temp tree to count files/directories and assert expected outcomes.

The tests provide direct signals for the mutation behavior consumed by robustness file writers. They depend on a configured FIO runner and real filesystem effects.

Risks covered include wrong depth traversal, file count mismatch, and delete probability extremes. Residual risks include concurrency with path locks, Docker path mapping under unusual host layouts, and randomized branch choices in long robustness runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fio/workload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/fswalker.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/fswalker.go

This file adapts Google fswalker to the robustness comparer contract. `WalkCompare` has global diff filters that ignore expected restore differences such as times, root directory rename, directory size, and UID/GID changes from zero.

`Gather` walks a path with hashing and returns marshaled protobuf data. `Compare` unmarshals prior walk data, walks the restored path, generates a report, filters modified diffs, validates there are no added/deleted/modified/error entries, and writes summary plus JSON report on failure. Helpers clear hostname, reroot paths relative to the source root, print summaries, and validate reports.

State is serialized walk protobuf bytes and transient reports. Dependencies are `github.com/google/fswalker`, protobuf, reporter/walker wrappers, and filter semantics. Risks include filters hiding real metadata regressions, report JSON being huge, path reroot errors, and hashing size limits in walker policy. Tests cover gather/compare, filters, validation, and rerooting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/fswalker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/fswalker_test.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/fswalker_test.go

This file tests `WalkCompare`. It builds temp directory scenarios for identical data, content changes, deletions, permission/time-like differences, directory/root rename filtering, report validation, and rerooting behavior.

The tests exercise both success paths and failure-report behavior, including custom global filters. They rely on real filesystem mutations and fswalker report structures.

Risks covered include false positives from expected metadata drift and false negatives from invalid reports. Residual risk remains around large files, platform-specific UID/GID/time behavior, and hashing limits. These are key signals for snapshot restore correctness checks in robustness tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/fswalker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/protofile/protofile.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/protofile/protofile.go

This file contains a helper for writing protobuf messages in text format. `WriteTextProto` marshals a `proto.Message` with `prototext.Marshal`, appends a newline if needed, and writes it to a path with mode `0644`.

It is used by the fswalker `walker` and `reporter` wrappers to create temporary policy/config files accepted by the upstream fswalker APIs.

State is only the written temp file. Risks are straightforward: write permissions, non-atomic writes, and caller responsibility for cleanup. Tests for walker/reporter indirectly validate this helper.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/protofile/protofile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter.go

This file wraps fswalker reporter creation and comparison. `Report` writes a temporary report config, loads a reporter from it, and compares two in-memory walk protobufs. `ReportFiles` does the same for serialized walk files. `writeTempConfigFile` writes config textproto through `protofile`.

Control flow is temp-file based because upstream fswalker APIs consume config files. Cleanup uses `defer os.RemoveAll` on temp config paths.

State is transient config files and loaded report structures. Dependencies are `github.com/google/fswalker`, fswalker protobufs, and `protofile`. Risks include temp cleanup errors ignored, config file mode/contents, and upstream reporter behavior changes. Unit tests cover file-based reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter_test.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter_test.go

This file tests the reporter wrapper with walk files. It constructs fswalker protobuf data, writes before/after inputs, invokes `ReportFiles`, and asserts the report detects expected differences.

The test validates temp config generation, textproto writing, reporter loading, walk-file reading, and comparison output. It depends on fswalker protobuf structures and test logging.

Risks not covered include in-memory `Report` path, cleanup failures, and large reports. The test is a targeted signal that the wrapper can interoperate with the upstream fswalker reporter.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/reporter/reporter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/walker/walker.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/walker/walker.go

This file wraps fswalker walking. It defines a maximum file size to hash and provides `Walk` plus `WalkPathHash`.

`Walk` writes a temporary policy textproto, creates an upstream walker from the policy file, installs a callback to capture the produced `Walk`, runs the walker, and returns the captured protobuf. `WalkPathHash` builds a policy for a root path that hashes file contents up to the configured max size.

State is temporary policy files and captured walk data. Dependencies are upstream fswalker and `protofile`. Risks include callback not being called, max hash size hiding changes in very large files, cleanup errors ignored, and policy-file API changes. Walker tests cover success and failure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/walker/walker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/walker/walker_test.go -->
# sources/sync-backup/kopia/tests/tools/fswalker/walker/walker_test.go

This file tests fswalker walker wrapper behavior. `TestWalk` creates a test directory tree, runs a walk policy, and verifies output contains expected files. `TestWalkFail` checks error behavior for invalid policy/path scenarios.

These tests validate temporary policy generation, upstream walker integration, and captured protobuf output. Dependencies include `testdirtree`, fswalker protobufs, and test logging.

Risks covered include basic walker invocation failures. Residual risks include large-file hash cutoffs, symlink edge cases, and platform-specific filesystem metadata differences. The tests support robustness snapshot comparison reliability.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/fswalker/walker/walker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiaclient/kopiaclient.go -->
# sources/sync-backup/kopia/tests/tools/kopiaclient/kopiaclient.go

This file provides an in-process Kopia repository client used by the lightweight metadata persister. `KopiaClient` stores config path and password, and can create/connect, set cache limits, create snapshots from virtual key/value files, restore latest values, and delete all snapshots for a key.

`CreateOrConnectRepo` chooses S3 or filesystem storage, initializes if needed, then connects. `SnapshotCreate` opens the repo, creates a write session, builds source info and policy, uploads a virtual directory containing `data`, saves the snapshot manifest, flushes, and closes. `SnapshotRestore` lists snapshots for a key, picks the latest by start time, opens `root/data`, and reads bytes. `SnapshotDelete` deletes all manifests for the key. Helpers select storage, build virtual sources, source info, and latest manifest.

State persists in Kopia repository manifests/contents. Dependencies are repo/blob/snapshot internals, S3 env credentials, virtualfs, and robustness `ErrKeyNotFound`. Risks include repository handles not closed on early errors, latest selection by timestamp, hardcoded password/endpoint for tests, and deleting all key manifests. Persister-light tests validate integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiaclient/kopiaclient.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter.go

This file wraps Kopia CLI commands for repository, snapshot, server, ACL, and upgrade-related operations. `KopiaSnapshotter` owns a `Runner` and adds higher-level methods for connect/create, S3/filesystem modes, server startup, client authorization, snapshot create/restore/delete/list, GC, and parsing outputs.

Control flow builds CLI args with cache flags, no-update/progress flags, retention/parallel settings, and server control password. `CreateSnapshot` parses the snapshot ID from stdout or stderr. `ListSnapshots` cross-checks `manifest list` against `snapshot list --all`. Server mode generates TLS certs, waits for cert files and server status using retry loops, computes SHA-256 fingerprint, enables ACLs, and grants wildcard snapshot access. Helpers parse manifest IDs, snapshot list IDs, cert PEM, and "ACL already enabled" errors.

State is external Kopia config/repository/server process. Dependencies are `Runner`, `retry`, `crypto/x509`, CLI output formats, and environment. Risks include fragile output parsing, long retry timeouts, temp cert cleanup while server uses files, broad ACLs for tests, and command hangs without context deadlines. Tests cover parsing and executable integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_exe_test.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_exe_test.go

This file integration-tests snapshot listing against a real Kopia executable. It creates a filesystem repo, verifies the initial snapshot list is empty, creates snapshots, and checks both snapshot-list and manifest-list methods return the expected count and include the latest snapshot ID.

The helper `snapIDIsLastInList` checks ordering assumptions. The test is gated by executable availability through runner construction.

Risks covered include CLI output parsing and manifest/snapshot list consistency. Residual risks include server mode, S3 repositories, and different CLI output formats across versions. This is a strong signal for `KopiaSnapshotter.ListSnapshots`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_exe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_test.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_test.go

This file unit-tests snapshot list parsing. `TestSnapListParse` feeds sample `snapshot list --all --manifest-id` output to `parseSnapshotListForSnapshotIDs` and verifies extracted manifest IDs.

The test isolates a fragile parser from the need for an executable. It covers empty input and representative output lines.

Risks not covered include changes in `manifest list` output, localized/altered CLI output, and duplicate or malformed manifest tokens. Integration tests supplement this parser test with real CLI output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun.go

This file implements the low-level external Kopia command runner. `Runner` stores executable path, temp config dir, fixed config-file args, and environment containing the test repository password.

`NewRunner` requires `KOPIA_EXE`, creates a temp config dir under the provided base dir, and returns a runner. `Run` logs command execution, builds args, runs the process with background context, captures stdout and stderr, and returns strings plus error. `RunAsync` starts a background command, captures stderr in a buffer, applies platform-specific parent-death behavior, and returns the command. `Cleanup` removes the config dir.

State is temp config and external process state. Dependencies are OS process APIs and `setpdeath`. Risks include no timeout/cancellation, verbose logs leaking command output, async stderr buffer unbounded until process exit, and required env var causing skip/failure. Tests cover construction and basic run behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun_test.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun_test.go

This file tests the Kopia runner wrapper. It manipulates `KOPIA_EXE`, verifies missing-executable errors, creates runners with temp config, and runs commands expected to succeed or fail.

The tests validate environment gating, temp config setup, fixed arg injection, and error propagation from subprocess execution. They depend on a real Kopia executable when available and skip/branch otherwise.

Risks covered include missing env configuration and basic process failure. Residual risks include async server processes, output parsing, and timeout behavior. Higher-level snapshotter tests cover more command semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopiarun_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath.go

This non-Linux file provides a no-op `setpdeath` implementation for async Kopia commands. It returns the command unchanged.

The integration point is `Runner.RunAsync`, which calls `setpdeath` before starting server processes. On non-Linux systems there is no parent-death signal configuration, so child server cleanup relies on explicit test cleanup.

Risks are platform behavior differences: orphaned async server processes are more likely if tests crash on non-Linux. Linux-specific behavior is implemented separately. Test signals are indirect through server-mode robustness tests on each platform.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath_linux.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath_linux.go

This Linux implementation configures async Kopia commands with `syscall.SysProcAttr{Pdeathsig: SIGTERM}`. It returns nil unchanged when given nil.

The behavior ensures server processes launched by `Runner.RunAsync` are signaled if the parent test process dies, reducing leaked Kopia servers during robustness failures.

State is process attribute mutation before start. Risks include relying on Linux-specific semantics, existing `SysProcAttr` fields being overwritten if future code sets them earlier, and SIGTERM not guaranteeing cleanup. Integration is with server-mode snapshotters and multiclient tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/apt-publish.sh -->
# sources/sync-backup/kopia/tools/apt-publish.sh

This script publishes Debian/APT artifacts to a Google Cloud Storage package host. It requires `PACKAGES_HOST`, takes a package directory, signs/arranges packages using a fixed GPG key ID, and handles stable/testing distribution paths with retention for unstable packages.

Control flow exits without publishing when `PACKAGES_HOST` is unset, then prepares apt repository metadata and copies results to `gs://$PACKAGES_HOST/apt`. It distinguishes stable and testing distributions based on package/version inputs and keeps a bounded number of unstable `.deb` artifacts.

State is local package metadata plus remote GCS repository contents. Dependencies are bash, GPG, apt tooling, gsutil/gcloud environment, and naming conventions. Risks include accidental publish to wrong bucket, fixed key availability, retention deleting desired artifacts, and `set -e` stopping mid-publish without rollback. Test signals are likely release-pipeline execution rather than unit tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/apt-publish.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/cli2md/cli2md.go -->
# sources/sync-backup/kopia/tools/cli2md/cli2md.go

This command generates Hugo/Markdown CLI reference pages from the Kopia kingpin app model. It defines base output directory, common/advanced sections, flag escaping, default overrides, and functions to emit flags, args, app flags, command indexes, subcommands, and pages.

Control flow in `main` parses flags, verifies base dir, removes existing generated common/advanced sections, obtains the CLI model, generates global flags, and recursively flattens commands. `flattenChildren` carries parent flags into descendants and can force hidden status. `generateSubcommandPage` writes front matter, synopsis, usage, flags, args, examples/details, and subcommand listings. `escapeFlags` protects CLI flags from Markdown interpretation.

State is generated files under `content/docs/Reference/Command-Line`. Dependencies are kingpin model internals and Kopia CLI registration. Risks include deleting the wrong base dir, generated docs drift from CLI model fields, hidden/advanced command classification, and Markdown escaping gaps. Unit tests cover flag escaping only.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/cli2md/cli2md.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/cli2md/cli2md_test.go -->
# sources/sync-backup/kopia/tools/cli2md/cli2md_test.go

This file tests Markdown flag escaping. `TestEscapeFlags` runs table cases through `escapeFlags` and checks expected backtick-wrapped CLI flags in plain text.

The test directly protects generated documentation formatting for command-line flags, especially avoiding accidental Markdown list or emphasis interpretation. It depends on `testify/require`.

Risks not covered include full page generation, filesystem deletion/writes, command flattening, front matter, sorting, and advanced/common section partitioning. The test is narrow but useful for the most text-sensitive helper.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/cli2md/cli2md_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker-publish.sh -->
# sources/sync-backup/kopia/tools/docker-publish.sh

This script prepares and publishes multi-architecture Kopia Docker images. It copies amd64 and arm64 release artifacts plus `rclone` into the Docker build directory, sets executable permissions, computes tags from release metadata, builds/pushes images, and cleans copied binaries afterward.

Control flow defaults `DIST_DIR` and `DOCKERHUB_REPO`, derives extra tags for stable/testing releases, and uses Docker build/push commands against `tools/docker`. It assumes specific distribution artifact layout names.

State is temporary copied binaries in `tools/docker/bin-*` and remote Docker registry tags. Dependencies are bash, Docker, dist artifact naming, and DockerHub credentials. Risks include stale binaries if cleanup fails, wrong tags on version parsing mistakes, overwriting `latest`, and lack of rollback on partial pushes. Signals are release pipeline runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker-publish.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker/Dockerfile -->
# sources/sync-backup/kopia/tools/docker/Dockerfile

This Dockerfile builds the runtime Kopia image from `ubuntu:jammy`. It sets noninteractive locale/env defaults, Kopia config/log/cache/rclone paths, persistence behavior, and installs runtime packages before copying architecture-specific Kopia/rclone binaries based on `TARGETARCH`.

Control flow is Docker build-stage shell execution: install dependencies, create app directories, add binaries from `bin-amd64` or `bin-arm64`, expose volumes/ports as configured by the image, and define the Kopia server/client entrypoint behavior.

State is container filesystem layout under `/app` and environment defaults. Dependencies are Ubuntu package repositories, buildx `TARGETARCH`, and release script-provided binaries. Risks include base image CVEs, package drift, architecture copy mismatches, privileged/mount expectations, and env defaults affecting user deployments. Signals are Docker build/publish pipeline and compose smoke usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker/docker-compose.yml -->
# sources/sync-backup/kopia/tools/docker/docker-compose.yml

This compose file defines a sample Kopia container deployment. The service uses `kopia/kopia:latest`, runs as root, restarts unless stopped, enables privileged/SYS_ADMIN/AppArmor-unconfined settings, maps devices and volumes for config/cache/logs/repository/data, and exposes the web/server port.

Control flow is declarative Docker Compose configuration. It is intended as an example operational deployment rather than test code.

State persists through mounted host volumes for configuration, cache, logs, repository, and backed-up data. Dependencies are Docker Compose, host mount paths, and Linux privilege support. Risks include broad container privileges, root user operation, accidental exposure of server port, and users needing to customize volumes before production use. Signals are manual compose runs and Docker image compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/docker/docker-compose.yml -->
