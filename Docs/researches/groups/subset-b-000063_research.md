# subset-b-000063 Research

Grouped research for the listed containerd integration client and CRI integration files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_fuzz_test.go -->
# sources/cloud-native/containerd/integration/client/container_fuzz_test.go

## Purpose
Defines integration fuzzers that exercise containerd daemon startup, OCI image import, image metadata operations, unpacking, and container creation through the public Go client. The fuzzers are aimed at OSS-Fuzz and compare two daemon lifecycle modes: keeping one daemon across iterations versus tearing the daemon down after each iteration.

## APIs, Types, And Functions
The key helpers are `downloadFile`, `initInSteps`, `updatePathEnv`, `startDaemon`, `tearDown`, `checkIfShouldRestart`, `deleteSocket`, `checkAndDoUnpack`, `getImage`, `newContainer`, and `doFuzz`. The exported fuzz entry points are `FuzzIntegNoTearDownWithDownload`, `FuzzIntegCreateContainerNoTearDown`, and `FuzzIntegCreateContainerWithTearDown`. They depend on `github.com/AdaLogics/go-fuzz-headers` for bounded generation of tar archives, strings, integers, booleans, and OCI specs.

## Control Flow And State
Initialization state is held in package booleans that gate download, extraction, and PATH mutation. `doFuzz` starts the package-level `ctrd` daemon if needed, opens a client on `defaultAddress`, imports up to 30 fuzz-generated tar streams, lists images, and creates up to 50 fuzz-selected containers from either a fuzzed spec alone, an image plus fuzzed spec, or an image alone. Successful containers are deferred for deletion with snapshot cleanup. The download fuzzer spreads binary download, extraction, and PATH setup across iterations to avoid OSS-Fuzz iteration timeouts.

## Persistence And Integration Points
The fuzzer mutates `/tmp/containerd-2.0.1-linux-amd64.tar.gz`, `/tmp/containerd-binaries`, `/out/containerd-binaries`, `defaultRoot`, `defaultState`, and the containerd socket. It exercises containerd import, image listing, image size, unpack, and `NewContainer` paths against a live daemon launched with the shim debug config.

## Risks And Test Signals
The main risks are global process state, stale sockets, network-dependent binary download, unchecked generated OCI structures, and daemon data accumulation when teardown is disabled. Failures that mention a dead daemon trigger socket deletion so later iterations can recover. Useful signals are panics, fatal daemon-start errors, crashes in import/unpack/container creation, and behavioral differences between teardown modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_idmapped_linux_test.go -->
# sources/cloud-native/containerd/integration/client/container_idmapped_linux_test.go

## Purpose
Tests Linux overlayfs idmapped snapshot behavior for single ID maps, multi-range ID maps, and parallel unpack. It verifies that remapped overlay snapshots expose expected host ownership and hide implementation lower directories from direct host paths.

## APIs, Types, And Functions
The file contains `TestIDMappedOverlay`. It uses `overlayutils.SupportsIDMappedMounts`, `userns.IDMap`, `containerd.WithRemapperLabels`, `containerd.WithUserNSRemapperLabels`, `containerd.WithUnpackLimiter`, `WithNewSnapshot`, `oci.WithUserNamespace`, snapshot `Mounts`, and OCI ID mappings.

## Control Flow And State
The test skips unless overlayfs idmapped mounts are supported. Each table case pulls `testMultiLayeredImage` with unpack, creates a container using the overlayfs snapshotter and user namespace mapping, reads the snapshot mount options, rejects host-visible lowerdir paths, stats the overlay upperdir, and checks the upperdir UID/GID against the expected host mapping. Cleanup deletes the container snapshot and test image synchronously.

## Persistence And Integration Points
State is persisted in the overlayfs snapshotter, image service, content store, and snapshot labels that encode remapping metadata. The test integrates the client API, image unpacking, snapshot mount materialization, kernel overlayfs idmapped support, and container spec user namespaces.

## Risks And Test Signals
The test is kernel- and filesystem-dependent and will skip on hosts lacking idmapped overlay mounts. A failure signals broken snapshot label translation, unsafe lowerdir exposure, incorrect multi-map handling, or parallel unpack races affecting idmapped ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_idmapped_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_linux_test.go -->
# sources/cloud-native/containerd/integration/client/container_linux_test.go

## Purpose
Provides Linux-specific integration coverage for task resource updates, shim cgroups, descriptor leaks, daemon restart recovery, direct IO attach, user and user-namespace handling, host PID behavior, runtime options, ambient capabilities, OOM score propagation, and several runc/shim regressions.

## APIs, Types, And Functions
Important tests include `TestTaskUpdate`, `TestShimInCgroup`, `TestShimDoesNotLeakPipes`, `TestShimDoesNotLeakSockets`, `TestDaemonReconnectsToShimIOPipesOnRestart`, `TestContainerAttach`, `TestContainerUser`, `TestContainerAttachProcess`, `TestContainerLoadUnexistingProcess`, `TestContainerUserID`, `TestContainerKillAll`, `TestDaemonRestartWithRunningShim`, `TestContainerRuntimeOptionsv2`, `TestUserNamespaces`, `TestUIDNoGID`, `TestBindLowPortNonRoot`, `TestBindLowPortNonOpt`, `TestShimOOMScore`, `TestIssue9103`, `TestIssue10589`, and `TestIssue13030`. Helpers include `numPipes`, `writeToFile`, `getLogDirPath`, `checkUserNS`, and `testUserNamespaces`.

