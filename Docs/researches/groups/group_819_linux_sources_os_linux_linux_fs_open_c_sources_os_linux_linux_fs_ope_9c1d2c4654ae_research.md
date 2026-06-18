# Group Research: group_819_linux_sources_os_linux_linux_fs_open_c_sources_os_linux_linux_fs_ope_9c1d2c4654ae

Scope checked against `Docs/research_subset_a.md`; all listed files are under `sources/os/linux/linux`. Each source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/open.c -->
# File Research: sources/os/linux/linux/fs/open.c

Core VFS syscall and helper implementation for truncation, fallocate, access checks, directory/root changes, chmod/chown, open/openat/openat2/creat, close, and generic file open helpers. It is a central policy layer between userspace syscalls and filesystem-specific inode/file operations.

Key flows:
- `do_truncate()`, `vfs_truncate()`, `ksys_truncate()`, and `do_ftruncate()` validate regular files, write permissions, append-only state, LSM/fsnotify hooks, mount write access, leases, and idmapped mount ownership before calling `notify_change()`.
- `vfs_fallocate()` validates mutually exclusive fallocate modes, write permissions, append/immutable/swapfile restrictions, size overflow, and dispatches to `file->f_op->fallocate`.
- `do_faccessat()` implements real-credential `access()` semantics by optionally overriding fsuid/fsgid and capabilities, then performs path lookup, `noexec`, permission, and readonly checks.
- `chmod_common()` and `chown_common()` perform mount write accounting, delegation break/retry handling, LSM checks, idmapped ownership conversion, suid/sgid/capability stripping, and `notify_change()`.
- `do_dentry_open()` is the main file initialization path: binds path/inode/mapping, handles `O_PATH`, read/write accounting, file operation lookup, security/fsnotify hooks, leases, `->open()`, direct-I/O capability, readahead state, and cleanup on failure.
- `build_open_how()` and `build_open_flags()` normalize legacy and `openat2()` inputs, validate `RESOLVE_*` flags, handle `O_TMPFILE`, `O_PATH`, `O_SYNC`, `OPENAT2_REGULAR`, lookup flags, and access mode.
- `do_sys_openat2()`, `do_sys_open()`, syscall wrappers, `filp_open()`, `file_open_root()`, `vfs_open()`, `dentry_open()`, and `kernel_file_open()` provide user and in-kernel open entry points.
- `filp_flush()`, `filp_close()`, and `close()` handle filesystem flush callbacks, dnotify, POSIX lock cleanup, fd removal, and non-restartable close error normalization.
- `generic_file_open()`, `nonseekable_open()`, and `stream_open()` are exported helpers for filesystem/file-operation implementations.

Important dependencies and invariants:
- Heavy use of `mnt_idmap()`, `inode_permission()`, LSM hooks, fsnotify hooks, leases/delegations, `mnt_want_write*()`, and VFS name lookup helpers.
- Open flag validation intentionally rejects contradictory or unsafe combinations such as `O_DIRECTORY|O_CREAT`, unsupported `openat2()` flags, invalid `RESOLVE_*` combinations, and impossible `O_TMPFILE` modes.
- `do_dentry_open()` carefully unwinds path refs, fops refs, write access, and inode/file pointers on failure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/openpromfs/Makefile -->
# File Research: sources/os/linux/linux/fs/openpromfs/Makefile

Build glue for Sun OpenPROM filesystem support.

It compiles `openpromfs.o` when `CONFIG_SUN_OPENPROMFS` is enabled, with `inode.o` as the only object in the module/object aggregate.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/openpromfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/openpromfs/inode.c -->
# File Research: sources/os/linux/linux/fs/openpromfs/inode.c

Implements `openpromfs`, a small virtual filesystem exposing OpenPROM/OpenFirmware device-tree nodes as directories and properties as files.

Key structures and behavior:
- `op_inode_info` embeds `struct inode` and records whether the inode represents a firmware node or property.
- `property_show()` renders property values as printable strings, chained string lists, byte hex, or 32-bit hex words.
- `openpromfs_lookup()` searches a node’s children first, then properties, creates/initializes inodes via `openprom_iget()`, and returns `d_splice_alias()`.
- `openpromfs_readdir()` emits `.`, `..`, child node directories, then property files, using firmware `unique_id` values as inode numbers.
- Root setup in `openprom_fill_super()` creates inode `0`, binds it to `of_find_node_by_path("/")`, installs directory ops, and creates the root dentry.
- Module init creates a slab cache for `op_inode_info`, registers filesystem type `openpromfs`, and teardown unregisters plus drains RCU before destroying the cache.

