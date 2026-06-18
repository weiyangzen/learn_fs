# Group Research: group_1230_netbsd_src_sources_os_bsd_netbsd_src_lib_libpuffs_null_c_sources_os_6dd6bb08b117

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/null.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/null.c

This file implements a puffs-backed "nullfs" example/library helper that forwards vnode operations to ordinary host filesystem syscalls using paths built by libpuffs. `puffs_null_setops` installs fs and node callbacks for statvfs, file handles, lookup, create, mknod, attributes, fsync, removal, link, rename, directories, symlinks, readdir, read, and write, while using `puffs_genfs_node_reclaim` for reclaim.

The core metadata helper is `makenode`, which applies requested attributes with `processvattr`, creates a `puffs_node`, refreshes attributes from `lstat`, and fills `puffs_newinfo`. `processvattr` maps vnode attributes to `lchown`, `lchmod`, `lutimes`, and regular-file `truncate`. `writeableopen` temporarily chmods a file to owner-write if open for write fails with `EACCES`, then restores the original mode.

Lookup first verifies the backing path with `lstat`, then searches existing puffs nodes by inode using `puffs_pn_nodewalk`; this avoids returning stale removed nodes but is explicitly noted as slow. File-handle support uses `getfh`, strips an 8-byte fhandle header into a kernel fid-like blob, and only supports handles issued while the server is alive by caching copied fid data in `pn_data`.

Directory reads reopen the directory for each request and skip entries by repeated `readdir_r` calls based on the offset, then emits dirent cookies with `PUFFS_STORE_DCOOKIE`. Reads and writes open the file, seek, perform one syscall, and return residual bytes by subtracting bytes transferred from `*buflen`.

Important limitations are documented in comments: attribute updates have no rollback, file handles are not stable across server lifetime, directory offset handling avoids persistent state, and node lookup by inode is linear.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/null.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/opdump.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/opdump.c

This file contains debug pretty-printers for puffs request and response frames. It defines reverse maps for VFS operations, vnode operations, cache operations, error notifications, and flush operations, plus exported counts for the public `puffsdump.h` debug interface.

`puffsdump_req` prints request id, operation class, whether a reply is expected, operation type name, cookie, auxiliary buffer address/length, process id, and LWP id. For vnode operations it dispatches to specialized dump functions for lookup, read/write, open, target-cookie operations, readdir, create-like operations, and setattr. It also prints elapsed wall-clock time since the previous call under the global puffs lock.

`puffsdump_rv` prints operation-specific response fields for lookup, create-like operations, read/write, readdir, and getattr, followed by the request result and strerror text. The internal `dumpattr` routine formats `struct vattr` while suppressing `PUFFS_VNOVAL` fields as `NOVAL`, covering type, mode, link count, uid/gid, fsid, inode, size, block size, timestamps, generation, flags, rdev, bytes, filerev, and vaflags.

The remaining helpers print cookies, component names, lookup results, create results, read/write offsets and residuals, readdir offsets/residual/eof, open mode, target cookie, and attributes. The file is intentionally debug-only and contains comments acknowledging type punning between similar puffs message layouts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/opdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/paths.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/paths.c

This file implements libpuffs path construction and path comparison helpers used when a mount is created with `PUFFS_FLAG_BUILDPATH`. `puffs_path_pcnbuild` builds the full path for a component name relative to a parent puffs node, optionally applying a path transform and name modifier, then calls the configured `pu_pathbuild` routine and computes a hash if path hashing is enabled.

`puffs_path_prefixadj` is intended for nodewalk use after rename. It checks whether each node path has the old path as a full prefix, constructs a replacement path with the new prefix plus the suffix after the old prefix, updates the path hash, frees the old path object, and continues walking. If path rebuilding fails, the function aborts because partially rewritten path state would be inconsistent.

`puffs_path_walkcmp` performs exact path matching for node walks. It first checks length, then optionally rejects by stored hash, then calls the configured path comparator to handle exact comparison and collisions.

`puffs_path_buildhash` selects `hash32_strn` when using the standard string path builder and `hash32_buf` otherwise. The standard path functions treat paths as slash-separated strings: `puffs_stdpath_cmppath` compares exact paths or full-prefix matches, `puffs_stdpath_buildpath` joins parent and component paths, strips extra slashes, handles `..`, preserves root semantics, and allocates a new path string, and `puffs_stdpath_freepath` frees it.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/paths.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/pnode.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/pnode.c

