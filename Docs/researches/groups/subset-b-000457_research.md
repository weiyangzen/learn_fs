# Research: subset-b-000457

Grouped research for the Rook Ceph operator files in subset `subset-b-000457`. Each file section preserves the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/mirror.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/mirror.go

## Purpose
This file starts and updates the single CephFS mirror daemon deployment managed by `CephFilesystemMirror`. It bridges CR intent to Kubernetes Deployment state, including keyring generation, owner references, rollout annotations, memory validation, and update-or-recreate behavior.

## Important APIs and control flow
The main API is `(*ReconcileFilesystemMirror).start(filesystemMirror)`. It validates mirror pod memory with `controller.CheckPodMemory` using a 512 MiB minimum, builds a dataless daemon config for `rook-ceph-fs-mirror`, generates a CephX keyring, builds the Deployment via `makeDeployment`, annotates the pod template with the CephX secret resource version, sets the CR as controller owner, and records the last-applied hash. It first tries to create the deployment. If it already exists, it calls the package-level `updateDeploymentAndWait` hook, and if that update fails, it deletes and recreates the deployment to handle immutable selector changes.

## State and persistence
Persistent state is Kubernetes state: a Deployment owned by the `CephFilesystemMirror` CR plus a keyring Secret created by `generateKeyring` in adjacent mirror code. The Deployment template annotation `keyring.CephxKeyIdentifierAnnotation` forces restart when the keyring resource version changes. No Ceph on-disk daemon data is persisted by this path.

## Dependencies and integration points
The file depends on Rook controller helpers for labels, data path maps, owner references, keyrings, and deployment update orchestration. It integrates with Kubernetes AppsV1 deployments and with Banzai objectmatcher annotations. It uses `mon.UpdateCephDeploymentAndWait` through a variable for test stubbing.

## Risks and test signals
The delete-and-recreate fallback is operationally important but can briefly remove the daemon. Correctness depends on `makeDeployment` labels remaining compatible with selectors and with the update helper. Test coverage for this file is indirect through `spec_test.go`, which validates the generated pod/deployment shape, but the create/update/recreate branch itself is not directly exercised in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/mirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec.go

## Purpose
This file builds the Kubernetes Deployment and containers for the CephFS mirror daemon. It translates `CephFilesystemMirror` placement, labels, annotations, resources, priority, networking, and cluster image settings into a one-replica Deployment running `cephfs-mirror`.

## Important APIs and control flow
`makeDeployment` creates a pod template with a chown init container, the `fs-mirror` daemon container, daemon volumes, service account, host network or Multus settings, tolerations, placement, and optional log collector sidecar. It sets selector labels with `controller.CephDaemonAppLabels`, applies CR annotations/labels to the pod template and Deployment, and adds Rook/Ceph version labels. `makeChownInitContainer` delegates to `controller.ChownCephDataDirsInitContainer`. `makeFsMirroringDaemonContainer` runs `cephfs-mirror --foreground --name=client.fs-mirror` with daemon flags, env vars, resource requirements, default security context, and daemon volume mounts.

## State and persistence
The Deployment is the durable Kubernetes object. The daemon data path uses `controller.DaemonVolumes` and a dataless data path map supplied by `mirror.go`, so this spec primarily persists configuration through pod template fields and annotations. CR annotations and labels are copied to Kubernetes objects.

## Dependencies and integration points
The file is tightly coupled to Rook Ceph daemon helpers for command flags, security context, labels, volumes, version labels, log collection, and Multus attachment. It also depends on the Ceph cluster spec for image, data directory, network mode, and log collector settings.

## Risks and test signals
Selector and label changes can trigger immutable-field update problems handled by `mirror.go`. The daemon lacks a liveness probe, with a TODO noting that health checking remains incomplete. `spec_test.go` validates volume counts, service account, labels, resources, priority class, and standard pod-template expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec_test.go

## Purpose
This test verifies the Deployment/pod spec produced for the CephFS mirror daemon. It is a focused contract test for `makeDeployment`.

## Important APIs and control flow
`TestPodSpec` builds a fake `CephFilesystemMirror`, `CephCluster` spec, fake controller-runtime client, and `ReconcileFilesystemMirror`, then calls `makeDeployment`. It asserts the Deployment name, daemon volume and mount counts, projected volume source count, default service account, Ceph daemon labels, and the common pod-template suite provided by Rook test helpers.

