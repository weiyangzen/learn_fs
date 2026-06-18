# subset-b-000088 Research

Grouped research for CRI-O internal configuration helpers, CLI commands, dbus/systemd integration, and container factory code. Each source file has a marker-bounded section for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr_test.go -->
# sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr_test.go

Purpose: exercises the CNI manager readiness state machine, watcher notification behavior, shutdown semantics, garbage-collection deferral, and optional continuous health monitoring grace period. The file is test-only but documents the intended contract for `CNIManager` more completely than many callers do.

Important APIs/types/functions: `fakeCNIPlugin` implements the `ocicni.CNIPlugin` surface used by the manager, including `Status`, `StatusWithContext`, `GC`, pod setup/teardown, and network status methods. `newTestManager`, `newTestManagerWithGrace`, and `waitFor` build deterministic polling tests around short intervals and timeout guards. Main tests are `TestStatusPolling` and `TestGracePeriod`.

Control flow: tests start a manager with a fake plugin, mutate `statusErr`, and wait for `ReadyOrError` transitions. They verify initial readiness, startup recovery, runtime failure detection, recovery after failure, repeated flaps, shutdown cancellation, watcher delivery for ready/recovery/shutdown/already-ready states, abandoned watcher nonblocking behavior, GC on startup readiness, immediate GC when already ready, deferred GC when not ready, and GC error propagation.

State and persistence behavior: all state is in-memory test state: fake plugin status protected by a mutex, `gcCalls` as an atomic counter, manager readiness/error fields behind manager locks, watcher channels, and context cancellation. No disk persistence is used.

Dependencies/integration points: depends on `github.com/cri-o/ocicni/pkg/ocicni`, Go `testing`, `context`, `sync`, `atomic`, and `time`. It directly constructs a `CNIManager`, bypassing `New`, so it verifies manager internals and polling behavior without real CNI files or plugins.

Risks: timing-based tests can be sensitive to slow hosts because they rely on sleeps and polling deadlines. Since fake plugin methods mostly return nil for non-status operations, the tests do not validate real CNI setup/teardown behavior. The direct struct construction may miss initialization differences in `New`.

Test signals: this is the primary test signal for CNI manager health reporting. It gives strong coverage for readiness state transitions, watcher behavior, shutdown error reporting, and GC scheduling around readiness.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr_test_inject.go -->
# sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr_test_inject.go

Purpose: provides a `test` build-tag injection hook for replacing the CNI plugin inside an existing `CNIManager` during tests.

Important APIs/types/functions: `(*CNIManager).SetCNIPlugin(plugin ocicni.CNIPlugin) error` shuts down any currently installed plugin, assigns the supplied plugin, and calls `statusPollFunc` once to initialize readiness state without launching a racing background poller.

Control flow: when called, it first invokes `Shutdown` on the old plugin if present, returns that error if shutdown fails, replaces `c.plugin`, and performs a synchronous status poll with `isStartup=false`, ignoring the returned status/error intentionally for test setup.

State and persistence behavior: mutates only the in-memory `CNIManager.plugin` and readiness fields updated by `statusPollFunc`. It has no persistent storage behavior.

Dependencies/integration points: imports `context` and `ocicni`. The build tag `//go:build test` keeps this helper out of normal CRI-O binaries while allowing test code to control the otherwise internal plugin dependency.

Risks: because it ignores the poll result, callers must inspect manager state separately. The helper mutates manager internals and can race if used against a manager with active polling; the comment explicitly frames it as a way to avoid races in mocked setup.

Test signals: no independent tests in this file; it supports tests that need CNI plugin injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/cnimgr/cnimgr_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/conmonmgr/conmonmgr.go -->
# sources/cloud-native/cri-o/internal/config/conmonmgr/conmonmgr.go

Purpose: probes the configured `conmon` binary and records feature support gates derived from its semantic version and help output. CRI-O uses this to decide whether it can pass newer conmon options.

Important APIs/types/functions: `ConmonManager` stores `conmonVersion`, `supportsSync`, and `supportsLogGlobalSizeMax`. `New(conmonPath)` validates an absolute path, runs `conmon --version`, parses the third field as semver, and initializes feature booleans. `parseConmonVersion`, `initializeSupportsLogGlobalSizeMax`, `SupportsLogGlobalSizeMax`, `initializeSupportsSync`, and `SupportsSync` are the core helpers.

Control flow: `New` fails early for relative paths, failed command execution, short version output, or invalid semver. Sync support is pure version comparison against `2.0.19`. Log global size support is true at `2.1.2` or higher, otherwise it falls back to `conmon --help` and checks for `--log-global-size-max`, allowing backports.

State and persistence behavior: state is process-local inside the manager. It shells out through `cmdrunner` but writes no files. Feature detection logs informational messages through logrus.

Dependencies/integration points: depends on `github.com/blang/semver/v4`, logrus, and CRI-O `utils/cmdrunner`. It integrates with runtime/conmon launch configuration by exposing feature predicates to callers.

Risks: version parsing assumes `conmon --version` has at least three fields and the version is field 3. A nonstandard backported build can still be detected for only `--log-global-size-max`, not `--sync`. Help-output probing is best-effort and silent on command failure.

Test signals: companion tests mock `cmdrunner` to cover path validation, command failure, short output, version parsing, semver threshold boundaries, and help-output backport detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/conmonmgr/conmonmgr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/conmonmgr/conmonmgr_test.go -->
# sources/cloud-native/cri-o/internal/config/conmonmgr/conmonmgr_test.go

Purpose: validates `ConmonManager` construction and feature-detection rules without invoking a real conmon binary.

Important APIs/types/functions: uses `runnerMock.MockCommandRunner`, `cmdrunner.SetMocked`, and Ginkgo/Gomega test cases around `New`, `parseConmonVersion`, `initializeSupportsSync`, and `initializeSupportsLogGlobalSizeMax`.

Control flow: setup installs a mocked command runner. Tests assert failure for non-absolute paths, failed version command, malformed version output, and invalid semver. Threshold tables are expressed as individual examples for major/minor/patch/equal comparisons. Log-global-size tests additionally mock `--help` output for versions below the threshold.

State and persistence behavior: modifies global cmdrunner mock state for the test process. No disk state is used.

Dependencies/integration points: depends on Ginkgo/Gomega, gomock, CRI-O test mocks, and `cmdrunner`. It verifies the integration contract between the manager and the shell-command abstraction.

Risks: command expectations use broad `gomock.Any()` arguments, so they primarily verify behavior outcome rather than exact `--version`/`--help` invocation shape. Tests do not cover unusual version strings with prefixes or build metadata.

Test signals: strong unit coverage for conmon feature gates and error paths, including the backported `--log-global-size-max` fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/conmonmgr/conmonmgr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/conmonmgr/suite_test.go -->
# sources/cloud-native/cri-o/internal/config/conmonmgr/suite_test.go

Purpose: bootstraps the Ginkgo suite for the conmon manager package.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`. `BeforeSuite` creates a CRI-O `TestFramework`, stores `mockCtrl` from the framework for gomock usage, and calls setup; `AfterSuite` tears it down.

Control flow: Go test calls `TestLibConfig`, which registers Gomega failure handling and runs framework specs named `ConmonManagerConfig`. Suite hooks prepare and clean test framework state.

State and persistence behavior: owns process-local suite state and any temporary framework resources. No package behavior is implemented here.

Dependencies/integration points: integrates Ginkgo/Gomega with `github.com/cri-o/cri-o/test/framework`.

Risks: package tests depend on correct global framework setup; failures here can prevent all conmon manager tests from running.

Test signals: suite harness only; behavioral signal lives in `conmonmgr_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/conmonmgr/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/device/device_linux.go -->
# sources/cloud-native/cri-o/internal/config/device/device_linux.go

Purpose: parses configured and annotation-provided Linux device mappings into OCI runtime-spec device and cgroup resource entries.

Important APIs/types/functions: `Config` stores parsed `[]Device`; `Device` wraps `rspec.LinuxDevice` and `rspec.LinuxDeviceCgroup`; `New`, `LoadDevices`, `Devices`, and `DevicesFromAnnotation` are public. Internal helpers are `devicesFromStrings`, `parseDevice`, and `isValidDeviceMode`. `DeviceAnnotationDelim` is the comma delimiter for `io.kubernetes.cri-o.Devices`.

Control flow: `LoadDevices` parses admin-configured entries with no allow-list. `DevicesFromAnnotation` builds an allow map from configured allowed devices and parses comma-separated annotation entries. Each non-empty entry becomes `src`, `dst`, and permissions, must have an allowed source if an allow map is supplied, must map into `/dev/`, and must resolve through `devices.DeviceFromPath`. Parsed libcontainer device metadata is copied into OCI device and cgroup structures.

