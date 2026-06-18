<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform_helpers.go -->
# sources/cloud-native/containerd/api/types/platform_helpers.go

## Purpose
Provides hand-written conversion helpers between containerd protobuf `Platform` values and OCI image-spec `Platform` values.

## Important APIs and Types
`OCIPlatformToProto([]oci.Platform) []*Platform` allocates a protobuf slice and copies OS, OSVersion, Architecture, Variant, and OSFeatures. `OCIPlatformFromProto([]*Platform) []oci.Platform` performs the reverse copy.

## Control Flow
Both functions allocate output slices with the same length as input and iterate by index. They perform direct field copies only; no normalization or nil filtering is done.

## State and Persistence
No persistent state. The helpers transform in-memory platform metadata.

## Dependencies and Integration Points
Imports `github.com/opencontainers/image-spec/specs-go/v1` as `oci`. Integrates generated API types with OCI image-spec consumers and transfer/import/export code.

## Risks
`OCIPlatformFromProto` will panic if the input slice contains nil `*Platform` entries, because it dereferences fields directly. Neither function deep-copies the `OSFeatures` slice, so callers should avoid mutating source slices after conversion if aliasing matters.

## Test Signals
Unit tests should cover round-trip conversion, empty slices, OS features preservation, and nil input slice behavior. A nil-element test would document the current panic or motivate defensive handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform_helpers.go -->
