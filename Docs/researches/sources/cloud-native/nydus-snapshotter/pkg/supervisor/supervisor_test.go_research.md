<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor_test.go

Purpose: validates supervisor Unix socket handoff behavior and timeout cleanup.

Important tests: `TestSupervisor` creates a supervisor set, sends a 2 MiB random state payload and a temp-file FD from a simulated nydusd connection, then invokes `SendStatesTimeout(0)` and verifies the takeover side receives identical data. `TestSupervisorTimeout` starts a timed sender, waits past the timeout, and asserts later connection to the socket fails.

Control flow and state: the test uses real Unix sockets under a temp directory and the package-level `send`/`recv` helpers, so it exercises control message parsing and multi-`ReadMsgUnix` loops. Cleanup removes temp dirs/files and destroys the supervisor.

Dependencies/integration: relies on `net.DialUnix`, `crypto/rand`, temp files, and testify assertions. It runs on platforms supporting Unix sockets and FD passing.

Risks and test signals: covers large payload and timeout paths, but does not assert FD identity/content, concurrent `FetchDaemonStates` semaphore behavior, or `DestroySupervisor` FD close side effects. It is still a high-value signal for live-upgrade state transfer regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor_test.go -->
