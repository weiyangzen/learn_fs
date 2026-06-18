# sources/distributed-fs/openafs/src/WINNT/afsd/smb_ioctl.h

## Purpose
Declares the SMB pioctl transport interface and `smb_ioctl_t` per-FID state. It bridges SMB FIDs/users/virtual circuits, subst/TID path context, and cache-manager ioctl buffers.

## Important APIs, Types, And Functions
`smb_ioctl_t` stores owning `smb_fid`, current `smb_user`, TID path, subst prefix, and embedded `cm_ioctl_t`. `smb_ioctlProc_t` is the handler dispatch signature. Public functions cover initialization, ioctl FID setup, SMB core/V3/raw reads and writes, read preparation, path/parent parsing, token install, SMB name lookup, and handlers for ACLs, flushes, cells, sysname, server prefs, mountpoints, symlinks, rxkad, trace, ownership, Unix mode, verify data, and caller access.

## Control Flow
SMB open code calls `smb_SetupIoctlFid` for the magic pseudo-file. SMB receive paths route read/write calls to these functions; `smb_InitIoctl` connects VIOC opcode constants to handler declarations.

## State And Persistence
The header defines only transient pointer/buffer state. Persistence happens in `smb_ioctl.c` and delegated `cm_Ioctl*` handlers. Prefix and TID path fields are essential for path-relative pioctls.

## Dependencies And Integration Points
Includes `cm_ioctl.h` and `smb_iocons.h`, forward-declares SMB structures, and exposes cache flush helpers used by nearby SMB/cache code.

## Risks
Prototype and dispatch-table drift can break handlers. `smb_ioctl_t` owns several borrowed/allocated pointers, so cleanup must preserve lifetimes. Handler signatures expose raw mutable buffers and rely on disciplined length checks.

## Test Signals
Compile signature checks, successful dispatch of every registered opcode, repeated open/write/read/close leak checks, and path-relative pioctl tests validate this header.
