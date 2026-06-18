# sources/distributed-fs/beegfs/client_module/source/filesystem/helper/IoctlHelper.c

## Purpose
Copies and validates BeeGFS create-file ioctl arguments from userspace across ABI versions and converts preferred target arrays into internal lists.

## Important APIs and Functions
`IoctlHelper_ioctlCreateFileCopyFromUser()`, `V2()`, and `V3()` normalize older user structs into `BeegfsIoctl_MkFileV3_Arg`. `IoctlHelper_ioctlCreateFileTargetsToList()` converts a zero-terminated target array to a `UInt16List`. The `STRDUP_OR_RETURN` macro copies userspace strings with length validation and `strndup_user()`.

## Control Flow
Each copy function copies the fixed userspace struct, manually assigns scalar fields into the output struct to preserve null pointers for cleanup, duplicates required path/name strings, optionally duplicates symlink targets, validates preferred-target byte length against `numTargets + 1`, copies the raw target array, and checks the terminating zero. V1 and V2 fill newer fields with defaults; V3 preserves `storagePoolId`.

## State and Persistence
State is transient kernel allocations inside `outFileInfo` and `outCreateInfo`. Caller owns cleanup even on partial failure. Persistent effects occur later in create-file ioctl handlers, not here.

## Dependencies and Integration Points
Depends on ioctl ABI structs from `FhgfsOpsIoctl.h`, `CreateInfo`, `UInt16List`, `Logger`, storage pool constants, and user-copy helpers. It feeds file creation logic with validated kernel-owned data.

## Risks
On early error after some strings/arrays were allocated, caller must free partial output exactly as documented. Arithmetic `(numTargets + 1) * sizeof(uint16_t)` uses signed/int fields and should be tested for overflow or negative values from malformed userspace. `prefTargetsLen` can be larger than needed and drives `memdup_user()`. Mid-array zero is rejected during list conversion, after copy succeeds.

## Test Signals
Ioctl ABI tests for V1/V2/V3, missing/zero string lengths, invalid userspace pointers, symlink and non-symlink paths, insufficient/unbounded `prefTargetsLen`, missing terminator, zero target in middle, storage pool ID preservation, and cleanup after every partial failure.
