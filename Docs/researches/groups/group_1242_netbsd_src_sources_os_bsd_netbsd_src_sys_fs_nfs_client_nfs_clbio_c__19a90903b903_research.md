# Group Research: group_1242_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_client_nfs_clbio_c__19a90903b903

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/netbsd-src`, which is included in subset A. All eight listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clbio.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clbio.c

This file implements the NetBSD new NFS client’s buffer-cache, VM pager, direct I/O, read-ahead, write-behind, commit, and truncation paths. It is the central data-movement layer between vnode/page-cache operations and NFS RPC routines such as `ncl_readrpc()`, `ncl_writerpc()`, `ncl_commit()`, `ncl_readdirrpc()`, `ncl_readdirplusrpc()`, and `ncl_readlinkrpc()`.

Key entry points:
- `ncl_getpages()` services VM page faults by mapping requested pages through a pbuf KVA window, issuing an NFS read RPC, and marking only returned bytes valid.
- `ncl_putpages()` writes dirty VM pages through `ncl_writerpc()`, choosing unstable or filesync mode from pager sync flags and preserving dirty pages on error when configured.
- `ncl_bioread()` handles cached reads for regular files, symlinks, and directories, including cache-consistency checks, readahead, directory EOF state, and `NFSERR_BAD_COOKIE` recovery by replaying directory reads from the beginning.
- `ncl_write()` is the cached regular-file write path. It handles append/sync flushing, direct-I/O dispatch, file-size extension, dirty-range merging, unstable write commit pressure, `IO_UNIT` rollback, and non-contiguous write policy.
- `ncl_vinvalbuf()` flushes and invalidates dirty buffers/pages, coordinates interruptible mounts, clears `NMODIFIED` when async direct writes are drained, and issues pNFS layout commits when needed.
- `ncl_asyncio()` queues buffers to nfsiod workers, throttles per-mount queues, requests new workers, and avoids async commit/readdirplus cases that can deadlock or starve workers.
- `ncl_doio()` performs synchronous or nfsiod-driven buffer reads, writes, and commits.
- `ncl_doio_directwrite()` completes async direct writes staged by `nfs_directio_write()`.
- `ncl_meta_setsize()` updates local size state for truncation and trims cached buffers overlapping the new EOF.

Important behavior:
- Cache consistency is approximate and uses `NMODIFIED`, server mtime, local size-change flags, and explicit attribute-cache flushes.
- Regular-file reads use `vp->v_bufobj.bo_bsize`; directory reads use `NFS_DIRBLKSIZ`; symlink reads use `NFS_MAXPATHLEN`.
- Direct synchronous writes bypass the cache and force `NFSWRITE_FILESYNC`; async direct writes copy user data to staging memory, enqueue a `B_DIRECT` pbuf, and later write filesync from nfsiod context.
- Cached async writes may use `NFSWRITE_UNSTABLE`, set `B_NEEDCOMMIT`, and later try commit-only I/O before rewriting data.
- Recoverable write errors such as `EINTR`, `EIO`, and `ETIMEDOUT` keep buffers dirty for retry. Unrecoverable errors mark `BIO_ERROR`, invalidate the buffer, store `np->n_error`, set `NWRITEERR`, and flush the attribute cache.
- Write paths protect against leaking uninitialized data if a full-buffer write faults before filling a previously uncached buffer.
- File extension updates `np->n_size` and `vnode_pager_setsize()` after acquiring the target buffer to limit readers seeing garbage during append/extension races.

Concurrency and integration:
- Uses `np->n_mtx` for nfsnode flags, local size, attr-cache timestamps, and direct-I/O counters.
- Uses `ncl_iod_mutex` for nfsiod queues, worker assignment, and queue backpressure.
- Requires vnode lock upgrades around consistency and invalidation paths.
- Integrates with VM and buffer-cache APIs including `getpbuf()`, `pmap_qenter()`, `vm_object_page_clean()`, `vfs_busy_pages()`, `bufdone()`, `bdwrite()`, `bwrite()`, and `vnode_pager_undirty_pages()`.

Research notes:
- This is the highest-risk data-integrity file in the group.
- Delicate paths include `ncl_write()` dirty-range merging and append races, `ncl_doio()` recoverable vs unrecoverable write error classification, `ncl_asyncio()` worker/queue coordination, and async direct-write cleanup.
- `nfsm_uiombuf()` in `nfs_clcomsubs.c` only supports one iovec, which explains why this file splits direct writes into one-iovec chunks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clbio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clcomsubs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clcomsubs.c

This file contains common client-side NFS request/reply helpers. It constructs request mbuf chains, copies uio data into mbufs, decodes attributes, extracts file handles, maintains directory-cookie maps, serializes NFSv4 state IDs, and wraps small NFSv4 lock-owner/delegation lock operations.

Key entry points:
- `nfscl_reqstart()` initializes an `nfsrv_descript`, selects NFSv2/v3/v4 flags, starts the request mbuf chain, writes file handles, and emits NFSv4 compound headers and optional `SEQUENCE`, `PUTFH`, and pre-op `GETATTR`.
- `nfsm_uiombuf()` copies a single-iovec `uio` into an mbuf chain, optionally using cluster mbufs for larger payloads and adding XDR padding.
- `nfsm_loadattr()` decodes NFSv2, NFSv3, or NFSv4 file attributes into `struct nfsvattr`.
- `nfscl_getcookie()` maps logical directory offsets to NFS directory cookies, growing linked `struct nfsdmap` chunks when requested.
- `nfscl_mtofh()` extracts a returned file handle and optional attributes from NFS replies.
- `nfsm_stateidtom()` serializes NFSv4 state IDs, including all-zero, all-one, and seqid-zero variants.
- `nfscl_lockinit()`, `nfscl_lockexcl()`, `nfscl_lockunlock()`, and `nfscl_lockderef()` wrap client NFSv4 owner/delegation lock bookkeeping.

Important behavior:
- `nfsv4_opmap[]` maps internal procedure numbers to first NFSv4 operation, operation count, and compound tag.
- `nfs_bigrequest[]` selects cluster mbufs for large request payloads, especially write-style procedures.
- NFSv4.1 requests may prepend `SEQUENCE`; data-server write/commit special cases force an operation count of three.
- Attribute decoding handles version-specific details such as NFSv2 FIFO encoding, NFSv3 device numbers, hyper-sized file lengths, and NFSv4 delegated parsing via `nfsv4_loadattr()`.
- Directory cookies are stored in linked chunks of `NFSNUMCOOKIES`; offset zero maps to a static null cookie.

Dependencies:
- Relies on mbuf/XDR macros from `nfsport.h`, `nfsv4_opflag[]`, type conversion tables, `nfs_bigreply[]`, and global NFS stats.
- Used broadly by client RPC operation implementations to avoid duplicating request setup and reply parsing.

Research notes:
- This is protocol glue rather than policy.
- A bug here would affect request layout, XDR padding, reply decoding, directory traversal, or NFSv4 compound operation shape across many client operations.
- `nfsm_uiombuf()` explicitly asserts `uio_iovcnt == 1`, matching direct write splitting in `nfs_clbio.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clcomsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clkdtrace.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clkdtrace.c

