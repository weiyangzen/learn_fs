# Research: subset-b-009198

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/model.go -->
# sources/sync-backup/syncthing/lib/model/model.go

## Purpose

`model.go` defines Syncthing's central model service: the long-lived coordinator that binds configuration, folder runners, database index state, protocol connections, request handling, progress tracking, pending device/folder observation, cluster configuration exchange, scans, ignores, versioning, and user-facing query APIs. It implements `Model`, `connections.Model`, `protocol.Model` callbacks, and `config.Verifier`/committer behavior through `CommitConfiguration`.

The file is the integration layer between the BEP protocol layer and folder services. It does little direct file synchronization itself; instead it routes protocol events into `indexHandlerRegistry`, folder runner services, `db.DB`, `ProgressEmitter`, and config mutation helpers.

## Important APIs, Types, and Functions

- `service` is the local folder runner contract. Folder implementations must be suture services and expose scan, pull queue, override/revert, state, error, and statistics operations.
- `Model` is the public model facade used by APIs and other services. It includes scanning, folder state, ignore management, version restore, DB iteration/counts, completion, connection stats, pending device/folder operations, directory tree generation, and outbound block requests.
- `model` owns constructor dependencies (`config.Wrapper`, local `protocol.DeviceID`, `db.DB`, event logger, key generator), concurrency primitives, semaphores, folder maps, connection maps, remote state, device download state, index handlers, and testing counters.
- `NewModel` initializes maps, semaphores, the progress emitter, observed DB, per-device statistics, request limiters, and suture child services.
- `serve` subscribes to config, starts folders with `initFolders`, closes all connections on exit, and handles fatal errors plus deferred connection promotion.
- Folder lifecycle functions include `initFolders`, `newFolder`, `addAndStartFolderLocked`, `restartFolder`, `removeFolder`, and `cleanupFolderLocked`.
- Protocol inbound handlers include `Index`, `IndexUpdate`, `ClusterConfig`, `Closed`, `Request`, `DownloadProgress`, and `OnHello`.
- Config exchange helpers include `generateClusterConfig`, `ccHandleFolders`, `ccCheckEncryption`, `handleIntroductions`, `handleDeintroductions`, `handleAutoAccepts`, and `sendClusterConfig`.
- User/API read methods include `ConnectionStats`, `DeviceStatistics`, `FolderStatistics`, `Completion`, `NeedFolderFiles`, `RemoteNeedFolderFiles`, `LocalChangedFolderFiles`, `GlobalDirectoryTree`, `Availability`, and DB pass-through iterators/counts.
- State mutation APIs include `ScanFolders`, `ScanFolderSubdirs`, `SetIgnores`, `Override`, `Revert`, `BringToFront`, `ResetFolder`, `DismissPendingDevice`, and `DismissPendingFolder`.
- Helper types include `FolderCompletion`, `ConnectionStats`, `ConnectionInfo`, `TreeEntry`, `folderDeviceSet`, `syncMutexMap`, `deviceIDSet`, `storedEncryptionToken`, `updatedPendingFolder`, and `redactedError`.

## Control Flow

Startup flows through `NewModel` into suture children and `serve`. `serve` subscribes the model as a config committer, initializes all unpaused folders, cleans stale pending records, sends initial cluster configs, then waits for context cancellation, fatal errors, or the promotion timer. On shutdown, `closeAllConnectionsAndWait` closes every active protocol connection and waits on per-connection closed channels.

Folder startup creates ignore matchers, drops stale DB device indexes for devices no longer shared with the folder, creates roots/markers for blank folders, loads receive-encrypted tokens, hides Syncthing metadata paths, constructs versioners, warns about protected files, creates a runner via `folderFactories`, and registers the runner with index handlers. Restart is serialized per folder by `folderRestartMuts` so concurrent config commits do not leave duplicate runners alive.