## State and persistence
The test uses only in-memory runtime objects and a fake client. It does not create real Kubernetes resources or Ceph state. Its persistent signal is the expected shape of generated Kubernetes specs.

## Dependencies and integration points
The test uses Rook's scheme, fake controller-runtime client, Ceph version fixtures, resource quantity APIs, and `test.NewPodTemplateSpecTester`. It checks that mirror resources integrate with Rook's label and pod-template conventions.

## Risks and test signals
Coverage is strong for static Deployment construction but does not cover `start`, keyring generation, Kubernetes create/update behavior, Multus, host networking, or log collector injection. Failures here are likely to indicate label, resource propagation, volume, or service account regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/status.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/status.go

## Purpose
This file centralizes CephFilesystem status updates and mirroring/snapshot-schedule status projection. It keeps CR status synchronized with reconcile phase, info maps, CephX state, mirror health, and snapshot schedule checks.

## Important APIs and control flow
`(*ReconcileCephFilesystem).updateStatus` retries on conflicts, fetches the `CephFilesystem`, initializes status, sets `Phase`, `Info`, optional `ObservedGeneration`, and optional daemon CephX status, then writes status through `reporting.UpdateStatus`. Missing resources are treated as deletion races. `(*mirrorChecker).updateStatusMirroring` fetches the filesystem and replaces status with `toCustomResourceStatus`. `toCustomResourceStatus` builds mirroring and snapshot schedule status structs, stamps `LastChecked` when input lists are non-empty, preserves prior `LastChanged` when possible, always stores error/details text, and preserves phase/info from the current status.

## State and persistence
All state is persisted in the `CephFilesystem.status` subresource. CephX status is nested under `Status.Cephx.Daemon`. Mirroring and snapshot schedule details include timestamps formatted in UTC RFC3339. No external Ceph state is modified.

## Dependencies and integration points
The file depends on controller-runtime clients, Kubernetes conflict retry helpers, Rook reporting status updates, `k8sutil.ObservedGenerationNotAvailable`, and logging helpers. The mirror checker path is an integration point for asynchronous CephFS mirroring inspection.

## Risks and test signals
`toCustomResourceStatus` assumes `currentStatus` is non-nil when preserving `Phase` and `Info`; callers initialize it before use. The function assigns `mirrorStatusSpec.LastChanged` from either previous mirroring status or previous snapshot status, which makes last-change semantics easy to regress. No direct tests for this file appear in the subset, so timestamp preservation and details propagation rely on broader controller tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller.go

## Purpose
This file implements the controller for `CephFilesystemSubVolumeGroup` CRs. It creates, updates, pins, reports, and deletes CephFS subvolume groups, and keeps CSI operator client profile metadata aligned with the subvolume group.

## Important APIs and control flow
`Add` registers a field index on `spec.filesystemName/subvolumeGroupName` and installs the controller. `reconcile` fetches the CR, adds the finalizer, initializes status, waits for a ready `CephCluster`, loads cluster info, handles deletion, detects Ceph version, verifies the referenced `CephFilesystem` is ready, creates or updates the subvolume group, applies pinning through `cephclient.PinCephFSSubVolumeGroup`, updates status to Ready, and creates/updates the CSI client profile. External clusters skip creation/deletion of the Ceph subvolume group but still update status and CSI metadata.

Deletion lists other CRs with the same filesystem/group index. It deletes the Ceph subvolume group only when this is the last CR referencing it. `deleteSubVolumeGroup` treats ENOENT as success and ENOTEMPTY as a guarded failure; if force-delete is requested, it starts a cleanup Job and still returns a wrapped delete error describing cleanup. `cleanup` builds a resource cleanup job configured with subvolume group, filesystem, CSI namespace, and metadata pool. `buildClusterID` returns explicit `spec.clusterID` or a hash of namespace/filesystem/group. `formatPinning` renders status text for export, distributed, random, or default distributed pinning.

## State and persistence
State spans Kubernetes finalizers, CR status, CephFS subvolume groups, CephFS pinning metadata, CSI config/client profile objects, and optional cleanup Jobs. Status stores `Phase`, `ObservedGeneration`, and an info map containing `clusterID` and `pinning`.

