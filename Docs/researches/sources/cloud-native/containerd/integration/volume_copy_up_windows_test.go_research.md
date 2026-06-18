# sources/cloud-native/containerd/integration/volume_copy_up_windows_test.go

## Purpose

`volume_copy_up_windows_test.go` provides the Windows host ownership helper for the volume ownership integration test.

## Important APIs, Types, and Functions

- `getOwnership` calls `windows.GetNamedSecurityInfo` for file owner/DACL information and returns the owner SID string.

## Control Flow

The helper queries security info for the path, extracts the owner SID, and returns its string form.

## State and Persistence Behavior

It reads Windows filesystem security metadata and does not mutate state.

## Dependencies and Integration Points

It integrates with `TestVolumeOwnership` and depends on `golang.org/x/sys/windows` security APIs.

## Risks and Edge Cases

Errors can come from missing paths, permissions, or security descriptor lookup failures. It returns the SID rather than username because the username may be unknown on the host.

## Test Signals

The helper is indirectly covered by Windows volume ownership tests.
