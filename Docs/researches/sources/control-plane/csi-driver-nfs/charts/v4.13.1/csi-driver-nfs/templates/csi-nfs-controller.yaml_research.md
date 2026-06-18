# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This template renders the NFS CSI controller `Deployment`. It hosts the CSI provisioner, resizer, optional snapshotter sidecar, liveness probe, and privileged NFS CSI driver container that performs controller-side NFS mounts for provisioning and snapshot work.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` using Helm values for replicas, strategy, service account, image repositories, pull policies, resources, affinity, node selectors, tolerations, and priority class. Sidecars use `csi-provisioner`, `csi-resizer`, `csi-snapshotter`, and `livenessprobe`; the driver container runs `nfsplugin` with `--drivername`, `--mount-permissions`, `--working-mount-dir`, `--default-ondelete-policy`, `--use-tar-command-in-snapshot`, and `--enable-snapshot-compression`.

## Control Flow, State, and Persistence
The pod always uses `hostNetwork: true` and mounts the host kubelet pod directory with bidirectional propagation plus an `emptyDir` CSI socket. Affinity selection prefers explicit `.Values.controller.affinity` when it contains `nodeSelectorTerms`; otherwise `runOnControlPlane` and `runOnMaster` synthesize required node affinity. Leader election state for sidecars is stored in namespace-scoped `Lease` objects. Persistent state is Kubernetes PV/PVC/snapshot metadata and NFS backing directories, not pod-local storage.

## Dependencies and Integration Points
The controller depends on `rbac-csi-nfs.yaml`, the controller service account, `CSIDriver` registration, kubelet host paths, external-provisioner/resizer/snapshotter APIs, and optional snapshot CRDs. Image repositories can be absolute or composed from `image.baseRepo` when the repository value starts with `/`.

## Risks and Test Signals
Risks include privileged `SYS_ADMIN`, host networking, broad cluster RBAC, DNS sensitivity under `ClusterFirstWithHostNet`, and snapshot sidecar rendering when CRDs/RBAC are absent. v4.13.1's paired node template still reads controller DNS policy for the node pod, so test both controller and node DNS overrides. Signals are `helm template`, kubeconform validation, controller rollout, sidecar leader-election leases, successful PVC provisioning, expansion, deletion, and snapshot creation when enabled.
