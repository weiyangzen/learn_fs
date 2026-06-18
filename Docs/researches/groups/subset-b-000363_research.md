# Research: subset-b-000363

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-node.yaml

## Purpose
Deploys the Linux node-side CSI NFS plugin as a `kube-system` `DaemonSet` for release v4.7.0. It registers `nfs.csi.k8s.io` with kubelet on every tolerated node and runs the NFS CSI node service, node-driver-registrar, and liveness sidecar.

## Important APIs, Types, and Functions
The Kubernetes objects are `apps/v1` `DaemonSet`, hostPath volumes for `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and `/var/lib/kubelet/pods`, plus containers `liveness-probe`, `node-driver-registrar`, and `nfs`. Sidecar images are `livenessprobe:v2.13.1` and `csi-node-driver-registrar:v2.11.1`; the driver image is `registry.k8s.io/sig-storage/nfsplugin:v4.7.0`.

## Control Flow, State, and Persistence
Kubernetes schedules one pod per node with `hostNetwork: true`, `ClusterFirstWithHostNet`, broad tolerations, and `system-node-critical` priority. The driver listens on `/csi/csi.sock`, the registrar publishes that socket to kubelet through `/registration`, and the liveness probe exposes health on localhost port `29653`. Persistent state is host-mounted kubelet plugin registration and pod mount state; the DaemonSet itself uses rolling updates with `maxUnavailable: 1`.

## Dependencies and Integration Points
This manifest integrates with kubelet CSI plugin discovery, kubelet pod volume mount directories, Linux NFS mount support, Kubernetes liveness probing, and the controller/RBAC manifests that create the `csi-nfs-node-sa` service account. The NFS container is privileged and adds `SYS_ADMIN` because mount propagation and NFS operations require host-level mount privileges.

## Risks and Test Signals
Risks include privileged node workload blast radius, dependence on Linux-only host paths, plugin socket path mismatches, hostNetwork policy constraints, and broken mounts if bidirectional propagation is unavailable. Signals are successful DaemonSet rollout, registered `CSINode` driver entries, healthy liveness endpoint on `29653`, kubelet plugin registration success, and successful PVC mount/unmount operations on multiple nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-snapshot-controller.yaml

## Purpose
Deploys the external snapshot-controller for CSI snapshot reconciliation in `kube-system`. It is independent of the NFS plugin pod but required for `VolumeSnapshot` and `VolumeSnapshotContent` control loops.

## Important APIs, Types, and Functions
The file defines an `apps/v1` `Deployment` named `snapshot-controller` with two replicas, image `registry.k8s.io/sig-storage/snapshot-controller:v8.0.1`, leader election enabled, and leader election namespace `kube-system`. It uses service account `snapshot-controller` and `system-cluster-critical` priority.

## Control Flow, State, and Persistence
Two replicas are rolled with `maxSurge: 0`, `maxUnavailable: 1`, and `minReadySeconds: 15`, allowing only one active reconciler through leader election. The controller watches snapshot CRDs and persists desired/observed snapshot state through Kubernetes API objects, not local disk. Readiness depends on v1 snapshot CRDs being installed.

## Dependencies and Integration Points
It depends on snapshot CRDs, the RBAC in `rbac-snapshot-controller.yaml`, Kubernetes lease objects for leader election, and CSI snapshotter sidecars running with CSI drivers. It tolerates common control-plane taints so it can run on master/control-plane nodes.

## Risks and Test Signals
Risks include missing CRDs, insufficient snapshot RBAC, leader election namespace issues, and split-brain or downtime if replicas cannot acquire leases. Signals are available deployment replicas, a current leader lease, no CRD discovery errors, and successful reconciliation of `VolumeSnapshot` status fields.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-csi-nfs.yaml

## Purpose
Defines service accounts and cluster-wide permissions needed by the CSI NFS controller and node components for dynamic provisioning, snapshot sidecar interaction, event emission, node discovery, and leader election.

## Important APIs, Types, and Functions
The file creates `ServiceAccount` objects `csi-nfs-controller-sa` and `csi-nfs-node-sa` in `kube-system`, a `ClusterRole` named `nfs-external-provisioner-role`, and a `ClusterRoleBinding` named `nfs-csi-provisioner-binding`. Rules cover PVs, PVCs, storage classes, snapshot classes/snapshots/contents/status, events, CSINodes, nodes, leases, and read-only secrets.

## Control Flow, State, and Persistence
The controller service account is bound to provisioner permissions. Runtime state is Kubernetes API state: PV/PVC create-update-delete operations, snapshot content status patches, event writes, and lease objects for leader election. The node service account is created here but does not receive a binding in this file.

## Dependencies and Integration Points
This RBAC is consumed by `csi-nfs-controller` deployments and must match sidecar permissions for `csi-provisioner` and `csi-snapshotter`. Secret `get` supports CSI sidecar secret references, while lease permissions support leader-elected controllers.

## Risks and Test Signals
Risks include over-broad cluster permissions, missing verbs for newer sidecar versions, stale snapshot API group permissions, and namespace mismatches in bindings. Signals are clean startup of provisioner/snapshotter sidecars, no RBAC forbidden events, successful PV provisioning/deletion, and successful snapshot content status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-snapshot-controller.yaml

## Purpose
Provides RBAC for the external snapshot-controller. It allows the controller to bind snapshots to contents, update snapshot statuses, emit events, and coordinate leader election.

## Important APIs, Types, and Functions
The file creates service account `snapshot-controller`, cluster role `snapshot-controller-runner`, cluster role binding `snapshot-controller-role`, namespace role `snapshot-controller-leaderelection`, and role binding of the same name. Rules cover PV/PVC reads, PVC update, event creation/update/patch, snapshot class reads, snapshot content CRUD/status patch, snapshot read/update/patch, snapshot status update/patch, and coordination leases in `kube-system`.

## Control Flow, State, and Persistence
The snapshot-controller watches snapshot API objects and writes binding and status state through the permissions granted here. Leader election is scoped to `kube-system` leases, while resource reconciliation is cluster-scoped for snapshot content objects and namespaced for snapshots/PVCs.

## Dependencies and Integration Points
It pairs with `csi-snapshot-controller.yaml` and the snapshot CRDs. It also coordinates with CSI driver snapshotter sidecars that create or update `VolumeSnapshotContent` objects.

## Risks and Test Signals
Risks include missing status verbs causing stuck snapshots, overly broad delete access to snapshot contents, and role binding namespace mismatches. Signals are absence of `forbidden` logs in snapshot-controller, lease acquisition in `kube-system`, and snapshots progressing to bound/ready states.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/storageclass.yaml

## Purpose
Provides an example `StorageClass` named `nfs-csi` for dynamic provisioning through `nfs.csi.k8s.io`.

## Important APIs, Types, and Functions
The object is `storage.k8s.io/v1` `StorageClass` with `provisioner: nfs.csi.k8s.io`, parameters `server: nfs-server.default.svc.cluster.local` and `share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and mount option `nfsvers=4.1`. Commented secret parameters show how DeleteVolume mount options can be supplied.

