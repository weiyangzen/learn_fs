# sources/distributed-fs/openafs/src/afs/IRIX/osi_idbg.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_idbg.c

Purpose: implements IRIX IDBG debugger commands for inspecting AFS vcache, VFS list, and user/token state.

Important APIs/types/functions: `printflags`, `idbg_prafsnode`, `idbg_afsvfslist`, `idbg_pruser`, and `idbg_afsuser`. It uses `qprintf`, `VLRU`, `afs_calc_inum`, `VN_GET_PGCNT`, `afs_users`, `afs_FindToken`, and RXKAD token structures.

Control flow: debug entry points acquire `AFS_GLOCK`, print selected structures, and release the lock. `idbg_afsvfslist` walks the vcache LRU from tail to head and prints vnode type/ref/page/map/inode data. `idbg_afsuser` either dumps all hash buckets when passed `-1` or one specific `unixuser`.

State/persistence: read-only diagnostics over live kernel AFS state. No mutation except lock acquisition.

Dependencies/integration: registered by `Afs_init` in `osi_vfsops.c` via `idbg_addfunc`. Depends on IRIX IDBG and OpenAFS internal structure layout.

Risks/test signals: debug code can crash if handed stale pointers or if structure layouts drift. Token printing must avoid assuming a KAD token exists; this file checks for NULL. Test IDBG commands on active/inactive vcaches and users, with and without tokens.
