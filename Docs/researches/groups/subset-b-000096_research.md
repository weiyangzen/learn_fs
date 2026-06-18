# Research: subset-b-000096

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/inspect.go -->
# sources/cloud-native/cri-o/server/inspect.go

Purpose: implements CRI-O's extended HTTP inspection interface and helper serialization for `/config`, `/info`, `/containers/{id}`, pause/unpause, goroutine stacks, heap dumps, and optional pprof routes.

Important APIs and functions: `getIDMappingsInfo` reports configured UID/GID mappings or a full host mapping when none are configured. `getInfo` projects storage, cgroup, and default ID mapping data into `types.CrioInfo`. `getContainerInfo` resolves regular and infra containers, validates state and sandbox existence, selects an infra PID fallback from another running pod container, and returns `types.ContainerInfo`. `GetExtendInterfaceMux` builds the chi router and binds all inspect endpoints.

Control flow: container inspection first tries `GetContainer`, then `getInfraContainer`, then uses `StateNoLock` and the sandbox lookup before constructing JSON. HTTP handlers map known sentinel errors to 404 or 500 responses. Pause and unpause validate container state before calling runtime pause/unpause and status refresh. Heap dumps are written through a temporary file and copied to the response.

State and persistence: the file reads server config, container state, sandbox IPs, runtime status, and temporary heap data. Pause/unpause mutate runtime/container state through `ContainerServer.Runtime()` and then persist status through the runtime status update path.

Dependencies and integration: uses chi for routing, goccy JSON for response encoding, CRI-O internal `oci`, `sandbox`, `types`, and runtime interfaces, Go pprof/debug utilities, and `utils.WriteGoroutineStacksTo`.

Risks: pause/unpause are exposed as GET routes with side effects and depend on the extended-interface listener being appropriately protected. `getContainerInfo` uses `context.TODO()` in HTTP handlers, so cancellation/deadline propagation is absent. Heap dump generation can be expensive and writes a temp file. Infra PID fallback may hide missing infra PIDs by choosing an arbitrary running pod container.

Test signals: covered by both unit and Ginkgo tests for `/info`, `/containers`, pause/unpause error mapping, `getInfo`, successful `getContainerInfo`, and sentinel error returns for missing containers, nil state, and missing sandbox.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/inspect_ginkgo_test.go -->
# sources/cloud-native/cri-o/server/inspect_ginkgo_test.go

Purpose: Ginkgo tests for the extended inspect HTTP mux, focused on route registration and HTTP status behavior.

Important APIs and functions: initializes `sut.GetExtendInterfaceMux(false)` with `httptest.ResponseRecorder`; exercises `/info`, `/containers/{id}`, `/pause/{id}`, and `/unpause/{id}` through real HTTP requests.

Control flow: each case prepares the shared test server, mock runtime/config, container/sandbox state, serves one request through the chi mux, and asserts the response status.

State and persistence: mutates in-memory sandbox and container stores, plus container state objects, but does not persist runtime data. It validates error handling when sandboxes are removed after containers are registered.

Dependencies and integration: integrates server test framework helpers, mocked runtime behavior, `net/http/httptest`, chi, Ginkgo/Gomega, and `oci.ContainerState`.

Risks: success for pause/unpause is not deeply asserted because mocked runtime update failures drive 500 cases; the tests primarily protect HTTP status mapping and route presence.

Test signals: confirms `/info` success, valid and invalid `/containers` outcomes, route-not-found behavior for missing IDs, pause state conflict behavior, and unpause state conflict/update-error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/inspect_ginkgo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/inspect_test.go -->
# sources/cloud-native/cri-o/server/inspect_test.go

Purpose: unit tests for inspect helper functions without the HTTP mux.

Important APIs and functions: tests `getInfo` for storage/cgroup fields and `getContainerInfo` with injected lookup functions. It also validates the sentinel errors `errCtrNotFound`, `errCtrStateNil`, and `errSandboxNotFound`.

Control flow: builds synthetic `oci.Container` objects with image references, labels, annotations, mount/log paths, state timestamps, and sandbox IDs; then calls `getContainerInfo` and compares projected fields.

State and persistence: test state is entirely in memory. The tests avoid the real container server by injecting `getContainerFunc`, `getInfraContainerFunc`, and `getSandboxFunc`.

Dependencies and integration: uses CRI-O `oci`, `sandbox`, storage image reference parsing, Kubernetes CRI types, runtime-spec state, and default config setup.

Risks: tests verify regular container projection but do not cover infra-container PID fallback, nil image name handling, host-network pointer semantics, or HTTP serialization.

Test signals: strong coverage for normal field mapping and the three main failure branches in `getContainerInfo`; basic coverage for `getInfo` cgroup/storage projection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/label_linux.go -->
# sources/cloud-native/cri-o/server/label_linux.go

Purpose: Linux SELinux relabel helper for paths used by volumes and mounts.

Important APIs and functions: `securityLabel(path, secLabel, shared, maybeRelabel)` optionally canonicalizes the desired label and skips relabel when the current top-level file label already matches, then calls `label.Relabel`.

Control flow: when `maybeRelabel` is true, the function tries to canonicalize and compare labels; failures are logged but do not stop relabel. `label.Relabel` errors are returned unless the platform reports `ENOTSUP`.

State and persistence: mutates filesystem SELinux labels recursively or shared according to the caller's `shared` flag. It reads current labels before deciding to skip.

Dependencies and integration: uses opencontainers SELinux APIs and Linux `unix.ENOTSUP`. Called by container/sandbox volume setup paths that need process and mount labels applied.

Risks: skip optimization only checks the top-level path, so callers must ensure that is enough for their relabel semantics. Logging canonicalization failures while continuing can hide malformed labels until `Relabel`.

Test signals: no direct test in this subset; behavior is likely exercised indirectly through container/sandbox mount setup tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/label_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/label_unsupported.go -->
# sources/cloud-native/cri-o/server/label_unsupported.go

Purpose: non-Linux implementation of `securityLabel` where SELinux relabeling is unsupported or irrelevant.

Important APIs and functions: `securityLabel` accepts the same signature as the Linux implementation and returns nil.

Control flow: no validation, label lookup, or filesystem mutation occurs.

State and persistence: none.

Dependencies and integration: provides build-tag compatibility for server code that calls `securityLabel` on all platforms.

Risks: callers expecting enforcement should be aware that non-Linux platforms silently skip label application.

Test signals: no direct test; compile-time platform coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/label_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/listen_unix.go -->
# sources/cloud-native/cri-o/server/listen_unix.go

Purpose: non-Windows listener wrapper for CRI-O server sockets.

Important APIs and functions: `Listen(network, address)` directly delegates to `net.Listen`.

Control flow: no socket cleanup or address translation is performed here.

State and persistence: creates operating-system listeners, including Unix domain sockets when requested.

Dependencies and integration: used by server startup code that expects a platform-specific listener abstraction.

