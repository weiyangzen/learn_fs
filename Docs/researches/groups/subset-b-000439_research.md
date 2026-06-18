# subset-b-000439 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/localrules.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/localrules.yaml

Purpose: defines the local-cluster `PrometheusRule` set for Rook/Ceph monitoring in namespace `rook-ceph`, labeled for the `rook-prometheus` Prometheus instance. It is the alert policy bundle for Ceph health, mons, OSDs, MDS, mgr, placement groups, nodes, pools, health checks, hardware, Prometheus itself, RADOS, RBD mirroring, NVMe-oF, and cert-manager signals.

Important APIs/types/functions: Kubernetes `monitoring.coreos.com/v1` `PrometheusRule`; alerting groups include `cluster health`, `mon`, `osd`, `mds`, `mgr`, `pgs`, `nodes`, `pools`, `healthchecks`, `hardware`, `PrometheusServer`, `rados`, `generic`, `rbdmirror`, `nvmeof`, and `certmgr`. Representative alerts include `CephHealthError`, `CephMonDown`, `CephOSDDown`, `CephOSDFull`, `CephFilesystemDamaged`, `CephMgrIsAbsent`, `CephPGsInactive`, `CephPoolQuotaBytesCriticallyExhausted`, `CephDaemonSlowOps`, `PrometheusJobMissing`, `CephRBDMirrorImageSyncing`, and `CephNVMeoFGatewayDown`.

Control flow: the Prometheus Operator selects this object by labels and installs each rule group into Prometheus. Expressions query Ceph exporter and mgr metrics over windows, apply `for` durations to suppress short transients, and emit labels such as severity and annotations with runbook-oriented messages.

State and persistence: no application state is stored here. Rules are persisted as Kubernetes objects and Prometheus evaluates them against time-series data retained in the Prometheus store.

Dependencies/integration: depends on Prometheus Operator CRDs, Rook Ceph mgr/exporter metrics, kube-state or node metrics for some node checks, and matching `Prometheus.spec.ruleSelector` in `prometheus.yaml`.

Risks: alert expressions are tightly coupled to metric names and labels exported by Ceph versions. Local thresholds may be noisy for small test clusters, especially one-node pools, near-full OSDs, or intentionally absent daemons.

Test signals: `kubectl apply --server-side --dry-run`, `promtool check rules` after rendering YAML, and end-to-end Prometheus rule discovery with the `prometheus=rook-prometheus` selector.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/localrules.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/prometheus-service.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/prometheus-service.yaml

Purpose: exposes the example Prometheus instance as a Kubernetes `Service` named `rook-prometheus` in `rook-ceph`.

Important APIs/types/functions: `v1/Service` with `type: NodePort`, selector `prometheus: rook-prometheus`, and port `9090` exposed on node port `30900` targeting named container port `web`.

Control flow: Kubernetes routes traffic from node port 30900 to pods created by the Prometheus Operator for the `rook-prometheus` CR.

State and persistence: no durable state; it is a service routing object whose endpoints are derived from matching Prometheus pods.

Dependencies/integration: requires the Prometheus CR in `prometheus.yaml` to create pods with the matching label and a named `web` port.

Risks: fixed NodePort can conflict with cluster policy or another service, and NodePort exposes Prometheus broadly on every node unless network policy constrains it.

Test signals: service creation dry-run, endpoint population, and HTTP reachability to `/graph` or `/-/ready` through node port 30900.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/prometheus-service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/prometheus.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/prometheus.yaml

Purpose: installs the example Prometheus service account, RBAC aggregation, binding, and Prometheus Operator `Prometheus` resource for scraping Rook/Ceph metrics.

Important APIs/types/functions: includes `ServiceAccount/prometheus`, `ClusterRole/prometheus` with aggregation selector `rbac.ceph.rook.io/aggregate-to-prometheus=true`, `ClusterRole/prometheus-rules` granting read access to Prometheus Operator resources, `ClusterRoleBinding/prometheus`, and `Prometheus/rook-prometheus`.

Control flow: the Prometheus Operator reconciles the `Prometheus` CR, uses `serviceMonitorSelector.matchLabels.team=rook` and `ruleSelector.matchLabels.role=alert-rules`, and runs the instance under the `prometheus` service account. RBAC aggregation lets Rook monitoring roles contribute permissions without editing the top-level role.

State and persistence: Prometheus runtime state is owned by the operator-managed pods; this manifest persists only Kubernetes objects and resource requests/limits.

Dependencies/integration: requires Prometheus Operator CRDs, `ServiceMonitor` objects such as `service-monitor.yaml`, `PrometheusRule` objects such as `localrules.yaml`, and monitoring RBAC from `rbac.yaml`.

Risks: empty or mismatched selectors silently result in no targets or rules. Cluster-wide RBAC is broad enough to read monitoring CRs across namespaces.

Test signals: `kubectl get prometheus rook-prometheus`, operator-created StatefulSet/pods, discovered ServiceMonitors, and loaded rules under the Prometheus UI.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/prometheus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/rbac.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/rbac.yaml

Purpose: grants Prometheus the namespace-scoped permissions needed to discover and scrape Ceph manager and exporter metrics in `rook-ceph`.

Important APIs/types/functions: three `Role`/`RoleBinding` pairs: `rook-ceph-monitor`, `rook-ceph-metrics`, and `rook-ceph-monitor-mgr`. They bind the `rook-ceph/prometheus` service account and are labeled to aggregate into the `prometheus` ClusterRole.

Control flow: Kubernetes RBAC authorizes the Prometheus service account to list/watch pods, services, endpoints, configmaps, and Ceph-related resources used by the scrape configuration and ServiceMonitor discovery.

State and persistence: persists RBAC policy only; no runtime state.

Dependencies/integration: complements `prometheus.yaml`; assumes the Prometheus service account lives in `rook-ceph` and that Prometheus Operator service discovery uses Kubernetes API watches.

Risks: namespace and service account names are hard-coded. Missing aggregation labels or RoleBindings will produce scrape discovery failures that look like empty target lists.

Test signals: `kubectl auth can-i --as system:serviceaccount:rook-ceph:prometheus list endpoints -n rook-ceph` and Prometheus target discovery for mgr metrics.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/service-monitor.yaml -->
# sources/control-plane/rook/deploy/examples/monitoring/service-monitor.yaml

Purpose: defines the Prometheus Operator `ServiceMonitor` that discovers the Ceph manager metrics service.

Important APIs/types/functions: `monitoring.coreos.com/v1` `ServiceMonitor/rook-ceph-mgr` in `rook-ceph`, labeled `team: rook`, with a namespace selector for `rook-ceph`, a service label selector for `app: rook-ceph-mgr` and `rook_cluster: rook-ceph`, and endpoint `http-metrics`.

Control flow: Prometheus in `prometheus.yaml` selects this monitor by label, then the operator expands it into scrape config for services matching the selector.

State and persistence: persists scrape discovery configuration as a Kubernetes CR; Prometheus stores scraped samples separately.

Dependencies/integration: requires the Rook Ceph manager service to expose a named metrics port and the Prometheus CR to select `team: rook`.

Risks: label drift on the mgr service or endpoint port rename breaks metrics collection without failing the manifest.

Test signals: ServiceMonitor appears in Prometheus targets, `rook-ceph-mgr` service labels match, and metrics such as `ceph_health_status` are present.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/monitoring/service-monitor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/multus-validation-test-openshift.yaml -->
# sources/control-plane/rook/deploy/examples/multus-validation-test-openshift.yaml

Purpose: creates minimal OpenShift namespace RBAC for a Multus validation test service account.

Important APIs/types/functions: `ServiceAccount/multus-validation-test`, `Role/multus-validation-test`, and `RoleBinding/multus-validation-test` in `openshift-storage`.

Control flow: the role allows the validation pod or test workflow to interact with the namespace resources it needs while running Multus validation on OpenShift.

State and persistence: persists only service account and RBAC policy.

Dependencies/integration: integrates with OpenShift storage namespace conventions and Multus validation jobs/tests outside this file.

Risks: namespace is hard-coded to `openshift-storage`; applying in vanilla Kubernetes or a differently named OpenShift namespace needs edits.

Test signals: `kubectl auth can-i` for the service account and successful Multus validation pod execution.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/multus-validation-test-openshift.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/mysql.yaml -->
# sources/control-plane/rook/deploy/examples/mysql.yaml

Purpose: provides the MySQL half of the classic WordPress example, using Rook-backed dynamic storage through a PVC.

Important APIs/types/functions: `Service/wordpress-mysql`, `PersistentVolumeClaim/mysql-pv-claim`, and `Deployment/wordpress-mysql` using image `mysql:5.6`.

Control flow: the headless MySQL service selects pods labeled `app=wordpress,tier=mysql`; the deployment mounts the PVC at MySQL data storage and configures the database via environment variables.

State and persistence: database files are persisted in `mysql-pv-claim`, whose `storageClassName` is expected to point to a Rook Ceph block storage class.

Dependencies/integration: pairs with `wordpress.yaml` and requires a `rook-ceph-block` or equivalent storage class.

Risks: MySQL 5.6 is old for production use, example credentials are static, and PVC binding fails if the storage class is absent.

Test signals: PVC binds, MySQL pod becomes ready, and WordPress can connect to the service name.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/mysql.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/nfs-load-balancer.yaml -->
# sources/control-plane/rook/deploy/examples/nfs-load-balancer.yaml

Purpose: exposes a Ceph NFS server instance externally through a Kubernetes `LoadBalancer` service.

Important APIs/types/functions: `Service/rook-ceph-nfs-my-nfs-load-balancer` in `rook-ceph`, port `2049`, `externalTrafficPolicy: Local`, selector `app=rook-ceph-nfs`, `ceph_nfs=my-nfs`, `instance=a`.

