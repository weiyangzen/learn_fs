# subset-b-000358 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
Helm template for installing CSI external-snapshotter CRDs with the v4.7.0 NFS chart. It is gated by `externalSnapshotter.enabled` and `externalSnapshotter.customResourceDefinitions.enabled`, so snapshot APIs are only emitted when the chart is asked to manage them.

## Important APIs, Types, And Functions
Defines Kubernetes `CustomResourceDefinition` objects for `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` in `snapshot.storage.k8s.io`. Each CRD serves `v1`, keeps deprecated `v1beta1` schemas as non-storage/non-served compatibility definitions, exposes printer columns, and uses status subresources where relevant.

## Control Flow
At render time Helm either emits all three CRDs or nothing. Once applied, Kubernetes admission validates snapshot source one-of fields, required driver/deletion-policy/source/reference fields, restore-size formats, status fields, and class parameters.

## State And Persistence
CRDs persist as cluster-scoped API extensions and include `helm.sh/resource-policy: keep`, preventing Helm uninstall from deleting them. Snapshot resources created through these CRDs persist cluster state for PVC snapshots and their backing CSI handles.

## Dependencies And Integration Points
Requires `apiextensions.k8s.io/v1`, the snapshot controller, csi-snapshotter sidecar, and CSI drivers using `CreateSnapshot`, `ListSnapshots`, and snapshot content binding semantics. It integrates with the chart's optional snapshot controller and RBAC templates.

## Risks And Edge Cases
Installing CRDs from a workload chart can conflict with cluster-managed CRDs or newer external-snapshotter versions. Keeping CRDs on uninstall avoids data loss but leaves lifecycle drift. Consumers must verify bidirectional `VolumeSnapshot` and `VolumeSnapshotContent` binding before restore.

## Test Signals
Primary signal is `helm template` with both snapshot flags enabled, followed by Kubernetes dry-run or CRD schema validation. Runtime signals are successful snapshot controller startup and accepted `VolumeSnapshot` objects.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
Renders the v4.7.0 controller `Deployment` for the CSI NFS driver. The pod hosts control-plane sidecars plus the NFS CSI plugin in controller mode so dynamic provisioning, snapshotting, liveness, and server-side directory management run together.

## Important APIs, Types, And Functions
Uses `apps/v1 Deployment`, `.Values.controller.*`, `.Values.image.*`, `.Values.driver.*`, `include "nfs.labels"`, `hasPrefix`, `toYaml`, `nindent`, and Helm release namespace templating. Containers are `csi-provisioner`, `csi-snapshotter`, `liveness-probe`, and privileged `nfs`.

## Control Flow
Helm resolves image repositories, resource blocks, scheduling settings, and command-line flags. The provisioner connects to `/csi/csi.sock`, uses leader election, enables extra metadata, sets `HonorPVReclaimPolicy=false`, and waits up to 1200 seconds. The NFS container starts the CSI endpoint, mounts kubelet pods with bidirectional propagation, and receives node name from the pod spec.

## State And Persistence
State is mostly external: Kubernetes leases for leader election, PV/PVC/snapshot objects, the host kubelet pod mount tree, and NFS server paths. In v4.7.0 the controller also mounts an `emptyDir` at `.Values.controller.workingMountDir` for temporary NFS mounts.

## Dependencies And Integration Points
Depends on RBAC in `rbac-csi-nfs.yaml`, service accounts, snapshot CRDs if snapshotting is used, host networking for NFS mount operations, kubelet directory layout, and the `nfsplugin` binary flags defined by `cmd/nfsplugin/main.go`.

## Risks And Edge Cases
The `nfs` container is privileged with `SYS_ADMIN`, so scheduling and namespace isolation matter. `HonorPVReclaimPolicy=false` may ignore PV reclaim policy behavior that later chart versions enable. The explicit working mount `emptyDir` can hide host paths and differs from v4.8.0+.

## Test Signals
Use `helm template` and Kubernetes schema validation. Runtime checks include controller pod readiness, liveness endpoint on the configured health port, leader election leases, provisioned PVs, and successful cleanup respecting the configured delete policy.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
Declares the CSI NFS driver to Kubernetes through a `CSIDriver` object for the v4.7.0 chart.

## Important APIs, Types, And Functions
Uses `storage.k8s.io/v1 CSIDriver`, `.Values.driver.name`, `.Values.feature.enableInlineVolume`, and `.Values.feature.enableFSGroupPolicy`. The spec sets `attachRequired: false`, includes `Persistent` lifecycle mode, optionally includes `Ephemeral`, and optionally sets `fsGroupPolicy: File`.

## Control Flow
Helm always renders this object. Feature values determine whether inline CSI volumes and FSGroup policy are advertised to kubelet and admission.

## State And Persistence
The object is cluster-scoped Kubernetes configuration. It persists the driver's attach behavior and volume lifecycle capabilities, but it does not store volume data.

## Dependencies And Integration Points
The driver name must match the NFS plugin `--drivername` flag and StorageClass provisioner name. Kubelet, scheduler, and CSI sidecars use the `CSIDriver` object to understand whether attach operations are required and how FSGroup should be applied.

## Risks And Edge Cases
Mismatched driver names break provisioning and node registration. Enabling inline volumes or FSGroup policy on unsupported clusters or incompatible driver behavior can cause scheduling or mount failures.

