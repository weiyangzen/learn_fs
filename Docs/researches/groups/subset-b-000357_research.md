# subset-b-000357 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose

This Helm template installs the CSI external-snapshotter CRDs when `.Values.externalSnapshotter.enabled` is true. It emits three `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects in the `snapshot.storage.k8s.io` API group: namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. These resources are the API contract used by the NFS CSI controller sidecars and optional snapshot controller to request, bind, and track point-in-time volume snapshots.

## APIs, control flow, and state

The template has no runtime code; Helm controls rendering through a single conditional. The CRDs define `v1` as served/storage and retain deprecated `v1beta1` schemas as non-served/non-storage versions with deprecation warnings. `VolumeSnapshot.spec.source` uses `oneOf` to require either `persistentVolumeClaimName` for dynamic snapshots or `volumeSnapshotContentName` for pre-existing snapshots. Snapshot status persists controller-observed fields such as `boundVolumeSnapshotContentName`, `creationTime`, `readyToUse`, `restoreSize`, and `error`. `VolumeSnapshotClass` persists `driver`, `deletionPolicy`, and opaque `parameters`. `VolumeSnapshotContent` persists the binding to a `VolumeSnapshot`, CSI `driver`, `deletionPolicy`, source `volumeHandle` or `snapshotHandle`, optional `sourceVolumeMode`, and status including the CSI `snapshotHandle`.

## Dependencies and integration points

The CRDs are consumed by `csi-snapshotter` in the controller deployment, the optional external snapshot-controller deployment, and the RBAC templates granting access to `volumesnapshots`, `volumesnapshotclasses`, and `volumesnapshotcontents`. They also integrate with Kubernetes API server CRD validation, status subresources, printer columns, and CSI snapshot gRPC concepts such as `CreateSnapshot` and `ListSnapshots`.

## Risks and test signals

In v4.4.0, CRDs are tied only to `externalSnapshotter.enabled`; enabling the controller also creates cluster-wide CRDs, and disabling it prevents CRD installation even if users only want the APIs. This version does not set Helm's `resource-policy: keep`, so uninstall behavior can remove CRDs and potentially API objects depending on Helm and cluster behavior. Test by running `helm template` with `externalSnapshotter.enabled=true/false`, validating all three CRDs with `kubectl apply --dry-run=server`, and creating sample `VolumeSnapshot*` resources to confirm schema validation, status subresources, deprecated version handling, and RBAC alignment.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose

This template creates the `storage.k8s.io/v1` `CSIDriver` object for the NFS CSI driver. It advertises cluster-wide CSI driver capabilities under `.Values.driver.name`, which defaults to `nfs.csi.k8s.io`.

## APIs, control flow, and state

The rendered object sets `attachRequired: false`, telling Kubernetes that the driver does not need attach/detach controller operations before mounts. `volumeLifecycleModes` always includes `Persistent` and conditionally includes `Ephemeral` when `.Values.feature.enableInlineVolume` is true. When `.Values.feature.enableFSGroupPolicy` is true, `fsGroupPolicy: File` tells Kubernetes to apply file ownership behavior for mounted filesystems. The object stores declarative driver capability state in the Kubernetes API; it has no pod-local state or persistence.

## Dependencies and integration points

The `CSIDriver` object is consumed by kubelet, scheduler/storage control plane behavior, and CSI sidecars. It must match the `--drivername` argument used by both controller and node NFS plugin containers. Inline volume behavior must be coordinated with the driver's actual support and with workloads that use CSI ephemeral volumes.

## Risks and test signals

The main risk is capability drift: if the object advertises inline volumes or FSGroup behavior the driver/runtime cannot honor, workloads can fail at mount time or receive unexpected ownership. If the name differs from provisioned `StorageClass` drivers or container `--drivername`, Kubernetes treats them as different drivers. Test with `kubectl get csidriver`, provisioning a PVC through a matching `StorageClass`, pod mounts that exercise FSGroup, and a Helm render matrix toggling `enableInlineVolume` and `enableFSGroupPolicy`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose

This template deploys the node half of the NFS CSI driver as an `apps/v1` `DaemonSet`. Each Linux node runs a liveness probe, the CSI node-driver-registrar, and the privileged NFS plugin so kubelet can discover the driver and publish NFS volumes into pods.

## APIs, control flow, and state

The DaemonSet uses a rolling update strategy with `.Values.node.maxUnavailable`, host networking, configurable DNS policy, node selectors, tolerations, priority, and resource requests. The registrar exposes kubelet registration through `${kubeletDir}/plugins_registry` and points kubelet at `${kubeletDir}/plugins/csi-nfsplugin/csi.sock`. The NFS container receives node identity from `spec.nodeName`, exposes the CSI endpoint on the hostPath socket directory, and runs with `SYS_ADMIN`, privilege, and bidirectional propagation on `${kubeletDir}/pods`.

Node-side state is mostly socket and mount state in hostPath directories. The socket directory is `DirectoryOrCreate`; pod mount state lives under kubelet's pod directory; registration uses kubelet's plugin registry directory. The DaemonSet does not persist application data itself.

## Dependencies and integration points

The node pods integrate directly with kubelet CSI plugin registration, Linux mount namespaces, NFS client tooling inside the plugin image, host networking, and the `CSIDriver` object. In v4.4.0 the service account name is hard-coded as `csi-nfs-node-sa`, which must line up with RBAC/service-account creation.

## Risks and test signals

The privileged container and bidirectional host mounts create a high-impact security surface. The hard-coded node service account makes custom service-account naming brittle in this version. The template also lacks the later optional propagation of host `/etc/nfsmount.conf`, so node-level NFS mount tuning may not reach the plugin. Test by checking DaemonSet rollout on Linux nodes, kubelet plugin registration, `kubectl describe csinode`, successful pod volume mounts, liveness behavior on the node health port, and custom `kubeletDir` rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose

This template optionally deploys the Kubernetes CSI external snapshot-controller when `.Values.externalSnapshotter.enabled` is true. The controller reconciles `VolumeSnapshot` and `VolumeSnapshotContent` objects independently from the NFS CSI driver pods.

## APIs, control flow, and state

When enabled, Helm renders an `apps/v1` `Deployment` named from `.Values.externalSnapshotter.name`. It uses one or more replicas, rolling update with `maxSurge: 0`, `minReadySeconds: 15`, Linux node selection, a release-namespace service account, optional labels/annotations, controller tolerations, and the configured snapshot-controller image. The container starts with `--leader-election=true` and `--leader-election-namespace={{ .Release.Namespace }}`. Runtime state is stored in snapshot API resources, status subresources, events, and leader-election leases.

## Dependencies and integration points

The deployment depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, the `snapshot.storage.k8s.io` API group, and controller leader-election permissions in the release namespace. It complements the `csi-snapshotter` sidecar running inside the NFS controller deployment.

## Risks and test signals

In v4.4.0 this deployment does not template `imagePullSecrets`, so private registries require separate handling or later chart behavior. Enabling it in clusters that already install a platform snapshot-controller can create duplicate controllers. Test with `helm template` enabled/disabled, `kubectl rollout status`, lease creation, snapshot status updates, and failure behavior when CRDs are missing; `minReadySeconds` is intended to cover startup failures when v1 CRDs are unavailable.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose

This template creates service accounts and cluster RBAC for the NFS CSI controller and node components. It is guarded by `.Values.serviceAccount.create` for service accounts and `.Values.rbac.create` for the `ClusterRole`/`ClusterRoleBinding`.

## APIs, control flow, and state

When service-account creation is enabled, the template creates controller and node `ServiceAccount` resources in the release namespace. When RBAC is enabled, it creates a cluster role named `${rbac.name}-external-provisioner-role` and binds it to the controller service account. The role grants PV create/delete/list/watch, PVC list/watch/update, StorageClass and CSINode reads, Node reads, events writes, lease operations for leader election, and Secret reads.

In v4.4.0, snapshot permissions are conditionally included only when `.Values.externalSnapshotter.enabled` is true. Those permissions cover `VolumeSnapshotClass`, `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotContent/status` access needed by the provisioner/snapshot sidecar path.

## Dependencies and integration points

The controller deployment uses the controller service account for provisioning, snapshotting, event recording, and leader election. The node DaemonSet uses the node service account, but node-specific permissions are minimal here because kubelet registration happens through host paths.

## Risks and test signals

Conditional snapshot RBAC can break the always-present `csi-snapshotter` sidecar if snapshot CRDs are installed but the external snapshot-controller is disabled. Secret read access is cluster-wide and should be justified by provisioning needs. Test with `kubectl auth can-i --as system:serviceaccount:<ns>:<controller-sa>` for PV/PVC, leases, events, secrets, and snapshot resources under enabled/disabled snapshot settings, plus provisioning and snapshot workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose

This template creates the service account and RBAC needed by the optional external snapshot-controller. It renders only when `.Values.externalSnapshotter.enabled` is true.

## APIs, control flow, and state

The template emits a namespace-scoped `ServiceAccount`, a cluster-wide `ClusterRole`, a `ClusterRoleBinding`, and a namespace-scoped `Role`/`RoleBinding` for leader election. The cluster role grants read access to PVs and snapshot classes, PVC list/watch/update, event writes, CRUD-style access to `VolumeSnapshotContent`, status patching, and `VolumeSnapshot` update/patch/status update. If `.Values.externalSnapshotter.enabledDistributedSnapshotting` is set, it also grants Node reads. Lease state persists in the release namespace through the namespaced role.

## Dependencies and integration points

The RBAC is consumed by `csi-snapshot-controller.yaml` and depends on snapshot CRDs being installed or already present. It coordinates with the `csi-snapshotter` sidecar and Kubernetes API status subresources to keep snapshot objects reconciled.

## Risks and test signals

This is cluster-scoped authority, so enabling the controller grants broad snapshot mutation across namespaces. The `enabledDistributedSnapshotting` value is referenced here but absent from the default v4.4.0 values, so users must add it explicitly if needed. Test with `kubectl auth can-i` for each snapshot resource and status subresource, leader-election lease operations in the release namespace, and end-to-end dynamic snapshot creation/deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/values.yaml

## Purpose

This file is the default configuration contract for the v4.4.0 NFS CSI Helm chart. It selects image tags, service-account and RBAC names, driver capabilities, kubelet paths, controller/node scheduling, resources, snapshot-controller behavior, and image pull secrets.

## APIs, control flow, and state

The values feed every template in this chart. Image defaults point to `registry.k8s.io/sig-storage/nfsplugin:v4.4.0`, `csi-provisioner:v3.5.0`, `csi-snapshotter:v6.2.2`, `livenessprobe:v2.10.0`, `csi-node-driver-registrar:v2.8.0`, and `snapshot-controller:v6.2.2`. The driver defaults to `nfs.csi.k8s.io`, `mountPermissions: 0`, FSGroup policy enabled, inline volumes disabled, and `kubeletDir: /var/lib/kubelet`.

Controller defaults include one replica, `Recreate`, host-network DNS policy, control-plane tolerations, `system-cluster-critical`, liveness port `29652`, log level `5`, `/tmp` working mounts, and delete-on-delete behavior. Node defaults include liveness port `29653`, `maxUnavailable: 1`, broad toleration, and critical priority. `externalSnapshotter.enabled` defaults to true in v4.4.0.

## Dependencies and integration points

These values integrate with Helm template functions, Kubernetes scheduling, image registry access, kubelet host paths, and snapshot CRD/RBAC rendering. They are not persisted directly except through rendered Kubernetes resources and any Helm release state.

## Risks and test signals

The default external snapshot-controller and CRD installation can conflict with platform-managed snapshot infrastructure. The node service account is not configurable in v4.4.0 values even though service-account creation creates a node account in later chart versions. Test signals include `helm template` with defaults, custom image tags, disabled RBAC/service accounts, custom `kubeletDir`, and toggles for `enableFSGroupPolicy`, `enableInlineVolume`, and `externalSnapshotter.enabled`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/Chart.yaml

## Purpose

This is the Helm chart metadata for the v4.5.0 NFS CSI driver chart. It declares `apiVersion: v1`, chart `name: csi-driver-nfs`, description `CSI NFS Driver for Kubernetes`, `version: v4.5.0`, and `appVersion: v4.5.0`.

## APIs, control flow, and state

There is no executable control flow. Helm reads this file to identify the chart package and to expose chart/application versions in release metadata. The chart version should track the template/defaults bundled in `charts/v4.5.0`, while `appVersion` tracks the default NFS driver image version used by `values.yaml`.

## Dependencies and integration points

The metadata integrates with Helm packaging, dependency indexing, release history, chart repositories, and operators that inspect `.Chart.Name`, `.Chart.Version`, or `.Chart.AppVersion` through helper templates. It must remain consistent with the default `image.nfs.tag` and the source directory version.

## Risks and test signals

Version drift is the primary risk: if this file says v4.5.0 while values deploy another driver, release inventory becomes misleading. Test by running `helm lint`, `helm template`, and `helm show chart` for this directory, and by comparing `appVersion` with `values.yaml`'s NFS image tag.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose

This template installs the CSI snapshot CRDs for v4.5.0. It emits `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs for the `snapshot.storage.k8s.io` API group, preserving the v1 snapshot API and deprecated v1beta1 schemas.

