# Research Report: subset-b-000355

This grouped report covers the requested CSI NFS Driver Helm chart files from `sources/control-plane/csi-driver-nfs/charts`. Each section is source-path titled and wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This Helm template conditionally installs CSI snapshot CRDs when both `externalSnapshotter.enabled` and `externalSnapshotter.customResourceDefinitions.enabled` are true. It defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` in `snapshot.storage.k8s.io`, with `helm.sh/resource-policy: keep` so Helm uninstall does not remove cluster-wide snapshot APIs.

## APIs, Control Flow, and State
The template emits three `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects. `VolumeSnapshot` is namespaced and models user snapshot requests from either a PVC or pre-existing content. `VolumeSnapshotClass` is cluster-scoped and stores driver, deletion policy, and opaque parameters. `VolumeSnapshotContent` is cluster-scoped and represents the bound physical snapshot handle or source volume. The schema serves and stores `v1`; `v1beta1` remains present but deprecated and not served/stored. Status subresources persist readiness, errors, creation time, restore size, and binding references.

## Dependencies and Integration Points
The CRDs are consumed by the external snapshot controller, the NFS CSI snapshotter sidecar, Kubernetes API discovery, and user-created `VolumeSnapshot*` resources. They integrate with `snapshotclass.yaml`, `rbac-snapshot-controller.yaml`, and controller RBAC rules that watch and update snapshot resources.

## Risks and Test Signals
Cluster-scoped CRDs can conflict with CRDs installed by another chart or distribution; the keep policy also means upgrades and deletions need explicit CRD lifecycle care. Test with `helm template` for conditional rendering, `kubectl apply --dry-run=server`, and snapshot API discovery checks. Validate that `v1beta1` deprecation behavior matches supported Kubernetes versions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This template deploys the NFS CSI controller as an `apps/v1` `Deployment`. It hosts the control-plane CSI socket and sidecars that provision, resize, snapshot, and health-check NFS-backed volumes.

## APIs, Control Flow, and State
The Deployment is named from `controller.name`, uses `controller.replicas`, `controller.strategyType`, `hostNetwork: true`, `dnsPolicy`, and the controller service account. Scheduling either uses explicit `controller.affinity` or generated control-plane/master affinity when requested. Containers share an `emptyDir` socket at `/csi`: `csi-provisioner` performs PV/PVC provisioning with leader election, metadata, `HonorPVReclaimPolicy=true`, long timeouts, and retry backoff; `csi-resizer` handles volume expansion; optional `csi-snapshotter` is gated by `controller.enableSnapshotter`; `liveness-probe` exposes health; `nfs` is privileged, mounts kubelet pod directories bidirectionally, and serves the CSI endpoint.

## Dependencies and Integration Points
Images and resource blocks come from `values.yaml`. RBAC is provided by `rbac-csi-nfs.yaml`; snapshot operation also depends on snapshot CRDs and sidecar permissions. The controller writes transient CSI socket state only in `emptyDir` and uses host kubelet pod paths for mount operations.

## Risks and Test Signals
The privileged NFS container, host networking, and bidirectional mount propagation are high-trust settings. Misconfigured kubelet paths or DNS policy can break provisioning. Test with Helm rendering, controller pod readiness, leader election lease creation, dynamic PVC provisioning, resizing, snapshot creation when enabled, and liveness endpoint checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template creates the cluster-scoped `storage.k8s.io/v1` `CSIDriver` object that advertises the NFS CSI driver to Kubernetes.

## APIs, Control Flow, and State
The object name is `driver.name`, normally `nfs.csi.k8s.io`. It declares `attachRequired: false`, which tells Kubernetes no attach/detach controller operation is required for NFS volumes. It always lists `Persistent` in `volumeLifecycleModes`, optionally adds `Ephemeral` when `feature.enableInlineVolume` is true, and sets `fsGroupPolicy: File` when `feature.enableFSGroupPolicy` is true.

## Dependencies and Integration Points
The CSIDriver object must match the `--drivername` argument used by both controller and node NFS containers and the `provisioner` field in generated StorageClasses. Kubelet and CSI sidecars use it for capability discovery and volume lifecycle decisions.

