# Research: subset-b-000361

Grouped source research for selected NFS CSI driver deployment manifests. Each section preserves the source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/crd-csi-snapshot.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/crd-csi-snapshot.yaml

Purpose: Installs the external-snapshotter CustomResourceDefinitions required for CSI snapshot support. The file defines three API resources in `snapshot.storage.k8s.io`: namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. In this repository the same CRD payload is reused by v4.3.0, v4.13.1, and v4.13.2, so the API surface stays stable across those deployment bundles.

Important APIs and types: `volumesnapshots.snapshot.storage.k8s.io` exposes the user-facing snapshot request API with `.spec.source.persistentVolumeClaimName` for dynamic snapshot creation, `.spec.source.volumeSnapshotContentName` for binding an existing content object, optional `.spec.volumeSnapshotClassName`, and status fields such as `boundVolumeSnapshotContentName`, `readyToUse`, `restoreSize`, `creationTime`, and `error`. `volumesnapshotclasses.snapshot.storage.k8s.io` defines cluster-wide snapshot policy with `driver`, `deletionPolicy` (`Delete` or `Retain`), and free-form `parameters`; it uses `x-kubernetes-validations` to make `deletionPolicy`, `driver`, and `parameters` immutable. `volumesnapshotcontents.snapshot.storage.k8s.io` models the backing storage snapshot with required `driver`, `deletionPolicy`, `source`, and `volumeSnapshotRef`, plus status `snapshotHandle`, `readyToUse`, `restoreSize`, `creationTime`, and `error`. Each CRD serves and stores `v1`; `v1beta1` schemas remain present but are deprecated and not served or stored.

Control flow: Kubernetes API server admission and schema validation are the main control path. A user creates a `VolumeSnapshot` pointing at either a PVC or an existing `VolumeSnapshotContent`. The snapshot controller watches these CRDs, resolves the default or named `VolumeSnapshotClass`, creates or binds a `VolumeSnapshotContent`, and records status. The CSI snapshotter sidecar in the NFS controller talks to the driver over `/csi/csi.sock` for `CreateSnapshot`, `DeleteSnapshot`, and list/status behavior, while the snapshot controller owns the higher-level binding lifecycle. The CRDs also define additional printer columns for operational `kubectl get` views.

State and persistence behavior: These CRDs persist snapshot intent and binding state in etcd through Kubernetes custom resources. The source fields and content binding references are immutable by schema or controller contract. `VolumeSnapshot` stores user intent and readiness; `VolumeSnapshotContent` stores the durable CSI `snapshotHandle` returned by the storage driver and the deletion policy that governs cleanup of the external snapshot. No pod-local state is created by this file, but deleting or changing the CRDs affects all snapshot API objects cluster-wide.

Dependencies and integration points: Requires Kubernetes `apiextensions.k8s.io/v1` support and the external-snapshotter controllers deployed by the sibling `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, `csi-nfs-controller.yaml`, and `rbac-csi-nfs.yaml` manifests. It integrates with `VolumeSnapshotClass` objects such as `snapshotclass.yaml`, the NFS CSI driver name `nfs.csi.k8s.io`, and PVC/PV restore flows in the Kubernetes storage API.

Risks: CRDs are cluster-scoped API extensions, so applying, replacing, or deleting them is high blast radius. The bundled `v1beta1` schemas are deprecated and disabled; clusters or clients still using `v1beta1` requests will fail. Consumers must verify bidirectional binding between `VolumeSnapshot` and `VolumeSnapshotContent` before restore, as the schema comments warn. A `Delete` deletion policy can delete the backing storage snapshot when content is removed. CRD upgrades must preserve stored `v1` compatibility and should be handled before deploying snapshot controllers that require these resources.

Test signals: Validate with `kubectl apply --server-side --dry-run=server`, confirm all three CRDs become `Established`, and run `kubectl api-resources --api-group=snapshot.storage.k8s.io`. Create invalid objects that set both or neither source fields and expect schema rejection. Create a `VolumeSnapshotClass`, PVC-backed `VolumeSnapshot`, and confirm the snapshot controller creates/binds a `VolumeSnapshotContent`, updates readiness/status, and honors deletion policy. Regression tests should verify `v1beta1` is not served and that printer columns render expected fields.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-controller.yaml

Purpose: Deploys the v4.13.1 NFS CSI controller with provisioning, resizing, snapshotting, liveness, and the NFS driver in one controller pod. This is the full modern controller bundle for the v4.13.1 image tag.

Important APIs and types: The Deployment runs one replica in `kube-system` with `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, ServiceAccount `csi-nfs-controller-sa`, `priorityClassName: system-cluster-critical`, Linux node selector, `RuntimeDefault` seccomp, control-plane tolerations, and `CriticalAddonsOnly` toleration. Containers are `csi-provisioner:v6.1.0`, `csi-resizer:v2.0.0`, `csi-snapshotter:v8.4.0`, `livenessprobe:v2.17.0`, and `nfsplugin:v4.13.1`. Sidecars share `/csi/csi.sock`; provisioner and snapshotter use long 1200s timeouts and 30m retry max; provisioner enables `HonorPVReclaimPolicy=true` and disables `VolumeAttributesClass`; resizer disables `VolumeAttributesClass` and sets `handle-volume-inuse-error=false`. The driver is privileged with `SYS_ADMIN`, drops other capabilities, and uses bidirectional mount propagation on host `/var/lib/kubelet/pods`.

Control flow: The provisioner watches PVCs and creates/deletes/patches PVs through the CSI driver. The resizer watches PVC expansion and updates PV/PVC status. The snapshotter watches snapshot content and calls driver snapshot APIs. The liveness sidecar and driver health probe use localhost port 29652 with `--http-endpoint=localhost:29652`. All sidecars communicate with the NFS plugin over the shared Unix socket.

State and persistence behavior: Deployment state persists in Kubernetes; the socket is ephemeral `emptyDir`. Durable volume state is split between Kubernetes PV/PVC/Snapshot objects and the external NFS share. Leader-election leases are stored in the pod namespace from `POD_NAMESPACE`. No local persistent volume is mounted by the controller.

Dependencies and integration points: Requires v4.13.x RBAC, `CSIDriver`, `StorageClass`, snapshot CRDs, snapshot class, snapshot controller/RBAC, and a reachable NFS server. Sidecars use downward API `POD_NAMESPACE` for leader election, so moving the deployment namespace requires corresponding RBAC and object updates.

Risks: The privileged driver and hostPath mount are high trust. The controller needs host networking to mount NFS and cluster DNS to resolve service names. The long CSI timeout can delay failure reporting during backend outages. Resource requests are tiny relative to operations on large clusters. `VolumeAttributesClass=false` explicitly disables that feature even if the cluster supports it. Version skew with CRDs or RBAC can break snapshotter/resizer operations.

Test signals: Check all five containers ready, leader-election leases for provisioner/resizer/snapshotter, PVC provision/delete, PVC expansion, snapshot create/delete, liveness endpoint behavior, and NFS server DNS from the pod. Validate restricted capability drop still leaves the driver able to mount with `SYS_ADMIN` and privileged mode.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-driverinfo.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-driverinfo.yaml

Purpose: Registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`. This tells core storage controllers and kubelet that the driver does not require attach/detach operations and supports persistent volumes.

Important APIs and types: The manifest uses `CSIDriver.spec.attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`. `attachRequired: false` is important for NFS because the driver exposes network filesystems and does not need a `VolumeAttachment` object. `fsGroupPolicy: File` declares that Kubernetes may apply filesystem ownership changes for mounted volumes when a pod requests an `fsGroup`.

Control flow: The object is read by Kubernetes storage control loops and kubelet during CSI volume lifecycle operations. PVCs provisioned by the `nfs.csi.k8s.io` provisioner bind to PVs using this driver name; kubelet later consults the `CSIDriver` object while deciding whether to wait for attachment and how to handle ownership policy.

State and persistence behavior: The object is cluster-scoped persistent Kubernetes configuration. It does not create pods or local files. Changes to `attachRequired`, lifecycle modes, or `fsGroupPolicy` alter future scheduling and mount behavior for NFS CSI volumes and should be treated as driver contract changes.

Dependencies and integration points: Integrates with the node plugin registered by `csi-nfs-node.yaml`, the controller plugin in `csi-nfs-controller.yaml`, and storage objects that use provisioner/driver `nfs.csi.k8s.io`, including `StorageClass` and `VolumeSnapshotClass` manifests. Requires the `storage.k8s.io/v1` API, which is present on supported Kubernetes versions for this driver family.

Risks: If this object is missing, kubelet may assume default CSI behavior and attachment semantics that are wrong for NFS. If `fsGroupPolicy` is changed, pods relying on group ownership propagation can see permission changes. `volumeLifecycleModes` excludes `Ephemeral`; inline CSI ephemeral examples need a different driver declaration if enabled elsewhere.

Test signals: After apply, `kubectl get csidriver nfs.csi.k8s.io -o yaml` should show `attachRequired: false` and `fsGroupPolicy: File`. Provision a PVC with the NFS `StorageClass`, schedule a pod with and without `fsGroup`, and verify no `VolumeAttachment` is required. Confirm kubelet node-driver registration reports the same driver name.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-node.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-node.yaml

Purpose: Deploys the v4.13.1 NFS CSI node plugin as a system-node-critical DaemonSet. It registers the driver with kubelet and performs node-side NFS publish/unpublish operations.

Important APIs and types: The DaemonSet uses `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, ServiceAccount `csi-nfs-node-sa`, `priorityClassName: system-node-critical`, `RuntimeDefault` seccomp, Linux node selector, all-taint toleration, and rolling update `maxUnavailable: 1`. Containers are `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.13.1`. The registrar has `--csi-address=/csi/csi.sock` and `--kubelet-registration-path=/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`; v4.13.1 does not set a registrar `--timeout`. The NFS plugin is privileged, adds `SYS_ADMIN`, drops other capabilities, allows privilege escalation, mounts the plugin socket hostPath and `/var/lib/kubelet/pods` with bidirectional propagation, and serves health on localhost port 29653.

