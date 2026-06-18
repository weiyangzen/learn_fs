# Group Research: group_486_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_8ccbcc5dcaf1

Scope: `Docs/research_subset_a.md`

Files researched:
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_srv.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_stats.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_strerror.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_subr.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_sys.c`

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_srv.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_srv.c

## Purpose
Implements the server-side NFSv2 RPC procedures for illumos, translating wire-level NFSv2 operations into vnode/VFS operations and returning protocol attributes, filehandles, directory data, and status codes.

## Key Elements
Provides handlers for NFSv2 `getattr`, `setattr`, `lookup`, `readlink`, `read`, `write`, `create`, `remove`, `rename`, `link`, `symlink`, `mkdir`, `rmdir`, `readdir`, and `statfs`, plus matching `*_getfh` helpers and response-free routines. It converts filehandles with `nfs_fhtovp`, enforces read-only exports with `rdonly`, maps VFS errors through `puterrno`, and forces stable-storage semantics with `VOP_FSYNC`, `VOP_PUTPAGE`, or synchronous writes where required by the protocol.

The file handles compatibility details specific to NFSv2: 32-bit attribute overflow detection, legacy device-number compression/expansion, FIFO/special-file over-the-wire encodings, `sattr_to_vattr`, `vattr_to_nattr`, and the overloaded mtime nanosecond sentinel used to request server time. `acl_perm` approximates ACL permissions in returned mode bits, using restrictive or permissive behavior depending on export flags.

Path handling includes public filehandle/WebNFS lookup, multicomponent public lookup, referral symlink fabrication, charset/name conversion through `nfscmd_convname` and directory conversion helpers, `EX_NOHIDE` mount crossing with `rfs_cross_mnt`, and climbing above a nohide exported root with `rfs_climb_crossmnt`. Several write and namespace operations check NFSv4 delegations and set `T_WOULDBLOCK` to drop replies so clients retry after recall.

Write support has both `rfs_write_sync` and clustered `rfs_write`. The clustered path builds per-file async write lists protected by a per-zone `nfs_srv_t`, sorts requests by offset, coalesces contiguous data into larger `VOP_WRITE` calls, broadcasts completions to waiting service threads, and flushes changed ranges to stable storage.

## Dependencies
Depends on illumos vnode/VFS interfaces, credentials, zones, kstats, RPC/SVC request state, stream `mblk_t` buffers, VM/page interfaces, NFS export data, NFS ACL/security support, non-blocking mandatory lock helpers, RDMA chunk helpers, WebNFS/public filehandle routines, and NFSv4 delegation/referral support.

## Behavior/Risks
The handlers contain many protocol compatibility branches, so changes can break old NFSv2 clients even if they look redundant. Error paths must preserve vnode/export reference balancing and must distinguish normal errors from delegation conflicts that require `T_WOULDBLOCK`. The clustered write path uses stack-backed queue nodes while peer service threads wait on condition variables, making lifetime, locking, and status initialization (`RFSWRITE_INITVAL`) critical. Attribute conversion intentionally rejects values not representable in NFSv2, which can surface as `EFBIG`, `EOVERFLOW`, or `NFSERR_INVAL` for modern large files or timestamps.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_stats.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_stats.c

## Purpose
Defines and initializes the per-zone NFS kstats consumed by `nfsstat(8)` for NFS client, server, and ACL procedure accounting across NFSv2, NFSv3, and NFSv4.

## Key Elements
`nfsstat_zone_init_common` allocates a writable virtual named-kstat data block from a template and installs it in a specific zone. `nfsstat_zone_fini_common` removes those kstats by module/version/name. Templates enumerate server totals (`calls`, `badcalls`, referrals), NFSv2/v3/v4 client request counters, NFSv2/v3/v4 server procedure counters, and ACL request/procedure counters.

`nfsstat_zone_init` and `nfsstat_zone_fini` manage client-side per-zone `struct nfs_stats` data for all protocol versions. `rfs_stat_zone_init` and `rfs_stat_zone_fini` manage server-side per-zone `nfs_server`, `rfsproccnt_v2`, `rfsproccnt_v3`, `rfsproccnt_v4`, `aclproccnt_v2`, and `aclproccnt_v3` kstats stored in `nfs_globals_t`.

## Dependencies
Uses illumos kstat APIs, zone IDs, kernel memory allocation, `nfs/nfs.h`, and NFSv4 protocol definitions for the NFSv4 operation list.

## Behavior/Risks
The order and size of each template are ABI-like for tools reading named kstats. Adding, removing, or reordering entries can affect `nfsstat` output and any consumers expecting existing names. The helper returns allocated kstat data even if `kstat_create_zone` fails, and fini paths unconditionally free the corresponding template-sized allocations, so init/fini pairing must remain exact.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_strerror.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_strerror.c

## Purpose
Provides NFS-specific kernel printf/cmn_err wrappers that support syslog-style `%m` substitution for selected errno values.

## Key Elements
`nfs_perror` and `nfs_cmn_err` accept an errno value plus a printf-style format, expand every `%m` sequence into a human-readable error string with `expand_format_string`, then emit through zone-aware `vzprintf` or `vzcmn_err`. `nfs_strerror` maps a small errno subset used by NFS paths, including permissions, lookup, I/O, quota, stale handle, read-only filesystem, and memory errors.

The expansion function uses a fixed 1024-byte temporary buffer, falls back to `error %d` when no string is known or the named string will not fit, and emits a truncation warning if the expanded message cannot fit.

## Dependencies
Uses NFS headers, kernel varargs, zone-aware printf/cmn_err routines, errno constants, and simple string formatting helpers.

## Behavior/Risks
This is not a general `strerror` implementation; unknown errno values intentionally become `error N` or no message if space is exhausted. The `%m` expander is simple and only treats literal `%m` specially, so format-string behavior should not be extended casually. Buffer sizing and `strlen(buf)` use during construction make truncation behavior sensitive to edits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_strerror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_subr.c

## Purpose
Contains the shared NFS client support substrate: RPC client-handle caching, NFSv2/v3 and ACL RPC call loops, rnode/filehandle caches, access and readdir caches, memory reclaim, failover, custom NFS rwlocks, status conversion, zone setup, mount label policy, and assorted vnode helper routines.

## Key Elements
The RPC layer centers on `clget_impl`, `clfree_impl`, `nfs_clget`, `acl_clget`, `rfscall`, and `aclcall`. It caches kernel RPC `CLIENT` handles per zone by program/version/transport/protocol family, attaches security handles with `sec_clnt_geth`, reclaims idle handles under memory pressure, and records client stats. `rfscall` and `aclcall` implement hard/soft/semisoft mount retry behavior, interrupt handling, timeout backoff, server down/up messages, adaptive read/write transfer-size feedback, TSOL credential cloning with `NET_MAC_AWARE`, forced-unmount/zone-shutdown bailouts, and failover retries. `rfs2call`, `rfs3call`, `acl2call`, and `acl3call` add protocol-level status handling, credential network adjustment retries, NFSv3 jukebox delay loops, and NFSv2 procedure-unavailable mapping.

The rnode layer uses a Jenkins one-at-a-time hash over NFS filehandles, per-bucket rwlocks, a freelist protected by `rpfreelist_lock`, and an `rnode_cache`. `makenfsnode`, `makenfs3node`, and `makenfs3node_va` find or create vnodes/rnodes, cache attributes, set vnode type/device data, and store failover pathnames when needed. `rp_addfree`, `rp_addhash`, `rp_rmhash`, `rfind`, `destroy_rtable`, `rflush`, and `destroy_rnode` manage vnode references, hash membership, VFS holds, dirty page flushing, and safe destruction.

Cache helpers include `nfs_access_check`, `nfs_access_cache`, `nfs_access_purge_rp`, `rddir_cache_alloc`, `rddir_cache_hold`, `rddir_cache_rele`, and debug buffer accounting. Memory reclaim frees cached credentials, symlink contents, ACLs, pathconf data, access entries, readdir caches, and finally unused rnodes if lighter reclamation is insufficient.

Failover support includes filehandle copy callbacks, `failover_safe`, `failover_newserver`, `failover_thread`, `failover_wait`, `failover_remap`, and `failover_lookup`. It selects a responsive replica, updates root and non-root rnodes to new filehandles, purges DNLC data, validates remapped object type/size, preserves cached attributes where possible, and updates operation argument filehandles via `failinfo_t`.

Other utilities convert `vattr` to NFSv2/NFSv3 setattr structures, choose inherited directory group/mode behavior, mark swap-like files, generate `.nfs...` temporary names, initialize/finalize global tables and per-zone client state, convert errno/NFS statuses for v2 and v3, free `servinfo_t` chains, implement recursive writer-aware `nfs_rwlock_t`, compare cached readdir cookies, select global-zone client behavior for the upgrade workaround, enforce Trusted Extensions mount label policy, test for a controlling terminal, check extended-attribute directory contents, and return NFS uptime.

## Dependencies
Depends on illumos vnode/VFS/page/DNLC/session/zone/label/TSOL primitives, RPC client APIs, NFS v2/v3/v4 protocol headers, NFS ACL support, rnode/mount structures, kernel memory caches, kstats, credentials/security handles, server replica metadata, synchronization primitives, and path/dirent helpers.

## Behavior/Risks
This file is highly concurrency-sensitive. Rnode hash locks, vnode locks, freelist locks, mount rnode-list locks, and per-rnode state locks have documented ordering constraints; violating them risks deadlock or use-after-free. The failover code depends on stored pathnames matching replica namespace layout and validates only type/size as a heuristic, so remapping behavior is deliberately conservative. RPC retry logic must preserve hard-mount semantics without blocking shutdown/unmount paths forever. The client-handle cache spans zone lifecycle ordering concerns, which is why `clcleanup_zone` exists separately from ZSD destruction. Status conversion has debug and non-debug differences; callers must not assume every protocol status maps uniquely to errno.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_sys.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_sys.c

## Purpose
Implements the `nfssys` system-call dispatcher and related exported entry points for NFS kernel control operations initiated by userland daemons and administrative tools.

## Key Elements
`nfs_export` copies in `exportfs_args` using the caller data model and calls `exportfs`. `nfssys` switches on `enum nfssys_op`, applies `secpolicy_nfs` to privileged operations except `NFS_REVAUTH` and `NFS4_SVC`, copies in data-model-aware argument structures, and dispatches to NFS, RPC, lock manager, logging, idmap, mountd, and nfscmd subsystems.

Handled operations include NFSv4 client state clearing, RPC service pool create/wait/run, RDMA NFS service startup, NFS server daemon entry, exportfs, filehandle lookup, credential revocation, lock manager service/shutdown, NFS log flush, NFSv4 callback service, NFSv4 server quiesce registration, idmap argument delivery, distributed stable storage path delivery, ephemeral mount timeout setting, mountd door argument passing, and nfscmd door argument passing.

Global hooks such as `nfs_srv_quiesce_func` and `nfs_srv_dss_func` are filled by the server module when loaded. `rfs4_lease_time`, `rfs4_grace_period`, and `nfs4_dss_buflen` provide shared NFSv4 server/control state.

## Dependencies
Uses illumos syscall copyin/datamodel support, credential policy checks, RPC service pool APIs, NFS server/client/lock/log/idmap/export helpers, RDMA service startup, kernel memory allocation, and function pointers supplied by the `nfssrv` module.

## Behavior/Risks
This is a privilege and ABI boundary. Every case must copy in the correct structure layout for native and non-native data models and return errors through `set_errno`. Some operations rely on call ordering, such as `NFS4_DSS_SETPATHS_SIZE` before `NFS4_DSS_SETPATHS`, and module-loaded hooks return `ENOTSUP` when unavailable. Expanding this switch requires careful policy decisions because a missing privilege gate could expose server-control operations to unprivileged callers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_sys.c -->