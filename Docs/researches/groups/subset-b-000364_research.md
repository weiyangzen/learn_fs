# subset-b-000364 research

Grouped research report for the requested `csi-driver-nfs` NFS driver and release-tools files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/controllerserver_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/controllerserver_test.go

Purpose: exercises the NFS CSI controller server behavior for dynamic volume creation/deletion, controller capabilities, volume and snapshot ID parsing, snapshot creation/deletion, volume expansion, cloning from volumes and snapshots, and compression compatibility.

Important APIs and helpers: `initTestController`, `initTestControllerWithOptions`, `TestCreateVolume`, `TestDeleteVolume`, `TestControllerGetCapabilities`, `TestNfsVolFromId`, `TestNewNFSVolume`, `TestCopyVolume`, `TestCreateSnapshot`, `TestDeleteSnapshot`, `TestControllerExpandVolume`, `matchCreateSnapshotResponse`, `TestCreateSnapshotWithoutCompression`, `TestCreateSnapshotWithDifferentShareInSnapshotClass`, `TestCopyVolumeFromUncompressedSnapshot`, `TestArchiveNameWithCompression`, and `TestGetNfsVolFromID`. The tests operate through `ControllerServer` plus fake Kubernetes mounters and temporary filesystem paths.

Control flow: the create-volume cases validate required names, mount capabilities, storage-class parameters, octal mount permissions, default subdirectory selection, and response volume context mutation. Delete cases validate invalid IDs as idempotent success, delete/retain/archive policy behavior, and path cleanup. Snapshot tests create source and snapshot directories, mount fake shares, write tar archives, and compare only meaningful snapshot fields while treating timestamp and size as presence signals. Clone tests dispatch through `copyVolume` into `copyFromVolume` or `copyFromSnapshot`, including missing source IDs and broken snapshot archives.

State and persistence behavior: the tests create real directories and tar files under `/tmp` and tear them down via `TestMain` or case cleanup. They verify the controller's state encoding rather than external persistence: old slash-delimited IDs, new hash-delimited IDs, UUID fields, on-delete policy suffixes, snapshot archive names, and internal working mount paths.

Dependencies and integration points: depends on the CSI protobuf API, gRPC status codes, `mount.FakeMounter`, Go tar/gzip packages, and filesystem operations. It integrates tightly with `controllerserver.go`, `nfs.go`, `utils.go`, and `tar.go` by asserting exact ID strings and path layouts.

Risks: tests rely on hard-coded `/tmp` paths, so parallel external runs can collide if names overlap. Some assertions use exact error values or status strings, which makes wording changes visible. Fake mounter behavior does not prove real NFS server semantics, mount propagation, quota behavior, or cross-platform archive behavior.

Test signals: strong signal for controller parameter validation, path traversal rejection, deletion policy semantics, snapshot compression and backward compatibility, source-volume vs snapshot-class share selection, and CSI capability advertisement. It does not cover list/get volume implementations because those are intentionally unimplemented.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/controllerserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/fake_mounter.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/fake_mounter.go

Purpose: provides a test-only fake mount implementation for node and controller tests that need mount operations without touching real NFS mounts.

Important APIs and types: `fakeMounter` embeds `mount.FakeMounter` and overrides `Mount`, `MountSensitive`, and `IsLikelyNotMountPoint`. `NewFakeMounter` returns a `*mount.SafeFormatAndMount` with the fake as its `Interface`.

Control flow: `Mount` returns deterministic errors when the source or target contains `error_mount`. `MountSensitive` does the same for `error_mount_sens`. `IsLikelyNotMountPoint` returns an error for `error_is_likely`, returns mounted (`false, nil`) for `false_is_likely`, and otherwise returns not mounted (`true, nil`).

State and persistence behavior: no persistent state is maintained beyond the embedded fake type. The behavior is driven by string sentinels in the requested source, target, or file path.

Dependencies and integration points: integrates with `NodeServer` tests through Kubernetes `k8s.io/mount-utils` interfaces. It allows `NodePublishVolume`, `NodeUnpublishVolume`, and controller internal mount flows to be tested through the same interface shape as production mount code.

Risks: because it does not record mount tables unless the embedded fake behavior is used through other paths, it can miss real mount lifecycle issues. Sentinel substring matching can accidentally trigger if test names include those tokens.

Test signals: paired with `fake_mounter_test.go`, it validates deterministic mount, sensitive mount, and mountpoint error paths used by higher-level tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/fake_mounter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/fake_mounter_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/fake_mounter_test.go

Purpose: verifies the fake mounter's sentinel-driven success and error behavior.

Important APIs and helpers: `TestMount`, `TestMountSensitive`, and `TestIsLikelyNotMountPoint` install `fakeMounter` into a `mount.SafeFormatAndMount` and call the mount interface methods directly.

Control flow: each table includes source-error, target-error, and success cases. `IsLikelyNotMountPoint` cases cover an injected error path, default not-mounted behavior, and a sentinel path that reports already mounted.

State and persistence behavior: no external state is written. The tests replace the node server's mounter with an in-memory fake and compare returned errors with expected `fmt.Errorf` values.

Dependencies and integration points: depends on `getTestNodeServer` from node tests, `mount.SafeFormatAndMount`, and the fake mounter implementation. It protects the assumptions used by node publish/unpublish tests.

Risks: exact error comparison makes message edits visible. The fake does not emulate sensitive option handling or mount table mutation beyond returning errors.

Test signals: focused signal that all sentinel branches in `fake_mounter.go` behave as expected.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/fake_mounter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/identityserver.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/identityserver.go

Purpose: implements the CSI Identity service for the NFS driver.

Important APIs and types: `IdentityServer` embeds `csi.UnimplementedIdentityServer` and exposes `GetPluginInfo`, `Probe`, and `GetPluginCapabilities`.

Control flow: `GetPluginInfo` rejects empty driver name or version with `codes.Unavailable`, otherwise returns the configured driver name and vendor version. `Probe` always reports ready with a protobuf bool wrapper. `GetPluginCapabilities` advertises `PluginCapability_Service_CONTROLLER_SERVICE`.

State and persistence behavior: identity responses are derived from the in-memory `Driver` fields only. No persistent state, filesystem state, or network state is touched.