## Control Flow, State, and Persistence
PVCs referencing this class trigger the external provisioner to call `CreateVolume`, which creates a subdirectory on the configured NFS share. The reclaim policy asks the driver to remove the directory on PV deletion unless driver-specific `onDelete` behavior overrides it.

## Dependencies and Integration Points
It integrates with the CSI NFS controller, the NFS service named in `server`, Kubernetes storage class admission/defaulting, and mount option handling in node/controller publish paths.

## Risks and Test Signals
Risks include placeholder server/share values being used unchanged, immediate binding before workload scheduling, NFS version incompatibility, and destructive delete semantics. Signals are a bound PVC, a PV with `nfs.csi.k8s.io`, a created subdirectory on the share, and successful pod mount using NFSv4.1.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/crd-csi-snapshot.yaml

## Purpose
Installs the CSI snapshot API CRDs required by the snapshot-controller and CSI snapshotter sidecars. It defines the Kubernetes API surface for `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass` in group `snapshot.storage.k8s.io`.

## Important APIs, Types, and Functions
The file contains `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects with generated OpenAPI v3 schemas, printer columns, `status` subresources, and version blocks. `VolumeSnapshot` is namespaced and models user snapshot requests from a PVC or pre-existing content. `VolumeSnapshotContent` is cluster-scoped and models the physical snapshot handle, driver, source, deletion policy, class, reference, and status. `VolumeSnapshotClass` is cluster-scoped and carries driver parameters and deletion policy.

## Control Flow, State, and Persistence
The API server persists snapshot desired state and status. The v1 versions are served and storage versions; v1beta1 versions are present for compatibility and deprecation warnings, with some v1beta1 content marked unserved/non-storage. Snapshot controllers update status subresources, while users and sidecars create spec objects according to the schema's immutability and required-field constraints.

## Dependencies and Integration Points
The CRDs are consumed by `snapshot-controller`, `csi-snapshotter`, storage provisioners, and applications that restore PVCs from snapshots. They encode CSI fields such as snapshot handles, volume handles, restore size, ready-to-use state, deletion policy, and driver names.

## Risks and Test Signals
Risks include CRD version skew with snapshot-controller v8 sidecars, stale v1beta1 clients, missing status subresource permissions, and schema validation rejecting older manifests. Signals are successful CRD establishment, discovery of `snapshot.storage.k8s.io/v1`, snapshot-controller readiness, accepted `VolumeSnapshotClass` objects, and status updates on created snapshots.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-controller.yaml

## Purpose
Deploys the CSI NFS controller pod for v4.8.0. It runs the external provisioner, CSI snapshotter, liveness probe, and NFS CSI controller service in one `kube-system` deployment.

## Important APIs, Types, and Functions
The `apps/v1` `Deployment` `csi-nfs-controller` has one replica, service account `csi-nfs-controller-sa`, host networking, control-plane tolerations, and `system-cluster-critical` priority. Containers are `csi-provisioner:v5.0.2`, `csi-snapshotter:v8.0.1`, `livenessprobe:v2.13.1`, and `nfsplugin:v4.8.0`. The controller socket is `/csi/csi.sock`; liveness is on localhost port `29652`.

## Control Flow, State, and Persistence
The sidecars connect to the shared CSI socket and issue `CreateVolume`, `DeleteVolume`, `CreateSnapshot`, and related controller RPCs. The NFS container is privileged and mounts NFS shares internally to create/delete directories and snapshot archives. The pod uses `emptyDir` for the CSI socket and hostPath `/var/lib/kubelet/pods` with bidirectional propagation for mount visibility.

## Dependencies and Integration Points
It depends on RBAC from `rbac-csi-nfs.yaml`, snapshot CRDs/RBAC for snapshot flows, Linux NFS mount tools, kube-system leader election leases, and matching sidecar capabilities. Host networking is used because the controller also mounts NFS to create directories.

## Risks and Test Signals
Risks include privileged controller execution, long sidecar timeouts masking slow NFS behavior, leader election/RBAC mismatch, hostNetwork policy restrictions, and socket/container ordering issues. Signals are healthy liveness on `29652`, provisioner and snapshotter leaders elected, successful PVC provisioning, and snapshot archives created under the configured share.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-driverinfo.yaml

## Purpose
Registers cluster-level metadata for the NFS CSI driver using a `CSIDriver` object.

## Important APIs, Types, and Functions
The `storage.k8s.io/v1` `CSIDriver` is named `nfs.csi.k8s.io`, sets `attachRequired: false`, declares `volumeLifecycleModes: [Persistent]`, and sets `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
The object is read by Kubernetes storage components to decide attach behavior and fsGroup handling. Because NFS does not need a block-device attach phase, the attach/detach controller can skip controller publish flows.

## Dependencies and Integration Points
It integrates with kubelet, external provisioner behavior, pod security context fsGroup application, and the driver name returned by CSI identity APIs.

## Risks and Test Signals
Risks include driver name mismatch, unsupported lifecycle modes for ephemeral use, and fsGroup behavior surprises on NFS permissions. Signals are discovery of the `CSIDriver` object, PVs referencing the same driver name, and pod volume setup without attach operations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-node.yaml

## Purpose
Deploys the node-side CSI NFS plugin as a v4.8.0 `DaemonSet`, registering the driver with kubelet and performing node publish/unpublish mount operations.

