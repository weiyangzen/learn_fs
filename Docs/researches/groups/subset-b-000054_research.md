# subset-b-000054 Research

Grouped research for containerd daemon startup/config/server files and `ctr` administrative command files. Each section is bounded for reconciliation into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/main.go -->
# sources/cloud-native/containerd/cmd/containerd/command/main.go

Purpose: builds the `containerd` daemon `urfave/cli` application and owns the default foreground daemon startup path. It defines global daemon flags, wires subcommands (`config`, `publish`, `oci-hook`), installs custom help/version behavior, loads and migrates configuration, applies CLI overrides, creates top-level directories, initializes signal/service handling, cleans temporary mounts, and starts the server.

Important APIs/functions: `App()` returns the CLI app; `applyFlags()` overlays CLI values on `srvconfig.Config`; `setLogLevel()` and `setLogFormat()` configure global logging; `dumpStacks()` emits all goroutine stacks and optionally writes a temp log file. The action path uses `defaultConfig()`, `srvconfig.LoadConfigWithPlugins()`, `server.CreateTopLevelDirectories()`, `server.New()`, `server.Start()`, `notifyReady()`, `notifyStopping()` through platform helpers, and Windows service helpers through platform files.

Control flow: if an unexpected positional argument is present, command help is shown. Otherwise the command starts with a default config, conditionally loads the configured TOML path only when it exists or `--config` was explicitly set, applies flags, creates root/state/temp directories, handles Windows service registration/unregistration, starts signal handling before initialization, configures temp mount cleanup, registers tracing log hooks, initializes `server.New()` in a goroutine so startup can be canceled, sends the initialized server to the signal goroutine, starts server listeners, waits for readiness registrations, sends ready notification, then blocks until shutdown.

State and persistence: persistent state is rooted at `config.Root`; transient runtime state is `config.State`; temp mount state is `config.Root/tmpmounts`. CLI `--root` and `--state` are converted to absolute paths. Logging state is process-global logrus/containerd log configuration. Stack dumps are written under `os.TempDir()` when requested.

Dependencies/integration: integrates containerd plugin registry graph for config migrations, server package, mount temp mount cleanup, systemd notification files, Windows service files, OS signals, tracing hooks, and gRPC log suppression. The `--address` flag writes into server plugin config maps for GRPC and default-derived TTRPC.

Risks: startup intentionally runs server initialization asynchronously because backend locks can block; callers must handle early cancellation. `applyFlags()` assumes `config.Plugins` is initialized before address override. `--address` mutates generic `map[string]any` plugin config and returns invalid-argument errors if existing plugin config has the wrong shape. Signal ordering is important because termination can arrive before `serverC` receives the server.

Test signals: behavior is indirectly covered by server/config tests for config loading/migration and directory creation. No direct unit test in this file exercises the full `App().Action` boot sequence, signal races, temp mount cleanup, or service integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/main_unix.go -->
# sources/cloud-native/containerd/cmd/containerd/command/main_unix.go

Purpose: provides Unix-like daemon signal handling for Linux, Darwin, FreeBSD, and Solaris builds.

Important APIs/functions: `handledSignals` includes `SIGTERM`, `SIGINT`, `SIGUSR1`, and `SIGPIPE`; `handleSignals()` starts a goroutine and returns a `done` channel consumed by daemon startup.

Control flow: the goroutine waits for either the initialized `*server.Server` from `serverC` or an OS signal. `SIGPIPE` is ignored to avoid noisy nested logging. `SIGUSR1` triggers `dumpStacks(true)`. Other handled signals notify stopping, cancel the root context, stop the server if available, close `done`, and exit.

State and persistence: stores only an in-goroutine pointer to the server. `SIGUSR1` stack dumps persist to a temp file through `dumpStacks(true)`.

Dependencies/integration: called by daemon startup after `signal.Notify(signals, handledSignals...)`. Integrates with systemd notification variants via `notifyStopping()` and with `server.Stop()`.

Risks: if multiple termination signals arrive, `done` closes once because the goroutine returns. Shutdown before `serverC` delivery cancels context without stopping a nil server. The buffered signal channel in `main.go` reduces but does not remove all ordering risks.

Test signals: no local unit tests. Behavior is platform/runtime integration oriented.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/main_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/main_windows.go -->
# sources/cloud-native/containerd/cmd/containerd/command/main_windows.go

Purpose: provides Windows signal handling, ETW logging integration, and a Windows stack-dump trigger for the daemon.

Important APIs/functions: `handledSignals` handles `os.Interrupt`; `handleSignals()` mirrors Unix shutdown behavior; `setupDumpStacks()` creates a secured global Win32 event; `etwCallback()` dumps stacks on ETW capture-state requests; `init()` registers an ETW provider and logrus hook.

Control flow: `handleSignals()` starts a goroutine that records the server from `serverC`, handles interrupt by notifying stopping, canceling context, stopping the server, and closing `done`, then calls `setupDumpStacks()`. Stack dumps can be requested by signaling `Global\stackdump-<pid>` or by ETW provider capture.

State and persistence: stack dumps can be written to temp files. The Win32 event and ETW provider are intentionally process-lifetime resources.

Dependencies/integration: integrates `Microsoft/go-winio` ETW packages, Win32 security descriptors/events, logrus hooks, and containerd server shutdown.

Risks: event creation failures only log and do not fail startup. The stackdump goroutine waits forever for the process lifetime. ETW hook/provider are not explicitly closed.

Test signals: no local tests cover Windows signal, ETW, or event behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/main_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/notify_no_systemd.go -->
# sources/cloud-native/containerd/cmd/containerd/command/notify_no_systemd.go

Purpose: supplies no-op systemd notification functions for Linux builds compiled with `no_systemd`.

Important APIs/functions: `notifyReady(context.Context) error` and `notifyStopping(context.Context) error` both return nil.

Control flow: daemon startup and shutdown can call these functions unconditionally without linking `go-systemd`.

State and persistence: none.

Dependencies/integration: selected by build tag `linux && no_systemd`; keeps the same function signatures as systemd-enabled builds.

Risks: service managers expecting readiness/stopping notifications will not receive them in this build variant.

Test signals: no local tests; behavior is trivial and build-tag selected.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/notify_no_systemd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/notify_systemd.go -->
# sources/cloud-native/containerd/cmd/containerd/command/notify_systemd.go

Purpose: implements Linux systemd readiness and stopping notifications for normal Linux builds.

