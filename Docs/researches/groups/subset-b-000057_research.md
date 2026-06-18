# subset-b-000057 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/converter/uncompress/uncompress.go -->
# sources/cloud-native/containerd/core/images/converter/uncompress/uncompress.go

## Purpose

This file implements the image-converter function that rewrites compressed layer blobs into uncompressed tar layer blobs. It is used when a conversion pipeline wants OCI or Docker layer descriptors to point at plain tar content while retaining relevant content labels.

## Important APIs, Types, and Functions

`LayerConvertFunc` satisfies `converter.ConvertFunc`. It accepts a content store and descriptor, returns nil for non-layer or already-uncompressed layers, otherwise writes decompressed content back to the store and returns a descriptor with updated digest, size, and media type. `IsUncompressedType` classifies Docker and OCI tar layer media types that should not be decompressed again. `convertMediaType` maps gzip and zstd layer media types to their uncompressed equivalents, including deprecated non-distributable OCI layer forms.

## Control Flow

The converter gates on `images.IsLayerType` and `IsUncompressedType`, reads the source content metadata and blob, wraps the blob in a section reader of descriptor size, and passes it through `compression.DecompressStream`. It opens a deterministic writer reference derived from the source digest, truncates any prior interrupted writer state, copies the uncompressed stream, closes the decompressor, commits the writer, and then builds a descriptor from the original with new digest and size. `errdefs.IsAlreadyExists` is tolerated during commit so conversion can reuse already committed uncompressed blobs.

## State and Persistence Behavior

The only durable mutation is a new content-store blob under `convert-uncompress-from-<digest>`. Existing labels from the compressed blob are reused, but the uncompressed diff label `containerd.io/uncompressed` is removed because the new blob digest is already the uncompressed layer digest. The code mutates the `info.Labels` map returned by the content store in place, so callers should not assume that map remains unchanged.

## Dependencies and Integration Points

The function sits in `core/images/converter/uncompress` and integrates with the generic `converter` package, `core/content` stores, media-type helpers from `core/images`, archive compression detection, label constants, and OCI descriptors. It is relevant to image conversion, export, unpack, and distribution flows that need uncompressed layers.

## Risks and Edge Cases

Compression detection errors abort conversion. The copy path trusts `desc.Size` for the section reader, so mismatched descriptor sizes can truncate or fail reads. The commit passes size `0` and empty expected digest, relying on writer-computed values rather than explicit validation. Existing interrupted writer state is intentionally truncated, which is correct for this ref but assumes no concurrent conversion writer is using the same deterministic ref. Label map mutation can panic if `info.Labels` is nil before `delete`, depending on store behavior.

## Test Signals

Useful tests should cover nil result for non-layer and uncompressed media types, gzip and zstd conversion media-type rewrites, label preservation with `LabelUncompressed` removal, interrupted-writer truncation, already-exists commits, decompression failures, and descriptor digest/size correctness after conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/converter/uncompress/uncompress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/diffid.go -->
# sources/cloud-native/containerd/core/images/diffid.go

## Purpose

This file computes a layer DiffID, which is the digest of the uncompressed layer stream. DiffIDs are used to verify unpacked rootfs layers and to connect compressed content blobs to unpacked layer identity.

## Important APIs, Types, and Functions

`GetDiffID(ctx, cs, desc)` is the sole exported function. It returns the descriptor digest immediately for already-uncompressed Docker or OCI tar layers, consults the content info label `containerd.io/uncompressed` as a cache for compressed layers, and otherwise streams/decompresses the blob to compute the canonical digest. It uses `content.Store.Info`, `ReaderAt`, `content.NewReader`, and `compression.DecompressStream`.

## Control Flow

The function first checks media type. For compressed or otherwise non-fast-path descriptors, it loads content info, parses the cached uncompressed label if present, opens a reader, decompresses it, copies the uncompressed bytes into a canonical digest hash, and closes readers. It then stores the computed DiffID back into the content metadata labels via `cs.Update(ctx, info, "labels")`; update failure is only logged as a warning and does not fail the digest result.

## State and Persistence Behavior

The persistent state is the optional cache label written to the content store. Existing labels are preserved, and a nil labels map is initialized before writing. The source blob itself is not changed. The function closes both the decompressor and reader, with an explicit reader close checked before returning the digest.

## Dependencies and Integration Points

`GetDiffID` is a bridge between image descriptor media types, the content store, archive compression, OpenContainers digests, and containerd label conventions. It feeds rootfs verification, unpack workflows, and any code that needs the uncompressed identity of a packed layer.

## Risks and Edge Cases

Malformed cached label values fail through `digest.Parse`. Unknown or mislabeled compressed media types rely on `compression.DecompressStream` to detect compression. A content-update failure leaves the computation correct but uncached. The function returns the descriptor digest for uncompressed foreign/non-distributable layers without validating that the content is actually tar data.

## Test Signals

Good coverage includes uncompressed layer fast paths, cached-label parsing, cache miss computation for gzip/zstd layers, invalid cached labels, decompression errors, update failures logged but not returned, and ensuring computed labels are visible to subsequent calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/diffid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/handlers.go -->
# sources/cloud-native/containerd/core/images/handlers.go

## Purpose

This file defines the descriptor traversal and handler composition framework used throughout image fetch, walk, filtering, labeling, and referrer traversal. It provides both synchronous and parallel recursion over OCI descriptors.

## Important APIs, Types, and Functions

`Handler` and `HandlerFunc` define descriptor processors. `Handlers` chains handlers and honors `ErrStopHandler`. `Walk` recursively visits descriptors synchronously and honors `ErrSkipDesc`. `WalkNotEmpty` wraps `Walk` and returns `ErrEmptyWalk` when traversal yields no children. `Dispatch` recursively visits siblings in parallel with optional `semaphore.Weighted` concurrency limiting. `ChildrenHandler` adapts `Children`. `SetReferrers`, `SetChildrenLabels`, and `SetChildrenMappedLabels` enrich child lists or content labels. `FilterPlatforms` and `LimitManifests` filter and order descriptor children by platform.

## Control Flow

`Handlers` calls each handler for a descriptor and appends all children unless a handler returns `ErrStopHandler`. `Walk` processes each descriptor, recurses into returned children, and treats `ErrSkipDesc` as pruning. `Dispatch` starts one errgroup goroutine per sibling, acquires/releases the limiter around each handler invocation, cancels the group context on errors, and recurses on children. The label wrappers execute an underlying child-returning handler first, then update parent content metadata with generated GC reference labels before returning children.

## State and Persistence Behavior

Most handlers are stateless. `SetChildrenMappedLabels` mutates content metadata by writing label fields onto the parent descriptor's content info. Labels encode child digests using keys from `ChildGCLabels` or caller-provided mappings, add numeric suffixes for repeated key classes, and use digest hex suffixes for referrer SHA256 keys. `SetReferrers` mutates returned referrer descriptors in memory by adding `AnnotationManifestSubject`.

## Dependencies and Integration Points

The traversal APIs integrate with `core/content` providers/managers, OCI descriptors, platform matchers/comparers, `errgroup`, semaphores, and containerd media-type helpers. Fetchers, unpackers, GC label creation, manifest platform resolution, and referrer-aware operations compose these handlers.

## Risks and Edge Cases

`Dispatch` starts goroutines inside a loop with a local `desc := desc` inside the goroutine, which is safe on modern Go but still worth preserving if edited. Limiter acquisition happens before goroutine start and release after handler return; handler panics would leak semaphore capacity. `SetChildrenMappedLabels` assumes label keys are non-empty before indexing `key[len(key)-1]`. `LimitManifests` only errors on no match when a positive limit is requested. Platform-less descriptors are retained by filtering and sorted after platform-matched descriptors.

## Test Signals

Tests should exercise handler-chain stopping, skip-desc pruning, WalkNotEmpty empty detection, Dispatch error cancellation and limiter behavior, referrer annotation injection, GC label key generation including repeated keys and referrers, platform filtering, manifest limiting, and not-found behavior when no platform match exists.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/image.go -->
# sources/cloud-native/containerd/core/images/image.go