Risks: stale Unix socket cleanup must happen before calling this function; it will fail if the address is already bound.

Test signals: `listen_unix_test.go` confirms successful Unix socket bind and failure on a second bind to the same path.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/listen_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/listen_unix_test.go -->
# sources/cloud-native/cri-o/server/listen_unix_test.go

Purpose: Ginkgo tests for the non-Windows `Listen` wrapper.

Important APIs and functions: calls `server.Listen("unix", "address")` and asserts listener presence or bind error.

Control flow: first test creates a Unix socket and removes the path after the test. Second test binds once, then attempts a second bind to the same path.

State and persistence: creates a local Unix socket file named `address` in the test working directory and removes it with `defer os.Remove`.

Dependencies and integration: uses Ginkgo/Gomega and the public `server.Listen` wrapper.

Risks: the hard-coded relative socket path can collide with leftover files if cleanup fails, but the test deliberately exercises that behavior.

Test signals: validates successful bind and duplicate-bind error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/listen_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/listen_windows.go -->
# sources/cloud-native/cri-o/server/listen_windows.go

Purpose: Windows listener wrapper that maps CRI-O's Unix-style listener request to Windows named pipes.

Important APIs and functions: `Listen(network, address)` calls `winio.ListenPipe` when `network == "unix"`; otherwise it delegates to `net.Listen`.

Control flow: simple network switch with no cleanup or validation.

State and persistence: creates Windows named pipe listeners or normal network listeners.

Dependencies and integration: depends on `github.com/Microsoft/go-winio`; keeps the public `Listen` API consistent across platforms.

Risks: callers using `"unix"` on Windows get named-pipe semantics, so permissions and address syntax differ from Unix sockets.

Test signals: no Windows-specific tests in this subset; compile and platform CI are the likely guard.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/listen_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/masked_paths.go -->
# sources/cloud-native/cri-o/server/masked_paths.go

Purpose: constructs the default masked path list for Linux containers and appends caller-provided additions.

Important APIs and functions: `appendDefaultMaskedPaths` concatenates `defaultLinuxMaskedPaths()` with additional paths, sorts, and compacts duplicates. `defaultLinuxMaskedPaths` is a `sync.OnceValue` combining common defaults with CRI-O-specific `/proc/asound` and `/proc/interrupts`.

Control flow: the default list is computed once per process, then each append call sorts and deduplicates the combined result.

State and persistence: maintains process-local cached default masked paths; no disk persistence.

Dependencies and integration: depends on `go.podman.io/common/pkg/config.DefaultMaskedPaths` and Go slices/sync helpers. Used when generating OCI specs for masked kernel/proc paths.

Risks: because output is sorted, caller-supplied ordering is not preserved. `sync.OnceValue` means changes to external defaults after first call will not be observed.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/masked_paths.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/metric_descriptors_list.go -->
# sources/cloud-native/cri-o/server/metric_descriptors_list.go

Purpose: implements CRI `ListMetricDescriptors` by projecting configured pod metric descriptors.

Important APIs and functions: `ListMetricDescriptors` calls `s.config.EnabledPodMetrics()`, then `s.PopulateMetricDescriptors`, flattens the returned map values, and returns `types.ListMetricDescriptorsResponse`.

Control flow: counts total descriptors for capacity, appends all descriptor slices without sorting, and returns them.

State and persistence: read-only over server config and descriptor generation.

Dependencies and integration: integrates Kubernetes CRI runtime metric descriptors with CRI-O's internal metric descriptor population helpers.

Risks: response order follows map iteration for descriptor groups, so callers should not depend on deterministic ordering unless `PopulateMetricDescriptors` returns stable map behavior elsewhere.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/metric_descriptors_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/metrics/collectors/collectors.go -->
# sources/cloud-native/cri-o/server/metrics/collectors/collectors.go

Purpose: defines the set of Prometheus collector identifiers and helpers for normalizing configured metric collector names.

Important APIs and functions: `Collector`, `Collectors`, constants for every CRI-O metric collector, `FromSlice`, `ToSlice`, `All`, `Contains`, `Stripped`, and `String`.

Control flow: collector names can arrive with `container_runtime_crio_`, `crio_`, or no prefix; `Stripped` removes recognized prefixes and all comparisons use stripped names.

State and persistence: no state; all helpers are deterministic pure transformations.

Dependencies and integration: consumed by `metrics.go` to decide which Prometheus collectors to register, and by config parsing to support prefixed and unprefixed names.

Risks: prefix stripping is broad and may make two differently prefixed strings equivalent. Adding a new metric requires updating the constants and `All()` list.

Test signals: `collectors_test.go` covers prefix stripping, `FromSlice`, `ToSlice`, and `Contains` behavior across prefixed and unprefixed variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/metrics/collectors/collectors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/metrics/collectors/collectors_test.go -->
# sources/cloud-native/cri-o/server/metrics/collectors/collectors_test.go

Purpose: Ginkgo suite for collector-name normalization helpers.

Important APIs and functions: `TestCollectors`, suite setup/teardown with `TestFramework`, and specs for `Stripped`, `FromSlice`, and `ToSlice`.

Control flow: creates sample names with full, CRI-O-only, and no prefixes; asserts stripped output and containment semantics.

State and persistence: uses framework global state only; no external metrics registry is mutated by these tests.

Dependencies and integration: Ginkgo/Gomega, CRI-O test framework, and the collectors package under test.

Risks: does not assert `All()` contents or every real collector constant, so additions can miss test coverage.

Test signals: good focused coverage for the name-normalization contract used by metrics configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/metrics/collectors/collectors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/metrics/metrics.go -->
# sources/cloud-native/cri-o/server/metrics/metrics.go

Purpose: defines CRI-O's Prometheus metrics singleton, collector registration, metric mutation helpers, and HTTP/HTTPS/unix-socket serving.

Important APIs and functions: `New`, `Instance`, `Start`, `createEndpoint`, `startEndpoint`, `SinceInMicroseconds`, `SinceInSeconds`, `GetSizeBucket`, and many `Metric...` mutators for operations, image pulls, OOM, seccomp notifier, resource stages, monitor exits, and default runtime.

Control flow: `New` builds all Prometheus collectors and stores them in the package singleton. `Start` validates configs, creates a `/metrics` mux, starts TCP and optional Unix endpoints, and removes unused sockets first. `createEndpoint` registers only configured collectors. `startEndpoint` launches a goroutine serving HTTP or TLS and shuts down when the shared stop channel closes.

State and persistence: process-global `instance` holds collector objects. Prometheus default registry is mutated by `prometheus.Register`; failed duplicate registration aborts endpoint creation. Metrics values are in-memory counters/gauges/summaries. TLS cert generation may create or update cert/key files.

Dependencies and integration: uses Prometheus client libraries, CRI-O config TLS settings, cert reloader, process defunct counter, storage image references, and collector identifiers.

