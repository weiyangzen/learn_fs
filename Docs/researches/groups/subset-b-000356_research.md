# Research: subset-b-000356

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This Helm template installs the CSI external-snapshotter CRDs for the NFS CSI chart when both `externalSnapshotter.enabled` and `externalSnapshotter.customResourceDefinitions.enabled` are true. It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` resources in `snapshot.storage.k8s.io`.

## Important APIs, Types, and Functions
The key Kubernetes APIs are `apiextensions.k8s.io/v1` `CustomResourceDefinition`, namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. The schemas serve `v1` as storage and retain deprecated `v1beta1` entries with warning text but `served: false`. The template uses Helm conditionals and annotates CRDs with `api-approved.kubernetes.io`, `controller-gen.kubebuilder.io/version`, and `helm.sh/resource-policy: keep`.

## Control Flow, State, and Persistence
Rendering is all-or-nothing behind the two-value gate. Once applied, the CRDs persist cluster-wide and Helm is instructed to keep them during uninstall, so snapshot API state can outlive this chart release. The CRD schemas enforce immutable source selectors, bidirectional snapshot/content binding fields, deletion policies, status subresources, printer columns, and snapshot readiness/restore-size status.

## Dependencies and Integration Points
The CRDs are required by `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, the controller-side `csi-snapshotter` sidecar, and optional `snapshotclass.yaml`. They must be installed before snapshot controllers become ready.

## Risks and Test Signals
Main risks are cluster-wide ownership conflicts, incompatible pre-existing CRDs, and accidental disabling of CRD creation while enabling snapshot controllers in a cluster without snapshot APIs. Useful signals are `helm template` with both flags, `kubectl apply --server-side --dry-run=server`, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, and a dynamic `VolumeSnapshot` reaching `readyToUse`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template declares the cluster `CSIDriver` object for the NFS CSI driver. It tells Kubernetes how the driver participates in attachment, volume lifecycle modes, and filesystem group ownership handling.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `CSIDriver` with `metadata.name` from `.Values.driver.name`, `attachRequired: false`, and `volumeLifecycleModes` containing `Persistent` plus optional `Ephemeral` when `feature.enableInlineVolume` is true. `fsGroupPolicy: File` is conditionally emitted when `feature.enableFSGroupPolicy` is true.

## Control Flow, State, and Persistence
The manifest is unconditional. It persists as cluster-scoped driver metadata and is reconciled by Kubernetes storage components and kubelet plugin registration. There is no pod-local state, but changes affect how future pods and PVCs interact with the driver.

## Dependencies and Integration Points
It must match the `--drivername` passed to controller and node `nfsplugin` containers and the `provisioner` field in generated `StorageClass` objects. Kubelet registration from the node DaemonSet should advertise the same CSI driver name.

## Risks and Test Signals
Risks are driver-name drift, enabling inline ephemeral volume mode without testing node behavior, and changing `fsGroupPolicy` in a way that affects workload permissions. Signals include `kubectl get csidriver nfs.csi.k8s.io -o yaml`, node plugin registration success, PVC mount tests with `fsGroup`, and optional inline CSI pod volume tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template renders the node-plugin `DaemonSet` that registers the NFS CSI driver with kubelet and performs node-side NFS mount operations on every selected Linux node.

## Important APIs, Types, and Functions
It emits an `apps/v1` `DaemonSet` with `liveness-probe`, `node-driver-registrar`, and privileged `nfs` containers. It uses host paths for the CSI socket directory, kubelet pod mounts, and kubelet plugin registry. Optional host mount option propagation mounts `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d` when `feature.propagateHostMountOptions` is true.

## Control Flow, State, and Persistence
The DaemonSet uses rolling updates, host networking, Linux node selection, tolerations, optional affinity, and bidirectional mount propagation. The registrar publishes `{{ .Values.kubeletDir }}/plugins/csi-nfsplugin/csi.sock` to kubelet. Node state lives in host plugin directories, registration sockets, mounted pod volumes, and NFS mounts rather than in container filesystems.

## Dependencies and Integration Points
It depends on the node service account from RBAC, kubelet directory layout, `CSIDriver` metadata, and kubelet plugin registration behavior. The driver name must match controller, storage classes, and the `CSIDriver`.

