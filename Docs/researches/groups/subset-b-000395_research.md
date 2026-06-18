# subset-b-000395 Research

Grouped research report for the requested JuiceFS CSI driver subset. Each source file has a source-path title and is wrapped in deterministic reconciliation markers for splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/controller_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/controller_test.go

Purpose: tests the CSI controller service behavior implemented in the adjacent `controller.go`, including volume creation/deletion, capability reporting, validation, and snapshot/control-publish stubs. It is a broad controller unit-test file rather than production code.

Important APIs and functions: `TestNewControllerService` checks construction with patched command execution. `TestCreateVolume` covers normal dynamic volume creation, empty names, nil capabilities, duplicate/smaller capacity conflicts, and unsupported block capabilities. `TestDeleteVolume` validates dynamic PV deletion via `JfsDeleteVol`, empty volume IDs, provider errors, and static PV no-op behavior. The remaining tests exercise `ControllerGetCapabilities`, `ValidateVolumeCapabilities`, `isValidVolumeCapabilities`, unimplemented `GetCapacity`/`ListVolumes`, snapshot argument validation, and unimplemented controller publish/unpublish calls.

Control flow: most tests construct `controllerService` directly with in-memory `vols`, fake JuiceFS providers, and `dispatch.Pool` quota workers. Create/delete tests assert CSI gRPC status codes (`InvalidArgument`, `AlreadyExists`, `Internal`) after invoking service methods. Snapshot tests currently focus on missing required IDs rather than successful job creation paths.

State and persistence behavior: state is limited to the controller service `vols` map and mocked JuiceFS calls. No Kubernetes API state or filesystem state is persisted except for patched `exec.Command` behavior in construction tests.

Dependencies and integration points: depends on CSI protobufs, GoMock-generated JuiceFS mocks, gomonkey patching, GoConvey, fake Kubernetes clientsets, global config, `dispatch`, and resource volume locks. It verifies the controller-to-`juicefs.Interface` boundary for deletion/quota setup but does not run real JuiceFS or Kubernetes operations.

Risks and test signals: good signal for basic CSI validation and capability lists, but several later controller paths are only tested for unimplemented or invalid-input errors. Successful snapshot creation/deletion, restore, controller expansion, lock contention, and quota worker async completion are not deeply covered here. Tests rely on global config and monkey patching, so they are sensitive to constructor signatures and package-level state leakage.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/driver.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/driver.go

Purpose: defines the top-level CSI `Driver` that wires identity, controller, node, and provisioner services into one gRPC server.

Important APIs and types: `Driver` embeds `csi.UnimplementedIdentityServer`, `*controllerService`, `nodeService`, and `provisionerService`, and stores the gRPC server plus endpoint. `NewDriver` builds a Kubernetes client unless `config.ByProcess` is set, constructs controller/node/provisioner services, logs build metadata, and returns the assembled driver. `Run` optionally starts the external provisioner controller, parses the endpoint, listens on the endpoint transport, creates a gRPC server with an error-logging unary interceptor, and registers CSI Identity, Controller, and Node servers. `Stop` calls `d.srv.Stop()`.

Control flow: initialization is synchronous and fails fast on Kubernetes client or subservice construction errors. Runtime serving is blocking through `grpc.Server.Serve`; the provisioner runs in a background goroutine only when `config.Provisioner` is true.

State and persistence behavior: the driver itself persists only process-local service objects and server handles. External state is delegated to subservices: Kubernetes API access, mount state, provisioner leader-election leases, and JuiceFS state are not managed directly in this file.

Dependencies and integration points: integrates CSI gRPC registration, Prometheus registerers for subservice metrics, Kubernetes client creation, endpoint parsing from `util.ParseEndpoint`, global configuration, and service constructors in this package.

Risks and test signals: `Stop` assumes `Run` initialized `d.srv`; calling it before a successful `Run` would panic. `Run` uses `context.Background()` for provisioner lifetime, so shutdown coordination depends on process termination rather than a passed context. The constructor logs a misspelled `"verison"` key, which is harmless but visible in logs. Tests cover constructor success and a node-service error path, not real socket serving or provisioner goroutine lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/driver_suite_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/driver_suite_test.go

Purpose: provides the Ginkgo/Gomega test-suite entry point for the `driver` package.

Important APIs and functions: `TestService` registers Gomega's fail handler and calls `RunSpecs(t, "driver Suite")`.

Control flow: Go's `testing` package invokes `TestService`, then Ginkgo discovers package-level `Describe` specs in files such as `node_test.go`.

State and persistence behavior: none beyond global Ginkgo test registration. It does not allocate driver state or external resources itself.

Dependencies and integration points: depends on `github.com/onsi/ginkgo/v2` and `github.com/onsi/gomega`. It is required for BDD-style tests in this package to run under `go test`.

Risks and test signals: no behavioral coverage is present here. If Ginkgo specs or ordinary `testing` tests share global config, this suite file does not provide setup/teardown isolation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/driver_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/driver_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/driver_test.go