State and persistence behavior: parsed devices are cached in memory on `Config` so CRI-O validates configuration early and reuses normalized structures. It reads host device metadata through `DeviceFromPath`; it does not persist data.

Dependencies/integration points: depends on opencontainers runtime spec and runc/libcontainer devices. The container factory later consumes `device.Device` values to add devices and cgroup permissions to generated specs.

Risks: `parseDevice` uses colon splitting, so paths containing colons are unsupported. Destination validation only checks `/dev/` prefix, and source authorization checks only the source string. Device existence/type validation is host-dependent, making behavior vary across platforms and test environments.

Test signals: `device_test.go` covers malformed mappings, nonexistent devices, valid `/dev/null`, empty entries, annotation allow-list enforcement, and mixed invalid annotation inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/device/device_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/device/device_test.go -->
# sources/cloud-native/cri-o/internal/config/device/device_test.go

Purpose: unit-tests Linux device configuration parsing and annotation allow-list handling.

Important APIs/types/functions: creates `device.Config` with `device.New`, exercises `LoadDevices`, `Devices`, and `DevicesFromAnnotation` using Ginkgo/Gomega examples.

Control flow: tests verify that `invalid:invalid` fails as a malformed destination/mode, `/dev/invalid` fails host device resolution, `/dev/null:/dev/null:w` succeeds, and empty config entries are ignored. Annotation tests add source allow-lists and verify invalid format, invalid host device, successful allowed `/dev/null`, failure when one of multiple devices is invalid, empty annotation no-op, and rejection when the device is not in `allowed_devices`.

State and persistence behavior: test state is local `*device.Config`. Host dependency is `/dev/null` existing and `/dev/invalid` not being a valid device.

Dependencies/integration points: depends on Ginkgo/Gomega and the device package. It indirectly depends on the host device table through `DeviceFromPath`.

Risks: the tests are Linux-specific by package behavior; host device assumptions may not hold in unusual sandboxes. They do not cover destination outside `/dev` with an otherwise valid source, duplicate mode letters, or all permission combinations.

Test signals: good coverage for core parsing and annotation allow-list contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/device/device_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/device/device_unsupported.go -->
# sources/cloud-native/cri-o/internal/config/device/device_unsupported.go

Purpose: supplies no-op device configuration behavior for non-Linux builds.

Important APIs/types/functions: empty `Device` and `Config` structs; `New`, `LoadDevices`, `Devices`, and `DevicesFromAnnotation` keep the same public API as Linux. `LoadDevices` always returns nil, `Devices` returns nil, and annotation parsing returns an empty slice.

Control flow: no parsing or validation occurs under the `!linux` build tag.

State and persistence behavior: no state is stored, and no device filesystem access is performed.

Dependencies/integration points: selected by build tags to let shared CRI-O configuration code compile on unsupported platforms without Linux device injection.

Risks: non-Linux builds silently ignore configured or annotated devices, which is appropriate for portability but can surprise callers expecting validation parity.

Test signals: no direct tests in this file; Linux behavior is covered separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/device/device_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/device/suite_test.go -->
# sources/cloud-native/cri-o/internal/config/device/suite_test.go

Purpose: Ginkgo suite bootstrap for the device configuration tests.

Important APIs/types/functions: `TestDeviceConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers the Gomega fail handler, runs framework specs named `DeviceConfig`, creates the CRI-O test framework before the suite, and tears it down afterward.

State and persistence behavior: owns only test framework lifecycle state.

Dependencies/integration points: integrates Ginkgo/Gomega with CRI-O `test/framework`.

Risks: suite-level setup failure prevents all device tests from executing.

Test signals: harness only; parsing behavior is in `device_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/device/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/cgroups_linux.go -->
# sources/cloud-native/cri-o/internal/config/node/cgroups_linux.go

Purpose: detects host cgroup mode and controller availability for Linux CRI-O configuration validation and resource application.

Important APIs/types/functions: `CgroupIsV2`, `CgroupHasMemorySwap`, `CgroupHasHugetlb`, `CgroupHasPid`, and `checkRelevantControllers`. Package globals cache results and errors via `sync.Once`: memory swap, controller lookup, hugetlb, pid, and cgroup v2 errors.

Control flow: `CgroupIsV2` calls `cgroups.IsCgroup2UnifiedMode` each time and stores the error. `CgroupHasMemorySwap` is once-only; on cgroup v2 it parses `/proc/self/cgroup` and checks `memory.swap.current` under `/sys/fs/cgroup`, while cgroup v1 checks `memory.memsw.limit_in_bytes`. `CgroupHasHugetlb` and `CgroupHasPid` call `checkRelevantControllers`, which reads all subsystems and marks `pids`/`hugetlb` when present.

State and persistence behavior: caches detection booleans/errors in package globals. Reads kernel pseudo-filesystems but writes nothing.

Dependencies/integration points: uses `github.com/opencontainers/cgroups` and `go.podman.io/common/pkg/cgroups`. `node.ValidateConfig` and container resource setup consume these booleans to fail early or skip unsupported resource fields.

Risks: once-only caching means controller state changes after startup are ignored. Error globals are package-level and can be overwritten for cgroup v2 detection. The cgroup v2 memory swap path assumes `cg[""]` from parsed `/proc/self/cgroup` maps correctly to the unified hierarchy.

Test signals: no local tests in this subset; behavior is indirectly exercised through configuration validation and container resource paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/cgroups_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/cgroups_unsupported.go -->
# sources/cloud-native/cri-o/internal/config/node/cgroups_unsupported.go

Purpose: provides non-Linux stubs for cgroup detection functions.

Important APIs/types/functions: `CgroupIsV2`, `CgroupHasMemorySwap`, `CgroupHasHugetlb`, and `CgroupHasPid` all return false.

Control flow: no host probing is performed.

State and persistence behavior: no state and no filesystem access.

Dependencies/integration points: selected by `!linux` builds to preserve shared call sites in config validation and container resource generation.

Risks: non-Linux callers that rely on positive cgroup capabilities will never see them, so Linux-only resource behavior is disabled.

Test signals: no direct tests; stub behavior is trivial.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/cgroups_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/node_freebsd.go -->
# sources/cloud-native/cri-o/internal/config/node/node_freebsd.go

Purpose: implements FreeBSD node configuration validation as a no-op placeholder.

Important APIs/types/functions: `ValidateConfig() error` returns nil.

Control flow: callers can invoke `ValidateConfig` uniformly across platforms; FreeBSD performs no singleton probing in this file.

State and persistence behavior: no state and no persistence.

Dependencies/integration points: platform variant for the shared `node` package.

Risks: missing FreeBSD-specific validation means configuration errors may surface later at runtime as platform support grows.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/node_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/node_linux.go -->
# sources/cloud-native/cri-o/internal/config/node/node_linux.go

Purpose: performs early Linux node capability validation for CRI-O startup.

Important APIs/types/functions: `ValidateConfig` iterates a table of checks: hugetlb cgroup, pid cgroup, memory swap cgroup, cgroup v2, systemd `AllowedCPUs`, and `fs.may_detach_mounts`. Each entry has an init function, error pointer, activation pointer, and fatal flag.

Control flow: the function initializes cgroup mode first, then runs each table entry. If an error occurred, fatal entries return an error while nonfatal entries log warnings. If a fatal capability is not activated, it returns an error; if nonfatal inactive, it logs at info level. Successful activation is logged at debug level.

State and persistence behavior: triggers package-level singleton caches in cgroup, systemd, and sysctl helper files. It reads host state but writes nothing.

Dependencies/integration points: integrates with `CgroupHas*`, `CgroupIsV2`, `SystemdHasAllowedCPUs`, and `checkFsMayDetachMounts`. Startup configuration validation calls this to fail before container creation paths rely on missing kernel/systemd features.

Risks: depends on mutable package globals, so tests need isolation if added. Nonfatal checks may hide degraded behavior that later affects resource management. The fatal/nonfatal classification is policy-sensitive.

Test signals: no direct tests in this subset; behavior is indirectly depended on by server config validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/node_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/node_unsupported.go -->
# sources/cloud-native/cri-o/internal/config/node/node_unsupported.go

Purpose: provides a generic unsupported-platform `ValidateConfig` stub.

Important APIs/types/functions: `ValidateConfig() error` returns nil under `!linux && !freebsd`.

Control flow: no validation work.

State and persistence behavior: none.

Dependencies/integration points: platform compilation shim for shared callers.

Risks: unsupported builds do not receive early validation and may fail later where platform features are needed.

Test signals: no tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/node_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/sysctl_linux.go -->
# sources/cloud-native/cri-o/internal/config/node/sysctl_linux.go

Purpose: validates Linux sysctl state needed for CRI-O mount cleanup behavior.

