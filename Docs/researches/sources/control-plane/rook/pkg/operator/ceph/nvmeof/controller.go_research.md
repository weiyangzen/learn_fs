<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller.go

## Purpose
This file implements the `CephNVMeOFGateway` controller. It watches gateway CRs and owned Deployments/Services, validates gateway specs, manages readiness/finalizers/status, reconciles per-instance gateway Deployments and Services, generates default config maps, and tracks CephX key rotation status.

## Important APIs and control flow
`Add` registers CSI addons and CSI operator schemes, watches the CR, and watches owned Services/Deployments. `reconcile` fetches the CR, adds a finalizer, initializes status, waits for ready `CephCluster`, loads cluster info, handles deletion by removing finalizer, checks running/desired Ceph versions and upgrade state, validates `instances`, `group`, and `pool`, determines CephX key rotation, reconciles resources, and updates Ready status. `reconcileCreateCephNVMeOFGateway` validates external cluster version, counts current deployments by labels, scales down extra instances, and calls `upCephNVMeOFGateway`. `upCephNVMeOFGateway` creates default per-instance ConfigMaps unless `spec.configMapRef` is set, builds deployments, create-or-updates them, and creates Services. `downCephNVMeOFGateway` deletes Deployments and Services for removed indexes. `getNVMeOFGatewayConfig` builds INI config with default gateway/discovery/ceph/mtls/spdk/monitor sections and user overrides. ConfigMap helpers persist generated config and hash it. `updateStatus` writes phase, observed generation, and CephX daemon status with conflict retries.

## State and persistence
State includes `CephNVMeOFGateway.status`, finalizers, events, per-instance Deployments, Services, generated ConfigMaps, pod config hash annotations, CephX status, and Ceph-side NVMe gateway state initialized by the embedded script.

## Dependencies and integration points
The controller depends on Rook cluster readiness/version helpers, keyring status helpers, Kubernetes clients, INI generation, Rook labels/owner refs, and spec helpers. It integrates with Ceph config to discover the NVMe-oF image when the CR omits one, and with CSI/addons schemes for operator-wide API availability.

## Risks and test signals
Scale-down deletes resources in increasing index order from desired count to current count; label count correctness is critical. Custom `configMapRef` leaves config hash empty, so config changes in external ConfigMaps will not automatically roll pods. The controller updates status for key rotation but this subset does not show per-daemon key Secret generation like NFS. Tests cover readiness gates, invalid specs, single/multiple instances, scale down, multiple CRs, CephX status rotation, and config generation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller.go -->
