# subset-b-000429 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/role.yaml -->
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/role.yaml

Purpose: renders the namespace-scoped `rook-ceph-system` `Role` for the Helm-installed Rook Ceph operator when `.Values.rbacEnable` is true. It gives the operator authority to manage helper resources in the release namespace.

Important APIs/types/functions: Kubernetes `rbac.authorization.k8s.io/v1` `Role`, Helm `.Release.Namespace`, `.Values.rbacEnable`, and `include "library.rook-ceph.labels"`. Rules cover core `pods`, `configmaps`, and `services`; `apps`/`extensions` daemonsets, statefulsets, and deployments; `batch` cronjobs; `cert-manager.io` certificates and issuers; and `multicluster.x-k8s.io` serviceexports.

Control flow: Helm skips the entire document when RBAC is disabled. When rendered, the role is bound by `rolebinding.yaml` to the `rook-ceph-system` service account so the operator can create, update, watch, patch, and delete namespaced support objects while reconciling clusters and CSI/operator resources.

State and persistence: the Role is persisted as Kubernetes RBAC state. It stores no Ceph data, but changes immediately alter what the operator can mutate in its own namespace.

Dependencies/integration: depends on the chart library label helper, the matching service account and role binding, cert-manager only when certificate integration is used, and multicluster service export APIs only when multi-cluster service export is enabled.

Risks: permissions are broad inside the operator namespace, including workload deletion and `deletecollection`. Disabling RBAC assumes equivalent permissions already exist. Missing verbs can break reconciliation in ways that surface as operator errors rather than Helm failures.

Test signals: render with `rbacEnable=true` and `false`; verify labels and namespace; run `kubectl auth can-i` as `system:serviceaccount:<ns>:rook-ceph-system` for each resource group used by the operator.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/rolebinding.yaml -->
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/rolebinding.yaml

Purpose: renders the namespace-scoped `rook-ceph-system` `RoleBinding` when `.Values.rbacEnable` is true. It connects the operator service account to the namespace Role emitted by `role.yaml`.

Important APIs/types/functions: Kubernetes `rbac.authorization.k8s.io/v1` `RoleBinding`, `roleRef` to `Role/rook-ceph-system`, subject `ServiceAccount/rook-ceph-system`, Helm `.Release.Namespace`, `.Values.rbacEnable`, and `include "library.rook-ceph.labels"`.

Control flow: the binding is emitted only in RBAC-enabled installs. Kubernetes resolves the subject in the release namespace and grants it the permissions defined by the same-named Role. The operator deployment relies on this authorization after startup.

State and persistence: the binding persists as RBAC relationship state and has no data plane persistence. Updating or deleting it changes the effective permissions of already-running operator pods because Kubernetes authorizes each API request dynamically.

Dependencies/integration: depends on `serviceaccount.yaml` for the subject and `role.yaml` for the referenced Role. It complements broader cluster roles from the common manifests or chart templates that authorize CRD and cluster-wide operations.

Risks: namespace mismatch between the release and the service account subject leaves the operator under-authorized. Static object names can collide if multiple releases target one namespace. Disabling RBAC requires the operator identity to be bound elsewhere.

Test signals: `helm template` should show matching namespaces in metadata and subject. Runtime checks should verify the operator service account can create/update/delete configmaps, services, pods, and controller workloads in the release namespace.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/rolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/securityContextConstraints.yaml -->
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/securityContextConstraints.yaml

Purpose: conditionally renders OpenShift `SecurityContextConstraints` for Rook Ceph daemons and CSI pods when the cluster supports `security.openshift.io/v1`.

Important APIs/types/functions: OpenShift `security.openshift.io/v1` `SecurityContextConstraints`, Helm `.Capabilities.APIVersions.Has`, `.Values.useOperatorHostNetwork`, `.Release.Namespace`, and `include "library.rook-ceph.labels"`. The file emits `rook-ceph` for Rook/Ceph service accounts and `rook-ceph-csi` for ceph-csi-operator-managed CSI service accounts.

Control flow: non-OpenShift clusters render nothing. On OpenShift, `rook-ceph` allows privileged containers, hostPath, host IPC, selected capabilities, and optionally host networking/ports. `rook-ceph-csi` always allows host network, host ports, host PID, host IPC, hostPath, privileged containers, and `SYS_ADMIN`.

State and persistence: SCCs are cluster-level security policy state. They do not persist Ceph data, but they authorize pods that mount host devices, host paths, and privileged contexts needed by OSDs and CSI node plugins.

Dependencies/integration: integrates with service accounts `rook-ceph-system`, `rook-ceph-default`, `rook-ceph-mgr`, `rook-ceph-osd`, `rook-ceph-rgw`, `rook-ceph-nvmeof`, and ceph-csi controller/node plugin accounts. It depends on OpenShift SCC admission behavior.

Risks: the SCCs intentionally grant high privilege. The CSI SCC permits host PID and host networking by design. Missing a service account in `users` causes pod admission failures. Enabling host networking expands network exposure.

Test signals: render on OpenShift and non-OpenShift capability sets; verify SCC users match all service accounts created by chart and ceph-csi-operator; run pod admission smoke tests for OSD, RGW, mgr, and CSI node plugin pods.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/securityContextConstraints.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/serviceaccount.yaml -->
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/serviceaccount.yaml

Purpose: creates the service accounts used by the Rook Ceph operator and by the Ceph COSI driver.

