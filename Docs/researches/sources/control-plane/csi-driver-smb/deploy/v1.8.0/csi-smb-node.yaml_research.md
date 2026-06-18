# sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-node.yaml

## Purpose
Linux node DaemonSet for SMB CSI v1.8.0.

## Important APIs, Types, and Functions
Defines hostNetwork Linux node pod with livenessprobe v2.7.0, registrar v2.5.1, `smbplugin:v1.8.0`, privileged mode, `/csi` socket, plugin registry, and bidirectional `/var/lib/kubelet` mount propagation.

## Control Flow
The pod registers the SMB driver with kubelet and handles node-stage/node-publish CSI requests through the SMB container.

## State and Persistence
Persists node CSI socket and host mount state under `/var/lib/kubelet`. No container-local data persistence.

## Dependencies
Depends on Linux CIFS tooling/kernel support, kubelet CSI directories, and v1.8.0 sidecars.

## Integration Points
Works with the v1.8.0 controller, CSIDriver, and Linux `SafeFormatAndMount` implementation.

## Risks and Edge Cases
Privileged mount access and bidirectional propagation are necessary but high risk. DNS policy and host networking can influence SMB service name resolution.

## Test Signals
Rollout, liveness, CSINode registration, and successful pod volume mounts.