## Purpose

This file defines the image metadata model and core image inspection helpers for resolving manifests, configs, platforms, rootfs diff IDs, sizes, child descriptors, and local content completeness. It is a central descriptor/content utility layer for containerd images.

## Important APIs, Types, and Functions

`Image` holds name, labels, target descriptor, and timestamps. `Store` defines image CRUD with field-mask updates and delete options. `DeleteOptions`, `DeleteOpt`, `SynchronousDelete`, and `DeleteTarget` model delete behavior. Image methods `Config`, `RootFS`, and `Size` delegate to package functions. Package functions include `Manifest`, `Config`, `Platforms`, `Check`, `Children`, `RootFS`, `ConfigPlatform`, and internal `validateMediaType`.

## Control Flow

`Image.Size` walks target content using a handler chain that sums non-negative descriptor sizes and descends through platform-limited children. `Manifest` walks from an image descriptor, reading and validating manifests or indexes. For manifest descriptors it unmarshals an OCI manifest, checks descriptor or config platform when needed, and records the first match. For index descriptors it reads an index, filters and sorts manifest descriptors by platform, limits to one candidate, and continues walking. `Children` reads known manifest or index blobs, validates media type against document shape, and returns immediate config/layer or manifest children. `Check` resolves the target manifest, then verifies config and layer blobs by opening readers.

## State and Persistence Behavior

The file mostly reads from a content provider and does not mutate storage. It models persistent image records through `Image` and `Store` interfaces but does not implement a store here. `Check` opens and closes content readers to test availability. JSON blobs are parsed from the content store, and media-type validation rejects Docker schema 1 and mismatches between descriptor media type and document contents.

## Dependencies and Integration Points

It depends on `core/content`, `platforms`, `errdefs`, OCI image-spec descriptors/manifests/indexes/images, OpenContainers digests, and local handler/media-type helpers. Metadata stores implement `Store`; pull, fetch, unpack, export, and usage calculation use the descriptor readers and traversal helpers.

## Risks and Edge Cases

Several helpers assume OCI manifest shape even for Docker schema 2. `Manifest` returns the first sorted match and does not detect multiple equally valid platform matches beyond stable ordering. If an index has no match, it returns NotFound only after walking yields no manifest. `Check` ignores possible children under referenced components and only verifies config/layers. `validateMediaType` uses structural JSON heuristics, so unusual but valid future documents could be rejected.

## Test Signals

`image_test.go` directly covers `validateMediaType` for manifest/index pairs, declared media-type mismatches, and schema 1 rejection. Additional high-value tests should cover platform-less manifest resolution via config platform, platform sorting, `Check` missing vs present blobs, `Children` unknown media-type logging, negative descriptor sizes in `Size`, and config/rootfs parsing failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/image_test.go -->
# sources/cloud-native/containerd/core/images/image_test.go

## Purpose

This test file validates media-type consistency checks for image manifests and indexes. It protects callers from accepting content whose descriptor media type disagrees with the JSON document shape or embedded `mediaType` value.

## Important APIs, Types, and Functions

`TestValidateMediaType` is the only test. It builds OCI manifest and index documents, then calls unexported `validateMediaType` with Docker schema 2 manifest, OCI manifest, Docker manifest list, and OCI index media types. It also constructs documents containing only an embedded `mediaType` field and a schema1-style `fsLayers` field.

## Control Flow

The test first loops over descriptor media types and checks that manifest-shaped JSON is accepted only for manifest types and index-shaped JSON only for index types. It then loops over embedded media-type compatibility tables, asserting that manifest descriptors accept manifest embedded types and reject index embedded types, and vice versa. The final subtest checks schema1 detection through `fsLayers`.

## State and Persistence Behavior

The test is fully in-memory. It marshals JSON with `encoding/json` and does not touch content stores, metadata DBs, or global state.

## Dependencies and Integration Points

It depends on `ocispec.Manifest`, `ocispec.Index`, Docker/OCI media-type constants from the package under test, and `testify` assertions. It gives regression coverage for `Children` and `Manifest`, because both call `validateMediaType` before unmarshalling typed image documents.

## Risks and Edge Cases

The test focuses on structural mismatch and embedded media-type mismatch but does not cover invalid JSON, empty documents, documents containing both config/layers and manifests, or future media types. It also does not exercise error wrapping text from callers.

## Test Signals

Passing this test signals that descriptor/document type mismatches are rejected for the core Docker and OCI manifest/index media types and Docker schema1 content remains unsupported.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/image_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/imagetest/content.go -->
# sources/cloud-native/containerd/core/images/imagetest/content.go

## Purpose

This file provides test helpers for constructing image content graphs in a temporary content store. It lets tests build manifests, indexes, blobs, platforms, missing-layer scenarios, and expected size models without manually writing OCI JSON and content blobs.

## Important APIs, Types, and Functions

`Content` wraps an OCI descriptor, labels, size accounting, and child `Content` values. `ContentStore` embeds `content.Store` and carries test context. `NewContentStore` creates a local labeled content store with an in-memory label store. Methods `Index`, `Manifest`, `Blob`, `RandomBlob`, `JSONObject`, and `Walk` create or mutate graph content. Content creators include `SimpleManifest`, `SimpleIndex`, and `StripLayers`; modifiers include `AddPlatform` and `LimitChildren`. `memoryLabelStore` implements the local content label store.

## Control Flow

Blob creation computes the SHA256 digest, writes the blob with `content.WriteBlob`, and returns a descriptor/size wrapper. JSON helpers marshal typed objects and store them as blobs. Manifest and index helpers assemble descriptors from child `Content`, write the OCI JSON object, and attach child lists for recursive test expectations. `Walk` applies a mutation callback to a content node, recursively processes children, and replaces child values with mutated copies. `StripLayers` uses `Walk` to delete layer blobs from the store and set their content size to zero.

## State and Persistence Behavior

The helper writes real blobs to a temporary local content store. `memoryLabelStore` persists labels only in a mutex-protected in-memory map for the lifetime of the test. The `Content` graph mirrors store state when helpers are used; direct external mutations can make size and child metadata stale, which the file comments warn about.

## Dependencies and Integration Points

It integrates with `core/content`, `core/images`, the local content plugin, OCI descriptors, OpenContainers digests, and Go testing. It is used by image usage tests and can support traversal, size, filtering, and missing-content tests.

## Risks and Edge Cases

`RandomBlob` uses deterministic pseudo-random bytes seeded by size, so blobs with the same size share content/digest. Blob refs are just digest strings, which could collide with concurrent duplicate writes but are suitable for isolated tests. `SimpleManifest` layers are random bytes, not valid compressed tar streams, so unpack/diffid tests must not use them as real layers. `memoryLabelStore.Get` returns the map directly, allowing callers to mutate stored labels without `Set` or `Update`.

## Test Signals

Tests using these helpers should compare calculated usage to `SizeOfManifest` and `SizeOfContent`, verify missing layers after `StripLayers`, platform-limited graph traversal, label persistence in the local labeled store, and consistency of recursively mutated `Content` graphs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/imagetest/content.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/imagetest/size.go -->
# sources/cloud-native/containerd/core/images/imagetest/size.go

## Purpose

This file defines size accounting helpers for image test content graphs. It separates descriptor-reported manifest size, actually stored content size, snapshot usage, and uncompressed byte estimates.

## Important APIs, Types, and Functions

`Size` carries `Manifest`, `Content`, `Unpacked`, and `Uncompressed` counters. `ContentSizeCalculator` is a function type used by table tests. `SizeOfManifest` recursively sums `Content.Size.Manifest`, and `SizeOfContent` recursively sums `Content.Size.Content`.

## Control Flow

Both calculators use straightforward depth-first recursion over `Content.Children`. They add the current node's selected size counter and then add each child's recursive value.

