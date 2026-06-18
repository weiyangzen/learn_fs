# subset-b-000171 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_test.go -->
# sources/cloud-native/moby/daemon/command/daemon_test.go

## Purpose
Exercises daemon CLI configuration loading, TLS option defaults, duplicate/conflicting labels, registry options, daemon log setup, CDI spec-dir resolution, and an OpenTelemetry meter allocation regression.

## Important APIs, Types, And Functions
`defaultOptions` builds a `daemonOptions` with common and platform config flags installed. The tests call `loadDaemonCliConfig`, `configureDaemonLogs`, and `otel.Meter().Int64Counter`.

## Control Flow
Each test creates a temporary daemon JSON file or empty option set, mutates flags/env-derived fields, then asserts merged config fields or expected conflict errors. `TestCDISpecDirs` table-drives feature-flag and flag interactions.

## State And Persistence Behavior
State is test-local through temp files and process-wide logging/debug settings. The OTEL test reads runtime memory counters but does not persist data.

## Dependencies And Integration Points
Depends on `daemon/config`, `pflag`, `gotest.tools`, containerd logging, and OpenTelemetry. It protects the command package boundary where CLI flags become daemon config.

## Risks And Test Signals
Key signals are conflict errors for labels/node resources, TLS implicit enablement, log level stability after bad input, CDI defaults, and low allocation count for repeated OTEL counter lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_unix.go -->
# sources/cloud-native/moby/daemon/command/daemon_unix.go

## Purpose
Provides Unix-specific daemon command behavior: default config paths, umask normalization, SIGHUP reload, swarm run root, API port reservation, cgroup parent naming, and containerd startup selection.

## Important APIs, Types, And Functions
`getDefaultDaemonConfigDir`, `getDefaultDaemonConfigFile`, `setDefaultUmask`, `daemonCLI.setupConfigReloadTrap`, `getSwarmRunRoot`, `allocateDaemonPort`, `newCgroupParent`, and `daemonCLI.initContainerd`.

## Control Flow
RootlessKit toggles XDG config lookup through package state. SIGHUP is delivered to a goroutine that repeatedly invokes `reloadConfig`. TCP listener addresses are parsed, hostnames resolved, and each host IP is reserved in libnetwork's port allocator.

## State And Persistence Behavior
The file mutates process umask and installs a process signal handler. Port reservations live in the singleton port allocator. No disk writes occur directly.

## Dependencies And Integration Points
Integrates with `daemon.UsingSystemd`, `daemon/config`, `portallocator`, `homedir`, `os/signal`, and `golang.org/x/sys/unix`.

## Risks And Test Signals
Risks include wrong XDG path selection, surprising process-wide umask effects, hostname resolution failures preventing bind, and systemd cgroup parent formatting. Unix command tests cover config merge behavior; listener tests outside this item exercise listener inheritance.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_unix_test.go -->
# sources/cloud-native/moby/daemon/command/daemon_unix_test.go

## Purpose
Validates Unix-only daemon configuration loading for daemon flags, networking JSON keys, map options, and boolean defaults that are true in the default config.

## Important APIs, Types, And Functions
Uses `defaultOptions`, `loadDaemonCliConfig`, `config.Reload`, and platform-installed flags such as `selinux-enabled`.

## Control Flow
Tests prepare temp daemon JSON files, install default flags, optionally set flags, load the merged config, and assert platform-specific fields. Reload is invoked to ensure normalized boolean values do not cause later conflicts.

## State And Persistence Behavior
Only temp config files and in-memory flag sets are used. The reload callback observes the parsed config but does not alter daemon state.

## Dependencies And Integration Points
Connects command parsing to `daemon/config` Unix platform fields such as SELinux, bridge IP fields, userland-proxy defaults, and log options.

## Risks And Test Signals
Signals include `userland-proxy=false` surviving merge/reload, `bip`, `bip6`, and `ip` decoding into correct fields, and default `EnableUserlandProxy` remaining true when absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_windows.go -->
# sources/cloud-native/moby/daemon/command/daemon_windows.go

## Purpose
Implements Windows-specific daemon command hooks for config defaults, service readiness, shutdown notification, reload signaling, swarm roots, port allocation no-op behavior, and containerd startup decisions.

## Important APIs, Types, And Functions
`getDefaultDaemonConfigFile`, `setPlatformOptions`, `preNotifyReady`, `notifyShutdown`, `daemonCLI.setupConfigReloadTrap`, `getSwarmRunRoot`, `allocateDaemonPort`, `newCgroupParent`, `daemonCLI.initContainerd`, and `validateCPURealtimeOptions`.

## Control Flow
Windows defers the pidfile location until `Root` is known. Service startup is acknowledged before the daemon is fully ready. Reload is driven by a named global Win32 event watched in a goroutine. Containerd is initialized only when a non-legacy runtime needs it.

## State And Persistence Behavior
May set `cfg.Pidfile` under the data root and interacts with global Windows service state. Reload event names include the process ID.

## Dependencies And Integration Points
Integrates with `golang.org/x/sys/windows`, containerd log output, Windows service code in `service_windows.go`, and daemon config runtime names.

## Risks And Test Signals
Risks include service timeout ordering, reload event handle errors being ignored, and incorrect runtime gating around legacy HCS runtime. Windows service and config tests provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/daemon_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/debug/debug.go -->
# sources/cloud-native/moby/daemon/command/debug/debug.go

## Purpose
Centralizes process-level debug mode toggling for daemon command code.

## Important APIs, Types, And Functions
`Enable` sets `DEBUG=1` and containerd log level to debug. `Disable` unsets `DEBUG` and restores info level. `IsEnabled` checks whether `DEBUG` is non-empty.

## Control Flow
The functions are direct setters/getters with no branching beyond environment lookup.

## State And Persistence Behavior
Mutates process environment and global logger level. No durable persistence exists, but changes affect subsequent tests and daemon execution in the same process.

## Dependencies And Integration Points
Uses `os` and `github.com/containerd/log`. Command startup and tests can use this as a coarse global debug switch.

## Risks And Test Signals
The API is intentionally global, so callers must restore state in tests. Tests verify environment and log level transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/debug/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/debug/debug_test.go -->
# sources/cloud-native/moby/daemon/command/debug/debug_test.go

## Purpose
Tests the debug package's environment and logging side effects.

## Important APIs, Types, And Functions
`TestEnable`, `TestDisable`, and `TestEnabled` call `Enable`, `Disable`, `IsEnabled`, `os.Getenv`, and `log.GetLevel`.

## Control Flow
Tests toggle debug mode and assert the immediate process-level result. `TestEnable` registers cleanup to restore `DEBUG` and info log level.

## State And Persistence Behavior
Mutates process environment and global log level during test execution. Cleanup is important because later tests share the process.

## Dependencies And Integration Points
Depends on containerd logging. It verifies that the debug helper remains aligned with the logger used by daemon command code.

## Risks And Test Signals
Signals are exact `DEBUG=1`, empty `DEBUG` after disable, debug/info log levels, and `IsEnabled` returning true only for non-empty env state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/debug/debug_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker.go -->
# sources/cloud-native/moby/daemon/command/docker.go

## Purpose
Builds the `dockerd` Cobra command and exposes a `Runner` abstraction used by daemon entrypoints.

