# Research: subset-b-000092

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/store_test.go -->
# sources/cloud-native/cri-o/internal/ociartifact/store_test.go

Purpose: Ginkgo/Gomega tests for `ociartifact.Store` behavior around rejecting real container images from artifact paths and applying pinned-image metadata to artifact list/status results.

Important APIs/types/functions: test helpers build OCI manifests, Docker schema 2 manifests, schema 1 manifests, and OCI indexes. The suite exercises `Store.EnsureNotContainerImage`, `Store.List`, `Store.Status`, `SetPinnedImageRegexps`, `ErrIsAnImage`, mocked `Impl`, and mocked `LibartifactStore`.

Control flow: `EnsureNotContainerImage` tests first mock top-level manifest lookup, then cover direct manifest parsing, manifest-list parsing, platform instance selection, second manifest fetch, and error wrapping. Pinning tests mock libartifact list/inspect responses and verify CRI image `Pinned` flags from configured regexps.

State and persistence behavior: tests use temporary artifact roots and mock stores, so no durable artifact data is required. They validate in-memory regex state on `Store` and fake-store injection.

Dependencies and integration points: depends on `gomock`, CRI-O ociartifact mocks, `libartifact`, containers/image manifest constants, OCI image-spec media types, digest parsing, and the CRI image conversion path.

Risks: manifest classification is security-sensitive because image pulls must not be accepted as artifacts. Multi-arch handling can regress if instance digest lookup or manifest media-type parsing changes. Pinning by canonical name depends on how artifact names and digests are exposed.

Test signals: covers image rejection for OCI image config, empty config media type, Docker v2s2, Docker v2s1, bad manifest bytes, bad index bytes, instance-selection failures, and successful artifact cases with `artifactType` or custom config media types. Pinning coverage includes constructor regexps, runtime regexp updates, list/status results, name matching, and digest/canonical matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/store_test_inject.go -->
# sources/cloud-native/cri-o/internal/ociartifact/store_test_inject.go

Purpose: test-only injection hooks for replacing an `ociartifact.Store`'s concrete libartifact store and implementation with mocks.

Important APIs/types/functions: `SetFakeStore(LibartifactStore)`, `SetFakeImpl(Impl)`, and `FakeLibartifactStore` embedding the generated mock libartifact store.

Control flow: the setters directly assign private fields on `Store`; there is no validation or cleanup. Test code calls them after `NewStore` to route later store operations through gomock expectations.

State and persistence behavior: mutates only in-memory `Store` fields. The `//go:build test` tag prevents this test seam from existing in normal builds.

Dependencies and integration points: imports `github.com/cri-o/cri-o/test/mocks/ociartifact`. It integrates with `store_test.go` and with CRI-O's test build profile.

Risks: if `Store` internals change, these helpers can silently diverge from production construction. Because setters bypass invariants, they must remain limited to test builds.

Test signals: useful because artifact classification and pinning tests can isolate store logic from registry, filesystem, and libartifact behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/store_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/suite_test.go -->
# sources/cloud-native/cri-o/internal/ociartifact/suite_test.go

Purpose: Ginkgo suite bootstrap for the `ociartifact_test` package.

Important APIs/types/functions: `TestRun`, package-global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers the Gomega fail handler, runs framework specs named `OCIArtifact`, creates a CRI-O `TestFramework` before the suite, and tears it down afterward.

State and persistence behavior: initializes shared test framework state and temporary test resources. No production state is persisted.

Dependencies and integration points: depends on Ginkgo v2, Gomega, Go `testing`, and `github.com/cri-o/cri-o/test/framework`.

Risks: global `t` means individual tests assume suite setup succeeded. Failures in setup can cascade across the package.

Test signals: required for all OCI artifact tests using `t.Describe`, `t.MustTempDir`, and framework helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/ociartifact/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/opentelemetry/tracing_config.go -->
# sources/cloud-native/cri-o/internal/opentelemetry/tracing_config.go

Purpose: configures CRI-O OpenTelemetry tracing and exposes the package tracer.

Important APIs/types/functions: `tracingServiceName`, package-level `tracer`, `Tracer()`, and `InitTracing(ctx, collectorAddress, samplingRate)`.

Control flow: `InitTracing` reads hostname, builds a resource with service name, host name, and process PID, creates an insecure OTLP/gRPC trace exporter, chooses a parent-based sampler with either `NeverSample` or `TraceIDRatioBased(samplingRate/1_000_000)`, installs a batch span processor and tracer provider globally, installs trace-context plus baggage propagators globally, and returns gRPC interceptor options using that provider/propagator.

State and persistence behavior: mutates OpenTelemetry global tracer provider and global text-map propagator. It opens exporter state that callers must shut down through the returned `TracerProvider`.

Dependencies and integration points: uses OpenTelemetry SDK, OTLP trace gRPC exporter, grpc instrumentation options, semantic conventions, and CRI-O callers that instrument gRPC server/client handling.

Risks: global provider mutation affects the whole process. `WithInsecure` assumes collector transport is trusted or local. Sampling rate units are parts per million, so config validation must prevent surprising values.

Test signals: no local test in this subset; integration should verify hostname failures, exporter creation errors, sampling-rate boundaries, global propagation, and provider shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/opentelemetry/tracing_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/process/defunct_processes.go -->
# sources/cloud-native/cri-o/internal/process/defunct_processes.go

