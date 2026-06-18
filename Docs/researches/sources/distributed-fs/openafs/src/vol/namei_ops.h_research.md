# sources/distributed-fs/openafs/src/vol/namei_ops.h

## Purpose
Declares the public NAMEI backend interface used by the OpenAFS volume package when `AFS_NAMEI_ENV` is enabled. It exposes file-style wrappers, inode creation/open/read/write/link-count operations, salvage listing hooks, path-construction helpers, RO-to-RW conversion, hardlink replacement, work-queue integration for the online salvager, and directory cleanup.

## Important APIs, Types, And Functions
The main API surface includes `namei_fdopen`, `namei_unlink`, `namei_MakeSpecIno`, `namei_icreate`, `namei_icreate_init`, `namei_iopen`, `namei_irelease`, `namei_iread`, `namei_iwrite`, `namei_dec`, `namei_inc`, `namei_GetLinkCount`, `namei_SetLinkCount`, `namei_ViceREADME`, `namei_FixSpecialOGM`, `namei_ListAFSFiles`, `ListViceInodes`, `namei_HandleToName`, `namei_ConvertROtoRWvolume`, `namei_replace_file_by_hardlink`, `namei_SetWorkQueue`, and `namei_RemoveDirectories`. It defines platform-specific `namei_t` path buffers for NT and Unix.

## Control Flow
Callers generally use `IH_*` and `FDH_*` macros that resolve to these functions in NAMEI builds. Creation flows allocate an inode with `namei_icreate` or `namei_icreate_init`, open it with `namei_iopen`, read/write through `namei_iread` and `namei_iwrite`, and release storage with `namei_dec`. Salvage flows call `ListViceInodes` or `namei_ListAFSFiles` to enumerate encoded files and produce `ViceInodeInfo` records.

## State And Persistence
The header defines no storage itself, but it defines path buffer lengths and component layouts that must be large enough for persistent NAMEI paths. `NAMEI_PATH_LEN` and component constants are part of the ABI between path construction, listing, purge/nuke, and salvage repair code.

## Dependencies And Integration Points
The declarations depend on `nfs.h`, `viceinode.h`, volume/inode handle types, and `afs/work_queue.h` when `AFS_SALSRV_ENV` is present. This header is included by partition discovery, volume operations, purge/nuke, salvager, and any module needing NAMEI-specific path or link-table operations.

## Risks And Test Signals
Risks are declaration drift against `namei_ops.c`, path buffer truncation if the layout changes, and accidental use outside `AFS_NAMEI_ENV`. Compile coverage for NAMEI Unix, NAMEI NT, and online-salvager builds is the primary signal, with runtime checks around generated path length and salvage enumeration.
