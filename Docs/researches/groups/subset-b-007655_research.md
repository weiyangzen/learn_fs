# Research Group: subset-b-007655

This grouped report covers Lustre llite file-operation, CL-object, glimpse, and foreign-symlink handling assigned to `subset-b-007655`. Each section preserves its source path for reconciliation into the final source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/file.c -->
# sources/distributed-fs/lustre-release/lustre/llite/file.c

## Purpose

`file.c` is the main Lustre llite VFS file-operation bridge. It connects Linux `struct file_operations` and `struct inode_operations` to Lustre metadata RPCs, CLIO data I/O, layout-lock management, HSM/PCC/FLR features, distributed flocking, group locks, FIEMAP, fallocate, project quota flags, and attribute refresh.

The file is also the coordination point for per-open client state. `struct ll_file_data` instances stored in `file->private_data` track open mode, cached MDS open handles, lease handles, group locks, readahead state, PCC state, designated FLR mirror, write-failure reporting, and lock-no-expand behavior.

## Important APIs, Types, And Functions

- `ll_file_open()` / `ll_file_release()`: VFS open and close handlers. They allocate/free `ll_file_data`, reuse or acquire MDS open handles, authorize statahead for directories, initialize encryption/PCC state, track open frequency, and close handles with `md_close`.
- `ll_prepare_close()` / `ll_close_inode_openhandle()` / `ll_md_close()` / `ll_md_real_close()`: close packing and open-handle lifecycle. Close can carry ordinary attributes or close-intent biases for layout split/merge/swap, HSM release, resync completion, and PCC attach.
- `ll_dom_finish_open()` and `ll_dir_finish_open()`: populate page or directory caches from inline data returned by open/read-on-open replies.
- `ll_merge_attr()` / `ll_merge_attr_try()` / `ll_merge_attr_nolock()`: merge MDT inode timestamps with OST object attributes, including encrypted-file lazy cleartext-size handling.
- `ll_io_init()` and `ll_file_io_generic()`: initialize and execute CLIO read/write operations, including direct I/O, parallel DIO, AIO, append, FLR mirror selection, range locks, no-lock mode, retry, and partial-I/O splitting.
- `ll_do_fast_read()` and `ll_do_tiny_write()`: fast paths that use existing page-cache state for small reads or already-dirty single-page writes.
- `ll_file_read_iter()` / `ll_file_write_iter()`: VFS iter I/O entry points, with PCC interception, hybrid buffered-to-DIO switching, unaligned-DIO segment looping, stats, and heat tracking.
- `ll_lov_setstripe_ea_info()`, `ll_lov_getstripe_ea_info()`, `ll_lov_setstripe()`, `ll_file_getstripe()`: set/get LOV layout and stripe extended attributes, including composite, DoM, foreign, encrypted, and erasure-coding checks.
- `ll_get_grouplock()` / `ll_put_grouplock()`: user-visible group-lock ioctls, layered over `cl_get_grouplock()` and serialized by inode group state.
- `ll_lease_open()`, `ll_file_set_lease()`, `ll_file_unlock_lease()`, `ll_lease_close_intent()`: lease acquisition/release and lease-backed layout/HSM/PCC operations.
- `ll_data_version()` / `ll_ioc_data_version()`: CLIO data-version queries used by userspace ioctls, HSM release, migration, layout swap, and resync.
- `ll_hsm_release()`, `ll_hsm_state_set()`, `ll_hsm_import()`, `ll_layout_restore()`: HSM release/import/state/restore handling.
- `ll_file_ioctl()`: large ioctl dispatcher for flags, stripe/layout, group locks, data versions, HSM, leases, ladvise, heat, PCC, project quota, and fallback OBD ioctls.
- `ll_file_flock()`: distributed POSIX/flock lock path via MDT LDLM flock enqueues, including asynchronous lock-manager callbacks.
- `ll_getattr_dentry()` / `ll_getattr()` / `ll_inode_permission()`: stat and permission hooks with statahead, revalidation, glimpse, striped-directory attr merging, foreign-symlink stat mode, root squash, and 32-bit inode encoding.
- `ll_layout_refresh()`, `ll_layout_conf()`, `ll_layout_lock_set()`, `ll_layout_intent()`, `ll_layout_write_intent()`: layout-lock fetch, application, generation tracking, retry, and write-intent signaling.

Key local helper structs include `split_param`, `pcc_param`, `swap_layouts_param`, and `ll_swap_stack`, all used to marshal biased close or layout-swap arguments.

## Control Flow

Open starts with intent state left by lookup/atomic-open when available. If no valid open intent is present, `ll_file_open()` synthesizes one from kernel flags, requests open-by-FID, optionally asks for an open lock when open-cache thresholds are exceeded, and retries after `ll_intent_file_open()` returns an MDS open result. Per-inode read/write/exec open handles are cached under `lli_och_mutex`; additional opens increment the matching usecount and get local `ll_file_data` without another close RPC. On errors, intent references and open handles are released carefully because close errors are rarely retried by applications.

