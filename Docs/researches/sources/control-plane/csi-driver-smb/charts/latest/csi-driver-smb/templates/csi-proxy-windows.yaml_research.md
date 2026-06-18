## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: optionally deploys CSI Proxy as a Windows HostProcess DaemonSet when `.Values.windows.csiproxy.enabled` is true. This supports non-HostProcess SMB node deployments that need named pipe access to host filesystem and SMB operations.

Important template behavior: it renders a DaemonSet with rolling update, release namespace, labels, optional tolerations/affinity, Windows HostProcess security context, host networking, Windows nodeSelector, priority class, pull secrets, and a `csi-proxy` container. Image resolution supports either baseRepo-relative repositories or absolute repositories.

State is a cluster DaemonSet and its Windows host process pods. Dependencies include Windows nodes, HostProcess support, csi-proxy image, values for username/nodeSelector, and helper templates `smb.labels` and `smb.pullSecrets`. Risks include disabled default while needed for non-HostProcess mode, privileged host access, and Windows HostProcess version compatibility. Test signal is Helm render/install and Windows e2e mount behavior.