Inbound index flow validates that the announced folder exists, is shared with the sending device, and is not paused. It then locates the index handler for the connection and delegates full or incremental updates to `ReceiveIndex`, preserving BEP sequence metadata.

Inbound cluster config flow is more involved. `ClusterConfig` ignores secondary configs, ensures an index handler for the primary connection, validates that the remote and local device entries exist for every announced folder, optionally auto-accepts folders by modifying config and waiting for the commit, processes folder sharing/encryption/pending state in `ccHandleFolders`, records remote folder states, subscribes temporary indexes through `ProgressEmitter`, and applies introducer/deintroducer config mutations when the peer is configured as an introducer.

Connection flow starts with `OnHello` for unknown-device observation and `AddConnection` for known devices. `AddConnection` stores the connection by ID, appends it to the device's ordered connection slice, logs events, maybe adopts the remote device name, updates last-seen stats, and schedules promotion. `promoteConnections` chooses the first connection as primary for each device, sends a full cluster config to primaries, starts secondaries, and sends a secondary-marked cluster config. `Closed` removes connection state, unsubscribes temporary indexes for removed primaries, tears down index handlers when necessary, schedules promotion, updates device stats, emits disconnect events, and closes the connection's wait channel.

Inbound request flow validates nonnegative sizes/offsets, folder existence, sharing, pause state, canonical filename, internal-file rejection, ignore rejection, request semaphores, symlink traversal, optional temporary file reads, regular-file checks, read errors, and content hash validation. Hash mismatch on a normal folder schedules `recheckFile` to force-rescan a file that DB metadata says should have matched but disk bytes did not.

Config commit flow waits for startup, adds new folders, removes missing folders, restarts folders when restart-only settings or ignore cache behavior changed, emits pause/resume events, creates stats refs for new devices, closes connections for paused/removed devices, updates per-device request limiters, sends cluster configs to affected devices, cleans pending records, resizes global/folder semaphores, and returns whether no external restart is needed.

## State and Persistence Behavior

The central mutable state is guarded by `m.mut`. It includes folder configs, ignore matchers, folder runners, versioners, encryption password tokens/failures, live connections, per-device connection ordering, promoted connection IDs, request limiters, hello messages, device download states, remote folder states, and index handlers. Folder restarts also use a per-folder mutex stored in `syncMutexMap`.

Persistence is delegated primarily to `db.DB`, typed stats DB references, and `db.ObservedDB`. The model reads and writes local/remote file indexes, folder/device counts, sequences, block-hash lookup metadata, observed pending devices, observed pending folders, and per-device statistics. Folder removal drops folder DB state, while reset drops metadata only when the folder is paused. Unknown device/folder offers are persisted as pending observations and reconciled by `cleanPending`.

Receive-encrypted folder state persists an encryption token as JSON under the folder marker path (`MarkerName/EncryptionTokenName`). `ccCheckEncryption` loads or writes that token and caches it in memory. Path-related errors are wrapped in `redactedError` to keep sensitive paths out of public failure events.

Request limiting state uses semaphores. `newLimitedRequestResponse` takes bytes from per-device and global semaphores and returns them only when the protocol response is closed, so callers must close responses to avoid capacity leaks.

## Dependencies and Integration Points

`model.go` integrates with:

- `suture` and `svcutil` for service supervision.
- `config.Wrapper` for config subscriptions, defaults, validation, and mutation waits.
- `db.DB` and `db.ObservedDB` for file index, counts, stats, pending offers, and metadata persistence.
- `protocol.Connection`, BEP message structs, device IDs, vectors, and request/response types.
- Folder runner implementations registered in `folderFactories`.
- `ignore.Matcher`, `fs.Filesystem`, `osutil`, and `scanner` for path, ignore, symlink, read, and hash behavior.
- `events.Logger` for device, folder, download, cluster-config, pending, and failure events.
- `ProgressEmitter` for temporary index subscriptions and active pull progress.
- `versioner` for file versions and restore operations.
- `stats` for device/folder statistics.
- `semaphore` for global incoming request limits, per-device request limits, and folder I/O concurrency.

