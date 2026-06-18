<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/frombinary.go -->
# sources/cloud-native/buildkit/util/testutil/integration/frombinary.go

Purpose: imports an OCI/Docker image archive from a binary file into a temporary local content store for integration tests.

Important APIs and types: `providerFromBinary`.

Control flow: creates a temp content-store directory, opens the archive file, imports the index with `archive.ImportIndex`, reads and unmarshals the resulting index descriptor, and returns the first manifest descriptor, the content provider/store, and a cleanup function. On any error, the temp directory is removed.

State and persistence: creates a temporary BuildKit state directory and local containerd content store; caller-owned cleanup removes it after success.

Dependencies and integration: uses containerd local content store and image archive importer, OCI specs, JSON, and filesystem temp APIs.

Risks: assumes imported index contains at least one manifest. Cleanup is returned as a bare function and must be called by tests to avoid temp directory leaks.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/testutil/integration/frombinary.go -->