Important APIs/types/functions: package variable `checkFsMayDetachMountsErr`; function `checkFsMayDetachMounts() bool`.

Control flow: reads `/proc/sys/fs/may_detach_mounts` through `os.ReadFile`. On read failure it stores the error and returns false. If the trimmed value is not `"1"`, it records an explanatory error and returns false. Otherwise it returns true.

State and persistence behavior: records the last error in a package global but does not cache with `sync.Once`; each call rereads the procfs value.

Dependencies/integration points: used by `node.ValidateConfig` as a fatal Linux startup validation item.

Risks: hard-fails startup when the sysctl is missing or disabled; this is correct for expected CRI-O mount semantics but may be problematic in constrained or unusual kernels. The global error can be overwritten by repeated calls.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/sysctl_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/systemd_linux.go -->
# sources/cloud-native/cri-o/internal/config/node/systemd_linux.go

Purpose: detects whether the host systemd supports specific cgroup properties used by CRI-O.

Important APIs/types/functions: globals `systemdHasAllowedCPUsOnce`, `systemdHasAllowedCPUs`, and `systemdHasAllowedCPUsErr`; `SystemdHasAllowedCPUs`; and `systemdSupportsProperty(property string)`.

Control flow: `SystemdHasAllowedCPUs` caches a call to `systemdSupportsProperty("AllowedCPUs")`. The helper connects to systemd D-Bus with `dbus.NewSystemdConnection`, closes it on return, and calls `GetManagerProperty` to see whether the property is available.

State and persistence behavior: caches the boolean and error in package globals. It opens a transient D-Bus connection but writes no persistent state.

Dependencies/integration points: depends on `github.com/coreos/go-systemd/v22/dbus`; used by `node.ValidateConfig` as a nonfatal feature check for cgroup/systemd CPU controls.

Risks: startup behavior depends on systemd D-Bus availability. Result caching means a systemd upgrade/restart after first check is not observed until process restart.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/systemd_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/systemd_unsupported.go -->
# sources/cloud-native/cri-o/internal/config/node/systemd_unsupported.go

Purpose: provides non-Linux systemd feature stubs.

Important APIs/types/functions: `SystemdHasCollectMode`, `SystemdHasAllowedCPUs`, and `systemdSupportsProperty`. Both public checks return false; the helper returns false with nil error.

Control flow: no D-Bus probing.

State and persistence behavior: none.

Dependencies/integration points: selected on unsupported platforms to keep shared node validation code compiling.

Risks: all systemd-dependent feature detection is disabled on non-Linux builds.

Test signals: no tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/node/systemd_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nri/nri.go -->
# sources/cloud-native/cri-o/internal/config/nri/nri.go

Purpose: models CRI-O configuration for NRI, converts it to containerd NRI adaptation options, and applies NRI timeout globals.

Important APIs/types/functions: `Config` holds enablement, socket path, plugin path/config path, registration/request timeouts, connection disabling, tracing flag, and `DefaultValidator`. `DefaultValidatorConfig` mirrors validator plugin policy. Public methods include `New`, `IsDefaultValidatorDefaultConfig`, `Validate`, `WithTracing`, `ToOptions`, `ConfigureTimeouts`, and `DefaultValidatorConfig.ToNRI`.

Control flow: `New` populates containerd NRI defaults and an empty validator config. `defaultValidatorEqual` compares every validator field and compares `RequiredPlugins` after sorting, making ordering irrelevant. `ToOptions` appends options only for non-empty/non-nil settings, adds disabled external connections when requested, maps the default validator, and injects OpenTelemetry ttrpc interceptors when tracing is enabled. `ConfigureTimeouts` sets global NRI timeouts only when durations are nonzero.

State and persistence behavior: config state is in memory. `ConfigureTimeouts` mutates package-level NRI adaptation timeouts. No files are read or written.

Dependencies/integration points: integrates `github.com/containerd/nri/pkg/adaptation`, `github.com/containerd/nri/plugins/default-validator`, ttrpc, and otel ttrpc. CLI merge code writes these fields from flags; server startup consumes `ToOptions` and timeout configuration.

Risks: `Validate` currently returns nil, so bad paths or policy combinations are not checked here. `ToOptions` dereferences `c.withTracing` after nil-guarded blocks; because it uses `if c.withTracing`, callers must not call `ToOptions` on nil if tracing path might be evaluated. Global timeout mutation affects the process.

Test signals: no direct tests in this subset; CLI tests touch only selected NRI flag merging indirectly through config metadata shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nri/nri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_freebsd.go -->
# sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_freebsd.go

Purpose: implements a minimal FreeBSD namespace manager focused on jail/network namespace placeholders.

Important APIs/types/functions: `NamespaceManager` stores `namespacesDir` and `pinnsPath`; `New`, `Initialize`, `NewPodNamespaces`, `NamespacePathFromProc`, and `NamespaceFromProcEntry`.

Control flow: `Initialize` creates the namespace root directory. `NewPodNamespaces` rejects nil configs, returns an empty slice for no namespaces, and otherwise returns a `namespace` object for each non-host namespace using the namespace type string as the jail name. Host namespaces are skipped. `NamespacePathFromProc` always returns an empty string, and `NamespaceFromProcEntry` reports that proc-entry pinning is unsupported.

State and persistence behavior: creates `namespacesDir` with mode `0755`; namespace objects are in-memory and do not bind mount or persist real namespace files.

Dependencies/integration points: FreeBSD build variant sharing the common `nsmgr` API used by sandbox/container setup.

Risks: functionality is intentionally much thinner than Linux. `pinnsPath` is stored but unused. Host namespace skipping and synthetic jail names may need expansion for richer FreeBSD support.

Test signals: no direct FreeBSD tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_linux.go -->
# sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_linux.go

Purpose: manages Linux namespace lifecycle for pods by preparing namespace directories, invoking `pinns`, and pinning namespaces from existing process entries.

Important APIs/types/functions: `NamespaceManager` with `namespacesDir` and `pinnsPath`; `New`, `Initialize`, `NewPodNamespaces`, `chownDirToIDPair`, `getMappingsForPinns`, `NamespaceFromProcEntry`, `dirForType`, and `NamespacePathFromProc`.

Control flow: `Initialize` creates the root directory and subdirectories for supported namespace types, replacing files that block directory creation. `NewPodNamespaces` validates config, builds pinns arguments from requested namespace types, host mode, sysctls, and optional ID mappings, precomputes pin paths, optionally chowns pin directories, invokes `pinns`, cleans up mount points on failure, and returns `Namespace` handles from the generated paths. `NamespaceFromProcEntry` creates a pin file, validates `/proc/<pid>/ns/<type>`, bind-mounts it, and returns a namespace wrapper, cleaning up on errors.

State and persistence behavior: persists namespace bind-mount paths under `namespacesDir/<type>ns/<uuid>`. It may chown paths to mapped root IDs. Removal is delegated to namespace objects in `types_linux.go`.

Dependencies/integration points: uses CNI ns package, Google UUID, logrus, storage idtools, unix mount/unmount, CRI-O `utils`, and `cmdrunner`. Integrates with pod sandbox creation and container namespace sharing.

Risks: namespace path checks are inherently racy with infra container PID lifetime. Failure cleanup must unmount partially created paths. Mapping format must match `pinns` expectations. `typeToArg` omits PID namespace creation in this function, so unsupported types fail.

Test signals: no direct tests here; `nsmgr/test/utils.go` supplies spoofed namespace helpers for other tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_unsupported.go -->
# sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_unsupported.go

Purpose: provides namespace manager stubs for platforms other than Linux and FreeBSD.

Important APIs/types/functions: empty `NamespaceManager`; `New`, `Initialize`, `GetNamespace`, `NamespacePathFromProc`, and `NamespaceFromProcEntry`.

Control flow: construction succeeds, initialization returns nil, but namespace retrieval and proc-entry pinning return unsupported errors or empty paths.

State and persistence behavior: no state, directories, or mounts are created.

Dependencies/integration points: compile-time compatibility shim for shared CRI-O namespace management call sites.

Risks: callers must handle unsupported errors where namespace lifecycle management is required.

Test signals: no tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/test/utils.go -->
# sources/cloud-native/cri-o/internal/config/nsmgr/test/utils.go

Purpose: supplies lightweight namespace and container fixtures for tests outside `nsmgr`.

Important APIs/types/functions: `SpoofedNamespace` implements `nsmgr.Namespace` plus `Close`; `AllSpoofedNamespaces` provides net, ipc, uts, user, and pid namespace instances; `ContainerWithPid(pid int)` returns an `oci.Container` with a Linux spec containing the requested process PID.