## Risks and Test Signals
The v4.13.1 template uses `dnsPolicy: {{ .Values.controller.dnsPolicy }}` instead of `node.dnsPolicy`, so node-specific DNS overrides are ignored. Other risks include privileged `SYS_ADMIN`, host path availability, registration path mismatch on nonstandard kubelet directories, and host mount option propagation exposing host config. Signals are DaemonSet rollout on all intended nodes, registrar health endpoint, `kubectl get csinode` driver entries, pod mount/unmount tests, and DNS tests when overriding node policy.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This template optionally deploys the upstream CSI snapshot controller inside the NFS chart release. It provides the cluster control loop for binding `VolumeSnapshot` and `VolumeSnapshotContent` objects.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` when `externalSnapshotter.enabled` is true. Values control the name, replicas, labels, annotations, image, pull policy, image pull secrets, priority class, resource requests/limits, and scheduling. The container runs snapshot-controller with leader election and namespace-scoped leader-election leases.

## Control Flow, State, and Persistence
The Deployment has `minReadySeconds: 15` so it is not considered ready before CRD discovery settles. It uses a rolling update with `maxSurge: 0` and `maxUnavailable: 1`. Scheduling can inherit controller affinity or generated control-plane/master affinity. Runtime state is primarily leader-election leases and snapshot API object status updates.

## Dependencies and Integration Points
It depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, and the external snapshotter image configured in values. It works alongside the controller Deployment's `csi-snapshotter` sidecar; the controller handles Kubernetes object binding while the sidecar calls CSI snapshot operations.

## Risks and Test Signals
Risks are deploying a second snapshot controller in clusters that already provide one, enabling the controller without CRDs, and reusing controller scheduling/toleration knobs for a cluster-level component. Signals are snapshot-controller rollout, leader-election lease creation, no CRD discovery crash loops, and a `VolumeSnapshot` progressing to a bound content object.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates service accounts and cluster RBAC for the NFS CSI controller and node components. It grants the external provisioner and resizer the permissions needed to manage PV/PVC lifecycle, events, leases, secrets, and selected snapshot objects.

## Important APIs, Types, and Functions
When `serviceAccount.create` is true it emits controller and node `ServiceAccount` objects using `.Values.serviceAccount.controller` and `.Values.serviceAccount.node`. When `rbac.create` is true it emits `ClusterRole` objects for `external-provisioner` and `external-resizer`, plus `ClusterRoleBinding` objects to the controller service account. The provisioner role includes PV/PVC/storageclass/csinode/node/event/lease/secret permissions and snapshot read/update/status permissions.

## Control Flow, State, and Persistence
RBAC rendering is independently gated from service account rendering, allowing externally managed service accounts or roles. Bindings persist cluster-wide and authorize controller sidecars through the release namespace service account. There is no runtime state beyond Kubernetes authorization objects.

## Dependencies and Integration Points
The controller Deployment references the controller service account; the node DaemonSet references the node service account. Snapshot permissions are required by the provisioner and snapshotter paths when snapshot features are enabled. Lease permissions support sidecar leader election.

## Risks and Test Signals
Risks include broad cluster-level access, mismatched service account names when `serviceAccount.create=false`, and granting snapshot permissions even when external snapshot features are disabled. Signals include `kubectl auth can-i` checks as the controller service account, sidecar logs without RBAC forbidden errors, successful PVC create/delete/resize, and successful snapshot operations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template creates the service account, cluster role, cluster role binding, leader-election role, and role binding for the optional CSI snapshot controller.

## Important APIs, Types, and Functions
When `externalSnapshotter.enabled` is true it emits a `ServiceAccount`, a cluster `snapshot-controller-runner` role, a cluster binding, and namespaced leader-election `Role`/`RoleBinding`. Rules cover PV/PVC reads, PVC updates, events, `VolumeSnapshotClass`, `VolumeSnapshotContent`, `VolumeSnapshotContent/status`, `VolumeSnapshot`, `VolumeSnapshot/status`, optional node reads for distributed snapshotting, and coordination leases.

## Control Flow, State, and Persistence
The entire RBAC set is tied to the snapshot controller enable flag. Cluster roles persist independently of pods and authorize snapshot object reconciliation. Leader-election role state is namespace-scoped and matches the controller Deployment's `--leader-election-namespace`.

## Dependencies and Integration Points
This file supports `csi-snapshot-controller.yaml` and requires snapshot CRDs to make the API resources meaningful. It integrates with `.Values.externalSnapshotter.enabledDistributedSnapshotting` even though the default values do not define that key.

## Risks and Test Signals
Risks include cluster-wide write/delete privileges on snapshot contents, missing RBAC if a separately installed snapshot controller is expected to run outside this release, and values drift around distributed snapshotting. Signals are `kubectl auth can-i` for snapshot resources, successful lease creation, controller logs without forbidden errors, and snapshot object status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This small template optionally creates a `VolumeSnapshotClass` for the NFS CSI driver, allowing users to request snapshots without supplying their own class manifest.

## Important APIs, Types, and Functions
It emits `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` when `volumeSnapshotClass.create` is true. The class name comes from `.Values.volumeSnapshotClass.name`, `driver` comes from `.Values.driver.name`, and `deletionPolicy` comes from `.Values.volumeSnapshotClass.deletionPolicy`.

## Control Flow, State, and Persistence
The resource is cluster-scoped and persists independently of namespaces. Its deletion policy controls whether `VolumeSnapshotContent` and backing snapshot data are deleted or retained when bound snapshots are removed.

## Dependencies and Integration Points
It requires snapshot CRDs and a matching CSI driver name. It is consumed by user `VolumeSnapshot` objects and reconciled by the snapshot controller plus the NFS CSI snapshotter sidecar.

## Risks and Test Signals
Risks are creating the class before CRDs exist, using a deletion policy that conflicts with retention expectations, and driver-name mismatches. Signals include `helm template` with class creation enabled, `kubectl get volumesnapshotclass`, and a test snapshot using this class.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template optionally creates one default-style NFS CSI `StorageClass` and/or multiple additional storage classes from `storageClasses`. It exposes NFS server/share parameters and mount options to Kubernetes dynamic provisioning.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `StorageClass` objects. Important fields are `metadata.name`, chart labels, optional annotations, `provisioner: {{ .Values.driver.name }}`, `parameters`, `reclaimPolicy`, `volumeBindingMode`, `allowVolumeExpansion`, and `mountOptions`. The multi-class loop supports per-entry defaults for reclaim policy, binding mode, and expansion.

## Control Flow, State, and Persistence
The single class is gated by `storageClass.create`; the multi-class list is rendered whenever `.Values.storageClasses` is set. StorageClasses are cluster-scoped and influence future PVC provisioning. Persistent data is created on the configured NFS server/share/subdirectory by the CSI controller.

## Dependencies and Integration Points
The provisioner name must match the CSIDriver and `nfsplugin` driver name. Parameters integrate with the CSI NFS driver (`server`, `share`, `subDir`, `mountPermissions`, and provisioner secret fields for delete-time mount options). Mount options are used by kubelet during NFS mounts.

## Risks and Test Signals
In v4.13.1 the single-class template always emits an `annotations:` key even when no annotations are configured, producing an empty map. Other risks include missing NFS parameters, invalid mount options, multiple default classes, and relying on expansion without testing the resizer sidecar. Signals are `helm template` with single and multi-class values, server-side dry-run, PVC provisioning, mount option verification in pods, expansion tests, and reclaim-policy deletion/retention checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/values.yaml -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/Chart.yaml

## Purpose
This Helm chart metadata file identifies the v4.13.2 NFS CSI driver chart and ties the chart package version to the driver application version.

## Important APIs, Types, and Functions
It uses Helm chart API `v1` with `name: csi-driver-nfs`, `description: CSI NFS Driver for Kubernetes`, `version: 4.13.2`, and `appVersion: 4.13.2`.

## Control Flow, State, and Persistence
The file has no templating logic or runtime state. Helm uses it for chart packaging, dependency metadata, release history, and display.

## Dependencies and Integration Points
The version should align with `values.yaml` image tag defaults, especially `image.nfs.tag: v4.13.2`. Consumers may depend on the unprefixed semver-style chart version introduced in later chart lines.

## Risks and Test Signals
Risks are chart/app version drift and tooling assumptions around earlier versions that used a leading `v`. Signals are `helm lint`, packaged chart metadata inspection, and verifying the rendered nfsplugin image tag matches the advertised app version.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This file is the v4.13.2 snapshot CRD template for the NFS CSI chart. It installs `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs only when the chart is configured to run the external snapshotter and create CRDs.

