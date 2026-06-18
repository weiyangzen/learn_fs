# Research: subset-b-000362

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/crd-csi-snapshot.yaml

## Purpose
This manifest installs the Kubernetes CSI snapshot API CRDs needed by the NFS CSI deployment. It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` in the `snapshot.storage.k8s.io` API group, with both `v1` and `v1beta1` served versions and storage on `v1`.

## Important APIs, Types, and Functions
The important resources are three `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects: `volumesnapshots.snapshot.storage.k8s.io`, `volumesnapshotclasses.snapshot.storage.k8s.io`, and `volumesnapshotcontents.snapshot.storage.k8s.io`. Their OpenAPI schemas define snapshot source selection, `volumeSnapshotClassName`, bound content references, CSI `driver`, `deletionPolicy`, `source.volumeHandle` or `source.snapshotHandle`, `restoreSize`, `readyToUse`, creation time, error status, and finalizer-preserving status subresources. Additional printer columns expose readiness, source PVC/content, driver, deletion policy, restore size, bound snapshot, namespace, and age.

## Control Flow, State, and Persistence
There is no executable control flow, but the CRDs create persistent cluster-scoped API storage. Snapshot lifecycle state is persisted in custom resources and status subresources: `VolumeSnapshot` records user-facing intent and binding status, `VolumeSnapshotClass` records driver parameters and deletion policy, and `VolumeSnapshotContent` records provisioned or pre-provisioned snapshot handles and binding to a namespaced snapshot. The `v1beta1` served version keeps older clients usable while `v1` is the stored version.

## Dependencies and Integration Points
The file depends on Kubernetes apiextensions v1 and a cluster new enough to serve CRD structural schemas. It integrates with `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, the `csi-snapshotter` sidecar in the NFS controller deployment, and the NFS CSI driver name `nfs.csi.k8s.io` used by snapshot classes and contents.

## Risks and Test Signals
Risks include cluster-wide CRD replacement impact, schema drift with the snapshot-controller image version, and backwards compatibility exposure from serving both `v1` and `v1beta1`. Test signals are successful `kubectl apply`, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, discovery of both served versions, status-subresource updates by the snapshot controller, and a real PVC snapshot reaching `readyToUse=true`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-controller.yaml

## Purpose
This manifest deploys the v4.4.0 NFS CSI controller as a single `kube-system` `Deployment`. It hosts the controller-side NFS CSI process plus provisioner, snapshotter, and liveness sidecars that drive PVC provisioning and CSI snapshot operations.

## Important APIs, Types, and Functions
The main object is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica and labels `app: csi-nfs-controller`. Containers are `csi-provisioner:v3.5.0`, `csi-snapshotter:v6.2.2`, `livenessprobe:v2.10.0`, and `nfsplugin:v4.4.0`. The sidecars share `/csi/csi.sock`; provisioner and snapshotter enable leader election in `kube-system` and use long `--timeout=1200s` CSI calls. The NFS container runs `--nodeid=$(NODE_ID)` and `--endpoint=$(CSI_ENDPOINT)` with `SYS_ADMIN`, `privileged: true`, and bidirectional mount propagation on `/var/lib/kubelet/pods`.

## Control Flow, State, and Persistence
Kubernetes creates one controller pod on Linux, tolerating control-plane taints and using host networking so the controller can mount NFS while creating backing directories. The NFS driver creates the Unix CSI socket in an `emptyDir`, the sidecars connect to it, and leader-elected sidecars watch PVCs, PVs, snapshot resources, leases, and events through the service account. Persistent state lives in Kubernetes objects and host-mounted pod directories; pod-local socket state is ephemeral.

## Dependencies and Integration Points
This deployment depends on `rbac-csi-nfs.yaml` for `csi-nfs-controller-sa`, `csi-nfs-driverinfo.yaml` for the `CSIDriver`, snapshot CRDs and snapshot RBAC for snapshot flows, kubelet host paths, and registry images from `registry.k8s.io/sig-storage`. It also expects NFS client tooling and kernel mount support in the `nfsplugin` image and reachable NFS servers from host networking.

## Risks and Test Signals
Risks include privileged mount access, hostNetwork DNS behavior, long-running CSI operations tying up sidecars, missing CRDs causing snapshotter failures, and named health port exposure on the host network. Test signals are a ready deployment, healthy `/healthz` on port 29652, one lease holder for provisioner/snapshotter leader election, successful dynamic provisioning with `nfs.csi.k8s.io`, successful snapshot creation, and clean sidecar logs with no CSI socket connection errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-driverinfo.yaml

## Purpose
This file registers the NFS CSI driver with Kubernetes through a `CSIDriver` object. It tells Kubernetes that `nfs.csi.k8s.io` does not require attach/detach and supports persistent volumes.

## Important APIs, Types, and Functions
The only object is `storage.k8s.io/v1` `CSIDriver` named `nfs.csi.k8s.io`. Its key fields are `attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
The object is cluster-scoped and persistent. Kubernetes admission and kubelet CSI plumbing consult it when scheduling and mounting volumes, skipping attach-controller workflows and applying file-based fsGroup ownership policy when requested by pods.

