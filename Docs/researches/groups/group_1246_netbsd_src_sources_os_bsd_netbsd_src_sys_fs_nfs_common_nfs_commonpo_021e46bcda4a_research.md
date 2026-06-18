# Group Research: group_1246_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_common_nfs_commonpo_021e46bcda4a

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonport.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonport.c

This is NetBSD/FreeBSD-port glue for the shared NFS implementation. It owns common global storage, malloc types, mutexes, sysctls, module lifecycle, `nfssvc` common dispatch, timer setup, and small kernel API adaptation helpers.

Key contents:
- Defines common globals including `nfsv4root_mnt`, `nfsstatsv1`, nfsd/callback daemon counters, callback address, common callout, lock mutexes, and client/server callback hooks.
- Registers `vfs.nfs` sysctls for mbuf realignment counters, callback address, debug level, and uid/name hash size.
- Defines `M_NEWNFS*` malloc buckets for server cache/state, client state, file handles, socket requests, sessions, layouts, and strings.
- Implements `newnfs_realign()` for strict-alignment platforms by replacing unaligned mbuf chain portions with aligned mbufs.
- Provides wrappers for name lookup, credential copying/root credential creation, timed sleep, FSINFO defaults, pathconf fallback values, v4 root referral stub, short retry sleeps, and NFSv4 ACL support probing.
- Implements common `nfssvc` operations for id/name cache updates, stats copyout/zeroing, and `nfsuserd` port registration/removal.
- `nfscommon_modevent()` initializes shared locks, callouts, common state, and `nfsd_call_nfscommon`; unload refuses while nfsd, nfsuserd, or callback daemons are active.

Important dependencies:
- Uses `newnfs_init()`, `nfssvc_idname()`, `nfsrv_nfsuserdport()`, `nfsrv_nfsuserddelport()`, and `nfsrv_cleanusergroup()` from `nfs_commonsubs.c`.
- Hooks into `nfs_nfssvc.c` via `nfsd_call_nfscommon`.
- Relies on vnode/VFS operations such as `namei`, `VOP_PATHCONF`, and NFSv4 ACL pathconf support.

Risks and notes:
- Legacy stats conversion is manual and must stay synchronized with stat structure changes.
- Module unload ordering is sensitive because the destroyed mutexes are shared by client/server/common code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonsubs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonsubs.c

This is the main shared NFS protocol helper implementation. It handles mbuf/XDR construction and dissection, NFSv4 attribute parsing/emission, uid/gid owner mapping, common NFSv4 locking, reply initialization, socket send locks, UTF-8 checks, fs_locations parsing, and NFSv4.1 session slot sequencing.

Key contents:
- Defines shared XDR constants, NFS type conversion tables, `nfsboottime`, `nfscl_ticks`, ACL/userd globals, lease defaults, `nfs_bigreply`, and the NFSv4 operation flag table `nfsv4_opflag`.
- Implements mbuf and XDR helpers: `nfsm_mbufuio()`, `nfsm_dissct()`, `nfsm_advance()`, `nfsm_strtom()`, `nfsm_fhtom()`, `nfsrv_mtostr()`, `newnfs_trimleading()`, and `newnfs_trimtrailing()`.
- Implements IPv4/IPv6 address match helpers.
- Parses NFSv4 ACLs and attribute bitmaps through `nfsrv_dissectacl()`, `nfsrv_skipace()`, and `nfsrv_getattrbits()`.
- Implements the large `nfsv4_loadattr()` reader for NFSv4 attributes, including compare mode, vattr/statfs/fsinfo/pathconf fields, ACLs, owner/group strings, quotas, file handles, fs_locations, timestamps, and mounted-on file ids.
- Implements `nfsv4_fillattr()` and `nfsrv_putattrbit()` for emitting supported/fillable attribute bitmaps and encoded attribute values.
- Implements the common `nfsv4lock` primitive: exclusive lock acquisition, unlock-with-ref, ref release/acquire, nonblocking ref acquire, and lock testing.
- Implements uid/gid to string and string to uid/gid conversion, including `nfsuserd` upcalls, default nobody/nogroup mapping, numeric string policy, domain suffix handling, and four hash tables for user/group name/id cache entries.
- `nfssvc_idname()` initializes, updates, expires, and trims the owner/group mapping caches; `nfsrv_cleanusergroup()` frees them during common module unload.
- Implements UTF-8 validation and NFSv4 `fs_locations` string parsing/growth.
- Initializes reply mbufs in `nfsrvd_rephead()`, using clusters for known large replies.
- Serializes socket send/connect/disconnect paths with `newnfs_sndlock()` and `newnfs_sndunlock()`.
- Parses NFSv4.1 callback netaddr strings in `nfsv4_getipaddr()`.
- Implements NFSv4.1 session sequencing and slot management: `nfsv4_seqsession()`, `nfsv4_seqsess_cacherep()`, `nfsv4_setsequence()`, `nfsv4_sequencelookup()`, and `nfsv4_freeslot()`.