Control flow: The NFS plugin creates the CSI socket in the kubelet plugin directory. The registrar registers the driver name/path with kubelet. Kubelet calls the node CSI service to mount NFS volumes into pod directories, using the StorageClass/PV attributes prepared by the controller. Liveness probes watch the CSI socket and driver health endpoint.

State and persistence behavior: Socket and registration artifacts live on hostPath directories and are recreated by the DaemonSet. Volume mount state is node-local under kubelet pod directories; data persists remotely on NFS. The DaemonSet keeps one pod per eligible node and rolls updates one unavailable node at a time.

Dependencies and integration points: Requires the `CSIDriver` object, matching controller side, host kubelet paths, NFS client support, and cluster DNS/network access to NFS exports. It integrates with kubelet through `/var/lib/kubelet/plugins_registry` and with pod volume lifecycle through mount propagation.

Risks: High privilege is inherent to mount management. Broad toleration can place the plugin on nodes where NFS is blocked or unsupported. The absence of `--timeout` on the registrar can make kubelet registration hangs harder to bound; v4.13.2 adds this. HostPath paths assume a standard kubelet root.

Test signals: Check DaemonSet readiness on each node, `CSINode` driver registration, registrar logs, liveness endpoint on port 29653, pod mount/unmount, and node reboot or plugin restart recovery. Include tests with service DNS NFS endpoints and tainted nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-snapshot-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-snapshot-controller.yaml

Purpose: Deploys the external snapshot-controller v8.4.0 as a two-replica control-plane Deployment in `kube-system`. It reconciles CSI snapshot custom resources independently of the NFS CSI controller pod.

Important APIs and types: The Deployment uses `replicas: 2`, label `app: snapshot-controller`, `minReadySeconds: 15`, rolling update `maxSurge: 0`/`maxUnavailable: 1`, ServiceAccount `snapshot-controller`, Linux node selector, `system-cluster-critical` priority, `RuntimeDefault` seccomp, and control-plane tolerations. The container image is `registry.k8s.io/sig-storage/snapshot-controller:v8.4.0`, with `--v=2`, `--leader-election=true`, and `--leader-election-namespace=$(POD_NAMESPACE)` from downward API. Resource limit is memory 300Mi with small requests.

Control flow: Replicas contend for leader election in their own namespace. The leader watches `VolumeSnapshot`, `VolumeSnapshotClass`, `VolumeSnapshotContent`, PVC, and PV resources, then writes binding/status changes. CSI driver-specific work is delegated to snapshotter sidecars in controller deployments such as `csi-nfs-controller`.

State and persistence behavior: Snapshot objects and content persist in the Kubernetes API; leader election persists as a Lease. The pod has no local persistent storage. Using `POD_NAMESPACE` makes namespace relocation safer than the v4.3.0 hard-coded arg, provided RBAC also moves.

Dependencies and integration points: Requires CRDs, `rbac-snapshot-controller.yaml`, and a CSI snapshotter sidecar for the target driver. It integrates with `snapshotclass.yaml` and the NFS CSI driver name.

Risks: Missing CRDs prevent readiness. RBAC must grant leases in the runtime namespace. Memory limit increased from v4.3.0 but can still matter for very large clusters. Controller version must stay compatible with the installed CRD schema and sidecar versions.

Test signals: Verify two replicas, one leader lease in the pod namespace, readiness after CRDs, and snapshot lifecycle status updates. Test deployment namespace changes only with matching RBAC, and inspect logs for CRD/version compatibility warnings.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/rbac-csi-nfs.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/rbac-csi-nfs.yaml

Purpose: Creates ServiceAccounts and controller-side RBAC for the v4.13.x NFS CSI deployment. Compared with earlier versions, this file supports the provisioner, snapshotter, and resizer sidecars.

Important APIs and types: Defines ServiceAccounts `csi-nfs-controller-sa` and `csi-nfs-node-sa`; ClusterRole `nfs-external-provisioner-role` with PV get/list/watch/create/patch/delete, PVC get/list/watch/update, StorageClass watch, snapshot class/snapshot read, snapshot content update/patch/status, event writes, CSINode/Node reads, lease management, and secret get; binding `nfs-csi-provisioner-binding`; ClusterRole `nfs-external-resizer-role` with PV get/list/watch/update/patch, PVC read, PVC status update/patch, event writes, and lease management; and binding `nfs-csi-resizer-role`.

Control flow: The controller pod runs all sidecars under `csi-nfs-controller-sa`. The external provisioner watches PVCs and creates/patches/deletes PVs. The resizer watches expansion requests and updates PV/PVC status. The snapshotter watches snapshot APIs and updates snapshot content/status while invoking CSI calls on the NFS driver socket. Each sidecar uses leases for leader election.

State and persistence behavior: RBAC resources persist authorization policy and allow sidecars to mutate durable Kubernetes storage objects. The file does not create volumes, snapshots, or local state directly. Because all sidecars share the ServiceAccount, permission changes affect multiple controllers at once.

Dependencies and integration points: Paired with v4.13.x `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, `storageclass.yaml`, and `snapshotclass.yaml`. The secret read permission supports optional StorageClass provisioner secrets for DeleteVolume mount options.

Risks: Cluster-wide secret `get` is broad and should be reviewed for tenant boundaries. Missing `patch` on PVs or status verbs on PVCs would break modern provisioner/resizer behavior; this file includes them. Applying it without snapshot CRDs is allowed, but snapshot sidecars still cannot reconcile until the APIs exist. Shared ServiceAccount increases least-privilege surface.

Test signals: Use `kubectl auth can-i` as `system:serviceaccount:kube-system:csi-nfs-controller-sa` for PV patch/delete, PVC status patch, snapshot content status patch, events patch, leases create/update, and secrets get. Exercise provision, snapshot, resize, and delete flows and confirm events and status fields update.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/rbac-snapshot-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/rbac-snapshot-controller.yaml

Purpose: Grants the standalone snapshot controller permissions to reconcile CSI snapshot custom resources and to run leader election in `kube-system`. This RBAC file is paired with the v8.4.0 snapshot-controller deployment in the v4.13.x bundles.

Important APIs and types: Defines ServiceAccount `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and matching RoleBinding. The cluster role reads PVs, reads/updates PVCs, writes events, reads `VolumeSnapshotClass`, fully manages `VolumeSnapshotContent`, patches content status, gets/lists/watches/updates/patches/creates `VolumeSnapshot`, and updates/patches `VolumeSnapshot` status. The namespaced role grants full lease lifecycle verbs required for leader election.

Control flow: The deployment uses this ServiceAccount. Snapshot controller informers watch snapshot resources and storage dependencies, reconcile `VolumeSnapshot` to `VolumeSnapshotContent` binding, publish status, and coordinate active leadership with `coordination.k8s.io/leases` in `kube-system`.

State and persistence behavior: The file persists authorization policy only. The controller uses granted verbs to update Kubernetes snapshot objects and leader-election leases. It does not create local state, but privilege changes can immediately stop reconciliation or permit/deny snapshot object mutations.

Dependencies and integration points: Requires the CRDs in `crd-csi-snapshot.yaml`, the `snapshot-controller` deployment, and the CSI snapshotter sidecar/RBAC in the NFS controller. The extra `create` permission on `volumesnapshots` compared with v4.3.0 matches newer external-snapshotter controller expectations.

Risks: ClusterRole permissions are broad over all namespaces, which is necessary for cluster snapshot reconciliation but should be reviewed in multi-tenant clusters. Removing status or content verbs causes snapshots to hang. Leader-election Role is namespaced to `kube-system`; changing the deployment namespace or `--leader-election-namespace` requires matching RBAC edits.

Test signals: Use `kubectl auth can-i --as=system:serviceaccount:kube-system:snapshot-controller` for snapshot classes, contents, snapshots/status, PVCs, events, and leases. With two replicas, confirm a single lease holder and successful snapshot create/delete flows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/snapshotclass.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/snapshotclass.yaml