## Risks and Edge Cases

- Lock ordering matters. Some methods intentionally collect post-lock actions or wait outside `m.mut` to avoid deadlocks with folder shutdown or protocol connection callbacks.
- `folderCompletion` assumes `m.deviceDownloads[device]` exists for queried devices; most connected/known-device paths populate it, but unusual direct calls can be sensitive to nil map entries.
- Request responses must be closed by consumers. Capacity in request semaphores and buffers in `protocol.BufferPool` are released on `Close`.
- `CommitConfiguration` uses `reflect.DeepEqual` on restart-only config projections. Incorrect projections can either miss required restarts or restart too often.
- Auto-accept creates directories and writes default ignores while processing cluster configs; races are mitigated by config waiter synchronization but still carry filesystem and path-conflict risks.
- Receive-encrypted handshake is token-sensitive. Mismatched local/remote token direction returns distinct errors, and read/write failures are deliberately redacted.
- `GlobalDirectoryTree` assumes database directory entries precede child entries enough to build parents; malformed or unsorted metadata can produce parent lookup errors.
- Connection promotion depends on ordered `deviceConnIDs`, with index handling tied to the primary connection.

## Test Signals

`model_test.go` provides extensive coverage for this file. It exercises request validation, index benchmarks, device renaming and persistence, cluster config generation, encrypted cluster config filtering, introducer/deintroducer behavior, auto-accept permutations, ignore load/write behavior, scan recovery, directory tree rendering, folder add/pause/remove restart behavior, unknown-device index cleanup, disconnect cleanup, internal scan edge cases, request limit blocking, connection close on restart, modtime windows, device pause events, folder API errors, rename detection/sequence ordering, block-hash lookup maintenance, cluster config resend triggers, completion math, receive-only deletion accounting, encryption consistency, pending folder cleanup, and receive-only/receive-encrypted deletion behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/model.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/model_test.go -->
# sources/sync-backup/syncthing/lib/model/model_test.go

## Purpose

`model_test.go` is the broad regression and behavior suite for Syncthing's model service. It builds fake configurations, fake filesystems, fake protocol connections, and DB state to validate how `model.go` handles protocol requests, folder lifecycle, config changes, cluster config exchange, auto-accept, introducers, ignore files, scanning, connection cleanup, request limits, completion accounting, encryption compatibility, pending offers, and rename/block metadata.

The tests double as executable documentation for model edge cases. Many test names reference historical Syncthing issues, indicating bug-regression protection around deadlocks, panics, DB accounting, stale connection state, and scan consistency.

## Important APIs, Helpers, and Test Groups

- `newState` wraps config, starts a test model, and adds fake device connections.
- `createClusterConfig` and `addFolderDevicesToClusterConfig` build BEP cluster configs with local and remote device entries.
- `genFiles` creates deterministic `protocol.FileInfo` slices for index and benchmark scenarios.
- `saveConfig` and `loadConfig` are test-local copies for checking remote device name persistence.
- `changeIgnores` validates `LoadIgnores` and `SetIgnores` round trips.
- `waitForState` observes `events.StateChanged` until a folder reports an expected error string.
- `testConfigChangeTriggersClusterConfigs` asserts which connected devices receive cluster configs after folder sharing changes.
- `modtimeTruncatingFS` and `modtimeTruncatingFileInfo` simulate filesystems with coarse modtime resolution.
- `countIterator` consumes iterator/error-function pairs and fails tests on iterator errors.

Major test groups cover:

