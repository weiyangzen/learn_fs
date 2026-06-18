<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-controller.yaml

## Purpose
Deploys the CSI NFS controller pod for v4.8.0. It runs the external provisioner, CSI snapshotter, liveness probe, and NFS CSI controller service in one `kube-system` deployment.

## Important APIs, Types, and Functions
The `apps/v1` `Deployment` `csi-nfs-controller` has one replica, service account `csi-nfs-controller-sa`, host networking, control-plane tolerations, and `system-cluster-critical` priority. Containers are `csi-provisioner:v5.0.2`, `csi-snapshotter:v8.0.1`, `livenessprobe:v2.13.1`, and `nfsplugin:v4.8.0`. The controller socket is `/csi/csi.sock`; liveness is on localhost port `29652`.

## Control Flow, State, and Persistence
The sidecars connect to the shared CSI socket and issue `CreateVolume`, `DeleteVolume`, `CreateSnapshot`, and related controller RPCs. The NFS container is privileged and mounts NFS shares internally to create/delete directories and snapshot archives. The pod uses `emptyDir` for the CSI socket and hostPath `/var/lib/kubelet/pods` with bidirectional propagation for mount visibility.

## Dependencies and Integration Points
It depends on RBAC from `rbac-csi-nfs.yaml`, snapshot CRDs/RBAC for snapshot flows, Linux NFS mount tools, kube-system leader election leases, and matching sidecar capabilities. Host networking is used because the controller also mounts NFS to create directories.

## Risks and Test Signals
Risks include privileged controller execution, long sidecar timeouts masking slow NFS behavior, leader election/RBAC mismatch, hostNetwork policy restrictions, and socket/container ordering issues. Signals are healthy liveness on `29652`, provisioner and snapshotter leaders elected, successful PVC provisioning, and snapshot archives created under the configured share.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-controller.yaml -->
