# sources/control-plane/csi-driver-nfs/charts/v4.0.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v4.0.0 node DaemonSet with configurable kubelet directory.

Important APIs/types/functions: `DaemonSet`; `.Values.kubeletDir`, `.Values.controller.dnsPolicy`, node liveness/registrar/NFS containers, hostPath volumes.

Control flow: Host-networked node pods run on Linux, register `${kubeletDir}/plugins/csi-nfsplugin/csi.sock`, mount `${kubeletDir}/pods`, and expose the NFS CSI endpoint with mount-permissions.

State and persistence: Per-node socket, registry, and pod mount state under the configured kubelet directory.

Dependencies and integration points: Kubelet plugin registry, CSIDriver, workload pod mounts.

Risks: Template uses controller DNS policy for node pod DNS; wrong kubeletDir or missing plugin registry directory breaks registration. Test signals: DaemonSet rollout and kubelet registration on custom kubeletDir clusters.
