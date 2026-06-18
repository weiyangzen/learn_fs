# sources/cloud-native/buildkit/frontend/attestations/parse_test.go

Purpose: tests attestation option parsing.

Important test cases: simple SBOM/provenance parsing with default provenance version, extra SBOM parameters, and quoted CSV fields containing commas.

Control flow and state: table-driven subtests call `Parse`, require no error, and compare complete nested maps.

Dependencies and integration: uses `testify` assertions and intentionally compares provenance default version as literal `v1` to catch contract drift.

Risks and test signals: protects CSV parsing and default injection. It does not cover unknown type errors, legacy build-arg key parsing, or duplicate attributes.