Control flow: cloud or bare-metal load balancer integration provisions an external address and forwards NFS traffic to the selected NFS ganesha pod.

State and persistence: no storage state; service endpoints follow matching NFS pods.

Dependencies/integration: depends on `CephNFS/my-nfs` from `nfs.yaml` or `nfs-test.yaml` and a cluster load balancer implementation.

Risks: selector pins to instance `a`, so scaling or failover patterns may require a different service strategy. Exposing NFS externally needs network and firewall review.

Test signals: external IP assignment, endpoint selection, and successful NFS mount to the exported path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/nfs-load-balancer.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/nfs-test.yaml -->
# sources/control-plane/rook/deploy/examples/nfs-test.yaml

Purpose: supplies a reduced-size NFS example for tests, including the `CephNFS` daemon and its backing built-in pool.

Important APIs/types/functions: `CephNFS/my-nfs` with `server.active: 1` and debug log level, plus `CephBlockPool/builtin-nfs` mapped to the Ceph pool `.nfs` with replica size 1 and `requireSafeReplicaSize: false`.

Control flow: Rook reconciles the pool, then starts one NFS server daemon using the built-in pool for NFS-Ganesha state.

State and persistence: NFS daemon state is stored in the `.nfs` Ceph pool; the CRs persist desired daemon count and pool properties.

Dependencies/integration: requires Rook Ceph CRDs, an active Ceph cluster, and clients or tests that create exports.

Risks: one-replica pool is unsafe outside test clusters; debug logging can be verbose.

Test signals: CephNFS status ready, `.nfs` pool exists, and test exports can be mounted.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/nfs-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/nfs.yaml -->
# sources/control-plane/rook/deploy/examples/nfs.yaml

Purpose: documents and configures a standard `CephNFS` example with one active NFS server and optional commented sections for Kerberos/SSSD and backing pool setup.

Important APIs/types/functions: `CephNFS/my-nfs` in `rook-ceph`, `spec.server.active`, placement, annotations, labels, resources, and `logLevel: NIV_INFO`. The commented examples show `CephBlockPool`, Kerberos config maps, keytab secrets, and SSSD integration.

Control flow: Rook observes the CephNFS CR and creates NFS-Ganesha deployment resources. Optional security material can be enabled by uncommenting and adapting the Kerberos/SSSD resources.

State and persistence: daemon desired state is stored in the CR; NFS metadata can use a Ceph pool such as `.nfs`.

Dependencies/integration: requires Rook Ceph cluster, NFS CRD/controller, and optional secrets/configmaps for Kerberos.

Risks: many fields are commented placeholders; partial uncommenting can create invalid security configuration. One active server is a simple availability profile.

Test signals: NFS pod readiness, Ganesha logs, CephNFS status, and successful client mount.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/nfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/nvmeof-test.yaml -->
# sources/control-plane/rook/deploy/examples/nvmeof-test.yaml

Purpose: provides a minimal test manifest for a Ceph NVMe-oF gateway.

Important APIs/types/functions: `CephNVMeOFGateway/nvmeof` in `rook-ceph`; the spec configures the gateway server count, pool/reference parameters, and test-friendly settings for the NVMe-oF controller.

Control flow: Rook's NVMe-oF controller reconciles the gateway CR into gateway pods/services that front Ceph RBD over NVMe/TCP.

State and persistence: desired gateway topology is persisted in the CR; exported block data remains in Ceph pools/images.

Dependencies/integration: requires the NVMe-oF CRD/controller, Ceph cluster, and kernel/userland client support for NVMe/TCP tests.

Risks: test defaults are not production sizing, and gateway availability depends on the configured replica count and service exposure.

Test signals: gateway pod ready, service reachable on the NVMe-oF port, and client subsystem discovery/connect succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/nvmeof-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-a.yaml -->
# sources/control-plane/rook/deploy/examples/object-a.yaml

Purpose: defines one RGW object store, `store-a`, using pre-created shared pools.

Important APIs/types/functions: `CephObjectStore/store-a` in `rook-ceph`, `spec.sharedPools`, `gateway.port: 80`, `gateway.instances: 1`, anti-affinity against other RGW pods, and `priorityClassName: system-cluster-critical`.

Control flow: Rook binds the store to shared object pools and deploys one RGW gateway pod/service.

State and persistence: object data and metadata live in the referenced shared pools; the CR stores gateway desired state.

Dependencies/integration: intended to pair with `object-shared-pools.yaml` and `storageclass-bucket-a.yaml`.

Risks: shared pools create coupling between stores; deleting or changing the shared pools affects all dependent stores.

Test signals: RGW service creation, store status ready, and bucket provisioning through the matching bucket storage class.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-account.yaml -->
# sources/control-plane/rook/deploy/examples/object-account.yaml

Purpose: creates a Ceph RGW account object for account-oriented object user management.

Important APIs/types/functions: `CephObjectStoreAccount/my-account` in `rook-ceph` with `spec.store` pointing at the object store.

Control flow: the Rook object controller reconciles the account against RGW admin APIs after the target store is available.

State and persistence: the account exists in RGW metadata and desired state persists as a Kubernetes CR.

Dependencies/integration: requires a running `CephObjectStore` and RGW admin credentials managed by Rook.

Risks: account creation will fail or remain pending if the referenced store is absent or not ready.

Test signals: CR status ready and the corresponding RGW account present via `radosgw-admin account list/show`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-account.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-b.yaml -->
# sources/control-plane/rook/deploy/examples/object-b.yaml

Purpose: defines a second RGW object store, `store-b`, for demonstrating multiple object stores on shared pools.

Important APIs/types/functions: `CephObjectStore/store-b`, `spec.sharedPools`, one RGW gateway on port 80, pod anti-affinity, and cluster-critical priority class.

Control flow: Rook deploys a distinct RGW gateway while reusing the shared pool topology.

State and persistence: object state is stored in shared Ceph pools; the Kubernetes CR stores desired gateway count and scheduling policy.

Dependencies/integration: pairs with shared pool manifests and separate bucket classes/claims for multi-store scenarios.

Risks: pool sharing reduces isolation, and one gateway instance is a single pod availability profile.

Test signals: independent RGW service for `store-b` and successful bucket operations isolated by store name.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-bucket-claim-a.yaml -->
# sources/control-plane/rook/deploy/examples/object-bucket-claim-a.yaml

Purpose: requests an object bucket from the `store-a` bucket storage class.

Important APIs/types/functions: `objectbucket.io/v1alpha1` `ObjectBucketClaim/ceph-bucket-a`, `generateBucketName: ceph-bkt`, and `storageClassName: rook-ceph-bucket-a`.

Control flow: the lib-bucket-provisioner watches the OBC, calls Rook's bucket provisioner, creates an ObjectBucket, and writes connection credentials into a Secret/ConfigMap.

State and persistence: bucket data is persisted in Ceph RGW; the OBC and generated objects persist Kubernetes-side binding state.

Dependencies/integration: requires `storageclass-bucket-a.yaml` and `CephObjectStore/store-a`.

Risks: bucket names are generated, so consumers must read the generated config rather than assume a literal name.

Test signals: OBC `Bound` phase and generated Secret/ConfigMap with RGW endpoint and credentials.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-bucket-claim-a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-bucket-claim-delete.yaml -->
# sources/control-plane/rook/deploy/examples/object-bucket-claim-delete.yaml

Purpose: requests a bucket from a delete-reclaim bucket storage class.

Important APIs/types/functions: `ObjectBucketClaim/ceph-delete-bucket`, `storageClassName: rook-ceph-delete-bucket`, and optional `additionalConfig` placeholder.

Control flow: bucket provisioning creates a Ceph RGW bucket and binding resources. When the OBC is deleted, the storage class reclaim policy controls deletion of the backend bucket.

State and persistence: the RGW bucket holds object data; Kubernetes OBC/ObjectBucket resources track binding lifecycle.

Dependencies/integration: requires `storageclass-bucket-delete.yaml`, Rook bucket provisioner, and `CephObjectStore/my-store`.

Risks: delete reclaim policy can remove bucket data when the claim is deleted.

Test signals: bound OBC and backend bucket removal after deleting the claim.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-bucket-claim-delete.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-bucket-claim-notification.yaml -->
# sources/control-plane/rook/deploy/examples/object-bucket-claim-notification.yaml

Purpose: demonstrates adding bucket notification association labels to an object bucket claim.

Important APIs/types/functions: `ObjectBucketClaim/ceph-notification-bucket` with label `bucket-notification-my-notification: my-notification`, `generateBucketName: ceph-bkt`, and `storageClassName: rook-ceph-delete-bucket`.

Control flow: bucket provisioning creates the bucket, and Rook notification logic can use the label convention to associate the bucket with a named notification configuration.

State and persistence: bucket contents persist in RGW; notification metadata is stored in RGW/bucket configuration and referenced by Kubernetes labels.

Dependencies/integration: requires bucket storage class and a separately defined bucket notification named `my-notification`.

Risks: label-based association is easy to mistype and may not be validated at admission time.

Test signals: OBC bound and RGW bucket notification configuration visible through S3 notification APIs or Rook status.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-bucket-claim-notification.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-bucket-claim-retain.yaml -->
# sources/control-plane/rook/deploy/examples/object-bucket-claim-retain.yaml

Purpose: requests a bucket from a retain-reclaim bucket storage class.

Important APIs/types/functions: `ObjectBucketClaim/ceph-retain-bucket`, generated bucket prefix `ceph-bkt`, `storageClassName: rook-ceph-retain-bucket`, and optional `additionalConfig`.

Control flow: the bucket provisioner creates the bucket and binding objects; deleting the OBC should leave the backend bucket according to the retain reclaim policy.

