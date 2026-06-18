# subset-b-000344 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/volumeoptions.go -->
# sources/control-plane/ceph-csi/internal/cephfs/store/volumeoptions.go

Purpose: central CephFS CSI volume and snapshot option builder. It translates CSI request parameters, volume contexts, static PV attributes, CSI IDs, journals, Ceph cluster config, CephFS subvolume metadata, snapshot metadata, topology input, and encryption settings into `VolumeOptions`, `VolumeIdentifier`, `SnapshotIdentifier`, and `SnapshotOption` values used by CephFS controller/node paths.

Important APIs/types/functions: `VolumeOptions` embeds `core.SubVolume` and carries request name, cluster ID, monitors, filesystem/subvolume group/rados namespace, mount options, topology, shallow snapshot state, owner, connection, and optional `util.VolumeEncryption`. Entry points include `NewVolumeOptions()`, `NewVolumeOptionsFromVolID()`, `NewVolumeOptionsFromMonitorList()`, `NewVolumeOptionsFromStaticVolume()`, `NewSnapshotOptionsFromID()`, `GenSnapFromOptions()`, `GetClusterInformation()`, `IsShallowVolumeSupported()`, `IsVolumeCreateRO()`, `IsEncrypted()`, `InitKMS()`, `ConfigureEncryption()`, `CopyEncryptionConfig()`, `Connect()`, `Destroy()`, and `GetFSID()`.

Control flow: create-volume parsing starts with `getVolumeOptions()`, loads cluster information from `util.CsiConfigFile`, extracts `fsName` and optional pool/mounter/mount options/name prefix, initializes KMS, connects to monitors, queries filesystem ID and metadata pool, rejects CephFS topology-constrained provisioning, and, for read-only snapshot-backed shallow volumes, resolves the backing snapshot and validates inherited filesystem/subvolume options. Volume-ID parsing decomposes the CSI ID first to preserve invalid-ID behavior, loads monitors/group/rados namespace, connects with admin credentials, resolves filesystem name and metadata pool, reads journal image attributes, then populates either live subvolume info or backing snapshot paths. Static and monitor-list constructors parse legacy/static volume context values and connect directly.

State and persistence: no durable state is written here directly except through encryption passphrase copy helpers. The file reads persistent state from Ceph-CSI config, OMAP journals (`VolJournal`, `SnapJournal`), CephFS subvolume/snapshot info, Kubernetes owner fields, and KMS backends. `VolumeOptions.conn` is an owned Ceph cluster connection and must be destroyed by callers; `Destroy()` also tears down encryption resources. Snapshot-backed volumes persist inherited metadata by encoding roots such as `.snap/<snapshot>/<uuid>`.

Dependencies and integration points: depends on CSI protobufs, CephFS `core`, CephFS errors, CephFS util `VolumeID`, KMS, common util config/credentials/topology/encryption helpers, Kubernetes owner helpers, and logging. Controller create/delete/expand, node mount, snapshot, clone, and journal regeneration paths consume these option objects.

Risks: this is high-blast-radius request parsing. Required and optional options mix user input with cluster config; mismatched snapshot parents must be rejected to avoid cross-filesystem shallow mounts. `Connect()` is idempotent but error paths must call `Destroy()` to avoid leaked connections. Static/legacy volume paths accept context-supplied roots and monitors, which are sensitive to bad secrets or stale PV contexts. `IsVolumeCreateRO()` returns true if any capability is read-only, which matters for shallow snapshot enablement. KMS handling supports only CephFS file encryption and deliberately rejects unsupported DEK-store patterns.

Test signals: local tests cover read-only access mode detection and shallow-volume eligibility. Additional useful coverage would exercise invalid cluster config, static volume parsing, backing snapshot mismatch errors, journal fallback, KMS configuration, legacy monitor override from secrets, topology rejection, and connection cleanup on mid-constructor errors.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/volumeoptions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/volumeoptions_test.go -->
# sources/control-plane/ceph-csi/internal/cephfs/store/volumeoptions_test.go

Purpose: focused unit tests for CephFS shallow-snapshot and read-only create-volume helpers in `volumeoptions.go`.

Important APIs/types/functions: tests `IsVolumeCreateRO()` and `IsShallowVolumeSupported()` using CSI `VolumeCapability` and `CreateVolumeRequest` fixtures. The cases cover `MULTI_NODE_READER_ONLY`, `SINGLE_NODE_READER_ONLY`, writer modes, volume content sources, and snapshot content sources.

Control flow: each table-driven test runs subtests in parallel. `TestIsVolumeCreateRO` checks whether access modes are classified as read-only. `TestIsShallowVolumeSupported` combines access mode classification with `VolumeContentSource_Snapshot` presence, confirming that volume sources and writer modes do not enable shallow snapshot backing.

State and persistence: no external state, no Ceph cluster, no filesystem, and no KMS dependencies. The tests only construct protobuf objects in memory.

Dependencies and integration points: validates helper behavior consumed by `NewVolumeOptions()` before backing snapshot resolution. It indirectly protects the semantics that shallow CephFS volumes are only allowed for read-only volumes sourced from snapshots.

Risks: coverage is intentionally narrow. It does not check nil requests, nil capabilities inside a request, mixed capability lists where one entry is read-only and another is writable, explicit `backingSnapshot` parameter parsing, or the later snapshot inheritance checks. The test names are somewhat repetitive ("valid access mode"/"Invalid request"), which can make failures less descriptive.

Test signals: useful as a fast signal for regression in access-mode classification. Broader constructor tests with fake Ceph/Journals would be needed to validate the rest of `volumeoptions.go`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/store/volumeoptions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/util/mountinfo.go -->
# sources/control-plane/ceph-csi/internal/cephfs/util/mountinfo.go

Purpose: persists enough node-stage mount information to restore CephFS mounts, especially ceph-fuse mounts, after process or node-plugin restarts. Records live under `/csi/mountinfo`.

Important APIs/types/functions: `NodeStageMountinfo` holds a CSI `VolumeCapability`, secrets, and mount options. `nodeStageMountinfoRecord` is the JSON-friendly wire format containing protojson for the capability. Public helpers are `WriteNodeStageMountinfo()`, `GetNodeStageMountinfo()`, and `RemoveNodeStageMountinfo()`. Internal helpers are `fmtNodeStageMountinfoFilename()`, `toNodeStageMountinfoRecord()`, and `toNodeStageMountinfo()`.

Control flow: writes marshal the CSI capability through `protojson`, embed it in a JSON record with secrets and mount options, then write `nodestage-<volID>.json` with mode `0600`. Reads reverse the process and return `(nil, nil)` for missing files. Removes treat missing files as success.