## Control Flow And State
Most tests create a client, fetch or load `testImage`, create a container with a snapshot/spec, create a task, wait/start/kill/delete it, and assert kernel-visible state. The cgroup tests inspect cgroup v1 or v2 memory limits and shim process membership. The restart tests restart the package-level daemon and verify reconnect to running shims and log pipes. The attach tests use `directIO` and FIFO-backed stdin/stdout to prove `Task` and `Process` reload/attach behavior. The user namespace suite creates remapped snapshots or views, runs as a mapped user, and validates exit codes and setuid-bit preservation. Regression tests use `runc-fp` failpoints and FIFOs to force races around killed init processes, delayed exec startup, and parallel unpack whiteout handling.

## Persistence And Integration Points
The file touches containerd metadata, snapshotter state, shim sockets under `defaultState`, cgroup filesystems, `/proc`, OOM score files, runtime options, image rootfs metadata, and failpoint-controlled runc binaries. It also integrates with cgroups v1/v2 libraries, kernel user namespaces, overlay/native snapshot behavior, client event/status APIs, and the daemon restart helper.

## Risks And Test Signals
These tests are sensitive to root privileges, cgroup mode, available `runc-fp`, `lsof`, host user namespace support, and runtime flavor. Failures indicate high-risk regressions: resource updates not applied, leaked pipes or sockets, lost shim log forwarding after restart, broken attach semantics, incorrect UID/GID resolution, escaped child processes, OOM-score mismatch, bad runtime option propagation, exec/init race bugs, or incorrect whiteout processing during parallel unpack.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_test.go -->
# sources/cloud-native/containerd/integration/client/container_test.go

## Purpose
This is the broad cross-platform client integration suite for container, task, process, IO, metadata, event, and daemon restart behavior. It functions as an executable contract for the public containerd client API around `Container`, `Task`, `Process`, images, snapshots, specs, labels, extensions, runtime path selection, waits, deletes, and kill semantics.

## APIs, Types, And Functions
Key tests cover list/create/start/output/wait/exec/large exec args/PIDs/close IO/delete running/kill/missing binaries/stopped wait/force delete/hostname/metrics/extensions/update/info/labels/hooks/shim socket length/large TTY output/short task PID/events/daemon restart/task spec/container image/no image/no stdin/username/PTY. Helpers include `empty`, `readShimPath`, `copyShim`, `withStdout`, `withProcessTTY`, `initContainerAndCheckChildrenDieOnKill`, and the `directIO` wrapper implementing `IOCreate`, `IOAttach`, `Cancel`, `Close`, and `Delete`.

## Control Flow And State
The common pattern is to create a namespaced client, load or pull an image, create a container with `WithNewSnapshot` and `WithNewSpec`, create a task with a selected IO creator, wait before start, start, assert status/output/events, then delete task/container with snapshot cleanup. Metadata tests mutate and reload container labels, extensions, specs, images, and info. Regression tests subscribe to task exit events to ensure no duplicate exit event after delete and no exit event for a command-not-found task. Restart coverage restarts the global daemon while a task is running, expects the first wait to fail due to transport closure, waits for daemon serving, then waits/kills the same task again.

## Persistence And Integration Points
State is persisted through containerd metadata, content/images, snapshots, runtime shim directories, FIFO directories, event streams, task status, and OCI specs marshaled through typeurl. The file integrates with runc for one test that force-deletes a container behind containerd, the `containerd oci-hook` command, platform-specific helper functions, and runtime v2 shim path files.

## Risks And Test Signals
The suite catches API contract regressions that unit tests miss: incorrect exit-code propagation, missing pid accounting, leaked or blocked IO, wrong error classes, unsafe deletion while running, broken metadata update/load, task metrics availability, event duplication, shim path length limits, PTY corruption, and restart reconnection failures. Some tests are platform-specific or flaky-sensitive because they rely on process timing, Windows behavior, terminal output, and host tools such as `ps`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/content_test.go -->
# sources/cloud-native/containerd/integration/client/content_test.go

## Purpose
Adapts the upstream content store testsuite to a live containerd client content store. It verifies that the remote content service satisfies the common content.Store contract under separate namespaces and leases.

## APIs, Types, And Functions
`newContentStore` returns a testsuite-compatible context, `content.Store`, cleanup function, and error. `TestContentClient` invokes `testsuite.ContentSuite`. The helper uses `client.ContentStore`, `client.WithLease`, `testsuite.SetContextWrapper`, `namespaces.WithNamespace`, `ListStatuses`, `Abort`, `Walk`, and `Delete`.

## Control Flow And State
Each testsuite context wrapper increments an atomic namespace suffix and creates a lease. Cleanup iterates over every generated namespace, aborts active writes, walks stored content, and deletes each blob while tolerating not-found races.

## Persistence And Integration Points
The test persists content blobs, active ingest statuses, namespaces, and leases inside the running daemon. It integrates with `core/content/testsuite`, client lease handling, namespace propagation, and errdefs.

