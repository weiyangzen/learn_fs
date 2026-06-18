<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/manager.go -->
# sources/cloud-native/stargz-snapshotter/store/manager.go

## Purpose
Manages lazy layer resolution, caching, prefetch/background fetch, metrics, and reference lifetimes for stargz-store.

## Important APIs, Types, And Functions
- `NewLayerManager` creates a ref pool, background task manager, layer resolver, metrics controller, locks, and maps.
- `getLayerInfo` returns containers/storage-compatible layer metadata.
- `getLayer` resolves all layers in a reference concurrently until the requested TOC digest is cached.
- `resolveLayer` serializes duplicate layer resolution, handles zstd chunked TOC offset annotations, resolves the layer, starts prefetch/background fetch, and caches the layer.
- `use` and `release` maintain refcounts and call `layer.Done` when unused.
- `genLayerInfo` maps layer digest to image config DiffID and TOC digest.

## Control Flow
A layer request loads manifest/config, starts goroutines to resolve each manifest layer with a background context, waits for the desired TOC digest, and returns timeout or all-done errors if missing. Resolution is cached per ref/layer digest to avoid repeated failed work until the ref is fully released.

## State And Persistence
In-memory maps hold layer objects, refcounts, and resolution errors. The ref pool persists manifest/config metadata briefly under `pool`. Metrics are registered unless disabled. Background fetch/prefetch state is owned by layer objects.

## Dependencies And Integration Points
Integrates metadata store, stargz layer resolver, external TOC remote decompressor, zstd chunked annotations, task manager, named mutex, metrics, and registry hosts.

## Risks And Edge Cases
`errChan` is allocated but never written, so resolution failures are observed through timeout or all-done rather than immediate error propagation. Concurrent goroutines use `context.Background`, so client cancellation does not stop resolution. Refcount map deletion includes a suspicious `delete(r.refcounter, tocDigest.String())` against the top-level map.

## Test Signals
Signals should cover cache hits, duplicate resolution locking, prefetch/background fetch toggles, refcount release calling `Done`, manifest/config mismatch errors, missing target TOC timeout/all-done paths, and generated layer info flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/manager.go -->
