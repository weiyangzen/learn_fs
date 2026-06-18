# Research: subset-b-000459

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/util.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/bucket/util.go

## Purpose
`util.go` contains bucket-provisioner helpers for Rook Ceph object buckets. It starts the lib-bucket-provisioner controller, extracts storage-class/ObjectBucket metadata, validates the target CephObjectStore, parses OBC quota/policy/lifecycle options, and resolves the owning object store for existing ObjectBuckets.

## Important APIs, Types, and Functions
`NewBucketController()` computes the provisioner name from `object.GetObjectBucketProvisioner()` and creates a `provisioner.Provisioner` that watches all namespaces. Simple accessors read storage class parameters, ObjectBucket bucket names, Ceph users, endpoints, and static bucket names. `(*Provisioner).getObjectStore()` verifies the CephObjectStore CR in the cluster namespace. `additionalConfigSpecFromMap()` accepts only controller-allowed keys and converts Kubernetes quantities through `quanityToInt64()`. `GetObjectStoreNameFromBucket()` prefers `AdditionalState` keys `objectStoreName` and `objectStoreNamespace`, then falls back to parsing the legacy RGW service DNS name.

## Control Flow, State, and Persistence
The file does not persist state directly. It transforms OBC/OB/StorageClass state into provisioner inputs and errors early for missing object store CRs, disallowed extra config, invalid quantities, or malformed legacy bucket hosts. Object store ownership is persisted indirectly in ObjectBucket `Spec.AdditionalState`; legacy fallback is retained for older buckets.

## Dependencies and Integration Points
It integrates kube-object-storage `ObjectBucket`, Kubernetes `StorageClass`, Rook CephObjectStore clients, object-store DNS parsing, OBC additional-config allow-listing, Kubernetes quantity parsing, and the lib-bucket-provisioner runtime.

## Risks and Test Signals
Risks include relying on untyped string map keys, the misspelled helper name `quanityToInt64`, fallback behavior that cannot support all external-store endpoints, and invalid config being controlled by the global OBC allow-list. Tests should cover allowed/disallowed additional config, quantity parsing, AdditionalState resolution, legacy endpoint parsing, and missing CephObjectStore errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/bucket/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/config.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/config.go

## Purpose
`config.go` builds RGW daemon configuration: frontend port/TLS strings, cephx keyrings, Keystone authentication settings, and monitor config-store options for a CephObjectStore.

## Important APIs, Types, and Functions
`clusterConfig.portString()` maps object-store gateway settings to beast frontend port, TLS cert, and private-key arguments, using internal port `8080` when not host-networked. `rgwFrontendStr()` adds `ssl_options`, TLS 1.2 ciphers, TLS 1.3 ciphersuites, and TLS groups. `buildSSLOptions()` converts `SslOptionsSpec` booleans into Ceph beast option tokens. `generateCephXUser()` derives the `client.rgw...` user, and `generateKeyring()` creates or rotates a daemon key via `keyring.SecretStore`. `generateMonConfigOptions()` builds RGW monitor options for sync, usage logs, zone metadata, Keystone, S3, Swift, user overrides, and secret-backed overrides. `configureKeystoneAuthentication()` and `mapKeystoneSecretToConfig()` validate Keystone secrets and map OpenStack-style environment keys into RGW config.

## Control Flow, State, and Persistence
Frontend strings are pure transformations. Keyring generation persists Kubernetes Secrets and optionally rotates Ceph auth keys when `shouldRotateCephxKeys` is set. Monitor config is persisted with `monStore.SetAll()` under the RGW cephx identity and deleted with `DeleteDaemon()`. Secret-backed RGW config values are read at reconcile time from the cluster namespace.

## Dependencies and Integration Points
This file connects CephObjectStore CRD fields, Ceph monitor config database helpers, cephx keyring helpers, Kubernetes Secrets, Keystone auth, S3/Swift protocol knobs, and RGW deployment generation in `rgw.go`.

## Risks and Test Signals
Risks include invalid user-supplied `RgwConfig` overriding operator defaults, secret selector errors blocking reconciliation, Keystone validation only accepting password/v3 with matching domains, and TLS option strings requiring exact Ceph syntax. Tests cover port formatting, TLS options/ciphers/groups, cephx user names, default and override mon config, and secret-sourced RGW config.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/config_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/config_test.go

