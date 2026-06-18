# Group Research: group_1248_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_nlm_nlm_prot_impl_c_c7af6eafcbec

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_impl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_impl.c

Implements the kernel Network Lock Manager core for NetBSD's NFS lockd path. It owns global NLM initialization, syscall registration, server startup, RPC client creation, host/sysid tracking, NSM monitor/unmonitor integration, waiting client lock state, async server-side blocked lock state, and the concrete NLM operations used by the RPC stubs.

Important entry points include `sys_nlm_syscall()`, `nlm_server_main()`, `nlm_find_host_by_name()`, `nlm_find_host_by_addr()`, `nlm_host_monitor()`, `nlm_host_get_rpc()`, `nlm_register_wait_lock()`, `nlm_wait_lock()`, `nlm_cancel_wait()`, and the RPC-operation helpers `nlm_do_test()`, `nlm_do_lock()`, `nlm_do_cancel()`, `nlm_do_unlock()`, `nlm_do_granted()`, `nlm_do_granted_res()`, and `nlm_do_free_all()`.

The host model assigns local sysids, stores caller names and remote addresses, caches RPC handles briefly, publishes per-host sysctl counters, tracks NSM monitor state, and maintains pending/granted/finished async lock lists. Reboot notifications from NSM call `nlm_host_notify()`, which cancels pending async locks, clears local lock-manager state with `lf_clearremotesys()`, and can start client lock recovery when local client locks exist.

Lock operations translate NLM locks into `struct flock` and call `VOP_ADVLOCK()` or `VOP_ADVLOCKASYNC()`. Blocking server locks allocate `nlm_async_lock`, send `GRANTED_MSG` callbacks when granted, and wait for `GRANTED_RES` acceptance; rejected grants are unlocked locally. Client-side blocking waits are matched by file handle, pid, offset, and length when `nlm_do_granted()` receives a granted callback.

Key dependencies are kernel RPC/krpc, rpcbind/portmap, local NSM protocol XDR, NFS file handle and export APIs, vnode/VFS operations, `nfs_lock` hooks, taskqueue callbacks, sysctl, syscall registration, and lockf helpers. Operational risks center on cross-thread races between async lock callbacks, host reboot cleanup, RPC handle expiry, and module lifetime; the module explicitly refuses unload.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_impl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_server.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_server.c

Provides the RPC service implementation stubs for NLM protocol versions 0, 1, 3, and 4. The file mostly adapts older NLM structures and procedure numbers to the NLMv4 internal implementation in `nlm_prot_impl.c`.

The conversion helpers map legacy `nlm_lock`, `nlm_share`, `nlm_holder`, and result/status structures to their `nlm4_*` equivalents and back. Version 1 and version 3 procedures call the version 4 service helpers after conversion; version 3 adds share/unshare, non-monitored lock, and free-all wrappers.

Synchronous procedures return direct test/lock/cancel/unlock/granted results. Asynchronous `_MSG` procedures run the same operation, then send the matching `_RES` callback over a `CLIENT *` returned by the implementation layer. Most incoming `_RES` procedures are effectively ignored, except `nlm4_granted_res_4_svc()`, which calls `nlm_do_granted_res()` to complete an async server-side granted lock.

Share and unshare are not implemented as real share reservations: `nlm4_share_4_svc()` and `nlm4_unshare_4_svc()` zero the result and return denied. `nlm4_nm_lock_4_svc()` runs `nlm_do_lock()` with monitoring disabled. Result cleanup delegates to `xdr_free()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_server.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_svc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_svc.c

Generated-style RPC dispatcher for the NLM program. It decodes incoming RPC procedure numbers for versions 0, 1, 3, and 4, selects the correct XDR argument/result routines, invokes the local `*_svc` implementation function, sends replies when requested, frees decoded arguments, frees result storage, and releases the service request.

`nlm_prog_0()` only dispatches `NLM_SM_NOTIFY`. `nlm_prog_1()` handles classic NLM test, lock, cancel, unlock, granted, async message, and async result procedures. `nlm_prog_3()` delegates common version 1 procedures to `nlm_prog_1()` and adds share, unshare, non-monitored lock, and free-all. `nlm_prog_4()` dispatches the corresponding NLMv4 procedure set.

The file is tightly coupled to `nlm_prot_server.c` for service functions and `nlm_prot_xdr.c` for XDR codecs. It follows rpcgen conventions, including union argument/result storage and returning no normal RPC reply for asynchronous message handlers whose service function returns false.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_svc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_xdr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_xdr.c

Rpcgen-generated XDR serialization for NLM protocol data structures. It covers legacy NLM and NLMv4 statuses, holders, locks, lock/test/cancel/unlock arguments, share arguments/results, notify records, NSM status callbacks as used by NLM, and test/result unions.

Legacy NLM uses 32-bit offsets/lengths and `LM_MAXSTRLEN` caller names; NLMv4 uses 64-bit offsets/lengths, uint32 pids, and `MAXNAMELEN` caller names. Union encoders only serialize lock-holder details for denied test replies.

Every function returns `FALSE` on the first failed XDR primitive. The file is not policy-bearing; correctness depends on matching `nlm_prot.h` structure layout and the RPC dispatch tables in `nlm_prot_svc.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/sm_inter.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/sm_inter.h

