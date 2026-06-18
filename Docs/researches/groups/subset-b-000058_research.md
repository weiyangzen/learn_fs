# subset-b-000058 research

Grouped research report for the requested containerd metadata, metrics, and mount files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/gc_test.go -->
# sources/cloud-native/containerd/core/metadata/gc_test.go

Purpose: validates the metadata garbage-collection graph by constructing synthetic bbolt layouts for content, images, containers, snapshots, ingests, leases, and sandboxes. It is a white-box test of root discovery, reference discovery, removal behavior, and custom collector integration.

Important APIs and helpers: `TestResourceMax`, `TestGCRoots`, `TestGCRemove`, `TestGCRefs`, and `TestCollectibleResources` call internal GC context methods such as `scanRoots`, `scanAll`, `references`, and `remove`. The `testCollector` implements the package collector interfaces with `All`, `Active`, `ActiveWithBackRefs`, `Leased`, and `Remove`. Helper `alterFunc` builders (`addImage`, `addSnapshot`, `addContent`, `addIngest`, `addLease*`, `addContainer`, `addSandbox`) create exact bucket structures under `bucketKeyVersion`.

Control flow: each test opens a temporary bbolt database, applies a list of bucket mutations in one update transaction, then scans through the metadata GC implementation and compares sorted `gc.Node` lists. `TestGCRefs` first primes roots and then checks the reference set for many node types, including label references, back references, flat references, conditional snapshot references, and expired/non-expired resources.

State and persistence: the tests intentionally bypass public stores and write bbolt buckets directly, making them sensitive to schema names and label contracts. They cover namespace separation and resource key encoding such as `snapshotter/name` for snapshots and digest strings for content.

Dependencies and integration: depends on `github.com/containerd/containerd/v2/pkg/gc`, `boltutil`, `go-digest`, and `logtest`. It integrates with the metadata package's internal bucket helpers and GC label constants, so failures often indicate schema or label-semantic regressions.

Risks: because the tests mirror internal bbolt layout, any schema migration must update these helpers. Time-sensitive expiration checks use `time.Now()` and can be fragile if expiration boundary handling changes. The comparison helper sorts nodes but preserves duplicate references, so duplicate reference behavior is explicitly part of the signal.

Test signals: strong coverage for GC graph correctness, resource deletion, root expiration, custom resource collectors, back-reference hooks, and malformed reference labels. It does not exercise live DB compaction or concurrent GC execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/gc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/images.go -->
# sources/cloud-native/containerd/core/metadata/images.go

Purpose: implements the namespace-scoped `images.Store` on top of the metadata bbolt database, including image CRUD, filtering, validation, persistence encoding, lease linkage for expiring images, and create/update/delete event publication.

Important APIs and types: `imageStore`, `NewImageStore`, `Get`, `List`, `Create`, `Update`, and `Delete` implement the public image store contract. Internal helpers `validateImage`, `validateTarget`, `readImage`, `writeImage`, and `encodeInt` enforce image target requirements and serialize descriptor fields.

Control flow: every public method first requires a namespace from context. Reads use `view`; mutations use `update`. `Create` validates the image, creates the namespace images bucket, optionally records an image lease through `addImageLease`, creates an image bucket, stamps `CreatedAt` and `UpdatedAt`, writes labels/annotations/target, then publishes `/images/create`. `Update` reads the existing record, applies either full replacement or selected field paths (`labels`, `labels.KEY`, `annotations`, `annotations.KEY`, `target`), validates, preserves `CreatedAt`, refreshes `UpdatedAt`, writes the bucket, and publishes `/images/update`. `Delete` can check an expected target digest before bucket deletion and publishes `/images/delete`.

State and persistence: images live under the versioned namespace images bucket, one subbucket per image name. Timestamps, labels, and annotations are stored via `boltutil`; target descriptor fields are stored in a nested `target` bucket as digest, media type, and varint size. The store increments the DB dirty counter on delete so GC can be triggered.

Dependencies and integration: depends on `images.Store`, OCI descriptors, `filters`, `labels`, namespace context, bbolt errors, `epoch.FromContext` for deterministic timestamps, and metadata lease helpers. It integrates with the DB publisher for image lifecycle events and with GC through labels and lease references.

Risks: `Update` only supports full target replacement, not partial target fields. `addImageLease` only adds expiring images to an active lease; an update removing expiration does not explicitly remove old lease entries. `readImage` ignores varint decoding errors for size, so corrupt size bytes can silently decode to zero and be caught only if later validation occurs.

Test signals: covered by `images_test.go` for create/list/filter/update/delete, timestamp behavior, target validation, fieldpath behavior, and digest-guarded delete failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/images.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/images_test.go -->
# sources/cloud-native/containerd/core/metadata/images_test.go

Purpose: tests the bbolt-backed image store behavior for listing, filters, validation, fieldpath updates, timestamp semantics, and target-checked deletion.

Important APIs and helpers: `TestImagesList`, `TestImagesCreateUpdateDelete`, `imageBase`, `checkImageTimestamps`, and `checkImagesEqual`. The test operates through `NewImageStore(NewDB(...))`, not raw buckets.

Control flow: `TestImagesList` creates four images with labels and target annotations, then runs filter cases for full set, label disjunction, specific labels, name, combined filters, and target media type pattern. It deletes every image and expects a second delete to return not found. `TestImagesCreateUpdateDelete` table-drives create and update cases, including label replacement, single-label mutation, annotation mutation, full target replacement, invalid targets, update of a non-existent name, and digest-checked delete.

State and persistence: verifies timestamps are set on create, equal on create, and `UpdatedAt` advances on update while `CreatedAt` is preserved. Tests compare complete `images.Image` structs after get/list/update, so persisted labels, annotations, target size/media type/digest, and timestamps all matter.

Dependencies and integration: uses containerd `images` package, filter parser, `errdefs`, OCI descriptors, `go-digest`, and the local test DB environment. It validates behavior exposed by `images.go`.

Risks: tests rely on wall-clock timestamp ordering and assume update time is after create time. Table names become image names, so duplicate test names could collide if subtests were run in the same store with reused names.

Test signals: strong signal for store-level behavior and fieldpath semantics. It does not inspect event publication or lease side effects for expiring images.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/images_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/leases.go -->
# sources/cloud-native/containerd/core/metadata/leases.go

Purpose: implements a metadata-backed `leases.Manager` and the internal helpers used by content, ingest, image, and snapshot code to attach or remove resources from the current lease in context.

Important APIs and types: `leaseManager`, `NewLeaseManager`, `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources` implement the public lease contract. Internal helpers include `addSnapshotLease`, `removeSnapshotLease`, `addContentLease`, `removeContentLease`, `addIngestLease`, `removeIngestLease`, `addImageLease`, `removeImageLease`, and `parseLeaseResource`.

Control flow: public methods require a namespace. `Create` applies lease options, requires an ID, creates the namespace lease bucket, writes `createdat`, optional labels, and returns the created lease. `Delete` removes the lease bucket and increments DB dirty state. `List` parses filters, iterates lease subbuckets, reads timestamps and labels, and matches `adaptLease`. Resource add/delete methods validate the lease exists, parse resource type into nested bucket keys, and write or delete a nil value at the resource ID. `ListResources` walks content, images, ingests, and nested snapshotter buckets to rebuild `leases.Resource` values.

