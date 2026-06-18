# sources/cloud-native/buildkit/client/llb/definition.go

Purpose: reconstructs an LLB vertex graph from a marshaled protobuf definition, allowing definitions received over the wire to become `State`/`Output` objects again.

Important APIs/types/functions: `DefinitionOp` implements `Vertex` and stores digest-indexed ops, raw definition bytes, metadata, source locations, platform map, current digest/index, and a shared input cache. `NewDefinitionOp` parses `pb.Definition`, reconstructs source maps, finds the terminal pointer input, and initializes metadata. Methods implement validation, marshaling, output creation, and input traversal.

Control flow: constructor unmarshals every op into maps keyed by digest, extracts platform specs, reconstructs nested source-map states via recursive `NewDefinitionOp`, then treats the last pointer op as the selected output digest/index. `Marshal` validates and returns original bytes/metadata for the current digest. `Inputs` walks protobuf inputs, reusing cached child `DefinitionOp`s per digest/output index to preserve graph identity and reduce duplicate traversal.

State and persistence: all state is in-memory maps shared between child definition ops. `inputCache` is a synchronized map to support parallel graph walks; `mu` protects map access and current op reads.

Dependencies/integration points: `pb.Definition`, `pb.Op`, source maps, platform metadata, deterministic digest calculation, and `NewState(op.Output())` consumers.

Risks/test signals: malformed definitions can panic if assumptions about final pointer inputs are violated, though nil definitions and missing maps are handled by errors. Shared map mutation requires careful locking. `definition_test.go` checks equivalence, input-cache vertex count, nil input errors, and parallel walk safety.
