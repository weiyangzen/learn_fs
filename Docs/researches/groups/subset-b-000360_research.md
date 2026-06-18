# subset-b-000360 Research

Grouped research for the CSI NFS driver Kubernetes deployment manifests in `deploy/v4.12.0`, `deploy/v4.12.1`, and `deploy/v4.13.0`. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/crd-csi-snapshot.yaml

## Purpose
Installs the Kubernetes CSI snapshot API surface required by the NFS CSI deployment. The file defines three `apiextensions.k8s.io/v1` CRDs in API group `snapshot.storage.k8s.io`: namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`.

## Important APIs, Types, And Objects
`VolumeSnapshot` models a user's snapshot request. Its `spec.source` is a one-of union of `persistentVolumeClaimName` for dynamic creation or `volumeSnapshotContentName` for binding an existing content object. Status exposes `readyToUse`, `restoreSize`, `creationTime`, `error`, and `boundVolumeSnapshotContentName`.

`VolumeSnapshotClass` stores driver-level snapshot parameters with required `driver` and `deletionPolicy` values. `VolumeSnapshotContent` stores the cluster object that represents the backing CSI snapshot, requiring `deletionPolicy`, `driver`, `source`, and `volumeSnapshotRef`, plus status fields such as CSI `snapshotHandle`.

All three resources serve and store `v1`. Deprecated `v1beta1` schemas are present with warnings but `served: false` and `storage: false`, so beta clients cannot use them after this CRD is applied.

## Control Flow
This file must be applied before `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, and any `VolumeSnapshotClass` or `VolumeSnapshot` objects. Once registered, the Kubernetes API server validates snapshot objects against these schemas and stores them in etcd. The snapshot controller watches `VolumeSnapshot` and `VolumeSnapshotContent`; the CSI snapshotter sidecar binds requests to the NFS CSI driver over the controller socket.

## State And Persistence Behavior
The CRDs themselves are durable cluster-level API definitions. Snapshot objects created through them are persisted in Kubernetes etcd, with desired state in `spec` and controller-owned progress in `status` subresources. This manifest has no local filesystem state, but it changes the cluster's API discovery and validation behavior.

## Dependencies And Integration Points
Depends on the Kubernetes apiextensions API and the external-snapshotter API contract. It integrates with the snapshot controller RBAC, snapshot controller deployment, CSI snapshotter sidecar in the NFS controller deployment, and `snapshotclass.yaml` using driver `nfs.csi.k8s.io`.

## Risks And Edge Cases
Applying CRDs is cluster-wide and can affect every snapshot client. Because `v1beta1` is not served, older automation still using beta snapshot APIs will fail. Consumers must validate the bidirectional binding between `VolumeSnapshot` and `VolumeSnapshotContent` before restore. `sourceVolumeMode` is marked alpha in the schema, so compatibility should be checked during Kubernetes upgrades. The empty `status.acceptedNames` and `storedVersions` blocks are harmless in manifests because the apiserver owns CRD status.

## Test Signals
Use server-side dry-run or `kubectl apply --server-side --dry-run=server` to validate the CRDs, then confirm API discovery for `volumesnapshots`, `volumesnapshotclasses`, and `volumesnapshotcontents`. Exercise creation of a class, a PVC-backed `VolumeSnapshot`, status updates by the controller, and rejection of invalid source objects with neither or both source fields.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-controller.yaml

## Purpose
Defines the `kube-system/csi-nfs-controller` Deployment for the v4.12.0 NFS CSI driver. It runs the CSI controller plugin together with Kubernetes CSI sidecars for provisioning, expansion, snapshots, and liveness.

## Important APIs, Types, And Objects
The pod has five containers sharing `/csi/csi.sock` through an `emptyDir`: `csi-provisioner:v5.3.0`, `csi-resizer:v1.14.0`, `csi-snapshotter:v8.3.0`, `livenessprobe:v2.17.0`, and `nfsplugin:v4.12.0`. Sidecars use `--csi-address=$(ADDRESS)`, leader election in `$(POD_NAMESPACE)`, long CSI timeouts, and bounded retry intervals. The NFS plugin runs privileged with `SYS_ADMIN`, `allowPrivilegeEscalation: true`, `NODE_ID` from `spec.nodeName`, and `CSI_ENDPOINT=unix:///csi/csi.sock`.

## Control Flow
The Deployment starts one controller pod on Linux, with host networking and control-plane tolerations. Sidecars connect to the NFS plugin socket and watch Kubernetes resources: PVC/PV creation, expansion requests, and snapshot objects. The controller plugin mounts NFS and creates backing directories, using `/var/lib/kubelet/pods` mounted bidirectionally for mount propagation. The liveness probe polls the plugin health endpoint on `localhost:29652`.

## State And Persistence Behavior
The pod itself is stateless, but it orchestrates persistent Kubernetes objects and backing NFS directories. Leader election state is stored in `coordination.k8s.io` Lease objects. The CSI socket is ephemeral in `emptyDir`; kubelet pod mount state is accessed through the hostPath mount.

## Dependencies And Integration Points
Requires `rbac-csi-nfs.yaml` service account and roles, the `CSIDriver` object, snapshot CRDs/RBAC for snapshot sidecar operation, and the `StorageClass`/`VolumeSnapshotClass` resources that reference `nfs.csi.k8s.io`.

## Risks And Edge Cases
The controller is privileged, host-networked, and has bidirectional hostPath mount propagation, which is necessary for this driver but broadens node risk. A single replica makes leader election mostly future-proofing rather than HA. Resource requests are very small, so busy provision or snapshot workloads may be throttled. The deployment assumes `/var/lib/kubelet/pods`, which may differ on custom kubelet roots.