Important APIs/functions: `notifyReady()` sends `SdNotifyReady`; `notifyStopping()` sends `SdNotifyStopping`; `sdNotify()` wraps `daemon.SdNotify(false, state)` and logs whether a notification was actually sent.

Control flow: daemon startup calls ready after server readiness waits complete; signal handling calls stopping before canceling and stopping the server. `SdNotify` may return `notified=false` when `NOTIFY_SOCKET` is absent, which is logged at debug level.

State and persistence: no local persistent state; uses systemd notification socket from environment.

Dependencies/integration: selected by `linux && !no_systemd`; depends on `github.com/coreos/go-systemd/v22/daemon` and containerd logging.

Risks: notification errors are surfaced to callers, but main startup only warns on ready failure while shutdown logs stopping failure and continues.

Test signals: no local tests exercise systemd notification behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/notify_systemd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/notify_unsupported.go -->
# sources/cloud-native/containerd/cmd/containerd/command/notify_unsupported.go

Purpose: supplies no-op notification functions on non-Linux platforms.

Important APIs/functions: `notifyReady()` and `notifyStopping()` return nil.

Control flow: keeps daemon startup and shutdown platform-neutral by allowing unconditional calls.

State and persistence: none.

Dependencies/integration: selected by `!linux`; pairs with Windows and other non-Linux signal/service files.

Risks: readiness/stopping notification is intentionally unsupported outside Linux/systemd.

Test signals: no local tests; behavior is trivial.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/notify_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/oci-hook.go -->
# sources/cloud-native/containerd/cmd/containerd/command/oci-hook.go

Purpose: implements the hidden-style `containerd oci-hook` utility that templates hook arguments/environment from OCI runtime hook state and then `exec`s the requested hook binary.

Important APIs/functions: `ociHook` CLI command; `hookSpec` shallow config struct; `loadSpec()` reads bundle `config.json`; `loadHookState()` decodes OCI state from stdin; `templateContext` exposes `id`, `bundle`, `rootfs`, `pid`, `annotation`, and `status`; `templateList.render()` rewrites each argument/env entry; `render()` executes Go templates.

Control flow: command reads `specs.State` from stdin, loads bundle OCI config, builds a template context, templates CLI args and current environment, then replaces the process with `syscall.Exec(args[0], args, env)`.

State and persistence: reads bundle config and stdin; does not write state. Process image is replaced on success.

Dependencies/integration: uses Open Containers runtime-spec state/root structs, containerd OCI config filename constant, Go `text/template`, and Unix `syscall.Exec`.

Risks: no explicit check that at least one command arg exists before indexing `args[0]`. `newTemplateContext()` assumes `spec.Root` is non-nil and accesses `spec.Root.Path`. Template execution errors abort the hook; templates can expose annotation values into args/env.

Test signals: no local tests for nil root, missing args, or template behavior in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/oci-hook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/publish.go -->
# sources/cloud-native/containerd/cmd/containerd/command/publish.go

Purpose: implements `containerd publish`, a small binary path for publishing a protobuf `Any` event to containerd's events service.

Important APIs/functions: `publishCommand`; `getEventPayload()` reads stdin and unmarshals `types.Any`; `connectEvents()` builds an `EventsClient`; `connect()` creates a gRPC client using the containerd dialer and insecure local credentials.

Control flow: command injects the requested namespace into context, validates `--topic`, reads the event payload from stdin, dials `--address`, and calls `Events.Publish`. gRPC errors are converted to native errdefs.

State and persistence: reads stdin only; persists event by sending it to the daemon's events service.

Dependencies/integration: integrates `eventsapi`, containerd namespace helpers, protobuf wrapper package, `errgrpc`, gRPC backoff, and `pkg/dialer`.

Risks: `--address` has no command-local default and depends on app-level flag/default behavior. The connection is not explicitly closed in this helper. Stdin must already contain a serialized protobuf `Any`, not JSON.

Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/publish.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/service_unsupported.go -->
# sources/cloud-native/containerd/cmd/containerd/command/service_unsupported.go

Purpose: provides non-Windows stubs for Windows service integration hooks.

Important APIs/functions: `serviceFlags()`, `applyPlatformFlags()`, `registerUnregisterService()`, and `launchService()` are no-ops on `!windows`.

Control flow: daemon startup can call service hooks unconditionally; on non-Windows no flags are added and no early stop or service launch occurs.

State and persistence: none.

Dependencies/integration: selected by `!windows`; references server type and cli package for signature compatibility.

Risks: none beyond platform-specific feature absence.

Test signals: no local tests; stub behavior is trivial.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/service_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/service_windows.go -->
# sources/cloud-native/containerd/cmd/containerd/command/service_windows.go

Purpose: implements Windows Service Control Manager integration, log redirection, panic log handling, and service lifecycle shutdown for `containerd`.

Important APIs/functions: `serviceFlags()` adds service-name/register/unregister/run-service/log-file flags; `applyPlatformFlags()` captures flag values in package globals; `registerService()` and `unregisterService()` manage SCM entries; `registerUnregisterService()` handles early register/unregister/run-service setup; `launchService()` starts the SCM/debug service runner; `handler.Execute()` handles stop/shutdown; `initPanicFile()` redirects `STD_ERROR_HANDLE`; `removePanicFile()` removes empty panic logs.

Control flow: daemon startup applies flags and calls `registerUnregisterService(root)`. Register/unregister modes perform SCM operations and stop startup. Run-service mode allocates a console, initializes `root/panic.log`, redirects stderr/logrus/stdlog to either `--log-file` or NUL, then later `launchService()` starts the SCM handler and waits for it to report running. On SCM stop/shutdown, the handler stops the server, removes an empty panic file, closes `done`, and exits.

State and persistence: uses package-level service flags, panic file handle, and old stderr handle. Creates or rotates `panic.log` under the containerd root. Optional `--log-file` receives logrus/stdlog/stderr output.

Dependencies/integration: depends on `golang.org/x/sys/windows/svc`, `svc/mgr`, `svc/debug`, Win32 console/std-handle APIs, logrus, stdlib log, and containerd server stop semantics.

Risks: package globals mean tests or multiple app instances in one process would share service state. Panic file rotation ignores `os.Rename` errors. Running as service with no log file intentionally discards normal logs, leaving only panic diagnostics. SCM recovery actions are fixed to two restarts.

