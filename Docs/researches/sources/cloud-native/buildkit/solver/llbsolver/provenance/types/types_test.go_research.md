# sources/cloud-native/buildkit/solver/llbsolver/provenance/types/types_test.go

Purpose: verifies custom provenance environment fields are preserved as flattened JSON in both SLSA v1 internal parameters and SLSA v0.2 invocation environment.

Important APIs/types/functions: `TestMarsalBuildDefinitionSLSA1` and `TestMarshalInvocation` exercise `ProvenanceBuildDefinitionSLSA1`, `ProvenanceInternalParametersSLSA1`, `ProvenanceInvocationSLSA02`, and `Environment` JSON marshal/unmarshal.

Control flow: each test unmarshals JSON containing known fields and arbitrary custom keys, asserts known struct fields and `ProvenanceCustomEnv` contents, marshals back, and compares JSON equivalence.

State/persistence: no external state; JSON round-trip behavior is the persistence contract for attestations.

Dependencies/integration: Go `encoding/json` and testify.

Risks: the first test name contains a typo (`Marsal`) but does not affect behavior. Coverage is focused on JSON flattening, not SLSA conversion or Clone/Equal methods.

Test signals: strong for preserving arbitrary custom keys such as strings, numbers, objects, and arrays without nesting them under an internal field.