Control flow: `SpoofedNamespace` methods return stored type/path, and `Remove`/`Close` are no-ops. `ContainerWithPid` constructs a new `oci.Container`, sets its spec to `rspec.Spec{Linux: &rspec.Linux{Namespaces: []rspec.LinuxNamespace{}}, Process: &rspec.Process{}}`, and writes `State().Pid`.

State and persistence behavior: all fixtures are in-memory. No namespace files or mounts are created.

Dependencies/integration points: used by container namespace tests and other packages that need namespace-shaped values without actual kernel namespace operations. Depends on CRI-O `oci` and runtime-spec types.

Risks: no-op removal means tests using these fixtures cannot catch cleanup failures. The spoofed paths are plain strings and are not validated.

Test signals: helper only; coverage appears in consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/test/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/types.go -->
# sources/cloud-native/cri-o/internal/config/nsmgr/types.go

Purpose: defines the platform-independent namespace type names and public namespace interface.

Important APIs/types/functions: `NSType` string alias; constants `NETNS`, `IPCNS`, `UTSNS`, `USERNS`, `PIDNS`, and `ManagedNamespacesNum`; interface `Namespace` with `Path`, `Type`, and `Remove`.

Control flow: no executable logic; this is the shared contract consumed by platform-specific namespace managers and container factory code.

State and persistence behavior: none.

Dependencies/integration points: imported by `nsmgr` platform files and by container factory code that tracks PID namespaces.

Risks: `ManagedNamespacesNum` must remain synchronized with the namespace constants supported by platform implementations.

Test signals: no direct tests; implementations and consumers exercise the interface.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/types_freebsd.go -->
# sources/cloud-native/cri-o/internal/config/nsmgr/types_freebsd.go

Purpose: supplies FreeBSD namespace type/config structures and a minimal namespace implementation.

Important APIs/types/functions: `supportedNamespacesForPinning` returns only `NETNS`; `PodNamespacesConfig`, `PodNamespaceConfig`, internal `namespace`, `Path`, `Type`, `Remove`, and `GetNamespace`.

Control flow: `Remove` is idempotent via a mutex and `closed` flag. `GetNamespace` wraps a jail name into a namespace object without validation.

State and persistence behavior: namespace state is in memory (`closed`, `nsType`, `jailName`). No files or mounts are manipulated.

Dependencies/integration points: FreeBSD variant used by `nsmgr_freebsd.go` and shared callers.

Risks: only network namespace pinning is represented, and jail names are not validated.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/types_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/types_linux.go -->
# sources/cloud-native/cri-o/internal/config/nsmgr/types_linux.go

Purpose: implements the Linux namespace object model and namespace path validation/opening.

Important APIs/types/functions: `supportedNamespacesForPinning`, `PodNamespacesConfig`, `PodNamespaceConfig`, internal `namespace`, `NS` interface wrapper around CNI `NetNS`, `Path`, `Type`, `Remove`, and `GetNamespace`.

Control flow: `supportedNamespacesForPinning` lists net, ipc, uts, user, and pid. `Remove` locks, closes the namespace handle if open, marks it closed, checks the path, detaches any mount while ignoring `EINVAL`, and removes the path. `GetNamespace` calls `nspkg.GetNS`; on failure it returns a closed namespace with the path plus the error, allowing callers to track cleanup paths even when opening fails.

State and persistence behavior: namespace objects wrap an open namespace handle and a bind-mount path. `Remove` unmounts and deletes the pinned path from disk.

Dependencies/integration points: depends on CNI plugins `ns`, storage idtools via config types, and unix syscalls. Used by Linux namespace manager and container factory PID namespace tracking.

Risks: `Remove` is idempotent for closing but still attempts path cleanup; unmount/remove errors can propagate. Returning a namespace object alongside an error from `GetNamespace` requires callers to treat partial results carefully.

Test signals: no direct tests here; behavior is indirectly covered by namespace lifecycle consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/nsmgr/types_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/rdt/rdt.go -->
# sources/cloud-native/cri-o/internal/config/rdt/rdt.go

Purpose: manages CRI-O Intel RDT/resctrl configuration loading and container class lookup.

Important APIs/types/functions: constants `DefaultRdtConfigFile` and `ResctrlPrefix`; `Config` with `supported`, `enabled`, and `*rdt.Config`; `New`, `Supported`, `Enabled`, `Load`, `loadConfigFile`, and `ContainerClassFromAnnotations`.

Control flow: `New` sets the goresctrl logger, calls `rdt.Initialize`, and marks support false if initialization fails. `Load` disables the feature by default, exits successfully if unsupported or path is empty, reads YAML config, calls `rdt.SetConfig(tmpCfg, true)`, logs success, and stores the config while enabling RDT. `ContainerClassFromAnnotations` delegates class resolution to goresctrl and rejects non-empty classes when CRI-O RDT is disabled.

State and persistence behavior: loads YAML from disk and stores the parsed config in memory. It also configures goresctrl global RDT state through `Initialize` and `SetConfig`.

Dependencies/integration points: depends on `github.com/intel/goresctrl/pkg/rdt`, `sigs.k8s.io/yaml`, slog, and logrus. Container creation paths can use annotation-derived classes from this config.

Risks: host RDT support and resctrl mount state are external. Loading a config mutates global goresctrl state. Empty default path means RDT is opt-in.

Test signals: `rdt_test.go` covers missing files, invalid YAML shape, and a minimal valid config for `loadConfigFile`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/rdt/rdt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/rdt/rdt_test.go -->
# sources/cloud-native/cri-o/internal/config/rdt/rdt_test.go

Purpose: tests RDT YAML config file loading independently of host RDT enablement.

Important APIs/types/functions: `tempFileWithData` writes temporary test files; examples call unexported `loadConfigFile`.

Control flow: tests assert an error for a nonexistent file, an error for invalid config structure, and success for a minimal valid config containing a default partition, `l3Allocation`, and default class.

State and persistence behavior: writes temporary files through the CRI-O test framework and reads them through `loadConfigFile`.

Dependencies/integration points: uses Ginkgo/Gomega and the package-level test framework variable `t`. It validates the parser feeding `Config.Load`.

Risks: does not exercise `rdt.Initialize`, `rdt.SetConfig`, supported/disabled transitions, or annotation class enforcement.

Test signals: focused parser coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/rdt/rdt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/rdt/suite_test.go -->
# sources/cloud-native/cri-o/internal/config/rdt/suite_test.go

Purpose: Ginkgo suite bootstrap for RDT config tests.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers failure handling, runs framework specs named `RdtConfig`, and manages setup/teardown of the CRI-O test framework.

State and persistence behavior: suite-local framework state and temporary resources.

Dependencies/integration points: Ginkgo/Gomega and CRI-O `test/framework`.

Risks: harness failures block RDT tests.

Test signals: harness only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/rdt/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/notifier.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/notifier.go

Purpose: implements Linux seccomp user-notification socket handling for containers whose sandbox annotations request syscall tracing/action.

Important APIs/types/functions: `Notifier` wraps the Unix listener, syscall count map, expiry timer, and stop-containers policy. Public methods include `StopContainers`, `Close`, `AddSyscall`, `UsedSyscalls`, and `OnExpired`. `Notification` carries context, container ID, and syscall. Internal functions include `injectNotifier`, `NewNotifier`, `handler`, `handleNewMessage`, `closeStateFds`, and `parseStateFds`.

Control flow: `injectNotifier` gates on non-empty container ID, annotations, and message channel, then requires the seccomp notifier action annotation. It rewrites kill/errno syscall actions to `ActNotify`, sets `ListenerPath`, and starts a notifier. `NewNotifier` listens on a Unix socket, accepts runtime connections, receives a passed seccomp fd from OCI state, then spawns `handler`. `handler` receives one seccomp notification, sends a CRI-O notification, validates the ID, responds with `ENOSYS`, and exits. `parseStateFds` finds the named seccomp fd and closes unrelated received fds.

State and persistence behavior: creates a Unix socket at `NotifierPath/containerID`, holds listener state, counts syscalls in a `sync.Map`, and uses a timer for expiry callbacks. It closes file descriptors explicitly.

Dependencies/integration points: uses libseccomp-golang, runtime-spec seccomp state, Unix socket control messages, CRI-O annotations, and CRI-O logging. It is called from seccomp profile setup after profile conversion to runtime-spec format.

Risks: fd-passing parsing is strict about message sizes and SCM count. The accept goroutine lives until listener close. `OnExpired` refresh semantics depend on `Timer.Stop` behavior. Only the first syscall per fd is handled. Socket path parent creation is not handled here.

Test signals: no direct tests in this subset for notifier fd passing, action rewriting, timers, or socket lifecycle.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/notifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccomp.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/seccomp.go

