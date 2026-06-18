<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
## sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-proxy-windows.yaml

Purpose: renders an optional Windows `csi-proxy` HostProcess `DaemonSet` for chart v1.15.0. It exists to deploy the Windows csi-proxy service from the chart when `.Values.windows.csiproxy.enabled` is true, primarily for non-HostProcess Windows SMB node pods that need filesystem and SMB operations through named pipes.

Important APIs and inputs are `apps/v1 DaemonSet`, `.Values.windows.csiproxy.dsName`, tolerations, nodeSelector, affinity, priority class, HostProcess `securityContext.windowsOptions`, `hostNetwork: true`, pull secrets, and `.Values.image.csiproxy`. The container selection uses the same baseRepo-prefix pattern as other modern templates when the repository starts with `/`.

Control flow is a single Helm guard around `.Values.windows.csiproxy.enabled`. State is cluster and node-local: Kubernetes stores the DaemonSet while Windows hosts run csi-proxy and expose named pipes consumed by `csi-smb-node-windows.yaml`. Dependencies include Kubernetes Windows HostProcess support, the configured runAs user, Windows nodes, and compatible csi-proxy image versions.

Risks include enabling this on clusters without HostProcess support, running as a highly privileged Windows account, version skew between csi-proxy and the SMB plugin, scheduling conflicts if csi-proxy is already installed outside the chart, and chart defaults leaving it disabled even when non-HostProcess Windows nodes need it. Test signals are rendered manifest checks, Windows pod startup logs, host process creation, csi-proxy pipe presence, and SMB mount smoke tests from a Windows workload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/charts/v1.15.0/csi-driver-smb/templates/csi-proxy-windows.yaml -->
