# Research: subset-b-000338

Grouped research for Ceph-CSI chart defaults, RBD Helm templates, static Kubernetes deploy manifests, the `cephcsi` entrypoint, image/deploy automation, and Ceph version/user e2e helpers.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/values.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/values.yaml

Purpose: default values for the CephFS Helm chart, covering RBAC/service accounts, cluster config, KMS config, logging, `CSIDriver`, nodeplugin, provisioner, storage/snapshot/group-snapshot classes, optional Secret creation, `ceph.conf`, and internal socket/configmap names.

Important APIs/types/functions: no code APIs; the exported interface is the chart value schema. Key knobs include `csiConfig`, `encryptionKMSConfig`, `CSIDriver.fsGroupPolicy`, `nodeplugin.forcecephkernelclient`, kernel/fuse mount options, `provisioner.deployController`, sidecar images, `storageClass.fsName`, CephFS secret refs, and `driverName: cephfs.csi.ceph.com`.

Control flow: Helm templates consume these defaults to conditionally render service accounts, RBAC, DaemonSet/Deployment sidecars, metrics Services, StorageClass, SnapshotClass, GroupSnapshotClass, KMS/config ConfigMaps, and optional Secret.

State and persistence behavior: persistent configuration is Kubernetes object state plus CephFS subvolumes/snapshots created later by the driver. Secret values are disabled by default but include placeholder credentials when enabled.

Dependencies and integration points: integrates with Kubernetes CSI sidecars, CephFS mounters, Vault/KMS config, Prometheus metrics, kubelet plugin paths, and the Ceph-CSI `cephcsi` binary flags.

Risks: placeholder cluster IDs, filesystem names, and secrets must be replaced. `logLevel: 5` is verbose by default. Enabling generated Secrets with plaintext values is unsafe outside examples. Mount/kernel/fuse options can override runtime behavior globally. `externallyManagedConfigmap` shifts responsibility to the operator.

Test signals: mainly validated through Helm rendering, chart install tests, and CephFS e2e coverage that exercises provisioning, expansion, snapshots, and mount options.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/Chart.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/Chart.yaml

Purpose: Helm chart metadata for the Ceph RBD CSI chart.

Important APIs/types/functions: declares `apiVersion: v1`, `name: ceph-csi-rbd`, `appVersion: canary`, `version: 3-canary`, keywords, homepage, chart source URL, and icon.

Control flow: Helm tooling reads this file for packaging, indexing, dependency-free chart identity, and release metadata. `deploy.sh` rewrites `appVersion`, `version`, and source branch references during non-devel chart publication.

State and persistence behavior: no runtime state. The file contributes packaged chart metadata in chart repositories.

Dependencies and integration points: consumed by Helm, Artifact Hub/chart repositories, release automation, and humans browsing the chart.

Risks: `canary` values are appropriate for development but must be rewritten for stable releases. The chart metadata points to the devel branch by default, so release automation correctness matters.

Test signals: packaging/release jobs and `helm lint`/chart install checks are the primary validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/ceph-conf.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/ceph-conf.yaml

Purpose: renders the RBD chart's Ceph configuration ConfigMap.

Important APIs/types/functions: emits a `v1/ConfigMap` named from `.Values.cephConfConfigMapName`, with standard chart labels, `data.ceph.conf` from `tpl .Values.cephconf`, and an empty `keyring` key required by Ceph clients.

Control flow: Helm evaluates the templated `cephconf` string, allowing values to reference other chart fields, then mounts the resulting ConfigMap into provisioner and nodeplugin pods under `/etc/ceph/`.

State and persistence behavior: persisted as Kubernetes ConfigMap state. Running pods observe mounted ConfigMap contents according to Kubernetes volume update behavior.

Dependencies and integration points: depends on RBD chart helper templates for labels and on pod volume mounts in Deployment/DaemonSet templates.

Risks: malformed `cephconf` breaks Ceph client startup. `tpl` increases flexibility but also allows value-provided template evaluation. The keyring is deliberately empty, so credentials must come from CSI Secrets rather than this ConfigMap.

Test signals: Helm rendering, chart install smoke tests, and driver startup failures validate this path.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/ceph-conf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/csidriver-crd.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/csidriver-crd.yaml

Purpose: renders the Kubernetes `CSIDriver` object for the RBD driver.

Important APIs/types/functions: object name comes from `.Values.driverName`; spec sets `attachRequired: true`, `podInfoOnMount: true`, `fsGroupPolicy`, and `seLinuxMount`.

Control flow: installed once per driver name so Kubernetes can discover CSI driver capabilities and pass pod context to node publish operations.

State and persistence behavior: cluster-scoped Kubernetes API object. It affects scheduling/mount behavior but stores no driver data.

Dependencies and integration points: consumed by kubelet, external-attacher, Kubernetes storage controllers, and Ceph-CSI node publish logic that expects pod info.

Risks: driver name must match sidecar flags and StorageClass `provisioner`. Incorrect `fsGroupPolicy` or `seLinuxMount` changes security semantics for mounted volumes.

Test signals: Kubernetes CSI conformance, chart rendering, and e2e pod mount tests expose mismatches.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/csidriver-crd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/csiplugin-configmap.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/csiplugin-configmap.yaml

Purpose: renders the Ceph-CSI cluster configuration ConfigMap unless externally managed.

Important APIs/types/functions: gated by `not .Values.externallyManagedConfigmap`; writes `config.json` from `toJson .Values.csiConfig` and `cluster-mapping.json` from `toJson .Values.csiMapping`.

Control flow: driver pods mount this ConfigMap and read cluster monitors, per-driver network namespace paths, read-affinity config, RBD mirror counts, and disaster-recovery cluster/pool/filesystem mappings.

State and persistence behavior: Kubernetes ConfigMap persists cluster connection metadata. It does not hold Ceph auth secrets.

Dependencies and integration points: integrated with nodeplugin/provisioner mounts, `configMapName`, optional `configMapKey`, and Ceph-CSI internal config loading.

Risks: empty default config means no usable Ceph cluster until operators populate values or manage the ConfigMap externally. Cluster IDs must match StorageClass/SnapshotClass parameters and should remain immutable.

Test signals: driver startup, provisioning attempts, and config reload behavior validate this object.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/csiplugin-configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/encryptionkms-configmap.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/encryptionkms-configmap.yaml

Purpose: renders KMS configuration for encrypted RBD volumes.

Important APIs/types/functions: emits a `v1/ConfigMap` named from `.Values.kmsConfigMapName`; `data.config.json` is `toJson .Values.encryptionKMSConfig`.

Control flow: RBD node and provisioner pods mount the ConfigMap at `/etc/ceph-csi-encryption-kms-config/`; the driver resolves `encryptionKMSID` StorageClass parameters against this JSON.

State and persistence behavior: Kubernetes ConfigMap holds non-secret KMS connection/config metadata. Secrets/tokens are separate, including service account projected tokens when enabled.

Dependencies and integration points: integrates with Vault/KMS providers, StorageClass encryption options, and `oidc-token` projected volumes.

Risks: KMS JSON shape is provider-specific and weakly validated at template time. Storing sensitive values in this ConfigMap would be an operator error.

Test signals: encryption e2e tests and driver startup/provisioning logs expose invalid KMS config.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/encryptionkms-configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/extra-deploy.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/extra-deploy.yaml

Purpose: injects arbitrary extra Kubernetes objects into an RBD Helm release.

Important APIs/types/functions: ranges over `.Values.extraDeploy`, emits `---`, and renders each object through `tpl (. | toYaml) $`.

Control flow: any value-provided object becomes part of the rendered chart, with full chart context available during templating.

State and persistence behavior: depends entirely on the extra objects supplied by the operator.

