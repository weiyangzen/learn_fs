# sources/cloud-native/moby/daemon/seccomp_unsupported.go

## Purpose
Provides the non-Linux seccomp implementation, where seccomp support is unavailable and applying seccomp options is a no-op.

## Important APIs, Types, And Functions
`supportsSeccomp` is false. `WithSeccomp` returns a containerd OCI `SpecOpts` closure that accepts the standard parameters and returns nil.

## Control Flow
No control flow beyond returning success from the spec option.

## State And Persistence
No spec, container, or daemon state is changed.

## Dependencies And Integration Points
Compiles on non-Linux platforms and satisfies shared OCI spec generation code.

## Risks And Edge Cases
Security behavior differs by platform: non-Linux builds silently do not apply seccomp profiles. Callers must gate seccomp expectations on `supportsSeccomp`.

## Test Signals
No file-local tests. Cross-platform builds validate the stub signature.
