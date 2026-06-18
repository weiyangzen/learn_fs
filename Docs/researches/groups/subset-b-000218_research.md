# Research: subset-b-000218

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/daemonstore.go -->
## sources/cloud-native/nydus-snapshotter/pkg/store/daemonstore.go

Purpose: provides `DaemonRafsStore`, a narrow adapter that exposes daemon and RAFS instance persistence through the underlying Bolt-backed `Database`. It is the storage facade used by manager/recovery code so callers do not manipulate Bolt buckets directly.

Important APIs: `NewDaemonRafsStore`, `AddDaemon`, `UpdateDaemon`, `DeleteDaemon`, `WalkDaemons`, `CleanupDaemons`, `AddRafsInstance`, `UpdateRafsInstance`, `DeleteRafsInstance`, `WalkRafsInstances`, and `NextInstanceSeq`. Each method forwards to `Database` with `context.TODO()` for write helpers or passes the caller context for walkers/cleanup.

Control flow and state: the wrapper has no independent state beyond `db *Database`; persistence is entirely delegated to the `daemons` and `instances` buckets in `database.go`. Duplicate daemon insertion propagates `ErrAlreadyExists`; missing update/delete behavior follows database semantics.

Dependencies and integration: imports daemon and rafs domain types and is consumed by manager/filesystem recovery paths that need durable daemon process state and RAFS mount metadata.

Risks and test signals: the adapter itself is thin and untested directly; coverage comes from `database_test.go`. Risk lies in the silent use of `context.TODO()` on writes, which ignores caller cancellation/deadlines.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/daemonstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database.go -->
## sources/cloud-native/nydus-snapshotter/pkg/store/database.go

Purpose: implements the persistent BoltDB store for nydus daemon states and RAFS filesystem instances under `<root>/nydus.db`. It is the durable restart/recovery layer for snapshotter-managed daemons and mounted instances.

Important APIs/types: `Database`, `NewDatabase`, `Close`, daemon CRUD (`SaveDaemon`, `UpdateDaemon`, `DeleteDaemon`, `CleanupDaemons`, `WalkDaemons`), RAFS CRUD (`AddRafsInstance`, `UpdateRafsInstance`, `DeleteRafsInstance`, `WalkRafsInstances`), and `NextInstanceSeq`. Helpers define the `v1` root bucket, `version` key, `daemons` bucket, `instances` bucket, JSON `putObject/updateObject/getObject`, and directory creation.

Control flow and persistence: `NewDatabase` creates the root directory, opens Bolt with a four-second timeout, then `initDatabase` creates `v1/daemons` and `v1/instances`. If the old non-v1 layout is detected it invokes `tryTranslateRecords`; if version is `v1.0` it invokes `tryUpgradeRecords` to add daemon mode metadata and writes `v1.1`. Write APIs use Bolt update transactions and JSON serialize domain structs keyed by daemon ID or snapshot ID. `NextInstanceSeq` uses Bolt bucket sequence allocation.

Dependencies/integration: depends on bbolt, containerd logging, project `daemon`, `rafs`, and `errdefs`. `snapshot.NewSnapshotter` constructs it and passes it into manager/cache layers.

Risks and test signals: JSON schema changes must remain backward compatible. `DeleteDaemon`/`DeleteRafsInstance` do not report not-found as an error. `NextInstanceSeq` starts a manual transaction and only rolls back when its local `err` is non-nil, so future edits must preserve commit/rollback correctness. `database_test.go` covers daemon CRUD plus legacy translation/upgrade.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database_compat.go -->
## sources/cloud-native/nydus-snapshotter/pkg/store/database_compat.go

Purpose: migrates pre-v1 snapshotter database records into the current v1 daemon/RAFS schema and upgrades v1.0 daemon records to v1.1 by filling `DaemonMode`.

Important APIs/types: `SharedNydusDaemonID`, `CompatDaemon`, `WalkCompatDaemons`, `RedirectInstanceConfig`, `tryTranslateRecords`, and `tryUpgradeRecords`. `CompatDaemon` models legacy daemon rows with config/socket/log directories, snapshot/image IDs, fs driver, pid, and optional mount points.

Control flow and persistence: `WalkCompatDaemons` scans the legacy top-level `daemons` bucket. `tryTranslateRecords` first detects whether a shared daemon record exists. In shared mode it writes one shared daemon config state and converts per-instance records into `rafs.Rafs` entries pointing at the shared daemon, copying legacy config files into the new shared-daemon directory. In dedicated mode it writes one daemon and one RAFS instance per record. `tryUpgradeRecords` walks current daemons; if `DaemonMode` is missing it infers shared/dedicated from fs driver and mountpoint, updates each daemon, then writes `version=v1.1`.

Dependencies/integration: tightly coupled to `config` constants for fscache/fusedev and root mountpoint, plus `daemon.ConfigState` and `rafs.Rafs`. Called only from `Database.initDatabase`.

Risks and test signals: legacy optional pointer fields are dereferenced according to detected mode; malformed legacy rows can panic if required pointers are nil. Config file redirect failures are logged as warnings, not hard failures. `database_test.go` exercises both multiple dedicated daemon migration and shared daemon migration, including copied config files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database_compat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/store/database_test.go

Purpose: validates the BoltDB store and compatibility migration behavior for daemon and RAFS records.

Important tests/helpers: `Test_daemon` covers daemon insertion, duplicate rejection, deletion, walking, and cleanup. `TestLegacyRecordsMultipleDaemonModes` writes a legacy top-level `daemons` bucket with two fusedev dedicated records, opens the new database, and verifies migrated daemon states and RAFS instances. `TestLegacyRecordsSharedDaemonModes` writes fscache shared-mode legacy records and verifies one shared daemon, two RAFS instances, and redirected config files. Helpers include `prepareCompatTestConfig`, `writeLegacyDatabase`, `writeConfigFile`, `listDaemons`, and `listRafsInstances`.

Control flow and state: tests build temporary roots, manually seed legacy Bolt buckets, then rely on `NewDatabase` to trigger `initDatabase` migration/upgrade. They inspect results through public walkers rather than private buckets.

Dependencies/integration: uses bbolt directly to create old-format data and `config.ProcessConfigurations` to seed global config mode assumptions.

