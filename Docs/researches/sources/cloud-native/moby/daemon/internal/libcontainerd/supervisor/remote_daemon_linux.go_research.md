<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_linux.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_linux.go

Purpose: provides Linux-specific containerd supervisor constants, socket path derivation, stop/kill behavior, and cleanup.

Important APIs and types: constants `binaryName`, `sockFile`, `debugSockFile`; functions `defaultGRPCAddress`, `defaultDebugAddress`, `stopDaemon`, `killDaemon`, and `platformCleanup`.

Control flow: addresses are Unix socket paths under state dir. `stopDaemon` sends SIGTERM, waits up to `shutdownTimeout`, and SIGKILLs if still alive. `killDaemon` sends SIGUSR1 for a stack trace, waits briefly, then kills. `platformCleanup` removes the gRPC socket path.

State and persistence: mutates process state and removes socket files.

Dependencies and integration: used by `remote_daemon.go`; depends on `syscall` and Docker `process.Alive/Kill`.

Risks: signal delivery can affect an unrelated process if pid reuse occurs after stale pid-file reuse. Socket cleanup ignores errors.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_linux.go -->
