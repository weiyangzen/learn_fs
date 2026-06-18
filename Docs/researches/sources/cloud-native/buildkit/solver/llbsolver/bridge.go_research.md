<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/bridge.go -->
## sources/cloud-native/buildkit/solver/llbsolver/bridge.go

Purpose: implements the LLB frontend bridge over solver jobs, workers, source policy, cache importers, entitlements, executor access, source metadata resolution, and lazy cache importer resolution.

Important APIs and types: `llbBridge` fields hold builder, frontends, worker resolvers, cache importer functions, cache manager memo, session manager, provenance store, proxy-network mode, and lazily loaded executor. Methods include `Warn`, `loadResult`, `policy`, `validateEntitlements`, `Run`, `Exec`, `loadExecutor`, `ResolveSourceMetadata`, `resolveSourceMetadata`, `cmKey`, and `newLazyCacheManager`. `lazyCacheManager` implements the solver cache manager interface by waiting for async importer construction.

Control flow: `loadResult` resolves a worker, loads entitlements/source policy, validates request policies, builds a source policy engine, memoizes cache importers by stable key, loads LLB with policy/entitlement/cap/resource options, prunes detected pruned cache ids, then calls `builder.Build`. Execution methods validate entitlements, attach proxy policy, lazily load worker executor once, and delegate. Source metadata resolution applies policy before calling worker metadata resolution inside progress context.

State and persistence: cache importer managers are memoized in `cms` under `cmsMu`; executor is cached with `sync.Once`. Lazy cache managers start goroutines and close `waitCh` when ready. No durable state.

Dependencies and integration: central bridge between frontend gateway, solver, worker controller, remotecache, sourcepolicy, entitlements, sessions, executor, and provenance/proxy helpers.

Risks and test signals: risks include lazy importer goroutine errors surfacing late, cache importer key collisions, policy bypass when `withPolicy` is false, and proxy network netmode rewriting. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/bridge.go -->