Dependencies and integration points: supports local extensions such as Secrets, ServiceMonitors, additional RBAC, or policy objects without modifying the chart.

Risks: this is a powerful escape hatch. Bad objects can fail the whole release, conflict with chart-owned objects, or grant unexpected permissions. `tpl` evaluates user-provided templates.

Test signals: Helm template/lint and cluster admission are the main validation; chart tests rarely cover operator-specific extras.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/extra-deploy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/groupsnapshotclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/groupsnapshotclass.yaml

Purpose: optionally renders a `VolumeGroupSnapshotClass` for RBD group snapshots.

Important APIs/types/functions: gated by `.Values.volumeGroupSnapshotClass.create`; emits `groupsnapshot.storage.k8s.io/v1beta2`, driver name, `clusterID`, `pool`, optional `volumeGroupNamePrefix`, group snapshotter secret name/namespace, annotations, labels, and deletion policy.

Control flow: when enabled, the external snapshotter group-snapshot feature can use this class to create group snapshot content through the RBD CSI driver.

State and persistence behavior: cluster-scoped snapshot class state; actual group snapshots are separate CRs and Ceph RBD group resources.

Dependencies and integration points: requires group snapshot CRDs/controllers and matching provisioner RBAC/sidecar feature gate.

Risks: API is beta; missing CRDs or disabled sidecar feature gates make this object unusable. `clusterID` and `pool` must match configured Ceph cluster/pool.

Test signals: group snapshot e2e coverage and Helm rendering with the create flag enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/groupsnapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-clusterrole.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-clusterrole.yaml

Purpose: renders cluster-wide RBAC for the RBD nodeplugin service account.

Important APIs/types/functions: gated by `.Values.rbac.create`; grants reads on nodes, secrets, configmaps, serviceaccounts, persistentvolumes, volumeattachments, and creation of `serviceaccounts/token`.

Control flow: the nodeplugin needs these permissions for node identity/topology, KMS/Vault token or connection secret access, config loading, PV lookup, volume attachment inspection, and projected service-account token creation.

State and persistence behavior: Kubernetes RBAC object only.

Dependencies and integration points: bound by the nodeplugin ClusterRoleBinding and consumed by the DaemonSet service account.

Risks: secret `get/list/watch` is broad cluster-wide access. Operators seeking least privilege may need namespace scoping or externally managed RBAC.

Test signals: mount/encryption/fencing/read-affinity e2e tests and Kubernetes authorization failures validate the permission set.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-clusterrole.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-clusterrolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-clusterrolebinding.yaml

Purpose: binds the RBD nodeplugin ClusterRole to its service account.

Important APIs/types/functions: gated by `.Values.rbac.create`; subject name uses `ceph-csi-rbd.serviceAccountName.nodeplugin`; namespace is `.Release.Namespace`; role name uses the nodeplugin fullname helper.

Control flow: Kubernetes authorization uses this binding when nodeplugin pods call API operations granted by the ClusterRole.

State and persistence behavior: cluster-scoped RBAC binding state.

Dependencies and integration points: depends on service account creation or a preexisting service account with the same resolved name.

Risks: namespace/name mismatches silently leave nodeplugin pods unauthorized. If the service account is reused, it inherits broad nodeplugin privileges.

Test signals: authorization failures in nodeplugin logs and e2e mount/encryption workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-clusterrolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-daemonset.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-daemonset.yaml

Purpose: renders the privileged RBD nodeplugin DaemonSet that serves node-stage/node-publish operations on every node.

Important APIs/types/functions: main `csi-rbdplugin` container runs `--type=rbd --nodeserver=true`, kubelet plugin/staging paths, CSI-Addons endpoint, topology/read-affinity/fencing flags, and slow-op logging. Sidecars include `driver-registrar` and optional `liveness-prometheus`.

Control flow: the pod runs on host network/PID, creates the CSI socket under the kubelet plugin directory, registers with kubelet through the registrar, maps/unmaps RBD devices, mounts volumes into kubelet pod paths, and exposes liveness metrics when enabled.

State and persistence behavior: hostPath state includes kubelet plugin sockets, pod mount propagation, `/dev`, `/run/mount`, `/sys`, `/lib/modules`, Ceph logs, and optional SELinux config. Keys are in memory-backed `emptyDir`; KMS tokens are projected.

Dependencies and integration points: requires privileged host access, Ceph config/KMS ConfigMaps, Kubernetes service account/RBAC, kubelet plugin registry, Ceph kernel modules or rbd-nbd, and CSI-Addons consumers.

Risks: high privilege and broad hostPath access are required but sensitive. Incorrect `kubeletDir`, registration path, or SELinux mounts can break registration/mounts. Read-affinity labels must match Ceph CRUSH locations.

Test signals: nodeplugin DaemonSet rollout, kubelet CSI registration, pod mount e2e tests, encryption tests, and metrics scraping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-http-service.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-http-service.yaml

Purpose: optionally exposes nodeplugin liveness/metrics over a Kubernetes Service.

Important APIs/types/functions: gated by `.Values.nodeplugin.httpMetrics.service.enabled`; supports annotations, clusterIP, externalIPs, loadBalancerIP/source ranges, service type, service port, and target container metrics port.

Control flow: selects DaemonSet pods by app/component/release labels and routes `http-metrics` traffic to the liveness-prometheus container.

State and persistence behavior: Service object state only.

Dependencies and integration points: used by Prometheus/ServiceMonitor and operators diagnosing nodeplugin health.

Risks: enabling external Service settings can expose metrics beyond the cluster. Label mismatches prevent endpoints from appearing.

Test signals: Helm rendering, endpoint population, and metrics scrape checks.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-http-service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-serviceaccount.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-serviceaccount.yaml

Purpose: optionally creates the RBD nodeplugin service account.

Important APIs/types/functions: gated by `.Values.serviceAccounts.nodeplugin.create`; name comes from the service-account helper and labels follow the chart/release/component scheme.

Control flow: the DaemonSet references this service account, and RBAC bindings grant it API permissions.

State and persistence behavior: namespace-scoped Kubernetes identity object.

Dependencies and integration points: tied to ClusterRoleBinding and projected service-account token use for KMS.

Risks: disabling creation requires an existing correctly named service account. Reusing a service account can couple privileges across workloads.

Test signals: pod admission and authorization behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-serviceaccount.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-clusterrole.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-clusterrole.yaml

Purpose: renders cluster RBAC for the RBD provisioner/controller Deployment and sidecars.

Important APIs/types/functions: grants access to secrets, PVs/PVCs, storageclasses, events, endpoints, replication CRDs, snapshots, group snapshots when enabled, configmaps, serviceaccounts, PVC status for resizing, nodes, CSINodes, serviceaccount tokens, and volumeattributesclasses. Some rules are conditional on attacher/resizer/group-snapshot settings.

Control flow: external-provisioner, attacher, resizer, snapshotter, and Ceph-CSI controller use these permissions during provisioning, attachment, expansion, snapshotting, leader election, metadata updates, and DR integrations.

State and persistence behavior: RBAC state only; it authorizes controllers that mutate PV/PVC/snapshot API objects and Ceph-side resources.

Dependencies and integration points: bound to the provisioner service account and must align with enabled sidecars/features in `provisioner-deployment.yaml`.

Risks: broad secret and storage-object privileges are powerful. Conditional group snapshot RBAC must match sidecar feature-gate settings or operations fail.

Test signals: provisioning, expansion, snapshot, clone, group snapshot, and replication e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-clusterrole.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-clusterrolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-clusterrolebinding.yaml

Purpose: binds the RBD provisioner ClusterRole to the provisioner service account.