## Test Signals
Validate with `kubectl get csidriver nfs.csi.k8s.io` after install, plus pod mount tests that confirm no attach phase is required.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
Renders the v4.7.0 node `DaemonSet` for the CSI NFS driver. It runs one pod per eligible Linux node to register the CSI socket with kubelet, serve node-stage/node-publish operations, and expose liveness health.

## Important APIs, Types, And Functions
Uses `apps/v1 DaemonSet`, `node-driver-registrar`, `liveness-probe`, and privileged `nfs` containers. Key values include `.Values.node.*`, `.Values.image.*`, `.Values.kubeletDir`, `.Values.feature.propagateHostMountOptions`, and the driver name and mount permissions.

## Control Flow
Helm renders scheduling, resources, and optional image pull secrets. Kubelet starts the pod on nodes, the registrar points kubelet at `${kubeletDir}/plugins/csi-nfsplugin/csi.sock`, the NFS plugin listens on `unix:///csi/csi.sock`, and liveness probes both the sidecar and plugin endpoint.

## State And Persistence
The DaemonSet uses host paths for the CSI plugin socket, plugin registry, kubelet pod mount directory, and optionally `/etc/nfsmount.conf` plus `/etc/nfsmount.conf.d`. Volume mount propagation is bidirectional for kubelet pod mounts.

## Dependencies And Integration Points
Requires kubelet plugin directories, Linux nodes, privileged mount capabilities, service account/RBAC, and the same driver name as the `CSIDriver` and StorageClass. Host networking is required because losing the original NFS connection can break mounts.

## Risks And Edge Cases
Privileged hostPath access is broad and sensitive. Wrong `kubeletDir` breaks registration. Optional propagation of host NFS mount config can create host coupling. The template uses controller DNS policy for node pods, which is intentional in this chart but ties node networking to controller defaults.

## Test Signals
Signals include `CSINode` entries, node-driver-registrar liveness success, socket creation under kubelet plugins, pod volume mounts, and host mount propagation behavior during workload pod restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
Optionally deploys the external snapshot controller for the v4.7.0 chart when `.Values.externalSnapshotter.enabled` is true.

## Important APIs, Types, And Functions
Uses an `apps/v1 Deployment` named from `.Values.externalSnapshotter.name`. It supports custom labels/annotations, replica count, priority class, image pull secrets, resources, and the `snapshot-controller` image from `.Values.image.externalSnapshotter`.

## Control Flow
Helm emits nothing if snapshotter support is disabled. If enabled, Kubernetes rolls a Linux-only deployment with leader election in the release namespace. `minReadySeconds: 15` accounts for controller startup behavior when v1 CRDs are missing.

## State And Persistence
The deployment itself has no durable storage. Runtime state is held in snapshot API objects, events, and leader election leases. It watches PVCs, PVs, `VolumeSnapshot*` resources, and status subresources through RBAC.

## Dependencies And Integration Points
Requires snapshot CRDs, RBAC from `rbac-snapshot-controller.yaml`, and a controller image compatible with the installed CRDs. It coordinates with the NFS CSI `csi-snapshotter` sidecar, which performs CSI calls.

## Risks And Edge Cases
Enabling it in clusters that already provide a snapshot controller can create duplicate controllers. If CRDs are absent or incompatible, readiness and controller loops fail. The template reuses controller tolerations, so scheduling assumptions are inherited.

## Test Signals
Render with `externalSnapshotter.enabled=true`, verify deployment readiness, leader election lease creation, and successful `VolumeSnapshot` binding/status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
Creates service accounts and core RBAC needed by the v4.7.0 CSI NFS controller and node components.

## Important APIs, Types, And Functions
Conditionally emits `ServiceAccount` objects when `.Values.serviceAccount.create` is true and a `ClusterRole` plus `ClusterRoleBinding` when `.Values.rbac.create` is true. Permissions cover PVs, PVCs, StorageClasses, snapshots, events, CSINodes, nodes, leases, and secrets.

## Control Flow
Helm controls whether accounts and RBAC are rendered. The controller service account is bound to a cluster role named from `.Values.rbac.name`, while the node account is created but not bound here because node operations mostly depend on registration and host access.

## State And Persistence
RBAC and service accounts are persistent cluster objects. They grant ongoing permissions to sidecars and remain until deleted by Helm or cluster operations.

