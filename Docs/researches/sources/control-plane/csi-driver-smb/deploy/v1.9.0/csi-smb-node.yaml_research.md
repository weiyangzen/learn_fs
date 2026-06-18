# sources/control-plane/csi-driver-smb/deploy/v1.9.0/csi-smb-node.yaml

## Purpose
Linux node DaemonSet for SMB CSI v1.9.0.

## Important APIs, Types, and Functions
Linux hostNetwork DaemonSet with livenessprobe v2.7.0, registrar v2.5.1, `smbplugin:v1.9.0`, privileged security context, CSI socket hostPath, kubelet mountpoint hostPath, and plugins registry hostPath.

## Control Flow
Serves node CSI RPCs from `/csi/csi.sock`, registers with kubelet, and performs CIFS mounts into kubelet-managed pod paths.

## State and Persistence
Host mount state and sockets persist in kubelet directories. Pod replacement does not remove existing host mounts by itself.

## Dependencies
Depends on Linux CIFS support, kubelet, mount propagation, and v1.9.0 images.

## Integration Points
Works with v1.9.0 controller and CSIDriver. Linux cleanup uses `mount-utils` rather than the Windows SMB mapping flag.

## Risks and Edge Cases
Privileged host access, mount propagation, DNS behavior, and stale mounts remain operational risks.

## Test Signals
DaemonSet rollout, health endpoint, CSINode registration, and successful stage/publish/unpublish/unstage flows.