## Important APIs, Types, And Functions
`newDaemonCommand`, package `init`, `Runner`, `daemonRunner.Run`, and `NewDaemonRunner`. Flags include version, config-file, common daemon flags, platform config flags, and service flags.

## Control Flow
Startup creates default config, wraps it in `daemonOptions`, configures Cobra metadata, installs flags, and runs `newDaemonCLI`. `--validate` exits after parsing with `configuration OK`; otherwise execution delegates to platform `runDaemon`.

## State And Persistence Behavior
Package init exports product name to BuildKit API caps and sets `honorXDG` when RootlessKit is detected. Runner setup changes global log format and command IO streams.

## Dependencies And Integration Points
Integrates Cobra, BuildKit API caps, rootless detection, daemon config, version metadata, platform logging, and service flag registration.

## Risks And Test Signals
Risks include config lookup during version-only paths, global rootless path policy, and flag/config coupling. Command and options tests cover flag installation and config merge behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker_unix.go -->
# sources/cloud-native/moby/daemon/command/docker_unix.go

## Purpose
Supplies Unix-specific daemon command run and logging wiring.

## Important APIs, Types, And Functions
`runDaemon` calls `cli.start`; `initLogging` directs containerd log output to stderr.

## Control Flow
There is no extra wrapper behavior on Unix: the daemon CLI starts directly under the provided context.

## State And Persistence Behavior
Only global logger output is mutated. The file performs no disk or daemon state changes by itself.

## Dependencies And Integration Points
Used by `NewDaemonRunner` in `docker.go` and the platform build tags. Depends on `github.com/containerd/log`.

## Risks And Test Signals
Risk is mainly stream routing regressions for daemon logs. Integration coverage comes from command startup tests and CLI execution paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker_windows.go -->
# sources/cloud-native/moby/daemon/command/docker_windows.go

## Purpose
Adds Windows service handling and ETW logging setup around daemon command execution.

## Important APIs, Types, And Functions
`runDaemon` calls `initService`, may clear `Pidfile`, starts `cli.start`, and calls `notifyShutdown`. `initLogging` writes logs to stdout and adds an ETW hook.

## Control Flow
Service registration/unregistration can short-circuit startup. Running as SCM service changes pidfile behavior and routes shutdown status back to service code.

## State And Persistence Behavior
Mutates global logger output/hooks and may clear daemon pidfile config while under service management. ETW hook persists for process lifetime.

## Dependencies And Integration Points
Integrates `service_windows.go`, Microsoft winio ETW logrus hook, containerd logging, and platform `daemonCLI` lifecycle.

## Risks And Test Signals
Risks include swallowed ETW hook setup errors, divergent stdout/stderr behavior from Unix, and service mode suppressing pidfiles. Windows service paths are the primary integration signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/error.go -->
# sources/cloud-native/moby/daemon/command/error.go

## Purpose
Defines a simple command error type carrying a textual status and integer status code.

## Important APIs, Types, And Functions
`StatusError` has `Status` and `StatusCode` fields and implements `error` through `Error`.

## Control Flow
`Error` formats both fields as `Status: <status>, Code: <code>`.

## State And Persistence Behavior
No mutable state or persistence. Values are immutable unless callers modify the struct.

## Dependencies And Integration Points
Uses only `fmt`. Intended for command execution paths that need to return an exit/status detail through the error channel.

## Risks And Test Signals
No direct tests in this subset. The main risk is callers needing structured access but receiving only a formatted string unless they type-assert `StatusError`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/grpclog.go -->
# sources/cloud-native/moby/daemon/command/grpclog.go

## Purpose
Reduces noise from gRPC's default logger by remapping gRPC info, warning, and error streams to lower daemon log levels.

## Important APIs, Types, And Functions
`configureGRPCLog` constructs a `grpclog.LoggerV2` from containerd logger writers: info to trace, warning to debug, and error to warn.

## Control Flow
The function is called before Cobra execution in `daemonRunner.Run` and globally replaces gRPC logging.

## State And Persistence Behavior
Mutates gRPC global logger state for the process lifetime.

## Dependencies And Integration Points
Depends on `containerd/log` and `google.golang.org/grpc/grpclog`. It affects BuildKit/containerd/daemon gRPC integrations.

## Risks And Test Signals
Risk is hidden diagnostics if severity mapping is too low. There are no direct tests here; operational log volume and daemon startup logs are integration signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/grpclog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/httphandler.go -->
# sources/cloud-native/moby/daemon/command/httphandler.go

## Purpose
Multiplexes Docker HTTP API traffic and BuildKit/gRPC traffic on the same HTTP server and configures daemon gRPC tracing/error interceptors.

## Important APIs, Types, And Functions
`httpHandler`, `newHTTPHandler`, `ServeHTTP`, `newGRPCServer`, and `unaryInterceptor`.

## Control Flow
`ServeHTTP` routes HTTP/2 requests with `application/grpc` content to the gRPC server and all other requests to the API handler. `newGRPCServer` installs OTEL stats and BuildKit error interceptors. The unary interceptor skips tracing export calls to avoid recursive traces and logs other gRPC errors.

## State And Persistence Behavior
Keeps references to context, gRPC server, and API handler. No disk persistence. In debug logging, stack traces are written to stderr.

## Dependencies And Integration Points
Integrates BuildKit tracing/error helpers, daemon OTEL utilities, containerd defaults for message sizes, and the Docker API server.

## Risks And Test Signals
Risks include protocol/content-type misclassification, trace-export recursion, and stderr stack output volume under debug. Test signals are mostly integration-level API and BuildKit gRPC behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/httphandler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/main_linux_test.go -->
# sources/cloud-native/moby/daemon/command/main_linux_test.go

## Purpose
Registers Linux-only reexec helper commands before command package tests run.

## Important APIs, Types, And Functions
`TestMain` registers `testListenerNoAddrCmdPhase1` and `testListenerNoAddrCmdPhase2` with `reexec.Register`, then exits early if `reexec.Init` handles a helper process.

## Control Flow
Test process initialization first wires helper names to functions, then either runs the reexec helper path or invokes `m.Run`.

## State And Persistence Behavior
Mutates process-level reexec registry. No durable state.

## Dependencies And Integration Points
Depends on `github.com/moby/sys/reexec`. Supports listener inheritance tests in adjacent Linux command files.

## Risks And Test Signals
Risk is missing helper registration causing subprocess tests to run the normal test binary path. The signal is successful Linux listener tests that depend on these names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/main_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/metrics.go -->
# sources/cloud-native/moby/daemon/command/metrics.go

## Purpose
Starts the daemon Prometheus-style metrics HTTP endpoint when configured.

## Important APIs, Types, And Functions
`startMetricsServer` validates the address, reserves the daemon port, listens on TCP, registers `/metrics` with `go-metrics`, and runs `http.Server.Serve` in a goroutine.

## Control Flow
Empty address is a no-op. Non-empty address must pass `allocateDaemonPort` and `net.Listen`; serving errors other than listener closure are logged.

## State And Persistence Behavior
Creates a live TCP listener and goroutine. No shutdown handle is returned, so lifecycle is tied to process/listener closure.

## Dependencies And Integration Points
Depends on libnetwork port reservation, Go HTTP, containerd logging, and Docker metrics registry handler.