Purpose: tests `NewDriver` construction under normal, subservice-error, and `config.ByProcess` modes.

Important APIs and functions: `TestNewDriver` uses GoConvey cases. It patches `k8s.NewClient`, `newNodeService`, `newProvisionerService`, `exec.Command`, and `(*exec.Cmd).CombinedOutput` to avoid real Kubernetes or command execution, then asserts the endpoint is preserved or an error propagates from node service construction.

Control flow: each case replaces package functions with fakes, builds a Prometheus registerer using `util.NewPrometheus`, and calls `NewDriver`. The `by process` case sets `config.ByProcess = true` to skip Kubernetes client creation.

State and persistence behavior: manipulates global `config.ByProcess`, patches global functions, and constructs transient fake clientsets. It does not run the gRPC server or create persistent resources.

Dependencies and integration points: depends on gomonkey, GoMock, GoConvey, fake Kubernetes clientsets, Prometheus utility helpers, and driver subservice constructors. It is intended to verify constructor orchestration rather than CSI behavior.

Risks and test signals: the patch functions shown in this file use older signatures for `newNodeService` and `newProvisionerService` than the current implementations, which now accept Prometheus/leader-election arguments. That suggests the test may be stale or fail to compile until updated. The test also mutates `config.ByProcess` without restoring it, creating possible cross-test contamination.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/driver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/fakes.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/fakes.go

Purpose: builds an in-memory fake `Driver` for tests that need controller and node services without real Kubernetes, real mounts, or real JuiceFS.

Important APIs and functions: `NewFakeDriver(endpoint, fakeProvider)` constructs a `Driver` with a fake endpoint, fake controller service, and fake node service. The fake controller uses the supplied `juicefs.Interface`, an empty `vols` map, and a quota dispatch pool. The fake node service uses a fake Kubernetes clientset, fake mount table containing `/tmp/csi-mount/target`, a fake exec runner, metrics, unmounted-path tracking, and test-local volume locks.

Control flow: the helper creates Prometheus metrics, builds a `mount.SafeFormatAndMount` with `mount.NewFakeMounter`, and returns a partially populated driver. It does not construct a provisioner service or gRPC server.

State and persistence behavior: all state is process-local and test-scoped: fake mount entries, maps, sync maps, metrics, and locks. No filesystem or Kubernetes API writes occur.

Dependencies and integration points: integrates test code with `juicefs.Interface`, fake client-go, Kubernetes mount fake utilities, `testingexec.FakeExec`, `util.NewPrometheus`, `dispatch.Pool`, and `resource.VolumeLocks`.

Risks and test signals: useful for isolating CSI method tests, but it does not mirror all production fields, especially provisioner service and shared volume locks. Metrics registration can conflict if reused with duplicate metric names under the same registerer.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/fakes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/identity.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/identity.go

Purpose: implements the CSI Identity service for the JuiceFS CSI driver.

Important APIs and functions: `GetPluginInfo` returns `config.DriverName` and the build-time `driverVersion`. `GetPluginCapabilities` advertises `CONTROLLER_SERVICE`. `Probe` returns an empty successful response.

Control flow: all methods are simple request logging plus deterministic response construction. No validation, health check, or external dependency is involved.

State and persistence behavior: no mutable state is changed. The only data read is package/global configuration and build metadata.

Dependencies and integration points: uses CSI protobuf types, klog, and `config.DriverName`. These methods are registered by `Driver.Run` and are called by the container orchestrator during CSI discovery.

Risks and test signals: `Probe` does not verify node/controller readiness or backend health, so it only signals that the gRPC process can answer. Tests assert exact responses for plugin info, capabilities, and probe.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/identity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/identity_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/identity_test.go

Purpose: unit-tests the CSI Identity methods.

Important APIs and functions: `TestDriver_GetPluginInfo` checks that the response contains `config.DriverName` and the default empty vendor version in test builds. `TestGetPluginCapabilities` asserts the single `CONTROLLER_SERVICE` plugin capability. `TestDriver_Probe` asserts an empty successful `ProbeResponse`.

Control flow: each test constructs a minimal `Driver` value and calls the identity method directly without a gRPC server.

State and persistence behavior: no persistent state. Tests read package globals such as `driverVersion`.

Dependencies and integration points: depends on CSI protobufs, `grpc.Server` type only for struct field shape, Go's `reflect.DeepEqual`, and `config.DriverName`.

Risks and test signals: good regression signal for advertised identity constants. It does not cover logging, nil request handling beyond the tested values, or build-time version injection.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/identity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/mocks/mock_fs.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/mocks/mock_fs.go

Purpose: provides small fake `os.FileInfo` implementations for filesystem-related tests.

Important APIs and types: `FakeFileInfoIno1` and `FakeFileInfoIno2` implement `Name`, `Size`, `Mode`, `ModTime`, `IsDir`, and `Sys`. Their `Sys` methods return `*syscall.Stat_t` values with distinct inode numbers 1 and 2. `FakeFileInfoIno1` returns permissive mode; `FakeFileInfoIno2` returns device mode.

