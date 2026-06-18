# Group Research: group_481_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_a890500072a8

Scope checked against `Docs/research_subset_a.md`: both files are under `sources/os/illumos/illumos-gate`, which is included in subset A. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_subr.c

NFSv4 client support routines for shared protocol helpers, RPC handle caching, compound RPC dispatch, volatile-filehandle remapping, readdir caching, zone-local client state, direct I/O toggling, and failover classification.

Key responsibilities:
- Provides basic NFSv4 object helpers: filehandle copy/compare, stateid compare, errno/NFSv4 status translation, NFSv4 time conversion, UTF-8/string conversion, directory-name validation, and bad-owner diagnostics.
- Manages per-zone RPC client-handle caches through `clget4()`, `clfree4()`, `clreclaim4_zone()`, zone init/fini hooks, and the global low-memory reclaim callback.
- Implements `authget()` security-handle selection, including server-provided SECINFO retry state via `SV4_TRYSECINFO`.
- Implements the central client RPC path: `nfs4_rfscall()` performs RPC handle acquisition, signal masking, hard/soft mount retry behavior, timeout backoff, failover return decisions, zone-shutdown/forced-unmount exits, and recovery fact/event queueing. `rfs4call()` wraps this for NFSv4 `COMPOUND` calls and updates per-operation stats.
- Supports failover and volatile filehandle recovery with `remap_lookup()`, `nfs4_remap_file()`, `nfs4_check_remap()`, and `nfs4_make_dotdot()`, rebuilding filehandles from stored path state and updating attributes, parent handles, stubs, and shared filehandle records.
- Frees server information chains with `sv4_free()` and prints/debugs filehandles and rnodes under DEBUG.
- Implements an AVL-backed NFSv4 readdir response cache keyed by cookie and request count, with reference counting, wait/broadcast behavior while entries are being filled, purge, destroy, and interrupt handling.
- Initializes and tears down NFSv4 subr state with `nfs4_subr_init()` and `nfs4_subr_fini()`, including the client-handle cache and zone key.
- Implements `nfs4_directio()` and `nfs4_has_pages()` for page-cache flushing/direct I/O state.
- Classifies failover-worthy RPC errors through `nfs4_try_failover()` and the indexed `try_failover_table`.
- Provides `nfs4_error_zinit()` and `nfs4_error_init()` convenience initializers.

Major dependencies:
- Kernel primitives: zones, kmem caches, kstats, AVL trees, mutexes, condition variables, credentials, signals, vnode/VFS, and DTrace/SDT probes.
- RPC/TLI client APIs: `CLIENT`, `CLNT_CALL`, `clnt_tli_kcreate`, `clnt_tli_kinit`, auth handles, and RPC status/error structures.
- NFSv4 client internals from `nfs4.h`, `rnode4.h`, and `nfs4_clnt.h`, including `mntinfo4_t`, `servinfo4_t`, `rnode4_t`, recovery state, shared filehandles, filename/path helpers, compound XDR helpers, recovery queues, and attribute cache functions.

Important control flow:
- Normal over-the-wire calls go through `rfs4call()` -> `nfs4_rfscall()` -> `nfs_clget4()`/`clget4()` -> `authget()` -> `CLNT_CALL()` -> `clfree4()`.
- Hard mounts keep retrying retryable RPC failures with exponential backoff unless shutdown, forced unmount, interrupt, unrecoverable RPC status, or failover handling takes over.
- Failover mounts return selected transport errors to higher recovery code instead of looping locally.
- Remap recovery uses the mount root and the rnode’s saved path to issue lookup compounds, then validates type/size where requested before replacing the rnode’s filehandle and cached attributes.
- Readdir cache lookup may drop locks for sleeping allocation and re-search afterward; callers must hold the rnode read lock and state lock on entry.

Concurrency and locking:
- Client-handle cache state is protected by `nfscl_chtable4_lock`.
- Global per-zone client data is protected by `nfs4_clnt_list_lock`.
- Readdir cache trees are protected by the rnode state lock, while individual cache entry refcounts have their own mutex.
- Remap and recovery paths coordinate with mount recovery locks, rnode state locks, and shared filehandle update helpers.
- Several paths deliberately avoid holding locks across sleeping allocation or RPC.

Notable risks:
- `str_to_utf8()` sets zero-length state for null/empty input but does not return before `strlen(nm)`, so callers must not pass null despite the apparent guard.
- The UTF-8 conversion routines mostly validate embedded nulls and slash/name restrictions; they do not perform full RFC UTF-8 validation.
- `nfs4_rfscall()` has many mount-state exits; changes can easily affect forced unmount, zone shutdown, recovery-thread behavior, or hard-mount retry semantics.
- Readdir cache correctness depends on precise lock ordering around `r_rwlock`, `r_statelock`, entry condition variables, and purge/removal flags.
- Filehandle remap updates must preserve vnode type/size expectations or intentionally mark recovery failed; otherwise stale or crossed-server objects could be misrepresented.
- The failover table assumes RPC enum values are stable enough for direct indexing, with fallback behavior if they are not.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vfsops.c

NFSv4 VFS implementation for illumos: module/VFS registration, mount argument ingestion, root vnode creation, mount-root support, unmount/freevfs handling, server/clientid lifecycle, referrals, symlink resolution during mount, replica/failover server lists, and SETCLIENTID lease setup.