State and persistence: RGW bucket data persists beyond claim deletion; Kubernetes binding state is removed or released.

Dependencies/integration: requires `storageclass-bucket-retain.yaml` and target `CephObjectStore/my-store`.

Risks: retained buckets can become orphaned and need manual cleanup or re-import.

Test signals: OBC binds, deleting it does not delete the RGW bucket, and credentials cleanup behaves as expected.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-bucket-claim-retain.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-ec.yaml -->
# sources/control-plane/rook/deploy/examples/object-ec.yaml

Purpose: defines a production-style object store with replicated metadata and erasure-coded data pool.

Important APIs/types/functions: `CephObjectStore/my-store`; metadata pool replicated size 3; data pool erasure coded with `dataChunks: 2`, `codingChunks: 1`; compression disabled; `preservePoolsOnDelete: true`; one gateway instance on port 80; health check enabled.

Control flow: Rook creates pools, configures RGW metadata/data placement, then deploys the gateway.

State and persistence: metadata and object data persist in Ceph pools, and pool preservation prevents automatic deletion on CR removal.

Dependencies/integration: requires enough OSD failure domains for size 3 and EC profile creation.

Risks: EC pools need sufficient OSDs and may not support all workloads like replicated pools. Preserved pools require manual cleanup.

Test signals: store ready, EC pool health, and S3 put/get/delete operations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-ec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-external.yaml -->
# sources/control-plane/rook/deploy/examples/object-external.yaml

Purpose: registers an externally hosted RGW endpoint as a Rook `CephObjectStore`.

Important APIs/types/functions: `CephObjectStore/external-store` with `gateway.port: 80` and `gateway.externalRgwEndpoints` containing IP `192.168.39.182`.

Control flow: Rook treats the store as externally reachable and exposes/provisions bucket resources against the configured RGW endpoint rather than deploying RGW pods.

State and persistence: bucket and object state live in the external Ceph/RGW cluster; Kubernetes stores only the object store reference.

Dependencies/integration: requires network reachability to the external endpoint and compatible RGW admin credentials/configuration.

Risks: static IP must be edited for each environment, and Rook cannot control external RGW availability.

Test signals: object store status and successful S3/admin calls through the external endpoint.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-external.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multi-instance-test.yaml -->
# sources/control-plane/rook/deploy/examples/object-multi-instance-test.yaml

Purpose: creates a test realm/zone topology with three object-store gateways sharing one zone but exposing different protocol combinations.

Important APIs/types/functions: `CephObjectRealm`, `CephObjectZoneGroup`, `CephObjectZone`, object stores `store-admin`, `store-s3`, `store-swift`, and `CephObjectStoreUser/multi-instance-user`.

Control flow: Rook creates the realm, zone group, zone pools, then reconciles three RGW instances against the same zone with protocol-specific settings before creating the user.

State and persistence: realm/zone metadata and bucket data live in Ceph RGW pools; CRs persist the topology.

Dependencies/integration: requires object multisite CRDs and a test cluster accepting one-replica pools.

Risks: multiple gateways sharing one zone can conflict if protocol or admin settings are misconfigured.

Test signals: all three object stores ready and user credentials usable against the intended protocol endpoints.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multi-instance-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-pull-realm-test.yaml -->
# sources/control-plane/rook/deploy/examples/object-multisite-pull-realm-test.yaml

Purpose: test-sized secondary-cluster multisite configuration that pulls a realm from a primary object store.

Important APIs/types/functions: `Secret/realm-a-keys`, `CephObjectRealm/realm-a` with `spec.pull`, `CephObjectZoneGroup/zonegroup-a`, `CephObjectZone/zone-b` using one-replica pools, and `CephObjectStore/zone-b-multisite-store`.

Control flow: Rook uses the realm pull endpoint and keys to import realm metadata, creates a secondary zone, then starts an RGW for that zone.

State and persistence: pulled realm metadata and zone pools persist in the secondary Ceph cluster; credentials persist in the secret.

Dependencies/integration: requires a reachable primary zone endpoint and valid access/secret keys.

Risks: placeholder secret data must be replaced; one-replica pools are test only.

Test signals: realm pull succeeds, secondary zone appears in `radosgw-admin zone list`, and sync status advances.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-pull-realm-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-pull-realm.yaml -->
# sources/control-plane/rook/deploy/examples/object-multisite-pull-realm.yaml

Purpose: production-oriented example for pulling an RGW realm into a secondary Rook namespace.

Important APIs/types/functions: `Secret/realm-a-keys`, `CephObjectRealm/realm-a` with pull configuration, `CephObjectZoneGroup/zonegroup-a`, `CephObjectZone/zone-b` with replicated size 3 metadata/data pools, and `CephObjectStore/zone-b-multisite-store`.

Control flow: the secondary cluster imports realm metadata from the primary, creates a zone in that realm, and exposes it through a local RGW gateway.

State and persistence: realm/zone metadata and replicated pools persist in Ceph; pull credentials persist in Kubernetes Secret.

Dependencies/integration: needs primary realm endpoint, enough OSDs for replica size 3, and network connectivity between sites.

Risks: stale or leaked pull keys are sensitive; incorrect endpoints leave the realm pending.

Test signals: object realm status ready, RGW sync status healthy, and cross-site object replication.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-pull-realm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-realm-test.yaml -->
# sources/control-plane/rook/deploy/examples/object-multisite-realm-test.yaml

Purpose: creates only the realm, zone group, and zone pieces of a test multisite object topology.

Important APIs/types/functions: `CephObjectRealm/test-realm`, `CephObjectZoneGroup/test-zonegroup`, and `CephObjectZone/test-zone` with one-replica metadata/data pools and `sharedPools` support.

Control flow: Rook reconciles the realm hierarchy before any object store gateway is attached.

State and persistence: RGW realm/zone metadata and zone pools persist in Ceph; CRs persist desired topology.

Dependencies/integration: intended to pair with `object-multisite-store-test.yaml`.

Risks: without a store, this creates backend topology but no client endpoint; one-replica pools are unsafe for production.

Test signals: realm, zonegroup, and zone statuses ready before creating the store.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-realm-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-store-test.yaml -->
# sources/control-plane/rook/deploy/examples/object-multisite-store-test.yaml

Purpose: attaches a test object store gateway to the `test-zone` multisite topology.

Important APIs/types/functions: `CephObjectStore/test-store` with one gateway instance on port 80 and `spec.zone.name: test-zone`.

Control flow: after the realm/zone resources exist, Rook deploys an RGW gateway bound to that zone.

State and persistence: object data follows the referenced zone's pools; the CR persists gateway desired state.

Dependencies/integration: requires `object-multisite-realm-test.yaml` or equivalent `test-zone`.

Risks: applying this before the zone exists leaves reconciliation pending.

Test signals: store ready, RGW service created, and S3 operations routed to `test-zone`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-store-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-test.yaml -->
# sources/control-plane/rook/deploy/examples/object-multisite-test.yaml

Purpose: provides a compact test multisite configuration with one realm, one zone group, one zone, and one store.

Important APIs/types/functions: `CephObjectRealm/realm-a`, `CephObjectZoneGroup/zonegroup-a`, `CephObjectZone/zone-a` with one-replica pools and compression disabled for data, and `CephObjectStore/multisite-store`.

Control flow: Rook creates the topology in dependency order and starts one RGW gateway in `zone-a`.

State and persistence: test pools hold object and metadata state; CRs hold desired realm and gateway state.

Dependencies/integration: requires Rook object controllers and a small test Ceph cluster.

Risks: replica size 1 and `requireSafeReplicaSize: false` are test-only.

Test signals: all CRs ready and basic S3 object lifecycle against `multisite-store`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite.yaml -->
# sources/control-plane/rook/deploy/examples/object-multisite.yaml

Purpose: production-style single-site piece of an RGW multisite setup.

Important APIs/types/functions: `CephObjectRealm/realm-a`, `CephObjectZoneGroup/zonegroup-a`, `CephObjectZone/zone-a` with size 3 replicated metadata/data pools and `bulk` data parameter, plus `CephObjectStore/multisite-store`.

Control flow: Rook configures RGW realm metadata, zone group, zone pools, and a gateway for the zone.

State and persistence: RGW metadata and objects persist in the configured replicated pools.

Dependencies/integration: needs sufficient OSDs and may later pair with a secondary pull-realm manifest.

Risks: topology changes after buckets exist can disrupt multisite sync; one gateway instance is not highly available.

Test signals: realm/zone/store ready, `radosgw-admin period get` valid, and S3 operations succeed.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-multisite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-openshift.yaml -->
# sources/control-plane/rook/deploy/examples/object-openshift.yaml

Purpose: adapts the standard object-store example for OpenShift by using RGW port 8080 and an OpenShift `Route`.

Important APIs/types/functions: `CephObjectStore/my-store` with replicated metadata/data pools, `preservePoolsOnDelete: true`, gateway port 8080, anti-affinity, health check, and `Route/rook-ceph-rgw-my-store`.

Control flow: Rook creates pools and RGW gateway; OpenShift routes external HTTP traffic to the RGW service.

State and persistence: pools are preserved on object store deletion; route state persists as an OpenShift object.

Dependencies/integration: requires OpenShift route API and a Rook Ceph cluster in `rook-ceph`.

Risks: OpenShift-specific `Route` is not portable to vanilla Kubernetes; preserving pools requires manual lifecycle cleanup.

Test signals: route admitted, RGW service endpoint ready, and S3 access through the route host.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-openshift.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-separate-pools-test.yaml -->
# sources/control-plane/rook/deploy/examples/object-separate-pools-test.yaml

Purpose: creates explicit one-replica RGW pools for a test object store that uses separate pools rather than Rook-created defaults.

