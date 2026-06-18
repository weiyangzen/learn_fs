# sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-node-windows.yaml

## Purpose
Windows DaemonSet for the v1.7.0 SMB CSI node plugin. It deploys the liveness sidecar, node-driver-registrar, and `smbplugin:v1.7.0` on Windows nodes.

## Important APIs, Types, and Functions
Defines an `apps/v1` DaemonSet named `csi-smb-node-win` in `kube-system`, with Windows node selector, `csi-smb-node-sa`, plugin socket at `C:\csi\csi.sock`, kubelet registration path, health port `29643`, and CSI proxy filesystem/SMB pipe hostPaths for v1 and v1beta1.

## Control Flow
Kubernetes schedules one pod per Windows node. The SMB container starts with endpoint, node ID, and metrics address flags. The registrar registers the Windows kubelet plugin socket, and the liveness probe checks the CSI endpoint through the health endpoint.

## State and Persistence
Persistent host state lives under `C:\var\lib\kubelet\plugins\smb.csi.k8s.io\`, `plugins_registry`, and CSI proxy named pipes. Rolling updates permit one unavailable node pod.

## Dependencies
Depends on Windows kubelet layout, CSI proxy named pipes, `registry.k8s.io/sig-storage/livenessprobe:v2.6.0`, `csi-node-driver-registrar:v2.5.0`, and `smbplugin:v1.7.0`.

## Integration Points
Integrates with kubelet CSI registration, Windows CSI proxy filesystem and SMB APIs, node identity injection through `spec.nodeName`, and RBAC from `rbac-csi-smb.yaml`.

## Risks and Edge Cases
Missing CSI proxy pipes or host directories prevent startup. Both v1 and v1beta1 pipes are mounted for compatibility, increasing deployment assumptions. Windows socket path escaping is fragile.

## Test Signals
Signals are DaemonSet rollout, registrar liveness probe, `/healthz` success on `29643`, successful CSINode registration, and SMB mount operations on Windows nodes.