State and persistence: leases live under `v1/<namespace>/leases/<lease-id>`. Resource references are nested by type, with snapshots stored as `snapshots/<snapshotter>/<snapshot-key>`. Content resource IDs are normalized through digest parsing. Image lease helpers only attach images with `containerd.io/gc.expire` labels, matching expiring image GC semantics.

Dependencies and integration: depends on `leases`, `boltutil`, `filters`, `namespaces`, `errdefs`, bbolt, and `go-digest`. It is called by image, content, ingest, and snapshot metadata paths when `leases.WithLease` has been placed in context.

Risks: invalid or unsupported resource types produce `ErrInvalidArgument` or `ErrNotImplemented`; callers must preserve these distinctions. Helper functions panic if the namespace has not already been required in code paths where that invariant is assumed. Delete helpers silently succeed when the resource-type bucket does not exist, making cleanup idempotent but possibly masking missing lease references.

Test signals: `leases_test.go` covers create/delete/list filtering, duplicate IDs, supported and unsupported resource types, digest validation, snapshot type encoding, resource listing, and deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/leases.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/leases_test.go -->
# sources/cloud-native/containerd/core/metadata/leases_test.go

Purpose: verifies metadata lease lifecycle, filter behavior, and resource reference validation/listing/deletion.

Important APIs and helpers: `TestLeases`, `TestLeasesList`, and `TestLeaseResource` exercise `NewLeaseManager`, `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`.

Control flow: `TestLeases` creates leases inside bbolt transactions, expects duplicate create to map to `ErrAlreadyExists`, lists created leases and timestamps, then deletes them and checks not-found behavior. `TestLeasesList` creates labeled leases and table-drives ID and label filters. `TestLeaseResource` creates one lease, attempts to add content, ingest, image, and snapshot resources plus invalid lease/container/snapshot type cases, then validates `ListResources` uniqueness and snapshot deletion.

State and persistence: tests use the real bbolt-backed lease manager, including transactional context via `boltutil.WithTransaction`. Resource expected values reflect normalized content digest IDs and nested snapshot type strings such as `snapshots/overlayfs`.

Dependencies and integration: uses `leases`, bbolt, `errdefs`, and metadata test environment helpers. It is a direct behavioral check for `leases.go`.

Risks: the create/delete test has lenient error handling around expected delete errors, so not all delete-error paths are equally strong. Resource list ordering is not assumed; the test uses a map.

Test signals: good coverage for lease CRUD, filters, supported resource encodings, duplicate add idempotency, and explicit rejection of unsupported resource families.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/leases_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/migrations.go -->
# sources/cloud-native/containerd/core/metadata/migrations.go

Purpose: declares ordered metadata database migrations and implements schema transitions for snapshot child links, ingest bucket restructuring, a historical no-op, and sandbox bucket relocation.

Important APIs and types: `migration` holds schema, version, and function. `migrations` is the ordered migration list. Migration functions are `addChildLinks`, `migrateIngests`, `migrateSandboxes`, and `noOpMigration`.

Control flow: `addChildLinks` iterates every namespace and snapshotter, finds snapshots with a `parent`, and adds each child key under the parent's `children` bucket when the parent exists. `migrateIngests` moves deprecated flat ingest entries from `content/ingest` into structured `content/ingests/<ref>/ref`, then deletes the deprecated bucket. `migrateSandboxes` creates the version bucket, iterates root-level namespace buckets other than `v1`, copies sandbox buckets and subbuckets into `v1/<namespace>/sandboxes`, then deletes the old root namespace buckets. `noOpMigration` intentionally returns nil for the old bolt-to-bbolt transition.

State and persistence: all migrations mutate bbolt schema in place. `migrateSandboxes` copies key/value entries and one nested subbucket level for each sandbox, and treats unexpected deeper buckets as errors. `addChildLinks` deliberately skips inconsistent parent references rather than failing the migration.

Dependencies and integration: used by metadata DB open/upgrade paths elsewhere in the package. It depends on bbolt and bucket key constants shared by stores and GC.

Risks: migration order is contractually important and comments require a migration test for each new entry. `migrateSandboxes` deletes all non-`v1` root buckets after attempting sandbox migration; if unexpected root buckets existed, they would be removed by design in this schema transition. `addChildLinks` can leave inconsistent child state if parent buckets are missing.

Test signals: this file itself has no tests in the subset, but related snapshot remove behavior depends on child links, and sandbox tests depend on post-migration bucket layout assumptions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/migrations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/namespaces.go -->
# sources/cloud-native/containerd/core/metadata/namespaces.go

Purpose: implements a transaction-scoped `namespaces.Store` backed by metadata bbolt buckets, including namespace creation, label management, listing, and guarded deletion.

Important APIs and types: `namespaceStore`, `NewNamespaceStore`, `Create`, `Labels`, `SetLabel`, `List`, `Delete`, `listNs`, and `isBucketEmpty`.

Control flow: `Create` ensures the version bucket, validates namespace identifier and labels, creates the namespace bucket, then writes labels under the labels bucket. `Labels` returns an empty map when no label bucket exists. `SetLabel` validates the key/value and deletes the label when value is empty. `List` returns all subbuckets under the version bucket. `Delete` applies delete options, calls `listNs`, refuses non-empty namespaces with a failed-precondition error, and deletes the namespace bucket otherwise.

State and persistence: namespaces are top-level subbuckets under `bucketKeyVersion`. Labels are stored in a dedicated labels bucket. Deletion checks only major object families for emptiness: images, blobs, containers, and per-snapshotter snapshot buckets.

Dependencies and integration: depends on identifier and label validation packages, namespace API types, bbolt, and metadata bucket helpers. It is used within DB transaction paths that expose namespace management.

Risks: `Delete` assumes the version bucket exists before deleting; callers should only delete known namespaces. `listNs` intentionally returns object type summaries rather than exact objects, so error messages are diagnostic but not exhaustive. The delete emptiness check must be kept in sync with persisted object families that should block namespace deletion.

Test signals: `namespaces_test.go` covers empty deletion and deletion refusal when containers and snapshotter data exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/namespaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/namespaces_test.go -->
# sources/cloud-native/containerd/core/metadata/namespaces_test.go

Purpose: tests namespace creation and guarded deletion for both empty and non-empty namespace states.

Important APIs and helpers: `TestCreateDelete` uses `NewNamespaceStore`, `Create`, and `Delete`; it also creates a container through `NewContainerStore` and writes snapshotter data directly.

Control flow: table cases create a namespace, optionally populate it with a container and snapshotter bucket, then attempt deletion inside a bbolt update transaction. The empty case expects success; the non-empty case expects an error containing both containers and snapshotter data.

State and persistence: the test writes under the real namespace bucket layout, including `createSnapshotterBucket`, to validate the same emptiness checks used by namespace deletion.

Dependencies and integration: integrates namespace store with container store and snapshotter bucket helpers. Uses `testDB`, `namespaces.WithNamespace`, protobuf `Any`, and testify assertions.