This file provides puffs node allocation, list management, accessors, and `puffs_newinfo` setters. `puffs_pn_new` allocates and zeroes a `struct puffs_node`, stores private data and mount pointer, initializes `pn_va` with `puffs_vattr_null`, inserts the node in the mount's pnode list, and marks the mount with `PUFFS_FLAG_PNCOOKIE`.

`puffs_pn_remove` removes a node from the mount list and marks it `PUFFS_NODE_REMOVED`; `puffs_pn_put` frees a node, first freeing its path object with the mount's path-free callback and removing it from the list if it was not already removed. This means removed nodes are still freed through the common put path but are not removed twice.

`puffs_pn_nodewalk` linearly walks the mount's pnode list, using next-pointer prefetch before invoking the callback so callbacks can safely remove the current node. A non-NULL callback return value stops the walk and is returned to the caller.

The rest of the file exposes small accessors for vattr, private data, path object, mount, and mount-specific private data. `puffs_newinfo_setcookie`, `setvtype`, `setsize`, `setrdev`, `setva`, `setvattl`, and `setcnttl` fill kernel-return fields through pointers held in `struct puffs_newinfo`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/pnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/puffs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/puffs.c

This is the central libpuffs mount, configuration, daemonization, and event-loop implementation. It exports standard puffs mount options, owns the global `pu_lock`, initializes `struct puffs_usermount`, fills the kernel vnode operation mask from configured callbacks, opens/mounts `/dev/puffs`, and drives request processing through kqueue and frame controllers.

`puffs_init` allocates the usermount and kernel arguments, sets `PUFFSVERSION`, kernel flags, operation mask, mount names, default statvfs/root info/message length/time32 flag, stores the operations table, initializes node and frame lists, installs FS frame callbacks, default path functions, default error notification, and sets state to `PUFFS_STATE_BEFOREMOUNT`. It frees the passed ops table after copying it.

Configuration helpers set blocking mode, stack size, root node and root info, private mount data, mount display names, max request length, file-handle size, cookie hash buckets, path callbacks, name modifiers, error notification, cookie mapping, main-loop callbacks, timeout, and pre/post operation hooks. `puffs_setback` sets selected kernel setback bits for operations where that is legal.

`puffs_mount` supports a special `PUFFS_COMFD` environment path for passing mount data over an existing descriptor; otherwise it canonicalizes the mountpoint, opens `_PATH_PUFFS`, fills `pa_fd`, and calls `mount(MOUNT_PUFFS, ...)`. It adds `MNT_NOSUID|MNT_NODEV` for non-root users and tears down deferred daemon notification state.

The main loop sets the puffs fd nonblocking, registers frame IO with kqueue, installs signal events requested by `puffs_unmountonsignal`, creates a call context, and enters `puffs__theloop`. The loop schedules pending contexts, calls an optional loop function, tries to flush queued writes before waiting, manages EVFILT_WRITE enable/disable, dispatches read/write/signal events to frame handlers, handles close/error notification, and frees deferred removed IO descriptors. `puffs_exit` sends an unmount frame and `finalpush` attempts to write all pending frames before returning.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/puffs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/puffs.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/puffs.h

This public libpuffs header defines the user-facing puffs API, data structures, flags, callback table, and helper prototypes. It includes kernel vnode, mount, namei, stat, statvfs, and puffs message-interface definitions.

Key data structures include `puffs_pathobj`, `puffs_pathinfo`, `puffs_kcache`, `puffs_node`, `puffs_cn`, and the large `puffs_ops` callback table. `puffs_node` stores vnode-like attributes, private data, optional built path, mount pointer, list linkage, and optional cache information. `puffs_cn` wraps kernel component-name data, credentials, and a built full path.

The header defines lib flags such as `PUFFS_FLAG_BUILDPATH`, `PUFFS_FLAG_OPDUMP`, `PUFFS_FLAG_HASHPATH`, and `PUFFS_FLAG_PNCOOKIE`, kernel/lib flag masks, puffs-specific IO/access/fsync constants, setattr/write flags, mount options, and dirent helper macros. `PUFFSOP_PROTOS`, `PUFFSOP_INIT`, `PUFFSOP_SET`, and `PUFFSOP_SETFSNOP` help filesystems declare and install operation callbacks.

