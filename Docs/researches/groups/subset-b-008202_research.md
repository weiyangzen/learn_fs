# Research Report: subset-b-008202

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-instrumented.go -->
# sources/object-store/minio/cmd/os-instrumented.go

## Purpose
This file wraps common filesystem operations with MinIO OS metrics and optional trace publication. It is the instrumentation entry point for operations such as remove, mkdir, rename, open, stat, direct I/O open, and fdatasync.

## Important APIs, Types, and Functions
`osMetric` enumerates tracked operation classes and is paired with generated string output in `osmetric_string.go`. `globalOSMetrics` stores lifetime counters and last-minute latency buckets. `updateOSMetrics` returns a deferred closure that records duration and, when OS trace subscribers exist, publishes `madmin.TraceInfo` via `globalTrace`.

The exported wrappers are `RemoveAll`, `Mkdir`, `MkdirAll`, `Rename`, `OpenFile`, `Access`, `Open`, `OpenFileDirectIO`, `Lstat`, `Remove`, `Stat`, `Create`, and `Fdatasync`. `init` injects `OpenFile`, `OpenFileDirectIO`, and `Open` into `internal/ioutil` hooks so shared IO helpers automatically use instrumentation.

## Control Flow and State
Each wrapper defers a closure returned by `updateOSMetrics`, then calls the underlying standard-library, disk, or platform-specific helper. `OpenFile` chooses read or write metrics by masking flags with `writeMode`. The metrics state is process global and uses atomic counters plus `lockedLastMinuteLatency`.

## Dependencies and Integration Points
The file integrates with `madmin.OSMetrics`, `globalTrace`, `globalLocalNodeName`, `disk.OpenFileDirectIO`, `disk.Fdatasync`, and platform-specific helpers from `os_unix.go`, `os_windows.go`, or `os_other.go`.

## Risks and Test Signals
Tracing can include paths, so subscribers receive sensitive filesystem paths. Metrics depend on every caller using these wrappers rather than raw `os` functions. The direct test signal is limited in this subset, but OS read/rename/mkdir tests exercise wrappers indirectly through `Mkdir`, `Rename`, and `Open`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-instrumented.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-readdir-common.go -->
# sources/object-store/minio/cmd/os-readdir-common.go

## Purpose
This small common file defines the shared API for MinIO directory listing helpers while leaving implementation to platform-specific files.

## Important APIs, Types, and Functions
`readDirOpts` carries `count` and `followDirSymlink`. `readDir` returns all entries by passing `count: -1`; `readDirN` returns at most `count` entries by forwarding to `readDirWithOpts`.

## Control Flow and State
There is no persistent state. The functions are simple adapters that normalize caller intent before dispatching to platform-specific `readDirWithOpts`.

## Dependencies and Integration Points
`readDirWithOpts` is implemented in `os_unix.go`, `os_windows.go`, and `os_other.go`. Callers elsewhere in MinIO get a stable API independent of `syscall.ReadDirent`, Windows `FindFirstFile`, or `os.File.Readdir`.

## Risks and Test Signals
Semantics such as symlink directory handling, count behavior, and trailing slash formatting depend on the selected platform implementation. `os-readdir_test.go` validates common behavior across empty directories, files, directories, symlinks, errors, and count limits.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-readdir-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-readdir_test.go -->
# sources/object-store/minio/cmd/os-readdir_test.go

## Purpose
This test file validates MinIO's cross-platform `readDir` and `readDirN` behavior for error handling, regular files, directories, symlinks, and bounded listing.

## Important APIs, Types, and Functions
`TestReadDirFail` verifies nonexistent paths, file-as-directory behavior, and Linux permission-denied behavior. `setupTestReadDirEmpty`, `setupTestReadDirFiles`, `setupTestReadDirGeneric`, and `setupTestReadDirSymlink` build reusable fixtures. `TestReadDir` compares full listings after sorting. `TestReadDirN` checks count edge cases including zero, negative, exact, less-than, and greater-than counts.

## Control Flow and State
Tests create temporary directories and files, use `t.TempDir` plus explicit teardown, and sort entries before comparison because filesystem ordering is not stable. Symlink tests are skipped on Windows.

## Dependencies and Integration Points
The tests exercise `readDir`, `readDirN`, and platform-specific implementations indirectly. They depend on MinIO error values such as `errFileNotFound`, `globalWindowsOSName`, and slash-suffixed directory entries.

