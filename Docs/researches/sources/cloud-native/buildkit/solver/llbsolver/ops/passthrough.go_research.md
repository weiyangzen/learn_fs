# sources/cloud-native/buildkit/solver/llbsolver/ops/passthrough.go

Purpose: implements a passthrough op that selects and clones specified input results as outputs.

Important APIs/types/functions: `passthroughOp`, `NewPassthroughOp`, `CacheMap`, `Exec`, and `Acquire`. Cache identity is `buildkit.passthrough.v0` plus serialized `pb.PassthroughOp`; dependency count is the source vertex input count.

Control flow: constructor validates the op and records input count. `CacheMap` creates a dependency slot for each input. `Exec` allocates outputs equal to `op.Outputs`, validates each referenced input index against runtime inputs, clones non-nil inputs, and leaves nil input outputs nil.

State/persistence: no state beyond cloned result references. Cloning transfers independent ownership to callers.

Dependencies/integration: uses solver result clone semantics, cachedigest JSON hashing, `opsutils.Validate`, and protobuf passthrough op fields. Vertex names are generated in `vertex.go`.

Risks: incorrect clone/release behavior would leak or double-release refs. Runtime validation protects against stale/invalid output mappings even if constructor validation was incomplete.

Test signals: no direct tests in this subset. Behavior is small but should be covered by solver integration around frontend passthrough usage.