## Dependencies and integration points
The controller uses controller-runtime, Rook cluster readiness and finalizer helpers, Ceph CLI client helpers for subvolume group lifecycle and pinning, CSI config helpers, `csiopv1.ClientProfile`, and Rook cleanup-job machinery. It integrates with `CephFilesystem` readiness and external-cluster semantics.

## Risks and test signals
Deletion behavior intentionally avoids deleting shared subvolume groups until the last CR is removed; the field index must match `getSubvolumeGroupName` or shared-reference detection can be wrong. Force cleanup starts asynchronous cleanup but returns an error from deletion, so callers see a failure while cleanup proceeds. Tests cover no-cluster and not-ready requeues, successful creation, external mode CSI update, Multus cluster path, deterministic cluster ID hashing, and pinning formatting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller_test.go

## Purpose
This test file validates key reconciliation paths and helpers for `CephFilesystemSubVolumeGroup`.

## Important APIs and control flow
`TestFilesystemSubvolumeGroupController` builds fake clients, fake Rook clientsets, and mock Ceph executors. It exercises missing cluster and not-ready cluster requeues, filesystem-not-ready requeue, successful subvolume group creation and pinning, CSI config map creation, external-mode CSI config updates without Ceph subvolume creation, and a Multus cluster path. `Test_buildClusterID` verifies deterministic hashed cluster IDs and explicit `spec.clusterID` override. `Test_formatPinning` verifies default distributed pinning and export/distributed/random rendering.

## State and persistence
The tests persist state only in fake Kubernetes clients and mocked clientsets. They create mock monitor secrets, CSI config maps, and CR status updates in memory. Mock executor responses simulate Ceph status, daemon versions, subvolume group create, and pin commands.

## Dependencies and integration points
The tests register Rook and CSI operator API schemes, use Rook test clientsets, `exectest.MockExecutor`, CSI config helpers, and controller-runtime fake clients. They validate integration among CephCluster readiness, CephFilesystem status, Ceph CLI invocation, and CSI config updates.

## Risks and test signals
The tests cover creation and readiness but not deletion, shared subvolume group reference handling, ENOENT/ENOTEMPTY delete errors, force cleanup jobs, or status conflict retries. Mock command matching is narrow, so changes to Ceph command order or arguments can expose integration regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/subvolumegroup/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/config.go

## Purpose
This file generates NFS-Ganesha CephX identities and config text, and manages Kerberos-related Ganesha config stored in RADOS objects. It also provides atomic helper functions for prepending/removing config blocks in RADOS with object locks.

## Important APIs and control flow
Identity helpers derive node IDs, client IDs, config object names, and RADOS URLs. `generateKeyring` creates or rotates a per-daemon `client.nfs-ganesha.<nfs>.<id>` key with monitor read caps and OSD read/write caps scoped to the `.nfs` pool and optional namespace, then writes a Kubernetes Secret. `getGaneshaConfig` returns the base Ganesha config using RADOS recovery, RADOS URLs, RGW identity, and NFSv4 settings. `setRadosConfig` adds or removes Kerberos config according to `nfs.Spec.Security.KerberosEnabled()`.

`setKerberosRadosConfig` writes the Kerberos block into a `kerberos` RADOS object and atomically prepends an include block into the main `conf-nfs.<name>` object. `removeKerberosRadosConfig` atomically removes that include block and deletes the Kerberos object. `atomicPrependToConfigObject` and `atomicRemoveFromConfigObject` create temp files, lock the RADOS object, fetch current content, skip idempotent work, rewrite content, put it back, and unlock with timeout-tolerant logging.

## State and persistence
Persistent state includes Ceph auth users, Kubernetes keyring Secrets, `.nfs` RADOS namespace objects (`conf-nfs.<name>` and `kerberos`), and the contents of Ganesha config in RADOS. Temporary files are local process state and are closed but not explicitly removed.

## Dependencies and integration points
The code depends on Rook Ceph client command wrappers, RADOS lock/unlock helpers, keyring secret store helpers, cluster context, Ceph version data, and NFS security CRD fields. It integrates with CSI/user changes to Ganesha exports by taking RADOS object locks before config mutation.

## Risks and test signals
Atomic config changes depend on exact string containment/replacement; formatting changes can create duplicate include blocks or fail removal. RADOS lock failures block reconciliation, and unlock failures are logged but tolerated because locks have timeouts. Tests in `controller_test.go` and `nfs_test.go` mock RADOS commands indirectly; this file's atomic read/write behavior is not deeply unit-tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/controller.go

