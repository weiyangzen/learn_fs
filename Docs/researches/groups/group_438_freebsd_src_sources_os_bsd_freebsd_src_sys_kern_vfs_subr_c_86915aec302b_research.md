# Group Research: group_438_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_vfs_subr_c_86915aec302b

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/freebsd-src` source tree. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_subr.c

Read completely: 7537 lines, 187007 bytes.

Implements FreeBSD's core VFS vnode and mount support layer. It manages vnode table initialization, vnode allocation/recycling/reclaim, mount busy references, per-mount vnode lists, vnode-buffer association, syncer scheduling, periodic inactive/msync processing, poll/kqueue/inotify event glue, access checks, root vnode caching, mount vnode iteration helpers, and DDB/sysctl diagnostics.

Major structures and global state:
- Tracks vnode population with `numvnodes`, `desiredvnodes`, `wantfreevnodes`, `freevnodes`, `vlowat`, `vhiwat`, `gapvnodes`, reclaim counters, allocation sleep counters, and `vnlruproc` wake state.
- Maintains global vnode LRU-ish ordering in `vnode_list`, with marker vnodes for free and reclaim scans.
- Uses `vnode_zone` as the UMA/SMR-backed vnode allocator and `vfs_smr` for lockless vnode lookup/ref acquisition paths.
- Uses `buf_trie_zone` and `buf_trie_smr` for per-bufobj clean/dirty buffer pctries.
- Defines syncer state with `syncer_workitem_pending`, `sync_mtx`, `sync_wakeup`, `syncer_delayno`, `rushjob`, `syncer_state`, and per-delay work queues of dirty `bufobj`s.
- Uses per-CPU `struct vdbatch` to batch requeueing of newly free vnodes and reduce global `vnode_list_mtx` traffic.
- Provides vnode type and mode conversion tables, vnode/mount sysctl nodes, filesystem event knlists, and optional DDB display commands.

Initialization and sizing:
- `vntblinit()` computes `desiredvnodes` from physical memory and kernel virtual memory limits, clamps it to `MAXVNODES_MAX`, initializes vnode/mount locks and list markers, creates `vnode_zone`, preallocates buffer trie nodes, allocates vnode counters, initializes syncer queues, and sets up per-CPU vnode requeue batches.
- `vnode_init()` zeroes new vnode memory, initializes vnode/interlock/lockmgr state, bufobj state, namecache state, range locks, dead state, hold-count SMR guard, and inserts the vnode before the free marker.
- `vnode_fini()` removes a vnode from global lists, destroys range locks, lockmgr/interlock state, and bufobj locks.
- KASAN-specific constructor/destructor logic keeps list/batch fields valid while marking most freed vnode memory poisoned.

Mount and VFS helpers:
- `vfs_busy()` and `vfs_unbusy()` implement mount busy locking/reference semantics around unmount, including fast per-thread operation accounting and slow `MNTK_UNMOUNT`/`MNTK_REFEXPIRE` handling.
- `vfs_getvfs()` looks up mounts by `fsid`; `vfs_busyfs()` adds a lockless direct-mapped fsid cache but validates after busying.
- `vfs_suser()` checks jail constraints and mount-owner privilege, with delegation-aware filesystem handling.
- `vfs_getnewfsid()` generates unique mount fsids using a guarded rolling base.
- `vfs_timestamp()` centralizes file timestamp precision policy.
- `vattr_null()` initializes vnode attributes to `VNOVAL`/empty defaults.
- `vfs_unmountall()` forcibly unmounts filesystems during reboot in reverse mount order, deferring `/dev` until after root-dependent mounts.

Vnode allocation and LRU/reclaim:
- `vn_alloc()` optimistically increments `numvnodes`, falls back to `vn_alloc_hard()` under pressure, and always returns a vnode via `M_WAITOK`.
- `vn_alloc_hard()` may recycle one free vnode, wake `vnlru`, sleep briefly for reclamation, or grow over target when necessary.
- `vnlru_proc()` is the background vnode recycler. It first uses a light path that only recycles free vnodes, then escalates through forced passes that reclaim unused non-free vnodes based on resident-page thresholds and namecache-source conditions.
- `vlrureclaim()` scans the global vnode list with a marker, skips active/held/free/doomed/large-object vnodes, starts writes nonblocking, locks candidates, and calls `vgonel()` when reclaimable.
- `vnlru_free_impl()` recycles free vnodes, optionally constrained to a filesystem ops vector, and intentionally avoids requeueing failures to prevent frozen-write loops.
- `vtryrecycle()`, `vrecycle()`, and `vrecyclel()` reclaim unused vnodes while respecting vnode locks, filesystem write suspension, hold counts, and doomed state.
- `vnlru_alloc_marker()`/`vnlru_free_marker()` and mount-list marker helpers support safe long scans that may drop locks.

Buffer-object and syncer behavior:
- `bufobj_invalbuf()` flushes and invalidates all buffers for a `bufobj`, optionally saving dirty data first, waiting for outstanding I/O, and removing VM cache pages when appropriate.
- `vinvalbuf()` wraps `bufobj_invalbuf()` for vnodes and skips borrowed VM objects.
- `flushbuflist()` walks clean/dirty buffer lists, filters normal vs alternate data, locks each buffer with timeout semantics, writes delayed buffers when saving, or invalidates/releases them.
- `vtruncbuf()` invalidates buffers past a new EOF, writes metadata buffers, waits for output, and updates vnode pager size.
- `v_inval_buf_range()` and `v_inval_buf_range_locked()` invalidate selected logical-block ranges and remove corresponding pages.
- `bgetvp()` attaches a buffer to a vnode clean list with pctrie duplicate detection; `brelvp()` removes it and drops the vnode hold.
- `reassignbuf()` moves a buffer between clean and dirty bufobj lists, sets `BO_NONSTERILE`, and adds/removes the bufobj from the syncer worklist using file/directory/metadata delay policies.
- `sched_sync()` is the filesystem syncer daemon. It advances round-robin delay slots, fsyncs dirty work items lazily, honors rush requests, speeds up during shutdown, and pats the watchdog while draining.
- `sync_fsync()`, `sync_inactive()`, and `sync_reclaim()` implement the special syncer vnode used per mount by `vfs_allocate_syncvnode()`/`vfs_deallocate_syncvnode()`.

Vnode references, inactive, and reclaim:
- `getnewvnode()` assigns a vnode from the allocator or per-thread reserve, resets identity fields, updates lock witness names, initializes counters/sequence counter, sets ops and bufops, applies MAC labels, initializes hash value, and returns the constructed-but-not-mounted vnode.
- `vget_prep_smr()`, `vget_prep()`, `vget_finish()`, `vget_finish_ref()`, `vref()`, and `vrefact()` convert hold/use references into usable vnode references, including SMR-safe failure paths.
- `vrele()`, `vput()`, and `vunref()` release use counts with different lock-state contracts. Last-use release goes through `vput_final()`, which performs or defers inactive processing.
- `vhold()`, `vholdnz()`, `vhold_smr()`, `vdrop()`, `vdropl()`, and recycling-specific drop variants maintain hold counts, free-vnode accounting, SMR guard state, and global-list requeueing.
- `vlazy()`, `vunlazy()`, `vdefer_inactive()`, and `vfs_periodic*()` manage deferred inactive processing on per-mount lazy vnode lists.
- `vinactive()`/`vinactivef()` call `VOP_INACTIVE()`, coordinate `VI_OWEINACT` and `VI_DOINGINACT`, and clean vnode pages asynchronously unless `VV_NOSYNC` is set.
- `vflush()` walks all mount vnodes, syncing write-close cases, skipping system vnodes when requested, forcing or rejecting busy vnodes, and handling root vnode reference allowances.
- `vgonel()` is the central teardown path: marks the vnode doomed, begins seqc modification, removes lazy state, purges namecache, notifies upper mounts, closes active vnodes, runs inactive if owed, reclaims socket state, invalidates buffers, destroys VM vnode objects, calls `VOP_RECLAIM()`, purges advisory locks, removes from mount lists, resets to dead vnode ops, and transitions to `VSTATE_DEAD`.
- `freevnode()` verifies all vnode state is clean, destroys MAC/poll state as needed, clears special fields and flags, ends the seqc free pairing, and returns the vnode to UMA.

Events, polling, and operation hooks:
- `v_addpollinfo()` lazily allocates per-vnode poll/kqueue/inotify state; `vn_pollrecord()` records select/poll interest and consumes queued events.
- `vfs_kqfilter()` attaches vnode read/write/event knotes, takes vnode holds, and sets `V2_KNOTE`; `filt_vfsdetach()` drops those holds.
- `filt_vfsread()`, `filt_vfswrite()`, and `filt_vfsvnode()` implement vnode filter readiness, revoke handling, EOF/oneshot state, and file-size based read readiness.
- `vfs_event_signal()` and `fs_filtops` expose global filesystem event knotes.
- Many `vop_*_pre/post` hooks wrap filesystem operations to maintain vnode sequence counters, send kqueue hints, send inotify events, validate debug invariants, notify upper mounts for unlink/reclaim, and manage temporary rename holds.
- `vop_rename_pre()`/`vop_rename_post()` are careful about multi-vnode holds and event delivery but intentionally avoid generic seqc rename bracketing because some filesystems relookup mid-rename.
- Debug hooks under `INVARIANTS` assert correct lock state for lookup, fsync, strategy, lock/unlock, and inactive VOPs.

Access, attributes, and utility APIs:
- `vaccess_vexec_smr()` provides SMR-safe execute/search permission checks for fast path lookup, falling back with `EAGAIN` when MAC modules may need full checks.
- `vaccess()` implements Unix DAC plus privilege fallback for `VEXEC`, `VREAD`, `VWRITE`, `VADMIN`, and `VAPPEND`, with directory lookup privilege distinct from file execute privilege.
- `extattr_check_cred()` enforces system vs user extended attribute credential rules.
- `vfs_unixify_accmode()` reduces rich `accmode_t` rights to Unix/POSIX ACL-compatible bits or rejects delete semantics that cannot be represented.
- `vn_dir_check_exec()` applies directory execute checks unless lookup explicitly used `NOEXECCHECK`.
- `vn_isdisk_error()`/`vn_isdisk()` validate character device vnodes backed by disk devices.
- `vn_need_pageq_flush()` tests whether a vnode's VM object may need dirty-page flushing.
- `vfs_read_dirent()` moves one directory entry to user I/O and appends NFS-style cookies when requested.
- `init_va_filerev()` seeds file revision values from uptime.
- `vn_getsize_locked()`/`vn_getsize()` fetch and validate vnode size through `VOP_GETATTR()`.

Root caching, iteration, sysctl, and diagnostics:
- `vfs_cache_root()` uses mount operation-thread fast paths to return a referenced/locked cached root vnode, falling back to `VFS_CACHEDROOT()` and clearing doomed cached roots.
- `vfs_cache_root_clear()` and `vfs_cache_root_set()` support mount code that owns `mnt_vfs_ops` serialization and updates root vnode seqc/reference state.
- `__mnt_vnode_first_all()`, `__mnt_vnode_next_all()`, and marker-free helpers iterate all non-doomed vnodes on a mount while holding marker references safely.
- `__mnt_vnode_first_lazy()`, `__mnt_vnode_next_lazy()`, and lazy marker helpers iterate per-mount lazy vnode lists with filtering and lock-order-aware relocking.
- `sysctl_vfs_conflist()` and compatibility helpers export filesystem configuration lists; deprecated generic VFS sysctl handling remains for old userland.
- `sysctl_vfs_ctl()` dispatches filesystem-specific sysctl requests by fsid and validates filesystem type names.
- `vn_printf()` prints detailed vnode state, flags, counters, lock info, VM object/buffer counts, and filesystem-specific data.
- DDB commands display locked vnodes, individual vnodes, and mount details including flags, stats, credentials, counters, syncer state, and active/inactive vnode lists.

Key invariants and risks:
- Vnode lifetime is split across `v_usecount`, `v_holdcnt`, `VHOLD_NO_SMR`, lock state, `v_state`, `VIRF_DOOMED`, mount-list membership, lazy-list membership, and VM object holds. Any imbalance can cause use-after-free, leaked vnodes, or unreclaimable mounts.
- SMR lookup requires type-stable vnode memory and strict `VHOLD_NO_SMR` transitions. `vhold_smr()` and `vdropl_final()` are intentionally race-sensitive.
- Lock ordering is central: mount busy locks precede vnode locks for cross-mount lookup; mount list locks, vnode interlocks, bufobj locks, vnode locks, and syncer locks are combined with marker scans and try-lock fallbacks to avoid deadlocks.
- `vgonel()` has many side effects and must run with the vnode exclusively locked and interlocked; weakening its state transitions can leave buffers, VM objects, advisory locks, namecache entries, upper-mount dependencies, or poll state attached to dead vnodes.
- Buffer list membership depends on `BX_VNDIRTY`/`BX_VNCLEAN`, pctrie identity, delayed-write flags, syncer `BO_ONWORKLST`, and bufobj locks staying consistent.
- The syncer worklist and dirty-buffer delays are shutdown-sensitive; incorrect worklist accounting can hang shutdown or lose lazy writeback.
- `vnlru` is explicitly heuristic and contains documented limitations around large RAM systems, ZFS/non-VM-object filesystems, frozen writes, and reclaim target tuning.
- `vflush()` and forced unmount paths can race active users and must carefully handle root refs, write-close semantics, busy vnodes, and filesystem suspension.
- Operation hooks maintain sequence counters and event delivery for namecache/fast-lookup consumers; missing begin/end pairs or event notifications can make lockless lookup observe inconsistent namespace state.
- `vfs_cache_root()` assumes mount operation serialization and validates against doomed roots; stale root caching can return dead vnodes or leak root references.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/vfs_subr.c -->