## Dependencies And Integration Points
Integrates with `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, provisioner leader election, event recording, PV/PVC reconciliation, and optional snapshot sidecar behavior inside the controller deployment.

## Risks And Edge Cases
The provisioner role can create, patch, and delete PVs and update snapshot contents, so excessive namespace reuse or service-account sharing increases blast radius. Disabling RBAC requires equivalent external permissions.

## Test Signals
Use `kubectl auth can-i` for PV/PVC, lease, event, and snapshot verbs under the controller service account. Runtime failures appear as sidecar forbidden errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
Defines optional RBAC for the external snapshot controller in the v4.7.0 chart.

## Important APIs, Types, And Functions
Gated by `.Values.externalSnapshotter.enabled`. Emits a `ServiceAccount`, cluster-scoped `ClusterRole`/`ClusterRoleBinding`, and namespace-scoped `Role`/`RoleBinding` for leader election. Permissions cover PVs, PVCs, events, VolumeSnapshot classes/contents/snapshots, status subresources, and optionally nodes for distributed snapshotting.

## Control Flow
When enabled, the snapshot controller gets cluster-wide watch/update/delete permissions for snapshot reconciliation and namespaced lease permissions in the release namespace. The optional distributed snapshotting branch adds node list/watch/get access.

## State And Persistence
RBAC objects persist in the cluster and authorize the controller to mutate snapshot API state. The actual reconciliation state is in snapshot objects and leader election leases.

## Dependencies And Integration Points
Works with `csi-snapshot-controller.yaml` and `crd-csi-snapshot.yaml`. It must match external-snapshotter controller expectations for the image version configured in values.

## Risks And Edge Cases
Cluster-wide snapshot permissions are powerful. If multiple chart releases use the same external snapshotter name, role and binding names can collide. Missing status permissions break readiness and snapshot status updates.

## Test Signals
Check `kubectl auth can-i` for `volumesnapshotcontents/status patch` and `volumesnapshots/status update` as the snapshot service account, then create/delete a snapshot to verify controller reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
Optionally renders an example NFS `StorageClass` for the v4.7.0 chart when `.Values.storageClass.create` is true.

## Important APIs, Types, And Functions
Uses `storage.k8s.io/v1 StorageClass`, `.Values.storageClass.name`, `.Values.storageClass.parameters`, `reclaimPolicy`, `volumeBindingMode`, and `mountOptions`. The provisioner is hard-coded to `nfs.csi.k8s.io` in this version.

## Control Flow
If enabled, Helm emits one StorageClass with chart labels, optional parameters, reclaim policy, binding mode, and mount options. Workload PVCs then trigger csi-provisioner to create NFS-backed PVs.

## State And Persistence
The StorageClass is cluster-scoped configuration. It does not hold data, but its parameters are copied into dynamic provisioning decisions and influence PV lifecycle.

## Dependencies And Integration Points
Provisioner name must match the driver name. Parameters such as NFS server, share, subdirectory, mount permissions, and optional provisioner secret references are documented in values.

## Risks And Edge Cases
Hard-coding the provisioner can drift if `.Values.driver.name` is changed. There is no annotations block in v4.7.0, so marking it default requires external patching.

## Test Signals
Render with `storageClass.create=true`, create a PVC using the class, and verify PV creation, mount options, and reclaim behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/values.yaml

## Purpose
Default configuration for the v4.7.0 CSI NFS Helm chart.

## Important APIs, Types, And Functions
Defines image repositories/tags, service-account names, RBAC naming, driver name and mount permissions, feature flags, kubelet directory, controller/node scheduling and resources, external snapshotter settings, image pull secrets, and example StorageClass parameters.

## Control Flow
Templates read these values to decide which objects render, which images run, what command flags are passed, and how pods are scheduled. v4.7.0 sets NFS plugin `v4.7.0`, csi-provisioner `v5.0.1`, csi-snapshotter and snapshot-controller `v8.0.1`, livenessprobe `v2.13.1`, and registrar `v2.11.1`.

## State And Persistence
Values are Helm release input. They become persisted Kubernetes object specs and influence persistent resources such as PVs, StorageClasses, CRDs, and RBAC.

## Dependencies And Integration Points
Couples every template in this chart. Key integrations include `driver.name` matching the `CSIDriver` and StorageClass, `kubeletDir` matching host kubelet layout, and snapshot flags controlling CRD/controller/RBAC emission.

## Risks And Edge Cases
Default snapshotter is disabled, StorageClass creation is disabled, and controller/node pods require privileged NFS mount capability. The example StorageClass lacks annotations in this version. Changing `driver.name` can break the v4.7.0 storageclass template because it hard-codes the provisioner.

## Test Signals
`helm template` across default and enabled-feature values, plus install smoke tests for provisioning, node registration, and optional snapshotting.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/Chart.yaml

## Purpose
Helm chart metadata for CSI NFS driver release v4.8.0.

## Important APIs, Types, And Functions
Uses Helm chart API `apiVersion: v1`, `name: csi-driver-nfs`, `description: CSI NFS Driver for Kubernetes`, `version: v4.8.0`, and `appVersion: v4.8.0`.

## Control Flow
Helm reads this metadata when packaging, installing, listing releases, and resolving chart identity. It does not render Kubernetes resources itself.

## State And Persistence
The metadata is stored in Helm release records and chart archives, identifying the chart and application version used for an installation.

## Dependencies And Integration Points
Integrates with values and templates under the same chart directory. The `appVersion` should align with `.Values.image.nfs.tag` and release artifacts.

## Risks And Edge Cases
Version drift between `Chart.yaml`, image tags, and source code can confuse upgrades and provenance. Since this is Helm v1 chart metadata, compatibility depends on the consuming Helm tooling.

## Test Signals
`helm lint`, `helm package`, and comparing rendered image tags against `appVersion` are the main signals.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
Installs the same external-snapshotter CRDs as the v4.7.0 chart, gated by `externalSnapshotter.enabled` and CRD management values.

## Important APIs, Types, And Functions
Defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs with v1 storage schemas, deprecated v1beta1 definitions, printer columns, OpenAPI validation, and status subresources.

## Control Flow
Helm emits all CRDs only when snapshotter and CRD installation are enabled. Kubernetes then handles validation, stored versions, status updates, and discovery for snapshot APIs.

## State And Persistence
The CRDs are cluster-scoped and annotated with Helm keep policy, so they survive chart uninstall. They define the persistent API surface for snapshot request, class, and content objects.

## Dependencies And Integration Points
Requires compatible external-snapshotter components and cluster support for `apiextensions.k8s.io/v1`. The snapshot controller and sidecar use these resources for binding PVC snapshots to CSI snapshot handles.

## Risks And Edge Cases
This file is byte-identical to v4.7.0 and v4.9.0 in this source set, so CRD behavior does not move with the chart image releases. Cluster-wide CRD ownership can conflict with separately installed snapshot APIs.

## Test Signals
Render with snapshot flags enabled, apply via dry-run, and verify snapshot resources can be created and reconciled by the configured controller.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
Renders the v4.8.0 controller `Deployment` for CSI NFS control-plane functions.

## Important APIs, Types, And Functions
Defines an `apps/v1 Deployment` with `csi-provisioner`, `csi-snapshotter`, `liveness-probe`, and privileged `nfs` containers. Uses Helm values for images, leader election namespace, resource blocks, controller scheduling, driver name, mount permissions, working mount directory, and delete policy.

## Control Flow
The provisioner connects to the shared CSI socket, runs leader election, creates metadata, and sets `--feature-gates=HonorPVReclaimPolicy=true`. The NFS container starts the CSI endpoint with controller flags and mounts kubelet pods with bidirectional propagation. Images can be resolved through `baseRepo` when repository values start with `/`.

## State And Persistence
Persistent state is in Kubernetes PV/PVC/snapshot objects, events, leases, and NFS server directories. Unlike v4.7.0, this template no longer mounts an `emptyDir` at `.Values.controller.workingMountDir`.

## Dependencies And Integration Points
Integrates with controller service account/RBAC, node daemonset, snapshot CRDs/RBAC when enabled, kubelet host paths, and the `nfsplugin` flags in `cmd/nfsplugin/main.go`.

## Risks And Edge Cases
The privileged controller can mount NFS and host kubelet pod paths, so node placement matters. The removal of the temporary working mount volume changes filesystem behavior compared with v4.7.0. Reclaim policy honoring can alter deletion outcomes during upgrades.

## Test Signals
Check rendered deployment diffs from v4.7.0, controller pod readiness, PV deletion behavior with different reclaim policies, leader leases, and liveness endpoint status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
Declares the v4.8.0 chart's CSI NFS driver metadata to Kubernetes.

## Important APIs, Types, And Functions
Emits `storage.k8s.io/v1 CSIDriver` using `.Values.driver.name`, `attachRequired: false`, persistent lifecycle mode, optional ephemeral lifecycle mode, and optional `fsGroupPolicy: File`.

## Control Flow
Always rendered by Helm. Feature flags add optional lines to the `CSIDriver` spec before Kubernetes consumes the object for CSI scheduling and kubelet behavior.

## State And Persistence
The cluster-scoped `CSIDriver` object persists driver capabilities. It does not manage NFS data directly.

## Dependencies And Integration Points
Must align with the driver name in controller/node plugin args and StorageClass provisioner. Kubelet uses it with the node-driver-registrar socket registration.

## Risks And Edge Cases
This file is byte-identical to v4.7.0 and v4.9.0 in this set. A custom driver name must be propagated everywhere or dynamic provisioning and registration fail.

## Test Signals
`kubectl get csidriver`, rendered spec inspection, and successful PVC mount without an attach operation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
Renders the v4.8.0 node `DaemonSet` for CSI socket registration and node-side NFS mount operations.

## Important APIs, Types, And Functions
Uses `apps/v1 DaemonSet`, liveness-probe, node-driver-registrar, and privileged NFS plugin containers. Values control kubelet paths, resources, image tags, mount options propagation, scheduling, health ports, and driver flags.

## Control Flow
Each Linux node gets a pod. The registrar registers the plugin socket path with kubelet, the NFS plugin serves CSI node calls from `/csi/csi.sock`, and liveness probes monitor both the registrar and plugin HTTP endpoint.

## State And Persistence
Uses hostPath volumes for plugin socket, plugin registry, and kubelet pods. Optional host NFS mount configuration files/directories are mounted when `propagateHostMountOptions` is true. Mount state persists on the node through kubelet and host mount namespaces.

## Dependencies And Integration Points
Depends on kubelet directory layout, privileged mount capability, service account existence, `CSIDriver`, and workload PVCs referencing the NFS StorageClass.

## Risks And Edge Cases
This template is byte-identical across v4.7.0, v4.8.0, and v4.9.0 here. Wrong host paths or missing host networking break registration and mount continuity. Privileged hostPath access should be treated as node-level trust.

## Test Signals
DaemonSet rollout, registrar liveness, `CSINode` plugin entries, workload pod NFS mounts, and mount option propagation checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
Optionally renders the snapshot-controller deployment for the v4.8.0 chart.

## Important APIs, Types, And Functions
Uses `apps/v1 Deployment`, `.Values.externalSnapshotter.*`, `.Values.image.externalSnapshotter`, optional image pull secrets, labels, annotations, resources, and leader election arguments.

## Control Flow
If the snapshotter is enabled, Helm emits a Linux deployment with `minReadySeconds: 15`, rolling update parameters, seccomp defaulting, and leader election in the release namespace. If disabled, it emits nothing.

## State And Persistence
No local storage. Runtime state consists of Kubernetes snapshot resources, events, and lease objects.

## Dependencies And Integration Points
Requires snapshot CRDs and RBAC, and coordinates with CSI sidecars in the controller deployment. The image tag is supplied by values and should match the CRD version.

## Risks And Edge Cases
This template is byte-identical across the three chart versions in this group. Duplicate cluster snapshot controllers can race. Missing CRDs cause readiness and reconcile failures.

## Test Signals
Render with snapshotter enabled, verify deployment readiness and leases, and exercise snapshot create/delete flows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
Creates the v4.8.0 chart's service accounts and core CSI NFS RBAC.

## Important APIs, Types, And Functions
Conditionally creates controller and node `ServiceAccount` resources plus a cluster role/binding for the external provisioner role. The role grants PV/PVC, StorageClass, snapshot, event, CSINode, node, lease, and secret read permissions as required by the sidecars.

## Control Flow
Rendered based on `.Values.serviceAccount.create` and `.Values.rbac.create`. The controller service account receives the cluster role; the node service account is available for the daemonset.

## State And Persistence
RBAC resources and service accounts persist as Kubernetes authorization state. They have no storage of their own but authorize mutations of durable PV and snapshot resources.

## Dependencies And Integration Points
Used by `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, csi-provisioner, csi-snapshotter sidecar, leader election, and event recording.

