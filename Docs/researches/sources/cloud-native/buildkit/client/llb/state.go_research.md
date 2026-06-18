# sources/cloud-native/buildkit/client/llb/state.go

Purpose: central public LLB state graph API, including immutable state chaining, graph marshaling, output/input/vertex interfaces, constraints, metadata options, and platform/resource helpers.

Important APIs/types/functions: `State`, `Output`, `Vertex`, `StateOption`, `Constraints`, `ConstraintsOpt`, `OpMetadata`, `NewState`, `NewConstraints`, `Marshal`, recursive `marshal`, `Run`, `File`, metadata getters/setters, `Requires`, `WithOutput`, `WithImageConfig`, `output.ToInput`, constraints option adapters, metadata merge/conversion, platform constants, `Require`, cache export controls, progress group, Linux resource options, and local unique ID.

Control flow: `NewState` initializes output, root dir, and platform from output. State options build linked value chains. `Marshal` creates constraints, recursively marshals vertex inputs with duplicate digest and vertex caches, adds a final pointer op to selected output, records root metadata caps, and serializes source maps. `Run`, `File`, and `Requires` construct exec, file, and passthrough vertices. Constraint options implement multiple option interfaces so the same option can apply to runs and sources.

State and persistence: states are value chains with pointers to previous states and optional async state; public operations return new states. Constraints include generated `LocalUniqueID`, platform, worker filters, metadata, caps, and source locations. Marshal caches live in individual vertices; no external persistence.

Dependencies/integration points: every LLB operation file, protobuf solver APIs, platform normalization, identity generation, source maps, image config JSON, API caps, and solver consumers.

Risks/test signals: recursive marshal can be sensitive to vertex identity and digest cache ordering. `Validate` assumes output/vertex are non-nil. Metadata merge overwrites several fields such as progress group and Linux resources. Linux resources intentionally live in metadata, not op bytes. Tests in `state_test.go`, `llbtest/platform_test.go`, `exec_test.go`, and many fileop tests cover platform, source maps, metadata, resources, and deterministic definitions.