Dependencies and integration points: depends on CSI protobuf types, gRPC status codes, and `wrapperspb`. Registered by `server.go` when `Driver.Run` starts the gRPC server.

Risks: readiness is unconditional, so it does not prove mount dependencies, endpoint health, or controller/node initialization. Capability advertisement assumes a controller service is always registered.

Test signals: `identityserver_test.go` covers success and missing driver metadata paths, readiness response, and advertised plugin capability.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/identityserver_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/identityserver_test.go

Purpose: validates CSI Identity service responses and error handling.

Important APIs and helpers: `TestGetPluginInfo`, `TestProbe`, and `TestGetPluginCapabilities` use `NewEmptyDriver` to create normal, empty-name, and empty-version driver states.

Control flow: plugin info cases call `GetPluginInfo` and compare expected gRPC errors for unavailable name or version. Probe asserts a non-nil response with ready=true. Capabilities asserts the single controller-service plugin capability.

State and persistence behavior: entirely in-memory. The tests mutate only the driver metadata used by identity responses.

Dependencies and integration points: depends on CSI types, gRPC status codes, testify assertions, and `nfs_test.go` helpers. It validates what clients see when `server.go` registers the identity service.

Risks: exact equality for capability structs can be sensitive to additional capabilities. It does not exercise server registration or gRPC transport.

Test signals: solid unit signal for the identity server's public CSI contract.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/identityserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/nfs.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/nfs.go

Purpose: defines the main NFS CSI driver configuration, runtime state, default capabilities, startup sequence, corruption helper, and metadata replacement helper.

Important APIs and types: `DriverOptions`, `Driver`, constants for parameter names and metadata placeholders, `NewDriver`, `NewNodeServer`, `Run`, `AddControllerServiceCapabilities`, `AddNodeServiceCapabilities`, `IsCorruptedDir`, and `replaceWithMap`.

Control flow: `NewDriver` copies deployment options into a `Driver`, registers default controller capabilities for create/delete, single-node multi-writer, clone, snapshot, and expansion, registers node stats and multi-writer capabilities, initializes volume locks, and creates timed caches for volume stats and deletion idempotency. `Run` logs version metadata, creates a Kubernetes mounter, wraps it with force-unmount support on Linux, constructs the node server, registers identity/controller/node services in a non-blocking gRPC server, and waits.

State and persistence behavior: maintains in-memory driver metadata, CSI capabilities, locks, and timed caches. It does not persist volumes; persistent storage state is represented by NFS directories created by controller/node operations.

Dependencies and integration points: depends on CSI protobufs, `k8s.io/mount-utils`, klog, runtime metadata, and the local timed cache implementation. It is the entry point connecting identity, controller, node, and gRPC server files.

Risks: `Run` fatals on version YAML or server startup failures. Default cache expiry is mutated in local options after some fields have already been copied, while cache construction uses the corrected value. `replaceWithMap` iterates map keys in random order, so overlapping placeholders would be order-dependent.

Test signals: `nfs_test.go` covers fake driver construction, `Run` in test mode, capability constructors, corrupted-dir helper basics, and metadata replacement behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/nfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/nfs_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/nfs_test.go

Purpose: tests driver helpers that are shared across identity, controller, and node tests.

Important APIs and helpers: `NewEmptyDriver`, `TestNewFakeDriver`, `TestIsCorruptedDir`, `TestRun`, `TestNewControllerServiceCapability`, `TestNewNodeServiceCapability`, and `TestReplaceWithMap`.

Control flow: `NewEmptyDriver` builds small in-memory drivers with optional missing name or version and initializes locks plus the stats cache. `TestRun` starts the gRPC server on `tcp://127.0.0.1:0` with test mode enabled so it stops itself after startup. Capability tests instantiate several enum values. Replacement tests cover empty strings, empty keys, empty values, and multiple PVC/PV placeholders.

State and persistence behavior: creates temporary directories and a symlink for corrupted-dir checks, and starts a transient local gRPC listener. No volume state is persisted.

Dependencies and integration points: depends on CSI enums, testify, filesystem helpers, and `Driver.Run`. It supplies helpers consumed by identity, fake mounter, and node tests.

Risks: `TestRun` depends on local TCP listener availability and the test-mode goroutine timing. The corrupted-dir test has limited coverage and does not force a real corrupted mount error.

Test signals: good smoke coverage for driver initialization helpers and server startup, but not a full integration test of real NFS operations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/nfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/nodeserver.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/nodeserver.go

Purpose: implements the CSI Node service for publishing/unpublishing NFS volumes, reporting node identity/capabilities, returning filesystem stats, and rejecting unsupported stage/unstage/expand operations.

