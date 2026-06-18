# Group Research: subset-b-000070

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_windows.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_windows.go

This Windows-only CRI server file implements pod sandbox stats collection and conversion for the CRI `PodSandboxStats` API. The main entry point is `criService.podSandboxStats`, which rejects non-ready sandboxes, gathers task metrics for the sandbox and its containers, converts hcsshim `wstats.Statistics` into CRI Windows CPU/memory/network/process usage, and saves CPU samples back into sandbox/container stores for later `UsageNanoCores` deltas.

Important functions include `convertMetricsToWindowsStats`, `toPodSandboxStats`, `appendCPUPodStats`, `appendMemoryPodStats`, `listWindowsMetricsForSandbox`, `convertToCRIStats`, `getUsageNanoCores`, `windowsNetworkUsage`, `saveSandBoxMetrics`, and `getSandboxPidCount`. Control flow is metric-fetch, metric type decode, per-container filtering by running state, CRI conversion, pod-level summation, filesystem lookup through `GetSnapshot`, network endpoint stats from HCN/HNS, and process counting through containerd tasks.

State behavior is cache-based: previous CPU samples are stored in `sandboxstore.Sandbox.Stats` and `containerstore.Container.Stats`, while writable-layer usage is read from the snapshot store. Risks include Windows HostProcess nil/empty sandbox metrics, missing snapshot timestamps when snapshot lookup fails, possible unsigned CPU counter underflow in `getUsageNanoCores` if usage decreases, partial metric maps, and endpoint stat failures being logged but not fatal. Dependencies include hcsshim, containerd tasks API, typeurl, CRI runtime types, snapshot/image FS paths, and local CRI stores. Tests cover delta calculation, pod aggregation, HostProcess scenarios, stopped init-container filtering, missing memory/CPU stats, and stats-cache persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_windows_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_windows_test.go

This test file validates the Windows sandbox stats conversion logic without requiring live Windows containerd tasks. It constructs fake hcsshim statistics, sandbox store objects, container store objects, and prior CPU sample caches to exercise `getUsageNanoCores`, `toPodSandboxStats`, and `saveSandBoxMetrics`.

`TestGetUsageNanoCores` confirms first-sample behavior returns zero and later samples derive nanocores from cumulative CPU deltas over wall-clock nanoseconds. `Test_criService_podSandboxStats` drives the conversion path with table cases: no pod metric errors, pod totals include sandbox plus running containers, running init containers are included, stopped init containers are excluded, prior cache enables nonzero nanocore rates, nil or empty sandbox stats model HostProcess pods, missing container CPU does not fail, and missing pod stats does fail. Helper functions `sandboxPod`, `windowsStat`, `memoryStat`, and `newContainer` produce compact test fixtures.

`Test_criService_saveSandBoxMetrics` verifies persistence behavior for the stats caches. Nil pod stats, nil Windows stats, nil CPU, and nil `UsageCoreNanoSeconds` are skipped. Valid pod CPU stores sandbox samples, and valid container CPU stores container samples. Risks covered include nil-heavy Windows metrics and store update side effects. Remaining gaps are integration-level HCN network stats, actual containerd task metric requests, PID counting, and snapshot writable-layer lookup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stats_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_status.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_status.go

This file implements CRI `PodSandboxStatus` and helpers for translating internal sandbox state into CRI status plus verbose info. `criService.PodSandboxStatus` loads the sandbox from `sandboxStore`, determines IP reporting through `getIPs`, queries the sandbox controller via `SandboxStatus`, handles missing shim/controller status as `SANDBOX_NOTREADY`, merges updated resource information into the verbose `info` map, and falls back to the core sandbox metadata store if the controller returns a zero creation time.

The important helpers are `getIPs`, `setUpdatedResources`, `toCRISandboxStatus`, and `toDeletedCRISandboxInfo`. `getIPs` suppresses IP reporting for host-network pods or closed netns handles. `setUpdatedResources` unmarshals existing `info["info"]` into `podsandbox/types.SandboxInfo`, overlays the in-memory sandbox status `Overhead` and `Resources`, and marshals the value back into the info map. `toCRISandboxStatus` maps internal state strings into CRI enum values, preserves metadata, labels, annotations, runtime handler, namespace options, primary IP, and additional IPs. `toDeletedCRISandboxInfo` builds fallback verbose info for deleted/unavailable shims.

State and persistence are split: status uses in-memory sandbox status, controller state, cached metadata, and core sandbox metadata for created time fallback. Risks include invalid JSON in verbose info, nil netns edge cases, controller `NotFound` masking only expected shim death, and CRI's prohibition on zero `CreatedAt`. Tests cover state mapping, namespace/userns propagation, additional IPs, and updated resource injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_status_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_status_test.go

This test file verifies status conversion and updated-resource info merging for pod sandboxes. `TestPodSandboxStatus` constructs a sandbox metadata object with CRI metadata, labels, annotations, runtime handler, Linux namespace options, user namespace ID mappings, a primary IP, and additional IPv4/IPv6 addresses. It then checks `toCRISandboxStatus` maps internal ready and not-ready strings to the correct CRI enum and maps internal unknown to CRI `SANDBOX_NOTREADY`, since CRI has no unknown sandbox state.

`TestSetUpdatedResources` exercises `setUpdatedResources` with existing JSON info, nil resources, invalid JSON, and nil info maps. It validates that sandbox status `Overhead` and `Resources` are overlaid into `podsandbox/types.SandboxInfo` while existing fields such as `Pid` are preserved. Invalid JSON must return an error, while nil maps are no-ops.

The test signal is focused on pure conversion behavior rather than full `PodSandboxStatus` integration with a sandbox controller or core metadata store. Covered risks include accidental loss of namespace settings, additional IP formatting, unknown state mapping, resource updates not surfacing in verbose status, and JSON corruption handling. Gaps include controller `ErrNotFound` fallback, netns closed checks, created-time fallback from containerd's sandbox store, and host-network IP suppression.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stop.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_stop.go

This file implements CRI `StopPodSandbox` and the lower-level sandbox shutdown path. `StopPodSandbox` loads the sandbox by ID, treats a missing sandbox as success for CRI idempotency, blocks NRI plugin synchronization during stop, records tracing attributes, and delegates to `stopPodSandbox`.

`stopPodSandbox` first iterates all containers from `containerStore` and force-stops those belonging to the sandbox via `stopContainerRetryOnConnectionClosed`, avoiding the higher-level `StopContainer` race if containers are removed after listing. It stops the sandbox controller only when internal state is ready or unknown, tolerating `ErrNotFound` but failing other stop errors. It notifies NRI with `StopPodSandbox`, tears down CNI networking when a netns exists, removes the network namespace, updates metrics, and cleans up image mounts.

`waitSandboxStop` waits on the sandbox stop channel or context cancellation. `teardownPodNetwork` selects the runtime-specific CNI plugin, builds namespace options, calls `Remove`, and records operation counters/latency/errors. State behavior is mostly in-memory and external: stop state comes from `sandbox.Status`, stop signaling comes from `StopCh`, network cleanup mutates host namespaces/CNI state, and image-mount cleanup affects filesystem mounts. Risks include partial cleanup if container stop fails, CNI teardown behavior when setup never completed, closed netns path handling, and idempotency relying on store state. Tests cover `waitSandboxStop` cancellation, timeout, and already-stopped behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stop_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_stop_test.go

This test file targets the helper `criService.waitSandboxStop`. It constructs a test CRI service and sandbox store objects with different internal states, then verifies waiting behavior under context deadlines, cancellation, and already-stopped sandboxes.