Purpose: counts zombie processes by scanning a procfs-like tree and parsing `/proc/[pid]/stat`.

Important APIs/types/functions: `ProcessFS`, `Stat`, `DefunctProcesses`, `DefunctProcessesForPath`, and private `processStats`.

Control flow: opens the process filesystem root, reads directory names, filters numeric names as PIDs, reads each `stat` file, parses command and state, logs and skips per-process read/parse failures, and increments the count when state is `Z`.

State and persistence behavior: read-only filesystem inspection. It does not cache results and does not mutate procfs or process state.

Dependencies and integration points: depends on `os`, `filepath`, `strconv`, `strings`, and logrus. It can be used by node-health or metrics code that needs defunct process counts.

Risks: `/proc/[pid]/stat` command names can contain parentheses; the parser correctly uses the last `)` but still assumes the state byte exists two characters later. Races are expected because processes can exit between directory read and stat read.

Test signals: tests use fixture proc trees for zombie counts, empty process lists, invalid paths, and non-directory errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/process/defunct_processes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/process/defunct_processes_suite_test.go -->
# sources/cloud-native/cri-o/internal/process/defunct_processes_suite_test.go

Purpose: Ginkgo suite bootstrap for process package tests.

Important APIs/types/functions: `TestProcess`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers Gomega failures, runs `Process` framework specs, creates the test framework before tests, and tears it down after tests.

State and persistence behavior: initializes shared test fixtures and framework state; production state is untouched.

Dependencies and integration points: depends on Ginkgo v2, Gomega, Go `testing`, and CRI-O test framework helpers.

Risks: tests depend on relative fixture paths under the process package working directory.

Test signals: enables `t.Describe` use in `defunct_processes_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/process/defunct_processes_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/process/defunct_processes_test.go -->
# sources/cloud-native/cri-o/internal/process/defunct_processes_test.go

Purpose: validates zombie-process counting against procfs fixture directories.

Important APIs/types/functions: tests `process.DefunctProcessesForPath`.

Control flow: success contexts call the function with fixture roots containing zombie states, no zombies, no process directories, or no directories. Failure contexts call it with a missing path and a regular file path.

State and persistence behavior: read-only use of checked-in test fixture files.

Dependencies and integration points: uses Ginkgo/Gomega assertions and the public process API.

Risks: exact error-string assertions are OS/runtime-sensitive for path formatting. Fixture-relative paths require the package test working directory.

Test signals: expected counts are 7 zombies for `proc_success_1` and 0 for the other success fixtures; invalid path and non-directory cases return count 0 plus errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/process/defunct_processes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/registrar/registrar.go -->
# sources/cloud-native/cri-o/internal/registrar/registrar.go

Purpose: provides an in-memory concurrent name registry mapping unique names to keys and keys to their reserved names.

Important APIs/types/functions: `ErrNameReserved`, `ErrNameNotReserved`, `ErrNoSuchKey`, `Registrar`, `NewRegistrar`, `Reserve`, `Release`, `Delete`, `GetNames`, `Get`, and `GetAll`.

Control flow: `Reserve` is idempotent for the same name/key but rejects name reuse by a different key. `Release` removes one name from both indexes. `Delete` removes every name for a key. Getters lock around map access and return direct or shallow-copied structures.

State and persistence behavior: all state is process-local in two maps protected by a mutex. No persistence exists. `GetNames` returns the underlying slice, and `GetAll` shallow-copies the map but not the slices.

Dependencies and integration points: uses `sync.Mutex`, `errors`, and `maps.Copy`. Suitable for runtime name reservation where names must be globally unique.

Risks: callers mutating slices returned by `GetNames` or `GetAll` can mutate registry internals. There is no context cancellation or durable conflict recovery.

Test signals: tests cover idempotent reserve, conflict detection, release idempotence, delete, lookup failures, and map retrieval.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/registrar/registrar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/registrar/registrar_test.go -->
# sources/cloud-native/cri-o/internal/registrar/registrar_test.go

Purpose: verifies registrar name/key reservation semantics and suite setup.

Important APIs/types/functions: `TestRegistrar`, test framework setup, and specs for `Reserve`, `Release`, `GetNames`, `Delete`, `Get`, and `GetAll`.

Control flow: each test starts with a fresh registrar containing `testName -> testKey`. Specs then add names, repeat operations, or delete state and assert errors/contents.

State and persistence behavior: in-memory only. The suite uses global framework state but recreates the registrar per test.

Dependencies and integration points: depends on Ginkgo/Gomega and CRI-O's test framework.

Risks: duplicate `GetNames` describe blocks cover similar assertions. Tests do not exercise concurrent use or mutation of returned slices.

Test signals: confirms reserved-name conflicts return `ErrNameReserved`, missing key/name return `ErrNoSuchKey` and `ErrNameNotReserved`, and delete removes reverse mappings.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/registrar/registrar_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner.go -->
# sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner.go

Purpose: stores cleanup callbacks for a resource and runs them with bounded retry/backoff.

Important APIs/types/functions: `ResourceCleaner`, `cleanupFunc`, `NewResourceCleaner`, `Add`, `Cleanup`, and private `retry`.

Control flow: `Add` wraps a cleanup function in retry logging and prepends it, so cleanup runs in reverse add order. `Cleanup` executes functions sequentially and stops at the first final error. `retry` logs each attempt and uses Kubernetes `wait.ExponentialBackoff`.

State and persistence behavior: in-memory slice of callbacks only. No callback result is persisted, and callbacks decide their own external effects.

Dependencies and integration points: uses CRI-O contextual logging and `k8s.io/apimachinery/pkg/util/wait`. Used by `ResourceStore` to clean stale resources.

Risks: no synchronization around `funcs`, so callers should build a cleaner before concurrent cleanup. Retry treats all callback errors as retryable until the step budget is exhausted. Cleanup order is important for dependent resources.

Test signals: tests verify callbacks are called, transient failures are retried, and test build retry count stops after three failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_defaults.go -->
# sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_defaults.go

Purpose: production default retry budget for resource cleanup callbacks.

Important APIs/types/functions: package variable `defaultRetryTimes = 20`.

Control flow: `retry` in `resourcecleaner.go` reads this value when constructing exponential backoff.

State and persistence behavior: mutable package-level variable in production builds, though intended as a constant-like default.

Dependencies and integration points: selected by `//go:build !test`; overridden by `resourcecleaner_test_inject.go` in test builds.

