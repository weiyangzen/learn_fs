# sources/cloud-native/containerd/core/runtime/v2/socket_unix.go

## Purpose
Defines the maximum shim socket directory length for non-Linux, non-Windows Unix builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
`maxSocketDirLen` is `38`, derived from macOS-style Unix-socket path limits. It has no imports, state, or control flow.

The constant integrates with socket directory validation. Risks are platform assumptions for less common Unix targets. Test signals are build-tag compilation and socket path length validation tests.