Control flow: there is no control flow beyond returning fixed values from interface methods.

State and persistence behavior: no state is stored or mutated. Values are synthetic and deterministic.

Dependencies and integration points: used by tests that patch `os.Stat` and need inode/mode-like data without touching real files. Depends on `io/fs`, `syscall`, and `time`.

Risks and test signals: because these fakes return minimal metadata, they can mask behavior that depends on real ownership, permissions, timestamps, directories, or non-Unix `Sys` values. They are test fixtures only.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/mocks/mock_fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/mocks/mock_mount.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/mocks/mock_mount.go

Purpose: generated GoMock implementation of `k8s.io/utils/mount.Interface`.

Important APIs and types: `MockInterface` records calls for `GetMountRefs`, `IsLikelyNotMountPoint`, `List`, `Mount`, `MountSensitive`, and `Unmount`. `NewMockInterface` creates the mock and `EXPECT` exposes the recorder. Recorder methods build typed expectations for each mount operation.

Control flow: each mocked method calls `m.ctrl.Call`, casts return values, and returns them to tests. Recorder methods call `RecordCallWithMethodType`.

State and persistence behavior: state is held by GoMock's controller and expectation recorder. No actual mount operations occur.

Dependencies and integration points: generated from Kubernetes mount interfaces and used by driver/juicefs tests to assert bind mounts, mountpoint checks, and unmount behavior without kernel mount privileges.

Risks and test signals: generated code should not be manually edited. It can only validate expected method calls and return plumbing; it cannot detect runtime mount table semantics or Linux permission issues.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/mocks/mock_mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/node.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/node.go

Purpose: implements the CSI Node service, including publish/unpublish, node metadata, volume stats, health metrics, and unimplemented staging/expansion stubs.

Important APIs and types: `nodeService` embeds CSI unimplemented node server and `mount.SafeFormatAndMount`, and owns `juicefs.Interface`, node ID, Kubernetes client, Prometheus metrics, recently unmounted paths, quota dispatch pool, and volume locks. `newNodeMetrics` registers counters and a `volume_path_health` gauge. `newNodeService` creates a real mounter, JuiceFS provider, metrics, shared volume locks, and starts cleanup of old unmounted-path markers.

Control flow: `NodePublishVolume` validates target and mount capability, takes a per-target lock, skips already-mounted targets, creates the target directory, combines readonly/spec/volume-context mount options, calls `JfsMount`, creates or locates the volume subpath through `Jfs.CreateVol`, bind-mounts to the target, and optionally enqueues quota setting unless the controller already set quota or quota is disabled. `NodeUnpublishVolume` takes the same lock, delegates to `JfsUnmount`, marks the path recently unmounted, and deletes the health metric labels. `NodeGetVolumeStats` validates inputs, rejects recently unmounted paths, checks path existence and mountpoint state with timeouts, handles corrupted mounts asynchronously, records health, and returns byte and inode usage from `util.GetDiskUsage`.

State and persistence behavior: process-local state includes volume locks, metric counters/gauges, and a `sync.Map` of unmounted paths retained for roughly five minutes. External state includes filesystem target directories, mount table changes delegated to JuiceFS, Kubernetes corruption handling, and quota commands run asynchronously through the dispatch pool.

Dependencies and integration points: integrates CSI node RPCs, Kubernetes mount utilities, JuiceFS provider, Prometheus, global config, retry helpers, resource locks/corrupted-mount handling, and app pod volume paths. It depends on `volumeContext` keys such as `subPath`, `mountOptions`, `capacity`, and controller quota markers.

Risks and test signals: async quota failures are logged but do not fail publish. `req.Secrets` is nulled before logging, mutating the request object. `NodeGetVolumeStats` can start background corrupted-mount remediation after a failed check. Tests cover publish/unpublish success and core failures, capability/info/stub methods, and input validation, but not all stats success paths, corrupted mount handling, or concurrent lock contention.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/node_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/node_test.go

Purpose: tests the `nodeService` CSI node implementation using Ginkgo/Gomega and ordinary `testing` cases.

Important APIs and functions: the Ginkgo `Describe("nodeService")` block covers `NodePublishVolume` normal operation, readonly mounts, mount options from volume attributes and capabilities, `JfsMount` errors, `CreateVol` errors, bind errors, target creation errors, missing target, missing capability, invalid capability, and `NodeUnpublishVolume` success/failure/missing target. Later table tests cover `NodeGetCapabilities`, `NodeGetInfo`, `newNodeService`, `NodeExpandVolume`, `NodeGetVolumeStats` invalid input, `NodeStageVolume`, and `NodeUnstageVolume`.

Control flow: tests build a fresh `nodeService` with fake Kubernetes client, metrics, safe mounter, sync map, and volume locks. They use GoMock JuiceFS/Jfs objects to assert exact calls and gomonkey patches for filesystem and exec functions.

State and persistence behavior: uses in-memory fake clients, patched filesystem calls, fake metrics, and local lock state. It does not perform real mounts or disk usage queries in successful stats paths.

