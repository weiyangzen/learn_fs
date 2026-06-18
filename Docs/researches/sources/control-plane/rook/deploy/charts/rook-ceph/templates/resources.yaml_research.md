# Research: sources/control-plane/rook/deploy/charts/rook-ceph/templates/resources.yaml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000425`: lines 1-4554, `Docs/researches/chunks/subset-b-000425_research.md`
- `subset-b-000426`: lines 4555-9184, `Docs/researches/chunks/subset-b-000426_research.md`
- `subset-b-000427`: lines 9185-13982, `Docs/researches/chunks/subset-b-000427_research.md`
- `subset-b-000428`: lines 13983-17025, `Docs/researches/chunks/subset-b-000428_research.md`

## Chunk Research

### subset-b-000425: lines 1-4554

# sources/control-plane/rook/deploy/charts/rook-ceph/templates/resources.yaml lines 1-4554

## Scope

This chunk covers the first 4,554 lines of the Rook Ceph Helm chart's `templates/resources.yaml`. The file is a large generated CRD manifest template gated by `{{- if .Values.crds.enabled -}}`. When the chart value `crds.enabled` is true, Helm emits Kubernetes `apiextensions.k8s.io/v1` `CustomResourceDefinition` objects for Rook Ceph APIs. Every CRD in this range is annotated with `controller-gen.kubebuilder.io/version: v0.19.0` and `helm.sh/resource-policy: keep`, so Helm installs the CRDs but does not delete them automatically on chart uninstall.

The assigned range contains complete CRDs for:

- `CephBlockPoolRadosNamespace` (`cephblockpoolradosnamespaces.ceph.rook.io`), lines 2-350.
- `CephBlockPool` (`cephblockpools.ceph.rook.io`), lines 351-895.
- `CephBucketNotification` (`cephbucketnotifications.ceph.rook.io`), lines 896-1091.
- `CephBucketTopic` (`cephbuckettopics.ceph.rook.io`), lines 1092-1327.
- `CephClient` (`cephclients.ceph.rook.io`), lines 1328-1479.
- The beginning and large middle portion of `CephCluster` (`cephclusters.ceph.rook.io`), lines 1480-4554.

The range ends inside the `CephCluster.spec.storage.storageClassDeviceSets[].placement.podAffinity` schema. The rest of the `CephCluster` CRD and subsequent CRDs are outside this chunk and must be handled by later chunk research.

## Purpose

This template is the chart-distributed API surface for Rook's Ceph controllers. It teaches the Kubernetes API server which custom resources exist, which versions are served and stored, which schema validation rules apply, which fields are visible in `kubectl get`, and which resources expose the `status` subresource.

The file has no Go functions or application control flow of its own. Its operational purpose is declarative:

- Register Rook Ceph CRDs under the `ceph.rook.io` API group.
- Enforce OpenAPI v3 schemas for user-created Rook objects before they reach the operator.
- Preserve or reject fields using Kubernetes structural schema behavior, including `x-kubernetes-preserve-unknown-fields`, `x-kubernetes-int-or-string`, list/map type hints, and CEL validations.
- Expose status updates through `subresources.status` so controllers can update observed state separately from desired spec.
- Keep CRDs after Helm release removal to avoid deleting all custom resources and their cluster state accidentally.

Because CRDs are a cluster-level contract, this file is an integration boundary between Helm, the Kubernetes API server, Rook's Go controllers, Ceph daemons, Ceph CSI components, object storage integrations, and users applying Rook CRs.

## Important APIs, Types, And Fields

All CRDs in this chunk are namespaced, use `versions[].name: v1`, and set both `served: true` and `storage: true`. They require `metadata` and `spec` at the top-level object schema and expose `status: {}` as a subresource.

`CephBlockPoolRadosNamespace` defines RADOS namespaces within a Ceph block pool. Important spec fields are:

- `blockPoolName`, required and immutable, names the parent `CephBlockPool`.
- `clusterID`, optional, constrained to 1-36 characters matching `^[a-zA-Z0-9_-]+$`, and immutable.
- `name`, optional and immutable, allows the Ceph namespace name to differ from the CR name.
- `mirroring.mode`, `remoteNamespace`, and `snapshotSchedules` configure RBD mirroring and scheduled snapshots.

Its status includes generic Rook `conditions`, `phase`, arbitrary `info`, generated or reconciled mirroring details, mirroring health summaries, and snapshot schedule status. The status schema preserves unknown fields, which allows controller-side status evolution without immediate schema breakage.

`CephBlockPool` defines Ceph storage pools. Its schema exposes both replicated and erasure-coded pool options:

- `replicated.size` is required within the replicated block and controls replica count. Related fields include `requireSafeReplicaSize`, `replicasPerFailureDomain`, `subFailureDomain`, `targetSizeRatio`, and `hybridStorage` primary/secondary device classes.
- `erasureCoded.dataChunks` and `codingChunks` are required within the erasure-coded block. `algorithm` is limited to `isa` or `jerasure`; `stripeUnit` is an int-or-string constrained to selected values and a Kubernetes quantity-like pattern.
- Pool topology and behavior fields include `failureDomain`, `crushRoot`, `deviceClass`, `enableCrushUpdates`, `enableRBDStats`, `application`, `parameters`, and quotas.
- Mirroring includes `enabled`, `mode` (`pool`, `image`, or `init-only`), peer secret references, snapshot schedules, and status-check health settings.
- The optional `name` field is constrained to `.rgw.root`, `.nfs`, or `.mgr`, indicating this override is for special-purpose Ceph pools rather than arbitrary pool names.

`CephBlockPool` status persists `cephx.peerToken` key generation state, mirror status and info, snapshot schedule status, `poolID`, `observedGeneration`, `phase`, and arbitrary `info`. This lets Rook report both Kubernetes reconcile progress and Ceph-side pool state.

`CephBucketNotification` defines bucket notification rules. Its spec requires `topic`, and optionally includes `events` and `filter`. Event values are enumerated S3/RGW notification event names such as object create, remove, lifecycle, sync, replication, and restore events. Filters support object key filters by `prefix`, `suffix`, or `regex`, plus metadata and tag filters. Status records `conditions`, `observedGeneration`, and `phase`.

`CephBucketTopic` defines RGW notification topics. It requires `endpoint`, `objectStoreName`, and `objectStoreNamespace`. Endpoint schema supports:

- `http.uri`, `disableVerifySSL`, and `sendCloudEvents`.
- `amqp.uri`, `exchange`, `ackLevel` (`none`, `broker`, or `routeable`), and SSL verification control.
- `kafka.uri`, `ackLevel`, `mechanism`, SSL control, and username/password `SecretKeySelector` references.

It also supports `opaqueData` and `persistent`. Status exposes the generated topic `ARN`, `phase`, `observedGeneration`, and referenced `secrets` object identities.

`CephClient` defines CephX clients. Its spec requires `caps`, a map of subsystem capability strings, and supports optional `name`, immutable `secretName`, `removeSecret`, and `security.cephx` key rotation configuration. Status records CephX key version/generation, arbitrary `info`, `observedGeneration`, and `phase`.

`CephCluster` is the main Rook cluster API. The portion in this chunk includes printer columns for `dataDirHostPath`, monitor count, phase, status message, Ceph health, external mode, and FSID. Its spec fields covered here include:

