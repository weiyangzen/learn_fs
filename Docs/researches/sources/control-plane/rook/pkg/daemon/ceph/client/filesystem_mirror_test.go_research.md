# sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_mirror_test.go

Purpose: validates CephFS mirror command construction and basic response parsing.

Important test cases: `TestEnableFilesystemSnapshotMirror`, `TestDisableFilesystemSnapshotMirror`, `TestImportFilesystemMirrorPeer`, `TestCreateFSMirrorBootstrapPeer`, `TestRemoveFilesystemMirrorPeer`, and `TestFSMirrorDaemonStatus` each use mock executors to assert the command prefix and important positional args. `fsMirrorToken` provides a bootstrap token JSON fixture and the create test confirms the returned token is base64-decodable. Daemon status parsing checks daemon ID and filesystem name.

Control flow and dependencies: uses `exectest.MockExecutor`, `AdminTestClusterInfo()`, and `encoding/base64`. The daemon status test asserts the status command does not append the filesystem name, documenting global daemon-status behavior.

Risks and coverage gaps: no tests cover error idempotency for `ENOTSUP`, schedule add/retention/status APIs, newline-stripped JSON in schedule status, invalid bootstrap JSON, token trimming, or combined-output import errors. The test for daemon status indexes `args[5]` in a `NotEqual` assertion, which depends on standard flags being appended by `NewCephCommand()`.
