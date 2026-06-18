# Research: subset-b-000359

Grouped research for the NFS CSI driver deploy manifests, examples, install scripts, RBAC, snapshot resources, and selected historical release manifests. Each section preserves the source path as its title and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/crd-csi-snapshot.yaml

Purpose: installs the CSI snapshot API CRDs used by the NFS driver snapshot examples and by the snapshot sidecars. It defines `VolumeSnapshot` as a namespaced resource and `VolumeSnapshotClass` plus `VolumeSnapshotContent` as cluster-scoped resources under `snapshot.storage.k8s.io/v1`.

Important APIs/types/functions: the three `CustomResourceDefinition` objects expose the Kubernetes snapshot types, OpenAPI schemas, status subresources, additional printer columns, and accepted spec/status fields. Key fields include `VolumeSnapshot.spec.source`, `volumeSnapshotClassName`, `status.readyToUse`, `status.restoreSize`, `VolumeSnapshotClass.driver`, `deletionPolicy`, `parameters`, and `VolumeSnapshotContent.spec.source` with either `volumeHandle` or `snapshotHandle`.

Control flow: this manifest has no executable code; applying it extends the apiserver before `csi-snapshot-controller`, `csi-snapshotter`, `VolumeSnapshotClass`, and `VolumeSnapshot` objects are created. Snapshot creation then flows from a `VolumeSnapshot` to the external snapshot controller, through `VolumeSnapshotContent`, and finally through the NFS CSI driver's snapshot RPCs.

State and persistence: the CRDs make snapshot objects durable Kubernetes API state. `VolumeSnapshotContent` records binding, driver identity, deletion policy, source handles, ready state, restore size, and error status; actual NFS data remains in the driver/backend rather than in the CRD itself.

Dependencies and integration points: depends on Kubernetes `apiextensions.k8s.io/v1` and a cluster version supporting `snapshot.storage.k8s.io/v1`. It integrates with `rbac-snapshot-controller.yaml`, `csi-snapshot-controller.yaml`, `snapshotclass.yaml`, and the NFS controller's `csi-snapshotter` sidecar.

Risks: CRDs must be installed before snapshot controller pods become ready. Removing this file during uninstall can delete all snapshot API objects and their status history. Schema drift from the external-snapshotter version can break admission or controller expectations, and cluster-scoped snapshot content objects need careful RBAC.

Test signals: useful checks are `kubectl apply --server-side --dry-run=server`, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, creating `snapshotclass.yaml`, creating `example/snapshot/snapshot-nfs-dynamic.yaml`, and restoring with `pvc-nfs-snapshot-restored.yaml`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v6.2.0, csi-resizer v2.1.0, csi-snapshotter v8.5.0, livenessprobe v2.18.0, and the canary NFS plugin image from `gcr.io/k8s-staging-sig-storage/nfsplugin:canary`. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. leader election uses `$(POD_NAMESPACE)`, provisioner disables `VolumeAttributesClass`, resizer disables in-use resize errors and `VolumeAttributesClass`, and long 1200s CSI timeouts are configured for create/snapshot operations. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. The canary plugin image is intentionally unstable relative to tagged release manifests. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

Important APIs/types/functions: `attachRequired: false` tells Kubernetes there is no separate attach/detach controller operation for NFS volumes. The declared lifecycle modes are `Persistent` with `fsGroupPolicy: File`; versions with `fsGroupPolicy: File` ask Kubernetes to apply filesystem ownership policy at the file level where supported.

Control flow: after apply, the Kubernetes control plane uses this object during volume scheduling and mount preparation. The node-driver-registrar also advertises the same driver name from the node DaemonSet, so both cluster-level driver metadata and node plugin registration must agree.

State and persistence: this is persistent cluster API metadata. It stores no volume data but changes how the scheduler, kubelet, and admission paths treat NFS CSI volumes.

Dependencies and integration points: consumed by PV/PVC binding, inline or ephemeral CSI volumes if listed, StorageClass provisioning, and kubelet node registration. It must match the driver name used by `storageclass.yaml`, `snapshotclass.yaml`, static PVs, and inline CSI pod specs.

Risks: omitting a lifecycle mode prevents that workload pattern even if the driver binary supports it. Declaring unsupported lifecycle modes can make examples schedule but fail at mount time. Changing `fsGroupPolicy` can affect pod file ownership behavior and expose permission regressions.

Test signals: check `kubectl get csidriver nfs.csi.k8s.io -o yaml`, create a PVC through `nfs-csi`, and for versions declaring ephemeral support run the inline/generic ephemeral examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/csi-nfs-node.yaml

Purpose: deploys the node half of the NFS CSI driver as a Linux `DaemonSet` in `kube-system`. It runs on every schedulable node so kubelet can stage and publish NFS volumes for pods.

Important APIs/types/functions: the manifest defines `csi-nfs-node` with `hostNetwork: true`, broad toleration, `system-node-critical` priority in newer versions, and service account `csi-nfs-node-sa` where that account exists. Containers are livenessprobe v2.18.0, csi-node-driver-registrar v2.16.0, and the canary NFS plugin image. The registrar publishes the kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, while the NFS plugin is privileged, adds `SYS_ADMIN`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

Control flow: kubelet starts the DaemonSet pod, the NFS plugin serves `/csi/csi.sock` from the host plugin directory, the registrar creates the kubelet plugin registration record, and liveness probes restart the pod if the CSI endpoint stops responding. Workload pods that reference NFS CSI volumes then reach this node plugin through kubelet.

State and persistence: durable cluster state is in CSINode objects, PV/PVC objects, pod volume state, and the NFS server. HostPath state persists under `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and pod mount directories until kubelet or the driver cleans them up.

Dependencies and integration points: depends on kubelet plugin directories, Linux mount propagation, the controller deployment for provisioning, the `CSIDriver` object for driver metadata, and reachable NFS network paths from every node.

Risks: privileged mount operations and bidirectional propagation are required but sensitive. Host networking changes DNS and firewall assumptions. If the registrar path or driver name diverges from `nfs.csi.k8s.io`, kubelet will not associate volumes with the plugin. Stale hostPath socket directories can hide failed upgrades.

Test signals: verify DaemonSet readiness on all Linux nodes, inspect `kubectl get csinode`, run a pod mounting `pvc-nfs-dynamic`, and check kubelet/plugin logs for registration and NodePublishVolume success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/csi-snapshot-controller.yaml

Purpose: deploys the external snapshot controller that reconciles Kubernetes `VolumeSnapshot` and `VolumeSnapshotContent` objects for CSI drivers.

Important APIs/types/functions: the file defines an `apps/v1` `Deployment` named `snapshot-controller` in `kube-system`, usually with two replicas, service account `snapshot-controller`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and image `registry.k8s.io/sig-storage/snapshot-controller:v8.5.0`. Arguments enable leader election in the pod namespace or `kube-system` depending on the release.

Control flow: after snapshot CRDs exist, the controller watches `VolumeSnapshot`, `VolumeSnapshotClass`, `VolumeSnapshotContent`, PV, and PVC objects. It binds snapshot requests to snapshot contents, coordinates status updates, and relies on CSI snapshotter sidecars in driver controller pods for driver-specific RPC execution.

State and persistence: the controller persists reconciliation state through snapshot API objects, status fields, Kubernetes Events, and leader-election Leases. It stores no snapshot data in the pod.

Dependencies and integration points: requires `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, and driver-side `csi-snapshotter` support. It integrates with `snapshotclass.yaml` and all `deploy/example/snapshot` resources.

Risks: starting before CRDs are installed leaves the deployment unready or crash-looping. Version skew between the controller, CRDs, and `csi-snapshotter` sidecar can break status transitions. Running two replicas requires working leader election RBAC.

Test signals: check rollout status, verify leader election Leases in `kube-system`, create `snapshot-nfs-dynamic.yaml`, and confirm a ready `VolumeSnapshotContent` plus successful restored PVC.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/cloning/nginx-pod-restored-cloning.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/cloning/nginx-pod-restored-cloning.yaml

Purpose: example Kubernetes manifest demonstrating PVC clone restore smoke test after `pvc-nfs-cloning` binds for the NFS CSI driver.

Important APIs/types/functions: defines Pod resource(s) named `nginx-nfs-restored-cloning`. It mounts PVC `pvc-nfs-cloning` at `/mnt/nfs` and appends timestamps through an nginx container. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/cloning/nginx-pod-restored-cloning.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/cloning/pvc-nfs-cloning.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/cloning/pvc-nfs-cloning.yaml

Purpose: example Kubernetes manifest demonstrating CSI PVC data-source cloning path for the NFS CSI driver.

Important APIs/types/functions: defines PersistentVolumeClaim resource(s) named `pvc-nfs-cloning`. It requests a 10Gi `ReadWriteMany` NFS volume from `nfs-csi` with `dataSource.kind: PersistentVolumeClaim` pointing at `pvc-nfs-dynamic`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/cloning/pvc-nfs-cloning.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/daemonset-nfs-ephemeral.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/daemonset-nfs-ephemeral.yaml