## Dependencies and Integration Points
It integrates with the controller and node plugin deployments, storage classes that name `nfs.csi.k8s.io`, and kubelet plugin registration under `/var/lib/kubelet/plugins/csi-nfsplugin`. It depends on Kubernetes support for `storage.k8s.io/v1` `CSIDriver`.

## Risks and Test Signals
Risks include driver-name mismatch with storage classes or node registration, incorrect fsGroup policy expectations for NFS exports, and applying the object before a cluster version supports the selected fields. Test signals are `kubectl get csidriver nfs.csi.k8s.io`, successful PVC scheduling without VolumeAttachment objects, node-driver-registrar reporting the same name, and pod mounts honoring requested fsGroup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-node.yaml

## Purpose
This manifest deploys the v4.4.0 NFS CSI node plugin as a Linux `DaemonSet`. It registers the driver with kubelet on every node and performs node-side NFS mount operations for pods.

## Important APIs, Types, and Functions
The main object is an `apps/v1` `DaemonSet` named `csi-nfs-node` in `kube-system`. Containers are `livenessprobe:v2.10.0`, `csi-node-driver-registrar:v2.8.0`, and `nfsplugin:v4.4.0`. The registrar advertises `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` through `/registration`; the NFS container runs privileged with `SYS_ADMIN`, uses `--endpoint=unix:///csi/csi.sock`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

## Control Flow, State, and Persistence
Kubernetes rolls the DaemonSet with `maxUnavailable: 1` and schedules it on every Linux node via broad tolerations. The driver creates the CSI socket under a hostPath plugin directory, the registrar registers it with kubelet, and kubelet calls the node service to stage and publish NFS volumes. Persistent node state is hostPath socket/registration data and bind mounts under kubelet pod directories; the liveness container probes the shared socket on health port 29653.

## Dependencies and Integration Points
The node plugin depends on `csi-nfs-node-sa`, the `CSIDriver` object, kubelet plugin and plugin registry host paths, host networking, Linux mount propagation, and the NFS CSI controller for provisioning. It integrates directly with kubelet rather than the Kubernetes API for most node calls.

## Risks and Test Signals
Risks include privileged node access, kubelet path differences, missing mount propagation support, stale registration sockets during upgrades, and NFS connectivity failures hidden as pod mount timeouts. Test signals are one ready pod per Linux node, `kubectl get csinode` listing `nfs.csi.k8s.io`, registrar liveness success, healthy port 29653, and pods successfully mounting dynamically provisioned NFS PVCs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-snapshot-controller.yaml

## Purpose
This manifest deploys the external CSI snapshot controller used by the v4.4.0 bundle. It reconciles `VolumeSnapshot` and `VolumeSnapshotContent` objects independently of the NFS CSI driver pods.

## Important APIs, Types, and Functions
The object is an `apps/v1` `Deployment` named `snapshot-controller` in `kube-system` with two replicas, `minReadySeconds: 15`, rolling update `maxSurge: 0`, and `maxUnavailable: 1`. It runs `registry.k8s.io/sig-storage/snapshot-controller:v6.2.2` with `--leader-election=true`, `--leader-election-namespace=kube-system`, and verbosity 2.

## Control Flow, State, and Persistence
Kubernetes schedules two Linux controller pods with control-plane tolerations and `system-cluster-critical` priority. Only the elected replica actively reconciles snapshot API objects; the second replica provides failover. It waits for v1 snapshot CRDs before readiness and persists state by updating snapshot custom resources and events.

## Dependencies and Integration Points
It depends on snapshot CRDs from `crd-csi-snapshot.yaml` and permissions from `rbac-snapshot-controller.yaml`. It integrates with the NFS controller's `csi-snapshotter` sidecar, which talks to the CSI driver, while this controller owns the Kubernetes-level snapshot binding loop.

## Risks and Test Signals
Risks include deploying the controller before CRDs, insufficient RBAC for status updates, mismatched controller/CRD versions, and leader-election lease conflicts in `kube-system`. Test signals are two available replicas, one active leader lease, no CRD discovery crash loops, status updates on `VolumeSnapshot`, and successful snapshot deletion according to `deletionPolicy`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/rbac-csi-nfs.yaml

## Purpose
This RBAC bundle grants the NFS CSI controller the cluster permissions needed for provisioning, snapshot sidecar coordination, events, and leader election. It also creates the node service account used by the DaemonSet.

