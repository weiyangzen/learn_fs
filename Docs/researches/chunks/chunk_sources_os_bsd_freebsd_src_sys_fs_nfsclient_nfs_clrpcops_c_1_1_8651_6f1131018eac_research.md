# Chunk Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clrpcops.c lines 1-8651

## Scope

This report covers `sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clrpcops.c` lines 1-8651 for subset A (`Docs/research_subset_a.md`). The chunk contains the beginning and bulk of the FreeBSD NFS client RPC operation layer for NFSv2, NFSv3, NFSv4.0, NFSv4.1, NFSv4.2, and pNFS client data-server I/O. It spans ordinary vnode-facing RPC wrappers, lower-level XDR builders/parsers, NFSv4 client/open/lock/delegation/session setup, directory enumeration, ACLs, layout/device handling, and pNFS file/flex-file read/write/commit paths. The chunk ends inside `nfsrpc_createlayout()` immediately after emitting the NFSv4 `OPEN` claim type `NFSV4OPEN_CLAIMNULL`; parsing and cleanup for this create+layout compound continue in the next chunk.

## Public And Internal APIs Covered

- Basic RPC entry points: `nfsrpc_null()`, `nfsrpc_access()`, `nfsrpc_accessrpc()`, `nfsrpc_getattr()`, `nfsrpc_getattrnovp()`, `nfsrpc_setattr()`, and the internal `nfsrpc_setattrrpc()`.
- NFSv4 open/close state APIs: `nfsrpc_open()`, `nfsrpc_openrpc()`, `nfsrpc_opendowngrade()`, `nfsrpc_close()`, `nfsrpc_doclose()`, `nfsrpc_closerpc()`, `nfsrpc_openconfirm()`, and `nfsrpc_setclient()`.
- Lookup and namespace APIs: `nfsrpc_lookup()`, `nfsrpc_readlink()`, `nfsrpc_mknod()`, `nfsrpc_create()`, `nfsrpc_createv23()`, `nfsrpc_createv4()`, `nfsrpc_remove()`, `nfsrpc_rename()`, `nfsrpc_link()`, `nfsrpc_symlink()`, `nfsrpc_mkdir()`, `nfsrpc_rmdir()`, and `nfscl_invalidfname()`.
- Data I/O APIs: `nfsrpc_read()`, `nfsrpc_readrpc()`, `nfsrpc_write()`, `nfsrpc_writerpc()`, `nfsrpc_commit()`, `nfsrpc_deallocate()`, `nfsrpc_deallocaterpc()`, `nfsrpc_allocate()`, `nfsrpc_allocaterpc()`, and `nfsrpc_advise()`.
- Directory APIs: `nfsrpc_readdir()` and `nfsrpc_readdirplus()`, including NFSv4 synthetic dot/dotdot generation and optional name-cache population from readdirplus results.
- Locking APIs: `nfsrpc_advlock()`, `nfsrpc_lockt()`, `nfsrpc_locku()`, `nfsrpc_lock()`, and `nfsrpc_rellockown()`.
- Filesystem metadata APIs: `nfsrpc_statfs()`, `nfsrpc_pathconf()`, `nfsrpc_fsinfo()`, `nfsrpc_renew()`, `nfsrpc_getdirpath()`, `nfsrpc_delegreturn()`, `nfsrpc_getacl()`, `nfsrpc_setacl()`, and `nfsrpc_setaclrpc()`.
- NFSv4.1 session/client APIs: `nfsrpc_exchangeid()`, `nfsrpc_createsession()`, `nfsrpc_destroyclient()`, `nfsrpc_reclaimcomplete()`, `nfscl_initsessionslots()`, `nfscl_freenfsclds()`, and `nfscl_getsameserver()`.
- pNFS layout and DS APIs: `nfsrpc_layoutget()`, `nfsrpc_getdeviceinfo()`, `nfsrpc_layoutcommit()`, `nfsrpc_layoutreturn()`, `nfsrpc_layouterror()`, `nfsrpc_getlayout()`, `nfsrpc_fillsa()`, `nfscl_doiods()`, `nfscl_findlayoutforio()`, `nfscl_doflayoutio()`, `nfscl_dofflayoutio()`, `nfsrpc_readds()`, `nfsrpc_writeds()`, `nfsrpc_writedsmir()`, `nfsio_writedsmir()`, `start_writedsmir()`, `nfsrpc_commitds()`, `nfsio_commitds()`, and `start_commitds()`.
- Layout parsing helpers: `nfsrv_setuplayoutget()`, `nfsrv_parselayoutget()`, `nfsrv_parseug()`, `nfsrpc_getopenlayout()`, `nfsrpc_openlayoutrpc()`, and the first half of `nfsrpc_createlayout()`.

## Control Flow And Behavior

Most public vnode-facing routines are wrappers around lower-level RPC builders. For NFSv4 they first acquire a usable stateid via client/open/lock state helpers, perform the RPC, translate recovery-sensitive server errors, release state references, and retry around grace, delay, stale state, old state, bad session, expired client ID, and selected bad stateid cases.

`nfsrpc_open()` only performs NFSv4 opens for regular files. It computes access and delegation request bits, gets or creates local open state, optionally tries an open+layout compound for pNFS, installs returned delegations, increments local open counts only after success, and retries on recovery errors. `nfsrpc_doclose()` releases outstanding byte-range locks, sends `LOCKU` and `ReleaseLockOwner`/`FreeStateID`, then serializes close against the open owner rwlock.