Risks: singleton/global Prometheus registry behavior can create duplicate-registration problems in repeated tests or multiple server instances. Some metric methods ignore unused parameters (`image`, `name`) and only increment aggregate counters. The unix socket endpoint uses the same handler and stop channel as TCP. TLS startup fatal-logs from the goroutine on cert errors.

Test signals: `metrics_test.go` covers only timing helper behavior. Runtime integration in `server.go` starts metrics when enabled, but collector registration and endpoint lifecycle have limited direct coverage in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/metrics/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/metrics/metrics_test.go -->
# sources/cloud-native/cri-o/server/metrics/metrics_test.go

Purpose: Ginkgo suite for small metrics helper behavior.

Important APIs and functions: `TestMetrics` registers the suite, framework setup/teardown, and specs for `metrics.SinceInMicroseconds`.

Control flow: compares elapsed microseconds for a time one millisecond in the past and for `time.Now()`.

State and persistence: no metrics registry or server endpoint state is created by these tests.

Dependencies and integration: Ginkgo/Gomega, CRI-O test framework, Go time package, metrics package.

Risks: test coverage is narrow and does not exercise metric registration, endpoint startup, TLS, unix sockets, or mutator label behavior.

Test signals: confirms the helper returns non-zero for elapsed time and zero for immediate timestamps at microsecond resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/metrics/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/naming.go -->
# sources/cloud-native/cri-o/server/naming.go

Purpose: creates and reserves Kubernetes-style infra container names for pod sandboxes.

Important APIs and functions: `makeSandboxContainerName` joins `k8s`, `POD`, pod name, namespace, UID, and attempt with underscores. `ReserveSandboxContainerIDAndName` validates config/metadata, generates a non-cryptographic storage ID, and reserves the generated name through `ReserveContainerName`.

Control flow: validation happens before ID generation; reservation errors propagate to the caller.

State and persistence: mutates the server's container-name reservation index. The generated ID is used as the reservation owner.

Dependencies and integration: depends on Kubernetes CRI sandbox metadata, CRI-O `oci.InfraContainerName`, and storage `stringid.GenerateNonCryptoID`. Called during `RunPodSandbox` before storage creation.

Risks: duplicate metadata fields produce duplicate names and reservation failure; callers must release reserved names on later sandbox-creation failure.

Test signals: `naming_test.go` covers successful reservation, nil config, missing metadata, and duplicate-name reservation failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/naming.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/naming_test.go -->
# sources/cloud-native/cri-o/server/naming_test.go

Purpose: Ginkgo tests for sandbox infra container name reservation.

Important APIs and functions: exercises `sut.ReserveSandboxContainerIDAndName` with valid metadata, nil config, missing metadata, and duplicate metadata.

Control flow: the duplicate test reserves once, then retries with the same metadata and expects an error.

State and persistence: mutates the in-memory name reservation store in the test server and cleans it up via framework teardown.

Dependencies and integration: CRI-O server test framework, Ginkgo/Gomega, and CRI sandbox metadata types.

Risks: does not assert exact generated name format, only that a name is non-empty or reservation fails.

Test signals: protects validation and duplicate-reservation behavior used by sandbox creation cleanup logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/naming_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/nri-api.go -->
# sources/cloud-native/cri-o/server/nri-api.go

Purpose: adapts CRI-O pod/container lifecycle to containerd NRI and exposes CRI-O objects through the NRI domain interface.

Important APIs and functions: `nriAPI.start`, lifecycle hooks `runPodSandbox`, `updatePodSandbox`, `stopPodSandbox`, `removePodSandbox`, `createContainer`, `postCreateContainer`, `startContainer`, `postStartContainer`, `updateContainer`, `postUpdateContainer`, `stopContainer`, `removeContainer`, `undoCreateContainer`; upward interface methods `GetName`, `ListPodSandboxes`, `ListContainers`, `GetPodSandbox`, `GetContainer`, `UpdateContainer`, and `EvictContainer`; wrappers `criPodSandbox` and `criContainer`; converters `fromCRILinuxResources` and `toCRIResources`.

Control flow: all downward hooks no-op when NRI is disabled. Pod start undo calls NRI stop/remove if run fails. Container create asks NRI for an adjustment, then applies it through runtime-tools with annotation filtering, resource checks, BlockIO/RDT resolvers, and CDI device injection. Upward updates resolve the target container, ignore missing containers, skip non-running/non-created containers, and call runtime update before updating CRI-O's resource cache. Eviction resolves and stops the target container.

State and persistence: mutates OCI specs during NRI create adjustments, updates container runtime resources, may inject CDI devices, and can stop containers on eviction. Wrapper getters copy labels/annotations where needed to avoid exposing mutable pod maps directly.

Dependencies and integration: deep integration with containerd NRI API, runtime-tools generate wrapper, CDI, goresctrl BlockIO, CRI-O cgroup/runtime/node feature checks, RDT, sandbox/container stores, CRI resource types, and OCI runtime specs.

Risks: many upward paths intentionally ignore missing objects, which is safe for stale NRI requests but can hide lookup failures. `GetID` and `GetPodSandboxID` depend on annotations in the OCI spec. Resource conversion must stay aligned with CRI/NRI semantics; unsupported cgroup features are stripped during adjustment. CDI refresh failures are logged but not fatal before injection.

Test signals: no direct tests in this subset. Lifecycle integration is indirectly exercised by sandbox/container creation and update paths when NRI is enabled or mocked.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/nri-api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/rootless_linux.go -->
# sources/cloud-native/cri-o/server/rootless_linux.go

Purpose: adjusts generated OCI specs for rootless CRI-O execution on Linux.

Important APIs and functions: `hasNetworkNamespace`, `makeOCIConfigurationRootless`, and `getAvailableV2Controllers`.

Control flow: removes device cgroup rules, then prunes memory/CPU/cpuset/pids/io/rdma/hugetlb resource settings when cgroup v2 delegation lacks the required controller. It clears OOM score and AppArmor profile, removes `gid=` mount options, bind-mounts host `/sys` read-only when no network namespace is present, and clears Linux cgroups path.

State and persistence: mutates the in-memory OCI generator spec. Reads `/proc/self/cgroup` and `/sys/fs/cgroup/.../cgroup.controllers` to detect delegated controllers.

Dependencies and integration: uses opencontainers cgroups/runtime-spec/generate, CRI-O cgroup manager paths, and rootless environment handling in sandbox creation.

Risks: missing or unreadable cgroup controller files cause nil controller maps and broad resource pruning. The hugetlb warning text says RDMA limit, likely a copy-paste issue. Rootless behavior depends on accurate namespace detection.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/rootless_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/rootless_unsupported.go -->
# sources/cloud-native/cri-o/server/rootless_unsupported.go

Purpose: non-Linux no-op implementation for rootless OCI spec adjustment.

Important APIs and functions: `makeOCIConfigurationRootless(g *generate.Generator)` exists for cross-platform compilation and does nothing.

