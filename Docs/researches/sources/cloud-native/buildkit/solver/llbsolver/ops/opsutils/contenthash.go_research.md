# sources/cloud-native/buildkit/solver/llbsolver/ops/opsutils/contenthash.go

Purpose: provides content-based cache digest calculation for selected paths of worker refs.

Important APIs/types/functions: `Selector`, `Selector.HasWildcardOrFilters`, and `NewContentHashFunc`. Selectors carry path, wildcard, symlink-following, include/exclude filters, and required paths.

Control flow: `NewContentHashFunc` returns a `solver.ResultBasedCacheFunc`. When invoked, it asserts the result is a `*worker.WorkerRef`, defaults an empty selector list to the root selector, and computes `contenthash.Checksum` for each selector concurrently through `errgroup`. Individual selector digests are joined with NUL bytes and hashed as a digest list.

State/persistence: no state is persisted here; contenthash may consult cache metadata and snapshot contents through the immutable ref. The returned closure captures the selector slice.

Dependencies/integration: used by exec and file ops for dependency cache keys. Depends on `cache/contenthash`, solver result interfaces, session group, worker refs, and `cachedigest`.

Risks: selector mutation after closure creation would affect future calls because the slice is captured. Errors include ref ID for diagnostics. Concurrent checksum calculation must be safe for the underlying ref/contenthash implementation.

Test signals: covered indirectly by exec/file cache-map tests and broader contenthash tests outside this subset.
