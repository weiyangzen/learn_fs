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