Risks: as a variable, in-package code could modify it. Production cleanup can take a long time because each callback has 20 exponential-backoff steps starting at 500 ms.

Test signals: paired test build file lowers retries to make failure tests fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_defaults.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_test.go -->
# sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_test.go

Purpose: validates `ResourceCleaner` callback invocation and retry behavior.

Important APIs/types/functions: tests `NewResourceCleaner`, `Add`, and `Cleanup`.

Control flow: specs add callbacks that set booleans, callbacks that fail twice before success, and a callback that always fails. Assertions check final error state and call counts.

State and persistence behavior: in-memory counters and booleans only.

Dependencies and integration points: uses context.Background, Ginkgo/Gomega, and the test-build retry budget.

Risks: tests do not assert reverse cleanup order or context cancellation behavior. Backoff timing can still slow tests if retry defaults leak in.

Test signals: demonstrates retry-until-success and failure after exactly three attempts under the test build tag.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_test_inject.go -->
# sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_test_inject.go

Purpose: test-only override of resource cleanup retry count.

Important APIs/types/functions: `defaultRetryTimes = 3` under `//go:build test`.

Control flow: selected at compile time instead of the production defaults file; `retry` uses this smaller value automatically.

State and persistence behavior: package variable only; no persistence.

Dependencies and integration points: integrates with `resourcecleaner_test.go` to keep retry tests bounded.

Risks: tests must run with the intended build tag or retry expectations and timing change.

Test signals: supports the assertion that an always-failing cleanup function is invoked three times.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcestore.go -->
# sources/cloud-native/cri-o/internal/resourcestore/resourcestore.go

Purpose: tracks recently-created resources by name until another CRI-O path retrieves them, while notifying waiters and cleaning up stale unused resources.

Important APIs/types/functions: `ResourceStore`, `Resource`, `IdentifiableCreatable`, `New`, `NewWithTimeout`, `Close`, `Get`, `Put`, `Delete`, `WatcherForResource`, `SetStageForResource`, `StageUnknown`, and the cleanup goroutine.

Control flow: construction starts `cleanupStaleResources`. `Put` creates or fills a placeholder and notifies watchers. `Get` removes a fully-put resource, calls `SetCreated`, and returns its ID. `WatcherForResource` creates placeholders for in-progress resources and returns the current stage. Cleanup marks put resources stale on one tick and reaps them on the next, running their cleaner outside the mutex.

State and persistence behavior: state is in-memory map plus watcher channels. Cleanup side effects are delegated to `ResourceCleaner`; no store state survives process restart.

Dependencies and integration points: uses CRI-O logging, logrus, mutexes, timers, and caller-supplied resource/cleanup implementations. It coordinates duplicate or retried create requests.

Risks: watcher sends occur while holding the mutex but channels are buffered by one. Placeholders must be deleted if never put and only staged, or they can leak. Cleanup timing is between one and two timeout intervals.

Test signals: tests cover put/get, duplicate put failure, `SetCreated`, multiple watcher notification, stale cleanup invocation, no cleanup before put, and stage creation/update.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcestore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcestore_test.go -->
# sources/cloud-native/cri-o/internal/resourcestore/resourcestore_test.go

Purpose: validates `ResourceStore` lifecycle, watcher, timeout cleanup, and stage behavior.

Important APIs/types/functions: local `entry` implements `IdentifiableCreatable`; specs call `New`, `NewWithTimeout`, `Put`, `Get`, `WatcherForResource`, `SetStageForResource`, and `Close`.

Control flow: no-timeout tests perform immediate put/get and watcher flows. Timeout tests create a short timeout store, add cleanup callbacks, and wait for channels. Stage tests create or update stage values and read them through watchers.

State and persistence behavior: all state is in-memory; timeout tests rely on goroutines and channel synchronization.

Dependencies and integration points: uses Ginkgo/Gomega, context, time, and resourcecleaner.

Risks: timeout-based tests can be slow or flaky under load. Some stores created in `BeforeEach` are replaced in tests, so cleanup via `Close` must cover the active instance.

Test signals: verifies stale resources are cleaned and become unavailable, placeholders are not cleaned before `Put`, watchers receive notifications, and stage defaults to `unknown`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/resourcestore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/suite_test.go -->
# sources/cloud-native/cri-o/internal/resourcestore/suite_test.go