## Important APIs, Types, and Functions
The file creates `ServiceAccount` objects `csi-nfs-controller-sa` and `csi-nfs-node-sa` in `kube-system`, a `ClusterRole` named `nfs-external-provisioner-role`, and a `ClusterRoleBinding` named `nfs-csi-provisioner-binding`. Rules allow PV get/list/watch/create/delete, PVC get/list/watch/update, storageclasses get/list/watch, snapshot class/snapshot get/list/watch, snapshot content get/list/watch/update/patch including status, event create/update/patch, CSINode and node reads, lease create/update/patch, and secret get.

## Control Flow, State, and Persistence
RBAC resources are persistent cluster state. They do not execute logic, but Kubernetes authorization checks use them whenever the controller pod's sidecars watch objects, update PVC/PV metadata, write snapshot content status, emit events, or acquire leader-election leases.

## Dependencies and Integration Points
The binding targets `csi-nfs-controller-sa`, which is referenced by `csi-nfs-controller.yaml`. The node service account is referenced by `csi-nfs-node.yaml`, although this file does not grant node-specific cluster permissions. Snapshot permissions depend on the snapshot CRDs existing or being installable later.

## Risks and Test Signals
Risks include broad cluster-scoped rights, missing `patch` on PVs for newer sidecars, secret read exposure, and install ordering where RBAC references API groups before CRDs are available. Test signals are successful `kubectl auth can-i` checks as the controller service account, sidecars acquiring leases, PV/PVC event creation, and no forbidden errors in provisioner or snapshotter logs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.4.0/rbac-snapshot-controller.yaml

## Purpose
This file grants the external snapshot controller the permissions required to reconcile Kubernetes CSI snapshot objects and to coordinate leader election.

## Important APIs, Types, and Functions
It creates the `snapshot-controller` service account, `snapshot-controller-runner` cluster role and binding, and a namespaced `snapshot-controller-leaderelection` role and binding in `kube-system`. The cluster role can read PVs, read/update PVCs, create/update/patch events, read snapshot classes, create/read/update/delete/patch snapshot contents, patch snapshot content status, read/update/patch snapshots, and update/patch snapshot status. The role grants full lease lifecycle verbs for leader election.

## Control Flow, State, and Persistence
The resources persist as Kubernetes authorization state. The snapshot-controller deployment uses them to watch snapshot API resources, bind snapshot contents, update status subresources, emit events, and maintain a lease so only one replica reconciles actively.

## Dependencies and Integration Points
It is paired with `csi-snapshot-controller.yaml` and the CRDs in `crd-csi-snapshot.yaml`. It integrates with the `snapshot.storage.k8s.io` API group and with the NFS CSI snapshotter sidecar through shared custom resources rather than direct pod-to-pod calls.

## Risks and Test Signals
Risks include missing status-subresource verbs, lease permissions scoped to the wrong namespace, and overbroad delete rights on snapshot contents. Test signals are absence of authorization errors in snapshot-controller logs, a valid leader-election lease, updates to `VolumeSnapshot.status`, event creation, and successful deletion of `VolumeSnapshotContent` objects under both Retain and Delete policies.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.4.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/crd-csi-snapshot.yaml

## Purpose
This v4.5.0 manifest installs the same CSI snapshot API CRDs as v4.4.0. It provides cluster-wide `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` API storage for the NFS CSI snapshot components.

## Important APIs, Types, and Functions
The three `CustomResourceDefinition` objects are `volumesnapshots.snapshot.storage.k8s.io`, `volumesnapshotclasses.snapshot.storage.k8s.io`, and `volumesnapshotcontents.snapshot.storage.k8s.io`. They serve `v1` and `v1beta1`, store `v1`, define structural schemas for snapshot sources, classes, CSI drivers, deletion policies, content bindings, restore size, readiness, error status, and expose status subresources and kubectl printer columns.

## Control Flow, State, and Persistence
The CRDs are declarative cluster API definitions. Once applied, Kubernetes persists snapshot resources and allows controllers to update status subresources while users create or delete snapshot intent objects. The v4.5.0 file is byte-identical to the v4.4.0, v4.6.0, and v4.7.0 CRD files in this repository, so release changes come from controller image versions rather than schema changes.

## Dependencies and Integration Points
It depends on Kubernetes CRD support and integrates with `snapshot-controller:v6.3.1`, `csi-snapshotter:v6.3.1`, NFS storage classes, and any user-created `VolumeSnapshotClass` using `driver: nfs.csi.k8s.io`.

