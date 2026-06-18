<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/exporter.go -->
## sources/cloud-native/buildkit/solver/exporter.go

Purpose: exports solver cache records and dependency links to a `CacheExporterTarget`, including remote result metadata, backlinks, secondary exporters, and merged exporters.

Important APIs and types: `exporter.ExportTo`, `addBacklinks`, `getBestResult`, `compareCacheRecord`, and `mergedExporter.ExportTo`. The `exporter` carries a cache key, preferred records, optional single record, context option injector, secondary edge context, and override flag.

Control flow: `ExportTo` initializes per-call context maps for backlink memoization and recursion cycle prevention. It clones and sorts records by newest `CreatedAt` then lower `Priority`, loads result remotes, optionally resolves local refs into remotes, recursively exports dependency cache keys, adds secondary exporters from merged edges, exports backlinks unless disabled, validates all dependency slots have records, and finally calls `t.Add` for the root cache key. `addBacklinks` recursively walks backend backlink metadata and suppresses incomplete link sets.

State and dependencies: no durable state here; it reads cache manager backend/results and writes to exporter target. Context stores memo maps for one export traversal. Dependencies include cache manager internals, OCI digests, and containerd errdefs.

Integration points: remote cache export, inline cache export, scheduler cache exporting, and llbsolver exporter code all route through this machinery via `ExportableCacheKey.Exporter`.

Risks and test signals: recursive graph export must avoid cycles and incomplete dependency records. Error handling intentionally continues on dependency export failures in some loops, which may omit cache links. `exporter_test.go` covers record ordering only; broader scheduler cache export tests outside this subset cover integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/exporter.go -->
