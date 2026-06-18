# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v4.10.0 controller Deployment including provisioner, resizer, optional CSI snapshotter, liveness probe, and NFS driver.

Important APIs/types/functions: `Deployment`; sidecars `csi-provisioner`, `csi-resizer`, `csi-snapshotter`, `liveness-probe`, `nfs`; values for image `baseRepo`, strategy, snapshotter, tar snapshots, default on-delete policy, scheduling, resources, and security contexts.

Control flow: Host-networked controller uses scheduling branch logic, then starts sidecars against `/csi/csi.sock`. Snapshotter container renders only when `controller.enableSnapshotter` is true. NFS driver receives mount permissions, working dir, delete policy, and tar snapshot flags.

State and persistence: PV/PVC resize/provision/snapshot state, leases, events, CSI socket, and host pod mounts.

Dependencies and integration points: Requires RBAC including resizer and snapshot permissions, snapshot CRDs for snapshot workflows, and kubelet host paths.

Risks: Privileged host mounts, leader election, image repository composition, and snapshot flags require integration testing. Test signals: PVC create/delete/resize and VolumeSnapshot workflows.