Purpose: Ginkgo suite bootstrap for resource store tests.

Important APIs/types/functions: `TestResourceStore`, global `t *TestFramework`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers fail handler, runs framework specs named `ResourceStore`, sets up test framework state, and tears it down afterward.

State and persistence behavior: shared test framework state only.

Dependencies and integration points: depends on Ginkgo v2, Gomega, Go testing, and CRI-O test framework helpers.

Risks: global framework use means test files depend on suite initialization.

Test signals: enables `t.Describe` in resource cleaner/store tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/resourcestore/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/composite_hooks.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/composite_hooks.go

Purpose: adapts multiple runtime handler hooks into one `RuntimeHandlerHooks` implementation.

Important APIs/types/functions: `CompositeHooks` and methods `PreCreate`, `PreStart`, `PreStop`, and `PostStop`.

Control flow: each lifecycle method iterates hooks in configured order and stops immediately on the first error.

State and persistence behavior: stores only an ordered slice of hook implementations; no persistence.

Dependencies and integration points: used by `HooksRetriever.Get` when high-performance/default CPU-load-balance behavior and GOMAXPROCS injection both apply. It passes through OCI generator, sandbox, and container pointers.

Risks: hook ordering is semantically important. A failing earlier hook prevents later hooks from running, which can skip compensating behavior.

Test signals: no direct file-local tests, but hook retriever and GOMAXPROCS/high-performance tests exercise composed behavior indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/composite_hooks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/default_cpu_load_balance_hooks_linux.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/default_cpu_load_balance_hooks_linux.go

Purpose: Linux hook that disables `cpuset.sched_load_balance` on stopped container cgroups to avoid stale cgroups interfering with exclusive CPU scheduling.

Important APIs/types/functions: `DefaultCPULoadBalanceHooks` embeds `cgmgr.CgroupManager`; lifecycle no-op methods; `PostStop`.

Control flow: `PostStop` skips spoofed containers and cgroup v2, errors if no cgroup manager exists, resolves pod/container cgroup managers, and calls `disableCPULoadBalancingV1`.

State and persistence behavior: writes cgroup v1 cpuset files through helper functions; no CRI-O state is stored.

Dependencies and integration points: integrates with cgroup manager abstractions, node cgroup-version detection, sandbox cgroup parent, and container ID.

Risks: only meaningful on cgroup v1. Missing or stale cgroup paths can cause post-stop errors. Incorrect writes can affect CPU scheduling for unrelated cgroups.

Test signals: high-performance hook tests verify default hook selection when CPU-load-balancing annotations are allowed globally.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/default_cpu_load_balance_hooks_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/default_cpu_load_balance_hooks_unsupported.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/default_cpu_load_balance_hooks_unsupported.go

Purpose: non-Linux no-op implementation of default CPU-load-balance hooks.

Important APIs/types/functions: empty `DefaultCPULoadBalanceHooks` and no-op lifecycle methods.

Control flow: every method returns nil.

State and persistence behavior: no state and no filesystem/cgroup writes.

Dependencies and integration points: selected by `//go:build !linux` so callers can compile against the same interface on unsupported platforms.

Risks: behavior differs from Linux intentionally; tests on non-Linux cannot validate cgroup behavior.

Test signals: compile-time platform coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/default_cpu_load_balance_hooks_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/gomaxprocs_hooks_linux.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/gomaxprocs_hooks_linux.go

Purpose: injects `GOMAXPROCS` into selected container OCI specs to improve Go workload behavior for burstable and best-effort pods without CPU limits.

Important APIs/types/functions: `GomaxprocsHooks`, `PreCreate`, no-op `PreStart`/`PreStop`/`PostStop`, `calculateGOMAXPROCS`, and `injectGOMAXPROCS`.

Control flow: `PreCreate` skips when the sandbox has the skip annotation, when the cgroup parent is not burstable/besteffort, or when CPU quota is set. It reads CPU shares, calculates a doubled rounded-up CPU request with a fallback floor, and adds `GOMAXPROCS` unless already present.

State and persistence behavior: mutates only the OCI spec generator's process environment.

Dependencies and integration points: integrates with sandbox annotations/cgroup parent, OCI generator, CRI-O annotation constants, and `HooksRetriever` when `MinInjectedGOMAXPROCS` is configured.

Risks: cgroup-parent string matching is heuristic. Injecting can override future runtime/container defaults if skip conditions are wrong. CPU shares of zero still result in at least the fallback/one.

Test signals: unit tests cover env injection/skipping and CPU-share-to-GOMAXPROCS calculations across best-effort, fractional, and large CPU requests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/gomaxprocs_hooks_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/gomaxprocs_hooks_linux_test.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/gomaxprocs_hooks_linux_test.go

Purpose: validates GOMAXPROCS environment injection and CPU-share calculation helpers.

Important APIs/types/functions: tests `injectGOMAXPROCS` and `calculateGOMAXPROCS`.

Control flow: table tests create Linux OCI generators, prepopulate env values, call injection, and compare whether a new env var appears. Calculation table tests feed shares/fallback pairs and expected results.

State and persistence behavior: in-memory OCI spec mutation only.

Dependencies and integration points: uses Ginkgo/Gomega and runtime-tools `generate`.