## Test Signals
Validate with Kubernetes schema dry-run, then check all containers become ready and `/healthz` responds. Functional tests should create and delete PVCs using `nfs-csi`, expand a PVC, create a snapshot, restore from a snapshot, and confirm sidecar leader-election Leases and event emissions are present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-driverinfo.yaml

## Purpose
Registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

## Important APIs, Types, And Objects
The object sets `attachRequired: false`, declares `volumeLifecycleModes: [Persistent]`, and uses `fsGroupPolicy: File`. This tells Kubernetes that volumes from this driver do not require a CSI attach/detach phase, are persistent-volume oriented, and may have file ownership adjusted according to pod `fsGroup`.

## Control Flow
The scheduler, attach/detach controller, kubelet, and CSI sidecars consult this object when handling volumes provisioned by `nfs.csi.k8s.io`. Because attach is disabled, pods can proceed without waiting for a `VolumeAttachment` object. Node publishing is handled by the node daemonset rather than a separate attach controller.

## State And Persistence Behavior
This is a durable cluster-scoped API object persisted in etcd. It stores driver capability metadata only; it does not persist volume state or runtime sockets.

## Dependencies And Integration Points
Integrates with `StorageClass.provisioner`, `VolumeSnapshotClass.driver`, the node-driver-registrar registration path, and the NFS controller/node plugin identity. The name must match the CSI driver name returned by the plugin.

## Risks And Edge Cases
If the plugin reports a different driver name, provisioning and snapshot resources will not bind correctly. `fsGroupPolicy: File` can introduce recursive permission work on large NFS trees, depending on Kubernetes behavior and volume contents. Persistent-only mode means ephemeral inline CSI use is not declared.

## Test Signals
After applying, verify `kubectl get csidriver nfs.csi.k8s.io -o yaml`. Provision a pod using an NFS CSI PVC and confirm no `VolumeAttachment` is created for the volume. Test pod `fsGroup` behavior on files written through the mounted NFS volume.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-node.yaml

## Purpose
Defines the `kube-system/csi-nfs-node` DaemonSet for v4.12.0. It runs one NFS CSI node plugin per Linux node, registers the driver with kubelet, and performs node-stage/node-publish mount operations.

## Important APIs, Types, And Objects
The pod contains `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.12.0`. The registrar points kubelet at `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` through `--kubelet-registration-path`. The NFS plugin runs privileged with `SYS_ADMIN`, `NODE_ID` from the node name, and `CSI_ENDPOINT=unix:///csi/csi.sock`.

## Control Flow
The DaemonSet schedules on all Linux nodes with broad tolerations and host networking. The NFS plugin creates its CSI socket in the hostPath plugin directory, the registrar creates kubelet plugin registration under `/var/lib/kubelet/plugins_registry`, and the liveness probe checks `localhost:29653`. Mount operations propagate through the bidirectional `/var/lib/kubelet/pods` hostPath.

## State And Persistence Behavior
Runtime socket and registration files live under kubelet host paths. Volume mount state is maintained by kubelet and the host mount table, while Kubernetes workload state remains in API objects. The DaemonSet strategy rolls one unavailable node pod at a time.

## Dependencies And Integration Points
Requires `csi-nfs-node-sa`, the matching `CSIDriver`, kubelet's CSI plugin registry, Linux NFS client support, and the controller-created PVs. It shares the driver name and socket contract with the controller deployment.

## Risks And Edge Cases
Privileged hostPath access and bidirectional mount propagation are powerful. Custom kubelet roots or read-only host paths will break registration or mounts. Host networking is used because existing NFS connections can break otherwise, so port collisions on the health endpoint should be considered. Broad tolerations place the pod on tainted infrastructure nodes too.

## Test Signals
Validate that every node has a ready daemon pod, kubelet reports the CSI driver in `CSINode`, and `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` exists. Mount a PVC on multiple nodes, restart a daemon pod, and verify workloads keep or recover NFS mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-snapshot-controller.yaml

## Purpose
Deploys the external CSI snapshot controller in `kube-system` for the v4.12.0 manifest set. It provides the cluster-level control loop that binds `VolumeSnapshot` and `VolumeSnapshotContent` objects.

## Important APIs, Types, And Objects
The Deployment runs two replicas of `registry.k8s.io/sig-storage/snapshot-controller:v8.3.0` with `--leader-election=true` and leader election in `$(POD_NAMESPACE)`. It has `minReadySeconds: 15`, rolling update settings of `maxSurge: 0` and `maxUnavailable: 1`, Linux node selection, cluster-critical priority, runtime-default seccomp, and control-plane tolerations.

## Control Flow
After the snapshot CRDs exist, the controller watches snapshot API objects and drives binding, status, and content lifecycle. Only the elected replica actively reconciles. The controller coordinates with CSI snapshotter sidecars, which perform CSI calls against specific drivers such as `nfs.csi.k8s.io`.

## State And Persistence Behavior
The controller persists progress by updating Kubernetes snapshot resources and status subresources. Leader election state is stored in Leases. The Deployment pods have no durable local storage.

## Dependencies And Integration Points
Requires `crd-csi-snapshot.yaml` and `rbac-snapshot-controller.yaml`. It integrates with `VolumeSnapshotClass` resources, `VolumeSnapshot` requests, `VolumeSnapshotContent` binding, and the per-driver snapshotter sidecar in `csi-nfs-controller.yaml`.

## Risks And Edge Cases
If CRDs are missing, comments note the controller may fail readiness or exit quickly, so rollout order matters. Two replicas require correct RBAC for leader election. Because this is a shared cluster controller, changing it can affect snapshots for all CSI drivers, not just NFS.