Important APIs/types/functions: eight `CephBlockPool` resources including `.rgw.root`, control, meta, log, buckets index, non-EC buckets, OTP, and buckets data pools, all labeled/applicationed for RGW usage with `pg_num`/autoscale test parameters.

Control flow: applying this prepares the pool topology that an object store can reference for separated RGW functions.

State and persistence: each pool stores a specific slice of RGW metadata or object data.

Dependencies/integration: intended for object store tests that require pre-created named pools.

Risks: small `pg_num`, autoscale off, and replica size 1 are not production safe.

Test signals: all pools exist and the object store using them reaches ready state.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-separate-pools-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-shared-pools-test.yaml -->
# sources/control-plane/rook/deploy/examples/object-shared-pools-test.yaml

Purpose: test-sized shared pool set for multiple RGW object stores.

Important APIs/types/functions: `CephBlockPool/rgw-root`, `rgw-meta-pool`, and `rgw-data-pool`, all with replica size 1 and RGW application metadata.

Control flow: Rook creates these pools; object stores with `sharedPools` can then use the same root/meta/data pool set.

State and persistence: object metadata and data are stored in the shared pools and therefore shared by dependent stores.

Dependencies/integration: supports `object-a.yaml` and `object-b.yaml` test scenarios.

Risks: one-replica pools are unsafe and pool sharing can blur failure domains between stores.

Test signals: pools ready and both `store-a` and `store-b` can start against them.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-shared-pools-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-shared-pools.yaml -->
# sources/control-plane/rook/deploy/examples/object-shared-pools.yaml

Purpose: production-style shared RGW pool set with replicated root/meta pools and erasure-coded data.

Important APIs/types/functions: `CephBlockPool/rgw-root` and `rgw-meta-pool` with replica size 3, plus `CephBlockPool/rgw-data-pool` using EC `dataChunks: 2` and `codingChunks: 1`.

Control flow: Rook creates pool resources that object stores can reference via `sharedPools`.

State and persistence: root/meta and object data persist in shared pools.

Dependencies/integration: intended for stores such as `object-a.yaml` and `object-b.yaml`.

Risks: EC data pool requires enough OSDs and careful workload compatibility; shared pools couple store lifecycles.

Test signals: pools healthy and object stores using shared pools can provision buckets.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-shared-pools.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-test.yaml -->
# sources/control-plane/rook/deploy/examples/object-test.yaml

Purpose: minimal test object store using one-replica metadata and data pools.

Important APIs/types/functions: `CephObjectStore/my-store` with metadata/data `replicated.size: 1`, `preservePoolsOnDelete: false`, and one gateway instance on port 80.

Control flow: Rook creates the pools and a single RGW gateway for quick test use.

State and persistence: buckets and objects live in one-replica Ceph pools that can be deleted with the CR.

Dependencies/integration: requires a running Rook Ceph cluster and object CRDs.

Risks: no redundancy and pool deletion on CR removal make it unsuitable for durable data.

Test signals: store ready and simple S3 smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-user.yaml -->
# sources/control-plane/rook/deploy/examples/object-user.yaml

Purpose: creates an RGW user for an existing object store.

Important APIs/types/functions: `CephObjectStoreUser/my-user` in `rook-ceph`, `spec.store: my-store`, and `displayName`.

Control flow: Rook reconciles the user by calling RGW admin APIs and writes credentials to a Kubernetes Secret.

State and persistence: user metadata persists in RGW; credentials persist in Kubernetes Secret.

Dependencies/integration: requires `CephObjectStore/my-store` and RGW admin connectivity.

Risks: deleting/recreating the user rotates or removes credentials, affecting clients.

Test signals: user CR ready and generated secret can authenticate S3 operations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object-user.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object.yaml -->
# sources/control-plane/rook/deploy/examples/object.yaml

Purpose: standard Rook Ceph object store example for a replicated RGW deployment.

Important APIs/types/functions: `CephObjectStore/my-store`, replicated metadata/data pools size 3 with compression disabled and `bulk` data parameter, `preservePoolsOnDelete: false`, one gateway on port 80 with pod anti-affinity and cluster-critical priority, plus health checks.

Control flow: Rook creates pools, configures RGW, and deploys the gateway service/pod.

State and persistence: object metadata and data are stored in Rook-created Ceph pools; pools may be deleted when the CR is deleted.

Dependencies/integration: supports user, bucket storage class, OBC, and external service examples.

Risks: one gateway instance is not HA; `preservePoolsOnDelete: false` can remove data during deletion.

Test signals: object store status ready, RGW service healthy, and S3 bucket lifecycle passes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/object.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/operator-openshift.yaml -->
# sources/control-plane/rook/deploy/examples/operator-openshift.yaml

Purpose: deploys the Rook Ceph operator on OpenShift with SecurityContextConstraints and OpenShift-specific privileged hostpath behavior.

Important APIs/types/functions: `SecurityContextConstraints/rook-ceph` and `rook-ceph-csi`, `ConfigMap/rook-ceph-operator-config`, CSI operator image set ConfigMap, `OperatorConfig`, RBD and CephFS CSI `Driver` CRs, and `Deployment/rook-ceph-operator`.

Control flow: OpenShift SCCs permit required privileged/host operations, ConfigMaps feed operator settings, CSI CRs configure drivers, and the deployment runs `docker.io/rook/ceph:master` with args `ceph operator`.

State and persistence: operator desired settings persist in ConfigMaps and CRs; the operator maintains cluster state through watched Ceph CRs.

Dependencies/integration: requires namespace `rook-ceph`, Rook RBAC/common manifests, OpenShift SCC API, and CSI operator CRDs.

Risks: privileged SCCs and host access are powerful; image tag `master` is mutable; `ROOK_HOSTPATH_REQUIRES_PRIVILEGED=true` differs from vanilla Kubernetes.

Test signals: SCC binding accepted, operator deployment ready, CSI driver CRs reconciled, and logs show successful startup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/operator-openshift.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/operator.yaml -->
# sources/control-plane/rook/deploy/examples/operator.yaml

Purpose: deploys the standard Rook Ceph operator and CSI driver configuration for Kubernetes.

Important APIs/types/functions: `ConfigMap/rook-ceph-operator-config` with `ROOK_*` settings, CSI image set ConfigMap, `OperatorConfig/ceph-csi-operator-config`, RBD and CephFS `Driver` CRs, and `Deployment/rook-ceph-operator` using image `docker.io/rook/ceph:master`.

Control flow: Kubernetes starts the operator deployment under service account `rook-ceph-system`; the operator reads config values, reconciles Ceph CRDs, and coordinates CSI operator/driver resources.

State and persistence: configuration persists in ConfigMaps and CSI CRs; operator runtime state is stateless apart from Kubernetes leader/reconcile state and managed Ceph resources.

Dependencies/integration: requires CRDs, common RBAC/service accounts, CSI operator CRDs, and a namespace named `rook-ceph`.

Risks: mutable `master` image tag, many commented config toggles, disabled operator metrics bind address by default, and hard-coded namespace expectations.

Test signals: operator pod ready, no config parse errors, CSI driver resources created, and creating a `CephCluster` triggers reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/operator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/osd-env-override.yaml -->
# sources/control-plane/rook/deploy/examples/osd-env-override.yaml

Purpose: demonstrates environment variable overrides for OSD pods through a named ConfigMap.

Important APIs/types/functions: `ConfigMap/rook-ceph-osd-env-override` in `rook-ceph` with data key `ASAN_OPTIONS`.

Control flow: the Rook operator can mount/read this ConfigMap and add configured environment variables to OSD daemons.

State and persistence: persists only config key/value data; OSD runtime behavior changes after pod reconciliation/restart.

Dependencies/integration: requires the operator logic that recognizes `rook-ceph-osd-env-override`.

Risks: arbitrary env overrides can destabilize OSDs; ASAN options are mostly for debug/test builds.

Test signals: OSD pod environment contains the key and OSD startup logs reflect the override.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/osd-env-override.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/osd-purge.yaml -->
# sources/control-plane/rook/deploy/examples/osd-purge.yaml

Purpose: runs the Rook OSD purge job to remove an OSD from a Ceph cluster.

Important APIs/types/functions: `batch/v1 Job/rook-ceph-purge-osd`, image `docker.io/rook/ceph:master`, args invoking OSD removal with an OSD ID placeholder, service account `rook-ceph-purge-osd`, Ceph admin secret and config volumes, and environment variables such as `ROOK_MON_ENDPOINTS`, `ROOK_CEPH_USERNAME`, `ROOK_FSID`, and `ROOK_LOG_LEVEL`.

Control flow: the job starts a container with Ceph/Rook config, authenticates to the cluster, and executes the purge command for the configured OSD.

State and persistence: modifies durable Ceph cluster state by removing OSD metadata/auth/CRUSH entries; Kubernetes job state records execution.

Dependencies/integration: requires admin credentials, monitor endpoints, correct FSID, and prior OSD drain/safe-to-destroy handling.

Risks: wrong OSD ID or FSID can destroy the wrong daemon metadata; image tag is mutable.

Test signals: job completes, `ceph osd tree` no longer lists the OSD, and Ceph health returns to expected state.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/osd-purge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool-builtin-mgr.yaml -->
# sources/control-plane/rook/deploy/examples/pool-builtin-mgr.yaml

Purpose: manages the built-in Ceph manager pool through a Rook `CephBlockPool` CR.

Important APIs/types/functions: `CephBlockPool/builtin-mgr` with `spec.name: .mgr`, failure domain `host`, replicated size 3, safe replica requirement, compression disabled, and mirroring disabled.

Control flow: Rook reconciles the CR against the existing or desired `.mgr` Ceph pool.

State and persistence: `.mgr` stores Ceph manager module state and metadata.