Notable details:
- `op_mutex` serializes traversal of firmware node/property lists.
- The `options/security-password` property is mode `0600`; other properties are readonly regular files.
- The filesystem is single-instance via `get_tree_single()`, anonymous-super backed, `SB_NOATIME`, and uses `simple_statfs`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/openpromfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/Kconfig -->
# File Research: sources/os/linux/linux/fs/orangefs/Kconfig

Defines `CONFIG_ORANGEFS_FS` as a tristate filesystem option labelled `ORANGEFS (Powered by PVFS) support`.

It selects `FS_POSIX_ACL` and describes OrangeFS as a parallel filesystem for high-end computing systems.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/Makefile -->
# File Research: sources/os/linux/linux/fs/orangefs/Makefile

Builds the OrangeFS kernel filesystem module/object when `CONFIG_ORANGEFS_FS` is enabled.

The aggregate `orangefs.o` includes ACL, file, cache, utility, xattr, dcache, inode, sysfs, module init, superblock, device request, namei, symlink, directory, bufmap, debugfs, and waitqueue objects.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/acl.c -->
# File Research: sources/os/linux/linux/fs/orangefs/acl.c

Implements POSIX ACL get/set support for OrangeFS by storing ACLs in OrangeFS extended attributes.

Key behavior:
- `orangefs_get_acl()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`, fetches the xattr via `orangefs_inode_getxattr()`, and converts it with `posix_acl_from_xattr()`.
- RCU ACL lookup returns `-ECHILD`; OrangeFS performs blocking xattr RPCs.
- `__orangefs_set_acl()` converts ACLs with `posix_acl_to_xattr()` and writes/removes the backing xattr through `orangefs_inode_setxattr()`, then updates the VFS ACL cache.
- `orangefs_set_acl()` uses `posix_acl_update_mode()` for access ACLs, writes the ACL, and propagates resulting mode changes with `__orangefs_setattr_mode()`.

Important interactions:
- Depends on xattr implementation and inode setattr path.
- Treats missing ACL xattrs and unsupported ACL operations as no ACL (`NULL`) for get.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/dcache.c -->
# File Research: sources/os/linux/linux/fs/orangefs/dcache.c

Implements OrangeFS dentry revalidation.

Key behavior:
- `orangefs_revalidate_lookup()` sends an `ORANGEFS_VFS_OP_LOOKUP` upcall for the parent/name pair.
- Positive dentries are kept only if lookup succeeds and the returned handle matches the cached inode.
- Negative dentries are kept only if lookup still returns `-ENOENT`.
- Successful revalidation refreshes `d_fsdata` timeout via `orangefs_set_timeout()`.
- `orangefs_d_revalidate()` trusts unexpired dentries, rejects RCU lookup with `-ECHILD`, always trusts root, and then validates positive inode contents with `orangefs_inode_check_changed()`.

Important invariants:
- Dentry timeout is jiffies-based and configured by `orangefs_dcache_timeout_msecs`.
- Lookup and getattr revalidation are distinct: name validity is checked first, inode attribute freshness second.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/dcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/devorangefs-req.c -->
# File Research: sources/os/linux/linux/fs/orangefs/devorangefs-req.c

Implements the `/dev/pvfs2-req` character device used as the OrangeFS kernel/userspace RPC bridge.

Key behavior:
- Only one userspace client-core may open the device; opens must be `O_NONBLOCK` and from `init_user_ns`.
- `orangefs_devreq_read()` selects queued kernel operations from `orangefs_request_list`, skips operations for filesystems pending remount, copies protocol/version/tag/upcall to userspace, marks the op in-progress, and inserts it into the in-progress hash table.
- `orangefs_devreq_write_iter()` accepts daemon downcalls, validates protocol version/magic/tag, removes the matching in-progress op, copies the downcall and optional readdir trailer, then marks the op serviced or handles cancellation/give-up state.
- `orangefs_devreq_release()` finalizes bufmap state, marks mounted filesystems pending, purges waiting and in-progress operations, runs down shared buffers, and clears userspace version/open state.
- Ioctls expose protocol magic and max up/down sizes, initialize the shared buffer map, trigger remount-all, report upstream module status, and update debugfs client/kernel debug state.
- Compat ioctl translates 32-bit `ORANGEFS_DEV_MAP`.