## Important APIs, Types, and Functions
It emits three `apiextensions.k8s.io/v1` CRDs in `snapshot.storage.k8s.io`, with `v1` as the served storage version and non-served deprecated `v1beta1` schemas retained for conversion metadata. It uses OpenAPI validation, status subresources, printer columns, `oneOf` source selection, `Delete`/`Retain` deletion policy enums, and Helm `helm.sh/resource-policy: keep`.

## Control Flow, State, and Persistence
The top-level conditional is `and .Values.externalSnapshotter.enabled .Values.externalSnapshotter.customResourceDefinitions.enabled`. CRDs are cluster-scoped API definitions and will survive chart uninstall because of the keep annotation. Snapshot objects and status fields are then reconciled by the external snapshot controller and CSI snapshotter sidecar.

## Dependencies and Integration Points
This template integrates with the optional snapshot-controller Deployment/RBAC, the controller Deployment's `csi-snapshotter` sidecar, and optional `VolumeSnapshotClass` creation. It is byte-identical to the v4.13.1 version.

## Risks and Test Signals
Risks include ownership conflicts with platform-managed snapshot CRDs, disabling CRD creation in clusters without existing APIs, and stale retained CRDs during downgrade/upgrade testing. Signals include `helm template` with CRD flags, server-side dry-run, CRD discovery before controller readiness, and an end-to-end snapshot/restore workflow.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This file renders the v4.13.2 NFS CSI controller Deployment, combining controller-side CSI sidecars with the privileged NFS plugin container.

## Important APIs, Types, and Functions
The template emits an `apps/v1` `Deployment` with containers for `csi-provisioner`, `csi-resizer`, optional `csi-snapshotter`, `liveness-probe`, and `nfs`. It passes provisioner feature gates for `HonorPVReclaimPolicy` and `VolumeAttributesClass=false`, resizer `VolumeAttributesClass=false`, long timeouts/retry intervals, and NFS driver arguments for mount permissions, working mount dir, delete policy, tar snapshot mode, and snapshot compression.

## Control Flow, State, and Persistence
Rendering follows values for replica count, Recreate/Rolling strategy type, scheduling, image pull secrets, and resources. The pod uses host networking and a host kubelet pods mount with bidirectional propagation. Sidecar leader election is persisted in namespace `Lease` objects; provisioned volume and snapshot state lives in Kubernetes objects and the external NFS share.

## Dependencies and Integration Points
The Deployment depends on controller RBAC, service account names, snapshot CRDs/RBAC when snapshotting is enabled, the `CSIDriver` object, and storage classes that target `.Values.driver.name`. Image repository handling supports either full repositories or paths joined with `image.baseRepo`.

## Risks and Test Signals
Risks are privileged mount capability, hostNetwork DNS behavior, sidecar version/API skew, snapshotter enabled without cluster snapshot APIs, and operational impact of `defaultOnDeletePolicy`. Signals are `helm lint`, `helm template`, rollout readiness, sidecar lease objects, PVC provision/delete/expand tests, and snapshot creation with compression/tar settings varied.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template creates the `CSIDriver` object that advertises the NFS CSI driver to Kubernetes for v4.13.2 installs.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `CSIDriver` with `attachRequired: false`, `volumeLifecycleModes: [Persistent]`, optional `Ephemeral`, and optional `fsGroupPolicy: File`. The object name comes from `.Values.driver.name`.