State and persistence: durable node-local state includes volume capability, mount options, and secrets. The file uses a fixed absolute directory (`/csi/mountinfo`) and does not create it; if the directory is missing, `WriteNodeStageMountinfo()` currently returns nil for `os.IsNotExist(err)`, which means failed persistence is silently ignored when the directory is absent. Secrets are protected by file mode but still exist at rest on the node.

Dependencies and integration points: depends on CSI protobufs, older `github.com/golang/protobuf/proto` bridging, `protojson`, JSON, and OS file APIs. NodeStage/restore logic in CephFS node paths consumes these records.

Risks: silent success on missing directory can hide restore-data loss. JSON corruption, protojson incompatibility, or permission problems surface on read/write. Volume IDs are placed in filenames; callers must ensure IDs are already safe and validated. Secret persistence increases node compromise impact.

Test signals: no tests in this work item. Useful coverage would include write/read/remove round-trips, missing directory behavior, malformed JSON/protojson, file permissions, and secret retention expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/util/mountinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/util/util.go -->
# sources/control-plane/ceph-csi/internal/cephfs/util/util.go

Purpose: tiny CephFS utility definitions shared by CephFS store and node/controller code.

Important APIs/types/functions: defines `type VolumeID string` for CephFS-specific volume identifiers and package variable `RadosNamespace = "csi"` for storing CSI-specific CephFS objects and keys.

Control flow: none beyond package initialization.

State and persistence: `RadosNamespace` is mutable package state, so tests or initialization code can override it. It represents the default namespace used for Ceph-side CSI metadata, not local process persistence.

Dependencies and integration points: `VolumeID` is used by mountinfo filename formatting and CephFS core path helpers. `RadosNamespace` aligns CephFS metadata with Ceph-CSI OMAP/journal conventions.

Risks: global mutable namespace can create cross-test contamination or surprising runtime behavior if changed after objects are constructed. The package does not validate namespace values.

Test signals: no direct tests are needed for the type alias, but code that overrides `RadosNamespace` should restore it to avoid leaking state between tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/validator.go -->
# sources/control-plane/ceph-csi/internal/cephfs/validator.go

Purpose: validates CephFS controller CSI requests before backend work begins, ensuring requests match advertised capabilities and CephFS feature support.

Important APIs/types/functions: methods on `ControllerServer` are `validateCreateVolumeRequest()`, `validateDeleteVolumeRequest()`, and `validateExpandVolumeRequest()`.

Control flow: create validation checks `CREATE_DELETE_VOLUME` capability, non-empty name, non-empty capabilities, rejects block volumes, calls `util.CheckReadOnlyManyIsSupported()`, then validates content source shape. Snapshot sources require a non-empty snapshot ID and return `NotFound` for missing/empty snapshot details per CSI semantics. Volume sources require a valid volume ID. Delete and expand validate controller capability and volume ID; expand also requires `CapacityRange`.

State and persistence: stateless validation only. It reads `cs.Driver` capability state and returns gRPC status errors.

Dependencies and integration points: uses common CSI driver capability validation, common volume-ID validation, read-only support checks, CSI protobufs, and gRPC status codes. It gates CephFS controller create/delete/expand operations.

Risks: subtle CSI code semantics matter: missing source objects intentionally map to `NotFound`, while unsupported data source maps to `InvalidArgument`. The block-volume rejection is a hard CephFS limitation. Capability checks depend on driver initialization being correct.

Test signals: no direct tests in this item. Useful tests would cover all status codes, nil capability entries, unsupported content source types, block rejection, volume clone ID validation, and missing capacity range.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/cephfs/validator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/controller/controller.go -->
# sources/control-plane/ceph-csi/internal/controller/controller.go

Purpose: starts and coordinates Ceph-CSI Kubernetes controller-runtime reconcilers that maintain auxiliary metadata such as PV journals and volume group replication journals.

Important APIs/types/functions: `Manager` interface requires `Add(manager.Manager, Config) error`; `Config` carries driver name, namespace, cluster name, and instance ID. `ControllerList` is the global registration list. `Start()` builds scheme/manager and runs all registered managers through `addToManager()`.

Control flow: `Start()` creates a runtime scheme with core Kubernetes and CSI-addons replication APIs, configures leader election using `<driverName>-<namespace>` leases, disables metrics, disables cache for full PV and Secret objects, gets in-cluster/rest config, switches content type to protobuf, creates the controller manager, registers all controllers, and blocks in `mgr.Start()` with signal handling.

State and persistence: process-global `ControllerList` is populated by package `Init()` functions. Kubernetes leader-election leases persist in the configured namespace. The manager uses API server state; PV/Secret caching is deliberately disabled to reduce memory in large clusters.

Dependencies and integration points: integrates controller-runtime, client-go scheme/rest config, CSI-addons replication CRDs, Kubernetes core API, and Ceph-CSI controller packages that append to `ControllerList`.

Risks: global registration order and repeated `Init()` calls can duplicate controllers. `GetConfigOrDie()` exits on config failure. Leader election ID depends on namespace and driver name, so misconfiguration can cause multiple active controllers or unwanted contention. Missing CRD handling is delegated to individual controllers.

Test signals: no direct tests here. Useful integration checks would start a fake manager with registered managers, verify cache disable configuration, and ensure each controller handles missing optional CRDs gracefully.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/controller/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/controller/persistentvolume/persistentvolume.go -->
# sources/control-plane/ceph-csi/internal/controller/persistentvolume/persistentvolume.go

Purpose: controller-runtime reconciler for Kubernetes `PersistentVolume` objects. It regenerates or repairs Ceph-CSI metadata/journal entries when PVs exist but backend OMAP metadata needs to be restored.

Important APIs/types/functions: `ReconcilePersistentVolume` owns a controller-runtime client, `ctrl.Config`, and an `IDLocker`. Public registration uses `Init()` and `Add()`. Key functions are `Reconcile()`, `reconcilePV()`, `newPVReconciler()`, `shouldReconcileBasedOnDriver()`, `add()`, `getCredentials()`, and `checkStaticVolume()`.

Control flow: watch predicates accept create/update/generic events for PVs not deleting and either missing `pv.kubernetes.io/provisioned-by` or matching this driver. Reconcile fetches the PV, skips missing/deleting objects, then `reconcilePV()` verifies CSI driver, claim binding, and non-static volume. It selects controller-expand or node-stage secret refs, serializes by volume handle, fetches user credentials from the secret, then dispatches by PV attributes: CephFS PVs have `fsName` and call `cephfsstore.SetSubVolCSIMetadata()`, while RBD PVs call `rbd.RegenerateJournal()` and logs if the handler changes.

State and persistence: writes or repairs Ceph-side OMAP/journal/subvolume metadata. Reads Kubernetes PVs and Secrets. Per-volume in-process locks prevent concurrent repair for the same handle, while controller concurrency is also set to one.

Dependencies and integration points: uses controller-runtime metadata watches, Kubernetes PV/Secret APIs, CephFS store metadata, RBD journal regeneration, common credentials, and controller config cluster/instance IDs.

