# Chunk Research: sources/os/darwin/xnu/bsd/vfs/vfs_subr.c lines 1-10231

## Scope

This chunk covers the first 10,231 lines of Darwin XNU's `bsd/vfs/vfs_subr.c`, within subset A (`sources/os/darwin/xnu`). It is the first chunk of a larger file; it stops inside `vnode_authorize_callback_int()` immediately after initializing the local authorization context and extracting `cred = ctx->vc_ucred`. Later authorization completion, authattr helpers, triggers, leases, and other tail code are cross-chunk material.

## Purpose

This chunk implements most core VFS/vnode support outside filesystem-specific VNOPs: vnode table initialization, mount/root boot and root switching, mount iteration and reference draining, vnode allocation/reuse/reclaim, device vnode aliasing, name/path helper APIs, VFS sysctl and kqueue events, basic vnode lookup/open/close helpers, object creation, and the first half of vnode authorization.

## APIs and Entry Points

- Initialization and globals: `vntblinit()`, global vnode lists (`vnode_free_list`, `vnode_dead_list`, `vnode_async_work_list`, `vnode_rage_list`), mount list (`mountlist`), vnode counters, telemetry (`freeable_vnodes`), SMR setup, worker-thread startup.
- Write and buffer state: `vnode_waitforwrites()`, `vnode_startwrite()`, `vnode_writedone()`, `vnode_hasdirtyblks()`, `vnode_hascleanblks()`.
- Mount/vnode iteration: `vnode_iterate_setup()`, `vnode_umount_preflight()`, `vnode_iterate_prepare()`, `vnode_iterate_reloadq()`, `vnode_iterate_clear()`, `vnode_iterate()`, plus mount lock/ref helpers (`mount_lock*`, `mount_ref/drop`, `mount_iterref/drop/drain/reset`, `mount_refdrain()`).
- Root and mount lifecycle: `vfs_busy()`, `vfs_unbusy()`, `vfs_rootmountalloc()`, `vfs_mountroot()`, `vfs_switch_root()`, `vfs_mount_recovery()`, `vfs_unmountall()`, shutdown progress timestamp helpers.
- Mount lookup/list APIs: `vfs_getvfs()`, `vfs_getvfs_with_vfsops()`, `vfs_getvfs_by_mntonname()`, `vfs_getnewfsid()`, `vfs_iterate()`, `mount_list_add/remove()`, `mount_lookupby_volfsid()`, `mount_list_lookupby_fsid()`.
- Device vnode support: `bdevvp()`, `checkalias()`, `get_vp_from_dev()`, `check_mountedon()`, `vnode_cmp_chrtoblk()`, `vcount()`, `vfs_mountedon()`, `vfs_setmounting()`, `vfs_setmountedon()`, `vfs_clearmounting()`.
- Vnode lifecycle: `vget_internal()`, `vnode_ref*()`, `vnode_rele*()`, `vflush()`, `vclean()`, `vn_revoke()`, `vnode_recycle()`, `vnode_reload()`, `vnode_reclaim_internal()`, `new_vnode()`, `vnode_get*()`, `vnode_put*()`, `vnode_hold/drop*()`, `vnode_suspend/resume()`, `vnode_drain()`, `vnode_getiocount()`.
- Path/name helpers: `vn_getpath*()`, `vn_getcdhash()`, package extension table APIs (`set_package_extensions_table()`, `is_package_name()`, `vn_path_package_check()`), `vn_searchfs_inappropriate_name()`.
- VFS control/event APIs: `vfs_sysctl_node`, `sysctl_vfs_vfslist()`, `sysctl_vfs_ctlbyfsid()`, `vfs_event_init()`, `vfs_event_signal()`, EVFILT_FS filter callbacks, `vfs_update_vfsstat()`, `sysctl_vfs_noremotehang()`.
- Public vnode convenience APIs: `vnode_lookupat()`, `vnode_lookup()`, `vnode_open()`, `vnode_close()`, `vnode_mtime()`, `vnode_flags()`, `vnode_size()`, `vnode_setsize()`, dirty-bit helpers.
- Creation/auth entry points: `vn_create()`, `vnode_create_ext()`, `vnode_create()`, `vnode_create_empty()`, `vnode_initialize()`, `vnode_addfsref()`, `vnode_removefsref()`, `vnode_link_lock/unlock()`, `vnode_authorize_init()`, `vnode_authorize()`, `vn_authorize_unlink/open/create/rename/mkdir/rmdir()`, `vnode_attr_authorize_dir_clone()`.

