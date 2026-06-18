# sources/control-plane/rook/deploy/examples/crds.yaml lines 4552-9179

## Scope

This chunk covers a generated Kubernetes CRD manifest segment from Rook's example CRDs. The requested range starts inside the `CephCluster` CRD schema, in the nested scheduling placement schema for OSD `storageClassDeviceSets`, continues through the end of the `CephCluster` `status` schema, includes the full `CephCOSIDriver` and `CephFilesystemMirror` CRDs, and ends inside the `CephFilesystem` CRD `status.info` map.

Because this is a large generated YAML manifest, there are no hand-written functions in the range. The important interfaces are Kubernetes API shapes: CRD metadata, OpenAPI v3 schema properties, required fields, enum constraints, nullable/preserved-unknown markers, printer columns, served/storage version flags, and status subresources.

## Purpose

`deploy/examples/crds.yaml` is the install-time API contract for Rook Ceph custom resources. This chunk defines or completes the API server validation schemas for several Ceph control-plane resources:

- The tail of `cephclusters.ceph.rook.io`, especially storage device set placement, OSD update controls, storage settings, and rich cluster status.
- `cephcosidrivers.ceph.rook.io`, a namespaced resource that configures deployment of the Ceph COSI driver and object provisioner sidecar.
- `cephfilesystemmirrors.ceph.rook.io`, a namespaced resource that configures `cephfs-mirror` daemon deployment.
- The beginning of `cephfilesystems.ceph.rook.io`, a namespaced resource that declares CephFS data pools, metadata pool, MDS deployment behavior, mirroring, deletion preservation, and the first part of status.

The API server uses these schemas to reject structurally invalid custom resources before Rook reconcilers act on them. Rook controllers then read accepted `spec` fields and write `status` fields through the status subresource.

## Important APIs, Types, And Fields

The `CephCluster` tail in this chunk includes the end of `spec.storage` and `status`.

Important `CephCluster` storage fields in this range include:

- `storageClassDeviceSets[*].placement`, using Kubernetes-style `nodeAffinity`, `podAffinity`, `podAntiAffinity`, `tolerations`, and `topologySpreadConstraints`.
- `portable`, `preparePlacement`, `resources`, `schedulerName`, `tuneSlowDeviceClass`, `tuneFastDeviceClass`, and per-device-set `volumeClaimTemplates`.
- PVC-like `volumeClaimTemplates` with `metadata`, `spec.accessModes`, `dataSource`, `dataSourceRef`, `resources`, `selector`, `storageClassName`, `volumeAttributesClassName`, `volumeMode`, and `volumeName`.
- `store.type`, constrained to `bluestore` or empty, and `store.updateStore`.
- cluster-level `useAllDevices`, `useAllNodes`, `volumeClaimTemplates`, `osdMaxUpdatesInParallel` with minimum `1`, `upgradeOSDRequiresHealthyPGs`, and `waitTimeoutForHealthyOSDInMinutes`.

The visible `CephCluster.status` fields expose controller-observed state:

- `ceph.capacity` with bytes available/total/used and `lastUpdated`.
- `ceph.details` as a map of health messages with required `message` and `severity`.
- `ceph.fsid`, `health`, `lastChanged`, `lastChecked`, `previousHealth`, and daemon `versions` maps for `cephfs-mirror`, `mds`, `mgr`, `mon`, `osd`, `overall`, `rbd-mirror`, and `rgw`.
- `cephx` key rotation state for `admin`, `cephExporter`, `crashCollector`, `csi`, `mgr`, `mon`, `osd`, and `rbdMirrorPeer`, including `keyCephVersion`, `keyGeneration`, and `csi.priorKeyCount`.
- standard `conditions`, `message`, `observedGeneration`, `phase`, `state`, `storage`, and `version`.

`CephCOSIDriver` is defined as group `ceph.rook.io`, kind `CephCOSIDriver`, plural `cephcosidrivers`, short name `cephcosi`, namespaced scope, version `v1`, served and storage. Its `spec` contains:

- `deploymentStrategy`, enum `Never`, `Auto`, or `Always`.
- `image` for the Ceph COSI driver container.
- `objectProvisionerImage` for the COSI sidecar.
- `placement` with the same Kubernetes scheduling primitives used across Rook daemon specs.
- `resources` with Kubernetes `claims`, `limits`, and `requests`.

`CephFilesystemMirror` is defined as kind `CephFilesystemMirror`, plural `cephfilesystemmirrors`, short name `cephfsm`, namespaced scope, version `v1`, with printer columns for `.status.phase` and age. Its `spec` includes:

- `annotations` and `labels` applied to related pod objects.
- `placement`, `priorityClassName`, and `resources` for `cephfs-mirror` pods.

Its `status` includes local daemon CephX key status, standard `conditions`, `observedGeneration`, and `phase`. The CRD enables `subresources.status`.