- Request security and semantics (`TestRequest`, request benchmarks, `TestRequestLimit`, `TestNewLimitedRequestResponse`).
- Cluster config, encryption, auto-accept, and introducer behavior (`TestClusterConfig`, `TestClusterConfigEncrypted`, `TestIntroducer`, many `TestAutoAccept...`, `TestCcCheckEncryption`, `TestCCFolderNotRunning`).
- Folder lifecycle and config commits (`TestIssue4357`, `TestPausedFolders`, `TestFolderRestartZombies`, cluster-config resend tests).
- Ignore file behavior (`TestIgnores`, `TestEmptyIgnores`, `TestIssue4094`, `TestIssue4903`).
- Scanning and DB accounting (`TestROScanRecovery`, `TestRWScanRecovery`, `TestInternalScan`, rename tests, block-list map tests, receive-only deletion tests).
- Connection and device cleanup (`TestDeviceRename`, `TestSharedWithClearedOnDisconnect`, `TestConnCloseOnRestart`, `TestDevicePause`, `TestDeviceWasSeen`).
- API-facing views (`TestGlobalDirectoryTree`, `TestFolderAPIErrors`, `TestSummaryPausedNoError`, completion tests, pending folder tests).

## Control Flow

Most tests construct a config wrapper, create a model using helper constructors, optionally start the model supervisor, mutate fake filesystem state or protocol state, then call model methods synchronously. For protocol flows, fake connections are added with `AddConnection`, cluster configs are injected with `ClusterConfig`, indexes with `Index`/`IndexUpdate`, and outbound cluster config delivery is observed through fake connection call hooks.

Auto-accept tests simulate remote devices announcing folders under many combinations: new folder, existing folder, multiple devices, disabled auto-accept, label/ID path selection, path conflicts, paused local folders, encrypted and unencrypted announcements, and concurrent acceptance. The tests then inspect `m.cfg.Folder` and sharing lists to confirm config mutation outcomes.

Scan tests mutate fake filesystems, call `ScanFolder` or `ScanFolders`, then inspect DB-derived APIs such as `LocalSize`, `GlobalSize`, `ReceiveOnlySize`, `LocalFilesSequenced`, `CurrentFolderFile`, and `AllForBlocksHash`. Several tests use timeouts because pull/index side effects are asynchronous.

Connection tests add fake or protocol connections, trigger config changes that pause/remove devices or folders, and wait for close channels, event subscriptions, or fake connection calls. These flows verify the model does not hold locks across blocking close/start paths.

## State and Persistence Behavior

The suite validates both in-memory maps and persistent DB/config effects. It checks that remote device names can be stored into config, pending folders are inserted/filtered/removed from `ObservedDB`, folder removal drops pending associations, unknown remote indexes are dropped when a folder starts, removed devices are removed from config and model connection/download/hello maps, and request limiters release semaphore capacity after responses close.

Filesystem persistence is exercised through fake and basic filesystems. Ignore tests assert empty ignore content deletes `.stignore`, non-empty content writes it, paused folder paths can be created for ignore writes, and missing fake paths are treated as empty ignore sets. Encryption tests cover token computation and cached token behavior but skip expensive token generation in short mode.

DB state is checked for rename sequence adjacency, block-hash lookup update after remove/modify/rename/type-change operations, deleted file accounting, receive-only changed flags, completion counters, and index reset metadata.

## Dependencies and Integration Points

Tests depend on Syncthing's internal test helpers, fake filesystem implementations, fake protocol connections, mock connection info, event logger subscriptions, config wrappers, `db` counts/observed records, protocol vectors and file info structs, versioner constants, scanner side effects through `ScanFolder`, and semaphore behavior.

Benchmarks integrate with the same model setup to measure full index, incremental index, outbound request, inbound request, and directory tree generation costs at different scales.

## Risks and Edge Cases Captured

