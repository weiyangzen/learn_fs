# sources/cloud-native/buildkit/client/llb/llbbuild/llbbuild.go

Purpose: defines an LLB `BuildOp` wrapper that invokes the LLB builder on an input definition source.

Important APIs/types/functions: `Build` returns a `StateOption` that replaces state output with a build op. `NewBuildOp` creates a `build` vertex from a source output and options. `build` implements both `llb.Vertex` and `llb.Output` methods. `BuildInfo`, `WithFilename`, and `WithConstraints` configure definition filename and constraints.

Control flow: marshal builds a `pb.BuildOp` with builder `pb.LLBBuilder`, maps `pb.LLBDefinitionInput` to input 0, optionally sets `pb.AttrLLBDefinitionFilename`, adds `CapBuildOpLLBFileName`, marshals constraints, converts the source output to an input, appends it, serializes the op, and caches it.

State and persistence: in-memory marshal cache only. The build op represents solver-side nested build execution rather than local persistence.

Dependencies/integration points: `llb.StateOption`, `llb.Output`, `llb.MarshalConstraints`, solver `pb.BuildOp`, capabilities, and definition-file attribute.

Risks/test signals: `Validate` is no-op and `NewBuildOp` accepts nil source, so nil source would fail during marshal. It uses non-deterministic `pop.Marshal()` rather than `deterministicMarshal`, though fields are small and test covers expected shape. `llbbuild_test.go` checks marshaled build op fields.