## Risks And Test Signals
Risks include untracked goroutine lifetime, long read-header timeout, and metrics port conflicting with published container ports if reservation fails. Integration signal is `/metrics` availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/options.go -->
# sources/cloud-native/moby/daemon/command/options.go

## Purpose
Defines common daemon CLI options and TLS certificate defaulting behavior.

## Important APIs, Types, And Functions
Constants for default TLS filenames and flag names; package vars sourced from `DOCKER_CONFIG`, `DOCKER_CERT_PATH`, and `DOCKER_TLS_VERIFY`; `daemonOptions`; `defaultCertPath`; `newDaemonOptions`; `installFlags`; `setDefaultOptions`.

## Control Flow
`installFlags` installs debug, validate, TLS, TLS verify, cert path, key path, and host flags. `setDefaultOptions` makes `--tlsverify` imply TLS, defaults TLS verification when TLS is on, nils TLS options when TLS is off, and clears implicit cert/key files that do not exist.

## State And Persistence Behavior
Uses and mutates package-level `configDir` and `dockerCertPath`. Reads certificate file existence but does not write files.

## Dependencies And Integration Points
Integrates `tlsconfig.Options`, daemon config defaults, daemon host validation, pflag, and historical Docker env vars.

## Risks And Test Signals
Risks include package-level env snapshots, non-XDG `DOCKER_CONFIG` legacy behavior, and implicit TLS verification surprises. Tests cover flag installation defaults and daemon config TLS merge behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/options_test.go -->
# sources/cloud-native/moby/daemon/command/options_test.go

## Purpose
Verifies common daemon option flag installation and default certificate paths.

## Important APIs, Types, And Functions
`TestCommonOptionsInstallFlags` and `TestCommonOptionsInstallFlagsWithDefaults` use `newDaemonOptions`, `installFlags`, `pflag.FlagSet.Parse`, and `defaultCertPath`.

## Control Flow
The first test parses explicit TLS cert flags and asserts they populate `TLSOptions`. The second parses no flags and asserts CA, cert, and key paths default under `defaultCertPath`.

## State And Persistence Behavior
No disk writes. Reads package-level default cert path state, which may derive from environment.

## Dependencies And Integration Points
Depends on `daemon/config`, pflag, and test assertions. Protects CLI flag compatibility.

## Risks And Test Signals
Signals are exact path propagation. The tests do not cover `setDefaultOptions` file-existence clearing or env var changes after package init.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/required.go -->
# sources/cloud-native/moby/daemon/command/required.go

## Purpose
Provides Cobra argument validation for commands that accept no positional arguments.

## Important APIs, Types, And Functions
`NoArgs` checks `args` and returns either nil, usage text for commands with subcommands, or a formatted no-arguments error.

## Control Flow
Empty args succeed. Commands with subcommands receive trimmed usage as the error. Leaf commands receive a message with command path, help hint, use line, and short description.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Uses Cobra command metadata and `pkg/errors`. Installed as `Args` for `dockerd` in `docker.go`.

## Risks And Test Signals
Risk is user-facing error format drift. It is indirectly tested by CLI parsing behavior rather than direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/required.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/service_unsupported.go -->
# sources/cloud-native/moby/daemon/command/service_unsupported.go

## Purpose
Provides the non-Windows stub for service flag registration.

## Important APIs, Types, And Functions
`installServiceFlags` accepts a `*pflag.FlagSet` and intentionally does nothing under `!windows`.

## Control Flow
No branching or side effects.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Keeps `docker.go` platform-neutral by providing a build-tagged function that only has behavior on Windows.

## Risks And Test Signals
Risk is minimal; accidental service flags on Unix would be an API change. Command flag tests on Unix implicitly rely on no service flags being installed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/service_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/service_windows.go -->
# sources/cloud-native/moby/daemon/command/service_windows.go

## Purpose
Implements Windows service registration, unregistration, SCM/debug service execution, event log forwarding, panic-file redirection, and service lifecycle signaling for dockerd.

## Important APIs, Types, And Functions
Service flag globals; `installServiceFlags`; `handler`; `etwHook.Levels` and `Fire`; `registerService`; `unregisterService`; `initService`; `handler.started`; `handler.stopped`; `handler.Execute`; `initPanicFile`; `removePanicFile`.

## Control Flow
`initService` handles mutually exclusive register/unregister actions, creates SCM/debug service handlers for `--run-service`, opens the event log when running as a service, starts `svc.Run` or `debug.Run`, and waits for handler readiness. `handler.Execute` reports pending/running/stopping status, reloads on `ParamChange`, stops on SCM stop/shutdown, and returns success or failure exit codes.

## State And Persistence Behavior
Registers/deletes Windows services and event logs, sets service recovery actions, redirects stderr and logger output to `<data-root>/panic.log`, rotates non-empty panic logs to `.old`, and removes an empty panic file after shutdown.

## Dependencies And Integration Points
Integrates Windows SCM packages, eventlog, daemon system checks, command lifecycle, and containerd/log hooks.

## Risks And Test Signals
Risks include global flag pointers, event-log open failures preventing service start, stderr handle restoration only for empty panic logs, and service readiness ordering. Signals come from Windows service registration/start/stop behavior and event log output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/service_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/testfiles/main.go -->
# sources/cloud-native/moby/daemon/command/trap/testfiles/main.go

## Purpose
Provides a tiny test binary that self-signals to exercise the trap package behavior in a separate process.

## Important APIs, Types, And Functions
`main` installs `trap.Trap`, maps `SIGNAL_TYPE` to `SIGTERM`, `SIGQUIT`, or interrupt, and uses `IF_MULTIPLE` to choose one signal or a tight signal loop.

## Control Flow
Cleanup sleeps one second and exits `99`. A goroutine finds the current process and sends the requested signal(s). The main goroutine sleeps long enough for trap behavior to decide the exit path.

## State And Persistence Behavior
Process-only signal state. No filesystem writes.

## Dependencies And Integration Points
Built by `trap_linux_test.go` and imports `daemon/command/trap`.

## Risks And Test Signals
Signals are exit code `99` for first SIGTERM/SIGINT cleanup and `128+signal` for repeated forced termination. SIGQUIT is sent but not part of trap's notify list.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/testfiles/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/trap.go -->
# sources/cloud-native/moby/daemon/command/trap/trap.go

## Purpose
Implements Unix command-style graceful shutdown on first interrupt/terminate and forced process exit after repeated signals.

## Important APIs, Types, And Functions
`forceQuitCount` is `3`. `Trap(cleanup func())` installs `signal.Notify` for `os.Interrupt` and `SIGTERM`.

## Control Flow
A goroutine counts received signals. The first signal launches `cleanup` once in a goroutine. Signals up to the threshold are logged and ignored after cleanup starts. A later signal exits immediately with `128 + signal`.

## State And Persistence Behavior
Installs process-wide signal notification and keeps interrupt count in the goroutine. No disk persistence.

## Dependencies And Integration Points
Uses containerd logging and Go signal/syscall packages. Used by the dockerd process to coordinate graceful cleanup.

## Risks And Test Signals
Risks include off-by-one force-exit semantics, cleanup goroutine still running during repeated signals, and process-wide signal handler interactions. Linux trap tests assert expected exit codes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/trap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/trap_linux_test.go -->
# sources/cloud-native/moby/daemon/command/trap/trap_linux_test.go