The table cases show that a ready sandbox with a short context timeout returns an error when no stop signal arrives, an already-cancelled context returns an error immediately, and a not-ready sandbox created through `sandboxstore.NewSandbox` has its stop channel already closed and returns nil before the long timeout. The important integration point is the `store.StopCh` embedded in `sandboxstore.Sandbox`; `NewSandbox` marks not-ready sandboxes as stopped by calling `Stop`.

The test provides a narrow signal for stop waiting semantics and context propagation. It does not exercise the larger `StopPodSandbox` control flow: container force stop, sandbox controller stop, NRI callbacks, CNI teardown, netns removal, metric updates, or image mount cleanup. Risks outside this test remain in idempotency and partial cleanup interactions, while this test specifically guards against deadlocks and incorrect handling of context cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_stop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_update_resources.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_update_resources.go

This file implements CRI `UpdatePodSandboxResources`, which updates pod-level overhead and resource limits for an existing sandbox. The handler loads the sandbox from the local sandbox store, adds a tracing sandbox ID, invokes NRI pre-update notification with the requested Linux `Overhead` and `Resources`, updates local in-memory sandbox status, persists the update into containerd's core sandbox store extensions, optionally pushes the updated extensions to the sandbox controller, and sends an NRI post-update notification.

The local status update stores both values as `runtime.ContainerResources{Linux: ...}` in `sandbox.Status.Overhead` and `sandbox.Status.Resources`. The core store persistence uses `podsandbox.UpdatedResources` under `podsandbox.UpdatedResourcesKey` via `sandboxInfo.AddExtension`, then updates only the `extensions` field. The controller update delegates to `sandboxService.UpdateSandbox` and tolerates `errdefs.ErrNotImplemented` for older sandbox controllers, logging at trace level. Other controller errors fail the request.

Integration points are CRI runtime requests, NRI hooks, local sandbox store, containerd client `SandboxStore`, typeurl-backed extensions, sandbox controller update, and later status reporting through `setUpdatedResources`. Risks include divergence between local status and core store if later persistence fails, nil resource requests still creating non-nil wrapper structs, pre-update NRI failures aborting before persistence, and post-update NRI failures being logged rather than returned. Tests cover not-found local store, core get/update failures, extension contents, controller not-implemented fallback, success, and controller error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_update_resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_update_resources_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/sandbox_update_resources_test.go

This test file verifies `UpdatePodSandboxResources` using a fake containerd core sandbox store and a recording sandbox service. `fakeSandboxStore` implements `Get` and `Update`, can inject errors, and captures the updated sandbox. `recordSandboxService` records the sandbox ID passed to `UpdateSandbox` and can return configured errors.

The table-style subtests cover local sandbox lookup failure, core sandbox store get failure, core store update failure, successful local status mutation plus core extension persistence, success when the sandbox controller does not implement update, success when it does, and failure when controller update returns a non-`ErrNotImplemented` error. The successful extraction test checks both state channels: local `sandboxStore` status contains `runtime.ContainerResources` wrappers with the expected Linux memory and CPU values, and core sandbox extensions contain a `podsandbox.UpdatedResources` decoded from typeurl data.

The tests establish that persistence must reach both the local store and core store, and that old controllers remain compatible. They do not exercise NRI error paths directly, post-update notification logging, or later `PodSandboxStatus` surfacing of the updated resources. A notable risk exposed by sequencing is that the local status can be mutated before core-store update failure is returned.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/sandbox_update_resources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/service.go

This is the central CRI service construction and lifecycle file. It defines `CRIService`, `sandboxService`, `RuntimeService`, `ImageService`, the large `criService` struct, `CRIServiceOptions`, and lifecycle methods `NewCRIService`, `Run`, `Close`, and `IsInitialized`. It also introspects runtime-handler feature support through `introspectRuntimeHandler`, `introspectRuntimeFeatures`, and `supportsCRIUserns`.

`NewCRIService` wires dependencies from containerd, runtime, image service, sandbox controllers, CNI, NRI, event monitor, streaming server, local stores, registrars, and the stats collector. It creates one shared SELinux label store, initializes container and sandbox stores with the stats collector, creates the sandbox service, initializes platform-specific behavior, creates CNI config monitors, initializes NRI, introspects runtime handlers, and sets CRI runtime features.