## Control Flow

`vntblinit()` initializes all vnode and mount queues, configures reclaim/deallocation policy from boot tunables, optionally enables SMR freeing for the vnode zone, and starts two permanent worker threads: `async_work_continue()` and `vn_laundry_continue()`. Those threads consume async-work/free/rage queues and drive deferred reclaim through `process_vp()`.

Mount iteration moves `mnt_vnodelist` into `mnt_workerqueue` under mount locks, returns each vnode to the main list as it is examined, and tracks newly inserted vnodes in `mnt_newvnodes`. `vnode_iterate()` obtains an iocount with `vget_internal()` before invoking a caller callback, while `vflush()` uses the same queue mechanics to reclaim or forcibly close vnodes during unmount.

Root mounting allocates a provisional root mount for each candidate filesystem type, calls either `vfc_mountroot` or `VFS_MOUNT`, then publishes the mount, initializes I/O attributes, probes root capabilities, starts the filesystem, and optionally labels root under MACF. Failure unwinds via `vfs_rootmountfailed()`.

`vfs_switch_root()` performs a multi-step destructive root pivot: validate incoming root, find destination covered vnodes, collect preserved mounts (`/dev`, Preboot, Recovery, VM, Update, iSCPreboot, Hardware, xarts, FactoryLogs, Diags), take transferred usecounts, rewrite mount coverage and `rootvnode`, purge name caches, optionally reorder `mountlist`, and fix mount names/backing-root flags across all mounts.

Vnode creation flows through `new_vnode()` and `vnode_create_internal()`. `new_vnode()` either allocates a fresh vnode, reuses a dead/free/rage vnode, forces allocation in dependency/deadlock cases, or waits/retries under vnode pressure. `vnode_create_internal()` initializes type, ops, UBC state, trigger/device/FIFO metadata, mount/name-cache membership, rapid-aging flags, secluded-memory eligibility, and special alias substitution for block/char devices.

Reclaim flows converge on `vnode_reclaim_internal()`: mark terminating, clear union wait, optionally revoke ttys, drain outstanding iocounts, revoke leases when enabled, call `vgone()`/`vclean()` for non-`VBAD` vnodes, bump `v_id` under the vnode list lock, verify UBC/name/parent/output cleanup, reset knotes, wake terminators, and put non-reuse vnodes back on an eligible list.

Authorization begins with higher-level operation-specific checks (`vn_authorize_*`) and funnels through `vnode_authorize()` into the registered kauth callback. This chunk covers cache lookup for previously authorized rights, POSIX mode checks, ACL evaluation, delete semantics, immutable flag checks, opaque filesystem delegation, and superuser handling. The main callback implementation continues in the next chunk.

## State and Invariants

- Vnode lifetime is split across holdcount, iocount, usecount, kusecount, writecount, list membership, mount references, and named references (`VNAMED_*`). Many panics enforce counter balance and impossible list states.
- `v_id` is the generation guard for stale references; reclaim increments it while holding `vnode_list_lock` so `vnode_getwithvid()` can reject stale cache/hash references.
- `VL_TERMINATE`, `VL_DRAIN`, `VL_DEAD`, `VL_MARKTERM`, `VL_NEEDINACTIVE`, and `VL_SUSPENDED` drive the vnode state machine. Callers may block, fail, or bypass drains depending on flags such as `VNODE_DRAINO`, `VNODE_ALWAYS`, `VNODE_NOBLOCK`, and `VNODE_NODEAD`.
- Freeable vnode policy is controlled by `vn_dealloc_level`, `numvnodes_min/max`, `reusablevnodes_max`, dead vnode thresholds, and `VCANDEALLOC`; SMR freeing temporarily blocks `vnode_hold_smr()` using `VNODE_HOLD_NO_SMR`.
- Mount lifetime uses both `mnt_count` and `mnt_iterref`; unmount drain sets negative iterref state and mount busy uses shared/exclusive `mnt_rwlock`.
- Device alias state lives in `specinfo`, `speclisth`, `SI_ALIASED`, `SI_MOUNTING`, and `SI_MOUNTEDON`; alias transitions rely on SPECHASH locking plus vnode holds/iocounts outside the hash lock.
- Authorization caches successful rights on vnodes, with named streams sometimes caching on the parent data fork for local-authorization filesystems.