Risks: missing secret refs produce hard errors. Driver detection for CephFS relies on `fsName` in volume attributes. Static volumes are skipped, so stale metadata for static PVs is intentional. The missing provisioner annotation path reconciles all such PVs, which is conservative for deleted annotations but can process unrelated objects until CSI driver check stops them.

Test signals: unit coverage exists for `shouldReconcileBasedOnDriver()` only. Additional tests should cover secret selection, static skip, CephFS/RBD dispatch, lock contention, missing claim ref, and fake-client reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/controller/persistentvolume/persistentvolume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/controller/persistentvolume/persistentvolume_test.go -->
# sources/control-plane/ceph-csi/internal/controller/persistentvolume/persistentvolume_test.go

Purpose: unit tests for the PV reconciler event-filter helper `shouldReconcileBasedOnDriver()`.

Important APIs/types/functions: `Test_shouldReconcileBasedOnDriver()` constructs `client.Object` inputs using `corev1.PersistentVolume` metadata and compares expected boolean decisions.

Control flow: table cases cover nil object, deletion timestamp, missing annotation, matching provisioner annotation, and non-matching provisioner annotation. All subtests run in parallel.

State and persistence: in-memory Kubernetes object metadata only.

Dependencies and integration points: protects the predicate used by the PV controller's metadata watch in `add()`. The missing-annotation case documents intended reconciliation of PVs where the provisioner annotation was removed.

Risks: does not cover update/delete/generic predicate wrappers, full reconcile behavior, nil annotation map, or CSI driver mismatch inside `reconcilePV()`. It validates only the first filter gate.

Test signals: good quick signal for event filtering regressions. Fake controller-runtime tests are still needed for full PV journal repair behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/controller/persistentvolume/persistentvolume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/controller/volumegroup/volumegroupreplicationcontent.go -->
# sources/control-plane/ceph-csi/internal/controller/volumegroup/volumegroupreplicationcontent.go

Purpose: controller-runtime reconciler for CSI-addons `VolumeGroupReplicationContent` objects. It regenerates RBD volume group replication journal metadata from Kubernetes CR state and referenced secrets.

Important APIs/types/functions: `ReconcileVGRContent` owns a Kubernetes client, controller config, and `IDLocker`. Registration functions are `Init()`, `Add()`, `newVGRContentReconciler()`, `ensureCRDsInstalled()`, and `add()`. Reconciliation helpers are `Reconcile()`, `getSecrets()`, and `reconcileVGRContent()`.

Control flow: `add()` first checks that both `VolumeGroupReplicationContent` and `VolumeGroupReplicationClass` CRDs are installed via the RESTMapper; if absent, it logs and skips controller creation. The controller watches `VolumeGroupReplicationContent`. Reconcile fetches the object, ignores not-found and deleting objects, then `reconcileVGRContent()` filters by provisioner, validates non-empty group handle, locks by handle, resolves attributes and secret references either from the object or fallback `VolumeGroupReplicationClass` parameters for older CRDs, loads secret data, creates an RBD manager, and calls `RegenerateVolumeGroupJournal()`.

State and persistence: reads Kubernetes CRs, classes, and Secrets; writes/repairs Ceph-side RBD volume group journal metadata. In-process locks serialize one group handle at a time.

Dependencies and integration points: depends on CSI-addons replication API types, controller-runtime, Kubernetes secrets, RBD manager/journal logic, and controller config driver/instance IDs. Annotations `replication.storage.openshift.io/group-replication-secret-name` and `...-namespace` carry secret references in newer CRD flows.

Risks: missing annotations or class parameters cause secret lookup failures. CRD absence silently disables the controller after logging, so deployments must monitor logs. Older/newer CRD compatibility branches need to stay aligned with API evolution. Lock errors are returned and may be retried by controller-runtime.

Test signals: no direct tests in this item. Useful coverage would fake RESTMapper CRD absence/presence, fallback class lookup, missing secret annotations, provisioner filtering, and journal regeneration calls.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/controller/volumegroup/volumegroupreplicationcontent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/cephfs/identity.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/cephfs/identity.go

Purpose: CSI-addons identity service implementation for the CephFS driver.

Important APIs/types/functions: `IdentityServer` embeds `identity.UnimplementedIdentityServer` and stores `*util.Config`. `NewIdentityServer()`, `RegisterService()`, `GetIdentity()`, `GetCapabilities()`, and `Probe()` implement the service.

Control flow: registration binds the server to a gRPC registrar. `GetIdentity()` returns configured driver name and `util.DriverVersion`. `GetCapabilities()` builds capabilities based on process role: controller mode advertises controller service and network fence; node mode advertises network fence get-clients. `Probe()` always returns ready true.

State and persistence: stateless apart from the immutable config pointer. No backend calls are made.

Dependencies and integration points: integrates CSI-addons identity protobufs, gRPC registration, and Ceph-CSI runtime config. Capabilities gate what CSI-addons sidecars/operators expect from CephFS endpoints.

Risks: capability accuracy depends on `IsControllerServer` and `IsNodeServer` config. There is no nil-config guard, so construction must pass a valid config. Probe is optimistic and does not check backend readiness.

Test signals: no direct tests here. Useful tests would validate exact capability sets for controller-only, node-only, combined, and neither-role configurations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/cephfs/identity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/cephfs/network_fence.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/cephfs/network_fence.go

Purpose: CephFS CSI-addons fence controller facade. It validates requests, constructs credentials and shared network fence objects, and exposes fence/unfence/get-clients RPCs for CephFS.

Important APIs/types/functions: `FenceControllerServer` stores `enableFencing`. Public functions are `NewFenceControllerServer()`, `RegisterService()`, `FenceClusterNetwork()`, `UnfenceClusterNetwork()`, and `GetFenceClients()`. Local `validateNetworkFenceReq()` checks CIDRs and `clusterID`.

Control flow: fence/unfence reject empty CIDRs or missing cluster ID, create admin credentials from request secrets, construct `networkfence.NetworkFence`, and call either `AddClientEviction()` for fencing or `RemoveNetworkFence()` for unfencing. Get-clients delegates to shared `networkfence.GetFenceClients()` with the server's auto-fencing flag.

State and persistence: no local persistence. Backend effects are CephFS client eviction and OSD blocklist changes performed by the shared networkfence package. Credentials create temporary key files and are deleted with `defer`.

Dependencies and integration points: depends on CSI-addons fence protobufs, gRPC, common credentials, gRPC status codes, and shared `internal/csi-addons/networkfence`. CephFS differs from RBD by using admin credentials and evicting active MDS clients before adding the blocklist.

Risks: validation only checks CIDR presence, not CIDR syntax; syntax errors surface later. Admin credentials are required. `enableFencing` only affects get-clients auto-unfence behavior, not explicit fence/unfence RPCs. Error mapping is mostly `Internal` after validation.