## Risks And Edge Cases
This file is byte-identical across v4.7.0, v4.8.0, and v4.9.0 here. Disabling RBAC shifts responsibility to the installer. Broad PV/snapshot permissions can be sensitive in shared clusters.

## Test Signals
`kubectl auth can-i` under the controller service account and absence of forbidden errors in provisioner/snapshotter logs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
Provides optional RBAC for the external snapshot controller in the v4.8.0 chart.

## Important APIs, Types, And Functions
When enabled, emits a snapshot-controller `ServiceAccount`, cluster role/binding, and namespaced role/binding for leader-election leases. Permissions cover snapshots, snapshot contents/classes, PVCs, PVs, events, statuses, and optionally nodes.

## Control Flow
The template is skipped unless `.Values.externalSnapshotter.enabled` is true. The distributed snapshotting flag conditionally adds node permissions.

## State And Persistence
RBAC state persists in Kubernetes and controls the controller's ability to reconcile snapshot API objects and update status.

## Dependencies And Integration Points
Pairs with `csi-snapshot-controller.yaml` and snapshot CRDs. It must remain compatible with the external-snapshotter image version configured in values.

## Risks And Edge Cases
This file is byte-identical across v4.7.0, v4.8.0, and v4.9.0 here. Name collisions are possible across releases if the same snapshotter name is reused. Missing status permissions cause partial reconciliation.

