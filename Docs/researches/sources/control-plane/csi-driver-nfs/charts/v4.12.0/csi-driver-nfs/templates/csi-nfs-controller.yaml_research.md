# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This template deploys the NFS CSI controller as an `apps/v1` `Deployment`. It hosts the control-plane CSI socket and sidecars that provision, resize, snapshot, and health-check NFS-backed volumes.

## APIs, Control Flow, and State
The Deployment is named from `controller.name`, uses `controller.replicas`, `controller.strategyType`, `hostNetwork: true`, `dnsPolicy`, and the controller service account. Scheduling either uses explicit `controller.affinity` or generated control-plane/master affinity when requested. Containers share an `emptyDir` socket at `/csi`: `csi-provisioner` performs PV/PVC provisioning with leader election, metadata, `HonorPVReclaimPolicy=true`, long timeouts, and retry backoff; `csi-resizer` handles volume expansion; optional `csi-snapshotter` is gated by `controller.enableSnapshotter`; `liveness-probe` exposes health; `nfs` is privileged, mounts kubelet pod directories bidirectionally, and serves the CSI endpoint.

## Dependencies and Integration Points
Images and resource blocks come from `values.yaml`. RBAC is provided by `rbac-csi-nfs.yaml`; snapshot operation also depends on snapshot CRDs and sidecar permissions. The controller writes transient CSI socket state only in `emptyDir` and uses host kubelet pod paths for mount operations.

## Risks and Test Signals
The privileged NFS container, host networking, and bidirectional mount propagation are high-trust settings. Misconfigured kubelet paths or DNS policy can break provisioning. Test with Helm rendering, controller pod readiness, leader election lease creation, dynamic PVC provisioning, resizing, snapshot creation when enabled, and liveness endpoint checks.
