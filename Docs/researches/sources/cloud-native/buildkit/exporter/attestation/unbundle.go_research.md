# Research: sources/cloud-native/buildkit/exporter/attestation/unbundle.go

## Purpose
Unbundles and validates attestation bundles.

## Important APIs, Types, and Functions
`Unbundle`, `sort`, `unbundle`, `Validate`, `validate`.

## Control Flow
Materializes bundle refs, walks files, parses in-toto JSON, validates shape, sorts deterministically, and returns individual attestations.

## State and Persistence
Temporary mounted/read snapshot content; output is in-memory.

## Dependencies and Integration Points
Depends on session/snapshot/result APIs, in-toto JSON, continuity fs, path handling. Called by image writer for per-platform attestations.

## Risks and Edge Cases
Malformed bundles and path/statement assumptions should fail early; sorting matters for reproducibility.

## Test Signals
Covered by attestation/export integration tests.
