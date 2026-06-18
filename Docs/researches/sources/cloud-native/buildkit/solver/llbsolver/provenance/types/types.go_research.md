# sources/cloud-native/buildkit/solver/llbsolver/provenance/types/types.go

Purpose: defines BuildKit-specific provenance data structures and conversion between SLSA v1 and SLSA v0.2 predicate layouts.

Important APIs/types/functions: constants `BuildKitBuildType1`, `BuildKitBuildType02`, `ProvenanceSLSA1`, `ProvenanceSLSA02`; types `BuildConfig`, `BuildStep`, source structs, `Parameters`, `RequestProvenance`, `Environment`, `BuildKitMetadata`, network metadata, SLSA predicate wrappers; methods `Validate`, `Clone`, `Equal`, `ConvertToSLSA02`, `ConvertToSLSA1`, and custom JSON marshal/unmarshal for `ProvenanceInternalParametersSLSA1` and `Environment`.

Control flow: clone/equal methods deep-copy and compare nested request structures. Conversion methods map builder, materials/resolved dependencies, config source, request parameters, build config, metadata, completeness, hermeticity, and custom environment fields between SLSA versions. Custom JSON handlers flatten unknown custom env keys into top-level JSON while preserving known fields.

State/persistence: these structs are serialized into attestation JSON. `ProvenanceCustomEnv` allows user-configured metadata but `Solver.New` forbids overriding builtin keys.

Dependencies/integration: in-toto SLSA v0.2/v1 packages, resource samples, protobuf ops/locations, OCI platform descriptors, digest types, and JSON.

Risks: JSON flattening can collide with future known fields if not guarded. Conversion is lossy for unsupported SLSA fields. Equal/Clone correctness affects provenance store ambiguity handling.

Test signals: `types_test.go` verifies custom env JSON round trips for SLSA1 internal parameters and SLSA0.2 invocation environment.