Risks: assertion checks error text, so wording changes in `Delete` may require test updates. It does not cover labels, `SetLabel`, duplicate namespace create, or image/blob blockers.

Test signals: focused signal that namespaces cannot be deleted while selected object families remain.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/namespaces_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/sandbox.go -->
# sources/cloud-native/containerd/core/metadata/sandbox.go

Purpose: implements the bbolt-backed sandbox metadata store for create, update, get, list, delete, validation, and serialization of sandbox runtime/spec/extension fields.

Important APIs and types: `sandboxStore`, `NewSandboxStore`, `Create`, `Update`, `Get`, `List`, `Delete`, and internal `write`, `read`, `validate`. The type asserts it implements `sandbox.Store`.

Control flow: public methods require a namespace. `Create` starts a tracing span, stamps timestamps, validates ID/timestamps, creates the sandbox bucket, and writes the sandbox without overwrite. `Update` reads the existing sandbox, defaults to updating labels/extensions/spec/runtime when no fieldpaths are provided, forbids changing runtime name in the no-fieldpaths path, applies selected full or dotted field updates, refreshes `UpdatedAt`, and writes with overwrite. `Get` and `List` read buckets through view transactions, with `List` applying parsed filters. `Delete` deletes the sandbox bucket and maps missing buckets to not found.

State and persistence: each sandbox is a bucket under `v1/<namespace>/sandboxes/<id>`. Timestamps, labels, extensions, and `Any` spec/options use `boltutil`. Runtime data is nested under a runtime bucket, with name and options. `Sandboxer` is stored as a direct key and defaults to empty when absent for compatibility.

Dependencies and integration: depends on `core/sandbox`, `boltutil`, filters, identifiers, namespaces, tracing, errdefs, typeurl, and bbolt. It integrates with metadata GC through sandbox labels and with tracing through `metadata.sandbox.*` spans.

Risks: `Update` does not call `validate` before writing directly, but `write` revalidates. Dotted field updates can set map entries to zero values when the input map lacks the key. Full update without fieldpaths allows replacing runtime options but rejects runtime name changes only in that path; explicit `runtime` fieldpath can replace the runtime struct.

Test signals: `sandbox_test.go` covers create/get, duplicate create, fieldpath update, get missing ID, list, filter list, delete, and comparison ignoring timestamps.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/sandbox_test.go -->
# sources/cloud-native/containerd/core/metadata/sandbox_test.go

Purpose: validates sandbox store persistence, update semantics, filtering, duplicate handling, and delete behavior.

Important APIs and helpers: tests call `NewSandboxStore`, `Create`, `Get`, `Update`, `List`, and `Delete`. `assertEqualInstances` uses `cmp.Diff` with shared comparison options such as `compareAny` and `ignoreTime`.

Control flow: tests create sandboxes with labels, protobuf `Any` specs/options, typeurl extensions, runtime data, and sandboxer strings. Update tests mutate one label, add one extension, and replace spec via fieldpaths. List tests check full listing and `id==1` filtering. Delete removes a sandbox then expects a subsequent get to return not found.

State and persistence: exercises nested runtime option storage, extension maps, sandboxer persistence, and timestamp-insensitive equality. It checks compatibility with nil and populated `Any` fields.

Dependencies and integration: uses `core/sandbox`, protobuf types, `typeurl`, errdefs, go-cmp, and metadata test DB helpers.

Risks: timestamps are ignored in equality, so only presence through production validation is indirectly covered. Runtime immutability on no-fieldpath update is not directly tested here.

Test signals: good CRUD and fieldpath coverage for `sandbox.go`; limited coverage for invalid IDs beyond missing get and for invalid fieldpaths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/sandbox_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/snapshot.go -->
# sources/cloud-native/containerd/core/metadata/snapshot.go

Purpose: wraps a backend `snapshots.Snapshotter` with metadata namespace mapping, bbolt persistence, leases, events, filtering, and garbage collection of backend snapshots no longer referenced by metadata.

Important APIs and types: `snapshotter`, `newSnapshotter`, `createKey`, `getKey`, `resolveKey`, and methods `Stat`, `Update`, `Usage`, `Mounts`, `Prepare`, `View`, `Commit`, `Remove`, `Walk`, `garbageCollect`, `walkTree`, `pruneBranch`, and `Close`. Helper types include `infoPair` and `treeNode`.

Control flow: public operations require namespace. Metadata snapshot names map to backend keys generated as `<namespace>/<sequence>/<key>`. `Stat` reads local labels/timestamps/parent/backend key, stats the backend key, and overlays local metadata. `Update` mutates local labels, validates them, writes timestamps and labels, and updates inherited labels on the backend inside the same transaction. `Prepare` and `View` route through `createSnapshot`, which reserves a backend key, handles `containerd.io/snapshot.ref` target deduplication, calls backend `Prepare` or `View`, then records metadata, parent child links, timestamps, labels, backend key, and lease references. `Commit` creates metadata for the committed name, moves child links from active key to committed name, removes active lease, and calls backend commit inside the transaction. `Remove` refuses snapshots with children, removes parent child links, deletes metadata, removes lease linkage, marks DB dirty, and publishes removal. `Walk` batches metadata pairs, stats backends, overlays local fields, and applies filters. `garbageCollect` builds the backend keys referenced by all namespaces, walks backend snapshot trees, and removes unreferenced branches child-first.

State and persistence: stores snapshots under `v1/<namespace>/snapshots/<snapshotter>/<name>`, with backend `name`, optional metadata parent, children bucket, timestamps, and labels. Only labels with the inherited prefix are forwarded to backend snapshotters. Dirty snapshotter state is recorded for deferred backend GC.

Dependencies and integration: depends on `snapshots`, metadata DB, bbolt, `boltutil`, `filters`, `labels`, namespace context, leases, events, mount types, logging, and backend `snapshots.Cleaner` when available. It is central to metadata DB snapshotter behavior.

Risks: backend operations in transactions reduce inconsistency windows but can leave metadata/backend divergence if the transaction fails after backend update/commit. Target reference handling depends on backend `Walk` honoring or at least being checked against labels and parent. `Walk` batching uses `lastKey` and mutable `pairs`; pagination correctness is important for large stores. `Commit` has special rebase behavior when active metadata lacks a parent but commit options include one.

Test signals: `snapshot_test.go` covers target reference deduplication, cross-namespace behavior, leases, and inherited labels; `snapshot_suite_test.go` runs the generic snapshotter suite against a native backend.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/snapshot_suite_test.go -->
# sources/cloud-native/containerd/core/metadata/snapshot_suite_test.go

Purpose: runs containerd's generic snapshotter tests against the metadata snapshotter wrapping the native snapshotter backend.

Important APIs and helpers: `newTestSnapshotter` creates a native snapshotter root, opens a metadata bbolt DB, wraps the native backend with `metadata.NewDB(...).Snapshotter("native")`, and returns cleanup. `TestMetadata` invokes `testsuite.SnapshotterSuite`.

Control flow: the test skips on Windows and requires root because the generic suite needs mount-capable snapshotter behavior. It creates isolated temporary roots for native snapshot data and metadata DB.

State and persistence: exercises real native snapshotter state plus metadata DB mapping state. Cleanup closes both wrapped snapshotter and DB.

