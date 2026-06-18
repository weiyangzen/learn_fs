<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/jobs.go -->
## sources/cloud-native/buildkit/solver/jobs.go

Purpose: defines BuildKit's solver job orchestration layer: active vertex graph sharing, job lifecycle, progress/tracing fanout, cache manager composition, operation deduplication, sub-build support, and provenance walking.

Important APIs and types: public surface includes `ResolveOpFunc`, `Builder`, `Solver`, `SolverOpt`, `NewSolver`, `Solver.NewJob`, `Solver.Get`, `Solver.Close`, `Job.Build`, `Job.Discard`, `Job.InContext`, `Job.Session`, `Job.Cleanup`, `Job.SetValue`, `Job.EachValue`, and `Job.CompatibilityVersion`. Internal types include `state`, `sessionGroup`, `subBuilder`, `sharedOp`, `activeOp`, `cacheWithCacheOpts`, `withProvenance`, `vertexWithMetadata`, `vertexWithCacheOptions`, and `SlowCacheError`.

Control flow: `Solver.load` recursively canonicalizes vertices and inputs, handles `IgnoreCache` by using a derived digest when necessary, creates or reuses active `state`, merges cache sources and metadata, records parent/child graph links, and connects progress writers. `Job.Build` loads the graph and delegates scheduling. `sharedOp` lazily resolves the concrete `Op`, deduplicates cache map, slow-cache, and exec work with `flightcontrol`, wraps errors with op and vertex details, and records progress/tracing. `Job.Discard` removes job references, releases unreferenced active states recursively, delays job map deletion for late status readers, and runs cleanup hooks.

State and persistence: state is in-memory only. Solver maps jobs by id and active states by digest; `state` tracks jobs, parents, children, releasers, cache managers, progress writer set, spans, op, and edges. `Job` tracks progress reader/writer, values, session id, unique provenance id, resolver cache, and releasers. No durable storage is written here.

Dependencies and integration: integrates with scheduler, edge index, cache managers, session groups, progress controller, tracing, compatibility values, resolver cache, errdefs, and provenance providers. `llbsolver/bridge.go` uses the `Builder` and `JobContext` contracts.

Risks and test signals: concurrency and lifecycle are the main risks: lock ordering, edge merge propagation, ignored-cache digest shifts, delayed deletion, cleanup release, and incomplete cancellation caching. `jobs_test.go` covers worker parallelism at integration level; scheduler tests outside this subset cover many shared-op behaviors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/jobs.go -->