Dependencies and integration points: depends on CSI protobufs, GoMock JuiceFS mocks, gomonkey, Ginkgo/Gomega, fake Kubernetes clients, klog context helpers, and resource locks. It validates the node-to-JuiceFS provider boundary and basic CSI response shapes.

Risks and test signals: strong signal for publish/unpublish branching and mount option composition. The tests do not exercise successful `NodeGetVolumeStats`, recently-unmounted suppression, corrupted mount recovery, quota dispatch behavior, or lock contention. Several `It("should succeed")` names actually expect errors, so test names are less precise than assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/provisioner.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/provisioner.go

Purpose: implements the external dynamic provisioner side of the CSI driver, translating PVC/StorageClass options into PVs and managing delete/restore/quota side effects.

Important APIs and types: `provisionerService` owns the JuiceFS provider, Kubernetes client, leader-election settings, snapshot client, provision metrics, quota pool, and volume locks. `newProvisionerService` creates the provider, snapshot client when REST config exists, metrics, and locks. `Run` starts `sig-storage-lib-external-provisioner` with driver name, leader election, lease duration, namespace, and configured worker threadiness. `Provision`, `RestoreDataSource`, and `Delete` implement the provisioner interface.

Control flow: `Provision` rejects PVC selectors, resolves StorageClass parameters and mount options through `resource.ObjectMeta`, chooses `subPath` from `pathPattern` or PV name, rejects read-only dynamic volumes without a path pattern, builds CSI PV attributes and secret refs, optionally adds secret finalizers, optionally enqueues controller-side quota setting, and triggers snapshot restore when `PVC.Spec.DataSource` references a ready `VolumeSnapshot`. `RestoreDataSource` validates snapshot/content binding, parses snapshot handles, resolves secrets, and calls `juicefs.RestoreSnapshot`. `Delete` honors reclaim policy, uses volume locks, checks whether other PVs share the same subpath, loads publish secrets, calls `JfsDeleteVol`, and removes secret finalizers when safe.

State and persistence behavior: persists Kubernetes PV specs, secret finalizers, background quota work, snapshot restore jobs through JuiceFS, and deletion side effects in the filesystem/backend. It also uses process-local Prometheus counters, dispatch pools, and locks.

Dependencies and integration points: integrates Kubernetes core APIs, external provisioner library, CSI snapshot clientset, JuiceFS provider, global config, resource helpers for object metadata/subpath/finalizer checks, quota feature detection, and StorageClass/PVC conventions.

Risks and test signals: quota setting is asynchronous, so provisioning can succeed even if quota later fails. If snapshot client creation fails, restore requests return a PV as finished without restoring data, which is logged but may surprise callers. The file is not directly covered by a dedicated listed test file; behavior is partially exercised indirectly through driver construction and controller/juicefs mocks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/provisioner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/version.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/version.go

Purpose: exposes build and runtime version metadata for the CSI driver.

Important APIs and types: build-time variables `driverVersion`, `gitCommit`, and `buildDate` are intended to be set by linker flags. `VersionInfo` serializes driver version, commit, build date, Go runtime version, compiler, platform, and `config.DisableGraceUpgrade`. `GetVersion` populates the struct from globals, `runtime`, and config. `GetVersionJSON` returns an indented JSON string.

Control flow: `GetVersionJSON` calls `GetVersion`, marshals with `json.MarshalIndent`, and returns the string or marshal error.

State and persistence behavior: no state is mutated or persisted. It reads process-global version/config values.

Dependencies and integration points: used by CLI/logging paths that need version output. Depends on `runtime`, `encoding/json`, `fmt`, and driver config.

Risks and test signals: zero-value build variables produce empty version fields in local/test builds. The JSON marshal path is straightforward; tests patch marshal errors and assert Go version formatting.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/version_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/driver/version_test.go

Purpose: tests version metadata helpers.

Important APIs and functions: `TestGetVersionJSON` patches `GetVersion` for a normal JSON path and patches `json.MarshalIndent` to force an error. `TestGetVersion` asserts the returned Go runtime version contains `go1.`.

Control flow: GoConvey handles the JSON cases; a standard subtest checks runtime metadata.

State and persistence behavior: no persistent state. Tests use monkey patches of package/global functions.

Dependencies and integration points: depends on gomonkey, GoConvey, `encoding/json`, and runtime behavior.

Risks and test signals: confirms JSON error propagation and basic runtime population. It does not validate linker-injected fields, platform string shape beyond Go version, or `DisableGraceUpgrade` configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/driver/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/batch.go -->
# sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/batch.go

Purpose: coordinates batch graceful upgrades of JuiceFS mount pods on the current node.

Important APIs and types: `BatchUpgrade` tracks a batch config name/index, Kubernetes client, recreate flag, selected `PodUpgrade` objects, and success/failure maps protected by a mutex. `NewBatchUpgrade` builds the object from an `upgradeRequest`. `fetchPods` loads upgrade config, lists mount pods on the local node, filters to names in the requested batch, checks upgrade eligibility, builds `PodUpgrade` records, and reports already-upgraded pods over the client connection. `BatchUpgrade` runs `gracefulShutdown` concurrently for each selected pod. `TriggerBatchUpgrade` is the CLI/client entry point that sends a `BATCH` request over a Unix socket and prints responses until a current-batch terminal message is seen.