Dependencies and integration: depends on `plugins/snapshots/native`, bbolt, `snapshots/testsuite`, testutil root checks, and the public metadata package. It is an integration-level signal rather than a white-box test.

Risks: root and platform requirements mean this suite is skipped in many CI contexts. Failures may originate from native snapshotter behavior, metadata wrapper behavior, kernel mount behavior, or environment.

Test signals: broad contract coverage for the metadata snapshotter as an implementation of the snapshotter interface.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/snapshot_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/snapshot_test.go -->
# sources/cloud-native/containerd/core/metadata/snapshot_test.go

Purpose: provides targeted unit tests and a fake backend snapshotter for metadata snapshot reference, lease, namespace, and inherited-label behavior.

Important APIs and helpers: `snapshotLease`, `TestSnapshotterWithRef`, `TestFilterInheritedLabels`, `tmpSnapshotter`, and `NewTmpSnapshotter`. The fake implements `snapshots.Snapshotter` with in-memory maps of snapshots and target references.

Control flow: `TestSnapshotterWithRef` creates a metadata DB with a fake snapshotter, uses leases in multiple namespaces, prepares and commits snapshots with `containerd.io/snapshot.ref`, verifies already-exists behavior, checks cross-namespace materialization of target snapshots, validates parent mismatch/not-found behavior, and checks lease resource changes for active and committed names. `TestFilterInheritedLabels` table-drives label filtering for the inherited label prefix. The fake backend models target deduplication by returning already-exists when a target with the same parent exists.

State and persistence: the test combines metadata bbolt state, lease resources, namespace contexts, and fake backend maps. The fake stores `snapshots.Info` keyed by backend name and target-to-backend-name indexes.

Dependencies and integration: uses leases, snapshots, mount, filters, namespaces, and errdefs. It is a direct test of `snapshot.go` target and lease flows.

Risks: fake backend behavior approximates but does not fully reproduce real snapshotter implementations. Time values and map iteration order are not central to assertions.

Test signals: strong signal for snapshot reference deduplication, lease attachment/removal, cross-namespace target sharing, and inherited label filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/cgroups.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/cgroups.go

Purpose: registers the Linux cgroups task monitor plugin and selects the cgroup v1 or v2 monitor implementation at initialization time.

Important APIs and types: `Config` with `NoPrometheus`, package `init` registering `plugins.TaskMonitorPlugin` ID `cgroups`, and `New` as plugin init function.

Control flow: plugin registration declares an event plugin dependency and migrates the previous plugin config name into the current task monitor config key. `New` creates a Docker metrics namespace unless Prometheus is disabled, obtains the event publisher, selects v2 when `cgroups.Mode() == cgroups.Unified` otherwise v1, registers metrics namespace when enabled, records the default platform, and returns the task monitor.

State and persistence: no persistent state. Runtime state is the selected monitor and registered Prometheus namespace.

Dependencies and integration: integrates with containerd plugin registry, events publisher, runtime task monitor interface, Docker metrics registry, cgroups mode detection, config migration, and platform metadata.

Risks: metrics namespace registration is global and should not be duplicated unexpectedly in tests. Selection depends on host cgroup mode, so behavior differs by environment. Disabling Prometheus still returns a monitor but collectors become inert.

Test signals: indirectly covered by `metrics_test.go`, which instantiates v1/v2 collectors based on cgroup mode; plugin registration itself is not directly tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/cgroups.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/common/type.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/common/type.go

Purpose: defines the shared interface used by cgroup metrics collectors to get task identity, namespace, and encoded stats.

Important APIs and types: `Statable` requires `ID() string`, `Namespace() string`, and `Stats(context.Context) (*types.Any, error)`.

Control flow: no runtime logic; v1 and v2 collectors accept `common.Statable` entries and call `Stats` under a namespaced timeout context during Prometheus collection.

State and persistence: none.

Dependencies and integration: depends on context and containerd protobuf `types.Any`. It bridges runtime tasks and metrics collectors without importing runtime task concrete types into descriptor files.

Risks: collectors assume returned `Any` can be unmarshaled into the selected cgroup version metrics type. Mismatched cgroup mode and stats payload type cause logged collection errors rather than returned errors.

Test signals: `metrics_test.go` defines `mockStatT` implementing this interface for concurrency regression coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/common/type.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/metrics_test.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/metrics_test.go

Purpose: regression test for a collector deadlock reported in containerd issue 6772, where metric collection and task addition could contend on locks.

Important APIs and types: `TestRegressionIssue6772`, local `Collector` interface, and `mockStatT` implementing `common.Statable`.

Control flow: the test creates a metrics namespace and chooses v1 or v2 collector based on host cgroup mode. One goroutine continuously calls namespace `Collect`, while many goroutines concurrently call collector `Add` with const labels. A metric drain goroutine prevents channel backpressure. The test fails if any add errors or if adds do not finish within 30 seconds.

State and persistence: no persistent state. Runtime state is collector task maps, namespace labels, and metrics channels.

Dependencies and integration: uses cgroups mode detection, v1/v2 collectors, typeurl marshaling of empty v1/v2 metrics payloads, Docker metrics namespace, and Prometheus metric channels.

Risks: this is a timing/concurrency regression test and may be sensitive to heavily loaded CI, though the timeout is generous. It validates absence of a deadlock but not emitted metric values.

Test signals: strong concurrency signal for `Collector.Add` versus `Namespace.Collect` lock ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/blkio.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/blkio.go

Purpose: declares Prometheus metric descriptors for cgroup v1 blkio statistics and maps blkio stat entries into labeled metric values.

Important APIs and data: `blkioMetrics` contains descriptors for merged, queued, service bytes, service time, serviced, io time, and sectors recursive stats. `blkioValues` converts `[]*v1.BlkIOEntry` into `[]value` with labels `op`, `device`, `major`, and `minor`.

Control flow: each metric returns nil when `stats.Blkio` is absent, otherwise delegates to `blkioValues` for the relevant recursive slice.

State and persistence: no state; descriptors are global package variables used by the v1 collector.

Dependencies and integration: depends on cgroup v1 metrics aliases, Docker metrics units, and Prometheus value types. Integrated by `v1.NewCollector` appending `blkioMetrics`.

Risks: metric cardinality depends on blkio device entries and can grow with device count. All values are gauges, so downstream rate calculations must be done by consumers.

Test signals: no direct value tests in subset; collector concurrency test can traverse descriptors with empty stats.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/blkio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/cgroups.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/cgroups.go

Purpose: implements the cgroup v1 runtime task monitor, wiring the Prometheus collector and v1 OOM event monitor to runtime tasks.

Important APIs and types: `NewTaskMonitor`, `cgroupsMonitor`, `cgroupTask`, `Monitor`, `Stop`, and `trigger`.

Control flow: `NewTaskMonitor` creates the metrics collector and OOM collector. `Monitor` adds the task to the collector, then, if the task exposes `Cgroup()`, obtains the cgroup and registers OOM monitoring. Missing cgroups are ignored; unsupported memory OOM monitoring is logged as a warning and not fatal. `Stop` removes the task from metric collection. `trigger` publishes a `TaskOOM` event under the task namespace.

State and persistence: runtime-only state in collectors and OOM epoll registrations.

