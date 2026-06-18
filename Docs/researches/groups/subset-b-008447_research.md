# Research: subset-b-008447

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/copy_test.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/copy_test.go

Purpose: Ginkgo/Gomega coverage for the Kubernetes monitor copy helpers, primarily `getCopyDetails` and `copyFiles` from `copy.go`. The tests validate how init and sidecar containers plan and execute binary, library, primary client-library, arbitrary file, and required non-empty file copies.

Important APIs and functions: the file exercises `getCopyDetails(inputDir, copyPrimaryLibrary, binaryOutputDirectory, copyFiles, copyBinaries, copyLibraries, requiredCopyFiles, currentContainerVersion, mode)` and `copyFiles(logger, outputDir, copyDetails, requiredCopies)`. It also relies on `executionModeInit`, `executionModeSidecar`, `binaryTestDirectoryEnv`, and `libraryTestDirectoryEnv` to make paths deterministic under temporary directories.

Control flow: tests are grouped by copy scenario. They first assert planning output maps from source paths to destination relative paths, then create temporary input files and verify `copyFiles` materializes expected files under output directories. Sidecar binary destinations include `bin/<full-version>/...`, while init binary destinations use the major/minor directory by default.

State and persistence behavior: tests create files in `GinkgoT().TempDir()` and use environment overrides for test-only binary/library roots. Required-copy tests verify empty files fail without producing destination files, while non-empty files are copied.

Dependencies and integration points: depends on Ginkgo, Gomega, OS file APIs, and monitor copy helper constants. It indirectly documents container bootstrap behavior used by `main.go` in init/sidecar modes.

Risks: coverage is strong for copy planning but path collision, permission failures, symlink behavior, and partial copy cleanup are not deeply explored here. Repeated "fdbserver and fdbbackup" contexts duplicate intent.

Test signals: high signal for destination path contracts, version-derived directory naming, primary library rename to `libfdb_c.so`, and required non-empty enforcement.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/internal/certloader/certloader.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/internal/certloader/certloader.go

Purpose: implements hot-loading TLS certificate support for the monitor HTTP server. It lets the Prometheus/pprof endpoint use `tls.Config.GetCertificate` so certificate material can be reloaded without restarting the monitor process.

Important APIs and types: `CertLoader` stores cert/key paths, a cached `tls.Certificate`, the cached key-file modification time, a mutex, and a logger. `NewCertLoader(logger, certFile, keyFile)` constructs it. `GetCertificate(*tls.ClientHelloInfo)` checks the key file mtime, returns the cached pair when unchanged, or reloads with `tls.LoadX509KeyPair`.

Control flow: each TLS handshake calls `GetCertificate`. The method stats the key file first, locks around cache inspection/update, compares `stat.ModTime()` with `cachedCertModTime`, logs reloads, and replaces the cached pair on successful load.

State and persistence behavior: no persistent writes. Runtime state is only the cached certificate and key-file mtime. The mtime source is the key file, not the cert file.

Dependencies and integration points: used by `monitor.go` when `certificate-path` or `certificate-key-path` is configured. Depends on `crypto/tls`, `os.Stat`, and `go-logr`.

Risks: certificate-only changes may not reload if the key file mtime is unchanged. Supplying only one of cert/key paths causes the HTTPS branch to run and fail during load. Concurrent handshakes are serialized through one mutex during reload.

Test signals: no direct tests in this subset; behavior is indirectly reachable through monitor HTTPS startup, but reload edge cases are not covered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/internal/certloader/certloader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/kubernetes.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/kubernetes.go

Purpose: wraps Kubernetes API/cache access for the monitor pod. It reads pod/node metadata, watches pod/node events, emits configuration timestamps, and writes annotations describing current monitor configuration and environment.

Important APIs and types: `kubernetesClient` embeds `client.Client`, carries `TimestampFeed`, pod namespace/name, optional node name, and a logger. `setupCache` creates an in-cluster controller-runtime cache filtered to the current pod and node. `createPodClient` wires informers and starts the cache. Methods include `getPodMetadata`, `getNodeMetadata`, `updateAnnotations`, `updateFdbClusterTimestampAnnotation`, `updateAnnotationsOnPod`, and informer callbacks `OnAdd`, `OnUpdate`, `OnDelete`.