Important APIs/types/functions: Kubernetes `v1` `ServiceAccount`, Helm `.Release.Namespace`, `include "library.rook-ceph.labels"`, and `include "library.imagePullSecrets"`. It emits `rook-ceph-system` with chart labels and `objectstorage-provisioner` with COSI driver labels.

Control flow: both service accounts are rendered unconditionally by this template. Any configured image pull secrets are inserted into both accounts through the shared library helper. Other RBAC templates bind these identities to namespace and cluster permissions.

State and persistence: service accounts are persistent Kubernetes identities. They produce tokens/credentials through Kubernetes mechanisms and become the subject used by operator and COSI workloads.

Dependencies/integration: `rook-ceph-system` integrates with operator deployments and RBAC in `role.yaml`, `rolebinding.yaml`, and broader common roles. `objectstorage-provisioner` integrates with COSI `Bucket*` resources and the object storage provisioner ClusterRole/ClusterRoleBinding.

Risks: adding pull secrets to both identities can widen registry credential availability. If RBAC is disabled or bindings are absent, service accounts exist but workloads fail authorization. The COSI account is useful only when COSI CRDs/controllers are installed.

Test signals: render with and without image pull secrets; verify service account names and namespaces match all RoleBinding and ClusterRoleBinding subjects; run operator and COSI pod startup smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/serviceaccount.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/servicemonitor.yaml -->
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/servicemonitor.yaml

Purpose: optionally creates a Prometheus Operator `ServiceMonitor` named `csi-metrics` for Ceph CSI metrics.

Important APIs/types/functions: `monitoring.coreos.com/v1` `ServiceMonitor`, Helm condition `and .Values.monitoring.enabled .Values.csi.serviceMonitor.enabled`, `.Values.csi.serviceMonitor.namespace`, `.Values.csi.serviceMonitor.labels`, `.Values.csi.serviceMonitor.interval`, and chart labels.

Control flow: Helm renders nothing unless global monitoring and CSI service monitoring are both enabled. The ServiceMonitor may live in an override namespace while its `namespaceSelector.matchNames` targets the release namespace. It selects services with `app: csi-metrics` and scrapes port `csi-http-metrics` at `/metrics`.

State and persistence: the object persists as monitoring configuration consumed by Prometheus Operator. It stores no metrics itself; Prometheus stores scraped metrics elsewhere.

Dependencies/integration: requires the Prometheus Operator CRD, CSI metrics services labeled `app: csi-metrics`, and Prometheus label selectors that match either chart labels or user-provided labels.

Risks: enabling this without the CRD causes apply failures. A namespace override can produce a valid ServiceMonitor that Prometheus does not select. Label or port drift in CSI metrics services silently prevents scraping.

Test signals: render all combinations of `monitoring.enabled`, `csi.serviceMonitor.enabled`, namespace override, custom labels, and interval. In-cluster tests should confirm Prometheus discovers `csi-metrics` targets and scrapes `/metrics`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/servicemonitor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/values.yaml -->
# sources/control-plane/rook/deploy/charts/rook-ceph/values.yaml

Purpose: defines default Helm values for the Rook Ceph operator chart, including images, CRD/RBAC toggles, operator scheduling and security, CSI operator/sidecar images, discovery settings, OBC controls, and monitoring.

Important APIs/types/functions: Helm values consumed by templates and subcharts. Key fields include `image`, `crds.enabled`, `resources`, `currentNamespaceOnly`, `reconcileConcurrentClusters`, `rbacEnable`, `containerSecurityContext`, `allowLoopDevices`, `monRunAsRoot`, `ceph-csi-operator`, `csi.*` sidecar image tags, `enableDiscoveryDaemon`, `useOperatorHostNetwork`, `hostpathRequiresPrivileged`, `enforceHostNetwork`, `imagePullSecrets`, `enableOBCWatchOperatorNamespace`, `obcAllowAdditionalConfigFields`, and `monitoring.enabled`.

Control flow: Helm templates read these values to decide which resources render and what environment, image, RBAC, ServiceMonitor, SCC, discovery, and CSI settings are applied. The `ceph-csi-operator` block configures the subchart when `csi.installCsiOperator` is true.

State and persistence: values do not persist directly until rendered into Kubernetes objects. CRD enablement is persistent and hazardous because deleting CRDs can destroy or orphan Rook-managed custom resources.

Dependencies/integration: integrates with all rook-ceph chart templates, the ceph-csi-operator subchart, Prometheus Operator, OpenShift SCCs, OBC provisioning, private registries, and Kubernetes scheduling/security APIs.

Risks: `image.tag: master` is a moving default; disabling CRD management after install can be destructive if CRDs are removed externally. Host networking, privileged hostPath mode, loop devices, and OBC additional config allowlists are security-sensitive. CSI image tag skew can break driver behavior.

Test signals: run `helm template` with default, production-pinned images, RBAC disabled, CRDs disabled, host-network enabled, monitoring enabled, and private registry secrets. Validate rendered manifests against the target Kubernetes/OpenShift API set.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/bucket-notification-endpoint.yaml -->
# sources/control-plane/rook/deploy/examples/bucket-notification-endpoint.yaml

Purpose: provides a simple HTTP endpoint for testing Ceph RGW bucket notifications. It deploys two nginx replicas and exposes them through a NodePort service.

Important APIs/types/functions: Kubernetes `apps/v1` `Deployment`, `v1` `Service`, label selector `run: my-notification-endpoint`, container image `nginx`, container port 80, service port 8080, targetPort 80, protocol TCP, and service type `NodePort`.

