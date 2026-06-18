# subset-b-005744 research

Grouped research report for OrangeFS and overlayfs source files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-utils.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-utils.c

Purpose: this file provides OrangeFS kernel-side utility logic for extracting filesystem IDs from queued operations, translating OrangeFS attributes into VFS inode state, pushing dirty inode attributes back to userspace, detecting stale inodes, normalizing OrangeFS protocol errors into Linux errno values, and translating VFS mode bits to OrangeFS permission bits. It is a bridge between the protocol structures in `protocol.h`/`upcall.h` and VFS-visible inode metadata.

Important APIs and functions: `fsid_of_op()` maps each `ORANGEFS_VFS_OP_*` upcall variant to the `fs_id` field embedded in the matching request. `orangefs_inode_flags()`, `orangefs_inode_perms()`, `orangefs_inode_type()`, and `ORANGEFS_util_translate_mode()` convert OrangeFS attribute bits to VFS inode flags, mode bits, object types, and back. `orangefs_inode_getattr()` drives the main getattr upcall and updates `i_uid`, `i_gid`, timestamps, size, blocks, mode, symlink target, and cache expiry. `orangefs_inode_check_changed()` performs a lighter type/link-target freshness check. `orangefs_inode_setattr()` serializes pending `orangefs_inode_s::attr_valid` changes into a setattr upcall. `orangefs_normalize_to_errno()` decodes OrangeFS error encoding via `PINT_errno_mapping`.

Control flow: getattr first checks `orangefs_inode->getattr_time`, pending local attribute changes, and dirty pages under `inode->i_lock`. If local attrs are pending it forces writeback with `write_inode_now()` and retries. It allocates a GETATTR op, requests either all attributes or all-but-size, services the op through `service_operation()`, then rechecks the cache/dirty state before applying the downcall. Existing inodes are validated with `orangefs_inode_is_stale()` before replacement; stale type or symlink-target changes mark non-root inodes bad and return `-ESTALE`. Setattr copies only bits listed in `attr_valid`, clears the mask before sending, and on failure marks the inode bad.

State and persistence behavior: metadata state lives in VFS inode fields and OrangeFS private inode fields (`refn`, `getattr_time`, `attr_valid`, `link_target`). There is no direct on-disk persistence here; durable changes are sent to the OrangeFS userspace client/server through queued kernel ops. Attribute cache lifetime is controlled by `orangefs_getattr_timeout_msecs`; dirty page state suppresses remote size refresh to avoid overwriting local writeback state.

Dependencies and integration points: the file depends on `orangefs-kernel.h` for private inode/op structures, `orangefs-dev-proto.h` for downcall response layout, `orangefs-bufmap.h`, VFS inode helpers, idmapping helpers, and `service_operation()` from the waitqueue path. It is called by inode/super operations such as writeback, getattr, setattr, symlink operation tables, and xattr/permission paths that require fresh inode state.