`Run` subscribes event monitoring, starts the stats collector after injecting task/list dependencies, recovers state, starts event monitor, CNI config syncers, streaming server, registers NRI, marks the service initialized, and waits for a critical component to exit before closing everything. State is in-memory plus recovered containerd/CRI state; `initialized` is an atomic bool. Risks include startup ordering, goroutine/channel shutdown correctness, nil dependency assumptions, runtime feature introspection failure being logged but not fatal per handler, and stable default-handler aliasing. Integrations include containerd client services, typeurl, runtime feature APIs, CNI, streaming, NRI, events, stores, and deprecation/CDI config. Tests use fakes from `service_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service_linux.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/service_linux.go

This Linux build-tagged file provides platform initialization and CNI load options for the CRI service. The package `init` computes `kernelSupportsRRO` by checking for kernel version at least 5.12, which later gates advertised recursive read-only mount support. `criService.initPlatform` handles user namespace warnings, SELinux enable/disable and category range configuration, CNI plugin creation, capability discovery, and CDI registry configuration.

The CNI setup builds a map from default runtime and runtime-specific `NetworkPluginConfDir` values. It chooses a minimum network attachment count of two by default, or one when `UseInternalLoopback` is enabled. For each network config directory it creates a `go-cni` instance with min network count, config directory, max config count, and plugin binary directories. It populates `c.netPlugin` keyed by runtime handler name.

State changes are process-global for SELinux and CDI, service-local for `netPlugin` and `allCaps`, and package-global for `kernelSupportsRRO`. Dependencies include moby userns detection, opencontainers SELinux, go-cni, containerd capability and kernelversion helpers, log, and CDI. Risks include panicking during package init if kernel version parsing fails, global SELinux disablement when config disables SELinux, userns/AppArmor/OOM-score incompatibility, and CDI configuration errors aborting service creation. `cniLoadOptions` returns loopback plus default config unless internal loopback is used.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service_other.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/service_other.go

This non-Linux, non-Windows build-tagged file provides stub platform behavior for `criService`. It implements `initPlatform` as a no-op returning nil and `cniLoadOptions` as an empty option slice. Its purpose is to let the CRI server package compile on unsupported or less-featured platforms without attempting Linux SELinux/CDI/CNI setup or Windows CNI setup.

The control flow is intentionally minimal: `NewCRIService` calls `c.initPlatform`, and on these platforms that step makes no changes to `netPlugin`, process capabilities, SELinux state, or CDI registry. Later code that depends on `netPlugin` must tolerate a nil or empty plugin map. `cniLoadOptions` is used by CNI config monitors and runtime config update paths; returning no options means no loopback/default config behavior is requested by this platform shim.

There is no persistence or external state mutation in this file. Its main integration point is the build-tag split with `service_linux.go` and `service_windows.go`. Risks are mostly behavioral gaps: CRI networking may not be initialized, platform-specific security support is absent, and tests for Linux/Windows behavior do not apply. This file has no direct tests in the listed set; compilation across build tags is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/service_test.go

This test-support file supplies fake services and a `newTestCRIService` constructor used by multiple CRI server unit tests. `fakeSandboxService` implements the local `sandboxService` interface with mostly `ErrNotImplemented` behavior, while `SandboxPlatform` returns the default platform and `SandboxController` returns `fakeSandboxController`. `fakeSandboxController` implements containerd sandbox controller methods with `ErrNotImplemented` stubs.

`fakeRuntimeService` returns `testConfig` and can load cached OCI specs from an in-memory map. The `testOpt` pattern allows specific tests to inject runtime service or mutate the constructed `criService`. `newTestCRIService` builds a CRI service with fake OS operations, label store, sandbox and container stores without stats collector, registrars, fake default CNI plugin, fake sandbox service, and default fake runtime/image services.

State is all in-memory and scoped to tests; no checkpointing or live containerd connection is used unless a test overrides the client. This helper is an integration point for status, stop, runtime config, and resource update tests. Risks include tests relying on incomplete fake behavior, `ErrNotImplemented` masking interactions not under test, and divergence from `NewCRIService` setup such as missing stats collector, event monitor, streaming server, NRI, runtime handlers, and platform initialization. Its value is deterministic isolation for narrow unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service_windows.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/service_windows.go

This Windows build-tagged file provides platform initialization and CNI load options for the CRI service. It defines `windowsNetworkAttachCount` as one because Windows adds loopback by default and CRI only requires one non-host network attachment to obtain the pod IP.

`criService.initPlatform` builds plugin configuration directories from the default CRI config and any runtime-specific `NetworkPluginConfDir` overrides. For each runtime name it chooses the runtime-specific `NetworkPluginMaxConfNum` when provided, otherwise the global value, and creates a `go-cni` plugin with min network count one, plugin config directory, max config count, and plugin binary directories. The result is stored in `c.netPlugin` by name.

`cniLoadOptions` returns only `cni.WithDefaultConf`, unlike Linux where loopback may be explicitly loaded. State behavior is limited to the service's `netPlugin` map; there are no SELinux, capability, CDI, or kernel feature checks. Dependencies are go-cni and CRI config. Risks include CNI initialization errors aborting service creation, runtime-specific network directory divergence, and Windows networking behavior depending on CNI defaults. This file is indirectly covered by service initialization expectations and Windows stats/status behavior, but it has no direct test in the listed files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/service_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/stats_collector.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/stats_collector.go

This Linux build-tagged file implements the background `StatsCollector` that periodically samples CPU usage for containers and sandboxes to support instantaneous CRI `UsageNanoCores`. `NewStatsCollector` derives collection interval and retention period from CRI config strings, falling back to one second collection and two minute retention, and sizes each per-ID `TimedStore` to at least two samples.

`SetDependencies` injects the containerd task metrics client and store listing callbacks. `Start` launches `collectLoop`; `Stop` closes `stopCh` once and waits on `doneCh`. `collect` uses the containerd `k8s.io` namespace and calls `collectContainerStats` and `collectSandboxStats`. Container collection builds a multi-filter task metrics request, extracts cgroup v1/v2 CPU totals from typeurl metric data, and stores samples by metric ID. Sandbox collection reads each sandbox's Linux cgroup parent and samples the parent cgroup directly so pod CPU includes all containers.

State is an in-memory map from container/sandbox ID to thread-safe `stats.TimedStore`, guarded by `StatsCollector.mu`. Stores are added by sampling fallback or explicit `AddContainer`, and removed by `RemoveContainer`. Risks include `Stop` blocking if called before `Start` because `doneCh` is never closed, silently ignored duration parse errors, cgroup path availability, cgroup v2 microsecond conversion, task metrics failures only logging at debug, and list callbacks needing to be set before start. Integration is through service `Run`, container/sandbox stores, task service, cgroups libraries, typeurl, and `store/stats`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/stats_collector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/stats_collector_other.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/stats_collector_other.go

This non-Linux build-tagged file provides a stub `StatsCollector` implementation so the CRI server can compile and run without Linux cgroup sampling. `NewStatsCollector` returns an empty collector, `SetDependencies` ignores the task service and store callbacks, `Start` and `Stop` are no-ops, `AddContainer` and `RemoveContainer` are no-ops, and both `GetUsageNanoCores` and `GetLatestSample` report no data.

The file preserves the same public API as the Linux implementation, allowing `service.go`, container store, sandbox store, and stats consumers to call collector methods without platform branching. There is no state, persistence, goroutine, cgroup dependency, or task metrics dependency. On Windows, sandbox stats use `sandbox_stats_windows.go` and store cached samples through container/sandbox stores rather than this background collector.

The main risk is behavior divergence: non-Linux platforms do not get background instantaneous CPU rate sampling, so callers must tolerate missing `UsageNanoCores` data. The stub intentionally prevents Linux cgroup-specific imports from leaking to other platforms. Test signal is mostly compilation across build tags and Windows stats tests; this file has no direct unit tests in the listed set.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/stats_collector_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/status.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/status.go

This file implements CRI `Status` and the containerd deprecation warning runtime condition. `criService.Status` always marks `RuntimeReady` true because serving CRI implies the containerd plugin is active. It initializes `NetworkReady` true, then consults the default CNI plugin status and marks it false with reason `NetworkPluginNotReady` if CNI reports an error.

The response includes `RuntimeFeatures` and a stable sorted list of runtime handlers collected from `c.runtimeHandlers`. In verbose mode it serializes the CRI config, Go runtime version, default CNI config, runtime-specific CNI load statuses, and default `lastCNILoadStatus` into `Info`. It then queries containerd introspection server state and appends `ContainerdHasNoDeprecationWarnings`, produced by `runtimeConditionContainerdHasNoDeprecationWarnings`.

`runtimeConditionContainerdHasNoDeprecationWarnings` filters deprecation warnings by configured ignore IDs, returns status true when none remain, or status false with reason `ContainerdHasDeprecationWarnings` and a JSON message map keyed by warning ID. Dependencies include CRI runtime types, go-cni behavior, containerd introspection API, JSON, maps/slices sorting helpers, and service config. Risks include verbose serialization errors, introspection failure failing status, CNI config marshal errors only logged, and condition message JSON stability. Tests cover deprecation filtering and runtime handler order stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/status_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/status_test.go

This test file covers two pieces of `status.go`: deprecation-warning condition construction and stable runtime-handler ordering. `TestRuntimeConditionContainerdHasNoDeprecationWarnings` builds one introspection deprecation warning and verifies the condition becomes false with the expected type, reason, and JSON message when not ignored, then true when the warning ID appears in the ignore list.

The rest of the file creates a fake introspection service and injects it into a private field of `containerd.Client` using reflection and unsafe pointers. This avoids a live gRPC connection while allowing `criService.Status` to call `client.IntrospectionService().Server`. `newStatusTestCRIService` returns a minimal service with that fake client and an empty runtime handler map.

`TestStatusRuntimeHandlersOrdering` creates 100 random runtime handlers, calls `Status` twice, and asserts the returned handler names stay in the same order. This specifically protects the sort added over map-derived values. Risks covered include nondeterministic map iteration leaking into CRI responses and deprecation ignore handling. Gaps include network-ready condition behavior, verbose info content, CNI config serialization, and introspection errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/streaming.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/streaming.go

This file adapts `criService` to the Kubernetes CRI streaming runtime interface used by exec, attach, and port-forward HTTP streams. `streamRuntime` wraps a `*criService`, and `newStreamRuntime` returns it as `streaming.Runtime` for `streaming.NewServer` in service construction.

`Exec` calls `criService.execInContainer` in the containerd CRI namespace with command, stdio writers/readers, TTY flag, and resize channel. If the command exits nonzero it returns `executil.CodeExitError` carrying the exit code, matching Kubernetes streaming expectations. `Attach` delegates to `criService.attachContainer` with the same namespace wrapping and stream parameters. `PortForward` validates the port is in the TCP/UDP user range `1..math.MaxUint16`, wraps the namespace, and delegates to `criService.portForward`.

`handleResizing` starts a goroutine, guarded by Kubernetes `runtime.HandleCrash`, that consumes terminal resize events until context cancellation or channel close. It ignores invalid sizes with height or width below one. There is no persistent state; the key dependencies are CRI service exec/attach/port-forward internals, containerd namespace utilities, Kubernetes streaming packages, and stdio streams. Risks include goroutine lifetime tied to context correctness, nil resize channel behavior, invalid port rejection, and exit code pointer assumptions from `execInContainer`. No direct tests are listed here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/streaming.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/test_config.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/test_config.go

This test-support file defines shared CRI server test constants and a baseline `testConfig`. `testRootDir` and `testStateDir` provide fake root/state directories. `testConfig` is a `criconfig.Config` with those directories, `TolerateMissingHugetlbController` enabled, default runtime name `runc`, and a single runtime configured with type `runc`, snapshotter `overlayfs`, and sandboxer `shim`.

The file has no executable control flow, no persistence, and no direct external dependencies beyond the CRI config package. It is used by `fakeRuntimeService.Config` and `newTestCRIService` to provide a consistent configuration surface for unit tests that exercise runtime config updates, sandbox status, resource updates, and other CRI server helpers.

The main integration point is test determinism: tests do not need to construct full production config and can rely on one default runtime handler. Risks are that the simplified config omits many production fields, including CNI directories, image config, stats collection periods, CDI, SELinux, NRI, and runtime feature details. Tests that depend on those fields must mutate `c.config` explicitly. There are no direct tests for this file; its signal comes through compilation and downstream unit tests that use `newTestCRIService`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/test_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/update_runtime_config.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/update_runtime_config.go

This file implements CRI `UpdateRuntimeConfig`, currently focused on pod CIDR updates used to generate CNI configuration from a template. The handler reads `RuntimeConfig.NetworkConfig.PodCidr`, returns immediately when empty, splits comma-separated CIDRs, trims whitespace, computes default routes with `getRoutes`, and uses `NetworkPluginConfTemplate` to decide whether containerd should write a CNI config.

If no template is configured, it logs and waits for other components. If the default CNI plugin is nil, it logs and returns. If the plugin status is already healthy, it skips generation. Otherwise it increments network status metrics, attempts `Load` with platform CNI load options, and only writes the generated config when the plugin remains not loaded. `writeCNIConfigFile` parses the template, creates the config directory, opens an atomic file at `10-containerd-net.conflist`, executes the template with primary CIDR, all CIDR ranges, and IPv4/IPv6 default routes, and closes the file.

State/persistence behavior is host filesystem mutation through atomic CNI config writes. Dependencies include CRI runtime config, `net.ParseCIDR`, text templates, atomicfile, CNI plugin status/load, metrics, and config paths. Risks include the apparent inverted nil-plugin log message, invalid CIDR aborting, template execution failure, deferred close assigning to a local `err` after earlier errors, and generating only after both status and load fail. Tests cover empty CIDR, missing template, ready network, and successful dual-stack config generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/update_runtime_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/update_runtime_config_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/update_runtime_config_test.go

This test file validates the CNI config generation path in `UpdateRuntimeConfig`. It creates a temporary CNI template using `PodCIDR`, `PodCIDRRanges`, and `Routes`, configures a test CRI service with a temporary CNI config directory and template path, and sends a dual-stack pod CIDR string containing IPv4 and IPv6 CIDRs.

The subtests cover four paths: empty CIDR does not generate a file, missing template does not generate a file, already-ready network does not generate a file, and a configured template with an unhealthy/unloadable fake CNI plugin generates `10-containerd-net.conflist`. For generation, it asserts the rendered config uses the first CIDR as `.PodCIDR`, includes both CIDR ranges, and adds both `0.0.0.0/0` and `::/0` routes.

The tests exercise filesystem persistence by writing the template and reading the generated config from a temp directory. They use `servertesting.FakeCNIPlugin` to force `Status` and `Load` errors. Covered risks include accidental config generation when not needed and incorrect route/range rendering. Gaps include invalid CIDR errors, template parse errors, directory creation errors, atomic close errors, nil default CNI plugin behavior, and metric side effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/update_runtime_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/version.go -->
# Research: sources/cloud-native/containerd/internal/cri/server/version.go

This small file implements CRI `Version`. It defines `containerName` as `containerd` and `kubeAPIVersion` as `0.1.0`, with a TODO noting this is not the actual CRI API version. `criService.Version` returns a `runtime.VersionResponse` containing the Kubernetes-facing version string, runtime name, containerd runtime version from `github.com/containerd/containerd/v2/version`, and CRI runtime API version from internal CRI constants.

There is no complex control flow, mutable state, persistence, or platform-specific behavior. The function ignores request fields and context. Its dependencies are the CRI runtime API package, containerd version package, and internal `constants.CRIVersion`.

Integration points are kubelet/crictl version probes and any client relying on CRI version metadata. Risks are mostly semantic drift: `kubeAPIVersion` remains a hardcoded legacy value while `RuntimeApiVersion` carries the internal CRI version, and external clients might interpret these fields differently. There are no direct tests in the listed set, so protection comes from compilation and integration/API compatibility expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/seutil/seutil.go -->
# Research: sources/cloud-native/containerd/internal/cri/seutil/seutil.go

This SELinux utility file provides `ChangeToKVM`, a helper for converting an existing process label to use the SELinux type from KVM container labels. If the input label is empty or SELinux is disabled, it returns an empty string and nil error. Otherwise it asks SELinux for KVM container labels, immediately releases the generated process label reservation, parses both the current label and KVM process label into SELinux contexts, replaces the current context's `type` field with the KVM type, and returns the resulting label string.

The control flow is intentionally small but has process-global SELinux integration. It depends on `opencontainers/selinux/go-selinux` for enablement checks, generated KVM labels, label release, context parsing, and context rendering. There is no local persistence, but SELinux label reservation/release affects global label allocation state.

Risks include invalid input labels returning parse errors, errors from parsing generated KVM labels, releasing a generated label while keeping only its type, and returning an empty label rather than the original label when SELinux is disabled. The helper is likely used by VM/Kata/KVM runtime paths that need KVM-compatible process types while preserving MLS/MCS level and other context fields. No direct tests are listed for this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/seutil/seutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/apparmor_linux.go -->
# Research: sources/cloud-native/containerd/internal/cri/sputil/apparmor_linux.go

This Linux security-profile helper converts CRI AppArmor profile configuration into containerd OCI `SpecOpts`. `GenerateApparmorSecurityProfile` delegates non-empty legacy profile strings to the shared `generateSecurityProfile` parser and returns nil when unset. `GenerateApparmorSpecOpts` enforces support and profile semantics.

If AppArmor is disabled, specifying anything other than `Unconfined` is an error; nil or unconfined returns no spec options. When enabled, nil security profile defaults to runtime default AppArmor. Invalid combinations where `LocalhostRef` is set for a non-localhost profile return an error. `Unconfined` returns nil, `RuntimeDefault` returns nil for privileged containers or `apparmor.WithDefaultProfile(appArmorDefaultProfileName)` otherwise, and `Localhost` verifies the profile exists under `/sys/kernel/security/apparmor/profiles` before returning `apparmor.WithProfile`.

`appArmorProfileExists` scans the kernel profile list for lines prefixed by the requested profile plus `" ("`. State behavior is external to the kernel AppArmor profile registry and OCI spec mutation through returned functions; there is no local persistence. Risks include filesystem access errors causing localhost profile failure, default profile TODO cleanup, privileged runtime-default bypass, localhost prefix trimming, and unsupported platforms hidden by build tags. Tests cover enabled/disabled semantics, unconfined/default/local invalid cases, privileged behavior, and struct-based `SecurityProfile` variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/apparmor_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/apparmor_linux_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/sputil/apparmor_linux_test.go

This Linux test file verifies AppArmor profile parsing and OCI spec option generation. `TestGenerateApparmorSpecOpts` uses table cases spanning legacy string profiles and direct CRI `SecurityProfile` structs. It checks disabled AppArmor behavior, defaulting when profile is unset, privileged container bypass for runtime default, unconfined no-op behavior, invalid profile strings, undefined localhost profiles, and invalid struct combinations.

When a spec option is expected, the test applies both the expected and actual `oci.SpecOpts` to copied OCI runtime specs and compares the resulting specs. This validates behavior at the mutation level rather than comparing function pointers. Undefined localhost profiles are expected to error because the test does not provision entries in `/sys/kernel/security/apparmor/profiles`.

The test signal covers most policy branches in `GenerateApparmorSpecOpts`, including Kubernetes `SecurityProfile` struct migration. It does not cover a successful existing localhost profile, real kernel profile scanning success, default profile creation/cleanup, or non-Linux build behavior. It also relies on local spec mutation helpers and does not launch containers. Risks guarded are accidental AppArmor application to privileged containers, silent acceptance of unsupported AppArmor requests, and malformed localhost handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/apparmor_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/seccomp_linux.go -->
# Research: sources/cloud-native/containerd/internal/cri/sputil/seccomp_linux.go

This Linux security-profile helper converts CRI seccomp settings into containerd OCI `SpecOpts`. `GenerateSeccompSecurityProfile` parses an explicit profile path first; when unset, it parses `unsetProfilePath` as the configured default; when both are empty it returns nil. The shared parser recognizes runtime/docker default, unconfined, and localhost-prefixed paths.

`GenerateSeccompSpecOpts` returns nil for privileged containers before checking seccomp support. If seccomp is disabled, any non-unconfined specified profile is an error, while nil or unconfined returns nil. When enabled, nil and unconfined both mean no spec option, runtime default returns `seccomp.WithDefaultProfile`, and localhost returns `seccomp.WithProfile` after trimming a possible `localhost/` prefix. Non-localhost profiles carrying `LocalhostRef` are rejected, as are unknown profile types.

State behavior is stateless until the returned spec option mutates an OCI spec. Dependencies include CRI runtime security profile types, containerd seccomp contrib helpers, and OCI spec option APIs. Risks include privileged containers bypassing even invalid profile settings, no existence validation for localhost seccomp profile paths in this helper, support-disabled errors depending on profile type, and default profile fallback semantics. Tests cover explicit/default/unset profiles, disabled support, privileged behavior, default profile variants, localhost prefix trimming, and invalid struct combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/seccomp_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/seccomp_linux_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/sputil/seccomp_linux_test.go

This Linux test file verifies seccomp profile parsing and spec option generation. `TestGenerateSeccompSecurityProfileSpecOpts` uses table cases for legacy string profile inputs, default profile fallback, privileged containers, disabled seccomp support, unconfined/no-profile behavior, runtime/docker defaults, localhost profiles, and direct CRI `SecurityProfile` structs.

Expected spec options are applied to an OCI runtime spec with Linux process capabilities, and actual options are applied to a deep copy of the same spec. Comparing the mutated specs validates that `seccomp.WithDefaultProfile` and `seccomp.WithProfile` produce the intended effect. The capability-rich process fixture also exercises more of the default seccomp profile generation path.

The tests cover important risks: unsupported seccomp requests fail loudly unless unconfined/nil, privileged containers skip seccomp, unset profile can use configured default, localhost prefixes are trimmed for both legacy and struct paths, and `LocalhostRef` on runtime-default profiles is invalid. Gaps include actual seccomp profile file existence, container runtime enforcement, non-Linux behavior, and malformed profile paths beyond the parser cases. This is a pure unit test suite with no persistent state.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/seccomp_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/securityprofile_linux.go -->
# Research: sources/cloud-native/containerd/internal/cri/sputil/securityprofile_linux.go

This shared Linux helper parses legacy profile path strings into CRI `runtime.SecurityProfile` structs for AppArmor and seccomp. It defines common constants: `profileNamePrefix` (`localhost/`), `runtimeDefault`, `dockerDefault`, `appArmorDefaultProfileName`, `unconfinedProfile`, and `seccompDefaultProfile`.

`generateSecurityProfile` maps `runtime/default`, `docker/default`, and empty string to `SecurityProfile_RuntimeDefault`, maps `unconfined` to `SecurityProfile_Unconfined`, and requires every other value to start with `localhost/`. Localhost values become `SecurityProfile_Localhost` with `LocalhostRef` stripped of the prefix. Invalid non-prefixed custom values return an error.

There is no persistence or external state in this file. It is a policy normalization layer used by `GenerateApparmorSecurityProfile` and `GenerateSeccompSecurityProfile`, preserving compatibility with older string-based security profile configuration while feeding newer CRI structured profiles. Risks include treating empty string as runtime default for callers that invoke this helper directly, while higher-level helpers may choose nil for unset; accepting `docker/default` as runtime default; and strict rejection of custom names without `localhost/`. Test coverage is indirect through AppArmor and seccomp test tables.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/sputil/securityprofile_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/container.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/container/container.go

This file defines the CRI in-memory container object and concurrent container store. `Container` embeds immutable `Metadata`, mutable `StatusStorage`, optional containerd client handle, optional IO, stop channel, stop-signal timeout flag, and cached CPU stats. Constructor options include `WithContainer`, `WithContainerIO`, and `WithStatus`, the last of which checkpoints status with `StoreStatus` and stops the stop channel for already-exited containers.

`NewContainer` initializes stop coordination and applies options. `Container.Delete` delegates to status checkpoint deletion. `Store` maintains a map by full ID, a truncation index for short-ID lookup, a shared SELinux label store, and optional stats collector. `Add` rejects duplicates, reserves the process label level, adds the ID to the truncation index, stores the container, and registers the ID with the stats collector. `Get` resolves truncated IDs. `List` returns a snapshot slice. `UpdateContainerStats` replaces cached stats for an existing container. `Delete` resolves the ID, closes IO, releases labels, removes index/map entries, and removes the stats collector store.

State is in-memory except status checkpointing handled by `status.go` and external label reservations. Risks include returning container values whose embedded pointers remain mutable, label reservation failures aborting add, truncation-index ambiguity, and stats cache replacement races avoided by store locks. Tests cover add/get/list/delete, truncated IDs, duplicate detection, stats update, SELinux label reserve/release under SELinux, and IO option behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/container_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/container/container_test.go

This test file validates the container store and container construction options. `TestContainerStore` builds several containers with fake status and SELinux-like process labels, adds them to a `Store`, retrieves them by generated truncated IDs, lists them, updates cached stats, checks duplicate add errors, deletes them by truncated IDs, and verifies deleted containers return `errdefs.ErrNotFound`.

When SELinux is enabled, the test overrides the label store's reserver/releaser callbacks to assert MCS levels are reserved once per level and released after the last container using that level is removed. The stats update section verifies `UpdateContainerStats` mutates the stored container values and `List` reflects those cached samples.

`TestWithContainerIO` checks that `WithContainerIO` attaches a `ContainerIO` pointer while a container without the option has nil IO. The tests exercise store locking indirectly but not with concurrency. Covered risks include truncation-index lookup, duplicate ID handling, stats cache mutation, stop-channel behavior from fake exited status, and label reference behavior. Gaps include checkpoint-backed `WithStatus`, IO close side effects on delete, stats collector callbacks, and real containerd client handles.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/fake_status.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/container/fake_status.go

This test helper supplies an in-memory `StatusStorage` implementation for container tests. `WithFakeStatus` is a `Container` option that installs `fakeStatusStorage` and closes the container stop channel when the fake status has `FinishedAt` set, simulating a task-exit event for exited containers.

`fakeStatusStorage` stores a `Status` protected by an RW mutex. `Get` returns the current status value. `UpdateSync` delegates to `Update` instead of writing any checkpoint. `Update` applies the supplied transactional `UpdateFunc`, leaves the old status unchanged on error, and stores the new status on success. `Delete` is a no-op returning nil.

There is no disk persistence, which is the point: tests can construct containers without temp checkpoint directories. The helper integrates with `NewContainer` options and any server/store tests that need status behavior without persistence. Risks are test fidelity gaps: `UpdateSync` does not exercise atomic file writes, `Get` does not deep-copy pointer fields like production status storage, and `Delete` never fails. It is used by container, sandbox stats, and service tests to model running/exited/failed containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/fake_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/metadata.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/container/metadata.go

This file defines immutable container metadata and versioned JSON encoding. `Metadata` records container ID, name, sandbox ID, CRI `ContainerConfig`, image reference, log path, stop signal, and SELinux process label. Comments note metadata is immutable after creation and checkpointed as a containerd container label, while resource limits are updatable elsewhere with containerd as source of truth.

`MarshalJSON` wraps the unversioned metadata in `versionedMetadata{Version: metadataVersion, Metadata: ...}` to avoid recursive marshaling. `UnmarshalJSON` decodes the wrapper and accepts only current version `v1`, returning an unsupported-version error otherwise. `metadataInternal` is the alias used to break recursive method calls.

State/persistence behavior is JSON serialization intended for labels/checkpoints outside this file. Dependencies include Go JSON and CRI runtime container config. Risks include strict version rejection during upgrades if migration is not added, pointer-valued `Config` being mutable despite metadata immutability convention, and consumers needing to preserve this wrapper format. Tests cover JSON marshal/unmarshal paths and unsupported versions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/metadata_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/container/metadata_test.go

This test file verifies container metadata JSON round-tripping. `TestMetadataMarshalUnmarshal` constructs a `Metadata` value with ID, name, sandbox ID, CRI container metadata, image reference, and log path. It compares normal `json.Marshal` output with the explicit `versionedMetadata` wrapper, checks direct `MarshalJSON` followed by `UnmarshalJSON`, direct `MarshalJSON` followed by `json.Unmarshal` into the wrapper type, and `json.Marshal` followed by `UnmarshalJSON`.

The unsupported-version case constructs a wrapper with a random version and asserts unmarshalling into `Metadata` fails. This protects the version gate in `UnmarshalJSON` and the non-recursive wrapper format.

The test signal focuses on serialization compatibility for metadata checkpointing in containerd labels. It does not test every metadata field, notably stop signal and process label, nor nil config behavior or migration from older versions. There is no filesystem persistence in this test; it validates only the JSON payload shape that other persistence layers store.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/status.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/container/status.go

This file defines container status state, checkpoint encoding, and synchronized status storage. `Status` includes PID, created/started/finished timestamps, exit code, reason/message, transient `Starting`, `Removing`, and `Unknown` flags, optional resource constraints, and restore marker. `State` derives CRI state from unknown flag and timestamps: finished wins over started, started over created, otherwise unknown.

`encode` and `decode` wrap status in `versionedStatus` version `v1`; transient flags are JSON-ignored. `StoreStatus` atomically writes `root/status` with mode 0600 through continuity, returning a `statusStorage`. `LoadStatus` reads and decodes that file. `statusStorage.Get` returns a deep copy so callers cannot mutate stored pointer fields. `deepCopyOf` manually copies Linux and Windows `ContainerResources`, including hugepage limits and Windows affinity CPU groups. `UpdateSync` updates memory and checkpoint atomically under lock; `Update` updates memory only; `Delete` renames the status file to a temporary deletion path and removes it idempotently.

Dependencies include JSON, filesystem, continuity atomic writes, CRI runtime types, and mutexes. Risks include manual deep-copy maintenance as resource fields grow, unsigned or invalid timestamp semantics left to callers, unsupported version migration, and `Update`/`UpdateSync` differing in persistence. Tests cover state derivation, encode/decode, transient field exclusion, rollback on update errors, checkpoint persistence, deep-copy isolation, Windows affinity copying, and idempotent delete.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/status_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/container/status_test.go

This test file validates container status state derivation, serialization, checkpoint persistence, transactional updates, deletion, and deep-copy behavior. `TestDeepCopyOfWindowsAffinityCpus` ensures Windows CPU affinity slices are copied without nil entries and mutations to the returned copy do not affect the original. `TestContainerState` verifies unknown, created, running, and exited state derivation from flags and timestamps.

`TestStatusEncodeDecode` confirms status JSON wrapping round-trips persistent fields while transient `Removing`, `Starting`, and `Unknown` are not encoded, and unsupported versions fail. `TestStatus` uses a temp directory to store the checkpoint, load it back, verify failed `Update` and `UpdateSync` roll back, verify memory-only `Update` does not change the on-disk checkpoint, verify `UpdateSync` does, confirm previously returned snapshots are immutable, and check idempotent deletion removes the status file.

The tests give strong signal for persistence correctness and transaction boundaries. They do not cover concurrent updates, every resource field, filesystem rename failure modes, or migration from old status versions. They guard the most important risk: divergence between in-memory status and checkpointed status must be intentional and predictable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/container/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/image/fake_image.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/image/fake_image.go

This test helper constructs an image `Store` preloaded with synthetic image metadata. `NewFakeStore` creates a normal `Store` with nil containerd image getter and content provider, using the default platform matcher. For each supplied `Image`, it fills `refCache` for every reference and inserts the image into the internal store with `store.add`.

The helper returns an error if any image cannot be added, wrapping the failed image. It intentionally does not support `Update`, because the underlying containerd getter/provider are nil; tests use it for local resolve/get/list/update-cache behavior where image data is already known.

State is in-memory only: reference cache, digest set, image map, and pinned reference map are initialized exactly like the production store. Dependencies are the image store implementation and containerd platform default. Risks are test-only fidelity gaps around content reads, image usage calculation, platform-specific manifest selection, and containerd image labels. It is used by `image_test.go` to validate update and reference behavior without a live containerd content store.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/image/fake_image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/image/image.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/image/image.go

This file implements CRI's image metadata cache. `Image` records image config digest ID, references, chain ID, compressed size, OCI image spec, and pinned state. `Store` holds a reference-to-ID cache, a containerd image getter, content provider, platform matcher, and an internal digest-indexed store.

`Update` locks the outer store, reads the image from containerd unless not found, builds local metadata with `getImage`, and delegates to `update`. `getImage` computes rootfs diff IDs and chain ID, compressed usage, config descriptor digest, config blob, OCI image spec, and pinned label state. `update` handles disappeared refs, unchanged refs with pin state changes, moved refs, and new refs.

The internal `store` protects image map, digest set for truncated lookup, and `pinnedRefs`. `add` merges references and pin state, `isPinned`, `pin`, and `unpin` manage per-reference pinning, `get` supports truncated digest lookup including algorithm-less prefixes, and `delete` removes a reference or the entire image when unreferenced.

State is an in-memory cache derived from containerd image/content stores; no disk persistence here. Dependencies include containerd images/content/usage APIs, digestset, OCI specs, distribution reference sorting, platform matching, CRI pinned-image labels, and set utilities. Risks include cache coherence with containerd events, pin state per ref, ambiguous truncated IDs, platform-limited image metadata, and content read/JSON errors. Tests cover internal add/get/list/delete, reference merging, pinned refs, fake-store update cases, and resolve behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/image/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/image/image_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/image/image_test.go

This test file validates both the internal image store and the outer reference cache behavior. `TestInternalStore` adds several digest-named images, retrieves them by truncated full digest and truncated algorithm-less digest, verifies ambiguous prefixes fail, lists images, merges a new reference into an existing image, ignores duplicate references, deletes references one at a time, and removes the image when no references remain.

`TestInternalStorePinnedImage` verifies pin tracking is per reference while the image-level `Pinned` flag remains true if any reference is pinned. It covers adding pinned refs, pinning an existing unpinned ref, unpinning one ref while another remains pinned, unpinning the last ref, and deleting a pinned ref.

`TestImageStore` uses `NewFakeStore` and direct `update` calls to cover outer cache scenarios: disappearing nonexistent refs, adding a new ref to an existing image, adding a new image, moving an existing ref to a new image ID, and removing an existing ref. It also verifies `Resolve` for present refs and not-found for removed refs. Gaps include live containerd image/content access, platform manifest selection, size calculation, OCI config unmarshalling errors, and event-driven cache refresh.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/image/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/label/label.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/label/label.go

This file implements a small SELinux process label reservation store. `Store` tracks MLS/MCS levels in a map from level string to reference count, with injectable `Releaser` and `Reserver` callbacks defaulting to `selinux.ReleaseLabel` and `selinux.ReserveLabel`.

`Reserve` parses the label with `selinux.NewContext`, extracts the `level` component, ignores empty levels, calls the reserver only when the level is not already tracked, and increments the count. `Release` parses the label, ignores invalid labels and empty levels, looks up the count, and either calls the releaser and deletes the level when count is one, deletes corrupt nonpositive counts, or decrements counts above one.

State is process-local reference counts plus external SELinux reservation/release side effects. The store is shared by sandbox and container stores in `NewCRIService`, preventing duplicate reservation of the same MCS level while multiple objects use it. Risks include invalid labels causing reserve errors but release no-ops, empty level labels being ignored, correctness depending on all add/delete paths balancing reserve/release, and injected callbacks used in tests. Tests under SELinux cover reference counting, bad input, unknown release, and over-release behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/label/label.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/label/label_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/label/label_test.go

This SELinux-dependent test file validates label store reference counting and bad input handling. Both tests skip when SELinux is not enabled, because the underlying label parser and semantics depend on SELinux support.

`TestAddThenRemove` overrides the store's reserver and releaser to count calls and assert the label level. It reserves two labels with the same MCS level, verifies only one map entry with count two, releases both labels, and confirms the map is empty while reserver and releaser were each called exactly once. This proves the store reserves per level, not per full label string.

`TestJunkData` verifies empty labels are ignored, malformed labels fail reserve and do not call callbacks, releasing unknown labels is a no-op, and over-releasing after one reserve only calls releaser once and leaves no level entry. The tests guard against label leaks and double-release bugs. Gaps include concurrent reserve/release, different levels in one test, behavior when SELinux parser accepts labels without levels, and integration with container/sandbox stores.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/label/label_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/metadata.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/metadata.go

This file defines immutable CRI sandbox metadata and versioned JSON encoding. `Metadata` records sandbox ID, name, CRI `PodSandboxConfig`, netns path, primary IP, additional IPs, runtime handler, CNI result, and SELinux process label. Comments note metadata is immutable after creation and checkpointed as a containerd container label.

`MarshalJSON` wraps the metadata in `versionedMetadata` with version `v1`; `metadataInternal` avoids recursive calls to `MarshalJSON`. `UnmarshalJSON` decodes the wrapper, accepts only `v1`, and returns an unsupported-version error otherwise. The metadata includes pointer-rich CRI config and CNI result data, so immutability is a convention enforced by store usage rather than by deep-copying here.

State/persistence behavior is serialization for labels/checkpoints outside this package; there is no direct disk write in this file. Dependencies include JSON, go-cni result type, and CRI runtime sandbox config. Risks include strict version rejection during upgrade without migration, mutable pointer fields, CNI result serialization compatibility, and preserving additional IPs/runtime handler for status reporting and network teardown. Tests cover wrapper JSON round-trips and unsupported versions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/metadata_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/metadata_test.go

This test file validates sandbox metadata JSON serialization. `TestMetadataMarshalUnmarshal` constructs a `Metadata` value with ID, name, and CRI pod sandbox metadata. It confirms normal `json.Marshal` matches an explicit `versionedMetadata` wrapper, direct `MarshalJSON` can be decoded by `UnmarshalJSON`, the wrapper can be decoded through `json.Unmarshal`, and `json.Marshal` output can be passed back to `UnmarshalJSON`.

The unsupported-version case builds a wrapper with a random version and asserts unmarshalling into `Metadata` fails. This protects the versioning contract used when sandbox metadata is checkpointed in containerd labels.

The test signal is focused on payload format compatibility, not full field coverage. It does not populate netns path, IPs, runtime handler, CNI result, process label, or nil config edge cases. There is no filesystem persistence or containerd label integration in the test. It guards the core risk that recursive JSON methods or unsupported-version handling could break recovery of sandbox metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/sandbox.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/sandbox.go

This file defines the internal CRI sandbox object and concurrent sandbox store. `Sandbox` embeds immutable metadata, status storage, sandboxer name, optional network namespace handle, stop channel, cached CPU stats for the sandbox/pause container, and an endpoint used for task or streaming API connections. `Endpoint.IsValid` checks for a non-empty address.

`NewSandbox` installs in-memory status storage and a stop channel, and marks the sandbox stopped immediately when initial state is `StateNotReady`. `Store` maintains sandboxes by full ID, a truncation index, a shared SELinux label store, and optional stats collector. `Add` rejects duplicates, reserves process labels, inserts the ID into the truncation index, stores the sandbox, and registers the ID with the stats collector. `Get` supports truncated ID lookup. `List` returns a snapshot slice. `UpdateContainerStats` replaces cached stats for an existing sandbox. `Delete` releases labels, removes the ID and map entry, and unregisters the stats collector.

State is in-memory; sandbox status is not checkpointed by this package, while metadata persistence is handled elsewhere. Risks include returning value copies with embedded mutable pointers, label balancing, truncation ambiguity, stats cache replacement, and not-ready initial state affecting wait behavior. Tests cover add/get/list/delete, unknown state retrieval, truncated IDs, duplicate errors, stats updates, and not-found after deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/sandbox_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/sandbox_test.go

This test file validates sandbox store behavior. `TestSandboxStore` constructs several sandboxes in ready and not-ready states plus one unknown-state sandbox, adds them to a store, retrieves normal sandboxes by truncated IDs, retrieves the unknown sandbox by full ID, lists all sandboxes, updates cached stats, checks duplicate add errors, deletes sandboxes by truncated IDs, and verifies deleted IDs return `errdefs.ErrNotFound`.

The test confirms that `NewSandbox` objects with different states can coexist in the store and that unknown state does not prevent retrieval. It also verifies `UpdateContainerStats` persists new cached stats into stored sandbox values visible through `List`.

The test signal covers basic map/index behavior, truncated-ID lookup, duplicate detection, stats cache mutation, and deletion. It does not exercise SELinux label reservation callbacks, stats collector add/remove callbacks, endpoint validity, network namespace cleanup, concurrent access, or stop-channel behavior directly. The stop-channel behavior for not-ready sandboxes is covered indirectly by `sandbox_stop_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/sandbox_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/status.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/status.go

