# sources/cloud-native/buildkit/solver/llbsolver/ops/diff.go

Purpose: implements the LLB diff op that returns a filesystem ref representing differences between lower and upper inputs.

Important APIs/types/functions: `diffOp`, `NewDiffOp`, `CacheMap`, `Exec`, and `Acquire`. The cache key is `buildkit.diff.v0` plus serialized `pb.DiffOp`; dependency count is based only on non-empty lower/upper refs.

Control flow: `Exec` maps compact input slice positions to logical lower and upper inputs, validates worker ref types, handles cheap identity cases, then calls `worker.CacheManager().Diff`. If both sides are empty it returns an empty worker ref, if lower is empty it clones upper, and if lower and upper have the same cache ref ID it returns empty.

State/persistence: creates a new diff immutable ref through the cache manager when needed. It does not maintain internal state and does not consume parallelism in `Acquire`.

Dependencies/integration: depends on worker cache manager diff implementation, `solver.ProgressControllerFromContext`, BuildKit cache refs, and `opsutils.Validate`.

Risks: input ordering is subtle because empty logical inputs are omitted from the runtime input slice. Nil or wrong `Sys()` values are hard errors. Same-ID optimization assumes cache ref identity is sufficient to represent no diff.

Test signals: no direct tests in this subset; expected coverage is integration around diff LLB operations and cache manager behavior.