Risks and test signals: tests cover happy-path legacy records but not missing optional pointer fields, corrupted JSON, version key edge cases, or duplicate records generated during migration. They give strong regression signals for schema conversion and daemon mode inference.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor.go -->
## sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor.go

Purpose: supervises nydusd runtime state handoff for failover/live upgrade. It receives serialized daemon state plus a Unix file descriptor from an old daemon and can later send those resources to a new daemon over a per-daemon Unix socket.

Important APIs/types: `StatesStorage`, in-memory `MemStatesStorage`, `Supervisor`, socket helpers `recv`/`send`, `FetchDaemonStates`, `SendStatesTimeout`, `Sock`, `SupervisorsSet`, `NewSupervisorSet`, `NewSupervisor`, `GetSupervisor`, and `DestroySupervisor`. `Supervisor` stores ID, socket path, last FD, data storage, mutex, and a single-flight semaphore.

Control flow and state: `FetchDaemonStates` acquires a semaphore, listens on the supervisor socket, runs a caller trigger, accepts the daemon connection, reads data/oob control messages, parses Unix rights, and saves the data/FD atomically. `SendStatesTimeout` listens on the same socket and asynchronously sends the stored state and FD to a connecting daemon. Timeout modes close the listener to unblock `Accept`. `DestroySupervisor` removes the supervisor from the set and closes any held FD.

Dependencies/integration: uses Unix domain sockets, `unix.ParseSocketControlMessage`, `syscall.UnixRights`, errgroup, semaphore, and project error definitions. It is integrated through daemon manager upgrade/recovery paths and the system controller hot-upgrade flow.

Risks and test signals: FD lifecycle is delicate; `save` overwrites state and keeps only positive FDs, and `load` does not consume resources. `recv` requires at least one control message, so state-only transfers fail. Tests cover large multi-read state payloads, FD transfer, sendback, and timeout behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor_test.go

Purpose: validates supervisor Unix socket handoff behavior and timeout cleanup.

Important tests: `TestSupervisor` creates a supervisor set, sends a 2 MiB random state payload and a temp-file FD from a simulated nydusd connection, then invokes `SendStatesTimeout(0)` and verifies the takeover side receives identical data. `TestSupervisorTimeout` starts a timed sender, waits past the timeout, and asserts later connection to the socket fails.

Control flow and state: the test uses real Unix sockets under a temp directory and the package-level `send`/`recv` helpers, so it exercises control message parsing and multi-`ReadMsgUnix` loops. Cleanup removes temp dirs/files and destroys the supervisor.

Dependencies/integration: relies on `net.DialUnix`, `crypto/rand`, temp files, and testify assertions. It runs on platforms supporting Unix sockets and FD passing.

Risks and test signals: covers large payload and timeout paths, but does not assert FD identity/content, concurrent `FetchDaemonStates` semaphore behavior, or `DestroySupervisor` FD close side effects. It is still a high-value signal for live-upgrade state transfer regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/system/system.go -->
## sources/cloud-native/nydus-snapshotter/pkg/system/system.go

Purpose: implements the experimental Unix-socket HTTP system controller for snapshotter maintenance: daemon listing, backend inspection, prefetch configuration, and rolling nydusd hot upgrade.

Important APIs/types: endpoint constants, `Controller`, `upgradeRequest`, JSON error helpers, `daemonInfo`, `rafsInstanceInfo`, `NewSystemController`, `Run`, route handlers (`getBackend`, `setPrefetchConfiguration`, `describeDaemons`, `getDaemonRecords`, `upgradeDaemons`), `upgradeNydusDaemon`, `buildNextAPISocket`, and `upgradeNydusdWithSymlink`.

Control flow and state: construction removes any stale socket, resolves a Unix address, and registers Gorilla mux routes. `Run` listens on the Unix socket, chowns it, and closes on signal. `describeDaemons` walks managers and live daemons, collecting RAFS instances, RSS, fs read metrics, references, sockets, and supervisor paths. Upgrade locks each manager, starts a new daemon with `--upgrade`, asks the supervisor to send state, waits for INIT/READY, calls takeover/start APIs, unsubscribes/exits old daemon, subscribes the new daemon, updates manager state, and finally atomically replaces the configured nydusd binary path with a symlink to the requested source.

Dependencies/integration: depends on filesystem, manager, daemon APIs, metrics, prefetch, signals, and mux. It is started from `snapshot.NewSnapshotter` when system controller config is enabled.

Risks and test signals: `jsonResponse` writes status before setting content type. `getDaemonRecords` is unimplemented. `upgradeDaemons` defers manager unlock inside a loop, so multiple managers stay locked until handler return. `SubscribeDaemonEvent` error handling returns `json.InvalidUnmarshalError{}` rather than wrapping the actual error. Tests only cover socket name incrementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/system/system.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/system/system_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/system/system_test.go

Purpose: unit-tests the helper that derives the next nydusd API socket name during hot upgrade.

Important test: `TestBuildUpgradeSocket` checks `buildNextAPISocket` converts `api.sock` to `api1.sock`, and increments numeric suffixes for `api2.sock`, `api23.sock`, and `api222.sock`.

Control flow and state: the test is pure and does not construct a controller or touch sockets. It validates the expected string transformation path used by `upgradeNydusDaemon`.

Dependencies/integration: uses testify assertions only.

Risks and test signals: no negative cases are covered for invalid socket names, multi-dot names, or non-`api` prefixes. The system controller’s HTTP routes, daemon upgrade sequence, symlink replacement, and signal-driven server shutdown remain untested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/system/system_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/tarfs/tarfs.go -->
## sources/cloud-native/nydus-snapshotter/pkg/tarfs/tarfs.go

Purpose: manages tarfs conversion and mounting for ordinary OCI layers. It downloads layer blobs, converts tar streams into nydus tarfs bootstraps/data, merges layers into an image bootstrap, optionally exports block-device images with dm-verity labels, and mounts EROFS on the host.

Important APIs/types: `Manager`, `snapshotStatus`, status constants, artifact name constants, `NewManager`, image metadata fetchers, `PrepareLayer`, `MergeLayers`, `ExportBlockData`, `MountTarErofs`, `UmountTarErofs`, `DetachLayer`, `CheckTarfsHintAnnotation`, `GetConcurrentLimiter`, and path helpers. State is tracked by `snapshotMap` keyed by snapshot ID; each status holds conversion state, blob ID/path, loop devices, EROFS mountpoint, waitgroup, and cancel function.

