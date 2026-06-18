# sources/cloud-native/buildkit/client/llb/definition_test.go

Purpose: regression tests for round-tripping marshaled definitions back into LLB states.

Important APIs/types/functions: `TestDefinitionEquivalence` covers scratch, image, exec, local, git, HTTP, file op, platform constraints, and mounts. `TestDefinitionInputCache` checks shared input caching and parallel traversal. `TestDefinitionNil` verifies nil input errors. `testParallelWalk` recursively traverses inputs with errgroup.

Control flow: each state is marshaled, converted to `DefinitionOp`, validated, converted back to state, marshaled again, and compared byte-for-byte plus metadata and platform. Cache test builds shared HTTP inputs through multiple mounts, verifies vertex count, then creates a large graph and recursively walks in parallel.

State and persistence: in-memory graph definitions only.

Dependencies/integration points: `NewDefinitionOp`, `NewState`, marshal helpers, `errgroup`, platform normalization, and digest metadata.

Risks/test signals: strong signal for deterministic roundtrip and race safety. It does not cover corrupted non-nil definitions with missing final inputs or malformed source location indexes beyond constructor checks.
