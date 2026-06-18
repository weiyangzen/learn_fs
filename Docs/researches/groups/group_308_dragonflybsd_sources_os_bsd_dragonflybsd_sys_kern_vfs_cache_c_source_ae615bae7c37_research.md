# Group Research: group_308_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_vfs_cache_c_source_ae615bae7c37

Scope checked against `Docs/research_subset_a.md`: all four files are within `sources/os/bsd/dragonflybsd`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_cache.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_cache.c

This file implements DragonFly BSD's namecache core: pathname component caching, vnode association/disassociation, negative cache entries, mountpoint traversal caching, namecache invalidation, root namecache setup, `getcwd`, and full-path reconstruction.

The central model is `struct namecache` as a tree plus hash table entry. Lookups are keyed by `(parent ncp pointer, component name)` using `nchashtbl`. Entries may be unresolved, positive-resolved to a vnode, or negative-resolved with `nc_vp == NULL`. Reference accounting is fundamental: a natural reference, a hash/topology reference, and either vnode-namecache or negative-list association references are carefully balanced. The code relies on the invariant that a final `1 -> 0` transition only destroys an unresolved, unlinked entry.

Key structures and caches:
- `struct nchash_head`: per-bucket list plus spinlock for namecache hash entries.
- `struct pcpu_ncache`: per-CPU negative-entry list, deferred zap count, and batched cache statistics.
- `struct mntcache` / `mntcache_elm`: per-CPU cache for frequently held mount and namecache references, reducing atomic refcount traffic.
- `struct ncmount_cache`: global set-associative cache mapping `(current mount, ncp)` to a mounted filesystem crossing result.

Important exported namecache lifecycle operations include `cache_hold`, `cache_drop`, `cache_copy`, `cache_get`, `cache_put`, `cache_lock`, `cache_unlock`, `cache_lock_maybe_shared`, `cache_zero`, `cache_changemount`, and `cache_drop_and_cache`. These wrap namecache and mount references together in `struct nchandle`.

Locking rules are explicitly encoded and high-risk:
- Namecache locks are generally ordered child-to-parent.
- Parent and child must both be locked to link a child into a parent's `nc_list`.
- Hash bucket spinlocks protect hash membership, but many lookup paths use generation/update-counter style validation to reduce blocking.
- Shared namecache locks are allowed for resolved entries unless disabled via `debug.ncp_shared_lock_disable`; unresolved or reclaimed vnode cases fall back to exclusive locking.

Association functions:
- `_cache_setvp` resolves an ncp to a vnode or to a negative entry, attaching to `vp->v_namecache` or a per-CPU negative list.
- `_cache_setunresolved` removes vnode or negative-list association and restores unresolved state.
- `_cache_auto_unresolve_test` and `_cache_auto_unresolve` expire timed entries and stale negative entries when a mount's namecache generation changes.
- `cache_settimeout` supports NFS-style timeout invalidation.

Invalidation and cleanup:
- `cache_inval` and `_cache_inval_internal` recursively invalidate topology, with deep recursion handled by `MAX_RECURSION_DEPTH` and resume tracking.
- `cache_inval_vp`, `cache_inval_vp_nonblock`, and `cache_inval_vp_quick` invalidate vnode associations, including a quick nonblocking path intended to help vnode recycling make progress.
- `cache_unlink` marks an entry destroyed and attempts vnode deactivation where appropriate.
- `cache_zap` removes trivial unresolved entries from topology and frees them, optionally walking upward.
- `cache_hysteresis`, `_cache_cleanneg`, `_cache_cleanpos`, and `_cache_cleandefered` enforce negative and unresolved cache pressure limits.

Lookup and resolution:
- `cache_nlookup` is the main new API lookup path. It returns a referenced, locked `nchandle`, creating unresolved entries when needed, reusing destroyed entries where possible, and updating per-CPU stats.
- `cache_nlookup_maybe_shared` is a nonblocking shared-lock lookup for already-resolved entries.
- `cache_nlookup_nonblock` is a nonblocking path used by NFS readdirplus-like code.
- `cache_nlookup_nonlocked` is an optimized resolved-entry lookup that returns failure on unstable state.
- `cache_resolve` resolves an unresolved ncp via `VOP_NRESOLVE`, handling destroyed entries, missing parent vnodes, mount roots, vnode reclaim races, and `EAGAIN` retry.
- `cache_resolve_mp` resolves a mount root through `VFS_ROOT`.
- `cache_resolve_dvp` resolves and returns a referenced parent directory vnode.