Purpose: manages seccomp enablement, CRI-O’s adjusted default profile, profile loading, OCI artifact profile resolution, and application of selected profiles to OCI specs.

Important APIs/types/functions: `DefaultProfile`, `validateSyscallIndex`, `removeStringFromSlice`, `Config`, `New`, `SetNotifierPath`, `NotifierPath`, `LoadProfile`, `LoadDefaultProfile`, `IsDisabled`, `Profile`, `Setup`, and `applyProfileFromBytes`.

Control flow: `DefaultProfile` lazily clones Podman/common’s default profile, removes `clone`, `clone3`, and `unshare` from an allow list, re-adds them only for `CAP_SYS_ADMIN`, blocks namespace-creating `clone` for non-`CAP_SYS_ADMIN`, and makes non-admin `clone3` return `ENOSYS` for glibc fallback. `Setup` first lets OCI artifact annotations provide a profile when the security field is nil or unconfined. Nil profile means unconfined. Disabled seccomp allows only unconfined/runtime-default semantics, rejecting custom profiles. Runtime default loads the configured profile into the generator config and may inject a notifier. Localhost reads the specified file and applies it from bytes.

State and persistence behavior: caches the default profile globally with `sync.Once`. `Config` holds enabled flag, current profile pointer, and notifier base path. It reads profile files and OCI artifact data but writes no profile state.

Dependencies/integration points: depends on goccy JSON, runtime-tools generator, Podman/common seccomp, CRI API `SecurityProfile`, image system context, unix constants, CRI-O seccomp OCI artifact store, and CRI-O tracing/logging. Container creation calls this to set `specGenerator.Config.Linux.Seccomp`.

Risks: `validateSyscallIndex` fatal-exits when upstream default profile layout changes, intentionally making vendor bumps loud. Default profile mutation relies on exact syscall list indexes. OCI artifact profiles take priority only when profile field is nil/unconfined. The disabled-seccomp branch policy is subtle for runtime default versus localhost.

Test signals: `seccomp_test.go` covers default profile retrieval, profile file loading, default reload, runtime-default setup, localhost setup, and missing localhost errors under enabled seccomp.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccomp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccomp_test.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/seccomp_test.go

Purpose: tests seccomp config construction, profile loading, default profile loading, and basic `Setup` behavior for runtime-default and localhost profiles.

Important APIs/types/functions: uses `seccomp.New`, `Profile`, `LoadProfile`, `LoadDefaultProfile`, `Setup`, and a helper `writeProfileFile` that writes a minimal JSON profile. It uses runtime-tools `generate.New("linux")` and CRI API `SecurityProfile`.

Control flow: each test creates a fresh config. Profile tests compare the default profile pointer/value and load a local temp profile. Setup tests skip when seccomp is disabled, then verify runtime-default setup returns the runtime-default string, localhost setup returns the local file path, and missing localhost files fail.

State and persistence behavior: writes temp profile files and mutates `sut.profile`. It may skip based on host/build seccomp enablement.

Dependencies/integration points: Ginkgo/Gomega, runtime-tools generator, CRI API security profiles, and host seccomp availability.

Risks: one conditional around "should not fail with non-existing profile" is guarded by `if sut != nil && !sut.IsDisabled()` even though enabled seccomp should make `LoadProfile` fail on missing files; this looks like a test description/condition mismatch or dead-risk path depending on build behavior. Tests do not cover OCI artifact priority, notifier injection, disabled custom-profile rejection, or default-profile syscall mutation details.

Test signals: useful smoke coverage for profile loading and setup, but important seccomp notifier and OCI artifact flows require separate tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccomp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccomp_unsupported.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/seccomp_unsupported.go

Purpose: provides no-op seccomp implementation when the `seccomp && linux && cgo` build constraints are not met.

Important APIs/types/functions: stub `Config`, `Notifier`, `Notification`, `New`, `Setup`, notifier path/profile methods, `NewNotifier`, notifier methods, notification accessors, `IsDisabled`, `Profile`, and `DefaultProfile`.

Control flow: `New` returns disabled config. `Setup` always returns nil notifier, empty reference, and nil error. Profile load/default methods are no-ops. Notifier and notification methods return zero values.

State and persistence behavior: no profile or notifier state is persisted; `enabled` is false.

Dependencies/integration points: keeps the same API surface for builds without seccomp support so container setup code can compile and degrade to unconfined behavior.

Risks: custom seccomp expectations are silently ignored by `Setup` in unsupported builds, unlike the enabled implementation’s more nuanced disabled-seccomp checks.

Test signals: no direct tests for unsupported build behavior in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccomp_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/impl.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/impl.go

Purpose: defines the minimal datastore abstraction needed by seccomp OCI artifact resolution.

Important APIs/types/functions: `Impl` interface with `PullData(context.Context, string, *datastore.PullOptions) ([]datastore.ArtifactData, error)`.

Control flow: no implementation; `SeccompOCIArtifact` depends on this interface to pull artifact bytes.

State and persistence behavior: none in this file.

Dependencies/integration points: references CRI-O `internal/ociartifact/datastore`. Tests replace the implementation through a test-only setter to mock pull behavior.

Risks: the interface exposes only pull data; callers cannot inspect source metadata beyond returned artifact data.

Test signals: mocked in `seccompociartifact_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/impl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact.go

Purpose: resolves seccomp profiles stored as OCI artifacts based on pod and image annotations.

Important APIs/types/functions: `SeccompOCIArtifact`, `New`, constants `SeccompProfilePodAnnotation` and `requiredConfigMediaType`, and `(*SeccompOCIArtifact).TryPull`.

Control flow: `New` creates a datastore-backed implementation rooted at the supplied graph root and system context. `TryPull` searches annotations in priority order: pod container-specific, pod-wide, image generic, image container-specific, then image pod-wide. If no annotation matches, it returns nil. With a profile reference, it calls `PullData` while enforcing the seccomp config media type, rejects empty artifact data, and returns the first artifact’s bytes.

State and persistence behavior: holds only the datastore implementation. Pulled profiles come from OCI artifact storage/network via the implementation; this file does not persist bytes itself.

Dependencies/integration points: integrates CRI-O annotations v2, OCI artifact datastore, image system context, and CRI-O logging. `seccomp.Config.Setup` uses it before normal security-profile handling when profile field is nil or unconfined.

Risks: only the first artifact data item is used. Annotation priority is security-sensitive. Pod annotation logging trims `/POD` or container suffixes for readability but uses exact values for lookup. Empty pulls are errors, not no-ops.

Test signals: tests mock `Impl.PullData` and cover no annotation, pod/image annotation variants, pull errors, and empty artifact data.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact_test.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact_test.go

Purpose: verifies seccomp OCI artifact annotation matching and datastore pull behavior.

Important APIs/types/functions: uses `seccompociartifact.New`, test-only `SetImpl`, gomock `MockImpl`, `datastore.ArtifactData`, and `TryPull`.

Control flow: setup creates a temp OCI artifact store, replaces its implementation with a mock, and prepares artifact data containing `{}`. Tests cover no matching annotations returning nil, matching image/pod/container annotations, pull error propagation, and empty artifact data rejection. Expected datastore calls return either artifact data, an error, or an empty slice.

State and persistence behavior: uses a temporary directory for store construction but mocked pulls avoid real network/artifact IO. Logrus output is discarded.

Dependencies/integration points: Ginkgo/Gomega, gomock, datastore artifact data, annotations v2, and the package mock generated for `Impl`.

Risks: broad gomock argument matchers verify behavior but not the exact profile reference or enforced media type in every test. Real datastore behavior is outside the test scope.

Test signals: good coverage for annotation resolution paths and error handling around `TryPull`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact_test_inject.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact_test_inject.go

Purpose: exposes a test-only setter for replacing `SeccompOCIArtifact`’s implementation.

Important APIs/types/functions: `(*SeccompOCIArtifact).SetImpl(impl Impl)`.

Control flow: directly assigns the provided implementation to `s.impl`.

State and persistence behavior: mutates only the in-memory implementation pointer.

Dependencies/integration points: build tag `test` keeps the hook out of production builds; tests use it to install a gomock implementation.

Risks: bypasses constructor invariants and should remain test-only.

Test signals: used by `seccompociartifact_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/suite_test.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/suite_test.go

Purpose: Ginkgo suite bootstrap for seccomp OCI artifact tests.

Important APIs/types/functions: `TestRun`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers fail handler, runs specs named `SeccompOCIArtifact`, initializes the CRI-O test framework before tests, and tears it down after.

State and persistence behavior: suite-level test framework state and temporary resources.

Dependencies/integration points: Ginkgo/Gomega and CRI-O test framework.

Risks: setup failure prevents artifact tests from running.