Test signals: tests only verify invalid empty requests return errors. Additional coverage should mock shared fence construction and check credential/error code behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/cephfs/network_fence.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/cephfs/network_fence_test.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/cephfs/network_fence_test.go

Purpose: minimal smoke tests for CephFS CSI-addons network fence RPC validation.

Important APIs/types/functions: `TestFenceClusterNetwork()` and `TestUnfenceClusterNetwork()` instantiate `NewFenceControllerServer(true)` and call RPCs with empty parameters, nil secrets, and nil CIDRs.

Control flow: both tests expect an error before any Ceph backend work is attempted, relying on `validateNetworkFenceReq()` to reject empty CIDRs/missing cluster ID.

State and persistence: no Ceph state, no filesystem state, and no socket state. Tests run fully in memory.

Dependencies and integration points: verifies the CephFS wrapper rejects malformed CSI-addons fence requests without needing a cluster.

Risks: tests do not validate successful request construction, admin credential handling, shared network fence calls, auto-unfence get-client behavior, or exact gRPC status codes.

Test signals: useful as a low-cost guard against accidentally accepting empty fence/unfence requests. It is not a behavioral test for fencing.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/cephfs/network_fence_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/networkfence/fencing.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/networkfence/fencing.go

Purpose: shared implementation of CSI-addons network fencing for CephFS and RBD. It converts CSI-addons CIDR requests into Ceph OSD blocklist changes, evicts matching CephFS clients, reports the local client CIDR for fencing, and optionally auto-unfences recently blocklisted clients.

Important APIs/types/functions: `NetworkFence` holds CIDRs, monitors, and credentials. Public functions include `NewNetworkFence()`, `AddClientEviction()`, `AddNetworkFence()`, `RemoveNetworkFence()`, `GetCIDR()`, `GetFenceClients()`, `autoUnfenceClientOnMatch()`, `containsMatchingBlockListEntry()`, and `matchEntry()`. Helpers include `listActiveClients()`, `evictCephFSClient()`, `getIPRange()`, `incIP()`, `activeClient.fetchIP()`, and `activeClient.fetchID()`.

Control flow: construction validates CIDR list, resolves `clusterID` to monitors, and stores credentials. `AddClientEviction()` lists active MDS clients via `ceph tell mds.0 client ls`, parses client IP/ID, evicts clients inside requested CIDRs, then calls `AddNetworkFence()`. Add/remove blocklist operations first try range-capable Ceph commands; on "invalid command" they fall back to expanding CIDRs into individual IP entries. `GetFenceClients()` connects to the cluster with user credentials, obtains FSID and client address, converts it to a single-host CIDR, and, if enabled, removes a matching short-lived blocklist entry after cooldown. Auto-unfence queries OSD blocklist through go-ceph and matches Ceph's `:0/32` or bracketed IPv6 `:0/128` formats.

State and persistence: durable backend state is Ceph OSD blocklist entries and CephFS MDS client eviction. The package reads cluster identity, client addresses, OSD blocklist contents, and active MDS client JSON. Cooldown decisions are time-based using `util.AutoBlocklistTime` and a fixed five-minute period.

Dependencies and integration points: used by both CephFS and RBD CSI-addons fence controllers. It depends on Ceph command execution for MDS client operations, common Ceph blocklist utility functions, go-ceph OSD admin APIs, common client-IP parsing/CIDR conversion, and gRPC status codes for `GetFenceClients()`.

Risks: expanding large CIDRs can be expensive and dangerous if range commands are unsupported. Fallback detection depends on matching "invalid command" in error text. The active client list always targets MDS rank 0. Auto-unfence timing is subtle: entries just created within cooldown return an error, while older short-lived entries are removed. Address parsing must handle IPv4, IPv6, and Ceph messenger prefixes. Blocklist removal for individual IPs uses nonce `"0"` and assumes Ceph matching semantics.

Test signals: tests cover CIDR expansion, client IP/ID parsing, blocklist match/cooldown behavior, and IPv4/IPv6 match suffix parsing. They do not mock Ceph CLI, OSD admin calls, or end-to-end blocklist add/remove.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/networkfence/fencing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/networkfence/fencing_test.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/networkfence/fencing_test.go

Purpose: unit tests for pure helper behavior in the shared network fence package.

Important APIs/types/functions: tests `getIPRange()`, `activeClient.fetchIP()`, `activeClient.fetchID()`, `containsMatchingBlockListEntry()`, and `matchEntry()`. Fixtures use go-ceph OSD blocklist entries and common `util.AutoBlocklistTime`/`MaxBlocklistTime`.

Control flow: CIDR tests assert full host expansion for small IPv4/IPv6 ranges. Client parsing tests cover standard CephFS client strings, IPv6 bracket strings, `v1:` messenger prefixes, empty strings, and ID parsing. Blocklist tests evaluate matching entries outside cooldown, inside cooldown, absent matches, long max-duration fences, and IPv6 entries. `matchEntry()` tests exact Ceph suffix handling for `:0/32` and `:0/128`.

State and persistence: entirely in memory, except time-sensitive entries use `time.Now()` relative deadlines.

Dependencies and integration points: protects parsing and policy used by both CephFS and RBD network fence RPCs, especially auto-unfence behavior.

Risks: time-based tests near boundary values could become flaky if execution delays are large, though the windows are minutes/hours. Tests do not cover huge CIDRs, invalid CIDR input for `getIPRange()`, Ceph command fallback, or actual go-ceph blocklist remove calls.

Test signals: strong helper-level coverage for parsing and cooldown decisions. End-to-end cluster or mocked admin tests would be needed for operational blocklist behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/networkfence/fencing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/encryptionkeyrotation.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/encryptionkeyrotation.go

Purpose: CSI-addons encryption key rotation controller for RBD volumes.

Important APIs/types/functions: `EncryptionKeyRotationServer` embeds the unimplemented CSI-addons encryption key rotation controller, stores driver instance and volume lock, and exposes `NewEncryptionKeyRotationServer()`, `RegisterService()`, and `EncryptionKeyRotate()`.

Control flow: `EncryptionKeyRotate()` validates volume ID, acquires the per-volume lock, creates an RBD manager from driver instance and request secrets, resolves the RBD volume by CSI ID, maps not-found/pool-not-found errors to `NotFound`, calls `RotateEncryptionKey()`, and returns an empty success response.

State and persistence: backend state is the RBD volume encryption key/passphrase metadata managed by lower RBD layers and KMS. This file only coordinates locking and RPC error mapping. Manager and volume handles are destroyed with defers.

Dependencies and integration points: depends on CSI-addons encryptionkeyrotation protobufs, RBD manager/volume APIs, RBD error sentinels, common ID validation, IDLocker, and logging. It is advertised by RBD CSI-addons identity when running as a node server.