## State and Persistence Behavior

There is no persistence. The functions read the in-memory `Content` graph and intentionally do not deduplicate repeated descriptors or consult the content store.

## Dependencies and Integration Points

The helpers live in the `imagetest` package and are used by usage calculator tests to compare manifest-based size against actual content-store-based size, especially when layers are removed.

## Risks and Edge Cases

Duplicate blobs are counted multiple times because the graph structure is accumulated, not unique digests. Deep graphs could recurse deeply, though image graphs are normally shallow. `Unpacked` and `Uncompressed` are modeled in `Size` but not used by these two functions.

## Test Signals

Signals are simple: usage tests should produce expected totals for simple manifests, indexes, stripped-layer graphs, and platform-limited indexes using these calculators.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/imagetest/size.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/importexport.go -->
# sources/cloud-native/containerd/core/images/importexport.go

## Purpose

This file declares the abstraction boundaries for image import and export implementations. It does not implement tar parsing or writing; it standardizes the interfaces consumed by higher-level image transfer code.

## Important APIs, Types, and Functions

`Importer` has `Import(ctx, store, reader) (ocispec.Descriptor, error)`, taking a content store and tar stream reader and returning the imported root descriptor. `Exporter` has `Export(ctx, store, desc, writer) error`, taking a content provider, root descriptor, and tar stream writer.

## Control Flow

There is no executable control flow beyond interface method signatures. Implementations define the actual import/export sequence.

## State and Persistence Behavior

Import implementations are expected to write content into a `content.Store`; export implementations read from a `content.Provider` and write to an `io.Writer`. This file owns no state.

## Dependencies and Integration Points

The interfaces depend on `context`, `io`, `core/content`, and OCI descriptors. They connect archive import/export implementations to containerd's content-addressed storage without binding callers to a concrete implementation.

## Risks and Edge Cases

The interfaces do not express image record creation, leases, namespace behavior, platform filtering, or progress reporting. Implementations must define tar format support, duplicate blob handling, descriptor validation, and error semantics.

## Test Signals

Interface-level signals are compile-time conformance for import/export implementations and integration tests that import an archive into a content store and export it back with descriptor and content integrity preserved.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/importexport.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/mediatypes.go -->
# sources/cloud-native/containerd/core/images/mediatypes.go

## Purpose

This file centralizes containerd image media-type constants and classification helpers. It covers Docker schema 2, OCI, checkpoint, encrypted, EROFS, and in-toto media types, plus helpers that map descriptors to GC label classes.

## Important APIs, Types, and Functions

Constants define Docker layer/config/manifest/list, checkpoint/restore, schema1 manifest, encrypted layers, EROFS layers, and in-toto media types. `DiffCompression` reports layer compression as `gzip`, `zstd`, empty, or `unknown`, or returns `ErrNotImplemented` for non-layer types. `parseMediaTypes` splits a media type into base and sorted suffixes. Classification helpers are `IsNonDistributable`, `IsLayerType`, `IsDockerType`, `IsManifestType`, `IsIndexType`, `IsConfigType`, `IsKnownConfig`, and `IsAttestationType`. `ChildGCLabels` and `ChildGCLabelsFilterLayers` choose GC reference label keys for child descriptors.

## Control Flow

`DiffCompression` strips suffixes, switches on base media type, and rejects wrapped Docker media types by returning empty compression. OCI layer types inspect the final sorted suffix for gzip or zstd. `IsLayerType` accepts OCI layer prefixes, known Docker layer bases after suffix parsing, and EROFS. `ChildGCLabels` prioritizes referrer subject annotations, then config, manifest, layer, and generic content label keys.

## State and Persistence Behavior

There is no persistence here. The functions produce classification values and label key strings used by traversal and metadata code to persist GC references elsewhere.

## Dependencies and Integration Points

The file integrates with OCI image-spec media types, `errdefs.ErrNotImplemented`, and `AnnotationManifestSubject` from the images package. Its GC label output is consumed by `SetChildrenLabels` and metadata garbage collection reference scanning.

## Risks and Edge Cases

`parseMediaTypes` sorts suffixes, so `DiffCompression` looking at the last suffix can be order-insensitive but can also change semantics for complex wrappers where suffix order matters. Docker uncompressed media types return `unknown` because legacy data may be compressed despite the media type. Prefix-based OCI layer detection can classify future layer variants broadly. Deprecated non-distributable types are still supported for compatibility.

## Test Signals

Tests should cover Docker and OCI gzip/zstd/uncompressed variants, encrypted/wrapped suffix behavior, EROFS classification, non-distributable detection, attestation/config/index/manifest classification, referrer-specific GC labels, layer filtering, and `ErrNotImplemented` on non-layer media types.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/mediatypes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/usage/calculator.go -->
# sources/cloud-native/containerd/core/images/usage/calculator.go

## Purpose

This file calculates image storage usage by walking an image descriptor graph and summing either manifest-reported sizes, actual content-store sizes, and optionally referenced snapshot usage.

## Important APIs, Types, and Functions

`usageOptions` stores platform, manifest limit, manifest-only mode, and snapshotter lookup. Options are `WithManifestLimit`, `WithSnapshotters`, and `WithManifestUsage`. `CalculateImageUsage(ctx, image, provider, opts...)` is the exported calculator and requires a `content.InfoReaderProvider`.

## Control Flow

The calculator builds an `images.ChildrenHandler`, wraps it with `LimitManifests` when a platform matcher is supplied, and dispatches from the image target with a concurrency limit of 3. For each descriptor, the handler attempts to discover children, treats missing content as zero usage unless the platform-limited path requires it, reads `content.Info` when actual usage or snapshots are needed, replaces descriptor size with larger actual store size, scans snapshot GC labels, asks configured snapshotters for usage, ignores benign missing/invalid snapshot usage errors, and atomically accumulates descriptor and snapshot sizes.

## State and Persistence Behavior

The function does not mutate metadata. It reads descriptor children, content info, labels, and snapshot usage. The atomic counter allows concurrent handler execution from `images.Dispatch`.

## Dependencies and Integration Points

It integrates `core/images` traversal, content info providers, snapshotters, errdefs, platform matchers, OCI descriptors, and semaphores. It is useful for image listing, CLI size reporting, and cleanup/accounting paths.

## Risks and Edge Cases

Manifest-only mode can count descriptor sizes for content that is not present. Without manifest-only, missing non-required descriptors are counted as zero. Actual content info size can override descriptor size only when larger, avoiding negative or understated sizes. Snapshot usage is discovered through `containerd.io/gc.ref.snapshot.<snapshotter>` labels, so missing labels produce no unpacked usage. Duplicate descriptors are counted each time traversal visits them.

## Test Signals

`calculator_test.go` covers simple manifest, index, missing-layer manifest-only, missing-layer actual usage, and platform manifest limiting. Further tests should include snapshotter usage labels, snapshot not-found/invalid-argument suppression, hard errors from snapshotters, missing platform-limited manifests, duplicate descriptor counting, and negative descriptor sizes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/usage/calculator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/usage/calculator_test.go -->
# sources/cloud-native/containerd/core/images/usage/calculator_test.go

## Purpose

This test file verifies image usage calculation against synthetic image graphs. It confirms the distinction between manifest-reported size and actual stored content size, including missing layers and platform-limited indexes.

## Important APIs, Types, and Functions

`TestUsageCalculation` is a table test using `imagetest.ContentCreator` inputs, `imagetest.ContentSizeCalculator` expected functions, and calculator options. It exercises `CalculateImageUsage`, `WithManifestUsage`, and `WithManifestLimit`.

## Control Flow

For each case the test creates a log-aware context, builds a temporary content store, generates a target content graph, constructs an `images.Image` targeting that descriptor, runs `CalculateImageUsage`, computes the expected size from the in-memory graph, and fails if the totals differ.

## State and Persistence Behavior

Tests write temporary content blobs and delete layer blobs in stripped-layer cases through `imagetest.StripLayers`. All state is isolated in the testing temp directory and in-memory label store.