The API covers lifecycle (`puffs_init`, `puffs_mount`, `puffs_mainloop`, `puffs_exit`, `puffs_daemon`, `puffs_cancel`), state/configuration, root handling, node allocation/removal/accessors, new-node reply setters, generic fs and genfs helpers, vattr conversion, credentials/access checks, call-context yield/continue/schedule, cache invalidation/flush, path construction, error notification, suspension, and frame-buffer/frame-vector operations.

The header also declares `PUFFSOP_PROTOS(puffs_null)`, making the null filesystem helper visible as a convenience, with an inline comment marking it as questionable public exposure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/puffs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/puffs_priv.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/puffs_priv.h

This private libpuffs header defines internal synchronization, mount state, frame IO, and call-context structures. It includes the puffs message interface, pthreads, public puffs definitions, and ucontext support.

`PU_LOCK` and `PU_UNLOCK` wrap the global `pu_lock`. `PU_CMAP` maps a cookie to a `puffs_node` either through the mount's cookie map callback or by direct cast. `struct puffs_framectrl` groups read, write, compare, got-frame, and fd-notify callbacks for a frame stream. `struct puffs_fctrl_io` stores per-fd frame IO state, send/rescue/event queues, current input frame, read/write wait counts, and list linkage. `FIO_EN_WRITE` and `FIO_RM_WRITE` decide when kqueue write interest should be enabled or disabled.

`struct puffs_usermount` is the private mount instance: operations table, puffs fd, max request length, flags, coroutine stack settings, main context, kqueue state, daemon pipe, root pnode, pnode list, call-context lists, path/name/cookie/error callbacks, pre/post hooks, frame controllers, IO lists, event array, loop callback and timeout, pending kernel args, next request id, and private data. State macros preserve low state bits while setting auxiliary flags.

`struct puffs_cc` represents a call context using either real `ucontext_t` state or a fake function/argument pair, plus caller pid/lwp id and scheduling linkage. `struct puffs_newinfo` stores pointers into reply message fields. The bottom of the file declares internal frame, main-loop, call-context, and FS-frame functions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/puffs_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/puffsdump.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/puffsdump.h

This debug-only public header exposes puffs operation dump helpers implemented by `opdump.c`. Its comment warns callers outside libpuffs that the interfaces are intended only for debug builds and are not stable.

It includes the puffs kernel message-interface header and declares top-level request and response dump functions, cookie and component-name dump functions, operation-specific dump helpers for read/write, readdir, lookup, create, open, attributes, and target cookies.

It also exports the reverse-map arrays and counts for VFS operations, vnode operations, error notifications, and flush operations. These arrays let debug code translate numeric operation classes/types into readable names without duplicating libpuffs internals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/puffsdump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/requests.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/requests.c

This file implements the default puffs filesystem frame controller for communication with the kernel-side provider. Frames are carried with a `struct putter_hdr` prefix and puffs request data.

`puffs__fsframe_read` incrementally reads from the fd into a `puffs_framebuf`. It first ensures enough bytes for the `putter_hdr`, then reads the remaining `pth_framelen` bytes. It grows the frame buffer window as needed, treats EOF as `ECONNRESET`, treats `EAGAIN` as incomplete but not fatal, and rewinds the frame buffer to offset zero when a full frame has arrived.

`puffs__fsframe_write` finalizes the frame length before the first write by mapping the leading `struct puffs_req` and setting `preq_pth.pth_framelen` to `preq_buflen`. It then writes until the full frame length is sent or the fd would block, again returning `ECONNRESET` for zero-byte writes and preserving partial progress via the frame buffer offset.

`puffs__fsframe_cmp` decides whether an incoming frame is a response to a previously sent frame. It maps both puffs request headers, rejects non-response frames by setting `*notresp`, and otherwise compares request ids. `puffs__fsframe_gotframe` rewinds a completed frame and hands it to `puffs__ml_dispatch`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/requests.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/subr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/subr.c

This file provides miscellaneous libpuffs helpers for dirents, no-op filesystem callbacks, generic vnode callbacks, statvfs initialization, vattr initialization/update, and vnode-type/mode/stat conversion.