This file defines the internal sandbox state machine and in-memory status storage. `State` has three values: `StateReady`, `StateNotReady`, and `StateUnknown`. `State.String` maps ready/not-ready to CRI enum string names, maps unknown to `SANDBOX_UNKNOWN` even though CRI has no unknown enum, and formats invalid values with the numeric value.

`Status` records sandbox process PID, creation time, exit time, exit status, internal state, and optional pod-level `Overhead` and `Resources` as CRI `ContainerResources`. These resource fields are updated by `UpdatePodSandboxResources` and later surfaced by status verbose info.

`StatusStorage` is intentionally simpler than container status storage: comments state sandbox status is not checkpointed, and future checkpointing should combine with the container status storage pattern. `StoreStatus` returns a mutex-protected `statusStorage`. `Get` returns the status value. `Update` applies an `UpdateFunc` transaction under lock and rolls back on error.

There is no disk persistence. Dependencies include CRI runtime types, time, strconv, and sync. Risks include no deep-copy for pointer resource fields, in-memory-only loss across restart, unknown state mapping requiring later CRI conversion to not-ready, and callers needing to use `Update` for atomicity. Tests cover update rollback/success and state string conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/status_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/status_test.go

This test file validates sandbox status storage transactions and state string conversion. `TestStatus` creates an initial status with PID, creation time, and unknown state, stores it with `StoreStatus`, and confirms `Get` returns the same value. It then applies an update function returning an error and verifies the stored status remains unchanged. A successful update changes the in-memory status to a ready state with a new PID and creation time.