## Dependencies and Integration Points

It connects the usage package to `core/images`, `imagetest`, `platforms.Only`, OCI platform descriptors, and `logtest`. It is a regression suite for descriptor traversal, content-store presence checks, and manifest-limit behavior.

## Risks and Edge Cases

There is a TODO for snapshot usage, so unpacked snapshot accounting is not verified. The synthetic layer blobs are not valid tar/gzip content, which is fine for usage but not unpack paths. The table does not check error cases for missing required platform manifests or provider errors.

## Test Signals

Passing tests indicate correct totals for manifest-only counting, content-backed counting, missing layers counted as zero when appropriate, and platform limit selection of a single manifest from an index.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/usage/calculator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/introspection/introspection.go -->
# sources/cloud-native/containerd/core/introspection/introspection.go

## Purpose

This file defines the core introspection service interface used by containerd components. It abstracts access to plugin listings, server metadata, and plugin-specific information.

## Important APIs, Types, and Functions

`Service` is the only exported type. It requires `Plugins(context.Context, ...string)`, `Server(context.Context)`, and `PluginInfo(context.Context, string, string, any)`, returning API protobuf response types from `api/services/introspection/v1`.

## Control Flow

There is no implementation control flow in this file. Concrete local or remote services implement the interface.

## State and Persistence Behavior

The interface owns no state. Implementations may read daemon plugin registry state or remote API responses, but this file only defines the contract.

## Dependencies and Integration Points

It depends on the introspection API protobuf package and `context`. The proxy implementation in `core/introspection/proxy/remote.go` adapts gRPC or ttrpc clients to this interface.

## Risks and Edge Cases

The `PluginInfo` options parameter is `any`, so implementations must agree on typeurl/protobuf encoding and return useful errors for unsupported option types. The variadic filters rely on the API's filter grammar rather than typed filter objects.

## Test Signals

Compile-time conformance of implementations, proxy round trips for all methods, filter propagation, and option marshaling failures are the main signals for this contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/introspection/introspection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/introspection/proxy/remote.go -->
# sources/cloud-native/containerd/core/introspection/proxy/remote.go

## Purpose

This file implements a remote introspection service proxy. It adapts supported gRPC or ttrpc client forms into the core `introspection.Service` interface.

## Important APIs, Types, and Functions

`NewIntrospectionProxy(client any)` accepts `api.IntrospectionClient`, `api.TTRPCIntrospectionService`, `grpc.ClientConnInterface`, or `*ttrpc.Client`, returning an `introspection.Service` or panicking on unsupported input. `introspectionRemote` implements `Plugins`, `Server`, and `PluginInfo`. `convertIntrospection` adapts the generated gRPC client to the ttrpc-shaped interface expected internally.

## Control Flow

Construction switches on concrete client type and normalizes it to an `api.TTRPCIntrospectionService`. `Plugins` logs filters and sends a `PluginsRequest`. `Server` sends an empty request. `PluginInfo` marshals non-nil options to protobuf `Any` via typeurl, sends a `PluginInfoRequest`, and converts transport errors to native errdefs errors.

## State and Persistence Behavior

The proxy stores only the remote client. It performs no local persistence and does not cache responses. All state comes from the remote introspection service.

## Dependencies and Integration Points

The proxy integrates generated introspection API clients, gRPC, ttrpc, `errgrpc.ToNative`, `typeurl` option encoding, protobuf `Any`/`Empty`, logging, and the core introspection interface. It is used by clients that need daemon introspection over a transport.

## Risks and Edge Cases

Unsupported client types panic rather than return an error. `PluginInfo` returns a wrapped marshal error before any RPC when options cannot be encoded. The gRPC adapter only forwards calls and relies on caller-provided contexts for deadlines/cancellation. Error conversion is applied to RPC errors, but marshaling errors remain ordinary Go errors.

## Test Signals

Tests should cover each accepted client type, unsupported-type panic, filters passed through `Plugins`, empty request for `Server`, options marshaling in `PluginInfo`, typeurl marshal failure, and gRPC error conversion to native errdefs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/introspection/proxy/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/context.go -->
# sources/cloud-native/containerd/core/leases/context.go

## Purpose

This file stores and retrieves lease IDs on contexts. It also ensures lease IDs propagate through gRPC metadata for remote calls.

## Important APIs, Types, and Functions

`WithLease(ctx, lid)` returns a context containing the lease ID under a private key and outgoing gRPC metadata. `FromContext(ctx)` returns the lease ID from the private context key or, if absent, from incoming gRPC metadata.

## Control Flow

`WithLease` wraps the context with `context.WithValue`, then calls `withGRPCLeaseHeader`. `FromContext` checks the local value first and falls back to `fromGRPCHeader`.

## State and Persistence Behavior

There is no persistence. Lease identity is request-scoped context state and optional gRPC metadata.

## Dependencies and Integration Points

It integrates with lease-aware content, snapshot, and metadata operations and with the gRPC helpers in `grpc.go`. Remote clients can set a lease once on context and have it reach server handlers.

## Risks and Edge Cases

The private value must be a string; empty strings are accepted. Incoming metadata is only consulted when the local context key is absent. Context values do not cross process boundaries unless the gRPC metadata path is used.

## Test Signals

Tests should verify local context retrieval, outgoing metadata creation, incoming metadata fallback, precedence of local value over incoming header, and behavior when no lease exists.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/grpc.go -->
# sources/cloud-native/containerd/core/leases/grpc.go

## Purpose

This file defines the gRPC metadata header used to propagate containerd lease IDs and helper functions to write and read that header.

## Important APIs, Types, and Functions

`GRPCHeader` is the header key `containerd-lease`. `withGRPCLeaseHeader` adds the lease ID to outgoing metadata, merging with existing outgoing metadata and putting the latest value first. `fromGRPCHeader` reads the first lease value from incoming metadata.

## Control Flow

Writing creates a single-pair metadata set. If outgoing metadata already exists, it joins the new pair before the old metadata. Reading checks for incoming metadata, then the header key, then returns the first value.

## State and Persistence Behavior

The helpers only mutate context metadata values. No lease object is created or persisted here.

## Dependencies and Integration Points

It depends on `google.golang.org/grpc/metadata` and is called by `WithLease`/`FromContext`. Server-side lease-aware code can retrieve lease identity from incoming RPC contexts.

## Risks and Edge Cases

Multiple lease headers can exist; the first value wins. Header values are not validated. Outgoing metadata is separate from incoming metadata, so a client context with outgoing lease headers will not be visible to `fromGRPCHeader` until transported by gRPC.

## Test Signals

Useful tests cover metadata merge ordering, no-header false returns, multiple header values selecting the first, and round-trip propagation through a gRPC call context.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/id.go -->
# sources/cloud-native/containerd/core/leases/id.go

## Purpose

This file provides lease option helpers for setting lease IDs. It includes explicit IDs and a simple random ID generator.

## Important APIs, Types, and Functions

`WithRandomID()` returns an option that sets `Lease.ID` to `<nanosecond>-<base64url random 3 bytes>`. `WithID(id)` returns an option that sets `Lease.ID` to the provided string.

## Control Flow

Each function returns a closure over a `*Lease`. The random form reads three random bytes, combines them with the current nanosecond value, and assigns the resulting string. The explicit form assigns the given ID directly.

## State and Persistence Behavior

The functions mutate only an in-memory `Lease` during option application. Persistence is handled by lease manager implementations.

## Dependencies and Integration Points

These options are passed to `leases.Manager.Create`, including metadata and proxy lease managers. They depend on `crypto/rand`, `base64`, `fmt`, and `time`.

## Risks and Edge Cases

`rand.Read` errors are ignored, so random bytes could remain zero if the system RNG fails. Three random bytes plus nanoseconds is not a strong global uniqueness guarantee under high concurrency or across processes. `WithID` performs no validation; managers must reject invalid or duplicate IDs.

