# sources/distributed-fs/beegfs/client_module/source/filesystem/helper/IoctlHelper.h

## Purpose
Declares helper functions for BeeGFS ioctl create-file argument import and target-list conversion.

## Important APIs and Types
Exports three create-file copy helpers for ioctl ABI versions and `IoctlHelper_ioctlCreateFileTargetsToList()`. Includes `App`, `Config`, OS compatibility, superblock/helper/ioctl definitions, optional compat support, and Linux mount APIs.

## Control Flow
The header provides the boundary used by ioctl handlers: import userspace arguments into a V3-shaped kernel struct, then convert preferred target arrays into internal create info.

## State and Persistence
No owned state. Declared functions allocate output members whose lifetime is managed by their callers.

## Dependencies and Integration Points
Integrated with `FhgfsOpsIoctl` create paths and user-copy validation. Optional `CONFIG_COMPAT` support brings in compat and inode definitions.

## Risks
Callers must pass zero-initialized output structs and must free partial allocations. Missing that convention can leak or double-free.

## Test Signals
Compile ioctl handlers with and without `CONFIG_COMPAT`; run create-file ioctl tests covering all ABI versions and cleanup paths.
