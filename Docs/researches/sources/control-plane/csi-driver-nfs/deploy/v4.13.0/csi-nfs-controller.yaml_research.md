<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-controller.yaml

## Purpose
Defines the v4.13.0 NFS CSI controller Deployment. Compared with v4.12.1, it updates CSI sidecars and the NFS plugin and explicitly disables the `VolumeAttributesClass` feature gate for provisioner and resizer sidecars.

## Important APIs, Types, And Objects
Runs one `csi-nfs-controller` pod in `kube-system` with `csi-provisioner:v6.1.0`, `csi-resizer:v2.0.0`, `csi-snapshotter:v8.4.0`, `livenessprobe:v2.17.0`, and `nfsplugin:v4.13.0`. The provisioner uses `--feature-gates=HonorPVReclaimPolicy=true,VolumeAttributesClass=false`; the resizer uses `-feature-gates=VolumeAttributesClass=false`. All sidecars connect to `/csi/csi.sock`.

## Control Flow
The controller plugin serves CSI on the shared socket. Provisioner, resizer, and snapshotter reconcile Kubernetes PVC/PV/VolumeSnapshot resources and call the plugin. The NFS plugin runs privileged with host kubelet pod access and health checks on `localhost:29652`. Leader election is namespace-scoped through Leases.

## State And Persistence Behavior
Local pod state is ephemeral. Persistent outcomes are Kubernetes PVs, PVC status, snapshot content/status, events, and Lease objects, plus NFS backing directories or snapshots created by the plugin.

## Dependencies And Integration Points
Requires the v4.13.0 RBAC, `CSIDriver`, snapshot CRDs, snapshot controller v8.4.0, and storage/snapshot classes using `nfs.csi.k8s.io`. Sidecar major upgrades imply compatibility expectations with the Kubernetes cluster version.

## Risks And Edge Cases
Privileged hostPath and hostNetwork exposure remain significant. `VolumeAttributesClass=false` avoids adopting newer sidecar feature behavior but should be revisited when enabling that Kubernetes feature. Major version bumps of provisioner and resizer can change supported flags or API interactions; dry-run and rollout tests are important.

## Test Signals
Confirm all container images and feature-gate flags in the running pod. Run provisioning, reclaim policy, resize, snapshot, restore, leader-election failover, and upgrade-from-v4.12.1 tests. Watch for sidecar flag parsing failures and forbidden API calls.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-controller.yaml -->