Control flow: no mutations.

State and persistence: none.

Dependencies and integration: keeps platform-specific sandbox creation code buildable on non-Linux targets.

Risks: non-Linux rootless behavior is not handled here.

Test signals: compile-time coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/rootless_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/runtime_config.go -->
# sources/cloud-native/cri-o/server/runtime_config.go

Purpose: implements CRI `RuntimeConfig`, currently reporting Linux cgroup driver configuration.

Important APIs and functions: `RuntimeConfig` returns `types.RuntimeConfigResponse` with `Linux.CgroupDriver`. `getCgroupDriver` maps CRI-O's cgroup manager to `SYSTEMD` or `CGROUPFS`.

Control flow: direct projection from config; request content is unused.

State and persistence: read-only over server config.

Dependencies and integration: integrates with Kubernetes CRI runtime configuration API and CRI-O cgroup manager abstraction.

Risks: only cgroup driver is reported; future CRI runtime config fields require extending this response.

Test signals: no direct test in this subset for `RuntimeConfig`; cgroup driver mapping is indirectly related to inspect info tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/runtime_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/runtime_status.go -->
# sources/cloud-native/cri-o/server/runtime_status.go

Purpose: implements CRI `Status` and verbose runtime info reporting.

Important APIs and functions: `Status` builds runtime and network readiness conditions, runtime feature flags, runtime handler feature entries, and optional verbose info. `createRuntimeInfo` serializes pause image and CRI-O runtime config.

Control flow: runtime readiness is always true in this file; network readiness is false with reason `NetworkPluginNotReady` if CNI plugin readiness reports an error. The runtime handler list includes every configured runtime plus an empty-name alias for the default runtime.

State and persistence: read-only over CNI readiness, configured runtimes, pause image, and runtime config.

Dependencies and integration: Kubernetes CRI runtime status API, CNI plugin readiness, runtime handler feature discovery for recursive read-only mounts and ID-mapped user namespaces.

Risks: network condition is only as accurate as `CNIPluginReadyOrError`. Runtime handler ordering follows map iteration over configured runtimes.

Test signals: `runtime_status_test.go` covers successful status, condition count/status in the default test setup, and verbose info presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/runtime_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/runtime_status_test.go -->
# sources/cloud-native/cri-o/server/runtime_status_test.go

Purpose: Ginkgo tests for CRI runtime status response behavior.

Important APIs and functions: calls `sut.Status` with normal and verbose requests.

Control flow: setup initializes the test server, then each spec asserts no error and response structure.

State and persistence: read-only over the test server configuration; no external runtime state changes.

Dependencies and integration: Ginkgo/Gomega, CRI runtime status types, CRI-O test framework.

Risks: the case named for CNI plugin status errors does not visibly configure an erroring CNI plugin in the file, so it may duplicate the happy path through fixture defaults.

Test signals: verifies two conditions are returned and verbose `Info` is populated.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/runtime_status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/safemount_freebsd.go -->
# sources/cloud-native/cri-o/server/safemount_freebsd.go

Purpose: FreeBSD placeholder for secure subpath mounting.

Important APIs and functions: empty `safeMountInfo`, no-op `Close`, and `safeMountSubPath` returning an empty info object with nil error.

Control flow: all inputs are ignored.

State and persistence: no file descriptors, mounts, or temporary paths are created.

Dependencies and integration: provides the same API as Linux for container mount setup.

Risks: callers receive apparent success without an actual bind mount on FreeBSD; platform code must not depend on Linux subpath behavior there.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/safemount_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/safemount_linux.go -->
# sources/cloud-native/cri-o/server/safemount_linux.go

Purpose: securely bind-mounts a subpath inside a volume while preventing path traversal or symlink escape.

Important APIs and functions: `safeMountInfo.Close` unmounts and closes the held file; `safeMountSubPath(mountPoint, subpath, runDir)` opens the subpath inside the mount root via `pathrs.OpenInRoot`, binds `/proc/self/fd/<fd>` to a temporary directory or file, and returns cleanup state.

Control flow: after secure open, the function stats the fd path, rejects symlinks, creates a temp mount target matching directory/file type, then performs `MS_BIND|MS_REC`.

State and persistence: opens a file descriptor that pins the resolved path, creates a temp file/directory under `runDir`, creates a bind mount, and cleans both mount and fd on `Close`.

Dependencies and integration: uses pathrs secure join/open primitives and Linux mount syscalls. Intended for Kubernetes subPath-style volume mount handling.

Risks: if bind mount succeeds but later caller forgets `Close`, temp mounts and fds can leak. If temp file creation succeeds and mount fails, the temp path is not removed here. Symlink rejection is explicit for the final target, complementing root-constrained open.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/safemount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_list.go -->
# sources/cloud-native/cri-o/server/sandbox_list.go

Purpose: implements CRI pod sandbox listing and streaming with filter support.

Important APIs and functions: `ListPodSandbox`, `StreamPodSandboxes`, `listPodSandboxes`, `filterSandboxList`, and `filterSandbox`.

Control flow: list filters in-memory sandboxes by optional ID, created-state, CRI state, and labels; then projects each sandbox's CRI object. Streaming chunks results by `streamChunkSize`.

State and persistence: read-only over sandbox store and pod ID index.

Dependencies and integration: Kubernetes CRI pod sandbox filters, Kubernetes field selectors for label matching, CRI-O sandbox store.

Risks: filtering is applied in both sandbox-object and CRI-object layers, which is redundant but defensive. Missing filtered IDs return an empty list instead of errors per CRI expectations.

Test signals: `sandbox_list_test.go` covers success, created-only filtering, listing without infra container, ID/state/label filters, and missing filtered IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_list_test.go -->
# sources/cloud-native/cri-o/server/sandbox_list_test.go

Purpose: Ginkgo tests for `ListPodSandbox` filtering and created-state behavior.

Important APIs and functions: exercises `sut.ListPodSandbox`, sandbox store mutation, `LoadSandbox`, and PodIDIndex-driven filtering.

Control flow: prepares sandboxes directly or through mocked manifest/state loading, then asserts returned item counts for unfiltered and filtered calls.

State and persistence: mostly in-memory, with helper-created dummy state for loaded sandbox tests.

Dependencies and integration: CRI-O test framework, OCI container state, runtime-spec status, CRI filters.

Risks: does not test streaming chunk behavior.

Test signals: strong coverage for the list path's key CRI semantics: skip uncreated sandboxes, allow created sandboxes without infra container, and treat missing filter IDs as empty results.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_metrics_list.go -->
# sources/cloud-native/cri-o/server/sandbox_metrics_list.go

Purpose: implements CRI pod sandbox metrics listing and streaming.

Important APIs and functions: `ListPodSandboxMetrics`, `StreamPodSandboxMetrics`, and `listPodSandboxMetrics`.

