# sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-node-windows.yaml

## Purpose
Windows node DaemonSet for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Extends the v1.8.0 Windows manifest by using `smbplugin:v1.9.0` and adding `--remove-smb-mapping-during-unmount=true` to the SMB container.

## Control Flow
Node pod registers the driver and mounts via CSI proxy pipes. On unmount, the v1 Windows mounter can remove SMB global mappings after reference counting.

## State and Persistence
Uses host kubelet plugin/registry directories and CSI proxy pipes. The remove-mapping flag makes local reference files under the Windows CSI mount base relevant to cleanup state.

## Dependencies
Depends on Windows CSI proxy, kubelet host paths, v1.9.0 plugin image, and refcounter logic in `pkg/mounter`.

## Integration Points
Connects directly to `RemoveSMBMappingDuringUnmount` driver option and Windows `SMBUnmount` behavior.

## Risks and Edge Cases
Incorrect reference counts can remove a global SMB mapping still used by another volume or leave mappings behind. Mixed v1/v1beta proxy environments may not support identical cleanup semantics.

## Test Signals
Windows mount/unmount tests, absence of leaked SMB global mappings, liveness, registrar probe, and successful repeated volume reuse.