Important dependencies:
- Coordinates with global request lists, operation state machine, bufmap, superblock list, debugfs, and waitqueue purge logic.
- Device polling reports `EPOLLIN` when kernel upcalls are queued.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/devorangefs-req.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/dir.c -->
# File Research: sources/os/linux/linux/fs/orangefs/dir.c

Implements OrangeFS directory file operations and readdir buffering.

Key behavior:
- `orangefs_dir` tracks the server readdir token, linked list of received directory parts, logical end position, and sticky error state.
- `do_readdir()` sends `ORANGEFS_VFS_OP_READDIR`, obtains a readdir slot, handles daemon restart/purge retries, validates trailer size, and updates the continuation token.
- Readdir trailers begin with `orangefs_readdir_response_s`; following entries are encoded as string length, string, padding, khandle, and padding.
- `parse_readdir()` stores trailer buffers as linked `orangefs_dir_part` nodes.
- `fill_from_part()` decodes entries from the current `ctx->pos`, emits names with inode numbers derived from khandles, and treats corrupt/invalid positioning as `EIO`.
- `orangefs_dir_iterate()` synthesizes `.` and `..`, reads more parts as needed, fills userspace buffers, and enforces position validity.
- `orangefs_dir_llseek()` frees cached parts and resets token when seeking backward.

Important details:
- Directory positions encode part number and byte offset using `PART_SHIFT`.
- Directory data is vmalloc-backed trailer memory freed on release or seek reset.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/downcall.h -->
# File Research: sources/os/linux/linux/fs/orangefs/downcall.h

Defines kernel-facing response structures sent from OrangeFS userspace daemon to the kernel.

Contents:
- Response payloads for I/O, lookup, create, symlink, getattr, mkdir, statfs, mount, xattr get/list, parameter requests, performance counters, filesystem keys, and feature negotiation.
- `orangefs_downcall_s` wraps operation type, status, optional trailer size/buffer, and a union of response payloads.
- `orangefs_readdir_response_s` defines the header stored at the beginning of readdir trailers.

Important role:
- This header is included by the device protocol and determines the ABI layout copied through `/dev/pvfs2-req`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/downcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/file.c -->
# File Research: sources/os/linux/linux/fs/orangefs/file.c

Implements OrangeFS regular file operations and the shared-memory direct I/O RPC helper.

Key behavior:
- `wait_for_direct_io()` allocates an operation, obtains a bufmap slot, copies write data into shared buffers, submits `ORANGEFS_VFS_OP_FILE_IO`, handles daemon restart retries, copies read data back to the iterator, and releases slot/op state.
- It uses uid `0` for I/O when VFS open mode already proved read/write access, preserving POSIX open-time permission semantics despite OrangeFS server-side per-I/O permission checks.
- `orangefs_revalidate_mapping()` serializes cache invalidation with a bitlock, writes back dirty pages, invalidates page cache, and refreshes a mapping timeout.
- Read and splice-read paths revalidate mapping under `i_rwsem` before using generic filemap reads.
- Write path revalidates mapping for writes beyond current size, then uses generic buffered write.
- `orangefs_fault()` refreshes file size before mmap faults; `orangefs_file_mmap_prepare()` revalidates mapping and installs vm ops.
- `orangefs_file_release()` flushes daemon readahead cache when enabled and page cache has pages.
- `orangefs_fsync()` writes back page cache, then sends `ORANGEFS_VFS_OP_FSYNC`.
- `orangefs_file_llseek()` refreshes size for `SEEK_END`.
- `orangefs_lock()` supports local-only POSIX locks when mounted with `local_lock`.
- `orangefs_flush()` writes back local page cache on close without sending server fsync.

Important exported table:
- `orangefs_file_operations` wires llseek/read/write/lock/mmap/open/splice/flush/release/fsync/setlease.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/inode.c -->
# File Research: sources/os/linux/linux/fs/orangefs/inode.c

Implements OrangeFS address-space operations, inode attribute operations, inode instantiation, and file attribute ioctls.