## Test Signals
Check deployment availability, leader-election Lease updates, and events on snapshot objects. Create a PVC snapshot and confirm `VolumeSnapshotContent` creation, bound status, `readyToUse`, and deletion behavior according to the class policy.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-csi-nfs.yaml

## Purpose
Defines service accounts and cluster RBAC used by the NFS CSI controller and node components in the v4.12.0 deployment set.

## Important APIs, Types, And Objects
Creates `csi-nfs-controller-sa` and `csi-nfs-node-sa` in `kube-system`. `nfs-external-provisioner-role` allows PV create/patch/delete, PVC get/list/watch/update, StorageClass reads, snapshot object reads and content/status updates, event writes, CSINode/node reads, Lease leader election, and Secret get. `nfs-external-resizer-role` allows PV/PVC reads, PV update/patch, PVC status update/patch, events, and Leases. Both ClusterRoles bind to `csi-nfs-controller-sa`.

## Control Flow
The controller Deployment uses these permissions for its sidecars. Provisioner permissions support dynamic PV lifecycle; resizer permissions support PVC expansion status; snapshot permissions let the snapshotter coordinate `VolumeSnapshotContent`; Lease permissions enable leader election.

## State And Persistence Behavior
RBAC objects are durable cluster policy. They do not store driver runtime state, but they gate all API mutations that the controller sidecars need to persist PVs, PVC status, snapshot content status, events, and election Leases.

## Dependencies And Integration Points
Tied directly to `serviceAccountName: csi-nfs-controller-sa` in the controller Deployment and `serviceAccountName: csi-nfs-node-sa` in the node DaemonSet. Snapshot permissions depend on snapshot CRDs being installed.

## Risks And Edge Cases
The controller account has broad cluster-level write access to PVs and snapshot contents plus read access to Secrets. The node service account is created but receives no explicit permissions in this file, which is fine if the node pod only needs kubelet/CSI host integration but should be checked against plugin behavior. Missing `update` on PVC status for the provisioner is deliberate because resizer owns status updates.

## Test Signals
Run `kubectl auth can-i --as=system:serviceaccount:kube-system:csi-nfs-controller-sa` checks for PV create, PVC status patch, Lease create/update, and snapshot content status patch. Exercise provisioning, expansion, and snapshot flows while watching for RBAC denial events.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-snapshot-controller.yaml

## Purpose
Provides the service account and RBAC policy for the shared external snapshot controller used by the v4.12.0 NFS CSI deployment.

## Important APIs, Types, And Objects
Creates `snapshot-controller` service account in `kube-system`. The `snapshot-controller-runner` ClusterRole grants reads on PVs, get/list/watch/update on PVCs, event writes, reads on `VolumeSnapshotClass`, full create/get/list/watch/update/delete/patch on `VolumeSnapshotContent`, patch on content status, get/list/watch/update/patch/create on `VolumeSnapshot`, and update/patch on snapshot status. A namespaced Role grants Lease operations for leader election.

## Control Flow
The snapshot controller Deployment uses these permissions to reconcile snapshot requests, create or delete content objects, update statuses, and coordinate active replicas through Leases.

## State And Persistence Behavior
The RBAC policy is durable cluster configuration. It enables the controller to persist snapshot lifecycle state in CR objects and write events; the policy itself has no runtime storage.

## Dependencies And Integration Points
Requires snapshot CRDs to make the referenced resources meaningful. Integrates with `csi-snapshot-controller.yaml`, `VolumeSnapshotClass`, per-driver CSI snapshotter sidecars, and PVC/PV resources used as snapshot sources.

## Risks And Edge Cases
This is cluster-wide snapshot authority, so misbinding or accidental changes can impact all CSI drivers. The leader-election Role includes Lease delete, which is broader than minimal update-only election in some deployments. If applied before CRDs, RBAC can exist but controller startup still depends on API discovery.

## Test Signals
Use `kubectl auth can-i` for content create/delete, snapshot status patch, and Lease update as the snapshot-controller account. Integration tests should verify dynamic snapshot creation, pre-provisioned content binding, status updates, and deletion policy handling.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/snapshotclass.yaml

## Purpose
Defines a `VolumeSnapshotClass` named `csi-nfs-snapclass` for snapshots handled by the NFS CSI driver.

## Important APIs, Types, And Objects
The class uses `apiVersion: snapshot.storage.k8s.io/v1`, `driver: nfs.csi.k8s.io`, and `deletionPolicy: Delete`. It has no parameters, so behavior is entirely driver default behavior plus the delete policy.

## Control Flow
Users reference this class from `VolumeSnapshot.spec.volumeSnapshotClassName`. The snapshot controller and CSI snapshotter use the driver field to route snapshot operations to the NFS CSI controller plugin.

## State And Persistence Behavior
The class is a persistent cluster-scoped configuration object. Snapshot contents created through it inherit deletion behavior, but the class itself does not store snapshot runtime status.

## Dependencies And Integration Points
Requires snapshot CRDs, snapshot controller RBAC/deployment, the CSI snapshotter sidecar, and a driver identity matching `nfs.csi.k8s.io`.

## Risks And Edge Cases
`deletionPolicy: Delete` means deleting the Kubernetes snapshot content is expected to delete the backing snapshot. That is convenient for cleanup but risky for retention workflows. Without parameters, any required backend-specific options must come from driver defaults.

## Test Signals
Create a `VolumeSnapshot` using this class, confirm it binds to a `VolumeSnapshotContent` with driver `nfs.csi.k8s.io`, then delete the snapshot and verify expected backing cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.0/storageclass.yaml

## Purpose
Defines a sample Kubernetes `StorageClass` named `nfs-csi` for dynamic provisioning through the NFS CSI driver.