## Risks and Test Signals
The suite catches regressions in symlink filtering, directory suffix formatting, count handling, and error normalization. It does not assert ordering or low-level `ReadDirent` parsing, and permission tests are Linux-only because permission semantics vary by platform and user privileges.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-readdir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-reliable.go -->
# sources/object-store/minio/cmd/os-reliable.go

## Purpose
This file provides reliability wrappers around destructive and structural filesystem operations used by storage code: remove-all, mkdir-all, and rename. The wrappers normalize errors and retry a small set of races that occur when directories are concurrently created or deleted.

## Important APIs, Types, and Functions
`removeAll` validates arguments and path length, then calls `reliableRemoveAll`, which retries once on non-empty-directory errors. `mkdirAll` validates input, calls `reliableMkdirAll`, and maps not-directory/path-not-found cases to `errFileAccessDenied`. `reliableMkdirAll` retries once on `os.IsNotExist`, adjusting `baseDir` upward. `renameAll` validates source and destination, calls `reliableRename`, and maps cross-device, missing, exists, and access errors into MinIO object-layer errors.

## Control Flow and State
No persistent state is kept. The retry policy is deliberately narrow: one retry for known races, then return the mapped error.

## Dependencies and Integration Points
The code relies on wrapper functions from `os-instrumented.go`, path-length validation, MinIO error classifiers, and platform-specific `osMkdirAll` and `RenameSys`.

## Risks and Test Signals
Too-broad retrying could hide real disk failures, while too-narrow mapping could surface platform-specific syscalls to object APIs. `os-reliable_test.go` validates invalid arguments, long paths, successful mkdir/rename, and missing-source rename handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-reliable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-reliable_test.go -->
# sources/object-store/minio/cmd/os-reliable_test.go

## Purpose
This test file verifies MinIO's reliable filesystem wrappers for mkdir-all and rename-all behavior.

## Important APIs, Types, and Functions
`TestOSMkdirAll` creates an XL storage setup, asserts empty path returns `errInvalidArgument`, asserts an overlong object path returns `errFileNameTooLong`, and checks successful nested directory creation. `TestOSRenameAll` creates a source volume, checks invalid source/destination handling, verifies a successful rename, confirms a second rename reports `errFileNotFound`, and tests long source and destination path failures.

## Control Flow and State
Tests rely on `newXLStorageTestSetup` to create storage-like paths. They call `mkdirAll` and `renameAll` directly and compare exact MinIO error values.

## Dependencies and Integration Points
The test uses path joining and XL setup helpers from the surrounding cmd test framework. It validates the behavior exposed to storage code rather than platform-specific syscall behavior.

## Risks and Test Signals
The tests cover validation and core success/error mapping, but do not simulate racing parent deletion, ENOTEMPTY removal races, cross-device renames, or Windows-specific path-not-found/not-directory ambiguity.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-reliable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-rename_linux.go -->
# sources/object-store/minio/cmd/os-rename_linux.go

## Purpose
This Linux-only file defines MinIO's low-level rename primitive for Linux.

## Important APIs, Types, and Functions
`RenameSys(src, dst string)` directly calls `syscall.Rename`.

## Control Flow and State
The function has no internal state or additional mapping. Higher-level error normalization is handled by `Rename` and `renameAll`.

## Dependencies and Integration Points
The file is selected by `//go:build linux`. `os-instrumented.go` calls `RenameSys` from the exported `Rename` wrapper, which records metrics and trace information.

## Risks and Test Signals
Direct syscall use preserves Linux errno behavior and avoids possible abstraction changes in `os.Rename`, but it also means Linux-specific behavior must be mapped correctly by higher layers. `os-reliable_test.go` exercises `renameAll` on the active platform.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-rename_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-rename_nolinux.go -->
# sources/object-store/minio/cmd/os-rename_nolinux.go

## Purpose
This non-Linux file supplies the portable rename primitive for all non-Linux builds.

## Important APIs, Types, and Functions
`RenameSys(src, dst string)` delegates to `os.Rename`.

## Control Flow and State
There is no state. The function delegates all behavior to the Go runtime and OS implementation.

## Dependencies and Integration Points
The build tag `!linux` excludes this file on Linux. It is called by `Rename` in `os-instrumented.go` and then normalized by higher-level reliable wrappers.

## Risks and Test Signals
Different operating systems return different errors for missing parents, destination directories, and permission failures; those are handled in `os-reliable.go`. Shared reliable rename tests provide partial coverage, but platform-specific edge cases remain dependent on CI coverage per OS.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-rename_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os_other.go -->
# sources/object-store/minio/cmd/os_other.go