Dependencies/integration: depends on Ceph mgr expectations and enough OSDs for three replicas.

Risks: changing the manager pool can affect Ceph dashboard/modules; deleting it may disrupt manager services.

Test signals: `.mgr` pool exists with configured size and Ceph mgr remains healthy.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool-builtin-mgr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool-ec.yaml -->
# sources/control-plane/rook/deploy/examples/pool-ec.yaml

Purpose: defines a simple erasure-coded block pool example.

Important APIs/types/functions: `CephBlockPool/ec-pool`, failure domain `host`, EC profile `dataChunks: 2`, `codingChunks: 1`, and compression disabled.

Control flow: Rook creates the EC profile and pool in Ceph.

State and persistence: data written to the pool is stored with EC layout across OSDs.

Dependencies/integration: requires enough OSDs and failure domains for 2+1 EC placement.

Risks: EC pools have workload and feature constraints compared to replicated pools and may need special storage class settings for RBD.

Test signals: pool ready, Ceph health clean, and pool detail shows the expected EC profile.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool-ec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool-mirrored.yaml -->
# sources/control-plane/rook/deploy/examples/pool-mirrored.yaml

Purpose: creates a replicated block pool with RBD mirroring enabled.

Important APIs/types/functions: `CephBlockPool/mirrored-pool`, replicated size 3, `mirroring.enabled: true`, and `mode: image`.

Control flow: Rook creates the pool and enables image-mode mirroring so individual RBD images can be mirrored.

State and persistence: RBD image data persists in the pool; mirroring state is stored in Ceph RBD metadata.

Dependencies/integration: pairs with `rbdmirror.yaml` and remote peer secrets/config.

Risks: mirroring without a configured peer or mirror daemon does not replicate data.

Test signals: `rbd mirror pool status` and active `CephRBDMirror` daemon health.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool-mirrored.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool-test.yaml -->
# sources/control-plane/rook/deploy/examples/pool-test.yaml

Purpose: minimal one-replica block pool for tests.

Important APIs/types/functions: `CephBlockPool/replicapool` in `rook-ceph`, failure domain `host`, replicated size 1.

Control flow: Rook reconciles the pool for quick single-node test use.

State and persistence: data stored in the pool has no redundancy.

Dependencies/integration: usually paired with a test `StorageClass`.

Risks: replica size 1 risks data loss and can mask production placement issues.

Test signals: pool ready and PVCs using the pool bind in small clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool.yaml -->
# sources/control-plane/rook/deploy/examples/pool.yaml

Purpose: standard replicated Ceph block pool example.

Important APIs/types/functions: `CephBlockPool/replicapool` with failure domain `host`, replicated size 3, safe replica requirement, compression disabled, mirroring disabled in image mode, and status check settings.

Control flow: Rook creates or updates the pool and its mirroring/status configuration.

State and persistence: RBD or other data in the pool is replicated across OSD failure domains.

Dependencies/integration: often consumed by RBD storage class examples and volume replication examples.

Risks: requires enough OSDs for size 3; changing pool parameters after use can affect data placement and health.

Test signals: pool status ready, `ceph osd pool get replicapool size`, and successful PVC provisioning.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/pool.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/radosnamespace-mirrored.yaml -->
# sources/control-plane/rook/deploy/examples/radosnamespace-mirrored.yaml

Purpose: defines an RBD RADOS namespace with mirroring configuration.

Important APIs/types/functions: `CephBlockPoolRadosNamespace/namespace-a`, `blockPoolName`, mirroring `remoteNamespace`, mode `image`, and snapshot schedule interval/start time.

Control flow: Rook creates the namespace under the pool and configures RBD namespace mirroring metadata.

State and persistence: namespace and mirror scheduling state persist in Ceph RBD metadata.

Dependencies/integration: requires the referenced block pool and RBD mirror daemon/peer setup.

Risks: remote namespace mismatch prevents replication; schedules can create unexpected snapshot load.

Test signals: namespace exists, mirror schedule appears through `rbd mirror snapshot schedule ls`, and mirror status is healthy.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/radosnamespace-mirrored.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/radosnamespace.yaml -->
# sources/control-plane/rook/deploy/examples/radosnamespace.yaml

Purpose: creates a basic RBD RADOS namespace inside a block pool.

Important APIs/types/functions: `CephBlockPoolRadosNamespace/namespace-a` with `spec.blockPoolName`.

Control flow: Rook reconciles the namespace into the named Ceph pool.

State and persistence: RBD images created in the namespace persist separately from the default pool namespace.

Dependencies/integration: requires the referenced `CephBlockPool` to exist.

Risks: consumers must set namespace-aware storage class parameters or they will use the default namespace.

Test signals: `rbd namespace ls <pool>` includes `namespace-a` and PVC provisioning works with namespace config.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/radosnamespace.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/rbdmirror.yaml -->
# sources/control-plane/rook/deploy/examples/rbdmirror.yaml

Purpose: deploys RBD mirror daemon(s) for mirrored pools.

Important APIs/types/functions: `CephRBDMirror/my-rbd-mirror` with `count`, placement, annotations, and CPU/memory resource requests/limits.

Control flow: Rook creates mirror daemon deployments that connect to local and remote peers and replay image journal/snapshot changes.

State and persistence: mirror daemon pods are stateless; mirroring state is in Ceph/RBD metadata and remote peer configuration.

Dependencies/integration: requires mirrored pools such as `pool-mirrored.yaml` and configured peers/secrets.

Risks: insufficient resources or peer misconfiguration stalls replication.

Test signals: daemon pod ready and `rbd mirror pool status` reports healthy replay.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/rbdmirror.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/rgw-external.yaml -->
# sources/control-plane/rook/deploy/examples/rgw-external.yaml

Purpose: exposes the RGW service externally through a `NodePort` service.

Important APIs/types/functions: `Service/rook-ceph-rgw-my-store-external`, labels and selector for `app=rook-ceph-rgw`, `rook_cluster=rook-ceph`, `rook_object_store=my-store`, port 80 targeting RGW port 8080.

Control flow: Kubernetes routes node traffic to the RGW service endpoints for `my-store`.

State and persistence: no data state; endpoints follow RGW pods.

Dependencies/integration: requires `CephObjectStore/my-store` and matching service labels.

Risks: NodePort exposes RGW on cluster nodes and target port must match gateway configuration.

Test signals: service endpoints populated and S3 request succeeds through node address/assigned port.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/rgw-external.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/sqlitevfs-client.yaml -->
# sources/control-plane/rook/deploy/examples/sqlitevfs-client.yaml

Purpose: demonstrates a Ceph client and helper deployment for SQLite VFS integration with Ceph.

Important APIs/types/functions: `CephClient/sqlitevfs` with caps, `ServiceAccount/sqlitevfs-setup`, ClusterRole/Binding for reading secrets/configmaps and patching deployment state, and `Deployment/sqlitevfs` with init/setup behavior plus an Alpine runtime container.

Control flow: Rook creates a Ceph client secret; the setup container uses Kubernetes API access to retrieve config/credentials and prepare `/libsqliteceph`; the main container runs with those artifacts mounted.

State and persistence: client identity persists in Ceph auth and Kubernetes Secret; deployment volume state is pod-local.

Dependencies/integration: requires Rook Ceph client controller, kubectl image, and Ceph config secrets.

Risks: broad cluster RBAC for setup should not be copied blindly; old image versions are examples.

Test signals: client secret created, setup completes, and the application can open SQLite data through Ceph VFS.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/sqlitevfs-client.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/storageclass-bucket-a.yaml -->
# sources/control-plane/rook/deploy/examples/storageclass-bucket-a.yaml

Purpose: defines a bucket provisioner `StorageClass` for object store `store-a`.

Important APIs/types/functions: `storage.k8s.io/v1` `StorageClass/rook-ceph-bucket-a`, provisioner `rook-ceph.ceph.rook.io/bucket`, `reclaimPolicy: Delete`, and parameters `objectStoreName: store-a`, `objectStoreNamespace: rook-ceph`.

Control flow: OBCs referencing this class invoke Rook's bucket provisioner for `store-a`.

State and persistence: StorageClass stores provisioning parameters; buckets are persisted in RGW.

Dependencies/integration: requires `CephObjectStore/store-a` and objectbucket CRDs.

Risks: delete reclaim policy removes backend buckets with claims.

Test signals: `object-bucket-claim-a.yaml` binds and produces credentials.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/storageclass-bucket-a.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/storageclass-bucket-delete.yaml -->
# sources/control-plane/rook/deploy/examples/storageclass-bucket-delete.yaml

Purpose: bucket provisioning class for `my-store` with delete reclaim behavior.

Important APIs/types/functions: `StorageClass/rook-ceph-delete-bucket`, bucket provisioner `rook-ceph.ceph.rook.io/bucket`, `reclaimPolicy: Delete`, and object store parameters.

Control flow: OBCs using this class create RGW buckets and delete them when claims are removed.

State and persistence: the class persists provisioning defaults; RGW stores bucket data until reclaim deletion.

Dependencies/integration: used by delete and notification OBC examples.

Risks: accidental OBC deletion can remove object data.

Test signals: bound OBC and backend bucket deletion on claim removal.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/storageclass-bucket-delete.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/storageclass-bucket-retain.yaml -->
# sources/control-plane/rook/deploy/examples/storageclass-bucket-retain.yaml

Purpose: bucket provisioning class for `my-store` with retain reclaim behavior.

Important APIs/types/functions: `StorageClass/rook-ceph-retain-bucket`, provisioner `rook-ceph.ceph.rook.io/bucket`, `reclaimPolicy: Retain`, and object store namespace/name parameters.

Control flow: OBCs using this class create RGW buckets but leave backend buckets after claim deletion.

