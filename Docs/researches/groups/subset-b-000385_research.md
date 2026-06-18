# subset-b-000385 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller.go -->
# sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller.go

Purpose: implements the CSI snapshot sidecar's per-`VolumeSnapshotContent` reconciliation logic. It decides whether a content object should create a backend CSI snapshot, poll backend snapshot status, clear status after deletion, or remove the content finalizer so the API server can finish deletion.

Important APIs/functions: `syncContent`, `createSnapshot`, `checkandUpdateContentStatus`, `createSnapshotWrapper`, `deleteCSISnapshotOperation`, `updateSnapshotContentStatus`, `clearVolumeContentStatus`, `GetCredentialsFromAnnotation`, `removeContentFinalizer`, `shouldDelete`, annotation helpers, `isCSIFinalError`, and `contentIsReady`. It uses `utils.PatchVolumeSnapshotContent` for JSON patches and a `Handler` wrapper for CSI `CreateSnapshot`, `DeleteSnapshot`, and status calls.

Control flow: `syncContent` first handles deletion candidates. Delete policy `Delete` with an independent snapshot handle calls CSI `DeleteSnapshot`, clears snapshot-related status, then removes the bound-protection finalizer; `Retain` and group-member contents skip backend deletion and only remove the finalizer. Non-deleted dynamic independent contents with source volume handles and no status call `CreateSnapshot`. Ready contents avoid repeated CSI calls and only clear the in-progress annotation. Everything else checks status via CSI `ListSnapshots` or falls back to creation when appropriate.

State and persistence: persistent state is stored in `VolumeSnapshotContent` status fields (`SnapshotHandle`, `ReadyToUse`, `CreationTime`, `RestoreSize`, `VolumeGroupSnapshotHandle`, `Error`), metadata finalizers, and the `AnnVolumeSnapshotBeingCreated` annotation. The controller also updates an in-memory cache through `storeContentUpdate` to suppress stale informer events.

Dependencies and integration: integrates Kubernetes snapshot CRDs, core events, secrets, snapshot classes, JSON patch helpers, CSI handler calls, deletion-secret annotations, list-secret parameters, and group snapshot annotations. It relies on common-controller annotations such as `AnnVolumeSnapshotBeingDeleted` to authorize destructive cleanup.

Risks and test signals: risks include retry storms on transient CSI/API errors, leaked backend snapshots if timeout annotations are mishandled, lossy status updates under conflicts, nil snapshot class handling, and group snapshot members accidentally routed through independent snapshot deletion. Tests in this subset cover cache ordering, deletion-policy branches, secret failures, group-member deletion skips, final-error classification indirectly through create behavior, and status/finalizer expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller_base.go -->
# sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller_base.go

Purpose: defines the sidecar controller object, constructor, informer wiring, workqueue worker loop, driver filtering, and local cache initialization for snapshot and optional group-snapshot content processing.

Important APIs/types/functions: `csiSnapshotSideCarController`, `NewCSISnapshotSideCarController`, `Run`, `enqueueContentWork`, `contentWorker`, `processNextItem`, `syncContentByKey`, `isDriverMatch`, `deleteContentInCacheStore`, and `initializeCaches`. The struct owns Kubernetes clients, event recorder, listers, sync predicates, workqueues, cache stores, CSI handler, feature flags, and group snapshot listers/queues.

Control flow: the constructor configures event broadcasting, the content workqueue, snapshot content/class informers, and optionally group snapshot informers. Add/delete events enqueue immediately; update events for `VolumeSnapshotContent` pass through `utils.ShouldEnqueueContentChange` to avoid loops from sidecar-owned status/finalizer updates. `Run` waits for informers, seeds local stores from listers, launches worker goroutines, and optionally attaches worker goroutines to a wait group for leader-election release-on-exit. Each queue item is fetched by key, resolved from the informer, filtered by driver/class, cached by resource version, and reconciled through `syncContent`.

State and persistence: this file maintains only runtime state: rate-limited queue contents and cache stores keyed by object identity. Durable state remains in the API server through the operation file. Deleted objects are removed from the local cache after informer not-found resolution.

Dependencies and integration: integrates client-go informers, workqueue, event recorder, feature gates, snapshot/group snapshot generated clients and listers, CSI snapshotter/group snapshotter interfaces, and utility cache functions. It shares the same controller type with group snapshot methods in neighboring files.

Risks and test signals: risks include skipped objects when class-driver metadata is stale or missing, group snapshot cache initialization not applying the same driver filter as normal content, non-reentrant worker assumptions with multiple workers, and stale cache resource-version parse failures. Tests cover resource-version ordering and parse errors through `StoreObjectUpdate`; broader informer/worker behavior is mostly integration-tested elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller_base.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller_test.go -->
# sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller_test.go

Purpose: unit-tests low-level controller cache update semantics and the deletion predicate for `VolumeSnapshotContent` objects.

Important APIs/functions: helper `storeVersion`, `TestControllerCache`, `TestControllerCacheParsingError`, and `TestShouldDelete`. The tests use `utils.StoreObjectUpdate`, a client-go cache store, `newContent` test fixtures, and deletion annotations/finalizers from the controller package.

Control flow: `storeVersion` creates a content object with a specific `ResourceVersion`, stores it, and validates both the return value and cache contents. `TestControllerCache` exercises first insert, same-version update, newer update, stale older update rejection, and numeric ordering where `"10"` must sort after `"2"`. `TestShouldDelete` constructs timestamp/annotation/binding scenarios and verifies the controller's boolean deletion gate.

State and persistence: all state is in-memory fake content and cache entries. The tests do not hit Kubernetes API clients or CSI mocks.

Dependencies and integration: depends on test fixture constructors from the sidecar test package, snapshot CRD types, client-go cache, and metadata utilities. It validates behavior consumed by `syncContentByKey` and `syncContent`.

Risks and test signals: strong signal for stale informer-event suppression and resource-version parsing. Deletion predicate coverage is narrow but covers nil deletion timestamp, unbound pre-provisioned content, explicit delete annotation, and fallback no-delete cases; it does not cover the create-in-progress annotation branch directly.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_delete_test.go -->
# sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_delete_test.go

Purpose: table-driven deletion reconciliation tests for `syncContent`, focused on whether the sidecar calls CSI delete, clears status, removes finalizers, emits events, and handles secret/class failures correctly.

Important APIs/data: global fixture values for sizes, policies, times, class parameters, deletion-secret annotations, `snapshotClasses`, and `TestDeleteSync`. Each `controllerTest` entry supplies initial contents, expected contents, expected CSI create/list/delete calls, fake secrets, injected reactor errors, expected events, and a test runner.

