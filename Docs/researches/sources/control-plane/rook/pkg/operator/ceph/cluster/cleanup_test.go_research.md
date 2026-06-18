# sources/control-plane/rook/pkg/operator/ceph/cluster/cleanup_test.go

Purpose: verifies the cleanup Job pod template and cleanup placement toleration aggregation for `cleanup.go`.

Important APIs and tests: `TestCleanupJobSpec` builds a minimal `CephCluster` with namespace, `DataDirHostPath`, and cleanup confirmation, then calls `cleanUpJobTemplateSpec` through a `ClusterController`. `TestCleanupPlacement` constructs a `ClusterSpec` with tolerations under multiple placement keys and a storage class device set, then checks the resulting `Placement`.

Control flow: the first test exercises the container/template path enough to confirm that `ROOK_DATA_DIR_HOST_PATH` and `ROOK_NAMESPACE_DIR` are placed in the first two env slots when a data dir is set. The second test incrementally adds tolerations for `all`, mon, mgr, mon arbiter, osd, and device-set placement and checks the count after each addition.

State and persistence behavior: test state is entirely fake clientsets and in-memory `CephCluster` objects. No Jobs are created; the test inspects generated `PodTemplateSpec` and `Placement` values only.

Dependencies and integration points: uses Rook fake clientsets, `clusterd.Context`, Rook Ceph API types, Kubernetes core toleration types, and `testify/assert`.

Risks: the env assertion is positional rather than name-based, so legitimate env reordering would break the test, while missing later env vars would not be detected. Placement tests validate counts more than exact ordering/content after the first case. There is no test that `startCleanUpJobs` creates correctly labeled Jobs or node selectors.

Test signals: provides focused regression coverage for cleanup pod env basics and toleration aggregation, leaving operational cleanup flow mostly untested.
