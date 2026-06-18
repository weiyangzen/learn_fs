<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/errors.go -->
# sources/cloud-native/buildkit/util/testutil/dockerd/client/errors.go

Purpose: formats user-facing Docker daemon connection failure errors for the test client.

Important APIs and types: `ErrorConnectionFailed`.

Control flow: returns a generic daemon-running message when host is empty, otherwise includes the target host.

State and persistence: pure error construction.

Dependencies and integration: used by request connection error handling.

Risks: message is modeled for Docker-style diagnostics; it wraps no underlying cause.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/dockerd/client/errors.go -->