Key behavior:
- Writeback tracks dirty byte ranges per folio in `orangefs_write_range`, including uid/gid, so writeback can preserve credentials and coalesce adjacent ranges.
- `orangefs_writepages()` batches compatible dirty folios into one `wait_for_direct_io(WRITE)` transfer up to bufmap slot size.
- `orangefs_readahead()` may expand large readahead windows, reads through shared-memory direct I/O, and marks folios uptodate.
- `orangefs_read_folio()` reads one folio via direct I/O, zeros unread tail through the iterator, flushes dcache, and ends the folio read.
- `orangefs_write_begin()` attaches/extends private write ranges or launders incompatible dirty folios.
- `orangefs_write_end()` updates inode size, handles short-copy zeroing, marks dirty, and schedules inode metadata sync.
- `orangefs_invalidate_folio()` trims or drops private write ranges on invalidation; unsupported punched-middle cases warn.
- `orangefs_direct_IO()` chunks iterator I/O by bufmap size, updates offsets, access time, mtime, and inode size.
- `orangefs_page_mkwrite()` attaches full-page write ranges for mmap writes and marks folios dirty under pagefault accounting.
- `orangefs_setattr_size()` refreshes size, adjusts page cache/i_size, sends `ORANGEFS_VFS_OP_TRUNCATE`, and marks time attrs when size changes.
- `__orangefs_setattr()` rejects unsupported sticky/setuid cases, records pending attrs/credentials in private inode state, copies attrs locally, and marks inode dirty for later server setattr.
- `orangefs_getattr()` refreshes OrangeFS attrs and fills VFS stat data.
- `orangefs_permission()` refreshes attrs before generic permission checks.
- `orangefs_fileattr_get/set()` maps Linux file flags to `user.pvfs2.meta_hint` xattr with limited supported flags.
- `orangefs_iget()` uses `iget5_locked()` keyed by OrangeFS fsid/handle and fetches attrs for new inodes.
- `orangefs_new_inode()` creates new VFS inodes for server-created objects, applies inherited ACLs, initializes ops, and inserts into inode hash.

Important tables:
- `orangefs_address_operations` supplies readahead/read/write/invalidate/release/free/migrate/launder/direct-IO.
- File inode operations include ACL, setattr/getattr, xattr list, permission, time update, and fileattr get/set.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/namei.c -->
# File Research: sources/os/linux/linux/fs/orangefs/namei.c

Implements OrangeFS directory inode operations for namespace changes.

Key behavior:
- `orangefs_create()` sends `ORANGEFS_VFS_OP_CREATE`, creates a local inode from returned ref, instantiates the dentry, sets dentry timeout, and updates parent mtime/ctime.
- `orangefs_lookup()` sends `ORANGEFS_VFS_OP_LOOKUP`, returns `NULL` inode for `ENOENT`, otherwise uses `orangefs_iget()` and `d_splice_alias()`.
- `orangefs_unlink()` sends `ORANGEFS_VFS_OP_REMOVE`, drops inode link count, and updates parent times; also used for `rmdir`.
- `orangefs_symlink()` validates target length, sends `ORANGEFS_VFS_OP_SYMLINK`, creates a symlink inode, sets symlink size locally, and updates parent times.
- `orangefs_mkdir()` sends `ORANGEFS_VFS_OP_MKDIR`, creates a directory inode, instantiates dentry, and keeps directory nlink effectively constant due to multi-client consistency limits.
- `orangefs_rename()` rejects nonzero rename flags, updates destination parent times, sends `ORANGEFS_VFS_OP_RENAME`, and updates overwritten dentry ctime.

Important exported table:
- `orangefs_dir_inode_operations` wires lookup, ACLs, create, unlink, symlink, mkdir, rmdir, rename, setattr/getattr, xattr listing, permission, and update_time.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-bufmap.c -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-bufmap.c

Implements OrangeFS shared buffer mapping and slot allocation between kernel and userspace daemon.