Control flow: fetches all sandboxes, converts them through `MetricsForPodSandboxList`, then appends metrics with a non-nil `GetMetric()` into the response. Streaming chunks by `streamChunkSize`.

State and persistence: read-only over sandbox store and metrics providers.

Dependencies and integration: CRI pod sandbox/container metrics APIs and CRI-O metrics projection helpers.

Risks: the `else` branch dereferences `metrics.GetMetric()` after checking that it is nil, which appears unreachable without panic if executed. The function also ignores request filters because `ListPodSandboxMetricsRequest` carries no filter in this implementation.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_metrics_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_network.go -->
# sources/cloud-native/cri-o/server/sandbox_network.go

Purpose: manages CNI network setup, status restoration, teardown, garbage collection, and CNI readiness waiting for pod sandboxes.

Important APIs and functions: `networkStart`, `getSandboxIPs`, `networkStop`, `cleanupCNIResultFiles`, `newPodNetwork`, `networkGC`, and `waitForCNIPlugin`.

Control flow: `networkStart` skips host network, builds `ocicni.PodNetwork`, runs CNI setup with a bounded context, fetches network status, records IPs, and adds hostport mappings once per IP family. A deferred cleanup calls `networkStop` if setup partially succeeds then later fails. `networkStop` removes hostports, builds the pod network, validates/may remove the netns, always attempts CNI teardown to avoid IP leaks, cleans stale CNI result files on failure, and marks network stopped even on many teardown failures to prevent retry loops.

State and persistence: mutates CNI state, hostport rules, sandbox network-stopped state, sandbox IPs in callers, netns filesystem paths, and `/var/lib/cni/results` cache files. `networkGC` delegates stale network cleanup to the configured CNI plugin.

Dependencies and integration: CNI current result parsing, ocicni, Kubernetes bandwidth annotations, hostport manager, sandbox annotations/cgroup parent/netns, platform-specific netns validation/cleanup, and metrics latency updates.

Risks: `cleanupCNIResultFiles` removes any cache file whose name contains the container ID, which is practical but string-based. Marking network stopped after teardown failure avoids loops but may leave external CNI state requiring GC. Startup timeout is based on the request deadline plus five minutes, which can still be long.

Test signals: no direct network tests in this subset; stop/remove/sandbox creation tests exercise some paths indirectly through mocks.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_network_freebsd.go -->
# sources/cloud-native/cri-o/server/sandbox_network_freebsd.go

Purpose: FreeBSD implementation stubs for Linux network namespace validation and cleanup hooks.

Important APIs and functions: `validateNetworkNamespace` returns nil; `cleanupNetns` logs a debug no-op.

Control flow: no validation or deletion is performed.

State and persistence: none.

Dependencies and integration: supports shared `networkStop` code on FreeBSD, where Linux netns files are not meaningful.

Risks: invalid/missing netns handling in `networkStop` is effectively bypassed on FreeBSD.

Test signals: compile-time/platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_network_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_network_linux.go -->
# sources/cloud-native/cri-o/server/sandbox_network_linux.go

Purpose: Linux-specific validation and cleanup of network namespace paths.

Important APIs and functions: `validateNetworkNamespace` opens the namespace with CNI `ns.GetNS` and closes it; `cleanupNetns` removes the path via `os.RemoveAll`.

Control flow: validation converts `GetNS` failures into contextual errors. Cleanup logs success or warning.

State and persistence: reads netns path validity and may delete netns filesystem entries.

Dependencies and integration: used by `networkStop` before/after CNI teardown; depends on containernetworking plugins `ns` package.

Risks: `RemoveAll` on a bad netns path is powerful, so path provenance from sandbox state must be trusted.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_network_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_network_unsupported.go -->
# sources/cloud-native/cri-o/server/sandbox_network_unsupported.go

Purpose: non-Linux/non-FreeBSD no-op network namespace hooks.

Important APIs and functions: `validateNetworkNamespace` returns nil and `cleanupNetns` logs a debug no-op.

Control flow: no platform-specific validation or cleanup occurs.

State and persistence: none.

Dependencies and integration: build-tag compatibility for shared network teardown logic.

Risks: unsupported platforms do not protect against invalid netns state here.

Test signals: compile-time coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_network_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_remove.go -->
# sources/cloud-native/cri-o/server/sandbox_remove.go

Purpose: implements CRI `RemovePodSandbox` and internal sandbox removal cleanup.

Important APIs and functions: `RemovePodSandbox` handles CRI lookup/idempotency semantics; `removePodSandbox` deletes containers, unmounts SHM, removes infra container, cleans spoofed cgroup, stops network, removes namespaces, releases names, deletes sandbox/index entries, emits deletion event, and notifies NRI.

Control flow: missing sandboxes return empty success except empty ID and not-created sandbox errors. Internal removal processes workload containers first, then infra, then network/namespaces/indexes.

State and persistence: mutates runtime/storage container state, SHM mounts, network/CNI state, namespace resources, pod name reservation, sandbox store, pod ID index, CRI event channel, NRI state, and spoofed sandbox cgroups.

Dependencies and integration: depends on container removal helpers, sandbox state, cgroup manager, network teardown, NRI, CRI events, and indexes.

Risks: removal order is sensitive: network stop happens after container deletion and SHM/infra cleanup. Failures abort subsequent cleanup, so callers may need retries. NRI removal failure is logged but does not fail removal.

Test signals: `sandbox_remove_test.go` covers not-created sandbox error and empty-ID error through stop/remove entry points, but not full successful cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_remove_test.go -->
# sources/cloud-native/cri-o/server/sandbox_remove_test.go

Purpose: Ginkgo tests for sandbox removal error behavior.

Important APIs and functions: exercises `sut.RemovePodSandbox` on an uncreated sandbox and `sut.StopPodSandbox` with an empty ID.

Control flow: adds a sandbox and ID index entry without marking it created, then expects removal to fail.

State and persistence: in-memory sandbox and PodIDIndex changes only.

Dependencies and integration: CRI-O test framework and CRI stop/remove request types.

Risks: test name includes remove, but one case calls stop for empty ID; successful removal cleanup is not covered here.

Test signals: protects error semantics for not-created sandboxes and empty IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run.go -->
# sources/cloud-native/cri-o/server/sandbox_run.go

Purpose: shared, platform-independent helpers for pod sandbox creation.

Important APIs and functions: constants `PodInfraOOMAdj` and `PodInfraCPUshares`; `privilegedSandbox`; `runtimeHandler`; `RunPodSandbox`; `convertPortMappings`; `getHostname`; `setPodSandboxMountLabel`.

Control flow: `RunPodSandbox` dispatches to platform-specific `runPodSandbox`. `privilegedSandbox` derives elevated sandbox status from privileged flag or host network/pid/ipc namespace modes. `runtimeHandler` validates non-empty handlers. `convertPortMappings` drops entries without host ports. `getHostname` uses host hostname for host-network pods or sandbox ID prefix for pod-network pods when no hostname is provided.