Risks: tests focus on helpers, not the full `PreCreate` skip logic for annotations, cgroup parent, or quota.

Test signals: covers pre-existing `GOMAXPROCS`, default env already merged into the spec, large values, value 1, fractional requests, and fallback floors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/gomaxprocs_hooks_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/high_performance_hooks_linux.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/high_performance_hooks_linux.go

Purpose: Linux implementation of CRI-O high-performance runtime hooks for CPU isolation, IRQ balancing, CPU quota, shared CPU handling, CPU power/frequency tuning, and exec CPU affinity.

Important APIs/types/functions: `HighPerformanceHooks`, lifecycle methods `PreCreate`, `PreStart`, `PreStop`, `PostStop`, `RestoreIrqBalanceConfig`, `ServiceManager`, `CommandRunner`, CPU/IRQ constants, and helpers for cgroup v1/v2 cpuset partitioning, IRQ SMP masks, CFS quota, c-states, frequency governors, shared CPUs, housekeeping CPUs, and exec cgroups.

Control flow: `PreCreate` checks eligibility, handles shared CPU annotations, injects isolated/shared/housekeeping env vars, and sets OCI `ExecCPUAffinity`. `PreStart` resolves cgroup managers, sets shared CPU child cgroups and quotas, disables CPU/IRQ load balancing, disables quota, tunes c-state/governor files, and optionally pre-creates an exec cgroup. `PreStop` reverses load-balancing, c-state, and governor changes. `PostStop` restores IRQ affinity when needed and delegates stale cgroup load-balance cleanup to the default hook.

State and persistence behavior: writes cgroup files, `/proc/irq/default_smp_affinity`, irqbalance config, system CPU power/cpufreq files, and backup files under `/var/run/crio/cpu`. It tracks disabled IRQ-affinity container IDs in memory and caches full CPU set once.

Dependencies and integration points: integrates with CRI-O config, annotations, sandbox/container objects, OCI specs, opencontainers cgroups, systemd/cgroup managers, kube cpuset parsing, resource quantities, `systemctl`, `irqbalance`, and node cgroup version detection.

Risks: host-level writes are high impact and require locking. Cgroup v2 partition setup assumes CRI-O can manage parent cpuset files. IRQ rollback only covers part of the update path. Global service/command runners and cached CPU set must be reset in tests. Incorrect annotations can alter CPU scheduling for the node.

Test signals: extensive tests cover IRQ masks, service restart vs oneshot fallback, housekeeping sibling logic, c-state/governor save-restore, irqbalance restore, rollback on config update failure, annotation parsing, shared CPU errors, exec affinity selection, hook retrieval, and concurrent IRQ-mask updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/high_performance_hooks_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/high_performance_hooks_test.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/high_performance_hooks_test.go

Purpose: broad unit/integration-style coverage for high-performance runtime hook helpers and hook selection.

Important APIs/types/functions: mock service/command runners, fixture builders, tests for `setIRQLoadBalancing`, `getHousekeepingCPUs`, `injectHousekeepingEnv`, `doSetCPUPMQOSResumeLatency`, `doSetCPUFreqGovernor`, `RestoreIrqBalanceConfig`, `handleIRQBalanceRestart`, `updateNewIRQSMPAffinityMask`, `convertAnnotationToLatency`, `setSharedCPUs`, `PreCreate`, and `HooksRetriever.Get`.

Control flow: tests create fake container specs, sandbox annotations, sysfs-like directories, irqbalance config files, and cgroup manager mocks. Several scenarios run hooks concurrently to verify locking around IRQ mask updates.

State and persistence behavior: writes temporary files under `fixtures/`, overrides package globals `serviceManager` and `commandRunner`, and resets them after relevant tests.

Dependencies and integration points: uses Ginkgo/Gomega, gomock, CRI-O sandbox/oci/config types, cgroup manager mocks, runtime-spec, runtime-tools generator, and cpuset utilities.

Risks: tests use filesystem fixtures and package-global mocks, so cleanup/reset is critical. Some cgroup operations are mocked and do not prove real kernel compatibility.

Test signals: strongest coverage in this subset for host-tuning behavior: IRQ disable/enable idempotence, housekeeping topology, PM QoS and governor restore, irqbalance restart/oneshot decisions, mask rollback, exec affinity and shared CPU env injection, nil hook vs high-performance hook vs default hook selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/high_performance_hooks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks.go

Purpose: declares the runtime handler hook interfaces and retriever state shared across platform implementations.

Important APIs/types/functions: package globals `cpuLoadBalancingAllowedAnywhereOnce` and `cpuLoadBalancingAllowedAnywhere`, `RuntimeHandlerHooks`, `HighPerformanceHook`, and `HooksRetriever`.

Control flow: no executable hook selection here; it defines the lifecycle interface that platform files implement.

State and persistence behavior: contains process-local cached global state for whether CPU load balancing is allowed anywhere, plus retriever fields for config and cached high-performance hook instance.

Dependencies and integration points: imports runtime-tools generator, sandbox, OCI container, and CRI-O config. Used by runtime code that invokes pre-create/pre-start/pre-stop/post-stop hooks.

Risks: `sync.Once` cache is global, so tests and config reload behavior must reset or account for it. Interface duplication is intentional but can drift from callers if lifecycle signatures change.

Test signals: hook selection tests reset the once value to simulate CRI-O restart/config changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_linux.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_linux.go