Control flow: environment variables `FDB_POD_NAMESPACE`, `FDB_POD_NAME`, and `FDB_NODE_NAME` select watched objects. Pod updates compare isolate annotation changes first; a change sends `time.Now().Unix()` to force reload. Otherwise, the outdated-config-map annotation is parsed and sent to `TimestampFeed`.

State and persistence behavior: persistent state is Kubernetes pod annotations applied server-side with field owner `fdb-kubernetes-monitor` and forced ownership. Annotation updates are retried except for deletion, not-found, or forbidden conditions.

Dependencies and integration points: integrates with `monitor.watchPodTimestamps`, `monitor.updateCustomEnvironmentFromNodeMetadata`, and the operator API annotation constants. It uses controller-runtime cache/client, client-go retry logic, and Kubernetes core Pod/Node metadata.

Risks: `updateAnnotationsOnPod` snapshots metadata once before retries, so conflict retries do not refetch fresh annotations. `context.Background()` is used for apply inside the retry closure, detaching from caller cancellation. Missing environment variables can lead to empty selectors.

Test signals: `kubernetes_test.go` covers fake-client setup, optional node watcher behavior, timestamp emission for valid/invalid annotations, isolate annotation changes, and annotation payload generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/kubernetes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/kubernetes_test.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/kubernetes_test.go

Purpose: validates `kubernetesClient` behavior with fake controller-runtime clients and informers. It documents pod/node watch setup, metadata retrieval, event-to-timestamp translation, and pod annotation updates.

Important APIs and functions: the tests call `createPodClient`, `getPodMetadata`, `getNodeMetadata`, `OnUpdate` indirectly through fake informers, and `updateAnnotations`. Test fixtures use `fake.NewClientBuilder`, `informertest.FakeInformers`, and `controllertest.FakeInformer`.

Control flow: setup creates a pod and node in a fake client and sets `FDB_POD_NAMESPACE`, `FDB_POD_NAME`, and `FDB_NODE_NAME`. The cache factory passed to `createPodClient` asserts those values. Event tests push pod updates through the fake informer and inspect `TimestampFeed`.

State and persistence behavior: fake Kubernetes API state records annotations written by server-side apply. Tests check the serialized current configuration annotation and JSON environment annotation, including recursive argument environment discovery and `BINARY_DIR`.

Dependencies and integration points: depends on Kubernetes API machinery, controller-runtime fake clients/cache, Ginkgo/Gomega, and API annotation constants. It is the primary test signal for `kubernetes.go`.

Risks: fake clients do not fully model API-server apply conflicts, RBAC failures, deletion timestamps, or informer cache timing. The tests cover happy-path annotation updates but not retry semantics.

Test signals: strong for watcher count when node watching is enabled/disabled, valid timestamp delivery, invalid timestamp suppression, isolate annotation reload triggers, and environment annotation shape.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/kubernetes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/main.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/main.go

Purpose: command entry point for `fdbkubernetesmonitor`. It supports launcher mode for supervising fdbserver, init mode for copying required binaries/libraries/config, and sidecar mode for version-dependent file copying plus idle signal wait.

Important APIs and functions: global flags define paths, mode, process count, pprof, node watch, TLS cert/key, and additional environment file. `initLogger` configures JSON zap logging with optional lumberjack rotation. `parseFlagsAndSetEnvDefaults` maps environment variables to flags. `main` parses flags, reads the version file, builds copy details, and dispatches by `executionMode`. `loadAdditionalEnvironment` parses `export KEY=value` lines.

Control flow: flags are registered first, environment defaults are applied before `pflag.Parse`, then current container version is read. Launcher mode loads additional env, parses the FDB version, creates a signal context, and calls `startMonitor`. Init mode copies files and exits. Sidecar mode copies only when its version differs from the main container version, then blocks until SIGINT/SIGTERM.

State and persistence behavior: writes log files when configured, copies files through `copyFiles`, and reads version/additional-env files. Launcher mode delegates pod annotation and process state to `monitor.go`.

Dependencies and integration points: integrates with copy helpers, `api.ParseFdbVersion`, monitor startup, zap/zapr logging, pflag, lumberjack, and OS signal handling.

Risks: environment defaults are applied before CLI parse, so malformed env values can abort flag parsing. `loadAdditionalEnvironment` tolerates unparsable lines by logging and continuing. Providing only one TLS file path reaches HTTPS setup and may fail later.

