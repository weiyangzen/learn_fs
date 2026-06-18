<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/nydusd.go -->
## sources/cloud-native/nydus-snapshotter/tests/nydusd.go

Purpose: test harness for launching a real `nydusd`, waiting until it reports `RUNNING`, and unmounting it after converter tests.

Important APIs/types: `NydusdConfig`, `Nydusd`, internal `daemonInfo`, JSON `configTpl`, `makeConfig`, `checkReady`, `NewNydusd`, `Mount`, and `Umount`.

Control flow and state: `NewNydusd` renders `configTpl` to the configured path. `Mount` first attempts an unmount, builds nydusd command-line args for config/mountpoint/bootstrap/apisock/log-level, runs the process asynchronously, then polls `/api/v1/daemon` over the Unix API socket until state `RUNNING`, process exit, or 10-second timeout. `Umount` runs the host `umount` command if the mount path exists.

Dependencies/integration: used by `converter_test.go` to verify generated bootstraps by mounting them. Depends on a real nydusd binary, Unix sockets, host mount permissions, and the daemon HTTP API.

Risks and test signals: `checkReady` creates an unbuffered channel and may block sending if `Mount` has already returned through another path. `defer resp.Body.Close()` inside a polling loop can delay body closure until goroutine exit. `Umount` does not stop the nydusd process directly; it relies on daemon behavior after unmount.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/nydusd.go -->