Control flow and persistence: `PrepareLayer` registers a preparing status and launches `blobProcess`. `blobProcess` resolves credentials, fetches the compressed blob by digest, decompresses it, optionally validates diffID from manifest/config, streams it through `generateBootstrap`, and marks status ready/failed. `generateBootstrap` uses a FIFO plus `io.TeeReader` so `nydus-image create --type tar-tarfs` consumes the tar stream while the raw tar is cached. `MergeLayers` waits for parent layers, orders bootstraps low-to-high, and runs `nydus-image merge`. `ExportBlockData` runs `nydus-image export --block`, parses dm-verity output, and mutates snapshot labels. `MountTarErofs` attaches tar/bootstrap files to loop devices, mounts EROFS, and annotates the RAFS object.

Dependencies/integration: integrates with registry remote/auth code, containerd compression/storage labels, config tarfs flags, `nydus-image`, Linux FIFO/mount/loopdev APIs, lru caches, singleflight, and filesystem/snapshot flows.

Risks and test signals: high operational risk: external binary execution, parsing CLI stdout, async goroutine failures, loop-device lifecycle, and host mount privileges. `blobProcess` returns early after starting a goroutine, so readiness must always be observed via waitgroup/status. No direct tests in this subset; snapshotter paths exercise it indirectly when tarfs is enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/tarfs/tarfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/display/display.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/display/display.go

Purpose: provides small formatting helpers for displaying byte and latency values in human-readable units.

Important APIs: `ByteToReadableIEC(uint32)` formats bytes using IEC units (`B`, `KiB`, `MiB`, etc.) with one decimal beyond bytes. `MicroSecondToReadable(uint64)` formats microseconds as `us`, milliseconds, or seconds with three decimals.

Control flow and state: both functions are pure and stateless. Byte formatting divides by 1024 until the appropriate IEC exponent; time formatting switches at 1000 and 1,000,000 microseconds.

Dependencies/integration: only depends on `fmt`; likely used by logging, metrics, or CLI display code.

Risks and test signals: `ByteToReadableIEC` accepts `uint32`, so it cannot display values above 4 GiB accurately if callers have larger counters. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/display/display.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/erofs/erofs.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/erofs/erofs.go

Purpose: wraps Linux EROFS mount/unmount operations for fscache-backed nydus filesystems and derives stable fscache IDs.

Important APIs: `Mount(domainID, fscacheID, mountpoint)`, `Umount(mountPoint)`, and `FscacheID(snapshotID)`. `Mount` builds either `domain_id=<domain>,fsid=<id>` for shared domains or `fsid=<id>` otherwise, then calls `unix.Mount("erofs", mountpoint, "erofs", 0, opts)`.

Control flow and state: the functions are stateless wrappers around kernel syscalls. On `EINVAL` with a domain ID, `Mount` logs a hint that shared domains require Linux kernel >= 6.1.

Dependencies/integration: uses `golang.org/x/sys/unix`, containerd logging, go-digest, and pkg/errors. `FscacheID` hashes `nydus-snapshot-<snapshotID>` to avoid raw snapshot IDs as fs cache IDs.

Risks and test signals: requires Linux EROFS/fscache support and mount privileges. Kernel compatibility is only logged, not feature-detected. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/erofs/erofs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/file/file.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/file/file.go

Purpose: exposes a single filesystem helper to determine whether a path exists and is a directory.

Important API: `IsDirExisted(path string) (bool, error)`. It calls `os.Stat`; not-exist returns `(false, nil)`, other stat errors propagate, and existing paths return `s.IsDir()`.

Control flow and state: stateless and synchronous; it does not create directories or follow any project-specific state.

Dependencies/integration: depends only on the Go standard library `os`. It is a utility for callers that need to distinguish absent paths from permission/stat failures.

Risks and test signals: name uses “Existed” but behavior includes non-directory existing paths returning false. It follows symlinks through `os.Stat`; callers needing symlink-aware behavior should not reuse it blindly. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/file/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/mount/mount.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/mount/mount.go

Purpose: provides common mountpoint detection, unmount, and wait-for-unmount helpers.

Important APIs/types: `Interface`, `Mounter`, `Mounter.Umount`, `NormalizePath`, `IsMountpoint`, and `WaitUntilUnmounted`. `Umount` first verifies the target is a mountpoint, then calls `syscall.Unmount(target, 0)`.

Control flow and state: `NormalizePath` resolves to an absolute symlink-evaluated path and stats it. `IsMountpoint` treats `/` as mounted and otherwise compares the device number of the path against its parent. `WaitUntilUnmounted` retries `IsMountpoint` up to 20 times with 50 ms delay and returns only the last error.

Dependencies/integration: uses `retry.Do` and project `errdefs.ErrDeviceBusy` to model still-mounted state. Mount detection follows traditional Unix device-boundary semantics.

Risks and test signals: bind mounts on the same device may not be detected by device comparison alone. `Umount` returns `"not mounted"` for non-mountpoints, which callers may need to treat as benign. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/mount/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser.go

Purpose: parses memory-size configuration strings into byte counts, including binary units and percentages.

Important APIs/state: `MemoryConfigToBytes(data string, totalMemoryBytes int)`, `InitUnitMultipliers`, and package globals `unitMultipliers` plus `sync.Once`. Supported units are `B`, `%`, and IEC suffixes `KiB/MiB/GiB/TiB/PiB` plus short forms `Ki/Mi/Gi/Ti/Pi`.

Control flow: empty string returns `-1`. A raw numeric string parses directly as bytes. Otherwise a regexp extracts a floating value and alphabetic/percent unit. Percentages are rounded with `+0.5` against `totalMemoryBytes`; known binary units multiply by the initialized map.

Dependencies/integration: uses regexp, strconv, sync, and pkg/errors. This feeds config parsing for resource limits or cache sizing.

Risks and test signals: unknown alphabetic units currently return multiplier zero without an error, yielding zero bytes. The regexp is not anchored, so strings with a valid prefix plus garbage can parse unexpectedly. `parser_test.go` covers valid empty, percent, raw, byte, and binary-unit cases, but not invalid/unknown units.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser_test.go