Control flow: fetch phase narrows the global batch plan to this node, then upgrade phase uses a wait group to run pod upgrades in parallel. Each pod failure records status, sends messages, and removes upgrade-process annotations when needed.

State and persistence behavior: process-local state includes `podsToUpgrade`, `successSum`, and `failSum`. External state is Kubernetes pod annotations/events/jobs and socket output; actual pod recreation is handled by `PodUpgrade` and resource helpers.

Dependencies and integration points: integrates config batch loading, Kubernetes pod listing by label/field selectors, resource eligibility/hash helpers, `PodUpgrade` from `grace.go`, and the shutdown Unix socket protocol.

Risks and test signals: the goroutine loop closes over `p` from the range; with modern Go range semantics this is safe, but older compilers would risk all goroutines using the same pod. The file assumes `batchIndex` is valid for `batchConfig.Batches[u.crtBatchIndex-1]`; malformed requests can panic. No listed test covers batch behavior directly.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/batch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/grace.go -->
# sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/grace.go

Purpose: implements the Unix-socket graceful upgrade control plane for JuiceFS mount pods, including single-pod upgrades, batch dispatch, canary validation, FUSE fd handoff, SIGHUP, and optional pod recreation tracking.

Important APIs and types: `ServeGfShutdown` starts a Unix socket listener and dispatches connections to `handleShutdown`. `upgradeRequest` and `parseRequest` decode socket messages. `SinglePodUpgrade`, `NewPodUpgrade`, and `(*PodUpgrade).gracefulShutdown` orchestrate one pod. Supporting methods include `prepareShutdown`, `sighup`, `isInUpgradeProcess`, `waitForUpgrade`, `uploadBinary`, `TriggerShutdown`, and `sendMessage`.

Control flow: incoming messages either list known FUSE fds, start a batch upgrade, or run a single-pod upgrade under a 30-minute timeout. A single upgrade fetches the mount pod, checks node and hash, verifies eligibility, reads JuiceFS `.config` from the mount point, creates and waits for a canary job, optionally annotates the pod as upgrading, captures/closes FUSE fd for recreate flows, uploads binaries for non-recreate flows, sends SIGHUP to the mount process, creates an event, and for recreate waits for a replacement ready pod with the same upgrade UUID.

State and persistence behavior: persistent side effects are Kubernetes annotations (`JfsUpgradeProcess`), events, Jobs, and possibly modified files inside the mount container. It reads mount-point config files and uses `passfd.GlobalFds` for FUSE session ID/fd state. Socket messages are transient progress output to the caller.

Dependencies and integration points: integrates Kubernetes client operations, `resource` upgrade eligibility and job/pod status helpers, `builder.NewCanaryJob`, `passfd`, config image feature detection, mount pod labels/annotations, and Unix domain socket clients.

Risks and test signals: errors from `NewPodUpgrade` can return nil `err` in some validation branches such as wrong node or missing hash, which can make failure diagnosis ambiguous. `waitForUpgrade` closes `done` in a defer while informer handlers may send to it, risking send-on-closed-channel if events race after return. Test coverage in the listed set only covers `parseRequest`; the operational Kubernetes/socket/fd paths require integration testing.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/grace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/grace_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/grace_test.go

Purpose: tests parsing of graceful-upgrade socket request messages.

Important APIs and functions: `Test_parseRequest` checks a pod request with explicit action, a pod request defaulting to `noRecreate`, and a batch request containing `batchConfig` and `batchIndex`.

Control flow: each table entry calls `parseRequest` and compares the resulting `upgradeRequest` with `reflect.DeepEqual`.

State and persistence behavior: no state is persisted or mutated. It is a pure string parsing test.

Dependencies and integration points: depends on the constants in `grace.go`, `fmt`, `reflect`, and Go's `testing`.

Risks and test signals: confirms basic protocol parsing only. It does not test malformed batch options, invalid indexes, socket I/O, Kubernetes upgrade flows, or fd handoff.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/grace/grace_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd.go -->
# sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd.go

Purpose: manages FUSE file descriptor discovery, storage, serving, and transfer across mount pod graceful upgrades using Unix domain sockets and ancillary file descriptor passing.

Important APIs and types: `Fds` owns a Kubernetes client, mutex, base path, and map from upgrade UUID to `fd` records. Global entry points include `InitGlobalFds`, `InitTestFds`, `GetFdAddress`, and `GlobalFds`. Methods include `PrintFds`, `ParseFuseFds`, `getFdAddress`, `StopFd`, `CloseFd`, `parseFuse`, `ServeFuseFd`, `serveFuseFD`, `handleFDRequest`, `UpdateSid`, and `GetSid`. Low-level helpers `GetFuseFd`, `getFd`, and `putFd` receive/send Unix file descriptors.