Purpose: example Kubernetes manifest demonstrating generic ephemeral volume scheduling and cleanup for the NFS CSI driver.

Important APIs/types/functions: defines DaemonSet resource(s) named `daemonset-nfs-ephemeral`. It runs one nginx writer per Linux node with an inline generic ephemeral volume claim template using `nfs-csi`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/daemonset-nfs-ephemeral.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/deployment.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/deployment.yaml

Purpose: example Kubernetes manifest demonstrating dynamic provisioning consumed by a Deployment for the NFS CSI driver.

Important APIs/types/functions: defines PVC plus Deployment resource(s) named `pvc-deployment-nfs/deployment-nfs`. It creates a shared `ReadWriteMany` PVC and a one-replica nginx deployment that writes hostname/date data to `/mnt/nfs`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/nfs-provisioner/nfs-server.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/nfs-provisioner/nfs-server.yaml

Purpose: example Kubernetes manifest demonstrating demo backend for the StorageClass examples for the NFS CSI driver.

Important APIs/types/functions: defines Service plus Deployment resource(s) named `nfs-server`. It runs an in-cluster NFS server service on TCP 2049 and UDP 111 backed by hostPath `/nfs-vol`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/nfs-provisioner/nfs-server.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/nfs-provisioner/nginx-pod.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/nfs-provisioner/nginx-pod.yaml

Purpose: example Kubernetes manifest demonstrating static PV binding against the demo NFS server for the NFS CSI driver.

Important APIs/types/functions: defines PV, PVC, Pod resource(s) named `pv-nginx/pvc-nginx/nginx-nfs-example`. It statically defines a CSI PV with volume handle `nfs-server.default.svc.cluster.local/share##`, binds a PVC with empty storageClassName, then mounts it into nginx at `/var/www`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/nfs-provisioner/nginx-pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/nginx-pod-inline-volume.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/nginx-pod-inline-volume.yaml

Purpose: example Kubernetes manifest demonstrating inline CSI volume support without PV/PVC objects for the NFS CSI driver.

Important APIs/types/functions: defines Pod resource(s) named `nginx-pod-inline-volume`. It uses an inline CSI volume with driver `nfs.csi.k8s.io`, server/share attributes, and optional mount options. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/nginx-pod-inline-volume.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/nginx-pod-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/nginx-pod-nfs.yaml

Purpose: example Kubernetes manifest demonstrating basic PVC consumption after dynamic provisioning for the NFS CSI driver.

Important APIs/types/functions: defines Pod resource(s) named `nginx-nfs`. It mounts existing PVC `pvc-nfs-dynamic` into an nginx container at `/mnt/nfs` and continuously writes timestamps. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/nginx-pod-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/pv-nfs-csi.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/pv-nfs-csi.yaml

Purpose: example Kubernetes manifest demonstrating static CSI PV definition for `pvc-nfs-static` for the NFS CSI driver.

Important APIs/types/functions: defines PersistentVolume resource(s) named `pv-nfs`. It defines a 10Gi `ReadWriteMany` static CSI PV with Retain policy, NFSv4.1 mount option, and NFS server/share attributes. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/pv-nfs-csi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/pvc-nfs-csi-dynamic.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/pvc-nfs-csi-dynamic.yaml

Purpose: example Kubernetes manifest demonstrating dynamic provisioning baseline used by pod, clone, and snapshot examples for the NFS CSI driver.

Important APIs/types/functions: defines PersistentVolumeClaim resource(s) named `pvc-nfs-dynamic`. It requests a 10Gi `ReadWriteMany` volume from StorageClass `nfs-csi`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/pvc-nfs-csi-dynamic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/pvc-nfs-csi-static.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/pvc-nfs-csi-static.yaml

Purpose: example Kubernetes manifest demonstrating static PV/PVC binding for the NFS CSI driver.

Important APIs/types/functions: defines PersistentVolumeClaim resource(s) named `pvc-nfs-static`. It requests 10Gi `ReadWriteMany` and binds explicitly to `pv-nfs` while still naming `nfs-csi`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/pvc-nfs-csi-static.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/snapshot/nginx-pod-restored-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/snapshot/nginx-pod-restored-snapshot.yaml

Purpose: example Kubernetes manifest demonstrating post-restore data path validation for the NFS CSI driver.

Important APIs/types/functions: defines Pod resource(s) named `nginx-nfs-restored-snapshot`. It mounts restored PVC `pvc-nfs-snapshot-restored` at `/mnt/nfs` and writes timestamps. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/snapshot/nginx-pod-restored-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/snapshot/pvc-nfs-snapshot-restored.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/snapshot/pvc-nfs-snapshot-restored.yaml

Purpose: example Kubernetes manifest demonstrating snapshot restore flow through Kubernetes dataSource API for the NFS CSI driver.

Important APIs/types/functions: defines PersistentVolumeClaim resource(s) named `pvc-nfs-snapshot-restored`. It requests 10Gi `ReadWriteMany` from `nfs-csi` with a `VolumeSnapshot` data source named `test-nfs-snapshot`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/snapshot/pvc-nfs-snapshot-restored.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/snapshot/snapshot-nfs-dynamic.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/snapshot/snapshot-nfs-dynamic.yaml

Purpose: example Kubernetes manifest demonstrating CSI snapshot creation path for the NFS CSI driver.

Important APIs/types/functions: defines VolumeSnapshot resource(s) named `test-nfs-snapshot`. It captures PVC `pvc-nfs-dynamic` with `volumeSnapshotClassName: csi-nfs-snapclass`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/snapshot/snapshot-nfs-dynamic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/snapshot/snapshotclass-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/snapshot/snapshotclass-nfs.yaml

Purpose: example Kubernetes manifest demonstrating snapshot class for example snapshots for the NFS CSI driver.

Important APIs/types/functions: defines VolumeSnapshotClass resource(s) named `csi-nfs-snapclass`. It binds snapshot operations to driver `nfs.csi.k8s.io` with `deletionPolicy: Delete`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/snapshot/snapshotclass-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/statefulset.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/statefulset.yaml

Purpose: example Kubernetes manifest demonstrating StatefulSet volume claim template behavior for the NFS CSI driver.

Important APIs/types/functions: defines StatefulSet resource(s) named `statefulset-nfs`. It runs one nginx pod with a `volumeClaimTemplates` entry named `persistent-storage` using `nfs-csi` and `ReadWriteOnce`. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/statefulset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/storageclass-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/example/storageclass-nfs.yaml

Purpose: example Kubernetes manifest demonstrating example dynamic provisioning class for the NFS CSI driver.

Important APIs/types/functions: defines StorageClass resource(s) named `nfs-csi`. It points dynamic provisioning at `nfs-server.default.svc.cluster.local` share `/`, uses Delete reclaim policy, Immediate binding, expansion, and NFSv4.1. The examples consistently target Linux nodes and use either StorageClass `nfs-csi`, driver `nfs.csi.k8s.io`, or PVCs created by companion example manifests.

Control flow: users apply prerequisite driver, StorageClass, and backend NFS resources first, then apply this manifest. Kubernetes binds or provisions the requested storage, kubelet asks the NFS CSI node plugin to publish it, and the nginx workload writes or serves data from the mounted path where applicable.

State and persistence: Kubernetes stores object state for the example resources. Data written by pods persists on the backing NFS server according to the PV/PVC reclaim policy, snapshot policy, or ephemeral-volume lifecycle in the specific example.

Dependencies and integration points: integrates with `storageclass-nfs.yaml`, `pvc-nfs-csi-dynamic.yaml`, `pv-nfs-csi.yaml`, `snapshotclass-nfs.yaml`, or the demo NFS server depending on the example. All pod examples depend on healthy node plugin registration and reachable NFS networking.

Risks: samples hard-code namespace `default`, NFS service DNS names, image tags, and simple shell write loops. They are useful smoke tests but not production templates. Delete policies and hostPath-backed demo storage can remove or expose data unexpectedly.

Test signals: apply prerequisites, apply this file, wait for bound PVCs or ready pods, inspect `/mnt/nfs` or `/var/www` contents, then delete resources and verify expected cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/example/storageclass-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/install-driver.sh -->
# sources/control-plane/csi-driver-nfs/deploy/install-driver.sh

Purpose: shell installer for applying the NFS CSI driver manifests from either upstream raw GitHub URLs or the local `./deploy` directory.

Important APIs/types/functions: the script uses Bash with `set -euo pipefail`, accepts `ver` as the first argument defaulting to `master`, and switches to local manifests when the second argument contains `local`. It builds `repo=https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/$ver/deploy`, appends `/$ver` for non-master versions, then runs `kubectl apply` for RBAC, CSIDriver, controller, and node manifests. If the second argument contains `snapshot`, it also applies snapshot CRDs, snapshot-controller RBAC, and snapshot-controller deployment.

Control flow: argument parsing selects remote versus local source, then the script applies core objects in dependency order before optional snapshot objects. Any failed `kubectl apply` aborts because of `set -e`.