Dependencies and integration: integrates runtime tasks, cgroup1 objects, event publisher, namespaces, Docker metrics, errdefs, and the OOM collector.

Risks: `Stop` removes metrics but does not directly deregister OOM fds; OOM collector cleanup relies on cgroup deletion events/state in `oom.go`. Tasks not implementing `cgroupTask` get metrics but no OOM event monitoring.

Test signals: indirectly exercised by collector tests; OOM event path is not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/cgroups.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/cpu.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/cpu.go

Purpose: declares cgroup v1 CPU Prometheus metrics for total, kernel, user, per-CPU, and throttling stats.

Important APIs and data: `cpuMetrics` includes `cpu_total`, `cpu_kernel`, `cpu_user`, `per_cpu` labeled by CPU index, `cpu_throttle_periods`, `cpu_throttled_periods`, and `cpu_throttled_time`.

Control flow: each descriptor returns nil when `stats.CPU` is absent. Per-CPU usage iterates `stats.CPU.Usage.PerCPU` and labels each value with the CPU index.

State and persistence: no persistent state; descriptors are global and appended into the v1 collector.

Dependencies and integration: depends on v1 stats aliases, Docker metrics units, Prometheus gauges, and collector descriptor machinery in `metric.go`.

Risks: per-CPU metrics can create high cardinality on large hosts. CPU cumulative counters are exposed as gauge values, so consumers need to understand the cgroup stat semantics.

Test signals: no direct value tests; empty stat handling is indirectly exercised by collector regression tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/cpu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/hugetlb.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/hugetlb.go

Purpose: declares cgroup v1 hugetlb metrics for usage, fail count, and maximum usage per hugepage size.

Important APIs and data: `hugetlbMetrics` produces `hugetlb_usage`, `hugetlb_failcnt`, and `hugetlb_max`, each labeled by `page`.

Control flow: metric functions return nil when `stats.Hugetlb` is absent, otherwise iterate the hugetlb stat slice and emit one value per page size.

State and persistence: no state; descriptor data is consumed by the v1 collector.

Dependencies and integration: depends on v1 metrics aliases, Docker metrics units, and Prometheus gauges.

Risks: page-size labels add cardinality proportional to configured hugepage sizes. Units differ between bytes and total counts and must remain consistent with descriptor names.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/hugetlb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/memory.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/memory.go

Purpose: declares the cgroup v1 memory metric set, covering memory.stat fields, hierarchical limits, usage/swap/kernel/kernel-tcp failcnt/limit/max/usage fields.

Important APIs and data: global `memoryMetrics` contains descriptors for cache, rss, mapped file, dirty/writeback, page counters/faults, active/inactive file and anon, unevictable, hierarchical limits, total variants, memory usage, swap, kernel, and kernel TCP metrics.

Control flow: each metric function checks for the relevant nested memory object before reading fields. Plain memory.stat fields check `stats.Memory`; usage/swap/kernel/kernel-tcp groups use generated getters such as `stats.GetMemory().GetUsage()` to avoid nil dereferences.

State and persistence: no state; metrics are stateless projections from cgroup v1 stats payloads into Prometheus samples.

Dependencies and integration: depends on cgroup v1 stats aliases, Docker metrics unit conventions, Prometheus gauges, and `v1.NewCollector`.

Risks: many memory.stat counters are exposed with `metrics.Bytes` even when kernel semantics are event/page counters, which is historical API behavior and hard to change. The metric list is large, so renames or unit changes are breaking for Prometheus consumers.

Test signals: no direct metric-value tests in subset; nil-safe collection is indirectly covered by empty stats in the concurrency regression test.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/metric.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/metric.go

Purpose: provides the small descriptor/value abstraction used by all cgroup v1 metric definition files.

Important APIs and types: `IDName`, `value`, `metric`, `(*metric).desc`, and `(*metric).collect`.

Control flow: `desc` creates a Prometheus descriptor in the provided Docker metrics namespace with common labels `container_id` and `namespace` plus metric-specific labels. `collect` calls the metric's `getValues`, then emits constant metrics either blocking or non-blocking depending on the caller's `block` flag.

State and persistence: no persistent state. Descriptor construction is repeated per collection call through the namespace helper.

Dependencies and integration: used by v1 CPU, memory, blkio, hugetlb, and pids metric definitions. Depends on Docker metrics namespace and Prometheus.

Risks: non-blocking mode can drop metrics when the channel is full. `MustNewConstMetric` will panic if descriptor/value/label cardinality is inconsistent, so metric definitions must keep labels aligned with emitted values.

Test signals: exercised indirectly by collector collection paths; no isolated tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/metric.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/metrics.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/metrics.go

Purpose: implements the cgroup v1 Prometheus collector that tracks stat-capable tasks and emits all configured v1 metrics.

Important APIs and types: `Trigger`, `NewCollector`, `taskID`, `entry`, `Collector`, and methods `Describe`, `Collect`, `collect`, `Add`, `Remove`, and `RemoveAll`.

Control flow: `NewCollector` returns an inert collector when namespace is nil; otherwise it appends pids, CPU, memory, hugetlb, and blkio metric definitions, allocates a stored metric channel, and registers with the namespace. `Collect` holds a read lock while spawning one goroutine per task to collect stats and flushing stored metrics, releases the lock, then waits for goroutines. `collect` calls task `Stats` with a namespace-aware timeout context, unmarshals into v1 metrics, chooses a child namespace with const labels if configured, and emits every metric. `Add` checks idempotently under a read lock, creates child const labels outside the write lock, then stores the entry. `Remove` and `RemoveAll` mutate the task map.

State and persistence: runtime-only task map keyed by `id-namespace`, metric definitions, and stored metrics channel. No persistent state.

Dependencies and integration: uses common `Statable`, cgroup v1 type aliases, typeurl, timeout setting from core metrics, namespace context, Docker metrics, Prometheus, and logging.

Risks: comments document historical deadlock risk with namespace locks and collector locks. Collection spawns goroutines while holding a read lock until stored metrics are flushed; slow task stats can still consume resources. Errors are logged and metrics for that task are skipped.

Test signals: `metrics_test.go` directly validates concurrent `Add` and namespace `Collect` do not deadlock.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/oom.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/oom.go

Purpose: monitors cgroup v1 OOM eventfds with epoll, exposes OOM counts as Prometheus metrics, and triggers task OOM events.

Important APIs and types: `newOOMCollector`, `oomCollector`, `oom`, `Add`, `Describe`, `Collect`, `Close`, `start`, `process`, and `flushEventfd`.

Control flow: `newOOMCollector` creates an epoll fd, optionally creates a `memory_oom` descriptor and registers with the metrics namespace, then starts an epoll loop goroutine. `Add` obtains a cgroup OOM event fd, stores an `oom` record keyed by fd, and registers fd with epoll. `start` waits forever in `EpollWait`, retrying through EINTR, and calls `process` for ready fds. `process` flushes the eventfd, removes and closes deleted cgroups, otherwise increments an atomic count and invokes triggers. `Collect` emits current counts as counters.

State and persistence: runtime-only epoll fd, fd-to-oom map, and per-cgroup atomic counters. No persistent state.

