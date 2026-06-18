# sources/cloud-native/buildkit/solver/llbsolver/ops/merge.go

Purpose: implements the LLB merge op, combining multiple immutable refs into one cache ref through the worker cache manager.

Important APIs/types/functions: `mergeOp`, `NewMergeOp`, `CacheMap`, `Exec`, and `Acquire`. Cache identity is `buildkit.merge.v0` plus serialized `pb.MergeOp`; dependencies match `op.Inputs`.

Control flow: `Exec` iterates runtime inputs, skips nil inputs and nil immutable refs, validates worker ref types, compacts valid refs, returns nil output when none remain, then calls `CacheManager().Merge` with progress and vertex description. The result is wrapped as a worker ref result.

State/persistence: merge creates a new immutable cache ref managed by the worker cache manager. The op itself has no mutable state and no parallelism acquisition.

Dependencies/integration: worker cache manager, BuildKit cache refs, solver progress controller, `opsutils.Validate`, and cachedigest JSON hashing.

Risks: nil output for zero refs must be expected by callers. Wrong input `Sys()` types are fatal. Merge ordering follows input order, so cache and filesystem semantics may depend on upstream ordering.

Test signals: no direct tests in this subset; integration coverage should verify merge layering semantics and cache export behavior.