Key responsibilities:
- Registers NFSv4 VFS and vnode operation tables in `nfs4init()` and releases module-level VFS state in `nfs4fini()`.
- Copies and validates user mount arguments in `nfs4_copyin()`, including transport config, server address, server path, hostname, secure mount data, AUTH_DH/RPCSEC_GSS security data, and failover-linked argument chains.
- Frees copied mount arguments with `nfs4_free_args()` and deep-copies security data with `copy_sec_data()` / `copy_sec_data_gss()`.
- Implements `nfs4_mount()`: permission checks, remount restrictions, trigger-stub handling for ephemeral mounts, transport validation, servinfo chain construction, RDMA substitution, security flavor setup, failover-list validation, zone/labeled-system policy checks, root vnode acquisition, SETCLIENTID setup, mount option application, and ephemeral mount recording.
- Resolves mount-time symlinks and referrals through `getlinktext_otw()`, `resolve_sympath()`, `resolve_referral()`, `update_servinfo4()`, `extract_referral_point()`, and `setup_newsvpath()`.
- Gets root filehandles and filesystem capabilities in `nfs4getfh_otw()`, building `PUTROOTFH`/`PUTPUBFH`, `GETFH`, `LOOKUP`, and `GETATTR` compounds, handling `NFS4ERR_SYMLINK`, `NFS4ERR_MOVED`, recovery-worthy errors, stale mount retries, and server fsinfo limits.
- Creates the mount state in `nfs4rootvp()`: initializes `mntinfo4_t`, VFS device/fsid fields, async queues/threads, per-mount locks/lists/kstats, shared filehandle table, open-owner state, root vnode, root/parent filehandles, zone references, and replica filtering.
- Implements VFS operations: `nfs4_unmount()`, `nfs4_root()`, `nfs4_statvfs()`, `nfs4_sync()`, `nfs4_vget()` returning `EREMOTE`, `nfs4_mountroot()` for diskless root, and `nfs4_freevfs()`.
- Manages client identity and lease state with global `nfs4_server_lst`, `nfs4setclientid()`, `nfs4setclientid_otw()`, server creation, mount-to-server list insertion/removal, lease-thread start/termination, and server refcount teardown.
- Supports failover server movement via `nfs4_move_mi()`, moving an `mntinfo4_t` from one `nfs4_server_t` to another and preserving open-file state counts.
- Handles forced unmount cleanup through `async_free_mount()`, `nfs4_free_mount_thread()`, and `nfs4_free_mount()`, waiting for outstanding over-the-wire calls and recovery before removing server linkage and destroying rnodes.

Major dependencies:
- Kernel VFS/vnode interfaces, mount argument ABI, zones, credentials, labeled security policy, kstats, kmem, CPR callbacks, async thread creation, DNLC, and root boot helpers.
- RPCSEC/AUTH_DH/RPCSEC_GSS security modules.
- NFSv4 client internals: compound calls, recovery framework, rnode table, shared filehandle table, async manager, inactive thread, ephemeral/mirror mount support, callbacks, lease renewal, open-owner tracking, referrals, and mount option parsing.

Important control flow:
- Regular mount path: `nfs4_mount()` copies args, builds `servinfo4_t` list, calls `nfs4rootvp()`, calls `nfs4setclientid()`, applies options, and records ephemeral mount metadata if needed.
- Root filehandle path: `nfs4rootvp()` initializes mount state first, then each replica is probed by `nfs4getfh_otw()`; duplicate or failing replicas are marked `SV4_NOTINUSE`, and the first usable server becomes `mi_curr_serv`.
- Mount-time path traversal retries failed stale/symlink/referral cases by restoring a saved `servinfo4_t` snapshot and redriving the lookup compound up to `nfs4_max_mount_retry`.
- SETCLIENTID path: find or create a shared `nfs4_server_t`, serialize pending clientid setup with `N4S_CLIENTID_PEND`, issue `SETCLIENTID` plus `SETCLIENTID_CONFIRM`, cache lease time and propagation delay, attach the mount to the server, and start lease renewal if needed.
- Normal unmount stops async work, flushes rnodes, handles ephemeral tree activation, removes the mount from server and zone lists, and relies on freevfs to drop the initial `mntinfo4_t` hold.
- Forced unmount marks the VFS unmounted and frees mount state asynchronously when possible.

Concurrency and locking:
- `nfs4_server_lst_lock` protects the global server list; each `nfs4_server_t` has `s_lock`.
- `mi_recovlock` controls mount/server linkage relative to recovery and over-the-wire operations.
- Mount/unmount state uses `mi_lock`, async locks/CVs, rnode-list locks, and server pending/clientid CVs.
- Forced unmount cleanup waits for `s_otw_call_count` and `mi_in_recovery` to drain before breaking server links.
- Zone references and VFS references are deliberately held while mount records are visible through server lists or worker threads.

Notable risks:
- Mount setup is partially initialized before the first root lookup succeeds; every error path must release zone refs, async threads, rnodes, servinfo chains, kstats, and `mntinfo4_t` holds consistently.
- `copy_svp()` appears to copy `svp->sv_dhsec` from the newly allocated target rather than the source, so AUTH_DH saved-state behavior should be reviewed if this path is active.
- Referral and symlink path rewriting uses fixed `MAXPATHLEN` buffers and slash-counting logic; malformed or edge-case paths can stress truncation/error handling.
- `nfs4getfh_otw()` encodes detailed assumptions about compound result positions; any change in lookup compound construction must keep index math synchronized.
- SETCLIENTID retry and `NFS4ERR_CLID_INUSE` handling intentionally has limited robustness, as noted by in-code comments.
- Server refcounts, VFS holds, and mount list links are tightly coupled; incorrect removal while open files remain can break lease renewal or recovery lookup paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_vfsops.c -->