Test signals: no local tests cover Windows SCM behavior, log redirection, panic file rotation, or service stop.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/command/service_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/main.go -->
# sources/cloud-native/containerd/cmd/containerd/main.go

Purpose: process entrypoint for the `containerd` binary.

Important APIs/functions: `main()` constructs `command.App()` and runs it with `os.Args`. The blank import of `cmd/containerd/builtins` registers built-in plugins.

Control flow: errors from the CLI app are printed to stderr as `containerd: <err>` and exit code 1 is returned.

State and persistence: no local state; plugin registration happens through imported package init functions.

Dependencies/integration: integrates daemon command package and builtins plugin registration.

Risks: if builtins import is removed, server plugin graph will be incomplete. Error formatting is intentionally minimal.

Test signals: no local tests; behavior is entrypoint glue.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/config/config.go -->
# sources/cloud-native/containerd/cmd/containerd/server/config/config.go

Purpose: defines containerd daemon configuration, TOML loading, imports, migration, merging, plugin config decoding, and disabled-plugin filtering.

Important APIs/types/functions: `Config` is the daemon config root; `StreamProcessor`, `GRPCConfig`, `TTRPCConfig`, `Debug`, `MetricsConfig`, `CgroupConfig`, and `ProxyPlugin` model config sections. `ValidateVersion()`, `MigrateConfig()`, `MigrateConfigTo()`, `v1MigratePluginName()`, `v1Migrate()`, `serviceMigrate()`, `Decode()`, `LoadConfig()`, `LoadConfigWithPlugins()`, `loadConfigFile()`, `resolveImports()`, `mergeConfig()`, `sliceTransformer`, and `V2DisabledFilter()` are the main APIs.

Control flow: loading starts with a pending queue seeded by the root config path. Each config is decoded with strict unknown-field logging fallback, optionally migrated from its version to the target `out.Version`, plugin-specific migrations run once per version step, config is merged into `out`, imports are resolved relative to the parent file or globbed, and circular imports are skipped via `loaded`. After all files, `ValidateVersion()` rejects too-new versions and short plugin names in disabled/required lists.

State and persistence: reads TOML files only. Merge behavior mutates the output `Config`: scalar zero values generally do not override non-zero values, slices append unique entries, plugin maps are merged by `mergo`, and `StreamProcessors`, `ProxyPlugins`, and `Timeouts` copy keys from later configs. Service migration moves legacy top-level GRPC/TTRPC/debug/metrics data into plugin config maps and clears migrated legacy fields.

Dependencies/integration: uses `pelletier/go-toml/v2` for strict/fallback decode, `mergo` for merge semantics, plugin registrations for config migration callbacks, containerd `version.ConfigVersion`, logging, and plugin URI filtering.

Risks: migration array length must track `version.ConfigVersion`. `LoadConfigWithPlugins()` uses root config version as the upper bound for drop-in config versions, so higher-version imports fail. Generic `map[string]any` plugin configs require careful type handling. `mergeConfig()` comments require updates when new map fields are added. `serviceMigrate()` has subtle compatibility behavior for deriving TTRPC from legacy GRPC.

Test signals: heavily covered by `config_test.go`: migration count, merge behavior, import resolution, unknown/default version behavior, plugin decode, CRI drop-in merge cases, service migration, and v3 TTRPC derivation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/config/config_test.go -->
# sources/cloud-native/containerd/cmd/containerd/server/config/config_test.go

Purpose: validates daemon config loading, merging, imports, migration, and service config migration behavior.

Important APIs/functions tested: `migrations`, `mergeConfig()`, `resolveImports()`, `LoadConfig()`, `LoadConfigWithPlugins()`, `Config.Decode()`, `Config.MigrateConfig()`, `serviceMigrate()`, and `testMergeConfig()` helper.

Control flow: tests create temporary TOML files, load them into `Config`, assert merged/migrated output, and in some cases marshal plugin subtrees back to TOML to compare expected structure. `TestServiceMigrate` uses subtests to cover full migration, TTRPC default derivation, explicit UID/GID preservation, existing plugin config preservation, and empty config.

State and persistence: uses `t.TempDir()` and temporary config files. No repository state is mutated.

Dependencies/integration: uses `testify/assert`, `testify/require`, `pelletier/go-toml/v2`, containerd defaults/version, and `logtest`.

Risks covered: catches missing migration functions when config version advances; validates import circularity handling; prevents higher-version drop-ins from silently loading; protects sparse GRPC import merge semantics; ensures legacy service fields migrate to version 4 plugin blocks.

Test gaps: tests focus on config behavior, not daemon startup. Some assertions compare TOML formatting, which can be sensitive to encoder output changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/server.go -->
# sources/cloud-native/containerd/cmd/containerd/server/server.go

Purpose: initializes and manages the main containerd server by applying process config, loading plugins, registering proxy plugins, starting server plugins, tracking readiness, and stopping plugin instances.

Important APIs/types/functions: `CreateTopLevelDirectories()`, `New()`, `recordConfigDeprecations()`, `server` interface, `Server` struct, `Start()`, `Stop()`, `RegisterReadiness()`, `Wait()`, `LoadPlugins()`, `proxyClients.getClient()`, and `readString()`.

Control flow: `New()` applies platform process settings, parses timeout config into global timeout registry, loads plugin graph, registers stream processors, computes GRPC/TTRPC addresses from plugin config with defaults, initializes plugins in dependency order, decodes plugin config, tracks required plugin failures, collects server plugins, and records deprecation hooks. `Start()` starts collected server plugins. `Stop()` walks initialized plugins in reverse and closes instances implementing `io.Closer`.

State and persistence: creates root/state/temp directories with permissions in `CreateTopLevelDirectories()`. Plugin init contexts receive per-plugin root/state directories and server addresses. `Server.ready` is a wait group used by plugins to delay readiness. Proxy gRPC client connections are cached by address in `proxyClients`.

Dependencies/integration: integrates plugin registry, proxy snapshot/content/sandbox/diff clients, OpenTelemetry gRPC stats, `dialer`, defaults, `timeout`, stream processor registration, warning service, and platform-specific `apply()`.

Risks: required plugin handling and readiness registration are strict: a plugin that registers readiness cannot later fail without aborting startup. Proxy plugin registration captures loop variables carefully through local variables; changes here can introduce closure bugs. `Stop()` logs close errors but continues. `readString()` only traverses `map[string]any` and ignores other TOML-decoded shapes.