`TestStateStringConversion` verifies `StateReady`, `StateNotReady`, and `StateUnknown` string values, plus formatting for an invalid numeric state. This matters because server-side status conversion uses these strings to map to CRI enums, and unknown must remain distinguishable internally even though CRI maps it to not-ready.

The tests cover rollback and simple mutation but not concurrent updates, pointer resource aliasing, overhead/resource fields, stop-channel side effects, or integration with `PodSandboxStatus`. They also intentionally do not test checkpointing because sandbox status storage is in-memory only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/sandbox/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/snapshot/snapshot.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/snapshot/snapshot.go

This file implements a small in-memory snapshot usage cache. `Key` identifies a snapshot by logical key and snapshotter name, preventing collisions between snapshotters. `Snapshot` records the key, snapshot kind, size in bytes, inode count, and latest update timestamp in nanoseconds.

`Store` wraps a map from `Key` to `Snapshot` with an RW mutex. `NewStore` initializes the map. `Add` upserts a snapshot. `Get` returns a snapshot or `errdefs.ErrNotFound`. `List` returns a snapshot slice of current values. `Delete` removes a key without error.

There is no disk persistence in this package; it caches information gathered elsewhere, and consumers such as Windows pod stats use it to fill writable-layer usage. Dependencies are containerd snapshot kinds and errdefs. Risks include stale size/inode data if callers do not refresh it, map iteration order in `List`, no truncated lookup, and silent delete of missing keys. Tests cover add/get/list/delete and key separation by snapshotter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/snapshot/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/snapshot/snapshot_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/snapshot/snapshot_test.go