## Important APIs, Types, and Functions
The manifest defines `csi-nfs-node` in `kube-system` with containers `liveness-probe`, `node-driver-registrar`, and `nfs`. It uses `livenessprobe:v2.13.1`, `csi-node-driver-registrar:v2.11.1`, and `nfsplugin:v4.8.0`. Important paths are `/csi/csi.sock`, `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, `/var/lib/kubelet/plugins_registry`, and `/var/lib/kubelet/pods`.

## Control Flow, State, and Persistence
The DaemonSet runs on all Linux nodes with broad tolerations and host networking. The registrar performs kubelet registration through the host plugin registry, while the privileged NFS container handles mount operations with `SYS_ADMIN` and bidirectional pod mount propagation. HostPath directories persist socket registration and mount state across pod restarts.

## Dependencies and Integration Points
It depends on kubelet CSI plugin registration, Linux NFS client support, service account creation in RBAC manifests, and the `CSIDriver` object. The health endpoint on port `29653` is probed by the liveness sidecar and Kubernetes.

## Risks and Test Signals
Risks include privileged node access, stale plugin sockets, incorrect registration path, missing hostPath directories, and NFS mount propagation failures. Signals are ready DaemonSet pods, successful kubelet registration, `CSINode` driver entries, healthy liveness probes, and successful pod-level NFS volume mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-snapshot-controller.yaml

## Purpose
Deploys snapshot-controller v8.0.1 for CSI snapshot API reconciliation in clusters using the v4.8.0 NFS driver manifests.

## Important APIs, Types, and Functions
The `apps/v1` `Deployment` named `snapshot-controller` runs two replicas in `kube-system`, uses service account `snapshot-controller`, enables leader election in `kube-system`, and uses image `registry.k8s.io/sig-storage/snapshot-controller:v8.0.1`.

## Control Flow, State, and Persistence
The deployment uses rolling updates with no surge and one unavailable replica, plus `minReadySeconds: 15` so CRD discovery failures surface before readiness. State lives in snapshot CRDs and leader-election leases rather than local storage.

## Dependencies and Integration Points
It depends on snapshot CRDs from `crd-csi-snapshot.yaml` and permissions from `rbac-snapshot-controller.yaml`. It coordinates with NFS controller `csi-snapshotter` sidecar operations for creating and deleting CSI snapshots.

## Risks and Test Signals
Risks include CRDs not installed before startup, RBAC gaps, control-plane scheduling restrictions, and leader election problems. Signals are available replicas, current lease ownership, no CRD discovery errors, and snapshots reaching ready status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-csi-nfs.yaml

## Purpose
Creates the service accounts and cluster permissions needed by the v4.8.0 CSI NFS controller-side sidecars and node service account.

## Important APIs, Types, and Functions
Objects include service accounts `csi-nfs-controller-sa` and `csi-nfs-node-sa`, `ClusterRole` `nfs-external-provisioner-role`, and `ClusterRoleBinding` `nfs-csi-provisioner-binding`. The role grants PV CRUD, PVC read/update, storage class read, snapshot object reads and content status updates, event writes, CSINode/node reads, lease CRUD, and secret reads.

## Control Flow, State, and Persistence
The external provisioner and snapshotter use these permissions while reconciling PVs, PVCs, snapshot contents, events, and leader election leases. The node service account is only declared here; node operations mainly rely on kubelet/host privileges in the DaemonSet.

## Dependencies and Integration Points
This RBAC must match `csi-provisioner:v5.0.2`, `csi-snapshotter:v8.0.1`, snapshot CRDs, and the controller deployment namespace. Secret read access supports CSI secret references passed to controller operations.

## Risks and Test Signals
Risks include cluster-wide permission breadth, missing verbs after sidecar upgrades, and service account namespace drift. Signals are sidecars starting without `forbidden` errors, leader election success, PV create/delete success, and snapshot content status patch success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-snapshot-controller.yaml

## Purpose
Grants snapshot-controller v8.0.1 the permissions required to reconcile CSI snapshot API objects.

## Important APIs, Types, and Functions
The file creates service account `snapshot-controller`, cluster role `snapshot-controller-runner`, cluster role binding `snapshot-controller-role`, role `snapshot-controller-leaderelection`, and a role binding in `kube-system`. It grants reads on PV/PVC/snapshot classes, update on PVCs and snapshots, CRUD on snapshot contents, status patch/update on snapshot resources, event writes, and lease CRUD.

## Control Flow, State, and Persistence
The controller watches `VolumeSnapshot` and `VolumeSnapshotContent`, updates binding/status fields, and uses a namespace lease to ensure only one active reconciler. Persistent state is all in Kubernetes API resources.

## Dependencies and Integration Points
It pairs with `csi-snapshot-controller.yaml`, the snapshot CRDs, and CSI snapshotter sidecars running with drivers such as NFS. The permissions are storage-wide and not tied to only NFS snapshots.

## Risks and Test Signals
Risks include stuck snapshots from missing status verbs, accidental delete power over snapshot contents, and lease namespace mismatches. Signals are a healthy leader lease, no RBAC denial events, and snapshots progressing through binding to ready.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.8.0/storageclass.yaml

## Purpose
Provides the v4.8.0 example `StorageClass` for dynamic NFS CSI provisioning.

## Important APIs, Types, and Functions
The `StorageClass` is named `nfs-csi`, uses provisioner `nfs.csi.k8s.io`, sets parameters `server` and `share`, uses `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and mount option `nfsvers=4.1`.

## Control Flow, State, and Persistence
When a PVC references the class, the external provisioner calls the driver controller to create a subdirectory under the configured NFS share. Delete reclaim policy triggers directory cleanup unless driver parameters or defaults choose retain/archive behavior.

## Dependencies and Integration Points
It depends on a real NFS server at the example DNS name or a user-modified value, the NFS CSI controller, node plugin mount support, and optional secret parameters for delete-time mount options.

## Risks and Test Signals
Risks include placeholder configuration, destructive delete semantics, immediate binding before scheduling constraints are known, and NFSv4.1 incompatibility. Signals are a bound PVC/PV, correct PV volume context, directory creation under the share, and a pod successfully mounting the volume.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.8.0/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/crd-csi-snapshot.yaml

## Purpose
Installs the snapshot API CRDs used by the v4.9.0 deployment set. This file is equivalent to the v4.8.0 CRD manifest and defines `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass`.

## Important APIs, Types, and Functions
The CRDs are `apiextensions.k8s.io/v1` resources in API group `snapshot.storage.k8s.io`, with OpenAPI schemas, printer columns, served/storage v1 versions, deprecated v1beta1 compatibility blocks, and `status` subresources. The schemas validate snapshot sources, content references, deletion policies, driver names, restore sizes, readiness, errors, and snapshot handles.

## Control Flow, State, and Persistence
The API server stores snapshot desired state and status. Users create snapshot requests/classes, the snapshot-controller binds snapshots to contents, and CSI snapshotter sidecars update physical snapshot status through the API. The CRD schemas are the durable contract for these objects.

## Dependencies and Integration Points
They integrate with snapshot-controller v8.0.1, CSI snapshotter v8.0.1, Kubernetes CRD discovery/admission, and driver-specific snapshot implementations such as NFS tar archive snapshots.

## Risks and Test Signals
Risks include CRD/controller version skew, deprecated v1beta1 clients, validation incompatibilities, and missing status RBAC. Signals are established CRDs, discovery of `snapshot.storage.k8s.io/v1`, accepted snapshot classes, and snapshots with status fields updated by controllers.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-controller.yaml

## Purpose
Deploys the v4.9.0 CSI NFS controller workload. It is the same controller topology as v4.8.0 with the NFS plugin image tag advanced to `v4.9.0`.

## Important APIs, Types, and Functions
The `apps/v1` `Deployment` `csi-nfs-controller` runs `csi-provisioner:v5.0.2`, `csi-snapshotter:v8.0.1`, `livenessprobe:v2.13.1`, and `nfsplugin:v4.9.0`. It uses service account `csi-nfs-controller-sa`, host networking, `system-cluster-critical` priority, Linux node selector, and control-plane tolerations.

## Control Flow, State, and Persistence
Sidecars communicate with the NFS CSI service over `/csi/csi.sock` in an `emptyDir`. Provisioning and snapshot RPCs cause the privileged NFS container to mount NFS shares and mutate directory/archive state. Liveness is served on localhost `29652`; leader election is handled by sidecars in `kube-system`.