Important APIs and types: `NodeServer`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeGetInfo`, `NodeGetCapabilities`, `NodeGetVolumeStats`, `NodeStageVolume`, `NodeUnstageVolume`, `NodeExpandVolume`, `makeDir`, `isStaleFileHandle`, and the test-injectable `lstatFunc`.

Control flow: `NodePublishVolume` validates volume capability, volume ID, and target path, locks by volumeID-targetPath, collects mount flags and readonly mode, parses `server`, `share`, `subdir`, metadata placeholders, mount options, and mount permissions, validates the final NFS source path, creates the target when missing, returns idempotently when already mounted, unmounts and remounts stale NFS handles, mounts with a timeout, and chmods when permissions are nonzero. `NodeUnpublishVolume` validates and locks, then uses forced cleanup when the mounter implements `MounterForceUnmounter`, otherwise normal cleanup. `NodeGetVolumeStats` caches statfs responses by volume ID after validating path existence.

State and persistence behavior: writes mount target directories and changes permissions on mounted paths. Uses in-memory locks and timed volume stats cache. It relies on the host mount table through Kubernetes mount utilities for actual persistence of mounts.

Dependencies and integration points: depends on CSI protobufs, gRPC status codes, klog, `k8s.io/mount-utils`, Kubernetes volume metrics, OS/syscall errors, and helper functions in `utils.go` and `nfs.go`. Controller internal mount/unmount routes through this node service.

Risks: `WaitUntilTimeout` times out the caller but cannot cancel the underlying mount goroutine. Path validation rejects only slash-separated `..`, not Windows backslash traversal. Mount options from the volume context are appended as a single string. Stats cache is keyed only by volume ID, not path, so reused IDs across paths can return stale stats until expiry.

Test signals: `nodeserver_test.go` covers validation errors, lock conflicts, missing target creation, readonly and zero-permission flows, stale handle remount, unpublish validation, node info/capabilities, statfs success/error, and stale-handle detection.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/nodeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/nodeserver_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/nodeserver_test.go

Purpose: validates CSI node publish/unpublish, node info/capabilities, volume stats, and stale NFS handle detection.

Important APIs and helpers: `TestNodePublishVolume`, `TestNodeUnpublishVolume`, `TestNodeGetInfo`, `TestNodeGetCapabilities`, `getTestNodeServer`, `TestNodeGetVolumeStats`, and `TestIsStaleFileHandle`.

Control flow: publish cases check missing capability, missing volume ID, missing target, lock conflicts, target creation, readonly mounts, already-mounted targets, PV/PVC metadata contexts, zero mount permissions, invalid octal permissions, and injected `ESTALE` remount. Unpublish cases check required fields, not-mounted cleanup, and lock conflicts. Stats cases cover missing IDs/paths, nonexistent paths, and normal statfs on a temporary directory.

State and persistence behavior: creates and removes test directories under the repository/test utility workdir and `/tmp`. Temporarily overrides `lstatFunc` to simulate stale handles and restores it in cleanup.

Dependencies and integration points: depends on `NewFakeMounter`, `NewEmptyDriver`, CSI protobufs, gRPC status codes, test utility path helpers, and `syscall.ESTALE`.

Risks: fake mounter means no real kernel mount table or NFS server is exercised. Some table fields are unused or only partially asserted. Volume stats success depends on host filesystem metric availability.

Test signals: useful unit-level signal for validation, locking, idempotency, stale remount behavior, and stat response construction.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/nodeserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/server.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/server.go

Purpose: provides a small non-blocking gRPC server wrapper for registering and serving CSI identity, controller, and node services.

Important APIs and types: `NonBlockingGRPCServer`, `NewNonBlockingGRPCServer`, `nonBlockingGRPCServer.Start`, `Wait`, `Stop`, `ForceStop`, and `serve`.

Control flow: `Start` increments a wait group and launches `serve` in a goroutine. `serve` parses the endpoint, removes stale Unix sockets, listens, creates a gRPC server with the `logGRPC` unary interceptor, conditionally registers provided CSI services, and calls `Serve`. In test mode it marks startup complete and schedules a graceful stop after a short delay so tests do not block forever.

State and persistence behavior: holds the active `*grpc.Server` and wait group in memory. It may delete a Unix-domain socket path before listening.

Dependencies and integration points: depends on `ParseEndpoint`, `logGRPC`, CSI registration functions, `net`, `os`, `sync`, `time`, gRPC, and klog. Called by `Driver.Run`.

Risks: failures call `klog.Fatal/Fatalf`, terminating the process rather than returning errors. `Stop`/`ForceStop` assume `server` has been initialized. Test-mode wait-group handling is subtle because it uses the same wait group for startup and final wait.

Test signals: indirectly smoke-tested by `TestRun`; no dedicated tests cover Unix socket cleanup, listener failures, or stop ordering.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/tar.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/tar.go

Purpose: implements Go-native tar/gzip pack and unpack helpers used by snapshot creation and restore when the driver is not configured to shell out to `tar`.

Important APIs and functions: `TarPack`, `tarVisitFileToPack`, `TarUnpack`, `tarUnpackFile`, `tarWriteFile`, and `closeAndWrapErr`.

Control flow: `TarPack` normalizes source and destination paths, rejects destinations under the source directory, creates the archive and optional gzip writer, walks the source tree, writes tar headers for files/directories/symlinks, and copies regular file contents. `TarUnpack` normalizes and creates the destination, resolves destination symlinks, opens optional gzip input, iterates tar headers, rejects zip-slip paths via `filepath.Rel`, checks existing ancestor symlinks to prevent writes outside the destination, creates directories, preserves symlinks as symlinks, removes existing symlinks before regular writes, writes files with mode permissions, verifies regular-file byte counts, and restores file and directory timestamps.

State and persistence behavior: creates archive files during pack and writes directories, files, symlinks, modes, and timestamps during unpack. It does not persist metadata outside filesystem content.

Dependencies and integration points: depends on Go archive/tar, gzip, filesystem, sorting, and error joining APIs. Controller snapshot code calls `TarPack` and `TarUnpack` for snapshot archives unless configured to use the external `tar` command.

Risks: `TarPack` uses `strings.HasPrefix(filepath.Dir(dstPath), srcDirPath)` which can reject prefix-collision paths such as `/tmp/src2` when source is `/tmp/src`; this is conservative but broad. `TarUnpack` preserves absolute symlink targets, which is archive-faithful but can create links pointing outside the destination. It does not apply ownership from tar headers.

Test signals: `tar_test.go` covers code/CLI interoperability, zip-slip rejection, same-directory packing rejection, symlink preservation, and timestamp restoration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/tar_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/tar_test.go

Purpose: validates the tar/gzip helpers for archive compatibility, traversal safety, symlink handling, and timestamp preservation.

Important APIs and helpers: `TestPackUnpack`, `produce`, `assertUnpackedFilesEqual`, `generateFileSystem`, `TestUnpackZipSlip`, `TestPackSameDir`, `TestSymlinks`, and `TestTarUnpackPreservesTimestamps`.

Control flow: pack/unpack compatibility generates combinations of four alternating pack/unpack operations using either Go code or the system `tar` CLI, then hashes resulting directories with `dirhash`. Zip-slip builds a malicious tar header with `../` and expects `tar.ErrInsecurePath`. Same-dir verifies pack rejects an archive inside the source. Symlink tests pack and unpack absolute and relative symlinks. Timestamp tests set known file and directory mtimes, pack/unpack, then compare restored mtimes with tolerance.

State and persistence behavior: creates temporary source/output directories, archives, symlinks, and a large test file. The large-file generator repeatedly overwrites a 1 MiB file rather than appending to 100 MiB, so it still tests non-empty binary content without the comment's implied size.

Dependencies and integration points: depends on the local tar helpers, the host `tar` executable for compatibility cases, `golang.org/x/mod/sumdb/dirhash`, and filesystem timestamp behavior.

Risks: CLI compatibility tests depend on `tar` availability and platform behavior. Absolute symlink tests can fail on platforms that restrict symlink creation. Hash comparisons focus on content and names, not every metadata bit.

Test signals: strong security and interoperability signal for snapshot archive operations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/tar_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/utils.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/utils.go

Purpose: contains shared constants and helpers for CSI capabilities, endpoint parsing, gRPC logging, per-volume locks, mount options, chmod behavior, server address normalization, path cleanup, timeouts, secret-derived mount capabilities, and path traversal validation.

Important APIs and types: constants `separator`, `delete`, `retain`, `archive`, `volumeOperationAlreadyExistsFmt`; `validateOnDeleteValue`; constructors `NewDefaultIdentityServer`, `NewControllerServer`, `NewControllerServiceCapability`, `NewNodeServiceCapability`; `ParseEndpoint`; `getLogLevel`; `logGRPC`; `VolumeLocks`; `getMountOptions`; `unixModeToFileMode`; `chmodIfPermissionMismatch`; `getServerFromSource`; `setKeyValueInMap`; `waitForPathNotExistWithTimeout`; `removeEmptyDirs`; `WaitUntilTimeout`; `getVolumeCapabilityFromSecret`; and `validatePath`.

Control flow: endpoint parsing accepts only `unix://` and `tcp://` with non-empty addresses. `logGRPC` logs sanitized requests/responses and lowers verbosity for chatty calls. `VolumeLocks` uses a mutex-protected set for nonblocking acquire/release. Chmod compares permission plus special bits before calling platform-specific `chmod`. Cleanup helpers poll for deletion and remove empty parent directories up to a depth limit. `WaitUntilTimeout` races a goroutine against `time.After`. `validatePath` rejects path segments exactly equal to `..`.