- Security-sensitive request handling rejects invalid paths, unshared folders, negative sizes, nonexistent files, missing or mismatched hashes, and read-past-EOF unless the short read hash matches.
- Auto-accept historically risked panics or path corruption around paused folders and concurrent config commits.
- Introducer removals must not remove devices shared independently or when removal skipping is configured.
- Folder restarts must be serialized to prevent duplicate runners.
- Request limiters must block concurrent oversized requests and release capacity on response close.
- Connection close during restart must not deadlock when protocol readers block.
- Scan logic must not mark inaccessible directory contents deleted, must handle directory/file type changes, case-only renames, batch flushes, and deleted receive-only states correctly.
- Cluster config generation for folders not fully running must still include expected folder/device metadata without exposing invalid index data.

## Test Signals

The file is itself the primary test signal for `model.go`. It contains dozens of unit/regression tests and several benchmarks. The coverage is strongest around externally observable behavior and historical regressions. Lower-level helper functions in `model.go` are commonly tested through model-level flows rather than isolated unit tests, which is appropriate for this integration-heavy component but means failures can sometimes require tracing through config, DB, protocol, and folder runner helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/model_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/progressemitter.go -->
# sources/sync-backup/syncthing/lib/model/progressemitter.go

## Purpose

`progressemitter.go` implements `ProgressEmitter`, the model subservice that publishes active pull progress locally through `events.DownloadProgress` and remotely through BEP `DownloadProgress` messages. It tracks active `sharedPullerState` instances, periodically detects changes, emits GUI/API event payloads, and advertises temporary block availability to subscribed peer connections.

The emitter is also a config committer. It enables, disables, clears, or retunes itself when progress update interval and temporary index threshold settings change.

## Important APIs, Types, and Functions

- `ProgressEmitter` stores config, active puller registry (`folder -> file -> state`), timer interval, minimum temporary-index block threshold, sent temporary-index state per device, subscribed connections, folders per connection, disabled flag, event logger, mutex, and timer.
- `progressUpdate` bundles a protocol connection, folder ID, and `protocol.FileDownloadProgressUpdate` list. Its `send` method sends a BEP `DownloadProgress` message.
- `NewProgressEmitter` creates maps, initializes the short timer, applies current config with `CommitConfiguration`, and returns a ready service.
- `Serve` subscribes to config and runs the timer loop. On timer ticks, it checks registry count and latest puller update timestamp, emits local events, computes remote updates, resets the timer when work remains, unlocks, then sends network messages outside the mutex.
- `sendDownloadProgressEventLocked` builds the nested event payload of folder/file to `PullerProgress`.
- `computeProgressUpdates` computes per-device, per-folder temporary-index append/forget updates using `sentDownloadState`.
- `CommitConfiguration` enables/disables progress emission, updates interval, updates `minBlocks`, and clears current state when disabled.
- `Register` and `Deregister` add/remove active puller states.
- `BytesCompleted` sums current active pull progress by folder.
- `temporaryIndexSubscribe` and `temporaryIndexUnsubscribe` manage peer subscriptions set up by the model after cluster config exchange.
- `clearLocked` sends cleanup messages for known sent temporary-index states and resets all maps.

## Control Flow

When a puller starts, it calls `Register`. If the registry was empty, the timer is reset so the service wakes up. On each timer tick, `Serve` scans all registered puller states for a newer `Updated` timestamp or a changed registry count. If nothing changed, no event or protocol message is emitted. If something changed, the service sends one local event snapshot and computes remote temporary-index deltas.

Remote update computation iterates subscribed device connections and only considers folders currently subscribed for that device. It filters out puller states for other folders, symlinks, directories, and files whose block count is at or below `minBlocks`. For active regular files above the threshold, it updates per-device `sentDownloadState`, producing append updates for new available blocks and forget updates for vanished or version-changed states. It also drops sent state for disconnected devices and cleans state for folders no longer shared with a device, although forget messages for unshared folders are intentionally not sent in the current code path.

Network sends happen after unlocking. This prevents blocked peer I/O from holding the emitter mutex and delaying puller registration/progress reads, at the cost of remote progress messages being best-effort under back-pressure.

## State and Persistence Behavior

