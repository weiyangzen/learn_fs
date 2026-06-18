# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin-provisioner.yaml

Purpose: static CephFS provisioner Service and Deployment manifest.

Important APIs/types/functions: Deployment has 3 replicas with anti-affinity, `cephfs-csi-provisioner` service account, main `csi-cephfsplugin --controllerserver=true`, external-provisioner, attacher, resizer, snapshotter with group snapshot feature, Ceph-CSI metadata controller, and liveness metrics sidecar on target port 8681.

Control flow: sidecars communicate with the CephFS controller over `unix:///csi/csi-provisioner.sock`, perform leader-elected Kubernetes storage operations, and expose metrics through the Service.

State and persistence behavior: ephemeral socket/key dirs; persistent state is Kubernetes PV/PVC/snapshot objects and CephFS subvolumes/snapshots/metadata.

Dependencies and integration points: mounts Ceph config, Ceph-CSI config, KMS config, host `/sys`, `/dev`, `/lib/modules`, and uses Kubernetes CSI sidecar images.

Risks: canary image defaults, hardcoded namespace/account names, and high timeout values are sample-oriented. Anti-affinity can block small clusters. KMS ConfigMap must exist even if empty.

Test signals: CephFS e2e provisioning, expansion, snapshots, metadata controller behavior, and metrics scrape.