Mountpoint support:
- `cache_findmount` uses the set-associative `ncmount_cache` to avoid frequent `mountlist_scan` calls when crossing mountpoints.
- `cache_ismounting` precaches new mountpoint mappings and invalidates stale ones.
- `cache_unmounting` clears cache entries related to a mount while holding per-CPU unmount interlocks.
- `cache_clrmountpt` clears `NCF_ISMOUNTPT` after verifying no mount still references the ncp.

NFS and disconnected vnode support:
- `cache_fromdvp` reconstructs namecache topology from a directory vnode, mainly for NFS server file-handle paths.
- `cache_fromdvp_try` and `cache_inefficient_scan` perform parent lookup and directory scans when ordinary topology is absent or paths are extremely deep.
- This is intentionally isolated because disconnected-namecache merging would complicate the core model.

Path reconstruction:
- `kern_getcwd` and syscall wrapper `sys___getcwd` build the current working directory path from `fd_ncdir` up to `fd_nrdir`, crossing mount roots through `mnt_ncmounton`.
- `cache_fullpath` and `vn_fullpath` reconstruct paths from arbitrary nchandles or vnodes, with optional mountpoint guessing.

Initialization and stats:
- `nchinit` allocates per-CPU namecache state, initializes `nchstats`, creates the hash table, and initializes mount cache locks.
- `cache_allocroot` creates root namecache handles.
- `vfs_cache_setroot` installs the system root vnode/namecache handle.
- `vfscache_rollup_cpu` rolls per-CPU counters into global sysctl-visible totals.

Notable dependencies include `sys/namecache.h`, `sys/nlookup.h`, vnode and mount internals, `VOP_NRESOLVE`, `VFS_ROOT`, mountlist scanning, per-CPU globaldata, lockmgr, spinlocks, vnode hold/ref APIs, and sysctl.

Implementation risks for future changes:
- Refcount transitions, vnode hold/drop balancing, and negative-list membership are tightly coupled.
- Many paths intentionally release and reacquire locks to avoid deadlocks; race rechecks are not optional.
- Mount cache entries store namecache pointers for comparison without full ncp references, so invalidation ordering matters.
- `NCF_DESTROYED`, `NCF_UNRESOLVED`, `NCF_DEFEREDZAP`, `NCF_ISMOUNTPT`, and generation updates drive correctness across lookup, invalidation, rename, and path reconstruction.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_cluster.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_cluster.c

This file implements clustered buffer-cache I/O for DragonFly BSD: synchronous and asynchronous read clustering, read-ahead marking, write clustering, write-behind heuristics, and clustered I/O completion fanout back to component buffers.

The file replaces older vnode-local clustering state with `struct cluster_cache`, a 4-way set-associative cache over vnodes and 1 MB logical zones. It tracks recent write clustering fields such as `v_lastw`, `v_cstart`, `v_lasta`, and `v_clen`. The cache is intentionally heuristic because vnode recycling can make entries stale, but it must remain self-consistent enough not to cluster unrelated offsets.

Tunables:
- `vfs.write_behind`: disables, enables, or backs off write-behind.
- `vfs.write_behind_minfilesize`: avoids write-behind for smaller files by default.
- `vfs.max_readahead`: caps desired read-ahead bytes.

Read path:
- `cluster_readx` replaces `bread()` with synchronous requested-block I/O plus asynchronous read-ahead.
- `cluster_readcb` is the asynchronous callback-based version.
- Both compute read-ahead from `minreq`, `maxreq`, `max_readahead`, file size, and block size.
- `B_RAM` marks a read-ahead trigger buffer; when later hit from cache, the code launches the next read-ahead window.
- `VOP_BMAP` is used to determine physical contiguity and burst size. If mapping fails or returns `NOOFFSET`, the path falls back to single-buffer I/O.