Test signals: no direct `main` tests in this subset; copy behavior, config parsing, and monitor subcomponents are tested separately.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/metrics.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/metrics.go

Purpose: defines custom Prometheus metrics for the Kubernetes monitor, tracking configuration changes, desired/running versions, process starts, and timestamps.

Important APIs and types: `metrics` holds counter/gauge vectors for restart count, configuration change count, last applied configuration timestamp, per-process start timestamp, running version, and desired version. `registerMetrics` creates and registers collectors. `registerConfigurationChange(version)` and `registerProcessStartup(processNumber, version)` update metric values.

Control flow: `monitor.startMonitor` registers metrics on a private registry, exposes `/metrics`, and stores the returned `metrics` object. `acceptConfiguration` calls `registerConfigurationChange`; `runProcess` calls `registerProcessStartup` after successful subprocess start.

State and persistence behavior: all state is in-memory Prometheus collector state. Previous desired/running version strings are tracked so old version gauges can be reset to zero when a different version appears.

Dependencies and integration points: depends on `prometheus/client_golang`. Metrics are consumed externally by Prometheus and by tests through registry gathering.

Risks: only a single previous running version is tracked globally, not per process, so mixed-version multi-process states may be simplified. GaugeVec label cardinality grows with observed versions until process lifetime ends.

Test signals: `metrics_test.go` verifies initial collectors, counter increments, desired/running version gauge resets, restart labels, and multi-process restart counter cardinality.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/metrics_test.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/metrics_test.go

Purpose: unit tests for the monitor Prometheus metric registration and update methods. It documents expected collector counts, labels, counter values, and version gauge reset behavior.

Important APIs and functions: tests create a fresh `prometheus.Registry`, call `registerMetrics`, then exercise `registerConfigurationChange` and `registerProcessStartup`. Gathered metric families are inspected with suffix checks against metric name constants and label constants.

Control flow: tests start with no custom metric observations, then add one or more configuration changes or process starts. Nested contexts check same-version and different-version transitions.

State and persistence behavior: all state is transient in a per-test registry. The tests verify cumulative counters and current-version gauges, including zeroing of previous version gauges after a version change.

Dependencies and integration points: uses Ginkgo/Gomega, Prometheus registry APIs, and Kubernetes pointer helpers for metric family names. It is tightly coupled to the names and labels in `metrics.go`.

Risks: tests assert metric family counts, which may be brittle if Prometheus client behavior changes or additional collectors are registered. They do not verify timestamp gauge values beyond collector presence.

Test signals: strong for restart count increments, process label values, desired/running version labels, and preservation of old version series at value zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/monitor.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/monitor.go

Purpose: implements the Kubernetes monitor process supervisor. It reads JSON process configuration, chooses the correct fdbserver binary, starts and restarts configured subprocesses, exposes metrics/pprof, watches local files, reacts to pod annotations, and coordinates shutdown.

Important APIs and types: `monitor` stores config file path, current container version, custom environment, active configuration bytes, last config time, process count/PIDs, mutex, pod client, logger, and metrics. `startMonitor` creates the pod client and HTTP server. Core methods include `readConfiguration`, `loadConfiguration`, `acceptConfiguration`, `runProcess`, `processRequired`, `processIsIsolated`, `watchConfiguration`, `handleFileChange`, `signalProcesses`, `run`, and `watchPodTimestamps`.

Control flow: startup creates Kubernetes watches, starts timestamp handling, registers metrics, starts HTTP/HTTPS metrics serving, then enters `run`. Config loads validate binary executability, node-label environment, generated arguments, and isolate annotation. Accepted configs spawn per-process loops. Each loop generates arguments, starts `exec.Cmd`, streams stdout/stderr to logs, waits, records exit, and backs off on non-zero exits.

State and persistence behavior: process IDs and active config are in-memory and mutex-protected. Persistent side effects are subprocesses, Kubernetes annotations, and cluster-file change annotations. File watches cover the monitor config and `/var/fdb/data/fdb.cluster`.

Dependencies and integration points: integrates with API config types, Kubernetes client, certloader, Prometheus, fsnotify, OS process/signal APIs, and the fdbserver binary layout.

Risks: long-running paths have race and lifecycle complexity. HTTPS startup logs and exits on `ListenAndServeTLS`, but if TLS is configured the following plain HTTP call is still lexically reachable after TLS returns. `readConfiguration` logs `err` when version is nil even though `err` may be nil. Cluster-file watch waits indefinitely for file creation.

