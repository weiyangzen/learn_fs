# sources/cloud-native/containerd/internal/nri/container.go

## Purpose
Defines the container metadata interface that containerd domains must implement for NRI, plus common conversion to NRI container protobuf/adaptation structures.

## Important APIs, Types, And Functions
`ContainerStatus`, `Container`, and `LinuxContainer` describe status, labels, args, mounts, hooks, Linux resources/devices, CDI devices, rlimits, user, seccomp, and networking. `commonContainerToNRI` and `containersToNRI` build NRI objects.

## Control Flow
Conversion reads fields from the interface and copies them into an `nri.Container`. Platform-specific files add Linux fields on Linux and omit them elsewhere.

## State And Persistence
No internal state. Converted NRI structures are snapshots of current domain state.

## Dependencies And Integration Points
Depends on `github.com/containerd/nri/pkg/adaptation`. Domain implementations in CRI or other namespaces supply concrete containers.

## Risks
Interface methods may return maps/slices by reference; conversion does not deep-copy them. Nil status would panic when fields are accessed.

## Test Signals
No direct tests in this subset. Conversion is exercised indirectly by NRI lifecycle tests/integration.
