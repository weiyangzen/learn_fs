# sources/distributed-fs/openafs/src/afs/UKERNEL/afs_usrops.h

## Purpose

`afs_usrops.h` declares the public libuafs user-operation API and the small doubly linked-list macros used by the UKERNEL wait queues. It is the consumer-facing header for `afs_usrops.c`.

## Important APIs, Types, and Functions

The header exposes `afs_cdir`, `afs_LclCellName`, and `afs_osicred_Initialized`, plus lifecycle APIs `uafs_InitThread`, `uafs_Setup`, `uafs_ParseArgs`, `uafs_Run`, `uafs_MountDir`, `uafs_mount`, `uafs_setMountDir`, `uafs_Shutdown`, and `uafs_RxServerProc`.

It declares path/attribute helpers `uafs_LookupName`, `uafs_LookupLink`, `uafs_LookupParent`, `uafs_GetAttr`, `uafs_afsPathName`, `uafs_IsRoot`, and `uafs_statmountpoint_r`; POSIX-like operations for directories, files, symlinks, links, renames, chmod, truncate, fsync, directory streams, access checks, and rights retrieval; token and PIOCTL-style helpers such as `uafs_SetTokens`, RPC stats toggles, and `call_syscall`.

The `DLL_INIT_LIST`, `DLL_INSERT_TAIL`, and `DLL_DELETE` macros manipulate intrusive doubly linked lists by named next/prev members.

## Control Flow

There is no executable control flow in this header. Its shape separates locking wrappers and `_r` variants: public non-`_r` functions acquire the AFS global lock in `afs_usrops.c`, while `_r` variants are intended for callers already inside the UKERNEL lock context.

## State and Persistence Behavior

The header itself owns no state. It defines external access to process-global libuafs state such as the config directory and local cell name. Persistence is entirely downstream in cache manager and host filesystem code.

## Dependencies and Integration Points

When compiled under `KERNEL`, the header includes `afs/sysincludes.h` and `afsincludes.h`, which provide the UKERNEL-renamed vnode, vattr, uio, and credential types. It is used by afsd glue, test programs, and any embedding application that drives libuafs.

## Risks and Edge Cases

The list macros are not type-safe, evaluate their arguments multiple times, and assume the element is present for deletion. The API exposes raw `char *`, integer descriptor, and `struct usr_vnode *` arguments, so ABI stability and caller-side lifetime rules matter.

## Test Signals

Build tests should ensure all declarations match `afs_usrops.c`, especially `_r` variants and platform-dependent structs. Integration tests should compile a small libuafs embedding program that includes this header and exercises setup, path lookup, file I/O, directory reads, token setup, and shutdown.
