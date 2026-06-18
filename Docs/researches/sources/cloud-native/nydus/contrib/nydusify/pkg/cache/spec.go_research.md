# sources/cloud-native/nydus/contrib/nydusify/pkg/cache/spec.go

## Purpose
This file defines the small data model used by the cache package for cache manifests and records.

## Important APIs, Types, and Functions
`Manifest` embeds `ocispec.Manifest` and adds an optional `mediaType` JSON field. `Record` stores a source chain ID, optional Nydus blob descriptor, Nydus bootstrap descriptor, and bootstrap diff ID.

## Control Flow
These types are passive structs. Cache import/export methods populate and consume them.

## State, Persistence, and Dependencies
`Manifest` maps directly to persisted registry JSON. `Record` is in-memory cache state. Dependencies are OCI descriptors and `opencontainers/go-digest`.

## Integration Points
`cache.go` uses these types to convert between OCI manifest layers and internal cache records. Other converter code consumes `Record` values for cache hits.

## Risks and Test Signals
The structs intentionally allow nil descriptors, so callers must guard when converting records. Tests in `cache_test.go` exercise many valid and invalid combinations.
