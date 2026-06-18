# sources/control-plane/csi-driver-smb/pkg/mounter/safe_mounter_unix.go

## Purpose
Linux/Darwin factory for Kubernetes `SafeFormatAndMount`.

## Important APIs, Types, and Functions
Defines `NewSafeMounter(_, _ bool)` returning `mount.SafeFormatAndMount{Interface: mount.New(""), Exec: utilexec.New()}`.

## Control Flow
Ignores Windows-specific flags and returns the standard mount implementation.

## State and Persistence
No state; callers perform actual mount operations.

## Dependencies
Depends on `k8s.io/mount-utils` and `k8s.io/utils/exec`.

## Integration Points
Used by SMB driver startup on Linux and Darwin.

## Risks and Edge Cases
No custom behavior for SMB mapping cleanup or HostProcess flags outside Windows.

## Test Signals
`safe_mounter_unix_test.go` verifies a nonnil mounter and nil error.