## Control Flow, State, and Persistence
It renders unconditionally and persists as cluster-scoped storage driver metadata. Kubernetes uses it when scheduling and mounting CSI volumes; kubelet registration confirms the runtime endpoint separately through the node DaemonSet.

## Dependencies and Integration Points
The name must match controller and node `--drivername` args plus StorageClass `provisioner`. This file is byte-identical across the listed chart versions.

## Risks and Test Signals
Risks are inconsistent driver names, untested inline ephemeral mode, and unexpected permission semantics from `fsGroupPolicy`. Signals include CSIDriver discovery, CSINode entries, successful PVC mounts, and workload tests that set `fsGroup`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template renders the v4.13.2 node DaemonSet for kubelet driver registration and node-side NFS volume mount handling.

## Important APIs, Types, and Functions
It emits an `apps/v1` `DaemonSet` with liveness probe, `node-driver-registrar`, and privileged `nfs` containers. Values configure update `maxUnavailable`, DNS policy, node service account, priority class, scheduling, resources, registrar health endpoint, kubelet directories, and optional host NFS mount configuration propagation.

## Control Flow, State, and Persistence
The DaemonSet uses host networking and host paths for `plugins/csi-nfsplugin`, `pods`, and `plugins_registry`. The registrar advertises the CSI socket path to kubelet, while the NFS driver performs mounts with bidirectional propagation into pod volume directories. v4.13.2 correctly reads `.Values.node.dnsPolicy`, unlike v4.13.1.

## Dependencies and Integration Points
It depends on kubelet path conventions, node service account creation, the `CSIDriver` object, and matching driver names. It also integrates with host-level NFS configuration if `feature.propagateHostMountOptions` is true.