State and persistence: retained bucket data persists in RGW after Kubernetes claim cleanup.

Dependencies/integration: used by `object-bucket-claim-retain.yaml`.

Risks: retained buckets can accumulate and need manual management.

Test signals: OBC binds and bucket remains after claim deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/storageclass-bucket-retain.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/subvolumegroup.yaml -->
# sources/control-plane/rook/deploy/examples/subvolumegroup.yaml

Purpose: creates a CephFS subvolume group for organizing CephFS CSI subvolumes.

Important APIs/types/functions: `CephFilesystemSubVolumeGroup/group-a`, `filesystemName`, and `pinning` configuration.

Control flow: Rook reconciles the CR by creating the named subvolume group in the target CephFS filesystem.

State and persistence: group metadata persists in CephFS; Kubernetes stores desired pinning policy.

Dependencies/integration: requires an existing `CephFilesystem`.

Risks: wrong filesystem name leaves the CR pending; pinning settings affect data placement.

Test signals: `ceph fs subvolumegroup ls <fs>` includes the group and CSI volumes can target it.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/subvolumegroup.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/toolbox-job.yaml -->
# sources/control-plane/rook/deploy/examples/toolbox-job.yaml

Purpose: runs a one-shot toolbox job and a script container against the Ceph cluster.

Important APIs/types/functions: `Job/rook-ceph-toolbox-job`, primary container using `/usr/local/bin/toolbox.sh --skip-watch`, a second script container, Ceph admin secret, monitor endpoint config, config override, and emptyDir config volume.

Control flow: the toolbox script writes Ceph config/keyring from mounted secrets and exits without endpoint watch; the script container can run scripted Ceph commands.

State and persistence: job completion is stored in Kubernetes; Ceph commands may modify cluster state depending on script content.

Dependencies/integration: requires Rook-created admin secret and mon endpoint ConfigMap.

Risks: example runs with admin credentials; scripts can mutate Ceph irreversibly.

Test signals: job completes and `ceph status` from the job succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/toolbox-job.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/toolbox-operator-image.yaml -->
# sources/control-plane/rook/deploy/examples/toolbox-operator-image.yaml

Purpose: deploys a long-running Ceph toolbox using the Rook operator image rather than the upstream Ceph image.

Important APIs/types/functions: `Deployment/rook-ceph-tools-operator-image`, service account `rook-ceph-default`, image `docker.io/rook/ceph:master`, shell command that writes `ceph.conf` and keyring, mounted admin secret and mon endpoints.

Control flow: the container continuously updates Ceph config as monitor endpoints change and then sleeps for interactive `kubectl exec` use.

State and persistence: pod-local config files are generated from Kubernetes secrets/configmaps; Ceph state is accessed externally through admin commands.

Dependencies/integration: requires admin secret, mon endpoint ConfigMap, and Rook image containing Ceph tooling.

Risks: mutable image tag and admin credentials in a long-running pod.

Test signals: deployment ready and `kubectl exec ... ceph status` succeeds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/toolbox-operator-image.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/toolbox.yaml -->
# sources/control-plane/rook/deploy/examples/toolbox.yaml

Purpose: deploys the standard interactive Ceph toolbox using upstream Ceph image `quay.io/ceph/ceph:v20`.

Important APIs/types/functions: `Deployment/rook-ceph-tools`, service account `rook-ceph-default`, shell script that writes `/etc/ceph/ceph.conf` and `/etc/ceph/keyring`, admin secret, mon endpoint ConfigMap, and config override volume.

Control flow: the container writes initial config, watches monitor endpoint symlink changes, and remains available for `kubectl exec`.

State and persistence: generated config/keyring are pod-local; durable state remains in Ceph and Kubernetes secrets.

Dependencies/integration: requires Rook-created `rook-ceph-mon` secret and `rook-ceph-mon-endpoints` config.

Risks: admin key exposure in an exec-able pod; image version must match supported Ceph tooling.

Test signals: pod ready and Ceph CLI commands work without explicit config flags.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/toolbox.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/two-object-one-zone-test.yaml -->
# sources/control-plane/rook/deploy/examples/two-object-one-zone-test.yaml

Purpose: tests two RGW object stores attached to a single zone.

Important APIs/types/functions: `CephObjectRealm/two-object-one-zone`, `CephObjectZoneGroup/two-object-one-zone`, `CephObjectZone/object-separate-pools`, and object stores `two-object-one-zone-alpha` and `two-object-one-zone-beta`.

Control flow: Rook creates the realm and zone, then deploys two separate RGW gateway services that reference the same zone.

State and persistence: both stores share zone metadata and pools; gateway desired state is separate per CR.

Dependencies/integration: requires a pre-existing or default pool topology for the zone.

Risks: shared zone means metadata coupling between both gateway instances.

Test signals: both stores ready and objects/buckets behave consistently through either endpoint according to zone semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/two-object-one-zone-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/volume-replication-class.yaml -->
# sources/control-plane/rook/deploy/examples/volume-replication-class.yaml

Purpose: defines an OpenShift volume replication class for RBD mirroring.

Important APIs/types/functions: `replication.storage.openshift.io/v1alpha1` `VolumeReplicationClass/rbd-volumereplicationclass`, provisioner, and parameters for the RBD CSI replication driver.

Control flow: VolumeReplication resources reference this class to tell the CSI replication sidecar how to promote/demote mirrored volumes.

State and persistence: class stores static driver parameters; replication state is in PVC/RBD metadata.

Dependencies/integration: requires OpenShift replication CRDs, Ceph CSI with mirroring support, and mirrored RBD pool.

Risks: provisioner/parameter mismatch prevents replication operations.

Test signals: class accepted and referenced by `volume-replication.yaml` without controller errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/volume-replication-class.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/volume-replication.yaml -->
# sources/control-plane/rook/deploy/examples/volume-replication.yaml

Purpose: declares desired replication state for a PVC.

Important APIs/types/functions: `VolumeReplication/pvc-volumereplication`, `volumeReplicationClass`, `replicationState`, and `dataSource` referencing a PVC.

Control flow: the replication controller calls CSI replication operations to make the PVC primary or secondary according to `replicationState`.

State and persistence: Kubernetes stores desired state and status; RBD image mirror state persists in Ceph.

Dependencies/integration: requires `volume-replication-class.yaml`, a mirrored RBD PVC, and replication controller/CSI sidecars.

Risks: promoting the wrong PVC can create split-brain in disaster recovery scenarios.

Test signals: status conditions reflect completed promote/demote and RBD mirror status agrees.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/volume-replication.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/wordpress.yaml -->
# sources/control-plane/rook/deploy/examples/wordpress.yaml

Purpose: provides the WordPress frontend half of the Rook-backed MySQL/WordPress sample.

Important APIs/types/functions: `Service/wordpress` type `LoadBalancer`, `PersistentVolumeClaim/wp-pv-claim`, and `Deployment/wordpress` using image `wordpress:4.6.1-apache`.

Control flow: the deployment mounts the PVC for WordPress content and connects to MySQL service from `mysql.yaml`.

State and persistence: WordPress files persist in `wp-pv-claim`; database state persists in the MySQL PVC.

Dependencies/integration: requires the MySQL example and a Rook-backed storage class.

Risks: old application image and example credentials are not production hardening.

Test signals: PVC bound, service gets external address, and WordPress install page can connect to MySQL.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/wordpress.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/olm/assemble/objectbucket.io_objectbucketclaims.yaml -->
# sources/control-plane/rook/deploy/olm/assemble/objectbucket.io_objectbucketclaims.yaml

Purpose: provides the OLM-assembled CRD for ObjectBucketClaim.

Important APIs/types/functions: `CustomResourceDefinition/objectbucketclaims.objectbucket.io`, group `objectbucket.io`, namespaced scope, kind `ObjectBucketClaim`, short name `obc`, version `v1alpha1`, schema for `spec.storageClassName`, `bucketName`/`generateBucketName`, and status subresource.

Control flow: Kubernetes API server uses the CRD to accept OBC resources; bucket provisioners watch OBCs to create ObjectBuckets and credentials.

State and persistence: OBCs persist claim intent and binding status in etcd.

Dependencies/integration: used by Rook's bucket provisioner and lib-bucket-provisioner semantics.

Risks: OLM assembly must remain aligned with upstream objectbucket schema; overly loose schema can allow invalid claims.

Test signals: CRD installs, OBCs pass validation, and status updates are accepted.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/olm/assemble/objectbucket.io_objectbucketclaims.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/olm/assemble/objectbucket.io_objectbuckets.yaml -->
# sources/control-plane/rook/deploy/olm/assemble/objectbucket.io_objectbuckets.yaml

Purpose: provides the OLM-assembled CRD for cluster-scoped ObjectBucket resources.

Important APIs/types/functions: `CustomResourceDefinition/objectbuckets.objectbucket.io`, cluster scope, kind `ObjectBucket`, short name `ob`, version `v1alpha1`, schema for endpoint, claim reference, storage class, reclaim policy, and status.

Control flow: bucket provisioners create/update ObjectBuckets in response to OBCs; the API server validates and stores those cluster-scoped bindings.

State and persistence: ObjectBuckets represent provisioned backend bucket bindings and store status in etcd.

Dependencies/integration: consumed by object bucket provisioner controllers and OBC lifecycle.

Risks: cluster-scoped objects need careful RBAC; schema drift from objectbucket upstream can break OLM installs.

Test signals: CRD install, ObjectBucket creation by OBC provisioning, and status subresource updates.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/olm/assemble/objectbucket.io_objectbuckets.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/images/Makefile -->
# sources/control-plane/rook/images/Makefile

Purpose: top-level image build entry for Rook images, currently delegating to the Ceph image build.