## Risks and Test Signals
Risks are cluster-wide API replacement, accidental removal of a served version still used by clients, and controller/schema version skew. Test signals are successful API discovery for `snapshot.storage.k8s.io/v1`, the snapshot controller staying ready after CRD install, successful creation of snapshot class/content/snapshot resources, and status updates through the status subresources.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-controller.yaml

## Purpose
This manifest deploys the v4.5.0 NFS CSI controller. It is structurally the same controller deployment as v4.4.0 with sidecar and driver image updates for the v4.5.0 release.

## Important APIs, Types, and Functions
The `Deployment` remains `csi-nfs-controller` in `kube-system`, one replica, hostNetwork, `ClusterFirstWithHostNet`, `system-cluster-critical`, Linux-only scheduling, and control-plane tolerations. Containers are `csi-provisioner:v3.6.1`, `csi-snapshotter:v6.3.1`, `livenessprobe:v2.11.0`, and `nfsplugin:v4.5.0`. Sidecars still use `/csi/csi.sock`, leader election, extra create metadata, and `--timeout=1200s`; the driver keeps privileged `SYS_ADMIN` access and port-named health checks on 29652.

## Control Flow, State, and Persistence
The pod lifecycle and controller flow mirror v4.4.0: the NFS process exposes a CSI socket from an `emptyDir`, sidecars drive Kubernetes watches and CSI calls, and state is persisted in PV/PVC/snapshot API objects plus host pod mount directories. The only behavioral deltas visible in YAML are upgraded images, so runtime changes depend on the new sidecar and driver binaries.

## Dependencies and Integration Points
It depends on the same RBAC, `CSIDriver`, snapshot CRDs, kube-system leader-election leases, Linux host mounts, and registry image availability as v4.4.0. The sidecar versions align with the v4.5.0 snapshot controller manifest.

## Risks and Test Signals
Risks include upgrade compatibility from provisioner v3.5.0 to v3.6.1, snapshotter v6.2.2 to v6.3.1, and liveness v2.10.0 to v2.11.0 while still using named health ports. Test signals are rollout success from v4.4.0, no forbidden or deprecated API warnings, healthy port 29652, successful provisioning and deletion, successful snapshots, and no CSI timeout regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-driverinfo.yaml

## Purpose
This file registers the v4.5.0 bundle's CSI driver identity. It is the same `CSIDriver` definition used in adjacent releases.