## Risks and Test Signals
Risks include privileged host mounts, socket registration failures when `kubeletDir` is wrong, DNS regressions under host networking, and accidental host NFS config mutation/visibility. Signals are DaemonSet availability, registrar HTTP health, CSINode driver entries, mount/unmount workloads, kubelet plugin logs, and comparing node DNS override rendering with v4.13.1.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This template optionally deploys the CSI snapshot controller for v4.13.2 chart installs. It is intended for clusters that do not already provide a snapshot controller.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` gated by `externalSnapshotter.enabled`, with configurable labels, annotations, replicas, image, image pull secrets, priority class, resources, and scheduling. The controller runs with `--leader-election=true` and `--leader-election-namespace={{ .Release.Namespace }}`.

## Control Flow, State, and Persistence
The Deployment waits at least 15 seconds before readiness, uses a rolling strategy with no surge, and applies Linux node selection plus optional control-plane/master affinity inherited from controller values. Runtime persistence is snapshot object reconciliation and leader-election leases.

## Dependencies and Integration Points
It requires `rbac-snapshot-controller.yaml`, snapshot CRDs, and an external snapshotter image compatible with the CRD schema. It complements the controller Deployment's CSI snapshotter sidecar.

## Risks and Test Signals
Risks are duplicate snapshot controllers, missing CRDs, broad cluster RBAC, and scheduling hidden behind controller affinity settings. Signals are rollout readiness, lease acquisition, no CRD discovery crash, and dynamic snapshot creation/binding.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This file renders service accounts and controller-side cluster RBAC for the v4.13.2 NFS CSI chart.

## Important APIs, Types, and Functions
It conditionally creates controller and node `ServiceAccount` objects, an `external-provisioner` `ClusterRole`, an `external-resizer` `ClusterRole`, and two `ClusterRoleBinding` objects. Provisioner rules cover PV/PVC create/update/delete flows, storage classes, CSINodes, nodes, events, leases, secrets, and snapshot content status updates. Resizer rules cover PV/PVC/status updates and events.

## Control Flow, State, and Persistence
`serviceAccount.create` and `rbac.create` independently gate object creation. RBAC is cluster-scoped and persists until explicitly removed by Helm. Controller sidecars use namespace service account tokens to exercise these permissions.

## Dependencies and Integration Points
The controller and node workloads reference the service account names in values. Lease permissions integrate with sidecar leader election, secret access supports CSI provisioner secret parameters, and snapshot permissions support snapshot-aware provisioning.

## Risks and Test Signals
Risks include broad permissions, name mismatches when bringing pre-created service accounts, and granting snapshot permissions in clusters without snapshot APIs. Signals are `kubectl auth can-i` checks, sidecar logs free of forbidden errors, PVC lifecycle tests, resizer tests, and snapshot status update tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This file renders RBAC for the optional v4.13.2 snapshot controller Deployment.

## Important APIs, Types, and Functions
It creates a snapshot-controller `ServiceAccount`, cluster role, cluster role binding, namespace `Role`, and namespace `RoleBinding` when `externalSnapshotter.enabled` is true. The cluster role grants snapshot class/content/snapshot read-write permissions, status updates, event writes, PV/PVC reads/updates, optional node reads, and lease permissions for leader election.

## Control Flow, State, and Persistence
All objects render only with the snapshot controller. Cluster-scoped permissions authorize reconciliation of snapshot API objects, while the namespace role controls leader-election leases in the release namespace.

## Dependencies and Integration Points
It supports the snapshot-controller Deployment and requires snapshot CRDs. The optional distributed snapshotting branch depends on `externalSnapshotter.enabledDistributedSnapshotting`, which is not present in the default values but can be supplied by users.

## Risks and Test Signals
Risks are over-privileged snapshot content access, duplicate controller installations, and undeclared optional values. Signals are authorization checks as the snapshot controller service account, lease creation, snapshot status updates, and controller logs under denied-RBAC scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This template optionally creates a cluster `VolumeSnapshotClass` for the v4.13.2 NFS CSI driver.

## Important APIs, Types, and Functions
It emits `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` when `volumeSnapshotClass.create` is true. It binds the class to `.Values.driver.name` and applies `.Values.volumeSnapshotClass.deletionPolicy`.

## Control Flow, State, and Persistence
The object is cluster-scoped and has no namespace. Its deletion policy is persisted and copied into dynamically created snapshot content behavior.

## Dependencies and Integration Points
It requires installed snapshot CRDs, a running snapshot controller, and the controller-side CSI snapshotter sidecar. Users reference the class from `VolumeSnapshot.spec.volumeSnapshotClassName`.

## Risks and Test Signals
Risks include CRD absence, driver-name mismatch, and unexpected deletion/retention semantics. Signals include dry-run validation, class listing, and a snapshot using the class reaching ready state.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template renders optional NFS CSI `StorageClass` resources for v4.13.2. It supports either a single configured class or a list of multiple classes.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `StorageClass` with chart labels, optional annotations, `provisioner` from the CSI driver name, optional driver parameters, reclaim policy, volume binding mode, expansion support, and mount options. The `storageClasses` loop provides per-class defaults and per-class `allowVolumeExpansion` handling.

## Control Flow, State, and Persistence
The single class renders only when `storageClass.create` is true. Multiple class entries render whenever `.Values.storageClasses` is set. StorageClasses persist cluster-wide and control future PVC provisioning onto the target NFS server/share.

## Dependencies and Integration Points
The provisioner must match the NFS CSI driver. Parameters feed the external provisioner and NFS plugin, including `server`, `share`, optional `subDir`, mount permissions, and secret references for delete-time mount options.

## Risks and Test Signals
v4.13.2 fixes v4.13.1's empty single-class `annotations:` emission by placing the key inside the `with` block. Remaining risks include invalid server/share values, bad NFS mount options, multiple default annotations, and untested expansion. Signals are rendered YAML with no empty annotation block, server-side dry-run, PVC bind/mount/delete, multi-class provisioning, and expansion tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/values.yaml

## Purpose
This values file supplies the default runtime and rendering configuration for the v4.13.2 NFS CSI Helm chart.

## Important APIs, Types, and Functions
It defines image defaults, service account names, RBAC names, driver settings, feature flags, kubelet directory, controller settings, node-driver-registrar health settings, node settings, external snapshotter settings, snapshot class defaults, image pull secrets, and storage class examples. Compared with v4.13.1, the only values change is `image.nfs.tag: v4.13.2`.

## Control Flow, State, and Persistence
Values drive Helm conditionals for RBAC, CRDs, snapshot controller deployment, volume snapshot class creation, storage classes, sidecar inclusion, mount option propagation, and scheduling. Defaults create the driver workloads and RBAC, enable the controller-side snapshotter, but do not deploy the external snapshot controller, CRDs, snapshot class, or storage class.

## Dependencies and Integration Points
The file integrates chart templates with CSI sidecar image versions, registry composition through `image.baseRepo`, Kubernetes priority classes, host kubelet paths, NFS snapshot behavior, and optional storage class parameters.

## Risks and Test Signals
Risks are sidecar/driver version skew, enabling snapshots without a cluster snapshot controller/CRDs, privileged host mount behavior, and registry mirroring mistakes with leading-slash repository values. Signals are `helm template` matrices, chart install/upgrade from v4.13.1, rendered image tag verification, PVC lifecycle, expansion, node registration, and optional snapshot tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/Chart.yaml

## Purpose
This metadata file identifies the v4.2.0 NFS CSI Helm chart.

## Important APIs, Types, and Functions
It uses Helm chart API `v1`, with `name: csi-driver-nfs`, description `CSI NFS Driver for Kubernetes`, and both `version` and `appVersion` set to `v4.2.0`.

## Control Flow, State, and Persistence
There is no templating or runtime state. Helm uses this file for package identity, release metadata, and chart version selection.

## Dependencies and Integration Points
The chart version should align with `values.yaml` defaults, especially the NFS plugin image tag `v4.2.0`. The leading `v` differs from later 4.13 chart metadata.

## Risks and Test Signals
Risks are version drift and automation that expects strict semver without a leading `v`. Signals are `helm lint`, package inspection, and rendered image tag comparison.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This template renders the v4.2.0 NFS CSI controller Deployment. It is a simpler controller than later versions, containing provisioner, liveness, and NFS driver containers only.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` with `csi-provisioner`, `liveness-probe`, and privileged `nfs` containers. It uses direct image repository/tag values, `--extra-create-metadata=true`, leader election, `--working-mount-dir`, driver name, mount permissions, and host kubelet pod mount propagation.

## Control Flow, State, and Persistence
The pod uses `hostNetwork: true`, controller DNS policy, optional affinity, hard-coded priority class `system-cluster-critical`, run-on-master/control-plane node selector labels, and an `emptyDir` CSI socket. Persistent effects are PV/PVC objects, events, leases, and directories on the configured NFS server.