## APIs, control flow, and state

Unlike v4.4.0, rendering is gated by both `.Values.externalSnapshotter.enabled` and `.Values.externalSnapshotter.customResourceDefinitions.enabled`. Each CRD includes Helm annotation `"helm.sh/resource-policy": keep`, so Helm should leave the CRD behind during uninstall. The CRD schemas model snapshot desired state and controller-observed status: `VolumeSnapshot.spec.source`, class selection, binding status, readiness, restore size, errors, `VolumeSnapshotClass.driver/deletionPolicy/parameters`, and `VolumeSnapshotContent` binding/source/status fields.

## Dependencies and integration points

The CRDs integrate with the API server, the optional snapshot-controller, the `csi-snapshotter` sidecar, and snapshot RBAC. The new `customResourceDefinitions.enabled` value lets cluster operators use a platform-provided snapshot API while still enabling the snapshot controller if desired.

## Risks and test signals

The double gate is safer but can surprise upgrades from v4.4.0: disabling the controller disables CRD rendering too, and setting `customResourceDefinitions.enabled=false` assumes CRDs already exist. `resource-policy: keep` prevents accidental CRD removal but can leave stale CRD versions after chart uninstall. Test `helm template` for all enabled/disabled combinations, validate server-side application of all three CRDs, check Helm uninstall behavior in a disposable cluster, and verify snapshot resource validation and status updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose

This v4.5.0 template deploys the host-networked NFS CSI controller `Deployment` with `csi-provisioner`, `csi-snapshotter`, `liveness-probe`, and the privileged NFS driver container.

## APIs, control flow, and state

The template renders from chart values for replicas, strategy, labels, image pull secrets, service account, scheduling, priority, resources, health port, and image tags. Both CSI sidecars use `/csi/csi.sock` and leader election in the release namespace. The NFS container receives `NODE_ID`, `CSI_ENDPOINT`, driver name, mount permissions, working mount directory, and default on-delete policy. Shared state is through an `emptyDir` socket, an `emptyDir` working mount directory, and hostPath `${kubeletDir}/pods` with bidirectional mount propagation; durable control-plane state is in Kubernetes API resources and leases.

## Dependencies and integration points

The deployment integrates with RBAC from `rbac-csi-nfs.yaml`, the `CSIDriver` object, StorageClasses using `nfs.csi.k8s.io`, snapshot APIs, kubelet host paths, Linux nodes, and registry images. v4.5.0 keeps the same controller template content as v4.4.0 while values update sidecar versions.

## Risks and test signals

The controller remains privileged and host-mounted, and sidecars in this version do not yet drop all capabilities. The `csi-snapshotter` sidecar is present regardless of whether the optional external snapshot-controller is enabled, so snapshot RBAC and CRD availability still matter. Test by rendering custom values, checking deployment rollout, provisioning PVCs, creating/deleting volumes, verifying liveness, checking leader-election leases, and exercising snapshots when CRDs are available.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose

This template renders the v4.5.0 `CSIDriver` object for the NFS CSI driver. It advertises the driver name and capabilities to Kubernetes storage components.

## APIs, control flow, and state

The object sets `attachRequired: false`, always advertises `Persistent` volume lifecycle support, conditionally advertises `Ephemeral` inline CSI volumes, and conditionally sets `fsGroupPolicy: File`. All conditionals are driven by `.Values.feature.enableInlineVolume` and `.Values.feature.enableFSGroupPolicy`. The persisted state is the Kubernetes `CSIDriver` API object; no pod-local state exists here.

## Dependencies and integration points

The object must match the `--drivername` passed to controller and node plugin containers and the `provisioner` value used by StorageClasses. Kubelet and storage admission behavior consume `attachRequired`, lifecycle modes, and FSGroup policy.

## Risks and test signals

Incorrect capability advertisement is the main risk. Enabling inline volumes or FSGroup policy without working runtime support can break workload mounts; changing the driver name creates a new identity from Kubernetes' perspective. Test `helm template`, `kubectl get csidriver -o yaml`, PVC provisioning, pod mounts with FSGroup, and optional inline CSI volume pods.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose

This template deploys the v4.5.0 NFS CSI node `DaemonSet`, running the liveness probe, node-driver-registrar, and privileged NFS plugin on every selected Linux node.

## APIs, control flow, and state

The DaemonSet renders rolling update settings, host networking, DNS policy, image pull secrets, priority, node selectors, tolerations, resources, and images from values. v4.5.0 changes the service account from a hard-coded `csi-nfs-node-sa` to `.Values.serviceAccount.node`, making custom service-account names viable. The registrar registers `${kubeletDir}/plugins/csi-nfsplugin/csi.sock` with kubelet. The NFS plugin runs with `SYS_ADMIN`, receives node identity and CSI endpoint, mounts the socket directory and `${kubeletDir}/pods`, and optionally mounts host `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d` when `.Values.feature.propagateHostMountOptions` is true.

## Dependencies and integration points