Purpose: Provides a default example `VolumeSnapshotClass` for the NFS CSI driver. It connects snapshot requests to driver `nfs.csi.k8s.io` and chooses `deletionPolicy: Delete`, meaning the backing snapshot should be removed when the snapshot content is deleted.

Important APIs and types: The resource is `snapshot.storage.k8s.io/v1`, kind `VolumeSnapshotClass`, named `csi-nfs-snapclass`. The two behavioral fields are `driver: nfs.csi.k8s.io` and `deletionPolicy: Delete`; no driver-specific parameters or default-class annotations are set.

Control flow: A `VolumeSnapshot` can reference this class by `.spec.volumeSnapshotClassName`. The snapshot controller uses it when binding a `VolumeSnapshotContent`, and the CSI snapshotter sidecar routes snapshot calls to the NFS CSI driver based on the matching driver name. Because there is no default annotation, snapshots that omit `volumeSnapshotClassName` need another default class or explicit class selection.

State and persistence behavior: This is cluster-scoped policy stored in the Kubernetes API. It does not create snapshots by itself. Its deletion policy is copied into dynamically provisioned snapshot content, so changing or deleting the class after creation does not necessarily change already-created content behavior.

Dependencies and integration points: Depends on the snapshot CRDs from `crd-csi-snapshot.yaml`, the snapshot controller deployment/RBAC, and the NFS controller sidecar `csi-snapshotter`. It must match the `CSIDriver` and CSI plugin name `nfs.csi.k8s.io`.

Risks: `deletionPolicy: Delete` is destructive for the external snapshot lifecycle. Operators expecting retained snapshots should change this to `Retain` before production use. Since this is only an example class and lacks parameters, environment-specific snapshot behavior must come from the driver defaults. Missing CRDs cause apply failure.

Test signals: Apply after the CRDs and verify `kubectl get volumesnapshotclass csi-nfs-snapclass`. Create a PVC-backed `VolumeSnapshot` that references the class, confirm `VolumeSnapshotContent.spec.deletionPolicy` becomes `Delete`, and validate snapshot deletion removes the content and triggers driver-side cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/storageclass.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.1/storageclass.yaml

Purpose: Provides an example dynamic-provisioning `StorageClass` named `nfs-csi` for the NFS CSI driver. It points the driver at a sample NFS server DNS name and share path and enables volume expansion.

Important APIs and types: The resource is `storage.k8s.io/v1`, kind `StorageClass`, with `provisioner: nfs.csi.k8s.io`. Parameters set `server: nfs-server.default.svc.cluster.local` and `share: /`. `reclaimPolicy: Delete` deletes the PV object and asks the driver to clean up provisioned storage on PVC removal. `volumeBindingMode: Immediate` provisions as soon as the PVC is created. `allowVolumeExpansion: true` enables PVC resize handling. `mountOptions` sets `nfsvers=4.1`. Commented parameters show optional provisioner secret fields for DeleteVolume mount options.

Control flow: A PVC referencing `storageClassName: nfs-csi` triggers the external provisioner in the controller deployment. The provisioner calls the NFS CSI driver over the controller socket with the StorageClass parameters, and the driver creates a backing directory under the configured NFS share. Node-stage/publish later mounts that export with the configured mount options.

State and persistence behavior: The StorageClass is persistent cluster policy. It does not hold per-volume state, but its parameters are copied into provisioning decisions and influence PV attributes. The backing NFS server/share must exist independently. `reclaimPolicy: Delete` can remove dynamically provisioned subdirectories when claims are deleted, depending on driver implementation and mount-secret configuration.

Dependencies and integration points: Requires the controller deployment with `csi-provisioner`, the NFS driver container, the RBAC rules for PV/PVC/StorageClass/events/secrets, and a resolvable/reachable NFS server from controller and node pods. It integrates with `csi-nfs-driverinfo.yaml` through the same driver name.

Risks: The bundled server value is an example and will fail unless that service exists. `Immediate` binding can provision before a consuming pod's node placement is known. `reclaimPolicy: Delete` is potentially destructive. NFS version mismatch, firewall rules, DNS failures, or missing kernel NFS client support on nodes will surface as mount/provisioning failures. Secrets for DeleteVolume mount options are commented out, so environments needing special mount options must enable and grant them explicitly.

Test signals: Apply with a real NFS server/share, create a PVC using `nfs-csi`, and verify PV creation, events, and the provisioned directory. Mount from a pod, write/read data, resize the PVC, and delete it to confirm reclaim behavior. Negative tests should cover bad server DNS, inaccessible share, unsupported `nfsvers`, and missing optional secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.1/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/crd-csi-snapshot.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/crd-csi-snapshot.yaml

Purpose: Installs the external-snapshotter CustomResourceDefinitions required for CSI snapshot support. The file defines three API resources in `snapshot.storage.k8s.io`: namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. In this repository the same CRD payload is reused by v4.3.0, v4.13.1, and v4.13.2, so the API surface stays stable across those deployment bundles.

Important APIs and types: `volumesnapshots.snapshot.storage.k8s.io` exposes the user-facing snapshot request API with `.spec.source.persistentVolumeClaimName` for dynamic snapshot creation, `.spec.source.volumeSnapshotContentName` for binding an existing content object, optional `.spec.volumeSnapshotClassName`, and status fields such as `boundVolumeSnapshotContentName`, `readyToUse`, `restoreSize`, `creationTime`, and `error`. `volumesnapshotclasses.snapshot.storage.k8s.io` defines cluster-wide snapshot policy with `driver`, `deletionPolicy` (`Delete` or `Retain`), and free-form `parameters`; it uses `x-kubernetes-validations` to make `deletionPolicy`, `driver`, and `parameters` immutable. `volumesnapshotcontents.snapshot.storage.k8s.io` models the backing storage snapshot with required `driver`, `deletionPolicy`, `source`, and `volumeSnapshotRef`, plus status `snapshotHandle`, `readyToUse`, `restoreSize`, `creationTime`, and `error`. Each CRD serves and stores `v1`; `v1beta1` schemas remain present but are deprecated and not served or stored.

Control flow: Kubernetes API server admission and schema validation are the main control path. A user creates a `VolumeSnapshot` pointing at either a PVC or an existing `VolumeSnapshotContent`. The snapshot controller watches these CRDs, resolves the default or named `VolumeSnapshotClass`, creates or binds a `VolumeSnapshotContent`, and records status. The CSI snapshotter sidecar in the NFS controller talks to the driver over `/csi/csi.sock` for `CreateSnapshot`, `DeleteSnapshot`, and list/status behavior, while the snapshot controller owns the higher-level binding lifecycle. The CRDs also define additional printer columns for operational `kubectl get` views.

State and persistence behavior: These CRDs persist snapshot intent and binding state in etcd through Kubernetes custom resources. The source fields and content binding references are immutable by schema or controller contract. `VolumeSnapshot` stores user intent and readiness; `VolumeSnapshotContent` stores the durable CSI `snapshotHandle` returned by the storage driver and the deletion policy that governs cleanup of the external snapshot. No pod-local state is created by this file, but deleting or changing the CRDs affects all snapshot API objects cluster-wide.

Dependencies and integration points: Requires Kubernetes `apiextensions.k8s.io/v1` support and the external-snapshotter controllers deployed by the sibling `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, `csi-nfs-controller.yaml`, and `rbac-csi-nfs.yaml` manifests. It integrates with `VolumeSnapshotClass` objects such as `snapshotclass.yaml`, the NFS CSI driver name `nfs.csi.k8s.io`, and PVC/PV restore flows in the Kubernetes storage API.

Risks: CRDs are cluster-scoped API extensions, so applying, replacing, or deleting them is high blast radius. The bundled `v1beta1` schemas are deprecated and disabled; clusters or clients still using `v1beta1` requests will fail. Consumers must verify bidirectional binding between `VolumeSnapshot` and `VolumeSnapshotContent` before restore, as the schema comments warn. A `Delete` deletion policy can delete the backing storage snapshot when content is removed. CRD upgrades must preserve stored `v1` compatibility and should be handled before deploying snapshot controllers that require these resources.

Test signals: Validate with `kubectl apply --server-side --dry-run=server`, confirm all three CRDs become `Established`, and run `kubectl api-resources --api-group=snapshot.storage.k8s.io`. Create invalid objects that set both or neither source fields and expect schema rejection. Create a `VolumeSnapshotClass`, PVC-backed `VolumeSnapshot`, and confirm the snapshot controller creates/binds a `VolumeSnapshotContent`, updates readiness/status, and honors deletion policy. Regression tests should verify `v1beta1` is not served and that printer columns render expected fields.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-controller.yaml

Purpose: Deploys the v4.13.2 NFS CSI controller with provisioning, resizing, snapshotting, liveness, and the NFS driver in one controller pod. This is the full modern controller bundle for the v4.13.2 image tag; compared with v4.13.1 the controller manifest changes only the NFS plugin image tag.

Important APIs and types: The Deployment runs one replica in `kube-system` with `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, ServiceAccount `csi-nfs-controller-sa`, `priorityClassName: system-cluster-critical`, Linux node selector, `RuntimeDefault` seccomp, control-plane tolerations, and `CriticalAddonsOnly` toleration. Containers are `csi-provisioner:v6.1.0`, `csi-resizer:v2.0.0`, `csi-snapshotter:v8.4.0`, `livenessprobe:v2.17.0`, and `nfsplugin:v4.13.2`. Sidecars share `/csi/csi.sock`; provisioner and snapshotter use long 1200s timeouts and 30m retry max; provisioner enables `HonorPVReclaimPolicy=true` and disables `VolumeAttributesClass`; resizer disables `VolumeAttributesClass` and sets `handle-volume-inuse-error=false`. The driver is privileged with `SYS_ADMIN`, drops other capabilities, and uses bidirectional mount propagation on host `/var/lib/kubelet/pods`.

