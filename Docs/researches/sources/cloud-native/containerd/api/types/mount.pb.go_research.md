<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/mount.pb.go -->
# sources/cloud-native/containerd/api/types/mount.pb.go

## Purpose
Generated Go bindings for containerd mount-related shared types.

## Important APIs and Types
`Mount` contains `Type`, `Source`, `Target`, and `Options`. `ActiveMount` wraps a `Mount` with `MountedAt`, `MountPoint`, and `Data map[string]string`. `ActivationInfo` groups a name, active mounts, system mounts, and labels. Generated map entry messages support `Data` and `Labels`.

## Control Flow
No business logic. Initialization builds descriptors for three messages plus two generated map entries.

## State and Persistence
These messages serialize mount configuration and activation state. They do not perform mounts or persist mount tables. `ActiveMount` records activation metadata that may be stored or communicated by snapshotter/runtime services.

## Dependencies and Integration Points
Depends on protobuf `Timestamp`. `Mount` is imported by task creation and runtime shim APIs; activation messages integrate with mount/snapshotter control paths.

## Risks
Mount fields are unvalidated strings here; invalid or dangerous source/target/options must be checked by services. Map ordering is nondeterministic. Cross-platform mount option semantics differ.

## Test Signals
Task create tests with rootfs mounts, snapshotter activation tests, serialization round trips, invalid mount validation in service layers, and platform-specific mount option tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/mount.pb.go -->
