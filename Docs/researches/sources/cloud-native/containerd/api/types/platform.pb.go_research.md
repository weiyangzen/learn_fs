<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform.pb.go -->
# sources/cloud-native/containerd/api/types/platform.pb.go

## Purpose
Generated Go binding for containerd's protobuf representation of an OCI platform.

## Important APIs and Types
`Platform` contains `OS`, `Architecture`, `Variant`, `OSVersion`, and repeated `OSFeatures`, with generated protobuf methods and getters.

## Control Flow
No business logic. Initialization builds a single-message descriptor.

## State and Persistence
The message carries platform selection metadata, often persisted in image metadata or transfer/import/export options.

## Dependencies and Integration Points
Depends only on protobuf runtime/reflection. `platform_helpers.go` converts to/from `opencontainers/image-spec/specs-go/v1.Platform`.

## Risks
The generated field name for `os_version` is `OSVersion` while the getter is `GetOsVersion`, which is normal generator behavior but easy to mistype. Platform normalization is not performed here; callers should use platform matching helpers elsewhere.

## Test Signals
Round-trip protobuf tests, OCI conversion tests, and image/platform matching tests for variant and OS feature preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform.pb.go -->