Test signals: harness only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/suite_test.go -->
# sources/cloud-native/cri-o/internal/config/seccomp/suite_test.go

Purpose: Ginkgo suite bootstrap for seccomp config tests.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers Gomega failure handling, runs framework specs named `SeccompConfig`, and manages test framework setup/teardown.

State and persistence behavior: suite-local test state only.

Dependencies/integration points: Ginkgo/Gomega and CRI-O `test/framework`.

Risks: harness failure blocks seccomp tests.

Test signals: harness only; behavior lives in `seccomp_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/seccomp/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/ulimits/suite_test.go -->
# sources/cloud-native/cri-o/internal/config/ulimits/suite_test.go

Purpose: Ginkgo suite bootstrap for ulimits config tests.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers failure handler, runs specs named `UlimitsConfig`, and sets up/tears down the CRI-O test framework.

State and persistence behavior: suite framework state only.

Dependencies/integration points: Ginkgo/Gomega and CRI-O `test/framework`.

Risks: harness setup failure blocks ulimits tests.

Test signals: harness only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/ulimits/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/ulimits/ulimits.go -->
# sources/cloud-native/cri-o/internal/config/ulimits/ulimits.go

Purpose: parses configured default ulimits into runtime-tools compatible resource limit entries.

Important APIs/types/functions: `Ulimit` with `Name`, `Hard`, and `Soft`; `Config` storing `[]Ulimit`; `New`, `LoadUlimits`, and `Ulimits`.

Control flow: `LoadUlimits` iterates strings such as `name=soft:hard`, parses with Docker `go-units.ParseUlimit`, converts to an rlimit with `GetRlimit`, and appends a `Ulimit` whose name is `RLIMIT_` plus the uppercased parsed name. Errors are wrapped with the original unrecognized string when parsing fails.

State and persistence behavior: parsed limits are stored in memory. No files are read or written.

Dependencies/integration points: depends on `github.com/docker/go-units`. The resulting names and values match runtime-tools expectations for OCI spec generation.

Risks: repeated `LoadUlimits` calls append rather than replace, so callers should load once on a fresh config. Error handling stops on the first invalid entry.

Test signals: `ulimits_test.go` covers empty defaults, invalid input, and a valid `locks=10:64` entry.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/ulimits/ulimits.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/ulimits/ulimits_test.go -->
# sources/cloud-native/cri-o/internal/config/ulimits/ulimits_test.go

Purpose: validates basic ulimits config construction and parsing.

Important APIs/types/functions: `ulimits.New`, `LoadUlimits`, and `Ulimits`.

Control flow: tests assert a new config has no limits, invalid `hi=-1:-1` returns an error and leaves limits empty, and valid `locks=10:64` succeeds and stores at least one limit.

State and persistence behavior: in-memory only.

Dependencies/integration points: Ginkgo/Gomega and the ulimits package.

Risks: does not assert exact normalized `RLIMIT_` names or hard/soft numeric values, and does not cover repeated loads.

Test signals: focused smoke coverage for parse success/failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/config/ulimits/ulimits_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/check.go -->
# sources/cloud-native/cri-o/internal/criocli/check.go

Purpose: implements `crio check`, a storage integrity checker and optional repair/wipe tool for CRI-O storage.

Important APIs/types/functions: `checkErrors` alias, `CheckCommand`, `crioCheck`, and the long `usageText`. Flags include `age`, `force`, `repair`, `quick`, and `wipe`.

Control flow: `crioCheck` loads config, opens the storage store, defers shutdown, builds `storage.CheckOptions` using either `CheckEverything` or `CheckMost`, parses maximum unreferenced-layer age, runs `store.Check`, logs detailed report entries, and determines whether errors exist. Without `--repair`, any errors produce a summarized error. With repair, it calls `store.Repair`, optionally removes the whole storage directory on repair failure when `--wipe` is set, and returns remaining read-only/container errors according to `--force`.

State and persistence behavior: reads and may mutate container storage when repair or wipe is requested. It can remove damaged containers when forced and can remove the storage directory through `lib.RemoveStorageDirectory`.

Dependencies/integration points: urfave/cli, logrus, containers/storage, CRI-O `lib`, config loading, and duration parsing utilities.

Risks: repair/wipe operations are destructive and assume CRI-O and containers are stopped. Quick check intentionally differs from startup quick repair behavior. Error summaries use counts by report map size, not total nested errors.

Test signals: no direct tests in this subset for `crio check`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/completion.go -->
# sources/cloud-native/cri-o/internal/criocli/completion.go

Purpose: implements shell completion generation for bash, fish, and zsh.

Important APIs/types/functions: `completion`, `bashCompletion`, `zshCompletion`, `zshQuoteCmd`, and `fishCompletion`; templates `bashCompletionTemplate` and `zshCompletionTemplate`.

Control flow: the command defaults to bash when no shell argument is given, requires exactly one shell argument otherwise, and dispatches to the selected generator. Bash and zsh generation iterate visible commands and global flags, skipping hidden commands. Zsh command entries are quoted with single quotes unless usage contains a single quote, in which case double quotes are used and `$` is escaped. Fish delegates to `c.App.ToFishCompletion`.

State and persistence behavior: writes generated completion script to `c.App.Writer`; no persistent files.

Dependencies/integration points: urfave/cli. `DefaultCommands` includes this command for CRI-O binaries.

Risks: generated bash completion is simple and only completes top-level commands/global flags. Zsh quoting covers `$` only in double-quoted fallback and may need expansion if usage strings contain other shell metacharacters.

Test signals: `criocli_test.go` covers `zshQuoteCmd` through the test-only export in `completion_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/completion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/completion_test.go -->
# sources/cloud-native/cri-o/internal/criocli/completion_test.go

Purpose: exposes unexported zsh completion quoting for external-package tests.

Important APIs/types/functions: `ZshQuoteCmd(name, usage string)` returns `zshQuoteCmd(name, usage)`.

Control flow: no logic beyond delegation.

State and persistence behavior: none.

Dependencies/integration points: compiled in the `criocli` package test context so `criocli_test.go` can call the helper from package `criocli_test`.

Risks: exporting test-only internals can hide API drift if the helper changes and tests are not updated.

Test signals: enables zsh quoting table tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/completion_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/config.go -->
# sources/cloud-native/cri-o/internal/criocli/config.go

Purpose: implements the `crio config` command for printing a commented CRI-O configuration template.

Important APIs/types/functions: `ConfigCommand` with a `--default` flag and inline action.

Control flow: action configures logrus to plain text info output, fetches the app config from metadata, optionally replaces it with `config.DefaultConfig` when `--default` is set, validates the config with `Validate(false)`, and writes the template to stdout via `WriteTemplate`.

State and persistence behavior: reads/validates in-memory config and writes to stdout. It does not write config files.

Dependencies/integration points: urfave/cli, logrus, and `pkg/config`. It relies on `GetConfigFromContext` metadata population from `GetFlagsAndMetadata`.

Risks: validation can fail and prevent template output. `--default` ignores CLI/config-file changes by constructing a new default config.

Test signals: no direct tests for `ConfigCommand` in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/criocli.go -->
# sources/cloud-native/cri-o/internal/criocli/criocli.go

Purpose: centralizes CRI-O CLI default commands, config metadata access, config-file loading, CLI flag merging, flag definitions, string-slice normalization, and timestamp formatting.

Important APIs/types/functions: `DefaultCommands`, `GetConfigFromContext`, `GetAndMergeConfigFromContext`, `mergeConfig`, `mergeConfigFiles`, `mergeRootConfig`, `mergeImageConfig`, `mergeRuntimeConfig`, `mergeRuntimesConfig`, `mergeNetworkConfig`, `mergeAPIConfig`, `mergeMetricsConfig`, `mergeTracingConfig`, `mergeNRIConfig`, `GetFlagsAndMetadata`, `getCrioFlags`, `StringSliceTrySplit`, and `Timestamp`.

Control flow: `GetFlagsAndMetadata` creates default config and flag list, storing the config under app metadata. `GetAndMergeConfigFromContext` loads the config from metadata, then merges config file, config directory, and explicit CLI flags. Merge helpers update only fields whose flags are set, preserving config-file values otherwise. Runtime merge handles conmon, runtimes, hooks, security, capabilities, devices, cgroups, namespace, logging, CRIU, read-only, SELinux, hostport, and timezone settings. `mergeRuntimesConfig` parses colon-delimited runtime handler specs with optional privileged-without-host-devices, config path, and minimum memory.

State and persistence behavior: mutates the in-memory `*libconfig.Config` stored in CLI metadata. It reads config files/drop-ins through `UpdateFromFile` and `UpdateFromPath`. It does not persist merged config except when other commands write output.

Dependencies/integration points: urfave/cli, logrus, Docker units, CRI-O logging, config, and metrics collectors. Every CRI-O command using shared flags depends on this file.