The template integrates with kubelet plugin registration, host mount propagation, host NFS configuration, Linux nodes, the `CSIDriver` object, and the node service account. State lives in host plugin sockets, kubelet registration paths, and active mounts rather than in chart-managed storage.

## Risks and test signals

The optional host NFS config propagation increases host coupling and can expose node-specific mount behavior to the plugin. The privileged container remains high risk. Test DaemonSet rollout, plugin registration, custom `.Values.serviceAccount.node`, both values of `propagateHostMountOptions`, custom kubelet directories, pod volume mounts, liveness probes, and node drain/rolling update behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose

This v4.5.0 template optionally deploys the external snapshot-controller `Deployment` when `.Values.externalSnapshotter.enabled` is true.

## APIs, control flow, and state

The deployment renders replicas, labels, annotations, service account, Linux node selection, priority, tolerations, image, resources, and leader-election arguments from values. v4.5.0 adds `imagePullSecrets` support, allowing private registry credentials to be attached to the snapshot-controller pod. It persists reconciliation state in snapshot objects, their status subresources, events, and leader-election leases.

## Dependencies and integration points

It depends on snapshot CRDs, `rbac-snapshot-controller.yaml`, the snapshot-controller image, and lease permissions in the release namespace. It works with the `csi-snapshotter` sidecar in the NFS controller deployment to implement Kubernetes CSI snapshot workflows.

## Risks and test signals

The controller should not be enabled in clusters that already provide a snapshot-controller unless duplicate reconciliation is intended. Missing CRDs cause startup/readiness failures; `minReadySeconds: 15` is meant to avoid marking it ready too early. Test rendering with image pull secrets, rollout with enabled/disabled CRDs, lease creation, snapshot status reconciliation, and private-registry image pulls.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose

This template creates service accounts and the controller ClusterRole/ClusterRoleBinding for the v4.5.0 NFS CSI chart.

## APIs, control flow, and state

It conditionally creates controller and node service accounts from `.Values.serviceAccount.*`, then conditionally creates a cluster role bound to the controller service account. The role grants PV/PVC/storageclass/csinode/node/event/lease/secret access needed by the external provisioner and driver. In v4.5.0, snapshot permissions are no longer conditional on `.Values.externalSnapshotter.enabled`; the controller service account always receives read/update/status access to `VolumeSnapshot*` resources.

## Dependencies and integration points

The controller deployment consumes the controller account for provisioning, snapshotter sidecar work, events, and leader election. The node DaemonSet consumes the node service account configured in values. The role assumes snapshot CRDs may exist even if this chart does not deploy the external snapshot-controller.

## Risks and test signals

Always granting snapshot permissions avoids broken snapshot sidecars but widens default RBAC in clusters not using snapshots. Cluster-wide Secret `get` remains sensitive. Test `kubectl auth can-i` for provisioning, leases, events, secrets, and snapshot resources, plus disabled `rbac.create` and custom service-account-name scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose

This template creates the v4.5.0 RBAC and service account for the optional external snapshot-controller. It renders only when `.Values.externalSnapshotter.enabled` is true.

## APIs, control flow, and state

The resources are a namespace service account, a cluster role, a cluster role binding, and a release-namespace role/rolebinding for leader election. The cluster role grants the snapshot controller read/write access to snapshot API resources and status subresources, PV/PVC reads and updates, and event writes. Optional distributed snapshotting adds Node read permissions. Lease objects store leader-election state.

## Dependencies and integration points

This RBAC is consumed by `csi-snapshot-controller.yaml` and depends on snapshot CRDs existing or being installed by `crd-csi-snapshot.yaml`. It coordinates with the NFS controller's `csi-snapshotter` sidecar and Kubernetes status subresources.

## Risks and test signals

The role is cluster-wide and can mutate snapshots in all namespaces. `enabledDistributedSnapshotting` is referenced but not present in default values, so behavior depends on an operator-supplied value. Test auth checks for every granted resource, leader election in the release namespace, enabled/disabled rendering, and end-to-end snapshot create/delete flows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/values.yaml

## Purpose

This is the default values contract for chart v4.5.0. It configures images, identities, RBAC, driver features, scheduling, resources, snapshot-controller behavior, CRD rendering, and image pull secrets.

## APIs, control flow, and state

Compared with v4.4.0, image tags advance to NFS plugin `v4.5.0`, provisioner `v3.6.1`, snapshotter/snapshot-controller `v6.3.1`, liveness probe `v2.11.0`, and registrar `v2.9.0`. It adds `.Values.serviceAccount.node`, `.Values.feature.propagateHostMountOptions`, and `.Values.externalSnapshotter.customResourceDefinitions.enabled`. It changes `.Values.externalSnapshotter.enabled` default from true to false, meaning the snapshot-controller and CRDs are not installed by default.