## Purpose
This file implements the `CephNFS` reconciler. It watches the CR and owned Deployments, Services, and ConfigMaps, coordinates cluster readiness and upgrades, manages finalizers, validates security, ensures NFS pool/config state, reconciles NFS-Ganesha daemon instances, and updates CR status including CephX rotation state.

## Important APIs and control flow
`Add`, `newReconciler`, `watchOwnedCoreObject`, and `add` install the controller and watches. `Reconcile` delegates to `reconcile` and reports events/status through `reporting.ReportReconcileResult`. `reconcile` fetches the CR, adds a finalizer, initializes empty/CephX status, validates `Spec.Security`, waits for a ready `CephCluster`, loads cluster info, handles deletion by removing Ganesha servers from the grace database and finalizer, waits for Ceph upgrades to finish, forces RADOS pool/namespace to `.nfs` and CR name, validates settings, decides whether CephX keys should rotate, configures the NFS pool, reconciles daemon deployments/services/config maps, and marks Ready with updated CephX status.

`reconcileCreateCephNFS` validates external cluster versions, counts current NFS deployments by labels, scales down if needed, then calls `upCephNFS` for create/update.

## State and persistence
State includes `CephNFS.status`, finalizers, events, `.nfs` pool/application state, Ganesha RADOS objects, per-daemon Deployments, Services, ConfigMaps, keyring Secrets, and Ganesha grace database entries.

## Dependencies and integration points
The reconciler depends on Rook cluster readiness/version helpers, keyring rotation helpers, Ceph command wrappers, Kubernetes clientsets, controller-runtime clients, and event recording. It integrates with `nfs.go` for daemon lifecycle, `config.go` for RADOS config/keyrings, `security.go` for pod security additions, and `spec.go` for Kubernetes resource generation.

## Risks and test signals
The reconciler mutates `cephNFS.Spec.RADOS` in-memory to `.nfs` and the CR name; callers must not assume user-provided RADOS fields survive reconciliation. It blocks during Ceph upgrades for non-external clusters and depends on deployment labels to compute scale-down targets. Tests cover readiness gates, invalid security, one/multiple instances, scale-down, multiple CRs, image override, key rotation, and Ganesha config object naming.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/controller_test.go

## Purpose
This file provides high-level reconciliation tests for the `CephNFS` controller, including lifecycle, scale, multiple CR isolation, image override, security validation, and CephX key rotation.

## Important APIs and control flow
`TestCephNFSController` sets up fake schemes, fake controller clients, mock clientsets, and mock Ceph/RADOS/Ganesha executors. It tests no-cluster and cluster-not-ready requeues, invalid SSSD security validation and event reporting, initial and repeated reconcile for one and three servers, scale-down from three to two and one, two independent CephNFS resources, and custom Ganesha image/pull policy propagation. `TestNFSKeyRotation` stubs Ceph versions and auth responses to verify first reconcile, status retention, brownfield unknown status, key-generation-driven rotation, and no extra rotation. `TestGetGaneshaConfigObject` verifies config object naming.

## State and persistence
All state is fake or mocked: Kubernetes Deployments/Services/ConfigMaps in a test clientset, CR status in a fake controller client, monitor secrets in fake core clientsets, and Ceph/RADOS command behavior from mock executors.

## Dependencies and integration points
The tests depend on Rook fake clientsets, controller-runtime fake clients, fake event recorders, keyring/version hooks, and deployment update stubs. They assert integration across controller status, deployment lifecycle, config maps, services, RADOS command calls, and CephX status.

## Risks and test signals
These tests are broad but still mock away actual RADOS object content, Kubernetes API conflict behavior, and Ceph command semantics. They are strong signals for label selectors, resource naming, scaling, status phase, and CephX generation regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/nfs.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/nfs.go

## Purpose
This file manages concrete NFS-Ganesha daemon lifecycle beneath the `CephNFS` reconciler: creating/updating per-instance ConfigMaps, Deployments, Services, RADOS config objects, keyrings, grace database entries, and scale-down cleanup.

