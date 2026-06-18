# sources/control-plane/rook/pkg/daemon/ceph/client/image_test.go

Purpose: validates RBD image list parsing under normal and debug-log-prefixed output, plus watcher list extraction.

Important test cases: `TestListImageLogLevelInfo` mocks `rbd ls -l` returning a normal JSON array or empty array and asserts parsed image counts. `TestListImageLogLevelDebug` prefixes the same payloads with multiline librados debug logs and verifies the regex still extracts JSON arrays. `TestGetWatchers` constructs `RBDStatus` with two watcher addresses and verifies `GetWatchers()` returns both.

Control flow and dependencies: tests use `exectest.MockExecutor` and `AdminTestClusterInfo()`. They assert the command is `rbd` and starts with `ls -l`, leaving standard args uninspected.

Risks and coverage gaps: tests do not cover namespace args, invalid JSON after regex extraction, no JSON array found, snapshot operations, image deletion/trash movement, trash removal via Ceph task, or `GetRBDImageStatus()` command parsing. The debug fixture protects a known real-world issue where librados logs contaminate stdout.