Test signals: `server_test.go` covers top-level directory validation and plugin config migration through `New()`. Plugin graph, proxy plugin behavior, readiness, and server start/stop ordering rely on broader integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/server_linux.go -->
# sources/cloud-native/containerd/cmd/containerd/server/server_linux.go

Purpose: applies Linux-specific daemon process settings.

Important APIs/functions: `apply(ctx, config)` sets OOM score and optionally moves the daemon process into a configured cgroup.

Control flow: if `config.OOMScore` is non-zero, it attempts to write the process OOM score and logs failures without aborting. If `config.Cgroup.Path` is set, cgroup v2 mode loads and adds the process; cgroup v1 mode loads or creates the cgroup and adds the process.

State and persistence: mutates kernel process OOM score and cgroup membership. May create a cgroup v1 path with empty Linux resources.

Dependencies/integration: uses `containerd/cgroups/v3`, cgroup1/cgroup2 packages, `sys.SetOOMScore`, runtime-spec LinuxResources, and logging.

Risks: OOM score failure is non-fatal, but cgroup membership failures are fatal. cgroup v1 deleted-path handling creates a new cgroup; cgroup v2 expects load success.

Test signals: no local unit tests in this file; process/cgroup behavior is environment-dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/server_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/server_other.go -->
# sources/cloud-native/containerd/cmd/containerd/server/server_other.go

Purpose: supplies a no-op server process config hook on non-Linux platforms.

Important APIs/functions: `apply(context.Context, *srvconfig.Config) error` returns nil.

Control flow: `server.New()` can call `apply()` unconditionally across platforms.

State and persistence: none.

Dependencies/integration: selected by `!linux`.

Risks: OOM score and cgroup config are ignored outside Linux.

Test signals: no local tests; stub behavior is trivial.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/server_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/server_test.go -->
# sources/cloud-native/containerd/cmd/containerd/server/server_test.go

Purpose: validates server directory setup errors and plugin config migration integration through `server.New()`.

Important APIs/functions tested: `CreateTopLevelDirectories()`, `srvconfig.LoadConfigWithPlugins()`, plugin `ConfigMigration`, and `New()`.

Control flow: directory tests assert root/state empty or equal paths fail with exact errors. `TestMigration` registers temporary plugins, writes an older-version config, runs config loading with plugin migration callbacks, and initializes a server to ensure migrated config reaches the correct plugin.

State and persistence: uses temporary config files and resets global plugin registry around migration test.

Dependencies/integration: uses plugin registry graph ordering, TOML marshal, version config number, and `testify/assert`.

Risks covered: prevents invalid root/state combinations and verifies plugin migration data can move between plugin IDs before initialization.

Test gaps: does not start server listeners, stop plugins, test readiness, or cover proxy plugin registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/containerd/server/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/app/main.go -->
# sources/cloud-native/containerd/cmd/ctr/app/main.go

Purpose: constructs the `ctr` CLI application and registers core administrative/debug commands.

Important APIs/functions: `extraCmds` extension slice, `init()` for gRPC log suppression and help/version flag customization, and `New()` for CLI app construction.

Control flow: `New()` sets app metadata, disables slice flag separator, enables bash completion, defines global flags (`debug`, `address`, `timeout`, `connect-timeout`, `namespace`), registers command modules, appends platform extra commands, and sets a `Before` hook that turns on debug logging.

State and persistence: global CLI flags influence later command contexts and client connections. No direct persistence.

Dependencies/integration: imports many `cmd/ctr/commands/*` packages for command registration, default address and namespace values, containerd logging, and version metadata.

Risks: `ctr` is explicitly unsupported/debug-oriented, so command compatibility is not guaranteed. Global `cli.VersionFlag`/`cli.HelpFlag` mutations affect the process-wide urfave/cli package.

Test signals: no local tests in this subset for app assembly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/app/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/app/main_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/app/main_unix.go

Purpose: adds the `shim` command to `ctr` on non-Windows builds.

Important APIs/functions: `init()` appends `shim.Command` to `extraCmds`.

Control flow: package init runs before `app.New()`, so the shim command appears after the common command list.

State and persistence: mutates package-level `extraCmds`.

Dependencies/integration: selected by `!windows`; integrates `cmd/ctr/commands/shim`.

Risks: order depends on init-time append. Windows builds intentionally omit this command.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/app/main_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/client.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/client.go

Purpose: centralizes `ctr` command context creation and containerd client construction.

Important APIs/functions: `AppContext()` injects namespace, timeout, and optional `SOURCE_DATE_EPOCH`; `NewClient()` checks socket accessibility, creates a containerd client with connect timeout, creates app context, and emits server deprecation warnings unless suppressed.

Control flow: each command calls `NewClient()`, defers cancel, then uses the returned client/context. Deprecation warnings are fetched from the introspection service unless `CONTAINERD_SUPPRESS_DEPRECATION_WARNINGS` parses true.

State and persistence: reads environment variables `SOURCE_DATE_EPOCH` and `CONTAINERD_SUPPRESS_DEPRECATION_WARNINGS`; no writes.

Dependencies/integration: containerd client package, namespace package, epoch helper, logging, and OS socket stat.

Risks: `NewClient()` requires the socket path to exist before dialing, which can reject dialer-supported non-files if used unexpectedly. Deprecation checking adds an introspection RPC to most commands and only warns on failure.

Test signals: no local tests in this subset; behavior is widely used by command modules.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/cni.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/cni.go

Purpose: defines metadata used when `ctr run` integrates with CNI and helper naming for namespaced container IDs.

Important APIs/types/functions: `CtrCniMetadataExtension` extension name; `NetworkMetaData` with `EnableCni`; `init()` registers the typeurl; `FullID()` returns `<namespace>-<containerID>` when namespace is present.

Control flow: type registration happens at init. `FullID()` reads namespace from context and formats accordingly.

State and persistence: no persistent state; typeurl registration is process-global.

Dependencies/integration: containerd client `Container`, namespace package, and typeurl registry.

Risks: full ID formatting can collide if namespaces/container IDs contain separator-like content, but matches existing ctr convention.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/cni.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/commands.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/commands.go

Purpose: provides shared flag sets and helper functions reused across `ctr` commands.

Important APIs/functions: exported flag groups `SnapshotterFlags`, `SnapshotterLabels`, `LabelFlag`, `RegistryFlags`, `RuntimeFlags`, `ContainerFlags`; `ObjectWithLabelArgs()`, `LabelArgs()`, `AnnotationArgs()`, `PrintAsJSON()`, and `WritePidFile()`.