Rpcgen-generated header for the Network Status Monitor protocol used by lockd. It defines SM program/version constants, procedure numbers, C structs, enum results, client/server prototypes, freeresult prototype, and XDR declarations.

Defined structures include monitored names, callback identity (`my_id`), monitor ids, monitor requests with 16-byte private cookies, state-change records, simple state replies, monitor result replies, and status notifications. Procedures include `SM_STAT`, `SM_MON`, `SM_UNMON`, `SM_UNMON_ALL`, `SM_SIMU_CRASH`, and `SM_NOTIFY`.

Within this group, `nlm_prot_impl.c` uses these definitions to register/unregister remote hosts with the local NSM and to clear monitor state at lockd startup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/sm_inter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/sm_inter_xdr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/sm_inter_xdr.c

Rpcgen-generated XDR serialization for the NSM structures declared in `sm_inter.h`. It serializes monitor names, callback identity, monitor ids, monitor requests, state-change notifications, state replies, enum results, combined result/state replies, and 16-byte private notification cookies.

The functions are straightforward wrappers around `xdr_string()`, `xdr_int()`, `xdr_enum()`, and `xdr_opaque()`, returning `FALSE` on decode/encode failure. The 16-byte `priv` field is important because `nlm_prot_impl.c` stores the NLM host sysid there to map NSM reboot notifications back to tracked hosts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/sm_inter_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_fha_new.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_fha_new.c

Implements the NFS server File Handle Affinity personality for the newer NFS server. It initializes `fha_params`, installs callback functions, creates the `vfs.nfsd.fha` sysctl subtree, and delegates scheduling decisions to the common FHA framework.

Callbacks translate NFSv2 procedure numbers to generic NFSv3-style procedure numbers, realign mbufs, extract a compact hash from an NFS file handle, classify reads and writes, parse read/write offsets, identify procedures without offsets, and select shared or exclusive lock types per NFS procedure. `fhanew_assign()` is the exported hook used by the RPC service pool to choose a service thread.

The file depends on common NFS RPC parsing macros, `newnfs_nfsv3_procid[]`, `newnfs_realign()`, `fha_init()`, `fha_uninit()`, `fha_assign()`, and `fhe_stats_sysctl()`. Its file-handle hash intentionally reduces a variable-size handle to a 64-bit xor-style value for scheduling affinity, not for security or identity.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_fha_new.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_fha_new.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_fha_new.h

Small kernel header for the newer NFS server FHA personality. It defines `FHANEW_SERVER_NAME` as `"nfsd"` and declares `fhanew_assign()` for assigning RPC requests to FHA-selected service threads.

This header is consumed by the NFS server krpc setup so the service pool can use the NFS-specific file-handle affinity callback.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_fha_new.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdcache.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdcache.c

Implements the NFS server duplicate request cache. The long file comment explains the design: false hits are worse than false misses, NFSv4 seqid ordering must not be broken, UDP uses the traditional xid/procedure/client cache, and TCP/NFSv4 uses stricter matching with request length/checksum, socket timing, and seqid references.

`nfsrvd_getcache()` allocates a request cache record and dispatches to UDP or TCP lookup. UDP keys on xid, NFS version, procedure, and client address, with an LRU list and in-progress suppression. TCP keys on xid/version/procedure plus request length/checksum and additional socket constraints, allowing multiple entries per key to avoid false hits.

`nfsrvd_updatecache()` decides whether to save a reply, return a cached reply for NFSv4 seqid handling, or free the entry. It saves status-only NFSv2 replies where possible and mbuf copies otherwise. `nfsrvd_sentcache()` records TCP reply sequence state after send, while `nfsrc_trimcache()` expires UDP/TCP entries by timeout, acknowledgment, final socket loss, high-water pressure, and refcount state.

Reference helpers `nfsrvd_refcache()` and `nfsrvd_derefcache()` pin cache entries for NFSv4 owner seqid sequencing. Cache entries are protected by per-bucket mutexes or the UDP mutex, with explicit `RC_LOCKED`/`RC_WANTED` entry locking. Sysctls control TCP high water, UDP high water, TCP timeout, and TCP non-idempotent caching.