Important APIs/types/functions: gated by `.Values.rbac.create`; subject uses `ceph-csi-rbd.serviceAccountName.provisioner` in the release namespace; role name uses the provisioner fullname helper.

Control flow: enables the controller Deployment and CSI sidecars to call cluster-scoped storage APIs.

State and persistence behavior: cluster-scoped RBAC binding only.

Dependencies and integration points: requires matching service account and ClusterRole.

Risks: namespace or helper-name drift results in unauthorized sidecars. Reusing the service account gives it broad storage privileges.

Test signals: Kubernetes authorization errors during provisioner startup and storage workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-clusterrolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-deployment.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-deployment.yaml

Purpose: renders the RBD controller/provisioner Deployment.

Important APIs/types/functions: main `csi-rbdplugin` runs `--type=rbd --controllerserver=true`, clone-depth/snapshot thresholds, CSI-Addons endpoint, cluster/instance/fencing/profiling flags, and metadata flag. Sidecars include external-provisioner, optional resizer, snapshotter, optional attacher, optional Ceph-CSI metadata controller, and optional liveness metrics container.

Control flow: Deployment replicas coordinate through leader election and shared socket `emptyDir`. The Ceph-CSI controller serves CSI calls; sidecars watch Kubernetes storage APIs, call the socket, and update PV/PVC/snapshot/attachment state.

State and persistence behavior: Kubernetes API objects store controller results; Ceph stores RBD images, snapshots, OMAP metadata, and optional encrypted metadata. In-pod sockets and key dirs are ephemeral.

Dependencies and integration points: depends on Ceph/KMS/config ConfigMaps, service account/RBAC, external CSI sidecar images, host `/dev` and `/sys`, lib modules, and optional projected KMS token.

Risks: version skew among sidecars and CSI driver affects feature support. Multi-replica anti-affinity may block scheduling on small clusters. Clone/snapshot thresholds must remain within driver validation. Host network changes DNS/network behavior.

Test signals: RBD provisioning, deletion, expansion, snapshots, clones, group snapshots, metrics, and controller failover tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-http-service.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-http-service.yaml

Purpose: optionally exposes provisioner/controller liveness metrics through a Service.

Important APIs/types/functions: gated by `.Values.provisioner.httpMetrics.service.enabled`; supports annotations, clusterIP, external IPs, load balancer settings, service type, and maps service port to `.Values.provisioner.httpMetrics.containerPort`.

Control flow: selects provisioner Deployment pods by app/component/release labels.

State and persistence behavior: Service object state only.

Dependencies and integration points: Prometheus/ServiceMonitor integration and debugging of controller health.

Risks: metrics endpoints may be unintentionally exposed with non-ClusterIP settings. No endpoints appear if labels differ from the Deployment.

Test signals: endpoint population and Prometheus scrape checks.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-http-service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-role.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-role.yaml

Purpose: renders namespace-scoped RBAC for provisioner leader election and configmap management.

Important APIs/types/functions: gated by `.Values.rbac.create`; grants configmaps `get/list/watch/create/update/delete` and leases `get/watch/list/delete/update/create`.

Control flow: external CSI sidecars use Leases for leader election and may use ConfigMaps for legacy locks/config.

State and persistence behavior: namespace-scoped RBAC; authorized controllers persist Lease/ConfigMap objects.

Dependencies and integration points: bound by the RoleBinding to the provisioner service account.

Risks: configmap delete/update permissions are broad in the namespace. Namespace mismatch breaks leader election.

Test signals: sidecar leader-election logs and HA provisioner e2e behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-rolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-rolebinding.yaml

Purpose: binds the namespace Role to the RBD provisioner service account.

Important APIs/types/functions: gated by `.Values.rbac.create`; subject and role names use RBD helper templates and `.Release.Namespace`.

Control flow: enables namespace-scoped leader election and configmap operations for provisioner sidecars.

State and persistence behavior: namespace-scoped RBAC binding only.

Dependencies and integration points: must align with Role and service account names.

Risks: a disabled or mismatched binding causes leader-election/config authorization failures while cluster RBAC may still appear correct.

Test signals: sidecar startup logs and multi-replica leader election.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-rolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-serviceaccount.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-serviceaccount.yaml

Purpose: optionally creates the RBD provisioner service account.

Important APIs/types/functions: gated by `.Values.serviceAccounts.provisioner.create`; named by `ceph-csi-rbd.serviceAccountName.provisioner`; labeled with app/chart/component/release/heritage/common labels.

Control flow: the provisioner Deployment uses this identity for all driver and sidecar Kubernetes API calls.

State and persistence behavior: namespace-scoped Kubernetes identity object.

Dependencies and integration points: ClusterRoleBinding, RoleBinding, projected KMS tokens, and pod `serviceAccountName`.

Risks: disabling creation requires a preexisting account with matching RBAC. Shared accounts inherit broad provisioner privileges.

Test signals: pod admission and authorization behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-serviceaccount.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/secret.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/secret.yaml

Purpose: optionally renders a Kubernetes Secret for RBD Ceph credentials and encryption passphrase.

Important APIs/types/functions: gated by `.Values.secret.create`; writes `stringData.userID`, `userKey`, and `encryptionPassphrase`; supports annotations and common labels.

Control flow: StorageClass and SnapshotClass secret reference parameters point driver sidecars/nodeplugin to this Secret when defaults are used.

State and persistence behavior: credentials persist in Kubernetes Secret storage; Kubernetes encodes but does not inherently protect values without cluster secret encryption/RBAC controls.

Dependencies and integration points: Ceph auth users, StorageClass secret fields, KMS/encryption flows, and provisioner/nodeplugin RBAC.

Risks: placeholder plaintext values must be replaced. Enabling chart-managed credentials can leak secrets via values files or release history.

Test signals: provisioning, staging, snapshotting, and encryption tests fail quickly with bad credentials.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/secret.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/snapshotclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/snapshotclass.yaml

Purpose: optionally renders an RBD `VolumeSnapshotClass`.

Important APIs/types/functions: gated by `.Values.volumeSnapshotClass.create`; sets driver, `clusterID`, optional `snapshotNamePrefix`, snapshotter secret name/namespace, annotations, labels, and deletion policy.

Control flow: external-snapshotter uses this class to create `VolumeSnapshotContent` objects and call the RBD CSI snapshot service.

State and persistence behavior: class is cluster-scoped; snapshots persist as Kubernetes snapshot CRs and Ceph RBD snapshots.

Dependencies and integration points: requires snapshot CRDs/controller, provisioner snapshotter sidecar, configured Ceph cluster ID, and credentials.

Risks: missing CRDs or secret namespace mismatch break snapshot creation. Deletion policy affects whether backing snapshots are retained.

Test signals: snapshot/restore e2e tests and Helm rendering with the create flag.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/storageclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/storageclass.yaml

Purpose: optionally renders the RBD `StorageClass`.

Important APIs/types/functions: gated by `.Values.storageClass.create`; emits provisioner driver name, `clusterID`, image features, optional pool/dataPool, mounter, mkfs options, encryption, KMS ID, topology-constrained pools, map/unmap options, striping/object size, CSI secret references, fstype, reclaim policy, expansion, and mount options.

Control flow: Kubernetes dynamic provisioning uses this class; external-provisioner passes parameters to the RBD CSI controller and nodeplugin later stages with matching secret refs.

State and persistence behavior: StorageClass is cluster state; provisioned PVCs become PVs and Ceph RBD images in the configured pool.

Dependencies and integration points: requires `ceph-csi-config` cluster ID, Ceph pool, Ceph auth Secret, RBD image feature compatibility, and sidecar/controller deployment.

