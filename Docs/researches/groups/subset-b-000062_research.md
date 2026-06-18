# Research: subset-b-000062

This grouped report covers the requested containerd source files. Each file section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/testsuite.go -->
# sources/cloud-native/containerd/core/snapshots/testsuite/testsuite.go

## Purpose
This file defines a reusable conformance suite for implementations of `snapshots.Snapshotter`. `SnapshotterSuite` takes a snapshotter factory and runs a broad set of behavioral tests covering active, committed, and view snapshots; filesystem layering semantics; metadata updates; filtering; removal; readonly views; close idempotency; root permissions; rename behavior; and deep layer stacks.

## Important APIs, Types, and Functions
`SnapshotterFunc` is the factory contract. `SnapshotterSuite` wires named subtests through `makeTest`, which creates a temporary root/work directory, installs a namespace and mount manager, initializes the snapshotter, and dumps the temp tree on failure. Helpers include `snapshotterPrepareMount`, `baseTestSnapshots`, `assertLabels`, and the package-level `opt` label set with `containerd.io/gc.root`.

## Control Flow
Each test prepares snapshots, mounts returned mounts into the work tree, mutates files with `fstest` appliers or `os.WriteFile`, unmounts, commits, stats, walks, views, and removes snapshots. The suite validates both data-plane file visibility and metadata-plane fields such as kind, parent, timestamps, labels, and filter results.

## State and Persistence
State is persisted through the snapshotter under a per-test root. The tests assert key lifecycle transitions: `Prepare` creates active snapshots, `Commit` removes the active key and creates a committed key, `View` creates readonly views, and `Remove` must reject committed parents while children exist. Labels are updated and filtered, with GC-root labels intentionally kept.

## Dependencies and Integration Points
The suite depends on `github.com/containerd/containerd/v2/core/snapshots`, mount manager helpers, `continuity/fs/fstest`, namespace context, and test utilities. Platform-specific helpers in `testsuite_unix.go` and `testsuite_windows.go` supply umask handling.

## Risks
Tests use real mounts, filesystem permissions, and platform behavior, so failures may reflect host capabilities as much as snapshotter bugs. Several cases require careful cleanup after mount failures. The 128-layer test stresses mount option limits and may expose snapshotter-specific constraints.

## Test Signals
This is itself a test suite. Strong signals include transitive parent checks, immutable field rejection, label field-path updates, view readonly enforcement through an actual write attempt, whiteout/delete semantics, file move behavior, walk filters, root permissions, close twice, and deep layering consistency.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/testsuite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/testsuite_unix.go -->
# sources/cloud-native/containerd/core/snapshots/testsuite/testsuite_unix.go

## Purpose
This Unix-only helper normalizes process umask for the snapshotter conformance suite.

## Important APIs, Types, and Functions
`clearMask` calls `syscall.Umask(0)` and returns a closure that restores the previous mask.

## Control Flow
`SnapshotterSuite` calls `clearMask` before registering tests and defers the returned restore function. All tests then run with a zero umask so mode assertions are not altered by the caller environment.

## State and Persistence
The only state is process-global umask. It is restored at suite exit.

## Dependencies and Integration Points
The file is selected by `//go:build !windows` and is paired with the Windows no-op implementation.

## Risks
Umask is process-wide, while tests run in parallel. The suite changes it around test registration, but any concurrent test in the same process could theoretically observe the temporary value.

## Test Signals
Supports mode-sensitive tests such as root permission and directory permission checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/testsuite_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/testsuite_windows.go -->
# sources/cloud-native/containerd/core/snapshots/testsuite/testsuite_windows.go

## Purpose
This Windows helper provides the same `clearMask` symbol as Unix builds without changing any process state.

## Important APIs, Types, and Functions
`clearMask` returns an empty restore closure.

## Control Flow
The snapshotter suite can call `clearMask` unconditionally while Windows builds avoid unsupported umask operations.

## State and Persistence
No state is read or written.

## Dependencies and Integration Points
This file is selected on Windows and complements the non-Windows implementation.

## Risks
Windows filesystem permission semantics differ from Unix, so tests depending on Unix modes are skipped or interpreted elsewhere.

## Test Signals
The helper keeps the suite buildable on Windows while preserving the shared suite API.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/snapshots/testsuite/testsuite_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/streaming/proxy/streaming.go -->
# sources/cloud-native/containerd/core/streaming/proxy/streaming.go

## Purpose
This file adapts gRPC or TTRPC streaming clients to containerd's internal `streaming.StreamCreator` interface.

## Important APIs, Types, and Functions
`NewStreamCreator` accepts generated gRPC clients, gRPC connections, TTRPC clients/services, or an existing `streaming.StreamCreator`. `streamCreator.Create` opens a service stream, sends a `StreamInit` message containing the requested stream ID, waits for an acknowledgement, and returns a `clientStream`. `clientStream` wraps send, receive, and close operations.

## Control Flow
Creation chooses a client adapter, opens a bidirectional stream, marshals the init object through `typeurl`, sends it as protobuf `Any`, receives an ack, and then proxies future `typeurl.Any` messages.

## State and Persistence
No durable state is stored. Runtime state is the active remote stream and its negotiated ID.

## Dependencies and Integration Points
Integrates `api/services/streaming/v1`, `typeurl`, gRPC, TTRPC, and `errgrpc.ToNative`. It is used by transfer proxying and stream-backed transfer endpoints.

## Risks
Stream creation depends on the remote side accepting the init handshake. EOF handling is special-cased, but other transport errors must be normalized correctly. A missing acknowledgement prevents stream use.

## Test Signals
No direct tests in this file; transfer streaming fuzz tests and proxy transfer paths exercise the stream abstraction indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/streaming/proxy/streaming.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/streaming/streaming.go -->
# sources/cloud-native/containerd/core/streaming/streaming.go

## Purpose
This file declares the core streaming interfaces used by transfer and proxy subsystems.

## Important APIs, Types, and Functions
`Stream` is a bidirectional object stream carrying `typeurl.Any` values with `Send`, `Recv`, and `Close`. `StreamGetter` retrieves streams by ID, `StreamCreator` creates them, and `StreamManager` combines retrieval with `Register`.

## Control Flow
There is no implementation. The interfaces define how higher-level packages can exchange typed messages and byte-stream protocol frames without depending on a concrete transport.

## State and Persistence
No state is stored here. Implementations decide stream lifetime and buffering.

## Dependencies and Integration Points
The package depends only on `context` and `typeurl`. It is implemented by local managers and proxy clients and consumed by transfer archive, registry, and progress streaming code.

## Risks
The interface has no backpressure or cancellation semantics beyond implementation behavior and `Close`; callers must layer flow control where needed.

## Test Signals
Concrete behavior is covered in transfer streaming tests and proxy integration paths rather than this definition file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/streaming/streaming.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/archive/exporter.go -->
# sources/cloud-native/containerd/core/transfer/archive/exporter.go

## Purpose
This file implements an image archive export transfer endpoint backed by a tar writer and serializable over transfer streams.

## Important APIs, Types, and Functions
`ImageExportStream` implements `transfer.ImageExporter` and `transfer.ImageExportStreamer`. Options select platforms, all-platform export, Docker compatibility manifest skipping, and non-distributable blob skipping. `Export` calls `images/archive.Export`. `MarshalAny` and `UnmarshalAny` bridge local writers to remote stream IDs.