Purpose: Linux hook retriever implementation selecting high-performance, default CPU-load-balance, and GOMAXPROCS hooks from runtime config and sandbox annotations.

Important APIs/types/functions: `NewHooksRetriever`, `Get`, `highPerformanceAnnotationsSpecified`, and `cpuLoadBalancingAllowed`.

Control flow: constructor logs deprecation warnings for high-performance handlers lacking allowed annotations. `Get` selects high-performance hooks if runtime name contains `high-performance` or sandbox has high-performance annotations; otherwise selects default CPU-load-balance hooks if the annotation is allowed anywhere. It appends GOMAXPROCS hooks when configured and returns nil, one hook, or `CompositeHooks`.

State and persistence behavior: caches one `HighPerformanceHooks` instance per retriever and uses package-global once-cached CPU-load-balancing allowance.

Dependencies and integration points: reads CRI-O runtime/workload config, annotation constants, cgroup manager config, IRQ balance path, shared CPU set, exec CPU affinity, and host sysfs/proc defaults.

Risks: `strings.Contains` runtime-name matching can include unintended names. Global `cpuLoadBalancingAllowedAnywhere` may become stale across config reloads unless process/tests reset it. Missing runtime config for a selected high-performance runtime logs an error and returns nil.

Test signals: high-performance tests cover high-performance name, arbitrary runtime with allowed annotations, default runtime with annotations, default CPU-load-balance selection, and nil hook cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_suite_test.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_suite_test.go

Purpose: Ginkgo suite entrypoint for runtime handler hook tests.

Important APIs/types/functions: `TestRuntimeHandlerHooks`.

Control flow: registers Gomega's fail handler and runs Ginkgo specs named `RuntimeHandlerHooks`.

State and persistence behavior: no shared CRI-O test framework state in this file; individual tests manage their fixtures.

Dependencies and integration points: uses Go testing, Ginkgo v2, and Gomega.

Risks: package-level state in tested code is reset inside individual tests, not by the suite.

Test signals: enables all runtimehandlerhooks package specs.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_unsupported.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_unsupported.go

Purpose: non-Linux runtime hook retriever implementation.

Important APIs/types/functions: `IrqSmpAffinityProcFile`, `NewHooksRetriever`, `HooksRetriever.Get`, and `RestoreIrqBalanceConfig`.

Control flow: constructor stores config. `Get` always returns a `DefaultCPULoadBalanceHooks` instance. `RestoreIrqBalanceConfig` is a no-op.

State and persistence behavior: no host tuning or persistence on unsupported platforms.

Dependencies and integration points: compiles the runtime hook interface for non-Linux builds and uses CRI-O logging span setup.

Risks: always returning a default hook differs from Linux's nil/no-op decisions, but that hook is itself no-op on unsupported platforms.

Test signals: compile-time platform coverage; no local non-Linux behavior tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/utils_linux.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/utils_linux.go

Purpose: utility functions for CPU mask conversion, irqbalance config editing, service control, and file checks used by Linux runtime hooks.

Important APIs/types/functions: `isASCII`, `cpuMaskByte`, `mapHexCharToByte`, `mapByteToHexChar`, `invertByteArray`, `isAllBitSet`, `calcIRQSMPAffinityMask`, `restartService`, `isServiceEnabled`, `updateIrqBalanceConfigFile`, `retrieveIrqBannedCPUMasks`, and `fileExists`.

Control flow: mask helpers parse comma-separated hex masks into little-endian byte arrays, set or clear CPU bits, compute inverted banned masks, pad to kernel-friendly 32-bit boundaries, and return comma-grouped hex strings. Config helpers replace or append `IRQBALANCE_BANNED_CPUS` lines.

State and persistence behavior: reads/writes irqbalance config files and executes `systemctl`. Mask helpers are pure.

Dependencies and integration points: depends on `hex`, `os`, `strings`, logrus, Kubernetes cpuset, and CRI-O command runner.

Risks: `calcIRQSMPAffinityMask` assumes the current mask is long enough for every CPU index. Config parsing uses a simple split on `=`, so unusual shell syntax is not preserved. `systemctl` calls depend on host service manager.

Test signals: utility tests cover bit set/clear cases, odd-length masks, short masks, inverse mask generation, and bounded config-file line count.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/utils_test.go -->
# sources/cloud-native/cri-o/internal/runtimehandlerhooks/utils_test.go

Purpose: unit tests for IRQ CPU mask math and irqbalance config file updates.

Important APIs/types/functions: tests `calcIRQSMPAffinityMask`, `updateIrqBalanceConfigFile`, plus helper functions `countLines`, `writeTempFile`, and `cpuSetOrDie`.

Control flow: table tests apply set/clear operations to masks and compare both affinity and inverted banned masks. Config-file test repeatedly updates the banned CPU line and verifies line count stays constant.

State and persistence behavior: uses temporary config files and removes them after tests.

Dependencies and integration points: uses Ginkgo/Gomega, bufio/os, and cpuset parsing.

Risks: tests do not cover non-ASCII mask input, too-short masks for high CPU indexes, or complex shell config syntax.

Test signals: catches endian/padding regressions and unbounded growth of irqbalance config files.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/runtimehandlerhooks/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/signals/signal.go -->
# sources/cloud-native/cri-o/internal/signals/signal.go