## Risks and Test Signals
A driver name mismatch prevents provisioning and node registration from lining up. Enabling inline ephemeral volumes changes Kubernetes admission and kubelet behavior. Test by rendering values combinations, checking `kubectl get csidriver nfs.csi.k8s.io`, and verifying pod mounts with FSGroup-sensitive workloads.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template deploys the node service as an `apps/v1` `DaemonSet`. It registers the CSI driver with kubelet on every Linux node and performs node-side NFS mount work.

## APIs, Control Flow, and State
The DaemonSet uses rolling updates with `node.maxUnavailable`, `hostNetwork: true`, the node service account, Linux node selector, tolerations, affinity, priority class, and pod seccomp defaulting. It runs `liveness-probe`, `node-driver-registrar`, and privileged `nfs`. The registrar points kubelet to `$(kubeletDir)/plugins/csi-nfsplugin/csi.sock` and mounts `/registration`; the NFS container exposes `unix:///csi/csi.sock`, receives `NODE_ID`, uses the configured driver name and mount permissions, and mounts kubelet pod directories with bidirectional propagation.

## Dependencies and Integration Points
HostPath volumes connect the pod to kubelet plugin, plugin registry, and pod mount directories. The CSIDriver object must share the same driver name, and kubelet must use the same `kubeletDir`. RBAC creates the node service account but node runtime behavior mostly depends on host filesystem and kubelet registration.

## Risks and Test Signals
Privileged SYS_ADMIN plus bidirectional host mounts are necessary but sensitive. Wrong `kubeletDir` or missing host directories blocks registration. Test with `kubectl get pods -l app=csi-nfs-node`, kubelet plugin registration files, successful volume mounts on multiple nodes, rolling update behavior, and liveness failures.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This template optionally deploys the upstream external snapshot controller when `externalSnapshotter.enabled` is true. It is separate from the NFS controller-side `csi-snapshotter` sidecar.

## APIs, Control Flow, and State
The template emits an `apps/v1` `Deployment` named by `externalSnapshotter.name`. It applies labels/annotations, replica count, rolling update strategy with `maxSurge: 0`, `minReadySeconds: 15`, Linux node selection, optional image pull secrets, controller-derived affinity/tolerations, seccomp defaulting, and a single snapshot-controller container with leader election in the release namespace.

## Dependencies and Integration Points
The controller requires snapshot CRDs, the service account and RBAC in `rbac-snapshot-controller.yaml`, and the image configured at `image.externalSnapshotter`. It watches `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass` resources and coordinates with CSI driver snapshotter sidecars.

## Risks and Test Signals
Many Kubernetes distributions already install a snapshot controller; enabling this chart copy can create duplicate controllers. If CRDs are absent, the controller is expected to fail readiness or exit. Test with Helm condition combinations, leader election lease creation, controller logs, and end-to-end snapshot provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates service accounts and cluster RBAC for the NFS controller and node components.

## APIs, Control Flow, and State
When `serviceAccount.create` is true it emits controller and node `ServiceAccount` resources in the release namespace. When `rbac.create` is true it emits two `ClusterRole`s and two `ClusterRoleBinding`s. The provisioner role grants PV create/patch/delete, PVC get/list/watch/update, StorageClass and CSINode reads, Node reads, event writes, snapshot resource reads/updates, lease writes for leader election, and secret reads. The resizer role grants PV/PVC/status update, event writes, and lease writes.

## Dependencies and Integration Points
The controller Deployment references `serviceAccount.controller`; the node DaemonSet references `serviceAccount.node`. Provisioner, resizer, and snapshotter sidecars depend on these permissions to reconcile Kubernetes storage objects. Secret access supports provisioner-secret mount option handling.

## Risks and Test Signals
This is cluster-wide access; overly broad or missing verbs affect all NFS CSI operation. Snapshot verbs are present even if snapshotter is disabled. Test with `kubectl auth can-i` for the controller service account, PVC create/delete, expansion, snapshot flows, and leader-election lease updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template conditionally creates the service account and RBAC needed by the standalone external snapshot controller.

## APIs, Control Flow, and State
When `externalSnapshotter.enabled` is true it emits a release-namespace `ServiceAccount`, a cluster role named `<externalSnapshotter.name>-runner`, a cluster role binding, a namespaced leader-election `Role`, and a `RoleBinding`. The cluster role can read PVs, read/update PVCs, write events, read snapshot classes, create/read/list/watch/update/delete/patch snapshot contents, patch snapshot content status, and read/update/patch/create snapshots and statuses. It optionally adds Node read permissions when `externalSnapshotter.enabledDistributedSnapshotting` is true, even though this value is not declared in the default values file.