Test signals: `monitor_test.go` covers node-label env injection, backoff math, config parsing, binary path selection, and isolate annotation. The full process loop, HTTP server, fsnotify paths, and shutdown delay are not directly exercised.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/monitor_test.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/monitor_test.go

Purpose: focused unit tests for selected monitor behaviors: node metadata environment injection, restart backoff calculation, and configuration parsing.

Important APIs and functions: tests call `updateCustomEnvironmentFromNodeMetadata`, `getBackoffDuration`, and `readConfiguration`. They construct `monitor` instances directly with fake Kubernetes clients and temporary files.

Control flow: node-label tests first run with no node metadata, then with fake Node labels containing slash/dot characters. Backoff tests use a table of error counts. Config tests write JSON config files, set a temporary executable `fdbserverPath`, and optionally add the isolate annotation to the fake pod.

State and persistence behavior: temp files model the config and executable. Fake Kubernetes client state provides pod/node metadata. The custom environment map is mutated in place with `NODE_LABEL_...` keys.

Dependencies and integration points: depends on `api.ProcessConfiguration`, fake controller-runtime client, Kubernetes core types, Ginkgo/Gomega, and `k8s.io/apimachinery/pkg/util/json`.

Risks: tests cover only `readConfiguration`, not `loadConfiguration` annotation writes or process spawning. Invalid JSON, missing executable, incompatible-version binary path selection, and argument-generation failures are not fully explored here.

Test signals: confirms node label sanitization, quadratic backoff capped at 60 seconds, nil config on missing version, protocol-compatible binary path override, and isolate annotation forcing `RunServers=false`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/monitor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/suite_test.go -->
## sources/storage-engines/foundationdb/fdbkubernetesmonitor/suite_test.go

Purpose: test suite bootstrap for the `fdbkubernetesmonitor` package. It connects Go's `testing` package to the Ginkgo/Gomega BDD suite.

Important APIs and functions: `TestAPIs(t *testing.T)` registers the Gomega fail handler, sets the default `Eventually` timeout to 10 seconds, and runs specs named `FDB Kubernetes monitor`.

Control flow: `go test` discovers `TestAPIs`, which starts all Ginkgo specs in the package. The timeout affects asynchronous assertions such as channel receives from fake informer events.

State and persistence behavior: no application state; only suite-level test configuration.

Dependencies and integration points: depends on `github.com/onsi/ginkgo/v2`, `github.com/onsi/gomega`, `testing`, and `time`. It is required for `copy_test.go`, `kubernetes_test.go`, `metrics_test.go`, and `monitor_test.go` to execute.

Risks: a package-wide 10 second eventually timeout can hide slow/failing async tests until timeout. No suite-level cleanup beyond individual test temp dirs and env helpers.

Test signals: confirms the package uses a single Ginkgo suite entrypoint and BDD-style specs rather than plain Go test functions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbkubernetesmonitor/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/CMakeLists.txt -->
## sources/storage-engines/foundationdb/fdbmonitor/CMakeLists.txt

Purpose: build definition for the native `fdbmonitor` executable, its reusable static library, and its unit test executable.

Important targets: defines `fdbmonitor` from `fdbmonitor.cpp`, `fdbmonitor_lib` from `fdbmonitor_lib.cpp`, and `fdbmonitor_tests` from `fdbmonitor_tests.cpp`. Links `SimpleOpt`, `Threads::Threads`, and `rt` on non-Apple Unix. It imports include directories from `fdbclient`.

Control flow: the file creates targets, strips debug symbols for packaging, removes thread-sanitizer compile/link options from `fdbmonitor`, installs either the target or stripped binary depending on `GENERATE_DEBUG_PACKAGES`, and defines sandbox helper targets.

State and persistence behavior: creates `${CMAKE_BINARY_DIR}/sandbox/data`, `logs`, and a configured sandbox `foundationdb.conf` if absent. Adds `clean_sandbox`, `start_sandbox`, and `generate_profile` custom targets.

Dependencies and integration points: integrates with FoundationDB's CMake helpers (`strip_debug_symbols`, `fdb_install`), `Sandbox.conf.cmake`, `generate_profile.sh`, `fdbserver`, `fdbcli`, and optional `mako`.

