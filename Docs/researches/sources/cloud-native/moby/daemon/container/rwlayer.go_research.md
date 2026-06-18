<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/rwlayer.go -->
# sources/cloud-native/moby/daemon/container/rwlayer.go

## Purpose
Defines the writable layer abstraction used by containers.

## Important APIs, Types, And Functions
`RWLayer` interface exposes `Mount(mountLabel string)`, `Unmount()`, and `Metadata()`.

## Control Flow
No implementation here; concrete graphdriver/containerd snapshot layers satisfy the interface.

## State And Persistence Behavior
Implementations manage mount reference counts and metadata persistence, but this interface file stores nothing.

## Dependencies And Integration Points
Referenced by `Container.RWLayer` and daemon graph/image storage code.

## Risks And Test Signals
Risk is contract ambiguity around multiple mounts and required unmount pairing. Storage driver and container lifecycle tests validate implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/rwlayer.go -->
