# sources/cloud-native/buildkit/solver/types.go

## Purpose
This file defines the central solver interfaces and data contracts: graph vertices, operation execution, result lifetimes, cache export, cache lookup, remote descriptors, and job-scoped services.

## Important APIs and Types
`Vertex`, `Edge`, `Index`, `VertexOptions`, and `VertexMetadata` model the build graph. `Result`, `CachedResult`, `CachedResultWithProvenance`, and `ResultProxy` model solver outputs. `Op` defines cache mapping, execution, and resource acquisition. `JobContext` exposes session, cleanup, resolver cache, and compatibility version. Cache contracts include `CacheMap`, `CacheManager`, `CacheRecord`, `ExportableCacheKey`, `CacheExporter`, `CacheExporterTarget`, `CacheLink`, `CacheExportResult`, `CacheExportOpt`, and `Remote`.

## Control Flow
This file is declarative except for `CacheExporterRecordBase.isCacheExporterRecord` and `(*CacheRecord).TraceFields`. Control flow is imposed by implementers: solver edges call `Op.CacheMap`, use `CacheManager.Query/Records/Load/Save`, run `Op.Exec` when no cache hit exists, and export records through `CacheExporter.ExportTo`.

## State and Persistence
The types describe both transient and persistent-ish state. `CacheRecord` carries stored record metadata such as ID, size, creation time, and priority. `Remote` describes content descriptors and providers used for transferable cache/image data. `JobContext.Cleanup` lets sources attach temporary resources to job lifetime.

## Dependencies and Integration Points
Dependencies include containerd content APIs, BuildKit sessions, protobuf progress groups, compression config, OCI descriptors, and digests. All solver source implementations in this subset implement or consume these interfaces.

## Risks
The contracts rely on implementers preserving cache-key purity: `CacheMap.Opts` must not affect computed cache keys, while `Digest`, selectors, and content digest functions must. Mutable slices/maps such as cache sources, descriptions, and descriptors should be treated carefully to avoid cross-solve mutation.

## Test Signals
The scheduler and cache storage tests exercise many of these contracts through fake `Op`, `CacheManager`, `Result`, and exporter implementations. Source-specific tests elsewhere validate registry/git/image implementations.
