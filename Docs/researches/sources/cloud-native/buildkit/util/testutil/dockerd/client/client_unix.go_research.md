<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client_unix.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/client_unix.go

Purpose: non-Windows default Docker host constant for the test client.

Important APIs and types: `DefaultDockerHost`.

Control flow: no runtime logic; sets default host to `unix:///var/run/docker.sock`.

State and persistence: constant only.

Dependencies and integration: consumed by `NewClientWithOpts`.

Risks: platform build tag controls inclusion; tests using defaults depend on a local Docker socket existing.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/client_unix.go -->