State and persistence: the script persists Kubernetes objects into the target cluster and has no local state. Remote mode depends on the current contents of the selected upstream branch/tag.

Dependencies and integration points: requires `kubectl` context access, network access for remote raw manifests unless local mode is used, and a deploy tree matching the selected version. It is the operational entry point for all YAML files in this subset.

Risks: the local mode check is substring-based and tied to the second argument, so argument ordering matters. Remote `master` installs mutable canary manifests. Snapshot install does not separately verify CRD readiness before deploying the controller.

Test signals: run in a disposable cluster with `local snapshot`, verify all expected objects, create a sample PVC and snapshot, and confirm rerunning the script is idempotent.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/install-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/rbac-csi-nfs.yaml

Purpose: grants the Kubernetes permissions needed by the NFS CSI controller and, in newer manifests, names the node service account used by the DaemonSet.

Important APIs/types/functions: the RBAC bundle defines service accounts such as `csi-nfs-controller-sa` and `csi-nfs-node-sa`, `ClusterRole` objects for `nfs-external-provisioner-role` and sometimes `nfs-external-resizer-role`, plus `ClusterRoleBinding` objects binding those roles in `kube-system`. This version contains controller and node service accounts, a provisioner ClusterRole with PV/PVC/StorageClass/snapshot/Event/CSINode/Node/Lease/Secret permissions, and a separate resizer ClusterRole for PVC status and resize events.

Control flow: sidecar containers authenticate through the bound service account tokens, watch Kubernetes resources, update PV/PVC or snapshot status, emit Events, and use `coordination.k8s.io` Leases for leader election. The RBAC file must be applied before controller pods start or their informers fail authorization.

State and persistence: RBAC objects are persistent cluster security policy. They do not store volume data, but they define which controllers can mutate storage and snapshot API state.

Dependencies and integration points: consumed by `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, the provisioner, resizer, and snapshotter sidecars. Secret access supports optional mount-option secrets referenced from StorageClass comments.

Risks: overbroad cluster roles increase blast radius for compromised controller pods. Missing snapshot or resize verbs surface as stuck PVCs or snapshots rather than manifest syntax errors. Older variants cannot support features added by later controller manifests without RBAC expansion.

Test signals: run `kubectl auth can-i` as the controller service account for PV/PVC/watch/update, leases create/update, secret get, and snapshot verbs where applicable; then exercise dynamic provisioning, resize, and snapshot examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/rbac-snapshot-controller.yaml

Purpose: grants the external snapshot controller permission to watch and mutate Kubernetes snapshot resources and to coordinate leader election.

Important APIs/types/functions: the file creates service account `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and matching RoleBinding in `kube-system`. Rules cover PV/PVC reads, PVC updates, Events, `VolumeSnapshotClass`, `VolumeSnapshot`, `VolumeSnapshot/status`, `VolumeSnapshotContent`, and `VolumeSnapshotContent/status`.

Control flow: once bound, snapshot-controller replicas can elect a leader, watch snapshot API objects, create and patch `VolumeSnapshotContent`, update `VolumeSnapshot` status, and emit Events. These permissions are separate from the NFS driver's own snapshotter sidecar RBAC.

State and persistence: the file persists security policy and leader-election access. Runtime snapshot state lives in the CRD objects updated under this authority.

Dependencies and integration points: required by `csi-snapshot-controller.yaml` and `crd-csi-snapshot.yaml`. It must be installed in the same namespace as the snapshot-controller deployment service account.

Risks: missing status verbs leave snapshots permanently pending. Cluster-scoped content update/delete permissions are powerful and should be limited to the snapshot controller service account. Namespace drift between service account, RoleBinding, and Deployment breaks leader election.

Test signals: `kubectl auth can-i` for snapshot resources as `system:serviceaccount:kube-system:snapshot-controller`, deployment rollout, and end-to-end snapshot create/delete with event inspection.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/snapshotclass.yaml

Purpose: defines the example `VolumeSnapshotClass` used for NFS CSI snapshot creation.

Important APIs/types/functions: the object is `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` named `csi-nfs-snapclass`, with driver `nfs.csi.k8s.io` and `deletionPolicy: Delete`.

Control flow: a `VolumeSnapshot` that references this class is reconciled by the snapshot controller, then by the NFS controller's `csi-snapshotter` sidecar, which calls the NFS CSI driver snapshot RPCs.

State and persistence: the class is persistent cluster configuration. Snapshot instances and contents persist separately; `Delete` instructs cleanup of snapshot content when the snapshot object is removed.

Dependencies and integration points: requires snapshot CRDs, snapshot-controller RBAC/deployment, and a controller deployment containing `csi-snapshotter`. It must use the same driver name as the `CSIDriver` and NFS plugin.

Risks: `Delete` is convenient for examples but can remove backend snapshot data. If the class exists without matching sidecars or CRDs, snapshot objects remain pending.

Test signals: apply with server-side dry run, create `snapshot-nfs-dynamic.yaml`, observe `VolumeSnapshotContent`, delete the snapshot, and verify content cleanup follows the policy.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/storageclass.yaml

Purpose: defines the default example dynamic provisioning class for the NFS CSI driver.

Important APIs/types/functions: the object is a `storage.k8s.io/v1` `StorageClass` named `nfs-csi`, with provisioner `nfs.csi.k8s.io`, parameters `server: nfs-server.default.svc.cluster.local` and `share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, `allowVolumeExpansion: true`, and mount option `nfsvers=4.1`.

Control flow: PVCs that name `storageClassName: nfs-csi` trigger the external provisioner in the controller deployment. The driver receives the server/share attributes, creates or selects an NFS subdirectory, and returns a CSI volume handle used by PVs and node publish calls.

State and persistence: the StorageClass is persistent cluster configuration. Provisioned PVs, PVCs, and NFS directories survive independently according to reclaim policy and driver delete behavior.

Dependencies and integration points: depends on the controller deployment, RBAC, `CSIDriver`, node DaemonSet, and a resolvable NFS service matching the `server` value. The optional commented secret parameters integrate with controller secret RBAC for delete-time mount options.

Risks: this sample hard-codes the demo NFS service DNS name and share root. `Immediate` binding can provision before a consumer pod's node constraints are known. `Delete` reclaim can remove backend subdirectories when PVCs are deleted, so it is risky for manual testing against valuable data.

Test signals: create `pvc-nfs-csi-dynamic.yaml`, wait for a bound PV, mount it with `nginx-pod-nfs.yaml`, test expansion, and confirm NFSv4.1 mount options on the node.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/uninstall-driver.sh -->
# sources/control-plane/csi-driver-nfs/deploy/uninstall-driver.sh

Purpose: shell installer for applying the NFS CSI driver manifests from either upstream raw GitHub URLs or the local `./deploy` directory.

Important APIs/types/functions: the script uses Bash with `set -euo pipefail`, accepts `ver` as the first argument defaulting to `master`, and switches to local manifests when the second argument contains `local`. It builds `repo=https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/$ver/deploy`, appends `/$ver` for non-master versions, then runs `kubectl apply` for RBAC, CSIDriver, controller, and node manifests. If the second argument contains `snapshot`, it also applies snapshot CRDs, snapshot-controller RBAC, and snapshot-controller deployment.

Control flow: argument parsing selects remote versus local source, then the script applies core objects in dependency order before optional snapshot objects. Any failed `kubectl apply` aborts because of `set -e`.

State and persistence: the script persists Kubernetes objects into the target cluster and has no local state. Remote mode depends on the current contents of the selected upstream branch/tag.

Dependencies and integration points: requires `kubectl` context access, network access for remote raw manifests unless local mode is used, and a deploy tree matching the selected version. It is the operational entry point for all YAML files in this subset.

Risks: the local mode check is substring-based and tied to the second argument, so argument ordering matters. Remote `master` installs mutable canary manifests. Snapshot install does not separately verify CRD readiness before deploying the controller.

Test signals: run in a disposable cluster with `local snapshot`, verify all expected objects, create a sample PVC and snapshot, and confirm rerunning the script is idempotent.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/uninstall-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v2.2.2, livenessprobe v2.5.0, and nfsplugin v3.0.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. the older controller has only provisioner, liveness, and driver containers; it does not include resizer or snapshotter sidecars. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. This older manifest lacks the later snapshot and resize controller sidecars, so those features require additional manifests or a newer version. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

Important APIs/types/functions: `attachRequired: false` tells Kubernetes there is no separate attach/detach controller operation for NFS volumes. The declared lifecycle modes are Persistent only; versions with `fsGroupPolicy: File` ask Kubernetes to apply filesystem ownership policy at the file level where supported.

Control flow: after apply, the Kubernetes control plane uses this object during volume scheduling and mount preparation. The node-driver-registrar also advertises the same driver name from the node DaemonSet, so both cluster-level driver metadata and node plugin registration must agree.

State and persistence: this is persistent cluster API metadata. It stores no volume data but changes how the scheduler, kubelet, and admission paths treat NFS CSI volumes.

Dependencies and integration points: consumed by PV/PVC binding, inline or ephemeral CSI volumes if listed, StorageClass provisioning, and kubelet node registration. It must match the driver name used by `storageclass.yaml`, `snapshotclass.yaml`, static PVs, and inline CSI pod specs.

Risks: omitting a lifecycle mode prevents that workload pattern even if the driver binary supports it. Declaring unsupported lifecycle modes can make examples schedule but fail at mount time. Changing `fsGroupPolicy` can affect pod file ownership behavior and expose permission regressions.

Test signals: check `kubectl get csidriver nfs.csi.k8s.io -o yaml`, create a PVC through `nfs-csi`, and for versions declaring ephemeral support run the inline/generic ephemeral examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-node.yaml

Purpose: deploys the node half of the NFS CSI driver as a Linux `DaemonSet` in `kube-system`. It runs on every schedulable node so kubelet can stage and publish NFS volumes for pods.

Important APIs/types/functions: the manifest defines `csi-nfs-node` with `hostNetwork: true`, broad toleration, `system-node-critical` priority in newer versions, and service account `csi-nfs-node-sa` where that account exists. Containers are livenessprobe v2.5.0, csi-node-driver-registrar v2.4.0, and nfsplugin v3.0.0. The registrar publishes the kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, while the NFS plugin is privileged, adds `SYS_ADMIN`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

Control flow: kubelet starts the DaemonSet pod, the NFS plugin serves `/csi/csi.sock` from the host plugin directory, the registrar creates the kubelet plugin registration record, and liveness probes restart the pod if the CSI endpoint stops responding. Workload pods that reference NFS CSI volumes then reach this node plugin through kubelet.

State and persistence: durable cluster state is in CSINode objects, PV/PVC objects, pod volume state, and the NFS server. HostPath state persists under `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and pod mount directories until kubelet or the driver cleans them up.