## Purpose
Integration-tests trap behavior by compiling and executing the helper program.

## Important APIs, Types, And Functions
`buildTestBinary` runs `go build` for `testfiles/main.go`. `TestTrap` runs cases for TERM and INT, single and repeated.

## Control Flow
Each case starts the helper executable with signal environment variables, waits for it to exit, type-asserts `*exec.ExitError`, and extracts the Unix wait status exit code.

## State And Persistence Behavior
Build artifacts live under `t.TempDir`. Child process signal behavior is isolated from the test process.

## Dependencies And Integration Points
Depends on Go toolchain, Unix signals, `os/exec`, and `gotest.tools`. It tests the public `trap.Trap` function via process exit behavior.

## Risks And Test Signals
Repeated-signal cases use an unbounded loop in the helper goroutine, so timing matters. Passing signals are exit `99` for single cleanup and `128+signal` for forced exit.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/trap/trap_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/commit.go -->
# sources/cloud-native/moby/daemon/commit.go

## Purpose
Implements container-to-image commit and config merge semantics between user changes and the original container image/container config.

## Important APIs, Types, And Functions
`merge` mutates a user config with image defaults. `Daemon.CreateImageFromContainer` performs commit validation, optional pause/unpause, Dockerfile-style config changes, image service commit/tag, event logging, and metrics.

## Control Flow
`merge` fills missing user, ports, env, labels, entrypoint/cmd, healthcheck fields, working dir, volumes, and stop signal. Commit rejects dead/removing containers and running Windows containers, pauses unless disabled or already paused, builds a new config from changes, merges old container config, commits through image service, tags if requested, and logs a commit event.

## State And Persistence Behavior
May pause/unpause the container, creates a persistent image, optionally writes a tag reference, logs events, and updates `metrics.ContainerActions`.

## Dependencies And Integration Points
Integrates daemon container lookup, Dockerfile config builder, image service, distribution references, events, errdefs, and metrics.

## Risks And Test Signals
Risks include merge precedence bugs, Windows running-commit restriction, pause failure ignored, and volume map copy direction preserving image volumes only if user map is initialized. Commit API and image tests outside this file are key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/builder.go -->
# sources/cloud-native/moby/daemon/config/builder.go

## Purpose
Defines daemon JSON configuration structures for BuildKit builder garbage collection, history, and entitlements.

## Important APIs, Types, And Functions
`BuilderGCRule.UnmarshalJSON`, `BuilderGCFilter.MarshalJSON`, `BuilderGCFilter.UnmarshalJSON`, `BuilderGCConfig.IsEnabled`, `BuilderGCConfig.UnmarshalJSON`, and structs `BuilderHistoryConfig`, `BuilderEntitlements`, `BuilderConfig`.

## Control Flow
GC rule and config unmarshalling map deprecated `keepStorage` fields to reserved-space fields. Filter JSON accepts the current array-of-`key=value` form and falls back to a deprecated map form.

## State And Persistence Behavior
No runtime state; these types control daemon JSON decode/encode and thus persisted daemon config semantics.

## Dependencies And Integration Points
Uses BuildKit daemon config duration, daemon internal filters, JSON, sorting, and string normalization. Consumed by `config.Config.Builder`.

## Risks And Test Signals
Risks include silently accepting malformed filters as empty values and compatibility pressure around deprecated fields. Builder config tests cover current/deprecated formats and default enabled behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/builder_test.go -->
# sources/cloud-native/moby/daemon/config/builder_test.go

## Purpose
Tests BuildKit builder GC JSON compatibility and defaults.

## Important APIs, Types, And Functions
`TestBuilderGC`, `TestBuilderGC_DeprecatedKeepStorage`, `TestBuilderGCFilterUnmarshal`, and `TestBuilderGC_Enabled` call `MergeDaemonConfigurations`, JSON unmarshal, and filter match helpers.

## Control Flow
Tests write temp daemon JSON with builder GC policy, merge it into config, and compare expected rules. A regression test feeds malformed filter text without `=` to ensure no panic. Enabled tests table-drive absent/empty/explicit values.

## State And Persistence Behavior
Only temp config files and in-memory structs.

## Dependencies And Integration Points
Depends on `daemon/config`, internal filters, JSON, go-cmp, and gotest tools.

## Risks And Test Signals
Signals include deprecated map filter parsing, `keepStorage` migration, policy preservation, and `IsEnabled` defaulting true unless explicitly false.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/builder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config.go -->
# sources/cloud-native/moby/daemon/config/config.go

## Purpose
Defines the platform-common daemon configuration model, default construction, config-file loading, flag/file conflict detection, validation, reload support, credential masking, and legacy option migration.

## Important APIs, Types, And Functions
Constants for defaults/API versions; maps `flatOptions`, `skipValidateOptions`, `skipDuplicates`, `migratedNamedConfig`; structs `LogConfig`, `NetworkConfig`, `TLSOptions`, `DNSConfig`, `CommonConfig`, `DaemonLogConfig`, `Proxies`; functions `New`, `Reload`, `MergeDaemonConfigurations`, `getConflictFreeConfiguration`, `configValuesSet`, `findConfigurationConflicts`, `ValidateMinAPIVersion`, `Validate`, `parseExecOptions`, `MaskCredentials`, `migrateHostGatewayIP`, `Sanitize`.

## Control Flow
`New` applies common defaults then platform defaults. Config loading reads JSON, decodes BOM-aware UTF-8/UTF-16 variants, flattens non-flat nested keys for conflict detection, adjusts bool flag values for explicit false config values, records `ValuesSet`, unmarshals into `Config`, and runs migrations. Merge overlays flags config onto file config using mergo, then validates.

## State And Persistence Behavior
Reads daemon JSON from disk and carries explicit config keys in `ValuesSet`. It does not write config. Reload calls a supplied callback after validation.

## Dependencies And Integration Points
Integrates pflag, daemon option types, registry validation, generic resource parsing, platform validation hooks, text encodings, and containerd logging formats.

## Risks And Test Signals
Risks include pre-merge reload validation for partial configs, flattening exceptions hiding conflicts, env-driven minimum API constraints, and URL credentials in error messages. Tests cover Unicode, conflicts, validation, reload, DNS parsing, credential masking, and sanitization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_linux.go -->
# sources/cloud-native/moby/daemon/config/config_linux.go

## Purpose
Defines Linux daemon platform configuration, defaults, binary lookup, rootless paths, swarm compatibility checks, and Linux-specific validation.

## Important APIs, Types, And Functions
Constants for IPC/cgroup namespace modes and runtime names; `BridgeConfig`, `DefaultBridgeConfig`, `Config`; methods `GetExecRoot`, `GetInitPath`, `LookupInitPath`, `GetResolvConf`, `IsSwarmCompatible`, `IsRootless`; functions `setPlatformDefaults`, `lookupBinPath`, `validatePlatformConfig`, `validatePlatformExecOpt`, `verifyUserlandProxyConfig`, `verifyDefaultIpcMode`, `validateFirewallBackend`, `validateFwMarkMask`, `verifyDefaultCgroupNsMode`.

