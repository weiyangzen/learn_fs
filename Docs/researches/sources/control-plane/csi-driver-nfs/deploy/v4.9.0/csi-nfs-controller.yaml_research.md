<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-controller.yaml

## Purpose
Deploys the v4.9.0 CSI NFS controller workload. It is the same controller topology as v4.8.0 with the NFS plugin image tag advanced to `v4.9.0`.

## Important APIs, Types, and Functions
The `apps/v1` `Deployment` `csi-nfs-controller` runs `csi-provisioner:v5.0.2`, `csi-snapshotter:v8.0.1`, `livenessprobe:v2.13.1`, and `nfsplugin:v4.9.0`. It uses service account `csi-nfs-controller-sa`, host networking, `system-cluster-critical` priority, Linux node selector, and control-plane tolerations.

## Control Flow, State, and Persistence
Sidecars communicate with the NFS CSI service over `/csi/csi.sock` in an `emptyDir`. Provisioning and snapshot RPCs cause the privileged NFS container to mount NFS shares and mutate directory/archive state. Liveness is served on localhost `29652`; leader election is handled by sidecars in `kube-system`.

## Dependencies and Integration Points
It depends on RBAC for the controller service account, snapshot CRDs/RBAC, Linux NFS client capabilities, Kubernetes lease resources, and the node plugin for actual workload mounts. HostPath `/var/lib/kubelet/pods` is mounted with bidirectional propagation.

## Risks and Test Signals
Risks include privileged controller scope, NFS mount failures from controller nodes, sidecar image/version skew, and hostNetwork restrictions. Signals are successful rollout, healthy liveness endpoint, active provisioner/snapshotter leaders, working PVC create/delete, and snapshot archive creation/restoration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-controller.yaml -->
