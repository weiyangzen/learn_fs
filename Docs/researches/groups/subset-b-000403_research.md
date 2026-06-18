# subset-b-000403 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/rpc/server.go -->
## sources/control-plane/longhorn-engine/pkg/sync/rpc/server.go

### Purpose
`server.go` implements the Longhorn engine sync-agent gRPC service that runs beside a replica. It is the local executor for file transfer, snapshot purge, backup create/restore/remove, replica rebuild transfer, snapshot clone, and snapshot hashing operations. The file bridges control-plane RPC requests from controllers/replica clients into on-disk replica mutations and background transfer jobs.

### Important APIs, Types, And Functions
The main type is `SyncAgentServer`, which embeds `enginerpc.UnimplementedSyncAgentServiceServer`, protects process state with an `RWMutex`, tracks the receiver port range, and owns shared status objects: `BackupList`, `SnapshotHashList`, `RestoreInfo`, `PurgeStatus`, `RebuildStatus`, and `CloneStatus`. `NewSyncAgentServer` registers the sync-agent service, reflection, identity-validation interceptors, and the profiler service.

`PurgeStatus`, `RebuildStatus`, and `CloneStatus` implement progress callbacks consumed by sparse-tools operations. The service methods include `FileRemove`, `FileRename`, `FileSend`, `VolumeExport`, `ReceiverLaunch`, `FilesSync`, `SnapshotClone`, `BackupCreate`, `BackupStatus`, `BackupRemove`, `BackupRestore`, `RestoreStatus`, `SnapshotPurge`, `SnapshotPurgeStatus`, `SnapshotHash`, `SnapshotHashStatus`, `SnapshotHashCancel`, and `SnapshotHashLockState`. Internal helpers such as `nextPort`, `launchReceiver`, `PrepareRebuild`, `FinishRebuild`, `PreparePurge`, `FinishPurge`, `StartRestore`, `FinishRestore`, `reloadReplica`, `replicaRevert`, `processRemoveSnapshot`, `replaceDisk`, and `rmDisk` encapsulate state transitions and replica-service calls.

### Control Flow
The server is stateful and strongly operation-gated. Restore starts through `BackupRestore`, validates request fields and backup credentials, decodes the requested backup name, then calls `StartRestore`. `StartRestore` decides whether a restore is a first full restore, incremental restore, or fallback full restore, starts backupstore work through the `backup` package, and sets `isRestoring`. A goroutine runs `completeBackupRestore`, polling `RestoreInfo` until completion, then reloads/reverts the replica or folds incremental delta data into the target snapshot before `FinishRestore` clears the state.

Rebuild file sync starts in `FilesSync`. `PrepareRebuild` rejects concurrent purge/rebuild work, initializes total progress from `SyncFileInfo.ActualSize`, and records source replica addresses. Local sync is attempted first when `LocalSync` is present, copying files under `/host` and validating sizes. Remote sync reconstructs backward-compatible source maps, opens source replica clients, launches per-file sparse REST receivers, asks source replicas to send files, retries failed file transfers with a Kubernetes backoff, and uses `perFileProgressOps` to subtract progress from failed attempts before retrying.

Snapshot purge runs asynchronously. `purgeSnapshots` retrieves disk-chain information, marks system-generated snapshots as removed, walks leaves toward roots, delays the snapshot immediately behind the head until the end, asks the replica service for remove operations, and executes sparse fold/prune/remove/replace actions. Snapshot clone selects a source replica snapshot, launches a receiver, exports content from the source, creates metadata, reloads the destination replica, and reverts to the cloned snapshot. Snapshot hashing creates `replica.SnapshotHashJob` tasks, stores them in `SnapshotHashList`, and falls back to checksum files when in-memory state has been refreshed away.

### State, Persistence, And Dependencies
The server persists no independent database, but it mutates durable replica files: snapshot `.img` files, `.meta` files, delta files, temporary `.snap_tmp` files, checksum files, and sparse disk chains. Runtime state is stored in booleans (`isPurging`, `isRestoring`, `isRebuilding`, `isCloning`), receiver port reservations, progress counters, and backup/hash lists protected by locks. It depends on `enginerpc`, `grpc`, identity interceptors, Longhorn `backup`, `backupstore`, `replica`, `replica/client`, sparse-tools REST/sparse operations, `flock`, `reexec`, Kubernetes backoff, and OS filesystem calls.

### Integration Points
The sync agent is called by controller-side sync tasks and replica clients during normal Longhorn operations. It calls back into the local `ReplicaService` over gRPC for reload, revert, disk mark/remove/replace, and prepare-remove APIs. Backup operations integrate with backupstore credentials and backup status objects. File transfer integrates with sparse-tools `ssync` over dynamically allocated ports. The profiler registration exposes runtime diagnostics under the sync-agent server name.

### Risks
The file coordinates destructive filesystem mutations, so ordering and cleanup matter. A failed restore must revert `RestoreInfo` and remove temporary files; a failed local sync must remove copied targets; a failed remote sync must not leave progress over-counted. Lock ordering is explicitly documented because server, backup, restore, and purge state can deadlock if future code nests locks differently. Port reservation leaks can block receivers until context cancellation. Many replica clients are created without instance names for compatibility, reducing identity strictness. Snapshot purge and restore depend on disk-name parsing conventions; malformed or unexpected disk chains can halt cleanup. `waitForRestoreComplete` has no context cancellation path and relies on restore status updates.

### Test Signals
Useful signals include gRPC sync-agent integration tests, sparse transfer retry tests, restore full/incremental/fallback restore tests, snapshot purge chain-shape tests, hash task status/cancel tests, and race tests around progress callbacks. Existing coverage is mostly indirect through higher-level engine integration and replica-client flows; focused unit tests should stress `perFileProgressOps.detach`, `PrepareRebuild` concurrency gates, purge progress division, checksum-file fallback, and cleanup after failure paths.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/rpc/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/sync.go -->
## sources/control-plane/longhorn-engine/pkg/sync/sync.go

### Purpose
`sync.go` is the controller-side orchestration layer for Longhorn replica synchronization tasks. It coordinates snapshot delete/purge, replica add/rebuild, restore-replica attachment, snapshot clone, and snapshot hashing across the replicas known to an engine controller.

### Important APIs, Types, And Functions
`Task` wraps a `controller/client.ControllerClient`; `NewTask` binds the client lifetime to a context. `TaskError` aggregates per-replica failures as `ReplicaError` values. JSON-facing status structs mirror sync-agent responses for purge, rebuild, clone, and hash jobs.

Primary methods are `DeleteSnapshot`, `PurgeSnapshots`, `PurgeSnapshotStatus`, `AddRestoreReplica`, `AddReplica`, `VerifyRebuildReplica`, `StartWithReplicas`, `RebuildStatus`, `HashSnapshot`, `HashSnapshotStatus`, and `HashSnapshotCancel`. Package-level helpers include `CloneSnapshot`, `CloneStatus`, `GetSnapshotsInfo`, `getNonBackingDisks`, `checkIfVolumeHeadExists`, and the private operation guards `isRebuilding`, `isHashingSnapshot`, `isPurging`, `markSnapshotAsRemoved`, `checkAndResetFailedRebuild`, `checkAndExpandReplica`, `reloadAndVerify`, and `getTransferClients`.

### Control Flow
Snapshot deletion first refuses removal when any replica is rebuilding, then marks the snapshot removed on every RW replica and cancels any matching hash job. Purge snapshots lists all replicas, rejects rebuild or active purge conflicts, then fan-outs `SnapshotPurge` calls to each replica client and aggregates failures.

Adding a normal replica starts the volume if no replicas exist. Otherwise it expands or validates the new replica size, resets stale failed rebuild state if needed, creates the replica in WO mode, selects RW source replicas, marks the target as rebuilding, asks the controller for the rebuild file list, rejects any file list containing `volume-head`, calls target `SyncFiles`, reloads the target, verifies rebuild, and clears the rebuilding flag. `getTransferClients` also enforces controller API version 6 rebuild-concurrency limits by trimming source replica addresses.

Snapshot clone selects the first RW source replica from the source volume, requires every target replica to be RW, then concurrently calls each target sync-agent clone RPC. Snapshot hashing validates all replicas are RW, not rebuilding, and not already holding the hash lock, then fans out hash requests. Hash status is fetched concurrently and converted into a per-address status map.

### State, Persistence, And Dependencies
This file keeps no long-lived state beyond the controller client. Durable state changes happen through controller and replica-client RPCs: replica creation, mode changes, rebuild flags, disk removal markers, reloads, snapshot purge mutations, snapshot clone files, and hash checksum files. Dependencies are Longhorn controller clients, replica clients, `enginerpc`, `types`, disk naming helpers, `multierr`, and goroutine synchronization primitives.

### Integration Points
`Task` is used by CLI/API control flows that need to coordinate all replicas rather than one sync-agent. It integrates with the controller's replica list, volume start/create/prepare/verify APIs, and with per-replica sync-agent methods. It converts low-level gRPC status into JSON structs consumed by upper layers.

### Risks
Most operations are distributed fan-outs where partial success is possible. `TaskError` reports failures but cannot undo already-started replica operations. Replica clients are often opened without instance names because source replicas are chosen from controller state, so identity validation depends on volume-level context. `GetSnapshotsInfo` trusts the healthy RW replica with the largest disk map, which is pragmatic but can expose transient in-progress state as truth. Hash status appends clients from goroutines under a mutex but closes after `Wait`; future changes must preserve that ordering.

### Test Signals
Signals include tests or integration scenarios for rebuild from multiple RW sources, API-version concurrency limiting, failed source selection, rejected head-file sync lists, restore replica size mismatch, purge skip behavior for already-purging replicas, clone fan-out error aggregation, and hash lock/rebuild conflict handling. Race tests are valuable for hash status and concurrent fan-out maps.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/sync/sync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/types/error.go -->
## sources/control-plane/longhorn-engine/pkg/types/error.go