Risks: no explicit check that the volume is encrypted before invoking lower-level rotation. Lock contention maps to `Aborted`. Credentials and KMS errors collapse mostly to `Internal`, so callers need logs for detail. Correctness depends on `RotateEncryptionKey()` atomicity.

Test signals: no direct tests in this item. Useful coverage would mock manager/volume lookups, lock contention, invalid IDs, not-found mapping, and rotation failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/encryptionkeyrotation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/identity.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/identity.go

Purpose: CSI-addons identity service implementation for the RBD driver, advertising RBD-specific addon capabilities.

Important APIs/types/functions: `IdentityServer` stores `*util.Config` and implements `NewIdentityServer()`, `RegisterService()`, `GetIdentity()`, `GetCapabilities()`, and `Probe()`.

Control flow: `GetIdentity()` returns driver name and `util.DriverVersion`. `GetCapabilities()` appends controller capabilities when `IsControllerServer` is true: controller service, offline reclaim space, network fence, volume replication, volume group, do-not-delete-volume-group-volumes, one-group limit, modify volume group, and get volume group. When `IsNodeServer` is true it appends node service, online reclaim space, encryption key rotation, and get-clients-to-fence. Probe always reports ready.

State and persistence: stateless except config. No Ceph connection is attempted.

Dependencies and integration points: integrates CSI-addons identity API and controls what external CSI-addons operators attempt against the RBD controller/node sockets.

Risks: advertised capability drift is high impact because operators may call unsupported RPCs or miss supported ones. Probe is not a backend health check. Nil config is not guarded.

Test signals: no direct tests here. Useful tests should snapshot controller/node capability lists and ensure future changes are intentional.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/identity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/network_fence.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/network_fence.go

Purpose: RBD CSI-addons fence controller facade. It validates network fence requests and delegates blocklist/get-client behavior to the shared networkfence package.

Important APIs/types/functions: `FenceControllerServer` with `enableFencing`, `NewFenceControllerServer()`, `RegisterService()`, `FenceClusterNetwork()`, `UnfenceClusterNetwork()`, `GetFenceClients()`, and local `validateNetworkFenceReq()`.

Control flow: fence/unfence validate non-empty CIDR list and `clusterID`, create user credentials, construct `networkfence.NetworkFence`, and call `AddNetworkFence()` or `RemoveNetworkFence()`. `GetFenceClients()` delegates to shared code with the auto-fencing flag.

State and persistence: no local state beyond the enable flag. Backend state changes are Ceph OSD blocklist entries. Credentials create temporary files and are deleted after RPC execution.

Dependencies and integration points: integrates CSI-addons fence protobufs, shared networkfence, common credentials, and gRPC status codes. Unlike CephFS, RBD fencing does not evict MDS clients and uses user credentials for explicit fence calls.

Risks: same validation limitations as CephFS wrapper; CIDR syntax is not checked until shared code. `NewUserCredentials()` errors in fence map to `Internal`, while unfence maps credential errors to `InvalidArgument`, an inconsistency that callers may observe. Large CIDR fallback risks live in the shared package.

Test signals: wrapper tests assert invalid requests return errors. More coverage should verify credential error code consistency and shared package invocation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/network_fence.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/network_fence_test.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/network_fence_test.go

Purpose: minimal smoke tests for RBD CSI-addons fence and unfence request validation.

Important APIs/types/functions: `TestFenceClusterNetwork()` and `TestUnfenceClusterNetwork()` instantiate `NewFenceControllerServer(true)` and send empty requests.

Control flow: both tests expect errors from validation before credentials or Ceph calls are reached.

State and persistence: none; all objects are in-memory protobufs.

Dependencies and integration points: protects the RBD fence wrapper from accepting empty CIDR/parameter requests.

Risks: does not inspect gRPC status codes or successful paths. It does not cover `GetFenceClients()`, credential handling, or shared networkfence behavior.

Test signals: basic invalid-input guard only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/network_fence_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/reclaimspace.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/reclaimspace.go

Purpose: CSI-addons reclaim space implementation for RBD, supporting offline controller-side sparsify and online node-side filesystem trim.

Important APIs/types/functions: `ReclaimSpaceControllerServer` exposes `ControllerReclaimSpace()` with driver instance and volume locks. `ReclaimSpaceNodeServer` exposes `NodeReclaimSpace()` with volume locks. Constructors and `RegisterService()` functions bind both services.

Control flow: controller reclaim validates volume ID, locks by ID, resolves the RBD volume through a manager, calls `Sparsify()`, treats `ErrImageInUse` as a no-op success, and maps other failures to gRPC errors. Node reclaim validates ID, locks, selects staging target path plus `/<volumeID>` or volume path, rejects multi-node capabilities and all block mode, then executes `fstrim <path>`.

State and persistence: controller-side effects are RBD image sparsification. Node-side effects are filesystem discard/TRIM on a mounted path. No local state is persisted. Locks prevent concurrent reclaim for the same volume in-process.

Dependencies and integration points: depends on CSI-addons reclaimspace protobufs, common CSI capability helpers, RBD manager/volume APIs, common command execution, and error sentinels. Identity advertises offline reclaim on controller and online reclaim on node.

Risks: `ErrImageInUse` is intentionally swallowed due to CSI-addons behavior, so offline reclaim may report success without space recovery. Node path construction assumes the driver's staging layout. Multi-node and block-mode rejection prevents corruption but may surprise users. `fstrim` availability and permissions are host-dependent.

Test signals: minimal tests cover invalid empty requests. Additional tests should cover path selection, multi-node/block rejection, lock contention, in-use no-op behavior, and command execution failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/reclaimspace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/reclaimspace_test.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/reclaimspace_test.go

Purpose: smoke tests for invalid reclaim-space requests without requiring a Ceph cluster or mounted filesystem.

Important APIs/types/functions: `TestControllerReclaimSpace()` creates a controller server with a new ID locker and sends an empty volume ID. `TestNodeReclaimSpace()` creates a node server and sends an empty volume ID/path/capability request.

Control flow: both tests expect errors from early validation.

State and persistence: no backend state or local mount state.

Dependencies and integration points: validates that reclaim-space RPCs fail fast for malformed required fields.

Risks: no coverage for success, in-use controller no-op, `fstrim`, capability rejection, or exact status codes.

Test signals: basic invalid-input guard only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/reclaimspace_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/replication.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/replication.go

Purpose: CSI-addons RBD volume replication controller. It implements enable/disable/promote/demote/resync/info workflows over RBD image mirroring and maps RBD mirror state into CSI-addons responses.