## Dependencies and Integration Points
It depends on the controller service account from RBAC, the external provisioner RBAC role, the `CSIDriver` object, and `StorageClass` resources supplied outside this chart version. It does not include resizer or snapshotter sidecars.

## Risks and Test Signals
Risks include no expansion sidecar, no snapshot support, privileged host mount access, old liveness `--health-port` style, and node placement through nodeSelector labels instead of node affinity. Signals are successful deployment rollout, leader-election lease creation, PVC provisioning/deletion, liveness health, and rendering with `runOnMaster`/`runOnControlPlane`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template registers the v4.2.0 NFS CSI driver as a Kubernetes `CSIDriver`.

## Important APIs, Types, and Functions
It emits `storage.k8s.io/v1` `CSIDriver` named from `.Values.driver.name`, with `attachRequired: false`, persistent lifecycle mode, optional inline ephemeral mode, and optional `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
It renders unconditionally and persists as cluster-scoped metadata used by storage scheduling and kubelet interactions. Runtime endpoint registration still comes from the node DaemonSet.

## Dependencies and Integration Points
The driver name must match controller/node `--drivername` and any external StorageClass provisioner field. This same template content is reused across all listed chart versions.

## Risks and Test Signals
Risks are name mismatch, enabling inline mode without node coverage, and changing fsGroup semantics. Signals are CSIDriver presence, CSINode registration, PVC mount success, and fsGroup workload checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template renders the v4.2.0 node DaemonSet that registers and runs the NFS CSI node plugin.

## Important APIs, Types, and Functions
It emits an `apps/v1` `DaemonSet` with liveness probe, node-driver-registrar, and privileged NFS plugin containers. It mounts kubelet plugin, pod, and registration host paths. The registrar uses an exec liveness probe invoking `/csi-node-driver-registrar --mode=kubelet-registration-probe`.

## Control Flow, State, and Persistence
The DaemonSet uses host networking, controller DNS policy, a hard-coded `csi-nfs-node-sa` service account, optional scheduling values, and rolling update max unavailable. Host state includes CSI sockets, plugin registration files, and pod volume mounts.

## Dependencies and Integration Points
It depends on RBAC creating the expected node service account, kubelet directories under `.Values.kubeletDir`, and a matching `CSIDriver`. It integrates with kubelet through the plugin registry and with workloads through bidirectional pod mount propagation.

## Risks and Test Signals
Risks include hard-coded service account use, older exec-based registrar probe, controller DNS policy reuse, privileged `SYS_ADMIN`, and kubelet directory mismatch. Signals are DaemonSet rollout, CSINode driver entries, registrar probe health, pod mount/unmount tests, and rendering with custom kubelet paths.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates service accounts and the external-provisioner RBAC used by the v4.2.0 NFS CSI chart.

## Important APIs, Types, and Functions
With `serviceAccount.create`, it creates service accounts named `csi-{{ .Values.rbac.name }}-controller-sa` and `csi-{{ .Values.rbac.name }}-node-sa`. With `rbac.create`, it creates one `ClusterRole` and one `ClusterRoleBinding` for the external provisioner. Rules include PV create/delete, PVC update, storageclass reads, events, CSINodes, nodes, leases, and secret reads.

## Control Flow, State, and Persistence
Service account names are derived from `rbac.name`, not from `serviceAccount.controller`, even though values define a controller name. The cluster role persists cluster-wide and authorizes the controller-side provisioner through a binding to the derived controller service account.

## Dependencies and Integration Points
The controller Deployment uses `.Values.serviceAccount.controller`, whose default matches the derived service account only when `rbac.name` remains `nfs`. The node DaemonSet uses hard-coded `csi-nfs-node-sa`, also matching defaults only for the default RBAC name.

## Risks and Test Signals
The main risk is service account name drift if users customize `rbac.name` or `serviceAccount.controller`. Other risks are broad cluster permissions and absence of resizer/snapshot roles. Signals are rendered-name inspection, `kubectl auth can-i` as the controller SA, no provisioner forbidden logs, and PVC lifecycle tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/values.yaml

## Purpose
This values file supplies defaults for the v4.2.0 NFS CSI chart, covering images, service accounts, RBAC, driver name, feature flags, kubelet directory, and controller/node pod settings.

## Important APIs, Types, and Functions
Defaults include nfsplugin `v4.2.0`, csi-provisioner `v3.3.0`, livenessprobe `v2.8.0`, node-driver-registrar `v2.6.2`, controller service account `csi-nfs-controller-sa`, driver name `nfs.csi.k8s.io`, kubelet dir `/var/lib/kubelet`, `enableFSGroupPolicy: true`, and `enableInlineVolume: false`.

## Control Flow, State, and Persistence
Values control rendering of service accounts/RBAC, controller and node Deployments/DaemonSets, image pull secrets, scheduling, log levels, health ports, and resources. There are no built-in storage class, snapshot, resizer, or external snapshot controller values in this chart version.

## Dependencies and Integration Points
The file is consumed by v4.2.0 templates and Kubernetes CSI sidecars. The defaults assume standard kubelet paths and registry.k8s.io images.

## Risks and Test Signals
Risks include service account naming mismatch when customizing values, no storage class examples, no expansion/snapshot support, and older sidecar versions. Signals are `helm template` with customized RBAC names, install smoke tests, PVC provisioning/deletion, node registration, and image pull validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/Chart.yaml

## Purpose
This metadata file identifies the v4.3.0 NFS CSI Helm chart.

## Important APIs, Types, and Functions
It uses Helm chart API `v1` with `name: csi-driver-nfs`, the standard description, `version: v4.3.0`, and `appVersion: v4.3.0`.

## Control Flow, State, and Persistence
It has no templating control flow. Helm records these fields in chart packaging and release metadata.

## Dependencies and Integration Points
The metadata should align with v4.3.0 image tags in values. The leading `v` version style matches v4.2.0 and v4.4.0 chart metadata but differs from v4.13.x.

## Risks and Test Signals
Risks are chart/app version drift and version parser assumptions. Signals are `helm lint`, chart package inspection, and rendered nfsplugin tag validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This v4.3.0 template installs the snapshot CRDs when the external snapshotter is enabled. It predates the later separate `customResourceDefinitions.enabled` value gate.

## Important APIs, Types, and Functions
It emits `apiextensions.k8s.io/v1` CRDs for `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent`, with `v1` storage schemas and deprecated non-served `v1beta1` schemas. It includes the upstream approval and controller-gen annotations but does not include Helm's `resource-policy: keep` annotation in this version.

## Control Flow, State, and Persistence
The only gate is `externalSnapshotter.enabled`, so enabling the snapshot controller also attempts to create cluster-wide CRDs. CRDs persist as Kubernetes API extensions, but without the Helm keep annotation their uninstall/upgrade lifecycle is more tightly tied to the release than v4.13.x.

## Dependencies and Integration Points
The CRDs are consumed by the v4.3.0 snapshot controller, snapshot RBAC, and controller-side `csi-snapshotter` sidecar. They must be present before the snapshot controller becomes ready.

## Risks and Test Signals
Risks include CRD ownership conflicts when a cluster already has snapshot CRDs, less flexible CRD lifecycle control than v4.13.x, and snapshot controller crash loops if CRDs fail to apply. Signals are `helm template` with `externalSnapshotter.enabled`, server-side dry-run, CRD discovery, and a dynamic snapshot readiness test.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This template renders the v4.3.0 NFS CSI controller Deployment, adding snapshot support compared with v4.2.0 but not yet including the resizer sidecar found in v4.13.x.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` with `csi-provisioner`, optional `csi-snapshotter`, `liveness-probe`, and privileged `nfs` containers. It adds pod `seccompProfile: RuntimeDefault`, read-only root filesystems for non-driver sidecars, `--default-ondelete-policy`, and an `emptyDir` mounted at `.Values.controller.workingMountDir`.