## Important APIs, Types, And Objects
The class sets `provisioner: nfs.csi.k8s.io`, `parameters.server: nfs-server.default.svc.cluster.local`, `parameters.share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, `allowVolumeExpansion: true`, and mount option `nfsvers=4.1`. Comments show optional provisioner secret parameters for mount options during `DeleteVolume`.

## Control Flow
PVCs referencing this class are picked up by the CSI provisioner sidecar, which calls the NFS CSI controller plugin to create a subdirectory or backing path under the configured share. Kubelet/node plugin later mounts the NFS export into pods using the declared mount option.

## State And Persistence Behavior
The StorageClass is durable cluster configuration. PVs dynamically created from it persist their NFS volume handle and reclaim behavior; actual data persists on the configured NFS server/share.

## Dependencies And Integration Points
Depends on a reachable NFS service at `nfs-server.default.svc.cluster.local`, the controller Deployment, node DaemonSet, RBAC, and `CSIDriver` identity. Expansion depends on the resizer sidecar and driver support.

## Risks And Edge Cases
The server value is an example default and may not exist in production. `reclaimPolicy: Delete` can remove backing data when PVCs are deleted. `Immediate` binding may provision before pod scheduling constraints are known. NFS v4.1 must be supported by the server and nodes.

## Test Signals
Create a PVC with this class, verify PV provisioning and pod mount success, write data through the mount, expand the PVC, and delete the PVC to confirm reclaim behavior on the NFS share.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.0/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/crd-csi-snapshot.yaml

## Purpose
Installs the same CSI snapshot API CRDs used by the v4.12.1 NFS CSI deployment. It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` in the `snapshot.storage.k8s.io` API group.

## Important APIs, Types, And Objects
`VolumeSnapshot` is namespaced and supports PVC-backed dynamic snapshots or binding to existing `VolumeSnapshotContent`. `VolumeSnapshotClass` is cluster-scoped and requires `driver` and `deletionPolicy`. `VolumeSnapshotContent` is cluster-scoped and requires `deletionPolicy`, `driver`, `source`, and `volumeSnapshotRef`. The `v1` versions are served/storage; deprecated `v1beta1` versions are declared but not served or stored.

## Control Flow
Apply this before snapshot controller and class manifests. The API server validates snapshot resources, then the external snapshot controller and per-driver CSI snapshotter reconcile those objects and call the NFS CSI driver where appropriate.

## State And Persistence Behavior
CRDs persist API definitions cluster-wide; snapshot resources created under them persist desired and observed state in etcd. Status subresources hold readiness, restore size, creation time, errors, and binding information.

## Dependencies And Integration Points
Depends on Kubernetes apiextensions v1 and external-snapshotter schema compatibility. Integrates with the v4.12.1 `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, `snapshotclass.yaml`, and `csi-nfs-controller.yaml`.

## Risks And Edge Cases
The beta API is unavailable despite schema presence, so old clients must use `snapshot.storage.k8s.io/v1`. The CRDs are shared infrastructure for all CSI snapshot-capable drivers. Binding correctness requires both `VolumeSnapshot` and `VolumeSnapshotContent` references to match before consumers restore from a snapshot.

## Test Signals
Validate server-side apply, confirm API discovery for all three resources, create both valid and invalid snapshot requests, and ensure the snapshot controller can update status subresources without schema or RBAC errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-controller.yaml

## Purpose
Defines the v4.12.1 `csi-nfs-controller` Deployment. It is functionally the v4.12.0 controller manifest with the NFS plugin image advanced to `nfsplugin:v4.12.1`.

## Important APIs, Types, And Objects
The Deployment runs one host-networked Linux pod using `csi-nfs-controller-sa`. Sidecars are `csi-provisioner:v5.3.0`, `csi-resizer:v1.14.0`, `csi-snapshotter:v8.3.0`, `livenessprobe:v2.17.0`, and `nfsplugin:v4.12.1`. All CSI sidecars communicate through `/csi/csi.sock`.

## Control Flow
Provisioner, resizer, and snapshotter watch Kubernetes storage objects and forward CSI calls over the shared socket to the NFS plugin. The NFS plugin runs privileged, mounts host kubelet pod paths bidirectionally, and exposes health on `localhost:29652`. Leader-election flags coordinate sidecars through namespace Leases.

## State And Persistence Behavior
The Deployment stores no local durable state. Kubernetes PVs, PVC status, snapshot content/status, events, and Leases persist the controller's decisions. The socket is recreated with the pod.

## Dependencies And Integration Points
Requires v4.12.1 RBAC, `CSIDriver`, snapshot CRDs, snapshot controller, and StorageClass/SnapshotClass objects using `nfs.csi.k8s.io`. The image tag is the only source-level change from v4.12.0 in this file.

## Risks And Edge Cases
The same privileged hostPath and hostNetwork risks as v4.12.0 apply. Version skew between sidecars and the v4.12.1 plugin should be validated, especially snapshot and resize calls. Low CPU requests may underrepresent busy controller needs.

## Test Signals
Run provisioning, expansion, snapshot, restore, and delete tests after upgrading from v4.12.0 to verify the plugin-only bump does not change object compatibility. Confirm the running image tag is `v4.12.1` and all sidecars can connect to the socket.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-driverinfo.yaml

## Purpose
Registers `nfs.csi.k8s.io` as a Kubernetes CSI driver for the v4.12.1 manifest set.

## Important APIs, Types, And Objects
The `CSIDriver` disables attach with `attachRequired: false`, declares only `Persistent` lifecycle mode, and sets `fsGroupPolicy: File`.

## Control Flow
Kubernetes control loops use this metadata when scheduling and mounting PVCs provisioned by the NFS CSI driver. No `VolumeAttachment` objects are needed; kubelet works directly with the node plugin after scheduling.

## State And Persistence Behavior
The object is cluster-scoped persistent metadata in etcd. It has no status section and does not hold per-volume runtime state.

## Dependencies And Integration Points
The name must match the controller and node plugin identity, `StorageClass.provisioner`, and `VolumeSnapshotClass.driver`. It complements node-driver-registrar registration in the DaemonSet.

## Risks And Edge Cases
Driver-name mismatch breaks storage and snapshot routing. File fsGroup handling can be costly for large NFS-backed trees. Persistent-only lifecycle excludes inline ephemeral CSI declarations.

## Test Signals
Verify `kubectl get csidriver nfs.csi.k8s.io`, provision a PVC-backed pod without VolumeAttachment creation, and check file ownership behavior for pods with an `fsGroup`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-node.yaml

## Purpose
Defines the v4.12.1 NFS CSI node DaemonSet. It is the per-node runtime responsible for kubelet registration and NFS volume mount/unmount operations.

## Important APIs, Types, And Objects
The DaemonSet runs `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.12.1`. It uses host paths `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/pods`, and `/var/lib/kubelet/plugins_registry`, with bidirectional mount propagation for pod mounts.

## Control Flow
On each Linux node, the NFS plugin serves CSI over `/csi/csi.sock`; the registrar advertises the host socket path to kubelet; kubelet calls the node service to publish volumes for pods. The liveness container checks `localhost:29653`.

## State And Persistence Behavior
The plugin socket and registration files are host-local runtime state. Actual mount state lives in the node mount table and kubelet directories. Kubernetes persists desired scheduling and volume attachment-free volume usage in API objects.

## Dependencies And Integration Points
Requires kubelet's CSI plugin registry, Linux NFS mount support, the v4.12.1 controller, matching `CSIDriver`, and provisioned PVs referencing the NFS CSI driver.

## Risks And Edge Cases
Privileged execution and bidirectional mount propagation remain the main operational risk. Kubelet root path assumptions must match the host. The plugin-only image bump from v4.12.0 should be tested for mount compatibility and upgrade behavior.

## Test Signals
Confirm one ready pod per target node, successful CSI registration in `CSINode`, mount/unmount behavior for workload pods, health endpoint readiness, and node pod rolling update with existing mounted workloads.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-snapshot-controller.yaml

## Purpose
Deploys the shared external snapshot controller for the v4.12.1 NFS CSI bundle.

## Important APIs, Types, And Objects
The Deployment runs two replicas of `snapshot-controller:v8.3.0` in `kube-system`, using service account `snapshot-controller`, leader election, Linux node selection, cluster-critical priority, and runtime-default seccomp. Readiness is delayed by `minReadySeconds: 15`.

## Control Flow
Once CRDs are available, the elected controller reconciles `VolumeSnapshot` and `VolumeSnapshotContent` objects. It updates status and binding state while per-driver snapshotter sidecars invoke CSI snapshot RPCs.

## State And Persistence Behavior
Snapshot state is persisted in Kubernetes custom resources and status subresources. Leader election uses Leases. Pods do not mount durable local storage.

## Dependencies And Integration Points
Requires `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, and snapshot sidecars in CSI driver controller deployments. For NFS, it connects indirectly through `csi-snapshotter:v8.3.0` in the v4.12.1 controller Deployment.