State and persistence behavior: lock state is in memory. Chmod and directory cleanup mutate filesystem metadata. Logging emits through klog. No durable driver metadata is persisted.

Dependencies and integration points: depends on CSI types, protosanitizer, gRPC interceptors, Kubernetes sets, klog, net IPv6 utilities, OS/filesystem APIs, and platform-specific `chmod` files. Used throughout controller, node, server, and tests.

Risks: `removeEmptyDirs` uses a raw prefix check after `filepath.Abs`, which can misclassify prefix collisions such as `/tmp/a2` under `/tmp/a`; path traversal validation ignores backslash separators; `WaitUntilTimeout` does not cancel a timed-out operation; mount options from secrets are represented as one mount flag string.

Test signals: `utils_test.go` covers endpoint parsing, log levels, mount-option lookup, chmod mismatch handling, IPv6 bracket formatting, case-insensitive map updates, on-delete validation, deletion polling, empty-dir removal, timeout behavior, secret mount options, and path traversal validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/utils_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/utils_test.go

Purpose: provides focused unit tests for shared utility functions used by the NFS driver.

Important APIs and helpers: `TestParseEndpoint`, `TestGetLogLevel`, `TestGetMountOptions`, `TestChmodIfPermissionMismatch`, `TestGetServerFromSource`, `TestSetKeyValueInMap`, `TestValidateOnDeleteValue`, `TestWaitForPathNotExistWithTimeout`, `TestRemoveEmptyDirs`, `TestWaitUntilTimeout`, `TestGetVolumeCapabilityFromSecret`, and `TestValidatePath`.

Control flow: table tests cover valid and invalid endpoints, lowered log levels for probe/capability/stats calls, case-insensitive mount option lookup, chmod no-op and mismatch paths, IPv4/IPv6/FQDN formatting, case-insensitive map replacement, supported delete/retain/archive policies, polling timeout, recursive empty-dir cleanup, goroutine timeout behavior, and slash-based path traversal detection.

State and persistence behavior: creates directories in the current working directory for chmod and cleanup tests, waits on real timers, and uses goleak to detect goroutine leaks after timeout tests.

Dependencies and integration points: depends on CSI protobufs and goleak. It verifies helper behavior consumed by controller/node/server paths.

Risks: some expected errors are platform-specific, especially invalid path and chmod behavior. The timeout test intentionally leaves a sleeping goroutine briefly and waits before goleak verification. Backslash traversal is explicitly expected not to fail, documenting the current Unix-centric validation.

Test signals: broad helper-level coverage with useful regression signal for security-sensitive path validation and timeout/cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/version.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/version.go

Purpose: reports build and runtime version metadata for logs and identity responses.

Important APIs and types: build-time variables `driverVersion`, `gitCommit`, and `buildDate`; `VersionInfo`; `GetVersion`; and `GetVersionYAML`.

Control flow: `GetVersion` constructs a `VersionInfo` from the requested driver name, ldflag-populated build variables, and Go runtime metadata. `GetVersionYAML` marshals that structure with `sigs.k8s.io/yaml` and trims surrounding whitespace.

State and persistence behavior: all state is process-global build metadata and runtime information. No external state is read or written.

Dependencies and integration points: used by `NewDriver`, `Driver.Run`, and identity server version reporting. Depends on `runtime`, `fmt`, `strings`, and YAML marshaling.

Risks: default values are `N/A` unless build ldflags set them. YAML key names come from JSON tags with spaces, so downstream parsers should not assume Go field names.

Test signals: `version_test.go` verifies default `VersionInfo` construction and YAML output consistency with the same marshaller.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/version_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/version_test.go

Purpose: validates version metadata helpers.

Important APIs and helpers: `TestGetVersion` and `TestGetVersionYAML`.

Control flow: `TestGetVersion` compares `GetVersion(DefaultDriverName)` with an expected struct containing default build metadata and runtime Go/compiler/platform values. `TestGetVersionYAML` marshals `GetVersion("")` with the same YAML package and compares it to `GetVersionYAML("")`.

State and persistence behavior: no filesystem or network state. It observes package-global build variables in their default test values.

Dependencies and integration points: depends on runtime metadata and `sigs.k8s.io/yaml`. It protects log/diagnostic output consumed by `Driver.Run`.