## Control Flow, State, and Persistence
Snapshot sidecar rendering follows `externalSnapshotter.enabled`. Control-plane/master scheduling is still implemented through nodeSelector labels when no custom nodeSelector overrides them. Sidecars use namespace leader election, and the NFS driver uses host pod mount propagation plus a pod-local working directory.

## Dependencies and Integration Points
The controller depends on v4.3.0 RBAC, service account defaults, snapshot CRDs when enabled, `CSIDriver`, and any externally supplied StorageClass. It does not include volume expansion support.

## Risks and Test Signals
Risks are optional snapshot sidecar without resources, lack of resizer, privileged host mounts, and older nodeSelector-based control-plane placement. Signals are rendered diffs with snapshot on/off, controller rollout, PVC lifecycle, snapshot creation when enabled, and checking the working mount directory is writable.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template creates the v4.3.0 `CSIDriver` declaration for the NFS CSI driver.

## Important APIs, Types, and Functions
It emits a `storage.k8s.io/v1` `CSIDriver` named from `.Values.driver.name`, with `attachRequired: false`, persistent lifecycle mode, optional ephemeral lifecycle mode, and optional `fsGroupPolicy: File`.

## Control Flow, State, and Persistence
The manifest is unconditional and cluster-scoped. It influences Kubernetes storage handling while the node DaemonSet supplies actual kubelet plugin registration.

## Dependencies and Integration Points
The name must match controller/node args and StorageClass provisioner names. This content is identical across all listed chart versions.

## Risks and Test Signals
Risks are driver-name drift and insufficient testing of optional lifecycle/fsGroup behavior. Signals are CSIDriver presence, CSINode registration, PVC mount tests, and fsGroup workload checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template renders the v4.3.0 node DaemonSet for NFS CSI plugin registration and node-side mounts.

## Important APIs, Types, and Functions
It emits an `apps/v1` `DaemonSet` with liveness probe, node-driver-registrar, and privileged `nfs` containers. Compared with v4.2.0 it adds pod `seccompProfile: RuntimeDefault`, read-only liveness root filesystem, and hard-coded `system-node-critical` priority.

## Control Flow, State, and Persistence
The DaemonSet uses host networking, `dnsPolicy: {{ .Values.controller.dnsPolicy }}`, hard-coded `csi-nfs-node-sa`, host paths for CSI socket/pods/plugin registry, and rolling updates. Host state is kubelet registration sockets and mounted pod volumes.

## Dependencies and Integration Points
It depends on the default service account names from RBAC, kubelet path defaults, and matching driver names. Kubelet consumes the registrar's socket registration path.