## Test Signals
Authorization checks for snapshot status verbs and an end-to-end snapshot lifecycle test.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
Optionally renders an NFS StorageClass for the v4.8.0 chart.

## Important APIs, Types, And Functions
Uses `storage.k8s.io/v1 StorageClass`, labels, `.Values.storageClass.annotations`, parameters, reclaim policy, volume binding mode, and mount options. The provisioner remains hard-coded as `nfs.csi.k8s.io` in this version.

## Control Flow
When `storageClass.create` is true, Helm emits one StorageClass and includes an annotations block even if no annotations are provided. PVCs selecting the class trigger the controller provisioner.

## State And Persistence
The StorageClass is cluster-scoped configuration that persists provisioning defaults. Parameters flow into PV creation and can reference provisioner secrets for mount options during delete.

## Dependencies And Integration Points
Depends on the NFS CSI provisioner deployment and driver name matching the hard-coded provisioner. Values include example server/share/subdirectory parameters and optional default-class annotation.

## Risks And Edge Cases
The annotations block is new compared with v4.7.0, but the provisioner remains hard-coded, so custom `driver.name` can still diverge. Empty annotations should be checked in rendered YAML for valid formatting.

## Test Signals
`helm template` with and without annotations, StorageClass creation, PVC dynamic provisioning, and default-class behavior if the annotation is set.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/values.yaml

## Purpose
Default configuration for the v4.8.0 CSI NFS Helm chart.

## Important APIs, Types, And Functions
Configures chart images, service accounts, RBAC, driver name, feature flags, kubelet directory, controller and node pod defaults, external snapshotter, image pull secrets, and example StorageClass settings.

## Control Flow
Templates consume these values for rendering Kubernetes objects and command arguments. v4.8.0 updates NFS plugin image to `v4.8.0` and csi-provisioner to `v5.0.2` while keeping snapshotter, liveness, registrar, and snapshot-controller tags aligned with v4.7.0 defaults.

## State And Persistence
Values are installed into Helm release metadata and rendered Kubernetes object specs. Resource limits, feature flags, and StorageClass parameters become persistent cluster configuration.

## Dependencies And Integration Points
Controls every chart template. Important cross-file links are `driver.name`, `kubeletDir`, snapshotter flags, controller/node liveness ports, and StorageClass annotations introduced in the example comments.