## Risks And Edge Cases
CRD rollout order is critical. As a shared controller, version or RBAC mistakes can affect snapshots cluster-wide. Two replicas depend on Lease permissions and apiserver availability for failover.

## Test Signals
Validate rollout, leader-election Lease churn during pod restart, dynamic snapshot creation, pre-provisioned content binding, status updates, and deletion policy behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-csi-nfs.yaml

## Purpose
Provides RBAC for the NFS CSI controller and node service accounts in the v4.12.1 manifest set.

## Important APIs, Types, And Objects
Creates `csi-nfs-controller-sa` and `csi-nfs-node-sa`. Binds `nfs-external-provisioner-role` and `nfs-external-resizer-role` to the controller account. Provisioner rules cover PV/PVC lifecycle, StorageClass reads, snapshot class/snapshot/content access, events, CSINode/node reads, Lease leader election, and Secret reads. Resizer rules cover PV updates, PVC status updates, events, and Leases.

## Control Flow
CSI sidecars in `csi-nfs-controller.yaml` use these permissions while watching storage API objects and writing reconciled state. The node account is present for the DaemonSet but does not receive additional Kubernetes API permissions here.

## State And Persistence Behavior
The RBAC objects persist as cluster policy and determine which API objects sidecars can mutate. They indirectly permit persistent state changes in PVs, PVC statuses, snapshot content statuses, events, and leader-election Leases.

## Dependencies And Integration Points
Must match the service account names used in controller and node workload manifests. Snapshot permissions rely on snapshot CRDs and are used by the CSI snapshotter sidecar.

## Risks And Edge Cases
Cluster-wide permissions are broad, and Secret read access should be limited to the controller account's actual needs. Missing or changed verbs usually surface as sidecar retry loops and events. The node account may need more permissions if future node plugin behavior starts calling the Kubernetes API directly.

## Test Signals
Run `kubectl auth can-i` checks as `csi-nfs-controller-sa` and execute dynamic provisioning, expansion, snapshot creation, and deletion. Watch sidecar logs for forbidden errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-snapshot-controller.yaml

## Purpose
Defines RBAC for the external snapshot controller in the v4.12.1 bundle.