Control flow: command packages append or consume these flag groups. Label parsing treats missing `=` as `true`; annotation parsing rejects missing `=`. `WritePidFile()` uses an atomic file writer after resolving an absolute path.

State and persistence: `WritePidFile()` writes a pid file atomically. Other helpers only parse CLI input or print JSON.

Dependencies/integration: containerd defaults, atomicfile helper, urfave/cli, JSON encoding.

Risks: `LabelArgs()` accepts empty keys and treats bare keys as true. `PrintAsJSON()` prints an error to stderr but still prints the marshaled string variable, which will be empty on marshal failure.

Test signals: no local tests in this subset; functions are exercised by command behavior elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/commands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/commands_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/commands_unix.go

Purpose: adds Unix/Linux runtime and container flags and returns runtime-specific option structs.

Important APIs/functions: `init()` appends runc/rootfs/cgroup/resource/device flags; `getRuncOptions()` builds runc `options.Options`; `RuntimeOptions()` validates and returns runc or generic runtime options.

Control flow: runc-specific flags are only valid with runtime `io.containerd.runc.v2`. `--runc-systemd-cgroup` requires a `--cgroup` flag from other command sets. `--runtime-config-path` returns `runtimeoptions.Options` for non-runc runtimes.

State and persistence: no persistence; creates protobuf option structs for container/task creation.

Dependencies/integration: runc options protobuf, runtimeoptions v1, urfave/cli.

Risks: validation references `--cgroup`, which is not declared in this file but may be supplied by commands that combine flag sets. Miscombined flags can produce confusing validation.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/commands_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/commands_windows.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/commands_windows.go

Purpose: adds Windows-specific container resource/device flags and stubs runtime options.

Important APIs/functions: `init()` appends CPU count/shares/max and Windows device flags; `RuntimeOptions()` returns nil.

Control flow: Windows builds mutate shared `ContainerFlags` during init. Runtime option construction is currently delegated elsewhere or unsupported.

State and persistence: no persistence.

Dependencies/integration: selected on Windows; uses urfave/cli.

Risks: runtime-specific Windows options are not produced by `RuntimeOptions()`, so consumers expecting options must handle nil.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/commands_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/containers/checkpoint.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/containers/checkpoint.go

Purpose: implements `ctr containers checkpoint`, creating a checkpoint image/reference from a container.

Important APIs/functions: `checkpointCommand` with `--rw`, `--image`, and `--task` flags.

Control flow: validates container ID and checkpoint ref, creates client/context, builds checkpoint options always including runtime metadata and optionally image/rw/task, loads the container, tries to load its task, pauses the task if present, defers resume, and calls `container.Checkpoint(ctx, ref, opts...)`.

State and persistence: writes checkpoint data into containerd image/content metadata under the requested ref. Temporarily pauses a running task.

Dependencies/integration: containerd client checkpoint APIs, `errdefs.IsNotFound`, and shared client helper.

Risks: if task pause succeeds but checkpoint or resume fails, resume errors are printed but not returned when checkpoint already failed. The command does not inspect task status before pausing.

Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/containers/checkpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/containers/containers.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/containers/containers.go

Purpose: implements `ctr containers` parent command and create/list/delete/label/info subcommands.

Important APIs/functions: `Command`, `createCommand`, `listCommand`, `deleteCommand`, `deleteContainer()`, `setLabelsCommand`, and `infoCommand`.

Control flow: create validates either config-file mode or image/ref mode and delegates to `run.NewContainer()`. List queries containers and prints quiet IDs or a table. Delete loads each container, deletes stopped/created tasks if present, and deletes the container with optional snapshot cleanup. Label updates container labels. Info prints container metadata, unmarshalling `Spec` with typeurl when present or when `--spec` is set.

State and persistence: creates/deletes container metadata, may delete snapshots, updates labels, and reads task/container state.

Dependencies/integration: shared command flags, `cmd/ctr/commands/run`, containerd client/container APIs, task IO loading via `cio.Load`, typeurl, errdefs, and tabwriter output.

Risks: delete refuses non-stopped containers and returns first error while logging subsequent failures. Create computes local `id/ref` validation but ultimately relies on `run.NewContainer()` for actual construction. Label output order is map-dependent.

Test signals: no local unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/containers/containers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/containers/restore.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/containers/restore.go

Purpose: implements `ctr containers restore`, restoring a container and optional live task from a checkpoint image/ref.

Important APIs/functions: `restoreCommand` with `--rw` and `--live`.

Control flow: validates target container ID and checkpoint ref, loads or fetches the checkpoint image, builds restore options for image/spec/runtime plus optional rw layer, calls `client.Restore()`, inspects the restored OCI spec for terminal use, creates a task with optional checkpoint data for live restore, starts it, and if TTY is used, waits, handles resize, deletes the task, and returns exit code.

State and persistence: creates restored container metadata and possibly a running task; may fetch checkpoint content from a remote; may restore writable layer state.

Dependencies/integration: containerd restore APIs, tasks helper package, console package, `cio`, errdefs, log.

Risks: non-TTY restore starts the task and returns without waiting or deleting it. TTY path depends on console raw-mode reset. Fetch-on-not-found is automatic and may surprise offline users.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/containers/restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/content/content.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/content/content.go

Purpose: implements the `ctr content` command family for content-store CRUD, active ingests, labels, editing blobs, and low-level remote fetch/push operations.

Important APIs/functions: `Command`, `getCommand`, `ingestCommand`, `activeIngestCommand`, `listCommand`, `setLabelsCommand`, `editCommand`, `deleteCommand`, `fetchObjectCommand`, `fetchBlobCommand`, `pushObjectCommand`, `edit()`, and `onCloser`.

Control flow: commands create a containerd client when operating on local content. `get` streams a blob to stdout. `ingest` writes stdin as a blob with optional expected descriptor. `active` lists active writer statuses. `list` walks content metadata. `label` updates selected label field paths. `edit` copies a blob to a temp file, runs `$EDITOR` command through `sh -c`, writes edited content back under an `edit-<digest>` ref, commits by writer digest, and prints the new digest. `delete` removes blobs. Remote object/blob commands use resolver fetchers. `push-object` reads a local blob and uploads it with a supplied media type.

State and persistence: reads/writes content blobs, content labels, ingest statuses, temp edit files, and remote registry content.