## Purpose
This Plan 9 and Solaris implementation supplies access, mkdir-all, directory iteration, directory listing, and global sync behavior for platforms that do not use the Unix `ReadDirent` fast path or Windows APIs.

## Important APIs, Types, and Functions
`access` uses `os.Lstat`. `osMkdirAll` delegates to `os.MkdirAll` and ignores `baseDir`. `readDirFn` opens a directory with instrumented `Open`, reads batches through `Readdir`, filters symlinked directories, and invokes a callback. `readDirWithOpts` returns regular files and slash-suffixed directories with optional count limiting and symlink directory following. `globalSync` records sync metrics and calls `syscall.Sync`.

## Control Flow and State
Directory reads process up to 1000 entries per batch. Missing directories are treated as no-op for `readDirFn` but as errors for `readDirWithOpts`. Symlinks are resolved with `Stat`; disappearing targets and too-many-symlink conditions are skipped.

## Dependencies and Integration Points
This file implements the common APIs consumed by `os-readdir-common.go` and `os-instrumented.go`. It depends on MinIO error mappers and slash constants.

## Risks and Test Signals
The implementation is simpler but may be slower than the Unix `ReadDirent` version. `readDirN` count limiting slices filesystem batches before filtering, so symlink skips can reduce returned counts. Shared readdir tests provide semantic coverage where these platforms are tested.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os_unix.go -->
# sources/object-store/minio/cmd/os_unix.go

## Purpose
This file implements optimized Unix filesystem primitives for Linux, Darwin, and BSD builds. It avoids higher-level directory APIs for listing hot paths and adds direct fd opens with metrics.

## Important APIs, Types, and Functions
`access` uses `unix.Access`. `openFileWithFD` calls `syscall.Open` with `O_CLOEXEC` and records read/write fd metrics. `osMkdirAll` is a forked recursive mkdir that can skip work under `baseDir`. `parseDirEnt` parses raw `syscall.Dirent` records into names and file modes. `readDirFn` and `readDirWithOpts` use pooled buffers and `syscall.ReadDirent`; `globalSync` calls `syscall.Sync`.

## Control Flow and State
The listing loop reuses `direntPool` and `direntNamePool`, reads raw directory blocks, skips `.` and `..`, and falls back to `Stat` for unknown file types or symlinks. Symlinked directories are ignored unless `followDirSymlink` is set. Directory entries are returned with a slash suffix.

## Dependencies and Integration Points
The code depends on `internal/bpool`, platform helper functions such as `direntNamlen` and `direntInode`, MinIO path and error helpers, and OS metrics from `globalOSMetrics`.

## Risks and Test Signals
Unsafe dirent parsing is sensitive to struct layout and record length validation. The code must avoid leaking pooled buffers and must handle files disappearing during scans. `os-readdir_test.go` covers user-visible semantics; low-level parse errors depend on platform CI and filesystem diversity.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os_windows.go -->
# sources/object-store/minio/cmd/os_windows.go

## Purpose
This Windows-only file implements access, mkdir-all, directory listing, and sync stubs using Windows filesystem APIs.

## Important APIs, Types, and Functions
`access` uses `os.Lstat`. `osMkdirAll` delegates to `os.MkdirAll`. `readDirFn` and `readDirWithOpts` use `syscall.FindFirstFile` and `FindNextFile` over `filepath.Clean(dirPath) + "\\*"`. `syscallErrToFileErr` maps Windows errors into MinIO file errors. `globalSync` is a no-op.

## Control Flow and State
The directory loops skip empty, `.` and `..` entries. Reparse points are treated as symlinks and resolved with `os.Stat`; symlinked directories are skipped unless explicitly followed in `readDirWithOpts`. Directory entries receive MinIO's slash separator.

## Dependencies and Integration Points
The implementation satisfies the common `readDirWithOpts`, `readDirFn`, `access`, and `osMkdirAll` contracts used by higher-level OS wrappers.

## Risks and Test Signals
Windows error mapping differs from Unix and can conflate missing paths with not-directory cases, which higher-level code explicitly accounts for. Symlink behavior depends on privileges. Shared read-directory tests skip symlink coverage on Windows but still validate listing and count behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/osmetric_string.go -->
# sources/object-store/minio/cmd/osmetric_string.go

## Purpose
This generated file provides string names for `osMetric` enum values used in metrics and traces.

