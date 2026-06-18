# sources/cloud-native/buildkit/client/llb/merge.go

Purpose: implements LLB merge operations that overlay multiple states into one state, commonly combined with `Diff`.

Important APIs/types/functions: `MergeOp` implements `Vertex`; `NewMerge` builds inputs and output; `Validate` requires at least two inputs; `Marshal` serializes `pb.MergeOp`; public `Merge` filters scratch inputs and applies capability `pb.CapMergeOp`.

Control flow: `Merge` removes scratch inputs, returns scratch for none, returns the single non-empty input unchanged for one, otherwise builds constraints, adds merge cap, and creates a merge output attached to the first input. Marshal validates, clears platform because merge is not platform-specific, appends each input as a protobuf input and merge input index, serializes deterministically, and caches.

State and persistence: in-memory marshal cache only; merged filesystem semantics are solver-side.

Dependencies/integration points: `Diff`, solver `pb.MergeOp`, capability metadata, and platform propagation tests.

Risks/test signals: merge order matters for overlay semantics and cache keys. `Validate` catches direct `NewMerge` misuse with less than two inputs; public helper optimizes those cases. `merge_test.go` covers scratch/single-input behavior.