Dependencies and integration: integrates cgroup1 `OOMEventFD`, cgroup state, task monitor trigger callbacks, unix epoll/eventfd reads, Docker metrics, Prometheus, and logging.

Risks: `Describe` emits `nil` descriptor if namespace was nil and the collector is still used directly. FDs stay registered until an event indicates deletion; idle stopped tasks may retain registrations. Event loop exits permanently on epoll wait errors.

Test signals: not directly tested in subset; cgroup v1 monitor wires it in `cgroups.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/oom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/pids.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v1/pids.go

Purpose: declares cgroup v1 PID metrics for PID limit and current PID count.

Important APIs and data: `pidMetrics` contains two metrics named `pids`, differentiated by Docker metrics units `limit` and `current`.

Control flow: both metric functions return nil when `stats.Pids` is absent; otherwise they emit one value from `Limit` or `Current`.

State and persistence: no state; descriptors are appended to the v1 collector.

Dependencies and integration: depends on v1 stats aliases, Docker metrics units, and Prometheus gauges.

Risks: same metric name with different unit relies on Docker metrics namespace naming conventions to produce distinct final descriptors. Missing pids controller data emits no sample.

Test signals: indirectly traversed by collector tests with empty stats.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v1/pids.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/cgroups.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v2/cgroups.go

Purpose: implements the cgroup v2 runtime task monitor, wiring tasks into the v2 Prometheus collector.

Important APIs and types: `NewTaskMonitor`, `cgroupsMonitor`, `Monitor`, and `Stop`.

Control flow: `NewTaskMonitor` creates a v2 collector and returns a monitor with context and publisher fields. `Monitor` adds the runtime task to the collector. `Stop` removes it from collection.

State and persistence: runtime-only collector task map; no persistent state. The publisher field is stored for parity with v1 but not used in this file.

Dependencies and integration: integrates runtime `TaskMonitor`, event publisher type, Docker metrics namespace, and the v2 collector.

Risks: cgroup v2 OOM is collected from memory events stats rather than event-published through this monitor, so behavior differs from v1. The unused publisher/context fields may mislead readers expecting v2 task OOM event publication here.

Test signals: indirectly exercised by collector concurrency test on unified cgroup hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/cgroups.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/cpu.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v2/cpu.go

Purpose: declares cgroup v2 CPU metrics from `cpu.stat`.

Important APIs and data: `cpuMetrics` includes `cpu_usage_usec`, `cpu_user_usec`, `cpu_system_usec`, `cpu_nr_periods`, `cpu_nr_throttled`, and `cpu_throttled_usec`.

Control flow: each metric returns nil when `stats.CPU` is absent, otherwise emits one gauge value from the corresponding cgroup v2 CPU field.

State and persistence: no state; metric definitions are global data consumed by `v2.NewCollector`.

Dependencies and integration: depends on v2 stats aliases, Docker metrics units, Prometheus gauges, and v2 descriptor abstraction.

Risks: units are microseconds for usage/time fields and totals for period counters; changing names/units would break monitoring consumers. Values are cumulative gauges.

Test signals: no direct value tests; empty stats path is indirectly covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/cpu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/io.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v2/io.go

Purpose: declares cgroup v2 IO metrics from per-device IO usage entries.

Important APIs and data: `ioMetrics` includes `io_rbytes`, `io_wbytes`, `io_rios`, and `io_wios`, all labeled by `major` and `minor`.

Control flow: metric functions return nil when `stats.Io` is absent, otherwise iterate `stats.Io.Usage` and emit one value per device.

State and persistence: no state; descriptors are consumed by the v2 collector.

Dependencies and integration: depends on v2 stats aliases, Docker metrics units, Prometheus, and strconv label conversion.

Risks: device-level labels can create cardinality proportional to block devices. Only read/write bytes and IO counts are exported here, not all possible cgroup v2 IO stats.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/io.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/memory.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v2/memory.go

Purpose: declares cgroup v2 memory and memory-events metrics for usage, swap, file/page activity, reclaim, slab, transparent huge page, working set, and OOM counts.

Important APIs and data: `memoryMetrics` includes `memory_usage`, `memory_usage_limit`, `memory_swap_usage`, `memory_swap_limit`, file dirty/writeback/mapped metrics, page activation/refill/scan/steal/fault metrics, active/inactive anon/file, anon/file/kernel/slab/socket/shmem fields, THP counters, workingset counters, and `memory_oom` from `MemoryEvents.Oom`.

Control flow: each metric checks `stats.Memory` or `stats.MemoryEvents` before reading fields and emits one unlabeled gauge value.

State and persistence: no state; stateless projection from cgroup v2 stats payloads into Prometheus samples.

Dependencies and integration: depends on v2 stats aliases, Docker metrics units, Prometheus gauges, and v2 collector.

Risks: like v1, many kernel counters are exposed under bytes units due to existing metric conventions. `memory_oom` is a gauge of the cgroup v2 events counter, not the eventfd-based counter used by v1.

Test signals: not directly value-tested; nil-safe behavior is indirectly covered by empty stats collection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/metric.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v2/metric.go

Purpose: provides the descriptor/value abstraction used by all cgroup v2 metric definition files.

Important APIs and types: `IDName`, `value`, `metric`, `(*metric).desc`, and `(*metric).collect`.

Control flow: `desc` creates descriptors with common labels `container_id` and `namespace` plus metric-specific labels. `collect` calls `getValues` and emits constant metrics either blocking or non-blocking.

State and persistence: no persistent state.

Dependencies and integration: used by v2 CPU, memory, IO, and pids metric files. Depends on Docker metrics namespace and Prometheus.

Risks: label cardinality mismatches panic through `MustNewConstMetric`. Non-blocking mode can drop samples when used.

Test signals: indirectly exercised by v2 collector paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/metric.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/metrics.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v2/metrics.go

Purpose: implements the cgroup v2 Prometheus collector that tracks stat-capable tasks and emits configured v2 metrics.

Important APIs and types: `NewCollector`, `taskID`, `entry`, `Collector`, and methods `Describe`, `Collect`, `collect`, `Add`, `Remove`, and `RemoveAll`.

Control flow: `NewCollector` builds an inert collector for nil namespace or registers a collector with pids, CPU, memory, and IO metrics. `Collect` read-locks the task map, spawns one goroutine per task to collect stats, flushes stored metrics, unlocks, then waits. `collect` calls task stats with a namespaced timeout context, unmarshals into v2 metrics, chooses optional const-label namespace, and emits each metric. `Add` is idempotent and creates child namespaces with labels outside the write lock. Remove operations mutate the task map.

State and persistence: runtime-only collector fields: namespace, stored metrics channel, task map, metric definitions, and mutex.

Dependencies and integration: depends on common `Statable`, v2 stats aliases, typeurl, timeout setting, namespace context, Docker metrics, Prometheus, and logging.

Risks: same lock-ordering concerns as v1 are documented. Slow or stuck task stats are bounded by `ShimStatsRequestTimeout`, but many tasks can still spawn many goroutines during collection.

Test signals: `metrics_test.go` covers concurrent `Add` and namespace collection on cgroup v2 hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/pids.go -->
# sources/cloud-native/containerd/core/metrics/cgroups/v2/pids.go

Purpose: declares cgroup v2 PID metrics for PID limit and current PID count.

Important APIs and data: `pidMetrics` contains two `pids` descriptors differentiated by units `limit` and `current`, with cgroup v2-specific help text.

Control flow: both functions return nil when `stats.Pids` is absent, otherwise emit one gauge from `Limit` or `Current`.

State and persistence: no state; descriptors are consumed by the v2 collector.

Dependencies and integration: depends on v2 stats aliases, Docker metrics units, and Prometheus.

Risks: same final-name/unit convention as v1 applies. Missing pids stats emit no sample.

Test signals: indirectly exercised by empty stats collector tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/cgroups/v2/pids.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/metrics.go -->
# sources/cloud-native/containerd/core/metrics/metrics.go

Purpose: initializes core containerd metrics metadata and default timeout settings.

Important APIs and data: constant `ShimStatsRequestTimeout` and package `init`.

Control flow: `init` creates a `containerd` metrics namespace, registers a labeled `build_info` counter with `version` and `revision`, increments it once, registers the namespace globally, and sets the shim stats request timeout to two seconds.

State and persistence: global metrics registry state and global timeout registry state; no disk persistence.

Dependencies and integration: depends on containerd version data, Docker metrics, and timeout package. The cgroup v1/v2 collectors use `ShimStatsRequestTimeout` when calling task stats.

Risks: initialization has global side effects at import time. Consumers relying on stats calls need to account for the two-second timeout.

Test signals: indirectly used by collector tests through timeout context creation; no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/types/v1/types.go -->
# sources/cloud-native/containerd/core/metrics/types/v1/types.go

Purpose: re-exports cgroup v1 stats protobuf/generated types under the containerd metrics package path.

Important APIs and types: aliases for `Metrics`, `BlkIOEntry`, `MemoryStat`, `CPUStat`, `CPUUsage`, `BlkIOStat`, `PidsStat`, `RdmaStat`, `RdmaEntry`, and `HugetlbStat`.

Control flow: no runtime logic; aliases allow typeurl unmarshaling and imports to refer to containerd's metrics types path while using `containerd/cgroups/v3/cgroup1/stats`.

State and persistence: none.

Dependencies and integration: used by v1 collectors and tests. Depends on `github.com/containerd/cgroups/v3/cgroup1/stats`.

Risks: type aliases couple containerd's public metrics type surface to upstream cgroups stats type names and fields.

Test signals: `metrics_test.go` creates empty `v1types.Metrics` payloads for collector regression testing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/types/v1/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/types/v2/types.go -->
# sources/cloud-native/containerd/core/metrics/types/v2/types.go

Purpose: re-exports cgroup v2 stats types under the containerd metrics package path.

Important APIs and types: aliases for `Metrics`, `MemoryStat`, `CPUStat`, `PidsStat`, and `IOStat`.

Control flow: no runtime logic; aliases allow collectors and typeurl payloads to use containerd package paths while relying on `containerd/cgroups/v3/cgroup2/stats`.

State and persistence: none.

Dependencies and integration: used by v2 collectors and tests.

Risks: public compatibility follows upstream cgroups v2 stats type shape.

Test signals: `metrics_test.go` marshals empty `v2types.Metrics` for collector regression coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metrics/types/v2/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/fuse_linux.go -->
# sources/cloud-native/containerd/core/mount/fuse_linux.go

Purpose: Linux-specific FUSE detection and FUSE unmount helper behavior.

Important APIs and data: constant `fuseSuperMagic`, `isFUSE`, and `unmountFUSE`.

Control flow: `isFUSE` calls `unix.Statfs` and compares filesystem type to the FUSE superblock magic, returning false on statfs errors. `unmountFUSE` tries `fusermount3 -u` and then `fusermount -u`, returning nil on first success or the last error.

State and persistence: no persistent state; executes external helper binaries.

Dependencies and integration: used by generic mount unmount code elsewhere in the mount package. Depends on Linux `statfs`, `os/exec`, and helper binaries.

Risks: absence of helper binaries or helper failure returns an error even if kernel unmount might otherwise work. `isFUSE` treats stat errors as non-FUSE, so callers must handle later unmount errors.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/fuse_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/fuse_unsupported.go -->
# sources/cloud-native/containerd/core/mount/fuse_unsupported.go

Purpose: non-Linux, non-Windows fallback for FUSE helpers.

Important APIs: `isFUSE` always returns false, and `unmountFUSE` returns a not-supported error string.

Control flow: no OS probing; this file is selected by build tags `!linux && !windows`.

State and persistence: none.

Dependencies and integration: keeps the mount package buildable on unsupported Unix-like platforms.

Risks: callers cannot perform FUSE-specific unmount behavior on these platforms through this helper.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/fuse_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/lookup_linux_test.go -->
# sources/cloud-native/containerd/core/mount/lookup_linux_test.go

Purpose: integration tests for `Lookup` on Linux filesystems and bind/overlay mounts.

Important APIs and helpers: `checkLookup`, `testLookup`, `TestLookupWithExt4`, `TestLookupWithXFS`, and `TestLookupWithOverlay`.

Control flow: ext4/xfs tests require root, create a loopback device, format it, mount it, bind-mount it elsewhere, and verify `Lookup` returns the expected filesystem type and mountpoint for mount roots and subdirectories. Overlay test creates lower/upper/work/merged dirs, mounts overlay, creates a directory and file, and verifies lookup returns the overlay mountpoint.

State and persistence: creates temporary filesystems and mountpoints and cleans them with testutil unmount and loopback close helpers.

Dependencies and integration: depends on root privileges, external `mkfs` and `mount`, continuity testutil/loopback helpers, and the mount package `Lookup`.

Risks: environment-sensitive; missing mkfs, unsupported filesystem, mount restrictions, or lack of root skips/fails tests. Overlay test uses real kernel overlay behavior.

Test signals: strong integration signal for mountinfo parent matching and canonical path handling on real mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/lookup_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/lookup_unix.go -->
# sources/cloud-native/containerd/core/mount/lookup_unix.go

Purpose: implements mountinfo lookup for non-Windows platforms.

Important APIs: `Lookup(dir string) (Info, error)`.

Control flow: canonicalizes the requested path, calls `mountinfo.GetMounts(mountinfo.ParentsFilter(resolvedDir))`, errors if no mounts match, and returns an `Info` populated from the last matching parent mount, including ID, parent ID, major/minor, root, mountpoint, options, optional fields, filesystem type, source, and vfs options.

State and persistence: reads kernel mountinfo state; no persistence.

Dependencies and integration: depends on `CanonicalizePath`, mount package `Info`, and `github.com/moby/sys/mountinfo`.

Risks: correctness depends on parent filter ordering from `mountinfo.GetMounts`; returning the last match is intended to select the most specific mount. Canonicalization errors surface before mountinfo lookup.

Test signals: `lookup_linux_test.go` covers ext4/xfs loop mounts, bind mounts, overlay mounts, directories, and files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/lookup_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/lookup_unsupported.go -->
# sources/cloud-native/containerd/core/mount/lookup_unsupported.go

Purpose: fallback implementation of `Lookup` for unsupported platforms.

Important APIs: `Lookup(dir string) (Info, error)` returns an error indicating lookup is not implemented for the current platform.

Control flow: no probing or state access.

State and persistence: none.

Dependencies and integration: provides build compatibility for platforms without mountinfo support.

Risks: callers must handle unsupported lookup on these platforms.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/lookup_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/loopback_handler_linux.go -->
# sources/cloud-native/containerd/core/mount/loopback_handler_linux.go

Purpose: implements a mount manager handler for `loop` mounts by attaching a backing file to a loop device and tracking it through a symlink.

Important APIs and types: `LoopbackHandler`, `loopbackHandler`, `Mount`, and `Unmount`.

Control flow: `Mount` rejects non-`loop` mount types with `ErrNotImplemented`, sets up a loop device with autoclear enabled, creates a symlink from the loop device path to the manager mountpoint, then disables autoclear so the loop device remains active while tracked. It returns an `ActiveMount` with mount metadata and mountpoint. `Unmount` reads the symlink, opens the loop device, enables autoclear, removes the symlink, and if symlink removal fails attempts to disable autoclear again to prevent untracked reuse.

State and persistence: loop device kernel state plus a filesystem symlink at the mount manager path. `MountedAt` records activation time.

Dependencies and integration: depends on `SetupLoop`, `setLoopAutoclear`, errdefs, logging, and the mount manager `Handler` interface.

Risks: mount path symlink creation failure after loop setup relies on defer close/autoclear for cleanup. If symlink removal fails and resetting autoclear also fails, the loop device may be cleaned while still tracked. TODOs note readonly and direct IO options are not handled.

Test signals: no direct handler tests in subset; loop device primitives are covered by `losetup_linux_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/loopback_handler_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/losetup_linux.go -->
# sources/cloud-native/containerd/core/mount/losetup_linux.go

