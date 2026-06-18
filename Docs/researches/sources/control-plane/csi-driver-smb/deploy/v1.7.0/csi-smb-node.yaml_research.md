# sources/control-plane/csi-driver-smb/deploy/v1.7.0/csi-smb-node.yaml

## Purpose
Linux DaemonSet for the v1.7.0 SMB CSI node plugin. It runs the node CSI service, liveness sidecar, and kubelet registrar on every Linux node.

## Important APIs, Types, and Functions
Defines `csi-smb-node` with host networking, Linux node selector, system-node-critical priority, privileged `smb` container, CSI socket hostPath, kubelet mountpoint hostPath with bidirectional mount propagation, and plugins registry hostPath.

## Control Flow
The SMB container serves CSI over `/csi/csi.sock`; the registrar exposes `/var/lib/kubelet/plugins/smb.csi.k8s.io/csi.sock` to kubelet. Kubelet then calls NodeStage/Publish methods for SMB volumes.

## State and Persistence
Persists the plugin socket and kubelet volume mounts under `/var/lib/kubelet`. The pod itself has no app data, but it manipulates host mounts through privileged mode and mount propagation.

## Dependencies
Depends on Linux CIFS mount support, kubelet plugin paths, `livenessprobe:v2.6.0`, `csi-node-driver-registrar:v2.5.0`, and `smbplugin:v1.7.0`.

## Integration Points
Integrates with kubelet CSI registration, node-local mount namespace, host networking/DNS policy, and node service account permissions.

## Risks and Edge Cases
Privileged host mount access has high blast radius. HostNetwork plus `dnsPolicy: Default` may affect SMB DNS behavior. Missing CIFS support or kubelet path drift causes runtime mount failures.

## Test Signals
Rollout, registrar liveness, `/healthz`, CSINode driver entry, and successful SMB volume stage/publish are primary signals.
