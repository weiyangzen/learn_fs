# sources/distributed-fs/openafs/src/vol/namei_ops.c

## Purpose
Implements the OpenAFS NAMEI backend, where vice "inodes" are represented as regular filesystem paths under the partition's `AFSIDat` tree instead of raw filesystem inodes. It maps `IHandle_t` values to platform-specific paths, creates and removes data files/directories, stores/reconstructs inode metadata, maintains synthetic link counts in a link-table special file, lists files for salvage, supports copy-on-write/hardlink replacement on Unix, and converts read-only volume storage into read-write volume storage for recovery workflows.

## Important APIs, Types, And Functions
Public entry points include `namei_iread`, `namei_iwrite`, `namei_HandleToName`, `namei_ViceREADME`, `namei_MakeSpecIno`, `namei_icreate`, `namei_icreate_init`, `namei_iopen`, `namei_dec`, `namei_inc`, `namei_replace_file_by_hardlink`, `namei_GetLinkCount`, `namei_SetLinkCount`, `ListViceInodes`, `namei_ListAFSFiles`, `namei_ConvertROtoRWvolume`, `PrintInode`, `namei_SetWorkQueue`, and `namei_RemoveDirectories`. Important internal helpers are `namei_HandleToInodeDir`, `namei_HandleToVolDir`, `namei_CreateDataDirectories`, `namei_RemoveDataDirectories`, `GetFreeTag`, `DecodeVolumeName`, `DecodeInode`, `_namei_examine_special`, `_namei_examine_reg`, and `namei_ListAFSSubDirs`.

## Control Flow
Normal file access starts with an `IHandle_t`; `namei_HandleToName` derives the full path from partition id, RW volume id, vnode number, uniquifier, special-file type, and link-table tag. `namei_icreate` allocates a tag, creates missing directories on `ENOENT`/`ENOTDIR`, opens the data file `O_CREAT|O_EXCL`, writes hidden metadata into Unix owner/group/mode bits or NT file creation time, and initializes link-count state. `namei_dec` decrements a synthetic link count and only unlinks data when it reaches zero; special inodes are validated and unlinked directly, with the link-table special inode removed only after its own count reaches zero. Salvage enumeration processes special files first so the link table is available before regular vnode files are decoded.

## State And Persistence
Persistent state is the `AFSIDat` hierarchy, encoded data-file names, special inode files, hidden file metadata, the link-table special file, and optional README warning files. Link counts are stored as 3-bit columns in 2-byte rows offset by vnode number after an 8-byte stamp area. Runtime state includes optional salvage work-queue TLS, a global link-count mutex in threaded builds, NT zero-link-count cleanup lists, and diagnostic globals such as `Testing` and `big_vno`.

## Dependencies And Integration Points
This file is active only under `AFS_NAMEI_ENV` and integrates with `ihandle`, vnode/volume metadata, partition id helpers, `viceinode.h`, `voldefs.h`, FSSYNC notifications during RO-to-RW conversion, and salvage code through `ListViceInodes`. `nuke.c`, `purge.c`, salvager code, volume creation, cloning, and vnode I/O all depend on its inode-compatible API.

## Risks And Test Signals
High-risk areas are path encoding compatibility, concurrent link-table updates, 3-bit link-count overflow, hidden metadata corruption, zero-link-count cleanup, crash windows between file creation and link-table updates, and directory removal races. Useful tests include NAMEI volume create/delete, clone/release/purge, salvager list and repair passes, link-count overflow/error injection, misplaced-file salvage detection, RO-to-RW conversion, and concurrent salvageserver scans.
