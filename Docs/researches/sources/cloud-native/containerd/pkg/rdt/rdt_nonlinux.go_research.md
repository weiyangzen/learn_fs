<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rdt/rdt_nonlinux.go -->
# sources/cloud-native/containerd/pkg/rdt/rdt_nonlinux.go

## Purpose
Non-Linux or no_rdt stub for RDT support.

## Important APIs, Types, And Functions
IsEnabled returns false, SetConfig is a no-op, and ContainerClassFromAnnotations returns empty class and nil error.

## Control Flow
All calls return immediately.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Maintains cross-platform API compatibility for packages that call rdt unconditionally.

## Risks And Edge Cases
Silent no-op behavior can hide configuration mistakes on unsupported builds unless higher layers report platform support.

## Test Signals
Build tags provide compile-time platform coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rdt/rdt_nonlinux.go -->
