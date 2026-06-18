# sources/cloud-native/buildkit/client/solve_resetcache_test.go

## Purpose
This unit-test source verifies `resetCacheStore`, the local cache cleanup routine in `solve.go` that deletes content-store blobs not reachable from `index.json` manifests.

## Important APIs, Types, and Functions
- `writeBlob` writes deterministic blobs into a containerd content store.
- `listDigests` lists all content-store digests for assertions.
- `setupCacheStore` creates a temporary local content store, writes config/layer/manifest blobs, and inserts the manifest into `index.json` with `ociindex.Tag`.
- `TestResetCacheStoreImageManifest`, `TestResetCacheStoreMultipleTags`, `TestResetCacheStoreNoOrphans`, `TestResetCacheStoreNestedIndex`, and `TestResetCacheStoreDockerMediaTypes` cover reachability shapes.

## Control Flow
Each test creates a local content store, writes referenced blobs and at least one orphan when relevant, writes an OCI index descriptor, calls `resetCacheStore`, and then asserts which digests remain. The nested-index and Docker media type cases ensure traversal uses containerd image children logic instead of a single hard-coded OCI manifest shape.

## State and Persistence Behavior
All state is stored under temporary directories using containerd's local content store and `ociindex` `index.json`. The function under test mutates the content store by deleting orphan blobs. Tests assert both preservation of referenced manifests/configs/layers and removal of orphan blobs.

## Dependencies and Integration Points
The tests depend on containerd content APIs, containerd image child traversal, local content-store implementation, OCI and Docker media type descriptors, and the `ociindex` helper. They are direct coverage for the cache export reset path used when local cache exporter attrs include `reset=true`.

## Risks and Edge Cases
The covered risk is data loss: reachable cache/image blobs must not be removed. The suite includes multiple tags, no-op reset, nested indexes, direct cache config descriptors, and Docker schema2 manifest lists. It does not simulate delete failures or corrupt index data.

## Test Signals
Passing tests show that cache reset is reachability-based rather than tag-count-based or media-type-specific. Failures would threaten local cache exports by either leaking old blobs or deleting current cache records.
