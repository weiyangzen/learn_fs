<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp.go -->
# sources/cloud-native/containerd/pkg/seccomp/seccomp.go

## Purpose
Public seccomp capability probe facade.

## Important APIs, Types, And Functions
IsEnabled delegates to platform-specific isEnabled implementation.

## Control Flow
Single call path with platform dispatch by build tags.

## State And Persistence
No direct state here; Linux implementation caches probe result.

## Dependencies And Integration Points
Used by runtime feature detection code that needs cross-platform seccomp availability.

## Risks And Edge Cases
The meaning is kernel support for seccomp/filter, not whether a profile is active.

## Test Signals
Covered indirectly through platform implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp.go -->