### Purpose
`error.go` defines Longhorn engine structured errors and helper functions for preserving function and rollback outcomes across local and gRPC boundaries.

### Important APIs, Types, And Functions
`ErrorCode` enumerates `ResultUnknown`, `FunctionFailedWithoutRollback`, `FunctionFailedRollbackSucceeded`, and `FunctionFailedRollbackFailed`. `Error` carries `Code`, `Message`, and `RollbackMessage`, implements `error`, and can serialize itself with `ToJSONString`. `WrapError` prefixes structured or unstructured errors, `CombineErrors` concatenates non-nil errors, `GenerateFunctionErrorWithRollback` maps function/rollback result pairs to a structured error, and `UnmarshalGRPCError` decodes a gRPC status message containing the JSON form.

### Control Flow
Callers build structured errors with `NewError` or by wrapping failures. Rollback-aware callers pass both primary and rollback errors to `GenerateFunctionErrorWithRollback`, which selects the most specific code. gRPC clients call `UnmarshalGRPCError` to recover structured fields from a status message.

### State, Persistence, And Dependencies
No state is persisted. The durable contract is the JSON shape embedded in status messages or logs. Dependencies are `encoding/json`, standard `errors`/`fmt`, and `google.golang.org/grpc/status`.

### Integration Points
The constants are used by engine APIs and rollback-capable workflows. `ErrNoSpaceLeftOnDevice` and `CannotRequestHashingSnapshotPrefix` are shared sentinel/message fragments used elsewhere in sync and replica logic.

### Risks
`WrapError` mutates an existing `*Error` in place, so sharing the same error object across callers can unexpectedly rewrite its message. `UnmarshalGRPCError` assumes the gRPC status message is JSON and returns `ResultUnknown` if not. `CombineErrors` loses structured fields by formatting combined strings.

### Test Signals
Tests should cover JSON serialization, rollback outcome mapping, wrapping structured versus unstructured errors, malformed gRPC statuses, and nil handling in `WrapError`/`CombineErrors`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/types/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/types/resource.go -->
## sources/control-plane/longhorn-engine/pkg/types/resource.go

### Purpose
`resource.go` defines JSON-serializable resource DTOs exchanged by Longhorn engine controller, replica, and sync APIs.

### Important APIs, Types, And Functions
`ReplicaInfo` reports replica state, disk chain, revision counters, backing file, snapshot usage, unmap setting, and file timing/size data. `DiskInfo` describes one snapshot/head disk with parent, children, removal flag, user-created flag, creation time, size, and labels. `PrepareRemoveAction` encodes disk operations such as coalesce/remove/replace/prune. `VolumeInfo` reports engine volume metadata and expansion/snapshot limit state. `ControllerReplicaInfo` records address and mode. `SyncFileInfo` maps source and target filenames plus actual allocated size.

### Control Flow
There is no runtime control flow. These structs are populated by replica/controller services, serialized to JSON, and transformed into gRPC response structs or higher-level sync plans.

### State, Persistence, And Dependencies
The file has no imports and no persistence. The struct tags define the external JSON contract; fields represent state persisted elsewhere in replica metadata files or controller memory.

### Integration Points
`sync.go`, `rpc/server.go`, replica clients, controller clients, and CLI output use these DTOs. Disk-chain conversion code maps Longhorn disk filenames into `DiskInfo` snapshots, and rebuild sync maps controller-prepared file lists into `SyncFileInfo`.

### Risks
Changing JSON field names is an API compatibility risk. `VolumeInfo.SnapshotMaxSize` uses the tag `json:"SnapshotMaxSize"` with an uppercase key, which callers may already depend on. Several numeric fields are strings in JSON for historical compatibility.

### Test Signals
Useful checks include JSON marshal/unmarshal compatibility, disk-chain child/parent shape preservation, and rebuild file-list conversion retaining `ActualSize`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/types/resource.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/types/types.go -->
## sources/control-plane/longhorn-engine/pkg/types/types.go

### Purpose
`types.go` centralizes engine-wide constants, enums, and interfaces used by controller, replica, backend, frontend, and sync packages.

### Important APIs, Types, And Functions
The file defines replica modes `WO`, `RW`, `ERR`, process states, engine states, backup credential environment variable names, frontend names, retry constants, `VolumeHeadName`, snapshot limits, data-server protocols, replica lifecycle states, and sync retry/concurrency defaults.

Interfaces include `ReaderWriterUnmapperAt`, `UnmapperAt`, `DiffDisk`, `Backend`, `BackendFactory`, `SharedTimeouts`, `Controller`, `Server`, `Frontend`, and `DataProcessor`. Data structs include `Replica`, `ReplicaSalvageInfo`, `Metrics`, `RWMetrics`, and `FileLocalSync`. Helpers convert between internal `Mode` and `enginerpc.ReplicaMode` and detect already-purging errors.

### Control Flow
Most behavior is declarative interface definition. Conversion helpers switch on known replica modes and default unknown values to `ERR`. `IsAlreadyPurgingError` performs substring matching on error messages.

### State, Persistence, And Dependencies
The file persists no state. It defines contracts implemented by replica backends and frontends that do persist volume data and expose monitor channels. Dependencies are `io`, `strings`, `time`, and generated `enginerpc`.

### Integration Points
Nearly every Longhorn engine package imports this file for modes, states, and interfaces. `SharedTimeouts` is implemented by `pkg/util/shared_timeouts.go`; disk/sync packages use `VolumeHeadName`, `SyncRetryCount`, and process state constants; gRPC adapters use mode conversion helpers.

### Risks
Because this is a shared contract file, adding methods to interfaces or changing constants can cascade across the engine. Error substring detection is fragile across message wording changes. Unknown gRPC modes becoming `ERR` is safe but can hide version skew.

### Test Signals
Tests should cover mode conversion round trips, defaulting of unknown modes, `IsAlreadyPurgingError` message compatibility, and compile-time interface conformance for backend/frontend implementations.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/disk/constant.go -->
## sources/control-plane/longhorn-engine/pkg/util/disk/constant.go

### Purpose
`constant.go` defines the canonical disk filename patterns, suffixes, labels, and sector sizes used by Longhorn engine snapshot/head/backing-image utilities.

### Important APIs, Types, And Functions
Constants include `VolumeHeadDiskPrefix`, `VolumeHeadDiskSuffix`, formatted `VolumeHeadDiskName`, `SnapshotDiskPrefix`, `SnapshotDiskSuffix`, formatted `SnapshotDiskName`, delta disk naming, metadata and checksum suffixes, temporary snapshot suffix, expansion snapshot name infix, replica expansion label key, and sector sizes for volumes, replicas, and backing images.

### Control Flow
There is no control flow. Other helpers format and parse names using these constants.

### State, Persistence, And Dependencies
The constants define on-disk persistent filenames such as `volume-snap-<name>.img`, `volume-delta-<name>.img`, `.meta`, and `.checksum`. The file has no imports.

### Integration Points
Disk utility functions, sync-agent restore/purge/clone code, replica metadata, backup code, and controller snapshot flows all rely on these naming contracts.

### Risks
Any naming change can make existing replicas unreadable or make parsers reject valid disk files. Sector-size constants affect low-level volume geometry assumptions and must match backend/front-end expectations.

### Test Signals
Unit tests should assert generated names, parser compatibility, and sector-size usage in backend initialization paths.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/disk/constant.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/disk/disk.go -->
## sources/control-plane/longhorn-engine/pkg/util/disk/disk.go

### Purpose
`disk.go` provides small helpers for generating and parsing Longhorn snapshot, delta, temporary, checksum, metadata, expansion, and head disk names.

### Important APIs, Types, And Functions
Functions include `GenerateSnapshotDiskName`, `GenerateSnapshotDiskChecksumName`, `GenerateSnapshotDiskMetaName`, `GenerateDeltaFileName`, `GenerateSnapTempFileName`, `GetSnapshotNameFromTempFileName`, `GetSnapshotNameFromDiskName`, `GenerateExpansionSnapshotName`, `GenerateExpansionSnapshotLabels`, and `IsHeadDisk`.

### Control Flow
Generation functions format strings from constants. Parser functions validate required prefixes/suffixes before trimming them; invalid names return errors. `IsHeadDisk` checks the head prefix and suffix.

### State, Persistence, And Dependencies
The helpers do not persist state, but their return values are persistent on-disk filenames and labels. Dependencies are `fmt`, `strconv`, and `strings`.

### Integration Points
`sync.go`, `rpc/server.go`, backup restore, snapshot purge, and replica disk-chain code use these helpers to avoid open-coded filename manipulation.

### Risks
The parsers are intentionally strict; callers passing a temp name to `GetSnapshotNameFromDiskName` or a disk name without the standard prefix will fail. Expansion labels use an unexported key, so external code should not recreate it by hand.

### Test Signals
Tests should cover valid/invalid snapshot disk names, temp-name round trips, head detection, checksum/meta suffix generation, and expansion snapshot labels.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/disk/disk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/fsfreeze.go -->
## sources/control-plane/longhorn-engine/pkg/util/fsfreeze.go

### Purpose
`fsfreeze.go` provides helper functions for freezing and safely unfreezing filesystems mounted from Longhorn block devices. It is mainly relevant to `tgt-blockdev` volumes during shutdown or recovery paths where a filesystem may have been mounted inside the engine container namespace.

### Important APIs, Types, And Functions
Path helpers are `GetFreezePointFromDevicePath`, `GetFreezePointFromVolumeName`, and `GetDevicePathFromVolumeName`. Runtime helpers are `FreezeFilesystem`, `UnfreezeFilesystem`, `UnfreezeAndUnmountFilesystem`, and `UnfreezeFilesystemForDevice`. Constants define `fsfreeze`, the not-frozen error substring, `/var/lib/longhorn/freeze`, the Longhorn device path prefix, and a five-second unfreeze timeout.

