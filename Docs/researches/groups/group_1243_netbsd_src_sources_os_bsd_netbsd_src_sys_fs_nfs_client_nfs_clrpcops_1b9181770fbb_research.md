# Group Research: group_1243_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_client_nfs_clrpcops_1b9181770fbb

Scope checked against `Docs/research_subset_a.md`: the listed file is under `sources/os/bsd/netbsd-src`, which is included in subset A. The single listed source file was read completely, from line 1 through line 5929.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clrpcops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clrpcops.c

This file implements the NetBSD new NFS client RPC operation layer for NFSv2, NFSv3, NFSv4.0, and NFSv4.1/pNFS. It is the main protocol-marshalling companion to vnode and buffer-cache code: vnode operations call these entry points to build NFS requests, send them through `nfscl_request()`/`newnfs_request()`, decode replies, update weak-cache-consistency attributes, and coordinate NFSv4 state recovery.

Key entry points:
- Basic RPCs: `nfsrpc_null()`, `nfsrpc_access()`, `nfsrpc_accessrpc()`, `nfsrpc_getattr()`, and `nfsrpc_getattrnovp()` implement ping, access checks, and file-handle based attribute fetches.
- NFSv4 open/close state: `nfsrpc_open()`, `nfsrpc_openrpc()`, `nfsrpc_openconfirm()`, `nfsrpc_opendowngrade()`, `nfsrpc_close()`, `nfsrpc_doclose()`, and `nfsrpc_closerpc()` drive open-owner sequencing, open state IDs, delegation handling, delayed close, and close-time lock cleanup.
- Attribute and ACL mutation: `nfsrpc_setattr()`, `nfsrpc_setattrrpc()`, `nfsrpc_getacl()`, `nfsrpc_setacl()`, and `nfsrpc_setaclrpc()` send SETATTR/ACL requests, obtaining a usable NFSv4 stateid when needed.
- Namespace operations: `nfsrpc_lookup()`, `nfsrpc_readlink()`, `nfsrpc_mknod()`, `nfsrpc_create()`, `nfsrpc_createv23()`, `nfsrpc_createv4()`, `nfsrpc_remove()`, `nfsrpc_rename()`, `nfsrpc_link()`, `nfsrpc_symlink()`, `nfsrpc_mkdir()`, and `nfsrpc_rmdir()` implement lookup, creation, deletion, rename, hardlink, symlink, and directory creation/removal across protocol versions.
- Data I/O: `nfsrpc_read()`, `nfsrpc_readrpc()`, `nfsrpc_write()`, `nfsrpc_writerpc()`, and `nfsrpc_commit()` perform file reads, writes, unstable-write verifier tracking, and commit verification.
- Directory I/O: `nfsrpc_readdir()` and, outside Apple builds, `nfsrpc_readdirplus()` translate server directory entries into BSD `struct dirent` records with embedded NFS cookies and synthesize NFSv4 `.`/`..` entries.
- Locking: `nfsrpc_advlock()`, `nfsrpc_lockt()`, `nfsrpc_lock()`, `nfsrpc_locku()`, and `nfsrpc_rellockown()` implement POSIX byte-range lock test/set/unlock flows and lock-owner release/free-stateid behavior.
- Mount, lease, and filesystem metadata: `nfsrpc_setclient()`, `nfsrpc_renew()`, `nfsrpc_getdirpath()`, `nfsrpc_statfs()`, `nfsrpc_pathconf()`, and `nfsrpc_fsinfo()` manage client IDs, lease renewal, mount root file-handle lookup, statfs, pathconf, and fsinfo.
- NFSv4.1 session and pNFS: `nfsrpc_exchangeid()`, `nfsrpc_createsession()`, `nfsrpc_destroysession()`, `nfsrpc_destroyclient()`, `nfsrpc_reclaimcomplete()`, `nfsrpc_layoutget()`, `nfsrpc_getdeviceinfo()`, `nfsrpc_layoutcommit()`, `nfsrpc_layoutreturn()`, `nfsrpc_getlayout()`, `nfsrpc_fillsa()`, `nfscl_doiods()`, `nfscl_findlayoutforio()`, `nfscl_doflayoutio()`, `nfsrpc_readds()`, and `nfsrpc_writeds()` implement sessions, layouts, device-info discovery, DS connections, and direct data-server I/O.