Purpose: exposes cross-platform signal aliases.

Important APIs/types/functions: package variables `Interrupt` and `Kill`.

Control flow: no functions; aliases are initialized from `os.Interrupt` and `os.Kill`.

State and persistence behavior: process-local variables only.

Dependencies and integration points: used by code that wants a CRI-O-local signals package while sharing names across platforms.

Risks: variables rather than constants can be reassigned inside the package. Signal semantics still depend on OS behavior.

Test signals: compile-time coverage only in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/signals/signal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/signals/signal_unix.go -->
# sources/cloud-native/cri-o/internal/signals/signal_unix.go

Purpose: Unix-specific signal aliases for termination and hangup.

Important APIs/types/functions: `Term os.Signal = unix.SIGTERM` and `Hup os.Signal = unix.SIGHUP`.

Control flow: selected for non-Windows builds by `//go:build !windows`.

State and persistence behavior: package-level variables only.

Dependencies and integration points: imports `golang.org/x/sys/unix`; supports Unix signal handling in shared CRI-O code.

Risks: Unix-only constants must not leak into Windows builds except through this abstraction.

Test signals: compile-time platform selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/signals/signal_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/signals/signal_windows.go -->
# sources/cloud-native/cri-o/internal/signals/signal_windows.go

Purpose: Windows-specific aliases for termination and hangup signals.

Important APIs/types/functions: `Term os.Signal = windows.SIGTERM` and `Hup os.Signal = windows.SIGHUP`.

Control flow: compiled on Windows by filename/build selection.

State and persistence behavior: package-level variables only.

Dependencies and integration points: imports `golang.org/x/sys/windows`; allows shared code to refer to `signals.Term` and `signals.Hup`.

Risks: Windows signal semantics differ from Unix and may not map perfectly to process-control expectations.

Test signals: compile-time platform coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/signals/signal_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/doc.go -->
# sources/cloud-native/cri-o/internal/storage/doc.go

Purpose: package documentation for CRI-O internal storage helpers.

Important APIs/types/functions: package comment and `package storage` declaration.

Control flow: none.

State and persistence behavior: none directly.

Dependencies and integration points: documents that the package helps create/manage CRI pod sandboxes, containers, and metadata in CRI-O's internal format and that the API is unstable.

Risks: documentation is broad and may lag the package's actual image-focused and runtime-storage responsibilities.

Test signals: compile/doc tooling only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image.go -->
# sources/cloud-native/cri-o/internal/storage/image.go

Purpose: implements CRI-O image service operations over containers/storage and containers/image: list/status, pull, delete/untag, short-name resolution, signature checks, image IDs, caching, and pinned-image matching.

Important APIs/types/functions: `ImageResult`, `ImageCopyOptions`, `CgroupPullConfiguration`, `ImageServer`, `GetImageService`, `ListImages`, `ImageStatusByName`, `ImageStatusByID`, `PullImage`, `UntagImage`, `DeleteImage`, `IsRunningImageAllowed`, `CandidatesForPotentiallyShortImageName`, `HeuristicallyTryResolvingStringAsIDPrefix`, `CompileRegexpsForPinnedImages`, `FilterPinnedImage`, and `WrapSignatureCRIErrorIfNeeded`.

Control flow: list/status resolve storage references, build or reuse image cache items, parse names, supplement repo digests, inspect labels/config/annotations, and verify mountpoints. Pull either runs in-process or reexecs `crio-pull-image` in a configured cgroup, streams JSON progress/result records, copies with signature policy, and falls back to OCI artifact pull for non-transient image-copy failures. Delete/untag resolves stable image IDs before mutation.

State and persistence behavior: persists images in containers/storage, caches immutable image metadata in memory, tracks in-progress names in `ImageBeingPulled`, may unmount stale image mountpoints, and can pull OCI artifacts into libartifact stores. Reexec passes store options over stdin.

Dependencies and integration points: depends heavily on containers/image, containers/storage, libimage/ociartifact, CRI errors, shortnames, signature policy, mountinfo, reexec, CRI-O references/config/logging, and platform `moveSelfToCgroup`.

Risks: image reference resolution is race-prone because tags can move; code switches to resolved refs where possible. Pull fallback must avoid masking cancellations/network errors. Pinned patterns use regexps and can panic on invalid `"*"`. Signature checks around multi-image manifests must select the correct instance.

Test signals: tests cover service construction, store getter, ID-prefix heuristics, short-name resolution including aliases and tag+digest normalization, untag paths, status/list failures, pull error paths, cancellation/deadline handling, and pinned regexp compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_id.go -->
# sources/cloud-native/cri-o/internal/storage/image_id.go

Purpose: provides a strongly typed wrapper around full containers/storage image IDs.

Important APIs/types/functions: `StorageImageID`, `ParseStorageImageIDFromOutOfProcessData`, private `parseStorageImageID`, `newExactStorageImageID`, `storageImageIDFromImage`, `ensureInitialized`, `IDStringForOutOfProcessConsumptionOnly`, `Format`, and `imageRef`.

Control flow: constructors validate full identifiers with containers/image reference helpers; zero values panic on use; `imageRef` builds a containers-storage reference for a validated ID.

State and persistence behavior: value type containing a private string. It represents durable storage IDs but does not itself persist anything.

Dependencies and integration points: integrates with `imageService` status/delete/signature paths and CRI out-of-process ID exchange with kubelet.