Purpose: verifies successful memory configuration parsing for supported formats.

Important test: `TestMemoryLimitToBytes` table-drives `MemoryConfigToBytes` with `totalMemoryBytes=10000`. It checks empty string, whole and fractional percentages, raw byte values, explicit `B`, and IEC units from Ki through Pi with and without trailing `B`.

Control flow and state: tests rely on the package singleton unit map being lazily initialized through the production function.

Dependencies/integration: uses testify assertions.

Risks and test signals: this test is a positive-case regression suite. It does not cover malformed input, unknown units, lowercase units, overflow/truncation of large floats, or regexp partial matches. Because production returns zero for unknown units, adding negative tests would likely reveal a validation gap.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry.go

Purpose: provides registry reference utilities and authenticated go-containerregistry transports.

Important APIs/types: `Image`, `ConvertToVPCHost`, `ParseImage`, `ParseLabels`, and `AuthnTransport`. `ConvertToVPCHost` inserts `-vpc` into the first DNS label unless already present. `ParseImage` returns registry host and repository path from a Docker reference. `ParseLabels` extracts target ref and target layer digest from containerd snapshot labels. `AuthnTransport` resolves credentials and creates a scoped registry transport with a 10-second timeout wrapper.

Control flow and state: functions are stateless. `AuthnTransport` treats nil or nil-pointer keychains as anonymous auth, resolves otherwise, and runs `transport.NewWithContext` in a goroutine to enforce a coarse timeout.

Dependencies/integration: uses distribution/reference, go-containerregistry name/auth/transport, containerd snapshotter labels, HTTP RoundTripper, and project callers such as transport pool and remote fetch code.

Risks and test signals: `ConvertToVPCHost` assumes a non-empty dotted host. The goroutine timeout in `AuthnTransport` can leave the goroutine running after returning timeout. Tests cover VPC host conversion and image parsing, but not auth transport timeout/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry_test.go

Purpose: tests registry host transformation and Docker image reference parsing.

Important tests: `TestConvertToVPCHost1` verifies a normal Aliyun registry host gains a `-vpc` suffix on the first label and an already-VPC host is unchanged. `TestParseImage` validates multi-segment repository paths, no-namespace repositories, a normal remote image, and one invalid reference.

Control flow and state: table-driven tests call pure functions and compare exact structs/errors.

Dependencies/integration: uses Go `reflect.DeepEqual` and testing package only.

Risks and test signals: coverage is limited to happy path parsing plus one invalid syntax case. It does not test Docker Hub implicit domain behavior, digest-only references, localhost without port, empty host input to VPC conversion, or auth transport creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/registry/registry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/retry/retry.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/retry/retry.go

Purpose: implements configurable retry behavior with attempt count, delay strategy, jitter, max delay, retry predicates, callbacks, and optional last-error-only reporting.

Important APIs/types: `RetryableFunc`, `AbortFunc`, `OnRetryFunc`, `DelayTypeFunc`, `Config`, `Option`, option helpers (`Attempts`, `Delay`, `MaxDelay`, `MaxJitter`, `DelayType`, `OnRetry`, `OnlyRetryIf`, `LastErrorOnly`), delay strategies (`FixedDelay`, `RandomDelay`, `BackOffDelay`, `CombineDelay`), `Do`, aggregate `Error`, `Unrecoverable`, `IsRecoverable`, and `WrappedErrors`.

Control flow and state: `Do` builds defaults, applies options, repeatedly calls the function, stores unpacked errors, checks recoverability/predicate, invokes `onRetry`, sleeps unless on the last attempt, and returns either nil, the last error, or an aggregate `Error`. `Unrecoverable` wraps an error so default retry logic stops.

Dependencies/integration: pure standard-library utility used by mount wait logic and likely other transient operations.

Risks and test signals: no direct tests in this subset. `RandomDelay` panics if `maxJitter` is zero because `rand.Int63n(0)` is invalid. `BackOffDelay` can overflow for large attempt numbers. `Error.Error` allocates a slice sized by non-nil count but indexes by original position, which can panic if nil holes precede later errors; current `Do` usually fills sequentially but future callers of `Error` could trigger it.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/retry/retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal.go

Purpose: provides process-wide shutdown signal handling shared by long-running components.

Important API/state: `SetupSignalHandler() <-chan struct{}` and package globals `once`, `stop`, and `shutdownSignals` (`os.Interrupt`, `SIGTERM`). The first call installs `signal.Notify` and launches a goroutine.

Control flow and state: on the first shutdown signal, the goroutine closes `stop`, broadcasting graceful shutdown. On a second signal, it calls `os.Exit(1)`. `sync.Once` ensures all callers receive the same channel and only one signal goroutine is installed.

Dependencies/integration: used by the system controller server to close its Unix listener. It is intentionally process-global.

Risks and test signals: because it is singleton global state, tests or components cannot reset it in-process. A second signal forces immediate exit, which can bypass deferred cleanup. `signal_test.go` verifies the broadcast behavior for two listeners.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal_test.go

Purpose: validates that `SetupSignalHandler` returns a stop channel that broadcasts to multiple goroutines on SIGINT.

Important test: `TestSetupSignalHandler` starts two goroutines waiting on the returned channel, sends SIGINT to the current process with `syscall.Kill`, sleeps one second, and asserts both waiters incremented an atomic counter.

Control flow and state: the test mutates process-global signal handler state and sends a real process signal. Because production uses `sync.Once`, this test can affect later tests in the same process.

Dependencies/integration: uses syscall, atomic, time, and testify require.

Risks and test signals: strong signal for the first-signal close behavior, but it does not test second-signal forced exit or SIGTERM. It can be order-sensitive with other tests that also install signal handlers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signals/signal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signer/signer.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/signer/signer.go

Purpose: verifies RSA/SHA-256 signatures over streamed input.

Important APIs/types: `Signer`, `New(publicKey []byte)`, and `Verify(input io.Reader, signature []byte)`. `New` PEM-decodes a PKCS#1 RSA public key and stores it. `Verify` streams input through SHA-256 and calls `rsa.VerifyPKCS1v15`.

Control flow and state: signer state is only the parsed public key. Verification reads the entire input stream into the hash, so callers must provide a fresh reader positioned at the beginning.