## Important APIs, Types, And Objects
Creates service account `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and a matching RoleBinding. Rules cover PV/PVC reads and PVC update, event writes, `VolumeSnapshotClass` reads, `VolumeSnapshotContent` full lifecycle and status patch, `VolumeSnapshot` get/list/watch/update/patch/create, snapshot status update/patch, and Lease operations.

## Control Flow
The snapshot controller uses this policy to reconcile snapshot custom resources and coordinate active replicas. It creates or updates content objects, writes status, emits events, and maintains leader-election Leases.

## State And Persistence Behavior
The policy is durable Kubernetes RBAC state. It controls access to persistent snapshot API objects but stores no snapshot runtime data itself.

## Dependencies And Integration Points
References snapshot API resources supplied by `crd-csi-snapshot.yaml` and the service account used by `csi-snapshot-controller.yaml`.

## Risks And Edge Cases
Because the controller is shared, RBAC denial or over-permission affects all CSI snapshot workflows. Lease delete is allowed; ensure that is acceptable under local policy. Applying RBAC without CRDs is syntactically acceptable but does not make the controller usable until discovery succeeds.

## Test Signals
Use `kubectl auth can-i` for snapshot content create/delete, snapshot status update, event create, and Lease update. Then run snapshot lifecycle tests and inspect events/status transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/snapshotclass.yaml

## Purpose
Defines the v4.12.1 `VolumeSnapshotClass` for the NFS CSI driver.

## Important APIs, Types, And Objects
The object is `snapshot.storage.k8s.io/v1`, named `csi-nfs-snapclass`, with `driver: nfs.csi.k8s.io` and `deletionPolicy: Delete`.

## Control Flow
Snapshot requests reference this class to select the NFS CSI snapshotter path. The snapshot controller binds the request and the sidecar calls the NFS CSI controller.

## State And Persistence Behavior
The class persists cluster-wide and influences future snapshot content deletion behavior. It stores configuration only, not per-snapshot status.

## Dependencies And Integration Points
Requires snapshot CRDs/controllers and a matching NFS CSI driver identity. It pairs with the v4.12.1 controller sidecar `csi-snapshotter:v8.3.0`.

## Risks And Edge Cases
The delete policy can remove backend snapshots when snapshot content is deleted. No parameters are set, so there is no manifest-level override for backend-specific snapshot behavior.

## Test Signals
Create and delete a snapshot using this class, then verify content driver fields, ready status, restore behavior, and backend cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.12.1/storageclass.yaml

## Purpose
Provides the sample `nfs-csi` StorageClass for v4.12.1 dynamic NFS CSI provisioning.

## Important APIs, Types, And Objects
The class uses provisioner `nfs.csi.k8s.io`, server `nfs-server.default.svc.cluster.local`, share `/`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, `allowVolumeExpansion: true`, and mount option `nfsvers=4.1`.

## Control Flow
PVCs select this class, the external provisioner calls the v4.12.1 NFS controller, and node plugins mount resulting PVs into pods with NFS v4.1.

## State And Persistence Behavior
StorageClass settings persist cluster-wide. Dynamically provisioned PVs and data on the NFS export are the durable operational state created from this configuration.

## Dependencies And Integration Points
Depends on the NFS server DNS name, NFS export availability, controller/node plugin deployments, RBAC, and the `CSIDriver` object.

## Risks And Edge Cases
The example server may not exist outside a sample cluster. Delete reclaim can remove data, Immediate binding can pre-provision before a pod is scheduled, and expansion requires working driver and NFS backend behavior.

## Test Signals
Provision a PVC, mount it in a pod, validate read/write, expand the claim, and observe PV/backing directory cleanup after deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.12.1/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/crd-csi-snapshot.yaml

## Purpose
Installs the CSI snapshot CRDs for the v4.13.0 NFS CSI deployment bundle. The file defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` under `snapshot.storage.k8s.io`.

## Important APIs, Types, And Objects
The CRDs expose `v1` as the only served and stored API version. Deprecated `v1beta1` schemas remain in the manifest but are not served or stored. `VolumeSnapshot` is namespaced and selects either a PVC source or existing content source. `VolumeSnapshotClass` is cluster-scoped driver policy. `VolumeSnapshotContent` is cluster-scoped backing snapshot state with required policy, driver, source, and snapshot reference fields.

## Control Flow
The apiserver registers these resources and enforces schema validation. The snapshot controller watches and updates them, while the NFS CSI snapshotter performs driver-specific CSI snapshot calls for classes using `nfs.csi.k8s.io`.

## State And Persistence Behavior
CRDs and custom resources are persisted in etcd. Snapshot status subresources carry controller-observed readiness, restore size, errors, creation time, and CSI snapshot handles.

## Dependencies And Integration Points
Used by v4.13.0 `snapshot-controller:v8.4.0` and `csi-snapshotter:v8.4.0`. Also integrates with RBAC, `snapshotclass.yaml`, and any workloads restoring PVCs from snapshots.

## Risks And Edge Cases
Cluster-wide CRD changes require upgrade care. Clients using `v1beta1` will fail because it is not served. Restore consumers must verify bound snapshot/content references before treating a snapshot as valid. The CRD schema must remain compatible with the sidecar versions in the same bundle.

## Test Signals
Run server-side apply validation, API discovery checks, invalid object rejection tests, dynamic snapshot creation, pre-provisioned content binding, and status update verification with the v8.4.0 controller/sidecar.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-controller.yaml

## Purpose
Defines the v4.13.0 NFS CSI controller Deployment. Compared with v4.12.1, it updates CSI sidecars and the NFS plugin and explicitly disables the `VolumeAttributesClass` feature gate for provisioner and resizer sidecars.

## Important APIs, Types, And Objects
Runs one `csi-nfs-controller` pod in `kube-system` with `csi-provisioner:v6.1.0`, `csi-resizer:v2.0.0`, `csi-snapshotter:v8.4.0`, `livenessprobe:v2.17.0`, and `nfsplugin:v4.13.0`. The provisioner uses `--feature-gates=HonorPVReclaimPolicy=true,VolumeAttributesClass=false`; the resizer uses `-feature-gates=VolumeAttributesClass=false`. All sidecars connect to `/csi/csi.sock`.