Control flow: cases exercise dynamic and pre-provisioned contents with `Delete` and `Retain` policies, deletion errors, invalid or missing secret references, missing classes, content disappearing before delete, bound contents that should not be deleted, and group snapshot member contents whose backend snapshot is owned by a group snapshot. The test runner feeds fixtures into a fake controller/reactor and performs one reconciliation pass.

State and persistence: state is simulated through fake `VolumeSnapshotContent` objects, fake secrets, expected API content status/finalizer mutations, and mocked CSI call ledgers. Persistent API effects being asserted include cleared snapshot handles, retained restore size in some branches, finalizer removal, and event emission.

Dependencies and integration: integrates the sidecar controller test harness, snapshot CRD fixtures, core secrets, deletion annotations, CSI mock handlers, and API reactors.

Risks and test signals: this is the main guard against data-loss regressions in deletion behavior. It signals correct non-deletion for `Retain`, finalizer retention on failed deletes, group-member delete suppression, and behavior with absent secrets. Risks remain around concurrent updates and real informer retry timing, which unit tests approximate only indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_finalizer_test.go -->
# sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_finalizer_test.go

Purpose: placeholder for future finalizer-specific sidecar controller tests.

Important APIs/functions: contains only `TestContentFinalizer`, which currently has all meaningful table-test content commented out.

Control flow: the test function performs no assertions and exits successfully.

State and persistence: no runtime, fake API, or CSI state is created.

Dependencies and integration: package-level imports only `testing`; commented code references the broader sidecar test harness and snapshot classes.

Risks and test signals: this file is effectively a missing-test signal. Finalizer behavior is partially covered through deletion tests, but direct add/remove finalizer scenarios and PVC/source finalizer interactions are not covered here.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_finalizer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/snapshotter/snapshotter.go -->
# sources/control-plane/external-snapshotter/pkg/snapshotter/snapshotter.go

Purpose: wraps raw CSI controller RPCs behind the sidecar's `Snapshotter` interface for create, delete, and status lookup operations against a CSI driver connection.

Important APIs/types/functions: `Snapshotter` interface, concrete `snapshot`, `NewSnapshotter`, `CreateSnapshot`, `DeleteSnapshot`, `isListSnapshotsSupported`, and `GetSnapshotStatus`. Return values include driver name, snapshot ID, creation time, restore size, ready flag, group snapshot ID, and errors.

Control flow: `CreateSnapshot` resolves the driver name with `csi-lib-utils/rpc.GetDriverName`, builds a `CreateSnapshotRequest`, forwards parameters and secrets, and unwraps the CSI `Snapshot`. `DeleteSnapshot` sends `DeleteSnapshotRequest`. `GetSnapshotStatus` first asks `ControllerGetCapabilities`; if `LIST_SNAPSHOTS` is absent it assumes the snapshot exists and ready, otherwise it calls `ListSnapshots` by ID and reads the first entry.

State and persistence: the wrapper is stateless aside from holding a `grpc.ClientConn`; persistence happens in the external CSI backend and later in Kubernetes CRD status by the controller.

Dependencies and integration: depends on CSI protobufs, gRPC, csi-lib-utils RPC helpers, and klog. It is consumed by the sidecar controller handler layer.

Risks and test signals: risks include nil CSI response fields, assuming ready when `ListSnapshots` is unsupported, repeatedly querying capabilities per status call, and using only the first list result. Tests cover create/delete requests with parameters/secrets, transient/final gRPC errors, list capability gating, list credentials, and missing list support fallback.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/snapshotter/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/snapshotter/snapshotter_test.go -->
# sources/control-plane/external-snapshotter/pkg/snapshotter/snapshotter_test.go

Purpose: tests the CSI RPC wrapper using a mock CSI driver, validating request construction and returned values for create, delete, and list/status operations.

Important APIs/functions: `createMockServer`, `TestCreateSnapshot`, `TestDeleteSnapshot`, `TestGetSnapshotStatus`, and `FakeCSIVolume`. It uses gomock, csi-test mock servers, csi-lib-utils connection/metrics, protobuf matchers, and gRPC status injection.

Control flow: each test starts one mock CSI driver and gRPC connection, registers expected controller/identity RPCs, invokes a `NewSnapshotter` method, and compares errors and output values. Create tests include default, parameter, secret, transient error, and final error cases. Delete tests mirror secret and error cases. Status tests vary `LIST_SNAPSHOTS` support and list response/errors.

State and persistence: all backend state is mocked; no Kubernetes API state is touched. `FakeCSIVolume` supplies a CSI PV handle for request construction.

Dependencies and integration: validates the contract expected by sidecar controller `Handler` implementations and ensures CSI protobuf request shapes remain stable.

Risks and test signals: good signal for API-level CSI call correctness. It does not cover nil `rsp.Snapshot`, empty `ListSnapshots` response, group snapshot ID assertion, or connection lifecycle failures beyond initial connect.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/snapshotter/snapshotter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/conversion.go -->
# sources/control-plane/external-snapshotter/pkg/utils/conversion.go

Purpose: provides small conversion helpers from CSI protobuf-style values to Kubernetes snapshot API status fields.

Important APIs/functions: `CSITimestampToKubernetes` converts a `timestamppb.Timestamp` to a Unix nanoseconds pointer; `CSISizeToKubernetes` converts a byte size to an `*int64` but treats zero as unset.

Control flow: both helpers are straight-line nil/zero guards followed by pointer return.

State and persistence: stateless; callers decide whether to persist returned pointers into CRD status.

Dependencies and integration: depends on protobuf timestamp types and is intended for controller status population.

Risks and test signals: risks are semantic: zero-size snapshots cannot be distinguished from absent size, and timestamp validity is delegated to protobuf conversion. Tests cover nil timestamp, non-nil timestamp, zero size, and non-zero size.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/conversion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/conversion_test.go -->
# sources/control-plane/external-snapshotter/pkg/utils/conversion_test.go

Purpose: verifies the CSI-to-Kubernetes scalar conversion helpers.

Important APIs/functions: `TestCsiSizeToKubernetes` and `TestCsiTimestampToKubernetes`.

Control flow: tests assert zero size and nil timestamp return nil, while non-zero size and current timestamp return expected int64 values.

State and persistence: no external state.

Dependencies and integration: depends on `timestamppb.Now` and the local conversion helpers.

