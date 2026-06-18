<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon_windows.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/daemon_windows.go

Purpose: Windows named-pipe scheme/path helper for test dockerd daemon.

Important APIs and types: `socketScheme` and `getDockerdSockPath`.

Control flow: returns `npipe://` scheme and a pipe path `//./pipe/dockerd-<id>`.

State and persistence: pure string construction.

Dependencies and integration: used by `Daemon.Sock` on Windows.

Risks: pipe name uniqueness depends on generated daemon ID.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon_windows.go -->