## Dependencies and Integration Points
The Deployment in `csi-snapshot-controller.yaml` uses this service account and relies on lease permissions for leader election. The RBAC targets the CRDs from `crd-csi-snapshot.yaml`.

## Risks and Test Signals
If `enabledDistributedSnapshotting` is used without matching snapshot-controller support, permissions may not match runtime expectations. Duplicate snapshot controllers can race. Test `kubectl auth can-i` for snapshot resources and leases, then run snapshot create/delete flows and inspect status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This small template optionally creates a default-style `VolumeSnapshotClass` for the NFS CSI driver when `volumeSnapshotClass.create` is true.

## APIs, Control Flow, and State
It emits `snapshot.storage.k8s.io/v1`, kind `VolumeSnapshotClass`, with name from `volumeSnapshotClass.name`, `driver` from `driver.name`, and `deletionPolicy` from `volumeSnapshotClass.deletionPolicy`. It contains no parameters or annotations by default.

## Dependencies and Integration Points
The class depends on snapshot CRDs being present and on the NFS CSI controller snapshotter being enabled to service snapshot requests. User `VolumeSnapshot` objects can reference this class by name.

## Risks and Test Signals
Creating this resource without installed CRDs fails. `deletionPolicy: Delete` can remove underlying snapshot data; `Retain` changes cleanup expectations. Test with `helm template`, dry-run apply, `kubectl get volumesnapshotclass`, and a `VolumeSnapshot` using the class.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template optionally creates one primary NFS `StorageClass` and any additional classes listed in `storageClasses`.

## APIs, Control Flow, and State
When `storageClass.create` is true it emits one `storage.k8s.io/v1` `StorageClass` named by `storageClass.name`, with labels, annotations, `provisioner: driver.name`, parameter map, reclaim policy, binding mode, `allowVolumeExpansion: true`, and optional mount options. When `storageClasses` is set it ranges over the list and emits multiple classes with per-entry names, annotations, parameters, reclaim policy defaulting to `Delete`, binding mode defaulting to `Immediate`, and `allowVolumeExpansion` defaulting true unless explicitly provided.

## Dependencies and Integration Points
Parameters such as NFS server, share, subDir, mount permissions, and provisioner secrets are consumed by the CSI provisioner and driver. Generated classes must match the CSIDriver/provisioner name.

## Risks and Test Signals
Invalid NFS server/share settings produce PVC provisioning failures. Multiple default-class annotations can conflict. Test by rendering both single and multiple class modes, creating PVCs, expanding PVCs, validating reclaim policy behavior, and checking mount options.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/values.yaml

## Purpose
This file is the default configuration contract for chart version 4.12.0. It controls image repositories/tags, service accounts, RBAC, driver behavior, scheduling, resources, optional snapshot controller/CRDs, and optional generated storage/snapshot classes.

## APIs, Control Flow, and State
Defaults use the NFS driver image tag `v4.12.0`, sidecars such as csi-provisioner `v5.3.0`, csi-resizer `v1.14.0`, csi-snapshotter and snapshot-controller `v8.3.0`, livenessprobe `v2.17.0`, and registrar `v2.15.0`. It enables service account and RBAC creation, sets `driver.name` to `nfs.csi.k8s.io`, enables FSGroup policy, disables inline volume, and configures kubeletDir. Controller defaults include one replica, host-network DNS, snapshotter enabled, tar snapshots disabled, delete-on-delete, critical priority, broad control-plane tolerations, and resource requests. Node defaults tolerate all taints and run critical priority. External snapshot controller and CRDs default off except CRD creation is true when the controller is enabled.

## Dependencies and Integration Points
All chart templates read these values. StorageClass and VolumeSnapshotClass examples document expected user overrides.

## Risks and Test Signals
Default `storageClass.create: false` means installing the chart alone does not create usable classes. Privileged host-mount defaults require trusted nodes. Test by rendering default and enabled feature profiles, checking image availability, and running PVC, resize, and snapshot workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/Chart.yaml

## Purpose
This Helm metadata file identifies chart version 4.12.1 of `csi-driver-nfs`.

## APIs, Control Flow, and State
It uses Helm chart `apiVersion: v1`, declares `name: csi-driver-nfs`, `description: CSI NFS Driver for Kubernetes`, `version: 4.12.1`, and `appVersion: 4.12.1`. It has no template logic, dependencies, maintainers, or values itself; Helm uses it as chart package metadata.