## Important APIs, Types, and Functions
The generated `_` compile-time check verifies enum ordinal stability. `_osMetric_name` and `_osMetric_index` encode names compactly. `func (i osMetric) String() string` returns a known name or `osMetric(<n>)` for out-of-range values.

## Control Flow and State
There is no mutable state. The stringer output is deterministic and tied to `os-instrumented.go`.

## Dependencies and Integration Points
`osTrace`, metrics reports, and admin output use this `String` method for operation names such as `OpenFileR`, `ReadDirent`, and `Fdatasync`.

## Risks and Test Signals
If `osMetric` constants change without regenerating this file, compile-time index checks fail. No standalone tests are needed beyond normal compilation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/osmetric_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/peer-rest-client.go -->
# sources/object-store/minio/cmd/peer-rest-client.go

## Purpose
This file implements the client side of MinIO internode peer operations. It wraps legacy REST endpoints and newer grid RPC/stream handlers for health, admin state, IAM reloads, bucket metadata, metrics, tracing, console logs, rebalance, binary updates, and performance diagnostics.

## Important APIs, Types, and Functions
`peerRESTClient` holds a peer host, `rest.Client`, grid host, and lazy grid connection lookup. `newPeerRESTClient` builds authenticated HTTP clients and a health check. `callWithContext` normalizes network failures to `errPeerNotReachable`. Many methods call typed grid handlers: `GetLocks`, `LocalStorageInfo`, `ServerInfo`, `GetMetrics`, IAM reload/delete functions, metacache functions, rebalance/tier reload functions, bandwidth and metrics methods. Legacy HTTP/gob methods include profiling, binary verify/commit, speed tests, drive speed tests, dev-null, netperf, and replication MRF streaming.

## Control Flow and State
Grid connections are cached in an atomic pointer after `globalGrid` becomes available. Streaming APIs start goroutines that reconnect every five seconds until context cancellation and drop data when downstream channels are full.

## Dependencies and Integration Points
The client depends on `peer-rest-common.go` constants, grid handlers registered by `peer-rest-server.go`, global internode transport/auth, madmin types, and notification/admin systems that fan out calls across `globalNotificationSys`.

## Risks and Test Signals
Nil or unavailable grid connections often return nil/no-op for best-effort reload calls, so callers must tolerate eventual consistency. Streaming backpressure drops trace/log/listen messages. Legacy HTTP paths need body draining to preserve connections. This subset has no direct client tests; server registration and higher-level admin tests are the likely coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/peer-rest-client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/peer-rest-common.go -->
# sources/object-store/minio/cmd/peer-rest-common.go

## Purpose
This file centralizes peer REST versioning, route paths, query/form key names, and a restart/update delay constant shared by peer client and server code.

## Important APIs, Types, and Functions
`peerRESTVersion` is `v39`, with `peerRESTPath` rooted under the MinIO reserved peer path. Constants define legacy method routes such as `/health`, `/verifybinary`, `/speedtest`, `/devnull`, and `/getreplicationmrf`. Key constants cover bucket/user/policy/signal/profiler/perf/metrics/listen parameters. `restartUpdateDelay` is 250 ms.

## Control Flow and State
There is no runtime control flow or state. This file is a compatibility contract.

## Dependencies and Integration Points
Both `peer-rest-client.go` and `peer-rest-server.go` consume these constants. Route versioning must remain aligned with registered handlers and remote clients during rolling updates.

## Risks and Test Signals
Changing route names or version without coordinated compatibility breaks internode communication. Query key mistakes can silently route wrong parameters to admin operations. Compilation catches missing constants, but behavioral compatibility relies on integration tests and rolling-upgrade discipline.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/peer-rest-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/peer-rest-server.go -->
# sources/object-store/minio/cmd/peer-rest-server.go

## Purpose
This file implements and registers the server side of MinIO peer REST/grid APIs. It exposes local node state and mutating admin operations to authenticated peers in distributed deployments.

## Important APIs, Types, and Functions
`peerRESTServer` is the handler receiver. The large `var` block defines pooled grid JSON/array wrappers and typed grid handlers for IAM, bucket metadata, stats, metrics, metacache, S3 bucket operations, rebalance, service signals, and streams. Handler methods include IAM delete/load operations, profiling, storage/server/system info, metric collection, bucket metadata reload/delete, listen/trace/console streaming, binary verify/commit, speed tests, netperf, replication MRF, heal/list/head/make/delete bucket, and `registerPeerRESTHandlers`.