Risks and test signals: stale detection relies on object type and symlink target only, so metadata races outside those fields depend on normal cache invalidation. `inode->i_blkbits = ffs(blksize)` should be covered for unusual block sizes. Error normalization logs and maps unknown protocol values to `-EINVAL`, which can mask server-side protocol drift. Tests should exercise cache hits, dirty-page getattr suppression, forced writeback retry, symlink target copy bounds, positive and encoded negative OrangeFS errors, root inode stale protection, and setattr failure paths that call `make_bad_inode()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/orangefs-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/protocol.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/protocol.h

Purpose: this header defines kernel-visible OrangeFS protocol constants, file handle/reference structures, error encoding bits, permission and attribute masks, xattr limits, object types, ioctl numbers, and debug/logging glue. It is the ABI-facing vocabulary shared by the OrangeFS kernel module and the userspace client-core protocol.

Important APIs and types: `struct orangefs_khandle` stores 16-byte object handles; `struct orangefs_object_kref` pairs a handle with an `fs_id`. `ORANGEFS_khandle_cmp()`, `ORANGEFS_khandle_to()`, and `ORANGEFS_khandle_from()` compare and marshal handles. `struct ORANGEFS_sys_attr_s` carries owner, group, perms, times, size, object type, flags, block size, distribution hints, and mask bits. `struct ORANGEFS_keyval_pair` models xattr key/value traffic. Constants such as `ORANGEFS_ATTR_SYS_*`, `ORANGEFS_TYPE_*`, `ORANGEFS_XATTR_*`, and `ORANGEFS_DEV_*` are consumed by upcall builders and ioctl handlers. `ORANGEFS_KERNEL_PROTO_VERSION` and `ORANGEFS_MINIMUM_USERSPACE_VERSION` gate kernel/userspace compatibility.

Control flow: the header itself has no runtime flow beyond inline handle helpers and `gossip_debug()`. The handle helpers are used by export and inode code to convert fixed 16-byte OrangeFS handles into larger buffers and back. Error constants define the bit layout decoded later by `orangefs_normalize_to_errno()`.

State and persistence behavior: protocol structs are fixed-size wire/ABI state. Comments call out 32/64-bit compatibility constraints, including xattr name/value sizing and `ORANGEFS_dev_map_desc` layout for mapped buffers. `ORANGEFS_sys_attr_s` contains pointer fields for userspace/system-interface ownership, but kernel code intentionally avoids copying `link_target` into that object for normal setattr.

Dependencies and integration points: depends on Linux kernel types, spinlock types, slab, ioctl macros, and `orangefs-debug.h`. It is included by almost every OrangeFS file in this subset, and its constants must match the userspace OrangeFS source definitions. Ioctl definitions integrate with the OrangeFS device node, while `gossip_debug()` routes debug output through the global `orangefs_gossip_debug_mask`.

Risks and test signals: ABI drift is the dominant risk: field size, alignment, enum, or bit changes can break older userspace clients, especially 32-bit compat paths. Handle conversion assumes at least 16 bytes of storage and uses pointer arithmetic on `void *`, relying on kernel compiler behavior. Tests should validate ioctl numbers, struct sizes/layouts on 32- and 64-bit builds, xattr length boundaries, handle round trips, and error-bit compatibility against the OrangeFS userspace headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/super.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/super.c

Purpose: this file implements OrangeFS superblock lifecycle, mount context parsing, root inode construction, statfs, remount coordination with the userspace client-core, export file handles, inode cache allocation/free, and final superblock teardown. It is the main VFS superblock integration layer for OrangeFS.

Important APIs and functions: `orangefs_init_fs_context()` allocates `orangefs_sb_info_s` and installs `orangefs_context_ops`. `orangefs_parse_param()` handles `acl`, `intr`, and `local_lock`. `orangefs_get_tree()` sends `ORANGEFS_VFS_OP_FS_MOUNT`, allocates an anonymous superblock with `sget_fc()`, calls `orangefs_fill_sb()`, links the superblock into `orangefs_superblocks`, and fetches feature bits when supported. `orangefs_kill_sb()` sends unmount, unlinks from the global list, waits against `orangefs_request_mutex`, and frees private superblock state. `orangefs_statfs()` forwards `statfs` to userspace. Export helpers `orangefs_encode_fh()` and `orangefs_fh_to_dentry()` encode OrangeFS handles and fsids. `orangefs_inode_cache_initialize()` creates the private inode slab with usercopy access to `link_target`.

Control flow: mount requires a source device/config server, sends a mount upcall, rejects null fsids, creates/fills the superblock, obtains the root inode from the root handle, and installs a root dentry. Failure after userspace mount triggers an unmount request or `deactivate_locked_super()`. Remount from client-core uses a priority `ORANGEFS_VFS_OP_FS_MOUNT` with `ORANGEFS_OP_NO_MUTEX`, then optionally requests feature flags. Kill first calls `kill_anon_super()`, then notifies userspace and removes the OrangeFS private superblock from the global list.

State and persistence behavior: persistent remote mount identity is represented in `orangefs_sb_info_s` fields such as `devname`, `fs_id`, `id`, `root_khandle`, `mount_pending`, flags, and list membership. The global `orangefs_superblocks` list is protected by `orangefs_superblocks_lock`; feature bits are stored globally in `orangefs_features`. Private inode state is slab allocated and frees cached xattrs during inode free.

Dependencies and integration points: integrates with VFS `super_operations`, `export_operations`, fs_context APIs, anonymous superblocks, dentry operations, xattr handlers, BDI setup, OrangeFS request operations, global request mutex, and userspace version detection. The export format must line up with `protocol.h` handle encoding and `orangefs_iget()`.

Risks and test signals: mount failure cleanup has several ownership transitions (`op_release`, anonymous superblock activation, `no_list`) that need leak and double-unmount coverage. `orangefs_statfs()` returns `ret` from `service_operation()` but only checks `downcall.status` after the call, so downcall/result consistency matters. Export handle encoding uses fixed raw words and must be stable across 64-bit handles. Tests should cover mount option show/reconfigure, interrupted statfs, client-core remount, userspace feature probing by version, root inode creation failure, xattr cache freeing, and unmount during remount-all synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/symlink.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/symlink.c

Purpose: this small file publishes the inode operation table for OrangeFS symlinks. It binds generic VFS symlink reading to OrangeFS metadata, xattr, permission, setattr, getattr, and timestamp helpers.

Important APIs and functions: `orangefs_symlink_inode_operations` sets `.get_link = simple_get_link`, `.setattr = orangefs_setattr`, `.getattr = orangefs_getattr`, `.listxattr = orangefs_listxattr`, `.permission = orangefs_permission`, and `.update_time = orangefs_update_time`.

Control flow: symlink target contents are prepared elsewhere during inode getattr/copy from the OrangeFS downcall into `orangefs_inode->link_target`; `simple_get_link()` then returns the cached `inode->i_link`. Metadata and permission operations delegate to common OrangeFS inode/xattr paths.

State and persistence behavior: this file owns no storage. Symlink target state lives in the OrangeFS private inode and is populated when `orangefs_inode_getattr()` handles a new symlink. Updates and timestamps are persisted through shared OrangeFS setattr/upcall logic.

Dependencies and integration points: depends on `protocol.h`, `orangefs-kernel.h`, and `orangefs-bufmap.h` for declarations. The operation table is selected by OrangeFS inode construction code for `S_IFLNK` objects.

Risks and test signals: correctness depends on new symlink inodes having `i_link` set before VFS follows the link and on stale symlink target detection in `orangefs_inode_is_stale()`. Tests should cover symlink lookup/follow, target length boundary at `ORANGEFS_NAME_MAX`, stale target replacement returning `-ESTALE`, listxattr on symlinks returning the expected unsupported behavior from xattr code, and timestamp/setattr propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/upcall.h -->
## sources/distributed-fs/ceph-client/fs/orangefs/upcall.h

Purpose: this header defines the request side of the OrangeFS kernel-to-userspace upcall ABI. Each `orangefs_*_request_s` structure describes the fixed wire payload for a VFS operation that will be queued to the client-core.

Important APIs and types: request structures cover file I/O, lookup, create, symlink, getattr, setattr, remove, mkdir, readdir/readdirplus, rename, statfs, truncate, readahead flush, mount/unmount, get/set/list/remove xattr, cancel, fsync, parameter get/set, performance counters, fs key lookup, and features negotiation. `struct orangefs_upcall_s` wraps common `type`, `uid`, `gid`, `pid`, `tgid`, trailer fields, and a union of all request payloads. `enum orangefs_param_request_type`, `enum orangefs_param_request_op`, and `enum orangefs_perf_count_request_type` enumerate tunable and counter operations.

Control flow: the header has no executable flow, but every `op_alloc(type)` user fills the matching member of `orangefs_upcall_s::req` before `service_operation()` queues the operation. `service_operation()` also fills `pid` and `tgid`; callers often fill credentials (`uid`, `gid`) and object references.

State and persistence behavior: upcall instances are transient operation state. Fixed-width fields and explicit pads preserve kernel/userspace ABI stability, especially for 32/64-bit interaction. The union design means only the request matching `type` is valid for a given op.

Dependencies and integration points: depends on protocol definitions such as `orangefs_object_kref`, `ORANGEFS_sys_attr_s`, `ORANGEFS_keyval_pair`, xattr limits, and I/O enums. It is paired with downcall structures in device protocol headers and consumed by waitqueue/device code and all OrangeFS VFS operation implementations.

Risks and test signals: union member mismatches or missing fsid/ref fields cause userspace to operate on the wrong object or fail decoding. Fixed string arrays require careful `strscpy()` and length fields; xattr and symlink limits must match userspace. Tests should validate struct sizes/offsets, operation-specific field population, cancellation tag handling, 32-bit compat layout, and version-gated `features` negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/upcall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/waitqueue.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/waitqueue.c

Purpose: this file implements the in-kernel OrangeFS operation queue and wait path that hands upcalls to the userspace client-core and waits for matching downcalls. It owns retry, timeout, purge, cancellation, and cleanup behavior for `service_operation()`.

Important APIs and functions: `service_operation()` is the central submission API. It stamps pid/tgid, optionally takes `orangefs_request_mutex`, inserts the op into `orangefs_request_list`, wakes the device waitqueue, waits for completion, normalizes status, retries purged operations, and handles interruption/timeouts. `purge_waiting_ops()` marks queued ops purged when client-core exits. `orangefs_cancel_op_in_progress()` converts an in-progress I/O op into a cancel op and requeues it. `wait_for_matching_downcall()` selects completion waits based on writeback/interruptible flags. `orangefs_clean_up_interrupted_operation()` removes waiting or in-progress ops and marks them given up.

Control flow: normal service transitions an op to waiting, links it at head for priority or tail otherwise, wakes client-core, releases the request mutex, and sleeps on `op->waitq`. A serviced op returns with `op->lock` held, is unlocked, then its downcall status is normalized. Timeout, signal, purge, or daemon absence flow into cleanup; purged operations return `-EAGAIN` until `ORANGEFS_PURGE_RETRY_COUNT`, after which they fail with `-EIO`. Shared-memory I/O ops are not internally retried because the caller must recycle the shared buffer.

State and persistence behavior: operation state is in list membership, `op_state` flags, `attempts`, `tag`, `downcall.status`, `waitq`, and shared-memory slot fields. Queue state lives in `orangefs_request_list`, `orangefs_request_list_waitq`, `orangefs_htable_ops_in_progress`, and daemon service status. No durable persistence is done; this is synchronization state between kernel threads and userspace client-core.

Dependencies and integration points: depends on OrangeFS op allocation/state helpers, global request mutex/list locks, completion APIs, daemon service tracking, and `orangefs_normalize_to_errno()`. All higher-level OrangeFS VFS operations funnel through this path.

Risks and test signals: list/lock ordering is critical because ops can be copied by the daemon while callers time out or receive signals. Cleanup handles a `list_empty()` case by waiting for `op->waitq`, which needs race coverage with device copy. Cancellation rewrites the op in place and stores `slot_to_free`, so I/O buffer lifetime must be verified. Tests should simulate daemon down, purge/retry, priority remount ordering, interruptible waits, writeback waits, timeout cleanup from waiting and in-progress states, and shared-memory I/O retry handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/waitqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/xattr.c -->
## sources/distributed-fs/ceph-client/fs/orangefs/xattr.c

Purpose: this file implements Linux VFS extended attribute operations for OrangeFS. It translates get/set/remove/list xattr calls into OrangeFS upcalls, maintains a small per-inode xattr cache, filters OrangeFS-private keys from listing, and exports the xattr handler table for superblock registration.

Important APIs and functions: `orangefs_inode_getxattr()` handles cache lookup, remote GETXATTR, `ENODATA` translation, size probes, and cache fill. `orangefs_inode_setxattr()` handles VFS flag translation, set or remove-on-null, remote SETXATTR, and cache invalidation. `orangefs_inode_removexattr()` sends REMOVEXATTR and treats missing attributes according to replace semantics. `orangefs_listxattr()` iterates LISTXATTR tokens, copies whole keys into the user buffer, and filters keys beginning with `system.pvfs2.` via `is_reserved_key()`. `orangefs_xattr_handlers` exposes a default prefix handler that receives full names.

Control flow: getxattr rejects symlinks and overlong names, then takes `xattr_sem` for read. A valid cached positive or negative entry returns without an upcall. Cache misses allocate a GETXATTR op, fill ref/key/key length, service it, validate returned value length, optionally copy the value to the caller, and cache the result for roughly one second or the configured getattr timeout for negative entries. Set/remove take the semaphore for write, perform the upcall, and delete matching cache entries. Listxattr loops until the OrangeFS token reaches `ORANGEFS_ITERATE_END` or the buffer fills.

State and persistence behavior: remote xattrs are persistent on OrangeFS servers; this file caches copies in `orangefs_inode_s::xattr_cache` buckets guarded by `xattr_sem`. Positive cache entries store key/value/length/timeout; negative entries use `length == -1`. The cache is freed from `orangefs_free_inode()` in `super.c`.

Dependencies and integration points: depends on VFS xattr helpers, POSIX ACL xattr names, OrangeFS op allocation/service, private inode state, and xattr constants from `protocol.h`. `orangefs_listxattr` is wired into symlink operations, and handlers are attached to the superblock in `orangefs_fill_sb()`.

Risks and test signals: `xattr_key()` is a simple modulo sum with possible collision chains, acceptable but worth stress coverage. Cached negative entries can hide newly-created attributes until timeout. `ORANGEFS_MAX_XATTR_LISTLEN` is much smaller than Linux `XATTR_LIST_MAX`, making list iteration important. Tests should cover symlink rejection, size probes, ERANGE, ENOENT-to-ENODATA translation, CREATE/REPLACE flag conversion, null-value removal, reserved-key filtering, multi-token list iteration, malformed server lengths/counts returning `-EIO`, cache invalidation after set/remove, and concurrent readers/writers under `xattr_sem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/orangefs/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/Kconfig -->
## sources/distributed-fs/ceph-client/fs/overlayfs/Kconfig

