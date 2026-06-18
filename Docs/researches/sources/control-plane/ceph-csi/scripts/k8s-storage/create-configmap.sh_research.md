<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-configmap.sh -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/create-configmap.sh

Purpose: creates or replaces a `ceph-csi-config` ConfigMap for Kubernetes external storage e2e jobs using Rook cluster information.

Control flow: requires namespace argument, fetches Rook toolbox pod, reads Ceph fsid and monitor service IP/port, chooses `kubectl replace` if ConfigMap exists otherwise `create`, and writes JSON config with clusterID and monitors.

State and persistence: creates/replaces Kubernetes ConfigMap in the supplied namespace.

Dependencies: kubectl, Rook namespace/pods/services, Ceph toolbox.

Integration points: StorageClasses and driver manifests use this config map for e2e provisioning.

Risks: assumes first toolbox pod and first monitor service/port are valid. Does not use `kubectl_retry`. Only writes a single monitor endpoint.

Test signals: no unit tests; e2e setup validates indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-configmap.sh -->