This file defines the `dtnfscl` DTrace provider for the NFS client. It exposes logical client RPC probes plus access-cache and attribute-cache probes.

Key components:
- `dtnfsclient_rpcs[]` maps NFS procedure slots to NFSv2, NFSv3, and NFSv4 probe names.
- `dtnfsclient_getargdesc()` describes probe argument types for cache probes and RPC probes.
- `dtnfsclient_provide()` creates probes for access cache, attribute cache, and NFSv2/v3/v4 RPC start/done events.
- `dtnfsclient_enable()` and `dtnfsclient_disable()` install or clear probe IDs and function pointers used by NFS client tracing macros.
- `dtnfsclient_load()` registers provider `nfscl` and installs generic NFS RPC probe hooks.
- `dtnfsclient_unload()` unregisters the provider and clears those hooks.
- `dtnfsclient_modevent()` is a minimal module event handler.

Probe model:
- Cache probes cover access-cache flush, get hit, get miss, load done, and attribute-cache flush/get/load events.
- RPC probes expose per-version start and done events. Done probes include an additional integer status argument.
- NFSv2 and NFSv3 probe arrays are sparse but sized like the NFSv4.1 procedure table for simple indexing.

Dependencies:
- Uses DTrace provider interfaces from `dtrace_bsd.h`.
- Stores probe IDs in global arrays such as `nfscl_nfs3_start_probes[]`.
- Hooks cache probes through global function pointers declared in `nfs_kdtrace.h`.
- Declares dependencies on `dtrace`, `opensolaris`, `nfscl`, and `nfscommon`.