Risks: invalid image features or mounter options fail on specific nodes. Secret namespace defaults to release namespace, which may not match workloads. Topology pools require exact label/domain config.

Test signals: RBD PVC provisioning, mount, expansion, topology, encryption, and reclaim tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/values.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/values.yaml

Purpose: default values and operator-facing schema for the RBD Helm chart.

Important APIs/types/functions: key groups are `rbac`, `serviceAccounts`, `csiConfig`, `csiMapping`, `encryptionKMSConfig`, logging, `CSIDriver`, `nodeplugin`, `provisioner`, `topology`, `storageClass`, snapshot/group snapshot classes, `secret`, `cephconf`, `extraDeploy`, and internal socket/configmap names.

Control flow: templates consume values to render config maps, RBAC, service accounts, node DaemonSet, controller Deployment, metric Services, StorageClass, SnapshotClass, GroupSnapshotClass, and optional Secret.

State and persistence behavior: values materialize as Kubernetes objects and then drive persistent Ceph RBD images/snapshots/metadata. Runtime sockets and key directories are ephemeral; Secrets and ConfigMaps persist in Kubernetes.

Dependencies and integration points: integrates with Helm, Kubernetes CSI sidecars, Ceph RBD, KMS providers, Prometheus, CSI-Addons, kubelet paths, and external snapshot/group-snapshot APIs.

Risks: defaults are development-oriented (`canary`, placeholder cluster/secrets, verbose logging, storage class disabled). Many parameters are strings expected by CSI, so boolean-looking values such as `encrypted` must remain strings. Broad RBAC and privileged host access are inherent.

Test signals: Helm render/lint, chart install tests, and RBD e2e coverage for provisioning, expansion, snapshots, clones, encryption, topology, read affinity, and metrics.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-rbd/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/cmd/cephcsi.go -->
# sources/control-plane/ceph-csi/cmd/cephcsi.go

Purpose: main entrypoint for the `cephcsi` binary; parses CLI flags, validates configuration, writes Ceph config, and dispatches to RBD, CephFS, NFS, NVMe-oF, liveness, or controller mode.

Important APIs/types/functions: `init` registers flags into global `util.Config`; `getDriverName` selects defaults; `printVersion`; `main`; `setPIDLimit`; `initControllers`; `validateCloneDepthFlag`; `validateMaxSnapshotFlag`; `logAndExit`.

Control flow: `main` handles `--version`, initializes feature gates, requires `--type`, validates driver name, optionally runs `automaxprocs`, adjusts PID limits for node servers, validates metrics URL for profiling/liveness, writes Ceph config, then switches on `conf.Vtype` to run the selected driver/controller.

State and persistence behavior: process-global `conf` holds parsed runtime state. `util.WriteCephConfig` writes local Ceph client config. Controllers and drivers create external Kubernetes/Ceph state through their packages.

Dependencies and integration points: imports internal driver packages, controller packages, liveness, util/log, automaxprocs, klog, controller-runtime logging, and kernel version utility.

Risks: no default driver for unknown type; errors exit the process. RBD clone/snapshot thresholds are hard validated. Deprecated `--setmetadata` is still passed by manifests but logged as no-op. PID-limit changes are best-effort.

Test signals: unit tests likely cover validation helpers elsewhere; deployment/e2e manifests exercise mode selection and flag compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/cmd/cephcsi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy.sh -->
# sources/control-plane/ceph-csi/deploy.sh

Purpose: release automation script that builds/pushes multi-architecture Ceph-CSI images and publishes RBD/CephFS Helm charts to `ceph/csi-charts`.

Important APIs/types/functions: `build_push_images` inspects base-image manifests, runs qemu-user-static, builds `amd64`/`arm64` images via make, creates manifests, and pushes. `push_helm_charts` rewrites chart metadata for release branches, rsyncs chart content, packages with Helm, indexes the repo, commits, and pushes.

Control flow: requires `GITHUB_TOKEN`; builds images first; creates temp chart checkout; installs Helm from configured script/version; clones chart repo; pushes RBD then CephFS charts; removes temp dir.

State and persistence behavior: mutates Docker registry state, local temp checkout, chart files in that checkout, git history in `ceph/csi-charts`, and remote chart index. Does not commit in this source repo.

Dependencies and integration points: Docker manifest/build, jq, qemu-user-static, make targets, Helm installer, curl, git, rsync, build env, and GitHub token.

Risks: `sed` rewrites are branch/version-sensitive. Docker experimental manifest behavior and multiarch base digests can fail. Token in push URL must be protected. Temp cleanup is simple and not trap-based.

Test signals: release CI logs, image manifest inspection, Helm package/index validation, and chart repository publication.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/Makefile -->
# sources/control-plane/ceph-csi/deploy/Makefile

Purpose: regeneration entrypoint for generated deploy manifests under `deploy/`.

Important APIs/types/functions: `all` depends on SCC, CephFS/NFS/RBD CSIDriver and config-map manifests, plus NFS provisioner RBAC. Each target depends on source files under `api/deploy/...` and runs `$(MAKE) -C ../tools generate-deploy`.

Control flow: any stale target invokes the central yaml generator rather than editing deploy YAML directly.

State and persistence behavior: updates generated YAML files in the deploy tree through the tools generator.

Dependencies and integration points: depends on API deploy sources and the `tools` make target. Comments in generated YAML point maintainers back to this pipeline.

Risks: several deploy files in this subset are generated and should not be modified directly. Target coverage is selective; not every manifest listed here has an explicit Makefile target.

Test signals: generator diffs, CI checks for generated manifests, and `make -C deploy all`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/ceph-conf.yaml -->
# sources/control-plane/ceph-csi/deploy/ceph-conf.yaml

Purpose: static sample ConfigMap for Ceph client configuration consumed by CSI pods.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-config`; `data.ceph.conf` contains cephx auth requirements and commented debug logging options; `data.keyring` is intentionally empty but present.

Control flow: static deploy manifests mount this ConfigMap under `/etc/ceph/` for nodeplugin and provisioner pods.

State and persistence behavior: Kubernetes ConfigMap persists client configuration; no secrets are stored here.

Dependencies and integration points: consumed by RBD, CephFS, and provisioner deployments; pairs with `ceph-csi-config` and Secrets for full connectivity.

Risks: debug logging comments can be enabled and produce high-volume logs. Missing `keyring` can break clients even if empty content is expected.

Test signals: driver pod startup and Ceph client connection attempts validate the file.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/ceph-conf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephcsi/image/Dockerfile -->
# sources/control-plane/ceph-csi/deploy/cephcsi/image/Dockerfile

Purpose: multi-stage Dockerfile for building and packaging the `cephcsi` binary.

Important APIs/types/functions: stages are `updated_base`, `builder`, and final CentOS Stream 9 minimal image. Build args include source dir, Go arch, base images, CSI image name/version, Git commit, Go root, and Ceph version.

Control flow: updates Ceph base repos, installs NFS utilities, downloads architecture-specific Go, installs build deps and Ceph dev libraries, copies source, runs `make cephcsi`, then copies the binary into final image and installs runtime packages including Ceph clients, `rbd-nbd`, `ceph-fuse`, `cryptsetup`, `nvme-cli`, filesystems, and `kmod`.

State and persistence behavior: final image contains `/usr/local/bin/cephcsi` and runtime packages; no runtime cluster state.

Dependencies and integration points: relies on `build.env`, Ceph RPM repos, Go downloads, dnf/microdnf, CGO/Ceph libraries, and `make cephcsi`.

Risks: network package/download availability affects reproducibility. Dynamic library check catches missing libs but not runtime kernel/tool compatibility. Broad runtime package set increases image surface.

Test signals: image build CI, `ldd` check, binary startup, and deployment e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephcsi/image/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin-provisioner.yaml -->
# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin-provisioner.yaml

Purpose: static CephFS provisioner Service and Deployment manifest.

Important APIs/types/functions: Deployment has 3 replicas with anti-affinity, `cephfs-csi-provisioner` service account, main `csi-cephfsplugin --controllerserver=true`, external-provisioner, attacher, resizer, snapshotter with group snapshot feature, Ceph-CSI metadata controller, and liveness metrics sidecar on target port 8681.

Control flow: sidecars communicate with the CephFS controller over `unix:///csi/csi-provisioner.sock`, perform leader-elected Kubernetes storage operations, and expose metrics through the Service.