## Risks And Edge Cases
Snapshotter and StorageClass creation remain disabled by default. Controller and node NFS containers require privileged operation. The default-class annotation is commented and must be enabled explicitly.

## Test Signals
`helm lint`, rendered YAML diffs from v4.7.0, install smoke tests, and provisioning/snapshotting tests under enabled feature flags.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/Chart.yaml

## Purpose
Helm chart metadata for CSI NFS driver release v4.9.0.

## Important APIs, Types, And Functions
Declares Helm `apiVersion: v1`, `name: csi-driver-nfs`, description, `version: v4.9.0`, and `appVersion: v4.9.0`.

## Control Flow
Helm uses this metadata during chart loading, packaging, installation, upgrade, and release display. It does not directly render resources.

## State And Persistence
The metadata is persisted in packaged charts and Helm release records, identifying this release as v4.9.0.

## Dependencies And Integration Points
Should align with values defaults, particularly the NFS plugin image tag `v4.9.0`, and with release automation such as Cloud Build image publishing.

## Risks And Edge Cases
Version mismatch between chart metadata and image tags can make upgrades unclear. Chart API v1 metadata is simple but less expressive than v2 dependency metadata.

## Test Signals
Run `helm lint`, package the chart, and compare rendered image tags and release labels against this metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
Optionally installs external-snapshotter CRDs for the v4.9.0 chart.

## Important APIs, Types, And Functions
Defines CRDs for namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. The schemas include v1 storage versions, deprecated v1beta1 compatibility schemas, source one-of constraints, status subresources, and printer columns.

## Control Flow
Helm emits all CRDs only when both snapshotter and CRD installation flags are true. Kubernetes stores the definitions and validates subsequent snapshot API objects against the OpenAPI schemas.

## State And Persistence
CRDs persist as cluster API extensions and use `helm.sh/resource-policy: keep`. The resources they enable store snapshot requests, classes, content handles, status, readiness, restore size, and errors.

## Dependencies And Integration Points
Requires snapshot controller and csi-snapshotter sidecar compatible with the v1 snapshot APIs. Integrates with RBAC and the optional snapshot controller deployment in this chart.

## Risks And Edge Cases
Byte-identical to the v4.7.0 and v4.8.0 CRD templates here, so CRD versions do not advance in v4.9.0. CRD ownership by Helm can conflict with cluster-level snapshot installations, and keep policy leaves resources after uninstall.

## Test Signals
`helm template` with snapshot CRDs enabled, Kubernetes server-side dry-run, and end-to-end `VolumeSnapshot` creation and restore checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
Renders the v4.9.0 CSI NFS controller `Deployment` with updated control-plane scheduling logic.

## Important APIs, Types, And Functions
Defines an `apps/v1 Deployment` with provisioner, snapshotter, liveness probe, and privileged NFS plugin containers. It uses Helm functions `contains`, `tpl`, `with`, `toYaml`, `hasPrefix`, and values for images, resources, driver flags, leader election, tolerations, node selectors, and affinity.

## Control Flow
The controller always uses host networking. If `.Values.controller.affinity` already contains `nodeSelectorTerms`, it is rendered directly. Otherwise `runOnControlPlane` and `runOnMaster` generate required node affinity rather than nodeSelector labels. The provisioner honors PV reclaim policy, and all sidecars communicate over `/csi/csi.sock`.

## State And Persistence
State lives in PV/PVC/snapshot objects, events, leader-election leases, host kubelet pod mounts, and NFS server directories. The socket directory is an `emptyDir`; kubelet pods are mounted from hostPath.

## Dependencies And Integration Points
Depends on RBAC, service accounts, kubelet host paths, snapshot CRDs/RBAC if enabled, image tags from v4.9.0 values, and `nfsplugin` controller flags including working mount directory and default delete policy.

## Risks And Edge Cases
The v4.9.0 affinity branch checks rendered affinity text for `nodeSelectorTerms`, which can miss nonstandard affinity shapes. Switching from nodeSelector labels to required node affinity changes scheduling semantics for control-plane placement. Privileged `SYS_ADMIN` remains a high-trust requirement.

## Test Signals
Render tests for custom affinity, `runOnControlPlane`, and `runOnMaster`; controller rollout; leader election; PV reclaim behavior; provisioning and delete policy tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
Declares the v4.9.0 CSI NFS driver to Kubernetes.

## Important APIs, Types, And Functions
Emits `storage.k8s.io/v1 CSIDriver` with driver name from `.Values.driver.name`, `attachRequired: false`, persistent lifecycle mode, optional ephemeral lifecycle mode, and optional `fsGroupPolicy: File`.

## Control Flow
Rendered unconditionally. Feature flags determine optional `volumeLifecycleModes` and FSGroup behavior in the final object.

## State And Persistence
The cluster-scoped object persists capability metadata used by kubelet and scheduler. It does not persist volume contents.

## Dependencies And Integration Points
Must match controller/node `--drivername`, node-driver-registrar registration, and StorageClass provisioner. Enables Kubernetes to skip attach operations for NFS.

## Risks And Edge Cases
Byte-identical to earlier versions in this set. Driver-name drift or unsupported feature flags can break provisioning or pod volume admission.

## Test Signals
Check rendered `CSIDriver`, `CSINode` plugin registration, and a PVC-backed pod that mounts without attach.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
Renders the v4.9.0 node `DaemonSet` for kubelet CSI registration and node-side NFS publish operations.