## Control Flow and State
Most grid handlers validate object layer availability, parse `grid.MSS` parameters, call a global subsystem, and return `grid.RemoteErr` on failure. Legacy HTTP handlers authenticate through `IsValid`, use gob or zstd when needed, and drain/encode response bodies. Service signals can sleep until a scheduled time and may write to `globalServiceSignalCh`.

## Dependencies and Integration Points
The file integrates with global IAM, bucket metadata, event notifier, replication stats, grid manager, lock server, profiler, object layer, rebalance pools, tier config, metrics registries, console system, and router setup.

## Risks and Test Signals
This is a high-blast-radius internode surface: handlers mutate IAM caches, bucket metadata, binary state, rebalance state, and service lifecycle. Parameter validation is uneven across handlers, and some reloads run asynchronously or best-effort. Streaming handlers must handle slow clients without blocking publishers. Coverage is mostly integration-level through admin, peer, and bucket tests rather than direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/peer-rest-server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/peer-s3-client.go -->
# sources/object-store/minio/cmd/peer-s3-client.go

## Purpose
This file implements clustered S3 bucket operations across MinIO peers with pool-aware quorum semantics.

## Important APIs, Types, and Functions
`peerS3Client` abstracts bucket list/heal/head/make/delete plus host and pool metadata. `localPeerS3Client` calls local helpers directly. `remotePeerS3Client` calls grid RPCs. `S3PeerSys` owns peer clients and pool count. `HealBucket`, `ListBuckets`, `GetBucketInfo`, `MakeBucket`, and `DeleteBucket` fan out to peers using `errgroup.WithNErrs` and reduce errors per pool.

## Control Flow and State
Peer clients are built from endpoint nodes, including the local node. Remote grid connections are lazily cached via atomic pointers. Each cluster operation gathers per-node responses, groups errors by pool membership, applies read/write quorum reducers, and returns object-layer errors. `ListBuckets` also queues partial bucket heals when bucket quorum is lost.

## Dependencies and Integration Points
The file depends on `peer-s3-server.go` local helpers, grid handlers declared in `peer-rest-server.go`, endpoint pool metadata, `globalDriveConfig`, `globalMRFState`, and MinIO quorum reducers.

## Risks and Test Signals
Nil grid connections currently return nil results for some remote calls, which can be treated as success and may weaken immediate consistency during startup. Delete rollback recreates buckets unless `NoRecreate` is set. Pool quorum logic is central to correctness and should be covered by distributed bucket operation tests, though no direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/peer-s3-client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/peer-s3-server.go -->
# sources/object-store/minio/cmd/peer-s3-server.go

## Purpose
This file implements local bucket operations used by the peer S3 grid layer: heal, list, stat, delete, and create bucket across local drives.

## Important APIs, Types, and Functions
Constants define peer bucket parameter keys. `healBucketLocal` inspects each local drive, records before/after drive state, optionally deletes dangling buckets, or recreates missing volumes. `listBucketsLocal` lists active and optionally deleted buckets using quorum-aware helpers. `cloneDrives` snapshots the local drive map. `getBucketInfoLocal`, `deleteBucketLocal`, and `makeBucketLocal` run operations across drives with concurrency and quorum reducers.

## Control Flow and State
Each operation snapshots `globalLocalDrivesMap` under read lock, then uses `errgroup.WithNErrs`, often with concurrency 32. Errors are reduced with read or write quorum using `bucketOpIgnoredErrs`. Heal mutates drives only when not dry-run.

## Dependencies and Integration Points
The code integrates with local `StorageAPI` drives, volume APIs, deleted-bucket metadata paths, madmin heal result structures, and peer RPC handlers in `peer-rest-server.go`.

## Risks and Test Signals
Drive snapshots can become stale while operations are running. Heal ignores some delete errors and uses state arrays that must remain aligned with drives. Correctness depends on quorum reducers and storage backends. Peer S3 client tests are not present here, so coverage is likely through distributed object-layer tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/peer-s3-server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/perf-tests.go -->
# sources/object-store/minio/cmd/perf-tests.go

## Purpose
This file implements object, drive, and network performance measurement helpers used by MinIO admin support tooling and peer REST endpoints.

## Important APIs, Types, and Functions
`SpeedTestResult` records upload/download bytes, timings, TTFB, and errors. `selfSpeedTest` performs concurrent PUTs then GETs using the MinIO client and records durations. `netPerfRX` tracks received bytes between connection timing boundaries. `netperf` streams random data to peer `DevNull` endpoints. `siteNetperf` performs similar cross-site traffic through replication admin clients. `perfNetRequest` builds and executes site netperf HTTP requests.

