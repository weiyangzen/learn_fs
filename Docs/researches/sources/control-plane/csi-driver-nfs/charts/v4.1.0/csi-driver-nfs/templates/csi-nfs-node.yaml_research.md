# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v4.1.0 node DaemonSet with service account and scheduling customization.

Important APIs/types/functions: `DaemonSet`; value-driven affinity/nodeSelector/tolerations/resources, `kubeletDir`, node service account, registrar/liveness/NFS containers.

Control flow: Runs host-networked on Linux using `serviceAccountName: csi-nfs-node-sa`, optional affinity and nodeSelector, then registers and serves the CSI socket under the configured kubelet directory.

State and persistence: Node-local hostPath socket/registration/mount state.

Dependencies and integration points: Node service account from `rbac-csi-nfs.yaml`, kubelet plugin registry, host NFS mount configuration.

Risks: ServiceAccount name is literal in this version, so custom `serviceAccount.node` is not available. Privileged mount access remains. Test signals: render node SA and DaemonSet together, check registration and PVC mount.