Dependencies/integration: standard crypto/x509/pem/rsa packages. It likely supports image signature verification through higher-level `signature` code.

Risks and test signals: `New` does not check for a nil PEM block before `block.Bytes`, so invalid non-PEM input can panic. It expects PKCS#1 public keys, not PKIX `BEGIN PUBLIC KEY` keys. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/signer/signer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/sysinfo/sysinfo.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/sysinfo/sysinfo.go

Purpose: exposes cached system memory information from the Linux `sysinfo` syscall.

Important APIs/state: `GetSysinfo`, `GetTotalMemoryBytes`, and package globals `sysinfo`, `sysinfoOnce`, `sysinfoErr`. `GetTotalMemoryBytes` initializes once and returns `int(sysinfo.Totalram)`.

Control flow and state: the first `GetTotalMemoryBytes` call populates the global cache. Subsequent calls return the same value/error for process lifetime.

Dependencies/integration: uses standard `syscall.Sysinfo_t`; useful for config parsers that accept memory percentages.

Risks and test signals: `Sysinfo_t.Totalram` should be multiplied by `Unit` on some platforms/architectures, but this code returns `Totalram` directly. Conversion to `int` can overflow on 32-bit architectures. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/sysinfo/sysinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool.go

Purpose: caches authenticated registry transports and resolves blob URLs, including redirect targets, for efficient remote blob access.

Important APIs/types: `Pool`, `NewPool`, `Resolve` interface, `Pool.Resolve`, and `redirect`. `Pool` holds an LRU of up to 3000 transports keyed by reference name plus a base `http.DefaultTransport`.

Control flow and state: `Resolve` builds a `/v2/<repo>/blobs/<digest>` URL, checks the transport cache, and validates cached transports by issuing a range GET through `redirect`. If cached redirect fails, it removes the cache entry, authenticates a new transport via `registry.AuthnTransport`, resolves redirect again, and caches the transport. `redirect` sends `Range: bytes=0-0`, accepts 2xx as the original endpoint and 3xx with `Location` as the redirected URL, drains the response body, and errors otherwise.

Dependencies/integration: uses go-containerregistry references/keychains, registry auth helper, groupcache LRU, HTTP, and containerd logging. It supports remote content fetch optimization.

Risks and test signals: `Resolve` holds the mutex across network calls, serializing all resolutions and making slow registries block unrelated refs. It keys cache by full ref name, not registry/repository scope alone. `pool_test.go` covers cache reuse and invalidation on redirect failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool_test.go

Purpose: tests transport pool resolution, cache hit behavior, and cache invalidation after a redirect failure.

Important components: `FakeReference` implements `name.Reference` for a local httptest repository. `TestResolve` starts a local HTTP server, creates a pool, resolves a fake digest three times, and asserts call counts and transport/url reuse.

Control flow and state: first resolve performs auth setup plus redirect. Second resolve uses cached transport and only redirects. Third resolve forces the server to fail once; the pool removes the cached entry, re-authenticates/retries, and returns the same effective transport/url.

Dependencies/integration: uses httptest, go-containerregistry `name`, and testify require. It exercises real HTTP behavior without an external registry.

Risks and test signals: digest is an arbitrary string and the server does not verify path/method/range headers, so URL construction is only partially covered. Concurrency and timeout behavior are untested.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/mount_option.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/mount_option.go

Purpose: builds special mount options for nydus-overlayfs and Kata Containers volumes, including proxy-mode guest pulls and tarfs raw block volumes with optional dm-verity.

Important APIs/types: `ExtraOption`, `remoteMountWithExtraOptions`, `mountWithKataVolume`, `mountWithProxyVolume`, `mountWithTarfsVolume`, `prepareKataVirtualVolume`, `parseTarfsDmVerityInfo`, `DmVerityInfo`, volume structs, `KataVirtualVolume`, parsing/encoding helpers, and volume type constants.

Control flow and state: `remoteMountWithExtraOptions` locates the bootstrap, daemon/instance config, detects fs version from bootstrap header, base64-encodes source/config/snapshotdir/version as `extraoption=...`, and returns a `fuse.nydus-overlayfs` mount. `mountWithKataVolume` augments overlay options with proxy and/or tarfs volume descriptors. Proxy volumes embed RAFS annotations as image-pull metadata. Tarfs volumes pick image-level or layer-level block annotations, resolve disk image paths, and encode volume descriptors, walking parent snapshots for layer raw blocks. `DmVerityInfo.Validate` checks hash algorithm, hash length, block counts/sizes, and hash offset alignment/range.

Dependencies/integration: tightly integrated with RAFS global cache, filesystem daemon lookup, snapshot metadata, nydus labels, daemon config dumping, bootstrap fs-version detection, and Kata runtime option contracts.

Risks and test signals: sensitive config is base64-encoded into mount options for nydus-overlayfs. `validateBlockSize` checks only range, not power-of-two despite test comments. Logging encoded volume JSON may expose metadata. Tests cover validation and parse/encode helpers, but not live mount construction with real snapshot metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/mount_option.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/mount_option_test.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/mount_option_test.go

Purpose: tests dm-verity and Kata virtual volume validation/parsing behavior.

Important tests: `TestDmVerityInfoValidation` enumerates invalid hash types, sizes, block counts, offsets, and a valid SHA-256 case. `TestDirectAssignedVolumeValidation`, `TestImagePullVolumeValidation`, and `TestNydusImageVolumeValidation` cover simple metadata/config validators. `TestKataVirtualVolumeValidation` checks direct-block volume validity. `TestParseDmVerityInfo` tests valid JSON and invalid JSON. `TestParseKataVirtualVolume` tests base64 encode/decode, invalid JSON, invalid base64, and missing required fields.

Control flow and state: pure tests over JSON/base64 structs; no mounts or snapshotter state.

Dependencies/integration: uses testify assertions.

Risks and test signals: comments say non-power-of-two sizes are invalid, but production range-only validation means `3000` passes if in range; this mismatch is a test/spec signal to inspect. Mount option construction paths are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/mount_option_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/process.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/process.go

Purpose: chooses how a `Prepare` operation should process a snapshot based on labels, fs driver, stargz/tarfs/index/referrer features, and whether the snapshot is a read-only layer or active writable layer.

