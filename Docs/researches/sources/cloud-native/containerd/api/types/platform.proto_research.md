<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform.proto -->
# sources/cloud-native/containerd/api/types/platform.proto

## Purpose
Canonical proto definition of containerd's platform message, aligned with the OCI platform specification.

## Important APIs and Types
`Platform` fields are `os`, `architecture`, `variant`, `os_version`, and repeated `os_features`.

## Control Flow
Schema only.

## State and Persistence
Represents platform metadata used for image selection, transfer, import/export, and compatibility decisions.

## Dependencies and Integration Points
No proto imports. Integrated with OCI platform structs through helper functions.

## Risks
The schema does not normalize architecture aliases, OS casing, or variant semantics. Compatibility decisions must use higher-level platform matchers.

## Test Signals
OCI conversion tests and multi-platform image selection tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/platform.proto -->