## Risks And Test Signals
Failures indicate mismatches between remote content service behavior and the common content contract, especially around concurrent namespaces, writer abort, lease lifecycle, delete idempotency, and content walking. The test is skipped in short mode because it exercises a live daemon and full content suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/content_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/convert_test.go -->
# sources/cloud-native/containerd/integration/client/convert_test.go

## Purpose
Tests image conversion from Docker media types to OCI media types, compressed layers to uncompressed tar layers, and multi-platform image metadata to a single selected platform.

## APIs, Types, And Functions
`TestConvert` uses `client.Fetch`, `converter.Convert`, `converter.WithDockerToOCI`, `converter.WithLayerConvertFunc`, `uncompress.LayerConvertFunc`, `converter.WithPlatform`, `images.Platforms`, and `images.Manifest`.

## Control Flow And State
The test fetches `testImage`, converts it to a derived reference, deletes the derived image during cleanup, inspects available platforms on the converted target, and then reads the manifest for the default strict platform to assert that every layer has `ocispec.MediaTypeImageLayer`.

## Persistence And Integration Points
Conversion writes new image records and content blobs through the client content store and image service. It integrates containerd's image converter package, OCI descriptors, platform matching, and layer decompression pipeline.

## Risks And Test Signals
Failures indicate conversion regressions in media type rewriting, layer conversion, platform filtering, or image record cleanup. Because the test fetches from an image reference and mutates daemon content, it is skipped in short mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/convert_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/daemon.go -->
# sources/cloud-native/containerd/integration/client/daemon.go

## Purpose
Provides a small process manager used by integration tests to start, stop, kill, wait for, and restart a containerd daemon under test.

## APIs, Types, And Functions
The central type is `daemon`, containing a mutex, daemon address, and `*exec.Cmd`. Methods are `start`, `waitForStart`, `Stop`, `Kill`, `Wait`, and `Restart`.

## Control Flow And State
`start` rejects duplicate starts, appends `--address`, launches the command, and stores the command/address. `waitForStart` polls every 500 ms, creates a client, checks `IsServing`, reads the plugin list, and fails if any plugin init error is not an allowed skip. `Stop` sends SIGTERM, `Kill` kills the process, `Wait` reaps and clears `cmd`, and `Restart` signals the process, waits, optionally invokes a callback, and relaunches with the same executable, arguments, stdout, and stderr.

## Persistence And Integration Points
The helper owns OS process state and a client connection address. It integrates with `client.New`, `IntrospectionService().Plugins`, `plugin.ErrSkipPlugin`, OS signals, and Windows-specific restart behavior that uses SIGKILL.

## Risks And Test Signals
The mutex prevents concurrent process mutation, but `Restart` holds the lock while waiting and relaunching, so tests depend on callbacks not reentering daemon methods. Failures expose daemon startup errors, plugin initialization failures, stale client sockets, or process lifecycle bugs that would invalidate many integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/daemon_config_linux_test.go -->
# sources/cloud-native/containerd/integration/client/daemon_config_linux_test.go

## Purpose
Verifies Linux daemon configuration paths that are hard to exercise through the default daemon: runtime root override and custom cgroup path creation.

## APIs, Types, And Functions
`TestDaemonRuntimeRoot` uses `newDaemonWithConfig`, `WithRuntime`, runc `options.Options{Root: ...}`, `WithNewSnapshot`, and task lifecycle APIs. `getCgroupPath` parses `/proc/self/mountinfo`. `TestDaemonCustomCgroup` checks `[cgroup].path` for cgroup v1.

## Control Flow And State
The runtime-root test starts a temporary daemon, pulls an image, creates a task with a custom runc root, asserts that `runtimeRoot/<namespace>/<id>` exists, then kills the task. The custom-cgroup test skips on unified cgroup v2, discovers mounted v1 controller paths, starts a daemon with a generated cgroup path, and asserts that known controllers create that path, cleaning it afterward.

## Persistence And Integration Points
The tests persist temporary daemon roots/states, custom runc runtime directories, and cgroup directories under host controller mounts. They integrate with daemon config loading, runc runtime options, the global test namespace, and Linux cgroup filesystems.

## Risks And Test Signals
Failures signal ignored runtime root configuration, ignored daemon cgroup path configuration, cgroup mount parsing drift, or cleanup problems that can leave host cgroup directories behind. The custom cgroup test is intentionally cgroup-v1-only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/daemon_config_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/export_test.go -->
# sources/cloud-native/containerd/integration/client/export_test.go

## Purpose
Exercises image export behavior across full multi-platform exports, sparse exports with missing content, Docker manifest compatibility, OCI-only export, index-only export, and valid OCI `org.opencontainers.image.ref.name` annotations.

## APIs, Types, And Functions
`TestExportAllCases` is table-driven with prepare/check functions. Helpers include `isImageInArchive`, `getPlatformManifest`, `assertOCITar`, and `assertOCIIndexAnnotationRefName`. It uses `client.Fetch`, `client.Export`, `archive.WithImage`, `archive.WithManifest`, `archive.WithPlatform`, `archive.WithSkipMissing`, `archive.WithSkipDockerManifest`, `images.Walk`, `images.Children`, `images.LimitManifests`, and `content.Store`.

## Control Flow And State
Each case creates a unique namespace and client, prepares content by fetching one platform or full metadata, optionally deletes non-index blobs to simulate sparse content, exports to a temp file, seeks back, validates OCI tar members, and inspects whether selected descriptors' blobs are present. One case exports a digest reference and decodes `index.json` to validate annotation grammar.