State and persistence behavior: ephemeral socket/key dirs; persistent state is Kubernetes PV/PVC/snapshot objects and CephFS subvolumes/snapshots/metadata.

Dependencies and integration points: mounts Ceph config, Ceph-CSI config, KMS config, host `/sys`, `/dev`, `/lib/modules`, and uses Kubernetes CSI sidecar images.

Risks: canary image defaults, hardcoded namespace/account names, and high timeout values are sample-oriented. Anti-affinity can block small clusters. KMS ConfigMap must exist even if empty.

Test signals: CephFS e2e provisioning, expansion, snapshots, metadata controller behavior, and metrics scrape.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin-provisioner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin.yaml -->
# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin.yaml

Purpose: static CephFS nodeplugin DaemonSet and metrics Service.

Important APIs/types/functions: privileged `csi-cephfsplugin --nodeserver=true`, driver registrar, liveness sidecar on 8681, host network/PID, kubelet plugin/pod hostPaths with bidirectional mount propagation, SELinux, modules, `/dev`, `/run/mount`, config/KMS mounts, and CephFS mountinfo hostPath.

Control flow: runs on every node, registers `cephfs.csi.ceph.com` with kubelet, mounts CephFS volumes using kernel or fuse mounters, and exposes liveness metrics.

State and persistence behavior: host plugin sockets, mount points, and mountinfo persist on nodes; keys are memory-backed.

Dependencies and integration points: kubelet plugin registry, Ceph config, cluster config, service account/RBAC, CephFS client tools, SELinux support, and metrics Service.

Risks: privileged host access and mount propagation are sensitive. Hardcoded `/var/lib/kubelet` and default namespace assumptions may not fit all clusters.

Test signals: DaemonSet readiness, kubelet registration, CephFS pod mount/unmount e2e, and metrics endpoints.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-config-map.yaml -->
# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-config-map.yaml

Purpose: generated empty Ceph-CSI cluster config ConfigMap for CephFS static deployments.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-csi-config` with `data.config.json: []`.

Control flow: operators replace or patch this list with cluster monitor information before driver use.

State and persistence behavior: Kubernetes ConfigMap; stores cluster connection metadata, not credentials.

Dependencies and integration points: mounted by CephFS nodeplugin/provisioner pods and generated from `api/deploy`.

Risks: empty default makes the deployment nonfunctional until configured. Direct edits may be overwritten by yamlgen.

Test signals: driver config loading and provisioning failures/successes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-config-map.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-nodeplugin-rbac.yaml -->
# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-nodeplugin-rbac.yaml

Purpose: static RBAC for CephFS nodeplugin.

Important APIs/types/functions: creates `cephfs-csi-nodeplugin` ServiceAccount in default namespace, ClusterRole with node read, secret get/list/watch, configmap get, serviceaccount get, and serviceaccounts/token create, plus ClusterRoleBinding.

Control flow: authorizes nodeplugin pods to read runtime config/secrets and create tokens for KMS flows.

State and persistence behavior: Kubernetes RBAC state only.

Dependencies and integration points: referenced by the CephFS DaemonSet serviceAccountName.

Risks: broad secret access and hardcoded default namespace require operator review. Static sample comments instruct namespace replacement but do not enforce it.

Test signals: nodeplugin authorization and mount/encryption e2e.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-nodeplugin-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-provisioner-rbac.yaml -->
# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-provisioner-rbac.yaml

Purpose: static RBAC for CephFS provisioner/controller sidecars.

Important APIs/types/functions: creates `cephfs-csi-provisioner` ServiceAccount, ClusterRole for nodes, secrets, events, PV/PVC/status, storageclasses, volumeattachments/status, CSINodes, snapshots/status/classes, group snapshots/status/classes, replication CRDs, configmaps, serviceaccounts, and token creation; also namespace Role/RoleBinding for configmaps and leases.

Control flow: supports provisioning, attaching, resizing, snapshotting, group snapshots, replication integration, and leader election.

State and persistence behavior: RBAC objects authorize controllers that mutate Kubernetes storage state.

Dependencies and integration points: used by CephFS provisioner Deployment and external sidecars.

Risks: broad storage and secret privileges; hardcoded default namespace must be customized. Permissions must match enabled sidecars and CRDs.

Test signals: CephFS storage workflows and sidecar authorization logs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csi-provisioner-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csidriver.yaml -->
# sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csidriver.yaml

Purpose: generated `CSIDriver` object for CephFS.

Important APIs/types/functions: name `cephfs.csi.ceph.com`; `attachRequired: true`, `podInfoOnMount: true`, `fsGroupPolicy: File`, `seLinuxMount: true`.

Control flow: Kubernetes uses it to advertise driver capabilities and pod-info requirements to kubelet/CSI.

State and persistence behavior: cluster-scoped API object only.

Dependencies and integration points: must match CephFS StorageClasses and driver flags.

Risks: direct edits are overwritten by yamlgen. Driver-name mismatch prevents provisioning/mounts from resolving.

Test signals: Kubernetes CSI discovery and CephFS e2e mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/cephfs/kubernetes/csidriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/csi-config-map-sample.yaml -->
# sources/control-plane/ceph-csi/deploy/csi-config-map-sample.yaml

Purpose: annotated sample `ceph-csi-config` ConfigMap showing cluster config and cluster-mapping JSON shapes.

Important APIs/types/functions: documents `clusterID`, `monitors`, RBD options (`netNamespaceFilePath`, `radosNamespace`, `mirrorDaemonCount`, node-publish secret), CephFS options (`subvolumeGroup`, mount options, rados namespace), NFS namespace path, read affinity labels, and DR mappings for cluster IDs, RBD pool IDs, and CephFS FSC IDs.

Control flow: operators copy/modify this data for real deployments; driver pods read it from mounted ConfigMap.

State and persistence behavior: sample only, but when applied it persists cluster connection metadata in Kubernetes.

Dependencies and integration points: StorageClass/SnapshotClass `clusterID` must match entries here; read-affinity and network namespace settings affect node operations.

Risks: sample JSON contains placeholders and illustrative ellipses, so it is not directly valid production JSON as-is. Adding rados namespaces to active configs can break existing volume metadata lookup.

Test signals: config parsing and provisioning/mount workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/csi-config-map-sample.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-config-map.yaml -->
# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-config-map.yaml

Purpose: generated empty Ceph-CSI config ConfigMap for NFS deployments.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-csi-config`, `config.json: []`.

Control flow: NFS driver pods mount this and expect operators to populate cluster entries including NFS network namespace config when needed.

State and persistence behavior: Kubernetes ConfigMap state only.

Dependencies and integration points: mounted by NFS provisioner and nodeplugin manifests.

Risks: empty default prevents functional provisioning/mounts. Generated file should be changed at source rather than edited here.

Test signals: NFS CSI driver startup and provisioning tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-config-map.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nfsplugin-provisioner.yaml -->
# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nfsplugin-provisioner.yaml

Purpose: static NFS provisioner Service and Deployment.