Important dependencies:
- Uses XDR/mbuf macros from `nfsm_subs.h` and porting shims from `nfsport.h`/`nfskpiport.h`.
- Calls ACL helpers declared in `nfs_var.h`: `nfsrv_dissectace()`, `nfsrv_buildacl()`, and `nfsrv_compareacl()`.
- Calls port functions such as `nfsmsleep()`, `newnfs_getcred()`, `nfsvno_getfs()`, `nfs_supportsnfsv4acls()`, `nfsrv_atroot()`, and `nfsv4root_getreferral()`.
- Calls RPC transport helpers `newnfs_connect()`, `newnfs_disconnect()`, and `newnfs_request()`.

Risks and notes:
- `nfsv4_loadattr()` and `nfsv4_fillattr()` are long protocol-critical switch statements; any new attribute requires synchronized parse, fill, bitmap, and size accounting behavior.
- User/group cache locking has documented lock ordering; violating it risks deadlock.
- Numeric owner string acceptance depends on AUTH_SYS/client flags or `nfsd_enable_stringtouid`, which is a security-sensitive compatibility choice.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_diskless.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_diskless.c

This file populates diskless NFS root boot configuration from loader environment variables. It supports legacy NFSv2-style boot state and NFSv3 file handles.

Key contents:
- Defines global `nfs_diskless`, `nfsv3_diskless`, and `nfs_diskless_valid`.
- `nfs_parse_options()` parses root mount options including soft/intr/conn/nolockd/nocto, NFSv2/v3, TCP/UDP, `rsize=`, and `wsize=`.
- `nfs_setup_diskless()` reads boot interface IP/netmask/gateway/hardware address, NFS root server/path/options, and encoded root file handle.
- Matches the boot interface by Ethernet MAC address, waiting up to `NFS_IFACE_TIMEOUT_SECS`.
- Fills either `nfsv3_diskless` with NFSv3 defaults or `nfs_diskless` with legacy NFSv2-compatible defaults.
- Helper parsers convert dotted IPv4 strings, Ethernet MAC strings, and loader `X...X` hex NFS file handles.
- `nfs_rootconf()` marks root as `nfs:` when bootp support is not providing root setup.

Important dependencies:
- Consumed by NFS mountroot logic via `nfsdiskless.h`.
- Depends on kernel environment variables, interface lists, IPv4 socket structures, and NFS client mount argument definitions.

Risks and notes:
- Boot setup is IPv4 and Ethernet oriented.
- `rsize`/`wsize` validation accepts 4 through 32768 bytes.
- File-handle parsing only accepts the custom loader hex format.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_diskless.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_fha.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_fha.c

This implements NFS File Handle Affinity scheduling. It assigns NFS server requests to service threads based on file handle and, for reads/writes, offset locality.