## Important APIs, Types, and Functions
The object is `storage.k8s.io/v1` `CSIDriver` named `nfs.csi.k8s.io` with `attachRequired: false`, persistent lifecycle support, and `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
The `CSIDriver` persists cluster-wide and changes Kubernetes volume behavior by suppressing attach/detach and advertising fsGroup handling. There is no executable flow in the YAML.

## Dependencies and Integration Points
It must match the driver name returned by `nfsplugin:v4.5.0`, the kubelet registration path in `csi-nfs-node.yaml`, and storage classes referencing `nfs.csi.k8s.io`.

## Risks and Test Signals
Risks are name drift, unsupported cluster versions, and fsGroup behavior not matching export permissions. Test signals include a present `CSIDriver`, no VolumeAttachment creation for NFS PVs, successful node registration, and pods mounting NFS PVCs under the expected group ownership.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-node.yaml

## Purpose
This manifest deploys the v4.5.0 NFS CSI node DaemonSet. It updates the node-side sidecars and NFS plugin image from v4.4.0 while preserving the same kubelet registration and mount behavior.

## Important APIs, Types, and Functions
The `DaemonSet` is `csi-nfs-node` in `kube-system` with rolling update `maxUnavailable: 1`, hostNetwork, Linux node selector, broad tolerations, and `system-node-critical` priority. Containers are `livenessprobe:v2.11.0`, `csi-node-driver-registrar:v2.9.0`, and `nfsplugin:v4.5.0`. The registrar points kubelet at `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`; the NFS container uses privileged `SYS_ADMIN`, bidirectional `/var/lib/kubelet/pods`, and health port 29653.

## Control Flow, State, and Persistence
Each node runs one pod that creates the CSI socket in the kubelet plugin hostPath, registers the driver through the plugins registry, and serves node-stage/node-publish calls. Persistent effects are kubelet registration files, CSI sockets, and pod volume mounts; Kubernetes object state is minimal beyond the DaemonSet and pods.

## Dependencies and Integration Points
It depends on kubelet hostPath layout, Linux mount propagation, `CSIDriver` identity, the controller deployment, and image availability for the v4.5.0 driver and sidecars. It uses `csi-nfs-node-sa` created by RBAC.

## Risks and Test Signals
Risks include registrar upgrade behavior, stale sockets during rolling updates, privileged mount operations, and NFS mount failures surfacing only at workload scheduling time. Test signals are every Linux node reporting a ready DaemonSet pod, successful `CSINode` driver advertisement, healthy 29653 probes, and pod-level NFS mount/unmount operations during a rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-snapshot-controller.yaml

## Purpose
This manifest deploys the v4.5.0 external snapshot controller. It updates the snapshot-controller image from v6.2.2 to v6.3.1 while keeping the same high-availability deployment shape.

## Important APIs, Types, and Functions
The object is an `apps/v1` `Deployment` named `snapshot-controller`, two replicas, `minReadySeconds: 15`, rolling update with no surge and one unavailable replica, Linux scheduling, control-plane tolerations, and `system-cluster-critical` priority. The single container runs `registry.k8s.io/sig-storage/snapshot-controller:v6.3.1` with verbosity 2 and leader election in `kube-system`.

## Control Flow, State, and Persistence
The elected replica watches and reconciles snapshot custom resources, while the second replica waits for failover. Persistent effects are updates to `VolumeSnapshot` and `VolumeSnapshotContent` status, events, finalizers, and leader-election lease state.

## Dependencies and Integration Points
It depends on the snapshot CRDs, snapshot-controller RBAC, and version-compatible `csi-snapshotter:v6.3.1` running in the NFS controller deployment. It uses shared API objects rather than direct access to the NFS driver.

## Risks and Test Signals
Risks include CRD/version skew, unavailable CRDs blocking readiness, and lease RBAC problems. Test signals are ready replicas, one active leader, no forbidden status updates, successful creation and binding of `VolumeSnapshotContent`, and snapshot status reaching ready.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/rbac-csi-nfs.yaml

## Purpose
This file provides the v4.5.0 NFS CSI service accounts and controller authorization. It is byte-identical to the v4.4.0 and v4.6.0 RBAC in this subset.

## Important APIs, Types, and Functions
It creates `csi-nfs-controller-sa`, `csi-nfs-node-sa`, `nfs-external-provisioner-role`, and `nfs-csi-provisioner-binding`. The cluster role grants PV create/delete but not patch, PVC update, storage class reads, snapshot reads and snapshot content updates/status updates, event writes, CSINode/node reads, lease writes, and secret reads.

## Control Flow, State, and Persistence
The resources persist authorization policy for the v4.5.0 controller. Sidecar API calls are admitted or denied based on these rules during provisioning, snapshotting, eventing, and leader election.

## Dependencies and Integration Points
The controller deployment references `csi-nfs-controller-sa`; the node DaemonSet references `csi-nfs-node-sa`. Snapshot-related rules integrate with `snapshot.storage.k8s.io` CRDs and the `csi-snapshotter` sidecar.

## Risks and Test Signals
Risks include missing PV patch permissions for later provisioner behavior, broad secret read permissions, and cluster-scoped access. Test signals are clean sidecar logs, successful leader election leases, PV/PVC lifecycle operations, snapshot content status updates, and positive `kubectl auth can-i` checks for each required verb.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.5.0/rbac-snapshot-controller.yaml

## Purpose
This v4.5.0 RBAC file authorizes the external snapshot controller. It is unchanged from the v4.4.0, v4.6.0, and v4.7.0 files in this subset.

## Important APIs, Types, and Functions
It defines the `snapshot-controller` service account, `snapshot-controller-runner` cluster role and binding, plus a namespaced lease role and binding. The rules cover PV/PVC reads and PVC updates, event writes, snapshot class reads, snapshot content full lifecycle and status patch, snapshot read/update/patch and status update/patch, and lease create/update/delete/list/watch/get.

## Control Flow, State, and Persistence
Authorization state persists in Kubernetes and gates the snapshot-controller reconciliation loop. The lease role supports active/passive behavior for the two-replica deployment.

## Dependencies and Integration Points
It is consumed by `csi-snapshot-controller.yaml` and depends on the snapshot API group provided by `crd-csi-snapshot.yaml`. It coordinates indirectly with the NFS CSI snapshotter sidecar through snapshot custom resources.

## Risks and Test Signals
Risks include missing subresource verbs, wrong leader-election namespace, and destructive permissions on snapshot contents. Test signals are no RBAC denials, a maintained leader lease, event creation, snapshot status transitions, and successful cleanup of snapshot content resources.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.5.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/crd-csi-snapshot.yaml

## Purpose
This v4.6.0 file installs the CSI snapshot CRDs used by the NFS CSI bundle. It is byte-identical to the v4.4.0, v4.5.0, and v4.7.0 snapshot CRD manifests in this repository.

## Important APIs, Types, and Functions
It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs in `snapshot.storage.k8s.io`, each with `v1` and `v1beta1` served versions. The schemas capture snapshot sources, class references, CSI driver names, deletion policy, snapshot handles, volume handles, volume snapshot references, restore size, ready state, errors, and status subresources.

## Control Flow, State, and Persistence
Applying the file adds persistent cluster API types. Users and controllers then create and mutate custom resources; the snapshot controller and CSI snapshotter update status and content bindings as the snapshot lifecycle advances.

## Dependencies and Integration Points
It integrates with `snapshot-controller:v6.3.3`, `csi-snapshotter:v6.3.3`, RBAC for both snapshot and NFS controllers, and storage classes/snapshot classes for `nfs.csi.k8s.io`.

## Risks and Test Signals
Risks include CRD replacement blast radius, compatibility with stored `v1beta1` clients, and controller readiness failures if CRDs are absent. Test signals include served API discovery, successful status-subresource writes, snapshot controller readiness, `VolumeSnapshotContent` binding, and PVC restore flows using `restoreSize`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-controller.yaml

## Purpose
This manifest deploys the v4.6.0 NFS CSI controller. Compared with v4.5.0, it upgrades controller sidecars and hardens containers by dropping Linux capabilities on non-privileged sidecars and dropping all non-added capabilities in the privileged NFS container.

## Important APIs, Types, and Functions
The `Deployment` remains a one-replica `csi-nfs-controller` in `kube-system`. Containers are `csi-provisioner:v4.0.0`, `csi-snapshotter:v6.3.3`, `livenessprobe:v2.12.0`, and `nfsplugin:v4.6.0`. The liveness sidecar switches from `--health-port=29652` to `--http-endpoint=localhost:29652`, and the NFS liveness probe targets `host: localhost`, `port: 29652` without declaring a named container port. Security contexts drop `ALL` capabilities for sidecars; the NFS container keeps `privileged: true`, adds `SYS_ADMIN`, drops `ALL`, and allows privilege escalation.

## Control Flow, State, and Persistence
The controller pod still creates a CSI socket in an `emptyDir`, runs sidecar watch loops through leader election, and mounts `/var/lib/kubelet/pods` bidirectionally for NFS directory operations. State persists in Kubernetes PV/PVC/snapshot resources, events, leases, and host pod mount paths. The v4.6.0 flow relies on localhost health endpoints rather than a named exposed port.

## Dependencies and Integration Points
It depends on the v4.6.0-compatible RBAC, `CSIDriver`, snapshot CRDs, snapshot controller, kubelet pod hostPath, host networking, and `registry.k8s.io/sig-storage` images. The provisioner v4.0.0 image may require RBAC verbs that older manifests did not need, making RBAC validation important.

## Risks and Test Signals
Risks include sidecar major-version behavior changes, capability-drop interactions with privileged NFS operations, localhost health endpoint binding differences, and RBAC gaps after upgrading to `csi-provisioner:v4.0.0`. Test signals are healthy 29652 probes, successful rollout, no permission-denied mount errors, no provisioner forbidden errors, successful provisioning/snapshotting, and stable leader-election leases.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-driverinfo.yaml

## Purpose
This file registers the v4.6.0 NFS CSI driver identity in Kubernetes. It is unchanged from the other release directories in this subset.

## Important APIs, Types, and Functions
The single `storage.k8s.io/v1` `CSIDriver` named `nfs.csi.k8s.io` declares `attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
Kubernetes persists this cluster-scoped object and uses it during volume admission, scheduling, attach decisions, and kubelet mount behavior. There is no runtime loop inside the manifest.