## Important APIs, Types, And Functions
Uses liveness-probe, node-driver-registrar, and privileged NFS plugin containers; hostPath volumes for socket, kubelet pods, and registration; optional host NFS config mounts; and values for node scheduling, resources, health port, log level, and image tags.

## Control Flow
Kubernetes schedules one pod per matching Linux node. The registrar advertises the kubelet registration path, the NFS plugin listens on the CSI socket, liveness checks use the configured health port, and optional host mount configuration is mounted when enabled.

## State And Persistence
HostPath socket and registration directories persist on nodes. NFS mount state and workload pod mounts are mediated through the kubelet pod directory with bidirectional propagation.

## Dependencies And Integration Points
Works with `CSIDriver`, kubelet, controller-provisioned PVs, host networking, and the NFS plugin binary. The driver name must match StorageClass and controller settings.

## Risks And Edge Cases
Byte-identical to v4.7.0 and v4.8.0 in this source set. Incorrect `kubeletDir`, missing registration directory, or restricted privileged execution blocks mounts. Host config propagation can make behavior node-dependent.

## Test Signals
DaemonSet readiness, registrar probe success, socket files under kubelet plugins, `CSINode` state, and workload pod mount/unmount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
Optionally deploys the external snapshot controller for the v4.9.0 chart.

## Important APIs, Types, And Functions
Defines an `apps/v1 Deployment` named from `.Values.externalSnapshotter.name`, with configurable image, resources, labels, annotations, replicas, priority class, image pull secrets, and leader-election flags.

## Control Flow
Rendered only when `externalSnapshotter.enabled` is true. The deployment runs on Linux nodes, uses release-namespace leader election, and waits at least 15 seconds before readiness to account for CRD availability behavior.

## State And Persistence
No persistent volume state. It persists effects through snapshot resources, status updates, events, and leader election leases.

## Dependencies And Integration Points
Requires snapshot CRDs and RBAC from this chart or an equivalent cluster install. Coordinates with the CSI snapshotter sidecar in the controller deployment.

## Risks And Edge Cases
Byte-identical to previous chart versions in this group. Enabling it alongside a cluster-managed snapshot controller can produce duplicate reconciliation. CRD absence or version mismatch is a primary failure mode.

## Test Signals
Snapshot controller deployment readiness, lease acquisition, no forbidden errors, and successful snapshot API lifecycle tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
Creates service accounts and controller RBAC for the v4.9.0 CSI NFS chart.

## Important APIs, Types, And Functions
Conditionally renders controller/node `ServiceAccount` resources plus the external provisioner `ClusterRole` and `ClusterRoleBinding`. Permissions include PV creation/deletion/patching, PVC updates, StorageClass reads, snapshot object access, event writes, CSINode and node reads, lease management, and secret reads.

## Control Flow
Service accounts and RBAC are gated separately. The controller service account is bound to cluster permissions when RBAC is enabled, while node service account creation supports the DaemonSet.

## State And Persistence
Authorization objects persist in the cluster and grant ongoing access to Kubernetes storage resources. They do not persist application data.

## Dependencies And Integration Points
Used by the v4.9.0 controller and node templates, csi-provisioner, csi-snapshotter, leader election, event recording, and secret-backed mount options.

## Risks And Edge Cases
Byte-identical to v4.7.0 and v4.8.0 here. The controller role has broad storage privileges. If RBAC is disabled, external roles must include all sidecar-required verbs.

## Test Signals
`kubectl auth can-i` for controller verbs and sidecar logs free of RBAC denial messages.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
Defines optional RBAC for the v4.9.0 external snapshot controller.

## Important APIs, Types, And Functions
When enabled, emits a snapshot-controller service account, cluster role/binding for snapshot reconciliation, and namespaced role/binding for leader election leases. Optional distributed snapshotting adds node read/watch permissions.

## Control Flow
Skipped when `externalSnapshotter.enabled` is false. When rendered, the controller can read PV/PVC objects, create/update/delete snapshot contents, update snapshot statuses, write events, and manage its lease.

## State And Persistence
RBAC resources persist as cluster authorization state. Snapshot controller state persists in snapshot API objects and leases.

## Dependencies And Integration Points
Pairs with `csi-snapshot-controller.yaml` and the snapshot CRD template. Permission shape must match the configured external-snapshotter image.

## Risks And Edge Cases
Byte-identical to prior versions in this set. Cluster-wide permissions and naming collisions across releases are the main risks. Missing leader-election role prevents stable controller operation.

## Test Signals
Authorization checks for snapshot status and content verbs, plus end-to-end snapshot creation and deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
Optionally renders a v4.9.0 NFS StorageClass.

## Important APIs, Types, And Functions
Uses `storage.k8s.io/v1 StorageClass`, labels, optional annotations, values-driven parameters, reclaim policy, volume binding mode, mount options, and a provisioner value set to `.Values.driver.name`.

## Control Flow
When `storageClass.create` is true, Helm emits the StorageClass. Compared with v4.8.0, the provisioner now follows the configured driver name, so custom driver names can be reflected consistently.

## State And Persistence
The StorageClass persists cluster-scoped provisioning defaults. Its parameters influence dynamically created PVs and deletion behavior.

