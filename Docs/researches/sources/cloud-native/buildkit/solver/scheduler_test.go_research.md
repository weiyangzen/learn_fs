# sources/cloud-native/buildkit/solver/scheduler_test.go

## Purpose
This large suite is the main behavioral specification for the solver scheduler, active graph, cache lookup, slow-cache calculation, result sharing, and cache export interactions.

## Important Tests and Fixtures
The early tests cover single-level active graph sharing, cache hits, parallel cache deduplication, cancellation in cache and exec phases, multi-level calculations, huge random graphs, optimized cache access, slow-cache hits, parallel inputs, error propagation, multiple cache sources, ignore-cache behavior, subbuilds, selectors, cache export modes, multiple cache maps, and partial selector export. Later tests target merged-edge races and regressions: merged edge lookup, cycle avoidance, multiple owners, missing cache records, cache load failure fallback, input request deadlock, unknown job IDs, and stale edge merge cleanup.

The fixture types `vertex`, `vertexConst`, `vertexSum`, `vertexAdd`, and `vertexSubBuild` implement both `Vertex` and `Op` patterns. They synthesize cache maps, execute deterministic dummy results, support slow cache functions/selectors/multiple cache maps, and count cache/exec calls with atomics. `trackingCacheManager` counts and optionally fails cache loads. `testExporterTarget` records exported cache graph records.

## Control Flow
Tests construct solvers with `ResolveOpFunc: testOpResolver`, create jobs, build `Edge` graphs, assert returned dummy values, and discard jobs to exercise active state cleanup. Parallelism uses `errgroup`, blocking functions, and repeated loops to surface races. Many assertions compare cache/exec counts and load counts to confirm that the scheduler avoids unnecessary work.

## State and Persistence
The tests inspect active solver maps, result release counters, in-memory cache managers, and exporter target records. They intentionally discard jobs at different times to validate active edge reference tracking.

## Dependencies and Integration Points
The suite is package-internal and reaches solver internals such as `actives`, `cacheManager`, `inMemoryStore`, and exporter implementations. It integrates with `session.Group`, OCI descriptors, BuildKit identity generation, and `testify/require`.

## Risks Covered
It covers duplicate execution, cache overloading, cancellation cause confusion, slow-cache result leaks, merged-edge cycles, stale active graph ownership, cache load fallback, and cache export graph shape. Because the fake vertices are synthetic, registry/image/git source behaviors are covered elsewhere.

## Test Signals
This is a high-signal regression suite for scheduler correctness. Several race-prone cases run multiple iterations, and call-count assertions give precise evidence for cache and execution decisions.