This test file validates the snapshot store's keying and basic operations. `TestSnapshotStore` creates three snapshots: two keys in one snapshotter and one same logical key in a different snapshotter. It adds them, retrieves each by full `Key`, lists all snapshots, attempts to delete an invalid key, deletes one valid key, and verifies the deleted key returns an empty snapshot plus `errdefs.ErrNotFound`.

The test confirms that `Key{Key, Snapshotter}` is the identity, not just the snapshot key string, and that delete is a no-op for missing keys. It also covers different snapshot kinds and metadata fields in stored values.

The test signal is intentionally narrow. It does not exercise concurrent access, stale update replacement semantics beyond initial add, ordering of `List`, or integration with image filesystem stats. It guards the in-memory cache behavior used by CRI stats paths, especially writable-layer lookup by container ID plus runtime snapshotter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/snapshot/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/stats/stats.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/stats/stats.go

This file defines `ContainerStats`, the minimal cached CPU sample used by CRI stores and stats conversion code. It contains `Timestamp`, the time at which stats were collected, and `UsageCoreNanoSeconds`, cumulative CPU usage across all cores since object creation.

The type is intentionally simple and has no methods, synchronization, persistence, or dependencies beyond Go `time`. It is embedded by pointer in `containerstore.Container.Stats` and `sandboxstore.Sandbox.Stats`, updated by Windows sandbox stats through `saveSandBoxMetrics`, and complemented by Linux `TimedStore` samples in `timed_store.go` and `StatsCollector`.