`puffs_gendotdent` emits either `.` or `..` by calling `puffs_nextdent`. `puffs_nextdent` checks whether the supplied result buffer has enough room for an aligned dirent, fills file number, type, name length, name, and record length, advances the dirent pointer, and subtracts from the residual length.

`puffs_fsnop_unmount`, `puffs_fsnop_sync`, and `puffs_fsnop_statvfs` provide simple defaults. The statvfs default sets block/frsize/iosize to `DEV_BSIZE`, all counts to zero, and name max to `MAXNAMLEN`. `puffs_zerostatvfs` wraps that default. `puffs_genfs_node_getattr` copies attributes from a puffs node and `puffs_genfs_node_reclaim` frees a puffs node with `puffs_pn_put`.

`puffs_setvattr` copies only meaningful, non-`PUFFS_VNOVAL` fields from one vattr to another. `puffs_vattr_null` initializes a vattr to VNON/NOVAL style defaults while setting block size from page size and zeroing flags/generation/vaflags. `puffs_vtype2dt`, `puffs_mode2vt`, `puffs_stat2vattr`, and `puffs_addvtype2mode` bridge vnode types, dirent dtypes, mode bits, and `struct stat`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/suspend.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/suspend.c

This file is a compatibility stub for puffs filesystem suspension. `puffs_fs_suspend` takes a `struct puffs_usermount *` but ignores it and returns `EOPNOTSUPP`.

The comment explains that suspension "used to be" implemented, but no longer is, and the function remains to avoid an ABI bump. Callers must therefore treat suspension as unsupported even though the symbol still exists in the library.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libpuffs/suspend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/Makefile

This Makefile builds the NetBSD `libquota` library. It sets `WARNS?=5`, names the library `quota`, and links against `librpcsvc`, which is needed by the NFS rquota backend.

The source list includes the public handle/open/schema/get/put/delete/cursor layers plus the three backend implementations: NFS RPC, old quota files, and kernel quotactl. The installed manual page is `libquota.3`, with many MLINKS for individual public functions such as `quota_open`, `quota_get`, `quota_put`, `quota_delete`, cursor operations, schema inspection, quota on/off, and `quotaval_clear`.

It includes `<bsd.own.mk>` and `<bsd.lib.mk>`, following the normal NetBSD library build pattern.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_cursor.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_cursor.c

This file implements the public quota cursor API and dispatches cursor operations to either legacy quota files or the kernel interface. NFS mode does not support cursors and returns `EOPNOTSUPP`.

`quota_opencursor` chooses restrictions based on the handle mode. Old files always require quotacheck-style access; kernel mode queries restrictions with `__quota_kernel_getrestrictions`. If restrictions include `QUOTA_RESTRICT_NEEDSQUOTACHECK` and old files are not already open, it initializes the old-file backend. It then allocates `struct quotacursor`, stores the handle, selects `QC_OLDFILES` or `QC_KERNEL`, and creates the backend cursor, preserving errno on allocation/creation failures.

`quotacursor_close` destroys the backend cursor and frees the wrapper. `quotacursor_skipidtype`, `quotacursor_get`, `quotacursor_getn`, `quotacursor_atend`, and `quotacursor_rewind` switch on `qc_type` and call the corresponding oldfiles or kernel helper. Any impossible cursor type falls through to `EINVAL`.

The design lets callers use one cursor API regardless of whether the mounted filesystem has a modern kernel quota iterator or must be scanned through quota1 files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_cursor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_delete.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_delete.c

This file implements the public `quota_delete` operation as a mode dispatcher. It rejects NFS handles with `EOPNOTSUPP`, because rquotad access is read-only in this library. Old quota-file handles call `__quota_oldfiles_delete`, and kernel handles call `__quota_kernel_delete`.

If the handle contains an unknown mode, the function sets `EINVAL` and returns -1. The file contains no policy beyond backend selection; actual deletion semantics are implemented by clearing old quota-file records or issuing a kernel `QUOTACTL_DEL` request.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_delete.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_get.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_get.c

This file provides `quotaval_clear` and the public `quota_get` dispatcher. `quotaval_clear` sets hard and soft limits to `QUOTA_NOLIMIT`, usage to zero, and both expire and grace time to `QUOTA_NOTIME`, establishing the library's representation for "no quota".