## Control Flow
`Export` builds archive options from configured images and platform policy, then writes an OCI/Docker archive to `iis.stream`. `MarshalAny` creates a stream ID, starts a goroutine copying bytes received from the remote stream into the local writer, and marshals the protobuf endpoint. `UnmarshalAny` retrieves the stream and wraps it with `WriteByteStream`.

## State and Persistence
Persistent effects are archive bytes written to the provided writer. The endpoint itself stores writer, media type, platform selectors, and export flags.

## Dependencies and Integration Points
Integrates `core/images/archive`, `core/transfer/plugins`, `core/transfer/streaming`, `core/streaming`, `typeurl`, and transfer protobuf types.

## Risks
The copy goroutine must close the local writer; errors are only logged. Platform defaults select `platforms.DefaultStrict` unless all-platform or explicit platforms are set, so callers must opt into multi-platform export.

## Test Signals
Covered indirectly by transfer import/export and stream roundtrip tests; no file-local unit test.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/archive/exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/archive/importer.go -->
# sources/cloud-native/containerd/core/transfer/archive/importer.go

## Purpose
This file implements an image archive import endpoint backed by a tar reader and serializable over transfer streams.

## Important APIs, Types, and Functions
`ImageImportStream` implements `transfer.ImageImporter` and `transfer.ImageImportStreamer`. `WithForceCompression` requests import compression. `Import` imports an archive index into a content store. `MarshalAny` sends the reader over a stream; `UnmarshalAny` receives it.

## Control Flow
`Import` optionally decompresses the input when media type is empty, applies compression import options, and calls `archive.ImportIndex`. For proxying, `MarshalAny` creates a stream and starts `SendStream`; `UnmarshalAny` resolves the stream and exposes `ReceiveStream` as the input reader.

## State and Persistence
Persistent effects are blobs and an import index written into the content store. Runtime state includes stream reader, media type, and compression flag.

## Dependencies and Integration Points
Uses image archive import, transfer streaming, compression detection, `typeurl`, and transfer protobuf registration from the paired exporter file.

## Risks
Compression handling depends on empty media type; callers providing an incorrect non-empty type can bypass decompression. Stream send errors are logged inside the streaming layer and not always returned synchronously to `MarshalAny`.

## Test Signals
Import behavior is exercised through local transfer import paths and streaming tests indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/archive/importer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/image/imagestore.go -->
# sources/cloud-native/containerd/core/transfer/image/imagestore.go

## Purpose
This file implements a local image store endpoint that can act as image source, destination, lookup target, platform filter, unpack request carrier, and transfer-proxy serializable object.

## Important APIs, Types, and Functions
`Store` holds image name, labels, platform filters, all-metadata mode, manifest limit, extra references, and unpack requests. Options include `WithImageLabels`, `WithPlatforms`, `WithManifestLimit`, `WithAllMetadata`, `WithNamedPrefix`, `WithDigestRef`, `WithExtraReference`, and `WithUnpack`. `Store`, `Get`, `Lookup`, `ImageFilter`, `Platforms`, `UnpackPlatforms`, `MarshalAny`, and `UnmarshalAny` implement transfer interfaces.

## Control Flow
`ImageFilter` wraps a child handler with platform filtering, mapped labels, all-metadata behavior, and manifest limits. `Store` resolves image records from explicit names or import annotations, creates digest and prefix-derived references, applies GC back-reference labels to extra refs when a primary image exists, then create-or-update loops in the image store. `Lookup` retrieves explicit references only. Marshal/unmarshal converts references, platforms, labels, and unpack configs to protobuf.

## State and Persistence
Persistent state is `images.Image` records in `images.Store`. Extra references may include `containerd.io/gc.bref.image` and immediate `containerd.io/gc.expire` labels so they are tied to the primary image.

## Dependencies and Integration Points
Integrates `core/images`, `core/images/archive` reference helpers, `remotes` filtering, `transfer/plugins`, `core/streaming`, protobuf transfer types, and OCI platform conversion.

## Risks
Reference derivation is subtle: annotation refs, containerd refs, OCI tag-only refs, digest refs, overwrite permission, and skip-named-digest have distinct behavior. `Store` mutates descriptor annotations by deleting the import ref-source marker. Prefix lookup for export is intentionally unimplemented.

## Test Signals
`imagestore_test.go` has table coverage for prefix, overwrite, tag-only, digest, skip digest, missing refs, no annotation, extra refs, GC labels, update-on-existing, and lookup behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/image/imagestore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/image/imagestore_test.go -->
# sources/cloud-native/containerd/core/transfer/image/imagestore_test.go

## Purpose
This file unit-tests `transfer/image.Store` reference resolution, GC labeling, and lookup behavior with an in-memory image store.

## Important APIs, Types, and Functions
`TestStore` drives a large table of reference scenarios. `TestLookup` validates direct lookup cases. `simpleImageStore` implements `images.Store` with a mutex-protected map and basic create/update/delete/get/list behavior.

## Control Flow
For each case, the test builds descriptors with containerd, OCI, generic import annotation, or no annotation. It calls `Store`, checks expected image names and digest targets, and verifies GC labels for primary versus extra references. Lookup tests prepopulate the simple store and compare sorted image names.

## State and Persistence
All persistence is in memory. The tests specifically validate labels that influence real GC persistence semantics in production stores.

## Dependencies and Integration Points
Uses `errdefs`, OCI descriptors, `go-digest`, and `core/images` annotations. It mirrors behavior relied on by archive imports and transfer local import/store paths.

## Risks
The in-memory store ignores filters and field paths, so it verifies reference logic rather than backend-specific store semantics. Time-sensitive GC expire labels are only checked for RFC3339 parsing, not exact value.

## Test Signals
Strong coverage exists for `WithNamedPrefix`, `WithDigestRef`, `SkipNamedDigest`, explicit extra references, missing references returning `ErrNotFound`, unsupported prefix export lookup returning `ErrNotImplemented`, and extra-reference GC label attachment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/image/imagestore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/export.go -->
# sources/cloud-native/containerd/core/transfer/local/export.go

## Purpose
This file implements local transfer from an image getter or lookup source to an image archive/exporter destination.

## Important APIs, Types, and Functions
`localTransferService.exportStream` accepts `transfer.ImageGetter`, `transfer.ImageExporter`, and transfer options.

## Control Flow
The method ensures a lease exists, emits progress start, obtains one or more images through `ImageLookup` or `Get`, calls `Export` with the service content store, then emits completion progress.

## State and Persistence
The method reads image records from `ts.images` and content blobs from `ts.content`; it writes exported bytes through the destination. A temporary lease protects resources during export when no lease is already present.

## Dependencies and Integration Points
Integrates transfer interfaces, local service lease handling, content store, and image store. Archive exporter is a common destination.

## Risks
If `ImageLookup` returns multiple images, destination export must handle the full set. Lease deletion is deferred, so destination errors still trigger cleanup.

## Test Signals
Covered through higher-level transfer/export integration; no file-local unit test.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/import.go -->
# sources/cloud-native/containerd/core/transfer/local/import.go

## Purpose
This file implements local transfer from an image archive/importer into content, image store records, and optional snapshots.

## Important APIs, Types, and Functions
`localTransferService.importStream` calls `ImageImporter.Import`, walks the imported index, stores top-level and child image references, applies optional filters, and optionally creates an `unpack.Unpacker`. `mergeMap` combines descriptor annotations.