## Important APIs and control flow
`upCephNFS` discovers daemons labeled to skip reconcile, loops over desired active instances (`a`, `b`, `c`, ...), creates/updates the config map, ensures the RADOS config object exists, applies Kerberos RADOS config, generates keyrings, builds and creates/updates the Deployment, creates the Service, and adds the server to the Ganesha grace database. `addRADOSConfigFile` stats and creates `conf-nfs.<name>`. `addServerToDatabase` and `removeServerFromDatabase` wrap `ganesha-rados-grace`. `generateConfigMap` and `createConfigMap` persist generated Ganesha config and return a stable hash. `downCephNFS` deletes Service, ConfigMap, grace DB entry, then Deployment for removed instances. `validateGanesha` checks required name/namespace/RADOS/active fields. `configureNFSPool` creates `.nfs` and enables the `nfs` application.

## State and persistence
State includes Kubernetes ConfigMaps, Deployments, Services, keyring Secrets, `.nfs` pool/application metadata, Ganesha config RADOS objects, Kerberos RADOS config, and grace database records. The config hash is persisted in Deployment pod template annotations.

## Dependencies and integration points
The file integrates Rook controller helpers, Ceph command wrappers, `ganesha-rados-grace`, deployment update machinery, Kubernetes owner references, skip-reconcile labels, and config/security/spec helpers from the same package.

## Risks and test signals
Scale-down deletes service/config before deployment and ignores grace DB remove errors by logging; partial failures can leave stale Ceph-side grace records. `configureNFSPool` unconditionally issues pool create and app enable commands, relying on Ceph idempotency or command behavior. Tests cover config hash stability, multi-instance creation, services, skip-reconcile behavior, and list-failure errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/nfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/nfs_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/nfs_test.go

## Purpose
This file tests lower-level NFS daemon lifecycle helpers, particularly config map hashing, multi-instance resource creation, and skip-reconcile handling.

## Important APIs and control flow
`TestReconcileCephNFS_createConfigMap` verifies repeated generation gives stable hashes, different daemon IDs produce different hashes, and different NFS names/configs produce different hashes. `TestReconcileCephNFS_upCephNFS` calls `upCephNFS` for two active servers and verifies two Deployments and Services with config-hash annotations. `TestUpCephNFS_SkipsReconcile` verifies a daemon deployment labeled with `ceph.rook.io/do-not-reconcile` is skipped. `TestUpCephNFS_SkipReconcileFails` verifies list failures from the Kubernetes clientset surface as errors.

## State and persistence
The tests use fake Kubernetes clientsets and fake controller-runtime clients. Created Deployments, Services, and ConfigMaps are in-memory only. Ceph auth is mocked through `exectest.MockExecutor`.

## Dependencies and integration points
The tests depend on Rook scheme, fake Kubernetes reactors, Rook config labels, Ceph version fixtures, and executor mocks. They validate integration among generated ConfigMaps, Deployment annotations, Services, and skip-reconcile label discovery.

## Risks and test signals
The tests do not exercise RADOS config object creation, Kerberos config mutation, grace database calls, or deployment update fallback in depth. They are good regression signals for deterministic config hashes and basic resource fan-out.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/nfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/security.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/security.go

## Purpose
This file augments NFS-Ganesha pod specs with optional SSSD and Kerberos support. It creates init containers, sidecars, volumes, and mounts needed for identity lookup, nsswitch overrides, generated Kerberos config, keytabs, and additional security files.

## Important APIs and control flow
`addSecurityConfigsToPod` checks `nfs.Spec.Security` and dispatches to SSSD and/or Kerberos helpers. `addSSSDConfigsToPod` always adds a generated `/etc/nsswitch.conf` init container and volume for SSSD, then optionally adds an SSSD sidecar, shared sockets/cache volumes, SSSD config file, additional files, and mounts into the Ganesha container. `addKerberosConfigsToPod` adds generated `krb5.conf` resources, mounts optional Kerberos config files and keytab, and updates the Ganesha container. `generateSssdSidecarResources` builds shared emptyDir volumes, optional config/additional-file volumes, SSSD sidecar, socket-copy init container, and extra Kerberos mounts when both features are enabled. `generateKrbConfResources` creates an init container that writes `krb5.conf` and optional `idmapd.conf`.

## State and persistence
Security state is expressed in pod spec volumes, mounts, init containers, and sidecars. Runtime files live in `emptyDir` volumes, ConfigMap/Secret projected volumes, and generated files mounted with `subPath`.

## Dependencies and integration points
The file depends on CephNFS CRD security types, Rook container lookup helpers, generated volume/mount helpers, cluster image settings, and Kubernetes core pod APIs. It integrates with `spec.go` after base containers are assembled.

