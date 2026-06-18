## sources/cloud-native/buildkit/util/flightcontrol/cached.go

Purpose: adds indefinite per-key memoization on top of `flightcontrol.Group`, preserving singleflight-style synchronization while caching successful results and optionally non-context errors.

Important API/type: `CachedGroup[T]` exposes `CacheError bool` and `Do(ctx, key, fn)`. Internal `result[T]` stores cached value/error pairs.

Control flow: `Do` delegates to the embedded `Group` so concurrent callers for the same key share execution. Inside the group callback it checks the cache under mutex. Successful cached values return immediately. Cached errors return only when `CacheError` is true; otherwise the function reruns. After `fn`, errors matching the current context cause are never cached. Nil errors and, when enabled, non-context errors are stored in `cache`.

State/persistence: in-memory map protected by mutex; no eviction and therefore unsuitable for unbounded or long-lived key spaces. `CacheError` is documented as immutable after first use. Dependencies: `context`, `sync`, `github.com/pkg/errors`.

Integration points: wraps the local `Group[T]` from `flightcontrol.go`. Risks: indefinite retention, mutable `CacheError`, and generic values that may themselves be mutable/shared. Test signals: `cached_test.go` covers successful memoization, default non-caching of errors, error caching, and cancellation-error exclusion.