## Purpose
`config_test.go` verifies the low-level RGW configuration builders used by object-store reconciliation, especially frontend formatting and monitor config generation.

## Important APIs, Types, and Functions
`newConfig()` creates a minimal `clusterConfig` with Squid version, non-host networking, and a fake Kubernetes client. `TestPortString`, `TestRgwFrontendStr`, and `TestBuildSslOptions` exercise gateway port/TLS and security option combinations. `TestGenerateCephXUser` checks Rook deployment-name to Ceph client-name conversion. `Test_clusterConfig_generateMonConfigOptions` validates default RGW monitor config, multisite sync disabling, `RgwConfig` overrides, and that `RgwCommandFlags` do not leak into mon config. `TestRgwConfigFromSecret` verifies secret lookup, missing-secret failure, and key extraction.

## Control Flow, State, and Persistence
The tests use fake clients and in-memory objects. `TestRgwConfigFromSecret` creates a Kubernetes Secret in the fake clientset and confirms `generateMonConfigOptions()` reads it. Most tests are table-driven transformations with no persisted state beyond fake API objects.

## Dependencies and Integration Points
The test suite depends on Ceph API types, fake Kubernetes clients, Rook test helpers, `stretchr/testify`, and pointer helpers. It indirectly guards deployment and mon-store behavior by asserting exact strings and maps generated from CRD specs.

## Risks and Test Signals
Strong signals include exact expected beast frontend strings, default-disabled legacy TLS versions, correct SDN internal port substitution, and secret-backed RGW config behavior. Gaps include Keystone secret mapping tests, keyring rotation errors, `RgwConfigFromSecret` invalid selector validation, and integration-level confirmation that Ceph accepts the produced option strings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/controller.go

## Purpose
`controller.go` is the main controller-runtime reconciler for `CephObjectStore`. It watches object-store CRs and owned Kubernetes objects, manages finalizers/status, coordinates CephCluster readiness and Ceph version state, creates or updates RGW services/pools/deployments/config, and safely deletes stores.

## Important APIs, Types, and Functions
`Add()`/`add()` register watches for CephObjectStore, owned Secrets/Services/Deployments, and externally referenced Secrets. `secretPredicate()` ignores Rook-owned Secrets, while `mapSecretToCR()` requeues object stores that reference changed RGW config or Keystone secrets. `Reconcile()` wraps `reconcile()` with panic recovery and reporting. `reconcile()` handles finalizers, status initialization, CephCluster readiness, cluster-info loading, deletion dependency checks, version/upgrade gates, cephx key-rotation decisions, validation, and create/update flow. `reconcileCreateObjectStore()` splits external and internal object-store reconciliation. `getMultisiteResourceNames()` and `retrieveMultisiteZone()` enforce multisite zone/zonegroup/realm readiness before RGW starts.

## Control Flow, State, and Persistence
Reconciliation writes CR status, finalizers, Kubernetes Services/Endpoints/Deployments/Secrets/ConfigMaps via `clusterConfig`, Ceph pools and multisite config through admin commands, mon config-store options, and cephx status. Deletion sets `Deleting`, checks bucket/user/zone dependents when possible, calls `deleteStore()`, and removes the finalizer. Create/update sets `Progressing` first and `Ready` with observed generation only after successful reconciliation.

## Dependencies and Integration Points
The controller integrates controller-runtime, Rook CephCluster readiness helpers, Ceph command execution, object multisite helpers, pool validation/creation, admin-ops endpoint setup, keyring rotation, Kubernetes event/status reporting, bucket/COSI dependency checks, and externally referenced Secrets.

## Risks and Test Signals
Risks include races with multisite zone setup, false deletion safety when admin context or pools are unavailable, secret watch fan-out across all stores in a namespace, cephx status assumptions for brownfield stores, and exact Ceph version comparison during upgrades. Tests cover no/ready cluster behavior, normal and multisite creation/deletion, zone-not-ready requeue, external stores, missing external credentials, secret-to-CR mapping, version comparison, and key rotation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/controller_test.go

## Purpose
`controller_test.go` exercises the CephObjectStore reconciler across readiness gates, normal creation, multisite behavior, external stores, secret mapping, version comparison, and cephx key rotation.