## Dependencies and Integration Points
It must match the driver name registered by `nfsplugin:v4.6.0` and the storage classes used by workloads. It integrates with the node DaemonSet's registrar and controller-side provisioner.

## Risks and Test Signals
Risks are driver-name mismatch, unsupported fsGroup policy on older clusters, and mismatched assumptions about NFS permissions. Test signals are a present `CSIDriver`, no attach objects for NFS volumes, matching `CSINode` entries, and successful pod mounts with fsGroup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-node.yaml

## Purpose
This manifest deploys the v4.6.0 NFS CSI node DaemonSet. It updates sidecars and hardens capability sets while keeping the same kubelet plugin registration path and NFS mount responsibilities.

## Important APIs, Types, and Functions
The DaemonSet uses `livenessprobe:v2.12.0`, `csi-node-driver-registrar:v2.10.0`, and `nfsplugin:v4.6.0`. The liveness sidecar switches to `--http-endpoint=localhost:29653`; the NFS container's liveness probe also targets `host: localhost` and numeric port 29653. Sidecar containers drop all capabilities, while the NFS container runs privileged, adds `SYS_ADMIN`, drops all other capabilities, and mounts `/var/lib/kubelet/pods` bidirectionally plus `/var/lib/kubelet/plugins/csi-nfsplugin` and `/var/lib/kubelet/plugins_registry` host paths.

