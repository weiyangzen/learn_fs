# sources/cloud-native/buildkit/client/llb/passthrough_test.go

Purpose: unit tests for passthrough and `State.Requires` behavior.

Important APIs/types/functions: `TestPassthroughRequiresMarshal`, `TestPassthroughMultipleOutputsMarshal`, `TestPassthroughRequiresNoDeps`, `TestPassthroughRequiresPreservesMetadata`, `TestPassthroughEmptyID`, and helpers to find passthrough vertices.

Control flow: tests build image states with requires or explicit passthrough ops, marshal definitions, locate passthrough protobuf ops, and assert input counts, IDs, output maps, absence when no deps, state metadata preservation, and error on empty ID.

State and persistence: no external persistence.

Dependencies/integration points: `Image`, `Requires`, `NewPassthroughOp`, `NewState`, protobuf decoding, and `Dir` metadata.

Risks/test signals: validates core dependency-only graph behavior. It does not cover invalid output indexes directly or solver execution semantics.