## Control Flow and State
`selfSpeedTest` runs uploads for `opts.duration`, then downloads created objects for another duration. It cancels all workers on first real error and bypasses API freeze with performance metadata. Network tests use a shared random reader and close an EOF channel after duration, then compute TX/RX rates from atomic counters and RX sampling windows.

## Dependencies and Integration Points
The file depends on global MinIO clients, IAM/root access config, site replication system, peer clients, `DevNull` handlers, admin transports, and madmin result types.

## Risks and Test Signals
Perf tests intentionally create load and objects under a speed-test prefix, so cleanup expectations matter outside this file. Shared reader concurrency and first-error strings can race semantically even though counters are atomic. RX calculations depend on connection timing; disconnections produce zero/error results. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/perf-tests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/policy_test.go -->
# sources/object-store/minio/cmd/policy_test.go

## Purpose
This file tests bucket policy permission evaluation and conversion between MinIO's internal bucket policy type and minio-go bucket access policy structures.

## Important APIs, Types, and Functions
`TestPolicySysIsAllowed` builds a policy with get-location and put-object allows, then verifies anonymous and owner actions across matching and nonmatching buckets. `getReadOnlyStatement` creates minio-go read-only statements. `TestPolicyToBucketAccessPolicy` and `TestBucketAccessPolicyToPolicy` check round-trip conversion and invalid version errors.

## Control Flow and State
Tests are table-driven and compare exact booleans, errors, and deep-equal policy structures. There is no persistent state.

## Dependencies and Integration Points
The tests depend on `github.com/minio/pkg/v3/policy`, policy conditions, minio-go policy types, and conversion functions implemented elsewhere in the cmd package.

## Risks and Test Signals
The tests guard policy compatibility and owner bypass behavior for bucket-level access. They do not cover deny statements, condition-rich policies, wildcard principals beyond `*`, or JSON serialization, so broader policy tests are needed elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/post-policy-fan-out.go -->
# sources/object-store/minio/cmd/post-policy-fan-out.go

## Purpose
This file implements POST object fan-out, allowing one incoming buffer to be written to multiple object keys with per-entry metadata and tags.

## Important APIs, Types, and Functions
`fanOutOptions` carries encryption type, key material, KMS context, checksum, and MD5 hex. `fanOutPutObject` accepts fan-out entries and the buffered object content, then returns per-entry `ObjectInfo` and error slices.

## Control Flow and State
The function launches one goroutine per fan-out entry. Each goroutine builds a hash reader over the shared immutable byte slice, copies metadata, parses tags, optionally wraps encryption with `newEncryptReader`, and calls `objectAPI.PutObject` with versioning flags from `globalBucketVersioningSys`. Errors are stored by entry index.

## Dependencies and Integration Points
It depends on MinIO's hash reader, encryption/KMS helpers, object-layer `PutObject`, versioning system, and minio-go fan-out entry definitions.

## Risks and Test Signals
Fan-out concurrency can amplify memory and object-layer load because every entry reads from the same in-memory buffer. Error assignment in deferred closes can overwrite earlier errors for an entry. Encryption disables content verification through a new hash reader with unknown size. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/post-policy-fan-out.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/post-policy_test.go -->
# sources/object-store/minio/cmd/post-policy_test.go

## Purpose
This test file validates S3 POST policy upload behavior for SigV2, SigV4, malformed requests, content-length policy enforcement, redirects, and a reserved-bucket exploit regression.

## Important APIs, Types, and Functions
Policy builders create V2/V4 JSON policies with bucket, key, credential, date, metadata, content-encoding, and optional content-length conditions. `TestPostPolicyReservedBucketExploit` ensures browser-style POST requests cannot write into `.minio.sys`. `TestPostPolicyBucketHandler` runs V2 and V4 success/failure cases, malformed body/base64/multipart cases, and content-length range checks. `TestPostPolicyBucketHandlerRedirect` verifies `success_action_redirect` uploads and redirect Location construction. Helper constructors build signed multipart requests.

## Control Flow and State
Tests initialize object-layer config, register only the PostPolicy endpoint, create buckets, send requests through the router, and verify HTTP status plus object metadata or backend absence. Some cases intentionally mutate request bodies or content type.

## Dependencies and Integration Points
The tests exercise request signing helpers, POST policy parsing/checking, API router behavior, object-layer writes, erasure disk reads, and response header construction.