Risks: tests intentionally assume ldflags are not overriding build variables in the unit-test environment. Runtime values vary by Go toolchain and platform but are computed dynamically in expected data.

Test signals: focused signal for version struct population and YAML formatting.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/.github/dependabot.yaml -->
# sources/control-plane/csi-driver-nfs/release-tools/.github/dependabot.yaml

Purpose: configures Dependabot for the release-tools repository copy.

Important configuration: uses Dependabot `version: 2`, enables beta ecosystems, and defines one update rule for the `github-actions` ecosystem in the root directory.

Control flow: Dependabot runs daily, labels PRs with `area/dependency`, `release-note-none`, and `ok-to-test`, and limits open dependency PRs to ten.

State and persistence behavior: state is maintained by GitHub Dependabot outside the repository; this file only declares desired scheduling and labels.

Dependencies and integration points: integrates with GitHub Actions workflow dependency scanning and Kubernetes project labeling conventions.

Risks: only GitHub Actions dependencies are covered; Go modules, Docker images, and other ecosystems are not updated by this config. Labels must exist or be acceptable in target repos.

Test signals: no local tests. Validation happens when GitHub parses the config and Dependabot starts opening PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/.github/workflows/codespell.yml -->
# sources/control-plane/csi-driver-nfs/release-tools/.github/workflows/codespell.yml

Purpose: runs codespell on pushes and pull requests for the release-tools repository copy.

Important configuration: workflow `codespell` checks out the repository at a pinned action commit and runs `codespell-project/actions-codespell` at a pinned commit. It enables filename checking and skips binary/image patterns, `.git`, the workflow itself, and `prow.sh`.

Control flow: GitHub Actions triggers on `push` and `pull_request`, runs on Ubuntu latest, checks out source, and executes the codespell action.

State and persistence behavior: no repository state is mutated. The workflow emits CI status and logs in GitHub Actions.

Dependencies and integration points: depends on GitHub Actions, actions/checkout, and the codespell action. It complements local spelling or boilerplate checks.

Risks: `prow.sh` is skipped, so spelling issues there are not caught. Pinned action SHAs must be maintained manually or by Dependabot.

Test signals: CI status is the signal; there are no in-repo tests for the workflow file.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/.github/workflows/trivy.yaml -->
# sources/control-plane/csi-driver-nfs/release-tools/.github/workflows/trivy.yaml

Purpose: scans the configured Go toolchain image for vulnerabilities with Trivy.

Important configuration: triggers on pushes to `master` and daily midnight UTC schedule. It checks out code, extracts `CSI_PROW_GO_VERSION_BUILD` from `prow.sh`, then scans `golang:<version>` with `aquasecurity/trivy-action`.

Control flow: the `Get Go version` shell step greps the release-tools `prow.sh` config line and writes the version to GitHub step output. The Trivy step scans the corresponding Golang image, outputs a table, ignores unfixed vulnerabilities, and fails on all severities including unknown.

State and persistence behavior: no repo mutation. Results are GitHub Actions logs/status.

Dependencies and integration points: integrates with `prow.sh` as the source of the supported Go version, GitHub Actions, actions/checkout, and Trivy.

Risks: parsing `prow.sh` with `grep|awk|sed` is brittle if the config line format changes. Scanning the base Golang image may fail for vulnerabilities unrelated to project code.

Test signals: CI failure signals vulnerable Go base image or parsing/action problems.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/.prow.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/.prow.sh

Purpose: custom Prow entrypoint for testing `csi-release-tools` itself, where the normal imported `prow.sh` flow is not appropriate.

Important commands: runs `./verify-shellcheck.sh`, `./verify-spelling.sh`, and `./verify-boilerplate.sh` against the current directory.

Control flow: the script uses a `bash -e` shebang so it stops on the first failed verification command.

State and persistence behavior: verification scripts may create temporary files or logs, but this wrapper itself does not mutate repository state.

Dependencies and integration points: expects release-tools verification scripts to be executable in the current working directory. Used by Prow jobs for the release-tools repository.

Risks: assumes the caller's working directory is the release-tools root. It does not run Go tests, Prow cluster flows, or cloud build logic.

Test signals: Prow pass/fail for shellcheck, spelling, and boilerplate quality gates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/boilerplate/boilerplate.py -->
# sources/control-plane/csi-driver-nfs/release-tools/boilerplate/boilerplate.py

Purpose: checks repository files for required Kubernetes copyright boilerplate headers.

Important APIs and functions: command-line arguments for file list, root directory, boilerplate directory, and verbosity; `get_refs`, `file_passes`, `file_extension`, `normalize_files`, `get_files`, `get_regexs`, and `main`.

Control flow: loads reference boilerplate files keyed by extension or basename, walks selected files while pruning skipped directories, strips Go build constraints and shell/Python shebangs, compares the first lines of each file against the reference after normalizing year values, and prints filenames that fail.

State and persistence behavior: reads source files and boilerplate reference files only. It writes failure filenames to stdout and optional diagnostics to stderr; it does not modify files.

Dependencies and integration points: invoked by `verify-boilerplate.sh`. Depends on Python standard libraries `argparse`, `difflib`, `glob`, `os`, `re`, `sys`, and `datetime`.

Risks: assumes a reference exists for each selected extension or basename. Year normalization only searches years from 2014 through the current year. Directory skipping is substring-based and can skip paths that merely contain a skipped token.

Test signals: no dedicated test file in this subset; `verify-boilerplate.sh` runs it as a gate and fails when any filenames are printed.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/cloudbuild.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/cloudbuild.sh

Purpose: thin Cloud Build entrypoint that delegates multi-architecture image build and push setup to release-tools `prow.sh`.

Important APIs and commands: sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: the `bash` script loads the shared Prow/release helper functions, then invokes `gcr_cloud_build`, which configures Docker credentials, optional QEMU support, derives `REV`, and calls `make push-multiarch`.

State and persistence behavior: state changes are performed by the delegated function: Docker credential configuration, possible QEMU registration, and pushed images. This file itself only controls execution.

Dependencies and integration points: used by `cloudbuild.yaml` as `./.cloudbuild.sh`, often as a symlink/copy in consuming CSI repos. Requires `release-tools/prow.sh` to exist at runtime.

