# sources/control-plane/juicefs-csi-driver/deploy/k8s.yaml

## Purpose
This generated manifest installs the JuiceFS CSI driver, dashboard, RBAC, default config, controller, node daemon, and CSIDriver object into `kube-system`.

## APIs, Control Flow, and State
It creates service accounts for controller, dashboard, and node components; ClusterRoles and bindings for dashboard reads/exec/jobs/config, node service operations, external provisioner, and snapshotter; a `juicefs-csi-driver-config` ConfigMap with `enableNodeSelector: false`; a dashboard Service and Deployment on port 8088; a controller StatefulSet with `juicefs-plugin`, `csi-provisioner`, `csi-resizer`, and liveness sidecar; a node DaemonSet with `juicefs-plugin`, registrar, and liveness sidecar; and a `storage.k8s.io/v1` CSIDriver named `csi.juicefs.com`.

## Dependencies and Integration Points
Images include `juicedata/csi-dashboard:v0.31.3`, `juicedata/juicefs-csi-driver:v0.31.3`, and Kubernetes CSI sidecars. HostPaths include kubelet plugin directories, `/var/lib/juicefs/volume`, `/var/lib/juicefs/config`, `/dev`, and `/var/run/juicefs-csi`. Dashboard RBAC backs the UI API actions researched in this subset.

## Risks and Test Signals
The manifest grants broad cluster permissions, privileged containers, SYS_ADMIN, hostPath mounts, and bidirectional mount propagation. It assumes kubelet paths and plugin registry layout. Test with `kubectl apply --dry-run=server`, RBAC `can-i`, controller leader election, PVC provision/resize, node registration, dashboard API access, and health probes.