### Control Flow
Freeze runs `fsfreeze -f` with no timeout because the command cannot safely be cancelled. Unfreeze runs `fsfreeze -u` with a short timeout and returns `(false, nil)` when the kernel reports the filesystem was not frozen. `UnfreezeAndUnmountFilesystem` unfreezes then calls Kubernetes mount cleanup. `UnfreezeFilesystemForDevice` first checks the canonical freeze point, then scans all mount points for the device and unfreezes any matching mount without unmounting non-canonical mounts.

### State, Persistence, And Dependencies
The file manipulates mount state and frozen filesystem state, not repository state. It depends on Longhorn device paths from `go-iscsi-helper`, common-libs exec interfaces, Kubernetes `mount-utils`, `fs` error matching, and logrus.

### Integration Points
Engine shutdown and frontend cleanup flows can call these helpers to release frozen filesystems before device teardown. Tests can inject fake executors and mounters through the function parameters.

### Risks
`fsfreeze` behavior is kernel/device dependent. A timeout on unfreeze may mean the kernel is still waiting for I/O errors, and the process may continue beyond the helper return. Error detection relies on the string `Invalid argument` for not-frozen state. Namespace assumptions depend on `/host` mount propagation.

### Test Signals
Tests should cover nil executor/mounter defaults, not-frozen errors, timeout errors, canonical mount cleanup, fallback mount scanning, empty volume/device names, and warning paths when mount-point checks fail.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/fsfreeze.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/once.go -->
## sources/control-plane/longhorn-engine/pkg/util/once.go

### Purpose
`once.go` implements a retryable variant of `sync.Once`: the guarded function is considered done only after it returns nil.

### Important APIs, Types, And Functions
`Once` stores an atomic `done` flag and a mutex. `Do(f func() error) error` provides the fast path for already-successful execution. `doSlow` serializes callers, invokes `f` only while `done == 0`, and stores `done = 1` after successful execution.

### Control Flow
Concurrent callers first atomically check `done`. If not done, one caller enters the mutex and runs `f`. A non-nil error is returned and leaves `done` unset, allowing future calls to retry. A nil error schedules the atomic store before returning; later calls skip `f`.

### State, Persistence, And Dependencies
State is in-memory only. Dependencies are `sync` and `sync/atomic`.

### Integration Points
This helper is useful for initialization paths that may fail transiently and should be retried rather than permanently poisoning a `sync.Once`.

### Risks
`Once` must not be copied after use. The guarded function runs while holding the mutex, so it should avoid recursive calls to the same `Once` and long blocking operations unless intentional.

### Test Signals
Tests should prove failed first calls can retry, successful calls run only once, and concurrent callers do not race the guarded function.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/once.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/once_test.go -->
## sources/control-plane/longhorn-engine/pkg/util/once_test.go

### Purpose
`once_test.go` validates the retryable `Once` behavior implemented in `once.go`.

### Important APIs, Types, And Functions
`TestOnce` uses the shared gocheck `TestSuite`. It defines a counter and a function that fails only on the first call. It calls `once.Do` twice serially, then ten times concurrently through a `sync.WaitGroup`.

### Control Flow
The first `Do` call increments the counter and returns an error, proving failure does not set `done`. The second call succeeds and sets `done`. Concurrent calls then assert `Do` returns nil and the counter remains `1`, proving the successful execution is not repeated.

### State, Persistence, And Dependencies
The test uses in-memory state only. Dependencies are `fmt`, `sync`, and `gopkg.in/check.v1`.

### Integration Points
The test belongs to the shared util test suite initialized in `util_test.go`.

### Risks
The test relies on the counter being accessed only inside the guarded function before success; it does not stress multiple concurrent failing callers.

### Test Signals
Passing this test signals correct retry-after-failure and once-after-success behavior. Additional tests could cover high-concurrency first-call failure and recursive use deadlock expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/once_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/shared_timeouts.go -->
## sources/control-plane/longhorn-engine/pkg/util/shared_timeouts.go

### Purpose
`shared_timeouts.go` implements a shared timeout policy for groups of goroutines where all workers may eventually time out, but the last remaining worker should be allowed a longer grace period.

### Important APIs, Types, And Functions
`SharedTimeouts` stores `shortTimeout`, `longTimeout`, and `numConsumers` under an `RWMutex`. `NewSharedTimeouts` constructs it. `Increment` and `Decrement` adjust consumers. `CheckAndDecrement(duration)` returns `longTimeout` if the duration exceeds the long limit, returns `shortTimeout` only when the duration exceeds the short limit and more than one consumer remains, and otherwise returns zero.

### Control Flow
Callers register with `Increment`, periodically compute their elapsed duration, and call `CheckAndDecrement`. A positive result means the caller must perform timeout handling and is removed from the consumer count. Short timeout is reserved for non-last consumers; the final consumer can wait until the long timeout.

### State, Persistence, And Dependencies
State is in-memory and protected by a mutex. Dependencies are `sync` and `time`. The concrete type implements the `types.SharedTimeouts` interface without importing engine types.

### Integration Points
The helper supports backend or IO flows where concurrent operations share failure budget. It is tested from `util_test.go`.

### Risks
`Decrement` and `CheckAndDecrement` can drive `numConsumers` negative if callers double-decrement or skip registration. The function does not record which consumer timed out, so correctness is caller-discipline based.

### Test Signals
Tests should cover short-timeout behavior with multiple consumers, long-timeout behavior for the final consumer, concurrent checks, and consumer count invariants.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/shared_timeouts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/util.go -->
## sources/control-plane/longhorn-engine/pkg/util/util.go

### Purpose
`util.go` collects general Longhorn engine helpers for address parsing, HTTP logging filtering, device node duplication/removal, volume name validation, file allocation statistics, label parsing, backup URL handling, backing file resolution, data-server address selection, and ID generation.

### Important APIs, Types, And Functions
Address helpers include `ParseAddresses`, `GetGRPCAddress`, `GetPortFromAddress`, and `GetAddresses`. Generic helpers include `Filter`, `Now`, `UUID`, and `RandomID`. HTTP handling is implemented by `FilteredLoggingHandler` and `filteredLoggingHandler.ServeHTTP`. Device helpers are `DuplicateDevice`, private `mknod`, `RemoveDevice`, `removeAsync`, and `remove`. File helpers are `GetFileActualSize`, `GetHeadFileModifyTimeAndSize`, and `ResolveBackingFilepath`. Validation and parsing helpers include `ValidVolumeName`, `Volume2ISCSIName`, `ParseLabels`, `UnescapeURL`, and `CheckBackupType`.

### Control Flow
`ParseAddresses` requires a host:port and derives control, data, and sync addresses by incrementing ports. `GetAddresses` switches between TCP and UNIX data-server protocols, using a host-mounted socket path for UNIX while still returning control and sync addresses. `FilteredLoggingHandler` bypasses combined logging for configured GET paths. Device removal runs asynchronously with a 30-second timeout to avoid hanging callers. `ResolveBackingFilepath` returns a path directly for files, or requires a directory to contain exactly one non-directory file.

### State, Persistence, And Dependencies
The file manipulates OS device nodes and reads file stat allocation data but stores no internal state. It depends on `net`, `http`, `url`, `os`, `syscall`, `unix`, gorilla handlers, logrus, Google UUIDs, and local `types`.

### Integration Points
Engine startup, frontend setup, backup restore, replica file accounting, CLI parsing, and HTTP servers use these helpers. `ParseLabels` integrates with Kubernetes-style validation from `validation.go`.

### Risks
`ParseAddresses` ignores `Atoi` errors after `SplitHostPort`, so malformed numeric ports can turn into zero-derived ports. Device major/minor calculation is Linux-specific. `remove` can leave a still-running goroutine if `os.Remove` blocks beyond the timeout. `UnescapeURL` only replaces the first escaped ampersand form of each pattern. `RandomID` assumes UUID string length is sufficient and uses a typoed constant name `randomIDLenth`.

### Test Signals
Existing tests cover label parsing, backing file resolution, and shared timeouts. Additional focused tests should cover address parsing invalid ports, UNIX socket address output, filtered logging behavior, device removal timeout with fakes, actual-size stat behavior, and URL unescaping edge cases.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/util_test.go -->
## sources/control-plane/longhorn-engine/pkg/util/util_test.go

### Purpose
`util_test.go` initializes the util package gocheck suite and validates label parsing, backing filepath resolution, and shared timeout behavior.

### Important APIs, Types, And Functions
`Test` connects gocheck to Go's testing package. `TestSuite` is registered as the suite. Helper functions `createTempDir` and `touchFile` create filesystem fixtures. Tests include `TestParseLabels`, `TestResolveFilepathNoOp`, `TestResolveFilepathFromDirectory`, `TestResolveFilepathTooManyFiles`, `TestResolveFilepathSubdirectory`, and `TestSharedTimeouts`.

### Control Flow
Label tests check empty input, multiple valid labels, invalid key rejection, permissive value contents, and single label output. Backing-file tests verify file passthrough, single-file directory resolution, multi-file rejection, and subdirectory rejection. Shared timeout tests register consumers concurrently, check below-short timeout no-op behavior, explicitly decrement one consumer, then concurrently verify only one of two consumers gets the short timeout before the final consumer gets the long timeout.

### State, Persistence, And Dependencies
Tests create temporary directories and files but do not clean them explicitly. Dependencies are `os`, `filepath`, `sync`, `atomic`, `testing`, `time`, and gocheck.

### Integration Points
These tests exercise `util.go`, `shared_timeouts.go`, and the Kubernetes-derived validation helper indirectly through `ParseLabels`.