## Risks and Test Signals
This is strong regression coverage for policy bypass and malformed request handling. It does not exhaustively test every policy operator or fan-out path. The reserved bucket test depends on erasure internals and browser-enable behavior to reproduce the exploit conditions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/post-policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/postpolicyform.go -->
# sources/object-store/minio/cmd/postpolicyform.go

## Purpose
This file parses and validates S3 POST policy forms. It converts JSON policy documents into strict internal structures and checks request form fields against the declared policy conditions.

## Important APIs, Types, and Functions
`startsWithConds` defines which keys permit `starts-with`. `contentLengthRange` and `PostPolicyForm` model parsed policy state. `sanitizePolicy` uses `jstream` to reject duplicate top-level JSON keys before standard decoding. `parsePostPolicyForm` decodes expiration and conditions, accepting map conditions and array conditions for `eq`, `starts-with`, and `content-length-range`. `checkPostPolicy` enforces expiration, condition matching, multiple-value rejection, and the rule that every non-exempt form field appears in policy conditions.

## Control Flow and State
Parsing first sanitizes, then decodes with `DisallowUnknownFields`. Validation builds a `mustFindInPolicy` map from canonicalized form fields, removes exemptions, evaluates each policy condition, and fails if unaccounted fields remain.

## Dependencies and Integration Points
The file integrates with POST policy handlers, MinIO HTTP constants, encryption header exceptions, minio-go set helpers, and S3-select `jstream`.

## Risks and Test Signals
Policy parsing is security-sensitive. Duplicate key rejection prevents malicious JSON overriding, and strict field coverage blocks hidden form inputs. Content-length range is parsed here but enforced by the handler. `postpolicyform_test.go` and `post-policy_test.go` cover duplicate rejection, expiration, condition failures, exceptions, and checksum/header omissions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/postpolicyform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/postpolicyform_test.go -->
# sources/object-store/minio/cmd/postpolicyform_test.go

## Purpose
This file unit-tests POST policy parsing and condition checking independent of the HTTP handler.

## Important APIs, Types, and Functions
`TestParsePostPolicyForm` checks missing expiration, invalid JSON, duplicate `expiration`, duplicate `conditions`, duplicate bucket-condition payloads through repeated top-level keys, and a valid policy. `formValues` is a small fluent wrapper around `http.Header`. `TestPostPolicyForm` builds a minio-go post policy and validates many form-field permutations against `checkPostPolicy`.

## Control Flow and State
Tests generate current or expired policy documents, base64 encode/decode as the handler would, parse with `parsePostPolicyForm`, and compare exact error strings from `checkPostPolicy`.

## Dependencies and Integration Points
The tests depend on minio-go post policy generation, MinIO HTTP header constants, and the parser/validator in `postpolicyform.go`.

## Risks and Test Signals
The tests are high-value security regression signals for duplicate JSON handling, unsupported hidden fields, multiple form values, V2 signature exceptions, x-ignore fields, and SSE header exceptions. Exact error string assertions can be brittle if messages are refactored.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/postpolicyform_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/prepare-storage.go -->
# sources/object-store/minio/cmd/prepare-storage.go

## Purpose
This file prepares erasure storage during startup: logging endpoint errors, cleaning temporary metadata, resolving peer liveness, loading or initializing `format.json`, and waiting for quorum.

## Important APIs, Types, and Functions
`printEndpointError` rate-limits repeated endpoint logs. `bgFormatErasureCleanupTmp` renames old temp buckets, creates deleted-temp metadata, removes writable-check leftovers, and schedules metacache cleanup. `isServerResolvable` performs peer liveness checks. `connectLoadInitFormats` loads all disk formats, handles fatal disk errors, validates format values, initializes fresh disks when appropriate, and returns the quorum format. `waitForFormatErasure` initializes storage disks and loops until format quorum is available or startup is stopped.

## Control Flow and State
Startup first creates disk handles, then repeatedly calls `connectLoadInitFormats`. Fresh clusters distinguish first disk from later disks with `errNotFirstDisk` and `errFirstDiskWait`. On success, the deployment ID is stored globally and pushed into HTTP metadata.

## Dependencies and Integration Points
The code depends on storage disk initialization, erasure format helpers, global endpoints, internode transport, logger, OS signal channel, and reliable filesystem wrappers from this subset.