`quota_get` routes by `qh_mode`: NFS handles use `__quota_nfs_get`, old quota-file handles use `__quota_oldfiles_get`, and kernel handles use `__quota_kernel_get`. Unknown modes return `EINVAL`.

The file intentionally keeps common API behavior thin and leaves backend-specific validation, scaling, and error translation to the selected implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_get.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_kernel.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_kernel.c

This file implements the modern kernel quota backend by wrapping `__quotactl` operations. `__quota_kernel_stat` issues `QUOTACTL_STAT` and underlies implementation-name, restriction, id-type count, and object-type count queries. Type-name and object-type detail functions issue `QUOTACTL_IDTYPESTAT` and `QUOTACTL_OBJTYPESTAT`.

`__quota_kernel_quotaon` fetches the oldfiles quota filename from fstab data and passes it to `QUOTACTL_QUOTAON`. Its comment explains that filesystems decide whether quotaon is valid and that repeated quotaon is allowed. `__quota_kernel_quotaoff` issues `QUOTACTL_QUOTAOFF`.

Data operations are straightforward: `__quota_kernel_get` uses `QUOTACTL_GET`, `put` uses `QUOTACTL_PUT`, and `delete` uses `QUOTACTL_DEL`, all keyed by the mountpoint stored in the quota handle.

Kernel cursors are thin wrappers around `struct quotakcursor`. Create opens with `QUOTACTL_CURSOROPEN`; destroy sends `QUOTACTL_CURSORCLOSE` and warns if that fails; skip, get, atend, and rewind map to the corresponding cursor quotactl operations. `cursor_getn` rejects `maxnum > INT_MAX`, returns the kernel-reported number of entries, and `cursor_get` simply asks for one entry. `cursor_atend` returns -1 on kernel error so simple nonzero tests stop iterating while advanced callers can distinguish errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_kernel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_nfs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_nfs.c

This file implements read-only NFS quota retrieval through the rquota RPC protocol. It scales remote rquota block values by the server-provided block size into DEV_BSIZE units and maps zero remote limits to `QUOTA_NOLIMIT`; nonzero limits are stored as remote value minus one, matching the library convention used elsewhere.

`rquota_to_quotavals` converts one `struct rquota` into separate block and inode `quotaval` records, setting expire times as current time plus server time-left values and grace to `QUOTA_NOTIME`. `callaurpc` resolves the host with `gethostbyname`, creates a UDP RPC client, installs default authunix credentials, and calls the requested procedure with a 25-second total timeout.

`__quota_nfs_get` validates id type as user or group and object type as blocks or files, then splits the mount device string as `host:path`. It first tries extended rquota version `EXT_RQUOTAVERS`, including group quota support. If the server reports version mismatch or no registered program and the request is for user quotas, it falls back to old `RQUOTAVERS`.

