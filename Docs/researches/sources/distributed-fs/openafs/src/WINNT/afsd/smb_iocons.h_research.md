# sources/distributed-fs/openafs/src/WINNT/afsd/smb_iocons.h

## Purpose
Shared constant header for Windows AFS pioctl operations used by afsd and command-line tools. It assigns stable VIOC opcode numbers, common payload structures, the magic ioctl pseudo-file name, and maximum pioctl sizes.

## Important APIs, Types, And Functions
Defines `chservinfo_t`, `gaginfo`, `ClearToken`, `sbstruct`, gag/cell/newcell flags, VIOC opcodes from `VIOC_FILE_CELL_NAME` through `VIOC_GETCALLERACCESS`, and test opcode `VIOC_VOLSTAT_TEST`. The magic pseudo-file names are `CM_IOCTL_FILENAME` and wide/no-slash variants. `CM_IOCTL_MAXDATA` is 16 KiB and `CM_IOCTL_MAXPROCS` is 64.

## Control Flow
No executable flow. Clients write an opcode plus payload to the magic SMB file; `smb_ioctl.c` treats the opcode as an index into `smb_ioctlProcsp`.

## State And Persistence
No direct state, but constants gate token installation/deletion, ACL changes, cache flushes, cell config, symlink and mountpoint operations, rxkad settings, owner/mode updates, and caller access queries.

## Dependencies And Integration Points
Included by `smb_ioctl.h`, afsd code, and user tools. Must match cache-manager `cm_Ioctl*` handlers and pioctl encoders.

## Risks
Opcode ABI drift breaks existing tools. Duplicate or out-of-range values misdispatch or fail. Payload structs are raw C ABI without self-description.

## Test Signals
Run all `fs`/`symlink` pioctl commands, invalid opcode tests, token payload validation, and max-size payload checks around 16 KiB.