## Risks and Test Signals
Risks include hard-coded node service account, controller DNS policy reuse, old exec-based registrar liveness probe, privileged host access, and no host mount option propagation feature yet. Signals are DaemonSet rollout, CSINode entries, registrar health, pod mount/unmount tests, and custom kubeletDir rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This template optionally deploys the v4.3.0 external snapshot controller.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` when `externalSnapshotter.enabled` is true. It uses configurable name, labels, annotations, replica count, image, pull policy, and controller tolerations, but hard-codes a small resource profile and does not expose image pull secrets in this version.

## Control Flow, State, and Persistence
The Deployment uses `minReadySeconds: 15`, rolling updates with no surge, Linux node selection, cluster-critical priority, and leader election in the release namespace. It writes status to snapshot API objects and uses namespace leases for leader state.

## Dependencies and Integration Points
It depends on v4.3.0 snapshot CRDs and `rbac-snapshot-controller.yaml`. It works with the controller Deployment's optional `csi-snapshotter` sidecar.

## Risks and Test Signals
Risks include duplicate cluster snapshot controllers, fixed resources, no imagePullSecrets support, and no affinity support in this version. Signals are snapshot controller rollout, lease creation, no CRD discovery crash, and successful VolumeSnapshot binding.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates v4.3.0 service accounts and external-provisioner RBAC, with snapshot permissions added only when the external snapshotter is enabled.

## Important APIs, Types, and Functions
It emits derived service account names `csi-{{ .Values.rbac.name }}-controller-sa` and `csi-{{ .Values.rbac.name }}-node-sa`. The provisioner `ClusterRole` covers PV/PVC/storageclass/events/CSINode/node/lease/secret access and conditionally adds snapshot class/snapshot/content/status reads and updates.

## Control Flow, State, and Persistence
Service account creation and RBAC creation are independently gated. Snapshot RBAC is gated by `externalSnapshotter.enabled`, unlike v4.13.x where snapshot rules are always present in the provisioner role. Persistent authorization state is cluster-scoped.

## Dependencies and Integration Points
The default derived service account names match the controller and node templates only under default `rbac.name: nfs`. The optional snapshot permissions support the controller's `csi-snapshotter` sidecar.

## Risks and Test Signals
Risks include service account name drift on custom values, no resizer RBAC, conditional snapshot permissions hiding forbidden errors only when the sidecar is enabled, and broad cluster permissions. Signals include rendered name checks, `kubectl auth can-i`, PVC lifecycle, and snapshot tests with the feature toggled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template renders RBAC for the v4.3.0 optional snapshot controller.

## Important APIs, Types, and Functions
It creates a snapshot controller service account, cluster role, cluster role binding, namespace role, and namespace role binding. Rules cover PV/PVC/event access, snapshot classes, snapshot contents, snapshot content status, snapshots, snapshot status, optional node reads for distributed snapshotting, and leader-election leases.

## Control Flow, State, and Persistence
All objects render when `externalSnapshotter.enabled` is true. The role persists as cluster authorization for snapshot reconciliation, and the namespaced role supports leader election in the release namespace.

## Dependencies and Integration Points
It supports `csi-snapshot-controller.yaml` and requires the snapshot CRDs emitted by the companion CRD template. The role grants `volumesnapshots` update/patch but not `create` in this version.

## Risks and Test Signals
Risks include missing create permission if future controller behavior expects it, duplicate snapshot controller installs, broad snapshot content modification rights, and optional value `enabledDistributedSnapshotting` not being declared in defaults. Signals are controller logs without RBAC denials, lease checks, snapshot create/update/status flows, and `kubectl auth can-i` coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/values.yaml

## Purpose
This values file configures the v4.3.0 NFS CSI chart, introducing snapshot-related image and controller defaults compared with v4.2.0.

## Important APIs, Types, and Functions
Defaults include nfsplugin `v4.3.0`, csi-provisioner `v3.5.0`, csi-snapshotter and snapshot-controller `v6.2.2`, livenessprobe `v2.10.0`, node-driver-registrar `v2.8.0`, driver name `nfs.csi.k8s.io`, controller default delete policy, and `externalSnapshotter.enabled: true`.

## Control Flow, State, and Persistence
Values control service account/RBAC creation, snapshot CRD/controller rendering, optional snapshot sidecar rendering, controller/node scheduling, health ports, resources, and image pull secrets. There are still no built-in StorageClass or VolumeSnapshotClass values in this file.

## Dependencies and Integration Points
The file binds v4.3.0 templates to CSI sidecar versions and snapshot-controller resources. It assumes standard kubelet paths and registry.k8s.io images.

## Risks and Test Signals
Risks include snapshot stack enabled by default, no CRD sub-gate, service account naming sensitivity, and no resizer/storageclass config. Signals are install smoke tests, snapshot CRD/controller readiness, PVC provisioning/deletion, node registration, and feature-off rendering with `externalSnapshotter.enabled=false`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.3.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/Chart.yaml

## Purpose
This metadata file identifies the v4.4.0 NFS CSI Helm chart.

## Important APIs, Types, and Functions
It uses Helm chart API `v1`, with `name: csi-driver-nfs`, description `CSI NFS Driver for Kubernetes`, `version: v4.4.0`, and `appVersion: v4.4.0`.

## Control Flow, State, and Persistence
The file has no runtime control flow or persisted cluster state. Helm uses it for chart packaging and release metadata.

## Dependencies and Integration Points
The version should align with the v4.4.0 chart directory's values and image defaults. It retains the leading-`v` version style used by v4.2.0 and v4.3.0.

## Risks and Test Signals
Risks are version drift and compatibility with semver parsers that reject a leading `v`. Signals are `helm lint`, chart package inspection, and rendered image tag checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/Chart.yaml -->
