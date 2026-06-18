# sources/cloud-native/containerd/plugins/mount/erofs/plugin_linux_test.go

## Purpose
Integration-style tests for Linux EROFS mounting through loop devices and fsmount behavior.

## Important APIs, Types, And Functions
`TestFsmountLoopDevice` creates an EROFS image, attaches a loop device, mounts it with `fsmount`, and reads a file. `TestMountOptionsPageSizeLimit` demonstrates traditional mount option length failure and fsmount success.

## Control Flow
Tests require root, `mkfs.erofs`, kernel EROFS support, and fsmount support. They build temporary EROFS images from a directory, attach loop devices, mount under temp mount points, inspect file contents, and unmount/detach.

## State And Persistence
Uses temporary directories, loop devices, kernel mounts, and generated EROFS images. Cleanup closes loop files and unmounts where needed.

## Dependencies And Integration Points
Depends on `testutil.RequiresRoot`, `internal/fsmount`, core mount helpers, `plugins/snapshots/erofs.FindErofs`, `mkfs.erofs`, and Linux syscalls.

## Risks
Environment-sensitive skips mean CI without privileges/tooling misses coverage. Tests can leave mounts/loop devices if cleanup paths fail.

## Test Signals
Strong signal for privileged Linux fsmount and EROFS image readability, plus regression coverage for PAGE_SIZE option limit handling.
