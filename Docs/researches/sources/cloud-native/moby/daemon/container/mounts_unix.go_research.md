<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/mounts_unix.go -->
# sources/cloud-native/moby/daemon/container/mounts_unix.go

## Purpose
Defines the Unix mount descriptor passed from container metadata to runtime mount setup.

## Important APIs, Types, And Functions
`Mount` fields include `Source`, `Destination`, `Writable`, `Data`, `Propagation`, `NonRecursive`, `ReadOnlyNonRecursive`, and `ReadOnlyForceRecursive`.

## Control Flow
The file has no behavior; it is a platform-specific type shape.

## State And Persistence Behavior
Instances may be marshaled to JSON for runtime configuration, but this file performs no IO.

## Dependencies And Integration Points
Used by Unix container mount methods for network, IPC, secrets, configs, tmpfs, and runtime setup.

## Risks And Test Signals
Risk is field drift with runtime consumers, especially recursive read-only flags. Mount integration tests are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/mounts_unix.go -->
