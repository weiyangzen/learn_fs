# sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-controller.yaml

## Purpose
Controller Deployment for SMB CSI v1.8.0. It runs external-provisioner, liveness probe, and the controller-capable SMB CSI process.

## Important APIs, Types, and Functions
Defines `apps/v1` Deployment `csi-smb-controller`, one replica, Linux node selector, control-plane tolerations, `csi-provisioner:v3.2.0`, `livenessprobe:v2.7.0`, and `smbplugin:v1.8.0`.

## Control Flow
The provisioner talks to the SMB CSI socket at `/csi/csi.sock` and performs leader-elected Create/DeleteVolume workflows. The SMB container exposes health port `29642` and metrics port `29644`.

## State and Persistence
Uses `emptyDir` for the internal controller socket. Cluster state is created through PV/PVC provisioning, events, and leases; no controller-local persistence survives pod restart.

## Dependencies
Depends on controller RBAC, Linux scheduling, sidecar images, the SMB CSI controller server, and kube-system leader-election leases.

## Integration Points
Pairs with `csi-smb-driver.yaml`, node DaemonSets, storage classes, and external-provisioner metadata injection.

## Risks and Edge Cases
Single replica relies on restart/leader election for availability. The SMB container is privileged even in the controller pod. Resource requests are small relative to provisioning bursts.

## Test Signals
Deployment rollout, liveness endpoint, provisioner leader-election lease, PVC provisioning/deletion, and metrics scraping on `29644`.
