# sources/cloud-native/buildkit/solver/pb/const.go

Purpose: this file defines small typed constants used throughout BuildKit's LLB protobuf model to express input and output indexes and conventional mount/build sentinel values.

Important APIs and constants: `InputIndex` and `OutputIndex` are typed `int64` aliases for referring to input vertices and output slots. `RootMount` is the root filesystem mount point `/`. `SkipOutput` is `OutputIndex(-1)` for disabled outputs. `Empty` is `InputIndex(-1)` for no-content input. `LLBBuilder` is `InputIndex(-1)` for the special nested build builder input. `LLBDefinitionInput` and `LLBDefaultDefinitionFile` both use `buildkit.llb.definition` to identify an LLB definition file used by `BuildOp`.

Control flow: there is no executable control flow. The constants are read by solver, frontend, and operation construction code when building or interpreting LLB graphs.

State and persistence: no local state is stored. These sentinel values appear in serialized LLB definitions and therefore form part of the persisted/cached graph contract. Reusing `-1` for several typed sentinel contexts is intentional because the types and consuming fields disambiguate meaning.

Dependencies and integration points: the constants integrate with `ops.proto` fields such as `Input.index`, `Mount.input`, `Mount.output`, `BuildOp.builder`, and `BuildInput.input`. `RootMount` is used by exec mount creation, and the LLB definition constants connect nested `BuildOp` behavior with filesystem inputs.

Risks and test signals: risks are mostly semantic misuse, such as passing `Empty` where a real input is required or forgetting that `LLBBuilder` and `Empty` share the same raw integer. There are no direct tests in this file; behavior is covered indirectly by solver and frontend tests that construct LLB graphs with root mounts, empty inputs, skipped outputs, and nested build definitions.