Risks and test signals: useful regression signal for nil-vs-zero status behavior; it does not test negative sizes or invalid timestamp values.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/conversion_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/patch.go -->
# sources/control-plane/external-snapshotter/pkg/utils/patch.go

Purpose: centralizes JSON Patch operations for snapshot and group snapshot CRDs, including optional subresources such as `status`.

Important APIs/types/functions: `PatchOp`, `PatchVolumeSnapshotContent`, `PatchVolumeSnapshot`, `PatchVolumeGroupSnapshot`, and `PatchVolumeGroupSnapshotContent`.

Control flow: each function marshals a slice of `PatchOp` to JSON, calls the generated client `Patch` method with `types.JSONPatchType`, passes optional subresources through, and returns either the patched object or the original object on error.

State and persistence: persists metadata/spec/status mutations to the Kubernetes API server through generated clients. It uses `context.TODO()` and does not apply retries itself.

Dependencies and integration: consumed heavily by controllers for finalizer, annotation, and status updates. Depends on generated snapshot clientsets, API machinery patch types, and JSON encoding.

Risks and test signals: risks include invalid JSON pointer escaping at call sites, replacing missing paths, lack of context cancellation, and caller confusion from returning the original object on errors. No direct tests in this subset cover patch helper behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/patch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/pvs.go -->
# sources/control-plane/external-snapshotter/pkg/utils/pvs.go

Purpose: provides cache index keys for looking up CSI persistent volumes by driver name and volume handle.

Important APIs/functions: `CSIDriverHandleIndexName`, `PersistentVolumeKeyFunc`, and `PersistentVolumeKeyFuncByCSIDriverHandle`.

Control flow: `PersistentVolumeKeyFunc` returns `driver^volumeHandle` only for non-nil CSI PVs; non-CSI or nil PVs map to the empty string. The component function formats the same key from explicit strings.

State and persistence: stateless; keys are used by informer indexes and lookups.

Dependencies and integration: depends on core `PersistentVolume` types and integrates with snapshot controller logic that needs to map PVC/PV sources to CSI driver handles.

Risks and test signals: separator collisions are theoretically possible if driver names or handles contain `^`; the code assumes CSI handles are safe enough for this indexing use. Tests cover nil, CSI, and hostPath PV inputs.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/pvs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/pvs_test.go -->
# sources/control-plane/external-snapshotter/pkg/utils/pvs_test.go

Purpose: unit-tests persistent volume CSI index key generation.

Important APIs/functions: `TestPersistentVolumeKeyFunc`.

Control flow: builds a CSI PV, a hostPath PV, and a nil PV case, then compares `PersistentVolumeKeyFunc` output with expected keys.

State and persistence: no external state.

Dependencies and integration: depends on core PV API types and validates keys used by informer indexes.

Risks and test signals: confirms non-CSI volumes do not pollute the CSI index; does not test the component helper directly or unusual characters in handles.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/pvs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/util.go -->
# sources/control-plane/external-snapshotter/pkg/utils/util.go

Purpose: shared utility surface for snapshot controllers: constants for annotations/finalizers/CSI parameter keys, cache version handling, name/key helpers, secret template resolution, credential loading, deletion/finalizer predicates, parameter filtering, logging status helpers, readiness predicates, and content update enqueue filtering.

Important APIs/types/functions: `secretParamsMap`; secret parameter maps for snapshot, group snapshot, list, and get operations; finalizer and annotation constants; `StoreObjectUpdate`; `GetSecretReference`; `GetGroupSnapshotSecretReference`; `GetCredentials`; `RemovePrefixedParameters`; finalizer predicates; ready/bound/created predicates; dynamic content-name functions; and `ShouldEnqueueContentChange`.

Control flow: cache updates compare numeric `ResourceVersion` values and reject older objects. Secret reference resolution requires name and namespace templates as a pair, expands whitelisted tokens, validates DNS names, and returns nil when no secret is configured. Credential loading reads Kubernetes secrets into string maps. Parameter filtering strips known reserved `csi.storage.k8s.io/*` keys and rejects unknown reserved keys. Enqueue filtering normalizes status, finalizers, managed fields, resource version, and sidecar-owned annotations before deep equality, while always allowing resyncs and ready transitions.

State and persistence: stateless except for reading Kubernetes secrets and returning data for callers to persist. Constants define durable API annotations/finalizers used across controllers.

Dependencies and integration: integrates core Kubernetes API types, snapshot/group snapshot CRDs, client-go caches and clients, validation helpers, semantic equality, klog, and set utilities. The sidecar and common controllers rely on these helpers for safe event filtering and CRD metadata conventions.

Risks and test signals: risks include token-template restrictions surprising users, reserved parameter drift, string-based credential conversion, resource-version parse assumptions, and enqueue filtering hiding meaningful changes if sanitization expands too far. Tests cover slice removal, secret template success/failure, prefixed parameter filtering, default-class annotations, and many enqueue-filter cases.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/util_test.go -->
# sources/control-plane/external-snapshotter/pkg/utils/util_test.go

Purpose: unit-tests broad utility behavior used by snapshot controllers.

Important APIs/functions: `TestRemoveString`, `TestGetSecretReference`, `TestRemovePrefixedCSIParams`, default annotation tests, and `TestShouldEnqueueContentChange`.

Control flow: table tests validate finalizer slice removal, secret reference template pairing and DNS validation, reserved CSI parameter stripping/erroring, snapshot and group default-class annotations, and update-event filtering across spec, status, finalizer, managed-field, sidecar annotation, external annotation, resync, and ready-transition scenarios.

State and persistence: test state is in-memory CRD/core objects; no Kubernetes client calls are made in this file.

Dependencies and integration: depends on snapshot CRDs, core API objects, metadata, pointer helpers, reflection, and utility constants.

Risks and test signals: strong signal for preventing controller self-update loops and reserved parameter leakage to CSI drivers. Gaps include `GetCredentials`, group secret reference templating, many finalizer/deletion predicates, logging helpers, and malformed resource versions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/vgs.go -->
# sources/control-plane/external-snapshotter/pkg/utils/vgs.go

Purpose: utilities for detecting and indexing `VolumeSnapshot` membership in a `VolumeGroupSnapshot`, and for building owner references from group snapshots.

Important APIs/functions: `VolumeSnapshotParentGroupIndex`, `getVolumeGroupSnapshotParentObjectName`, `IsVolumeGroupSnapshotMember`, `VolumeSnapshotParentGroupKeyFunc`, `VolumeSnapshotParentGroupKeyFuncByComponents`, `NeedToAddVolumeGroupSnapshotOwnership`, and `BuildVolumeGroupSnapshotOwnerReference`.

