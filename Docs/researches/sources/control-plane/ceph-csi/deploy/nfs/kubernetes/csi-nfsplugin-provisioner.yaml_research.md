# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nfsplugin-provisioner.yaml

Purpose: static NFS provisioner Service and Deployment.

Important APIs/types/functions: 3-replica Deployment with anti-affinity, main `csi-nfsplugin --controllerserver=true`, external-provisioner, attacher, resizer, snapshotter, liveness sidecar on 8682, and `nfs-csi-provisioner` service account.

Control flow: sidecars call the NFS CSI controller over `csi-provisioner.sock`, perform leader-elected Kubernetes storage operations, and expose metrics through the Service.

State and persistence behavior: ephemeral socket/key dirs; persistent state is Kubernetes storage objects and backend NFS/Ceph state managed by the driver.

Dependencies and integration points: `ceph-csi-config`, host `/sys`, CSI sidecars, Kubernetes RBAC, and `cephcsi --type=nfs`.

Risks: canary images and hardcoded defaults are sample-oriented. NFS manifest lacks Ceph config/KMS mounts used by RBD/CephFS because the integration surface is narrower.

Test signals: NFS provisioning, attach/resizer/snapshot sidecar behavior, and metrics.