Key behavior:
- `slot_map` tracks available descriptor slots with a bitmap, count, and waitqueue for both read/write slots and readdir slots.
- `get()` waits for free slots with `slot_timeout_secs`; `put()` clears bitmap bits and wakes waiters.
- `orangefs_bufmap_initialize()` validates daemon-provided mapping alignment and sizing, allocates metadata, pins userspace pages, groups them into folios, slices folios into descriptors, installs slot maps, and publishes `__orangefs_bufmap`.
- `orangefs_bufmap_map()` pins pages with `pin_user_pages_fast(FOLL_WRITE)`, flushes dcache, groups pages into folios, records per-descriptor folio arrays/offsets, and detects the optimized two-2MiB-folio case.
- `orangefs_bufmap_finalize()` marks maps as killed; `orangefs_bufmap_run_down()` waits for active users to drain, unpins pages, frees metadata, and clears the global map.
- `orangefs_bufmap_get/put()` manage data I/O slots; `orangefs_readdir_index_get/put()` manage readdir indices.
- `orangefs_bufmap_copy_from_iovec()` and `orangefs_bufmap_copy_to_iovec()` copy between kernel iterators and daemon shared buffers using `kmap_local_folio()`, with a fast path for two 2MiB folios per 4MiB slot.

Important invariants:
- Descriptor size must be page-size aligned and total size must equal `size * count`.
- Active slots must drain before pinned user pages are unmapped during daemon shutdown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-bufmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-bufmap.h -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-bufmap.h

Declares the OrangeFS bufmap API.

Exports initialization/finalization/run-down, slot size query, data slot get/put, readdir slot get/put, and iterator copy helpers used by file I/O, readdir, and the device ioctl path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-bufmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-cache.c -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-cache.c

Implements the OrangeFS operation slab cache and operation tag allocation.

Key behavior:
- `op_cache_initialize()` creates a usercopy-aware `orangefs_op_cache` for `orangefs_kernel_op_s` objects and initializes tag counter at `100`.
- `get_opname_string()` maps operation type constants to human-readable debug names.
- `orangefs_new_tag()` assigns monotonically increasing nonzero tags under a spinlock.
- `op_alloc()` allocates and initializes operation state, list head, lock, completion, invalid default up/down call types, unique tag, requested upcall type, attempts, and current fsuid/fsgid credentials.
- `op_release()` frees operations back to the slab cache.

Important role:
- Operations allocated here are the fundamental units queued to userspace and completed by downcalls.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-debug.h -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-debug.h

Defines OrangeFS debug mask bits used by gossip logging.

The file assigns one bit per subsystem (`super`, `inode`, `file`, `dir`, `utils`, `wait`, `acl`, `dcache`, `dev`, `name`, `bufmap`, `cache`, `debugfs`, `xattr`, `init`, `sysfs`) plus `none`, `all`, and max-mask constants. It is shared with kernel and non-kernel builds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-debugfs.c -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-debugfs.c

Implements OrangeFS debugfs controls under `/sys/kernel/debug/orangefs`.

Key behavior:
- Creates `debug-help`, `kernel-debug`, and later `client-debug` files.
- Maintains kernel keyword-to-mask mapping from `orangefs-debug.h`.
- Initially publishes help text with unknown client keywords; after userspace client reports its keyword/mask table, rebuilds help text and creates/updates `client-debug`.
- `orangefs_debug_read/write()` reads current debug strings and writes keyword lists. Kernel writes update `orangefs_gossip_debug_mask`; client writes send an `ORANGEFS_VFS_OP_PARAM` request to userspace.
- Converts masks to comma-separated keyword strings and keyword strings back to validated masks for kernel and client masks.
- Supports client debug mask/string updates through device ioctls: `orangefs_debugfs_new_client_mask()`, `orangefs_debugfs_new_client_string()`, and `orangefs_debugfs_new_debug()`.

Important synchronization:
- `orangefs_debug_lock` protects debug file backing strings.
- `orangefs_help_file_lock` protects debug-help contents.
- Module-load kernel debug mask can be preserved from being overwritten by client startup defaults.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-debugfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-debugfs.h -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-debugfs.h

Declares OrangeFS debugfs lifecycle and ioctl update helpers.

Functions cover init/cleanup, debug-help preparation, client mask/string ingestion, and generic debug mask update from userspace.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-debugfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-dev-proto.h -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-dev-proto.h

Defines OrangeFS kernel/userspace device protocol operation constants and shared protocol includes.

Contents:
- Operation type constants for file I/O, lookup, create, getattr, remove, mkdir, readdir, setattr, symlink, rename, statfs, truncate, readahead flush, mount/unmount, xattr ops, params, perf counters, cancel, fsync, fs key, readdirplus, and features.
- Feature bit `ORANGEFS_FEATURE_READAHEAD`.
- Debug string and max readdir-entry constants.
- Includes `upcall.h` and `downcall.h`, making it the central protocol ABI include.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-dev-proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-kernel.h -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-kernel.h

