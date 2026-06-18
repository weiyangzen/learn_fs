# sources/control-plane/csi-driver-nfs/charts/v3.0.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: v3.0.0 controller Deployment for dynamic NFS provisioning.

Important APIs/types/functions: `Deployment`; containers `csi-provisioner`, `liveness-probe`, `nfs`; values for names, service account, replicas, tolerations, resources, log level, and images.

Control flow: Host-networked controller runs on Linux, optionally tolerates control-plane taints, starts provisioner with leader election and extra metadata, probes the CSI socket, and starts the NFS driver with `--drivername` and liveness endpoint.

State and persistence: Uses emptyDir socket and hostPath kubelet pod mount. Persistent cluster state is created by sidecars as PVs/PVC updates/events/leases.

Dependencies and integration points: Requires RBAC, CSIDriver object, and kubelet pod path access for NFS directory operations.

Risks: Privileged `SYS_ADMIN` container, hostNetwork DNS assumptions, and no configurable kubelet path. Test signals: leader election lease, liveness probe, and PVC create/delete workflow.