Cluster read construction:
- `cluster_rbuild` combines physically contiguous, VMIO-backed buffers into a synthetic cluster pbuf.
- It avoids buffers already cached, locked, partially valid, dependency-blocked for reads, or not VMIO-backed.
- It maps collected pages into the pbuf with `pmap_qenter_noinval`.
- Fully valid pages are replaced with `bogus_page` and flagged with `B_HASBOGUS` to avoid unnecessary disk reads.
- The function preserves the original requested buffer as part of the cluster when possible and returns either the cluster buffer or the original buffer.

Completion path:
- `cluster_callback` handles completion for clustered reads and writes.
- It propagates errors to component buffers, panics on unexpected short cluster I/O, unmaps pbuf pages, releases the pbuf to vnode or mount pbuf pools, and calls `biodone` for each component.
- For writes, it calls `bundirty` on successful component completion.
- For direct I/O component buffers it restores `B_RELBUF` if needed.

Write path:
- `cluster_write` implements delayed clustered writes for normal filesystem writes.
- It detects logical and physical sequentiality using the cluster cache and `bio_offset`.
- It may call `VOP_REALLOCBLKS` to make delayed buffers physically contiguous.
- It delays, asynchronously writes, or write-behind flushes depending on sequentiality, async mount state, `seqcount`, memory pressure, EOF position, and tunables.
- `cluster_wbuild_wb` gates write-behind by mode and minimum file size.

Forced async write:
- `cluster_awrite` is the clustered equivalent of `bawrite`.
- It guarantees the passed buffer is eventually initiated for I/O even if `cluster_wbuild` cannot include it.

Cluster write construction:
- `cluster_wbuild` scans dirty delayed-write buffers from a starting logical offset and builds a pbuf for contiguous compatible buffers.
- It requires buffers to be dirty, not invalid, not locked, clusterable, and compatible in VMIO/commit flags.
- It checks physical contiguity through `bio_offset` and caps page count by `vmaxiosize`.
- It handles VM page busy/io state, starts soft dependencies when needed, maps pages into the pbuf, marks running buffer space, and submits through `vn_strategy`.

Reallocation support:
- `cluster_collectbufs` gathers current cluster buffers plus the newest buffer for `VOP_REALLOCBLKS`.
- It avoids blocking on unavailable buffers and removes gaps before returning the `cluster_save` list.

Utility helpers:
- `cluster_getcache` and `cluster_putcache` manage heuristic locked cluster-cache entries.
- `calc_rbuild_reqsize` determines per-request read cluster size from desired read-ahead and device maximum.
- `cluster_append` links component buffers to a cluster bio.
- `cluster_setram` and `cluster_clrram` synchronize `B_RAM` with the first VM page's `PG_RAM`.

Notable dependencies include the buffer cache, vnode pager/VM pages, `VOP_BMAP`, `VOP_REALLOCBLKS`, `vn_strategy`, pbuf allocation, mount/vnode pbuf counters, and low-level pmap page mapping.

Implementation risks for future changes:
- Cluster pbufs borrow component pages and must pair every `vm_page_io_start`, object pip increment, and pmap mapping with the expected completion cleanup.
- `B_RAM` placement controls read-ahead behavior and can cause degenerate I/O if set incorrectly.
- Write clustering is conservative around dependencies and locked pages; relaxing checks can deadlock or violate softdep ordering.
- Mixed block sizes, especially noted for HAMMER, are guarded by file-size and block-size boundary checks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_cluster.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_conf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_conf.c

This file locates and mounts the root filesystem during boot and provides helper routines for root device selection, interactive root prompts, devfs mounting, and reporting the real root mount string.

Global root state:
- Defines `rootvnode` and `rootnch`.
- Defines `M_MOUNT` allocation type for mount structures.
- Maintains legacy `rootdevnames[2]` candidates and `rootdev`.
- Registers `vfs_mountroot` via `SYSINIT` at `SI_SUB_MOUNT_ROOT`.

Root mount selection order in `vfs_mountroot`:
- Synchronizes device probing with `sync_devs` and sleeps for tunable `vfs.root.wakedelay`.
- Tries compiled-in `ROOTDEVNAME` when boot flags request default root.
- Prompts manually for `RB_DFLTROOT` or `RB_ASKNAME`.
- Tries built-in CD-ROM candidates under `RB_CDROM`.
- Tries loader/environment `vfs.root.mountfrom`.
- Tries a preexisting `rootdev` value.
- Tries legacy machine-dependent `rootdevnames`.
- Falls back to compiled default and finally manual prompt.
- Panics if all attempts fail.