## Dependencies and Integration Points
The version and appVersion should match the packaged tarball and default NFS driver image tag in `values.yaml`. Consumers and automation can use these fields for chart repository indexes, upgrade detection, and compatibility reporting.

## Risks and Test Signals
Metadata drift between `Chart.yaml`, the package name, and `values.yaml` image tag can mislead upgrade tooling. Test with `helm lint`, package metadata inspection, and comparison to the chart directory and tarball version.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This file is the 4.12.1 copy of the optional CSI snapshot CRD template. It installs the same `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` APIs when the external snapshotter and CRD creation flags are enabled.

## APIs, Control Flow, and State
The CRDs use `apiextensions.k8s.io/v1`, group `snapshot.storage.k8s.io`, and preserve CRDs on Helm uninstall. `VolumeSnapshot` is namespaced and tracks source PVC/content, class, bound content, readiness, restore size, and errors. `VolumeSnapshotClass` is cluster-scoped and requires driver plus deletion policy. `VolumeSnapshotContent` is cluster-scoped and stores physical snapshot source/handle, references, status, and restore size. `v1` is served/storage; `v1beta1` exists as deprecated not-served/not-storage schema.

## Dependencies and Integration Points
The CRDs are shared cluster infrastructure for the chart's optional snapshot controller, controller-side `csi-snapshotter`, generated snapshot class, and user snapshot resources. The 4.12.1 CRD content is identical to 4.12.0 in this tree.

## Risks and Test Signals
Installing CRDs from multiple charts can create ownership and upgrade conflicts; keeping CRDs means uninstall does not reset cluster state. Test rendering conditions, server-side dry-run, API discovery, and snapshot create/delete behavior against the installed snapshot controller.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This Deployment template runs the NFS CSI controller for chart 4.12.1, including provisioner, resizer, optional snapshotter, liveness probe, and privileged NFS CSI server containers.

## APIs, Control Flow, and State
It renders an `apps/v1` Deployment with controller labels, replica count, strategy, host networking, controller service account, scheduling knobs, Linux selector, priority, seccomp, tolerations, and shared `/csi` socket `emptyDir`. The provisioner uses leader election, `--extra-create-metadata=true`, `HonorPVReclaimPolicy=true`, timeout and retry settings. The resizer uses leader election and disables handling volume-in-use errors. The optional snapshotter shares the CSI socket. The `nfs` container receives node identity, CSI endpoint, driver name, mount permissions, working mount dir, delete policy, and tar snapshot mode.

## Dependencies and Integration Points
The 4.12.1 template is identical to 4.12.0; version behavior changes come from `values.yaml` image tags. It depends on RBAC, StorageClass configuration, kubelet pod hostPath, and snapshot CRDs when snapshots are enabled.

## Risks and Test Signals
Host network, privileged SYS_ADMIN, and bidirectional kubelet mounts expand the blast radius. Test with Helm lint/template, pod security admission policy, controller readiness, PVC provisioning, expansion, snapshot creation, and sidecar leader election.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template registers the CSI NFS driver with Kubernetes as a `CSIDriver` object for chart 4.12.1.

## APIs, Control Flow, and State
It renders `storage.k8s.io/v1`, kind `CSIDriver`, named by `driver.name`. It sets `attachRequired: false`, always supports persistent lifecycle, optionally supports ephemeral inline lifecycle, and conditionally sets `fsGroupPolicy: File`. It stores no runtime state beyond the cluster API object.

## Dependencies and Integration Points
The object must align with controller/node `--drivername` and StorageClass `provisioner`. Kubelet and Kubernetes storage controllers use it to understand attach, lifecycle, and FSGroup behavior.

## Risks and Test Signals
Mismatched driver names are a hard integration failure. Inline volume and FSGroup settings affect pod admission and mount ownership semantics. Test by rendering value permutations and checking actual CSIDriver state after install.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This DaemonSet template installs the 4.12.1 NFS CSI node service on every eligible Linux node.

## APIs, Control Flow, and State
It renders an `apps/v1` DaemonSet using node scheduling values, critical priority, host networking, seccomp, broad tolerations by default, and a rolling update strategy. Containers include liveness probe, node-driver-registrar, and privileged NFS CSI server. HostPath volumes persist the CSI socket under `kubeletDir/plugins/csi-nfsplugin`, expose kubelet plugin registry, and provide pod mount propagation through `kubeletDir/pods`.