Important APIs/types/functions: 3-replica Deployment with anti-affinity, main `csi-nfsplugin --controllerserver=true`, external-provisioner, attacher, resizer, snapshotter, liveness sidecar on 8682, and `nfs-csi-provisioner` service account.

Control flow: sidecars call the NFS CSI controller over `csi-provisioner.sock`, perform leader-elected Kubernetes storage operations, and expose metrics through the Service.

State and persistence behavior: ephemeral socket/key dirs; persistent state is Kubernetes storage objects and backend NFS/Ceph state managed by the driver.

Dependencies and integration points: `ceph-csi-config`, host `/sys`, CSI sidecars, Kubernetes RBAC, and `cephcsi --type=nfs`.

Risks: canary images and hardcoded defaults are sample-oriented. NFS manifest lacks Ceph config/KMS mounts used by RBD/CephFS because the integration surface is narrower.

Test signals: NFS provisioning, attach/resizer/snapshot sidecar behavior, and metrics.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nfsplugin-provisioner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nfsplugin.yaml -->
# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nfsplugin.yaml

Purpose: static NFS nodeplugin DaemonSet.

Important APIs/types/functions: privileged `csi-nfsplugin --nodeserver=true`, driver registrar, host network/PID, kubelet plugin and pod mount hostPaths with bidirectional propagation, `/dev`, `/sys`, `/run/mount`, SELinux, modules, Ceph config, Ceph-CSI config, and memory key dir.

Control flow: runs on each node, registers `nfs.csi.ceph.com` with kubelet, and performs node-stage/publish mounts through the CSI socket.

State and persistence behavior: host plugin sockets and pod mounts persist on node; key dir is ephemeral.

Dependencies and integration points: kubelet registration, NFS client tooling in image, config maps, nodeplugin RBAC, and host mount namespace.

Risks: privileged host access is broad. Hardcoded `/var/lib/kubelet` and default namespace assumptions may need customization.

Test signals: kubelet CSI registration and NFS volume mount e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nfsplugin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nodeplugin-rbac.yaml -->
# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nodeplugin-rbac.yaml

Purpose: minimal static ServiceAccount manifest for the NFS nodeplugin.

Important APIs/types/functions: creates `ServiceAccount` named `nfs-csi-nodeplugin`; no ClusterRole or binding appears in this file.

Control flow: the NFS node DaemonSet references this account, relying on limited or separately managed permissions.

State and persistence behavior: namespace-scoped identity object only.

Dependencies and integration points: consumed by `csi-nfsplugin.yaml`.

Risks: if nodeplugin later needs API access, this file alone is insufficient. Namespace is implicit, unlike many other static manifests.

Test signals: pod admission and any API authorization failures in nodeplugin logs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-nodeplugin-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-provisioner-rbac.yaml -->
# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-provisioner-rbac.yaml

Purpose: generated RBAC for the NFS provisioner.

Important APIs/types/functions: creates `nfs-csi-provisioner` ServiceAccount, ClusterRole for nodes, secrets, events, PV/PVC/status, storageclasses, volumeattachments/status, CSINodes, snapshot resources/classes/content/status, volumeattributesclasses, and namespace Role/RoleBinding for configmaps and leases.

Control flow: authorizes external sidecars to provision, attach, resize, snapshot, and lead-elect NFS CSI operations.

State and persistence behavior: RBAC objects only; authorized controllers mutate Kubernetes storage resources.

Dependencies and integration points: used by NFS provisioner Deployment and CSI sidecars.

Risks: generated and should be changed at source. The Role keeps legacy configmap create/delete support. Hardcoded default namespace must be adjusted.

Test signals: NFS provisioner sidecar authorization and storage e2e.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csi-provisioner-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csidriver.yaml -->
# sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csidriver.yaml

Purpose: generated `CSIDriver` object for NFS.

Important APIs/types/functions: name `nfs.csi.ceph.com`; `attachRequired`, `podInfoOnMount`, `fsGroupPolicy: File`, `seLinuxMount: true`, and `volumeLifecycleModes: Persistent`.

Control flow: Kubernetes discovers NFS CSI capabilities and uses pod-info/fsgroup settings during mounts.

State and persistence behavior: cluster-scoped Kubernetes object only.

Dependencies and integration points: must match NFS driver flags and StorageClass provisioner.

Risks: direct edits are overwritten by yamlgen. Lifecycle modes limit the object to persistent volumes.

Test signals: NFS CSI discovery and mount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nfs/kubernetes/csidriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-config-map.yaml -->
# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-config-map.yaml

Purpose: empty Ceph-CSI cluster config ConfigMap for NVMe-oF deployments.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-csi-config` with `config.json: []`.

Control flow: NVMe-oF pods mount it and require real cluster/gateway configuration before use.

State and persistence behavior: Kubernetes ConfigMap state.

Dependencies and integration points: mounted by NVMe-oF node and provisioner manifests.

Risks: empty default is nonfunctional. Unlike generated files with comments, this file has no "do not modify" header, so ownership may be less obvious.

Test signals: NVMe-oF driver config loading and provisioning/mount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-config-map.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nodeplugin-rbac.yaml -->
# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nodeplugin-rbac.yaml

Purpose: RBAC for NVMe-oF nodeplugin.

Important APIs/types/functions: creates `ceph-nvmeof-nodeplugin` ServiceAccount, ClusterRole for node read, secret get, configmap get, serviceaccount get, PV get, volumeattachment list/get, and serviceaccounts/token create, plus ClusterRoleBinding.

Control flow: authorizes nodeplugin access to configuration, credentials/tokens, and storage object metadata during node operations.

State and persistence behavior: Kubernetes RBAC state only.

Dependencies and integration points: referenced by NVMe-oF DaemonSet and SCC.

Risks: namespace defaults to `default`; secret access is narrower than RBD/CephFS but still sensitive. Binding name and service account must match DaemonSet.

Test signals: NVMe-oF node staging/publish and KMS/token authorization behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nodeplugin-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nodeplugin-scc.yaml -->
# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nodeplugin-scc.yaml

Purpose: OpenShift `SecurityContextConstraints` for the NVMe-oF nodeplugin.

Important APIs/types/functions: allows privileged containers, `SYS_ADMIN`, hostDir volumes, host IPC/network/PID, hostPath/configMap/projected/emptyDir volumes, runAsAny, seLinux RunAsAny, and grants to `system:serviceaccount:default:ceph-nvmeof-nodeplugin`.

Control flow: OpenShift admission uses this SCC to permit the privileged DaemonSet that loads NVMe/kernel functionality and mounts volumes.

State and persistence behavior: cluster security policy object.

Dependencies and integration points: tied to the nodeplugin service account and OpenShift SCC admission.

Risks: high privilege policy with default namespace baked in. The comment says "ssc" but means SCC. Must be carefully scoped in multi-tenant clusters.

Test signals: OpenShift pod admission and NVMe-oF nodeplugin rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nodeplugin-scc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nvmeofplugin-provisioner.yaml -->
# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nvmeofplugin-provisioner.yaml

Purpose: static NVMe-oF controller/provisioner Deployment.

Important APIs/types/functions: single replica, `nvmeof-csi-provisioner` service account, main `csi-nvmeofplugin --controllerserver=true`, external-provisioner, resizer, attacher, and projected KMS token; main plugin drops all capabilities and is not privileged.

Control flow: sidecars communicate over `unix:///csi/csi-provisioner.sock`, perform leader-elected Kubernetes storage operations, and call the NVMe-oF CSI controller.

State and persistence behavior: ephemeral socket and key dirs; persistent state is Kubernetes storage API objects and Ceph/NVMe-oF backend state.

Dependencies and integration points: Ceph config, Ceph-CSI config, RBAC, OpenShift annotation, KMS token projection, and sidecar images.