Risks: the large flag list must stay synchronized with `pkg/config` fields, defaults, env vars, and deprecations. `mergeRuntimesConfig` uses colon splitting, so values containing colons are not representable. `StringSliceTrySplit` supports comma fallback only for a single parsed value. Missing config files are skipped only when defaulted; explicit missing config is an error.

Test signals: `criocli_test.go` covers comma splitting copy semantics and two flag merge cases (`hostnetwork-disable-selinux`, `disable-hostport-mapping`), but most flags and runtime parsing are untested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/criocli.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/criocli_test.go -->
# sources/cloud-native/cri-o/internal/criocli/criocli_test.go

Purpose: tests selected CLI helper behavior: string-slice parsing, zsh completion quoting, and specific global flag merges.

Important APIs/types/functions: `StringSliceTrySplit`, test-only `ZshQuoteCmd`, `GetFlagsAndMetadata`, `GetConfigFromContext`, and `GetAndMergeConfigFromContext`.

Control flow: first suite constructs a `flag.FlagSet` with a `cli.StringSlice`, then verifies dense comma-separated, whitespace-trimmed comma-separated, and separately repeated values all normalize to three entries, and returned slices are copies. Completion tests use a table to verify single-quote default, double-quote fallback for usage containing apostrophes, and dollar escaping only in double-quoted output. Flag tests create an app/context, apply bool flags with `HasBeenSet`, and verify config merge changes for `hostnetwork-disable-selinux` and `disable-hostport-mapping`.

State and persistence behavior: all state is in-memory cli flag/app state.

Dependencies/integration points: Ginkgo/Gomega, urfave/cli, Go `flag`, and CRI-O config metadata.

Risks: coverage is narrow compared to the size of `criocli.go`; most flags, config file loading, runtime parsing, and command actions are untested.

Test signals: good regression coverage for helper parsing and two recently important bool flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/criocli_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/documentation.go -->
# sources/cloud-native/cri-o/internal/criocli/documentation.go

Purpose: provides CLI subcommands that generate man-page and markdown documentation for the app.

Important APIs/types/functions: `markdownDocTemplate`, `man()`, and `markdown()`.

Control flow: `man` returns a command that writes `c.App.ToMan()` output. `markdown` returns a command that temporarily overrides `cli.MarkdownDocTemplate` with CRI-O’s custom template, writes `c.App.ToMarkdown()`, and restores the original template with a deferred assignment.

State and persistence behavior: writes generated documentation to the app writer. Temporarily mutates the global urfave/cli markdown template during markdown generation.

Dependencies/integration points: urfave/cli documentation generation. `DefaultCommands` includes these commands.

Risks: global template mutation must be restored even on errors; the defer handles normal control flow. Concurrent documentation generation in the same process could observe the temporary template.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/documentation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/publish.go -->
# sources/cloud-native/cri-o/internal/criocli/publish.go

Purpose: exposes a hidden `publish` command for sending CRI-O events to an endpoint.

Important APIs/types/functions: `PublishCommand` with hidden `Name: "publish"`, `ArgsUsage: "PUBLISH"`, and an action that calls `lib.Publish`.

Control flow: action reads the hidden global `address` flag and the first positional argument, then passes them to `lib.Publish`.

State and persistence behavior: no local persistence; behavior depends on `lib.Publish`, which likely sends network or IPC event data.

Dependencies/integration points: urfave/cli and CRI-O internal `lib`.

Risks: hidden command has little validation here; argument/address validation is delegated to `lib.Publish`.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/publish.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/status.go -->
# sources/cloud-native/cri-o/internal/criocli/status.go

Purpose: implements `crio status` and subcommands for querying a running CRI-O daemon.

Important APIs/types/functions: constants `defaultCrioSocketPath` and `crioSocketPath`; `StatusCommand`; helpers `crioClient`, `configSubCommand`, `containers`, `info`, `goroutines`, and `heap`.

Control flow: `StatusCommand` requires subcommands and exposes `config`, `containers`, `info`, `goroutines`, and `heap`. `crioClient` builds a client from `--socket`. `configSubCommand` prints daemon config info. `containers` optionally filters by ID and supports verbose output. `info` prints version/config/storage/runtime details. `goroutines` and `heap` request runtime diagnostics and write them to stdout.

State and persistence behavior: reads daemon state over the CRI-O client socket and writes output to stdout. Does not mutate daemon state.

Dependencies/integration points: urfave/cli and `github.com/cri-o/cri-o/pkg/client`. Integrates with the CRI-O status API served by the daemon.

Risks: command success depends on daemon socket availability and permissions. Output is plain text and tightly coupled to client response structures. Filtering and verbose modes are implemented client-side.

Test signals: no direct tests for status commands in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/suite_test.go -->
# sources/cloud-native/cri-o/internal/criocli/suite_test.go

Purpose: Ginkgo suite bootstrap for CLI tests.

Important APIs/types/functions: `TestLibConfig`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers fail handler, runs framework specs named `CLIConfig`, initializes the CRI-O test framework, and tears it down.

State and persistence behavior: suite-local test framework state.

Dependencies/integration points: Ginkgo/Gomega and CRI-O test framework.

Risks: suite setup failures prevent CLI tests from running.

Test signals: harness only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/version.go -->
# sources/cloud-native/cri-o/internal/criocli/version.go

Purpose: implements `crio version` output.

Important APIs/types/functions: constants `fullVersionTemplate` and `versionTemplate`; `VersionCommand` with `--json` flag.

Control flow: action gets version information from `version.Get()`. With `--json`, it JSON-encodes the version struct to stdout. Otherwise it applies either full or short text templates depending on `c.App.Version`, printing app version plus git/build details.

State and persistence behavior: writes version text/JSON to stdout; no persistent state.

Dependencies/integration points: urfave/cli, goccy JSON, text/template, and CRI-O internal version package.

Risks: template execution errors are returned. Short template omits git/build details when app version is populated.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/wipe.go -->
# sources/cloud-native/cri-o/internal/criocli/wipe.go

Purpose: implements `crio wipe`, which removes CRI-O containers and optionally images after reboot/upgrade or when forced.

Important APIs/types/functions: `WipeCommand`, `crioWipe`, `ContainerStore`, `wipeCrio`, `getCrioContainersAndImages`, `deleteContainer`, and `deleteImage`.

Control flow: `crioWipe` loads config and storage, determines whether containers/images should be wiped from version files unless `--force` is set, handles unclean shutdown by removing the whole storage directory once and writing `/run/crio/crio-wipe-done`, exits early when internal wipe is enabled and not forced, skips if no container wipe is needed, then deletes CRI-O-owned containers and images. `getCrioContainersAndImages` scans storage containers, reads metadata, filters CRI-O containers, and records image IDs.

State and persistence behavior: reads version marker files and storage metadata. May remove the entire storage directory, unmount/delete containers, delete images, and write `/run/crio/crio-wipe-done`.

Dependencies/integration points: containers/storage, CRI-O config, internal storage metadata helpers, `lib.RemoveStorageDirectory`, and version wipe checks.

Risks: destructive by design. `os.ErrNotExist` from `Containers()` is returned despite being treated specially, which can propagate. Image IDs are not deduplicated before deletion. Running containers can make unmount/delete fail; failures are logged and deletion continues.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/criocli/wipe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/dbusmgr/dbusmgr.go -->
# sources/cloud-native/cri-o/internal/dbusmgr/dbusmgr.go

Purpose: manages a shared systemd D-Bus connection with rootless/root selection and automatic reconnect on closed connections.

Important APIs/types/functions: package globals `dbusC`, `dbusMu`, `dbusInited`, `dbusRootless`; `DbusConnManager`; `NewDbusConnManager`, `GetConnection`, `newConnection`, `RetryOnDisconnect`, and `resetConnection`.

Control flow: construction normalizes rootless=false when UID is 0, prevents mixing root and rootless managers in one process, and marks global initialization. `GetConnection` uses double-checked locking to lazily create the shared connection. `newConnection` selects user or system systemd D-Bus. `RetryOnDisconnect` repeatedly obtains a connection, retries immediately on `EAGAIN`, resets and reconnects on `dbus.ErrClosed`, and returns other errors.

State and persistence behavior: global in-memory shared connection and mode flags. No persistent files.

Dependencies/integration points: Linux build only. Uses coreos go-systemd D-Bus, godbus errors, OS UID, and `newUserSystemdDbus` from `user.go`. Used by systemd cgroup manager code.

Risks: process-wide singleton panics if root and rootless modes are mixed. `RetryOnDisconnect` can loop indefinitely on persistent `EAGAIN`. Uses `context.TODO` for system connection.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/dbusmgr/dbusmgr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/dbusmgr/user.go -->
# sources/cloud-native/cri-o/internal/dbusmgr/user.go

