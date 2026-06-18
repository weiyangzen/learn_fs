# Research: sources/cloud-native/buildkit/exporter/containerimage/export.go

## Purpose
Container image exporter implementation.

## Important APIs, Types, and Functions
`Opt`, `imageExporter`, `imageExporterInstance`, `New`, `Resolve`, `Export`, `pushImage`, `unpackImage`, `DefaultOCITypes`, descriptor reference helpers.

## Control Flow
Parses exporter options, clones source metadata, parses annotations, opens a lease, asks `ImageWriter.Commit` for a descriptor, tags/stores images, optionally unpacks, materializes lazy refs, returns response metadata and optional push finalize callback.

## State and Persistence
Persists content/images/snapshots in containerd stores, uses temporary leases, and may push to registries.

## Dependencies and Integration Points
Depends on containerd content/images/leases/rootfs, BuildKit cache/session/snapshot/exporter APIs, registry push, compression, OCI descriptors. Implements BuildKit `type=image` export/store/push flow.

## Risks and Edge Cases
Option conflicts, lazy ref completion, image create/update races, and push errors are important.

## Test Signals
Covered by image exporter integration tests.
