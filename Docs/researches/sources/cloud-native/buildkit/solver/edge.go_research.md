## sources/cloud-native/buildkit/solver/edge.go

Purpose: core scheduler state machine for one solver edge, coordinating dependency requests, cache-map loading, cache probing/loading, operation execution, result release, and incoming pipe responses.

Important APIs/types/functions: `edgeStatusType` states initial/cache-fast/cache-slow/complete. `edge`, `dep`, `edgeState`, and `edgeRequest` hold mutable scheduling state. Key methods include `unpark`, `processUpdates`, `recalcCurrentState`, `processCacheMapReq`, `processDepReq`, `processDepSlowCacheReq`, `respondToIncoming`, `createInputRequests`, `desiredStateDep`, `execIfPossible`, `loadCache`, and `execOp`.

Control flow: `unpark` processes completed async updates, responds to incoming requests when possible, starts cache-map loading, starts cache load or execution if desired complete and data is ready, or requests dependency states. Dependencies advance through fast cache keys, slow result-based cache, and complete results. Cache records short-circuit execution; failed cache loads remove loaded records and retry other paths. Executions save cache keys/results and return `CachedResult`.

State and persistence: in-memory edge state tracks cache maps, keys, records, dependency pipe receivers, loaded records, errors, result, owner/release counts, and debug flag. Persistence happens only through `op.Cache().Save` and cache manager calls.

Dependencies and integration points: integrates `activeOp`, `CacheManager`, `pipe` scheduler primitives, `CacheMap` dependency selectors/slow funcs, and result/exporter types.

Risks and test signals: this is concurrency-sensitive. Risks include stale state causing open incoming pipes, subtle cache phase decisions, result release races, and fallback forced solves. Debug hooks exist for diagnosis. Cache tests cover manager semantics, but edge scheduling itself needs broader solver integration tests outside this subset.