Purpose: this Kconfig file declares overlayfs build support and default feature toggles. It lets kernel builders enable overlayfs itself and choose default behavior for redirect directories, redirect following, inode indexing, NFS export support, xino inode mapping, metadata-only copy-up, and extra debug checks.

Important APIs and options: `OVERLAY_FS` is a tristate that selects `FS_STACK` and `EXPORTFS`. `OVERLAY_FS_REDIRECT_DIR`, `OVERLAY_FS_REDIRECT_ALWAYS_FOLLOW`, `OVERLAY_FS_INDEX`, `OVERLAY_FS_NFS_EXPORT`, `OVERLAY_FS_XINO_AUTO`, `OVERLAY_FS_METACOPY`, and `OVERLAY_FS_DEBUG` control defaults that are later interpreted by overlayfs module parameters and mount options. Dependencies encode important constraints: NFS export requires index and excludes metacopy, xino auto requires 64-bit, and metacopy selects redirect-dir.

Control flow: Kconfig has no runtime flow, but it controls which defaults are compiled into the overlayfs module and which help text warns about backward compatibility. Runtime mount options can still override most default-on features.

State and persistence behavior: the selected options become kernel configuration state. Several options affect persistent on-upper metadata formats such as redirect xattrs, index directory entries, origin xattrs, and metacopy xattrs; help text explicitly warns that these formats are not backward compatible with older kernels.