Important API: `chooseProcessor`, returning a handler function, target snapshot reference, commit labels, and error. Handler variants include default native overlay preparation, skip/commit-only behavior, remote nydus mount preparation, and proxy mount preparation.

Control flow: for read-only layers (`containerd.io/snapshot.ref` present), proxy mode marks proxy labels and skips unpacking, nydus meta layers use native unpack, nydus data layers skip, index/referrer alternatives skip with labels, stargz data layers may generate metadata and skip, and tarfs may prepare/export tarfs then skip. For active layers, it checks proxy-parent mode, nydus meta parents, index/referrer alternatives, stargz merged metadata, and tarfs parent data; matching remote paths mount nydusd/tarfs and return overlay mounts. Unmatched paths fall back to native overlay/bind mounts.

Dependencies/integration: central integration point for config, labels, filesystem feature managers, containerd storage metadata, and tarfs/stargz conversion.

Risks and test signals: behavior is order-sensitive; a label or feature change can redirect snapshot lifecycle. Some error handling around parent snapshot info reads `pInfo` before checking `pErr` in the proxy-driver warning path. No direct tests here; `snapshot_test.go` covers only lower-level mount-native behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/process.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/renewal.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/renewal.go

Purpose: periodically renews registry credentials for live RAFS instances and hot-reloads changed credentials into running nydusd daemons.

Important APIs: `startCredentialRenewal`, `credentialRenewalLoop`, and `reconcileCredentials`. `startCredentialRenewal` initializes the auth credential store, performs an immediate reconciliation, logs startup, and launches a ticker goroutine.

Control flow and state: reconciliation walks managers, then running daemons, then their RAFS instances. For each instance with an image reference, it marks the ref live, renews credentials through `auth.RenewCredential`, compares old/new base64 credentials, and calls `d.UpdateAuthConfig(snapshotID, kc)` when changed. After scanning, `auth.EvictStaleCredentials(live)` removes store entries not backed by a live RAFS instance.

Dependencies/integration: depends on manager daemon caches populated by filesystem recovery, daemon running states, auth credential store, and nydusd auth hot-reload API.

Risks and test signals: manager and daemon list methods must be concurrency-safe because the goroutine runs in the background. Hot reload failures are logged but do not stop renewal. Credential comparison via base64 assumes stable serialization. `renewal_test.go` only covers lifecycle with an empty manager list.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/renewal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/renewal_test.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/renewal_test.go

Purpose: smoke-tests credential renewal goroutine startup and cancellation.

Important test: `TestStartCredentialRenewalLifecycle` creates a cancellable test context, starts renewal with a 30 ms interval and an empty manager list, sleeps long enough for several ticks, cancels, then gives the goroutine time to observe cancellation.

Control flow and state: because managers are empty, `reconcileCredentials` is a no-op except credential-store initialization/eviction behavior.

Dependencies/integration: uses Go testing context and manager type only.

Risks and test signals: this is a lifecycle smoke test, not a behavioral credential renewal test. It does not assert hot-reload calls, stale eviction contents, running-state filtering, or changed-vs-unchanged credential handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/renewal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/snapshot.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/snapshot.go

Purpose: implements the containerd `snapshots.Snapshotter` for nydus. It wires config, daemon managers, cache, metrics, system controller, tarfs/stargz/index/referrer features, and the snapshot lifecycle operations.

Important APIs/types: `snapshotter`, `NewSnapshotter`, `Cleanup`, `Stat`, `Update`, `Usage`, `Mounts`, `Prepare`, `View`, `Commit`, `Remove`, `Walk`, `Close`, path helpers, parent-layer finders, snapshot creation/recovery helpers, tarfs merge, mount builders, cleanup helpers, and `treatAsProxyDriver`.

Control flow and state: `NewSnapshotter` initializes signature verification, Bolt store, recovery policy, optional cgroups, per-driver managers, metrics, filesystem, cache manager, optional index/referrer/tarfs managers, credential renewal, system controller/pprof, d_type validation, metadata store, snapshot root, and removal flags. `Prepare` creates an active snapshot then delegates behavior to `chooseProcessor`, committing skipped read-only layers when needed. `Mounts` and `View` detect nydus/tarfs/proxy/index/referrer cases and choose remote or native mounts. `Commit` records disk usage and commits active snapshots. `Remove` deletes metadata and optionally synchronously cleans orphan directories. `Cleanup` removes orphan snapshot dirs and unused cache blobs. `createSnapshotWithRecovery` can recreate proxy-mode placeholder parents when the local metadata DB lost a parent known to containerd.

Dependencies/integration: central integration with containerd storage, filesystem/daemon managers, labels, config globals, cache, metrics, system API, tarfs, cgroups, signature verification, and Linux filesystem behavior.

Risks and test signals: broad blast radius. Cgroup error condition uses `&&` where `||` may have been intended, potentially returning on supported fallback errors. Lazy parent recovery only supports proxy mode. Cleanup of cache blobs depends on filename parsing and daemon RAFS `UnderlyingFiles`. Tests in `snapshot_test.go` cover only `mountNative` and volatile option behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/snapshot_test.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/snapshot_test.go

Purpose: unit-tests native bind/overlay mount option construction.

Important tests: `TestMountNative` table-drives active/view/committed snapshots with zero, one, and multiple parents, asserting bind mounts or overlay mounts with expected `workdir`, `upperdir`, `lowerdir`, and `volatile` options. `TestMountNativeConfigVolatile` verifies config-level volatile is applied only to active snapshots.

Control flow and state: tests construct a minimal `snapshotter{root: ...}` without filesystem or metadata store and call `mountNative` directly.

Dependencies/integration: uses containerd mount/snapshot/storage types and testify require/assert.

Risks and test signals: good coverage for native mount formatting, but it does not exercise remote nydus mounts, tarfs/Kata volume options, snapshot metadata transactions, cleanup, or Prepare/View control flow.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/utils.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/utils.go

Purpose: holds small OS-specific helpers for snapshotter filesystem preparation.

Important APIs: `getSupportsDType(dir string)` delegates to `continuity/fs.SupportsDType`; `lchown(target string, st os.FileInfo)` extracts UID/GID from `syscall.Stat_t` and calls `os.Lchown`.

