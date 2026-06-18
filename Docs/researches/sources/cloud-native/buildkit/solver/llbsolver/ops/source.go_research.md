# sources/cloud-native/buildkit/solver/llbsolver/ops/source.go

Purpose: implements source operations that resolve external/local sources into snapshot refs and cache keys.

Important APIs/types/functions: `SourceOp`, `NewSourceOp`, `IsProvenanceProvider`, `Pin`, `instance`, `CacheMap`, `Exec`, and `Acquire`. Cache identity uses `buildkit.source.v0:<source cache key>` hashed through `cachedigest`; session sources are forced to a `random:` digest.

Control flow: `instance` lazily resolves a `source.Identifier` through `source.Manager.Identifier` and `Resolve`, caching the `SourceInstance`, identifier, and pin. `CacheMap` asks the instance for `CacheKey`, records the first pin, and returns source cache options plus completion status. `Exec` snapshots the source and wraps it as a worker ref result. `Acquire` optionally uses a weighted semaphore.

State/persistence: stores resolved source instance and pin in the op instance. Source snapshot refs and cache records are managed by source/cache layers.

Dependencies/integration: source manager, session manager, worker refs, platform constraints, solver cache maps, and provenance capture via `Pin` and source identifier `Capture`.

Risks: lazy instance state is mutex-protected but source resolution errors are not cached. Session-based cache keys deliberately randomize to avoid unsafe reuse. Pin is set only if empty, so repeated cache-map calls retain the first pin.

Test signals: no direct tests in this subset; source behavior is typically integration-tested through local/git/http/image source tests.