Dependencies and integration points: depends on kubelet plugin directories, Linux mount propagation, the controller deployment for provisioning, the `CSIDriver` object for driver metadata, and reachable NFS network paths from every node.

Risks: privileged mount operations and bidirectional propagation are required but sensitive. Host networking changes DNS and firewall assumptions. If the registrar path or driver name diverges from `nfs.csi.k8s.io`, kubelet will not associate volumes with the plugin. Stale hostPath socket directories can hide failed upgrades.

Test signals: verify DaemonSet readiness on all Linux nodes, inspect `kubectl get csinode`, run a pod mounting `pvc-nfs-dynamic`, and check kubelet/plugin logs for registration and NodePublishVolume success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.0.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.0.0/rbac-csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v3.0.0/rbac-csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v2.2.2, livenessprobe v2.5.0, and nfsplugin v3.0.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. the older controller has only provisioner, liveness, and driver containers; it does not include resizer or snapshotter sidecars. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. This older manifest lacks the later snapshot and resize controller sidecars, so those features require additional manifests or a newer version. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.0.0/rbac-csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v2.2.2, livenessprobe v2.5.0, and nfsplugin v3.1.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. the older controller has only provisioner, liveness, and driver containers; it does not include resizer or snapshotter sidecars. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. This older manifest lacks the later snapshot and resize controller sidecars, so those features require additional manifests or a newer version. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

Important APIs/types/functions: `attachRequired: false` tells Kubernetes there is no separate attach/detach controller operation for NFS volumes. The declared lifecycle modes are Persistent and Ephemeral; versions with `fsGroupPolicy: File` ask Kubernetes to apply filesystem ownership policy at the file level where supported.

Control flow: after apply, the Kubernetes control plane uses this object during volume scheduling and mount preparation. The node-driver-registrar also advertises the same driver name from the node DaemonSet, so both cluster-level driver metadata and node plugin registration must agree.

State and persistence: this is persistent cluster API metadata. It stores no volume data but changes how the scheduler, kubelet, and admission paths treat NFS CSI volumes.

Dependencies and integration points: consumed by PV/PVC binding, inline or ephemeral CSI volumes if listed, StorageClass provisioning, and kubelet node registration. It must match the driver name used by `storageclass.yaml`, `snapshotclass.yaml`, static PVs, and inline CSI pod specs.

Risks: omitting a lifecycle mode prevents that workload pattern even if the driver binary supports it. Declaring unsupported lifecycle modes can make examples schedule but fail at mount time. Changing `fsGroupPolicy` can affect pod file ownership behavior and expose permission regressions.

Test signals: check `kubectl get csidriver nfs.csi.k8s.io -o yaml`, create a PVC through `nfs-csi`, and for versions declaring ephemeral support run the inline/generic ephemeral examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-node.yaml

Purpose: deploys the node half of the NFS CSI driver as a Linux `DaemonSet` in `kube-system`. It runs on every schedulable node so kubelet can stage and publish NFS volumes for pods.

Important APIs/types/functions: the manifest defines `csi-nfs-node` with `hostNetwork: true`, broad toleration, `system-node-critical` priority in newer versions, and service account `csi-nfs-node-sa` where that account exists. Containers are livenessprobe v2.5.0, csi-node-driver-registrar v2.4.0, and nfsplugin v3.1.0. The registrar publishes the kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, while the NFS plugin is privileged, adds `SYS_ADMIN`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

Control flow: kubelet starts the DaemonSet pod, the NFS plugin serves `/csi/csi.sock` from the host plugin directory, the registrar creates the kubelet plugin registration record, and liveness probes restart the pod if the CSI endpoint stops responding. Workload pods that reference NFS CSI volumes then reach this node plugin through kubelet.

State and persistence: durable cluster state is in CSINode objects, PV/PVC objects, pod volume state, and the NFS server. HostPath state persists under `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and pod mount directories until kubelet or the driver cleans them up.

Dependencies and integration points: depends on kubelet plugin directories, Linux mount propagation, the controller deployment for provisioning, the `CSIDriver` object for driver metadata, and reachable NFS network paths from every node.

Risks: privileged mount operations and bidirectional propagation are required but sensitive. Host networking changes DNS and firewall assumptions. If the registrar path or driver name diverges from `nfs.csi.k8s.io`, kubelet will not associate volumes with the plugin. Stale hostPath socket directories can hide failed upgrades.

Test signals: verify DaemonSet readiness on all Linux nodes, inspect `kubectl get csinode`, run a pod mounting `pvc-nfs-dynamic`, and check kubelet/plugin logs for registration and NodePublishVolume success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.1.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.1.0/rbac-csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v3.1.0/rbac-csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v2.2.2, livenessprobe v2.5.0, and nfsplugin v3.1.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. the older controller has only provisioner, liveness, and driver containers; it does not include resizer or snapshotter sidecars. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. This older manifest lacks the later snapshot and resize controller sidecars, so those features require additional manifests or a newer version. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v3.1.0/rbac-csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v3.1.0, livenessprobe v2.6.0, and nfsplugin v4.0.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. the older controller has only provisioner, liveness, and driver containers; it does not include resizer or snapshotter sidecars. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. This older manifest lacks the later snapshot and resize controller sidecars, so those features require additional manifests or a newer version. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

Important APIs/types/functions: `attachRequired: false` tells Kubernetes there is no separate attach/detach controller operation for NFS volumes. The declared lifecycle modes are Persistent and Ephemeral plus `fsGroupPolicy: File`; versions with `fsGroupPolicy: File` ask Kubernetes to apply filesystem ownership policy at the file level where supported.

Control flow: after apply, the Kubernetes control plane uses this object during volume scheduling and mount preparation. The node-driver-registrar also advertises the same driver name from the node DaemonSet, so both cluster-level driver metadata and node plugin registration must agree.

State and persistence: this is persistent cluster API metadata. It stores no volume data but changes how the scheduler, kubelet, and admission paths treat NFS CSI volumes.

Dependencies and integration points: consumed by PV/PVC binding, inline or ephemeral CSI volumes if listed, StorageClass provisioning, and kubelet node registration. It must match the driver name used by `storageclass.yaml`, `snapshotclass.yaml`, static PVs, and inline CSI pod specs.

Risks: omitting a lifecycle mode prevents that workload pattern even if the driver binary supports it. Declaring unsupported lifecycle modes can make examples schedule but fail at mount time. Changing `fsGroupPolicy` can affect pod file ownership behavior and expose permission regressions.

Test signals: check `kubectl get csidriver nfs.csi.k8s.io -o yaml`, create a PVC through `nfs-csi`, and for versions declaring ephemeral support run the inline/generic ephemeral examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-node.yaml

Purpose: deploys the node half of the NFS CSI driver as a Linux `DaemonSet` in `kube-system`. It runs on every schedulable node so kubelet can stage and publish NFS volumes for pods.

Important APIs/types/functions: the manifest defines `csi-nfs-node` with `hostNetwork: true`, broad toleration, `system-node-critical` priority in newer versions, and service account `csi-nfs-node-sa` where that account exists. Containers are livenessprobe v2.6.0, csi-node-driver-registrar v2.5.0, and nfsplugin v4.0.0. The registrar publishes the kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, while the NFS plugin is privileged, adds `SYS_ADMIN`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

Control flow: kubelet starts the DaemonSet pod, the NFS plugin serves `/csi/csi.sock` from the host plugin directory, the registrar creates the kubelet plugin registration record, and liveness probes restart the pod if the CSI endpoint stops responding. Workload pods that reference NFS CSI volumes then reach this node plugin through kubelet.

State and persistence: durable cluster state is in CSINode objects, PV/PVC objects, pod volume state, and the NFS server. HostPath state persists under `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and pod mount directories until kubelet or the driver cleans them up.