## Dependencies and Integration Points
The registrar integrates with kubelet, the CSIDriver object advertises the same driver name, and the NFS container performs node-stage/publish mount operations. The 4.12.1 node template is identical to 4.12.0; runtime version changes come from default images.

## Risks and Test Signals
Registration silently fails when kubelet paths differ from `kubeletDir`. Privileged host access should be reviewed against cluster policy. Test node plugin registration, pod PVC mounts, DaemonSet rollout, and node health after kubelet restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This optional template deploys a standalone external snapshot controller for chart 4.12.1.

## APIs, Control Flow, and State
When `externalSnapshotter.enabled` is true it emits an `apps/v1` Deployment with release namespace, labels/annotations, replicas, selector, `minReadySeconds: 15`, rolling update strategy, Linux node selector, controller-derived affinity/tolerations, critical priority, seccomp, and one container running `snapshot-controller` with leader election in the release namespace.

## Dependencies and Integration Points
It depends on snapshot CRDs, RBAC in `rbac-snapshot-controller.yaml`, and the snapshot-controller image from values. It coordinates API-level `VolumeSnapshot*` resources separately from the NFS CSI sidecar that talks to the driver.

## Risks and Test Signals
Duplicating a cluster-provided snapshot controller can lead to competing reconciliation. Test that only one intended controller is active, CRDs are present before readiness, and snapshot statuses update correctly.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This 4.12.1 template creates service accounts and cluster RBAC for NFS CSI controller/node operation.

## APIs, Control Flow, and State
Conditionals are driven by `serviceAccount.create` and `rbac.create`. The service accounts live in the release namespace. The external provisioner role covers PV/PVC/StorageClass/snapshot reads and updates, Node/CSINode reads, event writes, lease writes, and secret reads. The external resizer role covers PV and PVC status updates, event writes, and lease writes. Bindings attach both roles to the controller service account.

## Dependencies and Integration Points
The controller Deployment uses the bound service account for sidecars. The node service account is created here but does not receive additional cluster role bindings in this template. Snapshot permissions support controller-side snapshotter integration.

## Risks and Test Signals
Missing RBAC appears as sidecar reconciliation errors; excessive RBAC increases cluster-level privilege. Test `kubectl auth can-i`, PVC lifecycle, resize, snapshot operations, and lease creation. This template is unchanged from 4.12.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template provides the optional standalone snapshot controller's service account, cluster permissions, and leader-election permissions.

## APIs, Control Flow, and State
It renders only when `externalSnapshotter.enabled` is true. It grants snapshot-controller access to PVs, PVCs, events, `VolumeSnapshotClass`, `VolumeSnapshotContent`, `VolumeSnapshot`, status subresources, and release-namespace leases. It optionally grants Node reads if `externalSnapshotter.enabledDistributedSnapshotting` is set.

## Dependencies and Integration Points
The RBAC is consumed by `csi-snapshot-controller.yaml` and requires the snapshot CRDs to exist. It integrates with Kubernetes lease state for leader election and writes snapshot status state into the Kubernetes API.

## Risks and Test Signals
The optional distributed snapshotting value is undeclared in defaults, so enabling it depends on caller-provided values. Test render output for that flag, `kubectl auth can-i` for all snapshot verbs, and end-to-end snapshot deletion policy behavior. This file is unchanged from 4.12.0.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This template optionally emits a `VolumeSnapshotClass` for NFS CSI snapshots in chart 4.12.1.

## APIs, Control Flow, and State
When `volumeSnapshotClass.create` is true, it renders a `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` named from values, with `driver` set to the CSI driver name and `deletionPolicy` from values. It does not persist namespaced state and has no Helm logic beyond the create guard.

## Dependencies and Integration Points
The resource depends on installed snapshot CRDs and is consumed by user `VolumeSnapshot` resources plus the snapshot controller/sidecars. It is unchanged from 4.12.0.

## Risks and Test Signals
Wrong driver names prevent the class from matching the CSI driver; deletion policy controls physical snapshot retention. Test with dry-run apply and a snapshot using this class.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template creates optional NFS `StorageClass` resources for chart 4.12.1.

