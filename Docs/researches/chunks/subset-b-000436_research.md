# sources/control-plane/rook/deploy/examples/csi-operator.yaml lines 5069-8786

## Scope

This chunk covers the tail of the `csi-operator.yaml` example manifest. It starts inside the OpenAPI v3 schema for a `csi.ceph.io` custom resource, continues through the end of that CRD definition, and then defines the runtime Kubernetes objects needed by the Ceph CSI operator and its managed CSI plugin service accounts.

The range is declarative YAML, not executable code. The important "APIs" are Kubernetes API objects, CRD schema fields, validation rules, RBAC permissions, and the operator Deployment contract consumed by Kubernetes and the Ceph CSI operator controller.

## Purpose

This portion of the manifest has two main jobs:

- Finish the CRD schema for CSI operator configuration, especially pod customization, sidecar resources, volumes, snapshot policy, encryption, liveness, logging, and scheduling behavior.
- Install the service accounts, namespace-scoped roles, cluster roles, bindings, and controller-manager Deployment that allow the Ceph CSI operator to reconcile Ceph CSI CRs and create/manage CephFS, RBD, NFS, and NVMe-oF CSI components.

The schema section preserves Kubernetes-native pod and volume shapes so users can declaratively customize generated CSI controller/node pods without bypassing API-server validation. The RBAC and Deployment section makes those CRDs actionable by giving the operator and plugin identities the permissions they need to watch storage resources, create CSI workloads, update CR status/finalizers, participate in leader election, and expose metrics.

## Important Kubernetes APIs And Manifest Objects

The first part of the chunk remains inside a large CRD `openAPIV3Schema`. The visible schema fields include CSI deployment options such as `deployCsiAddons`, `enableFencing`, `enableMetadata`, `encryption.configMapName`, `fsGroupPolicy`, `fuseMountOptions`, `generateOMapInfo`, `grpcTimeout`, `imageSet`, `kernelMountOptions`, `leaderElection`, `liveness`, `log.rotation`, `log.verbosity`, `nodePlugin`, and `snapshotPolicy`.

`nodePlugin` is a major schema surface. It allows pod-level customization for node plugin pods: `affinity`, `annotations`, `containerExtraArgs`, `enableSeLinuxHostMount`, `imagePullPolicy`, `kubeletDirPath`, `labels`, `priorityClassName`, `resources`, `serviceAccountName`, `tolerations`, `topology`, `updateStrategy`, and `volumes`. The embedded affinity schema mirrors Kubernetes `NodeAffinity`, `PodAffinity`, and `PodAntiAffinity`, including `preferredDuringSchedulingIgnoredDuringExecution`, `requiredDuringSchedulingIgnoredDuringExecution`, selectors, namespace selectors, match label keys, mismatch label keys, and topology keys.

The `resources` schema is split by CSI sidecar/container role: `addons`, `liveness`, `logRotator`, `plugin`, and `registrar`. Each role accepts Kubernetes-style resource `claims`, `limits`, and `requests`. Quantity fields use `x-kubernetes-int-or-string` and the Kubernetes quantity regex, which lets users express values such as integer CPU-like values or strings like `500m`, `128Mi`, and similar resource quantities.

The `volumes` array defines pairs of `mount` and `volume`. `mount` resembles Kubernetes `VolumeMount`, requiring `mountPath` and `name` and allowing `mountPropagation`, `readOnly`, `recursiveReadOnly`, `subPath`, and `subPathExpr`. `volume` embeds many Kubernetes volume sources, including `awsElasticBlockStore`, `azureDisk`, `azureFile`, `cephfs`, `csi`, `downwardAPI`, `emptyDir`, `ephemeral`, `fc`, `flexVolume`, `flocker`, `gcePersistentDisk`, `gitRepo`, `glusterfs`, `hostPath`, `image`, `iscsi`, `nfs`, `persistentVolumeClaim`, `photonPersistentDisk`, `portworxVolume`, `projected`, `quobyte`, `rbd`, `scaleIO`, `secret`, `storageos`, and `vsphereVolume`. Required fields are preserved for many source types, such as `volumeID` for AWS EBS, `diskName`/`diskURI` for Azure Disk, `secretName`/`shareName` for Azure File, `driver` for CSI, `spec` for ephemeral PVC templates, `pdName` for GCE PD, `iqn`/`lun`/`targetPortal` for iSCSI, `path`/`server` for NFS, `claimName` for PVCs, and `image`/`monitors` for RBD.