Key contents:
- `fha_init()` initializes hash-slot locks, default controls, tunable overrides, and runtime sysctls.
- `fha_uninit()` frees sysctl context and destroys hash locks.
- `fha_extract_info()` uses server-provided callbacks to normalize v2/v3 procedure numbers, realign mbufs, extract file handles, offsets, and lock type.
- Maintains `fha_hash_entry` records keyed by file handle with active service-thread lists and read/write/exclusive operation counts.
- `fha_hash_entry_choose_thread()` prefers existing threads with nearby read offsets, falls back to lower-load threads, or adds the current thread when within `max_nfsds_per_fh`.
- `fha_assign()` only performs placement for enabled NFS program v2/v3 requests; other requests stay on the current service thread.
- `fha_nd_complete()` decrements accounting and removes idle thread/file-handle entries.
- `fhe_stats_sysctl()` emits active FHA state as a string snapshot.

Important dependencies:
- Public structures and callbacks come from `nfs_fha.h`.
- Uses RPC `SVCTHREAD` scratch fields `st_p2`/`st_p3` and request scratch fields `rq_p1`/`rq_p2`/`rq_p3`.

Risks and notes:
- Correctness depends on each request assigned through FHA calling `fha_nd_complete()`.
- Hash entry lookup allocates a candidate before locking, then destroys it if an entry already exists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_fha.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_fha.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_fha.h

This header defines File Handle Affinity scheduler structures, defaults, callbacks, and exported functions.

Key contents:
- Defines defaults: FHA enabled, 4 MiB bin shift, 8 nfsd threads per file handle, and unlimited requests per nfsd.
- Defines `FHA_HASH_SIZE` as 251.
- Defines `struct fha_ctls`, `struct fha_hash_entry`, `struct fha_hash_slot`, `struct fha_info`, `struct fha_callbacks`, and `struct fha_params`.
- Callback table abstracts NFS wire decoding: procedure mapping, mbuf realignment, file-handle extraction, read/write checks, offset extraction, no-offset checks, lock-type selection, and stats sysctl handling.
- Declares `fha_init()`, `fha_uninit()`, `fha_assign()`, `fha_nd_complete()`, and `fhe_stats_sysctl()`.

Important dependencies:
- Only active under `_KERNEL`.
- Depends on RPC service thread/list types, mutexes, lists, and sysctl handler types.

Risks and notes:
- The header deliberately keeps FHA independent of exact NFSv2/v3 parsing by requiring callbacks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_fha.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_kdtrace.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_kdtrace.h

This header provides optional KDTrace/DTrace wrappers for NFS client access-cache and attribute-cache events.

Key contents:
- Under `KDTRACE_HOOKS`, declares probe IDs for access-cache flush/get-hit/get-miss/load-done events.
- Defines macros that call registered probe function pointers only when non-null.
- Provides matching attribute-cache probe macros.
- When tracing is disabled, all macros compile to no-ops.

Important dependencies:
- Includes `sys/dtrace_bsd.h` only when tracing support is enabled.
- Probe function pointers are supplied by the tracing subsystem.

Risks and notes:
- Instrumentation-only; disabled tracing should have no runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_kdtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_lock.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_lock.c

This bridges kernel NFS advisory byte-range locking to userland `rpc.lockd` through an `nfslock` pseudo-device.

Key contents:
- Exports `nfs_advlock_p = nfs_dolock` and `nfs_reclaim_p`.
- Defines an `nfslock` character device with open, close, read, and write methods.
- Requires `PRIV_NFS_LOCKD` and allows only one device opener.
- Queues `LOCKD_MSG` requests for userland lockd to read.
- `nfs_dolock()` validates lock ranges, extracts NFS vnode/server/file-handle info, builds a lockd message, sends it to userland, and waits for a per-process `nlminfo` reply.
- Retries unanswered non-unlock requests every 20 seconds.
- `nfslockdans()` validates reply version, pid start time, and sequence before storing return status and waking the waiting process.
- `nlminfo_release()` frees per-process NLM metadata.

Important dependencies:
- Wire structures are defined in `nfs_lock.h`.
- Relies on NFS client mount/vnode callbacks and `nlminfo` process state.
- Installs `nlminfo_release_p` for process cleanup.