Close reverses that state. `ll_file_release()` cleans up directory statahead, HSM copytool registration, PCC state, async write errors, and then calls `ll_md_close()`. `ll_md_close()` releases group locks and leases, consumes file-owned handles, decrements cached open-handle usecounts, and skips an MDS close only when a compatible cached OPEN lock remains. All close-intent variants eventually flow through `ll_close_inode_openhandle()`, which packs inode attributes, lazy size/block validity, data-modified HSM hints, lease handles, data versions, secondary FIDs, and operation-specific payloads before `md_close()`.

Read and write operations first offer the request to PCC. Reads then try fast page-cache reads before allocating a CL environment. Writes may switch to direct I/O by policy and may satisfy small dirty single-page writes through `ll_do_tiny_write()`. The generic CLIO loop initializes `CIT_READ` or `CIT_WRITE`, takes range locks for writes and direct reads unless a group lock is held, submits `cl_io_loop()`, waits/recycles synchronous DIO anchors, records bytes, handles partial I/O, and restarts for layout, mirror, or lock changes up to `RETRY_ATTEMPTS`.

Metadata operations are split between MDT and OST/CL layers. `ll_inode_revalidate()` fetches current metadata through an intent lock. `ll_getattr_dentry()` decides whether a glimpse is needed for size/blocks/mtime, lets PCC answer cached attrs, skips glimpse when MDT attributes are known authoritative, and otherwise calls `ll_glimpse_size()`. Non-regular and striped-directory attributes are merged by MDT directory stripe helpers.

Layout operations use LDLM layout locks. `ll_layout_refresh()` first checks cached layout generation, then under `lli_layout_mutex` either matches a local layout lock or sends an `IT_LAYOUT` intent. `ll_layout_lock_set()` fetches the layout LVB if absent, calls `ll_layout_conf()` to apply it to the CL object, waits/prunes on `-EBUSY`, and updates the inode layout generation when successful.

The ioctl dispatcher validates userspace buffers and privilege rules, then fans out to layout, lease, HSM, heat, PCC, project, flock, data-version, and fallback OBD control paths. Several ioctls intentionally reuse close-intent or lease paths so that metadata-server state transitions happen atomically with open-handle closure.

## State And Persistence Behavior

Most state is in memory: cached MDS open handles in `ll_inode_info`, per-file `ll_file_data`, CL object/layout state, LDLM locks, PCC attachment state, range-lock trees, heat counters, async write errors, and inode timestamps/blocks/size. Close RPCs persist file attributes, layout/HSM/PCC transitions, and data-modified flags back to the MDT. OST object state is changed through CLIO setattr/fallocate/fsync/data-version operations.

File size and block counts are deliberately lazy in several paths. `ll_prepare_close()` sends `OP_XVALID_LAZYSIZE`/`OP_XVALID_LAZYBLOCKS` when size/blocks are not authoritative. Encrypted files without keys report rounded sizes to userspace while preserving cleartext size in `lli_lazysize` for close. `AT_STATX_DONT_SYNC` can return lazy size/block fields without glimpse.

Layout state is persistent on the server but cached in the client via layout locks and CL object config. The client records `ll_layout_version` and refreshes it under layout-lock control. HSM state, archive IDs, data versions, and release/restore/import operations are persisted through MDT ioctls and biased close requests. Sessionless per-open flags such as no-lock, group-lock-held, lock-no-expand, and designated mirror are not persistent.

## Dependencies And Integration Points

`file.c` depends on llite internals, VVP/CLIO (`cl_io`, `cl_object`, `cl_lock`, `cl_page`), MDC/MDT metadata RPC helpers, LOV/LMV layout formats, LDLM locking, Linux VFS file/inode/stat/file-lock APIs, page cache helpers, encryption helpers, PCC hooks, HSM ioctl structures, Lustre OBD ioctl plumbing, and lprocfs stats.

Important cross-file integration includes `glimpse.c` for `ll_glimpse_size()` behavior, `lcommon_cl.c` for CL object initialization and OST setattr, `lcommon_misc.c` for group lock and OSC connect-flag update helpers, `llite_foreign.c`/`llite_foreign_symlink.c` for foreign fake symlink getattr mode and open/removal policy, and broader llite modules for directory, xattr, ACL, mmap, statahead, PCC, HSM, and layout callbacks.

## Risks And Edge Cases