### Risks
The shared timeout test prints durations to stdout, which is noisy but harmless. Temporary directories are not removed. Tests do not cover address parsing, device helpers, or URL parsing.

### Test Signals
Passing tests signal core label and backing-file behavior. Missing coverage remains around OS device operations and network address helpers.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/validation.go -->
## sources/control-plane/longhorn-engine/pkg/util/validation.go

### Purpose
`validation.go` vendors Kubernetes-style qualified-name and DNS-1123 subdomain validation for Longhorn label keys.

### Important APIs, Types, And Functions
Constants define qualified-name regex fragments, error messages, maximum name length, DNS label/subdomain regexes, and max subdomain length. `IsQualifiedName` validates optional `prefix/name` strings. `IsDNS1123Subdomain` validates DNS prefixes. `MaxLenError`, `RegexError`, `EmptyError`, and `prefixEach` format error messages.

### Control Flow
`IsQualifiedName` splits on `/`, validates optional prefix through DNS-1123 rules, validates non-empty and max-length name parts, then applies the qualified-name regexp. More than one slash returns a combined qualified-name error. DNS validation checks length then regex.

### State, Persistence, And Dependencies
There is no state beyond compiled regex values. Dependencies are `fmt`, `regexp`, and `strings`.

### Integration Points
`ParseLabels` in `util.go` uses `IsQualifiedName` for label keys. The logic mirrors Kubernetes validation, making Longhorn labels compatible with Kubernetes naming expectations.

### Risks
The file is copied code; future Kubernetes validation changes will not arrive automatically. Error text may be used in tests or user output, so wording changes can be externally visible.

### Test Signals
Tests should include valid names, invalid start/end characters, too-long names, valid and invalid DNS prefixes, empty parts, and multiple slash cases.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/util/validation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/renovate.json -->
## sources/control-plane/longhorn-engine/renovate.json

### Purpose
`renovate.json` configures Renovate dependency update behavior for the Longhorn engine repository.

### Important APIs, Types, And Functions
The config extends `github>longhorn/release:renovate-default`. A package rule disables updates for `github.com/rancher/go-rancher` on `master`, `main`, and version branches matching `v<major>.<minor>.x`.

### Control Flow
Renovate reads this JSON, inherits the shared Longhorn release defaults, then applies the local rule when package name and base branch match.

### State, Persistence, And Dependencies
The file persists repository automation policy. It depends on Renovate's config schema and the shared Longhorn release preset.

### Integration Points
GitHub Renovate runs use this file to decide whether to open dependency update PRs. It coordinates with `.github/mergify.yml`, which can auto-approve and merge Renovate PRs.

### Risks
The disabled package rule can leave `go-rancher` stale across all active branches. If the shared preset changes, inherited behavior changes without local file edits.

### Test Signals
Validation is mainly Renovate config validation and observing Renovate dry-run logs for expected disabled updates.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/renovate.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/ci -->
## sources/control-plane/longhorn-engine/scripts/ci

### Purpose
`scripts/ci` is the top-level local CI orchestrator for longhorn-engine.

### Important APIs, Types, And Functions
It accepts `SKIP_TASKS` as a space-delimited environment variable and defines the ordered task list: `build`, `validate`, `sync-grpc-py`, `test`, `integration-test`, and `package`.

### Control Flow
The script changes to the scripts directory, splits `SKIP_TASKS`, iterates over tasks, skips matching names, and executes each task script. `set -e` stops on the first failed task.

### State, Persistence, And Dependencies
It writes no state itself. Downstream scripts build binaries, run tests, sync generated files, and build images. It depends on bash and sibling executable scripts.

### Integration Points
`scripts/release` delegates directly to this script. CI jobs and developer workflows can set `SKIP_TASKS` to shorten runs.

### Risks
Task names must match exactly. Skipping critical tasks can hide failures. Since the script runs from `scripts`, sibling scripts must remain executable and relative paths must be stable.

### Test Signals
A smoke test can run with `SKIP_TASKS` covering all tasks to verify skip parsing, and CI runs verify downstream task order.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/ci -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/entry -->
## sources/control-plane/longhorn-engine/scripts/entry

### Purpose
`scripts/entry` is a container/developer entrypoint wrapper that forces vendored Go module mode and dispatches to repository scripts when the first argument names one.

### Important APIs, Types, And Functions
The script exports `GOFLAGS=-mod=vendor`, creates `bin`, then checks `./scripts/$1`. If present, it executes the script with all arguments; otherwise it executes the requested command directly.

### Control Flow
`set -e` fails fast. Dispatch is positional: `entry build` runs `./scripts/build`, while `entry bash` runs `bash`.

### State, Persistence, And Dependencies
It creates `bin/` and sets process environment. It depends on bash and the repository layout.

### Integration Points
This wrapper is suitable for Docker entrypoints and CI shells that need consistent vendored Go builds.

### Risks
If `$1` is empty, `[ -e ./scripts/$1 ]` tests the scripts directory and may attempt to run it with an empty command. Callers should pass a command.

### Test Signals
Smoke tests should verify script dispatch, direct command dispatch, and `GOFLAGS` propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/entry -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/integration-test -->
## sources/control-plane/longhorn-engine/scripts/integration-test

### Purpose
`scripts/integration-test` prepares and runs Longhorn engine integration tests inside an environment with instance managers, iSCSI tools, MinIO backup targets, backing files, and built engine binaries.

### Important APIs, Types, And Functions
The script creates a unique `TESTPREFIX`, defines `cleanupISCSI`, prepares backing/fixed directories, ensures `bin/longhorn` exists, bind-mounts `/host/dev` into `/dev` when available, exports S3 backup credentials and test certificates, creates raw/qcow2 backing files, copies engine binaries into instance-manager-accepted directories, starts two `longhorn-instance-manager` daemons, starts MinIO, sets `BACKUPTARGETS`, cleans Python caches, and runs `tox` in `integration` unless `NO_TEST` is set.

### Control Flow
`set -e` aborts on failures. Multiple `trap` registrations handle temporary directory cleanup and later instance-manager/iSCSI cleanup. The script starts background services, validates their PIDs with `ps`, then runs tests.

### State, Persistence, And Dependencies
It creates and removes `/tmp` replica directories, `/engine-binaries` content, `~/.minio/certs`, `/data/backupbucket`, and MinIO/instance-manager processes. Dependencies include `uuidgen`, `nsenter`, `iscsiadm`, `qemu-img`, `longhorn-instance-manager`, `minio`, `tox`, Python integration tests, and root-level mount permissions.

### Integration Points
This is the most complete local signal for engine behavior: rebuild, backup/restore, backing image, live upgrade, iSCSI, and instance-manager interactions.

### Risks
It assumes privileged container/host layout, can mount `/host/dev`, starts services on fixed ports, and writes fixed host paths. Cleanup depends on traps and can leave processes or iSCSI sessions if killed forcefully. Embedded test certificates are static and only for local MinIO.

### Test Signals
Successful `tox` completion is the primary signal. Setup failures around instance managers, MinIO, qemu conversion, or iSCSI cleanup indicate environmental rather than unit-code failures.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/integration-test -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/package -->
## sources/control-plane/longhorn-engine/scripts/package

### Purpose
`scripts/package` builds the Longhorn engine container image using Docker Buildx, optionally pushing and producing SBOM/provenance attestations.

### Important APIs, Types, And Functions
It sources `scripts/version`, then reads environment parameters including `REPO`, `IMAGE_NAME`, `TAG`, `PUSH`, `IS_SECURE`, `MACHINE`, `TARGET_PLATFORMS`, `IID_FILE`, `IID_FILE_FLAG`, `SRC_BRANCH`, and `SRC_TAG`. It selects `buildx` or `docker buildx`, detects architecture from `TARGET_PLATFORMS` or `uname -m`, builds Docker args, ensures binaries exist, pulls base images, runs buildx, and writes `bin/latest_image`.

### Control Flow
The script chooses `--push` or `--load`, optionally adds `--sbom` and provenance, computes `ARCH`, and runs a no-cache build of `package/Dockerfile`. It exits on unsupported architecture or command failure.

### State, Persistence, And Dependencies
It creates/updates `bin/latest_image`, may run `make build`, pulls base images, and builds local or remote images. Dependencies are Docker Buildx, Docker daemon, `grep`, `awk`, make, and the package Dockerfile.

### Integration Points
CI release flows and local packaging use this script. `scripts/ci` includes it after tests.

### Risks
The variable `IAMGE` is misspelled but consistently used; changing it carelessly can break tagging. Base images are always pulled, so builds depend on network availability. `TARGET_PLATFORMS` parsing assumes one `os/arch` pair, not comma-separated multi-platform lists.

### Test Signals
Signals include successful local `--load` image builds, pushed images for release, correct `bin/latest_image`, and expected provenance/SBOM output when `IS_SECURE=true`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/package -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/release -->
## sources/control-plane/longhorn-engine/scripts/release

### Purpose
`scripts/release` is a thin release entrypoint that delegates to the full CI script.

### Important APIs, Types, And Functions
It contains only a bash shebang and `exec $(dirname $0)/ci`.

### Control Flow
`exec` replaces the shell with `scripts/ci`, preserving arguments and environment.

### State, Persistence, And Dependencies
It writes no state and depends entirely on `scripts/ci`.

### Integration Points
Release automation can call a semantically named script while reusing the same build/validate/test/package pipeline.

### Risks
There is no separate release-specific validation. Any release behavior must be implemented in `ci` or downstream scripts.

### Test Signals
Running `scripts/release` should behave exactly like `scripts/ci`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/release -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/sync-grpc-py -->
## sources/control-plane/longhorn-engine/scripts/sync-grpc-py

### Purpose
`scripts/sync-grpc-py` verifies that Python gRPC generated code used by integration tests is synchronized with the `longhorn/types` repository.