- Metadata injection: `annotations`, `labels`, `placement`, `priorityClassNames`, and `resources` maps keyed by daemon/component.
- Ceph configuration: `cephConfig`, `cephConfigFromSecret`, and `cephVersion` with image and pull policy.
- Destructive or operational policies: `cleanupPolicy`, `continueUpgradeAfterChecksEvenIfNotHealthy`, `skipUpgradeChecks`, `removeOSDsIfOutAndSafeToRemove`, and storage migration confirmation.
- Daemon features: `crashCollector`, `dashboard`, `logCollector`, `mgr`, `mon`, `monitoring`, health checks, liveness probes, and startup probes.
- Cluster modes and networking: `external`, `network.hostNetwork`, `network.provider`, Multus selectors, address ranges, dual-stack, IP family, msgr2 requirements, compression/encryption, and multi-cluster services.
- Security: CephX key rotation policies for CSI, daemon keys, and RBD mirror peer tokens; OSD disk encryption key rotation; and KMS connection details.
- Storage selection and OSD orchestration: `storage.allowDeviceClassUpdate`, `allowOsdCrushWeightUpdate`, near/full/backfill ratios, device and path filters, explicit `devices`, per-node storage settings, PVC templates, `osdMaxUpdatesInParallel`, `scheduleAlways`, and the beginning of `storageClassDeviceSets`.

The `CephCluster` schema embeds large Kubernetes core API schemas for probes, affinities, tolerations, topology spread constraints, `ResourceRequirements`, `PersistentVolumeClaim` templates, endpoint addresses, and secret selectors. These embedded schemas are important because Rook CRs pass Kubernetes-native scheduling, storage, and health-probe configuration through to generated Deployments, StatefulSets, Jobs, Pods, Services, and PVCs.

## Control Flow

The effective control flow starts before Kubernetes reconciliation:

1. Helm evaluates `{{- if .Values.crds.enabled -}}`.
2. If enabled, Helm renders this section into YAML CRD resources.
3. Kubernetes stores each CRD and begins serving `ceph.rook.io/v1` APIs.
4. Users or other chart templates create Rook custom resources that must satisfy these schemas.
5. The API server validates required fields, enum values, numeric ranges, regex patterns, immutability CEL rules, and structural list/map hints.
6. Rook controllers watch these custom resources, reconcile corresponding Ceph state, and update `status` through the status subresource.
7. `kubectl get` and other clients use `additionalPrinterColumns` to show selected spec/status values.

There is no imperative branching beyond Helm's single `crds.enabled` guard in this range. The "flow" inside each CRD is schema-driven admission behavior. For example, changing `CephCluster.spec.dataDirHostPath`, `CephBlockPoolRadosNamespace.spec.blockPoolName`, `CephBlockPoolRadosNamespace.spec.clusterID`, `CephBlockPoolRadosNamespace.spec.name`, or `CephClient.spec.secretName` is blocked by CEL immutability rules after initial creation.

Several fields also guide later controller control flow. Pool mirroring fields determine whether Rook configures rbd-mirror and snapshot schedules. Bucket topic and notification specs determine RGW notification setup. `CephCluster.spec.external.enable` suppresses local creation of mon, mgr, osd, mds, and discovery daemons. `CephCluster.spec.network.provider` affects mon failover behavior and network attachment use. Storage fields drive OSD provisioning from raw devices, host paths, PVC templates, and storage class device sets.

## State And Persistence Behavior

The CRDs themselves are persistent cluster API definitions. The `helm.sh/resource-policy: keep` annotation means Helm should leave them installed even when the chart release is removed, preserving the API definitions and avoiding accidental deletion cascades of existing custom resources.

The custom resources defined here persist desired state in `spec` and observed state in `status`:

- Desired state includes Ceph pool layouts, RADOS namespace mirroring, bucket notification routing, Ceph client caps, cluster daemon images, monitor topology, networking, health probes, scheduling policy, security policy, and storage provisioning policy.
- Status state includes phases, conditions, observed generations, Ceph health details, pool IDs, generated ARNs, referenced secrets, CephX key generations, mirroring info/status, and snapshot schedule status.
- Several status objects use `x-kubernetes-preserve-unknown-fields`, so Rook can store controller-populated maps or evolving status payloads without rejecting unknown nested keys.
- Maps like `parameters`, `config`, `cephConfig`, `annotations`, `labels`, `resources`, and `placement` preserve user-controlled settings that the operator later translates into Ceph commands or Kubernetes workload specs.
- Secret references in `cephConfigFromSecret`, Kafka endpoint credentials, `CephClient.secretName`, CephX status, and KMS token names connect CR state to Kubernetes `Secret` persistence.

Some spec fields directly represent destructive or sensitive intent. `cleanupPolicy.confirmation` only accepts empty string or `yes-really-destroy-data`; storage migration confirmation only accepts empty string or `yes-really-migrate-osds`. These are schema-level guards against accidental data destruction or OSD migration, but the actual actions are performed by Rook controllers after reconciliation.

## Dependencies And Integration Points

The primary dependencies are Kubernetes CRD machinery and Rook's generated Go API/controller code. The CRD schemas must stay aligned with the Go structs generated by kubebuilder/controller-gen, otherwise users may be able to submit objects the controller does not understand or be blocked from submitting fields the controller expects.

Important integration points in this chunk include:

- Helm values: `.Values.crds.enabled` is the only render gate in this range.
- Kubernetes API server: validates schemas, CEL rules, status subresources, printer columns, structural schema extensions, atomic map/list behavior, and int-or-string fields.
- Rook Ceph operator: watches all defined CRs and owns reconciliation of Ceph-side pools, namespaces, clients, object topics, notifications, and clusters.
- Ceph monitors, managers, OSDs, dashboard, crash collector, RGW, rbd-mirror, and ceph-exporter: configured indirectly from the CR specs.
- Ceph CSI: `CephBlockPoolRadosNamespace.clusterID`, pool namespace configuration, `CephCluster.spec.csi`, and CephX key rotation settings affect CSI configuration and credentials.
- Kubernetes native objects: embedded schemas and references integrate with `Secret`, `ConfigMap`, `PersistentVolumeClaim`, `VolumeSnapshot`/data source references, `EndpointAddress`, probes, affinity, tolerations, topology spread constraints, storage classes, and priority classes.
- Prometheus integration: `CephCluster.spec.monitoring` controls rules/exporter settings and can reference external manager endpoints.
- Multus/MCS networking: network selectors, address ranges, provider switching, and multi-cluster service settings integrate with CNI and service export implementations.

## Risks And Edge Cases

CRD lifecycle is a major risk. Because Helm keeps these CRDs, uninstalling or reinstalling the chart can leave older CRD schemas behind. Upgrades must ensure CRDs are applied before custom resources that use new fields. Conversely, removing fields from the schema can break existing CRs or block updates if persisted objects contain now-invalid data.

The chunk contains multiple immutable or monotonic fields. `dataDirHostPath` cannot change after cluster creation; RADOS namespace identity fields and client secret names cannot change; CephX key generation values cannot decrease. This is correct for safety but can surprise users trying to repair a deployment by editing CRs in place.

Large embedded Kubernetes schemas raise compatibility concerns. Probe, PVC, resource claim, affinity, topology spread, endpoint, and volume data source fields reflect a specific Kubernetes API shape. If the chart is installed on an older cluster, some schema features or CEL validation behavior may not be supported. If Kubernetes adds or changes nested fields, the CRD can lag behind native object capabilities until regenerated.

The `CephCluster` schema exposes many fields that are operationally dangerous even when schema-valid. Cleanup confirmation, OSD migration confirmation, full ratio changes, storage device filters, `useAllDevices`, `removeOSDsIfOutAndSafeToRemove`, external mode, host networking, Multus selector changes, and key rotation policies can affect data availability, network reachability, or client credentials.

Some schema validation is intentionally shallow. Network CIDRs use a naive regex and rely on Rook for deeper validation. Many maps preserve unknown fields, so malformed Ceph config keys or provider-specific storage options can pass API admission and fail later in controller reconciliation or Ceph commands.