Control flow and state: stateless wrappers. `NewSnapshotter` uses `getSupportsDType` to reject backing filesystems without d_type support. `createSnapshotWithRecovery` uses `lchown` to propagate parent ownership to new snapshot directories.

Dependencies/integration: depends on Linux/Unix stat data and containerd continuity fs helpers.

Risks and test signals: `lchown` assumes `st.Sys()` is `*syscall.Stat_t`, so it is platform-specific. No direct tests in this subset; behavior is indirectly relevant to snapshot creation tests/integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/converter_test.go -->
## sources/cloud-native/nydus-snapshotter/tests/converter_test.go

Purpose: integration-heavy tests for nydus converter pack/merge/unpack/image-convert/reconvert behavior, including fs versions 5/6, chunk dictionaries, OCI refs, S3 backend, and encryption.

Important APIs/helpers: tar builders (`buildChunkDictTar`, `buildOCILowerTar`, `buildOCIUpperTar`), `packLayer`, `packLayerRef`, `unpackLayer`, `verify`, `buildChunkDict`, option structs, `TestPack`, `TestPackRef`, `TestUnpack`, `TestImageConvert`, and `TestImageReConvert`. Embedded RSA keys support encryption tests.

Control flow and state: tests synthesize OCI tar layers with whiteouts/opaque dirs/large files, convert layers through `converter.Pack`, merge bootstraps, mount with a real `nydusd` via `tests/nydusd.go`, and verify file trees. Image conversion tests start local Docker registry/MinIO containers, pull nginx with `ctr`, convert/push images, optionally encrypt bootstraps, and validate with `nydusify`. Reconvert converts a nydus image back to OCI.

Dependencies/integration: depends on Docker, containerd socket, ctr, nydusd, nydusify, AWS S3 client, MinIO image, root privileges for cache drop/mounts, and local content store APIs.

Risks and test signals: high-value end-to-end coverage but expensive and environment-sensitive. Several tests assume Docker/containerd availability and root privileges; `TestPackRef` is gated by `TEST_PACK_REF`. Failure cleanup relies on deferred container/image removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/converter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/kind.yaml -->
## sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/kind.yaml

Purpose: defines the Kind cluster configuration for nydus Kubernetes e2e tests.

Important contents: Kind API `kind.x-k8s.io/v1alpha4`, dual-stack IP family, containerd CRI config patches setting `discard_unpacked_layers=false` and `disable_snapshot_annotations=false`, and one control-plane node with `/dev/fuse` mounted from host to container.

Control flow and state: consumed by `tests/helpers/kind.sh` during `kind create cluster`. The containerd patch ensures annotations needed by the snapshotter are preserved and unpacked layers are not discarded in a way that breaks the test flow.

Dependencies/integration: depends on Kind, a host `/dev/fuse`, and containerd inside the Kind node.

Risks and test signals: single-node cluster only. Host Fuse device availability and permissions are required. Dual-stack networking can expose environment-specific issues but may also fail on hosts without IPv6 support.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/kind.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-cri.yaml -->
## sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-cri.yaml

Purpose: Kubernetes manifest deploying nydus snapshotter for e2e tests using CRI image-service auth.

Important resources: namespace, service account, cluster role allowing node get/patch, role binding, privileged hostNetwork/hostPID pod running `local-dev:e2e`, hostPath mounts for nydus/containerd/systemd/bin/Fuse paths, and ConfigMap containing `config.toml` and `nydusd.json`.

Control flow and state: pod command runs `/opt/nydus-artifacts/opt/nydus/snapshotter.sh deploy`; preStop runs cleanup. Config sets fusedev, multiple daemon mode, system controller socket, metrics on `:9110`, restart recovery, CRI keychain enabled, kubeconfig keychain disabled, and systemd service enabled. HostPath volumes persist snapshotter state and allow bidirectional mount propagation.

Dependencies/integration: consumed by `kind.sh` when `AUTH_TYPE=cri`; later kubelet is configured to use the snapshotter gRPC image service endpoint.

Risks and test signals: privileged pod with broad hostPath write access is appropriate for e2e but unsafe for production defaults. RBAC lacks secrets because CRI auth mode proxies image credentials instead of watching Kubernetes secrets.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-cri.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-kubeconf.yaml -->
## sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-kubeconf.yaml

Purpose: Kubernetes manifest deploying nydus snapshotter for e2e tests using kubeconfig-backed secret watching.

Important resources: same namespace/service account/pod/config structure as CRI manifest, but RBAC also grants `get/list/watch` on secrets. ConfigMap sets `enable_index_detect=true`, kubeconfig keychain enabled, CRI keychain disabled, and systemd service disabled.

Control flow and state: deployed by `kind.sh` when `AUTH_TYPE=kubeconf`. It relies on the snapshotter reading Kubernetes dockerconfigjson secrets through kubeconfig rather than kubelet image-service credential forwarding. The same privileged hostPath mounts expose containerd config, binaries, snapshotter data, `/run/containerd-nydus`, `/dev/fuse`, and systemd paths.

Dependencies/integration: integrates with e2e secret creation in `kind.sh`, index-detect validation, and snapshotter config parsing from mounted ConfigMap.

Risks and test signals: broader RBAC to secrets is required and should be scoped carefully outside tests. Index-detect is enabled here, making it the manifest used to test alternative nydus image detection through logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/e2e/k8s/snapshotter-kubeconf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/helpers.sh -->
## sources/cloud-native/nydus-snapshotter/tests/helpers/helpers.sh

Purpose: project-specific shell helpers for e2e setup, wrapping Docker/Kind/Kubectl/Nydus commands, installing tools, configuring Docker, logging in, and starting a local authenticated registry.

Important functions: `configure::rootful`, `configure::dockerd`, `exec::docker`, `exec::kind`, `exec::kubectl`, `exec::nydusify`, `docker::configpath`, `docker::login`, installers for kind/kubectl/nydus/nerdctl, and `start::registry`.

Control flow and state: rootful mode prepends `sudo` to selected commands and changes Docker config path. Installers download release artifacts into temp dirs and install binaries into `/usr/local/bin`. `start::registry` creates an htpasswd file with an httpd container, starts a registry container on port 5000, and returns `<host eth0 ip>:5000`.