Important behavior:
- The file is protocol-version aware throughout. NFSv2 uses older fixed-width offset/count forms, NFSv3 adds post-op and weak-cache-consistency attributes, NFSv4 builds compound operations with GETATTR/GETFH/PUTFH/SAVEFH/SEQUENCE-related behavior, and NFSv4.1 uses sessions instead of some NFSv4.0 confirmation/renew paths.
- NFSv4 stateful operations contain retry loops for grace, delay, stale client/state IDs, old state IDs, expired state, stale-dont-recover, and bad-session errors. Several paths call `nfscl_initiate_recovery()` or `nfscl_hasexpired()` and eventually collapse repeated recovery failures to `EIO`.
- Open/create paths parse read/write delegations, allocate `struct nfscldeleg`, store delegation stateids, size limits, ACE data, change attributes, and modification times, then pass delegations to `nfscl_deleg()`.
- Close-time cleanup releases byte-range locks before closing open state. For POSIX-lock servers it can unlock the whole file; for non-POSIX lock semantics it restricts server unlocks to whole-file locks.
- Write paths carefully roll back `uio` fields if an RPC reply reports failure after `nfsm_uiombuf()` consumed user data. Short writes adjust the `uio` and continue from the actual acknowledged length.
- Write and commit verifier handling updates mount or data-server verifiers and sets commit-required/stale-write-verifier state when the server verifier changes.
- NFSv4 WRITE compounds intentionally request a reduced attribute set that excludes owner/group to avoid name-mapping upcalls that could block behind dirty NFS buffers and cause near-deadlock.
- Directory reads maintain server cookies in the extra space after `d_name`, pad entries to `DIRBLKSIZ`, and mark EOF based on returned data, local buffer fullness, and server EOF flags.
- `nfsrpc_readdirplus()` can instantiate/cache vnodes from returned file handles and attributes, but deliberately skips `..` vnode acquisition to avoid lock-order problems.
- Several idempotency kludges exist for older protocol behavior: optional `vfs.nfs.ignore_eexist` maps retry-looking `EEXIST` from mkdir/symlink to success, and `nfsrpc_rmdir()` maps `ENOENT` to success as a retry reply assumption.

NFSv4.1 and pNFS details:
- `nfsrpc_exchangeid()` records server-owner identity, client ID, sequence ID, pNFS MDS/DS capability flags, and initializes session slot state.
- `nfsrpc_createsession()` requests fore/back channel parameters, optional persistent sessions, callback support, and stores negotiated slot counts and cache limits.
- `nfsrpc_fillsa()` connects to a data server address, performs ExchangeID/CreateSession for DS use, deduplicates sessions by address and by server owner, and links successful DS sessions into the mount session list.
- `nfsrpc_layoutget()` decodes file layout segments, validates layout type, offset/range, device IDs, stripe unit data, pattern offset, file-handle counts, and inserts accepted file-layout records in increasing offset order.
- `nfsrpc_getdeviceinfo()` decodes stripe indices and multipath address lists, prefers TCP addresses matching the MDS address family, creates or reuses DS sessions, and returns notify bits when supplied.
- `nfscl_doiods()` is the high-level pNFS data path: it obtains a client reference and stateid, acquires or fetches a matching layout, loops over layout ranges, chooses device info, and dispatches to data-server read/write helpers.
- `nfscl_doflayoutio()` maps logical file offsets onto dense or sparse file-layout stripes, chooses the data-server file handle, handles commit-through-MDS layout flags, and advances by stripe unit.

Concurrency and integration:
- The file is called from vnode operation code (`nfs_clvnops.c`), mount/statfs code (`nfs_clvfsops.c`), node lifecycle code (`nfs_clnode.c`), state recovery code (`nfs_clstate.c`), and buffer/page-cache code (`nfs_clbio.c`).
- It depends on common mbuf/XDR helpers from `nfs_clcomsubs.c` and wider NFS client state helpers such as `nfscl_open()`, `nfscl_getstateid()`, `nfscl_deleg()`, `nfscl_layout()`, `nfscl_adddevinfo()`, `nfscl_getlayout()`, `nfscl_rellayout()`, `nfscl_getbytelock()`, and `nfscl_relbytelock()`.
- Mount, client, node, data-server, and NFSv4 state locks are used via `NFSLOCKMNT`, `NFSLOCKNODE`, `NFSLOCKCLSTATE`, `NFSLOCKDS`, and NFSv4 lock/refcount wrappers.
- RPC descriptors must always free `nd_mrep` on success and most error exits. Many functions use `nfsmout` labels shared with XDR-dissection macros, so cleanup paths are part of normal control flow.

Research notes:
- This is the highest-value file for understanding how the NetBSD new NFS client turns local VFS operations into on-the-wire NFS compounds and how protocol errors drive client recovery.
- The most delicate correctness areas are NFSv4 sequence/stateid handling, open/delegation transitions, close-time lock release, write `uio` rollback, verifier/commit handling, directory cookie synthesis, and pNFS layout/device decoding.
- Security and robustness review should focus on XDR length/count validation, state recovery retry bounds, pNFS server-address selection, compound parsing after partial NFSv4 failures, and places that intentionally convert server errors to success for retry/idempotency compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clrpcops.c -->