Research notes:
- This file does not implement NFS behavior; it instruments behavior implemented elsewhere.
- The primary coupling is that RPC probe IDs are stored in NFS client arrays, while cache probes are enabled by swapping function pointers to `dtrace_probe`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clkdtrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clkrpc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clkrpc.c

This file implements kernel RPC service support for NFSv4 client callbacks. It lets a user-supplied callback socket be taken over by the kernel and serviced by the `nfscbd` RPC pool.

Key entry points:
- `nfscb_program()` is the RPC dispatch function registered for callback requests.
- `nfs_cbproc()` invokes `nfscl_docb()` and maps callback results to reply-or-drop behavior.
- `nfscbd_addsock()` reserves socket buffers, creates an RPC transport, steals the socket from the file descriptor, and registers `NFS_CALLBCKPROG`.
- `nfscbd_nfsd()` runs the callback service pool and optionally registers a Kerberos service principal for RPCSEC_GSS callbacks.
- `nfsrvd_cbinit()` initializes the callback service pool and synchronizes termination.

Important behavior:
- Only `NFSPROC_NULL` and `NFSV4PROC_CBCOMPOUND` are accepted.
- Non-null callbacks realign the request mbuf, capture caller address data, obtain credentials, and dispatch through `nfscl_docb()`.
- `NFSERR_DONTREPLY` causes the request to be dropped rather than answered.
- Only the first `nfscbd` caller runs the service pool; extra callers return after observing that a daemon is already active.
- `nfscbd_pool` is created lazily by `nfsrvd_cbinit()`.

Dependencies:
- Uses kernel RPC service APIs including `svc_dg_create()`, `svc_vc_create()`, `svc_reg()`, `svc_run()`, and `svc_sendreply_mbuf()`.
- Shares `nfscbd_pool`, `nfs_numnfscbd`, and `NFSDLOCKMUTEX` state with the wider NFS service framework.
- Calls the NFSv4 callback executor `nfscl_docb()`.