Control flow: the Deployment creates nginx pods with matching labels. The Service selects those pods and forwards port 8080 to container port 80 so a `CephBucketTopic` HTTP endpoint can target `http://my-notification-endpoint:8080`.

State and persistence: deployment replica state and service state persist in Kubernetes. The endpoint has no durable application state and is suitable only as a sample notification sink.

Dependencies/integration: integrates with `bucket-topic.yaml`, which references this service URI, and with Kubernetes service discovery in the namespace where both manifests are applied.

Risks: NodePort exposes the endpoint beyond the cluster depending on environment. The generic nginx image does not record or validate notification payloads, so it is weak as an assertion target. Namespace mismatch breaks DNS lookup from RGW.

Test signals: apply the manifest and verify two ready pods, service endpoints, and HTTP 200 from `my-notification-endpoint:8080`. Trigger an RGW notification and confirm delivery attempts reach the service.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/bucket-notification-endpoint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/bucket-notification.yaml -->
# sources/control-plane/rook/deploy/examples/bucket-notification.yaml

Purpose: defines a sample `CephBucketNotification` that subscribes to object creation events on a named topic with key, metadata, and tag filters.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephBucketNotification`, `spec.topic`, `spec.filter.keyFilters`, `metadataFilters`, `tagFilters`, and S3 event names `s3:ObjectCreated:Put` and `s3:ObjectCreated:Copy`.

Control flow: the Rook/RGW notification controller reconciles the CR in the application namespace, finds topic `my-topic`, and configures RGW notification rules. All listed filters must match for the notification to apply, while any listed event can trigger it.

State and persistence: the CR persists desired notification state in Kubernetes; RGW stores corresponding bucket notification configuration. Filter choices affect future object events but not existing objects.

Dependencies/integration: depends on a compatible CephObjectStore/RGW, topic `my-topic` from `bucket-topic.yaml`, bucket notification CRDs, and Ceph support for the selected S3 notification events and filter syntax.

Risks: regex and suffix/prefix filters are easy to mis-specify, leading to silent non-delivery. Topic namespace/name mismatch blocks reconciliation. Metadata and tag filters only match objects carrying the expected fields.

Test signals: create the topic and notification, upload objects that match and do not match each filter, then inspect RGW/topic delivery and CR status/events for reconciliation errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/bucket-notification.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/bucket-topic.yaml -->
# sources/control-plane/rook/deploy/examples/bucket-topic.yaml

Purpose: defines a sample `CephBucketTopic` named `my-topic` that routes RGW bucket notifications to an HTTP endpoint, with commented examples for AMQP and Kafka.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephBucketTopic`, `spec.objectStoreName`, `objectStoreNamespace`, `opaqueData`, `persistent`, and `endpoint.http.uri`, `disableVerifySSL`, `sendCloudEvents`. Commented fields document AMQP/Kafka `uri`, `ackLevel`, `exchange`, `useSSL`, and `mechanism`.

Control flow: Rook reconciles the topic CR in the application namespace and programs RGW notification topic configuration for object store `my-store` in namespace `rook-ceph`. Notifications referencing `my-topic` then publish to the configured endpoint.

State and persistence: the CR persists desired topic state. `persistent: false` indicates transient topic behavior in RGW rather than a durable queue managed by this manifest.

Dependencies/integration: integrates with `bucket-notification.yaml`, the nginx endpoint example, the target CephObjectStore, and RGW notification compatibility.

Risks: `disableVerifySSL: true` is unsafe for HTTPS production endpoints. Object store name/namespace must match an existing RGW. Non-persistent topics may lose events if the endpoint is unavailable.

Test signals: verify CR status after apply, confirm RGW topic creation, curl the HTTP endpoint from the RGW network path, and run object create/copy tests that trigger the paired notification.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/bucket-topic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/ceph-client.yaml -->
# sources/control-plane/rook/deploy/examples/ceph-client.yaml

Purpose: creates two sample `CephClient` users for OpenStack-style RBD consumers named `glance` and `cinder`.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephClient`, metadata namespace `rook-ceph`, and Ceph caps strings. `glance` receives `mon: profile rbd` and `osd: profile rbd pool=images`; `cinder` receives RBD access to `volumes` and `vms` plus read-only access to `images`.

Control flow: Rook reconciles each client CR by creating/updating a Ceph auth user and a Kubernetes secret containing the key. Consumers then use those credentials for RBD pool access.

State and persistence: client desired state persists in Kubernetes; Ceph auth entries and generated secrets persist until the CR is removed and finalization completes.

Dependencies/integration: depends on the CephCluster, target pools `images`, `volumes`, and `vms`, Rook CephClient CRDs, and applications that consume generated secrets.

Risks: caps are powerful for the named pools and should be narrowed for production tenants. Referencing missing pools causes application failures even if the client is created. Namespace mismatch changes where secrets are generated.

Test signals: apply after pools exist, inspect generated secrets, run `ceph auth get client.glance/client.cinder`, and verify RBD operations are allowed only for intended pools.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/ceph-client.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cleanup-job.yaml -->
# sources/control-plane/rook/deploy/examples/cleanup-job.yaml

Purpose: provides a manual per-node cleanup `Job` that runs Rook's `ceph clean host` logic when operator-managed cleanup did not run or a node needs explicit cleanup.

Important APIs/types/functions: Kubernetes `batch/v1` `Job`, service account `rook-ceph-default`, nodeSelector `kubernetes.io/hostname`, privileged root container `docker.io/rook/ceph:master`, args `["ceph", "clean", "host"]`, hostPath volumes for the Rook data directory, `/dev`, and `/run/udev`, and env vars sourced from `rook-ceph-mon` secret.

Control flow: the user replaces placeholders for job name, node hostname, and dataDirHostPath, then applies one job per node. The pod is pinned to that node, mounts host storage/devices, reads monitor secret and FSID, and sanitizes Rook/Ceph data according to env settings.

State and persistence: the Job persists execution history; the container mutates host disk and Rook data state destructively. Sanitization settings determine how much on-disk metadata is removed.

Dependencies/integration: depends on an existing cluster namespace, `rook-ceph-mon` secret keys `mon-secret` and `fsid`, matching `spec.dataDirHostPath`, udev/dev access, and privileged pod admission.

Risks: this is destructive and placeholder mistakes can clean the wrong node or path. The `master` image tag is moving. Privileged hostPath access is sensitive, and reclaim policies may leave PVs behind.

Test signals: dry-run render after replacing placeholders, verify node selection, inspect logs for FSID/path detection, and confirm target host data/device metadata is removed only on the intended node.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cleanup-job.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-external-management.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-external-management.yaml

Purpose: defines a minimal external-mode `CephCluster` for a cluster namespace where an already-running Rook operator manages an external Ceph cluster.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephCluster`, metadata `rook-ceph-external`, `spec.external.enable: true`, `dataDirHostPath`, and `cephVersion.image: quay.io/ceph/ceph:v20.2.1`.