Control flow: The provisioner watches PVCs and creates/deletes/patches PVs through the CSI driver. The resizer watches PVC expansion and updates PV/PVC status. The snapshotter watches snapshot content and calls driver snapshot APIs. The liveness sidecar and driver health probe use localhost port 29652 with `--http-endpoint=localhost:29652`. All sidecars communicate with the NFS plugin over the shared Unix socket.

State and persistence behavior: Deployment state persists in Kubernetes; the socket is ephemeral `emptyDir`. Durable volume state is split between Kubernetes PV/PVC/Snapshot objects and the external NFS share. Leader-election leases are stored in the pod namespace from `POD_NAMESPACE`. No local persistent volume is mounted by the controller.

Dependencies and integration points: Requires v4.13.x RBAC, `CSIDriver`, `StorageClass`, snapshot CRDs, snapshot class, snapshot controller/RBAC, and a reachable NFS server. Sidecars use downward API `POD_NAMESPACE` for leader election, so moving the deployment namespace requires corresponding RBAC and object updates.

Risks: The privileged driver and hostPath mount are high trust. The controller needs host networking to mount NFS and cluster DNS to resolve service names. The long CSI timeout can delay failure reporting during backend outages. Resource requests are tiny relative to operations on large clusters. `VolumeAttributesClass=false` explicitly disables that feature even if the cluster supports it. Version skew with CRDs or RBAC can break snapshotter/resizer operations. The only v4.13.2 controller delta from v4.13.1 is the driver image tag, so rollout tests should focus on driver behavior changes behind the same sidecar contract.

Test signals: Check all five containers ready, leader-election leases for provisioner/resizer/snapshotter, PVC provision/delete, PVC expansion, snapshot create/delete, liveness endpoint behavior, and NFS server DNS from the pod. Validate restricted capability drop still leaves the driver able to mount with `SYS_ADMIN` and privileged mode.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-driverinfo.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-driverinfo.yaml

Purpose: Registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`. This tells core storage controllers and kubelet that the driver does not require attach/detach operations and supports persistent volumes.

Important APIs and types: The manifest uses `CSIDriver.spec.attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`. `attachRequired: false` is important for NFS because the driver exposes network filesystems and does not need a `VolumeAttachment` object. `fsGroupPolicy: File` declares that Kubernetes may apply filesystem ownership changes for mounted volumes when a pod requests an `fsGroup`.

Control flow: The object is read by Kubernetes storage control loops and kubelet during CSI volume lifecycle operations. PVCs provisioned by the `nfs.csi.k8s.io` provisioner bind to PVs using this driver name; kubelet later consults the `CSIDriver` object while deciding whether to wait for attachment and how to handle ownership policy.

State and persistence behavior: The object is cluster-scoped persistent Kubernetes configuration. It does not create pods or local files. Changes to `attachRequired`, lifecycle modes, or `fsGroupPolicy` alter future scheduling and mount behavior for NFS CSI volumes and should be treated as driver contract changes.

Dependencies and integration points: Integrates with the node plugin registered by `csi-nfs-node.yaml`, the controller plugin in `csi-nfs-controller.yaml`, and storage objects that use provisioner/driver `nfs.csi.k8s.io`, including `StorageClass` and `VolumeSnapshotClass` manifests. Requires the `storage.k8s.io/v1` API, which is present on supported Kubernetes versions for this driver family.

Risks: If this object is missing, kubelet may assume default CSI behavior and attachment semantics that are wrong for NFS. If `fsGroupPolicy` is changed, pods relying on group ownership propagation can see permission changes. `volumeLifecycleModes` excludes `Ephemeral`; inline CSI ephemeral examples need a different driver declaration if enabled elsewhere.

Test signals: After apply, `kubectl get csidriver nfs.csi.k8s.io -o yaml` should show `attachRequired: false` and `fsGroupPolicy: File`. Provision a PVC with the NFS `StorageClass`, schedule a pod with and without `fsGroup`, and verify no `VolumeAttachment` is required. Confirm kubelet node-driver registration reports the same driver name.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-node.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-node.yaml

Purpose: Deploys the v4.13.2 NFS CSI node plugin as a system-node-critical DaemonSet. It registers the driver with kubelet and performs node-side NFS publish/unpublish operations.

Important APIs and types: The DaemonSet uses `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, ServiceAccount `csi-nfs-node-sa`, `priorityClassName: system-node-critical`, `RuntimeDefault` seccomp, Linux node selector, all-taint toleration, and rolling update `maxUnavailable: 1`. Containers are `livenessprobe:v2.17.0`, `csi-node-driver-registrar:v2.15.0`, and `nfsplugin:v4.13.2`. The registrar has `--csi-address=/csi/csi.sock` and `--kubelet-registration-path=/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock`; v4.13.2 adds registrar `--timeout=60s` compared with v4.13.1. The NFS plugin is privileged, adds `SYS_ADMIN`, drops other capabilities, allows privilege escalation, mounts the plugin socket hostPath and `/var/lib/kubelet/pods` with bidirectional propagation, and serves health on localhost port 29653.

Control flow: The NFS plugin creates the CSI socket in the kubelet plugin directory. The registrar registers the driver name/path with kubelet. Kubelet calls the node CSI service to mount NFS volumes into pod directories, using the StorageClass/PV attributes prepared by the controller. Liveness probes watch the CSI socket and driver health endpoint.

State and persistence behavior: Socket and registration artifacts live on hostPath directories and are recreated by the DaemonSet. Volume mount state is node-local under kubelet pod directories; data persists remotely on NFS. The DaemonSet keeps one pod per eligible node and rolls updates one unavailable node at a time.

Dependencies and integration points: Requires the `CSIDriver` object, matching controller side, host kubelet paths, NFS client support, and cluster DNS/network access to NFS exports. It integrates with kubelet through `/var/lib/kubelet/plugins_registry` and with pod volume lifecycle through mount propagation.

Risks: High privilege is inherent to mount management. Broad toleration can place the plugin on nodes where NFS is blocked or unsupported. The registrar timeout bounds registration calls, but too-short timeouts could expose slow kubelet or filesystem behavior during startup. HostPath paths assume a standard kubelet root.

Test signals: Check DaemonSet readiness on each node, `CSINode` driver registration, registrar logs, liveness endpoint on port 29653, pod mount/unmount, and node reboot or plugin restart recovery. Include tests with service DNS NFS endpoints and tainted nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-snapshot-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-snapshot-controller.yaml

Purpose: Deploys the external snapshot-controller v8.4.0 as a two-replica control-plane Deployment in `kube-system`. It reconciles CSI snapshot custom resources independently of the NFS CSI controller pod.

Important APIs and types: The Deployment uses `replicas: 2`, label `app: snapshot-controller`, `minReadySeconds: 15`, rolling update `maxSurge: 0`/`maxUnavailable: 1`, ServiceAccount `snapshot-controller`, Linux node selector, `system-cluster-critical` priority, `RuntimeDefault` seccomp, and control-plane tolerations. The container image is `registry.k8s.io/sig-storage/snapshot-controller:v8.4.0`, with `--v=2`, `--leader-election=true`, and `--leader-election-namespace=$(POD_NAMESPACE)` from downward API. Resource limit is memory 300Mi with small requests.

Control flow: Replicas contend for leader election in their own namespace. The leader watches `VolumeSnapshot`, `VolumeSnapshotClass`, `VolumeSnapshotContent`, PVC, and PV resources, then writes binding/status changes. CSI driver-specific work is delegated to snapshotter sidecars in controller deployments such as `csi-nfs-controller`.

State and persistence behavior: Snapshot objects and content persist in the Kubernetes API; leader election persists as a Lease. The pod has no local persistent storage. Using `POD_NAMESPACE` makes namespace relocation safer than the v4.3.0 hard-coded arg, provided RBAC also moves.

Dependencies and integration points: Requires CRDs, `rbac-snapshot-controller.yaml`, and a CSI snapshotter sidecar for the target driver. It integrates with `snapshotclass.yaml` and the NFS CSI driver name.

Risks: Missing CRDs prevent readiness. RBAC must grant leases in the runtime namespace. Memory limit increased from v4.3.0 but can still matter for very large clusters. Controller version must stay compatible with the installed CRD schema and sidecar versions.