Risks: comments identify an include-directory hack tied to the old build system. Disabling thread sanitizer is intentional because it changes observed restart behavior, but it also removes a class of instrumentation from this process.

Test signals: registers `add_test(NAME fdbmonitor_tests COMMAND fdbmonitor_tests)`, covering path and environment utility tests from the static library.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor.cpp -->
## sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor.cpp

Purpose: native process monitor executable for FoundationDB. It parses CLI options, locks a singleton pid file, watches configuration paths, loads process commands, supervises child processes, handles signals, relays child output, and enforces Linux RSS limits.

Important APIs and functions: `main` uses `SimpleOpt` options `--conffile`, `--lockfile`, `--loggroup`, `--daemonize`, and help flags. Platform signal handlers update `exit_signal` and `child_exited`. It calls library functions such as `joinPath`, `parentDirectory`, `mkdir`, `set_watches`, `load_conf`, `read_child_output`, `getRss`, and `kill_process`.

Control flow: startup canonicalizes the config path, configures inotify or kqueue, optionally daemonizes, locks/writes the lockfile, blocks signals, and enters a loop. Reloads rebuild watches and call `load_conf`. The loop waits on child pipes, config watch events, signals, fork retry deadlines, and RSS-check deadlines. SIGCHLD triggers wait/restart; SIGHUP reloads and resets delays; SIGINT/SIGTERM kills children, waits, unlinks lockfile, and exits.

State and persistence behavior: persists the pid in the lockfile and may daemonize. Runtime state is held in global process maps from `fdbmonitor_lib.cpp`. Configuration changes can kill/restart children. Linux RSS violations kill processes and rely on SIGCHLD restart handling.

Dependencies and integration points: depends on POSIX process/signal/file APIs, inotify on Linux, kqueue on Apple/FreeBSD, `fdbclient/versions.h`, and `fdbmonitor_lib`.

Risks: single-threaded event-loop correctness depends on careful signal masking and fd-set maintenance. Symlink and missing-path watch logic is complex. `wait(nullptr)` during shutdown relies on SIGCHLD ignored semantics.

Test signals: only indirectly covered by `fdbmonitor_tests`; full process supervision, signal, inotify/kqueue, daemon, and RSS behavior require integration/runtime tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor.h -->
## sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor.h

Purpose: public declarations and core command-construction logic for native `fdbmonitor`. It defines logging severities, platform fd abstractions, utility declarations, environment parsing helpers, and the `Command` type that translates ini sections into process argv and restart policy.

Important APIs and types: `Severity`, `ProcessID`, utility declarations (`timer`, `parseWithSuffix`, path helpers, `load_conf`, `kill_process`, etc.), `EnvVarUtils`, and `Command`. `Command` owns `argv`, stdout/stderr pipes, restart-delay fields, envvar strings, deconfiguration state, `kill_on_configuration_change`, and memory RSS limit.

Control flow: the `Command` constructor merges keys from process section, process-id subsection, and `general`; resolves restart settings; parses envvars/delete-envvars; reads `command`; configures memory limits; builds argv from the command string plus ini keys. It expands `$ID` and `$PID`, handles `flag_`/`flag-` boolean flags, and excludes monitor-only keys from child argv.

State and persistence behavior: each `Command` creates monitored pipes and owns duplicated argv strings. Destruction unmonitors and closes pipes. `update` carries forward mutable restart state while applying new policy values. `get_and_update_current_restart_delay` resets after a quiet interval, adds jitter, and backs off.

Dependencies and integration points: uses `SimpleIni`, POSIX pipes/fd watching, Linux memory defaults, and functions implemented in `fdbmonitor_lib.cpp`. Instances are stored in global maps and driven by `load_conf` and `start_process`.

Risks: command tokenization uses whitespace splitting, so quoted command arguments are not preserved. Invalid config often logs and returns from the constructor with `argv` possibly unset. Environment variable syntax permits exactly one equals sign, which excludes some values.

Test signals: `fdbmonitor_tests.cpp` covers `EnvVarUtils`; path helpers are declared here but implemented/tested in the library.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor_lib.cpp -->
## sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor_lib.cpp

Purpose: implementation library for native `fdbmonitor`. It provides logging, path handling, config value lookup, process maps, child process launching/killing, configuration loading/reconciliation, child output logging, and platform-specific file watch helpers.

