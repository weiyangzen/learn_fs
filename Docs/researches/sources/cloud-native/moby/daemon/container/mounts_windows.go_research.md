<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/mounts_windows.go -->
# sources/cloud-native/moby/daemon/container/mounts_windows.go

## Purpose
Defines the reduced Windows mount descriptor.

## Important APIs, Types, And Functions
`Mount` contains `Source`, `Destination`, and `Writable`.

## Control Flow
No executable behavior.

## State And Persistence Behavior
Instances are in-memory descriptors and may be serialized by runtime paths.

## Dependencies And Integration Points
Used by Windows secret/config mount methods and runtime setup.

## Risks And Test Signals
Risk is loss of Unix-only fields by design; Windows runtime consumers must not expect propagation/data flags. Windows mount integration tests are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/mounts_windows.go -->