## Persistence And Integration Points
The tests persist temporary tar archives and daemon content under per-test namespaces. They integrate with platform matchers, OCI archive layout, Docker `manifest.json` compatibility, content store deletion, and descriptor graph walking.

## Risks And Test Signals
Failures indicate broken missing-content handling, unexpected Docker manifest inclusion/exclusion, wrong platform filtering, incomplete descriptor closure in exported archives, or invalid ref-name annotations. Windows skips some all-platform cases because the test index does not carry the same platform breadth there.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/export_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_unix.go -->
# sources/cloud-native/containerd/integration/client/helpers_unix.go

## Purpose
Provides Unix implementations for platform-dependent integration helpers.

## APIs, Types, And Functions
The file defines `forceRemoveAll` and `SkipTestOnHost` behind the `!windows` build tag.

## Control Flow And State
`forceRemoveAll` delegates directly to `os.RemoveAll`, reflecting that Unix test cleanup does not need Windows container layer unprepare/deactivate semantics. `SkipTestOnHost` always returns false because there is no Unix host-version skip encoded here.

## Persistence And Integration Points
The helper is used by daemon and fuzz cleanup paths that remove containerd roots, state directories, and temp workspaces. It integrates only with the standard library on Unix builds.

## Risks And Test Signals
The risk is broad recursive deletion if callers pass an unsafe path; this file does no guard enforcement. Test signal is indirect through all integration cleanup that expects Unix roots to be removable after daemon/task teardown.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_unix_test.go -->
# sources/cloud-native/containerd/integration/client/helpers_unix_test.go

## Purpose
Supplies Unix test helper implementations for process commands, exit statuses, newlines, exec argument mutation, and direct FIFO-backed IO.

## APIs, Types, And Functions
The file defines `newLine`, `withExitStatus`, `withProcessArgs`, `withCat`, `withTrue`, `withExecExitStatus`, `withExecArgs`, and `newDirectIO`.

## Control Flow And State
Spec options mutate OCI process args to shell commands such as `sh -c "exit N"`, `cat`, and `true`, or delegate to `oci.WithProcessArgs`. Exec helpers mutate an existing `specs.Process`. `newDirectIO` creates a FIFO set via `cio.NewFIFOSetInDir`, wraps it with `cio.NewDirectIO`, and returns the test package's `directIO` wrapper.

## Persistence And Integration Points
The direct IO helper creates FIFO directories/files that must be closed/deleted by tests. The command helpers are consumed by container lifecycle tests and map generic test intent to Unix process semantics.

## Risks And Test Signals
Incorrect command translation would invalidate many cross-platform assertions about exit codes, line endings, stdin/stdout, and exec behavior. FIFO leaks or missed `Delete` calls are detectable through tests hanging or filesystem cleanup failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_windows.go -->
# sources/cloud-native/containerd/integration/client/helpers_windows.go

## Purpose
Provides Windows-specific cleanup for containerd test roots containing WCOW snapshot layers, plus a temporary host-version skip predicate.

## APIs, Types, And Functions
The file defines `forceRemoveAll`, `cleanupWCOWLayers`, `cleanupWCOWLayer`, and `SkipTestOnHost`. It depends on `hcsshim`, `osversion`, and Windows syscall errors.

## Control Flow And State
`forceRemoveAll` detects the Windows snapshotter directory under a containerd root and calls `cleanupWCOWLayers` before `os.RemoveAll`. Layer directories and `rm-*` directories are collected, sorted descending, and each layer is unprepared, deactivated, and destroyed through HCS driver APIs. Some unprepare errors are tolerated because layers may already be unprepared or only activated.

## Persistence And Integration Points
This helper mutates Windows container layers under `io.containerd.snapshotter.v1.windows/snapshots`. It integrates test cleanup with hcsshim's layer lifecycle and skips selected tests on Windows Server 2025 via `osversion.Build() == osversion.LTSC2025`.

## Risks And Test Signals
Wrong deletion order or ignored HCS states can leave mounted layers that block directory removal. Overly broad path traversal could affect unrelated directories if callers pass the wrong root. Test signal comes from Windows integration cleanup reliability and host-specific skips.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_windows_test.go -->
# sources/cloud-native/containerd/integration/client/helpers_windows_test.go

## Purpose
Supplies Windows test helper implementations matching the Unix helper API while using `cmd /c` command semantics and in-memory direct IO.

## APIs, Types, And Functions
The file defines `newLine`, `withExitStatus`, `withProcessArgs`, `withCat`, `withTrue`, `withExecExitStatus`, `withExecArgs`, `bytesBuffer`, and `newDirectIO`.

## Control Flow And State
Spec and exec helpers prefix process args with `cmd /c` where needed and use `more` as the cat equivalent. `bytesBuffer` wraps `bytes.Buffer` with a no-op `Close`. `newDirectIO` builds a `cio.DirectIO` from in-memory readers/writers instead of FIFOs, then wraps it in the shared `directIO` type.

## Persistence And Integration Points
The helper avoids filesystem FIFO state on Windows and is consumed by cross-platform container/task/exec tests. It integrates with Windows container command interpretation and CRLF output expectations.

