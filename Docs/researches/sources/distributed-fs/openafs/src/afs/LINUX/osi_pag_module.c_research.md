# sources/distributed-fs/openafs/src/afs/LINUX/osi_pag_module.c

## Purpose
This file implements a standalone Linux kernel module for OpenAFS PAG management without the full filesystem client. It initializes syscall/ioctl/proc support, starts the PAG manager, and provides stubs for NFS translator symbols needed by shared code.

## Important APIs, types, and functions
- Module parameters `nfs_server_addr` and `this_cell` configure standalone PAG manager behavior.
- Globals: `afs_global_lock`, `openafs_procfs`, `afs_global_owner`, and optional `afs_ns`.
- `afspag_init` is the standalone module init function.
- `afspag_cleanup` is the standalone module exit function.
- Stub `osi_linux_nfs_initreq` always denies with `EACCES`.
- Stub `afs_nfsclient_reqhandler` returns `EINVAL`.

## Control flow and behavior
Initialization records the current user namespace if applicable, calls `osi_Init`, installs syscall support, creates `/proc/fs/openafs` or equivalent based on `proc_root_fs` availability, installs the ioctl endpoint, initializes `afspag` with the configured NFS server address, and optionally sets the primary cell. Cleanup removes syscall hooks, frees tracked allocations, removes the ioctl entry and proc directory, and returns.

## State and persistence
State is limited to module globals, procfs entries, syscall hooks, allocator state, and PAG manager state initialized by `afspag_Init`. There is no filesystem registration or disk cache state.

## Dependencies and integration points
The standalone module shares OSI/syscall/ioctl/proc and PAG code with the full Linux module but does not initialize the AFS filesystem, inode cache, pagecopy thread, keyring hooks, or NFS translator. The NFS stubs satisfy references from common initialization code that is not actually reached.

## Risks
Init does not check `proc_mkdir` or `osi_ioctl_init` success. Cleanup order calls `osi_linux_free_afs_memory` before `osi_ioctl_clean`, so any unexpectedly live ioctl/proc user would be risky. The stubs deliberately deny NFS translator behavior; accidental use in a translator context would fail.

## Test signals
Load/unload the standalone PAG module, verify proc/ioctl endpoint creation/removal, run PAG creation/query user tools, test `this_cell` and `nfs_server_addr` parameters, and ensure no filesystem registration side effects occur.