State and persistence: `setPodSandboxMountLabel` reads and writes storage runtime metadata to persist the sandbox mount label.

Dependencies and integration: CRI runtime types, Kubernetes port protocols, hostport manager, storage metadata, runtime handler validation.

Risks: hostname derivation assumes sandbox IDs are at least 12 characters. Privileged classification treats any host namespace mode as privileged for runtime/storage behavior.

Test signals: sandbox run tests exercise dispatch and several validation/failure paths; platform-specific creation has much broader behavior than this shared file.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run_freebsd.go -->
# sources/cloud-native/cri-o/server/sandbox_run_freebsd.go

Purpose: FreeBSD implementation of pod sandbox creation, adapted to jails and reduced Linux feature support.

Important APIs and functions: `getSandboxIDMappings` returns nil, `runPodSandbox` performs full sandbox setup, `configureGeneratorForSysctls`, and `configureGeneratorForSandboxNamespaces`.

Control flow: similar high-level flow to Linux: build sandbox, reserve pod/container names, wait for CNI, validate runtime handler, filter annotations, create storage sandbox, build OCI spec annotations, add indexes, create namespaces, start storage, configure infra resources, save config, create/start infra container, run CNI, call NRI, and mark created. It uses a `ResourceCleaner` for failure cleanup except context-error cases.

State and persistence: mutates name reservations, storage containers, log directories, metadata labels/annotations, sandbox store, ID indexes, namespace manager state, storage mounts, generated config files, runtime container state, CNI state/IP annotations, resource store, and NRI state.

Dependencies and integration: storage runtime server, namespace manager with FreeBSD jail/VNET annotations, CNI, runtime handler hooks, CRI-O sandbox builder, OCI runtime, cgroup manager, resource store, NRI.

Risks: FreeBSD implementation duplicates significant Linux logic and can drift. Some Linux concepts are stubbed or simplified: no user namespace mappings, hostPID forced true, hostIPC unsupported, SELinux labels disabled when hostPID/IPC. Context-error cleanup behavior differs from Linux by skipping cleanup when `isContextError(retErr)`.

Test signals: no FreeBSD-specific tests in this subset; generic sandbox run tests may not cover this file on Linux CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run_linux.go -->
# sources/cloud-native/cri-o/server/sandbox_run_linux.go

Purpose: Linux implementation of pod sandbox creation, including user namespace mapping, OCI spec assembly, namespace/CNI setup, infra container lifecycle, resource cleanup, and NRI notification.

Important APIs and functions: `configureSandboxIDMappings`, `configureAutoUserNS`, `configurePrivateUserNS`, mapping helpers, `getSandboxIDMappings`, `runPodSandbox`, `prepareSecurityContext`, `finalizeSandboxCreation`, `prepareKubeAnnotations`, `reservePodNameOrGetExisting`, `populateSandboxLabels`, `configureGeneratorForSysctls`, `configurePingGroupRangeGivenIDMappings`, `configureGeneratorForSandboxNamespaces`, `setupSandboxShm`, `setupSandboxAnnotations`, `setupSandboxSeccomp`, `setupSandboxPortMappings`, `setupSandboxCgroupPath`, `setupSandboxIDMappings`, `setupSandboxResources`, `setupHostnameFile`, `setupUserNamespaceMounts`, `setupInfraContainer`, `configureAndSaveInfraContainer`, `createAndStartInfraContainer`, `setupSandboxNetwork`, `prepareSandboxMetadataAndLabels`, `setupSandboxStorage`, and `finalizeSandboxSpec`.

Control flow: creation is staged and cleanup-aware. It builds and validates sandbox config, generates name/ID, reserves pod and container names, waits for CNI when needed, validates runtime handler, merges default and pod annotations, computes user namespace mappings, creates storage sandbox, prepares log dirs and infra spec, stores SELinux labels, configures SHM/log links/indexes/hostname/annotations/ports/cgroups/resources/seccomp, registers the sandbox, creates managed namespaces, starts CNI, starts storage, finalizes mounts and rootless adjustments, creates/saves/starts infra container, annotates IPs, calls NRI, then marks the sandbox created unless the request context ended and progress must be stored for later cleanup/reuse.

State and persistence: mutates almost every sandbox creation surface: name indexes, resource store stage/progress, storage runtime metadata, log directories, SHM tmpfs, log-link mounts, container/pod ID indexes, sandbox store, OCI config files in storage and run dirs, namespace resources, CNI state, hostport rules, storage mounts, cgroups, runtime container state files, annotations, sandbox IPs, CRI event channel, and NRI state.

Dependencies and integration: CRI-O config, storage, sandbox builder, namespace manager, OCI generator/runtime, CNI/hostport, SELinux, seccomp, runtime handler hooks, cgroup manager, linklogs, idtools/unshare, Kubernetes annotations, NRI, metrics, and resource store.

Risks: this file has high cyclomatic complexity and many cleanup-order dependencies. User namespace mapping rejects unsafe mappings below configured minimums but must stay aligned with Kubernetes userns semantics. Context cancellation stores partially-created resources instead of cleanup, so resource-store correctness is critical. Rootless and dropped-infra branches materially change spec/cgroup/event behavior. Some cleanup functions run with background context to avoid expired request deadlines.

Test signals: `sandbox_run_test.go` covers several validation and early failure paths, including metadata validation, relative log path rejection, and storage/runtime failure cleanup. Many deep branches (userns modes, seccomp, CNI, NRI, rootless, dropped infra) are not directly covered in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run_test.go -->
# sources/cloud-native/cri-o/server/sandbox_run_test.go

Purpose: Ginkgo tests for `RunPodSandbox` validation and selected failure cleanup behavior.

Important APIs and functions: calls `sut.RunPodSandbox` with mocked storage runtime expectations and CRI sandbox configs.

Control flow: tests container creation failure after storage setup, nil/missing metadata validation, missing namespace validation, and relative log path rejection.

State and persistence: uses mocks for storage runtime calls, temporary paths, server name/index state, and test fixture setup. Some tests skip rootless where root is required.

Dependencies and integration: gomock storage runtime server, CRI-O test framework, storage container info, image-spec config, CRI sandbox types.

Risks: the file explicitly notes the internal function has high cyclomatic complexity and should be refactored for more isolated testing. It covers early errors more than successful sandbox creation.

Test signals: protects critical validation gates and confirms cleanup calls such as storage deletion are expected in early failure scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run_unsupported.go -->
# sources/cloud-native/cri-o/server/sandbox_run_unsupported.go

Purpose: unsupported-platform implementation for sandbox creation and ID mapping lookup.

Important APIs and functions: `runPodSandbox` and `getSandboxIDMappings` both return `"unsupported"` errors.

Control flow: no sandbox work is attempted.

State and persistence: none.

Dependencies and integration: build-tag fallback for platforms other than Linux and FreeBSD.

Risks: CRI runtime service cannot create pod sandboxes on these platforms.