## Test Signals

Tests should check explicit ID application, random ID non-empty format, low collision behavior in repeated calls, and manager-level duplicate/invalid ID handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/id.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/lease.go -->
# sources/cloud-native/containerd/core/leases/lease.go

## Purpose

This file defines the core lease model, resource model, manager interface, and common lease options. Leases retain resources so garbage collection does not remove them before they are fully referenced elsewhere.

## Important APIs, Types, and Functions

`Manager` defines create, delete, list, add/delete resource, and list resources operations. `Lease` carries ID, creation time, and labels. `Resource` carries type and ID for retained content, ingests, snapshots, or other resource types. `DeleteOptions` and `SynchronousDelete` control delete cleanup behavior. `WithLabel`, `WithLabels`, and `WithExpiration` mutate lease labels.

## Control Flow

Option functions initialize label maps when needed and then set or copy entries. `WithExpiration` writes `containerd.io/gc.expire` as an RFC3339 timestamp based on `time.Now().Add(d)`. The manager interface leaves concrete CRUD behavior to implementations.

## State and Persistence Behavior

The model is in-memory here, but labels have GC semantics in metadata: expiration labels can make leases stop acting as roots after the timestamp. Resource additions are persisted by manager implementations such as metadata or proxy services.

## Dependencies and Integration Points

It integrates with metadata GC, content ingest/write lease attachment, gRPC proxy managers, and client contexts carrying lease IDs. It uses `maps.Copy` for label merging and standard time formatting.

## Risks and Edge Cases

Label values are not validated by option helpers. `WithLabels` copies all entries, including empty values. Expiration depends on local clock and RFC3339 precision. `SynchronousDelete` is a function rather than a closure factory, so callers pass it directly as a `DeleteOpt`.

## Test Signals

`lease_test.go` covers label merging for empty and non-empty maps and equivalence between `WithLabels` and repeated `WithLabel`. Further tests should cover expiration label format, nil/empty label behavior, synchronous delete propagation, and resource retention through metadata GC.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/lease.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/lease_test.go -->
# sources/cloud-native/containerd/core/leases/lease_test.go

## Purpose

This test file verifies lease label option behavior. It protects label merging semantics used by lease creation and metadata GC labeling.

## Important APIs, Types, and Functions

`TestWithLabels` runs table cases for `WithLabels` and repeated `WithLabel`. `newLease` creates a lease with a defensive copy of initial labels.

## Control Flow

The test first applies `WithLabels` to leases with nil or existing labels and compares the resulting map to expected values. It then repeats the same cases by applying `WithLabel` for each input label and checking the same expected output.

## State and Persistence Behavior

All state is in-memory. The tests do not exercise a lease manager or metadata DB.

## Dependencies and Integration Points

It uses `maps.Copy`, `testify/assert`, and `testify/require`. It validates option helpers consumed by both local metadata and remote proxy lease managers.

## Risks and Edge Cases

The file does not test overwriting an existing key, empty values, nil input maps, expiration labels, random IDs, or delete options. It also does not validate labels through the metadata manager.

## Test Signals

Passing tests indicate label map initialization, merging, and preservation of existing labels work for both bulk and single-label option APIs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/lease_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/proxy/manager.go -->
# sources/cloud-native/containerd/core/leases/proxy/manager.go

## Purpose

This file implements a `leases.Manager` backed by the generated gRPC leases service client. It lets callers use the core leases interface against a remote containerd service.

## Important APIs, Types, and Functions

`NewLeaseManager(client)` returns a `leases.Manager`. `proxyManager` implements `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`. It converts between core `leases.Lease`/`leases.Resource` and API protobuf messages.

## Control Flow

`Create` applies lease options locally, sends a `CreateRequest`, converts gRPC errors to native errors, and maps the response timestamp through `protobuf.FromTimestamp`. `Delete` applies delete options and sends `DeleteRequest` with `Sync`. `List` sends filters and maps every response lease. Resource methods send the lease ID plus one resource or list response resources.

## State and Persistence Behavior

The proxy stores only the generated client. Persistent lease state lives on the remote service. Delete sync behavior is passed through to the server.

## Dependencies and Integration Points

It integrates generated leases API clients, core leases interfaces, `errgrpc.ToNative`, and protobuf timestamp conversion. It is used by clients communicating with containerd over gRPC.

## Risks and Edge Cases

The proxy trusts caller-provided lease/resource IDs and relies on server validation. It does not defensively copy label maps from responses. Only gRPC clients are supported here; ttrpc lease proxying would need a separate adapter. Option application errors stop before RPC.

## Test Signals

Tests should use a fake leases client to verify request fields, option application, timestamp conversion, error conversion, resource mapping, synchronous delete propagation, and list filter forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/leases/proxy/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/adaptors.go -->
# sources/cloud-native/containerd/core/metadata/adaptors.go

## Purpose

This file defines filter adaptors for metadata objects. Adaptors expose selected object fields to containerd's filter parser so list operations can filter images, containers, content statuses, leases, snapshots, and sandboxes.

## Important APIs, Types, and Functions

Adaptors include `adaptImage`, `adaptContainer`, `adaptContentStatus`, `adaptLease`, `adaptSnapshot`, and `adaptSandbox`. `checkMap` resolves dotted filter field paths against label or annotation maps. Each adaptor returns a `filters.AdapterFunc`.

## Control Flow

Each adaptor checks the first path segment and returns a string value plus a boolean indicating field presence. Nested paths support target digest/media type, runtime name, labels, and annotations. Snapshot kind is converted to `active`, `view`, or `committed`.

## State and Persistence Behavior

The functions read in-memory objects and do not mutate metadata. They influence which persisted objects are returned by list operations.

## Dependencies and Integration Points

They integrate metadata stores with `pkg/filters` and core object types from containers, content, images, leases, sandbox, and snapshots. Container and image stores use these adaptors during `List`.

## Risks and Edge Cases

Unknown fields return absent. `checkMap` joins all remaining path segments with dots, which allows label keys containing dots but means empty remaining paths look up an empty key. Snapshot name and parent return present even when empty. Adaptors expose only a subset of object fields; filters on unsupported fields silently do not match.

## Test Signals

List tests should cover every supported field path, labels with dotted keys, missing labels/annotations, snapshot kind strings, unsupported fields, and OR/AND filter behavior in callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/adaptors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/bolt.go -->
# sources/cloud-native/containerd/core/metadata/bolt.go

## Purpose

This file abstracts Bolt transaction execution and lets metadata operations reuse a transaction already stored on context. It is the bridge between context-scoped transactions and the DB's read/write transaction API.

## Important APIs, Types, and Functions

`Transactor` defines `View` and `Update`. `view(ctx, db, fn)` runs `fn` inside a read transaction, reusing `boltutil.Transaction(ctx)` when present. `update(ctx, db, fn)` similarly reuses a context transaction but rejects non-writable transactions.

## Control Flow

Both helpers check the context first. Without a context transaction they call `db.View` or `db.Update`. With a transaction, `view` directly invokes the callback. `update` checks `tx.Writable()` and returns a wrapped `ErrTxNotWritable` if the context transaction is read-only.

## State and Persistence Behavior

The helpers do not persist data themselves, but they control transaction boundaries for all metadata stores. Reusing a context transaction allows multi-object operations to be atomic across store calls.

## Dependencies and Integration Points

They depend on `boltutil.Transaction`, bbolt transactions, and bbolt error definitions. Metadata container/content/image/lease/snapshot stores call them for their CRUD operations.

## Risks and Edge Cases

A writable transaction in context bypasses `DB.Update`'s mutation callback and lock behavior unless the caller created it through the DB carefully. A read-only context transaction passed to update fails. Callers must ensure context transaction lifetime outlives the operation and is not used concurrently unsafely.

## Test Signals