## Control Flow
After lease setup and progress emission, import writes blobs and returns an index descriptor. The handler saves the index and, for the top-level index, reads and annotates manifests with `io.containerd.import.ref-source=annotation` before walking children. If the destination supports unpack, matched unpack configs are converted to `unpack.WithUnpackPlatform`. The image graph is walked with `images.WalkNotEmpty`, unpack completion is awaited, and each collected descriptor is stored as images.

## State and Persistence
Persistent effects include content blobs, image records, and optional snapshots. The temporary lease protects imported content during processing. Descriptor annotations guide image-name persistence.

## Dependencies and Integration Points
Uses `content.ReadBlob`, `images.Children`, `images.WalkNotEmpty`, transfer filtering/storing/unpack interfaces, `unpack.NewUnpacker`, and local supported platform matching.

## Risks
Import assumes the top-level descriptor is an OCI index JSON. Unsupported unpack configs are silently skipped through matching. Errors during walk require waiting for unpacker cleanup. `ErrNotFound` from image storage is logged and ignored, allowing descriptors without names.

## Test Signals
Indirectly covered by transfer import/export tests and image store tests for annotation-derived names.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/progress.go -->
# sources/cloud-native/containerd/core/transfer/local/progress.go

## Purpose
This file implements progress aggregation for local pull, push, and unpack operations.

## Important APIs, Types, and Functions
`ProgressTracker` tracks descriptors, parent relationships, extraction progress, and shutdown. `NewProgressTracker`, `HandleProgress`, `Add`, `MarkExists`, `AddChildren`, `ExtractProgress`, and `Wait` are the primary API. `StatusTracker` abstracts content or push status, and `NewContentStatusTracker` adapts `content.Store`.

## Control Flow
`HandleProgress` runs a goroutine loop receiving added descriptors, extraction updates, periodic ticks, and context cancellation. It polls active jobs, emits `waiting`, transfer-state, `already exists`, `complete`, `extracting`, and `extracted` events with descriptor metadata and parent refs.

## State and Persistence
Progress state is in-memory maps and channels. It reads content ingest statuses and content existence but does not persist data itself.

## Dependencies and Integration Points
Used by local pull fetch handlers, push wrappers, and unpack apply options. It depends on `content.Status`, `remotes.MakeRefKey`, OCI descriptors, `go-digest`, and transfer progress callbacks.

## Risks
Parent mappings may be incomplete if children are added before parent metadata. `Wait` uses a timeout to avoid hanging, so late progress goroutines can be cut short. Channel buffers are small and rely on nonblocking sends after closure.

## Test Signals
No direct tests; pull, push, and concurrent unpack integration provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/pull.go -->
# sources/cloud-native/containerd/core/transfer/local/pull.go

## Purpose
This file implements local image pull from a remote image fetcher into content, image records, and optional snapshots.

## Important APIs, Types, and Functions
`localTransferService.pull` coordinates resolve, verify, fetch, filter, unpack, schema conversion, and store. `fetchHandler` fetches each descriptor. `getSupportedPlatform` matches requested unpack configurations to service-supported snapshotter/platform combinations.

## Control Flow
The pull sets resolver options for concurrency, resolves the image, rejects Docker schema 1, runs configured verifiers, obtains a fetcher, builds handlers for progress, content fetch, media-type bug detection, children, and distribution-source labels, optionally wraps with an unpacker, dispatches the descriptor graph, waits for unpack, converts Docker manifests affected by the legacy media-type bug, then stores image records and emits progress.

## State and Persistence
Persistent effects are fetched content, distribution labels, unpacked snapshots, uncompressed labels from unpack, and image store records. A lease protects in-flight content. Progress uses content status polling.

## Dependencies and Integration Points
Integrates remotes/docker resolver/fetcher, image verifier plugins, image filters, local transfer config, unpack package, diff progress, snapshotter remote annotations, defaults, and transfer progress callbacks.

## Risks
Descriptor graph order affects progress parent tracking. Unpack is asynchronous and must always be waited on before storing the image. Schema 1 is rejected. Platform/snapshotter matching prefers default snapshotter when requested snapshotter is empty, which may surprise configurations with multiple matches.

## Test Signals
`pull_test.go` directly covers `getSupportedPlatform`. Integration client tests cover pull, selected platforms, all platforms, discard content after unpack, concurrency limit, tracing, and concurrent unpacks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/pull_test.go -->
# sources/cloud-native/containerd/core/transfer/local/pull_test.go

## Purpose
This file unit-tests platform and snapshotter matching for pull-time unpack selection.

## Important APIs, Types, and Functions
`TestGetSupportedPlatform` builds supported `unpack.Platform` entries and checks `getSupportedPlatform` results for exact platform/snapshotter, no-match, and default snapshotter fallback cases.

## Control Flow
Each table case calls `getSupportedPlatform`, asserts the boolean match, verifies nil platform behavior on no match, and checks snapshotter and matcher compatibility on match.

## State and Persistence
No persistence. Inputs are in-memory platform matchers and unpack configurations.

## Dependencies and Integration Points
Uses `platforms`, `transfer.UnpackConfiguration`, `unpack.Platform`, and `defaults.DefaultSnapshotter`. The behavior feeds `pull.go` and `import.go` unpack decisions.

## Risks
The test set covers representative Linux/default cases but not multiple non-default snapshotter ordering beyond fallback preference.

## Test Signals
Confirms exact snapshotter match, default fallback, platform mismatch rejection, and nil platform on failed match.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/pull_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/push.go -->
# sources/cloud-native/containerd/core/transfer/local/push.go

## Purpose
This file implements local image push from an image store source to a remote pusher, with optional upload progress.

## Important APIs, Types, and Functions
`localTransferService.push` drives image lookup and `remotes.PushContent`. `progressPusher` wraps a remote pusher and tracks upload status. `pushStatus` implements active status and content check. `progressWriter` updates offsets and marks completion.

## Control Flow
Push chooses a platform matcher from `ImagePlatformsGetter`, gets the image, creates a remote pusher, optionally wraps it with a progress tracker, and calls `remotes.PushContent` with upload limiter and handler wrapper. The wrapper adds descriptors and child relationships to progress. Writer commits mark content complete and handle already-exists progress.

## State and Persistence
The method reads local image/content and writes to the remote registry. In-memory maps track active refs and completed digests for progress.

## Dependencies and Integration Points
Uses transfer image getter/pusher interfaces, `remotes.PushContent`, `content.Ingester`, platform matchers, semaphore limiter, and local progress tracking.

## Risks
Progress status must remain consistent across already-existing pushes, commit failures, and content writers opened through either `content.Ingester` or remote `Pusher`. Push is sensitive to platform matcher configuration.

## Test Signals
Indirect coverage comes from push integration paths; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/tag.go -->
# sources/cloud-native/containerd/core/transfer/local/tag.go

## Purpose
This file implements a local image-to-image-store transfer used for tagging or copying image references.

## Important APIs, Types, and Functions
`localTransferService.tag` accepts an `ImageGetter` source and `ImageStorer` destination.

## Control Flow
The method ensures a lease, retrieves the source image from `ts.images`, then stores the same target descriptor through the destination image storer.

## State and Persistence
It reads an existing image record and creates or updates destination image records. The content itself is not copied.

## Dependencies and Integration Points
Uses transfer getter/storer interfaces and local lease handling. Typically the destination is `transfer/image.Store`.