Control flow: owner-reference scanning looks for `Kind=VolumeGroupSnapshot` with the current group snapshot API version. Key generation returns `namespace^parentName`. Ownership-add detection requires no existing owner reference and a non-empty `Status.VolumeGroupSnapshotName`. Owner-reference construction fills APIVersion, kind, name, and UID.

State and persistence: stateless; callers persist owner references or use keys in informer indexes.

Dependencies and integration: depends on snapshot and group snapshot CRD types, Kubernetes metadata, and namespaced names. It supports group snapshot reconciliation and snapshot indexing.

Risks and test signals: risks include API-version mismatch across beta/stable group snapshot versions, separator collision in keys, and using status as an ownership source before status is fully reconciled. Tests cover nil/no/wrong/correct owner references and ownership-add predicates.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/vgs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/vgs_test.go -->
# sources/control-plane/external-snapshotter/pkg/utils/vgs_test.go

Purpose: tests group snapshot membership detection, parent index key generation, and ownership-add predicates for `VolumeSnapshot` objects.

Important APIs/functions: `TestIsVolumeSnapshotGroupMember` and `TestNeedToAddVolumeGroupSnapshotOwnership`.

Control flow: table tests cover nil snapshots, snapshots without ownership, unrelated owner references, wrong group API version, correct group owner reference, missing ownership with status group name, and already-owned snapshots.

State and persistence: in-memory snapshot objects only.

Dependencies and integration: validates helper behavior for group snapshot controllers and informer indexes.

Risks and test signals: good signal for owner-reference parsing and missing-owner detection. It does not assert `BuildVolumeGroupSnapshotOwnerReference` directly or key generation from explicit components separately.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/utils/vgs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/certwatcher.go -->
# sources/control-plane/external-snapshotter/pkg/webhook/certwatcher.go

Purpose: watches TLS certificate and key files for changes and exposes the currently loaded certificate to the HTTPS webhook server.

Important APIs/types/functions: `CertWatcher`, `NewCertWatcher`, `GetCertificate`, `Start`, `Watch`, `ReadCertificate`, `handleEvent`, and fsnotify event helpers.

Control flow: construction loads the initial key pair and creates an fsnotify watcher. `Start` registers both file paths, starts `Watch` in a goroutine, blocks until context cancellation, then closes the watcher. Watch events for write/create/remove trigger a certificate reload; remove events also attempt to re-add the watch.

State and persistence: holds the current `tls.Certificate` in memory behind a mutex. Persistent state is the certificate/key files on disk, which are read but not written.

Dependencies and integration: adapted from controller-runtime internals; integrates `fsnotify`, `crypto/tls`, klog, and `http.Server` TLS `GetCertificate` callbacks.

Risks and test signals: risks include reload failure leaving the previous certificate active, watching removed files directly rather than parent directories, races around rotation patterns, and logging without surfacing errors to readiness. The webhook reload test exercises repeated file rewrites and `GetCertificate` changes.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/certwatcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/config.go -->
# sources/control-plane/external-snapshotter/pkg/webhook/config.go

Purpose: defines minimal TLS configuration input and a helper to create a static `tls.Config` from certificate files.

Important APIs/types/functions: `Config` with `CertFile` and `KeyFile`, and `configTLS`.

Control flow: `configTLS` loads the X.509 key pair from disk and returns a TLS config with the certificate installed; load failures call `klog.Fatal`.

State and persistence: reads certificate files and stores loaded certificate material in memory.

Dependencies and integration: depends on `crypto/tls` and klog. It can be used by webhook startup code when dynamic `CertWatcher` is not driving `GetCertificate`.

Risks and test signals: fatal exit makes this unsuitable for recoverable library use; static certificates will not reload. Dynamic reload behavior is tested in `webhook_test.go`, but this helper itself has no direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/convert.go -->
# sources/control-plane/external-snapshotter/pkg/webhook/convert.go

Purpose: implements conversion for `VolumeGroupSnapshotContent` between `groupsnapshot.storage.k8s.io/v1beta1` and `v1beta2`, preserving v1beta2-only per-snapshot status fields through a reversible annotation when downgrading.

Important APIs/functions: `convertGroupSnapshotCRD`, `convertVolumeGroupSnapshotContentFromV1beta1ToV1beta2`, `convertVolumeGroupSnapshotContentFromV1beta2ToV1beta1`, and `volumeSnapshotInfoAnnotationName`.

Control flow: the top-level converter rejects same-version conversions, unexpected kinds, and unsupported version pairs. Beta1-to-beta2 prefers the serialized annotation when present, installs it into `status.volumeSnapshotInfoList`, removes old `volumeSnapshotHandlePairList`, and clears the annotation. Without annotation it renames the old pair list. Beta2-to-beta1 serializes `volumeSnapshotInfoList` into the annotation, strips beta2-only fields from each entry, writes `status.volumeSnapshotHandlePairList`, and removes `volumeSnapshotInfoList`.

State and persistence: mutates an unstructured object copy that is returned to the API conversion framework. The annotation is durable storage for fields that v1beta1 cannot express.

Dependencies and integration: depends on unstructured Kubernetes object helpers, JSON serialization, metav1 statuses, and the webhook framework in this package.

Risks and test signals: risks include a panic-prone type assertion after JSON unmarshal if annotation content is not a slice, data loss if annotation is removed externally, and mutation of nested map entries in-place. Testdata covers annotation/no-annotation and status/no-status round trips in both directions.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/convert_test.go -->
# sources/control-plane/external-snapshotter/pkg/webhook/convert_test.go

Purpose: golden-file tests for group snapshot content conversion between v1beta1 and v1beta2.

Important APIs/functions: `TestFromBeta1ToBeta2`, `TestFromBeta2ToBeta1`, and `fromFile`.

Control flow: tests glob matching beta1 YAML files, derive paired beta2 filenames by string replacement, load both as unstructured objects, run the relevant conversion function, emulate API version assignment by the framework, and compare with semantic deep equality. Failures print JSON-formatted actual/expected objects.

State and persistence: reads YAML testdata only; no API server or network.

Dependencies and integration: depends on filepath globbing, sigs YAML decoding, unstructured objects, semantic equality, and the conversion code.

Risks and test signals: good signal for expected object transformations and annotation preservation. The glob-driven pairing depends on strict filename conventions and does not exercise the HTTP conversion review framework or malformed annotation errors.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/convert_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/framework.go -->
# sources/control-plane/external-snapshotter/pkg/webhook/framework.go

