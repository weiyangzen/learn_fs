# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-rbdplugin-provisioner.yaml

Purpose: static RBD provisioner Service and Deployment.

Important APIs/types/functions: 3-replica Deployment with main `csi-rbdplugin --controllerserver=true`, CSI-Addons endpoint, clone-depth flags, external-provisioner, snapshotter, attacher, resizer, metadata controller, liveness sidecar on 8680, KMS ConfigMap, Ceph config, and projected OIDC token.

Control flow: sidecars communicate with the RBD controller socket, perform leader-elected Kubernetes storage operations, and expose liveness metrics through the Service.

State and persistence behavior: ephemeral socket/key dirs; persistent state includes Kubernetes PV/PVC/snapshot/attachment objects, Ceph RBD images/snapshots, OMAP metadata, and optional KMS-backed encryption data.

Dependencies and integration points: RBD provisioner RBAC, Ceph config, Ceph-CSI config, KMS config, host `/dev`/`sys`/modules, CSI sidecars, and CSI-Addons.

Risks: canary image and default namespace are sample values. Host device access in controller pods is sensitive. Snapshotter group snapshot feature is enabled in static manifest, so CRDs/RBAC must exist.

Test signals: RBD provisioning, clone, snapshot/group-snapshot, expansion, metrics, and encryption tests.