Control flow: after `common-external.yaml` creates namespace/RBAC, applying this CR tells the operator to reconcile an external cluster rather than create mons/OSDs. The Ceph image is present so other Rook CRs such as RGW, MDS, or NFS can run helper daemons compatible with the external cluster.

State and persistence: the CR persists external cluster desired state and status; actual Ceph data lives outside this Kubernetes cluster or outside Rook management.

Dependencies/integration: depends on common RBAC for the external namespace, external cluster connection secrets/config expected by Rook external mode, and matching Ceph version/image compatibility.

Risks: the external cluster version must match the configured image. Missing external credentials leaves the CR unreconciled. Reusing `dataDirHostPath` across multiple clusters can collide with local state.

Test signals: apply after external common resources and imported connection secrets; verify CephCluster status, operator logs, and successful creation of dependent external-mode CRs such as object stores or filesystems.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-external-management.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-external.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-external.yaml

Purpose: defines an external-mode `CephCluster` for connecting Rook to an existing Ceph cluster without creating local Ceph daemons.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephCluster`, `spec.external.enable: true`, disabled crash collector, mon daemon health check interval, and commented external manager Prometheus endpoint configuration.

Control flow: after CRDs, common resources, operator, and external connection setup are applied, the operator reconciles the CR as an external cluster. It expects imported monitor endpoints and credentials instead of provisioning storage.

State and persistence: the CR stores desired external-cluster integration state in Kubernetes. Ceph data and core daemon state remain in the external Ceph cluster.

Dependencies/integration: depends on external cluster import scripts/secrets, `common-external.yaml` when a separate namespace is used, the Rook operator watch scope, and optional Prometheus endpoints for external manager metrics.

Risks: applying without required external secrets produces a nonfunctional cluster CR. Crash collection is disabled, reducing local diagnostics. Monitoring requires accurate manager IP/port configuration.

Test signals: verify CephCluster reaches ready/connected status, check operator logs for imported mon endpoints, create a simple storage/object CR against the external cluster, and test optional metrics scraping if enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-external.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-multus-test.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-multus-test.yaml

Purpose: defines a small one-node test `CephCluster` that uses Multus network attachments for public and cluster networks.

Important APIs/types/functions: Rook `CephCluster`, `spec.network.provider: multus`, `network.selectors.public`, `network.selectors.cluster`, `mon.count: 1`, `mgr.count: 1`, `storage.useAllNodes/useAllDevices`, and Ceph config overrides for single-replica test behavior.

Control flow: the operator creates a single-mon, single-mgr cluster, attaches Ceph pods to Multus networks named `public-net` and `cluster-net`, uses all available raw devices, and applies non-redundant Ceph settings suitable for tests.

State and persistence: Ceph state persists under `/var/lib/rook` and on selected devices. Multus network attachment state is external to this file.

Dependencies/integration: depends on `NetworkAttachmentDefinition` objects matching `public-net` and `cluster-net`, Rook CRDs/common/operator manifests, available raw devices, and Ceph image `quay.io/ceph/ceph:v20`.

Risks: `allowUnsupported: true`, one monitor, and pool size 1 are not production safe. Missing Multus attachments prevent pod networking. `useAllDevices` can consume unexpected disks.

Test signals: create required NADs, apply the cluster, verify pods have Multus interfaces, check mon/mgr readiness, and confirm Ceph health accepts the configured no-redundancy warnings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-multus-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-on-local-pvc.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-on-local-pvc.yaml

Purpose: demonstrates a production-style Rook Ceph cluster using manually defined local PVs: filesystem PVs for mons and block PVs for OSD PVCs.

Important APIs/types/functions: Kubernetes `StorageClass` `local-storage` with `kubernetes.io/no-provisioner`, six `PersistentVolume` objects with `Retain` reclaim policy and node affinity, and Rook `CephCluster` with mon `volumeClaimTemplate`, `storage.storageClassDeviceSets`, topology spread constraints, prepare pod anti-affinity, priority classes, and disruption management.

Control flow: Kubernetes binds local PVs only when consumers are scheduled. Rook creates mon PVCs from the filesystem template and OSD PVCs from the block-mode device set, then schedules OSD prepare and daemon pods across hosts `host0`, `host1`, and `host2`.

State and persistence: Ceph data persists on host devices `/dev/sdb` and `/dev/sdc` through Retain PVs and under `dataDirHostPath`. Deleting the cluster does not automatically delete retained local PV data.

Dependencies/integration: depends on exact node hostnames, real devices at configured paths, local PV support, Rook common/operator manifests, and Kubernetes scheduler topology behavior.

Risks: wrong device paths can destroy unintended disks. Hostname drift prevents PV scheduling. Retained PVs require manual cleanup before reinstall. Local PVs are not portable, so `portable: false` is required.

Test signals: verify PV availability and node affinity, apply the cluster, check PVC binding distribution, confirm three mons and three OSDs, and test node drain/PDB behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-on-local-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-on-pvc-minikube.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-on-pvc-minikube.yaml

Purpose: provides a single-node Minikube example using local PVs and PVC-backed OSDs for development testing.

Important APIs/types/functions: local `StorageClass`, four `PersistentVolume` objects for Minikube devices `/dev/vdb` through `/dev/vde`, Rook `CephCluster` with `mon.count: 1`, `allowMultiplePerNode: true`, one mgr, block-mode `storageClassDeviceSets`, and a `CephBlockPool` named `.mgr` with replica size 1.

Control flow: the single filesystem PV backs the mon, three block PVs back OSD PVCs, and Rook runs all Ceph daemons on the Minikube node. The built-in manager pool is explicitly created with unsafe single-replica settings.

State and persistence: data persists on the configured Minikube extra disks and `/var/lib/rook`. The `.mgr` pool and OSDs are intentionally non-redundant.

Dependencies/integration: depends on Minikube device naming, local PV support, Rook common/operator manifests, and an environment with extra disks created as described by the comments.

Risks: device names differ by Minikube driver. Single monitor and replica size 1 can lose data. `quay.io/ceph/ceph:v20` is less precise than a patch tag.

Test signals: verify Minikube has expected devices, PVs bind, CephCluster becomes ready, `.mgr` pool exists with size 1, and basic RBD/Ceph health commands succeed.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-on-pvc-minikube.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-on-pvc.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-on-pvc.yaml

Purpose: demonstrates a production-style cloud deployment where mons and OSDs are backed by dynamically provisioned PVCs, using `gp2-csi` as the sample storage class.

Important APIs/types/functions: Rook `CephCluster`, mon PVC template, `cephVersion` v20.2.1, two mgrs, dashboard SSL, monitoring options, log collector, `storageClassDeviceSets` with portable OSDs, topology spread constraints, prepare pod anti-affinity, optional metadata/WAL PVC templates, priority classes, disruption management, and commented KMS/key rotation configuration.

Control flow: the operator creates mon PVCs and OSD PVCs from the storage class, spreads OSD pods by hostname/zone where possible, tunes device class behavior for cloud disks, and manages PDBs during disruptions.

State and persistence: Ceph data persists in dynamically provisioned PVs plus host metadata under `/var/lib/rook`. Optional KMS secrets/config affect encryption key state when enabled.

Dependencies/integration: depends on a working `gp2-csi` or replacement storage class, topology labels, Rook common/operator manifests, Ceph image availability, and optional Vault/KMS resources if uncommented.

Risks: sample storage class and zone topology may not match the cluster. Portable OSD behavior relies on storage that can attach across nodes. Misconfigured KMS blocks encrypted OSD startup. Cloud disk performance affects Ceph health.

Test signals: render/apply with a real storage class, verify PVC provisioning, OSD spread, mgr failover, log collection, PDB creation, and optional KMS secret validation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-on-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-stretched-aws.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-stretched-aws.yaml

Purpose: defines an AWS-like stretched Ceph cluster using PVC-backed OSDs across zones with an arbiter zone.

Important APIs/types/functions: Rook `CephCluster`, `mon.count: 5`, `mon.stretchCluster` with `failureDomainLabel: topology.kubernetes.io/zone`, arbiter zone `us-east-2a`, OSD zones `us-east-2b` and `us-east-2c`, mon PVC template using `gp2-csi`, two storageClassDeviceSets, placement/preparePlacement node affinity, and `CephBlockPool` `.mgr` with `failureDomain: zone`, `size: 4`, and `replicasPerFailureDomain: 2`.

Control flow: Rook creates five monitors, assigns stretch roles by zone labels, schedules OSD PVC sets only in the two data zones, and configures the manager pool for zone-aware replicated placement.

State and persistence: Ceph state persists in AWS-style PVCs and Rook host path metadata. Stretch topology becomes part of Ceph CRUSH and pool placement behavior.

Dependencies/integration: requires zone labels, `gp2-csi`, sufficient nodes/PVC capacity in data zones, Rook stretch-cluster support, and an arbiter-capable topology.

Risks: wrong zone labels break stretch placement. `allowUnsupported: true` is not production-safe. Insufficient OSDs per failure domain prevents healthy replicated placement.

Test signals: validate node labels before apply, confirm mon zone assignments, inspect CRUSH map and `.mgr` pool properties, and run failure tests for one data zone and the arbiter zone.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-stretched-aws.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-stretched.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-stretched.yaml

Purpose: defines a raw-device stretched Ceph cluster with three zones, one arbiter zone, and all OSDs constrained to the two non-arbiter zones.

Important APIs/types/functions: Rook `CephCluster`, `mon.stretchCluster` with `failureDomainLabel: topology.kubernetes.io/zone`, `subFailureDomain: host`, zones `a`, `b`, and `c`, `storage.useAllNodes/useAllDevices`, `placement.arbiter` toleration, `placement.osd` node affinity to zones `b` and `c`, and `.mgr` `CephBlockPool` with zone failure domain and host sub-failure domain.

Control flow: the operator creates five mons, places arbiter monitor behavior according to stretch config, consumes raw devices only on nodes matching OSD placement, and applies a replicated manager pool suitable for two data zones plus arbiter.

State and persistence: Ceph data persists on all selected raw devices and `/var/lib/rook`; stretch placement persists in Ceph topology and pool settings.

Dependencies/integration: depends on correct node zone labels, available raw devices, control-plane tolerations for the arbiter if used, and Rook common/operator manifests.

Risks: `useAllDevices` can consume unintended disks. Incorrect labels or not enough hosts per zone break redundancy. `allowUnsupported: true` and stretch mode require careful version validation.

Test signals: verify node labels and devices, check OSD pods only in zones `b`/`c`, inspect mon quorum and CRUSH topology, and simulate zone/node loss to validate health behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-stretched.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-test.yaml -->
# sources/control-plane/rook/deploy/examples/cluster-test.yaml

Purpose: provides a minimal non-production Ceph cluster for quick tests on one or more nodes with raw devices.

Important APIs/types/functions: Rook `CephCluster`, `mon.count: 1`, `allowMultiplePerNode: true`, `skipUpgradeChecks: true`, one mgr with rook module, dashboard, disabled crash collector, `storage.useAllNodes/useAllDevices`, health checks, priority classes, disruption management, Ceph config for pool size 1, and `.mgr` `CephBlockPool` size 1.

Control flow: after common/operator manifests, Rook creates a one-mon/one-mgr cluster, consumes all raw devices, suppresses no-redundancy warnings, and creates a single-replica manager pool.

State and persistence: data persists on selected devices and `/var/lib/rook`, but redundancy is intentionally disabled. Upgrade safety gates are skipped.

Dependencies/integration: depends on available raw devices, Rook CRDs/operator/RBAC, Ceph image `quay.io/ceph/ceph:v20`, and a test environment where data loss is acceptable.

Risks: not production safe: one mon, pool size 1, all-device consumption, unsupported generic image tag, and skipped upgrade checks. Reinstall requires cleaning dataDirHostPath and devices.

Test signals: verify CephCluster readiness, `.mgr` pool size, dashboard availability, and expected HEALTH warnings suppressed by config. Confirm no production automation applies this file.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster.yaml -->
# sources/control-plane/rook/deploy/examples/cluster.yaml

Purpose: is the primary production-oriented CephCluster example for raw-device Rook deployments, documenting many supported cluster settings in one manifest.

Important APIs/types/functions: Rook `CephCluster` with `cephVersion`, `dataDirHostPath`, upgrade gates, mon/mgr counts, dashboard, monitoring/exporter settings, network encryption/compression/msgr2/Multus/host options, crash and log collectors, cleanup policy, placement/annotations/labels/resources, storage selection and config, disruption management, CSI read affinity, and health/liveness/startup probes.

Control flow: once CRDs/common/operator are installed, the operator reconciles the CR by creating mons, mgrs, OSD discovery/prepare/daemon resources, services, secrets, configmaps, collectors, PDBs, and optional monitoring/network behavior according to the spec.

State and persistence: Ceph state persists on selected raw devices and `dataDirHostPath`; Kubernetes stores CR status, secrets, services, and managed workloads. Cleanup policy can intentionally destroy host data only when confirmation is set.

Dependencies/integration: depends on Rook operator, common RBAC/service accounts, Ceph image availability, Kubernetes node/device topology, optional Prometheus, optional Multus, CSI drivers, and any configured placement labels/taints.

Risks: `useAllDevices` can claim unexpected disks. Cleanup confirmation is destructive. Generic network/security settings require kernel and CNI support. Production should pin exact image tags and validate upgrade gates.

Test signals: dry-run and apply in a representative cluster, verify mon quorum, mgr active/standby, OSD inventory, dashboard TLS, health checks, log collection, PDBs, and safe upgrade behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cluster.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/common-external.yaml -->
# sources/control-plane/rook/deploy/examples/common-external.yaml

Purpose: creates namespace-local prerequisites for managing an external Ceph cluster in `rook-ceph-external` while an operator runs in `rook-ceph`.

Important APIs/types/functions: Kubernetes `Namespace`, `RoleBinding` to `ClusterRole/rook-ceph-cluster-mgmt`, `RoleBinding` to `Role/rook-ceph-cmd-reporter`, service accounts `rook-ceph-cmd-reporter` and `rook-ceph-default`, and a namespaced `Role` allowing pod/configmap get/list/watch/create/update/delete.

Control flow: after the base operator/common resources exist, this manifest adds the external namespace and grants the operator service account permission to manage cluster-scoped workloads in that namespace. It also creates the command reporter identity used by Rook helper jobs.

State and persistence: namespace, RBAC, and service accounts persist as Kubernetes control-plane state. They do not store Ceph data but authorize external-mode reconciliation.

Dependencies/integration: depends on `common.yaml` having created `rook-ceph-cluster-mgmt` and on the operator watching `rook-ceph-external`. It pairs with `cluster-external.yaml` or `cluster-external-management.yaml`.

Risks: if the operator is configured current-namespace-only, it will not watch the external namespace. Subject namespace/name mismatches leave reconciliation unauthorized. The sample assumes `rook-ceph-external` unless edited.

Test signals: apply after base common/operator resources, run `kubectl auth can-i` as the operator service account in the external namespace, and verify external CephCluster reconciliation starts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/common-external.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/common-second-cluster.yaml -->
# sources/control-plane/rook/deploy/examples/common-second-cluster.yaml

Purpose: provides RBAC and service accounts needed for a second Rook Ceph cluster namespace, `rook-ceph-secondary`, managed by an operator in `rook-ceph`.

Important APIs/types/functions: Kubernetes `Namespace`, RoleBindings to `rook-ceph-cluster-mgmt`, `rook-ceph-cmd-reporter`, and `rook-ceph-mgr-system`; service accounts for cmd reporter, default, mgr, OSD, purge OSD, and RGW; roles for cmd reporter, OSD, purge OSD, and mgr; ClusterRole/ClusterRoleBinding for OSD node listing; and ClusterRoleBinding for mgr cluster access.

Control flow: base `common.yaml` creates shared ClusterRoles. This file creates namespace-local identities and binds them so the operator can reconcile a second CephCluster and its daemons in the secondary namespace.

State and persistence: all objects are persistent Kubernetes namespace/RBAC/identity state. They authorize creation, deletion, purging, and manager-module operations for a second cluster, but do not store Ceph data directly.

Dependencies/integration: depends on base ClusterRoles from `common.yaml`, operator watch scope, and any secondary CephCluster manifest applied later.

Risks: comments mention templating, but the checked-in manifest is hardcoded to `rook-ceph-secondary`. RBAC is broad, including deployment deletion, PVC deletion, and Ceph CR patch/update. Static ClusterRoleBinding names can collide if copied without renaming.

Test signals: run auth checks for operator, mgr, OSD, and purge service accounts; apply a secondary cluster; verify resources stay isolated to `rook-ceph-secondary` except expected cluster-wide mgr/OSD node access.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/common-second-cluster.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/common.yaml -->
# sources/control-plane/rook/deploy/examples/common.yaml

Purpose: creates the foundational namespace, service accounts, ClusterRoles, Roles, and bindings required before deploying the Rook Ceph operator and cluster examples in the `rook-ceph` namespace.

Important APIs/types/functions: Kubernetes `Namespace`, `ClusterRole`, `ClusterRoleBinding`, `Role`, `RoleBinding`, and `ServiceAccount`. Major roles include `objectstorage-provisioner-role`, `rook-ceph-cluster-mgmt`, `rook-ceph-global`, `rook-ceph-mgr-cluster`, `rook-ceph-mgr-system`, `rook-ceph-object-bucket`, `rook-ceph-osd`, `rook-ceph-system`, `rook-ceph-cmd-reporter`, `rook-ceph-mgr`, `rook-ceph-osd`, and `rook-ceph-purge-osd`.

Control flow: users apply this before `operator.yaml` and cluster manifests. It grants the operator global watch/update/status/finalizer access for Rook CRDs, namespace management rights for workloads/secrets/services/configmaps, object bucket provisioning permissions, mgr module permissions, OSD topology permissions, purge job permissions, CSI operator resource permissions, and COSI provisioning permissions.

State and persistence: the file creates durable authorization and identity state. It does not persist Ceph data, but it gates every later reconciliation path and allows controllers to create persistent secrets, CRs, PVCs, PVs, services, deployments, jobs, and events.

Dependencies/integration: must stay synchronized with Rook CRDs, manager/operator code, CSI and COSI APIs, ObjectBucket APIs, OpenShift machine/disruption APIs, Multus network attachment definitions, and all example cluster manifests.

Risks: RBAC is intentionally broad and cluster-scoped. Missing new CRD resources breaks reconciliation after upgrades, while over-broad permissions increase service-account compromise impact. Static names assume one primary Rook deployment per cluster/namespace.

Test signals: compare role resource lists with CRDs and controllers, run `kubectl auth can-i` matrices for operator/mgr/OSD/purge/COSI accounts, and perform an end-to-end apply of common, operator, and a sample cluster.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/bucketaccess.yaml -->
# sources/control-plane/rook/deploy/examples/cosi/bucketaccess.yaml

Purpose: defines a sample COSI `BucketAccess` that requests S3 credentials for an existing bucket claim.

Important APIs/types/functions: `objectstorage.k8s.io/v1alpha1` `BucketAccess`, metadata namespace `default`, `spec.bucketClaimName: sample-bucket`, `bucketAccessClassName: sample-bac`, `credentialsSecretName: sample-access-secret`, and `protocol: s3`.

Control flow: the COSI controller and Rook Ceph COSI driver reconcile the access request, use the referenced access class for authentication details, and create/update the named credentials secret.

State and persistence: the BucketAccess object and generated secret persist in Kubernetes. Actual bucket/user permissions are managed in Ceph RGW by the driver.

Dependencies/integration: depends on `bucketclaim.yaml`, `bucketaccessclass.yaml`, installed COSI CRDs/controllers, `CephCOSIDriver`, and the referenced object store user secret.

Risks: namespace mismatch with the bucket claim or secret expectations breaks provisioning. The named secret contains credentials and needs normal secret access controls. Alpha COSI APIs may change.

Test signals: apply with the paired class/claim/driver, verify status, confirm `sample-access-secret` exists, and test S3 access using the generated credentials.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/bucketaccess.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/bucketaccessclass.yaml -->
# sources/control-plane/rook/deploy/examples/cosi/bucketaccessclass.yaml

Purpose: defines a COSI `BucketAccessClass` that tells the COSI controller how to grant S3 access through the Rook Ceph driver.

Important APIs/types/functions: `objectstorage.k8s.io/v1alpha1` `BucketAccessClass`, `driverName: rook-ceph.ceph.objectstorage.k8s.io`, `authenticationType: KEY`, and parameters `objectStoreUserSecretName` and `objectStoreUserSecretNamespace`.

Control flow: BucketAccess objects reference this class. The controller passes the driver name and parameters to the Rook Ceph COSI driver, which uses the privileged object store user secret to create credentials.

State and persistence: the class is cluster-scoped COSI configuration. It does not contain credentials directly, but it points to a secret that authorizes bucket access management.

Dependencies/integration: depends on COSI CRDs/controllers, the Rook Ceph COSI driver, and secret `rook-ceph-object-user-my-store-cosi` in namespace `rook-ceph`.

Risks: stale or wrong secret references prevent access provisioning. KEY authentication exposes long-lived credentials through generated secrets. The driver name must exactly match the installed driver.

Test signals: apply with the driver and secret present, create a BucketAccess using `sample-bac`, and verify credentials are generated and work against RGW.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/bucketaccessclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/bucketclaim.yaml -->
# sources/control-plane/rook/deploy/examples/cosi/bucketclaim.yaml

Purpose: defines a sample COSI `BucketClaim` requesting an S3 bucket using the sample bucket class.

Important APIs/types/functions: `objectstorage.k8s.io/v1alpha1` `BucketClaim`, metadata namespace `default`, `spec.bucketClassName: sample-bcc`, and `protocols: [s3]`.

Control flow: the COSI controller watches the claim, resolves `BucketClass/sample-bcc`, asks the Rook Ceph COSI driver to provision a bucket, and records binding/status information for the claim.

State and persistence: the claim persists desired bucket state in Kubernetes; the driver creates corresponding RGW bucket state in Ceph. Deletion behavior is controlled by the referenced bucket class.

Dependencies/integration: depends on `bucketclass.yaml`, COSI CRDs/controllers, the Ceph COSI driver, and an object store user with bucket capabilities.

Risks: alpha API stability, missing bucket class, or missing driver prevents provisioning. Namespace-local application code still needs a BucketAccess to obtain credentials.

Test signals: apply with the bucket class and driver installed, verify claim status/binding, list the bucket in RGW, then delete and confirm behavior follows the class deletion policy.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/bucketclaim.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/bucketclass.yaml -->
# sources/control-plane/rook/deploy/examples/cosi/bucketclass.yaml

Purpose: defines a sample COSI `BucketClass` for provisioning RGW buckets through the Rook Ceph COSI driver.

Important APIs/types/functions: `objectstorage.k8s.io/v1alpha1` `BucketClass`, `driverName: rook-ceph.ceph.objectstorage.k8s.io`, `deletionPolicy: Delete`, and parameters pointing to `objectStoreUserSecretName` and namespace.

Control flow: BucketClaim objects reference this class. The COSI controller invokes the matching driver with the parameters, and the driver provisions/deletes RGW buckets according to the deletion policy.

State and persistence: the class persists cluster-level provisioning policy. Referenced buckets persist in Ceph RGW until deleted by claim lifecycle and policy.

Dependencies/integration: depends on COSI CRDs/controllers, the Rook Ceph COSI driver, and a privileged object store user secret created by the `cephcosidriver.yaml` sample or equivalent.

Risks: `deletionPolicy: Delete` can remove buckets when claims are deleted. Wrong secret namespace/name blocks provisioning. Driver-name drift leaves claims unhandled.

Test signals: create a BucketClaim using `sample-bcc`, verify bucket creation in RGW, then delete the claim in a test environment and confirm bucket deletion behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/bucketclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/cephcosidriver.yaml -->
# sources/control-plane/rook/deploy/examples/cosi/cephcosidriver.yaml

Purpose: enables the Rook Ceph COSI driver and creates a privileged RGW user for provisioning COSI buckets and access credentials.

Important APIs/types/functions: Rook `ceph.rook.io/v1` `CephCOSIDriver` with `spec.deploymentStrategy: "Auto"` and `CephObjectStoreUser` named `cosi` in `rook-ceph` with `store: my-store`, display name, and wildcard `user` and `bucket` capabilities.

Control flow: the Rook operator reconciles `CephCOSIDriver` by deploying or configuring the COSI driver automatically. It reconciles `CephObjectStoreUser` by creating an RGW user and Kubernetes secret that BucketClass and BucketAccessClass parameters can reference.

State and persistence: the driver CR and object store user CR persist in Kubernetes. RGW user credentials and capabilities persist in Ceph and in generated Kubernetes secrets.

Dependencies/integration: depends on a CephObjectStore named `my-store`, COSI CRDs/controllers, RBAC for `objectstorage-provisioner`, and the bucket class/access class manifests that reference the generated secret.

Risks: wildcard user and bucket capabilities are intentionally high privilege and should be scoped carefully in production. Store name mismatch prevents user creation. Automatic deployment depends on operator support for the COSI driver.

Test signals: apply after object store creation, verify driver pods/resources, confirm the object user secret exists, and provision a bucket/access pair using the sample COSI classes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/cosi/cephcosidriver.yaml -->