Control flow: initialization creates a global registry and asynchronously scans the base path for `fuse_fd_comm.*` sockets belonging to live eligible mount pods. `getFdAddress` allocates a per-upgrade socket path if no fd is known. `parseFuse` connects to an existing pod socket to receive the FUSE fd, stores it, and starts a server socket. `handleFDRequest` sends the saved fd and setting to a requester, closes local ownership, then receives a replacement fd or close message. `StopFd` and `CloseFd` clean up descriptors and socket directories.

State and persistence behavior: process-local state is guarded by `globalMu` and includes fd integers, fuse settings, session IDs, and socket paths. Filesystem state includes per-upgrade directories and Unix socket files under `basePath`. Kernel fd ownership is actively transferred and closed, so incorrect sequencing can leak or prematurely close FUSE fds.

Dependencies and integration points: integrates Kubernetes pod listing/labels, upgrade UUID helpers, global graceful-upgrade config, mount path existence checks, Unix sockets, `syscall.Sendmsg`/`Recvmsg`, `SCM_RIGHTS`, and `config.SupportFusePass`.

Risks and test signals: `ParseFuseFds` launches goroutines that capture loop variables (`entry` and `subdir`); under older Go versions this could target the wrong directory. `getFd` assumes rights parsing succeeds and may append nil/empty rights before checking errors. Socket server goroutines rely on `done` closure and listener close behavior. No listed tests cover fd transfer, so this path is high-risk and integration-dependent.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd_linux.go -->
# sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd_linux.go

Purpose: provides the Linux-specific `Recvmsg` flag for close-on-exec fd reception.

Important APIs and constants: under build tag `linux`, `msgCmsgCloexec` is defined as `syscall.MSG_CMSG_CLOEXEC`.

Control flow: no runtime control flow. The Go build selects this file on Linux.

State and persistence behavior: no mutable state.

Dependencies and integration points: used by `passfd.getFd` as the flags argument to `syscall.Recvmsg`, ensuring received descriptors are marked close-on-exec on Linux.

Risks and test signals: small platform shim. Behavior depends on Linux kernel support for `MSG_CMSG_CLOEXEC`; there are no direct tests in the listed set.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd_other.go -->
# sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd_other.go

Purpose: provides the non-Linux fallback for the `Recvmsg` close-on-exec flag.

Important APIs and constants: under build tag `!linux`, `msgCmsgCloexec` is defined as `0`.

Control flow: no runtime control flow. The Go build selects this file on non-Linux platforms.

State and persistence behavior: no mutable state.

Dependencies and integration points: used by `passfd.getFd` so the package can compile on platforms that do not define `syscall.MSG_CMSG_CLOEXEC`.

Risks and test signals: received file descriptors may not be close-on-exec on non-Linux platforms. The broader FUSE fd passing feature is likely Linux-oriented despite this compile shim.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs.go -->
# sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs.go

Purpose: implements the central JuiceFS provider abstraction used by CSI controller, node, and provisioner services. It converts Kubernetes/CSI inputs into JuiceFS settings, mounts file systems through process or pod strategies, binds pod targets, manages quotas/auth/status, and orchestrates snapshot Jobs.

Important APIs and types: `Interface` combines Kubernetes mount operations with JuiceFS-specific operations such as `JfsMount`, `JfsDeleteVol`, `JfsUnmount`, `SetQuota`, `Settings`, `AuthFs`, `Status`, and snapshot methods. `juicefs` owns a safe mounter, Kubernetes client, mount implementation, and cache-cleanup maps. `jfs` represents a mounted filesystem and implements `GetBasePath`, `CreateVol`, `BindTarget`, and `GetSetting`.

Control flow: `NewJfsProvider` selects process or pod mounting based on `config.ByProcess`. `JfsMount` validates the kubelet target, builds settings through `genJfsSettings`, parses app info, mounts via `MountFs`, and returns a `jfs` wrapper. `Settings` merges PV/PVC/node context, allowed PVC annotations, secrets, options, and global config into `config.JfsSetting`, then optionally runs auth/format in process mode. `getUniqueId` implements storage-class and filesystem-share mount identity rules. `JfsUnmount` unmounts the target, resolves the mount pod or process refcount, cleans cache when needed, and delegates to mount implementations.

State and persistence behavior: process-local state includes `UUIDMaps` and `CacheDirMaps` for cache cleanup in process mode. Filesystem state includes target directories, subpath directories, bind mounts, mount points, cache directories, and cleanup operations. Kubernetes state includes mount pods, PV/PVC/SC/Secret reads, snapshot/restore/delete Jobs, and snapshot Secrets. External command state includes JuiceFS auth/format/quota/status subprocesses with environment variables.

Dependencies and integration points: integrates Kubernetes core/client-runtime APIs, CSI config parsing, mount package utilities, `podmount.MntInterface`, builder Jobs, resource helpers, global config, process exec, and JuiceFS CLI paths for CE/EE. It is the main boundary between CSI RPC code and actual JuiceFS/Kubernetes side effects.

