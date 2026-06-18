# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-deployment.yaml

Purpose: renders the RBD controller/provisioner Deployment.

Important APIs/types/functions: main `csi-rbdplugin` runs `--type=rbd --controllerserver=true`, clone-depth/snapshot thresholds, CSI-Addons endpoint, cluster/instance/fencing/profiling flags, and metadata flag. Sidecars include external-provisioner, optional resizer, snapshotter, optional attacher, optional Ceph-CSI metadata controller, and optional liveness metrics container.

Control flow: Deployment replicas coordinate through leader election and shared socket `emptyDir`. The Ceph-CSI controller serves CSI calls; sidecars watch Kubernetes storage APIs, call the socket, and update PV/PVC/snapshot/attachment state.

State and persistence behavior: Kubernetes API objects store controller results; Ceph stores RBD images, snapshots, OMAP metadata, and optional encrypted metadata. In-pod sockets and key dirs are ephemeral.

Dependencies and integration points: depends on Ceph/KMS/config ConfigMaps, service account/RBAC, external CSI sidecar images, host `/dev` and `/sys`, lib modules, and optional projected KMS token.

Risks: version skew among sidecars and CSI driver affects feature support. Multi-replica anti-affinity may block scheduling on small clusters. Clone/snapshot thresholds must remain within driver validation. Host network changes DNS/network behavior.

Test signals: RBD provisioning, deletion, expansion, snapshots, clones, group snapshots, metrics, and controller failover tests.
