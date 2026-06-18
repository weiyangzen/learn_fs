# sources/control-plane/csi-driver-smb/charts/v1.20.0/csi-driver-smb/templates/csi-smb-node-windows.yaml

## Purpose
This template renders the legacy, non-HostProcess Windows SMB CSI node `DaemonSet` for chart `v1.20.0`. It is active when `.Values.windows.enabled` and `not .Values.windows.useHostProcessContainers`, giving Windows nodes a CSI registrar, liveness probe, and SMB node plugin that communicate through Windows filesystem paths and CSI proxy pipes.

## Important APIs, Types, And Functions
The API is `apps/v1/DaemonSet`. Containers are `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar uses `DRIVER_REG_SOCK_PATH` under `.Values.windows.kubelet`, and the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, optional volume stats, and `--remove-smb-mapping-during-unmount` in newer charts. The pod mounts kubelet, plugin, registration, and v1 and v1beta1 CSI proxy filesystem/SMB named pipes host paths.

## Control Flow
Helm applies Windows tolerations, node selectors, optional affinity, pull secrets, resources, and priority class. Modern charts render this file only when HostProcess mode is disabled, while HostProcess mode is handled by the sibling `csi-smb-node-windows-hostprocess.yaml` file. It uses `.Values.serviceAccount.node` in modern charts.

## State And Persistence Behavior
Persistent node state is the kubelet plugin directory and registration directory on the Windows host. SMB mappings are host-visible through CSI proxy; the unmount cleanup flag controls whether mappings are removed during teardown.

## Dependencies And Integration Points
This path depends on a working Windows CSI proxy installation exposing the expected named pipes, Windows-compatible CSI sidecar images, kubelet path conventions, and matching `CSIDriver`/registrar driver names.

## Risks And Test Signals
Risks include missing CSI proxy pipes, path escaping errors, incompatible Windows image tags, and stale SMB mappings. Test by templating both HostProcess modes, checking DaemonSet scheduling on Windows nodes, verifying plugin registration, and mounting/unmounting an SMB PVC on Windows.