Dependencies and integration points: integrates with the kernel build system, documentation in `Documentation/filesystems/overlayfs.rst`, and source files in the overlayfs module that check config defaults. `OVERLAY_FS_NFS_EXPORT` depends on the index feature because file handle decoding relies on indexed lower-to-upper relationships.

Risks and test signals: enabling incompatible defaults can create upper layers that older kernels interpret incorrectly. NFS export and metacopy are mutually constrained because lower-handle stability and metadata-only upper files conflict. Build tests should cover all option combinations allowed by dependencies, especially builtin/module/disabled overlayfs, 32-bit builds without xino auto, NFS export dependency enforcement, and debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/Makefile -->
## sources/distributed-fs/ceph-client/fs/overlayfs/Makefile

Purpose: this Makefile wires the overlayfs module into the kernel build and lists the object files that compose `overlay.o`.

Important APIs and targets: `obj-$(CONFIG_OVERLAY_FS) += overlay.o` builds overlayfs when configured. `overlay-objs` includes `super.o`, `namei.o`, `util.o`, `inode.o`, `file.o`, `dir.o`, `readdir.o`, `copy_up.o`, `export.o`, `params.o`, and `xattrs.o`.

Control flow: there is no runtime control flow. Build control is conditional on `CONFIG_OVERLAY_FS`, and all listed objects are linked into one module/builtin object.