Test signals: compile-time coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_run_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stats.go -->
# sources/cloud-native/cri-o/server/sandbox_stats.go

Purpose: implements CRI `PodSandboxStats` for a single sandbox.

Important APIs and functions: `PodSandboxStats` resolves the sandbox through `getPodSandboxFromRequest` and returns `s.StatsForSandbox(sb)`.

Control flow: lookup error propagates; otherwise response construction is direct.

State and persistence: read-only over sandbox store and stats providers.

Dependencies and integration: CRI stats API and CRI-O stats aggregation helpers.

Risks: error semantics mirror `getPodSandboxFromRequest`, so empty IDs and not-created sandboxes are errors.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stats_list.go -->
# sources/cloud-native/cri-o/server/sandbox_stats_list.go

Purpose: implements CRI pod sandbox stats listing and streaming.

Important APIs and functions: `ListPodSandboxStats`, `StreamPodSandboxStats`, and `listPodSandboxStats`.

Control flow: optional stats filter is converted to a normal pod sandbox filter for ID/label matching, then `StatsForSandboxes` is called. Streaming chunks by `streamChunkSize`.

State and persistence: read-only over sandbox store and stats helpers.

Dependencies and integration: CRI stats list/stream APIs, sandbox filtering from `sandbox_list.go`, and CRI-O stats aggregation.

Risks: stats filter supports ID and labels here, not state; output includes whatever `StatsForSandboxes` returns for matching sandboxes.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stats_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_status.go -->
# sources/cloud-native/cri-o/server/sandbox_status.go

Purpose: implements CRI `PodSandboxStatus`, including network IP projection, namespace options, evented PLEG fields, and verbose runtime spec info.

Important APIs and functions: `PodSandboxStatus`, `toPodIPs`, and `createSandboxInfo`.

Control flow: resolves sandbox or returns gRPC NotFound. Builds status from sandbox state/labels/annotations/metadata and namespace options. If pod events are enabled, attaches timestamp and container statuses. First sandbox IP becomes `Network.Ip`; remaining IPs become `AdditionalIps`. Verbose mode serializes infra container image/pid/spec or only spec for spoofed infra containers.

State and persistence: read-only over sandbox/container state, except container status collection may call other server APIs that refresh or compute state.

Dependencies and integration: CRI status API, evented PLEG support, OCI container spec/state, goccy JSON, gRPC status codes.

Risks: verbose info depends on infra container availability and serializability. Evented PLEG container-status lookup can make status slower and introduce additional errors.

Test signals: `sandbox_status_test.go` covers success, multiple IPs, empty ID error, and verbose info serialization including runtime spec and image.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_status_test.go -->
# sources/cloud-native/cri-o/server/sandbox_status_test.go

Purpose: Ginkgo tests for pod sandbox status response content.

Important APIs and functions: calls `sut.PodSandboxStatus` with normal and verbose requests after preparing test containers/sandboxes.

Control flow: asserts success for a running infra container, checks first/additional IP mapping, expects error for empty sandbox ID, and verifies verbose `info` JSON contains OCI version and image.

State and persistence: in-memory sandbox/container state and spec mutations.

Dependencies and integration: CRI-O test framework, OCI container state/spec, CRI status request types.

Risks: does not cover evented PLEG container-status inclusion or spoofed infra verbose output.

Test signals: strong coverage for common status projection and multi-IP response behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop.go -->
# sources/cloud-native/cri-o/server/sandbox_stop.go

Purpose: implements CRI `StopPodSandbox` wrapper and CRI-specific idempotent lookup behavior.

Important APIs and functions: `StopPodSandbox` resolves the requested sandbox and delegates to platform-specific `stopPodSandbox`.

Control flow: empty ID errors are returned. Not-created sandboxes return a clear error. Missing sandboxes return an empty successful response to satisfy CRI idempotency. Found sandboxes are stopped by platform code.

State and persistence: mostly read-only until delegation; platform implementation mutates runtime/network/sandbox state.

Dependencies and integration: CRI request/response types, sandbox ID lookup, platform-specific stop implementation.

Risks: missing sandbox success can hide unexpected index/store divergence, although it follows CRI expectations.

Test signals: `sandbox_stop_test.go` covers already-stopped behavior, missing sandbox idempotency, and empty ID error.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop_freebsd.go -->
# sources/cloud-native/cri-o/server/sandbox_stop_freebsd.go

Purpose: FreeBSD implementation for stopping a pod sandbox.

Important APIs and functions: `stopPodSandbox` serializes stop operations with the sandbox stop mutex, stops network, stops workload containers in parallel, stops infra, removes namespaces, unmounts SHM, notifies NRI, marks stopped, and emits a stopped event.

Control flow: returns early if already stopped after network cleanup. Splits request timeout between workload containers and infra. Uses `errgroup` for parallel workload container stops and handles unknown/stopped infra errors as non-fatal.

State and persistence: mutates runtime container states, network/CNI state, namespace resources, SHM mounts, NRI state, sandbox stopped flag, and CRI event channel.

Dependencies and integration: storage/OCI errors, stop timeout helper, CRI-O stopContainer, NRI, sandbox managed namespaces.

Risks: similar cleanup-order sensitivity as Linux. Event generation is unconditional on FreeBSD after setting stopped, unlike Linux's spoofed-infra special case.

Test signals: generic stop tests may not execute this file on Linux CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop_linux.go -->
# sources/cloud-native/cri-o/server/sandbox_stop_linux.go

Purpose: Linux implementation for stopping pod sandboxes and cleaning associated resources.

Important APIs and functions: `stopPodSandbox`.

Control flow: locks the sandbox stop mutex, unmounts linked pod logs if configured, tears down network, returns if already stopped, splits timeout between workload containers and infra, stops workload containers in parallel, stops infra, removes managed namespaces, unmounts SHM, notifies NRI, marks stopped, and emits a stopped event for spoofed infra containers where no monitor exit will generate one.

State and persistence: mutates log-link mounts, CNI/hostport state, runtime container states, namespace resources, SHM mounts, NRI state, sandbox stopped flag, and possibly CRI event channel.

Dependencies and integration: linklogs annotations, Kubernetes pod UID label, networkStop, stopContainer, storage/OCI errors, `errgroup`, NRI, evented PLEG.

Risks: network teardown happens before checking `sb.Stopped`, so already-stopped sandboxes can still run network cleanup. Parallel stop failures abort infra cleanup. Timeout partitioning must be kept in sync with CRI request deadline behavior.

Test signals: `sandbox_stop_test.go` covers already-stopped/network-stopped success, missing sandbox idempotency, and empty ID errors; deep parallel stop and log unlink paths are not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop_test.go -->
# sources/cloud-native/cri-o/server/sandbox_stop_test.go

Purpose: Ginkgo tests for pod sandbox stop wrapper behavior.

Important APIs and functions: calls `sut.StopPodSandbox` with a prepared sandbox, invalid ID, and empty request.

