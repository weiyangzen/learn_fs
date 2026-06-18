# sources/cloud-native/buildkit/cache/remotecache/inline/inline.go

## Purpose

This file implements the inline cache exporter. Instead of uploading a separate remote cache object, it serializes cache records suitable for embedding into an image config's `moby.buildkit.cache.v0` field while aligning cache results to the actual image layer order.

## Important APIs, Types, and Functions

- `ResolveCacheExporterFunc` returns an inline exporter resolver.
- `NewExporter` creates an exporter backed by `v1.CacheChains`.
- `exporter.Finalize` is a no-op because inline cache bytes are produced per image layer set rather than at generic cache finalization.
- `ExportForLayers` filters cache records to the image's layer set, rewrites layer result references to match image order, and returns JSON cache records.
- `layerToBlobs` walks a parent chain from a top layer index and returns blob digests lowest-to-highest.

## Control Flow and State

The exporter collects cache records through its embedded `CacheExporterTarget`. `ExportForLayers` marshals the full cache graph, builds a descriptor subset containing only blobs that match the supplied image layer digests or their uncompressed labels, parses that subset into a fresh cache chain, and marshals it again. This removes cache entries unrelated to the exported image.

It then builds an image-layer blob index and rewrites each result. If a result chain matches the image layer order, it can be represented as a compact `CacheResult` with the top layer index. If the result uses layers in a different order, it is converted into `ChainedResult` with explicit per-layer indexes and the original `CacheResult` is removed. The function finally marshals only `cfg.Records`, resets internal cache chains, and returns the JSON.

State is transient. The exporter resets after producing inline bytes so subsequent image exports do not reuse stale collected records.

## Dependencies and Integration Points

The exporter relies on v1 cache-chain marshal/parse, `cacheimporttypes` result shapes, containerd's uncompressed digest label, BuildKit compression defaults, and `solver.CacheExporterTarget`. It is invoked by image export paths that need inline BuildKit cache metadata in image configs.

## Risks and Edge Cases

If no cache layers match the supplied image layers, it logs a warning and returns nil. Matching considers both compressed blob digest and uncompressed digest annotation, which is necessary but can be confusing when layer digests differ by compression. Chained-result conversion fails if a result blob cannot be mapped to any supplied image layer. The mutation of `r.Results` while iterating through `r.Results` is subtle and should be kept under test when result structures change.

## Test Signals

No inline-specific tests are in this subset. Inline import handling in `remotecache/import.go` and generic v1 roundtrip tests provide indirect coverage, but `ExportForLayers` ordering and chained-result rewrite behavior are not directly exercised here.