The controller and node defaults otherwise preserve critical priority, host-network DNS policy, liveness ports, Linux scheduling, tolerations, resource requests/limits, `kubeletDir`, FSGroup policy, and driver name. Values become persisted only through rendered Kubernetes resources and Helm release state.

## Dependencies and integration points

The new node service account value integrates with the v4.5.0 node DaemonSet template. `propagateHostMountOptions` integrates with node hostPath mounts for `/etc/nfsmount.conf`. The CRD toggle integrates with the snapshot CRD template and lets operators rely on separately managed CRDs.

## Risks and test signals

The default disabling of external snapshotter/CRDs changes install behavior from v4.4.0 and can break users expecting snapshots immediately after install. Host mount option propagation can create node-specific behavior. Test default `helm template`, upgrade from v4.4.0, explicit snapshot enablement, custom node service accounts, host mount option propagation, and private registry image pull secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/Chart.yaml

## Purpose

This is the Helm metadata file for chart v4.6.0. It declares the chart as `csi-driver-nfs`, describes it as `CSI NFS Driver for Kubernetes`, and sets both `version` and `appVersion` to `v4.6.0`.

## APIs, control flow, and state

There is no runtime control flow. Helm uses the file for packaging, chart repository indexes, release history, and chart metadata inspection. The `appVersion` should match the default NFS plugin image tag in `values.yaml`; the `version` should match the templates under the v4.6.0 directory.

## Dependencies and integration points

Helper templates and release tooling can read `.Chart.Name`, `.Chart.Version`, and `.Chart.AppVersion`. Operators use these fields to audit installed chart/application versions and compare them against rendered images.

## Risks and test signals

Metadata drift is the main risk. Test with `helm lint`, `helm show chart`, and a comparison between this `appVersion` and `values.yaml`'s `image.nfs.tag`. Package tests should ensure the directory name, chart version, and app version all remain coherent.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml

## Purpose

This v4.6.0 template installs the Kubernetes CSI snapshot CRDs for `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` when snapshot-controller and CRD installation are both enabled.

## APIs, control flow, and state

The template is structurally identical to v4.5.0 for the requested file. Helm renders it only under `and .Values.externalSnapshotter.enabled .Values.externalSnapshotter.customResourceDefinitions.enabled`. Each CRD is annotated with `controller-gen.kubebuilder.io/version: v0.8.0`, the snapshot API approval URL, and Helm `resource-policy: keep`. The schemas define v1 served/storage resources, deprecated non-served v1beta1 versions, status subresources, printer columns, immutable source/binding fields, deletion policy enums, CSI driver/source fields, readiness, restore size, creation time, error, and CSI snapshot handles.

## Dependencies and integration points

The CRDs integrate with the API server, the NFS controller's `csi-snapshotter` sidecar, the optional snapshot-controller deployment, and both CSI and snapshot-controller RBAC templates. They are cluster-scoped install-time resources even though `VolumeSnapshot` objects themselves are namespaced.

## Risks and test signals

Keeping CRDs on uninstall protects snapshot API data but can leave stale CRDs after removing the chart. Operators must ensure the CRDs exist when snapshot workflows are enabled but chart CRD rendering is disabled. Test enabled/disabled Helm rendering, server-side dry-run application, `kubectl explain volumesnapshot`, deprecated v1beta1 request warnings, status-subresource updates, and full snapshot create/delete/restore-size validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose

This v4.6.0 template deploys the NFS CSI controller `Deployment` with provisioner, snapshotter, liveness probe, and privileged NFS driver containers.

## APIs, control flow, and state

The control flow is Helm value rendering plus repository-prefix conditionals for images. v4.6.0 introduces `.Values.image.baseRepo` behavior: if a component repository starts with `/`, the image becomes `baseRepo + repository + :tag`; otherwise the repository is used as a full image name. It also updates liveness probe arguments from `--health-port` to `--http-endpoint=localhost:<port>`, removes named container ports for healthz, and points Kubernetes liveness HTTP checks at `host: localhost` and the numeric configured port.

Sidecar security contexts now drop all capabilities, and the privileged NFS container adds `SYS_ADMIN` while dropping all other capabilities. State remains shared through `/csi` `emptyDir`, `/tmp` working mount `emptyDir`, and hostPath `${kubeletDir}/pods`; durable state is Kubernetes PV/PVC/snapshot/event/lease data.

## Dependencies and integration points

The deployment depends on RBAC, service accounts, the `CSIDriver`, kubelet host paths, Linux nodes, CSI sidecar images, and optional snapshot APIs. It integrates with leader election, NFS mount operations, and host networking.