The range ends mid-schema. Research or review of only this chunk must not assume it has the full `CephCluster` definition. In particular, the `storageClassDeviceSets` placement schema continues after line 4554, and status fields plus later CRDs are outside this work item.

Because this file is generated, hand edits are risky. Manual changes can drift from Go API definitions, controller assumptions, CRD generation annotations, or Helm chart packaging. Any schema change should normally be made in the source Go types and regenerated.

## Test Signals

High-signal validation for this chunk is CRD rendering and API-server admission, not unit tests inside this file:

- `helm template` for the rook-ceph chart with `crds.enabled=true` should render CRDs beginning with these resources; with `crds.enabled=false`, this guarded block should not render.
- Rendered YAML should parse cleanly and contain valid `apiextensions.k8s.io/v1` CRDs with `served: true`, `storage: true`, and `subresources.status`.
- Server-side dry-run apply against a supported Kubernetes version should accept the CRDs.
- Sample valid CRs for `CephBlockPoolRadosNamespace`, `CephBlockPool`, `CephBucketNotification`, `CephBucketTopic`, `CephClient`, and `CephCluster` should pass admission.
- Negative admission tests should reject invalid enum values, missing required fields such as bucket topic `endpoint` or client `caps`, invalid destructive confirmation strings, invalid ratio bounds, invalid port ranges, and immutable-field updates.
- Operator integration tests should confirm that status subresource updates work and that printer columns show phase, health, pool metadata, bucket topic ARN, and cluster FSID/health where applicable.
- CRD regeneration checks should compare this rendered schema against the output produced by current Rook API types and controller-gen to catch accidental manual drift.

### subset-b-000426: lines 4555-9184

# sources/control-plane/rook/deploy/charts/rook-ceph/templates/resources.yaml lines 4555-9184

## Scope

This chunk is a generated Helm chart CRD manifest range from Rook's `rook-ceph` chart. It starts inside the `CephCluster` OpenAPI schema, specifically in the `storage.storageClassDeviceSets[].placement` pod affinity selector subtree, then continues through the end of the `CephCluster` CRD status schema. It then contains the complete `CephCOSIDriver` and `CephFilesystemMirror` CRDs and the beginning through `status.info` of the `CephFilesystem` CRD.

The file is declarative Kubernetes YAML, generated by `controller-gen.kubebuilder.io/version: v0.19.0` and annotated with `helm.sh/resource-policy: keep` on each CRD. There are no executable functions in this range; the important interfaces are Kubernetes CustomResourceDefinitions, their served/stored `v1` schemas, printer columns, status subresources, validation constraints, and schema extensions.

## Purpose

The chart installs or preserves the Kubernetes API surface used by the Rook Ceph operator. The resources in this chunk let users describe Ceph cluster storage behavior, the Ceph COSI driver deployment, CephFS mirroring daemons, and CephFS filesystems. Kubernetes API server validation uses these schemas before the operator ever reconciles a custom resource.

For `CephCluster`, this range covers late storage configuration and status. The storage part includes portable storage class device set scheduling, prepare placement, resource requirements, PVC templates, OSD store settings, `useAllDevices`, `useAllNodes`, upgrade guard fields, and OSD health wait timeouts. The status part exposes Ceph health, capacity, daemon versions, CephX key generation tracking, conditions, observed generation, phase/state, storage status, and cluster version.

For `CephCOSIDriver`, this chunk defines a small namespaced CRD for deploying the COSI driver. The spec supports a deployment strategy enum (`Never`, `Auto`, `Always`), driver image, object provisioner sidecar image, Kubernetes placement controls, and container resources.

For `CephFilesystemMirror`, the CRD describes the cephfs-mirror daemon workload. It supports pod annotations, labels, placement, priority class, resources, status conditions, observed generation, phase, and CephX daemon key rotation status.

For `CephFilesystem`, this chunk defines the filesystem's pool and MDS-facing schema through the beginning of status. It covers `dataPools`, `metadataPool`, `metadataServer`, filesystem mirroring settings, deletion preservation flags, mirror status checks, and status fields for CephX, conditions, and info.

## Important APIs And Schema Surfaces

The `CephCluster` continuation is centered on storage device sets. `placement` and `preparePlacement` embed Kubernetes scheduling structures: node affinity, pod affinity, pod anti-affinity, tolerations, topology spread constraints, label selectors, namespace selectors, and topology keys. The schema uses Kubernetes merge hints such as `x-kubernetes-list-type: atomic`, `x-kubernetes-map-type: atomic`, and `x-kubernetes-preserve-unknown-fields` to control patch behavior and unknown field preservation.

`CephCluster.storageClassDeviceSets[].resources` and `volumeClaimTemplates` embed Kubernetes-style resource and PVC schemas. Resource quantities are `int-or-string` values with Kubernetes quantity regex validation. PVC templates include metadata, access modes, `dataSource`, `dataSourceRef`, resource requests/limits, selectors, storage class, volume attributes class, volume mode, and explicit volume binding. Device sets require `count`, `name`, and `volumeClaimTemplates`.

`CephCluster.store` accepts OSD backend settings. `type` is constrained to `bluestore` or `bluestore-rdr`, and `updateStore` is protected by the explicit acknowledgement pattern `^$|^yes-really-update-store$`, reflecting that changing OSD store type destroys and recreates OSDs one at a time. Upgrade behavior is guarded by `upgradeOSDRequiresHealthyPGs` and `waitTimeoutForHealthyOSDInMinutes`.

`CephCluster.status.ceph` reports capacity, health details, FSID, health transition timestamps, previous health, and daemon version maps for `cephfs-mirror`, `mds`, `mgr`, `mon`, `osd`, `overall`, `rbd-mirror`, and `rgw`. `CephCluster.status.cephx` tracks key status for admin, ceph exporter, crash collector, CSI, mgr, mon, osd, and rbd mirror peer users. Each key status generally includes `keyCephVersion` and `keyGeneration`; CSI also reports `priorKeyCount`.

`CephCOSIDriver` exposes a namespaced `cephcosidrivers.ceph.rook.io` API with short name `cephcosi`. Its spec fields are workload deployment controls rather than storage data-plane settings: deployment strategy, images, placement, and resources. It has no explicit `status` schema or `status` subresource in this chunk.

`CephFilesystemMirror` exposes `cephfilesystemmirrors.ceph.rook.io` with short name `cephfsm`. It has printer columns for `.status.phase` and age, a `status` subresource, and a spec focused on daemon pod customization. Status mirrors the common Rook pattern: `cephx.daemon`, `conditions`, `observedGeneration`, and `phase`.

`CephFilesystem` exposes `cephfilesystems.ceph.rook.io` with short name `cephfs`. It has printer columns for desired active MDS count, age, and phase. The spec requires `dataPools`, `metadataPool`, and `metadataServer`. Pool schemas support replicated and erasure-coded configurations, pool application names, compression settings, CRUSH roots and device classes, CRUSH tunable updates, RBD stats, failure domains, mirroring, peer secrets, snapshot schedules, parameters, quotas, and mirror health checks.

`CephFilesystem.spec.metadataServer` is the MDS workload API. It requires `activeCount`, constrained from 1 to 50, and supports active standby mode, pod annotations/labels, cache memory limit/request factors from 0 to 1, liveness and startup probes, placement, priority class, and resources. Probe schemas embed Kubernetes `exec`, `grpc`, `httpGet`, and `tcpSocket` probe options.

## Control Flow

There is no imperative control flow in the YAML itself. The runtime flow is Kubernetes and Rook driven:

1. Helm renders `templates/resources.yaml` and submits the CRDs to the cluster. The `helm.sh/resource-policy: keep` annotation directs Helm to preserve CRDs during chart uninstall.
2. The Kubernetes API server registers the `ceph.rook.io/v1` resources and uses these OpenAPI schemas for create/update validation, pruning, unknown-field behavior, server-side apply merge behavior, printer columns, and `/status` subresource separation where configured.
3. Users or automation create `CephCluster`, `CephCOSIDriver`, `CephFilesystemMirror`, and `CephFilesystem` custom resources.
4. Rook operator controllers watch those resources. Spec fields from this chunk become reconciliation inputs for Ceph daemons, pools, PVC-backed OSDs, COSI driver workloads, cephfs-mirror workloads, MDS daemons, CephFS mirror schedules, and deletion behavior.
5. Controllers update status fields such as conditions, observed generation, phase, Ceph health, CephX key generations, and storage status. For CRDs with `subresources.status`, status updates are separated from spec writes.

For `CephCluster` OSD upgrades, the schema models operator decision inputs: the controller can require clean PGs before upgrading OSDs, wait a configured number of minutes before stopping an OSD, and use status fields to report health and storage state. For `CephFilesystem`, the controller derives Ceph pools from `dataPools` and `metadataPool`, then deploys and tunes MDS pods from `metadataServer`.

## State And Persistence Behavior

The CRDs themselves persist API definitions in Kubernetes, not Ceph data. The `keep` policy is significant because CRDs and their custom resources can remain after Helm release deletion, preserving access to existing Rook-managed custom resources.

Custom resource specs persist desired state in etcd. In this chunk that includes destructive or long-lived storage intent: OSD PVC templates, use-all-device settings, OSD backend store type, filesystem pool layouts, erasure coding parameters, replication size, quotas, mirror peer secret names, snapshot schedules, and preserve-on-delete flags.

Custom resource statuses persist observed state. `CephCluster.status.ceph` stores health, capacity, versions, and FSID. `CephCluster.status.storage` stores deprecated OSD data, device classes, migration pending counts, and OSD store type counts. CephX status stores key generations and Ceph versions that created keys, which lets the operator reason about rotation progress and brownfield states. `observedGeneration` fields connect status to a specific reconciled spec generation.

Kubernetes schema extensions affect persistence semantics. `x-kubernetes-preserve-unknown-fields` appears on several flexible objects such as placement/resource/parameter/status-check fragments, allowing future or implementation-specific fields to remain in stored objects. `x-kubernetes-list-type: atomic` means many embedded Kubernetes lists are replaced as whole lists during apply/merge, which matters for affinity terms, selectors, topology spread constraints, and tolerations.

Deletion behavior is explicitly modeled for filesystems. `preserveFilesystemOnDelete` keeps the CephFS filesystem in the cluster and implies pool preservation; `preservePoolsOnDelete` keeps backing pools; `preservePoolNames` prevents pool name rewriting. These fields determine whether deleting a `CephFilesystem` CR removes only the Kubernetes desired-state object or also Ceph data-plane resources.

## Dependencies And Integration Points

The primary dependency is Kubernetes `apiextensions.k8s.io/v1` CRD behavior. The schemas embed many core Kubernetes API concepts: `ObjectMeta`-like metadata, `ResourceRequirements`, `PersistentVolumeClaim` spec fragments, `LabelSelector`, node and pod affinity, tolerations, topology spread constraints, and probe definitions. The API server enforces structural schema requirements and uses the CRD's status subresources and printer columns.

The Rook Ceph operator is the consumer of these APIs. It must have Go API types and reconciliation logic matching this generated schema. Schema mismatches can break users before reconciliation or allow invalid values that later fail in controllers. The operator also depends on these status fields for CLI visibility, upgrade workflows, key rotation reporting, and health reporting.

Ceph is the data-plane dependency behind the specs. Pool settings map to Ceph replicated or erasure-coded pools, CRUSH topology and device classes, quotas, mirroring, snapshot schedules, CephFS metadata servers, and cephfs-mirror peers. The `CephCOSIDriver` resource integrates with Kubernetes COSI components through the driver and object provisioner images.

Helm is the delivery mechanism, but the source is generated YAML rather than hand-written templates in this range. Chart users receive these CRDs as part of the Rook Ceph chart, while CRD updates must remain compatible with existing stored custom resources.

## Risks And Edge Cases

The range begins mid-schema, so changes near the start must be reconciled with the preceding `CephCluster.storageClassDeviceSets` definition. Treating this chunk as a standalone YAML document would be incorrect until line 6331, where the next CRD begins.

The embedded Kubernetes schemas are large and repetitive. Manual edits to affinity, PVC, resource, or probe fragments can easily diverge from Kubernetes structural schema expectations, especially list/map merge annotations and `int-or-string` quantity validation.

Several fields represent high-risk storage operations. `store.updateStore` intentionally requires an acknowledgement string because it destroys and recreates OSDs. `useAllDevices` and `useAllNodes` can consume broad storage inventory. Pool replication size, erasure coding chunks, CRUSH roots, device classes, and preserve-on-delete flags can affect durability, placement, and data retention.

Status schemas are operational contracts. Removing or renaming `phase`, `conditions`, `observedGeneration`, Ceph health, version maps, or CephX key generation fields can break kubectl output, automation, upgrade checks, and key rotation observability.

Feature-gated Kubernetes fields appear in embedded PVC/resource schemas, including Dynamic Resource Allocation claims, `dataSourceRef`, cross-namespace volume data sources, and `volumeAttributesClassName`. Clusters with older API servers or disabled gates may validate CRDs but later reject or ignore corresponding workload/PVC behavior.

`CephCOSIDriver` lacks a status subresource in this chunk, unlike the mirror and filesystem CRDs. Automation should not assume every Rook CRD in this file supports `/status`.

`x-kubernetes-preserve-unknown-fields` provides compatibility flexibility but weakens strict validation for those subtrees. Invalid operator-specific keys may be stored and only fail later during reconciliation.

## Test Signals

High-signal validation starts with rendering and validating the chart CRDs:

- `helm template` for the `rook-ceph` chart should produce valid multi-document YAML containing these CRDs.
- `kubectl apply --server-side --dry-run=server` against a compatible test cluster should accept the rendered CRDs.
- `kubectl explain cephcluster.spec.storage.storageClassDeviceSets`, `kubectl explain cephcosidriver.spec`, `kubectl explain cephfilesystemmirror.spec`, and `kubectl explain cephfilesystem.spec.metadataServer` should expose the fields described in this chunk.
- Creating minimal valid custom resources should enforce required fields: `CephFilesystem` requires `dataPools`, `metadataPool`, and `metadataServer`, and `metadataServer.activeCount` must be between 1 and 50.
- Negative validation should reject invalid enum/pattern values, such as a `CephCOSIDriver.spec.deploymentStrategy` outside `Never|Auto|Always`, an OSD store type outside `bluestore|bluestore-rdr`, or an `updateStore` value other than empty or `yes-really-update-store`.
- Operator e2e or integration tests should verify that status updates populate `conditions`, `observedGeneration`, `phase`, Ceph health/version data, CephX key generation data, and filesystem info without spec/status conflicts.
- Storage lifecycle tests should cover `preserveFilesystemOnDelete`, `preservePoolsOnDelete`, OSD PVC template handling, mirroring peer secret names, and snapshot schedule fields because these settings influence persistent Ceph resources beyond the Kubernetes CR object.

### subset-b-000427: lines 9185-13982

# sources/control-plane/rook/deploy/charts/rook-ceph/templates/resources.yaml lines 9185-13982

## Scope

This chunk is a slice of the Helm chart resource template that installs Rook-Ceph CustomResourceDefinitions. It begins inside the tail of the `CephFilesystem` CRD status schema, includes complete CRDs for `CephFilesystemSubVolumeGroup`, `CephNFS`, `CephNVMeOFGateway`, `CephObjectRealm`, and `CephObjectStoreAccount`, and ends inside the `CephObjectStore` CRD gateway schema before that CRD is complete.

