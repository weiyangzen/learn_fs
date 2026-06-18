# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose

This template deploys the NFS CSI controller as an `apps/v1` `Deployment`. It runs the CSI external provisioner, CSI snapshotter sidecar, liveness probe, and the NFS CSI driver container in one host-networked pod so the controller can provision NFS-backed volumes and perform controller-side mount work.

## APIs, control flow, and state

Helm renders metadata labels, namespace, replica count, strategy, image pull secrets, scheduling constraints, priority, resources, service account, and image tags from `values.yaml`. The `csi-provisioner` talks to `/csi/csi.sock`, uses leader election in the release namespace, creates extra metadata, and waits up to 1200 seconds. The `csi-snapshotter` also talks to the same socket with leader election. The NFS plugin receives `NODE_ID` from `spec.nodeName`, `CSI_ENDPOINT=unix:///csi/csi.sock`, the configured CSI driver name, mount permissions, working mount directory, and default on-delete policy.

The pod persists no application data. It uses an `emptyDir` socket directory shared by the sidecars, an `emptyDir` working mount directory, and a hostPath mount of `${kubeletDir}/pods` with bidirectional mount propagation. State is primarily held in Kubernetes objects such as PVs, PVCs, snapshots, leases, and events; the deployment itself is declarative state.

## Dependencies and integration points

This deployment depends on the service account and cluster role from `rbac-csi-nfs.yaml`, the `CSIDriver` object, kubelet host paths, Linux nodes, registry images, and snapshot CRDs if snapshot operations are used. The privileged NFS container requires `SYS_ADMIN` for mount operations and host networking for NFS behavior.

## Risks and test signals

The template grants a privileged controller container and bidirectional host mounts, so scheduling it on unexpected nodes is sensitive. v4.4.0 image references are direct repository/tag strings and lack later hardening such as dropping all capabilities on sidecars. Test signals include `helm template` rendering with custom node selectors/tolerations, pod readiness and liveness on the configured health port, successful dynamic provisioning, leader-election lease creation, NFS mount cleanup, and snapshot creation when snapshot APIs are installed.
