# sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-node-windows.yaml

## Purpose
Windows node DaemonSet for SMB CSI v1.8.0.

## Important APIs, Types, and Functions
Same topology as v1.7.0 but updates sidecars to `livenessprobe:v2.7.0`, `csi-node-driver-registrar:v2.5.1`, and `smbplugin:v1.8.0`.

## Control Flow
Schedules on Windows nodes, exposes CSI socket under `C:\csi`, registers with kubelet, and connects the SMB container to CSI proxy filesystem/SMB pipes.

## State and Persistence
Host state remains in kubelet plugin, registry, and CSI proxy pipe paths. No SMB mapping cleanup flag is enabled in this version.

## Dependencies
Depends on Windows kubelet, CSI proxy v1 or v1beta1 named pipes, and v1.8.0 images.

## Integration Points
Integrates with v1.8.0 RBAC, CSIDriver, and Windows mounter implementations that can negotiate CSI proxy versions.

## Risks and Edge Cases
Compatibility with v1beta1 pipes is preserved but may hide CSI proxy upgrades. Global SMB mappings can outlive pod lifecycle depending on node unmount behavior.

## Test Signals
DaemonSet rollout, registrar probe, health endpoint, successful Windows staging/publishing, and CSI proxy pipe availability.
