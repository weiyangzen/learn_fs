# sources/cloud-native/containerd/plugins/snapshots/devmapper/blkdiscard/blkdiscard.go

## Purpose
This file wraps the Linux `blkdiscard` command for devmapper snapshot cleanup.

## Important APIs, Types, And Functions
`Version` runs `blkdiscard --version`, `CheckBinary` verifies the binary is on PATH, `BlkDiscard` discards all blocks for a device path, and private `blkdiscard` executes the command.

## Control Flow
All command wrappers use `exec.Command(...).CombinedOutput()` and return command output or error.

## State And Persistence
The wrapper can irreversibly discard blocks on the specified block device. It does not track state itself.

## Dependencies And Integration Points
`pool_device.go` uses this indirectly through `dmsetup.DiscardBlocks` when discard behavior is enabled.

## Risks
Callers must verify the device is correct and not in use. Errors are command errors without structured stderr wrapping in this package.

## Test Signals
No direct tests for this wrapper are included. `dmsetup_test.go` indirectly exercises discard behavior.
