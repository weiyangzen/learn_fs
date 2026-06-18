<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_unsupported.go -->
# sources/cloud-native/cri-o/server/container_remove_unsupported.go

## Purpose

This non-Linux build-tagged file provides a no-op seccomp notifier cleanup implementation.

## Important APIs, Types, and Functions

`removeSeccompNotifier(ctx, c)` has the same signature as the Linux implementation and returns immediately.

## Control Flow

The shared removal code can call this method unconditionally. On non-Linux platforms there is no seccomp notifier state to close.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It depends only on context and internal `oci.Container` types to satisfy the shared method surface.

## Risks and Edge Cases

If a non-Linux runtime later supports an equivalent notification resource, this no-op would need replacement.

## Test Signals

No direct tests are present; build-tag compilation is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_remove_unsupported.go -->