## Risks
The destination controls the final name and labels; this method does not validate content availability beyond the existing source image target.

## Test Signals
Indirectly covered by client image/tag workflows outside this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/tag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/transfer.go -->
# sources/cloud-native/containerd/core/transfer/local/transfer.go

## Purpose
This file defines the concrete local transfer service and dispatch matrix for source/destination combinations.

## Important APIs, Types, and Functions
`localTransferService` holds content store, image store, upload/download/unpack limiters, and `TransferConfig`. `NewTransferService` constructs it. `Transfer` dispatches pull, push, export, tag, echo, and import. `withLease` creates a default 24-hour lease if none is already on the context. `TransferConfig` carries leases, concurrency limits, duplication suppression, base handlers, unpack platforms, verifiers, and registry config path.

## Control Flow
`Transfer` applies transfer options, type-switches on source and destination interfaces, and calls the operation-specific method. Unsupported matrices return `ErrNotImplemented` with stringified endpoint names.

## State and Persistence
Service state is references to stores and config. `withLease` persists temporary leases through the configured lease manager and deletes them on operation completion.

## Dependencies and Integration Points
This is the hub for `core/transfer` contracts, content/images/leases, `unpack`, image verifier, and semaphore limiters. It is likely instantiated by transfer plugins.

## Risks
Dispatch relies on interface implementation, so an endpoint implementing multiple interfaces can change route selection. Lease deletion errors are returned by deferred cleanup only in operation methods that check them explicitly; this file provides the cleanup function.

## Test Signals
Covered indirectly by transfer operation tests and integration pull/import/export workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/local/transfer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/plugins/plugins.go -->
# sources/cloud-native/containerd/core/transfer/plugins/plugins.go

## Purpose
This file provides a process-local registry mapping API protobuf type URLs to concrete transfer endpoint Go types.

## Important APIs, Types, and Functions
`Register` records the type URL of an API object and the reflect type of a transfer object. `ResolveType` constructs a new registered concrete value for a received `typeurl.Any`.

## Control Flow
Endpoint packages call `Register` in `init`. Transfer proxy/server code can later inspect an incoming type URL and instantiate the matching object before unmarshalling it.

## State and Persistence
State is an in-memory global map guarded by an RW mutex. Duplicate registration and invalid type URL generation panic.

## Dependencies and Integration Points
Uses `typeurl`, `reflect`, `sync`, and `errdefs`. Archive, image store, and registry endpoints register here.

## Risks
Registration is global and panic-based for duplicates, so package initialization order and duplicate imports matter. Unknown type URLs return `ErrNotFound`.

## Test Signals
No direct tests in this file; exercised by proxy transfer marshaling/unmarshaling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/plugins/plugins.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/proxy/transfer.go -->
# sources/cloud-native/containerd/core/transfer/proxy/transfer.go

## Purpose
This file implements a client-side transfer proxy that forwards transfer requests over gRPC or TTRPC and bridges progress streams back to local callbacks.

## Important APIs, Types, and Functions
`NewTransferrer` adapts generated clients, client connections, TTRPC clients, or existing transfer services. `proxyTransferrer.Transfer` marshals source and destination endpoints and sends `TransferRequest`. `marshalAny` delegates to stream-aware marshalers when available.

## Control Flow
Transfer options are converted to API options. If progress is requested, a stream is created and a goroutine receives transfer progress protobufs, converts descriptors back to OCI form, and calls the local progress callback. Source and destination are marshaled, wrapped in protobuf `Any`, and sent to the remote transfer service.

## State and Persistence
No durable state. Runtime state includes the transfer client, stream creator, and active progress goroutine.

## Dependencies and Integration Points
Integrates transfer API, streaming interfaces, transfer streaming ID generation, `typeurl`, gRPC/TTRPC adapters, errgrpc normalization, and OCI descriptor conversion.

## Risks
Progress goroutine logs unmarshalling/receive issues but does not fail the transfer. Endpoint marshaling requires all endpoint types to be registered or natively marshalable. Transport error conversion must preserve containerd errdefs semantics.

## Test Signals
Indirectly covered by client transfer API integration and stream tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/proxy/transfer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/registry/registry.go -->
# sources/cloud-native/containerd/core/transfer/registry/registry.go

## Purpose
This file implements an OCI registry transfer endpoint that can resolve, fetch, push, provide credentials, configure hosts, and serialize itself for proxy transfer.

## Important APIs, Types, and Functions
Options configure headers, credentials, hosts directory, default scheme, HTTP debug/trace, and client log stream. `NewOCIRegistry` builds a Docker resolver. `OCIRegistry` implements `ImageFetcher`, `ImagePusher`, `ImageResolverOptionSetter`, string/image helpers, and stream-aware marshal/unmarshal. `credCallback` implements remote credential requests over a stream.

## Control Flow
Creation builds `config.HostOptions`, including credential callbacks and HTTP debug hooks, then creates a Docker resolver. Pull uses `Resolve` and `Fetcher`; push uses `Pusher`, appending the descriptor digest to tag-only refs. `MarshalAny` serializes headers and config, opens auth/log streams when needed, and serves credential requests in a goroutine. `UnmarshalAny` reconstructs host options, installs a streamed credential callback, and configures debug output.

## State and Persistence
State is in-memory registry configuration, resolver, optional stream handles, and credentials helper. It does not persist registry data locally.

## Dependencies and Integration Points
Uses containerd remotes/docker resolver, registry host config, transfer plugins, streaming byte streams, HTTP debugging, transfer protobuf types, and transfer local pull/push.

## Risks
Credential callbacks use `context.Background` in resolver host options and serialize requests with a mutex. HTTP debug log streaming requires closing writers on context cancellation. Header map conversion keeps only `Header.Get` values, not all repeated values.

## Test Signals
Indirectly exercised by pull/push integration, proxy transfer, and credentialed registry tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/registry/registry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/streaming/reader.go -->
# sources/cloud-native/containerd/core/transfer/streaming/reader.go

## Purpose
This file adapts a containerd object stream into an `io.ReadCloser` with explicit window-based flow control.

## Important APIs, Types, and Functions
`ReadByteStream` returns a `readByteStream`. `readByteStream.Read` receives `Data` messages and buffers overflow bytes. `Close` closes the underlying stream.

## Control Flow
A goroutine sends `WindowUpdate` messages until the local receive window reaches `windowSize`, then waits for reads to consume window. `Read` first drains `remaining`, checks context/error channels, receives a message, unmarshals it, copies data into the caller buffer, decreases window, and signals for another update when below threshold.

## State and Persistence
State is per-stream memory: window credit, buffered remaining bytes, update/error channels, and context.

## Dependencies and Integration Points
Consumes `core/streaming.Stream`, transfer protobuf `Data` and `WindowUpdate`, and `typeurl`. It is a lower-level helper for transfer stream endpoints.

## Risks
The window sender may block writing `errCh` if no reader consumes errors. Unknown message types return errors. Remaining-byte handling must preserve data when caller buffers are smaller than frames.

## Test Signals
Streaming fuzz tests cover byte roundtrips and edge cases through related send/receive helpers; direct `ReadByteStream` coverage is limited.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/streaming/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/streaming/stream.go -->
# sources/cloud-native/containerd/core/transfer/streaming/stream.go

## Purpose
This file implements byte transfer over `streaming.Stream` using `Data` frames and window updates.

