# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/handlers.go

## Purpose
Provides generic remotes helper handlers for fetching, pushing, ref-key naming, platform/non-distributable filtering, and distribution-source annotation.

## Important APIs, Types, And Functions
`WithMediaTypeKeyPrefix`, `MakeRefKey`, `FetchHandler`, `Fetch`, `PushHandler`, `PushContent`, `SkipNonDistributableBlobs`, `FilterManifestByPlatformHandler`, and `annotateDistributionSourceHandler`.

## Control Flow
`MakeRefKey` chooses stable content writer refs by descriptor media type, annotation ref name, and optional context prefix. `FetchHandler` downloads descriptors into an ingester, while `Fetch` handles existing writers, inline descriptor data, size-zero rejection, and remote fetch copy. `PushContent` traverses children, records manifests and indexes so children upload before parents, annotates source labels when possible, dispatches pushes with a limiter, and reports missing index dependencies specially. Filtering handlers skip non-distributable blobs or keep only config for non-target platform manifests.

## State And Persistence
Fetch and push write to content stores or remote registries. Context can hold media-type ref prefixes. Source annotations are copied from content labels into descriptor annotations during push traversal.

## Dependencies And Integration Points
Central integration layer between containerd `images.Dispatch`, content stores, the local `Fetcher`/`Pusher` interfaces, platform matchers, Docker source-label helpers, and registry push/fetch implementations.

## Risks And Edge Cases
`Fetch` rejects descriptors reporting size zero, which may reject broken registries before attempting streaming. Push order is managed manually for manifests/indexes to satisfy registry dependency rules. Non-distributable filtering must preserve configs so manifests remain parseable.

## Test Signals
`handlers_test.go` covers custom ref-key prefixes and non-distributable filtering, including child descriptor filtering from a real local content store.