## Control Flow
Defaults initialize ulimits, shm size, seccomp, IPC mode, runtime map, cgroup namespace based on cgroup v1/v2, userland proxy path lookup, and rootless or rootful root/exec/pid paths. Validation checks proxy path, IPC mode, fixed IPv6 CIDR, firewall backend, fwmark mask, and cgroup namespace mode.

## State And Persistence Behavior
No writes, but default paths determine where daemon state will persist. Binary lookup reads filesystem/PATH and rootless mode reads homedir helpers.

## Dependencies And Integration Points
Integrates containerd cgroups, rootless detection, bridge validation, daemon opts, homedir, and OS executable lookup.

## Risks And Test Signals
Risks include missing `docker-proxy` only surfacing when proxy remains enabled, rootless environment lookup failures, and swarm incompatibility with nftables unless feature-gated. Linux config tests cover feature merge, init path, host gateway migration, and fwmark parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_linux_test.go -->
# sources/cloud-native/moby/daemon/config/config_linux_test.go

## Purpose
Tests Linux-specific daemon configuration parsing, merging, feature flags, host gateway IP migration, legacy compatibility, and firewall mark validation.

## Important APIs, Types, And Functions
Tests cover `getConflictFreeConfiguration`, `MergeDaemonConfigurations`, `New`, `GetInitPath`, host-gateway IP options, and `validateFwMarkMask`.

## Control Flow
Table tests construct JSON config and flag sets, merge config, assert decoded platform fields, or assert precise conflict/validation errors. Host-gateway tests exercise old/new config names and flag conflicts.

## State And Persistence Behavior
Uses temp daemon JSON files and in-memory flag/config values only.

## Dependencies And Integration Points
Depends on pflag, daemon opts, netip, container API types, and gotest assertions. It guards Linux platform hooks used by common config merge.

## Risks And Test Signals
Signals include named option flattening, default ulimits/log/network opts, feature map conflicts, `docker-init` default precedence, IPv4/IPv6 host gateway cardinality, legacy skip-validate keys, and fwmark mask syntax.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_test.go -->
# sources/cloud-native/moby/daemon/config/config_test.go

## Purpose
Provides broad platform-common tests for daemon config file decoding, conflict detection, validation, reload behavior, API version bounds, DNS parsing, and proxy credential sanitization.

## Important APIs, Types, And Functions
`makeConfigFile`, `TestDaemonConfigurationUnicodeVariations`, `TestFindConfigurationConflicts*`, `TestValidateConfigurationErrors`, `TestValidateConfiguration`, `TestValidateMinAPIVersion`, `TestConfigDNS`, `TestReload*`, `TestMaskURLCredentials`, and `TestSanitize`.

## Control Flow
Tests create temp JSON files, configure pflag sets including named options, merge or reload config, and compare returned config/errors. Validation tests merge partial overrides into defaults before calling `Validate`.

## State And Persistence Behavior
Temp files only. Some reload tests depend on root privileges for default missing config behavior. Global environment is not materially changed.

## Dependencies And Integration Points
Uses mergo, text encodings, registry opts, IPAM opts, pflag, go-cmp, and gotest. It is the main regression suite for `config.go`.

## Risks And Test Signals
Signals include BOM handling, invalid UTF-8 offsets, unknown option errors, masked proxy credentials in conflicts, platform-specific exec-opt validation, reload callback atomicity expectations, DNS scope handling, and duplicate-label normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_windows.go -->
# sources/cloud-native/moby/daemon/config/config_windows.go

## Purpose
Defines Windows daemon platform configuration defaults and validation.

## Important APIs, Types, And Functions
Constants `StockRuntimeName` and `WindowsV1RuntimeName`; `BridgeConfig`, `DefaultBridgeConfig`, `Config`; methods `GetExecRoot`, `GetInitPath`, `IsSwarmCompatible`, `IsRootless`; functions `setPlatformDefaults`, `validatePlatformConfig`, `validatePlatformExecOpt`.

## Control Flow
Defaults derive root, exec-root, and pidfile from `%programdata%`. Validation warns that non-default MTU is ignored and rejects Linux-only firewall backend. Exec options allow `isolation` and reject Linux cgroup driver.

## State And Persistence Behavior
No writes, but default paths define Windows daemon state locations.

## Dependencies And Integration Points
Uses containerd logging, Windows environment, and common config validation hooks.

## Risks And Test Signals
Risks include empty `%programdata%` producing relative paths and warnings rather than errors for ignored MTU. Windows config tests cover merge behavior; common validation tests cover exec-opt platform split.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_windows_test.go -->
# sources/cloud-native/moby/daemon/config/config_windows_test.go

## Purpose
Tests Windows daemon config merge behavior for common fields.

## Important APIs, Types, And Functions
`TestDaemonConfigurationMerge` calls `New`, installs debug/restart/log flags, sets flags, and invokes `MergeDaemonConfigurations`.

## Control Flow
The test reads a JSON file setting debug, overlays explicit restart and log flags, and verifies the merged config combines file and flag sources.

## State And Persistence Behavior
Temp config file only.

## Dependencies And Integration Points
Depends on pflag, daemon opts, and gotest. It covers the Windows implementation of common config merge hooks.

## Risks And Test Signals
Signal is preservation of `Debug` from file and `AutoRestart`/log config from flags. It does not exercise Windows path defaults or service-specific config.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/config_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/opts.go -->
# sources/cloud-native/moby/daemon/config/opts.go

## Purpose
Parses daemon node generic resource configuration into API swarm generic resources.

## Important APIs, Types, And Functions
`ParseGenericResources` accepts `[]string` and returns `[]swarm.GenericResource`.

## Control Flow
Empty input returns nil. Non-empty input is parsed by swarmkit's generic resource parser, then converted from gRPC objects to API objects.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Integrates daemon config validation with swarmkit generic resources and daemon cluster conversion code. Called by `config.Validate`.

## Risks And Test Signals
Risks are parser error propagation and mixed named/discrete resource semantics. Common config tests assert malformed and mixed resources fail.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/config/opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/configs.go -->
# sources/cloud-native/moby/daemon/configs.go

## Purpose
Adds swarm config references to an existing daemon container.

## Important APIs, Types, And Functions
`Daemon.SetContainerConfigReferences` resolves a container by name/id and appends `*swarmtypes.ConfigReference` values to `c.ConfigReferences`.

## Control Flow
The method calls `GetContainer`; on success it appends all refs and returns nil.

## State And Persistence Behavior
Mutates the in-memory container object only. This function does not lock the container or checkpoint to disk by itself.

## Dependencies And Integration Points
Integrates daemon container lookup with swarm config reference handling used later by container mount generation.

## Risks And Test Signals
Risks include no explicit locking/checkpointing and duplicate refs if called repeatedly. Mount-related container code is the downstream signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/configs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container.go -->
# sources/cloud-native/moby/daemon/container.go

## Purpose
Implements daemon-level container lookup, loading, registration, creation, dependency discovery, and common container/host-config validation.

## Important APIs, Types, And Functions
`GetContainer`, `load`, `register`, `newContainer`, `getEntrypointAndArgs`, `GetByName`, `GetDependentContainers`, `setSecurityOptions`, `verifyContainerSettings`, `validateContainerConfig`, `validateHostConfig`, `validateCapabilities`, `validateHealthCheck`, `validatePortBindings`, `translateWorkingDir`.