- Open-handle caching is concurrency-sensitive. `lli_och_mutex`, per-mode usecounts, lease stealing, and error cleanup need to remain balanced or handles can leak, double-close, or skip required MDT close.
- Close errors are hard to recover from because VFS callers rarely retry `close()`. The implementation prioritizes local cleanup even when the close RPC fails.
- The generic I/O loop has many restart conditions: layout changes, FLR mirror retries, partial buffered I/O chunking, DIO/AIO completion, and append size refresh. Iterator state and range-lock release are high-risk areas.
- Hybrid I/O mutates `ki_flags` to direct I/O for large buffered requests. Pipe iterators, PCC attach, unaligned DIO, and older-server compatibility all have special handling.
- Attribute reporting is intentionally not strict POSIX atime behavior; Lustre avoids MDT RPCs on every read.
- Encrypted files without keys require rounded visible sizes and special close/getattr/seek/fiemap behavior.
- Foreign fake symlinks are regular files or directories presented as symlinks; callers must pass the `foreign` flag to `ll_getattr_dentry()` to avoid normal size/layout validation and to expose `S_IFLNK`.
- Several ioctl paths trust complex userspace structures after manual size checks. `LL_IOC_LADVISE`, lease unlock payloads, and FID2PATH variable buffers deserve fuzz coverage.
- Distributed flocking mixes kernel local locks and MDT LDLM locks. Async `lm_grant` callbacks, cancel races, and lockd owner comparison workarounds are subtle.
- Layout lock application can fail with `-EBUSY` while I/O is using the object; the prune/retry path must avoid stale layouts and deadlocks.

## Test Signals