Control flow: prepares a created sandbox and marks its network stopped, then verifies stop succeeds. Invalid IDs should succeed idempotently; empty IDs should error.

State and persistence: in-memory sandbox/container setup plus sandbox stopped/network-stopped flags.

Dependencies and integration: CRI-O test framework and CRI stop request types.

Risks: package describe name says `PodSandboxStatus`, likely copy-paste. Does not assert container stop, NRI, namespace, or log cleanup.

Test signals: protects CRI idempotency and empty-ID validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop_unsupported.go -->
# sources/cloud-native/cri-o/server/sandbox_stop_unsupported.go

Purpose: unsupported-platform implementation for pod sandbox stopping.

Important APIs and functions: `stopPodSandbox` returns `"unsupported"`.

Control flow: no stop work is attempted.

State and persistence: none.

Dependencies and integration: build-tag fallback for platforms other than Linux and FreeBSD.

Risks: runtime cannot stop pod sandboxes on unsupported platforms through this implementation.

Test signals: compile-time coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_stop_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_update_resources.go -->
# sources/cloud-native/cri-o/server/sandbox_update_resources.go

Purpose: implements CRI `UpdatePodSandboxResources` by forwarding pod overhead/resource updates to NRI.

Important APIs and functions: `UpdatePodSandboxResources`.

Control flow: resolves sandbox by request ID, returns gRPC NotFound on lookup failure, calls `s.nri.updatePodSandbox` with overhead and resources, then returns an empty success response.

State and persistence: does not directly mutate CRI-O cgroups; any effect depends on NRI plugins and NRI integration.

Dependencies and integration: CRI update sandbox resources API, gRPC status codes, NRI pod update hook.

Risks: with NRI disabled this becomes a successful no-op. Direct CRI-O cgroup resource updates are not performed in this file.

Test signals: `sandbox_update_resources_test.go` covers success for an available sandbox and error for an invalid sandbox.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_update_resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_update_resources_test.go -->
# sources/cloud-native/cri-o/server/sandbox_update_resources_test.go

Purpose: Ginkgo tests for sandbox resource update lookup behavior.

Important APIs and functions: calls `sut.UpdatePodSandboxResources`.

Control flow: adds a container/sandbox for success, then calls the API with that ID; separately calls with invalid ID and expects an error.

State and persistence: in-memory sandbox setup only; NRI is inactive/no-op in normal test setup.

Dependencies and integration: CRI-O test framework and CRI update request types.

Risks: does not verify NRI payload conversion or plugin-side resource mutation.

Test signals: covers API success/no-op and NotFound behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/sandbox_update_resources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/selinux.go -->
# sources/cloud-native/cri-o/server/selinux.go

Purpose: derives alternate SELinux process labels for KVM-isolated and init/systemd-style containers.

Important APIs and functions: `KVMLabel`, `InitLabel`, and `swapSELinuxLabel`.

Control flow: empty input label returns empty output for SELinux-disabled environments. Otherwise it obtains a reference KVM or init container label, releases it, parses both contexts, replaces the destination `type` with the reference label's `type`, and returns the modified context.

State and persistence: no filesystem mutation; interacts with SELinux label allocation/release state through the SELinux library.

Dependencies and integration: used by sandbox/container spec setup when runtime type requires KVM or init labels.

Risks: errors parsing either SELinux context abort label generation. Only the `type` field is swapped; other context fields remain from the original container label.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/selinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/server.go -->
# sources/cloud-native/cri-o/server/server.go

Purpose: defines the central CRI-O `Server` type, streaming service adapter, startup/shutdown lifecycle, restore/wipe behavior, sandbox/container store wrappers, exit monitoring, evented PLEG generation, registry reload watching, and artifact-store access.

Important APIs and functions: `Server`, `StreamService`, pull operation structs, `StopStreamServer`, streaming request helpers, `restore`, `Shutdown`, `getIDMappings`, `New`, `startReloadWatcher`, `useDefaultUmask`, `wipeIfAppropriate`, sandbox/container add/get/remove wrappers, `getPodSandboxFromRequest`, monitor functions, status helper functions, `generateCRIEvent`, `isNotFound`, mirror registry watcher functions, and `ArtifactStore`.

Control flow: `New` validates config, sets system context, prepares dirs, creates the container server, restores IRQ balance config, configures hostport and ID mappings, adjusts rootless env, builds artifact store and `Server`, configures max threads, redirects stdin to `/dev/null`, restores existing pods/containers, optionally wipes stale resources/images, starts streaming server, reload watchers, metrics server, seccomp notifier, NRI, and systemd watchdog. `restore` scans storage metadata, separates pods/containers, loads recoverable objects, deletes broken pods/containers and releases names, runs CNI GC, retries deleted-pod network cleanup asynchronously, and restores sandbox IPs.

State and persistence: owns runtime server state, config copy, stream server, hostport manager, monitors channel, ID mappings, event channel, pull synchronization map, resource store, seccomp notifiers, NRI API, hooks retriever, and artifact store. It mutates storage, indexes, names, network state, image store, clean-shutdown file, fsnotify watchers, metrics server, and event channel. `Shutdown` syncs graph root and optionally writes/syncs clean shutdown marker after storage shutdown.

Dependencies and integration: CRI image/runtime service interfaces, container server library, storage, CNI, hostport, streaming, TLS cert reload, fsnotify, metrics, seccomp, NRI, watchdog, runtime handler hooks, artifact storage, Kubernetes CRI types, system signals, and version wipe logic.

Risks: startup is complex and side-effect heavy; partial failures can delete storage containers or images. `restore` launches asynchronous network cleanup after startup. `generateCRIEvent` has a possible nil-status logging hazard if `getSandboxStatuses` returns error with nil status and the log references `sandboxStatuses.GetMetadata()`. Mirror registry watcher uses debounced events and a buffered channel that could block if reload processing stalls.

Test signals: this subset does not include `server_test.go`; related tests in this subset indirectly use server setup and wrappers. Many startup, restore, watcher, and shutdown paths require broader integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_freebsd.go -->
# sources/cloud-native/cri-o/server/server_freebsd.go

Purpose: FreeBSD implementation of Go runtime thread-limit configuration for CRI-O.

Important APIs and functions: `configureMaxThreads` reads `kern.threads.max_threads_per_proc`, sets Go's max thread limit to 90 percent of that value, and logs the configured value.

Control flow: sysctl read errors are ignored with nil return. Successful reads compute `(value / 100) * 90`, then call `debug.SetMaxThreads`.

State and persistence: mutates the Go runtime's process-wide max thread setting.

Dependencies and integration: called during `New` server initialization on FreeBSD; uses `golang.org/x/sys/unix` sysctl and `runtime/debug`.

Risks: integer math truncates before multiplying by 90, so small values lose precision. Ignoring sysctl errors favors startup resilience over explicit warnings.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_freebsd.go -->