`projected` volume sources include current Kubernetes projection types: `clusterTrustBundle`, `configMap`, `downwardAPI`, `podCertificate`, `secret`, and `serviceAccountToken`. These schemas retain required path-like fields and mark config map/secret references as atomic maps. This is important for server-side apply and CRD merge behavior.

The end of the CRD schema sets `snapshotPolicy` to one of `none`, `volumeGroupSnapshot`, or `volumeSnapshot`, provides a top-level `log.verbosity` constrained from 0 to 3, leaves `status` as an object, marks the CRD version `served: true` and `storage: true`, and enables the `status` subresource.

After the CRD, the chunk defines ServiceAccounts in `rook-ceph`: controller and node plugin identities for CephFS, NFS, NVMe-oF, and RBD, plus the `ceph-csi-controller-manager` service account for the operator itself.

Namespace-scoped `Role` objects provide plugin-local permissions. Controller plugin roles for CephFS, NVMe-oF, and RBD can manage `coordination.k8s.io` leases, manipulate `csiaddons.openshift.io/csiaddonsnodes`, read pods/replicasets, and update Deployment/DaemonSet finalizers. Node plugin roles can manage CSI addons nodes, read pods/replicasets, and update workload finalizers. `ceph-csi-leader-election-role` grants the manager access to ConfigMaps, Leases, and Events for controller-runtime leader election.

ClusterRole objects are the broad control-plane permissions. Viewer/editor roles are generated for `cephconnections`, `clientprofiles`, `clientprofilemappings`, `drivers`, and `operatorconfigs` under `csi.ceph.io`, with status reads included. `ceph-csi-manager-role` lets the operator manage ConfigMaps, Services, DaemonSets, Deployments, custom CSI objects, their finalizers/status, `operatorconfigs`, and `storage.k8s.io/csidrivers`. The metrics roles provide `/metrics` read access plus TokenReview and SubjectAccessReview permissions for authenticated metrics serving.

CSI plugin ClusterRoles differ by storage backend. CephFS, NFS, NVMe-oF, and RBD controller roles can read or manage PVs/PVCs, StorageClasses, CSINodes, Nodes, VolumeAttachments, Events, Secrets/ConfigMaps, snapshot resources, service account tokens, and token reviews. CephFS and RBD include group snapshot and OpenShift replication/group-snapshot APIs; RBD also reads `cbt.storage.k8s.io/snapshotmetadataservices`. Node plugin ClusterRoles are narrower, centered on reading nodes, secrets, PVs, volume attachments, config maps, service accounts/tokens, token reviews, events, and PVCs as needed by node-side CSI operations.

RoleBindings and ClusterRoleBindings connect each role to the matching ServiceAccount. The manager service account is bound to manager and metrics-auth ClusterRoles and to the namespace leader-election Role. Each plugin service account is bound to both its namespace Role and backend-specific ClusterRole.

The final Deployment installs `ceph-csi-controller-manager` in `rook-ceph` with one replica, the `ceph-csi-controller-manager` service account, `/manager --leader-elect`, and image `quay.io/cephcsi/ceph-csi-operator:v1.0.1`. It sets `OPERATOR_NAMESPACE` from the pod namespace, `CSI_SERVICE_ACCOUNT_PREFIX` to `ceph-csi-`, and `WATCH_NAMESPACE` to an empty string, implying cluster-wide watching. Health endpoints are `/healthz` and `/readyz` on port 8081. The container has small CPU/memory requests and limits, drops all Linux capabilities, disallows privilege escalation, uses a read-only root filesystem, and the pod runs as non-root.

## Control Flow

The runtime flow is Kubernetes-driven:

1. Applying this manifest registers or updates CRD schema validation and status-subresource behavior for the CSI operator CRDs.
2. Kubernetes creates the service accounts, roles, cluster roles, bindings, and controller-manager Deployment.
3. The Deployment starts one manager pod running `/manager --leader-elect`.
4. Controller-runtime leader election uses the namespace Role over ConfigMaps/Leases/Events so only the active manager reconciles.
5. The manager watches `csi.ceph.io` resources and storage APIs according to `ceph-csi-manager-role`.
6. When reconciling CSI driver CRs/config, the manager creates/updates Deployments, DaemonSets, Services, ConfigMaps, CSIDrivers, and status/finalizer fields.
7. Managed CSI controller and node pods run under backend-specific service accounts. Their Role and ClusterRole permissions let sidecars perform provisioning, attaching, snapshotting, token review, event emission, lease handling, and CSI addons node registration as applicable.

The schema portion affects control flow before reconciliation starts: invalid CR specs are rejected by the API server, defaults may be applied for fields such as several secret names and legacy volume defaults, and structural schema hints such as atomic maps/lists affect how apply/patch operations merge user intent.

## State And Persistence Behavior

Persistent state is stored in Kubernetes, not in local files:

- CRD definitions persist accepted schemas, version storage flags, and the `status` subresource.
- Custom resources created later under `csi.ceph.io` persist desired CSI operator state and status.
- RBAC objects persist the authorization model for operator and plugin identities.
- Leader election persists transient coordination state in ConfigMaps or Leases in the `rook-ceph` namespace.
- Generated Deployments, DaemonSets, Services, ConfigMaps, CSIDrivers, PV/PVC updates, snapshots, group snapshots, and finalizers are reconciled through Kubernetes resources.

The schema uses `x-kubernetes-list-type: atomic` for many embedded Kubernetes arrays and `x-kubernetes-map-type: atomic` for selected references/selectors. This affects persistence during server-side apply: callers replace whole atomic lists/maps rather than merging individual nested items. The `status` subresource separates controller-written status from user-written spec, which is required for safe reconciliation.

The Deployment sets `WATCH_NAMESPACE` to an empty value, so persisted operator behavior is cluster-scoped unless downstream tooling patches this value. `CSI_SERVICE_ACCOUNT_PREFIX` is also persisted as pod environment and must align with the service account names declared in this same chunk.

## Dependencies And Integration Points

This manifest integrates with standard Kubernetes APIs: `v1` ServiceAccounts, RBAC `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding`, `apps/v1` Deployments/DaemonSets, `coordination.k8s.io` Leases, storage resources under `storage.k8s.io`, snapshots under `snapshot.storage.k8s.io`, and core PV/PVC/Node/Secret/ConfigMap/Event APIs.

It also integrates with non-core or optional APIs:

- `csi.ceph.io` custom resources managed by the Ceph CSI operator.
- `csiaddons.openshift.io/csiaddonsnodes` for CSI addons integration.
- `groupsnapshot.storage.k8s.io` and `groupsnapshot.storage.openshift.io` for volume group snapshot flows.
- `replication.storage.openshift.io` group replication resources.
- `cbt.storage.k8s.io/snapshotmetadataservices` for changed-block-tracking snapshot metadata support.
- `authentication.k8s.io/tokenreviews` and `authorization.k8s.io/subjectaccessreviews` for token validation and authenticated metrics/access checks.

The RBAC names and service account names are tightly coupled. For example, `ceph-csi-rbd-ctrlplugin-crb` must bind `ceph-csi-rbd-ctrlplugin-cr` to `ceph-csi-rbd-ctrlplugin-sa`, and the operator's `CSI_SERVICE_ACCOUNT_PREFIX=ceph-csi-` must match the `ceph-csi-*` service account naming convention.

The schema embeds Kubernetes pod customization APIs rather than inventing a separate scheduling model. This makes it integrate naturally with cluster-level schedulers, topology labels, tolerations, priority classes, update strategies, resource quotas, secret/configmap projection, and volume mounting policies.

## Risks And Edge Cases