## Control Flow
Lookup tries exact ID, exact name, then unique prefix through the replica view. Registration initializes stdin pipes, locks the container, adds it to the live store, and checkpoints to the replica/disk. Creation generates ID/name, sets hostname, entrypoint args, image/platform fields, and base metadata. Validation checks working dir, stop signal, env, healthcheck timing, mounts, extra hosts, ports, restart policy, capabilities, isolation, annotations, then platform validation.

## State And Persistence Behavior
`load` reads from disk; `register` writes checkpoint data and updates in-memory stores. `newContainer` constructs unsaved state.

## Dependencies And Integration Points
Integrates container store/view DB, image service, network settings, link index, mount parser, capabilities normalization, errdefs, and daemon platform validation.

## Risks And Test Signals
Risks include non-atomic register add/checkpoint, `getEntrypointAndArgs` assuming non-empty cmd when entrypoint absent, replica/live store skew, and validation gaps on nil configs. Container creation/start tests are downstream signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/archive_windows.go -->
# sources/cloud-native/moby/daemon/container/archive_windows.go

## Purpose
Provides Windows path resolution and stat helpers for archive/copy operations inside a container root filesystem.

## Important APIs, Types, And Functions
`Container.ResolvePath` and `Container.StatPath`.

## Control Flow
`ResolvePath` requires `BaseFS`, strips/checks a Windows system drive, treats input as an absolute container path, resolves the directory in container scope, and appends the final path component. `StatPath` lstats the resolved path and, for symlinks, resolves the symlink target inside the container and reports it as an absolute container path.

## State And Persistence Behavior
Reads filesystem metadata only. No writes.

## Dependencies And Integration Points
Uses `moby/go-archive` drive/path helpers and `Container.GetResourcePath`. Used by archive APIs and Windows secret/config symlink creation.

## Risks And Test Signals
Risks include TOCTOU between resolution and stat, path separator/drive handling, and errors when `BaseFS` is unset. Archive/copy tests are expected integration signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/archive_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/attach_context.go -->
# sources/cloud-native/moby/daemon/container/attach_context.go

## Purpose
Manages a lazily-created cancelable context shared by attach calls for one container.

## Important APIs, Types, And Functions
`attachContext` holds a mutex, context, and cancel function. `init` creates or returns the current context. `cancel` cancels and clears it.

## Control Flow
Both methods lock around context state. After cancellation, a future `init` creates a fresh background-derived context.

## State And Persistence Behavior
In-memory only; cancellation is used to detach active attach operations.

## Dependencies And Integration Points
Used by `Container.AttachContext` and `Container.CancelAttachContext` in `container.go`.

## Risks And Test Signals
Risks include background context lacking daemon cancellation and concurrent attach calls observing a context just before cancellation. Attach behavior tests/integration are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/attach_context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container.go -->
# sources/cloud-native/moby/daemon/container/container.go

## Purpose
Defines the core container model, durable metadata IO, checkpointing, path scoping, logging setup, restart/stdio behavior, env generation, secret/config paths, and containerd task restoration helpers.

## Important APIs, Types, And Functions
`Container`, `ExitStatus`, `SecurityOptions`, `NewBaseContainer`, `FromDisk`, `toDisk`, `CheckpointTo`, `readHostConfig`, `WriteHostConfig`, `CommitInMemory`, `SetupWorkingDirectory`, `GetResourcePath`, `GetRootResourcePath`, `StartLogger`, `StopSignal`, `StopTimeout`, `InitDNSHostConfig`, `BackfillEmptyPBs`, `RestartManager`, `InitializeStdio`, `CreateDaemonEnvironment`, `RestoreTask`, `GetRunningTask`, and `rio`.

## Control Flow
Container load reads `config.v2.json`, migrates deprecated OS into `ImagePlatform`, and reads `hostconfig.json`. Checkpointing atomically writes config and host config, creates a deep-copy snapshot, and saves it to `ViewDB`. Runtime paths are resolved through symlink-in-scope helpers. Logger startup configures driver-specific log paths, optional nonblocking ring buffer, and local read cache. Stdio connects containerd direct IO to stream pipes.

## State And Persistence Behavior
Persists `config.v2.json`, `hostconfig.json`, logs, local log cache, and root-scoped metadata paths. Runtime-only fields include RW layer, exec store, stream config, log driver, containerd handles, and attach context.

## Dependencies And Integration Points
Integrates container API types, containerd IO/tasks, logger drivers, restart manager, volume mounts, network settings, swarm secrets/configs, OCI defaults, symlink scoping, atomic writer, OTEL tracing, and errdefs.

## Risks And Test Signals
Risks include TOCTOU in scoped paths, JSON deep-copy omissions for unexported/runtime fields, log driver cache visibility, nil `HostConfig` assumptions in restart/log code, and backward-compatible port-binding mutation. Tests cover stop signal/timeout, secret targets, JSON log path, and ring logger path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_test.go -->
# sources/cloud-native/moby/daemon/container/container_test.go

## Purpose
Tests selected container helpers for stop signal/timeouts, secret target path construction, and JSON logger path population.

## Important APIs, Types, And Functions
`TestContainerStopSignal`, `TestContainerStopTimeout`, `TestContainerSecretReferenceDestTarget`, `TestContainerLogPathSetForJSONFileLogger`, and `TestContainerLogPathSetForRingLogger`.

## Control Flow
Tests instantiate minimal `Container` values, call helper methods, and assert defaults/overrides. Logger tests create temp roots, start json-file loggers, defer close, and compare `LogPath`.

## State And Persistence Behavior
Logger tests create log files under temp directories. Other tests are in-memory only.

## Dependencies And Integration Points
Depends on container API types, swarm references, jsonfile logger, filepath, syscall, and gotest.

## Risks And Test Signals
Signals include fallback to SIGTERM and default timeout, invalid stop signal fallback, secret mount path defaulting, and nonblocking ring logger preserving json-file API log path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_unix.go -->
# sources/cloud-native/moby/daemon/container/container_unix.go

## Purpose
Implements Unix-specific container mounts, secret/config mount handling, resource updates, lazy unmounts, tmpfs conversion, hostname file creation, and mount point API mapping.

## Important APIs, Types, And Functions
Constants for default stop timeout and secret/config mount paths; `TrySetNetworkMount`, `BuildHostnameFile`, `NetworkMounts`, `CopyImagePathContent`, `ShmResourcePath`, `HasMountFor`, `UnmountIpcMount`, `IpcMounts`, `SecretMounts`, `UnmountSecrets`, `UpdateContainer`, `DetachAndUnmount`, `copyExistingContents`, `TmpfsMounts`, `GetMountPoints`, `ConfigFilePath`.

## Control Flow
Network mounts validate backing files, choose writability from rootfs or bind mount overrides, relabel when needed, and emit mount descriptors. Resource updates reject NanoCPU/CPUPeriod/CPUQuota conflicts, then selectively copy non-zero/non-nil resource fields and restart policy. Detach/unmount resolves mount destinations and unmounts them before volume cleanup.

## State And Persistence Behavior
Writes hostname files, relabels files, copies image contents into volumes, unmounts shm/secrets/volumes, and mutates `HostConfig.Resources` plus restart policy.

## Dependencies And Integration Points
Integrates Linux mount helpers, SELinux labels, containerd continuity copy, volume mount parser, swarm refs, and event logging for volumes.