## Control Flow, State, and Persistence
One pod per Linux node creates a hostPath CSI socket, registers it with kubelet, and handles node publish/unpublish calls. Rolling update limits disruption to one unavailable node plugin. Persistent node effects are CSI socket files, registration data, and kubelet-managed pod volume mounts.

## Dependencies and Integration Points
The DaemonSet depends on kubelet host paths, Linux mount propagation, host networking, `csi-nfs-node-sa`, the `CSIDriver`, and the controller deployment for provisioned volume metadata. It integrates with kubelet through the registrar sidecar and with the liveness sidecar through the shared CSI socket.

## Risks and Test Signals
Risks include capability hardening breaking mount operations, numeric localhost health probes not matching the process listener, registrar version changes, and stale plugin registration files. Test signals are DaemonSet readiness on all Linux nodes, healthy 29653 probes, `CSINode` entries for `nfs.csi.k8s.io`, successful workload mounts after a rolling update, and no mount propagation warnings.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-snapshot-controller.yaml

## Purpose
This manifest deploys the v4.6.0 external snapshot controller. It updates the controller image to v6.3.3 and adds capability dropping for the container.

## Important APIs, Types, and Functions
The `Deployment` is `snapshot-controller` in `kube-system`, two replicas, `minReadySeconds: 15`, `maxSurge: 0`, `maxUnavailable: 1`, Linux node selector, control-plane tolerations, and `system-cluster-critical` priority. The container runs `snapshot-controller:v6.3.3`, `--v=2`, and leader election in `kube-system`, with `securityContext.capabilities.drop: [ALL]`.

## Control Flow, State, and Persistence
The elected controller replica reconciles snapshot CRDs, updates status and events, and uses a coordination lease. The standby replica provides failover while rolling updates preserve one available controller. Persistent state is entirely Kubernetes API state.

## Dependencies and Integration Points
It depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, and the NFS controller's `csi-snapshotter:v6.3.3`. It also relies on the CRDs being present long enough for readiness because the deployment comments document startup failure when v1 CRDs are missing.

## Risks and Test Signals
Risks include image/CRD skew, missing status verbs, capability drop incompatibility if the image expected extra Linux capabilities, and leader-election namespace errors. Test signals are ready replicas, one leader lease, snapshot status updates, no forbidden errors, and clean upgrade from v6.3.1.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/rbac-csi-nfs.yaml

## Purpose
This v4.6.0 RBAC file creates the NFS CSI service accounts and controller permissions. It is unchanged from v4.4.0 and v4.5.0 despite the controller upgrading to `csi-provisioner:v4.0.0`.

## Important APIs, Types, and Functions
Objects are `csi-nfs-controller-sa`, `csi-nfs-node-sa`, `nfs-external-provisioner-role`, and `nfs-csi-provisioner-binding`. The role covers PV get/list/watch/create/delete, PVC update, storage class reads, snapshot class/snapshot reads, snapshot content update/patch/status, event writes, CSINode/node reads, lease writes, and secret get.

## Control Flow, State, and Persistence
The file persists cluster authorization rules that gate every controller sidecar API operation. It does not grant a binding to the node service account because node plugin work primarily occurs through kubelet host paths and CSI registration.

## Dependencies and Integration Points
It is consumed by `csi-nfs-controller.yaml` and `csi-nfs-node.yaml`. Snapshot API rules integrate with CRDs and the sidecar snapshotter; lease rules integrate with leader election in `kube-system`.

## Risks and Test Signals
Risks include possible missing `patch` on persistentvolumes for the newer v4 provisioner, broad cluster access, and secret read permission. Test signals include no RBAC denials from the v4.6.0 controller, successful PV creation/deletion, leader-election leases, event writes, and snapshot content status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.6.0/rbac-snapshot-controller.yaml

## Purpose
This file authorizes the v4.6.0 snapshot controller. It is identical to the snapshot-controller RBAC files in v4.4.0, v4.5.0, and v4.7.0.

## Important APIs, Types, and Functions
It creates a `snapshot-controller` service account, a `snapshot-controller-runner` cluster role and binding, and a `snapshot-controller-leaderelection` role and binding. Permissions include PV/PVC reads, PVC update, event writes, snapshot class reads, snapshot content create/read/update/delete/patch plus status patch, snapshot update/patch plus status update/patch, and lease lifecycle verbs.

## Control Flow, State, and Persistence
Kubernetes authorization uses these resources while the snapshot controller reconciles custom resources and coordinates active leadership. The role binding is namespaced for the lease but the main snapshot permissions are cluster-scoped.

## Dependencies and Integration Points
It depends on snapshot CRDs and is referenced by the service account in `csi-snapshot-controller.yaml`. It integrates with the NFS CSI stack through shared snapshot resources that the NFS snapshotter fulfills.