The emitter has no disk persistence. All state is in memory and protected by `mut`. `registry` tracks current active pullers. `sentDownloadStates` remembers what temporary block availability has already been announced to each device so messages can be incremental and cleanup/forget messages can be generated. `connections` and `foldersByConns` mirror temporary-index subscriptions controlled by the model.

Disabling the emitter clears active registry and sent states. `clearLocked` attempts to send cleanup messages before clearing, using `context.Background()`. Since cleanup sends occur while called under the lock, blocked protocol implementations would be more sensitive here than in the normal `Serve` send path.

## Dependencies and Integration Points

`ProgressEmitter` depends on:

- `config.Wrapper` and `config.Configuration` for runtime options.
- `events.Logger` for local `DownloadProgress` events.
- `protocol.Connection`, `protocol.DownloadProgress`, and `protocol.FileDownloadProgressUpdate` for BEP progress messages.
- `sharedPullerState`, `PullerProgress`, and `sentDownloadState` types defined elsewhere in the model package.
- The model's cluster-config handling, which calls `temporaryIndexSubscribe` and `temporaryIndexUnsubscribe` when peers are eligible for temporary indexes.

## Risks and Edge Cases

- Timer behavior depends on registry count. If a puller is registered while disabled, it is ignored; when re-enabled, old ignored states are not resurrected.
- `computeProgressUpdates` iterates maps, so update ordering is intentionally nondeterministic.
- Temporary-index cleanup for folders no longer shared is currently state-only; sending forget updates is commented out because unsharing normally reconnects the peer.
- `clearLocked` performs protocol sends under the mutex, unlike the normal timer path.
- The emitter filters on `len(file.Blocks) <= minBlocks`, so exactly-at-threshold files do not advertise temporary indexes.
- Progress events only emit on observed timestamp/count changes. Puller states must update their timestamps reliably.

## Test Signals

`progressemitter_test.go` validates local event emission for register/progress/deregister changes and no duplicate events when nothing changes. It also validates temporary-index message generation: minimum block threshold, append deltas, no-op unchanged timestamps, version changes producing forget plus append, puller creation timestamp changes, empty append updates, multi-file/multi-folder batching, deletion forget messages only once, inactive puller filtering, folder subscription changes, and state cleanup after unsubscribe.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/progressemitter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/progressemitter_test.go -->
# sources/sync-backup/syncthing/lib/model/progressemitter_test.go

## Purpose

`progressemitter_test.go` verifies `ProgressEmitter` behavior for local download progress events and remote BEP `DownloadProgress` messages. It focuses on event timing, state diffing, temporary-index eligibility, append/forget message correctness, subscription cleanup, and no-op behavior when state has not materially changed.

## Important APIs, Helpers, and Test Cases

- `timeout` is the short polling duration for event expectations.
- `caller` annotates test failures with the source call site.
- `expectEvent` polls an event subscription and asserts a `DownloadProgress` event with the expected top-level folder count.
- `expectTimeout` asserts that no event arrives within the short timeout.
- `TestProgressEmitter` exercises local event emission as a puller is registered, updated by copy/pull operations, and deregistered.
- `TestSendDownloadProgressMessages` is a detailed protocol-message state machine test for `computeProgressUpdates`.
- `sendMsgs` calls `computeProgressUpdates` under the emitter lock and sends the resulting messages to fake connections, matching production's split between computation and sends.

## Control Flow

`TestProgressEmitter` creates an event logger, config wrapper, and emitter with a positive interval, then manually sets `p.interval = 0` to make timer ticks immediate after registration. It first expects no event, registers a `sharedPullerState`, and then mutates that state through methods such as `copyDone`, `copiedFromOrigin`, `pullStarted`, and `pullDone`. Each mutation should produce exactly one local event, followed by a timeout when no further change occurs. Deregistration should emit an empty progress event.