Purpose: generic Kubernetes CRD conversion webhook framework for decoding `ConversionReview` requests, invoking a conversion function, and encoding the response with negotiated media type.

Important APIs/types/functions: `convertFunc`, `statusErrorWithMessage`, `statusSucceed`, `doConversionV1`, `serve`, `mediaType`, package `scheme`, `addToScheme`, `serializers`, `getInputSerializer`, and `getOutputSerializer`.

Control flow: `serve` reads the request body, chooses a serializer from `Content-Type`, decodes the object, only accepts apiextensions/v1 `ConversionReview`, calls `doConversionV1`, clears the request in the response, negotiates output from `Accept`, and encodes JSON/YAML. `doConversionV1` unmarshals each raw object to `unstructured.Unstructured`, calls the converter with the desired API version, sets converted APIVersion, and accumulates raw extensions.

State and persistence: stateless per request; no persistent storage. The runtime scheme and serializer map are package-level singletons.

Dependencies and integration: based on Kubernetes agnhost conversion webhook sample; integrates apiextensions v1/v1beta1 schemes, runtime serializers, HTTP, goautoneg, klog, and `convertGroupSnapshotCRD`.

Risks and test signals: risks include accepting only exact media type strings without parameters, potential nil request dereference for malformed `ConversionReview`, logging full request bodies, and no direct v1beta1 request handling despite v1beta1 being in the scheme. Conversion unit tests bypass this layer; webhook cert test only hits server startup/cert reload.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/framework.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_no_status_v1beta1.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_no_status_v1beta1.yaml

Purpose: beta1 golden input for converting an annotated `VolumeGroupSnapshotContent` with no status into v1beta2.

Important content: API version `groupsnapshot.storage.k8s.io/v1beta1`, kind `VolumeGroupSnapshotContent`, name `new-groupsnapshot-demo`, empty spec, and `groupsnapshot.storage.kubernetes.io/volume-snapshot-info-list` annotation containing two JSON entries with snapshot handle, volume handle, creation time, ready flag, and restore size.

Control flow: used by `TestFromBeta1ToBeta2`; the converter must deserialize the annotation, create `status.volumeSnapshotInfoList`, and remove the annotation.

State and persistence: represents persisted CRD metadata with conversion-preservation data stored only in an annotation.

Dependencies and integration: paired with `annotation_no_status_v1beta2.yaml`.

Risks and test signals: verifies annotation-driven restoration when beta1 has no status field. It also depends on annotation JSON being valid and shaped as a slice.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_no_status_v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_no_status_v1beta2.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_no_status_v1beta2.yaml

Purpose: expected v1beta2 output for annotated beta1 input without status.

Important content: API version `v1beta2`, same kind/name/spec, empty annotations map, and `status.volumeSnapshotInfoList` with two fully detailed entries including beta2-only creation/ready/restore fields.

Control flow: loaded as the expected object for `annotation_no_status_v1beta1.yaml`.

State and persistence: models the converted v1beta2 status that the API server should store or return.

Dependencies and integration: paired with beta1 source golden file and conversion test glob naming.

Risks and test signals: signals that annotation data takes precedence and annotation cleanup leaves an explicit empty annotations map.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_no_status_v1beta2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_status_v1beta1.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_status_v1beta1.yaml

Purpose: beta1 golden input where both the legacy status pair list and preservation annotation are present.

Important content: v1beta1 `VolumeGroupSnapshotContent` with ready and group handle status, `status.volumeSnapshotHandlePairList`, and annotation JSON containing the richer beta2 `volumeSnapshotInfoList` entries.

Control flow: conversion should use annotation content for beta2 status, remove the legacy pair list, preserve other status fields, and clear the annotation.

State and persistence: represents a downgraded object that carried beta2-only fields in metadata while retaining beta1-compatible status.

Dependencies and integration: paired with `annotation_status_v1beta2.yaml`.

Risks and test signals: verifies reversibility path from beta2 downgrade back to beta2 upgrade. It signals that annotation data can override/augment existing legacy status.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_status_v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_status_v1beta2.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_status_v1beta2.yaml

Purpose: expected v1beta2 output for beta1 input with both annotation and status.

Important content: v1beta2 content with ready and group handle retained, annotation cleared to `{}`, and `status.volumeSnapshotInfoList` populated with full entries.

Control flow: used as semantic equality target after beta1-to-beta2 conversion.

State and persistence: represents restored beta2 status after a reversible downgrade/upgrade sequence.

Dependencies and integration: paired with `annotation_status_v1beta1.yaml`.

Risks and test signals: confirms non-list status fields survive conversion and legacy `volumeSnapshotHandlePairList` is not retained.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/annotation_status_v1beta2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_no_status_v1beta1.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_no_status_v1beta1.yaml

Purpose: minimal beta1 conversion input with no annotation and no status.

Important content: v1beta1 `VolumeGroupSnapshotContent`, name `new-groupsnapshot-demo`, and empty spec.

Control flow: converter should make no status changes beyond the framework-updated API version.

State and persistence: represents an empty persisted CRD object.

Dependencies and integration: paired with `no_annotation_no_status_v1beta2.yaml`.

Risks and test signals: establishes the no-op conversion baseline.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_no_status_v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_no_status_v1beta2.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_no_status_v1beta2.yaml

Purpose: expected v1beta2 result for a minimal beta1 object with no annotation/status.

Important content: v1beta2 API version, same kind/name/spec, and no status.

Control flow: equality target for no-op beta1-to-beta2 conversion.

State and persistence: no status or metadata conversion state beyond APIVersion.

Dependencies and integration: paired with the beta1 minimal fixture.

Risks and test signals: catches accidental creation of empty status or annotation blocks in no-op conversion.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_no_status_v1beta2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_status_v1beta1.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_status_v1beta1.yaml

Purpose: beta1 input with legacy status list but no preservation annotation.

Important content: v1beta1 content with ready flag, group snapshot handle, and `status.volumeSnapshotHandlePairList` entries containing only snapshot and volume handles.

Control flow: converter should rename the legacy pair list to `status.volumeSnapshotInfoList` without adding beta2-only fields.

State and persistence: models native beta1 status that never passed through beta2 downgrade.

Dependencies and integration: paired with `no_annotation_status_v1beta2.yaml`.

Risks and test signals: verifies non-annotated upgrade remains lossy and does not invent creation/ready/restore per-entry values.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_status_v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_status_v1beta2.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_status_v1beta2.yaml

Purpose: expected v1beta2 output when beta1 legacy status is upgraded without annotation data.