Risks: no liveness Service/sidecar in this manifest unlike RBD/CephFS/NFS static provisioners. Single replica reduces HA. Hardcoded default namespace and canary image are sample-oriented.

Test signals: NVMe-oF provisioning, expansion, attach, and controller rollout tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nvmeofplugin-provisioner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nvmeofplugin.yaml -->
# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nvmeofplugin.yaml

Purpose: static NVMe-oF nodeplugin DaemonSet.

Important APIs/types/functions: privileged `csi-nvmeofplugin --nodeserver=true`, node id composed as `$(NODE_ID)::nqn.2025-08.io.ceph:$(NODE_ID)`, CSI-Addons endpoint, registrar, host network/PID, OpenShift storage-node toleration, hostPaths for `/dev`, `/sys`, `/run/mount`, modules, kubelet plugins/pods, SELinux, projected KMS token, and host log directory.

Control flow: runs on eligible nodes, registers `nvmeof.csi.ceph.com`, performs NVMe-oF node operations with host devices/modules, and writes plugin logs to a hostPath.

State and persistence behavior: host plugin socket, kubelet mounts, and `/var/lib/cephcsi/csi-nvmeofplugin` logs persist on node; keys are memory-backed.

Dependencies and integration points: kubelet, NVMe tooling/kernel modules, CSI-Addons, OpenShift SCC/RBAC, logrotate config volume reference, and cluster config.

Risks: references `nvmeof.csi.ceph.com-logrotate-config` volume but no mount appears in the container section in this file, which may indicate incomplete logrotate integration. Hardcoded NQN format and storage-node toleration are environment-specific.

Test signals: DaemonSet rollout, registrar registration, NVMe-oF attach/mount e2e, and log path validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nvmeofplugin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-provisioner-rbac.yaml -->
# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-provisioner-rbac.yaml

Purpose: RBAC for NVMe-oF provisioner/controller sidecars.

Important APIs/types/functions: creates `nvmeof-csi-provisioner` ServiceAccount, ClusterRole for nodes, secrets, events, PV/PVC/status, storageclasses, volumeattachments/status, CSINodes, volumeattributesclasses, snapshots/status/classes, group snapshots/status/classes, replication CRDs, configmaps, serviceaccounts, and serviceaccount token creation; Role/RoleBinding for configmaps and leases.

Control flow: authorizes external-provisioner/resizer/attacher/snapshot-capable workflows and leader election.

State and persistence behavior: Kubernetes RBAC only.

Dependencies and integration points: bound to NVMe-oF provisioner Deployment service account.

Risks: broad permissions with default namespace references. Snapshot/group-snapshot permissions exist even though the static NVMe-oF provisioner manifest does not run snapshotter.

Test signals: sidecar authorization, provisioning/expansion/attachment workflows, and RBAC review.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-provisioner-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-provisioner-scc.yaml -->
# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-provisioner-scc.yaml

Purpose: OpenShift SCC for the NVMe-oF provisioner.

Important APIs/types/functions: allows configMap/projected/emptyDir volumes, runAsAny, seLinux RunAsAny, not read-only root filesystem, drops all capabilities, and grants the `default:nvmeof-csi-provisioner` service account.

Control flow: OpenShift admission uses it for provisioner pods that do not require the nodeplugin's host privileges.

State and persistence behavior: cluster security policy state.

Dependencies and integration points: tied to `nvmeof-csi-provisioner` service account and OpenShift.

Risks: default namespace hardcoding. The SCC is permissive for user/SELinux but far less privileged than the nodeplugin SCC.

Test signals: OpenShift provisioner pod admission and rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-provisioner-scc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csidriver.yaml -->
# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csidriver.yaml

Purpose: `CSIDriver` object for NVMe-oF.

Important APIs/types/functions: name `nvmeof.csi.ceph.com`; sets `attachRequired`, `podInfoOnMount`, `seLinuxMount`, and `fsGroupPolicy: File`.

Control flow: Kubernetes uses it to discover the NVMe-oF CSI driver's attach and mount behavior.

State and persistence behavior: cluster-scoped Kubernetes object only.

Dependencies and integration points: must match NVMe-oF driver flags and StorageClass provisioner.

Risks: driver name mismatch breaks provisioning and kubelet registration.

Test signals: Kubernetes CSI discovery, attachment, and node publish tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csidriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-config-map.yaml -->
# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-config-map.yaml

Purpose: generated empty Ceph-CSI config ConfigMap for RBD deployments.

Important APIs/types/functions: `v1/ConfigMap` named `ceph-csi-config`, `config.json: []`.

Control flow: RBD pods mount it and require real cluster monitor/config entries before use.

State and persistence behavior: Kubernetes ConfigMap state.

Dependencies and integration points: mounted by RBD nodeplugin and provisioner manifests.

Risks: empty default is nonfunctional; generated file should be changed through `api/deploy` sources.

Test signals: RBD driver config loading and provisioning/mount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-config-map.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-nodeplugin-rbac.yaml -->
# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-nodeplugin-rbac.yaml

Purpose: static RBAC for the RBD nodeplugin.

Important APIs/types/functions: creates `rbd-csi-nodeplugin` ServiceAccount in default namespace, ClusterRole for node read, secret get/list/watch, configmap get, serviceaccount get, PV get, volumeattachment list/get, and token creation; binds it with ClusterRoleBinding.

Control flow: authorizes nodeplugin API calls for topology, config, KMS/secret access, PV/attachment lookup, and service account token projection.

State and persistence behavior: Kubernetes RBAC state only.

Dependencies and integration points: referenced by RBD DaemonSet and KMS/encryption flows.

Risks: broad secret access and hardcoded default namespace. Namespace comments rely on manual replacement.

Test signals: RBD node stage/publish, encryption, and authorization logs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-nodeplugin-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-provisioner-rbac.yaml -->
# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-provisioner-rbac.yaml

Purpose: static RBAC for RBD provisioner/controller sidecars.

Important APIs/types/functions: creates `rbd-csi-provisioner`, ClusterRole for nodes, secrets, events, PV/PVC/status, storageclasses, snapshots/status/classes/content, volumeattachments/status, CSINodes, group snapshots/status/classes, replication CRDs, volumeattributesclasses, configmaps, serviceaccounts, and token creation; plus namespace Role/RoleBinding for configmaps and leases.

Control flow: authorizes dynamic provisioning, resizing, attachment, snapshots, group snapshots, DR metadata, leader election, and sidecar state updates.

State and persistence behavior: RBAC objects authorize mutation of Kubernetes storage API state.

Dependencies and integration points: used by `csi-rbdplugin-provisioner.yaml`.

Risks: broad storage and secret permissions; namespace defaults must be customized. Permission set must track enabled sidecars/features.

Test signals: RBD e2e provisioning, snapshot, resize, attach, replication, and group snapshot tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-provisioner-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-rbdplugin-provisioner.yaml -->
# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-rbdplugin-provisioner.yaml

Purpose: static RBD provisioner Service and Deployment.

Important APIs/types/functions: 3-replica Deployment with main `csi-rbdplugin --controllerserver=true`, CSI-Addons endpoint, clone-depth flags, external-provisioner, snapshotter, attacher, resizer, metadata controller, liveness sidecar on 8680, KMS ConfigMap, Ceph config, and projected OIDC token.

Control flow: sidecars communicate with the RBD controller socket, perform leader-elected Kubernetes storage operations, and expose liveness metrics through the Service.

State and persistence behavior: ephemeral socket/key dirs; persistent state includes Kubernetes PV/PVC/snapshot/attachment objects, Ceph RBD images/snapshots, OMAP metadata, and optional KMS-backed encryption data.