Test signals: Verify two replicas, one leader lease in the pod namespace, readiness after CRDs, and snapshot lifecycle status updates. Test deployment namespace changes only with matching RBAC, and inspect logs for CRD/version compatibility warnings.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/rbac-csi-nfs.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/rbac-csi-nfs.yaml

Purpose: Creates ServiceAccounts and controller-side RBAC for the v4.13.x NFS CSI deployment. Compared with earlier versions, this file supports the provisioner, snapshotter, and resizer sidecars.

Important APIs and types: Defines ServiceAccounts `csi-nfs-controller-sa` and `csi-nfs-node-sa`; ClusterRole `nfs-external-provisioner-role` with PV get/list/watch/create/patch/delete, PVC get/list/watch/update, StorageClass watch, snapshot class/snapshot read, snapshot content update/patch/status, event writes, CSINode/Node reads, lease management, and secret get; binding `nfs-csi-provisioner-binding`; ClusterRole `nfs-external-resizer-role` with PV get/list/watch/update/patch, PVC read, PVC status update/patch, event writes, and lease management; and binding `nfs-csi-resizer-role`.

Control flow: The controller pod runs all sidecars under `csi-nfs-controller-sa`. The external provisioner watches PVCs and creates/patches/deletes PVs. The resizer watches expansion requests and updates PV/PVC status. The snapshotter watches snapshot APIs and updates snapshot content/status while invoking CSI calls on the NFS driver socket. Each sidecar uses leases for leader election.

State and persistence behavior: RBAC resources persist authorization policy and allow sidecars to mutate durable Kubernetes storage objects. The file does not create volumes, snapshots, or local state directly. Because all sidecars share the ServiceAccount, permission changes affect multiple controllers at once.

Dependencies and integration points: Paired with v4.13.x `csi-nfs-controller.yaml`, `csi-nfs-node.yaml`, `crd-csi-snapshot.yaml`, `rbac-snapshot-controller.yaml`, `storageclass.yaml`, and `snapshotclass.yaml`. The secret read permission supports optional StorageClass provisioner secrets for DeleteVolume mount options.

Risks: Cluster-wide secret `get` is broad and should be reviewed for tenant boundaries. Missing `patch` on PVs or status verbs on PVCs would break modern provisioner/resizer behavior; this file includes them. Applying it without snapshot CRDs is allowed, but snapshot sidecars still cannot reconcile until the APIs exist. Shared ServiceAccount increases least-privilege surface.

Test signals: Use `kubectl auth can-i` as `system:serviceaccount:kube-system:csi-nfs-controller-sa` for PV patch/delete, PVC status patch, snapshot content status patch, events patch, leases create/update, and secrets get. Exercise provision, snapshot, resize, and delete flows and confirm events and status fields update.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/rbac-snapshot-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/rbac-snapshot-controller.yaml

Purpose: Grants the standalone snapshot controller permissions to reconcile CSI snapshot custom resources and to run leader election in `kube-system`. This RBAC file is paired with the v8.4.0 snapshot-controller deployment in the v4.13.x bundles.

Important APIs and types: Defines ServiceAccount `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and matching RoleBinding. The cluster role reads PVs, reads/updates PVCs, writes events, reads `VolumeSnapshotClass`, fully manages `VolumeSnapshotContent`, patches content status, gets/lists/watches/updates/patches/creates `VolumeSnapshot`, and updates/patches `VolumeSnapshot` status. The namespaced role grants full lease lifecycle verbs required for leader election.

Control flow: The deployment uses this ServiceAccount. Snapshot controller informers watch snapshot resources and storage dependencies, reconcile `VolumeSnapshot` to `VolumeSnapshotContent` binding, publish status, and coordinate active leadership with `coordination.k8s.io/leases` in `kube-system`.

State and persistence behavior: The file persists authorization policy only. The controller uses granted verbs to update Kubernetes snapshot objects and leader-election leases. It does not create local state, but privilege changes can immediately stop reconciliation or permit/deny snapshot object mutations.

Dependencies and integration points: Requires the CRDs in `crd-csi-snapshot.yaml`, the `snapshot-controller` deployment, and the CSI snapshotter sidecar/RBAC in the NFS controller. The extra `create` permission on `volumesnapshots` compared with v4.3.0 matches newer external-snapshotter controller expectations.

Risks: ClusterRole permissions are broad over all namespaces, which is necessary for cluster snapshot reconciliation but should be reviewed in multi-tenant clusters. Removing status or content verbs causes snapshots to hang. Leader-election Role is namespaced to `kube-system`; changing the deployment namespace or `--leader-election-namespace` requires matching RBAC edits.

Test signals: Use `kubectl auth can-i --as=system:serviceaccount:kube-system:snapshot-controller` for snapshot classes, contents, snapshots/status, PVCs, events, and leases. With two replicas, confirm a single lease holder and successful snapshot create/delete flows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/rbac-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/snapshotclass.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/snapshotclass.yaml

Purpose: Provides a default example `VolumeSnapshotClass` for the NFS CSI driver. It connects snapshot requests to driver `nfs.csi.k8s.io` and chooses `deletionPolicy: Delete`, meaning the backing snapshot should be removed when the snapshot content is deleted.

Important APIs and types: The resource is `snapshot.storage.k8s.io/v1`, kind `VolumeSnapshotClass`, named `csi-nfs-snapclass`. The two behavioral fields are `driver: nfs.csi.k8s.io` and `deletionPolicy: Delete`; no driver-specific parameters or default-class annotations are set.

Control flow: A `VolumeSnapshot` can reference this class by `.spec.volumeSnapshotClassName`. The snapshot controller uses it when binding a `VolumeSnapshotContent`, and the CSI snapshotter sidecar routes snapshot calls to the NFS CSI driver based on the matching driver name. Because there is no default annotation, snapshots that omit `volumeSnapshotClassName` need another default class or explicit class selection.

State and persistence behavior: This is cluster-scoped policy stored in the Kubernetes API. It does not create snapshots by itself. Its deletion policy is copied into dynamically provisioned snapshot content, so changing or deleting the class after creation does not necessarily change already-created content behavior.

Dependencies and integration points: Depends on the snapshot CRDs from `crd-csi-snapshot.yaml`, the snapshot controller deployment/RBAC, and the NFS controller sidecar `csi-snapshotter`. It must match the `CSIDriver` and CSI plugin name `nfs.csi.k8s.io`.

Risks: `deletionPolicy: Delete` is destructive for the external snapshot lifecycle. Operators expecting retained snapshots should change this to `Retain` before production use. Since this is only an example class and lacks parameters, environment-specific snapshot behavior must come from the driver defaults. Missing CRDs cause apply failure.

Test signals: Apply after the CRDs and verify `kubectl get volumesnapshotclass csi-nfs-snapclass`. Create a PVC-backed `VolumeSnapshot` that references the class, confirm `VolumeSnapshotContent.spec.deletionPolicy` becomes `Delete`, and validate snapshot deletion removes the content and triggers driver-side cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/storageclass.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/storageclass.yaml

Purpose: Provides an example dynamic-provisioning `StorageClass` named `nfs-csi` for the NFS CSI driver. It points the driver at a sample NFS server DNS name and share path and enables volume expansion.

Important APIs and types: The resource is `storage.k8s.io/v1`, kind `StorageClass`, with `provisioner: nfs.csi.k8s.io`. Parameters set `server: nfs-server.default.svc.cluster.local` and `share: /`. `reclaimPolicy: Delete` deletes the PV object and asks the driver to clean up provisioned storage on PVC removal. `volumeBindingMode: Immediate` provisions as soon as the PVC is created. `allowVolumeExpansion: true` enables PVC resize handling. `mountOptions` sets `nfsvers=4.1`. Commented parameters show optional provisioner secret fields for DeleteVolume mount options.

Control flow: A PVC referencing `storageClassName: nfs-csi` triggers the external provisioner in the controller deployment. The provisioner calls the NFS CSI driver over the controller socket with the StorageClass parameters, and the driver creates a backing directory under the configured NFS share. Node-stage/publish later mounts that export with the configured mount options.

State and persistence behavior: The StorageClass is persistent cluster policy. It does not hold per-volume state, but its parameters are copied into provisioning decisions and influence PV attributes. The backing NFS server/share must exist independently. `reclaimPolicy: Delete` can remove dynamically provisioned subdirectories when claims are deleted, depending on driver implementation and mount-secret configuration.

Dependencies and integration points: Requires the controller deployment with `csi-provisioner`, the NFS driver container, the RBAC rules for PV/PVC/StorageClass/events/secrets, and a resolvable/reachable NFS server from controller and node pods. It integrates with `csi-nfs-driverinfo.yaml` through the same driver name.

Risks: The bundled server value is an example and will fail unless that service exists. `Immediate` binding can provision before a consuming pod's node placement is known. `reclaimPolicy: Delete` is potentially destructive. NFS version mismatch, firewall rules, DNS failures, or missing kernel NFS client support on nodes will surface as mount/provisioning failures. Secrets for DeleteVolume mount options are commented out, so environments needing special mount options must enable and grant them explicitly.

Test signals: Apply with a real NFS server/share, create a PVC using `nfs-csi`, and verify PV creation, events, and the provisioned directory. Mount from a pod, write/read data, resize the PVC, and delete it to confirm reclaim behavior. Negative tests should cover bad server DNS, inaccessible share, unsupported `nfsvers`, and missing optional secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.13.2/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-controller.yaml

Purpose: Deploys the v4.2.0 NFS CSI controller as a single `apps/v1` Deployment in `kube-system`. It runs the external provisioner, liveness probe, and NFS CSI driver container needed for dynamic NFS volume provisioning.

Important APIs and types: The pod uses `hostNetwork: true`, `dnsPolicy: Default`, ServiceAccount `csi-nfs-controller-sa`, Linux node selection, system-cluster-critical priority, and control-plane tolerations. Containers are `csi-provisioner:v3.3.0`, `livenessprobe:v2.8.0`, and `nfsplugin:v4.2.0`. The sidecars and driver share an `emptyDir` socket at `/csi/csi.sock`. The NFS container is privileged with `SYS_ADMIN`, mounts host `/var/lib/kubelet/pods` with bidirectional propagation, exposes health port 29652, and serves `/healthz`.

Control flow: The provisioner watches PVCs and StorageClasses using RBAC, then calls the NFS driver over the shared Unix socket to create/delete volumes. The controller driver container can mount the configured NFS export and create backing directories because it runs with host networking and privileged mount capabilities. The liveness sidecar probes the CSI socket and the NFS container's HTTP health endpoint.

State and persistence behavior: Kubernetes stores Deployment/ReplicaSet/Pod state. Runtime CSI socket state is ephemeral in `emptyDir`. Actual volume state lives on the external NFS server; the controller temporarily mounts host kubelet pod paths to perform mount-related operations. No persistent local volume is declared.

Dependencies and integration points: Depends on `rbac-csi-nfs.yaml`, `csi-nfs-driverinfo.yaml`, a StorageClass using `nfs.csi.k8s.io`, and network/NFS access from controller nodes. It integrates with kube-system leader-election leases and events through the provisioner.

Risks: `dnsPolicy: Default` with host networking may not resolve cluster service names such as the example `nfs-server.default.svc.cluster.local`, which later versions change to `ClusterFirstWithHostNet`. The privileged NFS container and bidirectional mount propagation are high privilege. This version lacks snapshotter and resizer sidecars, so snapshots and expansion are not supported by this deployment. Health probe args use older `--health-port` syntax.

Test signals: Apply RBAC and Deployment, verify one ready controller pod, check `/healthz` via liveness events, create a PVC using an NFS StorageClass, confirm PV creation and backing directory creation, and test DNS resolution of the configured NFS server from the host-networked pod.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-driverinfo.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-driverinfo.yaml

Purpose: Registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`. This tells core storage controllers and kubelet that the driver does not require attach/detach operations and supports persistent volumes.