`TestSendDownloadProgressMessages` creates a fake connection subscribed to two folders and directly manipulates `p.registry` with crafted `sharedPullerState` objects. It uses an `expect` helper to locate messages for a folder and verify update type, file version, and block indexes. The test repeatedly calls `sendMsgs` after changing availability, update timestamps, versions, creation timestamps, registry membership, and subscriptions.

## State and Persistence Behavior

The tests operate entirely in memory. They inspect fake connection `downloadProgressMessages` and the emitter's `sentDownloadStates` map. They verify that sent state remembers prior append messages, produces only diffs for newly available blocks, sends forgets when pullers disappear or versions change, and deletes device state after temporary-index unsubscribe.

No file or database persistence is involved.

## Dependencies and Integration Points

The test uses config wrappers, event logger service, fake protocol connections from the model test harness, `protocol.Vector`, `protocol.FileInfo`, and `protocol.FileDownloadProgressUpdateType*` constants. It depends on `sharedPullerState` methods from the puller implementation to update progress timestamps in the same way production pullers do.

## Risks and Edge Cases Captured

- No duplicate local events should be emitted when progress did not change.
- Temporary-index messages require more blocks than `TempIndexMinBlocks`; smaller files, directories, symlinks, and pullers in unsubscribed folders are ignored.
- Availability changes without an updated timestamp do not produce messages, matching the timestamp-driven design.
- Version changes require a forget for the old version and append for the new version.
- Puller recreation with the same file version still forces forget plus append because creation time changed.
- Deleted/disappeared pullers produce forget messages only once.
- Folder subscription cleanup currently does not send forget messages for unshared folders, and the test documents this behavior with commented expectations.

## Test Signals

These tests are strong coverage for `ProgressEmitter.computeProgressUpdates` and local event emission. They deliberately avoid depending on deterministic map iteration by locating updates dynamically. The main residual risk is that the tests call `computeProgressUpdates` directly for protocol messages rather than running the full `Serve` timer path, though `TestProgressEmitter` does cover the timer/event loop for local events.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/progressemitter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/queue.go -->
# sources/sync-backup/syncthing/lib/model/queue.go

## Purpose

`queue.go` implements `jobQueue`, a small mutex-protected FIFO used by folder pulling code to track files waiting to be pulled and files currently in progress. It provides queue mutation, promotion of a queued file to the front, completion removal, pagination for API/UI reporting, and reset/length helpers.

The queue stores only file names plus size/modification metadata for queued entries. Current code in this file only exposes names; `size` and `modified` are retained in `jobQueueEntry` for possible ordering or metadata use by surrounding puller code.

## Important APIs, Types, and Functions

- `jobQueue` has `progress []string`, `queued []jobQueueEntry`, and a mutex.
- `jobQueueEntry` stores `name`, `size`, and `modified` as Unix nanoseconds.
- `newJobQueue` returns an empty queue.
- `Push` appends a file entry to the queued FIFO.
- `Pop` removes the first queued entry, appends its name to `progress`, and returns the name plus success flag.
- `BringToFront` finds a queued filename and shifts it to queued index zero while preserving the relative order of earlier items behind it.
- `Done` removes a filename from `progress` if present.
- `Jobs` returns paginated progress names, queued names, and the number of skipped items across the combined `progress + queued` view.
- `Reset` clears both slices.
- `lenQueued` and `lenProgress` return counts under lock.

## Control Flow

The expected lifecycle is `Push` for files needing pull, `Pop` when a worker starts a file, and `Done` when the worker finishes or abandons that file. `BringToFront` can be called before `Pop` to prioritize a queued filename. `Jobs` is read-only from the caller's perspective but locks internally, computes the combined pagination window, copies names into fresh slices, and never exposes internal slices.

Pagination treats in-progress jobs as preceding queued jobs. If the requested page starts beyond the total count, it returns nil progress/queued slices and `skipped == total`. If the page falls entirely in progress, only progress is returned. Otherwise it returns the remaining progress names plus enough queued names to fill `perpage`.