## Risks and test signals

The new image composition path is useful for mirrored registries but can render bad images if repositories are inconsistently absolute. Capability dropping is safer but should be verified against sidecar runtime needs. Test default and slash-prefixed repositories, liveness endpoint behavior, pod security admission, provisioning, snapshot sidecar operation, leader-election leases, and mount cleanup on controller restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose

This v4.6.0 template renders the `CSIDriver` object for the NFS CSI driver, declaring attach and lifecycle capabilities to Kubernetes.

## APIs, control flow, and state

The rendered object sets `attachRequired: false`, includes `Persistent` lifecycle mode, optionally includes `Ephemeral`, and optionally sets `fsGroupPolicy: File`. The file is unchanged from v4.4.0/v4.5.0 except for the values it reads at render time. The object persists cluster-level driver capability state in the Kubernetes API.

## Dependencies and integration points

The driver name must match controller/node `--drivername` and StorageClass provisioner names. Kubernetes storage components and kubelet consume the attach, lifecycle, and FSGroup declarations when admitting and mounting workloads.

## Risks and test signals

The risk is mismatch between advertised and actual driver behavior. Test a rendered install with default and custom driver names, PVC provisioning, pod mount with FSGroup, and optional inline CSI volumes when enabled. Also verify upgrades do not delete/recreate the `CSIDriver` unexpectedly when only feature toggles change.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose

This v4.6.0 template deploys the node `DaemonSet` for the NFS CSI driver. It provides kubelet CSI registration, liveness probing, and privileged node-side NFS mount handling.

## APIs, control flow, and state

The DaemonSet renders host networking, DNS policy, image pull secrets, priority, scheduling constraints, tolerations, rolling update settings, resources, and images from values. Like the controller, v4.6.0 adds slash-prefixed repository support with `.Values.image.baseRepo`. It switches liveness-probe arguments to `--http-endpoint=localhost:<port>`, removes explicit healthz container ports, and makes Kubernetes liveness checks use numeric ports on localhost.

The registrar registers the CSI socket under `${kubeletDir}/plugins/csi-nfsplugin/csi.sock`. The NFS plugin remains privileged with `SYS_ADMIN` and bidirectional mount propagation to `${kubeletDir}/pods`; sidecars and plugin now drop all capabilities except the explicit add. Optional host NFS config propagation mounts `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d`.

## Dependencies and integration points

This template integrates with kubelet plugin registration, Linux host paths, mount namespaces, the `CSIDriver` object, NFS client behavior, image registries, and node scheduling. Runtime state is sockets, registration files, and mounts on the host.

## Risks and test signals

Image mirror composition can fail if repository values are malformed. Capability dropping and health endpoint changes need runtime validation. Host NFS config propagation may differ across distributions. Test default and mirrored images, DaemonSet rollout, kubelet registration, `CSINode` updates, pod volume mounts, liveness probes, custom `kubeletDir`, and both settings of `propagateHostMountOptions`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose

This v4.6.0 template optionally deploys the external snapshot-controller that reconciles Kubernetes `VolumeSnapshot` APIs.

## APIs, control flow, and state

It renders only when `.Values.externalSnapshotter.enabled` is true. The deployment includes configurable replicas, labels, annotations, image pull secrets, Linux node selection, priority, tolerations, resources, and leader-election arguments. v4.6.0 adds slash-prefixed repository support using `.Values.image.baseRepo` and adds a container security context that drops all capabilities. The controller persists reconciliation state through snapshot resources, status subresources, events, and leader-election leases.

## Dependencies and integration points

The deployment depends on snapshot CRDs, snapshot-controller RBAC, the configured image, and a compatible Kubernetes snapshot API. It complements the `csi-snapshotter` sidecar in the NFS CSI controller deployment.

## Risks and test signals

The external controller should not duplicate a cluster-provided snapshot-controller. Base-repo image composition can render invalid images if values are inconsistent. Test enabled/disabled rendering, private image pull secrets, slash-prefixed image repositories, capability-restricted runtime, leader-election lease updates, and end-to-end snapshot reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml

## Purpose

This v4.6.0 template creates service accounts and cluster RBAC for the NFS CSI driver controller path.

## APIs, control flow, and state

Service accounts render when `.Values.serviceAccount.create` is true, using configurable controller and node names. Cluster RBAC renders when `.Values.rbac.create` is true. The cluster role grants PV create/delete/list/watch, PVC get/list/watch/update, StorageClass reads, snapshot class/snapshot/content reads and content status updates, events writes, CSINode and Node reads, lease CRUD/update/patch for leader election, and Secret get. The binding attaches that role to the controller service account.