Important APIs and types: The manifest uses `CSIDriver.spec.attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`. `attachRequired: false` is important for NFS because the driver exposes network filesystems and does not need a `VolumeAttachment` object. `fsGroupPolicy: File` declares that Kubernetes may apply filesystem ownership changes for mounted volumes when a pod requests an `fsGroup`.

Control flow: The object is read by Kubernetes storage control loops and kubelet during CSI volume lifecycle operations. PVCs provisioned by the `nfs.csi.k8s.io` provisioner bind to PVs using this driver name; kubelet later consults the `CSIDriver` object while deciding whether to wait for attachment and how to handle ownership policy.

State and persistence behavior: The object is cluster-scoped persistent Kubernetes configuration. It does not create pods or local files. Changes to `attachRequired`, lifecycle modes, or `fsGroupPolicy` alter future scheduling and mount behavior for NFS CSI volumes and should be treated as driver contract changes.

Dependencies and integration points: Integrates with the node plugin registered by `csi-nfs-node.yaml`, the controller plugin in `csi-nfs-controller.yaml`, and storage objects that use provisioner/driver `nfs.csi.k8s.io`, including `StorageClass` and `VolumeSnapshotClass` manifests. Requires the `storage.k8s.io/v1` API, which is present on supported Kubernetes versions for this driver family.

Risks: If this object is missing, kubelet may assume default CSI behavior and attachment semantics that are wrong for NFS. If `fsGroupPolicy` is changed, pods relying on group ownership propagation can see permission changes. `volumeLifecycleModes` excludes `Ephemeral`; inline CSI ephemeral examples need a different driver declaration if enabled elsewhere.

Test signals: After apply, `kubectl get csidriver nfs.csi.k8s.io -o yaml` should show `attachRequired: false` and `fsGroupPolicy: File`. Provision a PVC with the NFS `StorageClass`, schedule a pod with and without `fsGroup`, and verify no `VolumeAttachment` is required. Confirm kubelet node-driver registration reports the same driver name.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-node.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-node.yaml

Purpose: Deploys the v4.2.0 NFS CSI node plugin as a DaemonSet on every Linux node. It registers `nfs.csi.k8s.io` with kubelet and performs node-side mount/publish operations for NFS-backed volumes.

Important APIs and types: The DaemonSet uses `hostNetwork: true`, `dnsPolicy: Default`, ServiceAccount `csi-nfs-node-sa`, Linux node selector, tolerates all taints, and uses rolling updates with `maxUnavailable: 1`. Containers are `livenessprobe:v2.8.0`, `csi-node-driver-registrar:v2.6.2`, and `nfsplugin:v4.2.0`. The registrar points kubelet at `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` and includes an exec liveness probe in kubelet-registration-probe mode. The NFS plugin is privileged with `SYS_ADMIN`, mounts `/var/lib/kubelet/plugins/csi-nfsplugin`, `/var/lib/kubelet/pods`, and `/var/lib/kubelet/plugins_registry`, and exposes health port 29653.

Control flow: On each node, the NFS plugin opens the CSI socket under the kubelet plugin directory. The node-driver-registrar connects to that socket and writes registration data into the kubelet plugin registry. Kubelet then calls NodePublish/NodeUnpublish against the socket for pods using NFS CSI volumes. The liveness sidecar checks socket/health state.

State and persistence behavior: DaemonSet state persists in Kubernetes. The CSI socket and plugin registration files persist on the node hostPath while the pod is running and are recreated after restart. Actual data persists on the remote NFS server; node-local mounts are under kubelet pod directories.

Dependencies and integration points: Requires kubelet plugin directories, Linux nodes with NFS client support, the matching `CSIDriver`, and controller-created PVs. Integrates with kubelet through the registrar and with pod volume lifecycle through hostPath mount propagation.

Risks: `dnsPolicy: Default` can break cluster-service NFS server names in node pods. Privileged mode and bidirectional mount propagation are required but high privilege. The registrar exec liveness probe uses old registrar behavior removed in later manifests. Nodes missing `/var/lib/kubelet/pods` or NFS utilities will fail mounts.

Test signals: Verify a DaemonSet pod on each target node, `CSINode` lists `nfs.csi.k8s.io`, kubelet plugin registration file exists, liveness probes pass, and a pod can mount/read/write an NFS CSI volume. Negative tests should cover bad DNS under host networking and absent NFS kernel/client support.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.2.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.2.0/rbac-csi-nfs.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.2.0/rbac-csi-nfs.yaml

Purpose: Creates the ServiceAccounts and controller-side ClusterRole/Binding needed by the v4.2.0 NFS CSI controller. This early v4 manifest grants external-provisioner permissions but does not include snapshotter or resizer permissions.

Important APIs and types: Defines ServiceAccounts `csi-nfs-controller-sa` and `csi-nfs-node-sa` in `kube-system`, ClusterRole `nfs-external-provisioner-role`, and ClusterRoleBinding `nfs-csi-provisioner-binding`. The role can get/list/watch/create/delete PVs, get/list/watch/update PVCs, read StorageClasses, write events, read CSINodes and Nodes, manage coordination leases, and get Secrets.

Control flow: The `csi-provisioner` sidecar in `csi-nfs-controller.yaml` uses these permissions to watch PVCs and StorageClasses, create/delete PVs, update PVCs, emit events, and use leases for leader election. The NFS driver container itself talks over the CSI socket and does not directly use most Kubernetes API permissions.

State and persistence behavior: RBAC objects persist authorization policy. They authorize PV/PVC mutations and lease updates but do not store volume state themselves. The node ServiceAccount is created for the DaemonSet even though this file grants no node-specific ClusterRole.

Dependencies and integration points: Paired with the v4.2.0 controller and node manifests. It supports `storageclass.yaml`-style dynamic provisioning in nearby versions, but v4.2.0's listed subset does not include snapshot CRDs or snapshot controller manifests.

Risks: The PV rule lacks `patch`, while later manifests add it; sidecar versions or workflows that patch PVs may fail. No resizer RBAC exists, matching the absence of a resizer sidecar. No snapshot permissions exist, matching the absence of snapshotter resources. Granting `secrets get` cluster-wide is useful for provisioner secrets but should be constrained in hardened deployments where possible.