Risks: zero-value panic is intentional but requires callers to always use constructors. It deliberately avoids `String()` to discourage casual string handling.

Test signals: tests verify valid parsing, invalid input rejection, zero-value panic, `fmt.Formatter` support, and non-implementation of `fmt.Stringer`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_id.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_id_test.go -->
# sources/cloud-native/cri-o/internal/storage/image_id_test.go

Purpose: verifies `StorageImageID` parsing, formatting, and encapsulation behavior.

Important APIs/types/functions: tests `ParseStorageImageIDFromOutOfProcessData`, `IDStringForOutOfProcessConsumptionOnly`, and `fmt.Formatter` behavior.

Control flow: specs parse a valid SHA256-like full ID, iterate invalid inputs, assert zero-value use panics, and check `%s`/`%q` formatting while confirming the type is not a `fmt.Stringer`.

State and persistence behavior: no persistent state.

Dependencies and integration points: uses Ginkgo/Gomega and Go fmt interfaces.

Risks: test data assumes the identifier validation rules used by containers/image. It does not test `imageRef` against a real store.

Test signals: protects the type-safety contract that image IDs are full validated IDs and not general strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_id_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_linux.go -->
# sources/cloud-native/cri-o/internal/storage/image_linux.go

Purpose: Linux implementation for moving the reexeced image-pull process into a transient systemd cgroup.

Important APIs/types/functions: `moveSelfToCgroup(cgroup string)`.

Control flow: chooses `system.slice` or `user.slice` for rootless mode, validates an explicit cgroup contains `.slice`, derives the slice base, builds a `crio-pull-image-PID.scope` unit name, and calls `utils.RunUnderSystemdScope` through a dbus connection manager.

State and persistence behavior: creates/moves the current process into a transient systemd scope. No image state is changed directly.

Dependencies and integration points: used by `pullImageChild` before opening the store. Depends on rootless detection, dbus manager, systemd scope utility, PID, and cgroup naming.

Risks: invalid cgroup names fail pulls using new cgroup mode. Systemd/dbus failures abort child pulls. Rootless slice selection must match the user session environment.

Test signals: no direct test in this subset; pull tests exercise error paths mostly before actual cgroup movement.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_test.go -->
# sources/cloud-native/cri-o/internal/storage/image_test.go

Purpose: tests core image service behavior using mocked containers/storage and CRI-O storage transport.

Important APIs/types/functions: specs for `GetImageService`, `GetStore`, `HeuristicallyTryResolvingStringAsIDPrefix`, `CandidatesForPotentiallyShortImageName`, `UntagImage`, `ImageStatusByName`, `ListImages`, `PullImage`, and `CompileRegexpsForPinnedImages`.

Control flow: setup constructs mocks, temp registries config paths, and an `ImageServer`. Tests configure gomock sequences for storage resolution, image metadata reads, big data, layers, and deletion. Pull tests call real copy paths with invalid policy/context inputs to assert failures.

State and persistence behavior: uses temporary config files and mock state only; no real image store is required.

Dependencies and integration points: Ginkgo/Gomega, gomock, CRI-O mockutils, containers/image references/storage transport, containers/storage mock store, and CRI-O config/reference helpers.

Risks: mocked storage sequences mirror containers/image internals, so upstream behavior changes may require helper updates. Pull tests validate failure behavior, not successful remote pulls.

Test signals: covers short-name aliases/search registries, tag+digest normalization, missing registry config, untag delete vs remove-name paths, corrupt/missing image status, list cache-building failures, cancellation/deadline propagation, and pinned regexp exact/keyword/glob cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_unsupported.go -->
# sources/cloud-native/cri-o/internal/storage/image_unsupported.go

Purpose: non-Linux implementation of image-pull cgroup movement.

Important APIs/types/functions: `moveSelfToCgroup(cgroup string) error`.

Control flow: immediately returns an unsupported error containing `runtime.GOOS`.

State and persistence behavior: no cgroup or filesystem changes.

Dependencies and integration points: selected by `//go:build !linux`; lets image service compile on non-Linux while making new-cgroup pull mode fail explicitly.

Risks: callers using `CgroupPull.UseNewCgroup` on unsupported platforms receive an error instead of silently ignoring the request.

Test signals: compile-time platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/image_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/mock_helpers_test.go -->
# sources/cloud-native/cri-o/internal/storage/mock_helpers_test.go

Purpose: shared gomock sequence helpers for storage image service tests.

Important APIs/types/functions: `mockStorageReferenceStringWithinTransport`, `mockResolveReference`, `mockResolveImage`, `mockStorageImageSourceGetSize`, and `mockNewImage`.

Control flow: helpers construct expected containers-storage references, return ordered mock sequences for successful or missing image resolution, simulate storage reference string formatting calls, simulate size lookup, and compose new-image setup.

State and persistence behavior: no persistent state; only gomock expectations.

Dependencies and integration points: depends on CRI-O mockutils, containers/image storage transport, containers/storage mocks, CRI-O storage transport mocks, and package test constants such as `testManifest`.

Risks: helpers encode expected call order and some containers/image internal behavior, making tests sensitive to dependency changes. Missing-image behavior assumes digestless lookup paths.

Test signals: enables concise status/list/untag tests while preserving exact mocked interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/storage/mock_helpers_test.go -->