Dependencies and integration points: depends on kubelet plugin directories, Linux mount propagation, the controller deployment for provisioning, the `CSIDriver` object for driver metadata, and reachable NFS network paths from every node.

Risks: privileged mount operations and bidirectional propagation are required but sensitive. Host networking changes DNS and firewall assumptions. If the registrar path or driver name diverges from `nfs.csi.k8s.io`, kubelet will not associate volumes with the plugin. Stale hostPath socket directories can hide failed upgrades.

Test signals: verify DaemonSet readiness on all Linux nodes, inspect `kubectl get csinode`, run a pod mounting `pvc-nfs-dynamic`, and check kubelet/plugin logs for registration and NodePublishVolume success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.0.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.0.0/rbac-csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.0.0/rbac-csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v3.1.0, livenessprobe v2.6.0, and nfsplugin v4.0.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. the older controller has only provisioner, liveness, and driver containers; it does not include resizer or snapshotter sidecars. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. This older manifest lacks the later snapshot and resize controller sidecars, so those features require additional manifests or a newer version. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.0.0/rbac-csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v3.2.0, livenessprobe v2.7.0, and nfsplugin v4.1.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. the older controller has only provisioner, liveness, and driver containers; it does not include resizer or snapshotter sidecars. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. This older manifest lacks the later snapshot and resize controller sidecars, so those features require additional manifests or a newer version. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

Important APIs/types/functions: `attachRequired: false` tells Kubernetes there is no separate attach/detach controller operation for NFS volumes. The declared lifecycle modes are Persistent and Ephemeral plus `fsGroupPolicy: File`; versions with `fsGroupPolicy: File` ask Kubernetes to apply filesystem ownership policy at the file level where supported.

Control flow: after apply, the Kubernetes control plane uses this object during volume scheduling and mount preparation. The node-driver-registrar also advertises the same driver name from the node DaemonSet, so both cluster-level driver metadata and node plugin registration must agree.

State and persistence: this is persistent cluster API metadata. It stores no volume data but changes how the scheduler, kubelet, and admission paths treat NFS CSI volumes.

Dependencies and integration points: consumed by PV/PVC binding, inline or ephemeral CSI volumes if listed, StorageClass provisioning, and kubelet node registration. It must match the driver name used by `storageclass.yaml`, `snapshotclass.yaml`, static PVs, and inline CSI pod specs.

Risks: omitting a lifecycle mode prevents that workload pattern even if the driver binary supports it. Declaring unsupported lifecycle modes can make examples schedule but fail at mount time. Changing `fsGroupPolicy` can affect pod file ownership behavior and expose permission regressions.

Test signals: check `kubectl get csidriver nfs.csi.k8s.io -o yaml`, create a PVC through `nfs-csi`, and for versions declaring ephemeral support run the inline/generic ephemeral examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-node.yaml

Purpose: deploys the node half of the NFS CSI driver as a Linux `DaemonSet` in `kube-system`. It runs on every schedulable node so kubelet can stage and publish NFS volumes for pods.

Important APIs/types/functions: the manifest defines `csi-nfs-node` with `hostNetwork: true`, broad toleration, `system-node-critical` priority in newer versions, and service account `csi-nfs-node-sa` where that account exists. Containers are livenessprobe v2.7.0, csi-node-driver-registrar v2.5.1, and nfsplugin v4.1.0. The registrar publishes the kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, while the NFS plugin is privileged, adds `SYS_ADMIN`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

Control flow: kubelet starts the DaemonSet pod, the NFS plugin serves `/csi/csi.sock` from the host plugin directory, the registrar creates the kubelet plugin registration record, and liveness probes restart the pod if the CSI endpoint stops responding. Workload pods that reference NFS CSI volumes then reach this node plugin through kubelet.

State and persistence: durable cluster state is in CSINode objects, PV/PVC objects, pod volume state, and the NFS server. HostPath state persists under `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and pod mount directories until kubelet or the driver cleans them up.

Dependencies and integration points: depends on kubelet plugin directories, Linux mount propagation, the controller deployment for provisioning, the `CSIDriver` object for driver metadata, and reachable NFS network paths from every node.

Risks: privileged mount operations and bidirectional propagation are required but sensitive. Host networking changes DNS and firewall assumptions. If the registrar path or driver name diverges from `nfs.csi.k8s.io`, kubelet will not associate volumes with the plugin. Stale hostPath socket directories can hide failed upgrades.

Test signals: verify DaemonSet readiness on all Linux nodes, inspect `kubectl get csinode`, run a pod mounting `pvc-nfs-dynamic`, and check kubelet/plugin logs for registration and NodePublishVolume success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.1.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.1.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.1.0/rbac-csi-nfs.yaml

Purpose: grants the Kubernetes permissions needed by the NFS CSI controller and, in newer manifests, names the node service account used by the DaemonSet.

Important APIs/types/functions: the RBAC bundle defines service accounts such as `csi-nfs-controller-sa` and `csi-nfs-node-sa`, `ClusterRole` objects for `nfs-external-provisioner-role` and sometimes `nfs-external-resizer-role`, plus `ClusterRoleBinding` objects binding those roles in `kube-system`. This version contains controller and node service accounts plus a provisioner ClusterRole with PV/PVC/StorageClass/Event/CSINode/Node/Lease/Secret access; no resizer or snapshot rules yet.

Control flow: sidecar containers authenticate through the bound service account tokens, watch Kubernetes resources, update PV/PVC or snapshot status, emit Events, and use `coordination.k8s.io` Leases for leader election. The RBAC file must be applied before controller pods start or their informers fail authorization.

State and persistence: RBAC objects are persistent cluster security policy. They do not store volume data, but they define which controllers can mutate storage and snapshot API state.

Dependencies and integration points: consumed by `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, the provisioner, resizer, and snapshotter sidecars. Secret access supports optional mount-option secrets referenced from StorageClass comments.

Risks: overbroad cluster roles increase blast radius for compromised controller pods. Missing snapshot or resize verbs surface as stuck PVCs or snapshots rather than manifest syntax errors. Older variants cannot support features added by later controller manifests without RBAC expansion.

Test signals: run `kubectl auth can-i` as the controller service account for PV/PVC/watch/update, leases create/update, secret get, and snapshot verbs where applicable; then exercise dynamic provisioning, resize, and snapshot examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.1.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/crd-csi-snapshot.yaml

Purpose: installs the CSI snapshot API CRDs used by the NFS driver snapshot examples and by the snapshot sidecars. It defines `VolumeSnapshot` as a namespaced resource and `VolumeSnapshotClass` plus `VolumeSnapshotContent` as cluster-scoped resources under `snapshot.storage.k8s.io/v1`.

Important APIs/types/functions: the three `CustomResourceDefinition` objects expose the Kubernetes snapshot types, OpenAPI schemas, status subresources, additional printer columns, and accepted spec/status fields. Key fields include `VolumeSnapshot.spec.source`, `volumeSnapshotClassName`, `status.readyToUse`, `status.restoreSize`, `VolumeSnapshotClass.driver`, `deletionPolicy`, `parameters`, and `VolumeSnapshotContent.spec.source` with either `volumeHandle` or `snapshotHandle`.

Control flow: this manifest has no executable code; applying it extends the apiserver before `csi-snapshot-controller`, `csi-snapshotter`, `VolumeSnapshotClass`, and `VolumeSnapshot` objects are created. Snapshot creation then flows from a `VolumeSnapshot` to the external snapshot controller, through `VolumeSnapshotContent`, and finally through the NFS CSI driver's snapshot RPCs.

State and persistence: the CRDs make snapshot objects durable Kubernetes API state. `VolumeSnapshotContent` records binding, driver identity, deletion policy, source handles, ready state, restore size, and error status; actual NFS data remains in the driver/backend rather than in the CRD itself.

Dependencies and integration points: depends on Kubernetes `apiextensions.k8s.io/v1` and a cluster version supporting `snapshot.storage.k8s.io/v1`. It integrates with `rbac-snapshot-controller.yaml`, `csi-snapshot-controller.yaml`, `snapshotclass.yaml`, and the NFS controller's `csi-snapshotter` sidecar.

Risks: CRDs must be installed before snapshot controller pods become ready. Removing this file during uninstall can delete all snapshot API objects and their status history. Schema drift from the external-snapshotter version can break admission or controller expectations, and cluster-scoped snapshot content objects need careful RBAC.

