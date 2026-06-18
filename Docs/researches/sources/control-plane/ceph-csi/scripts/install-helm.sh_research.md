<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/install-helm.sh -->
## sources/control-plane/ceph-csi/scripts/install-helm.sh

Purpose: installs Helm if needed and deploys or removes Ceph-CSI Helm charts for CephFS and RBD in a test cluster.

Control flow: detects arch, downloads Helm when absent, labels nodes for topology/read affinity, optionally fetches Rook fsid/admin key to generate StorageClasses and secrets, installs CephFS chart, checks Deployment/DaemonSet readiness, deletes shared config maps to avoid RBD install conflicts, installs RBD chart with topology and snapshot settings, and supports cleanup removing labels, uninstalling charts, and deleting namespace.

State and persistence: creates Kubernetes namespace/resources, labels nodes, optionally creates secrets/storageclasses, downloads Helm into `/tmp/cephcsi-helm-test`.

Dependencies: Helm, kubectl, Rook toolbox pod, build.env, `kubectl_retry`, chart directories.

Integration points: local/e2e chart validation for both CephFS and RBD.

Risks: command-line parsing allows legacy two-arg mode and option mode, making edge cases possible. Readiness checks compare replica fields that may be empty early. Secrets passed via `--set` can appear in process lists/logs. Cleanup deletes namespace entirely.

Test signals: no unit tests; install success is checked by Kubernetes readiness loops.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/install-helm.sh -->