`CephFilesystem` is defined as kind `CephFilesystem`, plural `cephfilesystems`, short name `cephfs`, namespaced scope, version `v1`, with printer columns for active MDS count, age, and phase. The visible `spec` requires `dataPools`, `metadataPool`, and `metadataServer`.

Important `CephFilesystem.spec` fields in this chunk include:

- `dataPools[]` and `metadataPool`, both using pool spec fields such as `application`, `compressionMode`, `crushRoot`, `deviceClass`, `enableCrushUpdates`, `enableRBDStats`, `failureDomain`, `name`, `parameters`, `quotas`, `replicated`, `erasureCoded`, `mirroring`, and `statusCheck`.
- `erasureCoded.algorithm` enum `isa` or `jerasure`, required `codingChunks` and `dataChunks`, and `stripeUnit` enum values such as `4Ki`, `16Ki`, `64Ki`, `256Ki`, and `1Mi`.
- `replicated.size` as a required field, plus `replicasPerFailureDomain`, `requireSafeReplicaSize`, `subFailureDomain`, `targetSizeRatio`, and `hybridStorage`.
- pool `mirroring` with `enabled`, `mode` enum `pool`, `image`, or `init-only`, peer secret names, and snapshot schedules.
- `metadataServer.activeCount`, required and constrained from `1` to `50`, plus `activeStandby`, pod annotations/labels, cache memory factors from `0` to `1`, liveness/startup probes, placement, priority class, and resources.
- filesystem-level `mirroring` with peer secrets, snapshot retention, and snapshot schedules.
- deletion behavior switches `preserveFilesystemOnDelete`, `preservePoolsOnDelete`, and `preservePoolNames`.
- filesystem-level `statusCheck.mirror`.

The visible `CephFilesystem.status` starts with `cephx.daemon`, standard `conditions`, and the beginning of `info` as a string map. Later status fields are outside this chunk.

## Control Flow

The runtime flow is Kubernetes and controller driven:

1. Operators install this CRD YAML into the cluster.
2. The Kubernetes API server registers the CRD endpoints, version `v1`, schema validation, printer columns, and status subresources.
3. Users or automation create resources such as `CephCOSIDriver`, `CephFilesystemMirror`, or `CephFilesystem`.
4. The API server validates submitted `spec` values against this schema, including required fields, enum values, numeric bounds, list/map semantics, and `x-kubernetes-int-or-string` quantities.
5. Rook controllers watch these custom resources and reconcile Kubernetes workloads and Ceph state from the accepted `spec`.
6. Controllers write observed health, phase, conditions, generation, CephX key generation, and other controller-owned fields to `status`.

Within this YAML chunk, control flow is declarative. There are no loops or branches implemented here; the behavioral branching happens in Kubernetes validation machinery and Rook reconcilers that consume these API objects.

For `CephCluster`, this chunk mainly supports reconcile decisions about OSD scheduling, PVC-backed storage, device set rollout concurrency, upgrade health requirements, and cluster health/status reporting.

For `CephCOSIDriver`, the key reconcile decision is `deploymentStrategy`: never deploy, automatically deploy when appropriate, or always deploy. The image and placement/resource fields parameterize the generated driver deployment.

For `CephFilesystemMirror`, the spec drives creation and scheduling of `cephfs-mirror` pods, while status reports phase and CephX key state.

For `CephFilesystem`, the spec drives creation of Ceph pools, CephFS volumes, MDS daemon deployments, filesystem mirroring schedules, peer configuration, and deletion/preservation behavior.

## State And Persistence Behavior

The persistent state is stored in Kubernetes custom resources. User-owned desired state lives under `spec`; controller-owned observed state lives under `status`.

Important persistence boundaries:

- CRDs themselves persist API shape in the Kubernetes API server.
- `CephCluster.status` persists health summaries, capacity, Ceph daemon version counts, CephX key generation metadata, storage status, and version information.
- `CephFilesystemMirror.status` persists phase, observed generation, conditions, and CephX daemon key metadata.
- `CephFilesystem.status` begins persisting CephX daemon key metadata, conditions, and an `info` string map in this chunk.
- `preserveFilesystemOnDelete`, `preservePoolsOnDelete`, and `preservePoolNames` are durable deletion semantics. They can cause Ceph-side pools/filesystems or names to survive Kubernetes CR deletion.
- PVC template fields in `CephCluster` storage are durable desired state for storage-backed OSD provisioning. Once actual PVCs/PVs exist, changing templates can have limited or controller-specific effects.
- `x-kubernetes-preserve-unknown-fields` appears on selected maps/objects such as pool `parameters`, resource requirements, status check wrappers, and status. This allows extension-like data to survive API server pruning where the schema permits it.

Status subresources are enabled for the completed CRDs in this chunk. That separates spec updates from status updates and lets controllers update status without taking ownership of user-authored spec.

## Dependencies And Integration Points

Primary dependencies are Kubernetes CRD and OpenAPI v3 schema semantics:

- `apiextensions.k8s.io/v1` CRDs.
- Kubernetes scheduling APIs embedded structurally: affinities, tolerations, topology spread constraints, probes, priority classes, and resource requirements.
- Kubernetes storage APIs embedded structurally: PVC templates, data sources, selectors, access modes, volume mode, storage classes, and volume attributes class names.
- Kubernetes status conventions: `conditions`, `observedGeneration`, `phase`, and `subresources.status`.

Rook/Ceph integration points include:

- Ceph OSD orchestration through `CephCluster.spec.storage`, device sets, OSD update concurrency, and upgrade health gates.
- Ceph daemon image/version reporting through `CephCluster.status.ceph.versions` and `status.version`.
- CephX key rotation tracking through repeated `keyCephVersion` and `keyGeneration` status objects.
- COSI integration through `CephCOSIDriver`, which coordinates Ceph object storage provisioning via COSI driver and sidecar images.
- CephFS mirroring integration through `CephFilesystemMirror` and `CephFilesystem.spec.mirroring`.
- CephFS pool and MDS integration through `CephFilesystem.spec.dataPools`, `metadataPool`, and `metadataServer`.
- Peer secret integration through `peers.secretNames`, used by Rook/Ceph mirroring workflows.

This chunk is generated by `controller-gen.kubebuilder.io/version: v0.19.0`. Changes should generally originate in the Go API type definitions and kubebuilder markers, then regenerate the CRDs, rather than hand-editing the generated YAML.

## Risks And Edge Cases

The chunk starts and ends inside larger CRD schemas. Research for this chunk should not treat line 4552 as the beginning of `CephCluster` or line 9179 as the complete `CephFilesystem` status schema.

The CRD schema validates structure but not all semantic constraints. For example, Ceph pool topology, CRUSH roots, device classes, mirroring peer secret correctness, CephFS snapshot schedule validity, and whether pool settings are safe for a real cluster are enforced by reconcilers, Ceph commands, or operational checks rather than by this YAML alone.

Several fields intentionally allow flexible maps or unknown fields. That is useful for Ceph parameters and controller status evolution, but it weakens API-server validation and increases the chance that typos survive admission until a controller or Ceph command rejects them later.

Deletion preservation flags are high impact. `preserveFilesystemOnDelete` automatically implies preserving pools, and the preserve flags can leave Ceph-side state after the Kubernetes CR is removed. Tests and operational runbooks need to distinguish Kubernetes object cleanup from Ceph data cleanup.

Scheduling schemas are deeply repeated across resources. Any drift in generated placement/probe/resource schemas can affect OSD, COSI driver, cephfs-mirror, and MDS pod scheduling. This is especially sensitive for newer Kubernetes fields such as `matchLabelKeys`, `mismatchLabelKeys`, `minDomains`, and dynamic resource allocation `claims`, because cluster API-server versions may vary.

`metadataServer.activeCount` is required and bounded `1` through `50`. That prevents empty MDS declarations but does not guarantee the Ceph cluster has enough resources or failure domains to support the requested active/standby topology.

Pool replication and erasure-coding fields allow low numeric values, including minimum `0` on some required counts. API acceptance does not necessarily mean Ceph will accept or safely operate the resulting pool; Rook reconcile validation remains important.

Generated CRD edits are fragile. Manual changes can desynchronize the manifest from the Go API types, examples, RBAC expectations, controller assumptions, and generated clients.

## Test Signals

High-signal checks for this chunk are API and controller oriented:

- `kubectl apply --server-side --dry-run=server -f sources/control-plane/rook/deploy/examples/crds.yaml` should validate the generated CRD manifest against the target Kubernetes API server.
- Creating minimal valid custom resources should enforce required fields: `CephFilesystem` should require `spec.dataPools`, `spec.metadataPool`, and `spec.metadataServer.activeCount`; `CephCOSIDriver` and `CephFilesystemMirror` should require `metadata` and `spec`.
- Invalid enum tests should reject unsupported values for `CephCOSIDriver.spec.deploymentStrategy`, pool `compressionMode`, pool mirroring `mode`, erasure-code `algorithm`, erasure-code `stripeUnit`, and OSD store `type`.
- Numeric-bound tests should reject `metadataServer.activeCount` outside `1..50`, `osdMaxUpdatesInParallel` below `1`, cache memory factors outside `0..1`, and replica/failure-domain fields below their declared minima.
- Status subresource tests should confirm controllers can update `status` without changing `spec` for `CephCluster`, `CephFilesystemMirror`, and `CephFilesystem`.
- Printer column tests should confirm `kubectl get cephfilesystem` shows ActiveMDS, Age, and Phase, and `kubectl get cephfilesystemmirror` shows Phase and Age.
- Reconciliation tests should cover COSI deployment strategies, cephfs-mirror pod placement/resources, CephFilesystem pool creation, MDS deployment with liveness/startup probes, mirror peer secret handling, snapshot schedule/retention behavior, and preserve-on-delete semantics.
- Regeneration tests should run the repository's CRD generation path and verify that this manifest remains stable, proving edits were made in source API definitions rather than only in generated YAML.