The file is functionally the same as v4.5.0 for the requested scope: snapshot permissions are always included rather than gated by external snapshot-controller enablement.

## Dependencies and integration points

The controller deployment depends on this role for the external provisioner and snapshotter sidecars. The role also supports leader election and event recording. Snapshot permissions integrate with CRDs that may be installed by this chart or by the cluster platform.

## Risks and test signals

The RBAC is broad and cluster-scoped; the Secret read and snapshot mutation/status permissions should be reviewed for least privilege. Test `kubectl auth can-i` for each sidecar behavior, disabled RBAC scenarios, custom service account names, provisioning, snapshot workflows, and leader-election lease operations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml

## Purpose

This template creates the service account and RBAC for the optional v4.6.0 external snapshot-controller deployment.

## APIs, control flow, and state

When `.Values.externalSnapshotter.enabled` is true, it renders a service account, cluster role, cluster role binding, release-namespace leader-election role, and role binding. Permissions cover PV/PVC reads and PVC updates, events, snapshot classes, snapshot contents including status, snapshots including status, and optional Node reads for distributed snapshotting. Leader-election state is stored in `coordination.k8s.io` leases in the release namespace.

## Dependencies and integration points

The RBAC is consumed by `csi-snapshot-controller.yaml` and depends on the snapshot API resources being present. It integrates with the same snapshot resources used by the NFS CSI snapshotter sidecar and by user `VolumeSnapshot` objects.

## Risks and test signals

Cluster-scoped snapshot permissions allow mutation across namespaces. The optional distributed snapshotting flag is not part of the default values file, so operators need explicit override knowledge. Test auth checks, enabled/disabled rendering, leader election, snapshot status writes, and behavior when CRDs are absent or managed externally.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/values.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/values.yaml

## Purpose

This file defines the default values for the v4.6.0 NFS CSI driver Helm chart. It configures image repositories/tags, RBAC and service accounts, driver capabilities, kubelet paths, controller and node scheduling/resources, snapshot-controller defaults, CRD rendering, and image pull secrets.

## APIs, control flow, and state

Compared with v4.5.0, it adds `image.baseRepo: registry.k8s.io` and advances images to NFS plugin `v4.6.0`, provisioner `v4.0.0`, snapshotter/snapshot-controller `v6.3.3`, liveness probe `v2.12.0`, and registrar `v2.10.0`. The base repo is used by templates only when a component repository starts with `/`; default repositories remain full image names. Snapshot-controller remains disabled by default while CRD creation remains true under the snapshotter block, meaning CRDs render only if both toggles are true.

Controller and node defaults preserve host-network DNS policy, liveness ports, resources, critical priority, tolerations, `kubeletDir`, driver name, FSGroup policy, inline-volume disabled, and optional host mount option propagation disabled. Values are persisted through Helm release state and rendered Kubernetes resources.

## Dependencies and integration points

The new base-repo setting integrates with v4.6.0 image conditionals in controller, node, and snapshot-controller templates. Other values drive `CSIDriver`, RBAC, CRD, service-account, deployment, and DaemonSet rendering.

## Risks and test signals

Image mirror behavior is easy to misconfigure because only slash-prefixed repositories use `baseRepo`. Upgrading sidecars may change Kubernetes compatibility expectations. Test default render, slash-prefixed mirror render, image pull behavior, upgrade from v4.5.0, snapshot enablement, custom service accounts, custom `kubeletDir`, and host mount option propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/Chart.yaml

## Purpose

This is the Helm chart metadata for the v4.7.0 NFS CSI driver chart. It declares `apiVersion: v1`, `name: csi-driver-nfs`, description `CSI NFS Driver for Kubernetes`, and sets both `version` and `appVersion` to `v4.7.0`.

## APIs, control flow, and state

The file has no runtime control flow. Helm consumes it for chart packaging, repository indexes, release metadata, and display through commands such as `helm show chart`. It is the metadata anchor for the v4.7.0 chart directory, whose templates and values may evolve beyond v4.6.0.

## Dependencies and integration points

The chart metadata integrates with Helm release history, helper templates that reference `.Chart.*`, and operator inventory tooling. `appVersion` should stay aligned with the default NFS plugin image tag in the same chart version's `values.yaml`.

## Risks and test signals

The primary risk is version skew between metadata, directory name, and default driver image. Test with `helm lint`, `helm show chart`, `helm template`, and a comparison against the v4.7.0 `values.yaml` NFS image tag. Packaging checks should ensure downstream chart repositories expose this version correctly.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/Chart.yaml -->
