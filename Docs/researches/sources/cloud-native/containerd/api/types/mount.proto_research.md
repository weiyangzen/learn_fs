<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/mount.proto -->
# sources/cloud-native/containerd/api/types/mount.proto

## Purpose
Canonical proto definitions for containerd mount data, described as a common language used by services when creating containers.

## Important APIs and Types
`Mount` follows mount syscall shape: `type`, `source`, `target`, and repeated `options`. `ActiveMount` adds activation time, mount point, and data. `ActivationInfo` groups active and system mounts with labels.

## Control Flow
Schema only. Mount execution and cleanup are implemented in snapshotter/runtime layers.

## State and Persistence
Carries mount configuration and activation metadata. Persistent meaning depends on callers storing activation info or using it to reconstruct active mounts.

## Dependencies and Integration Points
Imports protobuf `Timestamp`. Used by task create rootfs, runtime shim APIs, snapshotters, and activation-related services.

## Risks
Mount options are platform- and filesystem-specific and can be security-sensitive. The schema cannot prevent host path exposure, invalid targets, or unsupported options.

## Test Signals
Mount validation tests in service code, cross-platform task creation tests, and activation info serialization tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/mount.proto -->