`vfs_mountroot_try` handles one or more semicolon-separated root specifications in `<vfsname>:<device>` form. It allocates a root mount through `vfs_rootmountalloc`, marks it `MNT_ROOTFS`, tries to set `rootdev` for non-HAMMER filesystems, clears read-only for memory disks, and calls `VFS_MOUNT`.

On successful root mount, it:
- Inserts the mount first in the mount list.
- Initializes system time from root fs timestamp with `inittodr`.
- Obtains `/` through `VFS_ROOT`.
- Allocates a root namecache handle if the mount did not provide one.
- Sets current process vnode cwd/root fields and namecache cwd/root fields.
- Installs root vnode/namecache through `vfs_cache_setroot`.
- Allocates a syncer vnode if needed.
- Calls `VFS_START`.

On failure, it stops the syncer thread, unbusies and frees the mount, and reports the mount error.

`vfs_mountroot_devfs` mounts `devfs` on `/dev` after root is mounted. It optionally prefixes `/dev` with `init_chroot`, resolves the path with `nlookup`, validates that the target is a directory vnode, allocates and initializes a devfs mount, calls `VFS_MOUNT`, creates a mount-root namecache if needed, marks the mount-on ncp with `NCF_ISMOUNTPT`, inserts the mount after root, allocates a syncer vnode, and starts the filesystem. Its failure path explicitly unwinds vnode ops, syncer state, mount refs, and namecache refs.

Manual root prompting:
- `vfs_mountroot_ask` prints supported syntax, lets the user list disk devices with `?`, panic, abort, or try a mount string.
- `get_line` polls the console, supports enter, backspace/delete, `#` erase-one-character behavior, and Ctrl-U line kill.

Device helpers:
- `kgetdiskbyname` strips `/dev/` if present and uses devfs lookup to return a `cdev_t`.
- `setrootbyname` updates global `rootdev` from a disk name, clearing it on failure to avoid stale retries.
- With DDB enabled, `show disk/<name>` reports the matching `cdev_t`.

Sysctl:
- `vfs.real_root` reports environment variable `vfs.root.realroot` or an empty string.

Notable dependencies include boot flags, kernel environment variables, devfs, nlookup/namecache, mount list operations, VFS mount/root/start hooks, vnode locking, syncer vnode allocation, and console polling.

Implementation risks for future changes:
- Root mount success wires together vnode cwd/root state and namecache cwd/root state; these must stay consistent.
- Devfs mount failure cleanup is manual and order-sensitive.
- `vfs_mountroot_try` parses fixed-size buffers with kernel `scanf` patterns; changing accepted syntax should preserve bounds and semicolon iteration.
- HAMMER and HAMMER2 intentionally skip `setrootbyname`, reflecting filesystem-specific root-device semantics.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_default.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_default.c

This file defines default vnode and VFS operations plus compatibility shims that translate DragonFly's newer namecache-based `VOP_N*` API into older namei-style vnode operations for filesystems that have not implemented the new API directly.

`default_vnode_vops` supplies defaults for vnode operations. Most unsupported operations return `EOPNOTSUPP`, `EINVAL`, or `ENOTTY`; selected operations use standard implementations such as `vop_stdopen`, `vop_stdclose`, `vop_stdgetattr_lite`, `vop_stdpathconf`, `vop_stdioctl`, `vop_stdfdatasync`, `vop_stdmarkatime`, `vop_stdallocate`, and `vop_stdmountctl`. New namecache operations default to compatibility wrappers like `vop_compat_nresolve`, `vop_compat_ncreate`, `vop_compat_nremove`, and `vop_compat_nrename`.

Simple default error/null helpers:
- `vop_eopnotsupp`, `vop_ebadf`, `vop_enotty`, `vop_einval`, `vop_null`, and `vop_defaultop`.
- `vop_nolookup` returns `ENOTDIR`.
- `vop_nostrategy` reports missing strategy, marks the buffer with `B_ERROR`, sets `EOPNOTSUPP`, and completes the bio.