## Risks and Test Signals
Startup correctness depends on precise quorum and error classification. Wrong initialization on partially available disks can corrupt cluster membership, while over-fatal errors can block recovery. This subset has no direct tests; coverage likely comes from erasure startup and format tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/prepare-storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/rebalance-admin.go -->
# sources/object-store/minio/cmd/rebalance-admin.go

## Purpose
This file builds admin-facing rebalance status for erasure server pools.

## Important APIs, Types, and Functions
`rebalPoolProgress` reports object/version counts, bytes, bucket/object markers, elapsed time, and ETA. `rebalancePoolStatus` reports pool id, status, used fraction, and progress. `rebalanceAdminStatus` is the top-level status returned to admin clients. `rebalanceStatus` loads rebalance metadata, computes per-pool disk usage from `StorageInfo`, and fills progress/ETA for participating pools.

## Control Flow and State
The function loads persisted `rebalanceMeta` from pool 0, then derives current disk usage by summing disk available/total space per pool. ETA is estimated from target bytes, elapsed time, and bytes already processed, and is zeroed when the pool stopped or completed.

## Dependencies and Integration Points
The file depends on erasure pool metadata, storage info, rebalancing status enums, and admin serialization tags.

## Risks and Test Signals
`Used` can divide by zero if a pool reports zero total space. ETA can be unstable early in a rebalance, especially if `ps.Bytes` is zero. No direct tests in this subset; admin rebalance tests should verify stopped/completed/active cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/rebalance-admin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/rebalancemetric_string.go -->
# sources/object-store/minio/cmd/rebalancemetric_string.go

## Purpose
This generated file provides string names for the `rebalanceMetric` enum declared in rebalance implementation code.

## Important APIs, Types, and Functions
Compile-time index checks detect enum drift. `_rebalanceMetric_name` and `_rebalanceMetric_index` encode names, and `func (i rebalanceMetric) String() string` returns known names or `rebalanceMetric(<n>)`.

## Control Flow and State
There is no mutable state or branching beyond bounds checking in `String`.

## Dependencies and Integration Points
Rebalance metrics and logs use these names for operations such as `RebalanceBuckets`, `RebalanceObject`, `RebalanceRemoveObject`, and `SaveMetadata`.

## Risks and Test Signals
The main risk is stale generated output after enum changes; normal compilation catches ordinal changes through the generated check block.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/rebalancemetric_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/rebalstatus_string.go -->
# sources/object-store/minio/cmd/rebalstatus_string.go

## Purpose
This generated file provides string names for the `rebalStatus` enum used in rebalance metadata and admin status.

## Important APIs, Types, and Functions
The generated `_` function checks enum ordinal stability. `_rebalStatus_name`, `_rebalStatus_index`, and `func (i rebalStatus) String() string` map statuses to names: `None`, `Started`, `Completed`, `Stopped`, and `Failed`.

## Control Flow and State
There is no mutable state. Out-of-range statuses are formatted as `rebalStatus(<n>)`.

## Dependencies and Integration Points
`rebalance-admin.go` uses `ps.Info.Status.String()` to expose status text to admin clients.

## Risks and Test Signals
Stale generation is the main risk and is caught at compile time if enum values change. Behavioral tests should focus on rebalance admin output rather than this generated helper.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/rebalstatus_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/routers.go -->
# sources/object-store/minio/cmd/routers.go

## Purpose
This file composes MinIO's HTTP server router and distributed erasure internode routes.

## Important APIs, Types, and Functions
`registerDistErasureRouters` registers storage REST, peer REST, bootstrap, namespace lock handlers, and grid routes when running distributed erasure. `globalMiddlewares` defines the common middleware chain: custom headers, tracing, auth, browser redirects, cross-domain policy, request limits, request validity, upload forwarding, and bucket forwarding. `configureServerHandler` builds the mux router, registers admin, health, metrics, STS, KMS, and S3 API routers, and applies middlewares.

## Control Flow and State
Router setup is conditional on `globalIsDistErasure` for internode paths, then unconditionally adds public/admin service routers. The mux is configured with `SkipClean(true)` and encoded path support to preserve S3 object key semantics.

## Dependencies and Integration Points
This file integrates peer REST handlers from this subset, storage REST, lock REST, bootstrap handlers, grid managers, admin middleware, and all HTTP API routers.

## Risks and Test Signals
Middleware order is security- and observability-sensitive: tracing must see early returns, auth must run before handlers, and forwarding must occur after validity checks. Path normalization settings are critical for object key compatibility. Route coverage is likely integration-level through API/admin/router tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/routers.go -->
