# sources/cloud-native/buildkit/frontend/attestations/parse.go

Purpose: parses frontend attestation options from `attest:` keys and legacy `build-arg:BUILDKIT_ATTEST_` keys into typed attribute maps.

Important APIs: constants define supported types `sbom` and `provenance`; `Filter` extracts attestation-related options; `Validate` rejects unknown types; `Parse` lowercases type names, applies defaults, parses CSV-style key/value attributes, and validates output.

Control flow: each attestation value is parsed as CSV fields so commas can be escaped/quoted. Fields without `=` become empty-valued attributes. SBOM defaults `generator` to BuildKit Syft scanner; provenance defaults `version` to SLSA v1. Unknown attestation type errors early.

State and persistence: no persistence; parsed maps are consumed by dockerui/build frontend configuration.

Dependencies and integration: integrates provenance type constants and `go-csvvalue` for robust attribute parsing.

Risks and test signals: risks include duplicate attribute overwrite, unknown type rejection, and lowercasing type names while preserving attribute keys. `parse_test.go` covers simple and quoted-comma forms.