Important APIs/types/functions: `ReplicationServer` embeds CSI-addons unimplemented controller and the core RBD `ControllerServer`. Main RPCs are `EnableVolumeReplication()`, `DisableVolumeReplication()`, `PromoteVolume()`, `DemoteVolume()`, `ResyncVolume()`, and `GetVolumeReplicationInfo()`. Helpers include `getForceOption()`, `getFlattenMode()`, `getMirroringMode()`, `validateSchedulingDetails()`, `validateSchedulingInterval()`, `getSchedulingDetails()`, `checkRemoteSiteStatus()`, `timestampToString()`, `timestampFromString()`, `getGRPCError()`, `checkVolumeResyncStatus()`, `getCurrentReplicationStatus()`, and `checkVolumeUnpublished()`.

Control flow: all RPCs extract volume ID through `csicommon.GetIDFromReplication()`, create credentials, lock the volume, resolve the RBD volume through a manager, convert it to a mirror object, inspect mirror state, and perform the requested transition. Enable validates scheduling and flatten mode, flattens parent image if required, and enables snapshot or journal mirroring. Disable parses force and delegates disabling only when enabled. Promote requires enabled mirroring, promotes secondary images, handles busy promotion as failed precondition, and adds snapshot scheduling after promotion. Demote checks unpublished metadata before demoting primary images and stores `.rbd.image.creation_time` metadata for later resync detection. Resync requires a demoted enabled image, checks local/remote mirror status readiness, uses saved creation time plus force/not-syncing conditions to invoke `Resync()`, repairs image ID when ready, and returns readiness. Info requires a primary enabled image, fetches remote last-sync info, and maps mirror status to CSI-addons health.

State and persistence: mutates RBD mirroring state, snapshot schedules, image metadata, image IDs, and possibly parent flattening. Uses in-process volume locks and lower-layer manager/volume lifecycle. Persistent metadata key `.rbd.image.creation_time` is deliberately hidden from replication.

Dependencies and integration points: depends on go-ceph RBD/admin mirror APIs, CSI-addons replication protobufs, common CSI middleware ID extraction, RBD manager/types/errors, core RBD controller metadata keys, util credentials/locks, and gRPC status codes.

Risks: this file encodes a complex distributed state machine. Incorrect readiness detection can mark resync complete too early or force unnecessary resync. Demotion depends on node metadata cleanup to prove unpublished state. Error mapping determines operator retry behavior. Snapshot scheduling is only valid for snapshot mirroring; journal mode ignores scheduling parameters. Parent flattening behavior can be expensive. The nil-error path in `getGRPCError()` returns a status error with OK code and message, which is unusual but tested.

Test signals: helper tests cover schedule validation, schedule extraction, resync status parsing, remote readiness, gRPC error mapping, timestamp parsing, flatten mode, and status mapping. Cluster-backed or mocked tests are still needed for RPC transition behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/replication.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/replication_test.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/replication_test.go

Purpose: unit tests for helper logic that supports the RBD CSI-addons replication state machine.

Important APIs/types/functions: tests `validateSchedulingInterval()`, `validateSchedulingDetails()`, `getSchedulingDetails()`, `checkVolumeResyncStatus()`, `checkRemoteSiteStatus()`, `getGRPCError()`, `timestampFromString()`, `getFlattenMode()`, and `getCurrentReplicationStatus()`.

Control flow: schedule tests validate `m/h/d` suffixes, snapshot/journal mode behavior, optional start time rules, and default extraction. Resync status tests feed sample go-ceph status descriptions with present/zero/missing local snapshot timestamps. Remote readiness checks local/remote site states and `Up` flags. Error tests validate sentinel-to-gRPC code mapping. Timestamp tests validate round-trip and malformed strings. Status tests map local mirror state/up flags into CSI-addons `HEALTHY`, `DEGRADED`, `ERROR`, or `UNKNOWN` with messages.

State and persistence: pure in-memory fixtures, though time tests use current time values.

Dependencies and integration points: protects behavior that external replication operators depend on for retry/readiness/status decisions.

Risks: no tests exercise the actual RPC methods or RBD manager/mirror calls. Time round-trip compares `time.Time` values including monotonic behavior through `Equal`, which is normally fine but should remain watched if timestamp formatting changes. There is an expected `getGRPCError(nil)` oddity.

Test signals: strong helper coverage for parsing and mapping; missing integration coverage for real mirroring transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/replication_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/volumegroup.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/rbd/volumegroup.go

Purpose: CSI-addons RBD volume group controller implementation for create, delete, membership modification, and get operations.

Important APIs/types/functions: `VolumeGroupServer` stores driver instance and implements `NewVolumeGroupServer()`, `RegisterService()`, `CreateVolumeGroup()`, `DeleteVolumeGroup()`, `ModifyVolumeGroupMembership()`, and `ControllerGetVolumeGroup()`.

Control flow: create resolves all requested volume IDs, reuses an existing group from the first volume if present, validates all volumes are in the same group, creates or resolves the backend group, verifies existing group membership, optionally flattens parent images using `getFlattenMode()`, adds volumes when the group is empty, converts the group to CSI form, and copies request parameters into the volume group context. Delete resolves the group, treats not-found as idempotent success, refuses non-empty groups with `FailedPrecondition`, and deletes empty groups. Modify resolves the group, lists current volumes, computes remove/add sets by CSI ID, removes absent volumes, resolves and flattens new volumes, adds them, and returns CSI group state. Get resolves and converts the group, returning `NotFound` for missing groups.

State and persistence: mutates RBD volume group membership and group existence. It may flatten parent images before adding to groups. No local locks are present in this file, so concurrency control depends on backend idempotency and higher layers.

Dependencies and integration points: uses CSI-addons volumegroup protobufs, RBD manager/types/errors, shared replication helper `getFlattenMode()`, shared `getGRPCError()`, and gRPC status codes. Identity advertises the related volume group capabilities.

Risks: create only adds volumes when the group currently lists zero volumes; if a partially populated group exists, mismatch is detected for reused groups but new groups with unexpected existing members depend on backend behavior. No explicit per-group lock may allow concurrent membership races. Delete refuses non-empty groups because advertised capability says volume group deletion must not delete member volumes. Parameter copying into group context can expose backend parameters to callers.

Test signals: no direct tests in this item. Useful coverage would mock RBD manager/group/volume interfaces for idempotency, partial membership mismatch, delete non-empty behavior, modify diffing, flatten failures, and get missing-group mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/rbd/volumegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/server/server.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/server/server.go

Purpose: standalone gRPC server wrapper for CSI-addons services over Unix domain sockets.

Important APIs/types/functions: `ErrNoUDS`, `CSIAddonsService` interface with `RegisterService()`, `CSIAddonsServer` state (`scheme`, `path`, `server`, `services`), `NewCSIAddonsServer()`, `RegisterService()`, `Start()`, `Stop()`, and `serve()`.

Control flow: construction parses an endpoint URL and accepts only `unix://` schemes. Services are appended before `Start()`. Start creates a gRPC server with common unary middleware, registers each addon service, removes any stale socket path, listens on the Unix socket, and serves asynchronously. Stop gracefully stops the gRPC server if started.