Important APIs and functions: logging functions map `Severity` to syslog or structured stderr. Path helpers include `joinPath`, `cleanPath`, `popPath`, `abspath`, `parentDirectory`, and recursive `mkdir`. Process APIs include `getRss`, `start_process`, `kill_process`, `load_conf`, and `read_child_output`. Linux adds `set_watches`; Apple/FreeBSD add kqueue watch helpers.

Control flow: `load_conf` loads `CSimpleIni`, resolves target user/group, kills processes when uid/gid or command config requires restart, updates existing commands, starts new sections named with a dot suffix, and respects fork retry time. `start_process` forks, resets signals, redirects stdout/stderr to pipes, applies envvars/deletions, sets parent-death signal where supported, changes uid/gid, and execs the child.

State and persistence behavior: global maps `id_command`, `pid_id`, and `id_pid` hold live supervisor state. The library mutates child processes and logs output but does not persist config itself. RSS reads `/proc/<pid>/statm` on Linux.

Dependencies and integration points: depends on POSIX APIs, syslog, passwd/group lookup, SimpleIni, FoundationDB version macros, Flow error types in some utility paths, and platform watch primitives.

Risks: `execv` failure exits child with status 0, which may be interpreted as successful exit by parent restart logging. `read_child_output` logs partial reads line-by-line but may split long lines. `load_conf` mutates maps while iterating derived lists carefully, but this area is lifecycle-sensitive.

Test signals: `fdbmonitor_tests.cpp` covers path normalization/resolution and environment parsing. Process launch, uid/gid changes, config reload, and watch behavior have limited unit coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor_lib.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor_tests.cpp -->
## sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor_tests.cpp

Purpose: standalone C++ tests for reusable `fdbmonitor` library utilities. It uses assert-style checks rather than the FoundationDB actor unit-test framework.

Important APIs and functions: `testPathOps` exercises `popPath`, `cleanPath`, `abspath`, `parentDirectory`, `joinPath`, symlink resolution behavior, and recursive `mkdir`. `testEnvVarUtils` exercises `EnvVarUtils::extractKeyAndValue` and `keyValueValid`. `main` runs both groups.

Control flow: helper functions call a path function, print PASS/FAIL, and count errors. Path tests create `simfdb/backups/...` directories and symlinks, compare resolving and non-resolving absolute paths, then assert zero errors. Env tests assert valid key/value parsing and invalid cases for empty entries, multiple equals signs, empty values, and empty keys.

State and persistence behavior: creates local `simfdb` directories and symlinks in the test working directory. No cleanup is performed in this file.

Dependencies and integration points: links against `fdbmonitor_lib` via CMake and includes `fdbmonitor.h`. It is registered as a CTest by `CMakeLists.txt`.

Risks: tests mutate relative filesystem state and assume symlink support. They do not isolate via temp directories, which can interact with repeated local runs. They cover utility functions but not process supervision.

Test signals: good signal for path edge cases, symlink resolution modes, parent directory formatting, and strict environment variable validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor_tests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ActorFuzz.actor.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/ActorFuzz.actor.cpp

Purpose: generated actor-compiler fuzz corpus. It defines many small actors with varied control-flow constructs and an `actorFuzzTests` harness that asserts generated actors emit expected traces and return/error sentinels.

Important APIs and functions: generated `ACTOR Future<int> actorFuzz0` through `actorFuzz29` take `FutureStream<int> inputStream`, `PromiseStream<int> outputStream`, and `Future<Void> error`. `actorFuzzTests()` calls `testFuzzActor` for each actor and returns `{testsOK, 30}`.

Control flow: actors combine `state` variables, nested loops, range loops, `try/catch`, `continue`, `break`, `return`, `waitNext(inputStream)`, `wait(error)`, `throw operation_failed`, and `throw_operation_failed`. They send numeric markers to `outputStream`; expected vectors encode the correct actor lowering behavior.

State and persistence behavior: no persistent state. Each actor maintains actor-local state-machine variables generated for Flow's actor compiler.

Dependencies and integration points: includes `fdbrpc/ActorFuzz.h` and `flow/actorcompiler.h` last, as required by actor source transformation. Linked into tests through `ActorFuzzUnitTest.cpp`.

Risks: the file is generated and should not be edited directly. Expected marker sequences are brittle by design; generator changes require regenerating both actor bodies and expected outputs. It is excluded on Windows via `#ifndef WIN32`.