## Important APIs, Types, and Functions
The tests build fake controller-runtime clients, fake Rook clientsets, mock Ceph executors, and replace package globals such as `currentAndDesiredCephVersion`, `commitConfigChanges`, and `cephObjectStoreDependents`. Major cases include `TestCephObjectStoreController`, `TestCephObjectStoreControllerMultisite`, `TestCephObjectStoreControllerZoneNotReady`, `TestCephObjectExternalStoreController`, `TestDiffVersions`, `Test_mapSecretToCR`, and `TestKeyRotation`.

## Control Flow, State, and Persistence
The tests simulate CRs, CephCluster readiness, monitor secrets, Ceph command output, multisite JSON, object-store deletion timestamps, and generated Deployments/Secrets. They assert reconcile results, status phases, endpoint info, dependency checks, finalizer behavior, event-free success paths, and keyring secret contents after rotation.

## Dependencies and Integration Points
This suite integrates Rook API schemes, fake Kubernetes clients, mock Ceph command execution, Ceph version parsing, keyring status helpers, status/reporting code, and multisite admin command JSON. It is a high-value regression net for interactions that span Kubernetes objects and Ceph CLI output.

## Risks and Test Signals
Strong signals include requeue on missing/not-ready CephCluster, `Ready` status and endpoint population on success, no RGW start before a multisite zone is Ready, external-store missing-secret requeue, object-store secret watch mapping, and cephx generation tracking. Residual gaps include real controller watch wiring, real Ceph admin command failures, status update conflicts, and concurrent reconciles.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/cosi/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/cosi/controller.go

## Purpose
`cosi/controller.go` reconciles the experimental Ceph COSI driver deployment. It enables, disables, or waits to deploy the driver based on `CephCOSIDriver.Spec.DeploymentStrategy` and the presence of CephObjectStores.

## Important APIs, Types, and Functions
`Add()` registers a controller for `CephCOSIDriver` and also watches `CephObjectStore` events. `ReconcileCephCOSIDriver.reconcile()` enforces that at most one CephCOSIDriver CR exists, defaults deployment strategy to `Never`, deletes the driver deployment when disabled, requires the CR namespace to match the operator pod namespace, waits for object stores in `Auto` mode, and calls `startCephCOSIDriver()`. `startCephCOSIDriver()` creates the Deployment from `createCephCOSIDriverDeployment()` and updates it on `AlreadyExists`.

## Control Flow, State, and Persistence
The reconciler lists all CephCOSIDriver CRs instead of using only the request key. When disabled it deletes the Deployment named by the request. When enabled it persists a single Kubernetes Deployment in the operator namespace. Auto mode returns a timed requeue until at least one CephObjectStore exists.

## Dependencies and Integration Points
It integrates controller-runtime, Rook COSI CRDs, CephObjectStore events, Kubernetes Deployments, operator pod namespace environment, event recording, and reporting. Deployment shape is delegated to `spec.go`.

## Risks and Test Signals
Risks include singleton enforcement across namespaces, delete path using request namespaced name rather than discovered CR identity, update without resource-version merge semantics, and namespace dependence on `POD_NAMESPACE`. Tests cover default disabled behavior, Never/Always/Auto strategies, custom image, custom namespace rejection, object-store-triggered Auto deployment, and multiple CR errors.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/cosi/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/cosi/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/cosi/controller_test.go

## Purpose
`cosi/controller_test.go` verifies deployment-strategy behavior for the Ceph COSI driver controller.

## Important APIs, Types, and Functions
`TestCephCOSIDriverController` sets `POD_NAMESPACE`, builds fake clients and schemes, and runs the reconciler with combinations of CephCOSIDriver CRs and CephObjectStore CRs. It checks no-CR default behavior, explicit `Never`, `Always`, `Auto`, custom images, namespace validation, and multiple CR rejection.

## Control Flow, State, and Persistence
The tests use in-memory fake clients and inspect whether an `apps/v1.Deployment` exists after reconciliation. Auto mode without object stores is expected to requeue and not create a Deployment; Auto with an object store creates one. Always creates a Deployment even without object stores. Never avoids or deletes deployment state.

## Dependencies and Integration Points
The suite depends on Rook API schemes, Kubernetes apps scheme registration, fake controller-runtime clients, fake event recorders, and executor/test context scaffolding. It validates controller behavior and some deployment spec fields, such as the custom driver image.

