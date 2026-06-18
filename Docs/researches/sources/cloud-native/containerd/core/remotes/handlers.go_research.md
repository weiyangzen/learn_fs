<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/handlers.go -->
# sources/cloud-native/containerd/core/remotes/handlers.go

## Purpose
Provides generic image remotes handlers for fetching into content stores, pushing from content stores, filtering non-distributable content, platform-aware manifest traversal, distribution-source annotation propagation, and reference-key construction.

## Important APIs, Types, And Functions
- `WithMediaTypeKeyPrefix` adds context-scoped media type to ref-key prefix overrides.
- `MakeRefKey` builds stable content ingest refs from descriptor digest, ref-name annotation, media type classification, and context overrides.
- `FetchHandler` and `Fetch` fetch remote descriptors into a `content.Ingester`.
- `PushHandler`, `push`, and `PushContent` push local content to a `Pusher`.
- `SkipNonDistributableBlobs` filters foreign/non-distributable layers.
- `FilterManifestByPlatformHandler` lets non-target manifests only expose config descriptors.
- `annotateDistributionSourceHandler` and `copyDistributionSourceLabels` propagate distribution-source labels from parent descriptors/content info to children.
- `closeOnEOFReader` and `closeOnEOFReadSeeker` close remote bodies promptly on EOF while preserving seek support.

## Control Flow
Fetch opens a content writer using `MakeRefKey`, rejects zero-size descriptors, commits completed writers, copies inline `desc.Data` when available, otherwise fetches remote data and wraps the reader to close at EOF. Push opens either an ingester writer or pusher writer, obtains a section reader from the content provider, and copies bytes.

`PushContent` traverses an image graph with `images.Dispatch`. It first pushes configs/layers, records manifests and indexes, then pushes manifests and indexes in dependency order so child content exists before parent manifests. If the store can provide content info, distribution-source labels are copied into child annotations for cross-repo mount hints.

## State And Persistence
Fetch writes into a content store through `content.Ingester`; push writes to a remote registry through a pusher. Context stores media-type prefix overrides. `PushContent` keeps transient slices of manifests/indexes guarded by a mutex during dispatch.

## Dependencies And Integration Points
Integrates with `core/content`, `core/images`, `platforms`, `semaphore`, OCI descriptors, Docker pusher/fetcher implementations, and local content label conventions.

## Risks And Edge Cases
Zero-size remote descriptors are rejected because committing an empty entry for missing length would be misleading. Push ordering is critical for registry dependency checks. Non-distributable filtering must apply to both direct child lists and descriptor self-handling. Annotation propagation must not overwrite child annotations.

## Test Signals
`handlers_test.go` covers custom ref-key prefixes and non-distributable filtering against both synthetic child lists and a real local content store. Distribution-source propagation is exercised indirectly by pusher tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/handlers.go -->