Tests should cover transaction reuse, starting new transactions when absent, read-only transaction rejection, nested metadata calls inside a single update transaction, and callback/dirty behavior when operations bypass `DB.Update`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/bolt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/boltutil/context.go -->
# sources/cloud-native/containerd/core/metadata/boltutil/context.go

## Purpose

This file provides context helpers for carrying an existing bbolt transaction. Metadata code uses it to compose multiple store operations inside one transaction.

## Important APIs, Types, and Functions

`WithTransaction(ctx, tx)` returns a context containing the transaction under a private key. `Transaction(ctx)` retrieves the `*bolt.Tx` and a boolean.

## Control Flow

The functions are simple context value set/get operations. Type assertion ensures only `*bolt.Tx` values are returned.

## State and Persistence Behavior

The transaction pointer is request-scoped context state. Persistence depends on the transaction owner committing or rolling back outside this helper.

## Dependencies and Integration Points

It depends on `context` and bbolt. The metadata `view` and `update` helpers consume this context state, and tests use it to perform store operations inside explicit transactions.

## Risks and Edge Cases

Context values do not manage transaction lifetime or writability. Passing a closed or rolled-back transaction will fail later. This pattern should not be used across goroutines unless transaction safety is understood.

## Test Signals

Tests should verify retrieval of stored transactions, absence behavior, type safety, and successful metadata operations composed through a context transaction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/boltutil/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/boltutil/helpers.go -->
# sources/cloud-native/containerd/core/metadata/boltutil/helpers.go

## Purpose

This file provides reusable bbolt serialization helpers for common metadata fields: labels, annotations, timestamps, extension maps, and protobuf Any values.

## Important APIs, Types, and Functions

`ReadLabels`, `WriteLabels`, `ReadAnnotations`, and `WriteAnnotations` operate on child buckets. `ReadTimestamps` and `WriteTimestamps` store binary `time.Time` values for created/updated keys. `WriteExtensions` and `ReadExtensions` marshal maps of `typeurl.Any` into an `extensions` bucket. `WriteAny` and `ReadAny` marshal individual protobuf Any values.

## Control Flow

Map writers delete any existing child bucket, skip creation for empty maps, create a fresh bucket, write non-empty values, and delete zero-value keys from the caller's map. Readers return nil when a map bucket does not exist. Extension and Any helpers use containerd's protobuf shim and typeurl marshaling before storing bytes.

## State and Persistence Behavior

The helpers mutate bbolt buckets passed by callers. Labels/annotations are stored as nested key/value buckets, timestamps as binary blobs, extensions as protobuf Any bytes by extension name, and individual Any values as protobuf bytes under a named key.

## Dependencies and Integration Points

Container, image, content, sandbox, lease, and namespace metadata code use these helpers for consistent serialization. Dependencies include containerd protobuf packages, typeurl, bbolt, and `time`.

## Risks and Edge Cases

`writeMap` mutates the caller-provided labels map by deleting empty values. `WriteExtensions` does not remove an existing extensions bucket when the map is empty, so callers replacing extensions with nil need to ensure stale data is handled elsewhere. `ReadExtensions` returns protobuf Any wrappers, not fully unmarshaled typed values. Timestamp unmarshalling errors surface from potentially corrupt DB values.

## Test Signals

Tests should cover nil and empty maps, empty label deletion side effects, replacing existing label buckets, timestamp round trips, Any nil handling, extension map round trips, corrupt protobuf bytes, and stale extension removal behavior in callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/boltutil/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/buckets.go -->
# sources/cloud-native/containerd/core/metadata/buckets.go

## Purpose

This file documents and codifies the bbolt bucket schema for containerd metadata. It defines bucket key constants and helper functions for locating or creating namespace-scoped object buckets.

## Important APIs, Types, and Functions

Constants include schema/version keys, object buckets for labels/images/containers/snapshots/content/blobs/ingests/leases/sandboxes, field keys such as digest/media type/size/runtime/spec/snapshot fields, and a deprecated ingest bucket key. Helpers include `getBucket`, `createBucketIfNotExists`, path helpers for namespace labels and images, and getters/creators for image, container, snapshotter, blob, ingest, and sandbox buckets.

## Control Flow

`getBucket` walks a sequence of bucket keys and returns nil on the first missing bucket. `createBucketIfNotExists` creates the first bucket on the transaction and then creates each nested bucket. Object-specific helpers compose these primitives with namespace and object-type keys.

## State and Persistence Behavior

The file is the persistence map for metadata DB version `v1`. It lays out namespace labels, images, containers, snapshots, content blobs/ingests, sandboxes, and leases, including timestamps, labels, target descriptors, runtime/spec data, parent/children links, and lease resource buckets.

## Dependencies and Integration Points

All metadata stores and GC code depend on these key constants and helpers. The embedded schema comments are the reference for migrations and backward-compatible additions. It depends only on bbolt and OpenContainers digests.

## Risks and Edge Cases

Bucket key changes are schema changes and must be paired with migrations. Some helper names differ from schema comments historically, so code should rely on constants rather than prose alone. `createBlobBucket` uses `CreateBucket`, not `CreateBucketIfNotExists`, to detect duplicate content. Namespace name `version` is reserved by schema design.

## Test Signals

Migration tests, CRUD tests for each object type, and GC graph scans validate the bucket layout. Any schema change needs tests that old layouts migrate into the documented bucket tree and that helper getters find the expected buckets.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/buckets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/compare_test.go -->
# sources/cloud-native/containerd/core/metadata/compare_test.go

## Purpose

This test helper file defines custom `go-cmp` comparers used by metadata tests. It normalizes typed nils, timestamps, and protobuf Any values so object round-trip assertions focus on meaningful fields.

## Important APIs, Types, and Functions

`isNil` detects nil and typed nil pointers. `compareNil` treats two nil or typed nil values as equal. `ignoreTime` treats all `time.Time` values as equal. `compareAny` compares `typeurl.Any` values by type URL and raw value bytes.

## Control Flow

The comparers use `cmp.FilterValues` predicates to activate only for relevant value pairs, then supply equality functions. `compareAny` type-asserts both values and compares type URL plus bytes.

## State and Persistence Behavior

No state is persisted. These are test-only comparison utilities.

## Dependencies and Integration Points

Container metadata tests use these options when comparing containers that include timestamps, optional Any fields, and typed nil protobuf values. Dependencies include `reflect`, `bytes`, `time`, `typeurl`, and `go-cmp`.

## Risks and Edge Cases

`ignoreTime` hides timestamp regressions unless tests explicitly check timestamps elsewhere. `isNil` only treats pointers as typed nil, not nil slices/maps/interfaces of other kinds. `compareAny` compares serialized values, not semantic decoded messages.

## Test Signals

These helpers support container create/update tests. Separate timestamp checks in `containers_test.go` compensate for the broad `ignoreTime` comparer.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/compare_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/containers.go -->
# sources/cloud-native/containerd/core/metadata/containers.go

## Purpose

This file implements the metadata-backed container store. It persists container records in bbolt, supports filters, field-mask updates, validation, tracing, and marks metadata dirty when containers are deleted.

## Important APIs, Types, and Functions

`NewContainerStore(db)` returns a `containers.Store`. `containerStore` implements `Get`, `List`, `Create`, `Update`, and `Delete`. Internal helpers are `validateContainer`, `readContainer`, and `writeContainer`. It stores specs/runtime options/extensions as protobuf Any data and labels/timestamps through `boltutil`.

## Control Flow

Every public method requires a namespace from context. `Get` reads one bucket and unmarshals a container. `List` parses filters, iterates namespace container buckets, reads each record, and applies `adaptContainer`. `Create` validates input, creates a new container bucket, sets timestamps, and writes fields. `Update` loads the existing record, applies field paths for labels, extensions, spec, image, and snapshot key, rejects immutable changes on full replace, validates, updates `UpdatedAt`, and writes back. `Delete` deletes the bucket and increments the DB dirty counter.

## State and Persistence Behavior