## Risks and Test Signals
Signals are clear for strategy selection and namespace guardrails. Gaps include deployment update semantics, owner references, labels, placement/resources, sidecar image override, service account/volume details, and actual watch behavior from CephObjectStore events.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/cosi/controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/cosi/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/cosi/spec.go

## Purpose
`cosi/spec.go` constructs the Kubernetes Deployment, Pod template, labels, containers, volumes, and defaults for the Ceph COSI driver.

## Important APIs, Types, and Functions
`createCephCOSIDriverDeployment()` creates a one-replica Recreate Deployment with Rook revision history, 30-second minimum readiness, and 600-second progress deadline. `getCOSILabels()` extends standard Rook app labels with COSI-specific `app.kubernetes.io` labels. `createCOSIPodSpec()` creates two containers, applies placement, sets the service account, host networking policy, emptyDir socket volume, and pod labels. `createCOSIDriverContainer()` selects the Ceph COSI image, passes `--driver-prefix=rook-ceph`, exposes `POD_NAMESPACE`, mounts `/var/lib/cosi`, and applies resource requirements. `createCOSISideCarContainer()` selects the objectstorage provisioner sidecar image and mounts the same socket.

## Control Flow, State, and Persistence
The file is pure object construction. Persistent state appears when the controller creates or updates the returned Deployment. The shared emptyDir socket is process-local to the pod and is the integration channel between driver and sidecar.

## Dependencies and Integration Points
It integrates CephCOSIDriver spec fields for images, placement, and resources; operator label helpers; host-network enforcement; Kubernetes Deployment/Pod APIs; and COSI sidecar socket conventions.

## Risks and Test Signals
Risks include hard-coded default images, no explicit probes, no owner reference in this constructor, service-account assumptions, and potential global host-network side effects. Tests in `controller_test.go` cover custom driver image indirectly; additional tests should verify sidecar image override, placement, resources, labels/selectors, volumes, and service account.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/cosi/spec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/dependents.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/dependents.go

## Purpose
`dependents.go` computes deletion-blocking dependents for a CephObjectStore: buckets, CephObjectStoreUsers, and special multisite master-zone peer relationships.

## Important APIs, Types, and Functions
`CephObjectStoreDependents()` returns a `dependents.DependentList`. For multisite stores it first calls `CheckZoneIsMaster()`. Secondary zones skip bucket/user checks because the master is treated as source of truth. Master zones call `getMasterZoneDependents()`; if peer zones exist, deletion is blocked and an explanatory error is returned. Otherwise `getBucketDependents()` checks required pools and lists RGW buckets through Admin Ops, and the function lists `CephObjectStoreUser` CRs whose `Spec.Store` matches. `getMasterZoneDependents()` decodes `radosgw-admin zonegroup get` output and records non-current zones as peer dependents.

## Control Flow, State, and Persistence
The file reads Ceph pools, RGW admin APIs, zonegroup JSON, and Rook CRs. It does not mutate state. Missing pools cause bucket checks to be skipped so partially deleted or external stores can finish deletion.

## Dependencies and Integration Points
It integrates deletion finalizer logic in `controller.go`, Ceph admin command helpers, Admin Ops client, object-store pool discovery, Rook CephObjectStoreUser clientset, and the generic dependents reporting package.

## Risks and Test Signals
Risks include intentionally skipping checks when pools are missing, ignoring users for secondary multisite zones, admin-ops availability determining deletion safety, and peer-zone checks taking precedence over bucket/user details. Tests cover missing pools, buckets, users, secondary zones, master zones with and without peers, and expected dependency classes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/dependents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/dependents_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/dependents_test.go

## Purpose
`dependents_test.go` validates deletion-dependency behavior for standard and multisite CephObjectStores.

## Important APIs, Types, and Functions
`TestCephObjectStoreDependents` builds fake cluster contexts, fake Rook clientsets, mock Ceph executors, and mock RGW Admin Ops HTTP clients. It supplies pool lists and zonegroup/zone JSON for normal stores, secondary zones, and master zones. It creates `CephObjectStoreUser` CRs to test matching and non-matching user dependencies.

## Control Flow, State, and Persistence
Each subtest creates in-memory client state and invokes `CephObjectStoreDependents()`. The mocked Ceph executor returns pool lists and multisite JSON; the mocked HTTP client returns bucket arrays from the RGW admin bucket endpoint. The fake Rook clientset stores user CRs for listing.

