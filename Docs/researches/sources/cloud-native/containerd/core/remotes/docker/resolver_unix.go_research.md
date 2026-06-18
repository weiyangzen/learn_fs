<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_unix.go -->
# sources/cloud-native/containerd/core/remotes/docker/resolver_unix.go

## Purpose
Provides the non-Windows implementation of connection-refused detection used by HTTP fallback logic.

## Important APIs, Types, And Functions
- `isConnError(err error) bool` returns true when the error wraps `syscall.ECONNREFUSED`.

## Control Flow
`isPortError` in `resolver.go` calls this helper. If a no-port host fails with connection refused or timeout, the fallback transport may retry the request using `http://`.

## State And Persistence
No state.

## Dependencies And Integration Points
Build-tagged with `//go:build !windows`; depends on `errors` and `syscall`. Integrated only through `resolver.go` fallback helpers.

## Risks And Edge Cases
Platform-specific error wrapping must preserve `errors.Is` compatibility. This file excludes Windows-specific Winsock errors, which are handled separately.

## Test Signals
Indirectly covered by resolver HTTP fallback and port-error tests on non-Windows platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_unix.go -->