State and persistence: process state includes service list and server pointer. Filesystem state includes the Unix domain socket path, which is removed before listening. No service data is persisted here.

Dependencies and integration points: depends on Go net/url/net/os, gRPC, common CSI middleware, and logging. RBD/CephFS addon services register through this wrapper.

Risks: only unary middleware is configured; stream middleware is not used here. Existing socket path removal can delete a stale or incorrectly configured file. Empty endpoint parsing returns a generic parse/scheme error. `Stop()` before `Start()` is safe.

Test signals: tests cover valid Unix endpoints, empty endpoint, and non-UDS endpoint. Additional tests should cover stale socket removal, listen failures, service registration, and graceful stop.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/server/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/server/server_test.go -->
# sources/control-plane/ceph-csi/internal/csi-addons/server/server_test.go

Purpose: endpoint parsing tests for the CSI-addons Unix socket server constructor.

Important APIs/types/functions: `TestNewCSIAddonsServer()` exercises `NewCSIAddonsServer()`.

Control flow: subtests run in parallel for `unix:///tmp/csi-addons.sock` success, empty endpoint failure, and non-URL/non-UDS endpoint failure.

State and persistence: no socket is created because `Start()` is not called.

Dependencies and integration points: validates the construction gate before addon services bind sockets.

Risks: does not assert error wrapping with `ErrNoUDS`, nor path fields, service list initialization, start/stop behavior, or socket cleanup.

Test signals: fast guard for endpoint scheme handling.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-addons/server/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/controllerserver-default.go -->
# sources/control-plane/ceph-csi/internal/csi-common/controllerserver-default.go

Purpose: default CSI controller and group-controller capability endpoints shared by Ceph-CSI drivers.

Important APIs/types/functions: `DefaultControllerServer` embeds unimplemented CSI controller, group controller, and snapshot metadata servers and stores `*CSIDriver`. Methods are `ControllerGetCapabilities()` and `GroupControllerGetCapabilities()`.

Control flow: each method logs, checks that `Driver` is not nil, then returns the controller or group capability slices stored on the driver. Nil driver maps to `Unimplemented`.

State and persistence: reads in-memory capability state from `CSIDriver`.

Dependencies and integration points: used by driver-specific controller servers to satisfy standard CSI capability RPCs. Capabilities are populated via `CSIDriver.AddControllerServiceCapabilities()` and `AddGroupControllerServiceCapabilities()`.

Risks: if driver capabilities are not initialized, the server returns empty slices and callers may disable behavior. Nil driver is handled, but nil capability entries are not filtered.

Test signals: no direct tests in this item. Capability population tests should verify expected driver-specific values.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/controllerserver-default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/driver.go -->
# sources/control-plane/ceph-csi/internal/csi-common/driver.go

Purpose: shared CSI driver metadata and capability registry for Ceph-CSI driver instances.

Important APIs/types/functions: `CSIDriver` stores name, node ID, version, instance ID, fencing flag, topology, controller capabilities, group capabilities, and volume access modes. Key methods are `NewCSIDriver()`, `GetInstanceID()`, `GetNodeID()`, `IsFencingEnabled()`, `ValidateControllerServiceRequest()`, `AddControllerServiceCapabilities()`, `AddVolumeCapabilityAccessModes()`, `GetVolumeCapabilityAccessModes()`, `AddGroupControllerServiceCapabilities()`, and `ValidateGroupControllerServiceRequest()`.

Control flow: constructor rejects missing name/node/version/instance by logging and returning nil. Add methods convert enum slices into CSI capability protobufs and replace stored slices. Validate methods allow `UNKNOWN`, otherwise scan stored capabilities and return `InvalidArgument` when unsupported.

State and persistence: purely in-memory driver state. Instance ID is used by lower layers to distinguish OMAP/journal namespaces across driver deployments.

Dependencies and integration points: consumed by default identity/controller/node servers and driver-specific validators. Uses CSI protobufs, gRPC status, klog, and common logging.

Risks: constructor returns nil rather than error, so callers must check. Capability slices are replaced, not appended. Validation only checks advertised capabilities, so initialization drift changes request acceptance.

Test signals: no direct tests here. Useful coverage would verify constructor required fields, capability replacement, and validation status codes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/identityserver-default.go -->
# sources/control-plane/ceph-csi/internal/csi-common/identityserver-default.go

Purpose: default CSI identity server implementation shared by Ceph-CSI drivers.

Important APIs/types/functions: `DefaultIdentityServer` embeds `csi.UnimplementedIdentityServer` and stores `*CSIDriver`. Methods are `GetPluginInfo()`, `Probe()`, and `GetPluginCapabilities()`.

Control flow: `GetPluginInfo()` logs and returns driver name/version, rejecting empty values with `Unavailable`. `Probe()` returns an empty response. `GetPluginCapabilities()` always advertises controller service capability.

State and persistence: reads in-memory driver metadata only.

Dependencies and integration points: registered on CSI gRPC servers for all drivers using common identity behavior. The plugin capability influences CO expectations for controller service availability.

Risks: no nil-driver guard before dereferencing `ids.Driver`. Probe does not verify backend readiness. Always advertising controller service may be inappropriate if a node-only deployment uses this default without override.

Test signals: no direct tests. Useful tests would cover missing name/version, nil driver behavior, and plugin capability assumptions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/identityserver-default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/nodeserver-default.go -->
# sources/control-plane/ceph-csi/internal/csi-common/nodeserver-default.go

Purpose: default CSI node server behavior and shared mount option construction.

Important APIs/types/functions: `DefaultNodeServer` embeds `csi.UnimplementedNodeServer` and stores driver, type, mounter, node labels, and read-affinity options. Methods are `NodeGetInfo()`, `NodeGetCapabilities()`, and `ConstructMountOptions()`.

Control flow: `NodeGetInfo()` returns node ID and accessible topology from driver state. `NodeGetCapabilities()` returns a single `UNKNOWN` node capability. `ConstructMountOptions()` appends unique mount flags from the volume capability and appends `ro` when access mode is reader-only.

State and persistence: reads in-memory driver topology and node ID. No persistent state.

Dependencies and integration points: used by driver-specific node servers; `ConstructMountOptions()` feeds mount execution paths. Uses Kubernetes mount-utils and common read-only helper.

Risks: nil driver or nil volume capability can panic in callers if not guarded before use. Returning `UNKNOWN` node capability may be minimal but not descriptive. Mount option dedupe preserves existing slice order and appends only missing flags.

Test signals: read-only helper tests indirectly cover `ro` decision but `ConstructMountOptions()` itself is not directly tested here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/nodeserver-default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/server.go -->
# sources/control-plane/ceph-csi/internal/csi-common/server.go

Purpose: non-blocking standard CSI gRPC server wrapper for identity, controller, node, group controller, and snapshot metadata services.