## APIs, Control Flow, and State
It supports a single `storageClass` block and a list-style `storageClasses` block. Rendered classes use `driver.name` as provisioner, user-supplied NFS parameters, reclaim policy, volume binding mode, expansion settings, annotations, labels, and mount options. Multiple classes can express different NFS shares, reclaim policies, or mount behavior.

## Dependencies and Integration Points
The CSI provisioner consumes class parameters during PVC provisioning, and the NFS driver uses server/share/subDir and mount option inputs. It is unchanged from 4.12.0.

## Risks and Test Signals
Bad parameter maps fail at provisioning time rather than render time. Test default disabled rendering, single-class rendering, multi-class rendering, PVC creation, expansion, and reclaim behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/values.yaml

## Purpose
This file defines the default values for chart 4.12.1 and is the main configuration surface for all templates.

## APIs, Control Flow, and State
It is identical to 4.12.0 except the NFS driver image tag changes from `v4.12.0` to `v4.12.1`. It keeps sidecars at csi-provisioner `v5.3.0`, csi-resizer `v1.14.0`, csi-snapshotter/snapshot-controller `v8.3.0`, livenessprobe `v2.17.0`, and registrar `v2.15.0`. It enables service account and RBAC creation, defaults FSGroup policy on, inline volume off, snapshotter sidecar on, external snapshot controller off, and StorageClass/SnapshotClass creation off.

## Dependencies and Integration Points
All templates read these values for names, images, scheduling, resources, feature gates, RBAC, and class creation. The image tag should align with `Chart.yaml` appVersion.

## Risks and Test Signals
The chart deploys driver components but no default StorageClass unless users opt in. Test chart rendering under default, storage-class-enabled, snapshot-controller-enabled, and control-plane scheduling overrides, and verify the 4.12.1 image is pulled.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/Chart.yaml

## Purpose
This Helm metadata file identifies chart version 4.13.0 of the CSI NFS driver.

## APIs, Control Flow, and State
It declares `apiVersion: v1`, `name: csi-driver-nfs`, `description: CSI NFS Driver for Kubernetes`, `version: 4.13.0`, and `appVersion: 4.13.0`. There is no executable chart logic here; Helm uses it for packaging and chart repository metadata.

## Dependencies and Integration Points
The metadata should align with the directory, packaged tarball, and `values.yaml` NFS image tag. It marks the transition from 4.12.x to 4.13.0, where sidecar versions and template arguments change.

## Risks and Test Signals
Metadata mismatch affects upgrade automation and operator expectations. Test with `helm lint`, chart package inspection, and comparison to default image tags.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose
This is the 4.13.0 optional CSI snapshot CRD template. It installs the same cluster snapshot API definitions as the 4.12.x chart when the external snapshotter and CRD creation flags are enabled.