Dependencies/integration: content store APIs, remotes resolver APIs, digest parsing, Docker units, tabwriter, command registry resolver helpers, and `os/exec`.

Risks: `edit()` runs the editor via shell interpolation, so editor strings are shell-evaluated. `push-object` requires caller-supplied media type and digest. Label path construction can be sensitive to label keys containing path separators/dots. `ingest` expects a single invocation and notes it is not reentrant.

Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/content/content.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/content/fetch.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/content/fetch.go

Purpose: implements `ctr content fetch`, which pulls image manifests/configs/layers into the content store without unpacking, plus progress tracking helpers.

Important APIs/types/functions: `fetchCommand`, `FetchConfig`, `NewFetchConfig()`, `Fetch()`, `ShowProgress()`, `Jobs`, `StatusInfoStatus`, `StatusInfo`, and `Display()`.

Control flow: command creates client/context, builds resolver/platform/metadata/progress config from flags, and calls `Fetch()`. `Fetch()` tracks descriptors through an image handler, configures pull labels/resolver/platforms/all-metadata options, starts a progress goroutine polling content store statuses, calls `client.Fetch()`, cancels progress, waits for final display, and returns the image metadata.

State and persistence: stores fetched content and image metadata through containerd fetch. Progress state is in-memory plus content-store active status reads.

Dependencies/integration: shared registry resolver, containerd remote options, content store, image handlers, platform matching, `httpdbg`, progress writer, errdefs.

Risks: progress totals are approximate and comments note restart skew. `metadata-only` sets `AllMetadata` and a matcher of `platforms.Any()` to effectively avoid platform blobs. A suspicious flag check references `max-concurrent-uploaded-layers` in fetch config, likely shared with push/upload options rather than fetch.

Test signals: no local tests for progress/status behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/content/fetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/content/prune.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/content/prune.go

Purpose: implements `ctr content prune references`, removing GC reference labels from layer content to allow garbage collection.

Important APIs/functions: `pruneCommand`, `pruneReferencesCommand`, `isLayerLabel()`, and `isInteger()`.

Control flow: command creates client/context, optionally sets debug logging for dry run, walks all content, identifies layer reference labels by current and legacy prefixes, removes matching labels unless dry run, updates changed content records, creates a short-lived random lease, then deletes it synchronously unless `--async` was set to trigger GC.

State and persistence: mutates content labels and lease state. Dry run logs intended changes only.

Dependencies/integration: content store walk/update, leases service, containerd log, shared client helper.

Risks: label matching is string-prefix based and intentionally preserves config label index `0`; future label naming changes could be missed. Creating/deleting a lease is used to drive GC side effects.

Test signals: no local tests here for label classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/content/prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/deprecations/deprecations.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/deprecations/deprecations.go

Purpose: implements `ctr deprecations list`, printing deprecation warnings recorded by the server.

Important APIs/types/functions: `Command`, `listCommand`, `deprecationWarning`, `warnings()`, and `deprecationWarningFromPB()`.

Control flow: command sets `CONTAINERD_SUPPRESS_DEPRECATION_WARNINGS=1` to prevent `NewClient()` from printing warnings automatically, fetches introspection server info, converts protobuf warnings, and prints JSON or a tabular default format.

State and persistence: reads server introspection state; mutates process environment for the command process.

Dependencies/integration: containerd introspection API, shared client/JSON helper, protobuf timestamp conversion, tabwriter.

Risks: setting the environment is process-global and can affect later operations in the same process. Unknown format values fall back to default table behavior.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/deprecations/deprecations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/events/events.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/events/events.go

Purpose: implements `ctr events`, streaming containerd events and printing them with JSON-decoded payloads.

Important APIs/functions: `Command` action; blank import registers gRPC event types for typeurl decoding.

Control flow: creates client/context, subscribes to event service with CLI filter args, then loops selecting from event and error channels. Each event payload is unmarshaled from Any via typeurl, JSON marshaled, and printed with timestamp, namespace, topic, and payload.

State and persistence: read-only event subscription; no local persistence.

Dependencies/integration: containerd event service, typeurl registry, event type blank import, JSON encoding, log.

Risks: if event channel closes and returns nil repeatedly, loop behavior depends on service channel semantics; error channel returns end the command. Events with unknown Any types are skipped with warnings.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/events/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/convert.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/convert.go

Purpose: implements `ctr images convert`, creating a new image reference with transformed layer/media formats.

Important APIs/functions: `convertCommand`; converter options for platform selection, uncompressing layers, Docker-to-OCI media conversion, and EROFS layer conversion.

Control flow: validates source and target refs, selects default strict platform unless `--all-platforms` or explicit platforms are supplied, appends layer conversion functions for `--uncompress` and/or `--erofs`, validates EROFS mode `raw|zstd`, parses EROFS compressors and mkfs options, optionally enables Docker-to-OCI conversion, creates client/context, runs `converter.Convert()`, and prints the new target digest.

State and persistence: writes converted content and image metadata under the target reference.

Dependencies/integration: containerd image converter packages, EROFS converter, uncompress converter, platform parsing, shared client helper.

Risks: conversion options can be combined and order matters in the option list. `strings.Fields` for mkfs options does not support shell-like quoting. All-platforms conversion requires all referenced content to already exist.

Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/export.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/export.go

Purpose: implements `ctr images export`, exporting image references as an OCI archive stream/file.

Important APIs/functions: `exportCommand`; local archive options and transfer archive options.

Control flow: validates output path and at least one image, opens stdout or creates output file, then chooses transfer-service mode by default or direct local mode with `--local`. Transfer mode builds `tarchive` platform/compatibility/non-distributable options, adds extra image references to an image store source, and calls `client.Transfer()` to an export stream with progress. Local mode builds `archive.ExportOpt` values and calls `client.Export()`.

State and persistence: writes an archive to stdout or a file; reads image/content metadata.

Dependencies/integration: transfer API, archive exporter, image store transfer source, platform parser, progress handler.

Risks: output file is created before export and may remain partial on failure. Transfer and local modes have separate option implementations with possible semantic drift. Platform flags require content availability.

Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/images.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/images.go

Purpose: implements `ctr images` parent command and list/label/check/delete/prune subcommands.

Important APIs/functions: `Command`, `listCommand`, `setLabelsCommand`, `checkCommand`, `removeCommand`, and `pruneCommand`.