Important content: v1beta2 content retaining top-level status fields and containing `status.volumeSnapshotInfoList` with only snapshot and volume handle pairs.

Control flow: target for rename-only conversion path.

State and persistence: converted status remains less detailed because no preservation annotation was available.

Dependencies and integration: paired with `no_annotation_status_v1beta1.yaml`.

Risks and test signals: catches accidental addition/removal of per-entry fields during rename-only upgrade.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta1_to_v1beta2/no_annotation_status_v1beta2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/annotation_status_v1beta1.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/annotation_status_v1beta1.yaml

Purpose: expected beta1 result when downgrading a detailed v1beta2 status object.

Important content: v1beta1 content with a serialized `volume-snapshot-info-list` annotation preserving full entries, while `status.volumeSnapshotHandlePairList` contains only snapshot/volume handle pairs and top-level status fields remain.

Control flow: used by beta2-to-beta1 conversion test to confirm annotation creation and field stripping.

State and persistence: represents the reversible downgrade storage format.

Dependencies and integration: paired with `annotation_status_v1beta2.yaml`.

Risks and test signals: validates that beta2-only per-entry data is preserved outside the beta1 schema instead of being permanently lost.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/annotation_status_v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/annotation_status_v1beta2.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/annotation_status_v1beta2.yaml

Purpose: beta2 source fixture with detailed per-volume snapshot status used for downgrade testing.

Important content: v1beta2 `VolumeGroupSnapshotContent`, empty annotations, ready and group handle status, and `status.volumeSnapshotInfoList` entries with creation time, ready flag, restore size, snapshot handle, and volume handle.

Control flow: converter serializes this detailed list into an annotation, strips entry-level beta2-only fields for beta1 status, and renames the list.

State and persistence: represents rich beta2 API state before downgrade.

Dependencies and integration: paired with the expected beta1 fixture.

Risks and test signals: ensures downgrade path has source data for all fields that need preservation.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/annotation_status_v1beta2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/no_annotation_no_status_v1beta1.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/no_annotation_no_status_v1beta1.yaml

Purpose: expected beta1 result for downgrading a minimal beta2 object.

Important content: v1beta1 `VolumeGroupSnapshotContent`, name `new-groupsnapshot-demo`, empty spec, and no status or annotations.

Control flow: equality target for no-op beta2-to-beta1 conversion when no `volumeSnapshotInfoList` exists.

State and persistence: minimal object state.

Dependencies and integration: paired with `no_annotation_no_status_v1beta2.yaml`.

Risks and test signals: catches accidental annotation/status creation in no-op downgrade.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/no_annotation_no_status_v1beta1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/no_annotation_no_status_v1beta2.yaml -->
# sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/no_annotation_no_status_v1beta2.yaml

Purpose: minimal beta2 source fixture for downgrade conversion.

Important content: v1beta2 `VolumeGroupSnapshotContent`, same name and empty spec, with no status.

Control flow: converter should leave object content unchanged except APIVersion assigned by framework.

State and persistence: no conversion preservation state.

Dependencies and integration: paired with minimal beta1 expected fixture.

Risks and test signals: verifies no-op downgrade baseline.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/testdata/v1beta2_to_v1beta1/no_annotation_no_status_v1beta2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/webhook.go -->
# sources/control-plane/external-snapshotter/pkg/webhook/webhook.go

Purpose: starts the HTTPS conversion webhook server and wires readiness, conversion, TLS configuration, and certificate watching.

Important APIs/functions: `StartServer`.

Control flow: starts the `CertWatcher` in a goroutine, registers `/readyz` and `/convert` handlers, builds an `http.Server` with read/write/idle timeouts, creates a TLS listener on the requested port, and serves until listener/server failure.

State and persistence: server state is in-memory; certificate state comes from `CertWatcher`. No graceful shutdown call is wired beyond watcher context cancellation.

Dependencies and integration: integrates `net/http`, `crypto/tls`, klog, conversion framework `serve`, and dynamic TLS reload from `CertWatcher`.

Risks and test signals: risks include `Serve` returning an error after context cancellation being treated by caller as failure, fixed port binding issues in tests, and readiness not validating certificate/conversion health. `webhook_test.go` exercises startup and cert reload through this function.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/webhook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/webhook_test.go -->
# sources/control-plane/external-snapshotter/pkg/webhook/webhook_test.go

Purpose: integration-style test for dynamic TLS certificate reload in the webhook server.

Important APIs/functions: `TestWebhookCertReload` and `generateTestCertKeyPair`.

Control flow: the test creates a temp cert/key pair, starts `StartServer` with a `CertWatcher`-backed TLS config on port `30443`, reads the original certificate from `GetCertificate`, rewrites cert/key files five times, waits for fsnotify processing, and asserts both certificate bytes and RSA private key changed each time.

State and persistence: writes temporary `tls.crt` and `tls.key` files, starts a live local TLS server goroutine, and cleans the temp directory.

Dependencies and integration: uses crypto/x509 RSA certificate generation, fsnotify through `CertWatcher`, TLS config callback behavior, and the actual server startup path.

Risks and test signals: strong signal for simple file rewrite reloads. Risks include fixed port collisions, time-based sleeps causing flakiness, panics from the server goroutine, and no HTTP request/assertion against `/readyz` or `/convert`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/pkg/webhook/webhook_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/.github/dependabot.yaml -->
# sources/control-plane/external-snapshotter/release-tools/.github/dependabot.yaml

Purpose: Dependabot configuration for the release-tools repository's GitHub Actions dependencies.

Important keys: `version: 2`, `enable-beta-ecosystems: true`, one update rule for `package-ecosystem: github-actions`, root directory `/`, daily schedule, labels `area/dependency`, `release-note-none`, and `ok-to-test`, and open PR limit `10`.

Control flow: GitHub Dependabot periodically scans workflow actions and opens dependency update PRs under the configured labels.

State and persistence: stored as repository configuration; resulting PRs are persisted in GitHub.

Dependencies and integration: integrates GitHub Dependabot and repository triage conventions.

Risks and test signals: risks are noisy daily PRs or stale action pins if Dependabot cannot parse pinned SHAs. Validation signal is Dependabot successfully opening labeled action-update PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/.github/workflows/codespell.yml -->
# sources/control-plane/external-snapshotter/release-tools/.github/workflows/codespell.yml

Purpose: GitHub Actions workflow that runs codespell on pushes and pull requests.