## Risks and test signals
The helpers mutate container slices returned by `k8sutil.GetContainerByName`; correctness depends on that helper returning a writable reference into the slice. Volume names are fixed, so collisions with future base volumes would be risky. Shell-generated config content includes user-provided domain name without escaping. Tests cover nil/empty security, SSSD with and without config, resource propagation, volume/mount matching, and default pod preservation; Kerberos detail coverage is stronger in `spec_test.go` than in this file's direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/security.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/security_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/security_test.go

## Purpose
This file tests `addSecurityConfigsToPod` and SSSD-specific pod mutations for CephNFS.

## Important APIs and control flow
Test helpers create base CephNFS objects, a mock reconciler with Ceph image/version, and a mock pod with a Ganesha and dbus container. Tests verify nil and empty security specs add nothing. SSSD tests verify generated nsswitch and socket-copy init containers, SSSD sidecar insertion, volume and mount sets, image selection, resource propagation, optional config-map mount behavior, debug-level args, and preservation of pre-existing pod containers and volumes.

## State and persistence
All state is in-memory Kubernetes pod specs. The tests do not create real ConfigMaps, Secrets, or pods.

## Dependencies and integration points
The tests use CephNFS security CRD structs, Kubernetes resource quantities, Rook container spec testers, and helper functions that extract volume, mount, and container names. They validate integration between security helpers and the base pod structure expected from `spec.go`.

## Risks and test signals
Direct tests focus on SSSD; Kerberos-only and SSSD-plus-Kerberos paths are tested at Deployment level in `spec_test.go`. These tests are sensitive to volume names and resource formatting, making them useful for detecting accidental pod-spec drift.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/security_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/spec.go

## Purpose
This file generates Kubernetes Services, Deployments, containers, probes, labels, and volumes for each CephNFS Ganesha daemon instance.

## Important APIs and control flow
`generateCephNFSService` creates a Service exposing NFS TCP 2049 and metrics 9587, using headless service mode for host networking. `createCephNFSService` creates it with an owner reference and treats already-existing services as success. `makeDeployment` builds the one-replica Deployment with generated Ceph config init container, `nfs-ganesha` daemon container, `dbus-daemon` sidecar, ceph/keyring/ganesha/dbus volumes, host network or Multus settings, placement, priority, stable hostname for Kerberos, config hash annotation, labels, annotations, and security additions. `connectionConfigInitContainer` uses the Ceph cluster image to generate minimal Ceph config and mount keyrings. `daemonContainer` runs `ganesha.nfsd` in foreground with log level, env vars, resources, liveness probe, and config/keyring/dbus mounts. `defaultGaneshaLivenessProbe` uses `rpcinfo` for Ceph >= 18.2.1 and TCP otherwise. `dbusContainer`, image helpers, label helpers, and volume helpers define supporting sidecar and volumes.

## State and persistence
State is Kubernetes resource specification. Config content is mounted from ConfigMaps; Ceph config and dbus sockets use emptyDir; keyrings use Secrets. Deployment annotations carry config hash to trigger rollouts.

## Dependencies and integration points
The file depends on Rook controller helpers for labels, probes, Ceph config init containers, image pull policy, version labels, placement, Multus, and security context. It calls `security.go` to add SSSD/Kerberos pod additions.

## Risks and test signals
In `makeDeployment`, host-network DNS policy is set on `podSpec` after `podTemplateSpec` is created in one branch, so later mutations must be carefully reflected in the template. Service creation does not update existing Services, so port/label changes may not reconcile until deletion. Tests cover base deployment, SSSD, Kerberos, combined security, resource expectations, service account, priority, labels, and liveness probe defaults.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/spec_test.go

## Purpose
This file validates generated CephNFS Deployment specs across base, SSSD, Kerberos, combined security, and liveness-probe cases.

## Important APIs and control flow
`newDeploymentSpecTest` creates a reconciler fixture with fake clients, Ceph version/image, and a daemon config. `TestDeploymentSpec` checks a base deployment's config hash annotation, labels, resource propagation, priority class, and service account. Additional subtests verify SSSD sidecar and init containers, Kerberos init container and absence of SSSD when only Kerberos is set, combined SSSD/Kerberos init and sidecar presence, volume/mount consistency through the pod-template test suite, and default liveness probe properties.