The content is static Kubernetes CRD YAML generated by `controller-gen.kubebuilder.io/version: v0.19.0` and marked with `helm.sh/resource-policy: keep`. There are no Go functions or Helm conditionals in this chunk. The important interfaces are Kubernetes API schemas under `apiextensions.k8s.io/v1`, including validation rules, required fields, status subresources, printer columns, and embedded Kubernetes core types such as probes, resources, placement, volumes, and endpoint addresses.

## Purpose

The chart uses this file to make Rook's `ceph.rook.io/v1` APIs available in a cluster when the chart is installed. This chunk defines user-facing contracts for several Ceph services:

- `CephFilesystem` status tail for mirroring and snapshot schedule observability.
- `CephFilesystemSubVolumeGroup` for managing CephFS subvolume groups and CSI-facing metadata.
- `CephNFS` for deploying NFS-Ganesha servers backed by Ceph.
- `CephNVMeOFGateway` for deploying NVMe-oF gateways.
- `CephObjectRealm` for RGW multisite realm metadata and realm pull configuration.
- `CephObjectStoreAccount` for RGW account/root-user management.
- The opening and middle of `CephObjectStore`, covering RGW object-store auth, pools, and much of gateway pod configuration.

Because these are CRDs, the chunk's direct runtime role is admission and API persistence. It constrains what users can submit to the Kubernetes API server and what Rook controllers can write into status, but the reconciliation logic lives elsewhere in the operator source.

## Important APIs, Types, and Schema Contracts

The `CephFilesystem` tail at lines 9185-9339 describes status-only fields. `mirroringStatus` records CephFS mirror daemon state, including daemon IDs, managed filesystems, peer UUIDs, remote client/cluster/filesystem names, and peer failure/recovery counts. `snapshotScheduleStatus` records schedule details, checked/changed timestamps, filesystem path/subvolume identity, and retention counters such as created/pruned counts and first/last snapshot timestamps. `observedGeneration`, `phase`, and `subresources.status` make this state controller-owned status rather than spec input.

`CephFilesystemSubVolumeGroup` at lines 9340-9504 is a namespaced CRD with short names `cephfssvg` and `cephsvg`. Its required spec field is `filesystemName`. Important spec fields are `clusterID`, `csiMetadataRadosNamespace`, `dataPoolName`, `filesystemName`, optional subvolume group `name`, `pinning`, and `quota`. Several fields are immutable through CEL validations: `clusterID`, `csiMetadataRadosNamespace`, `filesystemName`, and `name`. `clusterID` is constrained to 1-36 characters matching `^[a-zA-Z0-9_-]+$`; `csiMetadataRadosNamespace` allows 1-1024 characters; `pinning` allows only one of `export`, `distributed`, or `random`; and `quota` is an `int-or-string` Kubernetes quantity. Status has a string map `info`, `observedGeneration`, and `phase`.

`CephNFS` at lines 9504-11633 is a namespaced CRD with short name `nfs`. Its spec requires `server`, and `server` requires `active`. Deprecated `spec.rados.pool` and `spec.rados.namespace` describe old Ganesha shared-config storage, now internally fixed to the `.nfs` pool and the CephNFS name. `spec.security.kerberos` supports config file and keytab file volume sources, a `domainName`, and a `principalName` defaulting to `nfs`; the generated principal shape is documented as `<principalName>/<namespace>-<name>@<realm>`. `spec.security.sssd.sidecar` allows an SSSD sidecar with required `image`, optional additional mounted files, SSSD config volume source, debug level, and resources. `spec.server` controls Ganesha pod count, labels, annotations, host networking, image and pull policy, liveness probe override/disable behavior, log level, placement, priority class, and resource requests/limits. Status exposes CephX daemon key tracking (`keyCephVersion`, `keyGeneration`), conditions, `observedGeneration`, and `phase`.

`CephNVMeOFGateway` at lines 11633-12549 is a namespaced CRD with short name `nvmeof`. Its spec requires `group`, `instances`, and `pool`. It supports pod labels/annotations, `configMapRef` for externally supplied `nvmeof.conf`, inline `nvmeofConfig` as a section/key/value map, host networking, optional image override, liveness probe override/disable behavior, placement, ports, priority class, and resources. Validation highlights include non-empty `group`, `pool`, `configMapRef`, and `image`; `instances` minimum 1; image max length 1024; and all NVMe-oF ports constrained to 1-65535. Status mirrors the NFS pattern with CephX daemon key generation/version, conditions, `observedGeneration`, and `phase`.

`CephObjectRealm` at lines 12549-12652 is a namespaced CRD with short name `cephor`. Its spec is nullable and contains `defaultRealm` plus optional `pull.endpoint`, whose value must match `^https*://`. Status uses the common conditions, `observedGeneration`, and `phase` pattern. This CRD is part of RGW multisite configuration and can either declare a local realm/defaulting behavior or pull realm metadata from another endpoint.

`CephObjectStoreAccount` at lines 12652-12774 represents an RGW account. Its spec requires immutable `store`, and optional immutable `accountID` must be exactly 20 characters matching `^RGW\d{17}$`. Optional display `name` accepts 1-2048 characters matching `^[a-zA-Z0-9 ._-]+$`. `rootUser` can set a root user display name matching `^[\w+=,.@-]+$` or `skipCreate` to leave root-user creation outside Rook. Status records the resolved `accountID`, `rootAccountSecretName`, `observedGeneration`, and `phase`.

`CephObjectStore` begins at lines 12774-13982 and continues beyond this chunk. The covered spec fields include allowed cross-namespace user creation via `allowUsersInNamespaces`, Keystone auth, data pool settings, `defaultRealm`, and much of `gateway`. `auth.keystone` requires `acceptedRoles`, `serviceUserSecretName`, and `url`; optional fields include `implicitTenants`, `revocationInterval`, and `tokenCacheSize`. `dataPool` embeds the common Ceph pool contract: application, deprecated `compressionMode`, CRUSH selectors, erasure coding with required `codingChunks` and `dataChunks`, failure domain, mirroring mode/peers/snapshot schedules, arbitrary pool `parameters`, quotas, replicated size/hybrid storage, and mirroring status checks. The covered `gateway` schema includes additional volume mounts rooted under `/var/rgw`, annotations, CA bundle reference, dashboard enablement, multisite sync traffic control, external RGW endpoint addresses, host networking, instance count, labels, ops-log sidecar resources, and placement.

## Control Flow

There is no procedural control flow in the YAML itself. The operational flow is Kubernetes and Rook driven:

1. Helm renders and applies this static CRD manifest as part of the Rook-Ceph chart.
2. Kubernetes stores each CRD and starts serving the `ceph.rook.io/v1` API resources declared in `spec.names`.
3. Users and automation create or update matching custom resources.
4. The Kubernetes API server validates objects against this OpenAPI v3 schema, including required fields, quantity patterns, enum values, CEL immutability rules, and list/map semantics.
5. Rook controllers watch the resources, reconcile Ceph daemons or RGW/CephFS/NFS/NVMe-oF state from `spec`, and write controller-owned fields under the `status` subresource.
6. `kubectl get` uses the `additionalPrinterColumns` defined here to show phase, endpoint, filesystem, quota, pinning, and age summaries depending on resource kind.

The chunk's partial boundaries matter. The first fields are still inside `CephFilesystem.status`, and the final `CephObjectStore.gateway.placement` subtree continues past line 13982. The merge lane should combine adjacent chunks before treating either CRD as fully described.

## State and Persistence Behavior