## Risks And Test Signals
Command quoting and prefixing are the main risks because a small mismatch changes observed exit codes or stdout. In-memory IO can hide FIFO-specific behavior, so Windows-specific failures may differ from Unix direct IO failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/image_test.go -->
# sources/cloud-native/containerd/integration/client/image_test.go

## Purpose
Tests image lifecycle APIs for unpack status, distribution source labels, content usage accounting, snapshot usage accounting, and snapshotter-platform compatibility errors.

## APIs, Types, And Functions
The file defines `TestImageIsUnpacked`, `TestImagePullWithDistSourceLabel`, `TestImageUsage`, and `TestImageSupportedBySnapshotter_Error`. It uses `Pull`, `Fetch`, `ImageService().Delete`, `Image.IsUnpacked`, `Image.Unpack`, `Image.Usage`, `Image.RootFS`, `images.Dispatch`, `images.LimitManifests`, content `Info`, usage options, default snapshotter, and platform matchers.

## Control Flow And State
Tests delete any preexisting image record, pull without unpack, assert unpack state, then unpack and reassert. Distribution label coverage walks the selected platform descriptor graph and checks `containerd.io/distribution.source.<registry>` labels include the repository name. Usage coverage compares single-manifest usage, all-manifest usage, manifest-reported usage, full fetched content, and snapshot usage after unpack. Unsupported snapshotter coverage pulls an image for the opposite OS and expects unpack to fail under platform checking.

## Persistence And Integration Points
The tests persist image records, content labels, descriptors, and snapshots in the default snapshotter. They integrate with registry pulls, platform filtering, content labeling, image usage options, and snapshotter platform validation.

## Risks And Test Signals
Failures indicate incorrect unpack tracking, lost distribution source labels, undercounted/overcounted usage, or allowing incompatible image layers into a snapshotter. Tests may depend on registry availability and platform-specific image references.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/import_test.go -->
# sources/cloud-native/containerd/integration/client/import_test.go

## Purpose
Exercises archive import/export and transfer-based image import for Docker v2 archives, OCI layouts, sparse indexes, labels, ref prefix/filter behavior, digest references, and garbage-collection safety after import.

## APIs, Types, And Functions
Tests are `TestExportAndImport`, `TestExportAndImportMultiLayer`, `TestImport`, and `TestTransferImport`. Helpers include `testExportImport`, `checkImages`, `createContent`, `createConfig`, `createManifest`, `createManifestList`, `createIndex`, `imagesProgress`, `createImages`, and `hash64`. The file uses `client.Export`, `client.Import`, `client.Transfer`, archive import/export options, transfer `image.Store`, `tartest`, content APIs, leases, compression, OCI specs, and platform matching.

## Control Flow And State
`testExportImport` fetches an image, exports it, deletes it, imports with an image ref translator, unpacks imported records, creates/deletes a lease to force GC, and verifies a container can still be created from the image. `TestImport` builds synthetic tar archives for valid and invalid Docker/OCI cases, imports them into unique namespaces, and checks resulting image names, target digests, manifests, labels, or expected errors. `TestTransferImport` builds OCI layouts with named, tag-only, manifest digest, and index digest references, transfers an import stream into an image store, tracks progress events, and verifies saved image descriptors.

## Persistence And Integration Points
The tests write temporary tar files/streams, daemon content, image records, leases, and snapshots. They integrate with OCI image layout grammar, Docker legacy archive layouts, archive ref translators, transfer progress, named/digest image storage options, and GC retention through leases/snapshots.

## Risks And Test Signals
Failures identify import regressions around sparse indexes, missing descendants, bad OS/arch configs, annotation-derived names, label propagation, digest ref overwrites, media type preservation, and GC deleting needed content. The multi-layer test skips unavailable architecture combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/import_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/lease_test.go -->
# sources/cloud-native/containerd/integration/client/lease_test.go

## Purpose
Verifies that lease resources protect snapshotter resources from garbage collection after an image is deleted, and that deleting the lease releases those resources.

## APIs, Types, And Functions
`TestLeaseResources` uses `LeasesService`, `ContentStore`, `ImageService`, `SnapshotService`, `leases.Create`, `leases.AddResource`, `leases.ListResources`, `leases.DeleteResource`, `leases.Delete`, `Pull`, `Image.Config`, `Image.RootFS`, and `identity.ChainID`.

## Control Flow And State
The test creates a random lease, pulls and unpacks the pause image using `native` or `windows` snapshotter, verifies config content and rootfs snapshot existence, adds a lease resource for the snapshot chain ID, deletes the image synchronously, verifies the config blob is gone while the snapshot remains, removes the resource, deletes the lease synchronously, and then expects the snapshot to be not found.

## Persistence And Integration Points
State spans leases, content blobs, image records, snapshotter metadata, and GC. The snapshotter name changes by OS, linking the same contract to native Linux and Windows snapshot backends.

## Risks And Test Signals
Failures signal GC retaining too much or deleting too aggressively, lease resource list drift, wrong snapshot resource type names, or OS snapshotter behavior that does not honor leases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/lease_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/migration_test.go -->
# sources/cloud-native/containerd/integration/client/migration_test.go

## Purpose
Tests `containerd config migrate` against the current default config and selected historical fixtures, ensuring old defaults and custom values migrate to the current generated default shape.