Test signals: very high signal for actor compiler semantics across exception and control-flow cases; low signal for application behavior because this is compiler/runtime validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ActorFuzz.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ActorFuzzUnitTest.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/ActorFuzzUnitTest.cpp

Purpose: small unit-test bridge that links the generated actor fuzz corpus into the Flow/FoundationDB unit-test framework.

Important APIs and functions: `forceLinkActorFuzzUnitTests()` is an empty symbol used to force linker inclusion. `TEST_CASE("/actorFuzz")` calls `actorFuzzTests()` and asserts all generated tests passed.

Control flow: the test receives a `{passed, total}` pair and asserts equality. It returns `Void()` for the actor-based unit-test runner.

State and persistence behavior: no persistent state. Test state is contained in generated actor executions and expected marker comparisons.

Dependencies and integration points: includes `fdbrpc/ActorFuzz.h` and `flow/UnitTest.h`. It depends on `ActorFuzz.actor.cpp` for `actorFuzzTests`.

Risks: if the generated corpus is not linked, this file is the intended anchor, but build-system changes can still affect inclusion. It reports only aggregate equality, so detailed failure information comes from lower-level `testFuzzActor`.

Test signals: clear pass/fail gate for all actor fuzz generated cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/ActorFuzzUnitTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileCached.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/AsyncFileCached.cpp

Purpose: implementation of cached asynchronous file access. It maintains global/non-simulated and per-simulated-machine page caches, routes reads/writes through cached pages, supports zero-copy page reads, truncation, flushing, and cleanup.

Important APIs and functions: global caches `pc4k`, `pc64k`, and `simulatorPageCaches`; `EvictablePage::~EvictablePage`; `AsyncFileCached::openFiles`; `open_impl`; templated `read_write_impl<writing>`; `readZeroCopy`; `releaseZeroCopy`; `changeFileSize`; `flush`; `quiesce`; and destructor.

Control flow: open chooses a 4K or 64K `EvictablePageCache` based on flags and simulation context. Reads/writes split requests by page, create or hit `AFCPage` objects, and wait for outstanding page futures. Truncation flushes a partial terminal page, removes pages beyond new EOF using either targeted lookups or map scan, then truncates the underlying file. Flush walks `flushable` pages until all are written.

State and persistence behavior: cached pages are in-memory; durable persistence remains with the underlying uncached file after flush/truncate. Length and previous length track file size locally. Orphaned zero-copy pages are reference-counted by data pointer after eviction.

Dependencies and integration points: depends on Flow futures, page cache classes from `AsyncFileCached.h`, `IAsyncFile`, network simulation state, knobs, and aligned allocation helpers.

Risks: comments note read/write path assumptions about no waits before `prevLength` update. Zero-copy requires aligned full-page reads within file length. Destructor aborts if any page cannot be evicted.

Test signals: no direct tests in this subset; behavior is likely covered by broader file-system and simulation tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileCached.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileChaos.h -->
## sources/storage-engines/foundationdb/fdbrpc/AsyncFileChaos.h

Purpose: simulation wrapper around `IAsyncFile` that injects disk delays and write corruption for storage files. It is used to exercise storage robustness under simulator-controlled disk failures.

Important APIs and type: `AsyncFileChaos` implements `IAsyncFile` and reference counting. Methods wrap `read`, `write`, `truncate`, `sync`, `size`, `debugFD`, and `getFilename`. `getDelay` consults `DiskFailureInjector` and updates `ChaosMetrics`.

Control flow: constructor enables chaos only for filenames containing `storage-` and excluding `sqlite-wal`. Reads, truncates, syncs, and size calls delay before forwarding when the injector returns a delay. Writes may copy the buffer into an arena, flip a random bit according to `BitFlipper`, log the corrupted block, update metrics, delay, then write either corrupted or original data.

State and persistence behavior: wrapper has no durable state, but injected corruption is persisted by forwarding corrupted bytes to the underlying file. In simulation, corrupted block metadata is tracked in `g_simulator->corruptedBlocks` and pruned on truncate.

Dependencies and integration points: depends on Flow futures, simulator globals, `DiskFailureInjector`, `BitFlipper`, `ChaosMetrics`, deterministic random, and `IAsyncFile`.

