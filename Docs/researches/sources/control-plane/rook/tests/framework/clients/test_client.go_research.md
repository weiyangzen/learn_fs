# sources/control-plane/rook/tests/framework/clients/test_client.go

Purpose: `TestClient` aggregates all individual Rook test operation wrappers into one fixture object and exposes cluster status.

Important APIs/types/functions: `TestClient` fields include block, filesystem, NFS, object, object user, pool, bucket, Ceph client, RBD mirror, topic, notification, and COSI clients plus the underlying `K8sHelper`. `CreateTestClient` constructs each wrapper with the same helper/manifests. `Status` calls `client.Status` using admin test cluster info.

Control flow: construction is straight-line dependency injection. `Status` creates a Ceph context from the helper, builds namespace-scoped admin cluster info, and returns Ceph status or a wrapped error.

State and persistence behavior: the struct holds references only. It does not own external state; individual client wrappers mutate Kubernetes and Ceph.

Dependencies and integration points: central integration point between test suites, `installer.CephManifests`, `utils.K8sHelper`, and Rook Ceph client APIs.

Risks: all clients share one helper and manifest settings, so namespace/version mistakes propagate broadly. The struct exposes fields directly, which keeps tests convenient but permits nil or swapped clients if manually constructed.

Test signals: creation has no direct validation. `Status` success confirms toolbox/admin command path is usable for later health checks.
