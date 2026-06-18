# Research: sources/cloud-native/buildkit/exporter/containerimage/attestations.go

## Purpose
SBOM/attestation helpers for image export.

## Important APIs, Types, and Functions
`intotoPlatform`, `supplementSBOM`, SPDX encode/decode, `fileLayerFinder` helpers.

## Control Flow
Decodes SPDX SBOMs, finds source files in target layers/remotes, supplements package/layer references, and returns amended attestations.

## State and Persistence
Uses temporary refs/remotes and releases finder resources; data is in-memory until written.

## Dependencies and Integration Points
Depends on cache refs, solver remotes, session content, SPDX libs, OCI descriptors. Integrated into `ImageWriter.Commit` per-platform attestation flow.

## Risks and Edge Cases
Layer lookup, lazy remotes, and SPDX format assumptions can break supplementation.

## Test Signals
SBOM exporter integration tests expected.