Test signals: useful checks are `kubectl apply --server-side --dry-run=server`, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, creating `snapshotclass.yaml`, creating `example/snapshot/snapshot-nfs-dynamic.yaml`, and restoring with `pvc-nfs-snapshot-restored.yaml`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v5.2.0, csi-resizer v1.13.1, csi-snapshotter v8.2.0, livenessprobe v2.15.0, and nfsplugin v4.10.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. leader election is pinned to `kube-system`, the provisioner enables `HonorPVReclaimPolicy`, and long 1200s CSI timeouts plus 30m retry intervals are configured. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. The release-tagged plugin image is stable for this version, but sidecar upgrades still need compatibility checks. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

Important APIs/types/functions: `attachRequired: false` tells Kubernetes there is no separate attach/detach controller operation for NFS volumes. The declared lifecycle modes are Persistent plus `fsGroupPolicy: File`; versions with `fsGroupPolicy: File` ask Kubernetes to apply filesystem ownership policy at the file level where supported.

Control flow: after apply, the Kubernetes control plane uses this object during volume scheduling and mount preparation. The node-driver-registrar also advertises the same driver name from the node DaemonSet, so both cluster-level driver metadata and node plugin registration must agree.

State and persistence: this is persistent cluster API metadata. It stores no volume data but changes how the scheduler, kubelet, and admission paths treat NFS CSI volumes.

Dependencies and integration points: consumed by PV/PVC binding, inline or ephemeral CSI volumes if listed, StorageClass provisioning, and kubelet node registration. It must match the driver name used by `storageclass.yaml`, `snapshotclass.yaml`, static PVs, and inline CSI pod specs.

Risks: omitting a lifecycle mode prevents that workload pattern even if the driver binary supports it. Declaring unsupported lifecycle modes can make examples schedule but fail at mount time. Changing `fsGroupPolicy` can affect pod file ownership behavior and expose permission regressions.

Test signals: check `kubectl get csidriver nfs.csi.k8s.io -o yaml`, create a PVC through `nfs-csi`, and for versions declaring ephemeral support run the inline/generic ephemeral examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-node.yaml

Purpose: deploys the node half of the NFS CSI driver as a Linux `DaemonSet` in `kube-system`. It runs on every schedulable node so kubelet can stage and publish NFS volumes for pods.

Important APIs/types/functions: the manifest defines `csi-nfs-node` with `hostNetwork: true`, broad toleration, `system-node-critical` priority in newer versions, and service account `csi-nfs-node-sa` where that account exists. Containers are livenessprobe v2.15.0, csi-node-driver-registrar v2.13.0, and nfsplugin v4.10.0. The registrar publishes the kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, while the NFS plugin is privileged, adds `SYS_ADMIN`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

Control flow: kubelet starts the DaemonSet pod, the NFS plugin serves `/csi/csi.sock` from the host plugin directory, the registrar creates the kubelet plugin registration record, and liveness probes restart the pod if the CSI endpoint stops responding. Workload pods that reference NFS CSI volumes then reach this node plugin through kubelet.

State and persistence: durable cluster state is in CSINode objects, PV/PVC objects, pod volume state, and the NFS server. HostPath state persists under `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and pod mount directories until kubelet or the driver cleans them up.

Dependencies and integration points: depends on kubelet plugin directories, Linux mount propagation, the controller deployment for provisioning, the `CSIDriver` object for driver metadata, and reachable NFS network paths from every node.

Risks: privileged mount operations and bidirectional propagation are required but sensitive. Host networking changes DNS and firewall assumptions. If the registrar path or driver name diverges from `nfs.csi.k8s.io`, kubelet will not associate volumes with the plugin. Stale hostPath socket directories can hide failed upgrades.

Test signals: verify DaemonSet readiness on all Linux nodes, inspect `kubectl get csinode`, run a pod mounting `pvc-nfs-dynamic`, and check kubelet/plugin logs for registration and NodePublishVolume success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-snapshot-controller.yaml

Purpose: deploys the external snapshot controller that reconciles Kubernetes `VolumeSnapshot` and `VolumeSnapshotContent` objects for CSI drivers.

Important APIs/types/functions: the file defines an `apps/v1` `Deployment` named `snapshot-controller` in `kube-system`, usually with two replicas, service account `snapshot-controller`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and image `registry.k8s.io/sig-storage/snapshot-controller:v8.2.0`. Arguments enable leader election in the pod namespace or `kube-system` depending on the release.

Control flow: after snapshot CRDs exist, the controller watches `VolumeSnapshot`, `VolumeSnapshotClass`, `VolumeSnapshotContent`, PV, and PVC objects. It binds snapshot requests to snapshot contents, coordinates status updates, and relies on CSI snapshotter sidecars in driver controller pods for driver-specific RPC execution.

State and persistence: the controller persists reconciliation state through snapshot API objects, status fields, Kubernetes Events, and leader-election Leases. It stores no snapshot data in the pod.

Dependencies and integration points: requires `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, and driver-side `csi-snapshotter` support. It integrates with `snapshotclass.yaml` and all `deploy/example/snapshot` resources.

Risks: starting before CRDs are installed leaves the deployment unready or crash-looping. Version skew between the controller, CRDs, and `csi-snapshotter` sidecar can break status transitions. Running two replicas requires working leader election RBAC.

Test signals: check rollout status, verify leader election Leases in `kube-system`, create `snapshot-nfs-dynamic.yaml`, and confirm a ready `VolumeSnapshotContent` plus successful restored PVC.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/rbac-csi-nfs.yaml

Purpose: grants the Kubernetes permissions needed by the NFS CSI controller and, in newer manifests, names the node service account used by the DaemonSet.

Important APIs/types/functions: the RBAC bundle defines service accounts such as `csi-nfs-controller-sa` and `csi-nfs-node-sa`, `ClusterRole` objects for `nfs-external-provisioner-role` and sometimes `nfs-external-resizer-role`, plus `ClusterRoleBinding` objects binding those roles in `kube-system`. This version contains controller and node service accounts, a provisioner ClusterRole with PV/PVC/StorageClass/snapshot/Event/CSINode/Node/Lease/Secret permissions, and a separate resizer ClusterRole for PVC status and resize events.

Control flow: sidecar containers authenticate through the bound service account tokens, watch Kubernetes resources, update PV/PVC or snapshot status, emit Events, and use `coordination.k8s.io` Leases for leader election. The RBAC file must be applied before controller pods start or their informers fail authorization.

State and persistence: RBAC objects are persistent cluster security policy. They do not store volume data, but they define which controllers can mutate storage and snapshot API state.

Dependencies and integration points: consumed by `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, the provisioner, resizer, and snapshotter sidecars. Secret access supports optional mount-option secrets referenced from StorageClass comments.

Risks: overbroad cluster roles increase blast radius for compromised controller pods. Missing snapshot or resize verbs surface as stuck PVCs or snapshots rather than manifest syntax errors. Older variants cannot support features added by later controller manifests without RBAC expansion.

Test signals: run `kubectl auth can-i` as the controller service account for PV/PVC/watch/update, leases create/update, secret get, and snapshot verbs where applicable; then exercise dynamic provisioning, resize, and snapshot examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/rbac-snapshot-controller.yaml

Purpose: grants the external snapshot controller permission to watch and mutate Kubernetes snapshot resources and to coordinate leader election.

Important APIs/types/functions: the file creates service account `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and matching RoleBinding in `kube-system`. Rules cover PV/PVC reads, PVC updates, Events, `VolumeSnapshotClass`, `VolumeSnapshot`, `VolumeSnapshot/status`, `VolumeSnapshotContent`, and `VolumeSnapshotContent/status`.

Control flow: once bound, snapshot-controller replicas can elect a leader, watch snapshot API objects, create and patch `VolumeSnapshotContent`, update `VolumeSnapshot` status, and emit Events. These permissions are separate from the NFS driver's own snapshotter sidecar RBAC.

State and persistence: the file persists security policy and leader-election access. Runtime snapshot state lives in the CRD objects updated under this authority.

Dependencies and integration points: required by `csi-snapshot-controller.yaml` and `crd-csi-snapshot.yaml`. It must be installed in the same namespace as the snapshot-controller deployment service account.

Risks: missing status verbs leave snapshots permanently pending. Cluster-scoped content update/delete permissions are powerful and should be limited to the snapshot controller service account. Namespace drift between service account, RoleBinding, and Deployment breaks leader election.

Test signals: `kubectl auth can-i` for snapshot resources as `system:serviceaccount:kube-system:snapshot-controller`, deployment rollout, and end-to-end snapshot create/delete with event inspection.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/snapshotclass.yaml

Purpose: defines the example `VolumeSnapshotClass` used for NFS CSI snapshot creation.

Important APIs/types/functions: the object is `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` named `csi-nfs-snapclass`, with driver `nfs.csi.k8s.io` and `deletionPolicy: Delete`.

Control flow: a `VolumeSnapshot` that references this class is reconciled by the snapshot controller, then by the NFS controller's `csi-snapshotter` sidecar, which calls the NFS CSI driver snapshot RPCs.

State and persistence: the class is persistent cluster configuration. Snapshot instances and contents persist separately; `Delete` instructs cleanup of snapshot content when the snapshot object is removed.

