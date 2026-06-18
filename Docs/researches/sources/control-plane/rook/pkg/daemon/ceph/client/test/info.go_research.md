# sources/control-plane/rook/pkg/daemon/ceph/client/test/info.go

This helper file supports Ceph client tests by creating minimal local Ceph config material and synthetic `ClusterInfo` instances without importing higher-level test packages.

`CreateConfigDir()` creates a config directory, writes `client.admin.keyring` and `mon.keyring` with test keys, and wraps filesystem errors. `CreateTestClusterInfo()` constructs a `client.ClusterInfo` with FSID, namespace, monitor secret, admin credentials, internal/external monitor maps, owner info, and context. It populates up to five monitor IDs from a fixed list and assigns endpoints `1.2.3.N:3300`, then calls `SetName()` with the namespace.

State is test-local filesystem content and in-memory cluster metadata. Dependencies include `os`, `path`, `context`, Rook Ceph client types, and owner-reference helpers. Integration points are tests that need realistic config paths, keyrings, monitor maps, or owner information while avoiding cyclic dependencies.

Risks are mostly test-scaffold limitations: only five monitors are supported, credentials are hard-coded fixtures, and the generated endpoints are not meant to represent all messenger variants. There are no direct tests for this file in the work item, but it is a foundational fixture for other client tests.
