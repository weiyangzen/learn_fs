# sources/cloud-native/containerd/integration/volume_copy_up_unix_test.go

## Purpose

`volume_copy_up_unix_test.go` provides the non-Windows host ownership helper for the volume ownership integration test.

## Important APIs, Types, and Functions

- `getOwnership` runs `stat -c %u:%g '<path>'` through `sh -c` and returns the command output.

## Control Flow

The helper formats a shell command, executes it, returns combined output on success, and propagates errors.

## State and Persistence Behavior

It reads filesystem metadata for a host path and does not mutate state.

## Dependencies and Integration Points

It integrates with `TestVolumeOwnership` in `volume_copy_up_test.go` and depends on Unix `stat` and shell quoting behavior.

## Risks and Edge Cases

The path is interpolated into a shell single-quoted string, so paths containing single quotes would break quoting. Test-generated paths normally avoid that.

## Test Signals

The helper is indirectly tested by `TestVolumeOwnership` on non-Windows platforms.