Test signals: Check `kubectl auth can-i` for the controller ServiceAccount against PV create/delete, PVC update, StorageClass watch, events create/patch, leases create/update, and secrets get. Provision and delete a PVC, inspect events, and verify leader-election leases are created in the configured namespace.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.2.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/crd-csi-snapshot.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/crd-csi-snapshot.yaml

Purpose: Installs the external-snapshotter CustomResourceDefinitions required for CSI snapshot support. The file defines three API resources in `snapshot.storage.k8s.io`: namespaced `VolumeSnapshot`, cluster-scoped `VolumeSnapshotClass`, and cluster-scoped `VolumeSnapshotContent`. In this repository the same CRD payload is reused by v4.3.0, v4.13.1, and v4.13.2, so the API surface stays stable across those deployment bundles.

Important APIs and types: `volumesnapshots.snapshot.storage.k8s.io` exposes the user-facing snapshot request API with `.spec.source.persistentVolumeClaimName` for dynamic snapshot creation, `.spec.source.volumeSnapshotContentName` for binding an existing content object, optional `.spec.volumeSnapshotClassName`, and status fields such as `boundVolumeSnapshotContentName`, `readyToUse`, `restoreSize`, `creationTime`, and `error`. `volumesnapshotclasses.snapshot.storage.k8s.io` defines cluster-wide snapshot policy with `driver`, `deletionPolicy` (`Delete` or `Retain`), and free-form `parameters`; it uses `x-kubernetes-validations` to make `deletionPolicy`, `driver`, and `parameters` immutable. `volumesnapshotcontents.snapshot.storage.k8s.io` models the backing storage snapshot with required `driver`, `deletionPolicy`, `source`, and `volumeSnapshotRef`, plus status `snapshotHandle`, `readyToUse`, `restoreSize`, `creationTime`, and `error`. Each CRD serves and stores `v1`; `v1beta1` schemas remain present but are deprecated and not served or stored.

Control flow: Kubernetes API server admission and schema validation are the main control path. A user creates a `VolumeSnapshot` pointing at either a PVC or an existing `VolumeSnapshotContent`. The snapshot controller watches these CRDs, resolves the default or named `VolumeSnapshotClass`, creates or binds a `VolumeSnapshotContent`, and records status. The CSI snapshotter sidecar in the NFS controller talks to the driver over `/csi/csi.sock` for `CreateSnapshot`, `DeleteSnapshot`, and list/status behavior, while the snapshot controller owns the higher-level binding lifecycle. The CRDs also define additional printer columns for operational `kubectl get` views.

State and persistence behavior: These CRDs persist snapshot intent and binding state in etcd through Kubernetes custom resources. The source fields and content binding references are immutable by schema or controller contract. `VolumeSnapshot` stores user intent and readiness; `VolumeSnapshotContent` stores the durable CSI `snapshotHandle` returned by the storage driver and the deletion policy that governs cleanup of the external snapshot. No pod-local state is created by this file, but deleting or changing the CRDs affects all snapshot API objects cluster-wide.

Dependencies and integration points: Requires Kubernetes `apiextensions.k8s.io/v1` support and the external-snapshotter controllers deployed by the sibling `csi-snapshot-controller.yaml`, `rbac-snapshot-controller.yaml`, `csi-nfs-controller.yaml`, and `rbac-csi-nfs.yaml` manifests. It integrates with `VolumeSnapshotClass` objects such as `snapshotclass.yaml`, the NFS CSI driver name `nfs.csi.k8s.io`, and PVC/PV restore flows in the Kubernetes storage API.

Risks: CRDs are cluster-scoped API extensions, so applying, replacing, or deleting them is high blast radius. The bundled `v1beta1` schemas are deprecated and disabled; clusters or clients still using `v1beta1` requests will fail. Consumers must verify bidirectional binding between `VolumeSnapshot` and `VolumeSnapshotContent` before restore, as the schema comments warn. A `Delete` deletion policy can delete the backing storage snapshot when content is removed. CRD upgrades must preserve stored `v1` compatibility and should be handled before deploying snapshot controllers that require these resources.

Test signals: Validate with `kubectl apply --server-side --dry-run=server`, confirm all three CRDs become `Established`, and run `kubectl api-resources --api-group=snapshot.storage.k8s.io`. Create invalid objects that set both or neither source fields and expect schema rejection. Create a `VolumeSnapshotClass`, PVC-backed `VolumeSnapshot`, and confirm the snapshot controller creates/binds a `VolumeSnapshotContent`, updates readiness/status, and honors deletion policy. Regression tests should verify `v1beta1` is not served and that printer columns render expected fields.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-controller.yaml

Purpose: Deploys the v4.3.0 NFS CSI controller with dynamic provisioning and CSI snapshot sidecar support. It updates sidecar versions, switches host-network DNS to cluster-aware mode, and adds pod-level seccomp defaults.