State and persistence behavior: no runtime state is owned here. The object list determines whether features implemented across this subset, such as copy-up, directory mutation, file I/O forwarding, export file handles, and inode metadata handling, are present in the final overlayfs binary.

Dependencies and integration points: depends on Kbuild conventions and the Kconfig symbol from `Kconfig`. The listed objects depend on shared declarations in `overlayfs.h`; omitting any object would break cross-file references such as `ovl_copy_up()`, `ovl_file_operations`, `ovl_dir_inode_operations`, or `ovl_export_operations`.

Risks and test signals: object ordering rarely matters for C symbol resolution but missing additions are easy to overlook when new source files are introduced. Build tests should verify overlayfs as module and builtin, link with all config combinations, and ensure feature symbols referenced by Kconfig-gated code resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/copy_up.c -->
## sources/distributed-fs/ceph-client/fs/overlayfs/copy_up.c

Purpose: this file implements overlayfs copy-up: creating upper-layer representations of lower objects when writes, metadata changes, hardlinks, redirects, NFS export indexing, or metacopy completion require an upper object. It preserves metadata, xattrs, ACLs, file attributes, origin/index references, fsverity digest state, and upper data state while coordinating workdir/tempfile operations.

Important APIs and functions: public entry points are `ovl_maybe_copy_up()`, `ovl_copy_up_with_data()`, `ovl_copy_up()`, `ovl_copy_xattr()`, `ovl_set_attr()`, `ovl_encode_real_fh()`, `ovl_get_origin_fh()`, and `ovl_set_origin_fh()`. Core helpers include `ovl_copy_up_file()` for clone/splice data copy with hole skipping, `ovl_copy_up_metadata()` for xattrs/fileattrs/origin/metacopy/size/owner/timestamps, `ovl_copy_up_workdir()` and `ovl_copy_up_tmpfile()` for the two staging strategies, `ovl_do_copy_up()` for index/destination decisions, and `ovl_copy_up_meta_inode_data()` for converting a metacopy inode into full upper data.

Control flow: `ovl_copy_up_flags()` verifies lower data, walks upward to the topmost ancestor lacking an upper, and calls `ovl_copy_up_one()` under overlay credentials. `ovl_copy_up_one()` gathers lower stat, validates uid/gid mappings, decides metadata fsync and metacopy policy, snapshots parent timestamps and symlink target if needed, serializes with `ovl_copy_up_start()`, then either creates a new upper/index object, links an existing upper alias, or completes data copy for a previous metacopy. Data copy first tries `vfs_clone_file_range()`, falls back to chunked `do_splice_direct()`, and uses `SEEK_DATA` to avoid filling holes where possible.