Risks and notes:
- Pending locks intentionally avoid interruptible sleep because abort signaling to userland lockd is incomplete.
- Close path drops queued requests without answering them, marked by an internal `XXX`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_lock.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_lock.h

This header defines the kernel/userland lockd protocol records.

Key contents:
- Defines `_PATH_NFSLCKDEV` as `nfslock`.
- `struct lockd_msg_ident` identifies a request by pid, pid start time, and message sequence.
- `LOCKD_MSG_VERSION` is 3.
- `LOCKD_MSG` carries flock data, wait/getlk flags, server address, NFSv3 flag, file-handle length/data, and credentials.
- `LOCKD_ANS_VERSION` is 1.
- `struct lockd_ans` carries matched identity, errno, and optional `F_GETLK` pid result.
- Kernel declarations expose `nfs_dolock()`, `nfs_advlock_p`, and `nfs_reclaim_p`.

Important dependencies:
- Uses `NFSX_V3FHMAX` for fixed maximum file-handle storage.
- Paired directly with `nfs_lock.c` and userland `rpc.lockd`.

Risks and notes:
- Structure layout changes require version bumps because the ABI is consumed across the kernel/userland boundary.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_lock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_module.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_module.c

This is a minimal NetBSD module wrapper for `nfs_common`.

Key contents:
- Declares `MODULE(MODULE_CLASS_MISC, nfs_common, NULL)`.
- `nfs_common_modcmd()` accepts `MODULE_CMD_INIT` and `MODULE_CMD_FINI`, returning success.
- Other module commands return `ENOTTY`.

Important dependencies:
- Uses the NetBSD module framework.
- Separate from the imported FreeBSD-style `DECLARE_MODULE` paths used elsewhere in this directory.

Risks and notes:
- No real initialization lives here; common runtime setup is in the ported common module code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_module.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_mountcommon.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_mountcommon.h

This header defines the common subset of NFS client mount state used by NLM/lock-manager integration.

Key contents:
- Declares callback typedefs for extracting NFS vnode info and invalidating vnode buffers.
- Defines `struct nfsmount_common` with a mutex, mount flags/state, mount pointer, timeout/retry values, hostname, and client-specific callback pointers.
- Intended to let lock-manager code work with multiple NFS client implementations through a shared mount-state prefix/subset.

Important dependencies:
- Uses `struct vnode`, `struct mount`, `struct sockaddr_storage`, `struct lwp`, and NFS mount flag conventions.
- Consumed by lock/client integration code, especially around advisory locking.

Risks and notes:
- Callback contracts must match concrete client mount implementations; mismatches affect lockd behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_mountcommon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_nfssvc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_nfssvc.c

This file implements the tiny module that owns the `nfssvc()` syscall entry and dispatches requests to loaded NFS submodules.

Key contents:
- Registers syscall `SYS_nfssvc` through `syscall_register()` on module load and deregisters on unload.
- Defines dispatch hooks: `nfsd_call_nfsserver`, `nfsd_call_nfscommon`, `nfsd_call_nfscl`, and `nfsd_call_nfsd`.
- `sys_nfssvc()` allows unprivileged stats retrieval but requires `PRIV_NFS_DAEMON` for other flags.
- Dispatches server socket/nfsd flags, client callback flags, common id/stats/userd flags, and nfsd admin/state flags to the corresponding hook.
- Converts `EINTR`/`ERESTART` returns to success.
- Refuses unload while any submodule dispatch hook is still registered.

Important dependencies:
- Uses `nfssvc.h` flag definitions and syscall/module framework APIs.
- Other NFS modules register by setting the global function pointers.

Risks and notes:
- Dispatch depends on non-null global hooks; wrong registration/unregistration ordering causes `EINVAL` or unload `EBUSY`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_nfssvc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_var.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_var.h

This is the central prototype and cross-module dependency header for the new NFS stack.

