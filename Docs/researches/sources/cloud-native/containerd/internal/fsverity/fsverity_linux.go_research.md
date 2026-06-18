# sources/cloud-native/containerd/internal/fsverity/fsverity_linux.go

## Purpose
Provides Linux fs-verity support detection, enablement, and enabled-state checks for files.

## Important APIs, Types, And Functions
`IsSupported(rootPath)` checks kernel version and attempts to enable fs-verity on a temp file under `rootPath`. `IsEnabled(path)` reads inode flags with `FS_IOC_GETFLAGS`. `Enable(path)` builds `fsverityEnableArg` and calls `FS_IOC_ENABLE_VERITY`.

## Control Flow
Support detection requires kernel >= 5.4 and successful enablement on a temp file. Enable chooses block size from page size and filesystem block size, then performs the ioctl.

## State And Persistence
`Enable` permanently marks a file fs-verity-enabled at the filesystem level. `IsSupported` creates and removes a temporary check directory/file.

## Dependencies And Integration Points
Uses kernelversion helpers, `unix` syscalls/ioctls, os/filesystem operations, and unsafe pointer syscall arguments. Integrates with content integrity workflows.

## Risks
Requires Linux kernel/filesystem support and appropriate privileges/capabilities. `Enable` opens files without deferring close in the current implementation, which is a file descriptor leak risk. Once enabled, file contents become immutable.

## Test Signals
`fsverity_test.go` runs root/ext4-dependent checks for enabling and reading enabled status.
