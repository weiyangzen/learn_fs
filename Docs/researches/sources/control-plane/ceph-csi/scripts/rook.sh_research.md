<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/rook.sh -->
## sources/control-plane/ceph-csi/scripts/rook.sh

Purpose: deploys, validates, and tears down a Rook Ceph cluster for Ceph-CSI testing.

Control flow: fetches Rook example manifests, disables Rook's own CSI drivers, optionally rewrites Ceph cluster image and health checks, deploys cluster/toolbox/filesystem/pool/subvolumegroup resources, then polls CephCluster health, manager pod, MDS pods, and RBD pool stats. Also creates/deletes additional replicated and erasure-coded block pools. An ERR trap dumps nodes, events, pods, operator logs, and Ceph CR YAML.

State and persistence: creates/deletes cluster-scoped and namespace Kubernetes resources and writes short-lived manifest files.

Dependencies: kubectl, curl, Rook raw GitHub manifests, Ceph toolbox, `kubectl_retry`.

Integration points: called by `minikube.sh` and e2e setup paths.

Risks: remote manifest version coupling, namespace/resource assumptions, and destructive teardown. Temporary `subvolumegroup.yaml` and pool files are created in current directory. Error trap exits process after log dump.

Test signals: health polling functions validate operational readiness, no unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/rook.sh -->
