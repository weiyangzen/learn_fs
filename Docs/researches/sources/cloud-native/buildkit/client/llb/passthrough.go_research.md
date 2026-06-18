# sources/cloud-native/buildkit/client/llb/passthrough.go

Purpose: implements passthrough LLB operations used to express dependencies/requirements while forwarding selected input outputs.

Important APIs/types/functions: `PassthroughInput` marks a state and whether it should be an output. `PassthroughOp` stores ID, input outputs, output map, constraints, and output objects. `NewPassthroughOp`, `NewPassthrough`, `Validate`, `Marshal`, `Output`, `OutputAt`, and `Inputs` define behavior.

Control flow: constructor filters scratch inputs, records all non-empty inputs, and creates output objects for inputs marked `Output`. Validation requires at least one input, a non-empty ID, at least one output, and valid output-map indexes. Marshal adds `CapPassthroughOp`, marshals constraints without platform, converts inputs to protobuf inputs, records output indexes, serializes deterministically, and caches.

State and persistence: in-memory op and marshal cache only; dependency semantics are solver-side.

Dependencies/integration points: `State.Requires` in `state.go`, solver `pb.PassthroughOp`, constraints/caps, and tests.

Risks/test signals: output closures capture `outputIndex` per loop with short declaration, which is safe in current Go semantics but worth preserving. Invalid `OutputAt` returns an output that fails later, making errors lazy. Tests cover requires, multiple outputs, no dependency shortcut, metadata preservation, and empty ID errors.