## APIs, Types, And Functions
`TestMigration` drives the command-line `containerd config default` and `containerd -c <file> config migrate`. Helpers are `currentDefaultConfig`, `replaceAllValues`, and `replaceValue`.

## Control Flow And State
The test writes the current default config to a temp file and always checks that migrating it is identity-preserving. On linux/amd64 builds whose default includes btrfs and devmapper, it also migrates `default-1.6.toml`, `default-1.7.toml`, and `custom-1.7.toml`. The custom expected output is derived by replacing selected current-default values such as sandbox image, streaming address/port/timeouts, and TLS streaming.

## Persistence And Integration Points
The test persists only temp config files and reads fixture TOML files. It integrates with the `containerd` binary, server config defaults, migration code, and fixture comments documenting removed or changed settings.

## Risks And Test Signals
Failures indicate unstable default config generation, incomplete migration rules, accidental loss of custom CRI stream/sandbox values, platform-dependent fixture mismatch, or a missing/broken `containerd` binary in PATH.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/migration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/mount_manager_linux_test.go -->
# sources/cloud-native/containerd/integration/client/mount_manager_linux_test.go

## Purpose
Tests the Linux mount manager service and runtime rootfs mount composition, including formatted loopback mounts and overlay mounts that reference earlier mounts by index.

## APIs, Types, And Functions
Tests are `TestMountManager` and `TestMountAtRuntime`. Helpers are `createImgFile`, `setupMount`, and `withImage`. The file uses `client.MountManager().List/Info`, `SnapshotService.View`, `container.NewTask` with `containerd.WithRootFS`, mount types `xfs` and `format/overlay`, `identity.ChainID`, image config reads, and OCI spec mutation.

## Control Flow And State
The first test asserts a fresh mount manager has no mounts. The runtime test creates an XFS image file, prepares directories on it, gets a read-only snapshot view for the image rootfs, then starts a container with a composed mount list that overlays the image root and loopback filesystem. It writes a file through the first task, ensures active mount info is present during the task and gone after deletion, then starts a second container using the previous upperdir as a lowerdir and verifies the file content is visible.

## Persistence And Integration Points
State includes a 300 MB loopback image, XFS filesystem metadata, snapshot views, active runtime mounts, and overlay upper/work directories. The test integrates with `mkfs.xfs`, kernel loop mounts, containerd mount formatting, mount manager tracking, and image config parsing.

## Risks And Test Signals
The test skips when `mkfs.xfs` is absent and is sensitive to mount permissions and filesystem support. Failures indicate broken mount placeholder substitution, mount manager leaks, runtime rootfs mount cleanup problems, or incorrect image-config-to-process conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/mount_manager_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/restart_monitor_test.go -->
# sources/cloud-native/containerd/integration/client/restart_monitor_test.go

## Purpose
Validates the container restart monitor plugin: always-restart behavior, paused task preservation, and on-failure retry counting.

## APIs, Types, And Functions
The file defines `newDaemonWithConfig`, `TestRestartMonitor`, `testRestartMonitorAlways`, `testRestartMonitorPausedTaskWithAlways`, `testRestartMonitorWithOnFailurePolicy`, and `convertTaskCreateEvent`. It uses server config loading, `restart.WithStatus`, `restart.NewPolicy`, `restart.WithPolicy`, client task lifecycle APIs, event subscription, container labels, and typeurl unmarshalling of `TaskCreate`.

## Control Flow And State
`newDaemonWithConfig` writes a temporary config, loads it to discover or synthesize an address, starts a daemon with temp root/state, waits for plugin readiness, and returns a cleanup closure. `TestRestartMonitor` enables `io.containerd.monitor.container.v1.restart` with a five-second interval, pulls the test image, then runs subtests. The always policy kills a running task and polls until it is running again before the deadline. The paused-task case pauses and ensures the monitor does not kill/restart it. The on-failure case starts an exit-1 task with `on-failure:1`, waits for a `/tasks/create` event, and checks restart count label equals one.

## Persistence And Integration Points
State spans temporary daemon config/root/state, task status, restart labels, event streams, and restart monitor plugin state. It integrates the client API with daemon plugin configuration and task event publication.

## Risks And Test Signals
Timing is the main risk: slow shutdown/restart can cause false failures around interval deadlines. Real failures indicate restart monitor interval misbehavior, paused task mishandling, event publication loss, or incorrect restart count labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/restart_monitor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/snapshot_test.go -->
# sources/cloud-native/containerd/integration/client/snapshot_test.go

## Purpose
Runs the shared snapshotter test suite against the daemon's default remote snapshotter client.

## APIs, Types, And Functions
`newSnapshotter` returns a `snapshots.Snapshotter`, cleanup function, and error for the testsuite. `TestSnapshotterClient` invokes `testsuite.SnapshotterSuite` with `defaults.DefaultSnapshotter`.

## Control Flow And State
The helper opens a containerd client, obtains `client.SnapshotService(defaults.DefaultSnapshotter)`, and returns a cleanup function that closes the client. The testsuite performs the actual snapshot operations.

## Persistence And Integration Points
The suite mutates snapshotter metadata and mounts through the running daemon. It integrates the remote snapshot service with the common snapshotter testsuite.