The CRDs themselves are persistent Kubernetes API definitions. The `helm.sh/resource-policy: keep` annotation means Helm should not delete them during uninstall, preserving the API definitions and reducing accidental loss of custom resources that depend on them.

Custom resources created under these CRDs persist in etcd as Kubernetes objects. Spec fields represent desired state owned by users or automation. Status fields such as `phase`, `conditions`, `observedGeneration`, mirroring state, snapshot schedule state, CephX key generation, account IDs, and secret names are intended to be written by Rook controllers through `subresources.status`.

Several fields encode state stability requirements. Immutable fields prevent API-level mutation after creation for CephFS subvolume group identity/CSI fields and object-store account `accountID`/`store`. Generated IDs and secrets are reflected into status, including subvolume group `clusterID` when omitted and object store account root credentials via `rootAccountSecretName`. CephX status tracks whether daemon credentials have been initialized or rotated by recording `keyGeneration` and the Ceph version that produced keys.

The schemas also allow controlled persistence of loosely structured operator inputs. Examples include `x-kubernetes-preserve-unknown-fields` on status and selected maps, arbitrary pool `parameters`, pod annotations/labels, `nvmeofConfig`, and Kubernetes `ResourceRequirements`. These preserve flexibility while still validating high-value fields.

## Dependencies and Integration Points

The primary dependency is the Kubernetes `apiextensions.k8s.io/v1` CRD API. The schemas inline many Kubernetes core API shapes: `VolumeSource`, `Probe`, `ResourceRequirements`, `Affinity`, `Toleration`, `TopologySpreadConstraint`, `EndpointAddress`, object metadata, status conditions, and `IntOrString` quantities.

Rook-specific integration points include:

- CephFS volume and subvolume-group management through `CephFilesystemSubVolumeGroup.spec.filesystemName`, pinning, quota, data pool, CSI cluster ID, and CSI metadata RADOS namespace.
- CephFS mirroring and snapshot scheduling observability through `CephFilesystem.status.mirroringStatus` and `snapshotScheduleStatus`.
- NFS-Ganesha deployment through `CephNFS.spec.server`, deprecated Ganesha RADOS config, Kerberos, and SSSD sidecar configuration.
- NVMe-oF gateway deployment through gateway group/ANA identity, RADOS config pool, inline or ConfigMap config, service ports, and pod scheduling controls.
- RGW multisite configuration through `CephObjectRealm.defaultRealm`, realm pull endpoint, `CephObjectStore.defaultRealm`, and gateway multisite sync settings.
- RGW account/user provisioning through `CephObjectStoreAccount.spec.store`, generated or user-specified account IDs, root user settings, and credential secret status.
- RGW object-store behavior through Keystone auth, data pool layout, mirroring settings, quotas, external endpoints, CA bundle, gateway placement, and operations-log sidecar resources.

The chart integration point is Helm applying `templates/resources.yaml`; there is no chart value interpolation in this chunk. The controller integration point is the Go API/controller code that generated and reconciles these schemas, but that code is outside this chunk.

## Risks and Edge Cases

CRD lifecycle is intentionally conservative because of `helm.sh/resource-policy: keep`, but that also means chart uninstall/reinstall may leave old CRD versions installed. Upgrades must be validated against existing custom resources, especially when schema validations become stricter.

The chunk includes several identity fields with immutability validations. Users cannot later change a subvolume group's `filesystemName`, `clusterID`, CSI metadata namespace, or explicit name, and cannot move an object-store account to a different store or alter its account ID. Mistakes require resource replacement or manual recovery.

Some schema validation is precise while other validation is intentionally loose. Port ranges, quantity patterns, account ID patterns, Keystone required fields, and one-of pinning are enforced at admission. By contrast, endpoint reachability, image contents, Ceph pool suitability, Kerberos realm correctness, SSSD config validity, and external RGW endpoint stability are only discoverable during reconciliation or runtime.

Several fields are deprecated but still accepted, including `CephNFS.spec.rados.pool`, `CephNFS.spec.rados.namespace`, and object-store pool `compressionMode`. Consumers may still submit them, but controller behavior may ignore or translate them according to newer internal defaults.

Security-sensitive configuration is exposed through volume sources and secret references. Kerberos keytabs, SSSD config, Keystone service user credentials, custom CA bundles, and RGW account root credentials require namespace and RBAC controls. The schema validates shape, not whether referenced secrets are present, readable by Rook, or appropriately scoped.

The generated CRD embeds large Kubernetes pod configuration schemas. These broaden the accepted API surface and can create compatibility concerns with Kubernetes version skew, especially for newer nested fields such as projected volume sources, pod certificates, resource claims, match label keys, mismatch label keys, and topology spread options.

The `CephObjectStore` CRD is incomplete in this chunk. Research or code review based only on lines 12774-13982 would miss later gateway fields, status, required fields, and subresource declarations.

## Test Signals

High-signal validation for this chunk is mostly Kubernetes/Helm oriented:

- `helm template` for the Rook-Ceph chart should render these CRDs without YAML syntax errors.
- `kubectl apply --server-side --dry-run=server` against a compatible cluster should accept the rendered CRDs.
- Creating minimal valid resources should pass admission: `CephFilesystemSubVolumeGroup` with `filesystemName`, `CephNFS` with `server.active`, `CephNVMeOFGateway` with `group`, `instances`, and `pool`, `CephObjectRealm` with empty or valid pull spec, and `CephObjectStoreAccount` with `store`.
- Negative admission tests should reject multiple subvolume-group pinning types, invalid object-store account IDs, invalid realm pull endpoints, out-of-range NVMe-oF ports, and updates to immutable fields.
- Controller e2e tests should confirm status writes through the status subresource, including `observedGeneration`, `phase`, conditions, CephX key status, generated account IDs, root account secret names, CephFS mirror status, and snapshot schedule status.
- Operational tests should verify that referenced secrets/config maps and mounted volume sources for Kerberos, SSSD, Keystone, CA bundles, additional files, and custom gateway/NFS config are consumed correctly by the relevant pods.
- Upgrade tests should confirm that existing CRs survive Helm uninstall/reinstall because CRDs are kept, and that schema changes do not break stored resources during chart upgrades.

### subset-b-000428: lines 13983-17025

# sources/control-plane/rook/deploy/charts/rook-ceph/templates/resources.yaml lines 13983-17025

## Scope

This chunk covers the final section of the Rook Ceph Helm chart's generated CRD template. The range starts inside the `CephObjectStore` CRD's `spec.gateway.placement.topologySpreadConstraints` schema and continues through the end of the `{{- if .Values.crds.enabled -}}` block.

The source range includes:

- The tail of `cephobjectstores.ceph.rook.io`, including RGW gateway settings, object-store pool schemas, protocol/security/shared-pool/multisite fields, status, and the scale/status subresources.
- Full CRD definitions for `CephObjectStoreUser`, `CephObjectZoneGroup`, `CephObjectZone`, and `CephRBDMirror`.
- The object bucket API CRDs `ObjectBucketClaim` and `ObjectBucket` in the `objectbucket.io` group.

This file is declarative Kubernetes/Helm YAML. There are no project-defined functions or executable methods in this chunk; the important API surface is the set of CRD schemas and subresources registered with the Kubernetes API server.

## Purpose

`resources.yaml` lets the Rook Ceph Helm chart install the Kubernetes APIs that the Rook operator and bucket provisioners reconcile. This chunk focuses on object storage, multisite object-store topology, RBD mirroring, and object bucket abstractions.

The chart-level purpose is controlled by the outer `{{- if .Values.crds.enabled -}}` guard: when CRD installation is enabled, Helm renders these `apiextensions.k8s.io/v1` resources. Each CRD has `helm.sh/resource-policy: keep`, so Helm should leave CRDs installed during chart uninstall. That matters because CRDs are the persistence boundary for all instances of these APIs.