### Important APIs, Types, And Functions
The script clones `https://github.com/longhorn/types.git` into `tmp-longhorn-types`, copies `generated-py/` into `integration/rpc`, removes the temporary clone, then checks `git diff --stat` for `_pb2.py` and `_pb2_grpc.py` changes.

### Control Flow
`set -e` is temporarily relaxed around the diff pipeline so it can inspect grep status. If generated Python files differ, it prints the diff stat and exits with failure.

### State, Persistence, And Dependencies
It writes `integration/rpc`, creates/removes `tmp-longhorn-types`, and depends on git and network access.

### Integration Points
`scripts/ci` runs this before tests, enforcing generated client compatibility for integration RPC code.

### Risks
It tracks the default branch of `longhorn/types`, so CI can fail due to upstream changes unrelated to this repository. A failed clone before cleanup can leave a temporary directory.

### Test Signals
No diff after sync is the success signal. A diff in generated Python files means the repository needs updated generated artifacts.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/sync-grpc-py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/test -->
## sources/control-plane/longhorn-engine/scripts/test

### Purpose
`scripts/test` runs Go unit tests for all non-vendor Longhorn engine packages and collects coverage.

### Important APIs, Types, And Functions
It discovers package directories by finding `.go` files, excluding `.git`, `.trash-cache`, `vendor`, and `bin`. It enables `-race` only when `ARCH=amd64` and runs `go test` with `-coverprofile=coverage.out` and tags `test qcow`.

### Control Flow
The script prints the package list, computes race options, and exits on any `go test` failure.

### State, Persistence, And Dependencies
It writes `coverage.out` and uses Go tooling. It depends on package discovery through Unix `find`, `xargs`, `dirname`, `sort`, and `grep`.

### Integration Points
`scripts/ci` runs this after validation and generated-code sync.

### Risks
Package discovery can include generated or experimental directories if they contain `.go` files outside excluded paths. Race coverage is architecture-gated by `ARCH`, not by actual `go env GOARCH`.

### Test Signals
Successful `go test` with coverage output is the signal. Race failures on amd64 should be treated as real concurrency issues unless environment-specific.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/test -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/validate -->
## sources/control-plane/longhorn-engine/scripts/validate

### Purpose
`scripts/validate` runs static validation for Longhorn engine Go packages.

### Important APIs, Types, And Functions
It discovers top-level Go package roots, expands them to `./<root>/...`, then runs `go vet`, `golangci-lint run --timeout=5m`, and `go fmt`, failing if formatting changes would be produced.

### Control Flow
`set -e` stops at the first failure. The formatting check pipes `go fmt` output to stderr and requires it to be empty.

### State, Persistence, And Dependencies
It should not persist changes; `go fmt` can rewrite files if they are unformatted, but the script expects no output. Dependencies are Go, golangci-lint, and Unix discovery commands.

### Integration Points
`scripts/ci` runs validation before generated Python sync and tests.

### Risks
The package discovery compresses paths to first-level directories, so unusual nested module layouts may not be represented precisely. Running `go fmt` as a validator can modify files before failing.

### Test Signals
Success means vet, golangci-lint, and formatting are clean.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/validate -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/version -->
## sources/control-plane/longhorn-engine/scripts/version

### Purpose
`scripts/version` computes shell variables describing the current Longhorn engine source version for build and packaging scripts.

### Important APIs, Types, And Functions
It sets `DIRTY` when tracked files have uncommitted changes, `COMMIT` from `git rev-parse --short HEAD`, `GIT_TAG` from the first tag containing HEAD, `VERSION` from a clean containing tag or from commit plus dirty suffix, `GITCOMMIT` from the full hash, and `BUILDDATE` from UTC RFC3339 seconds with `T` separator.

### Control Flow
The script is intended to be sourced. It branches on clean tagged state versus commit-derived state.

### State, Persistence, And Dependencies
It writes no files, only shell variables. It depends on git and GNU `date --rfc-3339=seconds`.

### Integration Points
`scripts/package` sources it to determine image tags and build metadata.

### Risks
`git tag -l --contains HEAD | head -n 1` can choose an arbitrary tag when multiple tags contain a commit. Untracked files are ignored for dirty detection.

### Test Signals
Checks should verify clean tagged, clean untagged, and dirty tree outputs.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/scripts/version -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/update-longhorn-deps.sh -->
## sources/control-plane/longhorn-engine/update-longhorn-deps.sh

### Purpose
`update-longhorn-deps.sh` updates selected Longhorn Go dependencies to their `master` branches and refreshes module/vendor state.

### Important APIs, Types, And Functions
It runs `go get` for `github.com/longhorn/go-iscsi-helper@master`, `github.com/longhorn/sparse-tools@master`, and `github.com/longhorn/backupstore@master`, then runs `go mod tidy` and `go mod vendor`.

### Control Flow
The script is linear and has no `set -e`, so later commands may run after earlier failures depending on shell behavior.

### State, Persistence, And Dependencies
It mutates `go.mod`, `go.sum`, and `vendor/`. It depends on network access and Go modules.

### Integration Points
Maintainers use it to refresh Longhorn-internal dependencies before PRs.

### Risks
Tracking `master` can introduce unreviewed breaking changes. Lack of `set -e` can leave partially updated state. Vendor changes can be large and need validation.

### Test Signals
After running, `go mod tidy`, `go test`, `scripts/validate`, and integration tests should pass.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/update-longhorn-deps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/version.go -->
## sources/control-plane/longhorn-engine/version.go

### Purpose
`version.go` implements the Longhorn engine CLI `version` command.

### Important APIs, Types, And Functions
`VersionCmd` returns a `cli.Command` named `version` with a `--client-only` flag. `VersionOutput` contains `ClientVersion` and optional `ServerVersion` fields. `version` obtains local build metadata from `meta.GetVersion`, optionally connects to the controller using global `url`, `volume-name`, and `engine-instance-name`, fetches server version detail, and prints indented JSON.

### Control Flow
The command action calls `version` and logs fatally on error. When `client-only` is false, it creates a controller client, defers close with logging, calls `VersionDetailGet`, and includes the result. JSON marshal failure is returned.

### State, Persistence, And Dependencies
It reads build metadata and remote controller state but writes only stdout. Dependencies are `urfave/cli`, `encoding/json`, logrus, controller client, and `meta`.

### Integration Points
This CLI command helps users compare client binary version with running engine controller version.

### Risks
Without `--client-only`, the command depends on a reachable controller and correct global flags. Fatal logging exits the process from the action wrapper.

### Test Signals
Tests should cover client-only JSON output, remote server version inclusion with a fake controller client, and error propagation for connection/version failures.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/bug.yaml -->
## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/bug.yaml

### Purpose
`bug.yaml` defines the GitHub issue form for Longhorn bug reports.

### Important APIs, Types, And Functions
The template sets title prefix `[BUG]`, issue type `Bug`, labels `kind/bug`, `require/qa-review-coverage`, and `require/backport`, and contains required fields for bug description, expected behavior, support bundle, and environment. Optional fields cover reproduction, additional context, and workaround/mitigation.

### Control Flow
GitHub renders the YAML as a structured issue form when users choose "Bug report". Required validations block submission until core fields are provided.

### State, Persistence, And Dependencies
It persists issue metadata defaults and form schema. Dependencies are GitHub issue forms and the label/type names configured in the repository.

### Integration Points
Issue automation workflows consume labels and issue type to add projects, create backport tasks, and update sprint state.

### Risks
Required support bundles can discourage reports when users cannot generate one. Label changes can trigger automation unexpectedly. The empty assignee entry is inert but odd.

### Test Signals
Validation is through GitHub issue form rendering and checking newly created bug issues have expected labels/type/title prefix.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/bug.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/config.yml -->
## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/config.yml

### Purpose
`config.yml` configures repository issue-template behavior.

### Important APIs, Types, And Functions
It disables blank issues and provides a contact link to GitHub Discussions for usage questions.

### Control Flow
GitHub reads this file when presenting issue creation choices. Users cannot open a blank issue through the standard UI.

### State, Persistence, And Dependencies
It persists repository issue intake policy and depends on GitHub issue-template config syntax.

### Integration Points
Structured issue forms and issue-management automations rely on users selecting one of the defined templates rather than bypassing metadata.

### Risks
Disabling blank issues can block legitimate reports that do not fit templates. The discussion link must remain valid.

### Test Signals
Manual GitHub UI verification should show no blank issue option and the Discussions contact link.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/epic.yaml -->
## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/epic.yaml

### Purpose
`epic.yaml` defines the issue form for grouping features, enhancements, or tasks under an Epic.

### Important APIs, Types, And Functions
It sets title prefix `[EPIC]`, issue type `Epic`, label `Epic`, and asks for problem context, task breakdown, and optional additional context.

### Control Flow
GitHub renders required textareas for problem and tasks; submission creates an Epic issue with the configured metadata.

### State, Persistence, And Dependencies
The file persists issue intake schema and depends on GitHub issue type/label configuration.

### Integration Points
Epic issues can be linked manually to child issues and may be picked up by project automation through labels or type.

### Risks
The template asks users to create sub-task issues but does not automate that linkage. The `assignees` list has an empty item.

### Test Signals
Create-form rendering and resulting issue metadata are the main validation signals.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/epic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/feature.yaml -->
## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/feature.yaml

### Purpose
`feature.yaml` defines the GitHub issue form for new Longhorn feature requests.

### Important APIs, Types, And Functions
It sets title prefix `[FEATURE]`, issue type `Feature`, and labels `kind/feature`, `require/lep`, `require/doc`, `require/auto-e2e-test`, and `require/manual-test-plan`. It includes problem, desired solution, alternatives, and additional context fields.

### Control Flow
Only the problem field is required. Labels drive downstream automation for documentation, test planning, LEP requirements, and automation-test issue creation.

