<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/containerd/containerd.go -->
# sources/cloud-native/buildkit/util/testutil/containerd/containerd.go

Purpose: test helper for retrieving the version of a running containerd daemon.

Important APIs and types: `GetVersion`.

Control flow: creates a containerd client with a 60-second timeout, calls `Version`, fails the test immediately on client or version errors, and returns the version string.

State and persistence: opens a client connection and closes it with defer; no persistence.

Dependencies and integration: uses containerd v2 client and `testing.T`. Intended for integration tests.

Risks: uses `t.Fatal`, so it is not usable outside tests. Uses `context.TODO` with the client timeout option.

Test signals: helper itself has no tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/containerd/containerd.go -->