Container records live under `v1/<namespace>/containers/<id>`. Stored fields include timestamps, spec Any, image, snapshotter, snapshot key, runtime name/options, extensions, sandbox ID, and labels. Deletion removes the metadata record but does not directly delete snapshots/content; dirty state triggers later GC.

## Dependencies and Integration Points

It integrates with core container types, metadata bucket helpers, `boltutil`, filters, namespace context, identifier and label validation, protobuf/typeurl, tracing, errdefs, and bbolt errors. GC uses container records as roots to retain referenced snapshots and labeled references.

## Risks and Edge Cases

Full updates only permit selected mutable fields and explicitly reject runtime name and snapshotter changes. Field paths are stringly typed and lower-case names such as `snapshotkey`. Label and extension subfield updates create maps if needed and can delete labels by writing empty values through `WriteLabels`. `writeContainer` deletes and recreates the runtime bucket but `WriteExtensions` may leave stale extension data if callers pass empty extension maps without deleting the bucket first.

## Test Signals

`containers_test.go` covers list filters, create/update/delete, invalid updates, immutable fields, label deletion, extensions, timestamps, and validation errors. Additional tests should cover sandbox ID persistence, runtime options round trip, stale extension removal, and GC retention of container snapshots.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/containers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/containers_test.go -->
# sources/cloud-native/containerd/core/metadata/containers_test.go

## Purpose

This test file validates the metadata container store's filtering, create/update/delete behavior, validation, timestamp handling, and protobuf Any comparison.

## Important APIs, Types, and Functions

`TestContainersList` creates multiple containers and checks filter results by labels, ID, and runtime name. `TestContainersCreateUpdateDelete` is a large table covering invalid and valid update cases. Helpers include `checkContainerTimestamps`, `checkContainersEqual`, and `testEnv`. The test registers the OCI runtime spec type with typeurl in `init`.

## Control Flow

The list test creates containers inside explicit Bolt transactions using `boltutil.WithTransaction`, mirrors expected objects, applies filters both locally and through the store, and compares results. The create/update/delete test creates a container, checks timestamps and round-trip equality, applies an update with specified field paths, checks expected error causes or updated record, then retrieves the object again for persistence verification.

## State and Persistence Behavior

Tests use a temporary bbolt database with namespace `testing`. They persist real container buckets and verify created/updated timestamps, label removal, extension replacement or isolated field updates, spec Any values, image and snapshot fields, and delete NotFound behavior.

## Dependencies and Integration Points

The tests exercise `NewContainerStore`, `boltutil.WithTransaction`, filters, namespaces, typeurl/protobuf Any, errdefs, bbolt, logtest, go-cmp options from `compare_test.go`, and testify assertions.

## Risks and Edge Cases

The tests account for Windows timestamp granularity. They do not exhaustively test runtime options, sandbox ID persistence, concurrent transactions, or all possible invalid identifiers/labels. Some field names intentionally reflect store API spelling, so tests help catch accidental field-mask changes.

## Test Signals

Passing tests indicate container CRUD persists the expected fields, filters match supported paths, immutable fields stay protected, label/extension field masks work, timestamps are set correctly, and validation errors are wrapped with errdefs causes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/containers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/content.go -->
# sources/cloud-native/containerd/core/metadata/content.go

## Purpose

This file implements a metadata-backed, namespace-aware content store wrapper. It controls content visibility, label metadata, ingest tracking, shared vs isolated namespace policy, lease attachment, event publication, and backend content cleanup.

## Important APIs, Types, and Functions

`newContentStore` constructs `contentStore`, which embeds a backend `content.Store`. Public methods include `Info`, `Update`, `Walk`, `Delete`, `ListStatuses`, `Status`, `Abort`, `Writer`, and `ReaderAt`. `namespacedWriter` wraps backend writers and implements `Close`, `Write`, `Digest`, `Truncate`, `Commit`, `Sync`, `Status`, plus internal `createAndCopy` and `commit`. Helpers include `getRef`, `isSharedContent`, `validateInfo`, `readInfo`, `writeInfo`, `readExpireAt`, `writeExpireAt`, and `garbageCollect`.

## Control Flow

Reads require a namespace and verify the digest exists in namespace metadata before accessing backend content. `Writer` validates a non-empty ref, checks for existing namespace content, optionally marks an existing backend blob as shared, creates an ingest bucket and lease reference, writes a backend ref unless shared, and returns a namespaced writer. `namespacedWriter.Commit` syncs backend writes before opening the metadata transaction, validates size/digest, commits backend content if needed, creates the namespace blob bucket, writes timestamps/labels/size, removes ingest metadata and lease, attaches content to the current lease, and publishes a create event outside transactions. `Delete` removes namespace blob metadata, removes lease references, marks DB/content dirty, and publishes a delete event.

## State and Persistence Behavior

Content metadata is stored under `v1/<namespace>/content/blob/<digest>` with timestamps, size, and labels. Active ingests live under `v1/<namespace>/content/ingests/<ref>` with backend ref, optional expiration, and optional expected digest. Backend content is shared physically, while namespace metadata controls access. GC later deletes unreferenced backend blobs and aborts unreferenced backend ingests. Lease context can attach content or ingests under namespace lease buckets.

## Dependencies and Integration Points

The wrapper integrates `core/content`, metadata DB transactions, leases, namespace context, local/shared namespace labels, events, errdefs, OCI descriptors, OpenContainers digests, bbolt, label validation, and metadata GC. It is returned by `DB.ContentStore()`.

## Risks and Edge Cases

Writer shared mode can return a nil backend writer until data is written or truncated; methods must handle that split path. Commit tolerates backend AlreadyExists but still needs metadata creation to avoid duplicate namespace records. Sync before metadata lock reduces long lock holds but assumes writer implements `content.Syncer`. `ListStatuses` and `Status` translate namespace refs to backend refs, so stale ingest metadata can hide backend status. `isSharedContent` scans all namespaces for the shared label and matching blob, which can be expensive.

## Test Signals

`content_test.go` runs containerd content suites for shared and isolated policies plus lease tests for committed content and active ingests. Additional tests should cover event publication, stale ingest expiration, shared writer copy-on-write through `Write`/`Truncate`, label field updates, backend cleanup, and access denial across namespaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/content.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/content_test.go -->
# sources/cloud-native/containerd/core/metadata/content_test.go

## Purpose

This test file validates the metadata content store wrapper against containerd's content-store contract and verifies lease linkage for committed blobs and active ingests.

## Important APIs, Types, and Functions

`createContentStore` builds a local content store plus metadata DB and namespace wrapper used by testsuite helpers. `createContentStoreWithPolicy` adapts DB options into a testsuite init function. `TestContent` runs content, cross-namespace shared, cross-namespace isolated, and shared-namespace isolated suites. `TestContentLeased` and `TestIngestLeased` check lease buckets. Helpers include `createLease`, `checkContentLeased`, and `checkIngestLeased`.

## Control Flow

The testsuite wrapper creates unique namespaces per test and optionally marks namespaces as shared by writing the shared namespace label through the namespace store. Lease tests create a metadata DB, create a lease, write or begin content through a lease-bearing context, then inspect Bolt buckets to assert content or ingest resource references exist or are removed after commit/abort.

## State and Persistence Behavior

Tests use temporary local content and metadata databases. They directly inspect `v1/<namespace>/leases/<lease>/content` and `.../ingests` buckets to verify lease persistence. The content suites exercise backend blob storage, namespace metadata, and policy-dependent sharing behavior.

## Dependencies and Integration Points

The file integrates `core/content/testsuite`, metadata DB, local content store, leases, namespace labels, bbolt, errdefs, digest and OCI descriptors. It is the strongest behavioral signal for `content.go`.

## Risks and Edge Cases

Event publishing and backend garbage collection are not directly checked here. Lease checks inspect internal bucket paths, which is appropriate for metadata but couples tests to schema. The shared namespace wrapper writes labels in a raw DB update and assumes namespace store behavior.

## Test Signals

