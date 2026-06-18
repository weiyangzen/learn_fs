# sources/cloud-native/buildkit/cache/remotecache/export.go

## Purpose

`remotecache/export.go` defines the generic remote cache exporter contract and the content-addressed exporter used for registry/content backends. It serializes cache chains into OCI index or image-manifest artifacts, uploads layer blobs/config/manifest, and returns the exported manifest descriptor to clients.

## Important APIs, Types, and Functions

- `ResolveCacheExporterFunc` is the resolver signature for cache exporter backends.
- `Exporter` extends `solver.CacheExporterTarget` with `Name`, `Finalize`, and `Config`.
- `Config` carries compression settings.
- `CacheType`, `ExporterResponseManifestDesc`, and `CacheType.String` describe export artifact style.
- `NewExporter` builds a `contentCacheExporter` with v1 cache chains and content ingester.
- `ExportableCache` can hold either an OCI/Docker index or an OCI image manifest.
- `NewExportableCache`, `MediaType`, `AddCacheBlob`, `FinalizeCache`, `SetConfig`, and `MarshalJSON` abstract the artifact shape.
- `contentCacheExporter.Finalize` pushes layers, writes cache config, writes manifest/index, and returns descriptor metadata.
- `withRemoteCacheErrorDetails` enriches unexpected remote status errors.

## Control Flow

`NewExporter` creates a v1 cache chain target. During solver export, cache records are added to that target. `Finalize` marshals chains into a cache config plus descriptor/provider pairs. Empty layer sets produce a warning and skip export. Otherwise, it creates an `ExportableCache`, collects layer descriptors in cache-config order, and uses `images.Dispatch` with a concurrency semaphore to copy all layer blobs from their providers into the ingester.

After layer upload, descriptors are added to the manifest/index in order and media types are converted for OCI or Docker compatibility. The cache config JSON is content-addressed and written as a blob with BuildKit cache config media type. The config descriptor is inserted into the artifact, the final manifest/index JSON is written as another content blob, and its descriptor is marshaled into `cache.manifest` response metadata.

## State and Persistence Behavior

The exporter writes all cache artifacts to the configured content ingester under digest refs. The manifest/index references layer descriptors and the config descriptor. No local state is persisted by this file beyond the v1 chain target accumulated before finalization. The returned descriptor lets callers publish or reference the generated remote cache artifact.

## Dependencies and Integration Points

This file integrates containerd content/images/remotes errors, BuildKit remotecache v1 chains and config media types, solver cache export targets, content copy utilities, progress/logging, resolver concurrency limits, compression media-type conversion, OCI specs, and digest calculation. Registry cache exporters and related backends build on this generic exporter.

## Risks and Edge Cases

- Image-manifest cache format requires OCI media types; `NewExportableCache` rejects Docker media types in that mode.
- Empty cache exports return nil metadata after reporting a skipped export, so callers must handle no manifest descriptor.
- Layer copying is parallel, but manifest order is restored afterward from the original layer descriptor slice.
- Remote status errors are enriched only for `ErrUnexpectedStatus`; other errors pass through with normal wrapping.
- Any missing descriptor/provider pair for a cache layer aborts finalization.

## Test Signals

This subset does not include direct tests for `remotecache/export.go`. It is indirectly exercised by cache-chain and `GetRemotes` tests that validate descriptors, compression media types, and annotations; backend-specific exporter tests elsewhere would be needed for end-to-end artifact validation.
