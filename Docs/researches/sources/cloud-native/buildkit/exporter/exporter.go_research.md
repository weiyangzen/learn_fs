# Research: sources/cloud-native/buildkit/exporter/exporter.go

## Purpose
Generic exporter interfaces and config.

## Important APIs, Types, and Functions
`Source`, `Attestation`, `Exporter`, `ExporterInstance`, `FinalizeFunc`, `ExportBuildInfo`, `DescriptorReference`, `Config`.

## Control Flow
Solver resolves an exporter instance, calls `Export`, receives metadata/finalize/descriptors, and runs finalize when needed.

## State and Persistence
Contracts only; persistence depends on implementation.

## Dependencies and Integration Points
Depends on cache refs, solver result generics, compression config, OCI descriptors. Common boundary for all BuildKit exporters.

## Risks and Edge Cases
Finalize and descriptor release lifetimes must be respected to avoid leaks/GC races.

## Test Signals
Compile and integration tests.