## State and Persistence Behavior

All state is in memory and protected by `q.mut`. The queue does not persist to disk or database. It does not deduplicate filenames, so callers are responsible for avoiding duplicate queued entries if that matters. `Done` is idempotent for absent names. `BringToFront` is a no-op when the file is absent or already first.

## Dependencies and Integration Points

`queue.go` depends only on the Go standard library (`sync`, `time`). It is integrated through folder runner/puller code and surfaced through the model's `NeedFolderFiles`, which asks a running folder service for `Jobs(page, perpage)` and then maps returned names back to global `protocol.FileInfo` records.

## Risks and Edge Cases

- Queue ordering is FIFO except for explicit `BringToFront`.
- No deduplication means duplicate pushes can lead to duplicate work unless higher layers prevent it.
- `Jobs` assumes positive page/perpage values. Invalid values could produce unexpected slice behavior because the method does not validate inputs.
- `jobQueueEntry.size` and `modified` are not used by this file, so callers should not expect internal sorting by size or modification time.
- Long queues make `BringToFront` O(n) and use slice shifting; benchmarks cover this but it is not optimized for extremely frequent arbitrary promotions.

## Test Signals

`queue_test.go` validates push/pop/done lifecycles, absent `Done` calls, empty queue behavior, explicit bring-to-front ordering including first and last elements, and pagination across queued-only and mixed progress/queued states. Benchmarks cover arbitrary bumping in a 10k queue and push/pop/done throughput for 10k files.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/queue_test.go -->
# sources/sync-backup/syncthing/lib/model/queue_test.go

## Purpose

`queue_test.go` verifies the behavior and performance characteristics of `jobQueue`. It ensures FIFO pop semantics, in-progress tracking, completion removal, bring-to-front reordering, empty/absent operations, and pagination over the combined progress-plus-queued view.

## Important APIs and Test Cases

- `TestJobQueue` covers a mixed lifecycle of pushing four files, popping them, marking them done, pushing them back, bringing queued files to the front, and handling absent `Done`/`BringToFront` calls.
- `TestBringToFront` focuses specifically on ordering after promoting first, middle, and last queued elements. It uses `messagediff.PrettyDiff` for readable order failures.
- `BenchmarkJobQueueBump` measures `BringToFront` cost on 10k files using random file choices.
- `BenchmarkJobQueuePushPopDone10k` measures queue construction and full drain/done throughput for 10k files.
- `TestQueuePagination` validates `Jobs(page, perpage)` for queued-only state, after one file is in progress, and after eight files are in progress.

## Control Flow

The tests instantiate a new queue, call queue methods directly, and check returned progress/queued slices and skip counts after each state transition. Pagination tests create ten files, request several page/per-page combinations, then progressively move files from queued to progress with `Pop`.

## State and Persistence Behavior

The tests verify only in-memory state. They inspect returned copies from `Jobs` and, in `TestJobQueue`, also inspect internal slice lengths for progress and queued. There is no filesystem, DB, or event dependency.

## Dependencies and Integration Points

The test file uses the Go standard testing, rand, slices, fmt, and time packages plus `github.com/d4l3k/messagediff` for human-readable diffs. It reuses `genFiles` from `model_test.go` for benchmark data.

## Risks and Edge Cases Captured

- Bringing the first queued element to front should leave ordering unchanged.
- Bringing the last queued element to front should preserve the relative order of all earlier elements behind it.
- Calling `Done` for a nonexistent file should not mutate queue state.
- Popping from an empty queue should return `ok == false`.
- `Jobs` skip counts must represent the combined progress and queued offset, including out-of-range pages.
- Mixed progress/queued pagination must fill the page from progress first, then queued entries.

## Test Signals

The queue tests provide focused coverage for all exported package-local queue methods. They do not test invalid pagination inputs such as zero or negative values, which remains a caller-contract assumption.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/model/queue_test.go -->