Control flow: list prints image refs or detailed table with target type/digest/size/platforms/labels. Label updates image labels with optional replace-all. Check verifies required content and unpack status for default platform/snapshotter and prints table or ready refs. Delete removes named image refs and can request synchronous GC on the last target. Prune requires `--all`, identifies images unused by current containers, and deletes the last one synchronously.

State and persistence: reads/writes image metadata, labels, container references, content availability, and snapshot unpack state; delete/prune can trigger garbage collection.

Dependencies/integration: image service, container service, content store, core images helpers, platform helpers, progress byte formatting, errdefs, tabwriter.

Risks: prune only compares image names used by containers and does not support filters beyond all. Delete reports first non-not-found error while continuing. Label replace-all appends `"labels"` once per supplied label key, which is redundant but functional.

Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/images.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/import.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/import.go

Purpose: implements `ctr images import`, importing OCI/Docker archive streams into containerd with optional unpacking and reference translation.

Important APIs/functions: `importCommand`; transfer import options; local `containerd.ImportOpt` construction.

Control flow: command creates client/context and chooses transfer-service mode by default or local direct mode with `--local`. Transfer mode rejects `--discard-unpacked-layers`, computes base prefix and digest/named reference options, chooses unpack platform, opens stdin/file, creates an import stream, and calls `client.Transfer()` with progress. Local mode builds archive ref translators, digest/index/compression/platform/all-platform/discard-label options, creates a lease, opens input, calls `client.Import()`, closes input, and unpacks each imported image unless `--no-unpack`.

State and persistence: writes content blobs, image metadata, optional unpacked snapshots, and temporary lease state; reads archive from stdin or file.

Dependencies/integration: containerd import APIs, transfer archive/image APIs, diff apply sync-fs, platform matching, leases, logging.

Risks: transfer and local paths differ: transfer only unpacks one platform even with all-platforms. `--discard-unpacked-layers` requires local and conflicts with `--no-unpack`. Auto-generated import prefixes use the current date and may overwrite named annotations in transfer mode.

Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/inspect.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/inspect.go

Purpose: implements `ctr images inspect`, printing an image tree and optional content JSON.

Important APIs/functions: `inspectCommand`.

Control flow: creates client/context, reads the image ref, fetches image metadata from image service, builds display printer options with stdout and optional verbose content, and prints the image tree using the content store.

State and persistence: read-only image/content access.

Dependencies/integration: `pkg/display` image tree printer, image service, content store.

Risks: no explicit empty-ref validation before image lookup, so errors depend on image service behavior.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/mount.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/mount.go

Purpose: implements `ctr images mount`, unpacking an image and mounting or activating a snapshot view/prepare for inspection.

Important APIs/functions: `mountCommand`.

Control flow: validates image ref, derives snapshot/lease key from target or random suffix, creates client/context, chooses default snapshotter if unset, creates a lease with expiration, parses platform, loads image metadata, unpacks image for the platform, computes chain ID from rootfs diff IDs, creates a read-only view or writable prepare snapshot, optionally reuses existing mounts, activates through mount manager when supported, mounts to target or uses a bind source when target omitted, prints chain ID and target.

State and persistence: creates lease, snapshot view/prepare, may mount filesystem at target, and may activate mount manager state. On returned error, deferred cleanup releases lease if created.

Dependencies/integration: image service, snapshot service, mount manager, diff sync-fs, leases, defaults, platforms, identity chain ID.

Risks: target omitted only works when a single bind mount is returned. If mount fails, snapshot cleanup is attempted but can fail and only prints to err writer. Random key uses three random bytes plus nanosecond, sufficient for CLI but not globally collision-proof.

Test signals: no local tests; mount behavior is integration/system dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/pull.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/pull.go

Purpose: implements `ctr images pull`, fetching, registering, and unpacking images from remote registries.

Important APIs/types/functions: `pullCommand`, transfer-mode setup, local fetch/unpack path, `progressNode`, `ProgressHandler()`, `DisplayHierarchy()`, `displayNode()`, `prefixes()`, `displayName()`, `shortenName()`, and `Display()`.

Control flow: validates ref, creates client/context, then defaults to transfer-service mode unless `--local`. Transfer mode rejects local-only flags, creates static credentials and registry source, resolves platforms with default Linux substitution on Darwin, configures unpack/store metadata/labels, and runs `client.Transfer()` with hierarchical progress. Local mode creates a lease, uses content fetch config, fetches content, resolves platforms, unpacks each selected platform, optionally prints chain ID, and prints elapsed time.

State and persistence: writes content, image metadata, snapshots, and leases. Progress state is in-memory.

Dependencies/integration: transfer registry/image APIs, content fetch helpers, containerd image APIs, diff sync-fs, platform helpers, progress writer, identity chain IDs.

Risks: transfer mode and local mode support different flags, enforced by runtime validation. All-platform unpack support in transfer mode is noted as TODO. Progress tree parent attachment can display roots before parents arrive, though update logic later re-parents known nodes.

Test signals: no local tests for pull paths or progress rendering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/push.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/push.go

Purpose: implements `ctr images push`, uploading local image content to a remote registry.

Important APIs/types/functions: `pushCommand`, `pushjobs`, `newPushJobs()`, `pushjobs.add()`, and `pushjobs.status()`.

Control flow: validates remote ref, creates client/context, then defaults to transfer-service mode unless `--local`. Transfer mode rejects local-only flags, creates credentials/registry destination, resolves local ref defaulting to remote ref, configures optional platform filters, and calls `client.Transfer()` with progress. Local mode resolves manifest descriptor either from `--manifest` or local image metadata, optionally narrows to one platform manifest, enables HTTP trace, builds resolver, starts an errgroup for `client.Push()` plus progress rendering, skips non-distributable blobs unless allowed, applies max concurrent upload option, and waits.

State and persistence: reads local content/image metadata and writes remote registry blobs/manifests. Progress status uses Docker status tracker state.

Dependencies/integration: transfer registry/image APIs, remotes/docker status tracker, content progress display, errgroup, platform/image child traversal, resolver helpers.

Risks: default transfer path rejects many registry flags that local path supports. In local platform narrowing, if no matching manifest is found the descriptor may remain the index. Non-distributable blobs are skipped by both handler and wrapper when not allowed.

Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/tag.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/tag.go

Purpose: implements `ctr images tag`, creating one or more new image references for an existing image.

Important APIs/functions: `tagCommand`.

Control flow: validates source and at least one target, creates client/context, then defaults to transfer-service mode unless `--local`. Transfer mode validates target references unless skipped and transfers from source store to each target store. Local mode creates a lease, fetches source image metadata, validates each target, attempts create, and if `--force` with already-exists, deletes and recreates.