## APIs, Control Flow, and State
It emits `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs in `snapshot.storage.k8s.io` with `v1` served/storage schemas and deprecated `v1beta1` schemas not served or stored. `VolumeSnapshot` stores namespaced snapshot intent and readiness. `VolumeSnapshotClass` stores cluster-scoped driver/deletion-policy configuration. `VolumeSnapshotContent` stores cluster-scoped physical snapshot binding, source, status, and error state. CRDs are annotated with `helm.sh/resource-policy: keep`.

## Dependencies and Integration Points
Snapshot controller, NFS CSI snapshotter sidecar, RBAC, generated snapshot classes, and user snapshot resources all depend on these CRDs. In this repository the CRD body is unchanged from 4.12.1.

## Risks and Test Signals
CRD ownership and versioning remain the main risk because CRDs are global and kept after uninstall. Test conditional rendering, server-side dry-run, discovery of `snapshot.storage.k8s.io/v1`, and snapshot lifecycle operations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This 4.13.0 Deployment template runs the CSI NFS controller and updated sidecars for provisioning, resizing, snapshotting, and health.

## APIs, Control Flow, and State
The Deployment structure matches 4.12.x but includes important argument changes. `csi-provisioner` now passes `--feature-gates=HonorPVReclaimPolicy=true,VolumeAttributesClass=false`; `csi-resizer` passes `-feature-gates=VolumeAttributesClass=false`; the privileged `nfs` container adds `--enable-snapshot-compression={{ .Values.controller.enableSnapshotCompression }}`. Image references also support repositories beginning with `/` by prefixing `image.baseRepo`, which is used by new sidecar defaults.

## Dependencies and Integration Points
It depends on `values.yaml` for upgraded sidecar images, `controller.enableSnapshotCompression`, RBAC, snapshot CRDs, StorageClass values, and kubelet host paths. The CSI socket remains an `emptyDir` shared among sidecars and the NFS container.

## Risks and Test Signals
Disabling `VolumeAttributesClass` is explicit compatibility behavior for newer sidecars and should be tested during Kubernetes upgrades. Snapshot compression changes snapshot artifact behavior and restore expectations. Test Helm rendering, sidecar startup with feature gates, PVC provisioning, resizing, compressed and uncompressed snapshots, and liveness probes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose
This template renders the 4.13.0 `CSIDriver` registration for the NFS CSI driver.

## APIs, Control Flow, and State
It creates `storage.k8s.io/v1` `CSIDriver`, named from `driver.name`, with `attachRequired: false`, persistent lifecycle, optional ephemeral lifecycle, and optional `fsGroupPolicy: File`. It stores static cluster driver capability state.

## Dependencies and Integration Points
The object ties Kubernetes driver discovery to controller/node `--drivername` and StorageClass provisioner names. It is unchanged from 4.12.x and remains central to kubelet volume handling.

## Risks and Test Signals
Driver-name drift breaks provisioning and mounting. FSGroup and inline volume flags should be tested with workloads that rely on ownership changes or CSI ephemeral volumes. Validate rendered YAML and installed `CSIDriver`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This DaemonSet template installs the 4.13.0 node-side NFS CSI service and kubelet registrar.

## APIs, Control Flow, and State
The base node flow matches 4.12.x: host networking, Linux node selection, node service account, critical priority, seccomp, liveness probe, registrar, privileged NFS server, hostPath CSI socket, kubelet pod directory, and plugin registry. New in 4.13.0, `nodeDriverRegistrar.livenessProbe.enabled` can add `--http-endpoint`, a healthz port, and a Kubernetes liveness probe to the registrar container. Image repository handling also prefixes `image.baseRepo` when a repository starts with `/`.

## Dependencies and Integration Points
The optional registrar health settings are defined in `values.yaml`. Runtime still depends on kubelet plugin paths, CSIDriver name alignment, and bidirectional mount propagation for pod volumes.

## Risks and Test Signals
Registrar liveness can improve recovery but may restart a registrar if health port settings are wrong. Test both disabled default and enabled health probe rendering, kubelet registration after rollout, pod volume mounts, and node pod liveness behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This optional Deployment runs the external snapshot controller for chart 4.13.0.

## APIs, Control Flow, and State
When enabled, it renders the same snapshot-controller Deployment structure as 4.12.x: release namespace, configurable labels/annotations, replicas, `minReadySeconds: 15`, rolling update, Linux selector, controller-derived affinity/tolerations, critical priority, seccomp, and leader election in the release namespace. It supports the 4.13 image repository convention where `/sig-storage/snapshot-controller` is prefixed by `image.baseRepo`.

## Dependencies and Integration Points
The controller integrates with snapshot CRDs and `rbac-snapshot-controller.yaml`. Its default image tag in 4.13.0 is `v8.4.0`, matching newer snapshot sidecars.

## Risks and Test Signals
The same duplicate-controller risk applies. Test rendering, image resolution, CRD readiness, leader election, and status reconciliation for snapshot create/delete flows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose
This template creates controller/node service accounts and cluster roles for 4.13.0 NFS CSI sidecars.

## APIs, Control Flow, and State
It is unchanged from 4.12.x. `serviceAccount.create` controls two ServiceAccounts. `rbac.create` controls provisioner and resizer ClusterRoles plus bindings to the controller service account. Permissions cover PV/PVC lifecycle, StorageClass reads, snapshot resource reads and content/status updates, events, CSINodes, Nodes, leader-election leases, and secret reads.

## Dependencies and Integration Points
These permissions are used by the updated 4.13.0 sidecars, including newer provisioner/resizer versions with explicit `VolumeAttributesClass=false`. The node service account is referenced by the DaemonSet.

## Risks and Test Signals
New sidecar versions may require permission review even if the RBAC did not change. Test with sidecar logs, `kubectl auth can-i`, PVC create/delete, resize, and snapshot flows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose
This template provides RBAC for the optional 4.13.0 external snapshot controller.

## APIs, Control Flow, and State
It conditionally emits the snapshot-controller service account, cluster role, cluster role binding, namespaced leader-election role, and role binding. Verbs cover PV/PVC reads and PVC updates, events, snapshot class/content/snapshot lifecycle and status updates, leases, and optional Node reads for distributed snapshotting.

## Dependencies and Integration Points
It is consumed by `csi-snapshot-controller.yaml` and relies on CRDs from `crd-csi-snapshot.yaml`. It is unchanged from 4.12.x while default snapshot-controller image advances to `v8.4.0`.

## Risks and Test Signals
RBAC may need validation against the newer snapshot-controller image. Test authorization, lease creation, snapshot status updates, deletion policy handling, and optional distributed snapshotting rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/snapshotclass.yaml

## Purpose
This template optionally creates the 4.13.0 NFS `VolumeSnapshotClass`.

## APIs, Control Flow, and State
When `volumeSnapshotClass.create` is true it emits a cluster-scoped `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` with name, driver, and deletion policy from values. The template has no parameters, labels, or annotations beyond those fields.

## Dependencies and Integration Points
It depends on snapshot CRDs and the NFS snapshotter path. The class driver must match `driver.name`, which defaults to `nfs.csi.k8s.io`.

## Risks and Test Signals
Wrong deletion policy has data-retention consequences. Test rendering, dry-run apply, and snapshot creation using the class. The template is unchanged from 4.12.x.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/storageclass.yaml

## Purpose
This template optionally creates one or more NFS `StorageClass` objects for chart 4.13.0.

## APIs, Control Flow, and State
The single-class and multi-class rendering paths are unchanged from 4.12.x. Classes use `driver.name` as provisioner, user parameters for NFS endpoint/path behavior, reclaim policy, volume binding mode, expansion controls, annotations, labels, and mount options. Multi-class entries default reclaim policy to `Delete`, binding mode to `Immediate`, and expansion to true.

## Dependencies and Integration Points
Provisioner sidecar version is newer in 4.13.0, but the class contract remains the same. NFS driver runtime consumes server/share/subDir/mount options and optional provisioner secrets.

## Risks and Test Signals
Provisioning failures typically surface after PVC creation, so class examples should be tested against real NFS endpoints. Test rendering, PVC bind, mount options, expansion, and reclaim behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/values.yaml

## Purpose
This is the default configuration contract for chart 4.13.0 and captures the main behavioral changes from 4.12.x.

## APIs, Control Flow, and State
It bumps the NFS image to `v4.13.0`, provisioner to `v6.1.0`, resizer to `v2.0.0`, snapshotter and snapshot-controller to `v8.4.0`, while keeping livenessprobe `v2.17.0` and registrar `v2.15.0`. Sidecar repositories move to `/sig-storage/...` entries combined with `image.baseRepo: registry.k8s.io`. It adds `controller.enableSnapshotCompression: true`, and a `nodeDriverRegistrar` block with optional liveness probe settings. Existing defaults for RBAC, service accounts, driver name, FSGroup policy, kubeletDir, scheduling, resources, external snapshotter, StorageClass, and SnapshotClass remain.

## Dependencies and Integration Points
Template changes in controller and node consume the new values. StorageClass examples remain documentation for NFS parameters and multiple class creation.

## Risks and Test Signals
Repository prefix logic makes image rendering sensitive to leading slashes. Snapshot compression changes storage behavior. New sidecar major versions need compatibility tests. Validate rendered images, feature gates, registrar liveness on/off, PVC lifecycle, expansion, snapshots, and upgrades from 4.12.x.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/Chart.yaml

## Purpose
This Helm metadata file identifies chart version 4.13.1 of `csi-driver-nfs`.

## APIs, Control Flow, and State
It declares Helm chart `apiVersion: v1`, `name: csi-driver-nfs`, description, `version: 4.13.1`, and `appVersion: 4.13.1`. It has no runtime control flow or state beyond chart packaging metadata.

## Dependencies and Integration Points
The metadata should match the chart directory, packaged `csi-driver-nfs-4.13.1.tgz`, and the 4.13.1 default NFS driver image tag in `values.yaml`. In this work item only `Chart.yaml` is mapped for v4.13.1, but repository diffs show the adjacent values file differs from 4.13.0 as part of the patch release.

## Risks and Test Signals
If appVersion or version drift from packaged contents, chart repository consumers can select or report the wrong release. Test with `helm lint`, package metadata inspection, and version consistency checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/Chart.yaml -->