## Important APIs, Types, and Functions
Constants `maxRead` and `windowSize` define frame and credit sizes. `SendStream` reads from an `io.Reader` and sends data subject to remote credit. `ReceiveStream` returns an `io.Reader` backed by an `io.Pipe`. `GenerateID` creates stream IDs.

## Control Flow
`SendStream` starts one goroutine to receive `WindowUpdate` messages and another to read chunks and send `Data`. It honors credit and closes the stream at EOF. `ReceiveStream` periodically sends window updates, receives data frames, writes them into a pipe, and closes the pipe on EOF or error.

## State and Persistence
All state is transient: pooled buffers, window credit, pipes, and stream IDs. No durable storage.

## Dependencies and Integration Points
Used by archive import/export, registry debug logs, and transfer proxy progress/byte streaming. Depends on transfer protobuf types, typeurl, logging, crypto random, and `core/streaming`.

## Risks
Several TODOs note lack of explicit remote error messages. Read errors other than EOF are logged and end the stream. `GenerateID` ignores random read errors and uses nanosecond plus three random bytes, sufficient for low collision risk but not a durable identifier.

## Test Signals
`stream_test.go` fuzzes send/receive, chained streams, writer path, and EOF-with-data behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/streaming/stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/streaming/stream_test.go -->
# sources/cloud-native/containerd/core/transfer/streaming/stream_test.go

## Purpose
This file fuzz-tests transfer byte streaming correctness across send, receive, chained stream, writer, and EOF edge cases.

## Important APIs, Types, and Functions
`FuzzSendAndReceive` seeds representative byte slices. Helpers run send/receive, chained streams, and `WriteByteStream`. `TestSendReceiveEOFWithData` covers the `io.Reader` contract where a final read returns data and `io.EOF`. `pipeStream` and `testStream` implement an in-memory bidirectional stream.

## Control Flow
Each fuzz run copies expected bytes into a stream-backed writer/reader setup, reads all output, and compares byte equality. Chained tests route bytes through three stream conversions.

## State and Persistence
No persistence. In-memory channels simulate stream send/recv and closure.

## Dependencies and Integration Points
Exercises `SendStream`, `ReceiveStream`, `WriteByteStream`, `windowSize`, and `core/streaming.Stream` behavior.

## Risks
The in-memory stream is simpler than gRPC/TTRPC streams and may not expose transport buffering or cancellation races. Fuzzing still provides strong byte-preservation coverage.

## Test Signals
Strong signal for empty input, single byte, over-window data, repeated data, chained transfer, writer transfer, and EOF-with-data preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/streaming/stream_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/streaming/writer.go -->
# sources/cloud-native/containerd/core/transfer/streaming/writer.go

## Purpose
This file adapts a containerd object stream into an `io.WriteCloser` with window-based backpressure.

## Important APIs, Types, and Functions
`WriteByteStream` returns a `writeByteStream`. `writeByteStream.Write` sends `Data` messages while consuming atomic window credit. `Close` closes the stream.

## Control Flow
A goroutine receives `WindowUpdate` messages and increments remaining credit. `Write` waits for credit, slices input into at most `maxRead` and available-credit chunks, marshals each chunk, sends it, and decrements credit.

## State and Persistence
State is transient atomic credit, update channel, context, and stream reference.

## Dependencies and Integration Points
Used by archive export unmarshal and registry debug-log streaming. Depends on transfer protobuf types, typeurl, logging, and `core/streaming`.

## Risks
Context cancellation during a blocked write returns `io.ErrShortWrite`. Send errors end the write. The receiver goroutine logs unexpected message types and continues, so protocol misuse may not fail immediately.

## Test Signals
`runWriterFuzz` in `stream_test.go` validates byte preservation through this writer path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/streaming/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/transfer.go -->
# sources/cloud-native/containerd/core/transfer/transfer.go

## Purpose
This file defines the core transfer abstraction and endpoint interfaces used across local and proxy transfer implementations.

## Important APIs, Types, and Functions
`Transferrer` exposes `Transfer`. Source/destination contracts include resolver/fetcher/pusher, image filter/store/get/lookup, importer/exporter, stream import/export, unpacker, and platform getter interfaces. Options include progress, download limiter, max concurrent downloads, and concurrent layer fetch buffer. `Progress` is the common progress event shape.

## Control Flow
There is no implementation; concrete services use these interfaces as a dispatch matrix. Option functions mutate simple config structs.

## State and Persistence
No persistence. The interfaces describe which implementations may read/write content, images, remote registries, streams, and snapshots.

## Dependencies and Integration Points
This package connects content store writers, image store records, OCI descriptors/platforms, `images.HandlerFunc`, and `semaphore.Weighted`. Local transfer and proxy transfer are primary consumers.

## Risks
Because routing is interface-based, endpoint types implementing multiple contracts can be dispatched differently depending on source/destination combinations. Progress event names are convention-based rather than typed enums.

## Test Signals
Covered through tests of concrete local, image, registry, streaming, and integration client behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/transfer/transfer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/unpack/unpacker.go -->
# sources/cloud-native/containerd/core/unpack/unpacker.go

## Purpose
This file implements asynchronous image layer unpacking integrated into image descriptor walking.

## Important APIs, Types, and Functions
`Platform` describes platform matcher, snapshotter, applier, snapshot options, capabilities, config type, and layer types. `Unpacker` wraps an image handler with `Unpack` and is finalized with `Wait`. Options set platforms, fetch limiter, duplication suppressor, and unpack limiter. Internal helpers lock descriptors/chain IDs, fetch layers, apply diffs, and convert bind mounts to overlay mounts for parallel overlayfs.

## Control Flow
`Unpack` intercepts manifests, separates layers from configs, and starts `unpack` when a matching config is handled. `unpack` reads config, validates diff IDs, chooses a platform, precomputes chain IDs, prepares snapshots, starts or coordinates layer fetch, applies layer diffs, verifies diff IDs, commits snapshots, records uncompressed labels, and updates config GC refs. Sequential mode commits layer-by-layer; parallel mode applies layers concurrently but commits/rebases in order.

## State and Persistence
Persistent effects include prepared/committed snapshots with labels for snapshot ref, parent chain ID, diff ID, and inherited labels; content labels for uncompressed diff IDs; and config labels referencing the final snapshot. Temporary snapshots are removed on abort.

## Dependencies and Integration Points
Integrates content store, diff appliers, image handlers, snapshotters, mount types, identity chain IDs, cleanup helpers, keyed mutexes, tracing, and transfer local pull/import.

## Risks
Correctness depends on descriptor graph order, config/layer count matching, snapshot cleanup on every error path, lock release, and ordered commits under parallel unpack. Parallel rebase is enabled only with an unpack limiter and snapshotter `rebase` capability. Overlayfs bind-to-overlay conversion is a temporary workaround.

## Test Signals
`unpacker_test.go` benchmarks chain ID calculation and tests bind-to-overlay conversion. Integration tests cover pull with unpack, discard content after unpack, and concurrent unpack limiter behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/unpack/unpacker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/unpack/unpacker_test.go -->
# sources/cloud-native/containerd/core/unpack/unpacker_test.go

## Purpose
This file benchmarks chain ID calculation strategies and tests overlay mount conversion used by parallel overlayfs unpack.