Compatibility namecache API:
- `vop_compat_nresolve` resolves a locked namecache entry by calling old lookup on the parent directory vnode, then uses `cache_setvp` for positive or negative results and records whiteout state.
- `vop_compat_nlookupdotdot` performs old `".."` lookup for NFS/namecache topology reconstruction.
- `vop_compat_ncreate`, `vop_compat_nmkdir`, `vop_compat_nmknod`, and `vop_compat_nsymlink` perform old CREATE lookup expecting `EJUSTRETURN`, then call the corresponding old create operation and update the locked ncp.
- `vop_compat_nlink` creates a hardlink target, using `CNP_NOTVP` to avoid source/target vnode alias issues.
- `vop_compat_nwhiteout` translates create/delete/lookup whiteout operations.
- `vop_compat_nremove` performs old DELETE lookup, rejects directories, calls old remove, and marks the ncp destroyed via `cache_unlink`.
- `vop_compat_nrmdir` validates directory removal constraints, calls old rmdir, invalidates the ncp and vnode on success.
- `vop_compat_nrename` performs old delete lookup for the source and old rename lookup for the target, then calls old rename and updates topology through `cache_rename`.

Standard vnode operations:
- `vop_stdpathconf` returns POSIX constants for common `_PC_*` names.
- `vop_stdopen` initializes file object type/ops/data, takes a vnode ref, increments write/open counts.
- `vop_stdclose` decrements write/open counts with assertions.
- `vop_stdgetattr_lite` derives `vattr_lite` from full `VOP_GETATTR`.
- `vop_stdgetpages` and `vop_stdputpages` delegate to generic vnode pager routines when a mount exists.
- `vop_stdnoread` and `vop_stdnowrite` return `EINVAL`.
- `vop_stdfdatasync` delegates to `VOP_FSYNC_FP`.

Mount control and allocation:
- `vop_stdmountctl` returns visible mount flags as a string or delegates journal operations to `journal_mountctl`.
- `vop_stdallocate` implements a generic fallocate-like operation by validating/growing size with `VOP_SETATTR`, then reading existing regions or zero-filling and writing blocks across the requested range. It updates `a_offset` and `a_len` to reflect progress.
- `vop_stdioctl` implements default `FIOSEEKDATA`/`FIOSEEKHOLE` behavior for regular files, treating data as present until EOF and hole at file size.

Default VFS operations:
- `vfs_stdroot`, `vfs_stdstatfs`, `vfs_stdvptofh`, `vfs_stdquotactl`, `vfs_stdvget`, `vfs_stdfhtovp`, `vfs_stdcheckexp`, `vfs_stdnosync`, and `vfs_stdextattrctl` return unsupported.
- `vfs_stdstart`, `vfs_stdsync`, `vfs_stdinit`, and `vfs_stduninit` succeed without action.
- `vfs_stdstatvfs` calls `VFS_STATFS` and converts `statfs` fields to `statvfs`.
- `vfs_stdac_init` enables quota/accounting support through `vq_init` for selected filesystem type names.
- `vfs_stdac_done` calls `vq_done`.
- `vfs_stdncpgen_set` and `vfs_stdncpgen_test` are no-op defaults for mount namecache generation support.
- `vfs_stdmodifying` enforces read-only mount behavior by returning `EROFS`.

Notable dependencies include old and new vnode operation interfaces, namecache APIs from `vfs_cache.c`, vnode locking/refcounting, `componentname`, buffer/bio completion, VM vnode pager, mount flags, journal mountctl, quota accounting, and statfs/statvfs compatibility.

Implementation risks for future changes:
- Compatibility wrappers intentionally lock parent directory vnodes exclusively because older filesystems may store lookup side effects in inode state.
- Old lookup may return parent-directory lock state through `CNP_PDIRUNLOCK`; each wrapper must release exactly according to that flag.
- Namecache updates after old operations are required for correctness. Missing `cache_setvp`, `cache_unlink`, `cache_inval`, or `cache_rename` calls would desynchronize old vnode behavior from the new topology.
- `vop_compat_nrename` is especially sensitive because old rename consumes/release semantics differ for source and target vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_default.c -->