Operationally, the CRDs in this range define:

- How RGW-backed `CephObjectStore` resources configure gateway pods, pools, protocol exposure, security options, shared pools, and multisite zone membership.
- How `CephObjectStoreUser` resources request RGW users, credentials, admin capabilities, operation masks, and quotas.
- How multisite `CephObjectZoneGroup` and `CephObjectZone` resources model realm/zonegroup/zone hierarchy and pool placement.
- How `CephRBDMirror` resources request RBD mirror daemons and peer secrets.
- How object bucket claims and cluster-scoped object bucket records interoperate with the object bucket provisioner API.

## Important CRD And Schema Surfaces

`CephObjectStore` is already open before this chunk begins. The visible gateway schema includes Kubernetes scheduling placement fields, `port`, `securePort`, `priorityClassName`, RGW pod `resources`, TLS certificate reference, service labels/annotations, runtime RGW config, startup RGW command flags, secret-sourced RGW config, and `readAffinity`. `readAffinity.type` is constrained to `localize`, `balance`, or `default`, and the inline description calls out Ceph Tentacle v20 support. `rgwConfig` is documented as runtime configuration, while `rgwCommandFlags` is startup configuration that restarts RGW pods.

`CephObjectStore.spec.healthCheck` defines `readinessProbe` and `startupProbe` wrappers. Each wrapper has a `disabled` flag plus an embedded Kubernetes-style `Probe` schema covering `exec`, `grpc`, `httpGet`, `tcpSocket`, thresholds, periods, timeouts, initial delays, success thresholds, and termination grace periods. Unknown fields are preserved at the wrapper level, which gives the operator room to tolerate Kubernetes probe schema drift.

`CephObjectStore.spec.metadataPool` uses the same pool schema pattern as object-store data pools: pool application, deprecated `compressionMode`, CRUSH root/device class, optional CRUSH tunable updates, RBD stats, erasure coding, replicated settings, arbitrary parameters, quotas, mirroring configuration, and mirroring health checks. The erasure-coded profile requires `dataChunks` and `codingChunks`, constrains the algorithm to `isa` or `jerasure`, and limits `stripeUnit` to known quantities such as `4Ki`, `16Ki`, `64Ki`, `256Ki`, and `1Mi`. The replicated profile requires `size` and supports hybrid storage tiers, safe replica enforcement, failure-domain replica counts, and capacity target hints.

`CephObjectStore.spec.protocols` controls RGW API exposure. `enableAPIs` can explicitly enable the RGW API set (`s3`, `s3website`, `swift`, `swift_auth`, `admin`, `sts`, `iam`, `notifications`) and overrides the deprecated `protocols.s3.enabled` boolean. The Swift subsection exposes `accountInUrl`, `urlPrefix`, and object versioning. The S3 subsection has `authUseKeystone` and the deprecated `enabled` flag.

`CephObjectStore.spec.security` defines RGW TLS/KMS settings. It includes OpenSSL cipher lists for TLS v1.3 and TLS v1.2-or-lower, TLS group names, key rotation settings, a generic KMS stanza, an S3 SSE-KMS/SSE-S3-related stanza, and `sslOptions` booleans for beast frontend options such as `sslv2`, `sslv3`, `tlsv1_0`, `tlsv1_1`, and `tlsv1_2`.

`CephObjectStore.spec.sharedPools` defines the schema for storing multiple object-store namespaces in existing pools. `dataPoolName` and `metadataPoolName` are guarded by CEL immutability validations. `poolPlacements` define placement target names, data/metadata pool names, optional non-EC data pool names, one default placement marker, and up to ten additional storage classes per placement. Several descriptions warn that changing pool names after creation can lead to data loss because pool names are embedded in RADOS namespaces.

`CephObjectStore.spec.zone` links the store to a multisite `CephObjectZone` by name. A top-level CEL validation rejects `defaultRealm: true` when `zone.name` is set, preventing an object store from simultaneously acting as the default realm and as a member of a multisite zone.

`CephObjectStore.status` records operator-owned state: CephX daemon key generation/version, conditions, endpoints, an info map, message, observed generation, phase, gateway replica count, and selector. The CRD exposes both `status` and `scale` subresources. The scale subresource maps desired replicas to `.spec.gateway.instances`, current replicas to `.status.replicas`, and label selector to `.status.selector`.

`CephObjectStoreUser` defines namespaced RGW users. `spec.accountRef` refers to a same-namespace `CephObjectStoreAccount` and is immutable by CEL validation. `spec.capabilities` exposes RGW admin capability categories such as `bucket`, `buckets`, `user`, `users`, `metadata`, `usage`, `roles`, `zone`, logs, cache, rate limit, OIDC provider, and user policy, with each value constrained to `*`, `read`, `write`, or `read, write`. `spec.keys` accepts access-key and secret-key `SecretKeySelector` references; if keys are omitted, the operator is expected to generate credentials. `spec.opMask` is a set of up to three values from `read`, `write`, and `delete`, and can intentionally be an empty list to remove all operation permissions. `spec.quotas` limits buckets, objects, and total size. Status records info, generated or referenced key secret object references, observed generation, and phase.

`CephObjectZoneGroup` is a small namespaced multisite CRD. Its spec requires `realm`, linking the zone group to a `CephObjectRealm`. Status follows the common Rook shape: conditions, observed generation, and phase.

`CephObjectZone` models a zone within a zone group. Its spec requires `zoneGroup`, can list `customEndpoints` for externally reachable RGW endpoints, and has `dataPool`, `metadataPool`, `sharedPools`, and `preservePoolsOnDelete` settings. `preservePoolsOnDelete` defaults to true for zones. Pool and shared-pool schemas mirror the object-store pool placement patterns, including immutable shared-pool names and placement storage-class definitions. Status again uses conditions, observed generation, and phase.

`CephRBDMirror` defines namespaced RBD mirror daemons. Its spec requires `count` with a minimum of one. It supports pod annotations/labels, peer secret names, Kubernetes placement rules, tolerations, topology spread constraints, priority class, and resource requirements. The resource schema includes `claims` for Dynamic Resource Allocation, plus standard `limits` and `requests` quantity maps. Status records CephX daemon key state, conditions, observed generation, and phase.

`ObjectBucketClaim` is a namespaced `objectbucket.io/v1alpha1` CRD. Its spec is intentionally loose: `storageClassName`, `bucketName`, `generateBucketName`, `additionalConfig` with unknown fields preserved, and `objectBucketName`. Status preserves unknown fields and has a status subresource. This is the user-facing claim API for dynamic object bucket provisioning.

`ObjectBucket` is the cluster-scoped `objectbucket.io/v1alpha1` companion record. Its spec includes `storageClassName`, an optional endpoint object (`bucketHost`, `bucketPort`, `bucketName`, `region`, `subRegion`, and endpoint-level `additionalConfig`), optional `authentication`, `additionalState`, `reclaimPolicy`, and optional `claimRef`. Status preserves unknown fields. The schema is intentionally permissive so bucket provisioners can store implementation-specific connection/authentication state.

## Control Flow

The runtime flow begins outside this chunk, in Helm and the Kubernetes API server:

1. Helm renders this template only when `.Values.crds.enabled` is true.
2. Kubernetes applies each rendered `CustomResourceDefinition`.
3. The API server creates REST endpoints for each served/storage version and enforces OpenAPI validation, CEL validations, required fields, enum constraints, quantity patterns, nullable behavior, and subresource boundaries.
4. Users, controllers, or automation create custom resources against those APIs.
5. The Rook Ceph operator and object bucket provisioners watch those resources, reconcile external Ceph/Kubernetes state, and update `status` through status subresources.