Important keys/steps: workflow name `codespell`, triggers `push` and `pull_request`, Ubuntu runner, pinned `actions/checkout` and `codespell-project/actions-codespell`, `check_filenames: true`, and skip patterns for images, sum files, git metadata, the workflow file, and prow script.

Control flow: GitHub runs the job, checks out the repo, then executes the codespell action with configured exclusions.

State and persistence: no repo mutation; produces CI status/check logs.

Dependencies and integration: integrates GitHub Actions, pinned third-party actions, and spelling policy used by release-tools.

Risks and test signals: pinned action SHAs improve supply-chain stability but require updates. Skip patterns can hide spelling errors in excluded files. Signal is a passing `codespell` check.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/.github/workflows/trivy.yaml -->
# sources/control-plane/external-snapshotter/release-tools/.github/workflows/trivy.yaml

Purpose: scheduled and master-branch GitHub Actions workflow that scans the configured Go builder image for vulnerabilities with Trivy.

Important keys/steps: workflow name, push-to-master and daily cron triggers, checkout, shell step extracting `CSI_PROW_GO_VERSION_BUILD` from `prow.sh`, and pinned `aquasecurity/trivy-action` scanning `golang:<version>` with exit code `1` for all severities and `ignore-unfixed: true`.

Control flow: checkout repo, parse Go version into `$GITHUB_OUTPUT`, then run Trivy against the corresponding official Golang image.

State and persistence: no repo mutation; vulnerability findings persist in workflow logs and check status.

Dependencies and integration: integrates GitHub Actions, Trivy, `prow.sh` config conventions, and container image vulnerability feeds.

Risks and test signals: parsing `prow.sh` with grep/awk/sed is fragile, scanning only the base Go image may miss repo-built image layers, and all severities can cause frequent failures. Signal is scheduled workflow failure when the selected Go image has unfixed or fixed vulnerabilities matching policy.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/.prow.sh -->
# sources/control-plane/external-snapshotter/release-tools/.prow.sh

Purpose: Prow test entrypoint for the csi-release-tools repository itself.

Important commands: `./verify-shellcheck.sh "$(pwd)"`, `./verify-spelling.sh "$(pwd)"`, and `./verify-boilerplate.sh "$(pwd)"`.

Control flow: bash `-e` exits on the first failed verifier after running from the repository root.

State and persistence: no intended persistent changes; verifier scripts may produce logs.

Dependencies and integration: integrates Prow jobs with shellcheck, spelling, and boilerplate verification scripts.

Risks and test signals: assumes verifier scripts are executable and present in cwd. Strong signal for release-tools hygiene but does not run Go tests or workflow validation.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/boilerplate/boilerplate.py -->
# sources/control-plane/external-snapshotter/release-tools/boilerplate/boilerplate.py

Purpose: verifies that source files contain the expected Kubernetes license boilerplate for their extension or basename.

Important APIs/functions: argument parsing for filenames/rootdir/boilerplate-dir/verbose, `get_refs`, `file_passes`, `file_extension`, `normalize_files`, `get_files`, `get_regexs`, and `main`.

Control flow: loads reference boilerplate text files by extension, discovers target files from explicit args or a tree walk, skips vendor/generated/cache paths, strips Go build tags and shell/Python shebangs, compares the beginning of each file against the reference after normalizing years, and prints failing filenames.

State and persistence: read-only over the repository; writes failures to stdout and optional verbose diagnostics to stderr.

Dependencies and integration: Python standard library only. Used by release-tools verification scripts and Prow.

Risks and test signals: exits with status `0` even when files fail because it prints failures rather than returning nonzero; callers must interpret output. Assumes every extension has a matching boilerplate reference and that year ranges start at 2014.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/cloudbuild.sh -->
# sources/control-plane/external-snapshotter/release-tools/cloudbuild.sh

Purpose: generic Cloud Build entrypoint that delegates image build logic to release-tools `prow.sh`.

Important commands: sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: shell loads shared Prow/release helper functions, then runs the Google Container Registry build helper.

State and persistence: build state and pushed images are managed by `gcr_cloud_build`; this wrapper creates no local state by itself.

Dependencies and integration: requires repositories to import release-tools and provide Cloud Build substitutions/environment expected by `prow.sh`.

Risks and test signals: risks are source path assumptions and failures hidden in sourced helper code. Signal is successful multi-arch Cloud Build image publication.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/cloudbuild.yaml -->
# sources/control-plane/external-snapshotter/release-tools/cloudbuild.yaml

Purpose: reusable Google Cloud Build configuration for Kubernetes CSI multi-architecture image builds.