### State, Persistence, And Dependencies
The template persists metadata defaults and depends on GitHub issue form schema plus repository labels.

### Integration Points
`create-issue.yml` watches `require/auto-e2e-test`; other issue workflows add project status and milestones.

### Risks
Defaulting every feature to automation and manual test requirements can create follow-up noise for non-testable features. Label renames would break automation.

### Test Signals
New feature issues should get the expected type, labels, and title prefix; auto-test issue automation should trigger when labels are applied.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/feature.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/improvement.yaml -->
## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/improvement.yaml

### Purpose
`improvement.yaml` defines the issue form for improvements to existing Longhorn features.

### Important APIs, Types, And Functions
It sets title prefix `[IMPROVEMENT]`, issue type `Improvement`, labels `kind/improvement`, `require/doc`, `require/manual-test-plan`, and `require/backport`, and asks for related feature/problem, desired solution, alternatives, and additional context.

### Control Flow
GitHub enforces the related-feature/problem field as required and applies default metadata at issue creation.

### State, Persistence, And Dependencies
It persists issue intake schema and depends on configured labels and issue types.

### Integration Points
Default backport and documentation/test labels feed issue management workflows and release planning.

### Risks
Automatically requiring backports for all improvements may create unnecessary backport tasks. Empty assignee entry is harmless but untidy.

### Test Signals
Issue form rendering and metadata on created improvement issues validate the file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/improvement.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/mergify.yml -->
## sources/control-plane/longhorn/.github/mergify.yml

### Purpose
`mergify.yml` configures automated PR approval, merge, and conflict notification rules for the Longhorn repository.

### Important APIs, Types, And Functions
Rules merge PRs with successful Drone CI, at least two approvals, and approval by `@longhorn/maintainer`; merge bot PRs from Renovate or Mergify after Drone CI; auto-approve Renovate PRs; and comment on conflicting PRs.

### Control Flow
Mergify evaluates rules against PR state and runs `merge`, `review`, or `comment` actions when conditions match.

### State, Persistence, And Dependencies
The file persists merge policy and depends on Mergify, the Drone status name `continuous-integration/drone/pr`, GitHub review data, and team membership.

### Integration Points
It interacts with Renovate config and branch protection. Auto-merge uses rebase strategy.

### Risks
Status check name drift will disable merges. Auto-approving bot PRs relies on Renovate policy being safe. Conflict comments can be noisy.

### Test Signals
Observe Mergify dry-run/dashboard rule matches and successful auto-merge of eligible bot and maintainer-approved PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/mergify.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/add-issue-to-projects.yml -->
## sources/control-plane/longhorn/.github/workflows/add-issue-to-projects.yml

### Purpose
This workflow adds opened, reopened, or milestoned issues to the correct Longhorn GitHub Projects for Longhorn members, community reporters, and QA/devops items.

### Important APIs, Types, And Functions
It has three jobs: `longhorn`, `community`, and `qa`. Each creates a GitHub App token. Membership checks use `tspascoal/get-user-teams-membership`, issue/project operations use `actions/add-to-project`, `octokit/request-action`, and `titoportas/update-project-fields`.

### Control Flow
The Longhorn job treats `github-actions[bot]` as a member, otherwise checks org teams, then adds member-created non-test issues to project 8. The community job adds non-member issues to project 5 and sets `Status,Sprint` to `New,[0]`. The QA job adds member issues labeled `kind/test` or `area/infra` to project 4.

### State, Persistence, And Dependencies
It mutates GitHub Projects and uses organization membership data. It depends on app secrets, pinned actions, project URLs, labels, and project fields.

### Integration Points
Works with issue templates that apply labels and with update workflows that later move project status.

### Risks
Membership outcome handling differs between jobs. Project number/field changes break updates. App-token permissions are broad but necessary for projects.

### Test Signals
Test by opening issues as member, bot, and non-member with/without QA labels and verifying project placement and fields.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/add-issue-to-projects.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/backport-pr.yml -->
## sources/control-plane/longhorn/.github/workflows/backport-pr.yml

### Purpose
This workflow links backport pull requests opened against `master` or version branches to existing backport issues.

### Important APIs, Types, And Functions
It checks out the repo, detects PR titles containing `backport #`, extracts the base branch and original issue number from the PR body, detects fork PRs, creates an app token for fork cases, and uses `gh`, `curl`, and `jq` to find and comment on the matching backport issue.

### Control Flow
Only forked backport PRs with an original issue number continue to linking. Branch names have `.x` stripped and periods escaped for search. The workflow searches open issues with matching branch and original issue title, then comments with the PR URL.

### State, Persistence, And Dependencies
It writes issue comments. Dependencies include GitHub CLI, curl, jq, app secrets, and consistent backport PR body/title conventions.

### Integration Points
It complements `create-issue.yml`, which creates `[BACKPORT][vX.Y]...` issues from labels.

### Risks
The search query is title-based and can miss renamed issues or match the wrong issue. It only runs linking for fork PRs. PR body parsing expects `longhorn/longhorn#<number>`.

### Test Signals
Create a synthetic backport PR body referencing a source issue and confirm the expected backport issue receives a comment.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/backport-pr.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/check-sprint-last-day.py -->
## sources/control-plane/longhorn/.github/workflows/check-sprint-last-day.py

### Purpose
`check-sprint-last-day.py` determines whether the current date is the final day of the current iteration in a GitHub Projects v2 project.

### Important APIs, Types, And Functions
Functions are `get_github_project_info`, `get_current_sprint`, and `is_today_is_in_last_day_of_current_sprint`. It queries the GitHub GraphQL API for organization projects and iteration field configuration, treats each sprint as a 14-day interval, and exits 0 only on the last day.

### Control Flow
The script reads `GITHUB_TOKEN` and CLI args `github_org github_repo github_project`, finds the project by title, gets current iteration by comparing dates to `startDate + 13 days`, prints details, and exits 1 when not the last day.

### State, Persistence, And Dependencies
It persists nothing. Dependencies are `requests`, environment token, GraphQL schema for Projects v2, and local timezone/date of the runner.

### Integration Points
`periodic-issue-sprint-update.yml` calls it to gate sprint rollover operations.

### Risks
The `github_repo` argument is unused. It assumes the first iteration field is the sprint field and that sprints are exactly 14 days. Missing JSON fields can raise `AttributeError`.

### Test Signals
Unit tests with mocked GraphQL responses should cover current sprint detection, no sprint found, final day, non-final day, and API failure.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/check-sprint-last-day.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/close-issue.yml -->
## sources/control-plane/longhorn/.github/workflows/close-issue.yml

### Purpose
`close-issue.yml` closes generated backport or automation-test issues when their trigger labels are removed from the source issue.

### Important APIs, Types, And Functions
It reacts to `issues.unlabeled`. The `backport` job handles labels containing `backport/`; the `automation` job handles `require/automation-e2e`. It uses `xom9ikk/split` and `actions/github-script` to search generated issues and close matches.

### Control Flow
For backports, it builds a title search `[BACKPORT][v<version>]<source title>` and filters issues labeled `kind/backport` created by `github-actions[bot]`. For automation, it searches `[TEST]<source title>` issues labeled `kind/test` from the bot. Matching generated issues are closed.

### State, Persistence, And Dependencies
It mutates issue state and depends on generated title conventions, labels, and creator identity.

### Integration Points
It complements `create-issue.yml`, reversing generated issue lifecycle when labels are removed.

### Risks
Title-based matching can miss renamed generated issues or close the wrong issue if titles collide. The automation label checked is `require/automation-e2e`, while feature templates use `require/auto-e2e-test`, so naming drift is a risk.

### Test Signals
Remove backport and automation labels from test issues and verify the corresponding generated issues close.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/close-issue.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/codespell.yml -->
## sources/control-plane/longhorn/.github/workflows/codespell.yml

### Purpose
`codespell.yml` runs spelling checks on pull requests.

### Important APIs, Types, And Functions
It triggers on PRs to `master` and `v*.*.*` branches, checks out the repository, and runs `codespell-project/actions-codespell` with filename checking and skip patterns for YAML, scripts, vendor, maintainers, license, and Go module files.

### Control Flow
The action scans changed repository content according to codespell behavior and fails the job on detected spelling errors.

### State, Persistence, And Dependencies
It writes no repo state. Dependencies are the pinned checkout and codespell actions.

### Integration Points
The workflow acts as a PR management quality gate.

### Risks
The skip pattern excludes all YAML and scripts, leaving many user-facing texts unverified. Branch pattern `v*.*.*` may not match `vX.Y.x` maintenance branches.

### Test Signals
Introduce a known typo in a non-skipped file on a test PR and confirm the job fails.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/conventional-commits.yml -->
## sources/control-plane/longhorn/.github/workflows/conventional-commits.yml

### Purpose
This workflow enforces conventional commit messages and semantic PR titles.

### Important APIs, Types, And Functions
It runs on PR open/edit/synchronize/reopen with read permissions. It checks out full history, runs `wagoid/commitlint-github-action`, and runs `amannn/action-semantic-pull-request` allowing types such as `feat`, `fix`, `docs`, `test`, `chore`, `ci`, `revert`, and `BREAKING`.

### Control Flow
Both lint steps read PR commits/title and fail the job if format rules are violated.

### State, Persistence, And Dependencies
It writes no state. Dependencies are pinned actions and the default commitlint configuration provided by the action.

### Integration Points
It supports release note and changelog hygiene by normalizing commit and PR titles.

### Risks
Full history checkout can be slower. Allowed type list must stay aligned with repository conventions. The uppercase `BREAKING` type may or may not match semantic-release expectations.

### Test Signals
PRs with invalid titles or commit messages should fail; valid conventional commits should pass.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/conventional-commits.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/create-issue.yml -->
## sources/control-plane/longhorn/.github/workflows/create-issue.yml

