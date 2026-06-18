<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/install-snapshot.sh -->
## sources/control-plane/ceph-csi/scripts/install-snapshot.sh

Purpose: installs or removes Kubernetes CSI snapshot controller and snapshot/group-snapshot CRDs for tests.

Control flow: builds URLs for external-snapshotter release, downloads RBAC/controller YAML to temp files, rewrites namespace and image tag, injects `--feature-gates=CSIVolumeGroupSnapshot=true` on create, applies or deletes group snapshot CRDs, controller resources, and standard snapshot CRDs. Install waits for snapshot-controller pod readiness.

State and persistence: Kubernetes CRDs/RBAC/deployment in target namespace; temp files.

Dependencies: curl, sed, kubectl_retry, external-snapshotter GitHub raw manifests.

Integration points: required before snapshot e2e tests and volume group snapshot tests.

Risks: a sed expression for replacing a false feature gate contains `----feature-gates`, which may fail to update an existing false argument. Remote manifests and default `v5.0.1` must remain compatible with cluster version. Deletes CRDs cluster-wide.

Test signals: readiness loop validates pod availability; no unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/install-snapshot.sh -->