Dependencies and integration points: requires snapshot CRDs, snapshot-controller RBAC/deployment, and a controller deployment containing `csi-snapshotter`. It must use the same driver name as the `CSIDriver` and NFS plugin.

Risks: `Delete` is convenient for examples but can remove backend snapshot data. If the class exists without matching sidecars or CRDs, snapshot objects remain pending.

Test signals: apply with server-side dry run, create `snapshot-nfs-dynamic.yaml`, observe `VolumeSnapshotContent`, delete the snapshot, and verify content cleanup follows the policy.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.10.0/storageclass.yaml

Purpose: defines the default example dynamic provisioning class for the NFS CSI driver.

Important APIs/types/functions: the object is a `storage.k8s.io/v1` `StorageClass` named `nfs-csi`, with provisioner `nfs.csi.k8s.io`, parameters `server: nfs-server.default.svc.cluster.local` and `share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, `allowVolumeExpansion: true`, and mount option `nfsvers=4.1`.

Control flow: PVCs that name `storageClassName: nfs-csi` trigger the external provisioner in the controller deployment. The driver receives the server/share attributes, creates or selects an NFS subdirectory, and returns a CSI volume handle used by PVs and node publish calls.

State and persistence: the StorageClass is persistent cluster configuration. Provisioned PVs, PVCs, and NFS directories survive independently according to reclaim policy and driver delete behavior.

Dependencies and integration points: depends on the controller deployment, RBAC, `CSIDriver`, node DaemonSet, and a resolvable NFS service matching the `server` value. The optional commented secret parameters integrate with controller secret RBAC for delete-time mount options.

Risks: this sample hard-codes the demo NFS service DNS name and share root. `Immediate` binding can provision before a consumer pod's node constraints are known. `Delete` reclaim can remove backend subdirectories when PVCs are deleted, so it is risky for manual testing against valuable data.

Test signals: create `pvc-nfs-csi-dynamic.yaml`, wait for a bound PV, mount it with `nginx-pod-nfs.yaml`, test expansion, and confirm NFSv4.1 mount options on the node.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.10.0/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/crd-csi-snapshot.yaml

Purpose: installs the CSI snapshot API CRDs used by the NFS driver snapshot examples and by the snapshot sidecars. It defines `VolumeSnapshot` as a namespaced resource and `VolumeSnapshotClass` plus `VolumeSnapshotContent` as cluster-scoped resources under `snapshot.storage.k8s.io/v1`.

Important APIs/types/functions: the three `CustomResourceDefinition` objects expose the Kubernetes snapshot types, OpenAPI schemas, status subresources, additional printer columns, and accepted spec/status fields. Key fields include `VolumeSnapshot.spec.source`, `volumeSnapshotClassName`, `status.readyToUse`, `status.restoreSize`, `VolumeSnapshotClass.driver`, `deletionPolicy`, `parameters`, and `VolumeSnapshotContent.spec.source` with either `volumeHandle` or `snapshotHandle`.

Control flow: this manifest has no executable code; applying it extends the apiserver before `csi-snapshot-controller`, `csi-snapshotter`, `VolumeSnapshotClass`, and `VolumeSnapshot` objects are created. Snapshot creation then flows from a `VolumeSnapshot` to the external snapshot controller, through `VolumeSnapshotContent`, and finally through the NFS CSI driver's snapshot RPCs.

State and persistence: the CRDs make snapshot objects durable Kubernetes API state. `VolumeSnapshotContent` records binding, driver identity, deletion policy, source handles, ready state, restore size, and error status; actual NFS data remains in the driver/backend rather than in the CRD itself.

Dependencies and integration points: depends on Kubernetes `apiextensions.k8s.io/v1` and a cluster version supporting `snapshot.storage.k8s.io/v1`. It integrates with `rbac-snapshot-controller.yaml`, `csi-snapshot-controller.yaml`, `snapshotclass.yaml`, and the NFS controller's `csi-snapshotter` sidecar.

Risks: CRDs must be installed before snapshot controller pods become ready. Removing this file during uninstall can delete all snapshot API objects and their status history. Schema drift from the external-snapshotter version can break admission or controller expectations, and cluster-scoped snapshot content objects need careful RBAC.

Test signals: useful checks are `kubectl apply --server-side --dry-run=server`, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, creating `snapshotclass.yaml`, creating `example/snapshot/snapshot-nfs-dynamic.yaml`, and restoring with `pvc-nfs-snapshot-restored.yaml`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-controller.yaml

Purpose: deploys the NFS CSI controller in `kube-system`. The controller handles control-plane CSI calls such as dynamic provisioning, deletion, expansion in newer versions, and snapshot orchestration when the matching sidecars are present.

Important APIs/types/functions: the manifest is an `apps/v1` `Deployment` named `csi-nfs-controller` with one replica, `hostNetwork: true`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and service account `csi-nfs-controller-sa`. It runs csi-provisioner v5.2.0, csi-resizer v1.13.1, csi-snapshotter v8.2.0, livenessprobe v2.15.0, and nfsplugin v4.11.0. The driver container is privileged, adds `SYS_ADMIN`, exposes the CSI socket at `/csi/csi.sock`, and mounts `/var/lib/kubelet/pods` bidirectionally so controller-side NFS directory operations can use host mount semantics.

Control flow: Kubernetes schedules the deployment, the NFS container serves the CSI endpoint on an `emptyDir` socket, and sidecars connect to that endpoint. leader election is pinned to `kube-system`, the provisioner enables `HonorPVReclaimPolicy`, and long 1200s CSI timeouts plus 30m retry intervals are configured. Liveness probes use the local health endpoint and cause pod restarts when the driver endpoint stops responding.

State and persistence: controller state is mostly Kubernetes API state in PVs, PVCs, VolumeSnapshots, VolumeSnapshotContents, Leases, and Events. The pod itself uses an ephemeral CSI socket directory; persistent NFS data is stored on the configured server/share and subdirectories rather than in the controller pod.

Dependencies and integration points: depends on `rbac-csi-nfs.yaml` or the versioned RBAC file, `csi-nfs-driverinfo.yaml`, the node DaemonSet, kubelet pod mount paths, and a reachable NFS server. Snapshot behavior also depends on snapshot CRDs, snapshot controller RBAC, and snapshot class manifests.

Risks: privileged `SYS_ADMIN`, host networking, and bidirectional `/var/lib/kubelet/pods` mount propagation are high-trust settings. Controller placement on control-plane nodes relies on tolerations and may fail under custom taints. The release-tagged plugin image is stable for this version, but sidecar upgrades still need compatibility checks. Sidecar and CRD version skew is the main compatibility risk.

Test signals: validate with `kubectl apply --dry-run=server`, rollout status for `deployment/csi-nfs-controller`, a dynamically provisioned PVC from `storageclass.yaml`, expansion of an existing PVC for resize-capable versions, and snapshot/restore flows when snapshot sidecars are included.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`.

Important APIs/types/functions: `attachRequired: false` tells Kubernetes there is no separate attach/detach controller operation for NFS volumes. The declared lifecycle modes are Persistent plus `fsGroupPolicy: File`; versions with `fsGroupPolicy: File` ask Kubernetes to apply filesystem ownership policy at the file level where supported.

Control flow: after apply, the Kubernetes control plane uses this object during volume scheduling and mount preparation. The node-driver-registrar also advertises the same driver name from the node DaemonSet, so both cluster-level driver metadata and node plugin registration must agree.

State and persistence: this is persistent cluster API metadata. It stores no volume data but changes how the scheduler, kubelet, and admission paths treat NFS CSI volumes.

Dependencies and integration points: consumed by PV/PVC binding, inline or ephemeral CSI volumes if listed, StorageClass provisioning, and kubelet node registration. It must match the driver name used by `storageclass.yaml`, `snapshotclass.yaml`, static PVs, and inline CSI pod specs.

Risks: omitting a lifecycle mode prevents that workload pattern even if the driver binary supports it. Declaring unsupported lifecycle modes can make examples schedule but fail at mount time. Changing `fsGroupPolicy` can affect pod file ownership behavior and expose permission regressions.

Test signals: check `kubectl get csidriver nfs.csi.k8s.io -o yaml`, create a PVC through `nfs-csi`, and for versions declaring ephemeral support run the inline/generic ephemeral examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-node.yaml

Purpose: deploys the node half of the NFS CSI driver as a Linux `DaemonSet` in `kube-system`. It runs on every schedulable node so kubelet can stage and publish NFS volumes for pods.

