# sources/cloud-native/containerd/internal/nri/container_linux.go

## Purpose
Adds Linux-specific container metadata to NRI conversion.

## Important APIs, Types, And Functions
`containerToNRI` calls `commonContainerToNRI`, obtains `LinuxContainer`, and fills `nri.LinuxContainer` fields including namespaces, devices, resources, cgroups path, IO priority, scheduler, net devices, RDT, seccomp profile, sysctls, and seccomp policy.

## Control Flow
The function is selected by the `linux` build tag and attaches Linux payload before returning the NRI container.

## State And Persistence
No internal state; output is a metadata snapshot.

## Dependencies And Integration Points
Uses NRI adaptation helpers, including `nri.Int` for optional OOM score values. Feeds the NRI adaptation layer during container lifecycle calls and synchronization.

## Risks
Assumes `GetLinuxContainer` returns non-nil on Linux. Returned nested structures are not deep-copied.

## Test Signals
No direct tests in this subset; covered by NRI integration on Linux.