## Dependencies and Integration Points
It depends on RBAC for the controller service account, snapshot CRDs/RBAC, Linux NFS client capabilities, Kubernetes lease resources, and the node plugin for actual workload mounts. HostPath `/var/lib/kubelet/pods` is mounted with bidirectional propagation.

## Risks and Test Signals
Risks include privileged controller scope, NFS mount failures from controller nodes, sidecar image/version skew, and hostNetwork restrictions. Signals are successful rollout, healthy liveness endpoint, active provisioner/snapshotter leaders, working PVC create/delete, and snapshot archive creation/restoration.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-driverinfo.yaml

## Purpose
Declares cluster-level CSI driver metadata for `nfs.csi.k8s.io` in the v4.9.0 manifest set.

## Important APIs, Types, and Functions
The file defines a `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, persistent lifecycle mode only, and `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
Kubernetes control-plane and kubelet components read this object to skip attach workflows and apply fsGroup semantics for mounted files where supported. The object persists as cluster configuration.

## Dependencies and Integration Points
It must match the driver name registered by the node DaemonSet and returned by CSI identity. It integrates with PV provisioning, pod volume setup, and security context fsGroup handling.

## Risks and Test Signals
Risks include name mismatch, lack of ephemeral lifecycle declaration, and fsGroup behavior depending on NFS server permissions. Signals include the `CSIDriver` object existing, no attach attempts for NFS PVs, and successful pod volume setup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-node.yaml

## Purpose
Deploys the v4.9.0 node-side NFS CSI driver as a DaemonSet. Compared with v4.8.0, the relevant behavioral change in this manifest is the `nfsplugin:v4.9.0` image tag.

## Important APIs, Types, and Functions
The DaemonSet contains `liveness-probe`, `node-driver-registrar`, and `nfs` containers. It uses host paths for the CSI plugin socket, kubelet plugin registry, and pod mount directory. The NFS container is privileged, adds `SYS_ADMIN`, and listens on `unix:///csi/csi.sock`.

## Control Flow, State, and Persistence
Each Linux node runs a pod with host networking and `system-node-critical` priority. The registrar registers `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` with kubelet. Node publish/unpublish operations mutate host mount state under `/var/lib/kubelet/pods`, while registration data lives under kubelet plugin host paths.

## Dependencies and Integration Points
It integrates with kubelet CSI registration, Linux NFS mounts, the `CSIDriver` object, service account creation, and controller-created PV volume contexts. Liveness probing uses localhost port `29653`.

## Risks and Test Signals
Risks include privileged host access, stale socket or registry state, registration path mismatch, and mount propagation failures. Signals are ready DaemonSet pods, kubelet registration success, healthy liveness probes, and application pods mounting/unmounting NFS PVs cleanly.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-snapshot-controller.yaml

## Purpose
Deploys the external snapshot-controller for the v4.9.0 manifest set. It reconciles CSI snapshot Kubernetes resources independently of the NFS controller pod.

## Important APIs, Types, and Functions
The file defines an `apps/v1` `Deployment` named `snapshot-controller`, two replicas, image `snapshot-controller:v8.0.1`, service account `snapshot-controller`, leader election enabled in `kube-system`, and `system-cluster-critical` priority.

## Control Flow, State, and Persistence
Leader election chooses one active reconciler while two replicas provide availability. The controller watches and updates snapshot CRD objects, with `minReadySeconds: 15` guarding against early readiness when v1 CRDs are unavailable.

## Dependencies and Integration Points
It depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, control-plane scheduling tolerations, and CSI snapshotter sidecars in driver controller pods.

## Risks and Test Signals
Risks include missing CRDs, RBAC denials, leader election failures, and scheduling failures on tainted control-plane nodes. Signals include available replicas, lease ownership, no CRD discovery errors, and successful `VolumeSnapshot` status reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-csi-nfs.yaml

## Purpose
Defines RBAC for the v4.9.0 NFS CSI controller and declares controller/node service accounts.

## Important APIs, Types, and Functions
It creates `csi-nfs-controller-sa`, `csi-nfs-node-sa`, `nfs-external-provisioner-role`, and binding `nfs-csi-provisioner-binding`. The role includes permissions for PV/PVC provisioning, storage class reads, snapshot classes/snapshots/contents/status, event emission, CSINode/node reads, leader-election leases, and secret reads.

## Control Flow, State, and Persistence
The controller sidecars use these verbs to reconcile storage state through the Kubernetes API. Leases persist leader election state, events persist operation feedback, and PV/PVC/snapshot objects persist storage desired and observed state.

## Dependencies and Integration Points
It must match the sidecar versions in `csi-nfs-controller.yaml` and snapshot CRDs. It also supports CSI secret references and Kubernetes node/CSINode discovery.

## Risks and Test Signals
Risks include overbroad cluster privileges, missing verbs for sidecar upgrades, and namespace mismatches. Signals are no RBAC forbidden errors, successful leader election, successful dynamic provisioning, and snapshot content status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-snapshot-controller.yaml

## Purpose
Provides the permissions required by snapshot-controller v8.0.1 in the v4.9.0 manifest set.

## Important APIs, Types, and Functions
The manifest creates the `snapshot-controller` service account, `snapshot-controller-runner` cluster role and binding, plus `snapshot-controller-leaderelection` role and binding in `kube-system`. Rules cover PV/PVC reads, PVC update, event writes, snapshot class reads, snapshot content CRUD/status patch, snapshot update/patch, snapshot status update/patch, and lease CRUD.

## Control Flow, State, and Persistence
The controller uses cluster-level permissions to bind snapshot contents and namespace-scoped lease permissions to elect a single active reconciler. Snapshot object state is persisted in the Kubernetes API through spec/status updates.

## Dependencies and Integration Points
It integrates with the snapshot-controller deployment, snapshot CRDs, and CSI driver snapshotter sidecars. It applies cluster-wide, not just to NFS-related snapshots.

## Risks and Test Signals
Risks include status update denials causing stuck snapshots, broad delete authority on snapshot contents, and wrong namespace for leader-election RBAC. Signals are healthy lease acquisition, no forbidden errors, and snapshots reaching bound/ready status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.9.0/storageclass.yaml

## Purpose
Provides the v4.9.0 example `StorageClass` for NFS CSI dynamic provisioning.