Key dependencies are `struct nfsrv_descript`, mbuf copy/free APIs, NFS statistics, TCP acknowledgment hooks from the service transport, NFSv4 seqid code, and shared cache tables defined in `nfs_nfsdport.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdkrpc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdkrpc.c

Provides the kernel RPC front end for the NFS server. It registers NFS program versions on server sockets, converts incoming `svc_req` records into `nfsrv_descript`, authenticates credentials, enforces optional privileged-port policy for NFSv2/v3, coordinates duplicate request caching, dispatches actual NFS request execution, and sends mbuf replies.

`nfssvc_program()` is the main RPC dispatcher. It maps NFSv2 procedure numbers to generic server procedure numbers, validates supported NFS versions, realigns request mbufs, fetches RPC credentials and GSS flavor flags, takes the NFSv4 suspend shared reference, checks NFSv4 root export state, calls `nfs_proc()`, and sends or drops the reply based on duplicate-cache results.

`nfs_proc()` handles duplicate request cache lookup/update around `nfsrvd_dorpc()`. NFSv4.1 bypasses the classic DRC and uses session-slot reply caching. Earlier versions use `nfsrvd_getcache()`, `nfsrvd_updatecache()`, and `nfsrc_trimcache()`.

`nfsrvd_addsock()` steals a userspace socket into a kernel RPC transport and registers NFSv2/v3/v4 based on sysctl min/max versions. `nfsrvd_nfsd()` runs the service pool, optionally registers Kerberos service names, and tears down state on exit. `nfsrvd_init()` creates the `nfsd` service pool and installs FHA request assignment.

Important dependencies include krpc service transports, rpcsec_gss, FHA, duplicate cache code, NFSv4 root/suspend locks, `nfsrvd_dorpc()`, session caching, and shared `nfsd` module state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdkrpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdmodule.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdmodule.c

Minimal NetBSD module wrapper declaring `nfs_server` as a miscellaneous module depending on `nfs_common`. Its `nfs_server_modcmd()` accepts init and fini commands and returns `ENOTTY` for unknown module commands.

The file contains no server implementation; real NFS server load/unload behavior for this code group lives in `nfs_nfsdport.c`'s `nfsd_modevent()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdmodule.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdport.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdport.c

Large portability and integration layer between the protocol-level NFS server and NetBSD/FreeBSD-style kernel VFS primitives. It defines global NFS server state, sysctls, reply-cache hash tables and locks, NFSv4 pseudo-root mount state, server module load/unload handling, and many `nfsvno_*` wrappers used by higher-level NFS service code.

The vnode operation wrappers cover attributes, file handles, access checks, setattr, namei/path buffers, readlink, read/write mbuf I/O, create/mknod/mkdir/symlink, remove/rmdir/rename/link, fsync/commit, statfs, NFSv4 open/create, filerev updates, NFSv4 fillattr glue, directory reading, settable attribute decoding, export credential mapping, export checks, file-handle-to-vnode lookup, and optional local advisory locks for NFSv4.

Directory service code is substantial. `nfsrvd_readdir()` builds NFSv2/v3 directory replies from `VOP_READDIR()` results, filters invalid/whiteout entries, handles UFS cookie behavior, enforces reply size, and emits EOF flags. `nfsrvd_readdirplus()` supports NFSv3 readdirplus and NFSv4 readdir attributes, optionally using `VFS_VGET()` or `VOP_LOOKUP()`, handling ZFS snapshot quirks, crossing mount points for NFSv4 when enabled, referrals, rdattr_error, file handles, and attribute reply trimming.

Attribute parsing is split between `nfsrv_sattr()` for NFSv2/v3/v4 dispatch and `nfsv4_sattr()` for NFSv4 attrbit parsing. The NFSv4 parser handles size, ACL, mode, owner, owner_group, access/modify time setting, unsupported attributes, attrlist padding, and BADXDR/ATTRNOTSUPP reporting.

Export and credential logic includes `nfsd_excred()`, `nfsvno_checkexp()`, `nfsvno_fhtovp()`, `nfsd_fhtovp()`, and `nfsvno_testexp()`. It applies root squashing/anonymous exports, AUTH_SYS versus RPCSEC_GSS security flavor checks, v4-only exports, optional fallback for the NFSv4 pseudo root, and NFSv4 traversal of unexported file systems where allowed.

Control paths include `nfssvc_nfsd()` and `nfssvc_srvcall()` for adding sockets, starting nfsd workers, public file handles, v4 root export setup, stable restart file setup, client revoke/dump operations, lock dump operations, stable backup signaling, and suspend/resume of nfsd threads. `nfsd_modevent()` initializes caches, locks, NFS state, service pools, pseudo-root mount state, delegation hooks, and nfssvc callbacks on load; unload refuses while nfsd threads run, discards NFSv4 state, cleans caches, destroys locks, and frees hash tables.

Important implementation risks are mostly lifetime and locking related: vnode lock state must match each VOP call, namei buffers are manually owned, mbuf replies are copied/truncated by protocol size, mount busy references protect cross-mount readdirplus work, and module unload must coordinate NFSv4 state, service pools, reply caches, and global callback pointers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdport.c -->