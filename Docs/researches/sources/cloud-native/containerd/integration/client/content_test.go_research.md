<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/content_test.go -->
# sources/cloud-native/containerd/integration/client/content_test.go

## Purpose
Adapts the upstream content store testsuite to a live containerd client content store. It verifies that the remote content service satisfies the common content.Store contract under separate namespaces and leases.

## APIs, Types, And Functions
`newContentStore` returns a testsuite-compatible context, `content.Store`, cleanup function, and error. `TestContentClient` invokes `testsuite.ContentSuite`. The helper uses `client.ContentStore`, `client.WithLease`, `testsuite.SetContextWrapper`, `namespaces.WithNamespace`, `ListStatuses`, `Abort`, `Walk`, and `Delete`.

## Control Flow And State
Each testsuite context wrapper increments an atomic namespace suffix and creates a lease. Cleanup iterates over every generated namespace, aborts active writes, walks stored content, and deletes each blob while tolerating not-found races.

## Persistence And Integration Points
The test persists content blobs, active ingest statuses, namespaces, and leases inside the running daemon. It integrates with `core/content/testsuite`, client lease handling, namespace propagation, and errdefs.

## Risks And Test Signals
Failures indicate mismatches between remote content service behavior and the common content contract, especially around concurrent namespaces, writer abort, lease lifecycle, delete idempotency, and content walking. The test is skipped in short mode because it exercises a live daemon and full content suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/content_test.go -->