State and persistence: creates image metadata references; local mode may delete existing target refs under force.

Dependencies/integration: transfer image store, image service, leases, Docker/distribution reference parser, errdefs.

Risks: force delete/create is not atomic. Transfer mode ignores `--force`; existing target behavior depends on transfer service.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/tag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/unmount.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/unmount.go

Purpose: implements `ctr images unmount`, unmounting an image rootfs target and optionally removing related snapshot/lease state.

Important APIs/functions: `unmountCommand`.

Control flow: validates target, creates client/context, calls `mount.UnmountAll(target, 0)`, and if `--rm` is set, deletes a lease with ID equal to target and removes a snapshot with key equal to target from the chosen snapshotter. Prints target on success.

State and persistence: unmounts host filesystem mounts; optional deletion mutates lease and snapshot state.

Dependencies/integration: mount package, leases service, snapshot service, errdefs.

Risks: cleanup assumes target path equals lease ID and snapshot key, which matches explicit-target mount mode but not random-key/bind-source cases. Snapshotter default handling is delegated to snapshot service behavior; unlike mount.go it does not set defaults explicitly.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/unmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/usage.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/images/usage.go

Purpose: implements `ctr images usage`, printing snapshot size/inode usage for an unpacked image chain.

Important APIs/functions: `usageCommand`.

Control flow: validates ref, creates client/context, chooses default snapshotter if unset, gets image metadata, verifies the image is unpacked for that snapshotter, computes chain ID from rootfs diff IDs, then walks parent snapshots by repeatedly calling `Usage()` and `Stat()` until no parent remains, printing a table.

State and persistence: read-only snapshot/image metadata access.

Dependencies/integration: containerd image wrapper, snapshot service, defaults, identity chain ID, progress byte formatter, tabwriter.

Risks: only works after unpack. Parent walking assumes chain IDs map directly to snapshot keys. Error text says "mount" when validating image ref, likely copy/paste.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/images/usage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/info/info.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/info/info.go

Purpose: implements `ctr info`, printing server introspection info as JSON.

Important APIs/types/functions: `Info` wrapper struct and `Command`.

Control flow: creates client/context, calls `client.IntrospectionService().Server(ctx)`, stores response in `Info.Server`, and prints JSON.

State and persistence: read-only server introspection.

Dependencies/integration: introspection API and shared JSON/client helpers.

Risks: output is directly tied to server protobuf shape.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/info/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/install/install.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/install/install.go

Purpose: implements `ctr install`, installing binaries/libs from an image into an opt-style managed path.

Important APIs/functions: `Command` with `--libs`, `--replace`, and `--path`.

Control flow: creates client/context, reads image ref, loads the image, builds install options from flags, and calls `client.Install(ctx, image, opts...)`.

State and persistence: writes files through containerd install implementation, potentially replacing existing binaries/libs and using an alternate path.

Dependencies/integration: containerd client install APIs and shared client helper.

Risks: no command-local validation that ref is non-empty; errors come from image lookup. Replacement/path semantics are delegated to client install implementation.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/install/install.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/leases/leases.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/leases/leases.go

Purpose: implements `ctr leases` list/create/delete commands for containerd leases.

Important APIs/functions: `Command`, `listCommand`, `createCommand`, and `deleteCommand`.

Control flow: list applies filters and prints quiet IDs or table with created time and sorted labels. Create parses label args, optional ID, optional expiration defaulting to 24h, creates a lease, and prints the ID. Delete validates at least one ID, deletes each lease, and applies synchronous delete only to the last ID when `--sync` is set.

State and persistence: reads, creates, and deletes lease metadata; synchronous delete can trigger cleanup of unreferenced resources.

Dependencies/integration: leases service, shared client helper, tabwriter.

Risks: create label parsing ignores whether `=` was present and stores empty values for bare keys. Quiet flag usage text says blob digest, likely copied from content commands.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/leases/leases.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces.go

Purpose: implements `ctr namespaces` create/list/remove/label commands.

Important APIs/functions: `Command`, `createCommand`, `setLabelsCommand`, `listCommand`, and `removeCommand`.

Control flow: create validates namespace and creates it with parsed labels. Label sets or clears each label through namespace service. List prints names or names with sorted labels. Remove builds platform-specific delete options, deletes each target namespace, ignores not-found, logs other failures while returning the first error, and prints each target.

State and persistence: mutates namespace metadata and labels; Linux remove can also request namespace cgroup deletion.

Dependencies/integration: namespace service, shared label/client helpers, platform-specific `deleteOpts()`, errdefs, logging.

Risks: label updates are one RPC per label and not atomic. Remove prints targets even when not found. Namespace must be empty per description, enforced by service.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces_linux.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces_linux.go

Purpose: provides Linux namespace delete options.

Important APIs/functions: `deleteOpts()` returns `opts.WithNamespaceCgroupDeletion` when `--cgroup` is set.

Control flow: called by namespace remove command to translate CLI flag into service option.

State and persistence: can cause namespace cgroup deletion through runtime opts.

Dependencies/integration: runtime opts package and namespace delete option type.

Risks: only meaningful when the namespace cgroup exists and deletion is supported by the service/runtime.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces_other.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces_other.go

Purpose: provides non-Linux namespace delete option behavior.

Important APIs/functions: `deleteOpts()` returns nil.

Control flow: namespace remove command can call it unconditionally across platforms.

State and persistence: none beyond normal namespace deletion in caller.

Dependencies/integration: selected by `!linux`.

Risks: `--cgroup` has no platform-specific effect outside Linux.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/namespaces/namespaces_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/oci/oci.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/oci/oci.go

Purpose: implements `ctr oci spec`, printing the default generated OCI runtime spec for a platform.

Important APIs/functions: `Command` parent and `defaultSpecCommand`.

Control flow: creates app context, chooses the requested platform or the default platform string, calls `oci.GenerateSpecWithPlatform(ctx, nil, platform, &containers.Container{})`, and prints the spec as JSON.

State and persistence: read-only/generated output; no daemon client is required.

Dependencies/integration: containerd OCI spec generator, core container type, platform defaults, shared JSON/context helpers.

Risks: output depends on platform-specific defaults and current OCI generator behavior. Empty container input means this is a baseline spec, not image/container-specific.

Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/oci/oci.go -->