Important APIs/types/functions: the manifest defines `csi-nfs-node` with `hostNetwork: true`, broad toleration, `system-node-critical` priority in newer versions, and service account `csi-nfs-node-sa` where that account exists. Containers are livenessprobe v2.15.0, csi-node-driver-registrar v2.13.0, and nfsplugin v4.11.0. The registrar publishes the kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`, while the NFS plugin is privileged, adds `SYS_ADMIN`, and mounts `/var/lib/kubelet/pods` with bidirectional propagation.

Control flow: kubelet starts the DaemonSet pod, the NFS plugin serves `/csi/csi.sock` from the host plugin directory, the registrar creates the kubelet plugin registration record, and liveness probes restart the pod if the CSI endpoint stops responding. Workload pods that reference NFS CSI volumes then reach this node plugin through kubelet.

State and persistence: durable cluster state is in CSINode objects, PV/PVC objects, pod volume state, and the NFS server. HostPath state persists under `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/plugins_registry`, and pod mount directories until kubelet or the driver cleans them up.

Dependencies and integration points: depends on kubelet plugin directories, Linux mount propagation, the controller deployment for provisioning, the `CSIDriver` object for driver metadata, and reachable NFS network paths from every node.

Risks: privileged mount operations and bidirectional propagation are required but sensitive. Host networking changes DNS and firewall assumptions. If the registrar path or driver name diverges from `nfs.csi.k8s.io`, kubelet will not associate volumes with the plugin. Stale hostPath socket directories can hide failed upgrades.

Test signals: verify DaemonSet readiness on all Linux nodes, inspect `kubectl get csinode`, run a pod mounting `pvc-nfs-dynamic`, and check kubelet/plugin logs for registration and NodePublishVolume success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-snapshot-controller.yaml

Purpose: deploys the external snapshot controller that reconciles Kubernetes `VolumeSnapshot` and `VolumeSnapshotContent` objects for CSI drivers.

Important APIs/types/functions: the file defines an `apps/v1` `Deployment` named `snapshot-controller` in `kube-system`, usually with two replicas, service account `snapshot-controller`, Linux node selection, control-plane tolerations, `system-cluster-critical` priority, and image `registry.k8s.io/sig-storage/snapshot-controller:v8.2.0`. Arguments enable leader election in the pod namespace or `kube-system` depending on the release.

Control flow: after snapshot CRDs exist, the controller watches `VolumeSnapshot`, `VolumeSnapshotClass`, `VolumeSnapshotContent`, PV, and PVC objects. It binds snapshot requests to snapshot contents, coordinates status updates, and relies on CSI snapshotter sidecars in driver controller pods for driver-specific RPC execution.

State and persistence: the controller persists reconciliation state through snapshot API objects, status fields, Kubernetes Events, and leader-election Leases. It stores no snapshot data in the pod.

Dependencies and integration points: requires `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, and driver-side `csi-snapshotter` support. It integrates with `snapshotclass.yaml` and all `deploy/example/snapshot` resources.

Risks: starting before CRDs are installed leaves the deployment unready or crash-looping. Version skew between the controller, CRDs, and `csi-snapshotter` sidecar can break status transitions. Running two replicas requires working leader election RBAC.

Test signals: check rollout status, verify leader election Leases in `kube-system`, create `snapshot-nfs-dynamic.yaml`, and confirm a ready `VolumeSnapshotContent` plus successful restored PVC.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/rbac-csi-nfs.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/rbac-csi-nfs.yaml

Purpose: grants the Kubernetes permissions needed by the NFS CSI controller and, in newer manifests, names the node service account used by the DaemonSet.

Important APIs/types/functions: the RBAC bundle defines service accounts such as `csi-nfs-controller-sa` and `csi-nfs-node-sa`, `ClusterRole` objects for `nfs-external-provisioner-role` and sometimes `nfs-external-resizer-role`, plus `ClusterRoleBinding` objects binding those roles in `kube-system`. This version contains controller and node service accounts, a provisioner ClusterRole with PV/PVC/StorageClass/snapshot/Event/CSINode/Node/Lease/Secret permissions, and a separate resizer ClusterRole for PVC status and resize events.

Control flow: sidecar containers authenticate through the bound service account tokens, watch Kubernetes resources, update PV/PVC or snapshot status, emit Events, and use `coordination.k8s.io` Leases for leader election. The RBAC file must be applied before controller pods start or their informers fail authorization.

State and persistence: RBAC objects are persistent cluster security policy. They do not store volume data, but they define which controllers can mutate storage and snapshot API state.

Dependencies and integration points: consumed by `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, the provisioner, resizer, and snapshotter sidecars. Secret access supports optional mount-option secrets referenced from StorageClass comments.

Risks: overbroad cluster roles increase blast radius for compromised controller pods. Missing snapshot or resize verbs surface as stuck PVCs or snapshots rather than manifest syntax errors. Older variants cannot support features added by later controller manifests without RBAC expansion.

Test signals: run `kubectl auth can-i` as the controller service account for PV/PVC/watch/update, leases create/update, secret get, and snapshot verbs where applicable; then exercise dynamic provisioning, resize, and snapshot examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/rbac-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/rbac-snapshot-controller.yaml

Purpose: grants the external snapshot controller permission to watch and mutate Kubernetes snapshot resources and to coordinate leader election.

Important APIs/types/functions: the file creates service account `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and matching RoleBinding in `kube-system`. Rules cover PV/PVC reads, PVC updates, Events, `VolumeSnapshotClass`, `VolumeSnapshot`, `VolumeSnapshot/status`, `VolumeSnapshotContent`, and `VolumeSnapshotContent/status`.

Control flow: once bound, snapshot-controller replicas can elect a leader, watch snapshot API objects, create and patch `VolumeSnapshotContent`, update `VolumeSnapshot` status, and emit Events. These permissions are separate from the NFS driver's own snapshotter sidecar RBAC.

State and persistence: the file persists security policy and leader-election access. Runtime snapshot state lives in the CRD objects updated under this authority.

Dependencies and integration points: required by `csi-snapshot-controller.yaml` and `crd-csi-snapshot.yaml`. It must be installed in the same namespace as the snapshot-controller deployment service account.

Risks: missing status verbs leave snapshots permanently pending. Cluster-scoped content update/delete permissions are powerful and should be limited to the snapshot controller service account. Namespace drift between service account, RoleBinding, and Deployment breaks leader election.

Test signals: `kubectl auth can-i` for snapshot resources as `system:serviceaccount:kube-system:snapshot-controller`, deployment rollout, and end-to-end snapshot create/delete with event inspection.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/snapshotclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/snapshotclass.yaml

Purpose: defines the example `VolumeSnapshotClass` used for NFS CSI snapshot creation.

Important APIs/types/functions: the object is `snapshot.storage.k8s.io/v1` `VolumeSnapshotClass` named `csi-nfs-snapclass`, with driver `nfs.csi.k8s.io` and `deletionPolicy: Delete`.

Control flow: a `VolumeSnapshot` that references this class is reconciled by the snapshot controller, then by the NFS controller's `csi-snapshotter` sidecar, which calls the NFS CSI driver snapshot RPCs.

State and persistence: the class is persistent cluster configuration. Snapshot instances and contents persist separately; `Delete` instructs cleanup of snapshot content when the snapshot object is removed.

Dependencies and integration points: requires snapshot CRDs, snapshot-controller RBAC/deployment, and a controller deployment containing `csi-snapshotter`. It must use the same driver name as the `CSIDriver` and NFS plugin.

Risks: `Delete` is convenient for examples but can remove backend snapshot data. If the class exists without matching sidecars or CRDs, snapshot objects remain pending.

Test signals: apply with server-side dry run, create `snapshot-nfs-dynamic.yaml`, observe `VolumeSnapshotContent`, delete the snapshot, and verify content cleanup follows the policy.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/storageclass.yaml -->
# sources/control-plane/csi-driver-nfs/deploy/v4.11.0/storageclass.yaml

Purpose: defines the default example dynamic provisioning class for the NFS CSI driver.

Important APIs/types/functions: the object is a `storage.k8s.io/v1` `StorageClass` named `nfs-csi`, with provisioner `nfs.csi.k8s.io`, parameters `server: nfs-server.default.svc.cluster.local` and `share: /`, `reclaimPolicy: Delete`, `volumeBindingMode: Immediate`, `allowVolumeExpansion: true`, and mount option `nfsvers=4.1`.

Control flow: PVCs that name `storageClassName: nfs-csi` trigger the external provisioner in the controller deployment. The driver receives the server/share attributes, creates or selects an NFS subdirectory, and returns a CSI volume handle used by PVs and node publish calls.

State and persistence: the StorageClass is persistent cluster configuration. Provisioned PVs, PVCs, and NFS directories survive independently according to reclaim policy and driver delete behavior.

Dependencies and integration points: depends on the controller deployment, RBAC, `CSIDriver`, node DaemonSet, and a resolvable NFS service matching the `server` value. The optional commented secret parameters integrate with controller secret RBAC for delete-time mount options.

Risks: this sample hard-codes the demo NFS service DNS name and share root. `Immediate` binding can provision before a consumer pod's node constraints are known. `Delete` reclaim can remove backend subdirectories when PVCs are deleted, so it is risky for manual testing against valuable data.

Test signals: create `pvc-nfs-csi-dynamic.yaml`, wait for a bound PV, mount it with `nginx-pod-nfs.yaml`, test expansion, and confirm NFSv4.1 mount options on the node.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.11.0/storageclass.yaml -->