RPC failures are translated for convenience: unreachable or unsupported cases can become `ENOENT`. Rquota status `Q_NOQUOTA` returns a cleared quota value, `Q_EPERM` becomes `EACCES`, `Q_OK` returns either the converted block or file quota, and unknown status becomes `ERANGE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_oldfiles.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_oldfiles.c

This file implements direct access to old UFS/FFS quota1 files and fstab quota-option discovery. It keeps a process-global parsed fstab table of mountpoints with `userquota` and/or `groupquota` options, including optional explicit quota-file paths.

`__quota_oldfiles_load_fstab` parses `_PATH_FSTAB` once, skipping missing fstab silently, and records only `ffs` and `lfs` entries with quota options. `__quota_oldfiles_getquotafile` returns the explicit configured quota file or constructs the default `<mountpoint>/<QUOTAFILENAME>.<type>` path using `INITQFNAMES`. `__quota_oldfiles_initialize` opens configured user/group quota files read-write, falling back to read-only for `EACCES` or `EROFS`, and stores fds on the quota handle.

The `dqblk` conversion helpers map legacy quota1 limits, usage, and times to `quotaval`. Limit zero means `QUOTA_NOLIMIT`; otherwise limits are stored as value minus one. Default quota id records use position zero and map grace through expire-time fields. Id zero is treated specially: get suppresses limits/times, and put updates usage while preserving limits/times.

`__quota_oldfiles_doget` reads one `struct dqblk` at `id * sizeof(dqblk)` or position zero for the default id, validates complete reads, converts either block or file object values, and can report all-zero records for cursor skipping. `__quota_oldfiles_doput` reads or creates a blank record, merges object-specific updates, and writes the full dqblk back. Delete clears values through `quotaval_clear`.

`__quota_oldfiles_quotaon` closes direct fds, calls the kernel quotaon path, and switches the handle to kernel mode after success. The oldfiles cursor iterates users then groups, default entry then numeric ids, blocks then files, skipping all-zero records except at the effective end to avoid false failures. One caveat visible in `cursor_create`: it calls `fstat` on both handle fds without checking that disabled user/group fds are negative, so the caller's initialization/path selection matters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_oldfiles.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_open.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_open.c

This file implements quota handle creation/destruction and quota on/off dispatch. `quota_open` calls `statvfs` on any path within the target volume, loads fstab quota metadata, and selects backend mode in a documented order: NFS first, because it uses rquotad instead of kernel quota state; kernel mode if `ST_QUOTA` is set; old quota files if fstab enables quota options; otherwise `EOPNOTSUPP`.

On success it allocates `struct quotahandle`, stores duplicated mountpoint and mount device strings from `statvfs`, records the selected mode, and initializes oldfiles state and fds. Allocation failures preserve errno and free partial state. `quota_getmountpoint` and `quota_getmountdevice` return the stored strings.

`quota_close` closes open user/group quota file descriptors, frees the mount strings, and frees the handle. `quota_quotaon` rejects NFS, calls oldfiles quotaon for oldfiles handles, and calls kernel quotaon for kernel handles. `quota_quotaoff` rejects NFS, rejects oldfiles with `ENOTCONN` because direct oldfiles mode has not quotaon'd through the kernel, and calls kernel quotaoff for kernel handles. Unknown modes return `EINVAL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_put.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_put.c

This file implements the public `quota_put` operation as a backend dispatcher. NFS handles return `EOPNOTSUPP` because the rquota backend is read-only. Old quota-file handles call `__quota_oldfiles_put`, and kernel handles call `__quota_kernel_put`.

Unknown handle modes return `EINVAL`. All actual storage semantics, including old quota-file record merging and kernel `QUOTACTL_PUT`, live in the backend files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_put.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_schema.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_schema.c

This file implements schema and capability inspection for quota handles. `quota_getimplname` reports `"nfs via rquotad"` for NFS, delegates oldfiles and kernel implementation names to their backends, and returns `EINVAL` for invalid mode.

`quota_getrestrictions` reports NFS as 32-bit and read-only, oldfiles as needing quotacheck with uniform grace and 32-bit values, and kernel restrictions from `__quota_kernel_getrestrictions`. `quota_getnumidtypes` returns two for NFS and oldfiles and delegates kernel mode. `quota_idtype_getname` delegates kernel mode, otherwise maps user/group to `"user"`/`"group"` and invalid ids to `"???"` with `EINVAL`.

Object-type helpers follow the same pattern. `quota_getnumobjtypes` returns two except for kernel delegation. `quota_objtype_getname` maps blocks to `"block"` and files to `"file"` unless kernel mode supplies names. `quota_objtype_isbytes` delegates kernel mode, otherwise reports block quotas as byte-like and file quotas as count-like.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quota_schema.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quotapvt.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libquota/quotapvt.h

This private libquota header defines backend mode constants, internal handle/cursor structures, and backend function prototypes. `QUOTA_MODE_NFS`, `QUOTA_MODE_OLDFILES`, and `QUOTA_MODE_KERNEL` identify the selected implementation.

`struct quotahandle` stores the mountpoint, mount device, mode, and oldfiles-only state: whether files are open and user/group quota file descriptors. `struct quotacursor` stores the owning handle, cursor type (`QC_OLDFILES` or `QC_KERNEL`), and a union of backend cursor pointers.

The prototypes are grouped by backend. Kernel functions expose implementation metadata, restrictions, id/object type info, quotaon/off, get/put/delete, and cursor operations. The NFS interface only exposes get. Oldfiles functions include fstab loading/lookup, initialization, implementation name, quota-file discovery, quotaon, get/put/delete, and cursor operations. The header also declares `__quota_getquota` compatibility for the old library interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libquota/quotapvt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libradius/Makefile

