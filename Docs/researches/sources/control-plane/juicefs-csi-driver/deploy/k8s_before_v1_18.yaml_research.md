<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/k8s_before_v1_18.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/k8s_before_v1_18.yaml

## Purpose
Generated all-in-one Kubernetes manifest for installing the JuiceFS CSI driver on Kubernetes versions before 1.18. It is marked as kustomize output and uses `storage.k8s.io/v1beta1` `CSIDriver`, which is the compatibility difference from newer manifests.

## Important APIs, Types, and Resources
Defines ServiceAccounts for controller, node, and dashboard; ClusterRoles and bindings for provisioning, snapshotting, node services, and dashboard; `juicefs-csi-driver-config` ConfigMap; dashboard Service/Deployment; controller StatefulSet; node DaemonSet; and `CSIDriver csi.juicefs.com`. Images include `juicedata/juicefs-csi-driver:v0.31.3`, `juicedata/csi-dashboard:v0.31.3`, and sig-storage sidecars.

## Control Flow
Applying the manifest creates RBAC first, then config/service/workload resources. The controller StatefulSet exposes a CSI socket for provisioner/resizer/liveness sidecars and runs with leader election. The node DaemonSet registers the CSI driver with kubelet, mounts host paths, and serves node publish/unpublish calls. Dashboard deployment queries cluster state using its RBAC.

## State and Persistence
All durable state is Kubernetes API state plus hostPath directories under `/var/lib/juicefs`, kubelet plugin sockets, webhook/dashboard Services, and leader-election leases/configmaps. The ConfigMap embeds driver settings and mountPodPatch defaults.

## Dependencies and Integration Points
Depends on Kubernetes RBAC, apps/v1 workloads, sig-storage CSI sidecars, kubelet plugin paths, snapshot CRDs for snapshotter permissions, and JuiceFS CSI driver flag/config behavior. It is integrated with generated install scripts and should correspond to kustomize output from the deployment tree.

## Risks
Risks include broad RBAC (`nodes/proxy`, pod create/delete, secrets mutate, pod exec), privileged node/controller containers with bidirectional mount propagation, hostPath assumptions, outdated v1beta1 CSIDriver compatibility, and generated-file drift from source kustomize overlays.

## Test Signals
Signals are `kustomize build` parity checks, `kubectl apply --dry-run=server`, successful CSI registration on pre-1.18 clusters, dynamic/static volume tests, snapshot tests when CRDs exist, and dashboard health/metrics checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/k8s_before_v1_18.yaml -->