Read/write wrappers split large I/O into negotiated `nm_rsize`/`nm_wsize` chunks. Write validates one-iovec input, optionally implements NFSv4 append by verifying file size first, rolls back `uio` fields on retryable reply errors, tracks the lowest commitment level, updates write verifiers, and deliberately avoids owner/group attributes in write GETATTR to avoid user/group mapping upcall deadlocks.

Directory enumeration converts wire entries into 4BSD `struct dirent` records, storing opaque NFS cookies after `d_name`. `readdir` and `readdirplus` only return full `DIRBLKSIZ` chunks or unchanged residual at EOF, synthesize NFSv4 dot/dotdot entries, validate server-supplied names, maintain cookie verifiers, and fill empty records to complete directory blocks.

pNFS control flow starts with layout/device discovery. `nfsrpc_getdeviceinfo()` parses file-layout stripe indices or flex-file address/version lists, chooses TCP endpoints, selects supported DS protocol versions, and connects through `nfsrpc_fillsa()`. `nfscl_doiods()` checks pNFS eligibility, pins the client, obtains an I/O stateid, finds or fetches a layout, selects file-layout or flex-file I/O, reports DS errors through layout error mechanisms, updates layout state, and rolls back `uio` state for mirrored write retry failures.

## State And Data Structures

- Global/sysctl state includes `vfs.nfs.ignore_eexist`, `vfs.nfs.dssameconn`, `vfs.nfs.maxcopyrange`, `nfs_exchangeboot`, `nfstest_outofseq`, `nfscl_assumeposixlocks`, `nfscl_enablecallb`, `nfsv4_cbport`, and `nfstest_openallsetattr`.
- Per-mount state includes protocol version, minor version, mount flags, max file size, rsize/wsize/readdir size, write verifier, root file handle, mount socket request, session list, client pointer, pNFS/flex-file flags, persistent-session state, case-insensitive state, and fake-root handling.
- Per-node state includes file handles, NFSv4 parent/name data, cached attributes, cookie verifier, open state pointer, named-attribute flags, local modification time, layout disable flag `NNOLAYOUT`, DS commit flag `NDSCOMMIT`, and write-opened state.
- NFSv4 state structures include `struct nfsclclient`, `struct nfsclsession`, `struct nfsclds`, `struct nfsclowner`, `struct nfsclopen`, `struct nfscllockowner`, `struct nfscllock`, `struct nfscldeleg`, and `nfsv4stateid_t`.
- pNFS layout state includes `struct nfscllayout`, `struct nfsclflayout`, `struct nfscldevinfo`, per-file layout file handles, flex-file mirrors, device IDs, stripe indices, layout ranges, layout stateid, mirror count, version index, DS address slots, and per-layout written/lastbyte state.

## Dependencies

- Kernel/VFS dependencies include vnodes, mounts, credentials, UIO/iovec, `struct dirent`, `struct flock`, namecache helpers, vnode references/locks, ACL types, POSIX advice constants, socket addresses, taskqueue tasks, sysctls, mbufs, mutexes, sleeps/wakeups, and FreeBSD RPC client control paths.
- NFS client dependencies include `nfscl_reqstart()`, `NFSCL_REQSTART`, `nfscl_request()`, `newnfs_request()`, `newnfs_connect()`, `newnfs_disconnect()`, `nfs_catnap()`, `nfscl_hasexpired()`, `nfscl_initiate_recovery()`, `nfscl_getstateid()`, `nfscl_open()`, `nfscl_getlayout()`, and XDR conversion helpers.
- pNFS dependencies include layout/device caches, DS error reporting, `nfsv4_getipaddr()`, `nfs_pnfsio()`, `nfs_pnfsiothreads`, reconnect backchannel binding, and optional RPCSEC_GSS service-principal conversion.

## Risks And Invariants

- XDR parsing is manually offset-driven. Correctness depends on exact compound operation ordering, `ND_NOMOREDATA` propagation, and bounded length/count validation.
- NFSv4 sequence IDs and stateids are fragile. Open owner, lock owner, open stateid, lock stateid, delegation stateid, layout stateid, and session sequencing are updated only after specific outcomes.
- Write paths mutate `uio` while constructing mbufs and must roll it back on server-side failure or mirrored retry. Mirrored DS writes treat short writes as I/O errors.
- Directory enumeration assumes system-space, single-iovec, `DIRBLKSIZ`-aligned buffers and private cookie storage after `d_name`.
- pNFS DS session reuse depends on matching IP address, server owner, DS/MDS flags, defunct state, and `vfs.nfs.dssameconn`.
- Layout/device parsers bound server-supplied counts to avoid unbounded allocation; partial allocation paths must free layout/device structures and file handles.
- Several duplicate-retry compatibility behaviors are sysctl/protocol scoped: symlink and mkdir can map `EEXIST` to success, and rmdir maps `ENOENT` to success.

## Cross-Chunk References

- This chunk ends inside `nfsrpc_createlayout()` at line 8651. The next chunk emits the name and remaining `SAVEFH`/`GETFH`/`GETATTR`/`RESTOREFH`/`LAYOUTGET` compound, sends it, parses state/delegation/layout replies, installs open state, and cleans up.
- Definitions after line 8651 include `nfsrpc_getcreatelayout()`, `nfsrpc_layoutgetres()`, `nfsrpc_copyrpc()`, `nfsrpc_clonerpc()`, `nfsrpc_seekrpc()`, `nfsm_split()`, and `nfscl_statfs()`. This chunk already calls several of those, so the final merge should connect those definitions back to these call sites.
- Later same-file code covers NFSv4.2 copy/clone/seek and mbuf splitting, complementing allocate/deallocate/advise and pNFS data paths covered here.