This Makefile builds the NetBSD `libradius` network protocol library. It enables fortified-source behavior with `USE_FORT?= yes`, installs the shared library under the normal shared-library directory, sets warnings to level 3, and suppresses one lint warning class with `LINTFLAGS+= -Sw`.

It builds from `radlib.c`, installs `radlib.h` and `radlib_vs.h` into `/usr/include`, and installs manual pages `libradius.3` and `radius.conf.5`. The library is compiled with `-DWITH_SSL` and `-DOPENSSL_API_COMPAT=0x10100000L`, and links against OpenSSL libcrypto from the external crypto subtree. This enables HMAC/MD5 message authenticator support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/radlib.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libradius/radlib.c

This file implements a UDP RADIUS client library for authentication and accounting. It handles server configuration, request construction, password hiding, message/request authenticators, retry scheduling, response validation, attribute parsing, vendor-specific attributes, and Microsoft MPPE key demangling.

The cryptographic helpers use OpenSSL MD5/HMAC when built with `WITH_SSL`. `insert_scrambled_password` applies the RFC password-hiding MD5 chain using the shared secret and request authenticator. `insert_request_authenticator` computes accounting request authenticators. `insert_message_authenticator` fills a zero-placeholder Message-Authenticator with HMAC-MD5 over the request. Response validation checks source address/port, packet length, response authenticator, and optional Message-Authenticator for non-accounting responses.

Configuration is done by `rad_add_server` or `rad_config`. `rad_config` reads `/etc/radius.conf` by default, parses whitespace/quoted fields with comments using `split`, supports optional `auth`/`acct` service tags, host:port, secret, timeout, and max tries, and ignores entries for the other handle type. Secrets and password buffers are wiped before free/close where possible.

`rad_create_request` initializes code, identifier, random authenticator, and attribute position. Attribute writers enforce call order, maximum message/attribute length, accounting restrictions, EAP Message-Authenticator requirements, and mutual exclusion between User-Password and CHAP password. The synchronous `rad_send_request` is built on nonblocking-style `rad_init_send_request` and `rad_continue_send_request`, which expose fd/timeval state to callers that want their own select loop. Servers are tried round-robin until each reaches its max tries.

Response readers include `rad_get_attr`, `rad_get_vendor_attr`, and conversion helpers for address, integer, and string values. Vendor writers package vendor id, vendor type, vendor length, and payload inside a `RAD_VENDOR_SPECIFIC` attribute and mark Microsoft CHAP attributes as password-bearing. `rad_demangle` and `rad_demangle_mppe_key` reverse RADIUS/MPPE encrypted data using the request authenticator and shared secret.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/radlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/radlib.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libradius/radlib.h

This public header defines the main RADIUS library constants and API. It declares packet codes for access request/accept/reject/challenge and accounting request/response, plus a large set of standard RADIUS attribute type constants and enumerated values for service type, framed protocol, compression, NAS port type, accounting status/authentication/termination causes, EAP, Message-Authenticator, IPv6 attributes, and related fields.

The API is centered on opaque `struct rad_handle`. It exposes handle creation for authentication and accounting (`rad_auth_open`, `rad_acct_open`, deprecated `rad_open`), server/config setup, close, request creation, attribute writers for address/int/string/raw data, Message-Authenticator insertion, request sending in blocking and staged forms, response attribute iteration, conversion helpers, request authenticator extraction, server secret lookup, error-string access, and generic password demangling.

The header includes only system types and IPv4 address definitions needed by callers. Microsoft/vendor-specific support is separated into `radlib_vs.h`, though private code includes it for implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/radlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/radlib_private.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libradius/radlib_private.h

This private RADIUS header defines implementation constants and internal state structures. It includes the public RADIUS header and vendor-specific header.

Handle type constants distinguish authentication and accounting. Defaults include max tries, config path `/etc/radius.conf`, standard RADIUS and accounting UDP ports, and timeout. Limits define error-message length, config line length, max server count, max message size, and significant password size. Packet offsets define code, identifier, length, authenticator, authenticator length, and start of attributes.

`struct rad_server` stores a server sockaddr, shared secret, timeout, maximum tries, and current try count. `struct rad_handle` stores the socket fd, server array and count, current identifier, last error, request buffer and length, cleartext password scratch state, CHAP/EAP/authenticator flags, response buffer and scan position, retry counters, selected server index, and handle type.

