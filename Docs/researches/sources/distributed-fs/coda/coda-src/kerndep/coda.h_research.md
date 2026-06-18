# sources/distributed-fs/coda/coda-src/kerndep/coda.h

## Purpose
User/kernel ABI header for Coda filesystem communication, shared by userland tools, Venus, and kernel-facing code.

## APIs, Types, and Functions
Defines Coda limits, open/access flags, `venus_dirent`, `CodaFid`, `coda_f2i()`, vnode attribute types, `coda_statfs`, opcode constants, upcall/downcall macros, `CODA_KERNEL_VERSION`, input/output message structs for root/open/store/release/close/ioctl/getattr/setattr/access/lookup/create/remove/link/rename/mkdir/rmdir/readdir/symlink/readlink/fsync/vget/statfs/access-intent, unions `inputArgs`, `outputArgs`, `coda_downcalls`, `ViceIoctl`, `PioctlData`, control-file constants, and mount data.

## Control Flow, State, and Persistence
No runtime flow beyond inline `coda_f2i()`, which hashes a four-word Coda FID to an inode number. The structs define persistent ABI layout for messages exchanged with Venus and ioctl/pioctl payloads.

## Dependencies and Integration
Depends on platform type definitions and ioctl macros. It underpins `pioctl.h`, directory conversion to `venus_dirent`, repair tools, and Coda kernel/Venus protocol compatibility.

## Risks and Test Signals
Risks include ABI/layout sensitivity, platform conditional type definitions, fixed max message/data sizes, pointer placeholders in wire structs, and kernel version compatibility. Test signals are kernel/Venus communication success, correct dirent parsing, pioctl payload size compatibility, and cross-platform builds.