Its integration role is to provide the previous CPU cumulative sample required to compute instantaneous `UsageNanoCores`. Risks are semantic rather than structural: callers must keep timestamp and cumulative value from the same measurement, handle nil pointers for first sample/no data, and avoid using stale or reset cumulative counters without guard logic. Windows `getUsageNanoCores` currently does not check for decreasing cumulative values, while `TimedStore` does. Tests cover usage indirectly in Windows stats, container/sandbox store stats updates, and timed-store calculations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/stats/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/stats/timed_store.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/stats/timed_store.go

This file implements `TimedStore`, a thread-safe time-ordered buffer of CPU samples. `CPUSample` stores timestamp, cumulative `UsageCoreNanoSeconds`, and calculated instantaneous `UsageNanoCores`. `NewTimedStore` configures retention age and max item count, with `-1` meaning no item limit.

`Add` creates a new sample, calculates nanocores from the last sample if present, appends fast-path in timestamp order or inserts out of order using binary search, recalculates affected rates for out-of-order insertion, evicts samples older than `timestamp - age` using a strict-after search, and trims to the newest `maxItems`. `GetLatest`, `GetLatestUsageNanoCores`, and `Size` use read locks. `calculateUsageNanoCores` returns zero for zero/negative intervals or decreasing cumulative usage, otherwise scales the usage delta by elapsed nanoseconds to nanocores.