Risks: `truncate` accesses `g_simulator->corruptedBlocks` in the delayed path without checking simulation mode, assuming this wrapper is used in simulator contexts. `getClassName` returns `"AsyncFileReadAheadCache"`, which appears copied and may be misleading for diagnostics.

Test signals: no direct unit tests here; simulator workloads and chaos metrics provide integration coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileChaos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileEIO.h -->
## sources/storage-engines/foundationdb/fdbrpc/AsyncFileEIO.h

Purpose: Unix libeio-backed implementation of `IAsyncFile`, selected as `Net2AsyncFile`. It provides asynchronous open/read/write/truncate/sync/size/delete/rename/stat operations and a generic dispatch path through the EIO thread pool.

Important APIs and type: `AsyncFileEIO` implements `IAsyncFile`. Static APIs include `init`, `stop`, `should_poll`, `open`, `deleteFile`, `renameFile`, `lastWriteTime`, `async_fsync_parent`, `async_fdatasync`, `async_fsync`, `waitAndAtomicRename`, and `dispatch`. Instance APIs wrap file operations and metrics. Private helpers include `openFlags`, `error`, `read_impl`, `write_impl`, `truncate_impl`, `sync_impl`, `size_impl`, `stat_impl`, `dispatch_impl`, `poll_eio`, and callbacks.

Control flow: file operations submit EIO requests with a `Promise<Void>`, await completion, cancel on actor cancellation, restore task priority through `delay(0, taskID)`, then translate EIO results to Flow errors. Atomic create writes to `<filename>.part` and renames after fsync plus parent directory fsync.

State and persistence behavior: each instance owns an fd, flags, filename, deferred `ErrorInfo`, and logical read/write metrics. Persistent effects are normal filesystem writes, truncates, renames, deletes, and fsyncs.

Dependencies and integration points: depends on libeio, Flow actors/futures, `IAsyncFile`, TD metrics, POSIX file APIs, and Apple `F_FULLFSYNC` custom handling. `eio_want_poll` schedules main-thread polling at `TaskPriority::PollEIO`.

Risks: write/truncate errors can be deferred through `ErrorInfo` and surface on sync, so callers must sync to observe durability failures. Correctness depends on polling callback scheduling. O_DIRECT is conditional on knobs and flags.

Test signals: no direct tests in this subset; file-system tests elsewhere usually validate `IAsyncFile` contracts and atomic write behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileEIO.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileEncrypted.cpp -->
## sources/storage-engines/foundationdb/fdbrpc/AsyncFileEncrypted.cpp

Purpose: encrypted `IAsyncFile` wrapper for append-only writes and read-only reads. It encrypts data in fixed-size blocks using FoundationDB stream cipher support and derives per-block IVs from filename-derived salt plus block number.

Important APIs and types: `AsyncFileEncryptedImpl` contains coroutine helpers `getFirstBlockIV`, `readBlock`, `read`, `write`, `sync`, and `zeroRange`. `AsyncFileEncrypted` exposes `read`, `write`, `zeroRange`, `truncate`, `sync`, `flush`, `size`, `getFilename`, zero-copy stubs, `debugFD`, `getIV`, and `writeLastBlockToFile`.

Control flow: read mode lazily obtains file size, clamps requested length at EOF, reads full encrypted blocks, decrypts each block, and copies requested slices. append-only write mode asserts writes occur exactly at current EOF, encrypts chunks into `writeBuffer`, writes full blocks as they fill, and reinitializes the encryptor for the next block. Sync writes the final partial block then syncs the underlying file.

State and persistence behavior: durable bytes are encrypted in the underlying file. Runtime state includes mode, current block, offset within block, write buffer, encryptor, cached file size, encryption block size, and first block IV. Truncate forwards to the underlying file only in append mode.

Dependencies and integration points: depends on `AsyncFileEncrypted.h`, Flow `StreamCipher`, global cipher key, `xxhash`, arenas, and Flow unit-test macros.

Risks: random writes are unsupported and enforced with assertions. `size` is read-only only. `readZeroCopy`/`releaseZeroCopy` throw `io_error`. IV salt strips directory and extension, so files with the same basename stem share first-block salt.

Test signals: embedded `TEST_CASE("fdbrpc/AsyncFileEncrypted")` writes random data in random chunks, syncs, reads in random chunks, and asserts plaintext round trip in simulation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbrpc/AsyncFileEncrypted.cpp -->