## Control Flow
The controller plugin serves CSI on the shared socket. Provisioner, resizer, and snapshotter reconcile Kubernetes PVC/PV/VolumeSnapshot resources and call the plugin. The NFS plugin runs privileged with host kubelet pod access and health checks on `localhost:29652`. Leader election is namespace-scoped through Leases.

## State And Persistence Behavior
Local pod state is ephemeral. Persistent outcomes are Kubernetes PVs, PVC status, snapshot content/status, events, and Lease objects, plus NFS backing directories or snapshots created by the plugin.

## Dependencies And Integration Points
Requires the v4.13.0 RBAC, `CSIDriver`, snapshot CRDs, snapshot controller v8.4.0, and storage/snapshot classes using `nfs.csi.k8s.io`. Sidecar major upgrades imply compatibility expectations with the Kubernetes cluster version.

## Risks And Edge Cases
Privileged hostPath and hostNetwork exposure remain significant. `VolumeAttributesClass=false` avoids adopting newer sidecar feature behavior but should be revisited when enabling that Kubernetes feature. Major version bumps of provisioner and resizer can change supported flags or API interactions; dry-run and rollout tests are important.

## Test Signals
Confirm all container images and feature-gate flags in the running pod. Run provisioning, reclaim policy, resize, snapshot, restore, leader-election failover, and upgrade-from-v4.12.1 tests. Watch for sidecar flag parsing failures and forbidden API calls.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-driverinfo.yaml

## Purpose
Registers the v4.13.0 NFS CSI driver identity and capabilities through the Kubernetes `CSIDriver` API.

## Important APIs, Types, And Objects
The `CSIDriver` is named `nfs.csi.k8s.io`, with `attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`.

## Control Flow
Kubernetes skips attach/detach controller work for this driver and relies on kubelet plus the node plugin for volume publishing. The object is consulted for scheduling and mount-time policy.

## State And Persistence Behavior
The object is persistent cluster metadata. It stores no runtime status or volume inventory.

## Dependencies And Integration Points
The name aligns with `StorageClass.provisioner`, `VolumeSnapshotClass.driver`, node-driver-registrar registration, and the plugin-reported CSI name.

## Risks And Edge Cases
Any mismatch in driver naming breaks class routing and kubelet registration. `fsGroupPolicy: File` can affect mount latency or file ownership behavior on large shares. The manifest does not declare ephemeral lifecycle support.

## Test Signals
Verify the `CSIDriver` object, mount a PVC-backed pod without `VolumeAttachment`, and test `fsGroup` behavior on mounted NFS files after v4.13.0 rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-node.yaml

## Purpose
Defines the v4.13.0 per-node NFS CSI DaemonSet. It registers the driver with kubelet and performs node-side mount operations for NFS CSI volumes.

## Important APIs, Types, And Objects
The containers are `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.13.0`. The pod uses host networking, `system-node-critical` priority, broad tolerations, runtime-default seccomp, and host paths for plugin socket, pods, and plugin registry.

## Control Flow
The NFS plugin serves CSI at `/csi/csi.sock`, the registrar exposes `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` to kubelet, and kubelet invokes node publish/unpublish operations as pods consume PVCs. Health is probed on `localhost:29653`.

## State And Persistence Behavior
Host socket/registration files and mount table entries are node-local runtime state. Kubernetes persists workload and PV references; NFS data persists on the configured server. DaemonSet rolling update allows one unavailable node pod at a time.

## Dependencies And Integration Points
Depends on kubelet CSI registration paths, Linux NFS utilities, the matching controller version, `CSIDriver`, and PVs provisioned by `nfs.csi.k8s.io`.

## Risks And Edge Cases
Privileged mount operations and bidirectional `/var/lib/kubelet/pods` propagation are required but sensitive. Health endpoint collisions are possible with host networking. Custom kubelet roots require manifest changes. Upgrade from v4.12.x should verify existing mounts survive node pod replacement.

## Test Signals
Check DaemonSet readiness across nodes, `CSINode` registration, socket presence, mount/unmount behavior, rolling update behavior with active pods, and liveness probe stability.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-snapshot-controller.yaml

## Purpose
Deploys the v8.4.0 external snapshot controller for the v4.13.0 NFS CSI bundle.

## Important APIs, Types, And Objects
The Deployment runs two `snapshot-controller:v8.4.0` replicas using service account `snapshot-controller`, leader election, `minReadySeconds: 15`, rolling update with `maxSurge: 0` and `maxUnavailable: 1`, Linux scheduling, cluster-critical priority, and runtime-default seccomp.

## Control Flow
The elected snapshot controller reconciles snapshot CRDs, creates/binds `VolumeSnapshotContent`, updates statuses, and coordinates with driver-specific CSI snapshotter sidecars such as the v8.4.0 sidecar in the NFS controller.

## State And Persistence Behavior
The controller writes persistent state to snapshot custom resources, statuses, events, and leader-election Leases. Pods have no durable local storage.

## Dependencies And Integration Points
Requires the snapshot CRDs and snapshot-controller RBAC. It should be version-compatible with `csi-snapshotter:v8.4.0` in the v4.13.0 controller deployment.

## Risks And Edge Cases
Startup depends on the v1 CRDs being available. The shared controller affects all CSI drivers in the cluster. Version upgrades from v8.3.0 should be checked for CRD and RBAC compatibility.

## Test Signals
Verify deployment rollout, leader election across two replicas, snapshot creation/deletion with NFS, and status updates after controller pod restarts. Compare behavior against v4.12.x before upgrade.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-csi-nfs.yaml