State and persistence behavior: persistent upper-layer state includes copied data, POSIX ACLs/security xattrs, selected fileattr flags, `overlay.origin`, `overlay.upper`, `overlay.metacopy`, digest flags, index entries, impure parent markers, nlink xattrs, and whiteout flags on copied-up directories. In-memory overlay inode flags such as `OVL_INDEX`, `OVL_UPPERDATA`, `OVL_HAS_DIGEST`, `OVL_VERIFIED_DIGEST`, and `OVL_WHITEOUTS` are updated after successful copy-up. Copy-up uses workdir temp names or `O_TMPFILE`, then atomically links/renames into the upper/index directory.

Dependencies and integration points: depends on VFS file copy, splice, llseek, xattr, ACL, fileattr, fsverity, exportfs file handles, security hooks (`security_inode_copy_up*`), overlay utility wrappers (`ovl_do_*`), index/workdir accessors, credential override helpers, and inode/dentry revalidation functions. It is invoked by open/write paths in `file.c`, metadata operations in `inode.c`, directory mutation in `dir.c`, and export handle encoding in `export.c`.

Risks and test signals: copy-up is race-prone and persistence-sensitive. Risks include partial temp cleanup failure, capability xattr loss during data writes, metacopy digest mismatch, index inconsistency, parent timestamp restoration best-effort failures, uid/gid overflow, clone/splice short copy, hole detection behavior on lower filesystems, and lock ordering with nested overlayfs. Tests should cover regular/dir/symlink/special copy-up, O_TRUNC forcing data copy, metacopy read/write transition, fsync strict modes, lower hardlinks with index on/off, NFS export disconnected copy-up, xattr/ACL/security hook errors, fsverity-required metacopy fallback, sparse files, signals during copy, and cleanup after rename/link failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/copy_up.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/dir.c -->
## sources/distributed-fs/ceph-client/fs/overlayfs/dir.c

Purpose: this file implements overlayfs directory inode operations: create, mkdir, mknod, symlink, link, unlink, rmdir, rename, tmpfile, whiteout management, opaque directory handling, redirect xattrs, and upper object instantiation. It is the main mutation engine for overlay namespace changes.

Important APIs and functions: exported/shared helpers include `ovl_cleanup()`, `ovl_cleanup_and_whiteout()`, `ovl_tempname()`, `ovl_create_real()`, and `ovl_create_temp()`. VFS operation implementations include `ovl_create()`, `ovl_mkdir()`, `ovl_mknod()`, `ovl_symlink()`, `ovl_link()`, `ovl_unlink()`, `ovl_rmdir()`, `ovl_rename()`, and `ovl_tmpfile()`, collected in `ovl_dir_inode_operations`. Key internal paths are `ovl_whiteout()`, `ovl_set_opaque()`, `ovl_create_upper()`, `ovl_create_over_whiteout()`, `ovl_remove_upper()`, `ovl_remove_and_whiteout()`, `ovl_set_redirect()`, `ovl_rename_start()`, and `ovl_rename_upper()`.

Control flow: creation first copies up the parent, takes write access, preallocates an overlay inode, initializes owner/mode, then creates or links the real upper object under overlay/creator credentials. If a whiteout exists at the target, creation uses a temp object and rename/exchange to replace it safely. Removal checks lower presence and directory emptiness; pure uppers are removed directly, while lower-backed entries are covered with whiteouts and possibly opaque empty dirs. Rename validates flags, rejects moves requiring userspace copy (`-EXDEV`), copies up source and relevant parents/targets, sets redirects/opaque markers as needed, performs upper rename, adjusts nlink and dir modification state, and cleans temporary whiteouts.

State and persistence behavior: persistent upper state includes whiteout character devices or shared whiteout links, opaque dir xattrs, redirect xattrs, impure dir xattrs, upper dentries, tmpfiles, POSIX ACLs, and upper directory contents. In-memory state includes dentry upper aliases, opacity/redirect flags, nlink adjustments, and dropped dentries after namespace changes. The whiteout cache (`ofs->whiteout`, `no_shared_whiteout`) is guarded by `whiteout_lock`.

Dependencies and integration points: depends on copy-up (`ovl_copy_up()`), nlink helpers from `inode.c`, xattr wrappers, ACL creation/set helpers, security credential hooks, VFS rename/create/remove APIs through `ovl_do_*`, readdir cache cleanup, backing tmpfile support, and dentry/inode aliasing helpers. Rename and link behavior must align with copy-up origin/index semantics and exportfs requirements.