### Purpose
`create-issue.yml` creates derived tracking issues when source issues receive labels for backports, automation tests, or UI work.

### Important APIs, Types, And Functions
The workflow has `backport`, `automation`, and `ui` jobs. It uses GitHub App tokens, team membership checks, `actions/github-script`, milestone lookup, label filtering shell snippets, `dacbd/create-issue-action`, Longhorn bot project actions, and `titoportas`/project field updates.

### Control Flow
For `backport/<version>` labels, member actions trigger lookup of existing `[BACKPORT][v<version>]` issues, milestone resolution, label filtering, assignee filtering to org members, issue creation or reopening, and project addition. For `require/auto-e2e-test`, it creates a `[TEST]` issue assigned to QA project. For `require/ui`, it creates a `[UI]` issue with `area/ui`, copied labels minus trigger labels, and the source milestone.

### State, Persistence, And Dependencies
It creates and reopens issues, sets labels/milestones/assignees, and adds project items. It depends on label names, issue title conventions, milestone names, app secrets, and project URLs.

### Integration Points
It is paired with `close-issue.yml` and issue templates that apply requirement labels by default.

### Risks
Title-based duplicate detection can fail after title edits. Milestone lookup for backports assumes `v<version>` exists. UI issue creation uses `github.event.issue.milestone.number`, which can be null if no milestone is present.

### Test Signals
Apply each trigger label to a member-created issue and verify generated issue metadata, duplicate prevention, reopening, project addition, and label filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/create-issue.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/create-release-task-issues.yml -->
## sources/control-plane/longhorn/.github/workflows/create-release-task-issues.yml

### Purpose
This manually dispatched workflow creates standard release task issues for a requested Longhorn release version.

### Important APIs, Types, And Functions
Inputs are `release_version`, `release_captain`, and `qa_captain`. The workflow creates an app token, checks out the repo, parses version metadata, validates `v<major>.<minor>.<patch>`, computes major-minor version, branch name, and feature-release flag, then invokes `rancher/gh-issue-mgr/create-an-issue` with release-related templates.

### Control Flow
Every release creates the main release task and security-fix task. Feature releases ending in `.0` also create regular feature-release tasks and performance benchmark tasks.

### State, Persistence, And Dependencies
It creates GitHub issues from templates and depends on app secrets, issue templates, version naming conventions, and the external issue manager action.

### Integration Points
Generated release issues feed release project tracking and captain assignments.

### Risks
Invalid input exits early. Template environment variable names must match template placeholders. Patch releases intentionally skip feature-release task templates.

### Test Signals
Manual dry runs with feature and patch versions should create the correct set of issues with expected env-substituted content.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/create-release-task-issues.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/periodic-issue-sprint-update.yml -->
## sources/control-plane/longhorn/.github/workflows/periodic-issue-sprint-update.yml

### Purpose
This workflow performs weekly sprint rollover updates for Longhorn GitHub Projects.

### Important APIs, Types, And Functions
It runs on Sunday 20:00 UTC and manual dispatch. It creates an app token, checks out the repository, runs `check-sprint-last-day.py`, and if that script succeeds, invokes `rancher/gh-issue-mgr/move-to-next-iteration` for Longhorn Sprint project 8, QA Sprint project 4, and Community Sprint project 5.

### Control Flow
The workflow gates all updates on being the last day of the current sprint. It clears current sprint values for items not in excluded statuses, moves `Review` items to next sprint, moves `Ready For Testing` items with no sprint into current sprint, and moves community `New` items to next sprint.

### State, Persistence, And Dependencies
It mutates GitHub Project iteration fields. Dependencies are app secrets, project numbers, field names `Sprint` and `Status`, status names, and the Python sprint checker.

### Integration Points
It coordinates with issue update workflows that add items and set statuses throughout the sprint.

### Risks
Incorrect sprint-date detection can skip or prematurely run rollover. Status name drift will leave items unchanged. Project-wide mutations are broad and should be monitored.

### Test Signals
Use workflow dispatch near a mocked or real sprint end and verify field updates on representative project items.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/periodic-issue-sprint-update.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/pr-review-reminder.py -->
## sources/control-plane/longhorn/.github/workflows/pr-review-reminder.py

### Purpose
`pr-review-reminder.py` gathers open PRs across Longhorn repositories and sends a Slack reminder listing requested reviewers.

### Important APIs, Types, And Functions
`REPOS` lists Longhorn repositories. `pr_review_reminder` runs `gh pr list` for each repo requesting number, title, author, review requests, and labels. `flatten_issues` formats Slack blocks in chunks of five PRs. `send_slack_notification` reads `SLACK_WEBHOOK_URL` and optional GitHub-to-Slack `USER_MAPPING`, then posts block-kit JSON with `requests`.

### Control Flow
The script skips bot-authored PRs and PRs labeled `pending`, collects reviewer logins, maps them to Slack mentions when possible, and sends one payload containing per-repo sections.

### State, Persistence, And Dependencies
It persists nothing. Dependencies are authenticated GitHub CLI, `requests`, Slack incoming webhook, and environment secrets.

### Integration Points
`pr-review-reminder.yml` schedules and runs the script after authenticating `gh`.

### Risks
A single Slack post can fail if block count or payload size grows too large, though chunks of five reduce section size. Repos with gh errors are skipped, which can hide missing reminders. The script prints payloads, potentially exposing PR metadata in logs.

### Test Signals
Mock `gh pr list` output and Slack responses to verify skip logic, reviewer mapping, chunking, and error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/pr-review-reminder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/pr-review-reminder.yml -->
## sources/control-plane/longhorn/.github/workflows/pr-review-reminder.yml

### Purpose
This workflow schedules and runs the PR review reminder Slack notification.

### Important APIs, Types, And Functions
It triggers manually and every Monday at 02:00 UTC, sets up Python 3, installs `requests`, creates a GitHub App token with read permissions, authenticates GitHub CLI, checks out the repository, and runs `.github/workflows/pr-review-reminder.py` with Slack and user-mapping secrets.

### Control Flow
The workflow prepares dependencies and credentials before invoking the Python script.

### State, Persistence, And Dependencies
It writes no repository state. It depends on app secrets, Slack webhook secret, user mapping secret, GitHub CLI availability, and pinned actions.

### Integration Points
It is the scheduler and runtime wrapper for `pr-review-reminder.py`.

### Risks
If `gh auth login` fails, the script cannot list PRs. Secret formatting for `USER_MAPPING` must be valid JSON. Schedule comment says GMT+8 and cron matches Monday 10:00 China time.

### Test Signals
Manual dispatch should post a Slack reminder or clearly fail on dependency/secret issues.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/pr-review-reminder.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/scan-and-notify-testing-items.py -->
## sources/control-plane/longhorn/.github/workflows/scan-and-notify-testing-items.py

### Purpose
`scan-and-notify-testing-items.py` scans a GitHub Projects v2 board for issues in testing-related statuses and sends a Slack reminder to QA.

### Important APIs, Types, And Functions
Functions include project lookup (`get_github_project_info`), current sprint detection (`get_current_sprint`, `is_today_is_in_last_day_of_current_sprint`), paginated project item listing (`list_issues_in_project`), Slack block formatting (`flatten_issues`), notification posting (`send_slack_notification`), and main orchestration (`scan_and_notify`).

### Control Flow
The script locates a project by title, determines the current sprint, paginates all project items with `Status` and `Sprint` fields, filters statuses `Ready For Testing` and `Testing`, splits results into current-sprint and non-current-sprint lists by sprint start date, formats assignee Slack mentions from optional JSON mapping, and posts a Slack message if any issues exist.

### State, Persistence, And Dependencies
It persists nothing. Dependencies are GitHub GraphQL API, `requests`, Slack webhook, `GITHUB_TOKEN`, `USER_MAPPING`, and specific project field names.

### Integration Points
`scan-and-notify-testing-items.yml` schedules the script. The commented-out last-day gate shows prior or planned coupling with sprint rollover timing.

### Risks
The code assumes every item has `status.name`; draft/non-issue items or missing fields can raise errors. It prints full project GraphQL responses. The current-sprint label text says "Previous Sprint" for `current_issues`, which may confuse recipients.

### Test Signals
Mock GraphQL pagination and Slack post calls to cover status filtering, sprint split, no-notification path, user mapping, and API error propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/scan-and-notify-testing-items.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/scan-and-notify-testing-items.yml -->
## sources/control-plane/longhorn/.github/workflows/scan-and-notify-testing-items.yml

### Purpose
This workflow schedules and runs the QA testing-item Slack scanner.

### Important APIs, Types, And Functions
It triggers every Sunday at 12:00 UTC and on manual dispatch with optional org/repo/project inputs. It creates a GitHub App token, checks out the repository, sets up Python, installs `requests`, resolves input defaults from environment variables, and runs `scan-and-notify-testing-items.py`.

### Control Flow
Manual inputs override default `longhorn`, `longhorn`, and `Longhorn Sprint` values. The script receives GitHub token, Slack webhook, and user mapping through environment.

### State, Persistence, And Dependencies
It writes no repo state. It depends on app secrets, Slack secrets, setup-python, checkout, and the Python script.

### Integration Points
It is the operational wrapper for `.github/workflows/scan-and-notify-testing-items.py`.

### Risks
The app token requests only contents/issues read permissions; Projects v2 access must be available through the app. Manual input expressions inside shell conditionals must remain valid for scheduled events.

### Test Signals
Manual dispatch with a test project should produce expected Slack output or no-op logs when no testing items exist.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/scan-and-notify-testing-items.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/scorecards.yml -->
## sources/control-plane/longhorn/.github/workflows/scorecards.yml

### Purpose
`scorecards.yml` runs OpenSSF Scorecard supply-chain security analysis.