Passing tests indicate the metadata content store satisfies the content store contract in default/shared and isolated policies, correctly attaches existing and newly committed content to leases, leases active ingests, and removes ingest lease records after abort/commit.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/content_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/db.go -->
# sources/cloud-native/containerd/core/metadata/db.go

## Purpose

This file defines the metadata database object that coordinates bbolt metadata, content and snapshot backends, migrations, mutation callbacks, event publishing, collectible resource registration, and garbage collection.

## Important APIs, Types, and Functions

Constants `schemaVersion` and `dbVersion` define the DB schema. Options include `WithPolicyIsolated` and `WithEventsPublisher`. `DB` holds the transactor, snapshotters, content store, GC locks/dirty flags, callbacks, collectors, and options. Public methods include `NewDB`, `Close`, `Init`, `ContentStore`, `Snapshotter`, `Snapshotters`, `View`, `Update`, `Publisher`, `RegisterMutationCallback`, `RegisterCollectibleResource`, and `GarbageCollect`. `GCStats` reports phase durations. Internal helpers include `publishEvents`, `getMarked`, `cleanupSnapshotter`, and `cleanupContent`.

## Control Flow

`NewDB` wraps the backend content store and snapshotters. `Init` opens a write transaction, discovers current schema/version by scanning migrations backward, applies needed migrations, creates the v1 bucket, and stores the current DB version, using a sentinel error to skip no-op commits. `Update` takes the GC read lock, runs a write transaction, and invokes mutation callbacks with dirty status on success. `GarbageCollect` takes the GC write lock, builds a collection context, marks reachable nodes, opens a write transaction to remove unmarked metadata nodes and set dirty backend flags, resets dirty counters, schedules event publication plus backend snapshot/content cleanup, finishes custom collectors, releases the lock, then waits for async cleanup.

## State and Persistence Behavior

The DB persists all metadata under bbolt schema `v1`. Dirty flags track deletions requiring GC, including which snapshotters and whether content need backend cleanup. Garbage collection removes metadata records first, then separately asks snapshotter/content backends to remove unreferenced data. Events are published only after successful metadata commit.

## Dependencies and Integration Points

It integrates bbolt, content stores, snapshotters, metadata migrations, events, namespace context, GC graph package, log/tracing through callers, and custom collectible resource collectors. Other metadata store implementations use `DB.Update` and `DB.View`.

## Risks and Edge Cases

Operations using a context transaction can bypass `DB.Update` callback timing. GC holds a write lock through marking and metadata sweep but releases before waiting for backend cleanup; this limits mutation during mark/sweep while allowing cleanup to continue. Collector start failures silently skip that resource type for the round. Event publication is asynchronous and logs failures rather than failing GC. Schema migration correctness is critical because all stores share bucket constants.

## Test Signals

`db_test.go` covers initialization versioning, migration cases, metadata collector behavior, GC benchmarking, helper store construction, and close semantics. Additional tests should cover mutation callbacks, event publishing after GC removals, isolated policy construction, collector start failure, and concurrent update/GC interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/db_test.go -->
# sources/cloud-native/containerd/core/metadata/db_test.go

## Purpose

This test file validates metadata DB initialization, migrations, garbage-collection graph behavior, benchmarks GC, and verifies DB close behavior.

## Important APIs, Types, and Functions

`testDB`, `newStores`, and `testEnv` create temporary DB/content/snapshot environments. `TestInit` verifies DB version. `TestMigrations` drives each migration through an init/check pair. `TestMetadataCollector` builds a mixed graph of content, snapshots, containers, images, leases, flat leases, and custom collectible resources. `BenchmarkGarbageCollect` measures GC over generated object sets. `TestClose` verifies underlying bbolt closure.

## Control Flow

Migration tests create old-layout data, run the selected migration, and inspect the resulting buckets. Collector tests register a custom resource collector, create objects in a single transaction, run `GarbageCollect`, scan all remaining nodes, and compare them to the expected reachable set. Benchmarks generate many repeated content/image/snapshot/container sets and repeatedly invoke GC under pprof labels.

## State and Persistence Behavior

The tests create real bbolt DBs, local content stores, and native snapshotters in temp directories. They exercise schema buckets, content metadata, snapshot metadata, leases, GC labels, custom collector state, backend cleanup, and DB close behavior.

## Dependencies and Integration Points

The file integrates most metadata subsystems: containers, images, content, leases, snapshots, bbolt, local content, native snapshots, GC package, protobuf Any, namespace context, migrations, and test collectors/helpers defined in the same package.

## Risks and Edge Cases

Migration test count is tied to `len(migrations)`, forcing new migrations to add coverage. The GC benchmark does not assert post-GC state during benchmarking. Some helper-created objects bypass public APIs for setup convenience, so public API coverage comes from other tests.

## Test Signals

Passing tests indicate DB version initialization, each migration's structural transformation, GC reachability across labels/leases/flat leases/custom resources, and safe DB close semantics. Benchmarks provide performance signals for mark/sweep scaling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/gc.go -->
# sources/cloud-native/containerd/core/metadata/gc.go

## Purpose

This file implements metadata garbage-collection graph construction and metadata record removal. It defines resource types, GC reference label semantics, custom collector integration, root scanning, reference traversal, all-resource scanning, and node removal.

## Important APIs, Types, and Functions

Resource constants include content, snapshots, containers, tasks, images, leases, ingests, streams, mounts, plus internal flat lease variants. `CollectionContext` and `Collector` define custom collectible resource hooks. `startGCContext` builds a `gcContext` with label handlers. Key methods are `scanRoots`, `references`, `scanAll`, `remove`, `sendLabelRefs`, `active`, `leased`, `cancel`, and `finish`. Helpers include `isExpiredImage` and `gcnode`.

## Control Flow

`startGCContext` installs handlers for root labels, forward references, back references, snapshot conditionals, conditional values, and registered custom collectors, sorting handlers for forward cursor seeks. `scanRoots` iterates namespaces, emits non-expired leases and their resource roots, non-expired images, unexpired ingests, label-rooted content/snapshots, containers, sandbox label references, active custom resources, and conditional back references after all values are collected. `references` returns outgoing edges for content labels, snapshot parents and labels, image target content and labels, ingest expected content, and container snapshots/labels. `scanAll` enumerates all metadata nodes plus custom collector nodes. `remove` deletes the relevant metadata bucket or delegates to custom collector remove, returning snapshot/image events where applicable.

## State and Persistence Behavior

GC state is a graph over bbolt metadata nodes. Labels such as `containerd.io/gc.root`, `containerd.io/gc.ref.content.*`, `containerd.io/gc.bref.*`, `containerd.io/gc.expire`, `containerd.io/gc.flat`, and conditional snapshot labels control reachability. Removal deletes metadata buckets for content, snapshots, images, leases, and ingests; backend physical cleanup is scheduled by `DB.GarbageCollect` after metadata sweep.

## Dependencies and Integration Points

The file integrates with bbolt bucket schema, `pkg/gc` tricolor traversal through `DB.getMarked`, event types for image/snapshot removals, log package, custom collectors, and metadata stores that write GC labels. Content and snapshot backend cleanup depends on dirty flags set by `DB.GarbageCollect` when `remove` deletes content/snapshot nodes.

## Risks and Edge Cases

Label parsing is string/byte-prefix based, so malformed labels are ignored or can create dead edges. Flat leases intentionally retain only directly leased resources and skip recursive label references. Expired images can still be retained by back references. Conditional snapshot references currently support only `usedat` duration comparisons and OR-style condition parsing. Custom collector start failures skip collection for that resource type this round. `scanAll` ignores callback errors from custom `c.all` nodes.

## Test Signals

`db_test.go` exercises GC reachability with roots, images, containers, snapshots, leases, flat leases, content labels, and custom collectible resources. Additional tests should cover expiration labels, invalid expiration values, conditional snapshot references, back references, malformed snapshot keys, removal event payloads, and custom collector cancel/finish error handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/metadata/gc.go -->