Key contents:
- Forward-declares common client, server, state, socket, vnode, credential, request, and pNFS structures.
- Declares server state functions for clients, sessions, stateids, opens, locks, delegations, stable storage, sequence checks, and administrative dump/revoke paths.
- Declares NFS server RPC operation handlers for NFSv3/v4 operations.
- Declares server request cache and socket entry points.
- Declares common helpers from `nfs_commonsubs.c`: mbuf/XDR helpers, attribute parsing/filling, locks, id/name conversion, UTF-8 validation, socket send locks, IP parsing, and sequence/session helpers.
- Declares client common/RPC/state/vfs/bio/node functions, including open/close, delegation, locking, pNFS layout/device handling, and request helpers.
- Declares server port/VFS helpers for vnode operations, file handles, export checks, read/write/create/remove/rename/link/symlink, attr conversion, and stable storage.
- Declares common KRPC and daemon socket functions.

Important dependencies:
- Binds together files in common, client, and server NFS subdirectories.
- Includes declarations for functions implemented in this group and many outside this group.

Risks and notes:
- This header is a broad coupling point; signature changes have high blast radius across the NFS stack.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfscl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfscl.h

This header contains small NFS client-side definitions shared by the v4 client.

Key contents:
- Defines `struct nfsv4node`, a variable-length object containing file-handle bytes followed by a name.
- Defines `NFS4NODENAME()` to locate the name after the file handle.
- Defines `NFSCL_REQSTART()` as a convenience wrapper around `nfscl_reqstart()` using vnode mount/node file-handle state.
- Defines lease/renew conversion macros `NFSCL_RENEW()` and `NFSCL_LEASE()`.
- Defines special setattr flags: full attrs, size zero, size -1, and size from rdev.
- Defines `NFSCL_DEBUG()` gated by `nfscl_debuglevel`.

Important dependencies:
- Depends on client vnode/node macros such as `VFSTONFS()` and `VTONFS()`.
- Uses NFSv4 client request and attribute-fill routines declared elsewhere.

Risks and notes:
- `nfsv4node` uses trailing storage, so allocation size must match file-handle and name lengths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfscl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsclstate.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsclstate.h

This header defines NFSv4 client state structures for clients, owners, opens, locks, delegations, sessions, and pNFS layouts/devices.

Key contents:
- Defines list/head types for open owners, lock owners, locks, delegations, layouts, file layouts, device info, and recall layout records.
- Defines delegation and layout hash sizes and hash macros.
- `struct nfsclsession` stores NFSv4.1 session id, clientid, slots, callback slots, sequence id, cache size, and fore/back channel slot counts.
- `struct nfsclds` stores per-MDS/DS session/socket/verifier/server-owner data.
- `struct nfsclclient` owns client-level owners, delegations, layouts, devices, lock, renew thread, mount pointer, lease/recovery flags, callback id, and client identity bytes.
- Defines state flags for client initialization, clientid, recovery, unmount, renew thread, IPv6, delegation, and recovery-in-progress.
- Defines open owner, delegation, open, lock owner, byte-range lock, and lockowner-by-filehandle structures.
- Defines pNFS layout, file layout, layout recall, and device-info structures, including inline helpers for device addresses and stripe indices.
- Defines `NFSCL_INCRSEQID()`.

Important dependencies:
- Uses NFS protocol constants, `nfsv4stateid_t`, `nfsv4lock`, `nfsslot`, `nfssockreq`, credentials, mounts, processes, and file-handle structures.
- Consumed by NFSv4 client state and RPC code.

Risks and notes:
- Several structures use flexible/trailing storage and require exact allocation sizing.
- Session slot arrays assume a 64-bit slot bitmap capacity.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsclstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsdiskless.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsdiskless.h

This header defines diskless NFS root boot structures.