## Important APIs, Types, and Functions
`generateRandomDiffIDs` creates benchmark inputs. `BenchmarkUnpackWithChainID` simulates repeated `identity.ChainID` calculation. `BenchmarkUnpackWithChainIDs` benchmarks precomputed `identity.ChainIDs`. `TestBindToOverlay` validates `bindToOverlay`.

## Control Flow
Benchmarks run for 5, 10, 25, and 50 layers. The unit test checks single bind mount conversion, overlay passthrough, and multiple-mount passthrough.

## State and Persistence
No persistence; all data is generated in memory.

## Dependencies and Integration Points
Uses `go-digest`, OCI identity helpers, and `core/mount`. The test protects an unpacker workaround needed when parallel overlayfs snapshotters provide bind mounts.

## Risks
Benchmarks are performance signals only and do not enforce thresholds. `bindToOverlay` test does not cover all mount option permutations.

## Test Signals
Confirms precomputed chain IDs are the intended optimization path and that only a single bind mount is rewritten to overlay with `upperdir` and no `rbind`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/unpack/unpacker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults.go -->
# sources/cloud-native/containerd/defaults/defaults.go

## Purpose
This file defines platform-independent default constants for containerd.

## Important APIs, Types, and Functions
Constants include default gRPC send/receive message sizes, namespace label keys for runtime/snapshotter/sandboxer defaults, and `DefaultSandboxer`.

## Control Flow
There is no executable control flow.

## State and Persistence
No state is persisted. Constants guide client/server configuration and namespace-label lookup.

## Dependencies and Integration Points
Used by client startup, integration tests, namespace default selection, and server configuration.

## Risks
Changing label keys or message limits is API/configuration visible and can break existing deployments.

## Test Signals
Integration client tests use default snapshotter/runtime labels and message behavior indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_darwin.go -->
# sources/cloud-native/containerd/defaults/defaults_darwin.go

## Purpose
This Darwin-specific file defines default runtime, socket paths, FIFO path, snapshotter, state directory, and differ.

## Important APIs, Types, and Functions
Constants include `DefaultRuntime`, `DefaultAddress`, `DefaultDebugAddress`, `DefaultFIFODir`, `DefaultSnapshotter`, `DefaultStateDir`, and `DefaultDiffer`.

## Control Flow
No executable flow.

## State and Persistence
Paths point at `/var/run/containerd` transient locations. The default snapshotter/differ are `erofs` because Darwin lacks Linux mount support.

## Dependencies and Integration Points
Used by Darwin builds of clients and daemon defaults.

## Risks
Defaults affect out-of-the-box connectivity and storage behavior on Darwin; snapshotter choice is constrained by platform support.

## Test Signals
No direct tests in subset; platform builds validate symbol availability.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_freebsd.go -->
# sources/cloud-native/containerd/defaults/defaults_freebsd.go

## Purpose
This FreeBSD-specific file defines the default runtime.

## Important APIs, Types, and Functions
`DefaultRuntime` is set to `wtf.sbk.runj.v1`.

## Control Flow
No executable flow.

## State and Persistence
No state; this is a compile-time constant.

## Dependencies and Integration Points
Combined with Unix non-Linux defaults for addresses, state, root, config, snapshotter, and differ.

## Risks
Changing the runtime affects all FreeBSD default container launches.

## Test Signals
Build coverage on FreeBSD validates this constant composes with other defaults.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_linux.go -->
# sources/cloud-native/containerd/defaults/defaults_linux.go

## Purpose
This Linux-specific file defines default socket paths, runtime, snapshotter, state directory, FIFO directory, and differ.

## Important APIs, Types, and Functions
Defaults include `/run/containerd/containerd.sock`, `/run/containerd/debug.sock`, `/run/containerd/fifo`, runtime `io.containerd.runc.v2`, snapshotter `overlayfs`, state dir `/run/containerd`, and differ `walking`.

## Control Flow
No executable flow.

## State and Persistence
The state directory is transient under `/run`; persistent root/config come from Unix defaults. Snapshotter default influences persisted snapshot metadata and unpack behavior.

## Dependencies and Integration Points
Used by Linux clients, integration tests, pull unpack matching, and daemon configuration.

## Risks
Changing defaults is deployment-visible. `DefaultSnapshotter` is used by transfer unpack matching when no snapshotter is requested.

## Test Signals
Integration client `TestMain` uses this default unless `TEST_SNAPSHOTTER` overrides it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_unix.go -->
# sources/cloud-native/containerd/defaults/defaults_unix.go

## Purpose
This Unix build-tagged file defines shared filesystem defaults for Unix-like systems.

## Important APIs, Types, and Functions
`DefaultConfigDir`, `DefaultRootDir`, and `DefaultConfigIncludePattern` point to `/etc/containerd`, `/var/lib/containerd`, and `/etc/containerd/conf.d/*.toml`.

## Control Flow
No executable flow.

## State and Persistence
`DefaultRootDir` is the persistent data root; config paths define daemon configuration discovery.

## Dependencies and Integration Points
Composes with Linux, Darwin, FreeBSD, and other Unix defaults.

## Risks
Path changes affect package layouts, daemon startup, and upgrade compatibility.

## Test Signals
Build and integration tests rely on these defaults unless explicit test roots are passed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_unix_other.go -->
# sources/cloud-native/containerd/defaults/defaults_unix_other.go

## Purpose
This file provides defaults for Unix platforms other than Linux and Darwin.

## Important APIs, Types, and Functions
Constants define default socket/debug/FIFO paths under `/var/run/containerd`, default snapshotter `native`, transient state dir `/var/run/containerd`, and differ `walking`.

## Control Flow
No executable flow.

## State and Persistence
State is transient under `/var/run`; persistent root/config come from shared Unix defaults.

## Dependencies and Integration Points
Build tag `unix && !linux && !darwin` combines with platform-specific runtime constants such as FreeBSD.

## Risks
`native` snapshotter is conservative but may differ in performance and semantics from overlay/erofs defaults.

## Test Signals
Platform build coverage validates symbol composition.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_unix_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_windows.go -->
# sources/cloud-native/containerd/defaults/defaults_windows.go

## Purpose
This Windows-specific file defines containerd defaults for paths, named pipes, runtime, snapshotter, differ, and FIFO behavior.

## Important APIs, Types, and Functions
Variables derive `DefaultRootDir`, `DefaultStateDir`, `DefaultConfigDir`, and `DefaultConfigIncludePattern` from `ProgramData` and `programfiles`. Constants include named-pipe addresses, differ `windows`, empty FIFO dir, runtime `io.containerd.runhcs.v1`, and snapshotter `windows`.

## Control Flow
No procedural flow beyond package variable initialization from environment variables.

## State and Persistence
Persistent root/state/config locations are environment-dependent Windows paths. Named pipes define API endpoints.

## Dependencies and Integration Points
Used by Windows clients, daemon defaults, and integration tests.

## Risks
Environment-variable casing matters (`ProgramData` and `programfiles`). Path defaults are evaluated at process start.

## Test Signals
Windows integration client files use Windows-specific defaults and image selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/defaults/defaults_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/defaults/doc.go -->
# sources/cloud-native/containerd/defaults/doc.go

## Purpose
This file supplies the package declaration and documentation anchor for `defaults`.

## Important APIs, Types, and Functions
No APIs beyond package `defaults`.

## Control Flow
No executable flow.

## State and Persistence
No state.

## Dependencies and Integration Points
Allows Go documentation tooling to describe the package even when defaults are split across build-tagged files.

