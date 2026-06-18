<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_windows.go

Purpose: provides Windows-specific containerd supervisor addresses and process stop behavior.

Important APIs and types: constants `binaryName`, `grpcPipeName`, `debugPipeName`; functions `defaultGRPCAddress`, `defaultDebugAddress`, `stopDaemon`, `killDaemon`, and `platformCleanup`.

Control flow: gRPC/debug addresses are fixed named pipes. `stopDaemon` finds the process, kills it, and waits. `killDaemon` delegates to Docker process kill. Cleanup is a no-op because named pipes do not need socket-file removal.

State and persistence: mutates the child process state; does not remove filesystem resources.

Dependencies and integration: used by `remote_daemon.go` on Windows.

Risks: stop is forceful rather than graceful. Fixed pipe names can conflict if multiple daemon instances run on the same host.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_windows.go -->