## Dependencies And Integration Points
Integrates with the csi-provisioner deployment, `CSIDriver`, driver name values, and NFS server/share parameters supplied by the user.

## Risks And Edge Cases
Annotations block rendering should be checked for empty values. Changing driver names during upgrades can orphan old StorageClasses or PVC expectations. Parameters remain opaque to Kubernetes and are validated mostly by the CSI driver.

## Test Signals
Render with custom `driver.name`, annotations, and mount options; create a PVC using the class; verify PV provisioner name and NFS mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/values.yaml

## Purpose
Default configuration for the v4.9.0 CSI NFS Helm chart.

## Important APIs, Types, And Functions
Defines image tags, service-account/RBAC defaults, driver name, mount permissions, feature flags, kubelet directory, controller and node defaults, snapshotter defaults, image pull secrets, and commented StorageClass examples.

## Control Flow
Templates consume these values to generate Kubernetes objects and plugin/sidecar command flags. v4.9.0 sets NFS plugin image `v4.9.0`, csi-provisioner `v5.0.2`, snapshotter/controller `v8.0.1`, livenessprobe `v2.13.1`, and registrar `v2.11.1`.

## State And Persistence
Values become Helm release metadata and rendered object specs. They define persistent cluster configuration for RBAC, CRDs if enabled, driver metadata, and optional StorageClass settings.

## Dependencies And Integration Points
Links all v4.9.0 templates. Notable integrations include `driver.name` now controlling the StorageClass provisioner, controller affinity flags, `kubeletDir` host paths, and optional snapshot controller/CRD flags.

## Risks And Edge Cases
Snapshotter and StorageClass remain disabled by default. Privileged NFS pods require permissive node policy. Upgrades from v4.8.0 should test control-plane scheduling and StorageClass provisioner behavior if custom driver names are used.

## Test Signals
`helm lint`, render diff from v4.8.0, install smoke tests for provisioning, scheduling with control-plane flags, node registration, and optional snapshots.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/cloudbuild.yaml -->
# sources/control-plane/csi-driver-nfs/cloudbuild.yaml

## Purpose
Google Cloud Build configuration for multi-architecture CSI NFS image builds and staging publication.

## Important APIs, Types, And Functions
Uses Cloud Build `timeout`, `options.substitution_option: ALLOW_LOOSE`, one build step image `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f`, entrypoint `./.cloudbuild.sh`, and substitutions `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

## Control Flow
Cloud Build runs `.cloudbuild.sh` with environment values for the git tag, base ref, registry name, and home directory. Comments state the repository must import csi-release-tools, provide `.cloudbuild.sh`, and accept a `binary` Dockerfile build argument.

## State And Persistence
Build outputs are container images pushed to the configured staging registry. The YAML itself has no runtime storage, but substitutions and Cloud Build logs preserve build metadata.

## Dependencies And Integration Points
Integrates with Kubernetes test-infra image-pushing workflows, csi-release-tools, `.cloudbuild.sh`, Dockerfiles that consume prebuilt binaries, and the `k8s-staging-sig-storage` registry.

## Risks And Edge Cases
The build image tag and release-tools expectations can drift. A too-short timeout would fail slow multi-arch builds, so this uses 7200 seconds. Loose substitutions prevent failures when optional refs are absent but can hide missing expected values.

## Test Signals
Run or dry-run Cloud Build configuration in the staging project, verify `.cloudbuild.sh` exists and is executable, and confirm images are published with the expected `_GIT_TAG`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/cmd/nfsplugin/main.go -->
# sources/control-plane/csi-driver-nfs/cmd/nfsplugin/main.go

## Purpose
Main entrypoint for the CSI NFS plugin binary. It parses runtime flags, initializes klog behavior, constructs NFS driver options, and starts the driver.

## Important APIs, Types, And Functions
Defines flags for CSI endpoint, node id, mount permissions, driver name, working mount directory, default delete policy, volume stats cache expiry, archived volume path removal, tar-based snapshot behavior, and snapshot compression. Uses `nfs.DriverOptions`, `nfs.NewDriver`, and `d.Run(false)`.

## Control Flow
`main` initializes klog flags, forces stderr logging and modern stderr threshold behavior, parses flags, warns if `nodeid` is empty, calls `handle`, and exits zero. `handle` copies flag values into `DriverOptions`, creates the driver, and runs it.

## State And Persistence
The entrypoint itself keeps no persistent state. Driver options control later persistence and side effects such as CSI socket serving, NFS mounts, volume directory deletion/retention, archive cleanup, snapshot data handling, and volume stats caching.

## Dependencies And Integration Points
Depends on `github.com/kubernetes-csi/csi-driver-nfs/pkg/nfs`, Go `flag` and `os`, and `k8s.io/klog/v2`. Helm controller and node templates pass the endpoint, node id, driver name, mount permissions, working mount dir, and delete policy flags used here.

## Risks And Edge Cases
Only an empty node id warning is emitted; startup continues, which may be acceptable for controller mode but risky for node behavior. Snapshot tar/compression and archived path flags have defaults that must match chart expectations. Invalid flag combinations are delegated to the driver package.

## Test Signals
Unit or integration tests should cover flag parsing into `DriverOptions`, default values, empty node-id logging, and end-to-end driver startup through controller and node chart deployments.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/cmd/nfsplugin/main.go -->