Purpose: provides Linux loop device setup, attach, detach, autoclear, and direct-IO configuration helpers.

Important APIs and types: constants `loopControlPath`, `loopDevFormat`, `ebusyString`; `LoopParams`; `getFreeLoopDev`; `setupLoopDev`; `SetupLoop`; `setLoopAutoclear`; `removeLoop`; `AttachLoopDevice`; and `DetachLoopDevice`.

Control flow: `getFreeLoopDev` opens `/dev/loop-control` and uses `LOOP_CTL_GET_FREE`. `setupLoopDev` opens backing file and loop device read-only or read-write, uses `LOOP_CONFIGURE` on kernels >= 5.8 to atomically configure fd, filename, readonly, autoclear, and direct IO flags, otherwise falls back to `LOOP_SET_FD`, `LOOP_SET_STATUS64`, and optional `LOOP_SET_DIRECT_IO`, cleaning up on errors. `SetupLoop` retries up to 99 times when free-loop races surface as EBUSY, with randomized backoff. `setLoopAutoclear` toggles `LO_FLAGS_AUTOCLEAR`. `AttachLoopDevice` attaches and returns the loop path after closing the handle. `DetachLoopDevice` clears each supplied loop fd.

State and persistence: manipulates kernel loop device state and backing file association. Autoclear determines whether kernel cleanup happens on last close.

