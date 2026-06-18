## sources/cloud-native/buildkit/solver/cachekey.go

Purpose: defines solver cache keys and dependency key wrappers.

Important APIs/types/functions: `NewCacheKey(dgst, vtx, output)` creates a root cache key id from `rootKey`. `CacheKeyWithSelector` pairs an exportable cache key with an optional selector digest and has trace fields. `CacheKey` stores id, dependency key matrix, operation digest, vertex digest, output index, cache-manager-specific ids, and index ids. `TraceFields`, `Deps`, `Digest`, `Output`, and `clone` expose safe views.

Control flow: methods lock around mutable fields. `Deps` returns cloned outer/inner slices so callers cannot mutate stored deps. `clone` copies manager id mapping but intentionally does not copy deps in this file unless the caller sets them.

State and persistence: cache keys are in-memory graph nodes. Manager-specific ids connect them to persistent `CacheKeyStorage`.

Dependencies and integration points: heavily used by `cacheManager`, scheduler `edge`, exporters, and tests. Uses digest identities for cache matching.

Risks and test signals: `TraceFields` dependency reporting overwrites `"id"`/`"selector"` in a map inside the loop, so each dependency group only retains the last dependency in trace output; functional behavior is unaffected but debug detail is reduced. Tests cover key matching through manager behavior.