## Risks And Test Signals
Risks include mount path resolution races, relabel failures except unsupported xattrs, resource zero-values meaning "no update", and memory/memoryswap conflict logic. Container update, mount, and swarm secret/config tests are downstream signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_windows.go -->
# sources/cloud-native/moby/daemon/container/container_windows.go

## Purpose
Implements Windows-specific container mount and update behavior for secrets, configs, volumes, tmpfs no-op handling, hostname no-op, and mount point API mapping.

## Important APIs, Types, And Functions
Constants for Windows secret/config mount paths and default stop timeout; `CreateSecretSymlinks`, `SecretMounts`, `UnmountSecrets`, `CreateConfigSymlinks`, `ConfigMounts`, `DetachAndUnmount`, `TmpfsMounts`, `UpdateContainer`, `BuildHostnameFile`, `GetMountPoints`, `ConfigsDirPath`, `ConfigFilePath`.

## Control Flow
Secrets/configs are exposed through internal mounts and symlinks at requested targets. Resource updates reject nearly all resource fields as unsupported on Windows, but allow restart policy changes subject to AutoRemove conflict rules.

## State And Persistence Behavior
Creates directories and symlinks inside the container rootfs, removes secret mount directories, mutates restart policy, and reports configs under `<container root>/configs`.

## Dependencies And Integration Points
Uses Windows archive path resolution, errdefs invalid-parameter errors, swarm refs, and volume unmount cleanup.

## Risks And Test Signals
Risks include symlink creation on hosts without privilege/support, no resource-update support except restart policy, and Windows configs not using secure secret storage. Windows integration tests should cover secrets/configs and update API behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/env.go -->
# sources/cloud-native/moby/daemon/container/env.go

## Purpose
Merges default environment variables with container/user overrides.

## Important APIs, Types, And Functions
`ReplaceOrAppendEnvValues(defaults, overrides []string) []string`.

## Control Flow
The function indexes default entries by key before `=`, then iterates overrides. Entries without `=` remove an existing default by setting a temporary empty marker. Entries with `=` replace matching keys or append new variables. A final pass removes marked entries.

## State And Persistence Behavior
Mutates the `defaults` slice backing array and returns the resulting slice. No external state.

## Dependencies And Integration Points
Used by `Container.CreateDaemonEnvironment` after daemon defaults, linked env, and user config env are assembled.

## Risks And Test Signals
Risks include in-place mutation surprising callers and empty-string environment values being used as deletion markers. Tests cover replacement, append, and removal behavior plus benchmarks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/env_test.go -->
# sources/cloud-native/moby/daemon/container/env_test.go

## Purpose
Tests and benchmarks environment override merging.

## Important APIs, Types, And Functions
`TestReplaceAndAppendEnvVars`, `BenchmarkReplaceOrAppendEnvValues`, and `benchmarkReplaceOrAppendEnvValues`.

## Control Flow
The unit test overrides `HOME`, appends `TERM`, removes `FOO`, ignores absent `BAR`, and asserts the final slice. Benchmarks vary extra random env count.

## State And Persistence Behavior
In-memory only. Benchmarks use crypto-random bytes to generate arbitrary keys/values.

## Dependencies And Integration Points
Depends on `crypto/rand` and gotest assertions. It validates behavior used by daemon container environment construction.

## Risks And Test Signals
Signal is exact merged env order/content. Benchmark random bytes may contain `=` or empty-ish strings depending on bytes read, but it is performance-oriented rather than semantic coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/env_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/exec.go -->
# sources/cloud-native/moby/daemon/container/exec.go

## Purpose
Defines exec configuration and an in-memory concurrent store for exec sessions associated with containers.

## Important APIs, Types, And Functions
`ExecConfig`, `NewExecConfig`, `ExecConfig.InitializeStdio`, `CloseStreams`, `SetExitCode`, `ExecStore`, `NewExecStore`, `Commands`, `Add`, `Get`, `Delete`, and `List`.

## Control Flow
New exec configs get a random ID, stream config, and `Started` channel. Stdio copies containerd direct IO to stream pipes and closes Windows stdin when not needed. Store operations lock around the map; `Commands` returns a shallow copied map.

## State And Persistence Behavior
Exec configs and store are runtime-only and are not serialized with containers. ExitCode is a pointer to distinguish unset from zero.

## Dependencies And Integration Points
Integrates containerd CIO, daemon stream config, libcontainerd process handles, random string IDs, and container exec API paths.

## Risks And Test Signals
Risks include shallow copy exposing mutable exec config pointers, callers needing to close `Started`, and runtime-only state loss after daemon restart. Exec API tests are downstream signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/health.go -->
# sources/cloud-native/moby/daemon/container/health.go

## Purpose
Wraps API health state with locking and monitor stop-channel lifecycle.

## Important APIs, Types, And Functions
`Health`, `String`, `Status`, `SetStatus`, `OpenMonitorChannel`, and `CloseMonitorChannel`.

## Control Flow
Status reads/writes are mutex-protected. Empty status defaults to unhealthy. Opening a monitor channel succeeds only once; closing it closes the channel, clears it, and marks health unhealthy for compatibility.

## State And Persistence Behavior
Health embeds API health data that may be serialized through container state. The stop channel is runtime-only.

## Dependencies And Integration Points
Uses container API health status constants and containerd logging. Consumed by container state stringification and health monitor code.

## Risks And Test Signals
Risks include defaulting not-yet-setup health to unhealthy and monitor close changing persisted status. Healthcheck integration tests are expected signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/history.go -->
# sources/cloud-native/moby/daemon/container/history.go

## Purpose
Provides sorting for containers by creation time descending.

## Important APIs, Types, And Functions
`History` implements `sort.Interface` through `Len`, `Less`, `Swap`, plus a `sort` helper.

## Control Flow
`Less` returns true when the second container was created before the first, producing newest-first order.

## State And Persistence Behavior
Sorts the slice in place. No external persistence.

## Dependencies And Integration Points
Used by `memoryStore.List` to return containers ordered by creation date.

## Risks And Test Signals
Risk is unstable ordering for equal timestamps. Memory store tests assert newer containers appear first.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/memory_store.go -->
# sources/cloud-native/moby/daemon/container/memory_store.go

## Purpose
Implements the daemon container `Store` interface with a mutex-protected in-memory map.

## Important APIs, Types, And Functions
`memoryStore`, `NewMemoryStore`, `Add`, `Get`, `Delete`, `List`, `Size`, `First`, `ApplyAll`, and private `all`.

## Control Flow
Add overwrites existing IDs. Read operations copy pointers under read lock. `List` sorts via `History`. `ApplyAll` snapshots all containers, then invokes the reducer concurrently for every container and waits.

## State And Persistence Behavior
Runtime-only map from IDs to container pointers. It does not persist or deep-copy containers.

## Dependencies And Integration Points
Satisfies `Store` used by daemon live container registry. `register` in daemon code writes here before checkpointing.

## Risks And Test Signals
Risks include overwriting existing IDs, reducers mutating containers concurrently, and store modifications inside reducers being prohibited only by comment. Tests cover CRUD, ordering, first-filter, and ApplyAll pointer mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/memory_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/memory_store_test.go -->
# sources/cloud-native/moby/daemon/container/memory_store_test.go