## Risks
Minimal; incorrect docs could mislead package users but no runtime behavior exists.

## Test Signals
Build-only signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/defaults/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/docs/user-namespaces/config.json -->
# sources/cloud-native/containerd/docs/user-namespaces/config.json

## Purpose
This JSON file is an OCI runtime configuration fixture/documentation example for running a container with a user namespace.

## Important APIs, Types, and Functions
Key fields include `ociVersion`, process settings, root path, hostname, standard mounts, Linux UID/GID mappings, device deny resources, namespace list including `user`, masked paths, and readonly paths.

## Control Flow
No executable flow. The runtime would interpret this as an OCI spec.

## State and Persistence
The spec references `/tmp/userns-test/rootfs` as rootfs and maps container ID 0 to host ID 65536 for both UID and GID over size 65536.

## Dependencies and Integration Points
Used by user-namespace documentation or manual runtime testing. It follows OCI runtime-spec shape and Linux namespace/mount conventions.

## Risks
It is a static example: host subuid/subgid availability, rootfs existence, cgroup version, and runtime support must match the environment. Formatting has unusual indentation but valid JSON.

## Test Signals
No direct automated tests in this subset; serves as a configuration example.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/docs/user-namespaces/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/addition_gids_test.go -->
# sources/cloud-native/containerd/integration/addition_gids_test.go

## Purpose
This Linux integration test validates CRI supplemental group handling against container-visible `id` output.

## Important APIs, Types, and Functions
`TestAdditionalGids` defines cases using `WithSupplementalGroups`, `WithRunAsUser`, `WithRunAsGroup`, and `WithRunAsUsername`. It uses `PodSandboxConfigWithCleanup`, `ContainerConfig`, runtime service create/start/status calls, and log inspection.

## Control Flow
The test ensures the BusyBox image exists, creates a sandbox with a log directory, creates a container running `id`, waits until it exits, reads its log file, and checks the expected group list.

## State and Persistence
State is created in CRI sandbox/container services and a temporary pod log directory. Container logs are the assertion source.

## Dependencies and Integration Points
Depends on CRI runtime service helpers, integration images, Kubernetes CRI API types, and Linux build tag.

## Risks
Expected group names depend on image `/etc/group` contents. Timing depends on container exit and log flush. It is Linux-only.

## Test Signals
Covers default groups, supplemental groups, numeric users/groups, username resolution, and combined username plus supplemental group behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/addition_gids_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/build_local_containerd_helper_test.go -->
# sources/cloud-native/containerd/integration/build_local_containerd_helper_test.go

## Purpose
This helper builds an in-process containerd client with core plugins initialized for integration tests.

## Important APIs, Types, and Functions
`buildLocalContainerdClient` loads plugins once, initializes them with per-plugin root/state paths, applies optional plugin tweak functions, and creates a client with in-memory services. `tweakContentInitFnWithDelayer` wraps the content plugin to delay commits. `contentStoreDelayer` and `contentWriterDelayer` implement the delay wrappers.

## Control Flow
Plugins are loaded through the server loader once. Each plugin gets a `plugin.InitContext` with root/state properties and decoded config. The helper adds each initialized plugin to a set, forces instance creation, and passes the last init context to `containerd.WithInMemoryServices`.

## State and Persistence
Test roots and states live under the caller's temp dir. The global `sync.Once` caches loaded plugin registrations. Delayer state wraps content writes and sleeps during commit.

## Dependencies and Integration Points
Imports many plugin packages for registration, server config/loading, content store, CRI constants, platform defaults, and containerd client construction.

## Risks
Plugin initialization order and the use of the last init context are subtle. Tweaking a plugin mutates a registration copy but must preserve original initialization. Commit delay can make tests timing-sensitive.

## Test Signals
Used by local in-memory integration tests to exercise real plugin wiring without a daemon process.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/build_local_containerd_helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/build_local_containerd_helper_test_linux.go -->
# sources/cloud-native/containerd/integration/build_local_containerd_helper_test_linux.go

## Purpose
This Linux-only helper imports additional plugins required for in-memory service initialization.

## Important APIs, Types, and Functions
It has blank imports for image verifier, sandbox, sandbox service, overlay snapshotter, and streaming plugins.

## Control Flow
No runtime flow beyond package initialization side effects from blank imports.

## State and Persistence
Plugin registrations are added to containerd's global plugin registry.

## Dependencies and Integration Points
Complements `build_local_containerd_helper_test.go` for Linux-specific plugin coverage.

## Risks
Missing blank imports can cause `WithInMemoryServices` tests to fail due to absent plugin registrations.

## Test Signals
Build and integration initialization signal only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/build_local_containerd_helper_test_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/benchmark_test.go -->
# sources/cloud-native/containerd/integration/client/benchmark_test.go

## Purpose
This file benchmarks client container creation and task start paths against a running containerd.

## Important APIs, Types, and Functions
`BenchmarkContainerCreate` times `NewContainer` with a pre-generated spec and new snapshots. `BenchmarkContainerStart` pre-creates containers, then times `NewTask` and `Start`.

## Control Flow
Both benchmarks create a client, resolve the test image, generate an OCI spec with `withTrue`, track containers for cleanup, reset timers around the target operation, and stop timers before cleanup.

## State and Persistence
Benchmarks create snapshots, containers, and tasks in the test namespace and clean them with snapshot cleanup.

## Dependencies and Integration Points
Uses the integration client harness, `containerd/client`, OCI spec generation, and test images.

## Risks
Benchmark results depend on daemon state, snapshotter, host performance, and image availability. Cleanup errors are reported after timing.

## Test Signals
Performance-oriented signal for container creation and task start overhead.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client.go -->
# sources/cloud-native/containerd/integration/client/client.go

## Purpose
This file provides shared integration client test globals and helpers.

## Important APIs, Types, and Functions
Constants and variables define `testNamespace`, address flag, stdio path, test snapshotter, and daemon handle. `testContext` creates a namespace-scoped context and optional test logger. `createShimDebugConfig` writes a temporary containerd config enabling runtime v1 shim debug.

## Control Flow
`init` registers the `-address` flag. `testContext` uses `context.WithCancel`, sets namespace, and attaches `logtest` when a test is provided. `createShimDebugConfig` writes TOML and exits the process on failure.

## State and Persistence
The shim debug config is a temp file. Globals are shared across integration tests and initialized by `TestMain` in `client_test.go`.

## Dependencies and Integration Points
Used by all integration client tests, daemon setup, and platform-specific defaults.

## Risks
`createShimDebugConfig` exits directly on file errors. Context creation cannot use `t.Context` yet, as noted by the comment.

## Test Signals
Harness support file; correctness is indicated by the integration suite starting and using the expected namespace/config.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_test.go -->
# sources/cloud-native/containerd/integration/client/client_test.go

## Purpose
This file is the main integration harness and core client behavior test set for containerd.

## Important APIs, Types, and Functions
`TestMain` starts or connects to containerd, configures defaults, pulls a seed image, runs tests, and tears down. `newClient` centralizes client creation. Tests cover new client, image pull, discard-content unpack, all/some platform fetch, download concurrency, tracing, concurrent unpacks, reconnect, namespace default runtime labels, and runtime info.