## Important APIs, Types, and Functions
The `StorageClass` `nfs-csi` uses `provisioner: nfs.csi.k8s.io`, parameters `server: nfs-server.default.svc.cluster.local` and `share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, and mount option `nfsvers=4.1`.

## Control Flow, State, and Persistence
PVCs using this class cause the external provisioner to call the NFS CSI controller, which creates a directory under the configured share and records parameters in PV volume context. On deletion, reclaim policy requests cleanup unless driver policy retains or archives.

## Dependencies and Integration Points
It depends on a reachable NFS server, NFS CSI controller and node pods, correct RBAC, and Linux NFS client compatibility with the configured mount options.

## Risks and Test Signals
Risks include example DNS/share values being left unchanged, delete reclaim removing user data, immediate binding limitations, and NFS version mismatch. Signals include bound PVCs, created NFS subdirectories, correct PV driver name, and pod mount success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.9.0/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/boilerplate/boilerplate.py -->
# sources/control-plane/csi-driver-nfs/hack/boilerplate/boilerplate.py

## Purpose
Checks repository files for required Kubernetes license boilerplate headers. It is used by the boilerplate verification script to list files whose header does not match the language-specific template.

## Important APIs, Types, and Functions
The script uses `argparse` options for file names, `--rootdir`, `--boilerplate-dir`, and `--verbose`. Key functions are `get_refs()`, `file_passes()`, `file_extension()`, `normalize_files()`, `get_files()`, `get_regexs()`, and `main()`. Reference templates are loaded from `boilerplate.*.txt` and matched by extension or basename.

## Control Flow, State, and Persistence
It walks the root directory unless explicit file names are provided, prunes skipped directories such as vendor and `.git`, selects files with supported extensions, strips Go build constraints and script shebangs before comparing, normalizes real years to `YEAR`, and prints failing file paths to stdout. It does not mutate the repository.

## Dependencies and Integration Points
It depends only on Python standard library modules and local boilerplate templates. `hack/verify-boilerplate.sh` invokes it with `--rootdir` and `--verbose` and treats any printed path as a failure.

## Risks and Test Signals
Risks include brittle path defaults, missing template keys for unusual extensions, `/dev/null` assumptions for quiet mode, and false failures from new build-tag/shebang shapes. Signals are empty stdout for a clean tree, verbose unified diffs for bad headers, and coverage of Go, shell, Python, Makefile, Dockerfile, and Bazel templates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/release-image.sh -->
# sources/control-plane/csi-driver-nfs/hack/release-image.sh

## Purpose
Publishes CSI NFS container images to an Azure Container Registry-backed release flow and checks the public latest image after a delay.

## Important APIs, Types, and Functions
The script expects one argument, an ACR registry name. It exports `OUTPUT_TYPE=registry`, `REGISTRY_NAME`, `REGISTRY=${REGISTRY_NAME}.azurecr.io`, `IMAGENAME=public/k8s/csi/nfs-csi`, `CI=1`, and `PUBLISH=1`, then runs `az acr login`, `make`, `make container push push-latest`, `docker pull`, and `docker inspect`.

## Control Flow, State, and Persistence
With `set -euo pipefail`, any failing command exits. After publishing it sleeps for 60 seconds, pulls `mcr.microsoft.com/k8s/csi/nfs-csi:latest`, and prints the image creation timestamp from `docker inspect`. Persistent effects are registry writes and local Docker image/cache changes.

## Dependencies and Integration Points
It depends on Azure CLI authentication, Docker, Makefile release targets, Azure Container Registry, and Microsoft Container Registry propagation. It is part of manual or CI release operations rather than normal build verification.

## Risks and Test Signals
Risks include publishing to the wrong registry, credentials leakage through shell environment, unquoted registry variables, propagation delays longer than 60 seconds, and use of mutable `latest`. Signals are successful ACR login, successful make/push targets, a pullable MCR image, and an updated `Created` timestamp.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/release-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-dependencies.sh -->
# sources/control-plane/csi-driver-nfs/hack/update-dependencies.sh

## Purpose
Regenerates Go module dependency pins and vendor contents in a deterministic, Kubernetes-style way.

## Important APIs, Types, and Functions
The script sets `GO111MODULE=on`, clears `GOPATH` and `GOFLAGS`, moves to the git root, and defines `prune-vendor()`, `ensure_require_replace_directives_for_all_dependencies()`, and `group_replace_directives()`. It uses `go mod edit -json`, `jq`, `go list -m -json all`, `go mod tidy`, and `go mod vendor`.

## Control Flow, State, and Persistence
It captures current `require` and `replace` directives, adds replace directives pinning versions, makes indirect dependencies explicit, repeats after `go mod tidy`, groups replace directives into a block, and regenerates `vendor`. It mutates `go.mod`, `go.sum`, and `vendor` content.

## Dependencies and Integration Points
It depends on Go modules, `jq`, `awk`, `xargs`, git root detection, and write access to module/vendor files. `verify-gomod.sh` and `verify-update.sh` detect whether running update scripts leaves uncommitted diffs.

## Risks and Test Signals
Risks include destructive vendor churn, dependency resolver changes across Go versions, `jq` absence, disabled `prune-vendor()` leaving extra files, and temporary directory cleanup not being automatic. Signals are `SUCCESS`, stable `go mod tidy/vendor`, grouped replace directives, and no git diff after expected updates are committed.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-dependencies.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-gofmt.sh -->
# sources/control-plane/csi-driver-nfs/hack/update-gofmt.sh

## Purpose
Applies canonical Go formatting to all non-vendor Go files in the repository.

## Important APIs, Types, and Functions
The script runs `find . -name "*.go" | grep -v "\/vendor\/" | xargs gofmt -s -w` under `set -euo pipefail`.

## Control Flow, State, and Persistence
It recursively locates Go files, excludes vendor paths, and rewrites files in place using simplified formatting. Persistent effects are source file formatting changes.

## Dependencies and Integration Points
It depends on the Go toolchain and is the fixer counterpart to `hack/verify-gofmt.sh`. It is also part of broader update/verification workflows.

## Risks and Test Signals
Risks include xargs behavior with no files, path handling for unusual file names, and formatting generated or unrelated Go files outside intended scope. Signals are no subsequent diff from `verify-gofmt.sh` and expected gofmt-only changes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-gofmt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-gomod.sh -->
# sources/control-plane/csi-driver-nfs/hack/update-gomod.sh

## Purpose
Updates `replace` directives for Kubernetes staging modules to match a specified Kubernetes release.

## Important APIs, Types, and Functions
The script requires a version argument with optional leading `v`, downloads Kubernetes `go.mod` from GitHub, extracts staging module names with `sed`, resolves module versions using `go mod download -json "${MOD}@kubernetes-${VERSION}"`, and writes replacements with `go mod edit`.

## Control Flow, State, and Persistence
It strips `v` from the argument, fails if empty, builds a shell array of `k8s.io/*` module names from the upstream Kubernetes release, then iterates and rewrites `go.mod` replace directives. It mutates only module metadata directly.

## Dependencies and Integration Points
It depends on network access to GitHub and module proxies, Go modules, `curl`, `sed`, and `go mod edit`. It complements dependency update scripts when aligning CSI dependencies with Kubernetes versions.

## Risks and Test Signals
Risks include network or upstream tag failures, unquoted echo/output, module proxy inconsistencies, and partially updated `go.mod` if a later module fails. Signals are replacement lines matching Kubernetes pseudo-versions and successful follow-up `go mod tidy`/`verify-gomod.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/update-gomod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-all.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-all.sh

## Purpose
Runs the main repository verification suite from the git root.

## Important APIs, Types, and Functions
The script computes `PKG_ROOT="$(git rev-parse --show-toplevel)"` and sequentially invokes `verify-gofmt.sh`, `verify-govet.sh`, `verify-yamllint.sh`, `verify-boilerplate.sh`, `verify-helm-chart-files.sh`, `verify-helm-chart.sh`, `verify-helm-chart-index.sh`, and `verify-gomod.sh`.

## Control Flow, State, and Persistence
With `set -euo pipefail`, the first failing verification stops the suite. It mainly checks repository state but some child scripts can install tools or regenerate module/vendor files before diffing.

## Dependencies and Integration Points
It integrates all local CI gates for formatting, vet, YAML, license headers, Helm packaging/index, chart image parity, and Go modules. It depends on the transitive tools required by each child script.

## Risks and Test Signals
Risks include non-hermetic behavior because child scripts may install packages from the network, mutate files before checking diffs, or require cluster-independent tool availability. Signals are all child scripts exiting zero and no unexpected git diff after verification.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-boilerplate.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-boilerplate.sh

## Purpose
Validates that source files have the expected Kubernetes license boilerplate headers.

## Important APIs, Types, and Functions
The script locates Python, installs an alternatives link to python3 if needed, sets `REPO_ROOT`, `boilerDir`, and `boiler`, runs `${boiler} --rootdir=${REPO_ROOT} --verbose`, and reports any returned file paths as failures. It defines a cleanup trap for a temporary `unitTestOut` file.

## Control Flow, State, and Persistence
It executes the Python checker, stores the list of bad files in a shell array, prints each bad path, and exits non-zero if any header is wrong. It does not repair files.

## Dependencies and Integration Points
It depends on `hack/boilerplate/boilerplate.py`, boilerplate templates, Python availability, and shell array handling. `verify-all.sh` includes it in the CI gate.

## Risks and Test Signals
Risks include attempting `update-alternatives` on systems without privileges, unused unit-test temp file plumbing, and path names with whitespace being split by shell arrays. Signals are "Done" with no listed files, or explicit "Boilerplate header is wrong for" messages.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-examples.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-examples.sh

## Purpose
Smoke-tests example Kubernetes workloads that use the NFS CSI driver.

## Important APIs, Types, and Functions
The script defines `rollout_and_wait()`, uses `kubectl apply`, parses applied resource names with `grep`/`awk`, calls `kubectl rollout status` for workload resources, and otherwise waits for readiness. It applies `deploy/example/storageclass-nfs.yaml`, then deployment and statefulset examples, with optional ephemeral daemonset when the first argument contains `ephemeral`.

## Control Flow, State, and Persistence
It applies the example storage class and workloads to the current Kubernetes context, waits up to five minutes per resource in namespace `default`, and leaves created resources in the cluster. Failures exit due to `set -euo pipefail`.

## Dependencies and Integration Points
It depends on a configured cluster, `kubectl`, a working CSI NFS installation, default namespace access, and example manifests. It is an integration smoke test rather than a unit test.

## Risks and Test Signals
Risks include mutating the active cluster, brittle parsing of `kubectl apply` output, namespace assumptions, and no cleanup. Signals are successful rollout/wait completion for deployment, statefulset, and optional ephemeral daemonset examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-examples.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-gofmt.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-gofmt.sh

## Purpose
Checks that all non-vendor Go files are formatted with `gofmt -s`.

## Important APIs, Types, and Functions
The script captures `diff=$(find . -name "*.go" | grep -v "\/vendor\/" | xargs gofmt -s -d 2>&1)` and fails if the diff is non-empty, instructing developers to run `hack/update-gofmt.sh`.

## Control Flow, State, and Persistence
It is read-only: gofmt emits diffs to stdout instead of rewriting. With strict shell options, command failures stop the script. Successful completion prints "No issue found".

## Dependencies and Integration Points
It depends on the Go toolchain and pairs with `update-gofmt.sh`. `verify-all.sh` runs it before vet and other gates.

## Risks and Test Signals
Risks include path handling for unusual names, xargs behavior on empty input, and excluding only paths containing `/vendor/`. Signals are an empty gofmt diff and zero exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-gofmt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-golint.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-golint.sh

## Purpose
Runs legacy golint checks through golangci-lint.

## Important APIs, Types, and Functions
The script checks for `golangci-lint`, installs v1.31.0 with the upstream install script if missing, appends `$(go env GOPATH)/bin` to `PATH`, and runs `golangci-lint run --no-config --enable=golint --disable=typecheck --deadline=10m`.

## Control Flow, State, and Persistence
It may download and install a linter into the Go bin directory, then runs linting across the repository. The script exits on the first failure due to strict shell settings.

## Dependencies and Integration Points
It depends on network access, Go, `curl`, and golangci-lint. It is not invoked by the shown `verify-all.sh`, but remains available as a separate quality gate.

## Risks and Test Signals
Risks include use of deprecated `golint`, old golangci-lint version compatibility with modern Go, network installation at verify time, and disabled typechecking reducing signal. Signals are successful linter execution and no reported golint issues.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-golint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-gomod.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-gomod.sh

## Purpose
Verifies that Go module metadata and vendor contents are up to date.

## Important APIs, Types, and Functions
The script sets `GO111MODULE=on`, runs `go mod tidy`, runs `go mod vendor`, checks `git diff`, fails with the diff if non-empty, then runs `go list -mod readonly -m all`.

## Control Flow, State, and Persistence
Unlike a purely read-only verifier, it regenerates module and vendor files before comparing the working tree. If regeneration changes files, it reports the diff and exits non-zero. Persistent effects may remain in the working tree on failure.

## Dependencies and Integration Points
It depends on Go modules, git, and vendor mode. It is the verification partner for dependency update scripts and is included in `verify-all.sh`.

## Risks and Test Signals
Risks include network/module cache differences, Go version churn, mutating the working tree during verification, and broad `git diff` including unrelated local changes. Signals are no diff after tidy/vendor and successful `go list -mod readonly -m all`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-gomod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-govet.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-govet.sh

## Purpose
Runs `go vet` across repository packages outside vendor.

## Important APIs, Types, and Functions
The script executes `go vet $(go list ./... | grep -v vendor)` with strict shell options.

## Control Flow, State, and Persistence
It lists packages, filters vendor, and runs vet once over the resulting package list. It does not intentionally mutate files.

## Dependencies and Integration Points
It depends on the Go toolchain, module resolution, and compilable packages. `verify-all.sh` includes it after gofmt verification.

## Risks and Test Signals
Risks include shell command length for very large package sets, broad `grep -v vendor` filtering, package list failures when module state is dirty, and Go version-dependent vet diagnostics. Signals are `go vet` exiting zero and the script printing "Done".
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-govet.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-files.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-files.sh

## Purpose
Verifies packaged Helm chart `.tgz` files match the chart source and checks the published Helm repo index path.

## Important APIs, Types, and Functions
The script disables git filemode tracking, checks initial `git diff`, expands any `charts/*/*.tgz` archives into their chart directories, checks `git diff` again, installs Helm from the upstream script, adds the `csi-driver-nfs` chart repository, and runs `helm search repo -l`.

## Control Flow, State, and Persistence
It fails if the working tree is already dirty or if unpacking chart packages produces diffs. It can install Helm and adds a Helm repo entry to the user's Helm config/cache.

## Dependencies and Integration Points
It depends on tar, git, curl, Helm installation, network access to Helm scripts and the upstream chart repo, and packaged chart archives. `verify-all.sh` includes it before chart lint/index checks.

## Risks and Test Signals
Risks include mutating Helm user config, network dependency, unpacking tarballs over source directories, dirty-tree false failures, and glob behavior with no `.tgz`. Signals are no git diff after extraction and successful `helm search repo`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-index.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-index.sh

## Purpose
Checks that HTTP URLs referenced by `charts/index.yaml` are reachable or correspond to local files.

## Important APIs, Types, and Functions
The script defines `check_url()` using `curl -I -m 5` and `check_yaml()` that greps `http` lines from the index and extracts the second whitespace-delimited field. It computes `PKG_ROOT` from git and validates each URL.

## Control Flow, State, and Persistence
For each URL, a non-200 HTTP status is treated as a warning only if a corresponding local path under the repository exists; otherwise the script exits non-zero. It does not mutate the repository.

## Dependencies and Integration Points
It depends on `curl`, git, shell text parsing, and `charts/index.yaml`. It is part of Helm release verification.

## Risks and Test Signals
Risks include brittle YAML parsing with `grep`/`awk`, transient network failures, redirects or auth returning non-200, and local path derivation assuming `master` in URLs. Signals are all URLs returning HTTP 200 or resolving to existing local files.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart-index.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-helm-chart.sh

## Purpose
Lints the latest Helm chart and verifies chart image settings match the deployment manifests.

## Important APIs, Types, and Functions
The script defines `get_image_from_helm_chart()` to read image repository/tag values with `yq`, including `baseRepo` handling for slash-prefixed repositories, and `validate_image()` for equality checks. It runs `helm lint`, installs Helm, pip, jq, and Python `yq` if missing, then compares image fields from `charts/latest/csi-driver-nfs/values.yaml` against `deploy/csi-nfs-controller.yaml` and `deploy/csi-nfs-node.yaml`.

## Control Flow, State, and Persistence
After linting, it extracts expected images from deploy manifests and actual images from Helm values, then exits on the first mismatch. It may install system packages or Python packages during verification.

## Dependencies and Integration Points
It depends on Helm, pip, jq, yq, curl, apt, the latest chart layout, and deploy manifest container ordering. It ensures Helm installs use the same sidecar and driver images as raw YAML manifests.

## Risks and Test Signals
Risks include requiring package-manager privileges, network installation, brittle container index assumptions, and failure if chart/deploy intentionally diverge. Signals are a successful `helm lint` and all image comparisons passing.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-spelling.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-spelling.sh

## Purpose
Runs spelling checks over tracked repository files outside vendor.

## Important APIs, Types, and Functions
The script pins `misspell` tool version `v0.3.4`, creates a temporary directory, installs `github.com/client9/misspell/cmd/misspell` into that directory if absent, then runs `git ls-files | grep -v vendor | xargs misspell`.

## Control Flow, State, and Persistence
It changes to the repository root, installs the tool in a temp directory when needed, captures misspell output to `errors.log`, prefixes errors, and exits with status 1 if any spelling issue is found. Temp files are removed via an EXIT trap.

## Dependencies and Integration Points
It depends on git, Go, network access if misspell is missing, and the external misspell ruleset. It is a standalone quality gate, not shown in `verify-all.sh`.

## Risks and Test Signals
Risks include false positives in code or generated files, broad vendor filtering by substring, network installs, and old tool behavior. Signals are an empty errors log and zero exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-update.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-update.sh

## Purpose
Checks that dependency update operations did not leave uncommitted repository changes.

## Important APIs, Types, and Functions
The script runs `git diff --shortstat`, and if non-empty, prints `git --no-pager diff` and exits one.

## Control Flow, State, and Persistence
It is read-only and purely checks the working tree after another update step has run. It prints "Done" on a clean tree.

## Dependencies and Integration Points
It depends on git and is intended to follow scripts such as `update-dependencies.sh` in CI to ensure generated files are checked in.

## Risks and Test Signals
Risks include failing on unrelated local changes and not checking untracked files. Signals are an empty `git diff --shortstat` and zero exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-yamllint.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-yamllint.sh

## Purpose
Validates YAML formatting for deployment, example, and Helm chart manifests, while enforcing parity between raw deploy YAML count and Helm template count.

## Important APIs, Types, and Functions
The script installs `yamllint` through apt if missing, sets `LOG=/tmp/yamllint.log`, counts `deploy/*.yaml` and chart template YAMLs excluding serviceaccount, then runs `yamllint -f parsable` over several deploy/example globs and the latest chart templates. It filters accepted warnings such as line length and chart-template syntax noise.

## Control Flow, State, and Persistence
It first compares YAML file counts between deploy manifests and Helm templates. Then it lints each path group, filters known noisy messages and CRD snapshot long lines, and exits if any remaining issue appears. It may install packages and writes a temporary log.

## Dependencies and Integration Points
It depends on apt, yamllint, shell globs, chart layout, deploy layout, and generated CRD exceptions. It is part of `verify-all.sh`.

## Risks and Test Signals
Risks include package-manager side effects, brittle file-count parity, unquoted globs, CRD exceptions hiding real issues, and Helm templates not being valid plain YAML. Signals are matching file counts and zero unfiltered yamllint messages.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-yamllint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/cache.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/cache.go

## Purpose
Implements a small TTL cache abstraction used by the NFS CSI driver, notably for volume deletion idempotency. It is a reduced version of an Azure cache pattern containing only methods used in this driver.

## Important APIs, Types, and Functions
Public types are `CacheReadType`, `GetFunc`, `Resource`, `TimedCache`, and `DisabledCache`. Internal `CacheEntry` stores key, data, per-entry mutex, and creation time. Key functions are `NewTimedCache()`, `TimedCache.getInternal()`, `TimedCache.Get()`, `TimedCache.Set()`, `DisabledCache.Get()`, and `DisabledCache.Set()`. Storage uses `k8s.io/client-go/tools/cache.Store`.

## Control Flow, State, and Persistence
`NewTimedCache` requires a getter and can return either a TTL-backed cache or disabled cache. `TimedCache.Get` creates a placeholder entry when missing, locks the entry, returns cached data if non-nil and not expired, otherwise calls the getter and updates `Data` and `CreatedOn`. `Set` inserts a fresh cache entry. State is in-memory only and lost on driver restart.

## Dependencies and Integration Points
It integrates with controller deletion flow through `Driver.volDeletionCache`, where a cached non-nil marker lets repeated `DeleteVolume` calls return success without redoing NFS deletion. It depends on Go synchronization, time, and Kubernetes cache store key functions.

## Risks and Test Signals
Risks include `Set` using `Store.Add` instead of update semantics, nil data never being considered cached, no deletion API, TTL-based idempotency only surviving process lifetime, and type assertions in `cacheKeyFunc`. Signals are concurrent `Get` calls invoking the getter once per expired key, TTL expiry causing refresh, and deletion retries being skipped within the cache window.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix.go

## Purpose
Provides the Unix implementation of the package-local `chmod` helper, preserving raw permission bits including setuid, setgid, and sticky bits.

## Important APIs, Types, and Functions
The file is built with `//go:build !windows` and imports `syscall`. Its only function is `chmod(path string, mode uint32) error`, which calls `syscall.Chmod(path, mode)`.

## Control Flow, State, and Persistence
Callers such as `chmodIfPermissionMismatch` delegate final permission changes to this function. The state change is filesystem metadata on the target path.

## Dependencies and Integration Points
It integrates with volume directory creation in `controllerserver.go` and node publish behavior in related helpers. It exists because `os.Chmod` with `os.FileMode` can mishandle special raw Unix bits in this code path.

## Risks and Test Signals
Risks include platform-specific syscall behavior, NFS server permission semantics, and failure under restricted permissions. Signals are tests proving modes such as `02770`, `01777`, and `04755` are applied exactly on Unix.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix_test.go

## Purpose
Tests that Unix chmod behavior preserves special permission bits when `chmodIfPermissionMismatch` adjusts NFS volume directories.

## Important APIs, Types, and Functions
The file is `!windows` only and defines `TestChmodIfPermissionMismatchSpecialBits`. It uses `t.TempDir`, `os.Mkdir`, `syscall.Chmod`, `chmodIfPermissionMismatch`, `os.Lstat`, and `syscall.Stat_t`.

## Control Flow, State, and Persistence
For each table case, the test creates a directory, sets an initial raw mode, calls `chmodIfPermissionMismatch` with the requested mode, then reads raw mode bits via `Stat_t.Mode & 07777` and compares them to the expected requested mode. Temp directories are automatically cleaned up by the test framework.

## Dependencies and Integration Points
It validates the Unix implementation in `chmod_unix.go` and the permission mismatch helper in `utils.go`. It protects controller/node code that applies `mountPermissions` to provisioned directories.

## Risks and Test Signals
Risks include running on filesystems that ignore special bits, OS-specific permission semantics, and test exclusion on Windows. Signals are exact preservation of setgid, sticky, already-set setgid, and setuid cases.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_windows.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_windows.go

## Purpose
Provides the Windows implementation of the package-local `chmod` helper so the package builds on Windows even though Unix special bits are unsupported.

## Important APIs, Types, and Functions
The file is built with `//go:build windows`, imports `os`, and defines `chmod(path string, mode uint32) error`, which calls `os.Chmod(path, os.FileMode(mode))`.

## Control Flow, State, and Persistence
Callers pass raw mode values, but on Windows only the permission semantics supported by `os.Chmod` apply. Filesystem metadata may change according to Windows/Go behavior.

## Dependencies and Integration Points
It is the platform counterpart to `chmod_unix.go` and keeps shared controller/node permission code portable at compile time.

## Risks and Test Signals
Risks include special bits being ignored, different ACL semantics from Unix, and runtime behavior not matching NFS/Linux expectations. Signals are successful Windows compilation and any Windows-specific permission tests passing if added.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/controllerserver.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/controllerserver.go

## Purpose
Implements the CSI controller service for the NFS driver: dynamic volume directory creation/deletion, snapshot archive creation/deletion, volume clone/restore, controller capability reporting, validation, and controller-side expansion responses.

## Important APIs, Types, and Functions
Key types are `ControllerServer`, internal `nfsVolume`, and internal `nfsSnapshot`. Major CSI methods are `CreateVolume`, `DeleteVolume`, `ValidateVolumeCapabilities`, `ControllerGetCapabilities`, `CreateSnapshot`, `DeleteSnapshot`, and `ControllerExpandVolume`; publish/unpublish/list/capacity/get/modify/list-snapshot calls are explicitly unimplemented where not supported. Helpers include `internalMount`, `internalUnmount`, `copyFromSnapshot`, `copyFromVolume`, `copyVolume`, `newNFSSnapshot`, `newNFSVolume`, `getInternalMountPath`, `getInternalVolumePath`, `getVolumeIDFromNfsVol`, `getSnapshotIDFromNfsSnapshot`, `getNfsVolFromID`, `getNfsSnapFromID`, `isValidVolumeCapabilities`, `validateSnapshot`, and `volumeFromSnapshot`.

## Control Flow, State, and Persistence
`CreateVolume` validates name/capabilities/storage class parameters, acquires a per-volume lock, builds an `nfsVolume`, internally mounts the NFS share through the node server, creates the target subdirectory, optionally applies `mountPermissions`, and optionally clones from a volume or restores from a snapshot. It returns a CSI volume ID encoding server, base directory, subdirectory, optional UUID, and selected `onDelete` policy. `DeleteVolume` parses that ID, honors `retain`, uses an in-memory TTL deletion cache for idempotency, internally mounts the share, then either archives by renaming to `archived-<subDir>` or recursively removes the directory and prunes empty parents. `CreateSnapshot` parses the source volume, builds a snapshot ID, mounts the snapshot share and source share, validates that an existing snapshot directory has only the expected archive name, then creates a compressed or uncompressed tar archive using either the system `tar` command or Go tar helpers. `DeleteSnapshot` mounts the snapshot share and removes the snapshot directory. Copy flows mount source and destination shares and use either `tar` extraction for snapshots or `cp -a` for volume clones. State persists on the NFS server as directories and tar archives; controller locks and deletion cache are process-local only.

## Dependencies and Integration Points
The controller depends on CSI protobuf APIs, gRPC status codes, klog, filesystem operations, `tar` and `cp` commands when configured, Go tar helpers, driver configuration fields such as `workingMountDir`, `defaultOnDeletePolicy`, `enableSnapshotCompression`, `useTarCommandInSnapshot`, `removeArchivedVolumePath`, node server `NodePublishVolume`/`NodeUnpublishVolume`, volume locks, and helper constants from `nfs.go`/`utils.go`. It integrates with external-provisioner, csi-snapshotter, Kubernetes `StorageClass` parameters (`server`, `share`, `subDir`, `onDelete`, metadata keys, `mountpermissions`), and `VolumeSnapshotClass` parameters.

## Risks and Test Signals
Risks include CSI ID format limits around directory depth and separator handling, path traversal if validation regresses, process-local idempotency cache loss on restart, privileged internal mounts from the controller pod, use of shell commands `tar`/`cp`, snapshot archive name collisions, stale archived directories, concurrent operations on the same NFS paths outside the lock key, and NFS permission/rename semantics. Strong test signals are controller tests for valid/invalid create parameters, mount permission parsing, delete retain/archive/delete behavior, nested subdirectory ID parsing, snapshot creation with and without compression, cross-share snapshot classes, restore from legacy uncompressed archives, special permission-bit tests, and successful end-to-end PVC clone/snapshot restore workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/controllerserver.go -->