## Purpose
Defines NFS CSI service accounts and controller RBAC for the v4.13.0 manifests.

## Important APIs, Types, And Objects
Creates `csi-nfs-controller-sa` and `csi-nfs-node-sa`. The provisioner ClusterRole grants PV lifecycle writes, PVC updates, StorageClass reads, snapshot class/snapshot reads, snapshot content/status updates, event writes, CSINode/node reads, Lease operations, and Secret reads. The resizer ClusterRole grants PV update/patch, PVC and PVC status access, events, and Leases. Both bind to the controller service account.

## Control Flow
Updated v4.13.0 sidecars use these permissions to watch and mutate Kubernetes storage objects while reconciling provisioning, expansion, reclaim, snapshots, events, and election.

## State And Persistence Behavior
RBAC resources persist cluster policy. They authorize the controller to write durable Kubernetes storage and snapshot state but do not hold runtime state themselves.

## Dependencies And Integration Points
Must match service account names in `csi-nfs-controller.yaml` and `csi-nfs-node.yaml`. Snapshot-related rules require snapshot CRDs and are used by `csi-snapshotter:v8.4.0`.

## Risks And Edge Cases
The same broad controller permissions from v4.12.x remain, including Secret get. Sidecar major version bumps in v4.13.0 should be checked against RBAC requirements; missing new permissions would appear as forbidden errors. The node service account remains unbound to explicit roles.

## Test Signals
Run `kubectl auth can-i` for all key provisioner/resizer/snapshotter operations as `csi-nfs-controller-sa`. Execute PVC create/delete, expansion, snapshot creation, and reclaim tests under v4.13.0 sidecars.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-snapshot-controller.yaml

## Purpose
Provides RBAC for the v8.4.0 external snapshot controller used by the v4.13.0 bundle.

## Important APIs, Types, And Objects
Creates `snapshot-controller` service account, a cluster role for snapshot reconciliation, a cluster role binding, and a namespaced leader-election Role/RoleBinding. Permissions include PV/PVC reads, PVC update, event writes, snapshot class reads, full snapshot content lifecycle with status patch, snapshot object create/update/patch/read, snapshot status update/patch, and Lease operations.

## Control Flow
The snapshot controller uses these permissions to watch snapshot resources, create and bind content objects, update status, emit events, and coordinate two replicas with leader election.

## State And Persistence Behavior
RBAC is durable cluster state. It enables writes to snapshot resources and Leases but stores no snapshot runtime data directly.

## Dependencies And Integration Points
Requires snapshot CRDs and is consumed by `csi-snapshot-controller.yaml`. It coordinates with per-driver snapshotter sidecars, including the NFS v4.13.0 controller's snapshotter.

## Risks And Edge Cases
Cluster-wide snapshot permissions affect all CSI drivers. The RBAC appears unchanged from v4.12.x while the controller image moves to v8.4.0, so compatibility should be verified. Leader election includes Lease delete permission.

## Test Signals
Use auth checks for snapshot content lifecycle, snapshot status patch, event write, and Lease update/delete. Run snapshot lifecycle tests with controller failover and inspect for forbidden errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/snapshotclass.yaml

## Purpose
Defines the v4.13.0 NFS CSI `VolumeSnapshotClass`.

## Important APIs, Types, And Objects
The class is named `csi-nfs-snapclass`, uses driver `nfs.csi.k8s.io`, and sets `deletionPolicy: Delete`.

## Control Flow
`VolumeSnapshot` objects select this class to route snapshot operations to the NFS CSI driver through the snapshot controller and CSI snapshotter.

## State And Persistence Behavior
The class persists as cluster configuration and controls deletion behavior for content created through it. Per-snapshot state lives in `VolumeSnapshot` and `VolumeSnapshotContent` objects.

## Dependencies And Integration Points
Depends on snapshot CRDs, the v8.4.0 snapshot controller/sidecar stack, and NFS CSI driver identity matching `nfs.csi.k8s.io`.

## Risks And Edge Cases
Delete policy can remove backing snapshots when Kubernetes snapshot content is deleted. No parameters are set, so all behavior beyond deletion policy is driver default behavior.

## Test Signals
Create, restore, and delete a snapshot with this class; verify content driver, ready status, and backend deletion semantics under v4.13.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.13.0/storageclass.yaml

## Purpose
Defines the v4.13.0 sample `nfs-csi` StorageClass for dynamic provisioning through the NFS CSI driver.

## Important APIs, Types, And Objects
The class uses `provisioner: nfs.csi.k8s.io`, server `nfs-server.default.svc.cluster.local`, share `/`, reclaim policy `Delete`, immediate binding, volume expansion enabled, and mount option `nfsvers=4.1`.

## Control Flow
PVCs referencing this class are reconciled by `csi-provisioner:v6.1.0`, which calls the v4.13.0 NFS controller. Pods mount the resulting PVs through node plugins using NFS v4.1.

## State And Persistence Behavior
The class is durable cluster configuration. Created PVs persist volume handles and reclaim behavior; data persists on the configured NFS export until deleted by reclaim/driver behavior.

## Dependencies And Integration Points
Requires a reachable NFS server at the configured DNS name, v4.13.0 controller/node deployments, RBAC, and `CSIDriver`. Expansion relies on `csi-resizer:v2.0.0` and driver support.

## Risks And Edge Cases
The server/share are sample values and can accidentally point to a broad root export. Delete reclaim can remove data. Immediate binding may not suit topology-sensitive clusters. NFS v4.1 support must be present on client nodes and server.

## Test Signals
Provision and mount a PVC, verify read/write and mount options, expand the PVC, delete the claim, and confirm expected cleanup on the NFS share after the v4.13.0 upgrade.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.0/storageclass.yaml -->
