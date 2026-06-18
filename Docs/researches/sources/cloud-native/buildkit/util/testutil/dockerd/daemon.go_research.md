<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/daemon.go

Purpose: starts and stops isolated dockerd instances for BuildKit integration tests.

Important APIs and types: `Daemon`, `Option`, `NewDaemon`, `WithBinary`, `WithExtraEnv`, `Sock`, `StartWithError`, `StopWithError`, and `lockingWriter`.

Control flow: `NewDaemon` creates unique working/root/exec/socket paths and applies options. `StartWithError` resolves the dockerd binary, builds data-root/exec-root/pid/containerd namespace/host args, adds debug defaults and storage driver/userns options, starts the process with test env vars, captures logs into synchronized buffers, and exposes a wait channel. `StopWithError` sends interrupt, waits up to 20 seconds, retries interrupts up to five times, then kills the process if needed.

State and persistence: creates temp directories, daemon root, pid file, exec root, socket path, process handle, log buffers, and wait channel. Removes pid file on clean stop but does not remove daemon root in this file.

Dependencies and integration: uses BuildKit identity for unique IDs, platform socket helpers, test log interfaces, and integration tests that need real Docker daemon behavior.

Risks: process lifecycle is timing-sensitive. `exec.CommandContext(context.TODO())` has no cancellation context. Stop logic can return `errDaemonNotStarted` for already finished processes. Socket path length constraints are handled by shortened exec-root and platform socket helpers.

Test signals: no direct tests in this subset; used by integration suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon.go -->