Dependencies/integration: sourced by `kind.sh` after generic `lib.sh`. Depends on Docker, curl/download helpers, tar extraction, GitHub/Nydus releases, and host install privileges.

Risks and test signals: mutates `/etc/docker/daemon.json` and restarts Docker, installs host binaries, and uses a fixed registry container/port. `ip addr show eth0` assumes host interface naming. It is operational test infrastructure, not production code.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/kind.sh -->
## sources/cloud-native/nydus-snapshotter/tests/helpers/kind.sh

Purpose: orchestrates the full Kind-based Kubernetes e2e flow for nydus snapshotter.

Important variables/flow: configurable `AUTH_TYPE`, `INDEX_DETECT`, `ROOTFUL`, versions for Kind/Kubernetes/Nydus, test registry credentials, and namespace. The script sources helper libraries, resolves latest Nydus release, builds static snapshotter binaries, builds a local e2e image, starts an authenticated registry, configures Docker, installs dependencies, converts/pushes a busybox nydus image, recreates a Kind cluster, deploys snapshotter manifest, restarts containerd, creates image pull secret, optionally points kubelet at the nydus image service for CRI auth, applies a test pod, validates readiness/logs, optionally checks index-detect log evidence, then deletes the pod.

Dependencies/integration: drives Makefile, Docker, Kind, kubectl, nydusify, GitHub API, local registry, and manifests in `tests/e2e/k8s`.

Risks and test signals: highly stateful and host-mutating: Docker daemon config, Kind cluster deletion, host binary installation, container lifecycle, kubelet/containerd restarts. Provides strong e2e confidence when it passes, especially for auth modes and index detection, but failures may stem from environment rather than code.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/kind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/lib.sh -->
## sources/cloud-native/nydus-snapshotter/tests/helpers/lib.sh

Purpose: generic bash utility library for e2e scripts, covering logging, required-tool checks, host installation, temp directories, tar extraction, HTTP downloads/healthchecks/checksums, and GitHub API helpers.

Important functions/state: log level constants/styles, `log::init`, `log::*`, `host::require`, `host::install`, `fs::mktemp`, `tar::expand`, `_http::get`, `http::get`, `http::healthcheck`, `http::checksum`, `github::settoken`, `github::request`, `github::tags::latest`, and `github::releases::latest`.

Control flow and state: strict bash options are enabled. `_http::get` wraps curl with retry/optional basic auth/TLS restrictions/header injection. GitHub helpers optionally use `GITHUB_TOKEN`; placeholder GitHub Actions expressions are ignored when not on GitHub. At load time it initializes logging and requires `jq`, `tar`, `curl`, and `shasum`.

Dependencies/integration: sourced by project helper scripts. Provides the primitives used by `helpers.sh` and `kind.sh`.

Risks and test signals: `http::checksum` appears to call `http::get -o ...`, but `http::get` expects output then URL, so that helper may be broken if used. Sourcing the library immediately exits if required tools are missing due to strict mode. No shell tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/nydusd.go -->
## sources/cloud-native/nydus-snapshotter/tests/nydusd.go

Purpose: test harness for launching a real `nydusd`, waiting until it reports `RUNNING`, and unmounting it after converter tests.

Important APIs/types: `NydusdConfig`, `Nydusd`, internal `daemonInfo`, JSON `configTpl`, `makeConfig`, `checkReady`, `NewNydusd`, `Mount`, and `Umount`.

Control flow and state: `NewNydusd` renders `configTpl` to the configured path. `Mount` first attempts an unmount, builds nydusd command-line args for config/mountpoint/bootstrap/apisock/log-level, runs the process asynchronously, then polls `/api/v1/daemon` over the Unix API socket until state `RUNNING`, process exit, or 10-second timeout. `Umount` runs the host `umount` command if the mount path exists.

Dependencies/integration: used by `converter_test.go` to verify generated bootstraps by mounting them. Depends on a real nydusd binary, Unix sockets, host mount permissions, and the daemon HTTP API.

Risks and test signals: `checkReady` creates an unbuffered channel and may block sending if `Mount` has already returned through another path. `defer resp.Body.Close()` inside a polling loop can delay body closure until goroutine exit. `Umount` does not stop the nydusd process directly; it relies on daemon behavior after unmount.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/nydusd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Cargo.toml -->
## sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Cargo.toml

Purpose: Rust package manifest for the `optimizer-server` utility, described as generating accessed-file information in a target mount namespace.

Important metadata/dependencies: package name `optimizer-server`, version `0.1.0`, edition 2021, Apache-2.0 OR BSD-3-Clause license, and Nydus authors. Dependencies include `clap` for CLI parsing, `lazy_static`, `libc`, `nix` for Unix/mount namespace/syscall work, `serde`/`serde_json` for data structures, and `signal-hook` for signal handling.

Control flow and state: Cargo manifest only; implementation is elsewhere. It declares runtime capabilities implied by dependencies rather than direct logic.

Dependencies/integration: built by the adjacent Makefile into `bin/optimizer-server`, likely packaged with snapshotter tooling.

Risks and test signals: dependency versions are pinned with older minor versions; security/compatibility updates should be reviewed periodically. No tests are declared in this manifest.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Makefile -->
## sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Makefile

Purpose: build automation for the Rust optimizer-server across target OS/architecture combinations, with format and clippy gates.

Important targets/variables: `OS`, `ARCH`, architecture/linker maps, `RUST_TARGET`, `RUST_LINKER`, `RUST_TYPE`, `all`, `.release_version`, `.format`, `build`, `release`, `static-release`, and `clean`. `build` runs rustup target add, cargo fmt check, cargo build, cargo clippy with `-Dwarnings`, and installs the binary into `bin/optimizer-server`.

Control flow and state: `release` adds `--release`, static CRT features, and stripping flags before building. `static-release` separately invokes clippy and a static release cargo build. `clean` removes cargo outputs and local bin artifacts.

Dependencies/integration: requires Rust toolchain, rustup, cargo, architecture-specific GNU cross linker, and install utility. It integrates the Rust tool into the repository’s binary output layout.

Risks and test signals: `static-release` repeats `-C target-feature=+crt-static` twice. Cross-linker names assume `<arch>-linux-gnu-gcc` naming and may not exist on hosts. Clippy is run after build in `build`, so format/build failures appear before lint failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/Makefile -->