`struct vendor_attribute` is the packed-in-practice layout used to construct and parse RADIUS vendor-specific attribute payloads: vendor id, nested attribute type, nested length, and data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/radlib_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/radlib_vs.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libradius/radlib_vs.h

This public vendor-specific RADIUS header defines Microsoft vendor id `311` and RFC 2548 Microsoft attribute codes, including MS-CHAP response/error/password/challenge attributes, MPPE encryption policy/types/send/recv keys, RAS metadata, ARAP password fields, filters, accounting auth/EAP type, DNS/NBNS server attributes, and ARAP challenge.

It defines `SALT_LEN` as 2 for MPPE key decoding and forward-declares `struct rad_handle`. The API adds vendor-specific helpers to parse a vendor attribute, put vendor address/raw/int/string attributes, and demangle Microsoft MPPE keys. These functions complement the base `radlib.h` API without exposing private handle layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libradius/radlib_vs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/Makefile

This Makefile builds `librefuse`, NetBSD's FUSE compatibility library implemented on top of puffs and pthreads. It enables fortified-source behavior, names the library `refuse`, and links against `libpuffs` and `libpthread`.

If `DEBUG` is defined, it adds `-g -DFUSE_OPT_DEBUG`. It includes the current directory in the preprocessor path and builds the main high-level, compatibility, logging, low-level, option, and signal source files. It installs `refuse.3` and public headers `fuse.h`, `fuse_opt.h`, `fuse_log.h`, and `fuse_lowlevel.h` into `/usr/include`.

It also includes `refuse/Makefile.inc`, which contributes additional versioned compatibility headers/sources used by the public `fuse.h` API selection layer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse.h

This public header exposes ReFUSE's high-level FUSE compatibility API. It includes option, buffer, channel, legacy, poll, session, stat, statvfs, and utime-related headers, then defines version selection logic for many FUSE API generations.

Version handling is central. `FUSE_MAKE_VERSION` supports the historical `(maj * 10 + min)` encoding and the FUSE 3.10-era `(maj * 100 + min)` encoding. ReFUSE declares implementation support through `_REFUSE_MAJOR_VERSION_` 3 and `_REFUSE_MINOR_VERSION_` 10. User code is expected to define `FUSE_USE_VERSION`; if not, external users get a warning and default to the latest version. `FUSE_VERSION`, `FUSE_MAJOR_VERSION`, and `FUSE_MINOR_VERSION` are tied to `FUSE_USE_VERSION`.

Common structs include `fuse_file_info`, `fuse_conn_info`, `fuse_context`, `fuse_config`, `fuse_loop_config`, and `fuse_args`, plus FUSE capability flags, ioctl flags, and readdir/fill-dir flags. Common functions include loop/exit/context, daemonize, interrupted check, cache invalidation by path, version strings, group lookup, cleanup-thread helpers, cache cleanup, and the internal generic `__fuse_main`.

The bottom half includes all versioned compatibility headers unconditionally, then uses `#if FUSE_USE_VERSION` blocks to alias `fuse_operations`, fill-dir types, mount/unmount/new/destroy/setup/teardown/loop/parse/fs wrappers, and inline `fuse_main`/`fuse_new`/`fuse_setup` signatures for API versions 1.1 through 3.10. This preserves source compatibility for filesystems written against older FUSE APIs while routing implementation to version-suffixed ReFUSE entry points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse_internal.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse_internal.h

This private ReFUSE header defines implementation-only structure and helper prototypes. It defines `_REFUSE_IMPLEMENTATION_` before including `fuse.h` so ReFUSE's own source files do not receive the public warning about missing `FUSE_USE_VERSION`.

The private `struct fuse` contains the underlying `struct puffs_usermount *`, a `dead` flag, and a pointer to the base `struct fuse_fs` layer. This confirms the high-level FUSE compatibility layer is backed by libpuffs.

`enum refuse_show_help_variant` defines internal help-output variants for full help and no-header help. Hidden declarations expose signal handler setup/removal, generic setup/teardown, generic `fuse_new`, mount/unmount/destroy, multithreaded loop, and command-line parsing. These symbols are hidden from users and are intended to be called by the versioned compatibility wrappers and implementation files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse_internal.h -->