Important APIs/types/functions: includes `image.mk`, sets `PLATFORMS`, exports `TINI_VERSION`, defines pattern target `ceph.%`, `do.build`, `build.all`, and `help`.

Control flow: `make build` flows through `image.mk` to `do.build`, which builds `ceph.$(PLATFORM)`. `build.all` installs prerequisites and builds configured platforms by invoking the `ceph` subdirectory.

State and persistence: produces local container images and optional cache tags through `image.mk`.

Dependencies/integration: depends on GNU Make, Docker/Podman command variables from common make files, and `images/ceph/Makefile`.

Risks: platform matrix is limited to amd64/arm64 and target behavior depends heavily on included make variables.

Test signals: `make -C images help`, `make -C images BUILD_CONTAINER_IMAGE=false`, and platform-specific image target dry runs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/images/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/images/ceph/Dockerfile -->
# sources/control-plane/rook/images/ceph/Dockerfile

Purpose: builds the Rook Ceph operator/toolbox image on top of a substituted Ceph base image.

Important APIs/types/functions: `FROM BASEIMAGE`, build args `S5CMD_VERSION` and `S5CMD_ARCH`, installs `iproute`, downloads `s5cmd`, copies `rook`, `toolbox.sh`, `set-ceph-debug-level`, monitoring files, and external cluster scripts, creates user `rook` UID 2016, sets entrypoint `/usr/local/bin/rook`.

Control flow: the Makefile copies artifacts into a temporary context and rewrites `BASEIMAGE` before Docker build.

State and persistence: image layers contain Rook binary, scripts, monitoring manifests, and helper tools.

Dependencies/integration: depends on Ceph base image, dnf repositories, GitHub s5cmd release, and built Rook binary.

Risks: network downloads during build reduce reproducibility; `dnf install` can fail when base repos are unavailable.

Test signals: image builds for both architectures and `rook`, `toolbox.sh`, `s5cmd`, and `ip` exist in the image.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/images/ceph/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/images/ceph/Makefile -->
# sources/control-plane/rook/images/ceph/Makefile

Purpose: builds the architecture-specific Rook Ceph container image and generates offline image lists.

Important APIs/types/functions: variables `CEPH_VERSION`, `BASEIMAGE`, `CEPH_IMAGE`, `S5CMD_ARCH`, `BUILD_CONTAINER_IMAGE`, `S5CMD_VERSION`, target `do.build`, `prerequisites`, yq v3 install target, and `list-image`.

Control flow: `do.build` prepares a temporary context, copies Dockerfile/scripts/Rook binary/monitoring/external scripts, replaces `BASEIMAGE`, runs Docker build unless disabled, and removes the context unless saved.

State and persistence: outputs local image `$(BUILD_REGISTRY)/ceph-$(GOARCH)` and optional `deploy/examples/images.txt`.

Dependencies/integration: depends on built Rook binary, monitoring manifests, Docker/Podman, curl, yq v3, and image cache logic from `image.mk`.

Risks: mutable Ceph version variable, temporary context cleanup issues, and offline image list extraction by regex can miss images.

Test signals: `BUILD_CONTAINER_IMAGE=false make -C images/ceph do.build`, real image build, and `make list-image` producing a non-empty sorted `images.txt`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/images/ceph/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/images/ceph/set-ceph-debug-level -->
# sources/control-plane/rook/images/ceph/set-ceph-debug-level

Purpose: helper script to set or reset Ceph debug levels across many Ceph subsystems.

Important APIs/types/functions: Bash functions `check` and `exec_ceph_command`; accepts integer 0 through 20 or `default`; iterates `CEPH_DEBUG_FLAG` and runs `ceph config set global debug_<flag> <level>` or `ceph config rm global debug_<flag>`.

Control flow: validates the single argument, builds ceph config commands for each debug flag, runs them in the background, and waits for all updates.

State and persistence: modifies Ceph monitor configuration database for global debug settings.

Dependencies/integration: requires `ceph` CLI configured with admin or suitable caps.

Risks: high debug levels can flood logs and storage; background commands suppress output, so individual failures may be hard to diagnose.

Test signals: invalid input exits non-zero, `default` removes settings, and `ceph config dump` reflects expected debug keys.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/images/ceph/set-ceph-debug-level -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/images/ceph/toolbox.sh -->
# sources/control-plane/rook/images/ceph/toolbox.sh

Purpose: initializes Ceph CLI configuration inside toolbox containers.

Important APIs/types/functions: constants `CEPH_CONFIG`, `MON_CONFIG`, `KEYRING_FILE`, `CONFIG_OVERRIDE`; functions `write_endpoints` and `watch_endpoints`; reads `ROOK_CEPH_SECRET` or `/var/lib/rook-ceph-mon/secret.keyring` and writes `[client]` keyring.

Control flow: reads monitor endpoints, strips mon names to produce `mon_host`, writes `/etc/ceph/ceph.conf`, appends config override if present, writes keyring, then watches endpoint ConfigMap symlink mtime unless `--skip-watch` is passed.

State and persistence: generated config/keyring are container-local; source secrets/configmaps persist in Kubernetes.

Dependencies/integration: used by toolbox deployment/job manifests and the Rook image.

Risks: shell parsing of endpoints depends on expected `name=addr` format; admin secret is written to disk in the pod.

Test signals: running with mounted secrets creates valid `ceph.conf`; changing mon endpoints rewrites config.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/images/ceph/toolbox.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/images/image.mk -->
# sources/control-plane/rook/images/image.mk

Purpose: shared image build and cache framework for Rook image Makefiles.

Important APIs/types/functions: forces `GOOS=linux`, maps `GOARCH` to platform arch, handles `CACHEBUST`, verbosity, `PULL`, `IMAGE_OUTPUT_DIR`, targets `build`, `clean`, `prune`, `clean.images`, `clean.build`, `cache.lookup`, `cache.images`, `cache.prune`, and `debug.nuke`.

Control flow: image-specific makefiles implement `do.build`; this file wraps builds with cache tagging, cleanup, and pruning. Cache tags use UTC timestamps and an MRU-like retention policy.

State and persistence: local container image cache under repository `cache/`, build registry images, and optional output directories.

Dependencies/integration: depends on common make library, Docker/Podman command variables, GNU utilities, and platform env.

Risks: cleanup/prune/delete targets remove local images and containers; cache date comparison depends on tag format.

Test signals: dry-run or isolated Docker environment for `cache.images`, `cache.prune PRUNE_DRYRUN=1`, and unknown GOARCH failure.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/images/image.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/mkdocs.yml -->
# sources/control-plane/rook/mkdocs.yml

Purpose: configures the Rook documentation site build with Material for MkDocs.

Important APIs/types/functions: site metadata, `docs_dir: Documentation/`, Material theme and overrides, palette toggles, navigation/search features, plugins `search`, `exclude`, `awesome-pages`, `macros`, `minify`, `redirects`, `mike`, and markdown extensions including pymdownx features.

Control flow: MkDocs reads this config, applies plugin transforms, renders Markdown from `Documentation/`, generates redirects, minifies output, and supports version selection through `mike`.

State and persistence: generated site artifacts are build outputs; version metadata is managed by mike during deploy.

Dependencies/integration: depends on MkDocs Material, configured plugins, `.docs/overrides`, `.docs/macros`, and documentation tree.

Risks: plugin version mismatches can break builds; external logo/favicon URLs affect offline builds.

Test signals: `mkdocs build --strict` and `mike` version selector smoke testing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/mkdocs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/register.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/register.go

Purpose: defines the root API group name for Rook Ceph APIs.

Important APIs/types/functions: package `cephrookio` and constant `CustomResourceGroupName = "ceph.rook.io"`.

Control flow: no runtime control flow; other packages import this constant when registering or referring to the API group.

State and persistence: no mutable state or persistence.

Dependencies/integration: integrates with Kubernetes API registration and generated CRD group naming.

Risks: changing this value would be a breaking API group migration for all Ceph CRDs.

Test signals: generated CRDs and clients use `ceph.rook.io` consistently.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/annotations.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/annotations.go

Purpose: provides typed annotation maps and helpers for applying component-specific annotations to Rook-managed Kubernetes objects.

Important APIs/types/functions: `AnnotationsSpec`, `Annotations`, getters such as `GetMgrAnnotations`, `GetDashboardAnnotations`, `GetMonAnnotations`, `GetOSDAnnotations`, `GetCleanupAnnotations`, `GetCephExporterAnnotations`, `GetCmdReporterAnnotations`, `GetCrashCollectorAnnotations`, `GetClusterMetadataAnnotations`, `mergeAllAnnotationsWithKey`, `ApplyToObjectMeta`, and `Merge`.

Control flow: component getters merge `all` annotations with component-specific entries. `ApplyToObjectMeta` initializes metadata annotations and only fills missing keys. `Merge` returns a new map copying receiver values first and only adding absent keys from the supplied map.

State and persistence: no global state; annotations persist on Kubernetes object metadata after reconciliation.

Dependencies/integration: uses Kubernetes `metav1.ObjectMeta` and `KeyType` constants from `keys.go`.

Risks: comments say supplied attributes override originals, but implementation preserves receiver values on conflicts; since `all.Merge(component)` is used, `all` wins over component-specific keys.

Test signals: `annotations_test.go` covers merge, YAML unmarshalling, apply behavior, nil maps, and component getter behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/annotations_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/annotations_test.go

Purpose: unit-tests the annotation helper behavior.

Important APIs/types/functions: `TestCephAnnotationsMerge`, `TestAnnotationsSpec`, `TestAnnotationsApply`, and `TestAnnotationsMerge`.

Control flow: tests construct annotation specs with and without `all`, unmarshal YAML to typed maps, apply annotations to `ObjectMeta`, and verify merge conflict behavior.

