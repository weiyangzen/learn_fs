# sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_external_test.go

Purpose: unit tests the small external-cluster spec validation/defaulting helper.

Important APIs and tests: `TestValidateExternalClusterSpec` constructs a `cluster` with a mutable `ClusterSpec` and calls `validateExternalClusterSpec` under several states.

Control flow: the test verifies that a blank external spec is accepted, setting a Ceph image without `DataDirHostPath` returns an error, adding `DataDirHostPath` clears the error, and enabling monitoring defaults `ExternalMgrPrometheusPort` to `9283`.

State and persistence behavior: all effects are in-memory mutation of `cluster.Spec`; the key persisted-like behavior is defaulting `Monitoring.ExternalMgrPrometheusPort` when it was zero.

Dependencies and integration points: uses Rook Ceph API types, a `mon.Cluster` placeholder, and `testify/assert`.

Risks: coverage is narrow and does not validate the main external reconcile path. It also does not test nonzero prometheus port preservation or interactions with missing/invalid external secrets.

Test signals: good for protecting `DataDirHostPath` requirement and default metrics port, weak for operational external cluster behavior.