## State and persistence
The tests build Deployment objects in memory without creating them through Kubernetes. The important state is the expected pod template shape and annotations.

## Dependencies and integration points
The test uses Rook fake clientsets, Ceph version fixtures, Rook pod-template tester utilities, Kubernetes resource quantities, and CephNFS CRD security fields. It exercises integration between `spec.go` and `security.go`.

## Risks and test signals
These tests are strong for static pod shape but do not validate Service generation, actual container command execution, host-network/Multus behavior, or custom image pull policy in this file. They catch many regressions involving security mounts, duplicate volumes, resource propagation, and liveness probe defaults.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/connectionconfig.sh -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/connectionconfig.sh

## Purpose
This embedded Bash script runs in the NVMe-oF gateway init container. It writes Ceph connection files, copies the admin keyring, renders `nvmeof.conf` from a ConfigMap template with pod runtime values, and asks Ceph to create/show the gateway.

## Important APIs and control flow
The script enables strict Bash flags, writes `/etc/ceph/ceph.conf` using `ROOK_CEPH_MON_HOST`, copies `/tmp/ceph/keyring` to `/etc/ceph/keyring`, sets file modes, replaces `@@POD_NAME@@`, `@@ANA_GROUP@@`, and `@@POD_IP@@` placeholders from `GATEWAY_NAME`, `ANA_GROUP`, and `POD_IP`, then runs `ceph "$@" nvme-gw create ... || true` and `ceph "$@" nvme-gw show ... || true`.

## State and persistence
It writes generated files into the pod's `/etc/ceph` volume. It also attempts to create/update Ceph NVMe gateway state through the Ceph CLI, but the command failures are ignored by `|| true`.

## Dependencies and integration points
The script is embedded by `spec.go` with `go:embed` and executed by `createCephConfigInitContainer`. It depends on mounted admin keyring, ConfigMap at `/config/nvmeof.conf`, pod IP env injection, Ceph CLI args passed from Rook helpers, and monitor host env vars.

## Risks and test signals
Ignoring `ceph nvme-gw create/show` failures can let the init container succeed even when Ceph-side gateway registration fails. Placeholder substitution is plain `sed`, so values containing sed metacharacters could be problematic. There are no direct shell tests in this subset; behavior is indirectly exercised through generated init-container specs and NVMe-oF controller tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/connectionconfig.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller.go

## Purpose
This file implements the `CephNVMeOFGateway` controller. It watches gateway CRs and owned Deployments/Services, validates gateway specs, manages readiness/finalizers/status, reconciles per-instance gateway Deployments and Services, generates default config maps, and tracks CephX key rotation status.

## Important APIs and control flow
`Add` registers CSI addons and CSI operator schemes, watches the CR, and watches owned Services/Deployments. `reconcile` fetches the CR, adds a finalizer, initializes status, waits for ready `CephCluster`, loads cluster info, handles deletion by removing finalizer, checks running/desired Ceph versions and upgrade state, validates `instances`, `group`, and `pool`, determines CephX key rotation, reconciles resources, and updates Ready status. `reconcileCreateCephNVMeOFGateway` validates external cluster version, counts current deployments by labels, scales down extra instances, and calls `upCephNVMeOFGateway`. `upCephNVMeOFGateway` creates default per-instance ConfigMaps unless `spec.configMapRef` is set, builds deployments, create-or-updates them, and creates Services. `downCephNVMeOFGateway` deletes Deployments and Services for removed indexes. `getNVMeOFGatewayConfig` builds INI config with default gateway/discovery/ceph/mtls/spdk/monitor sections and user overrides. ConfigMap helpers persist generated config and hash it. `updateStatus` writes phase, observed generation, and CephX daemon status with conflict retries.

## State and persistence
State includes `CephNVMeOFGateway.status`, finalizers, events, per-instance Deployments, Services, generated ConfigMaps, pod config hash annotations, CephX status, and Ceph-side NVMe gateway state initialized by the embedded script.

## Dependencies and integration points
The controller depends on Rook cluster readiness/version helpers, keyring status helpers, Kubernetes clients, INI generation, Rook labels/owner refs, and spec helpers. It integrates with Ceph config to discover the NVMe-oF image when the CR omits one, and with CSI/addons schemes for operator-wide API availability.

