<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/export.go -->
## sources/cloud-native/buildkit/solver/llbsolver/export.go

Purpose: coordinates result exporters, session-provided exporters, remote cache exporters, inline cache creation, exporter progress, verification warnings, and descriptor/result metadata.

Important APIs and types: `Solver.getSessionExporters`, `runCacheExporters`, `runInlineCacheExporter`, `exporterVertexID`, `Solver.runExporters`, `splitCacheExporters`, `inlineCacheExporter`, `asInlineCache`, `inlineCache`, and `withDescHandlerCacheOpts`.

Control flow: session exporters are discovered via session gRPC and resolved through the default worker. Remote cache exporters run concurrently in builder contexts, export the first cache key chain, finalize, and merge responses while respecting `IgnoreError`. Main exporters run concurrently, emit invalid-platform warnings, serialize inline cache generation with a mutex, pass job compatibility version, collect finalize functions/descriptors, and merge response maps. Inline cache extracts remote layer digests from a worker ref, exports cache in min mode with compression variants, then asks the inline exporter for per-layer data.

State and dependencies: mostly transient; no durable state except external exporter side effects. Uses session groups, progress, tracing, errgroup, worker refs, compression config, and cache descriptor handlers attached through solver cache options.

Integration points: called from llbsolver solve completion to produce image/local outputs and cache metadata.

Risks and test signals: concurrent closures must use correct loop variables; inline cache is serialized because exporters may share target state. Session exporter discovery tolerates unavailable/unimplemented. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/export.go -->