Central private OrangeFS kernel header defining structures, globals, helpers, and cross-file prototypes.

Key contents:
- Constants for default op/slot timeouts, device name, protocol magic, purge retry count, and max up/down device request sizes.
- `orangefs_vfs_op_states` and helpers/macros for waiting, in-progress, serviced, purged, given-up, and cancel states.
- `orangefs_kernel_op_s`, the queued RPC object containing tag, shared-memory slot state, upcall/downcall payloads, completion, lock, attempts, and list node.
- `orangefs_inode_s`, per-inode private state containing OrangeFS object ref, symlink target, xattr semaphore/cache, VFS inode, getattr/mapping timeouts, pending attr credentials, and bitlock.
- `orangefs_sb_info_s`, per-superblock private state containing root handle, fsid, mount id, mount flags, device name, pending state, and list linkage.
- Stats, cached xattr, and write-range structures.
- `ORANGEFS_I()` and `ORANGEFS_SB()` accessors.
- Khandle-to-inode hash conversion, root-handle check, and handle matching helpers.
- Prototypes for op cache, inode cache, module purge, waitqueue purge, superblock, inode, device, file, utility, xattr, and service-operation APIs.
- Operation flags for interruptible, priority, cancellation, no-mutex, async, and writeback operation modes.
- `fill_default_sys_attrs()` for create/mkdir/symlink requests and `orangefs_set_timeout()` for dentry expiration.

Important role:
- This header defines the local contract between OrangeFS VFS glue, request scheduling, userspace bridge, inode/page-cache code, and sysfs/debugfs controls.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-mod.c -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-mod.c

Implements OrangeFS module initialization, teardown, globals, and in-progress operation purge.

Key behavior:
- Defines global stats, hash table size, debug mask, timeout tunables, request mutex, in-progress hash table, request list, locks, and waitqueue.
- Registers filesystem type `pvfs2` with `orangefs_init_fs_context()` and `orangefs_kill_sb()`.
- Module init clamps negative timeouts, initializes operation and inode caches, allocates in-progress hash buckets, initializes fsid key table, prepares debugfs help, initializes debugfs/sysfs/device subsystem, and registers the filesystem.
- Cleanup unregisters filesystem, removes debugfs/sysfs, finalizes fsid/device/caches, asserts request/in-progress lists are empty, and frees hash table.
- `purge_inprogress_ops()` walks all hash buckets and marks each in-progress op purged, completing waiters.

Important dependencies:
- Init order matters because sysfs/debugfs/device and VFS operations rely on operation caches and global queues.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-mod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-sysfs.c -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-sysfs.c

Implements OrangeFS sysfs ABI under `/sys/fs/orangefs`.

Key behavior:
- Provides local integer tunables for `op_timeout_secs`, `slot_timeout_secs`, `cache_timeout_msecs`, `dcache_timeout_msecs`, and `getattr_timeout_msecs`.
- Exposes local stats `reads` and `writes`.
- Uses service operations to get/set daemon-side parameters: performance history/time/reset, readahead count/size/count_size/readcnt, and cache hard/soft/reclaim/timeout settings for acache, capcache, ccache, and ncache.
- Exposes performance counter reads under `perf_counters` by issuing `ORANGEFS_VFS_OP_PERF_COUNT`.
- Blocks writes to `perf_counters` and `stats`.
- Rejects readahead sysfs operations when `ORANGEFS_FEATURE_READAHEAD` is not negotiated.
- Validates user input ranges before sending parameter set operations.
- Creates kobjects for `/sys/fs/orangefs`, `acache`, `capcache`, `ccache`, `ncache`, `perf_counters`, and `stats`, with cleanup through `kobject_put()`.

Notable details:
- All sysfs attributes route through a shared `orangefs_attribute` wrapper and dispatch to integer or service-operation show/store handlers.
- Many daemon-backed reads/writes fail if the userspace client is not in service.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-sysfs.h -->
# File Research: sources/os/linux/linux/fs/orangefs/orangefs-sysfs.h

Declares OrangeFS sysfs lifecycle functions:

`orangefs_sysfs_init()` creates the sysfs hierarchy, and `orangefs_sysfs_exit()` releases it during module teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/orangefs/orangefs-sysfs.h -->