Purpose: detects and opens a rootless user systemd D-Bus connection, including special handling for user namespaces.

Important APIs/types/functions: `newUserSystemdDbus`, `DetectUID`, and `DetectUserDbusSessionBusAddress`.

Control flow: `newUserSystemdDbus` finds a bus address and UID, dials D-Bus, authenticates with external auth for that UID, sends Hello, and wraps the connection for go-systemd. `DetectUID` returns `os.Getuid` outside user namespaces; inside, it executes `busctl --user --no-pager status` and parses `OwnerUID=...`. `DetectUserDbusSessionBusAddress` prefers `DBUS_SESSION_BUS_ADDRESS`, then `$XDG_RUNTIME_DIR/bus`, then parses `DBUS_SESSION_BUS_ADDRESS=` from `systemctl --user --no-pager show-environment`.

State and persistence behavior: reads environment variables, checks filesystem existence for the user bus path, and shells out to busctl/systemctl. No persistent writes.

Dependencies/integration points: godbus, go-systemd, moby userns detection, CRI-O cmdrunner. Called from `DbusConnManager` when rootless mode uses user systemd.

Risks: rootless operation depends on user session D-Bus availability and external commands. Scanner parsing is strict about key prefixes. Authentication errors close the connection before returning.

Test signals: no direct tests here; command execution is abstracted through cmdrunner and could be mocked.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/dbusmgr/user.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container.go -->
# sources/cloud-native/cri-o/internal/factory/container/container.go

Purpose: defines CRI-O’s container factory abstraction and most of the logic that translates CRI container/sandbox config, image metadata, annotations, capabilities, privileges, and resources into an OCI runtime spec generator.

Important APIs/types/functions: public `Container` interface; hidden `container` struct; `New`, `SpecAddMount`, `SpecAddAnnotations`, `Spec`, `SetConfig`, `SetNameAndID`, getters, `SetRestore`, `SetPrivileged`, `LogPath`, `DisableFips`, `UserRequestedImage`, `ReadOnly`, `AddUnifiedResourcesFromAnnotations`, `SpecSetProcessArgs`, `WillRunSystemd`, `SpecSetupCapabilities`, `SpecSetPrivileges`, and `SpecSetLinuxContainerResources`.

Control flow: construction creates a runtime-tools generator for `runtime.GOOS`. `SetConfig` validates metadata/name and sandbox config exactly once. `SetNameAndID` generates or reuses an ID and constructs the Kubernetes container name. Annotation setup writes CRI-O/Kubernetes/image/sandbox metadata, labels, volumes, IPs, seccomp reference, stop signal, and systemd properties. Process args merge Kubernetes command/args with image entrypoint/cmd. Capability setup clears defaults, handles add/drop `ALL`, validates against kernel-supported capabilities, and writes bounding/effective/permitted/inheritable sets. Privileges set privileged mode or normal capabilities/masked paths. Resources apply CPU, memory, swap, cpusets, hugepages, and cgroup v2 unified settings.

State and persistence behavior: all state is in-memory on `container` and its OCI generator. It reads no files directly, but log path validation and node cgroup helpers consult host state through imported utilities.

Dependencies/integration points: integrates CRI API types, OCI image/runtime specs, runtime-tools generator, CRI-O annotations/constants/storage/config, capabilities, cgroup manager checks, node capability detection, nsmgr, kubelet labels, and logging.

Risks: very broad integration surface. `WillRunSystemd` assumes process args exist. `ReadOnly` dereferences `GetSecurityContext` through generated getters and relies on protobuf nil behavior. Capability and resource behavior are host-dependent. Annotation keys are security/compatibility sensitive. `Load`-time config validation must prevent inconsistent inputs where possible.

Test signals: focused tests cover config validation, name/ID generation, privileged gating, and log path behavior; many spec-generation paths are tested elsewhere or not in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_freebsd.go -->
# sources/cloud-native/cri-o/internal/factory/container/container_freebsd.go

Purpose: provides FreeBSD-specific SELinux label behavior for containers.

Important APIs/types/functions: `(*container).SelinuxLabel(sboxLabel string) ([]string, error)`.

Control flow: always returns an empty string slice and nil error.

State and persistence behavior: none.

Dependencies/integration points: FreeBSD platform variant of the container factory interface.

Risks: SELinux label handling is disabled on FreeBSD, as expected.

Test signals: no direct FreeBSD tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_linux.go -->
# sources/cloud-native/cri-o/internal/factory/container/container_linux.go

Purpose: implements Linux SELinux label resolution for containers.

Important APIs/types/functions: `(*container).SelinuxLabel(sboxLabel string) ([]string, error)`.

Control flow: returns nil when the container is privileged. Otherwise it reads the container Linux security context. If `SelinuxOptions` are unset, it returns the sandbox label. If options are set, it calls `utils.GetLabelOptions` to convert CRI SELinux options into label options and returns them.

State and persistence behavior: no persistent state; reads container config and sandbox label input only.

Dependencies/integration points: opencontainers SELinux package and CRI-O `utils`. Called during OCI spec setup to apply labels.

Risks: privileged containers intentionally bypass SELinux labeling. Invalid or incomplete SELinux options propagate errors from `GetLabelOptions`.

Test signals: no tests for this file in the listed subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_log_path_test.go -->
# sources/cloud-native/cri-o/internal/factory/container/container_log_path_test.go

Purpose: tests container log path resolution from CRI container and sandbox configuration.

Important APIs/types/functions: exercises `SetConfig`, `SetNameAndID`, `LogPath`, and constants `configLogPath`, `configLogDir`, `providedLogDir`.

Control flow: tests verify that sandbox-config `LogDirectory` takes precedence over the provided sandbox log dir, that the provided log dir is used when sandbox config lacks one, and that an empty container log path falls back to `<container-id>.log`.

State and persistence behavior: in-memory container config only; no log files are written.

Dependencies/integration points: Ginkgo/Gomega and CRI API types.

Risks: tests check substrings rather than exact joined paths and do not cover path traversal or invalid log paths; those are delegated to `utils.EnsureSaneLogPath`.

Test signals: focused coverage for log path precedence and defaulting.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_log_path_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_privileged_test.go -->
# sources/cloud-native/cri-o/internal/factory/container/container_privileged_test.go

Purpose: tests privileged-container gating against sandbox privilege state and nil Linux/security-context cases.

Important APIs/types/functions: exercises `SetConfig`, `SetPrivileged`, and `Privileged`.

Control flow: examples cover a privileged container in a privileged sandbox succeeding, an unprivileged container staying false, a privileged container in an unprivileged sandbox failing, and missing pod/container Linux or security context paths returning success while leaving `Privileged` false.

State and persistence behavior: in-memory CRI config only.

Dependencies/integration points: Ginkgo/Gomega and CRI API types.

Risks: tests do not assert exact error messages. Some duplicated cases have similar setup for missing container security context.

Test signals: good coverage for privilege escalation guard behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_privileged_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_setconfig_test.go -->
# sources/cloud-native/cri-o/internal/factory/container/container_setconfig_test.go

Purpose: validates container config initialization invariants.

Important APIs/types/functions: exercises `SetConfig`, `Config`, and `SandboxConfig`.

Control flow: tests assert success for a config with metadata/name and a sandbox config, failure for nil container config, empty config with nil metadata, empty metadata name, repeated config setting, and nil sandbox config.

State and persistence behavior: in-memory container object state only.

Dependencies/integration points: Ginkgo/Gomega and CRI API types.

Risks: does not cover already-set sandbox config independently of already-set container config, and does not assert specific error strings.

Test signals: strong coverage for constructor-style validation before later container setup steps rely on config presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_setconfig_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_setnameandid_test.go -->
# sources/cloud-native/cri-o/internal/factory/container/container_setnameandid_test.go

Purpose: tests container ID generation/reuse and Kubernetes-style container name construction.

Important APIs/types/functions: exercises `container.New`, `SetConfig`, `SetNameAndID`, `ID`, `Name`, and helper `setupContainerWithMetadata`.

Control flow: tests verify generated IDs are 64 characters, generated names contain pod name/namespace/UID, explicit old IDs are reused, empty sandbox metadata is accepted, and calling `SetNameAndID` before config setup fails.

State and persistence behavior: in-memory only; generated IDs use storage `stringid.GenerateNonCryptoID` through implementation.

Dependencies/integration points: Ginkgo/Gomega, CRI API types, and container factory package.

Risks: tests assert substrings rather than exact full name format and do not cover attempt number formatting.

Test signals: focused coverage for identity setup and precondition enforcement.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/factory/container/container_setnameandid_test.go -->