Risks: fails if called from a repo layout where `release-tools/prow.sh` is not available. All behavior is inherited from the large shared function.

Test signals: validated by Cloud Build jobs rather than local tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/cloudbuild.yaml -->
# sources/control-plane/csi-driver-nfs/release-tools/cloudbuild.yaml

Purpose: Google Cloud Build configuration for Kubernetes CSI multi-architecture image publishing.

Important configuration: sets a 7200-second timeout, allows loose substitutions, runs one step using `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f`, invokes `./.cloudbuild.sh`, and passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME`.

Control flow: Cloud Build fills substitutions, starts the Docker/gcloud image, executes the repository's `.cloudbuild.sh`, and relies on that script to call `gcr_cloud_build`.

State and persistence behavior: Cloud Build produces container images in the configured staging registry; the repository checkout is not committed back.

Dependencies and integration points: integrates with Kubernetes test-infra image-pushing jobs, the staging project `k8s-staging-sig-storage`, `cloudbuild.sh`, and consuming repos' Makefile/Dockerfile conventions.

Risks: assumes Dockerfiles accept a `binary` build argument and the repo supports `make push-multiarch`. Pinned builder images and substitutions need periodic maintenance.

Test signals: Cloud Build status and pushed image artifacts are the practical validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/contrib/get_supported_version_csi-sidecar.py -->
# sources/control-plane/csi-driver-nfs/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: helper script for listing supported Kubernetes CSI sidecar release versions and optional Docker images for documentation updates.

Important APIs and functions: `check_gh_command`, `duration_ago`, `parse_version`, `end_of_life_grouped_versions`, `get_release_docker_image`, `get_versions_from_releases`, and `main`.

Control flow: parses one or more `--repo owner/repo` arguments, ensures `gh` is installed, calls `gh release list`, groups semantic `vX.Y.Z` releases by major/minor, applies CSI support policy heuristics where latest is always supported, releases younger than one year are supported, and older minors with a patch younger than three months are supported, then prints supported versions and optionally release-page Docker image references.

State and persistence behavior: reads live GitHub release data via the GitHub CLI and current local time. It prints results; it does not write files.

Dependencies and integration points: depends on Python, `python-dateutil`, GitHub CLI authentication/network access, and release-note text conventions containing `docker pull ...`.

Risks: output changes over time because it uses current date and GitHub release state. Release list parsing assumes tab-delimited `gh release list` columns. Docker image extraction is regex-based and can miss changed release-note formats.

Test signals: no tests in this subset; correctness is manual and depends on GitHub CLI output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/contrib/get_supported_version_csi-sidecar.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/filter-junit.go -->
# sources/control-plane/csi-driver-nfs/release-tools/filter-junit.go

Purpose: filters and merges JUnit XML files so Prow/Spyglass artifacts focus on relevant CSI test cases.

Important APIs and types: command-line flags `-o` for output and `-t` for testcase name regex; XML structs `TestResults`, `TestSuite`, `TestCase`, and `SkipReason`; `main`.

Control flow: compiles the testcase regex, reads each input file or stdin, unmarshals either legacy `<testsuite>` or newer Ginkgo v2 `<testsuites><testsuite>` format, appends testcases, filters by name regex, de-duplicates by testcase name, replaces an all-skipped entry with a real run when available, marshals indented XML, and writes stdout or the output path.

State and persistence behavior: reads input XML files and writes one merged XML file. It does not modify inputs.

Dependencies and integration points: called by `prow.sh` after make, E2E, or sanity test steps. Depends on Go `encoding/xml`, flags, regexp, and OS file APIs.

Risks: stdin path uses `os.Stdin.Read(data)` with an empty slice, which will not read arbitrary stdin content correctly. Output testcase ordering is map iteration order, so merged XML order is nondeterministic. The XML structs preserve only selected fields.

Test signals: no dedicated tests in this subset; it is exercised indirectly by Prow artifact generation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/filter-junit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/generate-patch-release-notes.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/generate-patch-release-notes.sh

Purpose: automates generation of changelog PRs for Kubernetes CSI patch releases.

Important variables and functions: editable `releases` array, `gen_patch_relnotes`, `CSI_RELEASE_TOKEN`, and `GITHUB_USER`.

Control flow: for each configured `repo version`, parses the minor and patch numbers, computes the previous patch tag, enters the repo's `CHANGELOG` directory, fetches upstream, recreates a `changelog-release-<minor>` branch from the upstream release branch, runs the Kubernetes `release-notes` tool, prepends a new release notes section to `CHANGELOG-<minor>.md`, commits, force-pushes, and opens a GitHub PR.

State and persistence behavior: mutates local git branches and changelog files, writes temporary `out.md`/`tmp.md`, force-pushes branches, and creates PRs on GitHub.

Dependencies and integration points: depends on `gh`, `release-notes`, git remotes named upstream/origin, GitHub credentials, and Kubernetes CSI changelog layout.

Risks: the releases array is manual and empty by default. It force-pushes branches and deletes local branches. It assumes previous patch version exists and that changelog files live under `repo/CHANGELOG`.

Test signals: no tests; success is visible through generated changelog commits and PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/generate-patch-release-notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/go-get-kubernetes.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/go-get-kubernetes.sh

Purpose: updates Go module dependencies that come from `kubernetes/kubernetes` staging modules to a target Kubernetes release.

Important arguments and variables: optional `-p` prunes unused replace statements; required positional Kubernetes version `x.y.z`; `help`, `die`, `mods`, `packages`, and `deps`.

Control flow: fetches Kubernetes `go.mod` for the target tag, extracts staging module replace entries, adds or prunes local `go.mod` replacements to the corresponding `kubernetes-<version>` module versions, lists imported `k8s.io` packages, maps packages to modules with replace statements, builds a `go get` dependency list pinned to `kubernetes-<version>` or `v<version>` for `k8s.io/kubernetes`, and runs `go get`.

State and persistence behavior: mutates the current repository's `go.mod` via `go mod edit` and `go get`; may download modules into the Go module cache. It does not commit changes.

Dependencies and integration points: used by module update scripts and Prow/release workflows. Requires curl, sed, grep, Go modules, network access to GitHub and module proxies, and a valid current `go.mod`.

Risks: parsing upstream `go.mod` and local package lists is shell/regex based. It changes directory to `/` for module download to avoid local incomplete go.mod influence. `go list all` fallback may still fail in broken workspaces.

Test signals: no local tests; success is the final `SUCCESS` and resulting module graph/build.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/go-get-kubernetes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/go-modules-targeted-update.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/go-modules-targeted-update.sh

Purpose: batch-updates a curated list of Go modules across selected Kubernetes CSI sidecar release branches and opens PRs.

Important variables: `org`, `modules`, `releases`, `GITHUB_USER`, and required GitHub credentials. The default module list contains `github.com/kubernetes-csi/csi-lib-utils@v0.15.1`; release entries are commented out.

Control flow: for each `repo branch` in `releases`, fetches upstream, recreates `module-update-<branch>` from upstream, runs `go get` for each configured module, then `go mod tidy` and `go mod vendor`, pushes the branch to origin with force, and creates a PR against the branch with a release-note-none body.

State and persistence behavior: mutates local repo checkouts, go.mod/go.sum/vendor, git branches, remote branches, and GitHub PR state.

Dependencies and integration points: depends on bash arrays, git, Go modules, vendoring, `gh`, origin/upstream remote conventions, and Kubernetes CSI org workflow.

Risks: release list is manual and empty by default. Force pushes can overwrite existing update branches. The script does not run tests before pushing. Comments note interface incompatibilities must be resolved manually.

Test signals: no tests; PR creation and downstream CI are the validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/go-modules-targeted-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/go-modules-update.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/go-modules-update.sh

Purpose: batch-updates Kubernetes-related Go module dependencies across multiple Kubernetes CSI repositories and opens PRs.

Important arguments and variables: options `-u` for GitHub username and `-v` for Kubernetes version, `MAX_RETRY`, built-in repo/branch list, and required GitHub CLI authentication.

Control flow: logs into `gh`, iterates repository/branch pairs, fetches origin, recreates `module-update-<branch>`, refreshes `release-tools` via git subtree pull with conflict fallback by replacing the subtree from `FETCH_HEAD`, retries `go-get-kubernetes.sh -p <version>` with tidy/vendor cleanup, commits all changes, switches origin URL to the user's fork, runs `make test`, force-pushes, and creates a PR against `kubernetes-csi/<repo>`.

State and persistence behavior: heavily mutates local git checkouts, release-tools subtree, go.mod/go.sum/vendor, branches, remotes, and GitHub PRs.

Dependencies and integration points: depends on `go-get-kubernetes.sh`, git subtree, `gh`, Go tooling, Makefile tests, fork remotes, and a directory containing all listed repos.

Risks: uses `git reset --hard`-like cleanup indirectly through branch recreation and subtree replacement; can delete local update branches; force pushes; PR head uses `module-update-master` even when iterating variable branches, which may be wrong for non-master branches. Interface breakage is explicitly manual.

Test signals: `make test` before push is the local gate; downstream PR CI is final validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/go-modules-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/prow.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/prow.sh

Purpose: shared Kubernetes CSI Prow orchestration script for building components, creating kind clusters, deploying CSI drivers, running unit/E2E/sanity tests, collecting artifacts, merging JUnit output, and supporting GCR Cloud Build image pushes.

Important APIs and functions: `configvar`, `get_versioned_variable`, `version_to_git`, test selectors (`tests_enabled`, `sanity_enabled`, `tests_need_kind`), `ensure_paths`, `run`, `run_with_go`, installers for kind/ginkgo/dep/e2e/sanity, `git_checkout`, `git_clone`, `go_version_for_kubernetes`, `start_cluster`, `delete_cluster_inside_prow_job`, `find_deployment`, `install_csi_driver`, `install_snapshot_crds`, `install_snapshot_controller`, `collect_cluster_info`, `start_loggers`, `patch_kubernetes`, `run_e2e`, `run_sanity`, `make_test_to_junit`, `version_gt`, `main`, and `gcr_cloud_build`.

Control flow: the script initializes many configurable `CSI_PROW_*` defaults, including Go versions, Kubernetes/kind versions and images, driver deployment source, E2E focus/skip regexes, snapshotter version, and test matrix. `main` builds binaries/images with the configured Go toolchain, optionally runs unit tests and converts make output to JUnit, creates kind clusters when needed, installs snapshot CRDs/controller, deploys either locally built images or external driver deployments, runs sanity and E2E tests by focus groups, exports logs on failures, deletes clusters in Prow, and merges JUnit outputs through `filter-junit.go`. `gcr_cloud_build` handles image-push setup for Cloud Build.

State and persistence behavior: creates temporary work directories under `$GOPATH/pkg`, installs tools into a temp bin directory, clones repositories, builds images, tags and side-loads Docker images, creates/deletes kind clusters, writes kubeconfig/artifacts/JUnit files, and can push multi-arch images in Cloud Build. It does not itself commit repository changes.

Dependencies and integration points: central integration point for Makefiles, Docker, kind, kubectl, ginkgo, Kubernetes E2E tests, csi-test sanity, external-snapshotter CRDs/controller, git/GitHub repos, Cloud Build, and release-tools `filter-junit.go`. Consuming repos customize behavior through environment variables or wrapper `.prow.sh` files.

Risks: large shell surface with many external tool and network dependencies. Numerous values are parsed with grep/sed and word splitting. Cluster and image behavior depends on version compatibility among Kubernetes, kind, CSI sidecars, and deployment YAML. Some failures are fatal, while unit/E2E failures accumulate into a return code. Artifact ordering and cleanup can vary by Prow environment.

Test signals: no standalone unit tests for the script in this subset. Its signal is end-to-end Prow/Cloud Build execution: successful builds, unit test JUnit, E2E/sanity JUnit, cluster logs, and final merged JUnit.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/pull-test.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/pull-test.sh

Purpose: tests changes to `csi-release-tools` by importing the current checkout into another repository and running that repository's Prow checks.

Important variables and commands: `PULL_TEST_REPO_DIR`, `CSI_RELEASE_TOOLS_DIR`, `GIT_NO_LAZY_FETCH=0`, `git subtree pull --squash --prefix=release-tools`, and final `exec ./.prow.sh`.

Control flow: runs with `set -ex`, records the current release-tools directory, changes to the target repo, resets the target working tree, pulls the current release-tools checkout as a subtree on `master`, shows recent commits, and then executes the target repo's `.prow.sh`.

State and persistence behavior: mutates the target repository checkout by resetting it and creating a subtree merge commit or working tree change. It does not return to the original checkout because it `exec`s the target test script.

Dependencies and integration points: used by pull Prow jobs for csi-release-tools. Depends on git subtree, Prow checkout behavior, and `PULL_TEST_REPO_DIR` pointing at a suitable consumer repo.

Risks: `git reset --hard` is destructive to the target checkout by design. It assumes the release-tools branch is `master` and that the target repo has a compatible `.prow.sh`.

Test signals: downstream `.prow.sh` success after subtree import proves release-tools changes work in a consumer repo.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/pull-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/update-vendor.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/update-vendor.sh

Purpose: refreshes dependency vendoring for repositories using either dep or Go modules.

Important commands: checks for `Gopkg.toml` and runs `dep ensure`; otherwise checks for `go.mod`, runs `release-tools/verify-go-version.sh go`, then `go mod tidy` and `go mod vendor` with `GO111MODULE=on`.

Control flow: simple conditional selection based on dependency management files in the current directory.

State and persistence behavior: mutates dependency lock/vendor state through `dep ensure` or Go module tidy/vendor output. It does not commit changes.

Dependencies and integration points: used by release and maintenance workflows. Depends on dep for legacy repos, Go tooling for module repos, and the local `verify-go-version.sh` helper.

Risks: no `set -e` is present, so failures rely on command exit propagation from the last executed command in each branch. Repositories with both files prefer dep. Repositories with neither file silently do nothing.

Test signals: no direct tests; resulting `go mod tidy`, `go mod vendor`, or `dep ensure` output plus downstream build/test are validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/update-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/util.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/util.sh

Purpose: shared shell utility functions and color constants for Kubernetes release-tools scripts.

Important APIs and functions: `kube::util::sourced_variable`, `kube::util::sortable_date`, `kube::util::array_contains`, `kube::util::trap_add`, `kube::util::download_file`, `kube::util::wait-for-jobs`, `kube::util::join`, `kube::util::check-file-in-alphabetical-order`, and color variables.

Control flow: utilities provide reusable operations: membership checks, trap composition, curl downloads with retries, waiting for background jobs with aggregate failures, delimiter joins, and sorted-file verification with helpful remediation output.

State and persistence behavior: `download_file` removes and rewrites destination files. `trap_add` mutates shell trap state. Color variables are declared read-only if not already set.

Dependencies and integration points: intended to be sourced by shell verification/release scripts. Depends on standard Unix tools such as date, curl, sleep, jobs, wait, diff, and sort.

Risks: `download_file` contains `2&> /dev/null`, which appears intended as `2>/dev/null` and may not redirect as expected. `trap_add` parses `trap -p` output with awk and can be fragile for complex quoted trap commands.

Test signals: no direct tests in this subset; behavior is exercised by scripts that source it.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/util.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-boilerplate.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/verify-boilerplate.sh

Purpose: CI gate for validating required boilerplate headers across a repository.

Important variables and commands: strict shell options, `TOOLS`, `ROOT`, `boiler`, `mapfile -t files_need_boilerplate`, a temporary `unitTestOut`, and cleanup trap.

Control flow: ensures `python` exists, installing a python3 alternative if absent, resolves release-tools and root directories, runs `boilerplate.py --rootdir <root> --verbose`, captures failing filenames, prints each failure, and exits nonzero if any file fails.

State and persistence behavior: may register `/usr/bin/python` via `update-alternatives` in CI images, creates a temporary file, and reads source files. It does not modify checked-in files.

Dependencies and integration points: wraps `boilerplate/boilerplate.py` for `.prow.sh` and Makefile verification flows.

Risks: modifying system alternatives is invasive and requires permissions. `unitTestOut` is created but not otherwise used. The cleanup trap removes only that temp file.

Test signals: CI failure listing files with wrong headers is the output signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-go-version.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/verify-go-version.sh

Purpose: warns when the locally used Go toolchain major/minor version differs from the version configured for Prow builds.

Important arguments and commands: requires one argument pointing to a Go binary, runs `<go> version`, extracts major.minor with sed, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a warning block on mismatch.

Control flow: exits with usage error when no Go binary is provided; otherwise only warns on mismatch and does not fail.

State and persistence behavior: no mutation. It reads toolchain version and release-tools configuration.

Dependencies and integration points: called by `update-vendor.sh` and local verification workflows. Depends on `prow.sh` being sourceable from the current repo root.

Risks: sourcing `prow.sh` executes its top-level `configvar` calls and prints unless redirected, so future top-level side effects would affect this script. Version extraction ignores patch versions intentionally.

Test signals: warning text is the only signal; downstream commands continue.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-go-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-logcheck.sh -->
# sources/control-plane/csi-driver-nfs/release-tools/verify-logcheck.sh

Purpose: verifies contextual klog usage with the `sigs.k8s.io/logtools/logcheck` tool.

Important variables and commands: strict shell options, `LOGCHECK_VERSION` positional default `0.10.0`, `CSI_LIB_UTIL_ROOT`, a temporary install directory, `go install sigs.k8s.io/logtools/logcheck@v<version>`, and `logcheck -check-contextual -check-with-helpers <root>/...`.

Control flow: resolves the repository root as the parent of release-tools, creates a temp directory, installs the requested logcheck version into it, runs logcheck against all packages, and removes the temp directory on exit.

State and persistence behavior: writes only the temporary binary directory and Go module cache side effects from `go install`.

Dependencies and integration points: used by CI verification for repositories that have migrated to contextual logging conventions. Depends on Go tooling and network/module access unless cached.

Risks: always installs at runtime, which can be slow or fail due to network/module proxy issues. The variable name `CSI_LIB_UTIL_ROOT` is generic from another repo and may be confusing but resolves correctly.

Test signals: nonzero logcheck exit fails the verification job and points to logging call sites.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/release-tools/verify-logcheck.sh -->