## Dependencies and Integration Points
The tests cover interactions between pool discovery, Admin Ops bucket listing, Rook user CR listing, multisite zone master checks, and zonegroup peer detection. They also validate dependency labels used by deletion reporting.

## Risks and Test Signals
Signals include missing-pool skip behavior, no dependency for users pointing at other stores, user dependency for matching stores, secondary-zone deletion not blocked by buckets/users, master-zone bucket blocking when no peers exist, and master-zone peer blocking with an error when peer zones exist. Gaps include real RGW auth failures, malformed zonegroup JSON, and API-server errors while listing users.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/dependents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/json_helpers.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/json_helpers.go

## Purpose
`json_helpers.go` provides generic utilities for reading, updating, copying, and converting JSON-like `map[string]interface{}` objects used by object-store multisite/admin command logic.

## Important APIs, Types, and Functions
`getObjProperty[T]()` walks a required path and returns a typed terminal value. `updateObjProperty[T]()` walks a required path, replaces an existing terminal value, and returns the previous value, with JSON marshal/unmarshal fallback for typed slices such as `[]string`. `castJson()` converts arbitrary JSON-compatible values by marshaling and unmarshaling. `toObj()` converts a Go struct into a JSON object map. `deepCopyJson()` performs a JSON round-trip to produce an independent copy.

## Control Flow, State, and Persistence
The helpers are pure in-memory transformations except `updateObjProperty()`, which mutates the input map only after the full path exists. They return detailed errors for empty paths, missing keys, non-object intermediate nodes, and type mismatches.

## Dependencies and Integration Points
They depend only on `encoding/json`, `fmt`, and `strings`, and support higher-level code that patches decoded Ceph JSON structures before sending admin commands.

## Risks and Test Signals
Risks include the constrained generic type sets, JSON round-trip lossiness for numbers and custom types, update-only semantics that cannot create missing paths, and runtime type assertions on unstructured data. Tests cover successful and failing string/array reads, updates for strings/maps/arrays, missing paths, and deep-copy independence.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/json_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/json_helpers_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/json_helpers_test.go

## Purpose
`json_helpers_test.go` verifies the behavior and error surfaces of the unstructured JSON helper functions.

## Important APIs, Types, and Functions
`Test_getObjPropertyStr` tests nested string retrieval and wrong-type/missing-key failures. `Test_getObjPropertyObjArr` tests retrieval of `[]interface{}` object arrays and rejects other terminal types. `Test_deepCopyJson` confirms copied arrays do not alias the original. `Test_updateObjProperty`, `Test_updateObjPropertyObj`, and `Test_updateObjPropertyArr` verify replacement of existing nested fields and preservation of input JSON on missing paths.

## Control Flow, State, and Persistence
Tests decode JSON strings into maps, call helpers, and compare returned values plus marshaled output JSON. All state is in-memory; mutation checks focus on whether `updateObjProperty()` changes only existing terminal properties.

## Dependencies and Integration Points
The tests use Go JSON decoding, `reflect.DeepEqual`, and `stretchr/testify`. They protect helper behavior used by higher-level object-store JSON patching, where malformed Ceph JSON should produce actionable errors instead of silent mutation.

## Risks and Test Signals
Signals are strong for common string/object-array/map/array paths and deep copy behavior. Gaps include numeric conversions, empty path errors, non-object intermediate paths in `updateObjProperty()`, `toObj()`, `castJson()` failure cases, and generic `[]string` fallback conversion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/json_helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/mime.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/mime.go

## Purpose
`mime.go` manages the RGW `mime.types` file that Rook mounts into object-store pods so RGW can infer object content types for common file extensions.

## Important APIs, Types, and Functions
`clusterConfig.mimeTypesConfigMapName()` derives an object-store-specific ConfigMap name from the RGW instance name. `mimeTypesMountPath()` returns `/etc/ceph/rgw/mime.types`. `generateMimeTypes()` creates the ConfigMap key `mime.types` with the bundled `mimeTypes` constant unless the key already exists. `mimeTypesVolume()` and `mimeTypesVolumeMount()` build the ConfigMap volume and read-only mount at `/etc/ceph/rgw`. The `mimeTypes` constant is a large static MIME database covering application, audio, chemical, image, text, video, and other media types.

## Control Flow, State, and Persistence
On reconcile, `generateMimeTypes()` reads the ConfigMap key. If it exists, it deliberately avoids overwriting user/admin changes. If it is not found, it creates the key with the bundled content. Persistence is a Kubernetes ConfigMap owned by the object store.