## Risks And Test Signals
Failures indicate the default snapshotter's remote client does not satisfy the standard snapshotter contract for prepare/view/commit/remove/walk/stat behavior. The test is skipped in short mode because it drives a full integration suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/custom-1.7.toml -->
# sources/cloud-native/containerd/integration/client/testdata/custom-1.7.toml

## Purpose
Fixture representing a customized containerd 1.7-era config used to verify migration into the current default config while preserving selected user-provided values.

## APIs, Types, And Functions
This is TOML consumed by `containerd -c testdata/custom-1.7.toml config migrate` from `migration_test.go`. It uses version 2 config tables for root/state, cgroup, debug, grpc, metrics, CRI, CNI, runtime, registry, NRI, snapshotters, stream processors, timeouts, and ttrpc.

## Control Flow And State
There is no executable flow inside the fixture. Migration reads the file, drops removed settings, normalizes plugin layout, applies new defaults, and preserves custom values such as `sandbox_image = "custom.io/pause:3.10.2"`, `stream_idle_timeout = "2h0m0s"`, `stream_server_address = "127.0.1.1"`, `stream_server_port = "15000"`, and `enable_tls_streaming = true`.

## Persistence And Integration Points
The fixture models persistent daemon configuration. Comments mark settings that were removed or changed in later releases, including tracing, runtime v1, zfs/aufs, CriuPath, NoPivotRoot, SystemdCgroup, and transfer unpack config defaults.

## Risks And Test Signals
Its value is as a regression oracle: if it drifts from expected historical shape, migration tests may fail for fixture reasons rather than code reasons. It specifically signals whether migration preserves user intent while removing obsolete keys and adopting newer defaults like CDI/NRI enablement.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/custom-1.7.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/default-1.6.toml -->
# sources/cloud-native/containerd/integration/client/testdata/default-1.6.toml

## Purpose
Fixture for containerd 1.6 default config migration. It documents the older default config shape that should migrate to the current generated default on supported linux/amd64 builds.

## APIs, Types, And Functions
The TOML is consumed by `TestMigration` through the `containerd config migrate` CLI. It contains version 2 daemon, cgroup, grpc, CRI, CNI, runtime, registry, stream processor, snapshotter, timeout, and ttrpc sections.

## Control Flow And State
The fixture has declarative state only. During migration it is expected to gain or normalize newer defaults, including updated pause image, unprivileged port/ICMP defaults, metrics shimstats timeout, and removal or comments around obsolete runtime/tracing/snapshotter fields.

## Persistence And Integration Points
It represents persistent daemon configuration before newer CRI/NRI/transfer defaults existed. The migration test compares migrated output exactly with the current default generated by the local `containerd` binary.

## Risks And Test Signals
The fixture is platform-constrained because exact defaults depend on compiled snapshotters such as btrfs and devmapper. A failure signals either a real migration regression or an intentional default change that requires fixture/test expectation updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/default-1.6.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/default-1.7.toml -->
# sources/cloud-native/containerd/integration/client/testdata/default-1.7.toml

## Purpose
Fixture for containerd 1.7 default config migration. It captures the 1.7 default shape with comments marking settings whose defaults changed or whose keys were removed in newer releases.

## APIs, Types, And Functions
The file is TOML input to `containerd config migrate` in `migration_test.go`. It includes CRI settings such as CDI directories, unprivileged network defaults, sandbox image, CNI setup options, runtime sandbox mode, NRI plugin settings, transfer plugin settings, snapshotter settings, and timeouts.

## Control Flow And State
No code runs in the file itself. Migration should transform it to the current default config on supported builds, adding current defaults and omitting obsolete keys while keeping the expected normalized ordering and values.

## Persistence And Integration Points
The fixture represents persistent daemon config stored on disk. It integrates with migration code as an exact golden input for defaults around CRI, runtime v2 task, NRI, transfer, and snapshotters.

## Risks And Test Signals
The risk is fixture rot when defaults change intentionally. Test failures are useful signals for default migration drift, especially around sandbox image updates, CDI/NRI enablement, removed tracing/runtime-v1/zfs/aufs sections, and transfer unpack config behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/default-1.7.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/tracing.go -->
# sources/cloud-native/containerd/integration/client/tracing.go

## Purpose
Provides small OpenTelemetry helpers for integration tests that need to capture and validate spans in memory.

## APIs, Types, And Functions
The file defines `newInMemoryExporterTracer` and `validateRootSpan`. It uses `tracetest.InMemoryExporter`, `sdktrace.TracerProvider`, `sdktrace.WithBatcher`, and OpenTelemetry status codes.

## Control Flow And State
`newInMemoryExporterTracer` creates an in-memory exporter and tracer provider with a batcher. `validateRootSpan` scans exported span stubs, considers only root spans whose parent context is invalid, finds a span by expected name, asserts its status code is not `codes.Error`, and fails the test if no matching root span exists.

## Persistence And Integration Points
Span state is held in memory by the exporter for the duration of a test. The helpers integrate instrumented client or daemon code with test assertions without requiring an external collector.

## Risks And Test Signals
Batching can require tests to flush/shutdown the provider before inspecting spans. The helper only checks root span name and non-error status, so it is a coarse signal rather than a full trace-shape validator.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/transfer_test.go -->
# sources/cloud-native/containerd/integration/client/transfer_test.go