## Control Flow
`TestMain` parses flags, requires root outside short mode, detects CRIU, starts a daemon unless `-no-daemon`, waits for readiness, logs version, sets namespace default snapshotter, pulls the seed image with unpack, runs the suite, then stops/kills the daemon and removes test root. Individual tests create clients and use `testContext`.

## State and Persistence
The daemon uses `defaultRoot` and `defaultState`; tests create content, images, snapshots, leases, namespace labels, and tracing spans. Cleanup removes test root when the dedicated daemon is used.

## Dependencies and Integration Points
Integrates the real client API, daemon process helper, defaults, images package, leases, content/image stores, namespaces, OpenTelemetry, platform matchers, and semaphore unpack limiter.

## Risks
Requires root, network/image availability, and stable registry behavior. Some tests skip in short mode or CI. The discard-content test depends on synchronous GC and correct snapshot retention.

## Test Signals
High-value end-to-end coverage for pull/fetch/unpack/content GC, tracing spans, reconnect, namespace labels, runtime feature reporting, and concurrency options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_ttrpc_test.go -->
# sources/cloud-native/containerd/integration/client/client_ttrpc_test.go

## Purpose
This file integration-tests the TTRPC client utility against containerd's TTRPC endpoint.

## Important APIs, Types, and Functions
Tests cover `ttrpcutil.NewClient`, `Reconnect`, service retrieval, event forwarding, and close behavior.

## Control Flow
Tests skip in short mode, connect to `address + ".ttrpc"`, reconnect where applicable, forward a test event through the events service, close the client, and assert closed-client behavior returns `ttrpc.ErrClosed`.

## State and Persistence
Only transient client connections and a forwarded event envelope are created.

## Dependencies and Integration Points
Uses TTRPC event service API, protobuf timestamp/Any helpers, namespaces, and the shared integration address.

## Risks
Requires the daemon to expose the TTRPC socket and events service. Event forwarding is used as a liveness check, not as persisted event validation.

## Test Signals
Confirms TTRPC connect, reconnect, service use after reconnect, idempotent close, and expected closed error.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_ttrpc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_unix.go -->
# sources/cloud-native/containerd/integration/client/client_unix.go

## Purpose
This non-Windows file defines default integration-test daemon paths and address.

## Important APIs, Types, and Functions
Constants define `defaultRoot`, `defaultState`, and `defaultAddress` under `/var/lib/containerd-test` and `/run/containerd-test`.

## Control Flow
No executable flow.

## State and Persistence
The integration suite uses these paths for daemon root, state, and socket unless overridden.

## Dependencies and Integration Points
Consumed by `client.go` and `client_test.go`.

## Risks
Tests remove `defaultRoot`; path isolation is critical to avoid deleting real data. Requires privileges to access `/var/lib` and `/run`.

## Test Signals
Harness build/runtime configuration for Unix integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_unix_test.go -->
# sources/cloud-native/containerd/integration/client/client_unix_test.go

## Purpose
This non-Windows integration test file defines Unix test image/command defaults and verifies runtime option mutation during task creation.

## Important APIs, Types, and Functions
Globals choose BusyBox images and short/long commands. `TestNewTaskWithRuntimeOption` uses a `fakeTaskService` to capture `CreateTaskRequest` options. `fakeTaskService` implements minimal task service methods.

## Control Flow
The test creates a client with the fake task service, gets the test image, creates containers with runtime options, starts task creation with optional UID/GID/shim cgroup opts, unmarshals the captured task options, and compares them to expected runc options.

## State and Persistence
Containers and snapshot views are created through client APIs and cleaned up. Captured task requests are stored in a mutex-protected map.

## Dependencies and Integration Points
Uses runc options protobufs, client task creation, OCI image config, plugins runtime ID, typeurl unmarshalling, and protobuf comparison helpers.

## Risks
The fake task service only implements the methods needed for the test and returns not-found for get/delete. The test is specific to runc v2 option semantics.

## Test Signals
Confirms task opts can overwrite runtime option IO UID/GID and shim cgroup while preserving unrelated runtime option fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_windows.go -->
# sources/cloud-native/containerd/integration/client/client_windows.go

## Purpose
This Windows file defines the default integration-test named pipe address.

## Important APIs, Types, and Functions
`defaultAddress` is `\\.\pipe\containerd-containerd-test`.

## Control Flow
No executable flow.

## State and Persistence
No persisted state; the address selects the Windows named pipe endpoint.

## Dependencies and Integration Points
Used by shared client integration flags and setup on Windows.

## Risks
The address must match the daemon under test; named pipe availability is platform-specific.

## Test Signals
Build/configuration signal for Windows integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_windows_test.go -->
# sources/cloud-native/containerd/integration/client/client_windows_test.go

## Purpose
This Windows integration test helper selects test images and platform-specific commands/paths based on host Windows build.

## Important APIs, Types, and Functions
Globals set default root/state under Program Files, test image names, digest image, multilayer image, and short/long commands. `init` maps `osversion.Build()` to Nano Server image tags and panics when no supported image exists.

## Control Flow
At package initialization, the host build is inspected and a compatible image is selected. Newer builds beyond Windows Server 2022 default to `ltsc2022`.

## State and Persistence
Default root and state point into Program Files containerd test directories. Image selection is global process state.

## Dependencies and Integration Points
Uses hcsshim `osversion`, integration images, and shared client tests.

## Risks
Unsupported Windows builds panic during test initialization. Image compatibility is tied to host/container version compatibility rules.

## Test Signals
Provides platform-specific setup for the shared integration suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/client_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_checkpoint_test.go -->
# sources/cloud-native/containerd/integration/client/container_checkpoint_test.go

## Purpose
This Linux integration test file validates checkpoint and restore behavior with CRIU, including PTY, runtime/RW/task checkpoints, image-path checkpointing, leave-running checkpoints, and paused tasks.

## Important APIs, Types, and Functions
Tests include `TestCheckpointRestorePTY`, `TestCheckpointRestore`, `TestCheckpointRestoreNewContainer`, `TestCheckpointLeaveRunning`, `TestCheckpointRestoreWithImagePath`, and `TestCheckpointOnPauseStatus`. They use checkpoint/restore opts such as `WithCheckpointRuntime`, `WithCheckpointRW`, `WithCheckpointTaskExit`, `WithCheckpointTask`, `WithRestoreImage`, `WithRestoreSpec`, `WithRestoreRuntime`, `WithRestoreRW`, `WithCheckpointImagePath`, and `WithRestoreImagePath`.

## Control Flow
Each test skips when CRIU is unavailable, creates a client/container/task, starts a process, checkpoints it, deletes or keeps the task depending on scenario, restores a container/task, starts it, verifies behavior through output/status/process listing, then kills and cleans up.

## State and Persistence
Checkpoint images are persisted as containerd images or filesystem CRIU image directories. RW snapshots, runtime state, specs, and image metadata may be stored and restored. Test containers and snapshots are cleaned up.

## Dependencies and Integration Points
Requires Linux, CRIU, runtime checkpoint support, direct IO helpers, client container/task APIs, OCI spec helpers, `cio`, and Unix signals.

## Risks
Highly environment-sensitive: CRIU version, kernel features, runtime support, PTY handling, and process timing affect results. Cleanup must handle paused/running tasks carefully.

## Test Signals
Strong end-to-end coverage for checkpoint/restore with PTY input/output, task exit behavior, restoring to a new container, preserving running state after checkpoint, image-path dump/restore, and checkpointing while paused.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_checkpoint_test.go -->