Important keys: timeout `7200s`, loose substitutions, one build step using `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f`, entrypoint `./.cloudbuild.sh`, environment variables for tag, branch/ref, staging registry, and home, plus default substitutions for `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

Control flow: Cloud Build runs the configured image and invokes repository-specific `.cloudbuild.sh`, which usually delegates into release-tools image build helpers.

State and persistence: persists built container images to the configured staging registry; Cloud Build logs retain build evidence.

Dependencies and integration: integrates Kubernetes image-pushing infrastructure, csi-release-tools, repository Dockerfiles accepting `binary` build args, and staging projects.

Risks and test signals: risks include floating expectations around build image tooling, long timeout masking hangs, loose substitutions hiding missing values, and repo-specific Dockerfile incompatibility. Signal is successful Cloud Build and promoted staging image artifacts.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/contrib/get_supported_version_csi-sidecar.py -->
# sources/control-plane/external-snapshotter/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: helper script that queries GitHub releases for CSI sidecar repositories and prints versions still supported under Kubernetes CSI support-window policy, optionally with release image names.

Important APIs/functions: `check_gh_command`, `duration_ago`, `parse_version`, `end_of_life_grouped_versions`, `get_release_docker_image`, `get_versions_from_releases`, and `main`.

Control flow: validates `gh` availability, parses one or more `--repo` arguments, fetches `gh release list`, groups semver releases by major/minor, selects latest release always plus recent minor/patch lines based on one-year and three-month windows, prints dates/ages, and optionally calls `gh release view` to extract `docker pull` image names.

State and persistence: read-only network interaction through GitHub CLI; no local files are written.

Dependencies and integration: depends on Python, `python-dateutil`, GitHub CLI authentication/network access, CSI release naming conventions, and release-note text containing docker pull commands.

Risks and test signals: risks include current-date-dependent output, GitHub CLI table format changes, regex ignoring prereleases/non-v semver tags, and policy drift. Signal is plausible supported-version table output for known sidecar repos.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/contrib/get_supported_version_csi-sidecar.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/filter-junit.go -->
# sources/control-plane/external-snapshotter/release-tools/filter-junit.go

Purpose: command-line tool that merges and filters JUnit XML test results so only testcases whose names match a regular expression remain.

Important APIs/types/functions: flags `-o` and `-t`, structs `TestResults`, `TestSuite`, `TestCase`, `SkipReason`, custom skip marshal/unmarshal, and `main`.

Control flow: parses flags, compiles the testcase regex, reads each input file, unmarshals either direct `<testsuite>` or Ginkgo v2 `<testsuites><testsuite>` format, appends cases, filters by regex into a map keyed by testcase name, replaces all-skipped entries with real run entries when available, marshals the resulting suite, and writes to stdout or file.

State and persistence: reads input XML files/stdin and writes filtered XML to stdout or output path. The stdin branch appears flawed because `os.Stdin.Read(data)` reads into a nil slice.

Dependencies and integration: uses Go standard library XML, regexp, flags, and OS file APIs. Intended for Prow/Spyglass/Ginkgo test result post-processing.

Risks and test signals: map iteration makes output testcase ordering nondeterministic, stdin reading is likely broken, XML struct coverage is intentionally partial, and duplicate testcase handling may discard useful failures. No tests in this subset cover it.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/filter-junit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/generate-patch-release-notes.sh -->
# sources/control-plane/external-snapshotter/release-tools/generate-patch-release-notes.sh

Purpose: semi-automated release-manager script for generating patch release changelog entries and opening PRs against CSI sidecar release branches.

Important variables/functions: required env vars `CSI_RELEASE_TOKEN` and `GITHUB_USER`, editable `releases` array, `gen_patch_relnotes`, `minorPatchPattern`, branch naming `changelog-release-$minor`, and `gh pr create`.

Control flow: for each configured repo/version, derives minor and previous patch tag, checks out the upstream release branch into a local branch, runs Kubernetes `release-notes`, prepends generated notes to `CHANGELOG-$minor.md`, commits, force-pushes, and opens a PR with release-note-none body.

State and persistence: mutates local git worktrees, removes temporary files and `/tmp/k8s-repo`, creates commits, pushes branches, and opens GitHub PRs.

Dependencies and integration: depends on bash, git remotes named upstream/origin, GitHub CLI, release-notes tool, GitHub token, and CSI repo changelog layout.

Risks and test signals: destructive branch deletion/force-push behavior, empty default releases array, no regeneration handling, fragile version parsing, and direct changelog prepending. Signal is a generated PR with correct changelog diff and release-note body.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/generate-patch-release-notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/go-get-kubernetes.sh -->
# sources/control-plane/external-snapshotter/release-tools/go-get-kubernetes.sh

Purpose: updates Go module dependencies that come from `kubernetes/kubernetes` staging modules to a target Kubernetes version, adding necessary `replace` directives to avoid fake `v0.0.0` module revisions.

Important variables/functions: option `-p` for pruning unused replaces, `help`, `die`, target version argument, fetched Kubernetes `go.mod`, staging module extraction, `go mod edit -replace/-dropreplace`, package discovery via `go list`, and final `go get`.

Control flow: fetches upstream Kubernetes go.mod for `v<version>`, extracts staging modules, downloads each `kubernetes-<version>` module to discover concrete versions, writes replace directives, optionally prunes unused modules, lists k8s.io packages in the current module, maps packages to staging modules with replaces, and runs `go get` for the selected package versions.

State and persistence: mutates the current repo's `go.mod` and indirectly `go.sum`; network downloads populate module cache.

Dependencies and integration: depends on curl, sed, grep, Go modules, network access to GitHub/module proxy, and Kubernetes staging version conventions. Used by broader release-tools update scripts.

Risks and test signals: risks include remote go.mod parsing drift, command failure under partially broken modules, package-vs-module mapping edge cases, and unquoted dependency expansion. Success signal is `SUCCESS` plus clean `go mod tidy`/build in the caller.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/go-get-kubernetes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/go-modules-targeted-update.sh -->
# sources/control-plane/external-snapshotter/release-tools/go-modules-targeted-update.sh

Purpose: batch script for updating specific Go modules across selected CSI sidecar release branches and opening PRs.

Important variables: `org`, editable `modules` array, editable `releases` array, required `GITHUB_USER`, and PR body listing updated modules.

Control flow: for each repo/branch entry, fetches upstream, recreates `module-update-$branch`, runs `go get` for each target module, runs `go mod tidy` and `go mod vendor`, commits all changes, force-pushes to the user's fork, and opens a GitHub PR against the branch.

State and persistence: mutates multiple local git worktrees, vendored dependencies, go.mod/go.sum, branches, commits, remote branches, and PRs.

Dependencies and integration: depends on bash, git, Go toolchain, vendoring workflow, GitHub CLI, and repo remotes.

Risks and test signals: no automated build/test before PR creation, force-pushes branches, default releases list is commented out, and interface incompatibilities are explicitly manual. Signal is successful PR creation and later CI passing.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/go-modules-targeted-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/go-modules-update.sh -->
# sources/control-plane/external-snapshotter/release-tools/go-modules-update.sh

Purpose: broad batch update script for refreshing release-tools and Kubernetes Go dependencies across many CSI repositories and branches.

Important variables/control knobs: `MAX_RETRY=10`, options `-u` username and `-v` Kubernetes version, hard-coded repo/branch here-doc, branch name `module-update-$i`, `git subtree pull --prefix=release-tools`, retry loop around `release-tools/go-get-kubernetes.sh -p`, `make test`, and `gh pr create`.

Control flow: authenticates `gh`, iterates repos, fetches origin, recreates update branches, pulls csi-release-tools into `release-tools` with conflict fallback that replaces the directory from `FETCH_HEAD`, runs Kubernetes dependency update with retries and repeated tidy/vendor, commits, rewrites origin to the user's fork, runs tests, force-pushes, and opens PRs.

State and persistence: heavily mutates local repos, git branches/remotes, release-tools subtree, vendored dependencies, commits, remote branches, and GitHub PRs.

Dependencies and integration: depends on POSIX shell plus bash-like constructs in some environments, git subtree, Go toolchain, make targets, GitHub CLI, network access, and release-tools scripts.

Risks and test signals: risks include destructive branch deletion, remote URL mutation, hard-coded PR head `module-update-master` even when iterating other branches, fragile retry condition syntax, conflict fallback replacing release-tools wholesale, and running `gh auth login` interactively. Signal is successful `make test`, pushed branch, and PR for each repo.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/go-modules-update.sh -->