Risks and test signals: `validTarget` blocks any target containing `".."` or `"/."`, which is intentionally strict but could reject unusual valid paths. Async/cache cleanup and snapshot job polling rely on fixed timeouts. Snapshot delete returns success when the snapshot secret is missing, treating it as already deleted. Tests cover create volume directory logic, bind target branch behavior, mount/auth/format/cleanup helpers, `MountFs`, `ceFormat`, and target validation, but many Kubernetes Job, quota, unique ID, and real mount paths are integration-only.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs_suite_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs_suite_test.go

Purpose: provides the Ginkgo/Gomega test-suite entry point for the `juicefs` package.

Important APIs and functions: `TestService` registers the Gomega fail handler and calls `RunSpecs(t, "juicefs Suite")`.

Control flow: Go's test runner enters this function, then Ginkgo runs package-level specs from `juicefs_test.go`.

State and persistence behavior: no persistent state is created here.

Dependencies and integration points: depends on Ginkgo v2 and Gomega.

Risks and test signals: no direct behavior coverage. It does not isolate package-level config state that individual specs may mutate.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs_test.go

Purpose: tests the JuiceFS provider and mounted filesystem helpers with patched filesystem/exec behavior and mocked mount implementations.

Important APIs and functions: the `jfs` specs test `CreateVol` directory creation/error paths and `BindTarget` normal, already-bound, and bound-to-other-device cases. The `juicefs` specs test `JfsMount` for CE/EE, parse errors, missing token/bucket cases, mount failures, `JfsUnmount` behavior, `JfsCleanupMountPoint`, `AuthFs`, `MountFs`, and `ceFormat`. Ordinary tests cover `GetBasePath`, format command generation for pod mode, and `validTarget`.

Control flow: tests construct `juicefs` and `jfs` structs directly, patch functions such as `mount.PathExists`, `os.MkdirAll`, `mount.ParseMountInfo`, `os.Stat`, command output, and config UUID lookup, then assert results. GoMock mount and `MntInterface` objects verify call boundaries.

State and persistence behavior: uses global config mutations (`StorageClassShareMount`, `AccessToKubelet`, `ByProcess`, `CSIPod`) and environment variables such as `JFS_NO_UPDATE_CONFIG`, along with monkey patches. It does not perform real mounts, Kubernetes Job creation, or real JuiceFS CLI execution.

Dependencies and integration points: depends on Ginkgo/Gomega, gomonkey, GoMock, fake Kubernetes clientsets, Kubernetes mount utilities, config parsing, driver test fakes, and podmount mocks.

Risks and test signals: provides useful unit coverage for mount option and error plumbing. Some monkey patches in the file appear to use older method signatures, for example `AuthFs` without the current `force bool` argument, so the tests may need maintenance against the current implementation. The suite does not cover snapshot Jobs, `SetQuota`, `Status`, unique ID share-mount decisions, PVC annotation merging, or real process/pod mounting.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/juicefs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mocks/mock_jfs.go -->
# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mocks/mock_jfs.go

Purpose: generated GoMock implementation of the `juicefs.Jfs` interface.

Important APIs and types: `MockJfs` records calls to `BindTarget`, `CreateVol`, `GetBasePath`, and `GetSetting`. `NewMockJfs` creates the mock and `EXPECT` exposes typed expectation recorders.

Control flow: mocked methods delegate to the GoMock controller and cast returned values. Recorder methods register expected calls and argument matchers.

State and persistence behavior: state lives in GoMock expectations and call history. No actual filesystem or mount operations are performed.

Dependencies and integration points: used by node-service tests to assert that `NodePublishVolume` creates subpaths, bind-mounts targets, and reads settings for quota handling.

Risks and test signals: generated code should not be manually edited. It validates interface-level interactions only, not real mount behavior or `jfs` implementation details.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mocks/mock_jfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mocks/mock_juicefs.go -->
# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mocks/mock_juicefs.go

Purpose: generated GoMock implementation of the high-level `juicefs.Interface` used by driver/controller/node tests.

Important APIs and types: `MockInterface` mocks all JuiceFS provider and embedded mount operations, including `AuthFs`, snapshot methods, `CreateTarget`, `GetSubPath`, `JfsCreateVol`, `JfsDeleteVol`, `JfsMount`, `JfsUnmount`, `SetQuota`, `Settings`, `Status`, and Kubernetes mount `Mount`/`Unmount` methods. Recorder methods expose typed expectations for each call.

Control flow: each method calls the GoMock controller with arguments and casts configured return values. There is no business logic.

State and persistence behavior: no external state. Call state is retained in the mock controller.

Dependencies and integration points: used by CSI controller and node tests to decouple service logic from actual JuiceFS, Kubernetes, and mount side effects.

Risks and test signals: generated code must match the current `juicefs.Interface`; if the interface changes, stale mocks can cause compile failures or tests that no longer cover new methods. Mock tests validate call contracts but not real CLI/Kubernetes/mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mocks/mock_juicefs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/cci-serverless.go -->
# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/cci-serverless.go

