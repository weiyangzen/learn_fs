<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon_unix.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/daemon_unix.go

Purpose: non-Windows socket scheme/path helper for test dockerd daemon.

Important APIs and types: `socketScheme` and `getDockerdSockPath`.

Control flow: returns `unix://` scheme and creates a socket path under the supplied root using `<id>.sock`.

State and persistence: pure path construction.

Dependencies and integration: used by `Daemon.Sock` and daemon startup args.

Risks: generated path must fit unix socket length limits; parent code uses short IDs and temp root to help.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/daemon_unix.go -->