State and persistence: test-only in-memory state.

Dependencies/integration: uses `stretchr/testify/assert`, Kubernetes YAML converter, JSON unmarshal, and `metav1.ObjectMeta`.

Risks: tests encode the current non-overwrite merge behavior, so changing comments to match code or code to match comments needs test updates.

Test signals: run with `go test ./pkg/apis/ceph.rook.io/v1 -run Annotations`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/annotations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/cleanup.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/cleanup.go

Purpose: defines cleanup/sanitize constants and small helpers for Ceph cluster data cleanup policy.

Important APIs/types/functions: constants `SanitizeDataSourceZero`, `SanitizeDataSourceRandom`, `SanitizeMethodComplete`, `SanitizeMethodQuick`, `DeleteDataDirOnHostsConfirmation`; methods `CleanupPolicySpec.HasDataDirCleanPolicy`, `SanitizeMethodProperty.String`, and `SanitizeDataSourceProperty.String`.

Control flow: cleanup policy logic checks for exact confirmation string `yes-really-destroy-data` before treating host data dir cleanup as enabled.

State and persistence: no mutable state; values are persisted in `CephCluster.spec.cleanupPolicy`.

Dependencies/integration: depends on API types generated elsewhere in package v1.

Risks: confirmation string is intentionally strict; typos silently disable destructive cleanup.

Test signals: cluster validation/reconcile tests should cover confirmation, sanitize method/source string conversion, and destructive cleanup opt-in.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/cluster.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/cluster.go

Purpose: adds behavior helpers to `ClusterSpec` and `CephCluster`.

Important APIs/types/functions: `ClusterSpec.RequireMsgr2`, `ClusterSpec.NetworkEncryptionEnabled`, `ClusterSpec.IsStretchCluster`, `ClusterSpec.ZonesRequired`, and `CephCluster.GetStatusConditions`.

Control flow: `RequireMsgr2` returns true if network connections explicitly require msgr2 or enable compression/encryption. Stretch/zone helpers inspect monitor stretch cluster and zone settings.

State and persistence: reads fields from the CephCluster spec/status; conditions persist in `status.conditions`.

Dependencies/integration: used by reconcilers and status helpers when deciding network protocol requirements and zone-aware scheduling.

Risks: enabling compression implicitly requires msgr2; callers must understand that behavior.

Test signals: unit tests for nil connections, encryption/compression combinations, stretch cluster zones, and status condition pointer mutation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/doc.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/doc.go

Purpose: package documentation and code-generation markers for the Rook Ceph v1 API package.

Important APIs/types/functions: `+k8s:deepcopy-gen=package,register`, package comment "v1 version of the API", and `+groupName=ceph.rook.io`.

Control flow: no runtime logic; Kubernetes code generators consume the markers.

State and persistence: no state.

Dependencies/integration: integrates with deepcopy/client/CRD generation.

Risks: removing or changing markers breaks generated API artifacts.

Test signals: `make generate` or equivalent codegen produces expected deepcopy registration for v1.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/filesystem.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/filesystem.go

Purpose: exposes status condition access for `CephFilesystem`.

Important APIs/types/functions: method `CephFilesystem.GetStatusConditions() *[]Condition`.

Control flow: returns a pointer to `c.Status.Conditions` for generic condition update helpers.

State and persistence: mutating the returned slice pointer changes filesystem status conditions persisted through Kubernetes status updates.

Dependencies/integration: used by common status/condition reconciliation helpers.

Risks: callers receive a mutable pointer and must update status through the proper subresource path.

Test signals: generic condition updater works with `CephFilesystem` and status patch persists.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/keys.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/keys.go

Purpose: centralizes component key constants used for labels, annotations, placement, and daemon-specific maps.

Important APIs/types/functions: constants `KeyAll`, `KeyMds`, `KeyRgw`, `KeyMon`, `KeyMonArbiter`, `KeyMgr`, `KeyDashboard`, `KeyOSDPrepare`, `KeyRotation`, `KeyOSD`, `KeyCleanup`, `KeyMonitoring`, `KeyCrashCollector`, `KeyClusterMetadata`, `KeyCephExporter`, and `KeyCmdReporter`.

Control flow: no logic; helpers in labels/annotations use these keys to select component-specific maps.

State and persistence: keys appear in CR specs and generated Kubernetes object metadata.

Dependencies/integration: used across Ceph API and operator reconciliation code.

Risks: changing key strings breaks user specs that already use those map keys.

Test signals: label/annotation tests and CR examples using these keys continue to unmarshal and apply.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/keys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/labels.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/labels.go

Purpose: provides typed label maps, component-specific label selection, object metadata application, and DNS-safe label normalization.

Important APIs/types/functions: `SkipReconcileLabelKey`, `LabelsSpec`, `KeyType`, `Labels`, getters such as `GetMgrLabels`, `GetMonitoringLabels`, `GetCephExporterLabels`, `GetCmdReporterLabels`, `ApplyToObjectMeta`, `OverwriteApplyToObjectMeta`, `Merge`, `ToValidDNSLabel`, and `cutMiddle`.

Control flow: component getters merge `all` labels with component labels. Apply fills absent keys, overwrite apply replaces keys, and `ToValidDNSLabel` lowercases, converts invalid bytes to dashes, prepends `d` for numeric starts, trims dashes, and middle-truncates to DNS-1035 length.

State and persistence: no global state; labels persist on Kubernetes object metadata and affect selectors/reconciliation.

Dependencies/integration: uses Kubernetes validation constants and `metav1.ObjectMeta`.

Risks: `Merge` preserves receiver values despite comments about supplied override; `all` labels win collisions over component labels. DNS conversion operates byte-wise, not Unicode-aware.

Test signals: `labels_test.go` covers merge, apply/overwrite, YAML parsing, DNS conversion, and middle truncation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/labels_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/labels_test.go

Purpose: unit-tests label helper behavior and DNS label normalization.

Important APIs/types/functions: `TestCephLabelsMerge`, `TestLabelsSpec`, `TestLabelsApply`, `TestLabelsOverwriteApply`, `TestLabelsMerge`, `TestToValidDNSLabel`, and `Test_cutMiddle`.

Control flow: table-driven tests exercise metadata application, overwrite behavior, merge conflicts, YAML-to-JSON unmarshalling, symbol/digit/case conversion, maximum length handling, and `cutMiddle`.

State and persistence: test-only in-memory maps and ObjectMeta.

Dependencies/integration: uses `testify/assert`, Kubernetes YAML converter, JSON unmarshal, and DNS-1035 expectations from implementation.

Risks: test expectations lock in byte-wise DNS conversion and non-overriding merge semantics.

Test signals: `go test ./pkg/apis/ceph.rook.io/v1 -run Labels`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/labels_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/mirror.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/mirror.go

Purpose: adds small helpers for mirroring specs.

Important APIs/types/functions: `MirroringPeerSpec.HasPeers` and `FSMirroringSpec.SnapShotScheduleEnabled`.

Control flow: `HasPeers` returns true when `SecretNames` is non-empty; snapshot schedule helper returns true when `SnapshotSchedules` is non-empty.

State and persistence: reads CR spec fields persisted in pool/filesystem mirroring configuration.

Dependencies/integration: used by mirror reconcilers to decide whether to configure peers or schedules.

Risks: helper only checks list length, not validity or secret existence.

Test signals: nil/empty/non-empty peer and schedule cases in API or reconciler tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/mirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/namespace.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/namespace.go

Purpose: resolves the effective Ceph RADOS namespace name for a `CephBlockPoolRadosNamespace`.

Important APIs/types/functions: constants `ImplicitNamespaceKey = "<implicit>"`, `ImplicitNamespaceVal = ""`, and function `GetRadosNamespaceName`.

Control flow: if `spec.name` is `<implicit>`, returns empty string for the default RADOS namespace; if `spec.name` is set, returns it; otherwise falls back to the Kubernetes object name.

State and persistence: no state; result controls Ceph namespace naming persisted in Ceph.

Dependencies/integration: used by namespace reconcilers and storage integration that need explicit/default namespace mapping.

Risks: special sentinel `<implicit>` must be documented and preserved; empty string has semantic meaning.

Test signals: cases for implicit, explicit spec name, and metadata-name fallback.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/namespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/network.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/network.go

Purpose: validates and converts Ceph network configuration, especially host networking, Multus selectors, and address ranges.

Important APIs/types/functions: package variable `enforceHostNetwork`, methods `NetworkSpec.IsMultus`, `NetworkSpec.IsHost`, `NetworkSpec.NetworkHasSelection`, `NetworkSpec.GetNetworkSelection`, `AddressRangesSpec.IsEmpty`, `AddressRangesSpec.Validate`, `CIDRList.String`, functions `ValidateNetworkSpec`, `ValidateNetworkSpecUpdate`, `NetworkSelectionsToAnnotationValue`, `SetEnforceHostNetwork`, and `EnforceHostNetwork`.

Control flow: validation rejects legacy `hostNetwork` with non-default providers, requires selectors for Multus, parses public/cluster selectors with NetworkAttachmentDefinition utilities, restricts address ranges to host or Multus networking, validates CIDRs, and allows only limited provider updates involving `host`.

State and persistence: global `enforceHostNetwork` reflects operator config; network specs persist in CephCluster CRs and produce pod annotations.

Dependencies/integration: depends on Multus NAD client utilities, Go `net` CIDR parsing, JSON marshalling, and Rook network provider constants/types.

Risks: global enforce flag affects all specs in-process; legacy single-object JSON selector compatibility is intentionally hidden; update validation allows host toggles but rejects other provider changes.

Test signals: Multus selector parsing, multiple selection rejection, address range validation, host-network override, provider update policy, and annotation JSON output.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/network.go -->