Risks and test signals: high-risk areas are rename over lower/whiteout entries, directory emptiness checks racing with lookup/readdir, redirect length limits causing `-EXDEV`, whiteout sharing fallback on `-EMLINK`, hardlink/metacopy redirect interactions, casefold inheritance validation, and tmpfile private-data lifetime. Tests should cover create over whiteout, mkdir opaque behavior in merge parents, unlink/rmdir lower-backed entries, rename exchange/noreplace/overwrite, cross-directory redirects, impure marking for origin moves, lower hardlink link/unlink nlink accounting, tmpfile open/instantiate/release, whiteout cleanup failures, and POSIX ACL/mode preservation through umask correction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/export.c -->
## sources/distributed-fs/ceph-client/fs/overlayfs/export.c

Purpose: this file implements overlayfs exportfs/NFS file handle support. It encodes overlay inodes as upper or lower real file handles, ensures lower directory handles are decodable by copy-up/indexing when needed, and decodes handles back into connected overlay dentries using inode cache, index entries, and real-layer ancestry walks.

Important APIs and functions: `ovl_export_operations` provides `.encode_fh`, `.fh_to_dentry`, `.fh_to_parent`, `.get_name`, and `.get_parent`; `ovl_export_fid_operations` provides encode-only support when full NFS export is off. `ovl_encode_fh()` calls `ovl_dentry_to_fid()`, which uses `ovl_check_encode_origin()` and `ovl_encode_real_fh()`. Decode paths are split into `ovl_upper_fh_to_d()` and `ovl_lower_fh_to_d()`. Reconnection helpers include `ovl_obtain_alias()`, `ovl_lookup_real_inode()`, `ovl_lookup_real_ancestor()`, `ovl_lookup_real_one()`, `ovl_lookup_real()`, and `ovl_get_dentry()`.

Control flow: encode chooses upper handles for pure/non-indexed upper objects and lower handles for indexed/non-upper objects. For lower directories with NFS export enabled, `ovl_connect_layer()` may copy up a connectable ancestor before encoding to make future decode possible. Decode validates and aligns the overlay file handle, selects upper or lower path from `OVL_FH_FLAG_PATH_UPPER`, decodes the real file handle, checks index/origin state for lower handles, and either obtains a disconnected non-dir alias or walks from a connected ancestor to reconstruct a connected directory dentry.

State and persistence behavior: persistent decodeability depends on origin xattrs, upper/index file handles, index directory entries, and redirect/impure metadata produced by copy-up and rename paths. In-memory acceleration uses overlay inode cache lookups and dentry aliases; `OVL_E_CONNECTED` caches successful lower-layer connectivity on dentries. This file does not create durable state except indirectly by triggering copy-up during encode.

Dependencies and integration points: depends on exportfs real file handle encoding/decoding, overlay index/origin verification, copy-up, layer metadata, dentry lookup helpers, mount layer roots, and file handle validation helpers. It is tightly coupled to `copy_up.c` origin/index creation and `inode.c` inode hashing/verification.

Risks and test signals: handle stability is sensitive to redirects, non-indexed merge dirs, disconnected lower dentries, stale index entries, and underlying layer renames. Parent file handles are intentionally unsupported, requiring `no_subtree_check`. Tests should cover encode/decode for pure upper, non-indexed upper, indexed upper, lower file, lower directory, root, stale/removed entries, V0/V1 alignment, index lookup failures, lower layer moved outside root returning `-EXDEV`, copy-up-on-encode failure logging, and NFS export with redirect-heavy lower stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/file.c -->
## sources/distributed-fs/ceph-client/fs/overlayfs/file.c

Purpose: this file implements overlayfs regular file operations by opening and forwarding operations to the current real data file, while handling copy-up, metacopy transitions, credential override, flag synchronization, position synchronization, atime/mtime/ctime updates, fsync policy, mmap, fallocate, copy/clone/dedupe, splice, and flush.

Important APIs and functions: `ovl_file_operations` exposes open, release, llseek, read/write iter, fsync, mmap, fallocate, fadvise, flush, splice, copy_file_range, remap_file_range, and setlease. `ovl_open()` verifies lowerdata, maybe copies up for write/truncate, opens the real data file with `ovl_open_realfile()`, and stores an `ovl_file`. `ovl_real_file()` and `ovl_real_file_path()` lazily switch from the originally opened lower/metacopy file to an upper file after copy-up. `ovl_read_iter()`, `ovl_write_iter()`, `ovl_splice_*()`, and `ovl_copyfile()` use backing-file helpers with overlay credentials.

Control flow: open strips creation/truncation flags before passing to the underlying filesystem and stores the real file in private data. Read resolves the current real data file and delegates through `backing_file_read_iter()`. Write locks the overlay inode, copies mode/attrs, resolves the real file, strips sync flags if overlay sync policy says so, delegates write, and updates overlay attrs via the backing context end-write hook. `llseek` keeps overlay `f_pos` authoritative while using the real file for complex seeks. `fsync` avoids lower read-only sync and syncs only relevant upper data. Dedupe refuses to copy up lower-only files just for dedupe.