## Purpose
Tests the generic transfer service with a simple import-stream to export-stream echo path for empty, small, and large byte payloads.

## APIs, Types, And Functions
The file defines `TestTransferEcho`, `newImportExportEcho`, `WriteBytesCloser`, `newWaitBuffer`, `waitBuffer.Close`, `waitBuffer.Bytes`, and `displayBytes`. It uses `client.Transfer`, `archive.NewImageImportStream`, and `archive.NewImageExportStream`.

## Control Flow And State
Each subtest creates a wait buffer, transfers bytes from an import stream to an export stream, waits for the export stream to close before reading `Bytes`, and compares output with the expected input. `displayBytes` truncates large diagnostic output in failure messages.

## Persistence And Integration Points
The test does not intentionally persist image metadata; it validates stream plumbing through the containerd transfer service and archive stream adapters. The only state is the in-memory buffer and close channel.

## Risks And Test Signals
Failures indicate transfer stream corruption, close ordering bugs, or incorrect handling of zero-length and larger payloads. The wait buffer prevents reading before the async export side has closed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/transfer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_cgroup_mount_options_linux_test.go -->
# sources/cloud-native/containerd/integration/container_cgroup_mount_options_linux_test.go

## Purpose
Validates that starting a privileged CRI container does not remount the host cgroup v2 filesystem in a way that drops important mount options such as `nsdelegate` or `memory_recursiveprot`.

## APIs, Types, And Functions
The file defines `TestPrivilegedContainerCgroupMountOptions`. It uses `cgroups.Mode`, `mount.Lookup`, `EnsureImageExists`, `PodSandboxConfigWithCleanup`, `WithPodSecurityContext`, `ContainerConfig`, `WithSecurityContext`, and CRI runtime service methods.

## Control Flow And State
The test skips unless cgroup v2 is active and the host `/sys/fs/cgroup` mount has one of the target options. It records host mount options, creates a privileged sandbox and privileged BusyBox container, starts it, then looks up host mount options again and asserts any previously present target option is still present.

## Persistence And Integration Points
State includes CRI sandbox/container lifecycle and the host cgroup mount table. It integrates containerd CRI runtime behavior, privileged container setup, and low-level mount option inspection.

## Risks And Test Signals
The test protects against host-wide cgroup mount option regressions caused by privileged container setup. It is environment-sensitive and skips when the host lacks the relevant cgroup v2 options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_cgroup_mount_options_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_cgroup_writable_linux_test.go -->
# sources/cloud-native/containerd/integration/container_cgroup_writable_linux_test.go

## Purpose
Tests the CRI runtime `cgroup_writable` setting on cgroup v2 by verifying whether a container can create a directory under `/sys/fs/cgroup`.

## APIs, Types, And Functions
The file defines `newContainerdProcess` and `TestContainerCgroupWritable`. It uses temporary containerd config files, `newCtrdProc`, `remote.NewRuntimeService`, CRI image pull helpers, `RunPodSandbox`, `CreateContainer`, `StartContainer`, `ContainerStatus`, and `ExecSync`.

## Control Flow And State
Each table case starts a separate containerd process with `cgroup_writable = true` or `false`, opens a CRI runtime service, pulls BusyBox, creates and starts a sandbox/container, confirms it is running, then executes `mkdir sys/fs/cgroup/dummy-group`. The writable case expects success and empty stderr; the readonly case expects an error containing a read-only filesystem message.

## Persistence And Integration Points
State includes temporary daemon config/root, CRI pods/containers, image content, and cgroup filesystem permissions visible inside the container. Cleanup removes pods, closes the runtime service, and terminates the daemon.

## Risks And Test Signals
The test requires cgroup v2 and root-capable CRI integration. Failures indicate the runtime config is ignored, mount permissions are wrong, or cgroup filesystem error reporting changed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_cgroup_writable_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_event_test.go -->
# sources/cloud-native/containerd/integration/container_event_test.go

## Purpose
Validates the CRI `GetContainerEvents` streaming API for sandbox and container lifecycle events, including multiple concurrent event subscribers.

## APIs, Types, And Functions
The file defines timeouts, `TestContainerEvents`, `listenToEventChannel`, `drainContainerEventsChan`, and `checkContainerEventResponse`. It uses `runtimeService.GetContainerEvents`, `RunPodSandbox`, `CreateContainer`, `StartContainer`, `StopContainer`, `RemoveContainer`, `StopPodSandbox`, and `RemovePodSandbox`.

## Control Flow And State
The test creates two streaming clients, launches goroutines to receive events into channels, drains stale events from previous tests, then runs a lifecycle: sandbox create/start, container create, container start, container stop/remove, sandbox stop/remove. After each operation it checks both subscribers for the expected event type, the sandbox state when relevant, and the expected list of container states.

## Persistence And Integration Points
State is CRI runtime sandbox/container lifecycle plus streaming gRPC state. The test integrates event publication with status snapshots included in event responses and image availability for the pause container.

## Risks And Test Signals
The helper assumes returned `ContainersStatuses` ordering matches the expected state slice and uses fixed drain/read timeouts, so slow environments can fail. True failures indicate missed events, inconsistent event payload status, broken fan-out to multiple subscribers, or stale events leaking into new subscribers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/container_event_test.go -->