Research notes:
- This is inbound callback server plumbing for the client, not the normal outbound client RPC path.
- Socket ownership transfer in `nfscbd_addsock()` is significant: after transport creation, the user file is neutered with `badfileops` and `f_data = NULL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clkrpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clmodule.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clmodule.c

This is a small NetBSD module wrapper for `nfs_client`.

Key behavior:
- Declares `MODULE(MODULE_CLASS_MISC, nfs_client, "nfs_common,sysmon_taskq")`.
- `nfs_client_modcmd()` accepts `MODULE_CMD_INIT` and `MODULE_CMD_FINI`, returning success for both.
- Unknown module commands return `ENOTTY`.

Dependencies:
- Depends on `nfs_common` and `sysmon_taskq`.
- Does not initialize the detailed NFS client subsystem itself; substantive setup lives in files such as `nfs_clport.c`.

Research notes:
- This file is purely module metadata/control.
- It has no NFS protocol, vnode, cache, RPC, or I/O logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clmodule.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clnfsiod.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clnfsiod.c

This file manages NFS client asynchronous I/O daemon threads, `nfsiod`. These workers drain per-mount buffer queues populated by `ncl_asyncio()` in `nfs_clbio.c`.

Key state:
- `ncl_numasync` tracks active async daemon count.
- `ncl_iodwant[]` records per-worker availability.
- `ncl_iodmount[]` records which mount a worker is currently serving.
- `nfs_asyncdaemon[]` tracks allocated worker slots.
- `ncl_iodmax`, `nfs_iodmin`, and `nfs_iodmaxidle` control pool sizing and idle exit.

Key entry points:
- `sysctl_iodmin()` adjusts the minimum spare nfsiod count and creates workers as needed.
- `sysctl_iodmax()` adjusts the maximum and wakes excess idle workers so they can exit.
- `nfs_nfsiodnew_sync()` creates one worker while temporarily releasing `ncl_iod_mutex`.
- `ncl_nfsiodnew_tq()` services queued worker-creation tasks.
- `ncl_nfsiodnew()` requests async worker creation through `taskqueue_thread`.
- `nfsiod_setup()` initializes client state and starts the configured minimum worker count.
- `nfssvc_iod()` is the worker loop.

Worker behavior:
- A worker sleeps until assigned a mount with queued buffers.
- It removes buffers from `nm_bufq`, wakes producers waiting for queue drain, drops `ncl_iod_mutex`, and performs I/O.
- `B_DIRECT` write buffers are sent to `ncl_doio_directwrite()`.
- Normal buffers are sent to `ncl_doio()` with read or write credentials.
- Idle workers above `nfs_iodmin` exit after `nfs_iodmaxidle` seconds.
- Optional `vfs.nfs.defect` lets workers move away from mounts with multiple workers to improve fairness.

Dependencies:
- Closely coupled with `ncl_asyncio()` queueing and with `ncl_doio()`/`ncl_doio_directwrite()` execution.
- Uses `ncl_iod_mutex` as the central lock for pool and queue accounting.
- Exposes sysctls under `_vfs_nfs`.

Research notes:
- This is the async execution backend for read-ahead, write-behind, and async direct writes.
- Race-sensitive areas include worker sleep/timeout, mount dismount while I/O completes, queue-drain wakeups, and dynamic changes to `ncl_iodmax`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clnfsiod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clnode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clnode.c

This file implements core nfsnode allocation, root-node lookup, vnode inactive/reclaim handling, sillyrename cleanup, and cache invalidation.

Key entry points:
- `ncl_nhinit()` creates the `NCLNODE` UMA zone for `struct nfsnode`.
- `ncl_nhuninit()` destroys that zone.
- `ncl_nget()` looks up or creates an nfsnode by file handle; this variant is documented as root-directory oriented.
- `ncl_inactive()` handles vnode inactivity, including delayed NFSv4 close for regular files after mmap/page-cache flush.
- `ncl_reclaim()` tears down the vnode/nfsnode association.
- `ncl_invalcaches()` clears access-cache entries and the attribute cache.

Important behavior:
- `ncl_nget()` hashes file handles with FNV, searches `vfs_hash`, allocates a vnode/nfsnode on miss, attaches NFS buffer ops, initializes `n_mtx`, enables recursive/shared vnode locking, marks root vnodes, inserts into the mount queue, and inserts into the vnode hash.
- Sillyrename cleanup is split: `ncl_releasesillyrename()` invalidates buffers, removes the silly-renamed file, drops credentials, and defers directory `vrele()` via `sysmon_task_queue_sched()` to avoid lock-order reversal.
- `ncl_inactive()` flushes VM pages and NFS buffers before issuing delayed NFSv4 close, then preserves only `NMODIFIED` among nfsnode flags.
- `ncl_reclaim()` gives NLM a chance to abort locks, releases sillyrename state, destroys VM objects, closes remaining NFSv4 opens, removes the vnode from `vfs_hash`, calls `nfscl_reclaimnode()` for regular files, frees directory cookie maps, credentials, file handles, NFSv4 name state, mutexes, and the UMA allocation.

Dependencies:
- Uses `newnfs_vnodeops`, `buf_ops_newnfs`, `newnfs_vncmpf()`, `ncl_vinvalbuf()`, `ncl_flush()`, `nfsrpc_close()`, `nfscl_reclaimnode()`, and optional `nfs_reclaim_p`.
- Emits DTrace cache flush probes through `KDTRACE_NFS_ACCESSCACHE_FLUSH_DONE()` and `KDTRACE_NFS_ATTRCACHE_FLUSH_DONE()`.

Research notes:
- This is the lifecycle companion to the I/O files: it owns node identity and teardown, while `nfs_clbio.c` owns cached data movement.
- NFSv4 delayed close semantics make inactive/reclaim part of correctness, not just memory cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clport.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clport.c

This file is the NetBSD/FreeBSD porting and integration layer for the new NFS client. It provides vnode lookup variants, attribute-cache loading, NFSv4 client identity helpers, weak-cache-consistency parsing, setattr encoding, request dispatch, statfs/fsinfo loading, source-address selection, `nfssvc()` client operations, and module initialization.

Key entry points:
- `newnfs_vncmpf()` compares vnodes against file handles for `vfs_hash`.
- `nfscl_nget()` looks up or creates normal NFS client vnodes/nfsnodes from a consumed `struct nfsfh *`.
- `nfscl_ngetreopen()` finds an existing vnode during NFSv4 reopen recovery without requiring normal blocking vnode locking.
- `nfscl_loadattrcache()` loads `struct nfsvattr` into an nfsnode and optional `struct vattr`.
- `nfscl_fillclid()` constructs an NFSv4 client ID from mount ID, UUID, and random bytes.
- `nfscl_filllockowner()` encodes POSIX/flock lock-owner names.
- `nfscl_getparent()` returns a parent process thread for client recovery logic.
- `nfscl_start_renewthread()` starts the NFSv4 lease-renew kernel thread.
- `nfscl_wcc_data()` parses weak-cache-consistency data.
- `nfscl_postop_attr()` parses post-operation attributes.
- `nfscl_fillsattr()` serializes settable attributes for NFSv2, NFSv3, or NFSv4.
- `nfscl_request()` wraps `newnfs_request()` for client RPC dispatch.
- `nfscl_loadsbinfo()` maps NFS statfs data into `struct statfs`.
- `nfscl_loadfsinfo()` updates mount read/write/readdir sizes and max file size from FSINFO.
- `nfscl_getmyip()` selects the local source address used to reach the server.
- `newnfs_copyincred()` copies kernel credentials into NFS credential form.
- `nfscl_init()` performs one-time client initialization.
- `nfscl_checksattr()` removes no-op setattr fields and ensures time fields for verifier-related SETATTR behavior.
- `nfscl_maperr()` maps NFSv4 protocol errors to local errno values.
- `nfscl_procdoesntexist()` validates encoded POSIX lock-owner state against the process table.
- `nfssvc_nfscl()` handles client-facing `nfssvc()` operations for callback sockets, callback daemons, and mount-option dumping.
- `nfscl_modevent()` initializes the full client module.

Important behavior:
- `nfscl_nget()` attaches NFSv4 directory file-handle and component-name state to regular files so later `OPEN` operations can be issued.
- Existing NFSv4 regular-file nodes may have saved parent/name tuples replaced when the same file handle is found through a different lookup name.
- `nfscl_loadattrcache()` rejects changed file IDs with `EIDRM` and rate-limited warnings, protecting against broken servers or middleware returning attributes for the wrong object.
- Attribute-cache size reconciliation is careful around locally modified files: local size can win over smaller server size, larger server size can set `NSIZECHANGED`, and VM pager size changes may be deferred until after unlocking.
- NFSv4 fsid handling may synthesize `va_fsid` from per-node fsids so `getcwd(3)` works across server-side mounted subtrees.
- `nfscl_fillsattr()` emits version-specific setattr encodings, including NFSv3 guarded boolean fields and NFSv4 attribute bitmaps.
- `nfscl_loadfsinfo()` clamps preferred and maximum I/O sizes to NFS block/directory block alignment and updates mount `f_iosize`.
- `nfssvc_nfscl()` supports `NFSSVC_CBADDSOCK`, `NFSSVC_NFSCBD`, and `NFSSVC_DUMPMNTOPTS`.

Module integration:
- Defines global mutexes `nfs_clstate_mutex` and `ncl_iod_mutex`.
- On `MOD_LOAD`, calls `newnfs_portinit()`, initializes mutexes, initializes NFS client state, initializes callback RPC state, installs `ncl_call_invalcaches`, and installs `nfsd_call_nfscl`.
- Module unload is effectively unsupported; it returns busy if callback daemons exist and otherwise falls through to `EOPNOTSUPP`.
- Declares dependencies on `nfscommon`, `krpc`, `nfssvc`, and `nfslock`.

Research notes:
- This file is the highest-level integration surface in the group.
- The most security/data-integrity-relevant logic is file-handle identity handling, fileid-change detection, attribute-cache size reconciliation, callback `nfssvc()` socket intake, and NFSv4 error mapping.
- The WCC comparison path is worth review: one NFSv4 branch compares cached `tv_nsec` against a loaded `tv_sec`, which looks like a likely typo in consistency detection.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clport.c -->