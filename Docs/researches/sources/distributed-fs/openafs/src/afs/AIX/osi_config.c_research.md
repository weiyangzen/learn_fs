# sources/distributed-fs/openafs/src/afs/AIX/osi_config.c

Purpose: AIX kernel module configuration and compatibility glue. It registers/unregisters the AFS GFS, pins code and locks, allocates the timeout callout table, initializes the OSI layer, and imports non-exported AIX kernel functions/variables through a "kluge" table.

Important APIs and functions: `afs_config` handles `CFG_INIT` and `CFG_TERM`; `kmem_alloc`, `kmem_free`, `VN_RELE`, and `VN_HOLD` provide common wrappers; `kluge_init` imports entries in `kfuncs` and `kvars`; wrappers such as `ufdalloc`, `fpalloc`, `ufdfree`, `ffree`, `iptovp`, `dev_ialloc`, `iget`, `iput`, `commit`, and debug lock wrappers call imported function pointers.

Control flow: on init, `afs_config` takes `AFS_GLOCK`, imports kernel symbols, pins the config routine, calls `gfsadd`, initializes `afs_callout_lock`, installs locked vnode ops, and calls `timeoutcf`. On termination it calls `gfsdel`, unpins resources where supported, and shrinks the callout table.

State and persistence: persistent kernel state includes `afs_gfs` registration, pinned lock storage, imported function pointers, imported kernel variables, and timeout table capacity.

Dependencies and integration: depends on `export.h` import helpers, `get_toc` assembly, AIX GFS/config APIs, timeout code, vnode ops, and global AFS locking.

Risks and test signals: symbol import is fragile across AIX kernel versions and 32/64-bit signatures. Failure modes are module load failure, bad function pointer calls, or leaked pinned resources. Test signals are successful `CFG_INIT`, mount availability, and clean `CFG_TERM`.
