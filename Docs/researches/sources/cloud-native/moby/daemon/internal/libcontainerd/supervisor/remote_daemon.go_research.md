<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon.go

Purpose: starts, configures, monitors, restarts, and stops a child `containerd` daemon for Docker.

Important APIs and types: `remote` embeds containerd `config.Config` and tracks config file, daemon binary path, pid, pid file, logger, and lifecycle channels. `Daemon`, `DaemonOpt`, `Start`, `WaitTimeout`, `Address`, `getContainerdConfig`, `startContainerd`, and `monitorDaemon` are central.

Control flow: `Start` builds a default config with root/state/grpc/debug paths, applies options, creates state dir, launches `monitorDaemon`, and waits up to `startupTimeout`. `startContainerd` reuses an existing pid from the pid file if present; otherwise writes config TOML, starts `containerd --config`, redirects logs to Docker stdout/stderr, strips `NOTIFY_SOCKET`, locks the OS thread around `cmd.Start`/`Wait` on Linux-sensitive paths, writes the pid file, and records the process pid. `monitorDaemon` loops until context cancellation, starts/restarts containerd, creates a monitoring client, checks `IsServing`, reports initial startup, waits for daemon exit, retries transient failures, kills unresponsive daemons, and performs cleanup on exit.

State and persistence: writes `containerd.toml` and `containerd.pid` under state dir, owns child process state, and removes pid/socket resources during cleanup. Lifecycle channels coordinate startup and shutdown with callers.

Dependencies and integration: depends on containerd config/defaults/client/dialer, gRPC interceptors, Docker pidfile/process helpers, platform-specific address/stop/cleanup utilities, and TOML encoding. It is the daemon's local supervisor for the remote containerd runtime.

Risks: pid-file reuse assumes the recorded process is still the intended containerd. Startup and health-check timeouts are fixed constants. Restart loops must avoid tight spinning; the file uses delays but process liveness races remain. On startup failure after initial success, errors are logged and restart continues rather than surfacing to the original caller.

Test signals: no direct tests in this subset; behavior is system/integration tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon.go -->