## Dependencies

This code depends heavily on XNU VFS and vnode internals (`mount_internal.h`, `vnode_internal.h`, namei, buf, UBC, VM memory objects, kauth, MACF, kqueue, sysctl, disk ioctls, specfs, fifofs, NFS). It calls filesystem VNOP/VFS methods including `VFS_MOUNT`, `VFS_START`, `VFS_ROOT`, `VFS_GETATTR`, `VNOP_CREATE`, `VNOP_MKNOD`, `VNOP_OPEN`, `VNOP_CLOSE`, `VNOP_FSYNC`, `VNOP_RECLAIM`, `VNOP_INACTIVE`, `VNOP_ACCESS`, `VNOP_IOCTL`, and compound operations. It also uses external helpers such as `namei()`, `vn_open()`, `vn_close()`, `build_path_with_parent()`, `cache_enter_create()`, `cache_purgevfs()`, `ubc_*`, `memory_object_*`, `kauth_acl_*`, `mac_vnode_*`, `dounmount()`, `safedounmount()`, and `kernel_mount()`.

## Risks and Edge Cases

- Lock ordering is critical: mount iterate mutex before mount lock, vnode lock versus vnode list lock, SPECHASH lock dropped before vnode iocount acquisition, and root switch holding `rootvnode_rw_lock` while rewriting mount topology.
- Forced unmount/reclaim paths can block indefinitely on leaked iocounts unless `bootarg_no_vnode_drain` enables timeout behavior; shutdown has a special iocount reset escape when no output is pending.
- `vnode_create_internal()` notes a real race for reused `bdevvp` alias vnodes where unlocked flag manipulation can lose `VTHROTTLED`; the code compensates with an unconditional wakeup and reasserts selected flags under lock.
- `vfs_switch_root()` intentionally reaches a point of no return after validation; failures after destructive mount rewrites would be hard to recover.
- Sysctl compatibility code explicitly blocks unsafe old-style filesystem selectors because some filesystems treat user pointers as `struct sysctl_req` and may call through arbitrary function pointers.
- Authorization correctness depends on subtle ACL/POSIX precedence, sticky bit handling, immutable flag exceptions, owner/group membership uncertainty, and rights-cache invalidation by setattr/xattr paths outside this chunk.
- `vn_path_package_check()` temporarily writes NUL terminators into the supplied path buffer while scanning components, so callers must pass mutable path storage.
- Vnode pressure handling can force allocation, trigger jetsam on configured platforms, or panic when no recovery path exists.

## Cross-Chunk References

- `vnode_authattr_new_internal()` is declared and called by `vn_attribute_prepare()` but its implementation is after this chunk.
- `vnode_authorize_callback_int()` begins at the chunk boundary and continues after line 10231; this chunk does not include the full action-to-rights mapping, attribute fetches, final cache decisions, or error propagation.
- Trigger resolver functions are declared and partially referenced during create/reclaim (`vnode_resolver_create()`, `vnode_resolver_detach()`), but their implementations are later.
- Lease cleanup is referenced under `CONFIG_FILE_LEASES` (`vnode_revokelease()`), but lease allocation/breaking logic is in a later chunk.
- Later helpers referenced here include union-wait functions, filesystem type-name setters/getters, AppleDouble orphan cleanup, panic vnode tracing, path tracing, and read-ahead advice.

## Research Notes

The assigned line range was read completely. No final per-file report was created for this chunked file.