The manifest grants broad cluster permissions to CSI controller service accounts. PV/PVC create/update/delete, VolumeAttachment patch/status, snapshot content update/status, service account token creation, and TokenReview permissions are powerful. These are typical for CSI sidecars, but any namespace compromise of a plugin service account has cluster-level blast radius.

Optional API groups can be absent. Clusters without snapshot, group snapshot, OpenShift replication, CBT, or CSI addons CRDs may reject RBAC rules for unknown resources depending on API-server behavior and installation order, or the operator may reconcile features that remain unavailable. Install sequencing should account for optional CRDs.

The CRD embeds a very large subset of Kubernetes volume source schema, including legacy and cloud-provider-specific volume types. This is convenient but increases drift risk when Kubernetes removes, deprecates, or changes embedded fields. The schema already includes newer fields such as `podCertificate`, `clusterTrustBundle`, `volumeAttributesClassName`, and `recursiveReadOnly`, so compatibility with older Kubernetes API servers should be checked.

Atomic list/map annotations reduce merge ambiguity but can surprise users applying partial patches. For example, updating one projected source or affinity term can replace an entire atomic list rather than merging a single item.

Validation is uneven by design because the schema mirrors Kubernetes object shapes. Many string fields, object maps, tolerations, update strategy types, and mount options are only typed, not semantically constrained. The API server can accept values that later fail in the operator, scheduler, kubelet, or CSI sidecar.

`WATCH_NAMESPACE` is empty in the Deployment. That is appropriate for a cluster-scoped operator but is risky in multi-tenant clusters if the intended deployment should be namespace-scoped. It also requires the broad ClusterRoles defined here.

The operator image is pinned to `quay.io/cephcsi/ceph-csi-operator:v1.0.1`. Upgrading the image without updating CRDs/RBAC can create version skew; updating CRDs/RBAC without the image can expose fields the running controller does not understand.

The Deployment selector and pod template labels use `control-plane: ceph-csi-op-controller-manager`, while Deployment metadata also uses `control-plane: controller-manager`. That is valid because the selector matches the pod template, but tooling that expects the metadata label value to match the selector could be confused.

Security posture is good for the manager container, but this chunk only shows the operator Deployment. The generated CSI node plugins are likely privileged elsewhere because CSI node plugins commonly need host mounts and kubelet integration. The CRD also exposes `hostPath`, mount propagation, and `enableSeLinuxHostMount`, so downstream CRs can request sensitive host integration.

## Test Signals

High-signal validation for this chunk is manifest/API-server oriented:

- `kubectl apply --dry-run=server -f sources/control-plane/rook/deploy/examples/csi-operator.yaml` should validate the CRDs, RBAC, and Deployment against the target cluster API version.
- `kubectl get crd` should show the `csi.ceph.io` CRDs from earlier and this chunk with served/storage versions and status subresources.
- `kubectl auth can-i --as=system:serviceaccount:rook-ceph:ceph-csi-controller-manager ...` should confirm the manager can manage Deployments, DaemonSets, Services, ConfigMaps, CSIDrivers, and `csi.ceph.io` resources but not unrelated resources.
- Similar `kubectl auth can-i` checks for each `ceph-csi-*-ctrlplugin-sa` and `ceph-csi-*-nodeplugin-sa` should match the backend-specific ClusterRole rules.
- The `ceph-csi-controller-manager` Deployment should become Available with a single pod, `/healthz` and `/readyz` on port 8081 should pass, and logs should show successful leader election.
- Creating minimal valid CSI operator custom resources should exercise the CRD schema, reject invalid enum values such as unknown `snapshotPolicy`, and accept Kubernetes-style quantity strings in sidecar resource requests/limits.
- Reconciliation tests should verify that status updates work through the status subresource and that finalizers can be updated for `drivers`, `clientprofiles`, and `clientprofilemappings`.
- Clusters that do not install optional APIs should be tested explicitly because RBAC and reconciliation paths reference CSI addons, group snapshots, OpenShift replication, and CBT resources.

For static checks, YAML parsing and Kubernetes schema linting should cover every document in this range, verify that every RoleBinding/ClusterRoleBinding subject references an existing ServiceAccount from this manifest, and verify that every roleRef name has a matching Role or ClusterRole.