## Purpose
Tests the in-memory container store implementation.

## Important APIs, Types, And Functions
Tests call `NewMemoryStore`, `Add`, `Get`, `Delete`, `Size`, `List`, `First`, and `ApplyAll`.

## Control Flow
Each test creates a fresh store, manipulates containers, and asserts map size, lookup result, sorted order, filter result, or reducer mutation.

## State And Persistence Behavior
In-memory only; no disk writes.

## Dependencies And Integration Points
Uses `NewBaseContainer` and `History` sorting indirectly. It validates the live daemon store contract.

## Risks And Test Signals
Signals include Add increasing size, Delete removing entries, newest-first ordering, filter match by ID, and ApplyAll running reducers on stored pointers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/memory_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/monitor.go -->
# sources/cloud-native/moby/daemon/container/monitor.go

## Purpose
Resets runtime container IO/logging state after a container exits so it can be restarted.

## Important APIs, Types, And Functions
`loggerCloseTimeout` and `Container.Reset`.

## Control Flow
`Reset` closes streams, recreates stdin pipes when needed, waits up to ten seconds for the log copier to finish, closes the log driver, logs warnings/errors, and clears runtime logger fields.

## State And Persistence Behavior
Mutates runtime stream/log fields only. No direct disk persistence, though closing log drivers flushes their files/backends.

## Dependencies And Integration Points
Integrates stream config and logger copier/driver lifecycle. Called from container runtime/monitor paths and `InitializeStdio` error handling.

## Risks And Test Signals
Risks include truncated logs on timeout and callers needing to hold the container lock as documented. Container lifecycle/logging tests provide downstream signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/mounts_unix.go -->
# sources/cloud-native/moby/daemon/container/mounts_unix.go

## Purpose
Defines the Unix mount descriptor passed from container metadata to runtime mount setup.

## Important APIs, Types, And Functions
`Mount` fields include `Source`, `Destination`, `Writable`, `Data`, `Propagation`, `NonRecursive`, `ReadOnlyNonRecursive`, and `ReadOnlyForceRecursive`.

## Control Flow
The file has no behavior; it is a platform-specific type shape.

## State And Persistence Behavior
Instances may be marshaled to JSON for runtime configuration, but this file performs no IO.

## Dependencies And Integration Points
Used by Unix container mount methods for network, IPC, secrets, configs, tmpfs, and runtime setup.

## Risks And Test Signals
Risk is field drift with runtime consumers, especially recursive read-only flags. Mount integration tests are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/mounts_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/mounts_windows.go -->
# sources/cloud-native/moby/daemon/container/mounts_windows.go

## Purpose
Defines the reduced Windows mount descriptor.

## Important APIs, Types, And Functions
`Mount` contains `Source`, `Destination`, and `Writable`.

## Control Flow
No executable behavior.

## State And Persistence Behavior
Instances are in-memory descriptors and may be serialized by runtime paths.

## Dependencies And Integration Points
Used by Windows secret/config mount methods and runtime setup.

## Risks And Test Signals
Risk is loss of Unix-only fields by design; Windows runtime consumers must not expect propagation/data flags. Windows mount integration tests are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/mounts_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/rwlayer.go -->
# sources/cloud-native/moby/daemon/container/rwlayer.go

## Purpose
Defines the writable layer abstraction used by containers.

## Important APIs, Types, And Functions
`RWLayer` interface exposes `Mount(mountLabel string)`, `Unmount()`, and `Metadata()`.

## Control Flow
No implementation here; concrete graphdriver/containerd snapshot layers satisfy the interface.

## State And Persistence Behavior
Implementations manage mount reference counts and metadata persistence, but this interface file stores nothing.

## Dependencies And Integration Points
Referenced by `Container.RWLayer` and daemon graph/image storage code.

## Risks And Test Signals
Risk is contract ambiguity around multiple mounts and required unmount pairing. Storage driver and container lifecycle tests validate implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/rwlayer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/state.go -->
# sources/cloud-native/moby/daemon/container/state.go

## Purpose
Models container lifecycle state, wait semantics, containerd handle access, and state-to-API/status string conversions.

## Important APIs, Types, And Functions
`State`, `StateStatus`, `String`, `State`, `Wait`, `conditionAlreadyMet`, `IsRunning`, `GetPID`, `SetExitCode`, `SetRunning`, `SetRunningExternal`, `SetStopped`, `SetRestarting`, `SetError`, `IsPaused`, `IsRestarting`, `SetRemovalInProgress`, `ResetRemovalInProgress`, `IsRemovalInProgress`, `IsDead`, `SetRemoved`, `SetRemovalError`, `Err`, `notifyAndClear`, `C8dContainer`, and `Task`.

## Control Flow
State precedence is running paused, running restarting, running, removing, dead, created, exited. `Wait` returns immediately for already-met conditions or registers stop/removal waiters and bridges them to a context-aware result channel. Stop/restart/removal setters notify and clear relevant waiters.

## State And Persistence Behavior
Many fields serialize inside container config; removal-related fields, waiters, and containerd handles are runtime-only. The embedded mutex is the global container/state lock.

## Dependencies And Integration Points
Integrates API state/wait constants, libcontainerd container/task handles, and human-duration formatting. Used throughout daemon lifecycle and wait APIs.

## Risks And Test Signals
Risks include non-mutually-exclusive running/paused/restarting flags, wait goroutines retained until context/status, and lock requirements for handle access. Tests cover run/stop loops, timeout waits, removal waits, and correct exit status during restart.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/state_test.go -->
# sources/cloud-native/moby/daemon/container/state_test.go

## Purpose
Tests container state transitions and wait-channel behavior.

## Important APIs, Types, And Functions
`mockTask`, `TestStateRunStop`, `TestStateTimeoutWait`, and `TestCorrectStateWaitResultAfterRestart`.

## Control Flow
Tests start waits before and after state transitions, manually lock and mutate state through setters, then assert exit codes, PID values, timeout errors, and removal notification. Restart regression ensures waiters receive the exit code from the restart event even after state returns to running.

## State And Persistence Behavior
In-memory only. Uses context timeouts to prevent leaked waits.

## Dependencies And Integration Points
Depends on container API wait conditions and libcontainerd task interface. It guards daemon wait API correctness.

## Risks And Test Signals
Signals include immediate not-running waits for created/exited state, blocking waits while running, timeout exit code `-1`, final removal exit code, and restart wait exit code preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/state_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/store.go -->
# sources/cloud-native/moby/daemon/container/store.go

## Purpose
Defines the abstract container store contract used by the daemon.

## Important APIs, Types, And Functions
`StoreFilter`, `StoreReducer`, and `Store` interface methods `Add`, `Get`, `Delete`, `List`, `Size`, `First`, and `ApplyAll`.

## Control Flow
No implementation; implementers decide locking and ordering. `memoryStore` is the local implementation in this subset.

## State And Persistence Behavior
The interface does not require persistence or copies. Implementations may be runtime-only.

## Dependencies And Integration Points
Used by daemon container registry code to decouple live container access from concrete storage.

## Risks And Test Signals
Risk is weak contract around duplicate IDs, mutation during `ApplyAll`, and sorted `List` expectations. Memory store tests are the immediate signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/store.go -->
