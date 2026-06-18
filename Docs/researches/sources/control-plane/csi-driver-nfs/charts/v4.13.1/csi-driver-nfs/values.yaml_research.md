# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/values.yaml

## Purpose
This values file defines the default configuration for the v4.13.1 NFS CSI Helm chart. It controls images, service accounts, RBAC, driver behavior, controller and node pod scheduling, snapshot support, storage classes, and resource requests.

## Important APIs, Types, and Functions
Important value trees are `image`, `serviceAccount`, `rbac`, `driver`, `feature`, `kubeletDir`, `controller`, `nodeDriverRegistrar`, `node`, `externalSnapshotter`, `volumeSnapshotClass`, `imagePullSecrets`, `storageClass`, and commented `storageClasses`. Defaults use nfsplugin `v4.13.1`, csi-provisioner `v6.1.0`, csi-resizer `v2.0.0`, csi-snapshotter/snapshot-controller `v8.4.0`, livenessprobe `v2.17.0`, and node-driver-registrar `v2.15.0`.

## Control Flow, State, and Persistence
These values feed Helm conditionals and arguments across all templates. Defaults enable the controller snapshotter sidecar but disable the separately deployed external snapshot controller and optional snapshot CRDs. StorageClass and VolumeSnapshotClass creation are disabled by default, so installation registers the driver and workloads but does not create user-facing classes unless configured.

## Dependencies and Integration Points
The file binds chart rendering to Kubernetes storage APIs, CSI sidecar versions, registry naming conventions, host kubelet paths, NFS mount behavior, and optional CRD lifecycle. `image.baseRepo` composes sidecar images whose repository values start with `/`.

## Risks and Test Signals
Risks include version skew among CSI sidecars, enabling snapshot paths without CRDs/controller, broad default tolerations, privileged host integration, and the v4.13.1 node template ignoring `node.dnsPolicy`. Signals are value-matrix `helm template` runs, chart install/upgrade tests, PVC create/delete/resize, node registration, optional snapshot class/CRD/controller tests, and image pull validation in restricted registries.