### Important APIs, Types, And Functions
It triggers on branch protection rule changes, weekly schedule, and pushes to `master`. It sets default read-only permissions, grants the job `security-events: write` and `id-token: write`, checks out without persisted credentials, runs `ossf/scorecard-action` producing SARIF, uploads the SARIF artifact, and uploads it to GitHub code scanning.

### Control Flow
Scorecard writes `results.sarif`; subsequent steps publish it as an artifact and code-scanning result.

### State, Persistence, And Dependencies
It creates workflow artifacts and code-scanning alerts. Dependencies are pinned checkout, scorecard, upload-artifact, and codeql upload actions.

### Integration Points
Results feed GitHub security/code scanning and OpenSSF public score publication.

### Risks
`publish_results: true` exposes public score data. Branch protection checks may require optional PAT for full public-branch analysis, currently commented out.

### Test Signals
Successful scheduled run with uploaded SARIF and visible code-scanning results validates the workflow.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/scorecards.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/stale.yaml -->
## sources/control-plane/longhorn/.github/workflows/stale.yaml

### Purpose
`stale.yaml` marks inactive issues and PRs stale and closes them after a grace period.

### Important APIs, Types, And Functions
It triggers by workflow call, manual dispatch, and daily schedule. It runs `actions/stale` with separate issue/PR stale messages, close messages, stale labels, close label `wontfix`, 30 days before stale, 5 days before close, assignee exemptions, issue-label exemptions, draft PR exemption, and milestone exemption.

### Control Flow
The stale action scans issues/PRs, applies `stale`, and later closes eligible items while respecting exemptions.

### State, Persistence, And Dependencies
It mutates labels and issue/PR state. Dependencies are the pinned stale action and repository label names.

### Integration Points
The `wont-fix.yml` workflow also labels not-planned closures, so closed stale issues may share the `wontfix` label.

### Risks
Broad stale automation can close valid low-activity items unless they are assigned, milestoned, or exempt-labeled. Exempt label names must stay current.

### Test Signals
Dry-run or controlled test issues should verify stale label application and exemption behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/stale.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/update-branch-image-tags.yaml -->
## sources/control-plane/longhorn/.github/workflows/update-branch-image-tags.yaml

### Purpose
This release workflow updates Longhorn image tags in a repository branch to `<branch>-head`, regenerates manifests, and opens an auto-merge PR.

### Important APIs, Types, And Functions
It accepts a `branch` input, creates a GitHub App token, checks out that branch, installs `snapd` and `yq`, updates `deploy/longhorn-images.txt` via a shell `replace_images_tags` function, updates `chart/values.yaml` with `yq`, runs `scripts/generate-longhorn-yaml.sh`, creates a signed PR with `peter-evans/create-pull-request`, and enables automerge.

### Control Flow
The shell replacement scans lines for known `longhornio/*` images and rewrites tags. Chart values are updated field-by-field. Manifest regeneration then incorporates chart changes before PR creation.

### State, Persistence, And Dependencies
It mutates a branch through a generated PR. Dependencies are app secrets, snap/yq availability, chart values paths, deploy image list format, manifest generation script, and pinned PR actions.

### Integration Points
Used during release/branch maintenance to point deployment artifacts at branch-head images.

### Risks
The unused `repos_dir` and `modified` variable suggest script drift. Regex replacement is line-oriented and can mis-handle unusual image formats. Snap install can be slow or fail on GitHub runners.

### Test Signals
Manual dispatch on a test branch should produce a PR with expected image tag changes and regenerated manifests only.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/update-branch-image-tags.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/update-community-issue.yml -->
## sources/control-plane/longhorn/.github/workflows/update-community-issue.yml

### Purpose
`update-community-issue.yml` synchronizes community issue status, sprint, and milestone across GitHub Projects when issues or comments change.

### Important APIs, Types, And Functions
It triggers on issue labeled/milestoned/reopened/closed and issue comment created/edited events, with per-issue concurrency. It uses an app token, team membership check, project field lookup via `EndBug/project-fields`, `actions/add-to-project`, shell status decision logic, `titoportas/update-project-fields`, and `gh issue edit`.

### Control Flow
After membership and project-field checks, it adds the issue to community project 5. Member milestone events set `Resolved,[0]`; closed unresolved issues set `Closed`; reopened closed issues set `In Progress,[0]`; non-member comments on non-resolved/non-closed issues set `In Progress,[0]`; invalid/wontfix/duplicated labels set `Closed`. Resolved issues are also added to Longhorn Sprint project 8 and get Backlog milestone if missing.

### State, Persistence, And Dependencies
It mutates project fields, project membership, and milestones. Dependencies are project URLs, fields `Status,Sprint`, status values, app secrets, labels, and GitHub CLI.

### Integration Points
It complements add-issue and longhorn-issue workflows by managing community-reported issue lifecycle.

### Risks
The shell parses JSON-ish teams output by trimming brackets and splitting commas, which is fragile. The environment variable name `field-values` contains a hyphen; GitHub env supports it for expressions but shell variable access would be awkward. Project field lookup failures skip updates.

### Test Signals
Exercise each event branch with member/non-member actors and verify project fields, sprint, Longhorn project addition, and Backlog milestone behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/update-community-issue.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/update-longhorn-issue.yml -->
## sources/control-plane/longhorn/.github/workflows/update-longhorn-issue.yml

### Purpose
`update-longhorn-issue.yml` manages Longhorn member issue status in the Longhorn Sprint project.

### Important APIs, Types, And Functions
It triggers on issue labeled, milestoned, assigned, and unassigned events with per-issue concurrency. It creates an app token, treats `github-actions[bot]` as a member, checks real membership otherwise, fetches project `Status`, adds issues to Longhorn Sprint project 8, updates new project items to `New`, sets missing milestones to `Backlog` for real members, and conditionally applies `New Issues`.

### Control Flow
Only member-created issues proceed. The workflow avoids changing items already `Closed`. Assigned issues with empty or `New Issues` status stay/set `New Issues`; unassigned issues also set `New Issues`.

### State, Persistence, And Dependencies
It mutates project membership, project status, and milestones. Dependencies include app secrets, project URL, status field names, membership action, `gh`, and pinned project-field actions.

### Integration Points
Works with issue templates and add-issue workflow to keep Longhorn Sprint project populated and consistently staged.

### Risks
The initial `Update Item To New` can set `New` before later logic sets `New Issues`, causing extra project churn. Bot membership bypass affects generated issues. Status name changes break shell conditions.

### Test Signals
Member issue label/assignment/milestone events should add project items, set Backlog when missing, and avoid changing closed status.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/update-longhorn-issue.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/validate-yamls.yaml -->
## sources/control-plane/longhorn/.github/workflows/validate-yamls.yaml

### Purpose
`validate-yamls.yaml` validates selected Longhorn YAML files on pull requests.

### Important APIs, Types, And Functions
It triggers on PR open/edit/synchronize/reopen, checks out the repo, installs `yamllint`, creates a local `.yamllint` config extending defaults while disabling line length, trailing spaces, document start, and empty-line rules, then runs `yamllint -c .yamllint chart/questions.yaml`.

### Control Flow
The workflow fails when `yamllint` finds syntax or enabled rule violations in `chart/questions.yaml`.

### State, Persistence, And Dependencies
It writes a temporary `.yamllint` in the runner workspace only. Dependencies are apt, yamllint, and checkout.

### Integration Points
Protects Helm/Rancher question YAML from syntax regressions.

### Risks
Only `chart/questions.yaml` is validated despite the workflow name implying broader YAML coverage. Many style rules are disabled.

### Test Signals
PRs with invalid YAML in `chart/questions.yaml` should fail; valid YAML should pass.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/validate-yamls.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/wont-fix.yml -->
## sources/control-plane/longhorn/.github/workflows/wont-fix.yml

### Purpose
`wont-fix.yml` labels and demilestones issues closed as "not planned".

### Important APIs, Types, And Functions
It triggers on issue closure. `actions/github-script` checks `context.payload.issue.state_reason === "not_planned"`. If true, `actions-ecosystem/action-add-labels` adds `wontfix`, and another `github-script` clears the milestone.

### Control Flow
The second and third steps are conditional on the first step returning true.

### State, Persistence, And Dependencies
It mutates issue labels and milestone. Dependencies are GitHub issue `state_reason`, the `wontfix` label, and pinned actions.

### Integration Points
The label feeds community issue status automation, which treats `wontfix` as closed.

### Risks
Manual closures without not-planned reason are ignored. Clearing milestone may remove useful release context.

### Test Signals
Close a test issue as not planned and verify `wontfix` is added and milestone removed; close as completed and verify no change.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/.github/workflows/wont-fix.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/chart/Chart.yaml -->
## sources/control-plane/longhorn/chart/Chart.yaml

### Purpose
`Chart.yaml` defines the Longhorn Helm chart metadata.

### Important APIs, Types, And Functions
The chart is API version `v1`, named `longhorn`, with chart `version` and `appVersion` `1.12.0-dev`. It requires Kubernetes `>=1.25.0-0`, describes Longhorn as a distributed block storage system, lists keywords, project home, source repositories for Longhorn components, maintainer contact, and CNCF-hosted icon URL.

### Control Flow
Helm reads this metadata during chart packaging, dependency display, install validation, and repository indexing.

### State, Persistence, And Dependencies
The file persists release metadata for the chart. It depends on Helm chart schema, semantic versioning conventions, and valid component repository URLs.

### Integration Points
Chart packaging, Rancher catalog/app displays, and release workflows consume this metadata. Version fields should align with image tags and generated manifests.

### Risks
Version/appVersion drift can publish misleading charts. `apiVersion: v1` is older Helm chart metadata format. Kubernetes version constraints must stay aligned with actual template/API requirements.

### Test Signals
`helm lint`, chart packaging, install tests on supported Kubernetes versions, and release checks should validate this file.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/chart/Chart.yaml -->