## Risks and test signals
Scale-down deletes resources in increasing index order from desired count to current count; label count correctness is critical. Custom `configMapRef` leaves config hash empty, so config changes in external ConfigMaps will not automatically roll pods. The controller updates status for key rotation but this subset does not show per-daemon key Secret generation like NFS. Tests cover readiness gates, invalid specs, single/multiple instances, scale down, multiple CRs, CephX status rotation, and config generation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller_test.go

## Purpose
This file tests the NVMe-oF gateway controller's high-level reconcile behavior, CephX key rotation status, and generated gateway configuration.

## Important APIs and control flow
`TestCephNVMeOFGatewayController` builds fake clients, mock executors, and version stubs to exercise no-cluster/not-ready requeues, invalid specs, one gateway, repeated reconcile, three gateways, scale-down to two and one, and two independent gateway CRs. `TestNVMeOFKeyRotation` verifies initial CephX status, retention on subsequent reconcile, brownfield unknown status behavior, key-generation-driven status changes, and no unnecessary repeat rotation. `TestNVMeOFConfigGeneration` validates default INI values and user overrides/new sections. `TestNVMeOFConfigMapGeneration` verifies ConfigMap name, namespace, config key, placeholder pod IP, group, port override, and pool fields.

## State and persistence
Tests use fake Kubernetes clientsets for Services/Deployments/ConfigMaps and fake controller clients for CR/status state. Ceph status, config image lookup, and NVMe gateway commands are mocked.

## Dependencies and integration points
The tests depend on Rook fake clientsets, controller-runtime fake clients, fake event recorders, Ceph version stubs, INI parsing, and mock executors. They validate integration among controller reconciliation, spec generation, config generation, and status reporting.

## Risks and test signals
The tests do not execute the embedded shell script or validate actual Ceph-side NVMe gateway registration. They are strong signals for resource naming, scaling, spec validation, generated INI content, and CephX status transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec.go

## Purpose
This file generates Kubernetes Services, Deployments, init containers, daemon containers, labels, ports, placement defaults, and volumes for Ceph NVMe-oF gateway instances.

## Important APIs and control flow
`getPorts` resolves default or CR-specified IO, gateway, monitor, and discovery ports. `generateCephNVMeOFService` creates a per-instance Service exposing all four ports and uses headless service mode for host networking. `createCephNVMeOFService` creates the Service and treats AlreadyExists as success. `makeDeployment` validates reconciler state, builds a one-replica Deployment with generated Ceph config volume, admin keyring Secret, gateway ConfigMap volume, init container, privileged daemon container, host network/Multus settings, default and user placement, stable DNS hostname when valid, service account `rook-ceph-nvmeof`, labels, annotations, version labels, and config hash annotation. `getDefaultNVMeOFPlacement` adds topology spread by hostname. `createCephConfigInitContainer` embeds `connectionconfig.sh`, passes admin Ceph flags, sets gateway/pool/group/POD_IP env vars, mounts admin keyring, Ceph config, and config map, and runs privileged with SYS_ADMIN and NET_RAW dropped. `daemonContainer` resolves the image from CR or Ceph config, sets `CEPH_ARGS`, exposes ports, runs privileged, configures liveness probes, and mounts generated Ceph config. Helper functions provide default probes, labels, instance names, image lookup, gateway ConfigMap volume, and admin keyring volume/mount.

## State and persistence
State is Kubernetes resource spec plus generated files at pod runtime. Admin keyring is read from Secret `rook-ceph-admin-keyring`; generated Ceph files and rendered `nvmeof.conf` live in pod volumes. Deployment annotations store config hash for rollouts when Rook owns the ConfigMap.

## Dependencies and integration points
The file depends on embedded script support, Rook controller helpers for labels/probes/placement/Multus/version labels, Ceph config helpers for image lookup and default flags, Kubernetes validation for hostnames, and CephNVMeOFGateway CRD fields for ports, resources, placement, annotations, labels, image, and probes.

## Risks and test signals
Both init and daemon containers are privileged with SYS_ADMIN, increasing security sensitivity. Service creation does not update existing Services, so port changes may need manual recreation. If `spec.image` is empty and Ceph config lacks `mgr/cephadm/container_image_nvmeof`, deployment generation fails. Custom ConfigMap refs have empty config hash, so pod rollout is not automatic on config change. Tests for this file are mainly in `controller_test.go`, which verifies config map generation and controller resource lifecycle, but detailed deployment spec coverage appears limited in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec.go -->