## Dependencies and Integration Points
It integrates `clusterConfig`, Kubernetes ConfigMaps via `k8sutil.NewConfigMapKVStore`, owner references, RGW pod volume generation, and object-store deployment code that mounts the file.

## Risks and Test Signals
Risks include stale MIME definitions because existing ConfigMaps are never updated, user edits persisting across operator upgrades, large inline data increasing source size, mount-path assumptions, and ConfigMap ownership/deletion coupling. Useful tests would cover create, no-overwrite, ConfigMap get errors, volume naming, mount path, read-only mount, and deployment integration.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/mime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/controller.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/notification/controller.go

## Purpose
`notification/controller.go` reconciles `CephBucketNotification` CRs by provisioning RGW bucket notification configuration for labeled ObjectBucketClaims and their ObjectBuckets.

## Important APIs, Types, and Functions
`Add()` skips notification/OBC label controllers when `ROOK_DISABLE_OBJECT_BUCKET_CLAIM=true`; otherwise it registers both. `addNotificationReconciler()` watches `CephBucketNotification`. `Reconcile()` updates status and reports events. `reconcile()` fetches the notification, handles deletion/no-op, marks Reconciling, gets a provisioned topic via `topic.GetProvisioned()`, loads a ready CephCluster for the topic object-store namespace, lists OBCs matching `bucket-notification-<name>`, waits for ObjectBucket creation, resolves the bucket's CephObjectStore via `bucket.GetObjectStoreNameFromBucket()`, validates it matches the topic, and calls `createNotificationFunc()`.

## Control Flow, State, and Persistence
Status is persisted on the notification as Reconciling, Ready, or failed. RGW notification configuration is persisted externally through the provisioner/Admin Ops path. The controller itself does not label OBCs; that is handled by the companion OBC label reconciler registered from the same `Add()`.

## Dependencies and Integration Points
It integrates CephBucketTopic status/ARNs, ObjectBucketClaim/ObjectBucket CRs, Rook cluster readiness and cluster-info loading, bucket ownership helpers, notification provisioner functions, events/reporting, and OBC label conventions.

## Risks and Test Signals
Risks include topic ARN nil/not ready, cluster namespace mismatches, OBCs selected by labels before their ObjectBucket exists, fallback object-store parsing for older OBs, and status being marked failed for expected requeues. Tests cover missing topic, missing/not-ready cluster, unprovisioned topic, no OBCs, OBC without OB, successful OB notification, and bucket-host parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/object/notification/controller_test.go

## Purpose
`notification/controller_test.go` verifies CephBucketNotification reconciliation and object-store resolution from ObjectBuckets.

## Important APIs, Types, and Functions
`mockSetup()` creates fake cluster context, schemes, monitor Secret, and replaces `createNotificationFunc`, `getAllNotificationsFunc`, and `deleteNotificationFunc`. `testReconciler()` runs `ReconcileNotifications`, and `verifyEvents()` checks recorder output. `TestCephBucketNotificationController` covers topic/cluster readiness paths. `TestCephBucketNotificationControllerWithOBC` covers selected OBCs and ObjectBucket provisioning. `TestGetCephObjectStoreName` exercises legacy bucket-host parsing through the controller wrapper.

## Control Flow, State, and Persistence
Tests use fake controller-runtime clients and fake Kubernetes clients. Mocked provisioner functions record notification creation/deletion in slices. Event verification drains a fake recorder. OBC tests mutate OBC status from pending to bound and set `Spec.ObjectBucketName` before adding an ObjectBucket.

## Dependencies and Integration Points
The tests register Ceph, ObjectBucket, and Kubernetes schemes and use Rook test clients. They validate notification controller interactions with topic status, CephCluster readiness, monitor secret loading, OBC label selection, ObjectBucket lookup, and object-store DNS parsing.

## Risks and Test Signals
Signals include requeue without creation for missing topic/cluster/topic ARN/OB, success with no OBCs, creation when a bound OBC has an ObjectBucket, and parsing failures for malformed bucket hosts. Gaps include object-store mismatch validation, AdditionalState-based store resolution, createNotification errors, status conflict behavior, and companion OBC label controller behavior beyond shared mocks.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/object/notification/controller_test.go -->