Dependencies and integration points: RBD provisioner RBAC, Ceph config, Ceph-CSI config, KMS config, host `/dev`/`sys`/modules, CSI sidecars, and CSI-Addons.

Risks: canary image and default namespace are sample values. Host device access in controller pods is sensitive. Snapshotter group snapshot feature is enabled in static manifest, so CRDs/RBAC must exist.

Test signals: RBD provisioning, clone, snapshot/group-snapshot, expansion, metrics, and encryption tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-rbdplugin-provisioner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-rbdplugin.yaml -->
# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-rbdplugin.yaml

Purpose: static RBD nodeplugin DaemonSet and metrics Service.

Important APIs/types/functions: privileged `csi-rbdplugin --nodeserver=true`, kubelet plugin/staging paths, CSI-Addons endpoint, registrar, liveness sidecar on 8680, host network/PID, `/dev`, `/sys`, `/run/mount`, SELinux, modules, kubelet plugin/pod hostPaths, Ceph log hostPath, KMS config, and projected OIDC token.

Control flow: registers `rbd.csi.ceph.com` with kubelet, maps/unmaps RBD devices, stages/publishes volumes with mount propagation, and exposes metrics.

State and persistence behavior: host plugin socket, mapped devices, mountpoints, and Ceph logs persist on node; keys are memory-backed.

Dependencies and integration points: kubelet, Ceph kernel/rbd-nbd tooling, KMS, config maps, node RBAC, and CSI-Addons.

Risks: privileged host access is required and high risk. Hardcoded kubelet path/default namespace may not fit all installs. Read-affinity/topology options are commented and require careful label alignment.

Test signals: RBD node mount/unmount, encryption, CSI registration, read affinity, and metrics tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csi-rbdplugin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csidriver.yaml -->
# sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csidriver.yaml

Purpose: generated RBD `CSIDriver` object.

Important APIs/types/functions: name `rbd.csi.ceph.com`; `attachRequired: true`, `podInfoOnMount: true`, `seLinuxMount: true`, `fsGroupPolicy: File`.

Control flow: Kubernetes discovers driver capabilities and passes pod info for mount operations.

State and persistence behavior: cluster-scoped object only.

Dependencies and integration points: must match RBD StorageClass provisioner and driver flags.

Risks: direct edits are overwritten by yamlgen. Driver-name mismatch breaks storage class resolution and kubelet registration.

Test signals: RBD CSI discovery, attachment, and pod mount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/rbd/kubernetes/csidriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/scc.yaml -->
# sources/control-plane/ceph-csi/deploy/scc.yaml

Purpose: generated OpenShift `SecurityContextConstraints` for Ceph-CSI service accounts.

Important APIs/types/functions: SCC `ceph-csi` allows privileged containers, host network/PID/IPC, hostPath volumes, host ports, `SYS_ADMIN`, non-read-only root FS, runAsAny, seLinux RunAsAny, fsGroup/supplementalGroups RunAsAny, and configMap/projected/emptyDir/hostPath volumes. It grants RBD, CephFS, NFS, and NVMe-oF node/provisioner service accounts in `ceph-csi` namespace.

Control flow: OpenShift admission uses this SCC to permit CSI pods that require host access.

State and persistence behavior: cluster security policy state.

Dependencies and integration points: service account names/namespaces must match deployed manifests.

Risks: highly privileged policy. Namespace/service account mismatch prevents pod admission, while overbroad grants increase cluster risk.

Test signals: OpenShift deployment admission and CSI pod rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/scc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/service-monitor.yaml -->
# sources/control-plane/ceph-csi/deploy/service-monitor.yaml

Purpose: sample Prometheus Operator `ServiceMonitor` for Ceph-CSI metrics.

Important APIs/types/functions: `monitoring.coreos.com/v1 ServiceMonitor` named `csi-metrics` in `rook-ceph`, label `team: rook`, selects Services with `app: csi-metrics` in namespace `default`, scraping `http-metrics` path `/metrics` every 5s.

Control flow: Prometheus Operator reconciles this object into scrape configuration for matching metrics Services.

State and persistence behavior: monitoring API object; no CSI runtime state.

Dependencies and integration points: requires Prometheus Operator CRD and Services from static manifests.

Risks: namespace and labels are examples and often need changes. Frequent 5s interval may be too aggressive in larger clusters.

Test signals: ServiceMonitor admission, Prometheus target discovery, and metrics availability.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/deploy/service-monitor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/ceph.go -->
# sources/control-plane/ceph-csi/e2e/ceph.go

Purpose: e2e helper for parsing and comparing Ceph cluster versions.

Important APIs/types/functions: predefined major-version sentinels `CephVersionSquid`, `Tentacle`, and `Umbrella`; `cephVersion` fields and accessors; `String`; `UnmarshalJSON`; `GreaterEquals`; `getCephVersion`.

Control flow: `getCephVersion` runs `ceph --format=json version` in the toolbox pod, unmarshals the `version` string into `cephVersion`, and tests can gate behavior with `GreaterEquals`.

State and persistence behavior: no persistence; state is parsed version data returned to tests.

Dependencies and integration points: depends on e2e framework, `execCommandInToolBoxPod`, `rookNamespace`, Ceph CLI JSON output, and Go JSON unmarshalling.

Risks: parser assumes strings beginning `ceph version` with at least five space-separated parts and release at index 4. Future Ceph format changes can break tests.

Test signals: direct unit tests in `ceph_test.go` cover parse errors and comparisons.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/ceph.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/ceph_test.go -->
# sources/control-plane/ceph-csi/e2e/ceph_test.go

Purpose: unit tests for the Ceph version helper used by e2e tests.

Important APIs/types/functions: `TestCephVersionUnmarshalJSON` table-tests valid Squid string, invalid prefix, too few version numbers, invalid numeric major, missing build ID, and missing release name. `TestCephVersionGreaterEquals` table-tests major/minor/patch ordering and Reef/Squid comparisons.

Control flow: tests run in parallel at both top level and subtest level, instantiate `cephVersion`, call `UnmarshalJSON` or `GreaterEquals`, and compare fields/booleans.

State and persistence behavior: no external state.

Dependencies and integration points: standard Go testing package and helpers from `ceph.go`.

Risks: typo in error text (`expecred`) is cosmetic. Tests call `UnmarshalJSON` with unquoted strings, matching the implementation's trim behavior but not exact `encoding/json` invocation shape.

Test signals: provides direct coverage for version parsing and comparison edge cases.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/ceph_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/ceph_user.go -->
# sources/control-plane/ceph-csi/e2e/ceph_user.go

Purpose: e2e helpers for creating/deleting Ceph auth users and building least-capability strings for RBD and CephFS test users.

Important APIs/types/functions: constants for RBD/CephFS user and Kubernetes Secret names; `rbdNodePluginCaps`, `rbdProvisionerCaps`, `cephFSNodePluginCaps`, `cephFSProvisionerCaps`, `createCephUser`, and `deleteCephUser`.

Control flow: tests build caps based on pool/namespace, run `ceph auth get-or-create-key client.<user> ...` in the toolbox pod, trim returned key text, and later delete with `ceph auth del`.

State and persistence behavior: creates and deletes real Ceph auth entities in the test cluster. Kubernetes Secrets are referenced by constants but managed elsewhere.

Dependencies and integration points: depends on toolbox exec helper, `rookNamespace`, Ceph auth CLI, and capability recommendations from Ceph-CSI docs.

Risks: command construction joins capability strings into shell command text; inputs should remain controlled test values. Failed cleanup leaves test users in the cluster.

Test signals: indirectly exercised by e2e setup/teardown that provisions with dedicated Ceph users.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/e2e/ceph_user.go -->
