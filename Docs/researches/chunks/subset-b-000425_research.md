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
