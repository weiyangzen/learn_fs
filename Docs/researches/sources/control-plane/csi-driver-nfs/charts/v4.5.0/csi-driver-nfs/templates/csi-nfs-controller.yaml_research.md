# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose

This v4.5.0 template deploys the host-networked NFS CSI controller `Deployment` with `csi-provisioner`, `csi-snapshotter`, `liveness-probe`, and the privileged NFS driver container.

## APIs, control flow, and state

The template renders from chart values for replicas, strategy, labels, image pull secrets, service account, scheduling, priority, resources, health port, and image tags. Both CSI sidecars use `/csi/csi.sock` and leader election in the release namespace. The NFS container receives `NODE_ID`, `CSI_ENDPOINT`, driver name, mount permissions, working mount directory, and default on-delete policy. Shared state is through an `emptyDir` socket, an `emptyDir` working mount directory, and hostPath `${kubeletDir}/pods` with bidirectional mount propagation; durable control-plane state is in Kubernetes API resources and leases.

## Dependencies and integration points

The deployment integrates with RBAC from `rbac-csi-nfs.yaml`, the `CSIDriver` object, StorageClasses using `nfs.csi.k8s.io`, snapshot APIs, kubelet host paths, Linux nodes, and registry images. v4.5.0 keeps the same controller template content as v4.4.0 while values update sidecar versions.

## Risks and test signals

The controller remains privileged and host-mounted, and sidecars in this version do not yet drop all capabilities. The `csi-snapshotter` sidecar is present regardless of whether the optional external snapshot-controller is enabled, so snapshot RBAC and CRD availability still matter. Test by rendering custom values, checking deployment rollout, provisioning PVCs, creating/deleting volumes, verifying liveness, checking leader-election leases, and exercising snapshots when CRDs are available.
