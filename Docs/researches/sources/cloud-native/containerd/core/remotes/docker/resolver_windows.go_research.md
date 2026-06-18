<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_windows.go -->
# sources/cloud-native/containerd/core/remotes/docker/resolver_windows.go

## Purpose
Provides the Windows implementation of connection-refused detection used by HTTP fallback logic.

## Important APIs, Types, And Functions
- `isConnError(err error) bool` returns true for both `syscall.ECONNREFUSED` and `windows.WSAECONNREFUSED`.

## Control Flow
`isPortError` in `resolver.go` calls this helper when deciding whether a scheme fallback from HTTPS to HTTP is allowed for a host without an explicit port.

## State And Persistence
No state.

## Dependencies And Integration Points
Build-tagged with `//go:build windows`; depends on `golang.org/x/sys/windows` for Winsock error classification.

## Risks And Edge Cases
Correct fallback behavior on Windows depends on wrapping preserving `errors.Is` checks for Winsock constants.

## Test Signals
Covered indirectly by resolver fallback tests on Windows. No Windows-specific listed test targets this file directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/resolver_windows.go -->