## Risks and Test Signals
Risks include status updates failing if subresource verbs are incomplete, wrong lease namespace, and delete authority on snapshot contents. Test signals are successful leader election, event writes, snapshot content creation/deletion, status updates, and no authorization errors in logs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.6.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/crd-csi-snapshot.yaml

## Purpose
This v4.7.0 manifest installs the CSI snapshot CRDs for the NFS CSI bundle. The file is byte-identical to the v4.4.0 through v4.6.0 CRD files in this subset.

## Important APIs, Types, and Functions
It creates `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs under `snapshot.storage.k8s.io`, serving both `v1` and `v1beta1` and storing `v1`. Schemas define snapshot source references, CSI driver and class fields, deletion policies, snapshot handles, content references, readiness, restore size, error status, printer columns, and status subresources.

## Control Flow, State, and Persistence
The manifest has declarative API-install behavior only. Once present, it gives the snapshot controller and CSI snapshotter persistent custom resources for snapshot request, binding, and status state.

## Dependencies and Integration Points
It integrates with the v4.7.0 `snapshot-controller:v8.0.1` and `csi-snapshotter:v8.0.1` images, plus the NFS CSI driver name used in snapshot classes. Kubernetes must support apiextensions v1 and structural schemas.

## Risks and Test Signals
Risks include a large controller-sidecar version jump while the CRD schema stays unchanged, cluster-wide CRD update impact, and legacy `v1beta1` served-version expectations. Test signals are API discovery, no snapshot-controller CRD readiness failures, successful `VolumeSnapshot` creation and binding, and status updates on both snapshot and content resources.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-controller.yaml

## Purpose
This manifest deploys the v4.7.0 NFS CSI controller. It keeps the hardened v4.6.0 deployment shape and upgrades the provisioner, snapshotter, liveness probe, and NFS driver images.

## Important APIs, Types, and Functions
The `Deployment` is still one `csi-nfs-controller` replica in `kube-system` with hostNetwork, Linux node selection, control-plane tolerations, and shared `/csi/csi.sock`. Containers are `csi-provisioner:v5.0.1`, `csi-snapshotter:v8.0.1`, `livenessprobe:v2.13.1`, and `nfsplugin:v4.7.0`. Sidecars drop all capabilities, the NFS container is privileged with `SYS_ADMIN`, and health probing uses `--http-endpoint=localhost:29652` plus an HTTP liveness probe to localhost port 29652.

## Control Flow, State, and Persistence
The controller creates a pod-local CSI socket, sidecars run leader-elected Kubernetes watch loops, and the NFS driver performs controller-side mount/directory work through host networking and host pod mount access. Persistent state remains in PV/PVC/snapshot custom resources, events, coordination leases, and host-mounted kubelet pod directories.

## Dependencies and Integration Points
It depends on updated RBAC, especially because v4.7.0 RBAC adds PV patch permission, as well as the `CSIDriver`, snapshot CRDs, snapshot controller v8.0.1, and registry image availability. It integrates with storage classes and snapshot classes naming `nfs.csi.k8s.io`.

## Risks and Test Signals
Risks include major upgrades to `csi-provisioner:v5.0.1` and snapshotter v8.0.1, RBAC incompatibility if older RBAC is reused, and privileged host mount behavior. Test signals are no provisioner RBAC denials, healthy 29652 probes, successful PVC create/delete including PV patch operations, snapshot create/delete with v8 sidecars, and stable rollout from v4.6.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-driverinfo.yaml

## Purpose
This file registers the v4.7.0 NFS CSI driver with Kubernetes. It is the same `CSIDriver` manifest used in the earlier release directories in this subset.

## Important APIs, Types, and Functions
The object is `storage.k8s.io/v1` `CSIDriver` named `nfs.csi.k8s.io`. It declares no attach requirement, persistent lifecycle support, and file-based fsGroup policy.

## Control Flow, State, and Persistence
The `CSIDriver` is persistent cluster metadata consulted by Kubernetes and kubelet during volume admission, scheduling, and mount handling. It does not execute logic, but it changes the control-plane path by avoiding attach/detach for NFS volumes.

## Dependencies and Integration Points
It must match the v4.7.0 node plugin registration and storage class provisioner name. It integrates with `csi-nfs-controller.yaml`, `csi-nfs-node.yaml` from the same release, and user workloads consuming NFS PVCs.

## Risks and Test Signals
Risks include name mismatches during upgrades, old clusters lacking the selected `fsGroupPolicy` behavior, and NFS export permissions conflicting with fsGroup expectations. Test signals are a present `CSIDriver`, matching `CSINode` registrations, no VolumeAttachment resources for NFS PVs, and successful pod mount tests using a v4.7.0 provisioned PVC.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.7.0/csi-nfs-driverinfo.yaml -->