Dependencies and integration: depends on Linux loop ioctls from `x/sys/unix`, kernel version helper, randutil, and filesystem device nodes. Used by loopback mount handler and tests.

Risks: string matching `device or resource busy` is used for retry classification. Kernel version probing controls use of modern atomic loop configuration. Direct IO and readonly flags depend on kernel support. Attach without autoclear leaves cleanup responsibility to caller.

Test signals: `losetup_linux_test.go` covers missing backing file, readonly write failure, read-write write success, attach/detach, autoclear true cleanup, and autoclear false manual cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/losetup_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/losetup_linux_test.go -->
# sources/cloud-native/containerd/core/mount/losetup_linux_test.go

Purpose: integration tests for Linux loop device setup and cleanup behavior.

Important APIs and helpers: `createTempFile`, `TestNonExistingLoop`, `TestRoLoop`, `TestRwLoop`, `TestAttachDetachLoopDevice`, `TestAutoclearTrueLoop`, and `TestAutoclearFalseLoop`.

Control flow: each test requires root. Temporary backing files are truncated to 512 bytes. Tests verify missing file errors, readonly loop write rejection, read-write loop writes, attach/detach helper success, autoclear cleanup after closing the loop fd, and manual removal when autoclear is false.

State and persistence: uses real `/dev/loop*` devices and kernel loop state. Autoclear test compares backing inode through `IoctlLoopGetStatus64` until the device is cleared or retries expire.

Dependencies and integration: depends on root privileges, testutil, unix ioctls, filesystem stat data, and `losetup_linux.go` helpers.

Risks: environment-sensitive due to loop device availability and permissions. Autoclear polling has timing assumptions and can fail on slow cleanup. Tests manipulate real loop devices, so cleanup correctness is important.

Test signals: strong integration signal for loop setup flags and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/losetup_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager.go -->
# sources/cloud-native/containerd/core/mount/manager.go

Purpose: defines mount manager interfaces and shared data structures for activating, tracking, transforming, and deactivating mount sets.

Important APIs and types: `Manager`, `Handler`, `Transformer`, `ActivateOptions`, `ActivateOpt`, `WithTemporary`, `WithLabels`, `WithAllowMountType`, `ActiveMount`, and `ActivationInfo`.

Control flow: this file is interface and option definitions only. Option helpers mutate `ActivateOptions`. Implementations elsewhere use `Manager.Activate` to turn a mount array into manager-handled active mounts plus remaining system mounts, and use `Deactivate`, `Info`, `Update`, and `List` for lifecycle/state.

State and persistence: defines the in-memory shape of activation state. `ActivationInfo` includes unique name, active manager-handled mounts, remaining system mounts, and labels. `ActiveMount` records mount data, mountpoint, mounted time, and type-specific metadata.

Dependencies and integration: core contract for custom mount plugins such as loopback handlers and any bbolt-backed manager implementation. Uses context and time only.

Risks: interface comments establish important semantics: manager-handled mounts occur outside the container namespace, and returned system mounts are expected to be mounted by the runtime/container side. `AllowMountTypes` supports suffix matching by convention, which implementations must enforce consistently.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/buckets.go -->
# sources/cloud-native/containerd/core/mount/manager/buckets.go

Purpose: documents the bbolt schema for the mount manager package and defines shared bucket/key constants used by manager persistence code.

Important APIs and data: package-level bucket keys for IDs, mounts, leases, active/system mounts, type/source/target/options, mounted time, mountpoint, labels, and GC back-reference labels.

Control flow: no functions. The schema comment describes `v1/<namespace>/mounts/<mount name>` records, active/system ordered subbuckets, leases, and an unused unmount queue.

State and persistence: this file is the authoritative local schema map for mount manager bbolt persistence. It records fields such as created/updated time, lease, active mount order, mount type/source/target/options, active mountpoint, and labels.

Dependencies and integration: used by other files in `core/mount/manager` to read/write metadata and by GC-related code through back-reference label constants.

Risks: schema comments and byte constants must stay synchronized with actual manager implementation. Unused or legacy fields in the schema can confuse migration and cleanup work.

Test signals: no direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/buckets.go -->