Useful tests include open-cache reuse and close under read/write/exec modes; open-by-FID stale dentry retry; close-intent paths for HSM release, PCC attach, layout split/merge/swap, and resync done; encrypted open/getattr/close/seek behavior with and without keys; DoM read-on-open cache population; directory read-on-open cache population; fast-read fallback; tiny-write fallback; hybrid I/O switching thresholds; direct and unaligned vectored I/O; AIO/parallel-DIO completion; group-lock serialization and nonblocking behavior; lease set/get/unlock and broken-lease return modes; ladvise lockahead result mapping; stripe set/get including composite/DoM/foreign/EC layouts; FID2PATH for OST and encrypted names; fsync/flush async error propagation; flock sync/async/cancel paths; root-squash permission behavior; fallocate error mapping; layout refresh under revoked/blocked layout locks; and statx with `AT_STATX_DONT_SYNC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/foreign_symlink.h -->
# sources/distributed-fs/lustre-release/lustre/llite/foreign_symlink.h

## Purpose

`foreign_symlink.h` is the public llite declaration point for foreign fake-symlink support. It exposes sysfs attribute handlers that configure the feature and the inode-operation tables used when a Lustre foreign regular file or directory is presented to the Linux VFS as a symlink.

## Important APIs, Types, And Functions

- `foreign_symlink_enable_show()` / `foreign_symlink_enable_store()`: sysfs show/store for enabling fake-symlink interpretation on a mount.
- `foreign_symlink_prefix_show()` / `foreign_symlink_prefix_store()`: sysfs show/store for the absolute local prefix prepended to parsed foreign LOV/LMV values.
- `foreign_symlink_upcall_show()` / `foreign_symlink_upcall_store()`: sysfs show/store for the userspace upcall executable that provides parsing format information.
- `foreign_symlink_upcall_info_store()`: sysfs binary-format store used by the upcall to install parsed constant-string and substring descriptors.
- `ll_foreign_file_symlink_inode_operations`: inode operations for regular foreign files faked as symlinks.
- `ll_foreign_dir_symlink_inode_operations`: inode operations for foreign directories faked as symlinks.

## Control Flow

Other llite files include this header when they need to reference foreign-symlink sysfs handlers or swap an inode's `i_op` table. `llite_foreign.c` selects these operation tables when metadata/layout state identifies a foreign object of `LU_FOREIGN_TYPE_SYMLINK`. `llite_foreign_symlink.c` implements the declarations and uses the sysfs handlers to update fields in `struct ll_sb_info`.

## State And Persistence Behavior

The header declares no state. Runtime state lives in `ll_sb_info`: feature bits, prefix string and length, upcall path, parsed upcall item array, item count, mount namespace pointer, and the read/write semaphore protecting those fields. The configuration is mount-local and not persisted by this header.

## Dependencies And Integration Points

The prototypes depend on kernel `kobject`, `attribute`, `inode_operations`, and sysfs-style show/store conventions. The operation tables integrate with VFS symlink traversal through `.get_link`, stat through `.getattr`, permission checks, xattr listing, and directory lookup rejection for fake directory symlinks.

## Risks And Edge Cases

The header itself is low risk, but it exports a contract where sysfs stores must be mount-namespace aware and operation tables must be safe for inodes whose underlying mode is not `S_IFLNK`. Any signature drift with kernel `inode_operations` or sysfs handlers will break compile compatibility.

## Test Signals

Compile coverage should include builds with the current kernel `getattr`/`get_link` signatures. Integration tests should verify that enabling the feature causes `llite_foreign.c` to install the exported operation tables and that the sysfs attributes invoke the declared handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/foreign_symlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/glimpse.c -->
# sources/distributed-fs/lustre-release/lustre/llite/glimpse.c

## Purpose

`glimpse.c` implements llite/VVP glimpse-size support. A glimpse asks the Lustre lock and object layers for current file size, block count, and timestamps without revoking conflicting client locks. It is used by getattr, seek, fiemap, and other paths that need fresh file-size information from OST-side object state.

## Important APIs, Types, And Functions

- `dirty_cnt(struct inode *inode)`: returns a binary indication that the inode may have dirty page-cache or mmap state. It checks the mapping dirty tag and VVP mmap count.
- `cl_glimpse_lock(const struct lu_env *env, struct cl_io *io, struct inode *inode, struct cl_object *clob, int agl)`: requests a whole-file CL read lock with `CEF_GLIMPSE | CEF_MUST`; optional AGL mode adds speculative nonblocking flags.
- `cl_io_get(struct inode *inode, struct lu_env **envout, struct cl_io **ioout, u16 *refcheck)`: obtains a CL environment and `cl_io` for regular-file special operations.
- `__cl_glimpse_size(struct inode *inode, int agl)`: initializes a `CIT_GLIMPSE` CLIO, requests the glimpse lock, merges attributes for normal glimpses, and retries when FLR mirror state asks for restart.

The static `whole_file` descriptor represents a read lock over `[0, CL_PAGE_EOF]`.

## Control Flow

Callers enter through `__cl_glimpse_size()`. Non-regular inodes return `0` from `cl_io_get()` and are skipped. Regular files allocate a thread CL environment, set `ci_ndelay` and `ci_verify_layout`, and initialize a `CIT_GLIMPSE` I/O. If initialization says there is no work, the stored `ci_result` is returned. Otherwise `cl_glimpse_lock()` submits a whole-file glimpse lock request.

For normal, non-AGL glimpses, a successful request is followed by `ll_merge_attr()` so inode size, blocks, and timestamps reflect OST attributes. If the file has positive size but zero blocks, `dirty_cnt()` supplies a minimal block count so userspace tools do not treat a dirty or mmaped file as fully sparse. The CL lock is released and the CLIO finalized each iteration. `-EAGAIN` from a non-AGL FLR path can set `ci_need_restart` until all needed mirrors are tried.

## State And Persistence Behavior

No persistent state is written. The code updates in-memory inode attributes through `ll_merge_attr()` and may set `inode->i_blocks` to `1` when dirty/mmaped state indicates unwritten local data. It consumes transient CL environment, CLIO, and CL lock objects and releases them before returning.

## Dependencies And Integration Points

The file depends on LDLM/CLIO/VVP infrastructure, Linux page-cache dirty tags, and llite inode/object helpers. It integrates with `file.c` through `ll_merge_attr()` and the public glimpse wrapper used by getattr, seek, and fiemap paths. It relies on OSC behavior for `CEF_GLIMPSE`: conflicting locks trigger glimpse callbacks rather than ordinary lock revocation, and valid attributes can be returned even when the actual lock enqueue fails with `-ENAVAIL`.

## Risks And Edge Cases

- `dirty_cnt()` intentionally returns only 0 or 1, not a full dirty-page count. It is a sparse-file correctness hint, not an accurate block estimate.
- AGL mode is speculative and nonblocking, so callers must tolerate incomplete/non-authoritative refresh.
- Retry behavior depends on FLR mirror state in `cl_io`; missing retry limits in callers would risk loops, though the code tracks tried mirrors.
- The page-cache dirty lookup uses mapping internals and should be checked against kernel API changes.
- `ll_merge_attr()` can fail independently of the glimpse lock, so stat/seek callers need to propagate or tolerate those errors.

## Test Signals

Tests should cover regular versus non-regular input, normal glimpse with dirty pages and with mmap count, zero-size and positive-size sparse files, AGL nonblocking behavior, layout-change/FLR retry on `-EAGAIN`, failure injection around `OBD_FAIL_GLIMPSE_DELAY`, and attribute merge errors. Stat and seek integration tests should verify that freshly written remote sizes become visible after glimpse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/glimpse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/lcommon_cl.c -->
# sources/distributed-fs/lustre-release/lustre/llite/lcommon_cl.c

## Purpose

`lcommon_cl.c` contains common llite client-layer object helpers: propagating setattr operations to OST/CL objects, creating or updating CL objects when inode metadata arrives, safely tearing down CL objects during inode eviction, and deriving stable inode number/generation values from Lustre FIDs.

## Important APIs, Types, And Functions

- `cl_setattr_ost(struct inode *inode, const struct iattr *attr, enum op_xvalid xvalid, unsigned int attr_flags)`: sends CL setattr operations to OST-side objects, including truncate/fallocate-style metadata, flags, owner/group/project identity, and designated mirror from `ATTR_FILE`.
- `cl_file_inode_init(struct inode *inode, struct lustre_md *md)`: creates a new `cl_object` for a regular inode when metadata includes a valid FID, or updates an existing object's layout configuration.
- `cl_inode_fini(struct inode *inode)`: kills and drops the inode's CL object during eviction, using an emergency environment under memory pressure.
- `cl_fid_build_ino(const struct lu_fid *fid, int api32)`: maps a FID to a 32-bit or 64-bit inode number depending on platform/API constraints.
- `cl_fid_build_gen(const struct lu_fid *fid)`: derives inode generation, using IGIF generation when applicable and high flattened-FID bits otherwise.
- `cl_object_put_last()`: private helper that waits until only the inode-owned CL object reference remains before dropping it.
- `cl_inode_fini_env`, `cl_inode_fini_refcheck`, and `cl_inode_fini_guard`: emergency CL environment and serialization for eviction under allocation failure.

## Control Flow

`cl_file_inode_init()` is called when llite has new metadata. It ignores non-regular files and metadata without `OBD_MD_FLID`. For new inodes with no `lli_clob`, it requires the inode to still have `I_NEW`, marks the object config as `LOC_F_NEW`, and calls `cl_object_find()` directly against the top client device. Existing `lli_clob` objects receive `cl_conf_set()` with the new layout; `-EBUSY` is ignored because later I/O will handle layout reconfiguration.

`cl_setattr_ost()` obtains a CL environment, fills `io->u.ci_setattr` with times, size, valid flags, xvalid flags, parent FID, and truncate credentials when `ATTR_SIZE` is present. If a file is supplied, `ll_io_set_mirror()` and the VVP file descriptor are installed so ftruncate honors group locks and mirror selection. The `CIT_SETATTR` CLIO runs and restarts while `ci_need_restart` is set.

`cl_inode_fini()` is called after the inode cache is evicting its slave CL object. It tries to allocate a normal CL environment, but if that fails it locks `cl_inode_fini_guard` and uses the preallocated emergency environment. It kills the object, waits in `cl_object_put_last()` for external references to drain, drops the final reference, clears `lli_clob`, and releases the chosen environment.

## State And Persistence Behavior

The file manages in-memory CL object lifetime and layout configuration. `cl_setattr_ost()` causes persistent OST-side changes through the CL stack when it truncates or updates object attributes/flags. `cl_file_inode_init()` stores the CL object pointer in `ll_inode_info::lli_clob`; `cl_inode_fini()` clears it. FID-to-inode-number helpers are deterministic mappings and do not mutate state.

## Dependencies And Integration Points

This file depends on CL object/site/device APIs, VVP environment helpers, llite inode metadata, Lustre FID helpers, Linux inode state, and quota/user namespace conversion helpers. It is used by `file.c` for truncate, fallocate, encrypted flag propagation, project/ext flags, and CL object teardown. It integrates with layout configuration through `cl_conf_set()` and object creation through `cl_object_find()`.

## Risks And Edge Cases

- `cl_file_inode_init()` treats a non-new inode without `lli_clob` as `-EIO`; callers must only create CL objects during safe inode initialization.
- Ignoring `-EBUSY` from layout config relies on later I/O handling stale or contested layout state.
- `cl_object_put_last()` waits for references to drop; a leaked reference or blocked AST path can hang inode eviction.
- Emergency environment use is serialized and assumes `cl_inode_fini_env` has been initialized elsewhere.
- `cl_setattr_ost()` restarts while `ci_need_restart` is set and must keep file/mirror/group-lock context consistent across retries.
- FID flattening to 32-bit inode numbers can collide by design; generation handling is the mitigation.

## Test Signals

Tests should exercise new regular inode CL object creation, existing layout update including `-EBUSY`, non-regular/no-FID no-op behavior, unexpected non-new inode failure, truncate setattr with UID/GID/project propagation, file-backed ftruncate honoring group locks/designated mirrors, restart after layout change, inode eviction under normal and emergency environment paths, and 32-bit inode/generation mapping for IGIF and non-IGIF FIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/lcommon_cl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/lcommon_misc.c -->
# sources/distributed-fs/lustre-release/lustre/llite/lcommon_misc.c

## Purpose

`lcommon_misc.c` provides common llite/VVP support that does not belong to a specific VFS operation: updating client connect capability state when OSC imports change, initializing MDS layout EA reply sizes from data-target capabilities, and acquiring/releasing whole-file CL group locks.

## Important APIs, Types, And Functions

- `cl_init_ea_size(struct obd_export *md_exp, struct obd_export *dt_exp)`: private helper that queries the data export for maximum and default LOV EA sizes and calls `md_init_ea_size()` on the metadata export.
- `cl_ocd_update(struct obd_device *host, struct obd_device *watched, enum obd_notify_event ev, void *owner)`: OBD notification callback that intersects llite connect flags with OSC import flags and refreshes EA sizing.
- `cl_get_grouplock(struct cl_object *obj, unsigned long gid, int nonblock, struct ll_grouplock *lg)`: creates a `CIT_MISC` CLIO and requests a whole-file `CLM_GROUP` lock with the provided group id.
- `cl_put_grouplock(struct ll_grouplock *lg)`: releases the CL lock, finalizes the CLIO, and drops the CL environment captured by `cl_get_grouplock()`.

## Control Flow

`cl_ocd_update()` is invoked from the OBD observer notification chain. It accepts only set-up, non-stopping OSC devices. For valid OSC updates, it reads the import's negotiated `ocd_connect_flags`, locks `lustre_client_ocd`, intersects the current llite flags with the OSC flags, and refreshes MDS EA buffer sizing if a data export is present. Unexpected notifications are logged and rejected with `-EINVAL`.

`cl_get_grouplock()` obtains a CL environment, creates a VVP CLIO for `CIT_MISC`, and initializes a whole-file lock descriptor spanning `[0, CL_PAGE_EOF]` with mode `CLM_GROUP` and `cld_gid = gid`. It requests the lock with `CEF_MUST` plus optional `CEF_NONBLOCK`. On success, ownership of the CL environment, CLIO, lock, and gid is transferred into `struct ll_grouplock`; on failure everything allocated in the function is released.

`cl_put_grouplock()` assumes a populated `ll_grouplock`, releases the CL lock, finalizes the CLIO, and returns the CL environment.

## State And Persistence Behavior

`cl_ocd_update()` mutates in-memory client capability state and MDS EA-size configuration. It does not persist data itself, but the updated EA sizes affect subsequent MDS RPC buffer sizing. Group locks are distributed runtime locks held in LDLM/CL state; `ll_grouplock` stores the live handles needed for later release.

## Dependencies And Integration Points

The notification path depends on OBD devices/imports, OSC type names, connect flags from `lustre_idl.h`, `lustre_client_ocd`, and metadata/data exports. The group-lock path depends on CLIO, VVP environment helpers, whole-file CL lock descriptors, and the `ll_grouplock` structure used by `file.c` ioctl handlers.

## Risks And Edge Cases

- `cl_ocd_update()` intersects flags (`lco_flags &= flags`), so once a capability is cleared it will not be re-added through this path without broader reinitialization.
- Unexpected OBD notifications are hard failures and noisy; callers must register the callback only for appropriate OSC imports.
- `cl_get_grouplock()` maps positive `cl_io_init()` results to `-EOPNOTSUPP`, meaning released/unavailable layouts cannot hold a group lock.
- Group lock lifetime spans a CL environment. Every successful `cl_get_grouplock()` must be paired with exactly one `cl_put_grouplock()`.
- Nonblocking group locks can fail both on local inode serialization and remote CL lock acquisition; callers need to map `-EAGAIN` appropriately.

## Test Signals

Tests should cover OSC connect-flag changes, EA-size query failures, notification rejection for wrong type/stopping devices, group-lock success, nonblocking conflict failure, released-layout `-EOPNOTSUPP`, remote lock request errors, and double-release/leak detection through `LL_IOC_GROUP_LOCK` and `LL_IOC_GROUP_UNLOCK` integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/lcommon_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_foreign.c -->
# sources/distributed-fs/lustre-release/lustre/llite/llite_foreign.c

## Purpose

`llite_foreign.c` applies llite policy for Lustre foreign files and directories. A foreign LOV/LMV layout describes an object whose payload semantics are owned outside normal Lustre data layout. This file currently recognizes `LU_FOREIGN_TYPE_SYMLINK` and makes such regular files or directories behave like symlinks from the VFS perspective, while also protecting those external references from accidental removal.

## Important APIs, Types, And Functions

- `ll_manage_foreign(struct inode *inode, struct lustre_md *lmd)`: entry point that inspects file LOV or directory LMV metadata and installs fake-symlink inode operations for supported foreign types.
- `ll_foreign_is_openable(struct dentry *dentry, unsigned int flags)`: tells atomic-open logic whether a fake symlink should be opened or should instead drive VFS symlink following.
- `ll_foreign_is_removable(struct dentry *dentry, bool unset)`: checks whether a foreign file/directory may be removed, with an `unset` mode that marks the inode as explicitly removable.
- `ll_manage_foreign_file()` / `ll_manage_foreign_dir()`: private helpers that switch `inode->i_op` to foreign symlink operation tables.
- `should_preserve_foreign_file()` / `should_preserve_foreign_dir()`: policy helpers for protecting fake symlinks unless `LLIF_FOREIGN_REMOVABLE` has been set.

## Control Flow

`ll_manage_foreign()` is called after metadata/layout information is available. For regular files it first checks `lmd->layout`; if a layout buffer is present and has `LOV_MAGIC_FOREIGN`, it applies file policy immediately. If metadata did not carry the layout but a CL object exists, it performs a small `cl_object_layout_get()` into a `lov_foreign_md` header-sized buffer; `-ERANGE` is accepted because the magic/type header is enough for policy. For directories it checks the supplied `lmd->lsm_obj`, then falls back to `lli_lsm_obj` under `lli_lsm_sem`.

When a foreign type is `LU_FOREIGN_TYPE_SYMLINK`, the file helper assigns `ll_foreign_file_symlink_inode_operations` and clears `IOP_NOFOLLOW`; the directory helper assigns `ll_foreign_dir_symlink_inode_operations`. Other foreign types are logged and left unchanged.

`ll_foreign_is_openable()` prevents fake symlinks from being opened when the VFS should follow them, unless `O_NOFOLLOW` was requested. `ll_foreign_is_removable()` repeats the foreign layout lookup and returns false when policy says the fake symlink should be preserved. With `unset=true`, it sets `LLIF_FOREIGN_REMOVABLE` for supported symlink types so a later removal can proceed.

## State And Persistence Behavior

The file mutates only in-memory inode state: `inode->i_op`, `inode->i_opflags`, and `LLIF_FOREIGN_REMOVABLE` in `ll_inode_info`. It reads persistent LOV/LMV foreign metadata from MDT/CL layout state, but it does not change the foreign layout itself. Removal permission is a client-side policy gate; actual unlink/rmdir persistence occurs in the calling metadata operation.

## Dependencies And Integration Points

This file depends on `llite_internal.h`, LOV foreign metadata (`lov_foreign_md`), LMV foreign metadata (`lmv_foreign_md` / `lmv_stripe_object`), CL layout queries, `ll_foreign_file_symlink_inode_operations`, and `ll_foreign_dir_symlink_inode_operations` implemented in `llite_foreign_symlink.c`. It integrates with open, lookup, getattr, unlink, and rmdir paths in other llite code.

## Risks And Edge Cases

- Header-only CL layout reads intentionally tolerate `-ERANGE`; this relies on the foreign magic/type fields fitting in the small local struct.
- Endianness handling differs: file type uses `le32_to_cpu()` in logging and type checks in some places, while directory metadata is compared directly in several branches. Tests should confirm actual LMV layout byte order.
- Fake symlink behavior changes `i_op` on an inode whose mode may still be regular or directory. All VFS paths must be aware of `d_is_symlink()` versus `S_ISLNK()`.
- Cached inodes may not reflect feature enable/disable until revalidation, as noted in the implementation comments.
- If no CL object or LMV object is cached, removal policy logs uncertainty and allows removal.
- `unset=true` both reports preservation and marks the inode removable; callers must use the flag only for deliberate administrative removal.

## Test Signals

Tests should cover regular foreign symlink management from metadata-carried layout and from CL layout lookup, foreign directory symlink management from supplied and cached LMV, non-symlink foreign types, open without `O_NOFOLLOW` returning not-openable, open with `O_NOFOLLOW`, removal prevention, `unset=true` followed by allowed removal, missing CL/LMV cache behavior, and cached-inode behavior across feature toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_foreign.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_foreign_symlink.c -->
# sources/distributed-fs/lustre-release/lustre/llite/llite_foreign_symlink.c

## Purpose

`llite_foreign_symlink.c` implements the fake-symlink behavior declared in `foreign_symlink.h`. It turns foreign LOV/LMV metadata into a VFS symlink target by prefixing a mount-local absolute path and parsing the foreign free-form value either directly or through a userspace-provided format. It also exposes sysfs configuration for enabling the feature, setting the prefix, registering an upcall, and accepting the upcall's parse descriptors.

## Important APIs, Types, And Functions

- `foreign_symlink_alloc_and_copy_prefix()`: allocates a destination path buffer and writes `/<prefix>/`, returning the suffix insertion offset.
- `ll_foreign_symlink_default_parse()`: uses the whole foreign `lfm_value` as the relative suffix.
- `ll_foreign_symlink_upcall_parse()`: builds the suffix from configured `STRING_TYPE` constants and `POSLEN_TYPE` substrings of `lfm_value`.
- `ll_foreign_symlink_parse()`: selects default or upcall parse based on `LL_SBI_FOREIGN_SYMLINK_UPCALL`.
- `ll_foreign_readlink_internal()`: loads full foreign LOV/LMV metadata from regular-file CL layout or directory LMV cache and returns the parsed symlink target.
- `ll_foreign_get_link()` / `ll_foreign_put_link()`: VFS `.get_link` implementation and delayed cleanup.
- `ll_foreign_dir_lookup()`: rejects lookup inside fake directory symlinks with `-ENODATA`.
- `foreign_symlink_enable_show/store()`, `foreign_symlink_prefix_show/store()`, `foreign_symlink_upcall_show/store()`, `foreign_symlink_upcall_info_store()`: sysfs control surface.
- `ll_foreign_file_symlink_inode_operations` and `ll_foreign_dir_symlink_inode_operations`: operation tables installed by `llite_foreign.c`.
- `ll_foreign_symlink_getattr()`: calls `ll_getattr_dentry(..., foreign=true)` so fake symlinks stat as symlinks.

## Control Flow

For symlink traversal, VFS calls `ll_foreign_get_link()`. It rejects RCU-walk style calls with `-ECHILD`, then calls `ll_foreign_readlink_internal()`. Regular files fetch the layout size with `cl_object_layout_get()` using a zero-length buffer, allocate the returned size, and fetch the full LOV foreign metadata. Directories take a reference on cached `lli_lsm_obj` and treat its `lso_lfm` as a `lov_foreign_md` because the foreign LOV and LMV formats are intentionally compatible for this use.

Parsing then depends on mount configuration. Without an upcall descriptor, `ll_foreign_symlink_default_parse()` copies the foreign value after the configured prefix. With an installed descriptor array, `ll_foreign_symlink_upcall_parse()` first computes the output suffix size from all items, allocates the prefixed path, then appends either constant strings or substrings from the foreign value. Bounds checks ensure substring positions fit in `lfm_length`. The generated path is returned to VFS and freed through a delayed call.

Sysfs writes are mount-namespace gated by `has_same_mount_namespace()`. Enabling toggles `LL_SBI_FOREIGN_SYMLINK`. Prefix writes require an absolute path, allocate a replacement string, and swap it under `ll_foreign_symlink_sem`. Upcall writes accept an absolute executable or `"none"`, replace the upcall path, clear the upcall-active bit, and invoke the helper with the mount kobject name. The helper is expected to write binary parse info back to `foreign_symlink_upcall_info_store()`, which validates item alignment, count, string sizes, explicit end marker, allocates a new item array, swaps it under the semaphore, and frees the previous descriptor set.

## State And Persistence Behavior

All configuration state is per-mounted-client in `ll_sb_info`: feature bits, prefix path and size, upcall path, descriptor array, descriptor count, mount namespace, and `ll_foreign_symlink_sem`. The code allocates symlink target buffers per lookup and frees them with `OBD_FREE_LARGE`. Regular-file foreign metadata buffers are allocated per readlink and freed after parsing; directory metadata uses a referenced cached LMV object. No on-disk metadata is modified.

## Dependencies And Integration Points

The file depends on Linux VFS symlink/getattr/inode-operation APIs, sysfs kobject show/store conventions, usermode helper execution, Lustre allocation macros, CL layout retrieval, LMV stripe-object references, `ll_getattr_dentry()` from `file.c`, and foreign parsing structs/macros such as `ll_foreign_symlink_upcall_item`, `STRING_ITEM_SZ`, `POSLEN_ITEM_SZ`, `MAX_NB_UPCALL_ITEMS`, `STRING_TYPE`, `POSLEN_TYPE`, and `EOB_TYPE`.

It is installed by `llite_foreign.c` when foreign file/dir metadata identifies symlink type. The sysfs handlers are declared in `foreign_symlink.h` and are typically wired into the llite mount kobject elsewhere.

## Risks And Edge Cases

- `foreign_symlink_alloc_and_copy_prefix()` subtracts one from `ll_foreign_symlink_prefix_size`; configuration must ensure the prefix is initialized and NUL-terminated.
- Prefix and upcall store comments note that CR/LF/space stripping is not implemented. Sysfs writes with trailing newlines may become part of the path unless sanitized by callers.
- Default parsing trusts `lfm_length` and `lfm_value`; the code comments note missing double-checks of magic, length, and type after metadata load.
- Upcall path replacement and helper execution can race with descriptor installation; comments note a possible mismatch between the path and the format that eventually sets `LL_SBI_FOREIGN_SYMLINK_UPCALL`.
- `foreign_symlink_upcall_info_store()` parses binary data from userspace and allocates per-string memory. Error cleanup must free only initialized string items.
- The failure cleanup in `ll_foreign_symlink_upcall_parse()` frees `suffix_pos + items_size`, while allocation used `suffix_size + prefix_size + 3`; memory-debug correctness depends on allocator semantics and size matching expectations.
- Mount namespace checks protect sysfs writes, but reads are unrestricted.
- Fake directory symlink lookup returns `-ENODATA` for already cached directories when the feature was enabled after caching; callers must tolerate this transitional state.

## Test Signals

Tests should cover default parsing for file and directory foreign metadata, prefix length and `PATH_MAX` enforcement, missing CL object/LMV cache failures, encrypted or unusual path bytes in `lfm_value`, VFS `readlink`/`stat` mode exposure, RCU get-link `-ECHILD`, enabling/disabling from same and different mount namespaces, prefix updates while links are read, upcall path `"none"` and absolute path handling, successful helper invocation, valid descriptor arrays with string and substring items, malformed descriptor sizes/types/early EOB/too many items, substring out-of-bounds rejection, replacement/freeing of old descriptor arrays, and stale cached fake directory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_foreign_symlink.c -->