Key contents:
- Documents that diskless NFS setup is AF_INET-only and stored in network byte order.
- Defines `struct nfsv3_diskless` with interface alias, gateway, root NFS args, v3 file handle size/data, server address, root hostname, timestamp, and client hostname.
- Defines legacy `struct onfs_args` for old NFS mount argument layout.
- Defines legacy `struct nfs_diskless` with interface, gateway, old root args, v2 file handle, server address, hostname, timestamp, and client hostname.
- Exposes `nfsv3_diskless`, `nfs_diskless`, `nfs_diskless_valid`, `bootpc_init()`, `nfs_setup_diskless()`, and `nfs_parse_options()` under `_KERNEL`.

Important dependencies:
- Paired with `nfs_diskless.c`.
- Uses NFS file-handle size constants and mount argument definitions.

Risks and notes:
- The legacy and v3 structures coexist for boot compatibility; mountroot consumers must interpret `nfs_diskless_valid` correctly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsdiskless.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsdport.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsdport.h

This header provides BSD server-port macros for vnode attributes, exports, file handles, and debug/diagnostic no-ops.

Key contents:
- Defines `NFSVNO_*` macros for initializing and testing `nfsvattr` fields using NetBSD vnode attribute conventions.
- Defines `struct nfsexstuff`, a container for export flags and security flavors returned by file-handle-to-vnode lookups.
- Defines `NFSEXITCODE()` and `NFSEXITCODE2()` as no-ops for this port.
- Defines export flag tests such as exported, read-only, anonymous, strict access, and v4-only.
- Defines file-handle compare, lock-hash, file/vnode/cred/flag access, and component-name setup macros.
- Provides Darwin-style compatibility aliases for mount/statfs access and `NFSPATHLEN_T`.
- Defines min/max server file-handle size as `sizeof(fhandle_t)`.
- Defines `NFSD_DEBUG()` gated by `nfsd_debuglevel`.

Important dependencies:
- Used by common/server code to hide platform differences in attributes, exports, file handles, and vnode/mount access.

Risks and notes:
- Many macros encode platform assumptions; changing vnode attribute or export semantics requires auditing all users.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsdport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfskpiport.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfskpiport.h

This header provides KPI compatibility macros so shared NFS code can use Darwin-style names on BSD/NetBSD.

Key contents:
- Defines `mount_t` and mount access macros for statfs and flags.
- Provides vnode mount/type access macros.
- Defines `mbuf_t` and wrappers for mbuf free/data/length/next/header length mutations.
- Defines user-address cast macros.
- Provides uio residual, iov base, and iov length accessor/mutator macros.

Important dependencies:
- Included by common NFS code through the port layer.
- Wraps native NetBSD/FreeBSD mbuf, mount, vnode, and uio structures.

Risks and notes:
- This is portability glue; semantic drift between native structures and compatibility macros can break shared code subtly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfskpiport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsm_subs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsm_subs.h

This header defines low-level NFS mbuf/XDR build and dissect helpers.

Key contents:
- `NFSM_DATAP()` advances mbuf data.
- Inline `nfsm_build()` appends space to the current reply mbuf, allocating a new mbuf when needed.
- `NFSM_BUILD()` wraps `nfsm_build()` with typed assignment.
- Inline `nfsm_dissect()` returns contiguous request bytes or calls `nfsm_dissct()` for cross-mbuf cases.
- Inline `nfsm_dissect_nonblock()` is the nonblocking variant.
- `NFSM_DISSECT()` and `NFSM_DISSECT_NONBLOCK()` set `EBADRPC` and jump to `nfsmout` on failure.
- `NFSM_STRSIZ()` extracts and bounds-checks an XDR string length.
- `NFSM_RNDUP()` rounds XDR lengths to four-byte boundaries.

Important dependencies:
- Assumes callers use `struct nfsrv_descript` fields `nd_mb`, `nd_bpos`, `nd_md`, and `nd_dpos`.
- Depends on `nfsm_dissct()` implementation in `nfs_commonsubs.c`.

Risks and notes:
- These macros assume NFS-specific control flow, especially the `error` variable and `nfsmout` label.
- Incorrect size accounting can corrupt mbuf chains or produce malformed XDR.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsm_subs.h -->