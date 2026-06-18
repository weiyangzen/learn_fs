# sources/distributed-fs/beegfs-go/rst/remote/cmd/beegfs-remote/main.go

## Purpose
Main entrypoint for the BeeRemote service. It parses configuration, initializes logging and CTL globals, verifies the BeeGFS mount and license, starts worker/job/server components, and coordinates graceful shutdown.

## Important APIs, Types, And Functions
Defines build metadata variables (`binaryName`, `version`, `commit`, `buildTime`), constants including `FeatureLicenseStr`, capability map, and `main`. There are no exported library APIs.

## Control Flow
`main` registers CLI flags, handles version/help/dump-config/perf-profiling options, builds `configmgr.ConfigManager` with `config.AppConfig` and RST decode hook, initializes logger and CTL config, obtains BeeGFS mountpoint, sets signal cancellation, validates procfs mount config for `sysBypassFileAccessCheckOnMeta`, reads management TLS/auth material, creates a temporary management gRPC client for license verification, builds a `flex.BeeRemoteNode`, starts worker manager, job manager, and gRPC server, then waits for component error or OS signal before stopping components in reverse order.

## State And Persistence
Persistent interactions include logs, job DB path configured in lower layers, worker/remote activity, and server listening socket. This file reads cert/auth files and may start pprof HTTP server. It initializes global CTL logger and Viper state for reuse by lower packages.

## Dependencies And Integration Points
Integrates pflag, config manager, logger, CTL config, procfs parser, BeeGFS mount provider, mgmtd gRPC, license verification, worker manager, job manager, Remote server, OS signal handling, and pprof.

## Risks And Edge Cases
Startup uses fatal exits for configuration, mount, license, and component initialization failures. The pprof server ignores `ListenAndServe` errors. Procfs validation is warning-only except when a supported config key is present and set incorrectly. Management client is intentionally short-lived for license verification, so future management use must create its own client. Startup may block while resolving an inaccessible BeeGFS mount before mgmtd client setup.

## Test Signals
No direct tests. Integration or command tests would need dependency injection or process-level harnesses for config parsing, dump/version modes, procfs validation, license failure, component startup failure, and graceful shutdown.