Purpose: builds CCI serverless mount sidecar pod specs for JuiceFS, adapting common mount-pod generation to a non-privileged serverless environment.

Important APIs and types: constants define CCI annotation/driver values. `CCIBuilder` embeds `ServerlessBuilder`, PVC, and app pod context. `NewCCIBuilder` constructs it from a `JfsSetting`, capacity, app pod, and PVC. `NewMountSidecar` creates the sidecar pod, adds post-start mount/quota checking, serverless env vars, CCI-specific volumes, cache volumes, and the shell command. `OverwriteVolumes` rewrites app volumes to a CCI CSI `gpath` volume using the mountpoint. `OverwriteVolumeMounts` forces mount propagation to `None`. `genCCIServerlessVolumes` and `genNonPrivilegedContainer` build the check-mount secret volume and container security context.

Control flow: `NewMountSidecar` starts from `genCommonJuicePod`, computes capacity/community/quota path, ensures a lifecycle exists, appends env and volume configuration, then sets command to init plus mount commands. The post-start hook invokes the check-mount script with escaped subpath/name/quota/mount values and logs to the container stdout.

State and persistence behavior: no state is persisted by the builder itself. The produced pod spec will later create Kubernetes pod, secret volume, cache volumes, lifecycle hooks, and CCI CSI volume mounts.

Dependencies and integration points: integrates `BaseBuilder`, `ServerlessBuilder`, global config paths, common mount container names, CCI CSI driver annotations, Kubernetes core pod/volume APIs, and shell escaping.

Risks and test signals: correctness depends on the external check-mount script secret and CCI-specific CSI driver behavior. `SYS_ADMIN`/`MKNOD` are still requested despite "non-privileged" naming, so platform policy must allow those capabilities. No direct listed test covers this file.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/cci-serverless.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/common.go -->
# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/common.go

Purpose: provides shared pod, command, metadata, metrics, and secret-volume generation for JuiceFS mount pod builders.

Important APIs and types: `BaseBuilder` owns `*config.JfsSetting` and requested capacity. `genPodTemplate` builds a baseline pod from CSI pod attributes. `genCommonJuicePod` applies generated pod attributes, metadata, finalizer, service account, priority, restart policy, hostname, termination grace period, volumes, secret-sourced env vars, resources, lifecycle, probes, and metrics ports. Other helpers include `genHostname`, `genMountCommand`, `genInitCommand`, `getQuotaPath`, `getJobCommand`, `genMetricsPort`, `GenMetadata`, `_genMetadata`, and `_genJuiceVolumes`.

Control flow: common pod generation first refreshes pod attributes from config, adjusts encrypted init config compatibility, creates a container through a passed generator, overlays labels/annotations, mounts secret/config volumes, appends env vars, and chooses lifecycle/ports based on image support, webhook mode, host networking, and CE/EE mode. Command generation assembles CE or EE mount/format/job commands while handling subdir options, metrics defaults, RSA key options, readonly stripping for jobs, init config copies, and ACL config symlinks.

State and persistence behavior: builder methods are mostly pure transformations from `JfsSetting` to Kubernetes objects and shell strings, but `genCommonJuicePod` mutates `jfsSetting.InitConfig` when encrypted config is unsupported by the image. The resulting pods persist labels, annotations, finalizers, secret volumes, env vars, lifecycle hooks, and metrics ports in Kubernetes when created.

Dependencies and integration points: integrates global driver config, common labels/annotations/finalizers, security shell escaping, resource requirements from `PodAttr`, Kubernetes core APIs, and controller-runtime finalizer helpers. Downstream builders for pod/serverless/job modes reuse these helpers.

Risks and test signals: shell command construction is security-sensitive and relies on `security.EscapeBashStr` plus `util.QuoteForShell`. Metrics port parsing accepts up to six digits and does not validate port range. Map iteration over `Configs` yields nondeterministic volume order. Tests cover metadata generation and init command cases, not full pod templates, mount command generation, metrics parsing, or volume generation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/common_test.go -->
# sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/common_test.go

Purpose: tests selected common builder helpers for metadata and init command generation.

Important APIs and functions: `TestGenMetadata` verifies delete-delay and clean-cache annotations, user labels/annotations, internal JuiceFS UUID/unique ID annotations, pod hash/upgrade labels, and that internal annotations override user-provided values. `TestGenInitCommand` checks raw format command retention, CE RSA key addition, EE RSA ignore behavior, init-config copy command generation, EE ACL symlink addition, and CE ACL ignore behavior.

Control flow: each table case constructs a minimal `config.JfsSetting` or `BaseBuilder`, invokes the helper, and compares exact maps or strings.

State and persistence behavior: no external state. Tests operate on in-memory settings only.

Dependencies and integration points: depends on common label/annotation constants and builder/config types. It gives focused regression signal for metadata consumed by mount-pod selection and graceful upgrade logic.

Risks and test signals: useful coverage for two helper surfaces, but it does not cover `genCommonJuicePod`, volume generation, lifecycle/probe behavior, metrics port parsing, mount command generation, job command generation, or serverless builders.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/common_test.go -->
