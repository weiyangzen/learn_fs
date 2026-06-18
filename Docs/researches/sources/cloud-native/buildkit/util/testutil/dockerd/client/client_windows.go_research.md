<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client_windows.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/client_windows.go

Purpose: Windows default Docker host constant for the test client.

Important APIs and types: `DefaultDockerHost`.

Control flow: no runtime logic; sets default host to `npipe:////./pipe/docker_engine`.

State and persistence: constant only.

Dependencies and integration: consumed by `NewClientWithOpts`.

Risks: depends on Windows named pipe availability and permissions.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client_windows.go -->
