# Group Research: group_1249_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_server_nfs_nfsdserv_95636625ab9e

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdserv.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdserv.c

Implements the protocol-level service routines for NetBSD's new kernel NFS server. Each routine decodes request XDR from `struct nfsrv_descript`, validates protocol-specific arguments, performs permission/state checks, calls lower `nfsvno_*` VFS wrappers or NFSv4 state helpers, and appends the XDR reply. The file covers NFSv2, NFSv3, NFSv4.0, and parts of NFSv4.1.

The NFSv2/v3 filesystem operations include access, getattr, setattr, lookup, readlink, read, write, create, mknod, remove/rmdir, rename, link, symlink, mkdir, commit, statfs, fsinfo, and pathconf. NFSv3 weak cache consistency data is collected around mutating directory operations through pre/post attributes and `nfsrv_wcc()`.

NFSv4 support is much broader and stateful. The file implements byte-range locking (`LOCK`, `LOCKT`, `LOCKU`), open lifecycle (`OPEN`, `CLOSE`, `OPEN_CONFIRM`, `OPEN_DOWNGRADE`), delegation return/purge, `GETFH`, `SECINFO`, `VERIFY`/`NVERIFY`, client identity and lease operations (`SETCLIENTID`, `SETCLIENTID_CONFIRM`, `RENEW`, `RELEASE_LOCKOWNER`), and NFSv4.1 session/client operations (`EXCHANGE_ID`, `CREATE_SESSION`, `SEQUENCE`, `RECLAIM_COMPLETE`, `DESTROY_CLIENTID`, `DESTROY_SESSION`, `FREE_STATEID`). Unsupported operations are routed through `nfsrvd_notsupp()`.

The vnode ownership model is central. Most handlers receive a locked vnode from the dispatcher and must release it with `vput()`, `vrele()`, or `NFSVOPUNLOCK()` depending on whether the operation consumes the current file handle, returns a new current file handle to NFSv4 compound processing, or only needs an unlocked reference. Creation helpers `nfsrvd_symlinksub()` and `nfsrvd_mkdirsub()` share vnode/fh/attribute reply construction between NFSv3 and NFSv4 create paths.

NFSv4 attribute handling uses attrbit parsing and reply bitmaps. `GETATTR` rejects write-only set-time attributes, checks ACL/attribute read permissions, handles referrals, supports filehandle attributes, and accounts for cross-mount `mounted_on_fileid`. `SETATTR` validates stateids and uid/gid, then applies owner/group, size, time, mode, and ACL changes in phases so partial failure can return an accurate attribute bitmap.

Read/write paths validate regular-file type, clamp requested transfer sizes, check owner/strict export access, enforce NFSv4 stateids through `nfsrv_lockctrl()`, and construct version-specific replies. Writes return the server boot-time verifier and can report FILESYNC even for unstable writes when the `vfs.nfsd.async` sysctl is enabled, which is explicitly called out as crash-loss risk in the source.

Important dependencies include `nfsport.h`, mbuf/XDR macros (`NFSM_DISSECT`, `NFSM_BUILD`, `nfsm_*`), vnode/export helpers from the NFS server port layer (`nfsvno_namei`, `nfsvno_getattr`, `nfsvno_setattr`, `nfsvno_read`, `nfsvno_write`, `nfsvno_getfh`, `nfsvno_accchk`, etc.), NFSv4 state helpers (`nfsrv_openctrl`, `nfsrv_openupdate`, `nfsrv_lockctrl`, `nfsrv_setclient`, `nfsrv_getclient`, `nfsrv_checksequence`, `nfsrv_delegupdate`), ACL support under `NFS4_ACL_EXTATTR_NAME`, root export checks, and global server state such as `nfsboottime`, `nfs_rootfhset`, and `nfsrv_statehashsize`.

Notable risk areas are decode-error cleanup, mixed locked/unlocked vnode references, manual path-buffer and ACL allocation lifetimes, NFSv4 clientid consistency across compound/session context, partial `SETATTR` reply bitmap correctness, delegation/open-owner sequence updates even on errors, write verifier semantics under async mode, and root-export security checks for client/session control operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdserv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdsocket.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdsocket.c

Provides the server-side RPC dispatch layer for the new NFS server. Despite the filename, this file is not low-level socket I/O; it owns procedure dispatch tables, operation classification, statistics accounting, NFSv2/v3 RPC dispatch, and the NFSv4 compound interpreter that calls into `nfs_nfsdserv.c`.

The top-level dispatch tables split procedures by argument and file-handle shape. `nfsrv3_procs0`, `nfsrv3_procs1`, and `nfsrv3_procs2` dispatch NFSv2/v3-style operations that use the current file handle, return a new file handle, or use two file handles. `nfsrv4_ops0`, `nfsrv4_ops1`, and `nfsrv4_ops2` do the same for NFSv4 operations, with many unsupported NFSv4.1/pNFS-related operations mapped to `nfsrvd_notsupp()`.

Static classification tables mark non-idempotent requests for duplicate reply caching, filesystem-modifying requests for write coordination, operations that return file handles, and NFSv3-to-NFSv4 statistic IDs. `nfsrvd_statstart()` and `nfsrvd_statend()` update global `nfsstatsv1` counters, byte totals, operation counts, duration, and server busy time under `nfsrvd_statmtx`.

`nfsrvd_dorpc()` is the main dispatcher for non-compound requests and the entry point for NFSv4 compounds. For NFSv2/v3 it decodes the first file handle, resolves it to a vnode/export record with `nfsd_fhtovp()`, chooses shared locks for read-like procedures and exclusive locks for mutating ones, sets duplicate-cache save flags for non-idempotent operations, writes the reply header, calls the appropriate procedure table, finishes write sections, maps errors, and suppresses reply caching for transient or state-sensitive errors.

`nfsrvd_compound()` implements the NFSv4 compound state machine. It emits the reply tag and operation count placeholder, validates the minor version, iterates sub-operations, tracks the current file handle and saved file handle as vnode references plus export metadata, directly handles `PUTFH`, `PUTPUBFH`, `PUTROOTFH`, `SAVEFH`, and `RESTOREFH`, enforces NFSv4.1 `SEQUENCE` placement/session rules, checks referrals and wrong-security cases, coordinates `vn_start_write()`/`vn_finished_write()` for modifying operations, and dispatches to the NFSv4 operation tables.

The compound path also coordinates global NFSv4 state. Before executing operations it obtains or waits on `nfsv4rootfs_lock`, updates stable storage after grace-period transitions, revokes expired clients, removes expired client structures, and throws away stale open owners when flagged. It releases current/saved vnode references and the NFSv4 root reference on all exits.

Important dependencies include the service handlers in `nfs_nfsdserv.c`, operation metadata from `nfsv4_opflag[]`, file-handle/export helpers (`nfsrv_mtofh`, `nfsd_fhtovp`, `nfsvno_checkexp`, `nfsd_excred`), duplicate request state in `nd->nd_rp`, `nfsstatsv1`, vnode/mount write coordination, NFSv4 root/state locks, stable restart-file management, and client hash tables.

Notable risk areas are dispatch-table index alignment with protocol op numbers, NFSv4.1 sequence/session rule enforcement, current/saved file-handle reference balance, cross-mount export transitions, security flavor exceptions needed during NFSv4 mount traversal, memory-pressure replies, and avoiding duplicate-cache persistence for errors that would break state replay semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdsocket.c -->