For object stores, the Rook operator consumes `CephObjectStore.spec` to create or update RGW gateways, Kubernetes Services, pools, placements, security/KMS configuration, protocol enablement, and multisite configuration. Gateway scaling can be driven through the scale subresource because desired replica state maps to `.spec.gateway.instances`.

For object store users, the operator reads `CephObjectStoreUser.spec`, creates or updates RGW users in the referenced store, sources credentials from referenced Secrets or generates them, applies op masks, admin caps, and quotas, then writes phase and key Secret references to status.

For multisite resources, the operator links zones to zone groups and zone groups to realms. Zone custom endpoints determine how peer clusters reach RGW services; if a relevant endpoint is omitted, the schema description warns that RGW gateways may not receive multisite replication traffic.

For `CephRBDMirror`, the operator uses the required `count`, peer secrets, pod scheduling constraints, and resource requests to deploy and manage rbd-mirror daemons, then updates mirror phase and key tracking status.

For object bucket resources, the bucket provisioning flow generally starts with an `ObjectBucketClaim`. A provisioner creates or binds an `ObjectBucket`, stores endpoint/authentication/additional state there, and updates status. This chart only registers the API; provisioning behavior is implemented by controllers outside the CRD.

## State And Persistence Behavior

The Kubernetes API server persists all CR specs and status fields backed by etcd. These CRDs are persistent API definitions, not transient chart resources, because of the Helm keep annotation.

Important persistent state surfaces include:

- `CephObjectStore` desired RGW gateway configuration, pool definitions, protocol/security settings, shared-pool placements, and multisite zone membership.
- `CephObjectStore.status.endpoints`, `status.info`, `status.phase`, `status.conditions`, `status.replicas`, `status.selector`, and CephX key generation metadata.
- `CephObjectStoreUser` desired credentials, capabilities, operation masks, quotas, target store, and status references to key Secrets.
- `CephObjectZone` and `CephObjectZoneGroup` desired multisite topology plus status conditions and phases.
- `CephRBDMirror` desired daemon count, placement, peers, resource requirements, and CephX/status tracking.
- `ObjectBucketClaim` namespaced claim intent and `ObjectBucket` cluster-scoped binding/endpoint/authentication state.

Several fields intentionally preserve unknown fields, especially maps of arbitrary config, status blobs, and object bucket state. This preserves forward compatibility and implementation-specific data, but it also means the API server delegates many semantic checks to controllers.

Some state is protected against mutation by CEL validations. Notable examples are `CephObjectStoreUser.spec.accountRef` and shared-pool `dataPoolName`/`metadataPoolName`. These immutability checks protect identity and storage-layout state that cannot be safely renamed after data exists.

Deletion behavior is partly encoded in spec. `preservePoolsOnDelete` and `preserveRadosNamespaceDataOnDelete` determine whether backing pool or namespace data should survive custom resource deletion. For zones, `preservePoolsOnDelete` defaults to true.

## Dependencies And Integration Points

The primary dependencies are Kubernetes CRDs, Helm templating, and the Rook Ceph operator. The schemas depend on Kubernetes API conventions for `metadata`, status subresources, scale subresources, label selectors, affinity, tolerations, probes, resource quantities, Secret selectors, and CEL validations.

Ceph integration points include:

- RGW gateway deployment and configuration through `CephObjectStore`.
- RADOS pools, erasure coding, replication, quotas, CRUSH placement, RADOS namespaces, and pool placement targets.
- RGW S3/Swift/Admin/STS/IAM/notification APIs.
- Keystone authentication and KMS/SSE integrations.
- Multisite realm, zone group, zone, and endpoint configuration.
- CephX key tracking for local Ceph daemons.
- RBD mirror daemons and peer secret configuration.

Kubernetes integration points include:

- Secrets for RGW config values, object user access keys, object user secret keys, KMS tokens, TLS certificates, and mirror peers.
- Services for RGW endpoints and service annotations/labels.
- Pod scheduling APIs for gateway and rbd-mirror placement.
- Dynamic Resource Allocation through `resources.claims`, subject to the Kubernetes feature gate.
- The scale subresource for `CephObjectStore` gateway replicas.

The object bucket CRDs integrate with the `objectbucket.io` API used by bucket provisioners and consumers. `ObjectBucketClaim` is namespaced and claim-like; `ObjectBucket` is cluster-scoped and stores binding, endpoint, authentication, reclaim policy, and implementation state.

## Risks And Edge Cases

This file is generated CRD YAML. Manual edits can drift from the Go API types and controller expectations. Changes should normally come from Rook's API definitions and controller-gen output, then be propagated into the Helm chart.

Many fields are syntactically validated but semantically controller-validated. Examples include RGW config maps, RGW command flags, OpenSSL cipher names, TLS groups, KMS connection details, Keystone URLs, pool parameters, and object bucket state. Invalid values can pass API admission and fail later during reconciliation.

Storage layout fields are high risk. Pool names, shared pool names, placement targets, and storage-class data pool names may be embedded in RADOS namespaces or RGW placement config. The schema protects some fields with immutability validations, but descriptions still warn that renaming pool references can cause data loss.

Feature/version compatibility matters. `readAffinity` is documented as Ceph Tentacle v20-only. `resources.claims` depends on Kubernetes Dynamic Resource Allocation. TLS option behavior depends on RGW beast and the OpenSSL version in the Ceph image. Clusters running older Ceph or Kubernetes versions may accept the CR but fail reconciliation.

`SecretKeySelector.name` carries Kubernetes' backward-compatible default empty string. The inline Kubernetes description notes empty references are effectively wrong even when the schema permits them. This affects RGW config-from-secret and object user key references.

The permissive `x-kubernetes-preserve-unknown-fields` sections preserve compatibility but weaken admission-time validation. Object bucket `additionalConfig`, `authentication`, `additionalState`, and `claimRef` are especially loose because provisioners own much of their structure.

CRD upgrade behavior is important because these definitions are marked with Helm keep. Uninstalling/reinstalling the chart may leave old CRDs behind, so operators must handle CRD upgrades explicitly and verify stored objects still validate under the new schemas.

The `CephObjectStore` scale subresource depends on the operator maintaining `.status.replicas` and `.status.selector`. If those status fields are missing or stale, Kubernetes clients using scale semantics can show misleading state.

## Test Signals

High-signal validation for this chunk includes:

- `helm template` for the rook-ceph chart with `crds.enabled=true` should render these CRDs, and with `crds.enabled=false` should omit the whole CRD block.
- Kubernetes server-side dry-run or schema validation should accept every CRD in this range as `apiextensions.k8s.io/v1`.
- `kubectl explain` should expose the expected fields for `CephObjectStore`, `CephObjectStoreUser`, `CephObjectZoneGroup`, `CephObjectZone`, `CephRBDMirror`, `ObjectBucketClaim`, and `ObjectBucket`.
- Admission tests should reject invalid enum values for fields such as RGW API enablement, read affinity, pool mirroring mode, erasure coding algorithm, op masks, and user capability values.
- CEL admission tests should reject updates that mutate immutable fields such as `CephObjectStoreUser.spec.accountRef` and shared pool names.
- Rook e2e or integration tests should create an object store, scale its gateway instances, create object users with generated and secret-sourced credentials, exercise object store status endpoints, create multisite zone/zonegroup resources, and deploy an RBD mirror.
- Bucket provisioning tests should create an `ObjectBucketClaim`, observe a cluster-scoped `ObjectBucket`, and verify endpoint/authentication/status state is populated by the provisioner.
- Upgrade tests should confirm existing CRs still validate after CRD replacement and that Helm's keep annotation does not leave stale schemas unnoticed.