State and persistence behavior: per-open state is `struct ovl_file` with `realfile` and lazily cached `upperfile`. Persistent writes occur on the selected upper real file after copy-up. Overlay inode timestamps, size, flags, and atime are refreshed from real inodes after access/modify. File flags that can change after open (`O_APPEND`, nonblock, direct) are synchronized to real files by `ovl_change_flags()`.

Dependencies and integration points: depends on `copy_up.c` for write-triggered copy-up, `inode.c` for attr copying and permission-related state, backing-file APIs, VFS file operations, credentials, and lowerdata verification. Directory files use `ovl_dir_real_file()` from readdir code.

Risks and test signals: real file identity can change after metacopy/data copy-up, so lazy upper opening and cmpxchg must be race-safe. `mmap()` uses the originally opened realfile, making write/copy-up interactions important. Dedupe policy differs from clone/copy. Tests should cover read-only lower reads, open for write causing copy-up, metacopy write transition, flag changes after open, seek data/hole through real fs, fsync on lower/merge/upper with datasync, splice deadlock avoidance, fallocate privilege stripping, copy/clone/dedupe cross-layer cases, mmap after copy-up, and concurrent writers opening upperfile once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/inode.c -->
## sources/distributed-fs/ceph-client/fs/overlayfs/inode.c

Purpose: this file implements overlayfs inode metadata operations, inode construction/cache lookup, permission checks, getattr/stat mapping, setattr, ACL handling, symlink link reading, timestamp updates, fiemap, fileattr get/set, lockdep annotation, inode number mapping, and indexed nlink accounting. It connects overlay dentries to stable VFS inode behavior.

Important APIs and functions: VFS operations include `ovl_setattr()`, `ovl_getattr()`, `ovl_permission()`, `ovl_update_time()`, `ovl_fileattr_get()`, `ovl_fileattr_set()`, `ovl_get_acl_path()`, `do_ovl_get_acl()`, and `ovl_set_acl()`. Inode creation/cache APIs include `ovl_new_inode()`, `ovl_inode_init()`, `ovl_get_inode()`, `ovl_lookup_inode()`, `ovl_get_trap_inode()`, and `ovl_lookup_trap_inode()`. Nlink helpers are `ovl_set_nlink_upper()`, `ovl_set_nlink_lower()`, and `ovl_get_nlink()`. Operation tables for regular files, symlinks, and special files are defined here.

Control flow: setattr prepares attrs on the overlay inode, chooses metadata-only or full data copy-up for size changes, clears attr flags that should not reach the real fs, takes write access, applies changes to upper under overlay credentials, then copies attrs back. getattr reads the real path, overlays statx flags, optionally substitutes lower origin inode/block/nlink data for copy-up-stable identity, maps dev/ino through samefs/xino/pseudo-dev policy, and normalizes merge-dir nlink. Permission checks first apply generic overlay inode permissions under caller credentials, then check the real inode under mounter credentials, replacing lower write checks with read checks when copy-up would be needed.

State and persistence behavior: overlay inode state includes upper dentry, lower stack entry, redirect/lowerdata redirect strings, flags (`OVL_INDEX`, `OVL_CONST_INO`, `OVL_WHITEOUTS`, `OVL_IMPURE`, protection flags), mapped inode numbers, nlink values, ACL cache markers, and operation tables. Persistent state touched here includes upper inode attrs, ACL xattrs, fileattr/protattr xattrs, and index nlink xattrs (`overlay.nlink` using `L/U +/- diff` encoding). Trap inodes intentionally dead-mark layer roots to detect loops/conflicts.

Dependencies and integration points: depends on copy-up, xattr/protattr helpers, real fileattr ioctls, POSIX ACL APIs, idmapped mount translation, VFS getattr/permission/setattr, lockdep, overlay layer/index/origin utilities, and `file.c`/`dir.c` operation tables. It supplies inode helpers used by export handle decode and directory create/link paths.

Risks and test signals: stat identity is complex across samefs, xino, lower origin, metacopy blocks, index, redirects, and hardlinks. Permission semantics rely on the two-credential model and lower-write-to-read substitution. ACL idmapping clones must not mutate lower cached ACLs. Inode hashing by lower vs upper controls aliasing and fsnotify behavior. Tests should cover setattr truncate full copy-up, ATTR_OPEN clearing for fuse, getattr before/after copy-up with xino on/off, metacopy block reporting, indexed nlink xattr parsing failures, lower hardlink copy-up, idmapped ACL get/set, immutable/append protattr, trap inode conflicts, nested overlay lockdep classes, permission for lower write requiring mounter read, fiemap delegation, and fileattr security hook failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/overlayfs/inode.c -->
