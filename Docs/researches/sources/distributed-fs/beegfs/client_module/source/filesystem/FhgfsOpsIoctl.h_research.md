# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsIoctl.h

## Purpose
`FhgfsOpsIoctl.h` declares the BeeGFS ioctl entry points and defines compatibility ioctl command numbers for old kernel `FS_IOC_GETVERSION` variants. It is the narrow header that connects BeeGFS file operation tables to the ioctl implementation.

## Important APIs, Types, And Functions
- `BEEGFS_IOC_GETVERSION_OLD` maps to `FS_IOC_GETVERSION` when present or defines the old `_IOR('v', ...)` command manually.
- `BEEGFS_IOC32_GETVERSION_OLD` does the same for 32-bit compat mode when `CONFIG_COMPAT` is enabled.
- `FhgfsOpsIoctl_ioctl()` is the main unlocked ioctl callback.
- `FhgfsOpsIoctl_compatIoctl()` is the compat callback for 32-bit user space on 64-bit kernels.

## Control Flow
The header uses preprocessor feature checks to select existing kernel ioctl constants when available and local definitions otherwise. The implementation receives all other BeeGFS ioctl numbers from `uapi/beegfs_client.h`.

## State And Persistence Behavior
The header has no runtime state. Its constants preserve ABI behavior for older userspace and older kernels.

## Dependencies And Integration Points
It includes `asm/ioctl.h`, Linux kernel headers, BeeGFS `NumNodeID`, and the public BeeGFS client uapi header. It is consumed by file operation table setup and `FhgfsOpsIoctl.c`.

## Risks
Incorrect ioctl-number compatibility would break old tools, NFS/user-space filesystem generation checks, or 32-bit compat callers. Since only get-version compat is forwarded in `FhgfsOpsIoctl_compatIoctl()`, adding new compat-sensitive ioctls requires explicit updates.

## Test Signals
Builds on kernels with and without `FS_IOC_GETVERSION`, 32-bit compat ioctl smoke tests, and user-space `ioctl(GETVERSION)` regression tests validate this header.