Important APIs and types: The Deployment has one replica in `kube-system`, ServiceAccount `csi-nfs-controller-sa`, `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, `priorityClassName: system-cluster-critical`, and `seccompProfile: RuntimeDefault`. Containers are `csi-provisioner:v3.5.0`, `csi-snapshotter:v6.2.2`, `livenessprobe:v2.10.0`, and `nfsplugin:v4.3.0`. The CSI socket is an `emptyDir`; the driver mounts `/var/lib/kubelet/pods` bidirectionally and exposes health port 29652.

Control flow: Provisioner and snapshotter sidecars connect to `/csi/csi.sock` and use leader election in `kube-system`. The provisioner handles PVC/PV lifecycle; the snapshotter coordinates CSI snapshot calls against `VolumeSnapshotContent`; the NFS driver implements the CSI server and performs NFS mount/directory operations.

State and persistence behavior: Socket state is pod-local and ephemeral. Volume and snapshot records persist in Kubernetes and on the external NFS backend. The Deployment keeps a single controller replica, so sidecar leader election mainly protects against restarts or future scaling.

Dependencies and integration points: Requires `rbac-csi-nfs.yaml` for provisioner/snapshotter permissions, snapshot CRDs plus snapshot-controller/RBAC for full snapshot lifecycle, `csi-nfs-driverinfo.yaml`, and reachable NFS exports. Host-network DNS now supports cluster service resolution.

Risks: The privileged driver and hostPath mount remain sensitive. This version has no resizer sidecar, so `allowVolumeExpansion` requires a later controller. Snapshotter has no resource requests/limits in this manifest, unlike later v4.13.x. Liveness sidecar still uses `--health-port`, and health probes reference a named port. Applying this without CRDs/RBAC will leave snapshot sidecar unable to reconcile.

Test signals: Validate pod readiness, provision a PVC, create/delete a `VolumeSnapshot`, and inspect snapshotter logs for CSI calls. Confirm cluster DNS resolution from the host-network pod, seccomp profile admission, and liveness probe behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-driverinfo.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-driverinfo.yaml

Purpose: Registers the NFS CSI driver with Kubernetes through a `storage.k8s.io/v1` `CSIDriver` object named `nfs.csi.k8s.io`. This tells core storage controllers and kubelet that the driver does not require attach/detach operations and supports persistent volumes.

Important APIs and types: The manifest uses `CSIDriver.spec.attachRequired: false`, `volumeLifecycleModes: [Persistent]`, and `fsGroupPolicy: File`. `attachRequired: false` is important for NFS because the driver exposes network filesystems and does not need a `VolumeAttachment` object. `fsGroupPolicy: File` declares that Kubernetes may apply filesystem ownership changes for mounted volumes when a pod requests an `fsGroup`.

Control flow: The object is read by Kubernetes storage control loops and kubelet during CSI volume lifecycle operations. PVCs provisioned by the `nfs.csi.k8s.io` provisioner bind to PVs using this driver name; kubelet later consults the `CSIDriver` object while deciding whether to wait for attachment and how to handle ownership policy.

State and persistence behavior: The object is cluster-scoped persistent Kubernetes configuration. It does not create pods or local files. Changes to `attachRequired`, lifecycle modes, or `fsGroupPolicy` alter future scheduling and mount behavior for NFS CSI volumes and should be treated as driver contract changes.

Dependencies and integration points: Integrates with the node plugin registered by `csi-nfs-node.yaml`, the controller plugin in `csi-nfs-controller.yaml`, and storage objects that use provisioner/driver `nfs.csi.k8s.io`, including `StorageClass` and `VolumeSnapshotClass` manifests. Requires the `storage.k8s.io/v1` API, which is present on supported Kubernetes versions for this driver family.

Risks: If this object is missing, kubelet may assume default CSI behavior and attachment semantics that are wrong for NFS. If `fsGroupPolicy` is changed, pods relying on group ownership propagation can see permission changes. `volumeLifecycleModes` excludes `Ephemeral`; inline CSI ephemeral examples need a different driver declaration if enabled elsewhere.

Test signals: After apply, `kubectl get csidriver nfs.csi.k8s.io -o yaml` should show `attachRequired: false` and `fsGroupPolicy: File`. Provision a PVC with the NFS `StorageClass`, schedule a pod with and without `fsGroup`, and verify no `VolumeAttachment` is required. Confirm kubelet node-driver registration reports the same driver name.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-node.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-node.yaml

Purpose: Deploys the v4.3.0 NFS CSI node plugin as a Linux DaemonSet. It updates node sidecar versions, switches host-network DNS to `ClusterFirstWithHostNet`, and sets pod-level seccomp defaults.

Important APIs and types: The DaemonSet uses rolling updates, `hostNetwork: true`, `dnsPolicy: ClusterFirstWithHostNet`, ServiceAccount `csi-nfs-node-sa`, `priorityClassName: system-node-critical`, `RuntimeDefault` seccomp, Linux node selector, and all-taint toleration. Containers are `livenessprobe:v2.10.0`, `csi-node-driver-registrar:v2.8.0`, and `nfsplugin:v4.3.0`. The registrar still uses kubelet registration path `/var/lib/kubelet/plugins/csi-nfsplugin/csi.sock` and an exec liveness probe. The driver is privileged with `SYS_ADMIN`, uses hostPath socket and pods directories, and exposes health port 29653.

Control flow: The node plugin serves CSI over the host plugin socket. The registrar advertises the driver to kubelet via `/registration`. Kubelet invokes node operations for pods, and the liveness sidecar/driver health probe monitor the local endpoint.

State and persistence behavior: Runtime socket and registration state live on hostPath directories under `/var/lib/kubelet`; mounts and pod volume bind points live under `/var/lib/kubelet/pods`. Remote data persists on the NFS server. Kubernetes stores desired DaemonSet rollout state.

Dependencies and integration points: Requires `csi-nfs-driverinfo.yaml`, controller provisioned PVs, kubelet plugin registry support, Linux/NFS mount support, and RBAC ServiceAccount creation. Cluster-aware DNS is important for NFS server names that are Kubernetes services.

Risks: Privileged mount access and broad node toleration run this pod on all Linux nodes, including tainted nodes. Registrar exec liveness can fail if registrar flags change. Any mismatch between `DRIVER_REG_SOCK_PATH` and the `socket-dir` hostPath prevents kubelet registration. HostPath assumptions are kubelet-layout specific.

Test signals: Confirm DaemonSet rollout, node plugin registration in `CSINode`, successful pod mount/unmount, liveness probe stability, and DNS resolution of service-backed NFS servers from host-networked node pods.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-snapshot-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-snapshot-controller.yaml

Purpose: Deploys the external snapshot-controller v6.2.2 as a two-replica control-plane Deployment in `kube-system`. It reconciles the Kubernetes `VolumeSnapshot` and `VolumeSnapshotContent` API objects defined by the snapshot CRDs.

Important APIs and types: The Deployment has `replicas: 2`, selector/label `app: snapshot-controller`, `minReadySeconds: 15`, rolling strategy `maxSurge: 0` and `maxUnavailable: 1`, ServiceAccount `snapshot-controller`, Linux node selector, `system-cluster-critical` priority, `RuntimeDefault` seccomp, and control-plane tolerations. The container runs `registry.k8s.io/sig-storage/snapshot-controller:v6.2.2` with `--v=2`, `--leader-election=true`, and `--leader-election-namespace=kube-system`, with memory limit 100Mi and tiny CPU/memory requests.

Control flow: Both replicas start, but leader election makes one active reconciler. The controller watches snapshot CRDs, PVCs, PVs, and classes; it creates/binds content objects, updates status, and coordinates with CSI snapshotter sidecars. `minReadySeconds` is set to exceed the startup failure window when v1 CRDs are absent.

State and persistence behavior: Snapshot API state persists in etcd; leader-election state persists as Leases in `kube-system`. The Deployment has no local persistent storage. Rolling update settings keep at most one unavailable replica and avoid surge.

Dependencies and integration points: Requires snapshot CRDs and `rbac-snapshot-controller.yaml`. It works with the NFS controller's `csi-snapshotter` sidecar and `snapshotclass.yaml` to complete CSI snapshot lifecycle. It is intentionally separate from the CSI driver controller deployment.

Risks: If CRDs are missing, the controller will not become ready or will exit. Memory limit 100Mi may be tight in large clusters. Leader-election namespace is hard-coded to `kube-system`; moving the deployment needs RBAC/arg changes. Tolerations use `Equal value true` for control-plane taints, which may not match all taint forms.

Test signals: Confirm two replicas with one lease holder, readiness after CRDs are installed, successful VolumeSnapshot create/delete reconciliation, and status updates. Test CRD absence during startup and rolling updates with no control-plane outage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-snapshot-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/rbac-csi-nfs.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/rbac-csi-nfs.yaml

Purpose: Creates ServiceAccounts and controller-side permissions for the v4.3.0 NFS CSI deployment, including the newly added CSI snapshotter sidecar permissions.

Important APIs and types: Defines ServiceAccounts `csi-nfs-controller-sa` and `csi-nfs-node-sa`, ClusterRole `nfs-external-provisioner-role`, and binding `nfs-csi-provisioner-binding`. The role can manage PV provisioning, update PVCs, read StorageClasses, read snapshot classes/snapshots, get/list/watch/update/patch `VolumeSnapshotContent`, update/patch content status, write events, read CSINodes/Nodes, manage leases, and get Secrets.

Control flow: The external provisioner uses PV/PVC/StorageClass/event/lease permissions for dynamic provisioning. The `csi-snapshotter` sidecar in the controller uses snapshot permissions to watch snapshot objects/content and update content status around CSI snapshot calls. Both sidecars share the controller ServiceAccount and the `/csi/csi.sock` endpoint exposed by the NFS container.

State and persistence behavior: RBAC persists cluster authorization. It allows sidecars to create/update PV-related and snapshot-content state in the API and leader-election lease state. It does not store driver state itself.

Dependencies and integration points: Requires the v4.3.0 controller deployment with `csi-provisioner` and `csi-snapshotter`, the snapshot CRDs, `rbac-snapshot-controller.yaml`, and `csi-nfs-driverinfo.yaml`. The node ServiceAccount is consumed by the DaemonSet even though node API permissions are implicit/minimal.

Risks: The provisioner PV verbs still lack `patch`, which later v4.13.x adds. There is no resizer ClusterRole because v4.3.0 has no `csi-resizer` sidecar. Snapshot permissions are cluster-wide and must align with installed CRDs; applying before CRDs can still create RBAC, but sidecars will fail until APIs exist. Shared ServiceAccount means provisioner and snapshotter both receive all controller permissions.

Test signals: Verify controller ServiceAccount can watch snapshot resources and update `volumesnapshotcontents/status`, can create/delete PVs, and can manage leases. Create a PVC and snapshot, then inspect PV, VolumeSnapshotContent, and status event updates. Confirm no resize flow is expected for this version.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/rbac-csi-nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/rbac-snapshot-controller.yaml -->
## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/rbac-snapshot-controller.yaml

Purpose: Grants the standalone snapshot controller permissions to reconcile CSI snapshot custom resources and to run leader election in `kube-system`. This RBAC file is paired with `csi-snapshot-controller.yaml` for v4.3.0.

Important APIs and types: Defines ServiceAccount `snapshot-controller`, ClusterRole `snapshot-controller-runner`, ClusterRoleBinding `snapshot-controller-role`, Role `snapshot-controller-leaderelection`, and RoleBinding of the same name. The cluster role can read PVs, read/update PVCs, write events, read `VolumeSnapshotClass`, create/get/list/watch/update/delete/patch `VolumeSnapshotContent`, patch content status, get/list/watch/update/patch `VolumeSnapshot`, and update/patch `VolumeSnapshot` status. The namespaced role grants lease get/watch/list/delete/update/create for leader election.

Control flow: The snapshot-controller pod runs under this ServiceAccount. Informers watch PVC/PV and snapshot resources, then controller reconciliation updates snapshot objects and content objects according to binding and protection state. Lease permissions support the two-replica deployment's leader election so only the active controller mutates snapshot state.

State and persistence behavior: The RBAC resources persist authorization policy in the Kubernetes API. They do not store snapshot state themselves. They permit the controller to mutate snapshot CR status/content and leader-election `Lease` objects, so changes affect future reconciliation and high availability behavior.

Dependencies and integration points: Requires snapshot CRDs and the `snapshot-controller` Deployment. It also complements `rbac-csi-nfs.yaml`, which grants the CSI snapshotter sidecar driver-facing snapshot content permissions. Both layers are needed for full snapshot lifecycle.

Risks: The v4.3.0 role lacks `create` on `volumesnapshots`, unlike later v4.13.x manifests, so controller features that need creating snapshot objects would be blocked. Cluster-wide content permissions are broad but expected for this controller. Removing lease permissions can result in active/passive confusion or no leader. Namespace mismatches between the ServiceAccount, RoleBinding, and deployment break startup.

Test signals: Run `kubectl auth can-i` as `system:serviceaccount:kube-system:snapshot-controller` for each listed verb/resource, especially leases and snapshot status. Deploy two replicas and confirm one leader. Create, update, and delete snapshots while watching controller events and content/status writes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/deploy/v4.3.0/rbac-snapshot-controller.yaml -->