State is entirely in-memory under an RW mutex and used by Linux `StatsCollector` per container/sandbox ID. Risks include out-of-order first rate initially using the previous last sample before recalculation, strict eviction excluding samples exactly at the cutoff, float conversion for large counters, and no persistence across restarts. Tests cover empty behavior, first/second sample rates, half-core math, max item and age eviction, concurrent access, and invalid delta/decreasing counter cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/stats/timed_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/stats/timed_store_test.go -->
# Research: sources/cloud-native/containerd/internal/cri/store/stats/timed_store_test.go

This test file validates `TimedStore` behavior. Basic tests confirm a new store is empty, `GetLatest` returns nil, and `GetLatestUsageNanoCores` reports false until at least two samples exist. Add/get tests verify the first sample stores cumulative CPU but has zero calculated nanocores.

Rate tests check one-core and half-core calculations from cumulative CPU deltas over one- and two-second intervals. Capacity tests verify `maxItems` retains only newest samples, and age eviction keeps samples strictly after the eviction time. `TestTimedStoreConcurrentAccess` runs multiple writer and reader goroutines and asserts no panic plus bounded size. `TestCalculateUsageNanoCores` covers normal one-core/two-core calculations, zero time delta, negative time delta, and CPU usage decreasing after restart.

The test signal is strong for math and in-memory concurrency but does not cover out-of-order insertion explicitly, no-limit max item behavior beyond age eviction, float precision at very large counters, or integration with Linux `StatsCollector`. It guards the core correctness of `UsageNanoCores` values used by CRI stats responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/stats/timed_store_test.go -->