Important APIs/types/functions: `NonBlockingGRPCServer` interface, `Servers` service bundle, `NewNonBlockingGRPCServer()`, and `nonBlockingGRPCServer` methods `Start()`, `Wait()`, `Stop()`, `ForceStop()`, and `serve()`.

Control flow: `Start()` launches `serve()` in a goroutine and increments a wait group. `serve()` parses `unix://` or `tcp://` endpoints, removes stale Unix socket paths, listens, creates a gRPC server with unary and stream middleware, registers non-nil CSI services, then blocks in `Serve()`. Stop methods call graceful or forceful gRPC stop.

State and persistence: process state includes the gRPC server pointer and wait group. Filesystem state includes Unix socket cleanup and listener. No request state is persisted.

Dependencies and integration points: shared by Ceph-CSI driver binaries. Uses common middleware, CSI protobuf registrations, net/os, gRPC, klog fatal exits, and logging.

Risks: `serve()` calls `klog.Fatal/Fatalf` on parse/listen/serve errors, exiting the process. The server pointer is assigned only inside `serve()` after listener setup; calling stop too early could race with nil pointer. Unix endpoint handling prepends `/` to parsed address, matching existing endpoint format assumptions.

Test signals: no direct tests in this item. Endpoint parsing is tested through utils; server lifecycle would need integration tests with temporary sockets.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/utils.go -->
# sources/control-plane/ceph-csi/internal/csi-common/utils.go

Purpose: shared CSI utility layer for endpoint parsing, default server construction, capability construction, gRPC middleware/logging/restart behavior, request ID extraction, filesystem stats, and access-mode classification.

Important APIs/types/functions: key functions include `parseEndpoint()`, `NewVolumeCapabilityAccessMode()`, `NewDefaultNodeServer()`, `NewDefaultIdentityServer()`, `NewDefaultControllerServer()`, `NewControllerServiceCapability()`, `NewGroupControllerServiceCapability()`, `NewMiddlewareServerOption()`, `NewMiddlewareStreamServerOption()`, `GetIDFromReplication()`, `FilesystemNodeGetVolumeStats()`, `IsBlockMultiNode()`, `IsFileRWO()`, `IsReaderOnly()`, and `IsBlockMultiWriter()`. Internal middleware/helpers include `getReqID()`, `contextIDInjector()`, `wrapperServerStream`, `streamInterceptor()`, `logGRPC()`, `logSlowGRPC()`, `killOnSlowGRPCWithThreshold()`, `panicHandler()`, and `requirePositive()`.

Control flow: middleware chains inject a monotonically increasing context ID, derive request IDs from CSI/replication/volume group requests, log sanitized requests/responses, optionally log slow calls after context cancellation, optionally kill the process when unary handlers exceed ten minutes, and recover panics into internal errors. Stream middleware injects IDs and logs metadata snapshot requests. Filesystem stats verify mountpoint status, use Kubernetes statfs metrics, clamp negative usage values, optionally include inodes, and return a healthy volume condition. Access-mode helpers scan capability lists for block/multi-node/RWO/reader-only/multi-writer properties.

State and persistence: package-level atomic `id` labels requests. Package variable `osExit` is overrideable in tests. No durable state is written. `FilesystemNodeGetVolumeStats()` reads mount and filesystem state.

Dependencies and integration points: used by both standard CSI and CSI-addons servers, RBD replication ID extraction, RBD reclaim-space capability checks, and node stats implementations. Depends on CSI and CSI-addons protobufs, grpc middleware, proto sanitizer, klog/logging, Kubernetes mount-utils and volume metrics.

Risks: request ID extraction must track proto evolution, especially deprecated replication `VolumeId` versus `ReplicationSource`. `killOnSlowGRPC` exits the process for stuck unary calls, with reclaimspace excluded by prefix. Access helpers assume non-nil access modes in some paths (`IsBlockMultiNode()`), so callers must pass well-formed capabilities. Metrics conversion logs but does not fail for unavailable available/used values, while capacity/inodes failures do fail.

Test signals: broad tests cover request IDs, filesystem stats, positive clamping, access-mode helpers, and slow-GRPC restart/exclusion behavior. More tests could cover endpoint parsing, panic recovery, stream interceptor request IDs, and nil capability robustness.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/utils_test.go -->
# sources/control-plane/ceph-csi/internal/csi-common/utils_test.go

Purpose: unit and lightweight integration tests for common CSI utility helpers.

Important APIs/types/functions: tests include `TestGetReqID()`, `TestFilesystemNodeGetVolumeStats()`, `TestRequirePositive()`, `TestIsBlockMultiNode()`, `TestIsFileRWO()`, `TestIsBlockMultiWriter()`, `TestIsReaderOnly()`, and slow-GRPC tests for `killOnSlowGRPCWithThreshold()`.

Control flow: request ID tests construct many CSI, replication, and replication-source protobuf requests and assert `getReqID()` returns the expected fake ID or empty string. Filesystem stats walks up from the package working directory until it finds a mountpoint, then validates byte/inode usage. Access-mode tests build block and mount capabilities for single/multi node, reader, writer, and multi-writer modes. Slow-GRPC tests override package `osExit`, exercise fast/error/stuck handlers, and verify `/reclaimspace.` prefixes do not trigger exit.

State and persistence: mostly in-memory. Filesystem stats reads the local mounted filesystem. Slow-GRPC tests mutate `osExit` and intentionally avoid parallel execution for those cases.

Dependencies and integration points: protects middleware request labeling, node stats, RBD reclaim capability gating, CephFS read-only helpers, and process-restart safeguards.

Risks: filesystem stat test depends on the test environment having a discoverable mountpoint. Access helper tests do not cover nil access modes for every helper. Slow-GRPC stuck-handler test uses timing and goroutines, so thresholds need enough slack to avoid flakiness.

Test signals: strong regression signal for common helpers with careful non-parallel tests around global state.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/csi-common/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/driver/driver.go -->
# sources/control-plane/ceph-csi/internal/driver/driver.go

Purpose: defines the minimal interface implemented by Ceph-CSI driver types.

Important APIs/types/functions: `Driver` interface has one method, `Run(conf *util.Config)`, expected to start the driver and not return.

Control flow: none in this file; it is an abstraction boundary for concrete driver packages.

State and persistence: no state. Implementations decide their own server lifecycle and persistence.

Dependencies and integration points: imports common `internal/util.Config`. Driver binaries or dispatchers can depend on this package instead of concrete RBD/CephFS/NFS/NVMe-oF driver types.

Risks: because `Run()` is expected not to return, implementations must handle fatal errors and shutdown consistently. The interface has no context or error return, so graceful composition must happen through config/signals inside implementations.

Test signals: no direct tests needed for the interface. Compile-time implementation assertions in concrete drivers would be useful.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/driver/driver.go -->
