## sources/cloud-native/buildkit/solver/cacheopts.go

Purpose: carries cache-related runtime options through contexts and lets operations retrieve options from a state's ancestors.

Important APIs/types/functions: `CacheOpts` is `map[any]any`. `CacheOptGetterOf` fetches a getter from context. `WithCacheOptGetter` installs one. `withAncestorCacheOpts` creates a getter that walks a solver state and optionally ancestors to find requested keys from `op.cacheRes.Opts`. `walkAncestors` traverses active solver parents without revisiting digests. `ProgressControllerFromContext` retrieves a progress controller keyed by `progressKey`.

Control flow: getter builds a requested key set, walks current state first, skips errored vertexes, copies matching option values, and stops after current state unless `includeAncestors` is true. Ancestor traversal uses a stack and solver active map under read lock.

State and persistence: context values and in-memory solver state only.

Dependencies and integration points: used by solver operations that need cache result context options, especially progress propagation during cache load/export paths.

Risks and test signals: missing parents log warnings and skip that branch. Context key types are private, preventing external collisions. No direct tests in this subset.
