# Group Research: group_1061_linux_stable_sources_os_linux_linux_stable_fs_open_c_sources_os_lin_484ae60d5231

Scope: subset A from `Docs/research_subset_a.md`, covering the listed Linux stable VFS, OpenPROMFS, and OrangeFS files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/open.c -->
# File Research: sources/os/linux/linux-stable/fs/open.c

## Scope

This file implements core Linux VFS open-adjacent syscalls and helpers: `truncate`, `ftruncate`, `fallocate`, `access`, `chdir`, `chroot`, chmod/chown variants, file open construction, kernel open helpers, `open/openat/openat2/creat`, close flushing, and generic nonseekable/stream open helpers.

## Public And Internal APIs Covered

- Size and space APIs: `do_truncate()`, `vfs_truncate()`, `ksys_truncate()`, `do_ftruncate()`, `vfs_fallocate()`, `ksys_fallocate()`.
- Permission and cwd/root APIs: `do_faccessat()`, `access_override_creds()`, `chdir`, `fchdir`, `chroot`.
- Metadata APIs: `chmod_common()`, `vfs_fchmod()`, `do_fchmodat()`, `chown_common()`, `do_fchownat()`, `vfs_fchown()`.
- Open pipeline: `do_dentry_open()`, `finish_open()`, `finish_no_open()`, `vfs_open()`, `dentry_open()`, `dentry_open_nonotify()`, `kernel_file_open()`.
- Open argument handling: `build_open_how()`, `build_open_flags()`, `file_open_name()`, `filp_open()`, `file_open_root()`, `do_sys_openat2()`, `do_sys_open()`.
- Close and generic file helpers: `filp_flush()`, `filp_close()`, `close`, `vhangup`, `generic_file_open()`, `nonseekable_open()`, `stream_open()`.

## Control Flow And Behavior

- Truncation validates object type, write permission, append/lease/security/fsnotify state, write access, and mount write state before calling `notify_change()` under the inode lock.
- `fallocate` validates mutually exclusive mode bits, writable file mode, immutable/append/swapfile restrictions, overflow against `s_maxbytes`, LSM/fsnotify permissions, and delegates to `file->f_op->fallocate`.
- `access` optionally overrides subjective credentials to real uid/gid and adjusted capabilities, does path lookup, checks noexec for regular executable checks, calls `inode_permission()`, and reports read-only filesystems for write probes.
- chmod/chown operations handle idmapped mounts, delegation retry, LSM checks, privilege stripping, and `notify_change()`.
- `do_dentry_open()` sets file path, inode, mapping, write/read accounting, `f_op`, LSM and fsnotify open permissions, lease breaking, mode capabilities, readahead state, O_DIRECT support, and huge-page-cache invalidation for writers.
- `build_open_flags()` normalizes open flags, rejects invalid `openat2` resolve combinations, handles `O_PATH`, `O_TMPFILE`, `O_SYNC`, create/exclusive intent, lookup flags, and `RESOLVE_*` flags.
- `close` removes the fd before flushing, converts restart-style errors to `-EINTR`, and performs synchronous final `fput` on syscall return.

## State, Dependencies, And Invariants

- Depends on VFS path lookup, idmapped mounts, inode locking, LSM hooks, fsnotify, leases, file descriptor allocation, audit, mount write counts, and file operation tables.
- Write-access accounting balances inode, primary mount, and backing-file mount access for `FMODE_BACKING`.
- `O_PATH` files bypass normal open work and receive empty file operations plus `FMODE_PATH`.
- Open error paths must release fops, path references, write access, and reset embedded file path/inode fields exactly once.
- `openat2` performs stricter argument validation than legacy open syscalls; legacy paths pre-mask flags through `build_open_how()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/open.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/openpromfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/openpromfs/Makefile

## Scope

This Makefile builds the Sun OpenPROM filesystem support.

## Build Behavior

- Adds `openpromfs.o` when `CONFIG_SUN_OPENPROMFS` is enabled.
- Composes `openpromfs.o` from `inode.o`.

## Dependencies And Invariants

- The filesystem implementation is single-source in this directory.
- Build is gated entirely by the architecture/config option for OpenPROMFS support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/openpromfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/openpromfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/openpromfs/inode.c

## Scope

This file implements `openpromfs`, a single-instance pseudo filesystem exposing OpenPROM device-tree nodes as directories and properties as files.

## Public And Internal APIs Covered

- Inode private state: `struct op_inode_info` records whether an inode is a device node or property and stores the corresponding pointer.
- Property display: `is_string()`, `property_show()`, seq-file operations, `property_open()`, and `openpromfs_prop_ops`.
- Directory support: `openpromfs_lookup()`, `openpromfs_readdir()`, `openprom_operations`, `openprom_inode_operations`.
- Superblock and mount support: `openprom_alloc_inode()`, `openprom_free_inode()`, `openprom_iget()`, `openprom_fill_super()`, fs context operations, `openprom_fs_type`.
- Module lifecycle: slab cache creation/destruction and filesystem registration/unregistration.

## Control Flow And Behavior

- Lookup scans child OpenFirmware nodes first, then properties, matching dentry names to node basenames or property names under `op_mutex`.
- New node inodes become read/execute directories with lookup/readdir operations; property inodes become regular files using seq-file read operations.
- `security-password` under the `options` node is restricted to owner read/write while other properties are world-readable.
- Readdir emits `.` and `..`, then all child nodes as directories, then all properties as regular files, using OpenPROM unique IDs as inode numbers.
- Property reads render printable string lists separated by ` + `, otherwise render bytes or 32-bit words as hexadecimal text.
- `openprom_fill_super()` creates the root inode for `/`, sets `SB_NOATIME`, block size, magic, operations, and anonymous root dentry.

## State, Dependencies, And Invariants

- Protects OpenPROM traversal with global `op_mutex`.
- Depends on SPARC/OpenPROM interfaces: `struct device_node`, `struct property`, `of_find_node_by_path()`, `of_node_name_eq()`, and OpenPROM unique IDs.
- Root inode number is fixed at `OPENPROM_ROOT_INO`.
- Inode cache lifetime is protected with `rcu_barrier()` before slab destruction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/openpromfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/Kconfig

## Scope

This Kconfig entry exposes OrangeFS client filesystem support.

## Configuration Behavior

- Defines `ORANGEFS_FS` as a tristate option labeled `ORANGEFS (Powered by PVFS) support`.
- Selects `FS_POSIX_ACL`.

## Dependencies And Role

- The help text identifies OrangeFS as a parallel filesystem for high-end computing systems.
- POSIX ACL support is always selected when the filesystem is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/Makefile

## Scope

This Makefile builds the OrangeFS kernel client module.

## Build Behavior

- Adds `orangefs.o` when `CONFIG_ORANGEFS_FS` is enabled.
- Links `orangefs.o` from ACL, file, cache, utils, xattr, dcache, inode, sysfs, module, superblock, request-device, namei, symlink, directory, buffer-map, debugfs, and waitqueue objects.

## Dependencies And Role

- Captures OrangeFS as one VFS module with both filesystem entry points and the `/dev/pvfs2-req` daemon bridge.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/acl.c

## Scope

This file implements POSIX ACL get/set support for OrangeFS through extended attributes.

## APIs Covered

- `orangefs_get_acl()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`, retrieves the xattr, and converts it with `posix_acl_from_xattr()`.
- `__orangefs_set_acl()` converts an ACL to xattr form and writes/removes it with `orangefs_inode_setxattr()`.
- `orangefs_set_acl()` updates file mode when an access ACL can be represented in mode bits and then applies ACL storage.

## Control Flow And Behavior

- RCU ACL lookup is unsupported and returns `-ECHILD`.
- Missing ACL xattrs and server `-ENOSYS` are treated as no ACL.
- `NULL` ACL values translate to zero-length xattr writes, effectively remove operations.
- On successful set, the VFS ACL cache is updated with `set_cached_acl()`.
- Mode changes caused by ACL updates are propagated back through `__orangefs_setattr_mode()`.

## Risks And Invariants

- Allocates maximum xattr value length rather than probing, avoiding an extra network round trip.
- Uses `init_user_ns` for xattr ACL encoding/decoding.
- Invalid ACL type is rejected with `-EINVAL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/dcache.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/dcache.c

## Scope

This file implements OrangeFS dentry revalidation.

## APIs Covered

- `orangefs_revalidate_lookup()` reissues a no-follow lookup to validate positive and negative dentries.
- `orangefs_d_revalidate()` checks dentry timeout, handles RCU constraints, validates root dentries, and refreshes inode state.
- Exports `orangefs_dentry_operations` with `.d_revalidate`.

## Control Flow And Behavior

- Dentries are trusted until their `d_fsdata` timeout expires.
- RCU pathwalk revalidation returns `-ECHILD` after timeout.
- Positive dentries are dropped if lookup fails or returns a different handle.
- Negative dentries are kept only if lookup still returns `-ENOENT`.
- Positive dentries that pass lookup are further checked with `orangefs_inode_check_changed()`.

## Risks And Invariants

- Root handle dentries bypass network revalidation.
- Revalidation depends on OrangeFS object handles, not inode numbers, for identity.
- Timeout refresh is centralized through `orangefs_set_timeout()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/dcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/devorangefs-req.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/devorangefs-req.c

## Scope

This file implements the `/dev/pvfs2-req` character device that connects kernel VFS operations to the OrangeFS userspace client daemon.

## APIs Covered

- Device file operations: `orangefs_devreq_open()`, `orangefs_devreq_read()`, `orangefs_devreq_write_iter()`, `orangefs_devreq_release()`, ioctl, compat ioctl, and poll.
- Operation tracking: in-progress hash add/remove by operation tag.
- Daemon state: `is_daemon_in_service()`, `__is_daemon_in_service()`, single-open enforcement, userspace protocol version tracking.
- Ioctls: magic/size queries, shared buffer map installation, remount-all, upstream-kmod marker, and debugfs client/kernel mask updates.
- Device lifecycle: `orangefs_dev_init()` and `orangefs_dev_cleanup()`.

## Control Flow And Behavior

- The device can be opened only once, only from `init_user_ns`, and only with `O_NONBLOCK`.
- Reads copy protocol version, magic, tag, and upcall to userspace, then mark the op in progress and insert it into the in-progress hash.
- Reads skip operations for filesystems pending remount or unknown filesystems except mount/getattr/unmount cases.
- Writes parse header and downcall, validate protocol version and magic, remove the matching op by tag, optionally copy a READDIR trailer, and complete the waiting operation.
- Device release finalizes bufmap state, marks mounted filesystems pending remount, purges waiting and in-progress ops, runs down shared-memory slots, and clears daemon version state.
- `ORANGEFS_DEV_REMOUNT_ALL` serializes with `orangefs_request_mutex` and remounts tracked superblocks while carefully dropping the superblock spinlock around blocking work.

## State, Dependencies, And Invariants

- Uses global request list, in-progress hash table, wait queue, and per-op spinlocks.
- Shared-memory buffer map setup is delegated to `orangefs_bufmap_initialize()`.
- READDIR is the only operation allowed to carry a downcall trailer.
- Cancel and given-up operations require special completion/release handling.
- Protocol header sizes and magic must match userspace client expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/devorangefs-req.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/dir.c

## Scope

This file implements OrangeFS directory file operations and client readdir response parsing.

## APIs Covered

- Readdir transport: `do_readdir()`, `orangefs_dir_more()`.
- Trailer parsing and buffering: `parse_readdir()`, `fill_from_part()`, `orangefs_dir_fill()`.
- File operations: `orangefs_dir_llseek()`, `orangefs_dir_iterate()`, `orangefs_dir_open()`, `orangefs_dir_release()`, and `orangefs_dir_operations`.

## Control Flow And Behavior

- Directory stream state is stored per open file in `struct orangefs_dir`, with server token, linked response parts, end position, and sticky error.
- Part zero is synthesized for `.` and `..`; server data begins at part one.
- `ctx->pos` encodes part number in high bits and byte offset within a part in low bits.
- `do_readdir()` acquires a readdir slot, posts a READDIR op, retries if purged with `-EAGAIN`, and stores the returned continuation token.
- Server trailers start with `struct orangefs_readdir_response_s`; entry records contain name length, name, zero byte, padding, and object handle.
- Seek to an earlier offset with `SEEK_SET` discards cached parts so subsequent iteration can observe fresh directory state.

## Risks And Invariants

- Corrupt trailer layout or invalid userspace offsets are reported as `-EIO`.
- Trailer size must fit within `PART_SIZE`.
- Readdir slot accounting must balance `orangefs_readdir_index_get()` and `_put()`.
- Cached directory parts are `vfree()`d on release or reset.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/downcall.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/downcall.h

## Scope

This header defines kernel-visible OrangeFS downcall response structures returned by the userspace client daemon.

## APIs And Structures

- Defines per-operation responses for I/O, lookup, create, symlink, getattr, mkdir, statfs, mount, xattr, params, perf counters, fs keys, and feature negotiation.
- `struct orangefs_downcall_s` contains type, status, optional trailer metadata, and a union of operation responses.
- `struct orangefs_readdir_response_s` describes the header stored in READDIR trailers.

## Dependencies And Role

- Included through `orangefs-dev-proto.h` together with upcall definitions.
- Layout is shared across kernel/userspace protocol boundaries and uses fixed-width integer types plus explicit padding.

## Risks And Invariants

- Trailer buffers are currently used only for READDIR.
- Fixed buffer sizes such as `PERF_COUNT_BUF_SIZE` and `FS_KEY_BUF_SIZE` define userspace-visible ABI limits.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/downcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/file.c

## Scope

This file implements OrangeFS regular file operations, direct I/O transport through shared buffers, page-cache revalidation, mmap fault handling, fsync, llseek, local locks, and close flushing.

## APIs Covered

- Daemon I/O bridge: `wait_for_direct_io()`.
- Cache management: `flush_racache()`, `orangefs_revalidate_mapping()`.
- VFS file ops: read iter, splice read, write iter, mmap prepare, release, fsync, llseek, lock, flush, and `orangefs_file_operations`.

## Control Flow And Behavior

- `wait_for_direct_io()` allocates a FILE_IO op, obtains a shared-memory buffer slot, copies write data into the slot, posts the op, handles daemon restart retry with new slot/data recopy, and copies read data back to the iterator.
- OrangeFS lacks server-side open state, so kernel open mode is translated by setting upcall uid to root for permitted read/write operations to preserve POSIX open-time permission semantics.
- Read and splice paths take `i_rwsem` for read, revalidate mapping timeout, then use generic file/page-cache helpers.
- Writes beyond current size revalidate mapping before `generic_file_write_iter()`.
- mmap faults refresh file size before delegating to `filemap_fault()`.
- mmap prepare revalidates mapping, marks VMA sequential, clears random hint, sets vm ops, and records file access.
- `fsync` first writes back page cache, then sends an OrangeFS FSYNC op.
- `llseek(SEEK_END)` refreshes size before generic seek.
- Optional local locking uses VFS POSIX lock helpers only when mounted with `ORANGEFS_OPT_LOCAL_LOCK`.

## Risks And Invariants

- Shared buffer slots must be returned on every path.
- On interrupt, write semantics avoid returning `-EINTR` after data may have been written; partial write behavior depends on operation state.
- Mapping revalidation uses a bitlock to serialize invalidation, writeback, and page-cache invalidation.
- Close flush writes back local page cache but intentionally does not send server fsync.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/inode.c

## Scope

This file implements OrangeFS inode and address-space operations: buffered read/write, readahead, writeback batching, mmap page dirtying, direct I/O, setattr/getattr/permission/time/fileattr operations, inode lookup, and new inode creation.

## APIs Covered

- Address-space ops: `orangefs_readahead()`, `orangefs_read_folio()`, `orangefs_write_begin()`, `orangefs_write_end()`, `orangefs_writepages()`, invalidate/release/free/launder folio, `orangefs_direct_IO()`.
- mmap dirtying: `orangefs_page_mkwrite()`.
- Metadata: `orangefs_setattr()`, `__orangefs_setattr()`, `orangefs_setattr_size()`, `orangefs_getattr()`, `orangefs_permission()`, `orangefs_update_time()`.
- File attributes: `orangefs_fileattr_get()`, `orangefs_fileattr_set()`.
- Inode lifecycle: `orangefs_init_iops()`, `orangefs_iget()`, `orangefs_new_inode()`.

## Control Flow And Behavior

- Dirty folios carry `struct orangefs_write_range` private data recording byte range and credentials; writeback uses those ranges rather than blindly writing whole pages.
- `orangefs_writepages()` batches contiguous dirty ranges with matching uid/gid up to bufmap size, then sends them through `wait_for_direct_io()`.
- Readahead may expand large reads and transfers data in chunks up to 4 MiB through daemon shared buffers.
- `read_folio` launders dirty folios first, reads from daemon, zeroes unread portions, flushes dcache, and completes the folio.
- `write_begin` extends or replaces folio private write ranges, laundering if dirty state is incompatible.
- `write_end` updates `i_size`, zeroes short-copy stale ranges, marks dirty, unlocks/releases folio, and marks inode dirty.
- `page_mkwrite` attaches or updates a full-page write range, updates timestamps, marks dirty before returning a locked folio.
- Truncate refreshes size, adjusts page cache and `i_size`, sends TRUNCATE op, and updates ctime/mtime validity when size changed.
- `__orangefs_setattr()` rejects unsupported sticky/setuid cases, accumulates attribute updates with credential ownership, updates inode fields, and marks inode dirty.
- `orangefs_iget()` uses `iget5_locked()` keyed by OrangeFS fsid/handle; new inodes fetch attributes before installing operations.
- `orangefs_new_inode()` creates ACLs, fetches attributes, installs operations, writes default/access ACLs, inserts inode into hash, and reconciles mode.

## Risks And Invariants

- Folio private write ranges and credentials must stay consistent across invalidation, laundering, mmap writes, and batched writeback.
- Mapping invalidation is coordinated with `orangefs_revalidate_mapping()` bitlock.
- Fileattr flags are stored in `user.pvfs2.meta_hint`; only immutable, append, noatime, and internal mirror bit handling are allowed.
- Inode identity uses full OrangeFS handles for equality; inode number is a hash of the handle and can collide.
- Attribute writeback may force `write_inode_now()` when current credentials differ from accumulated attr credentials.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/namei.c

## Scope

This file implements OrangeFS directory inode namespace operations: create, lookup, unlink/rmdir, symlink, mkdir, and rename.

## APIs Covered

- VFS methods: `orangefs_create()`, `orangefs_lookup()`, `orangefs_unlink()`, `orangefs_symlink()`, `orangefs_mkdir()`, `orangefs_rename()`.
- Exports `orangefs_dir_inode_operations`.

## Control Flow And Behavior

- Create/mkdir/symlink allocate an OrangeFS op, fill parent ref and default sys attributes, copy names/targets, service the op, then instantiate a new VFS inode from the returned object reference.
- Lookup always issues a server lookup, including create-intent paths, so existing objects are not bypassed incorrectly.
- Successful lookups set dentry timeout and use `orangefs_iget()`; `-ENOENT` creates a negative dentry.
- Unlink and rmdir share REMOVE, drop target link count on success, and update parent mtime/ctime.
- Symlink validates target length, creates symlink object, then fixes `i_size` locally because symlink size cannot later be refreshed by getattr.
- Mkdir keeps directory link counts effectively constant because cross-client directory nlink consistency is not available.
- Rename rejects all nonzero rename flags, updates new parent time, sends RENAME, and updates overwritten target ctime if present.

## Risks And Invariants

- Names are bounded by `ORANGEFS_NAME_MAX - 1`.
- Parent timestamps are explicitly updated with `__orangefs_setattr()`.
- New dentries receive OrangeFS dcache timeouts for later revalidation.
- No advanced rename flags are supported.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-bufmap.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-bufmap.c

## Scope

This file implements the shared-memory buffer map used for OrangeFS kernel/userspace data transfer and separate slot allocation for I/O and readdir.

## APIs Covered

- Slot map internals: install, kill, run down, get, put, wait for free.
- Bufmap lifecycle: `orangefs_bufmap_initialize()`, `orangefs_bufmap_finalize()`, `orangefs_bufmap_run_down()`.
- Slot APIs: `orangefs_bufmap_size_query()`, `orangefs_bufmap_get()`, `orangefs_bufmap_put()`, `orangefs_readdir_index_get()`, `orangefs_readdir_index_put()`.
- Copy APIs: `orangefs_bufmap_copy_from_iovec()`, `orangefs_bufmap_copy_to_iovec()`.

## Control Flow And Behavior

- Userspace supplies a page-aligned mapping descriptor; the kernel pins all pages with `pin_user_pages_fast(FOLL_WRITE)`.
- Pinned pages are grouped into folios, then split into descriptor records with per-descriptor folio arrays and offsets.
- Descriptor slots are tracked with bitmaps and wait queues; waiters can time out or be interrupted.
- Finalize marks slot maps as dying; run-down waits until all slots are returned, clears the global bufmap, unpins pages, and frees metadata.
- Data copies map folios locally, copy from/to iterators, and validate complete copies.
- A fast path handles the common case of a descriptor backed by exactly two 2 MiB folios for up to 4 MiB transfers.

## Risks And Invariants

- User descriptors must be page-aligned, internally size-consistent, and page-size divisible.
- All pinned pages must be unpinned on partial initialization failures and final teardown.
- Slot counter state uses negative values to represent uninstalled or dying maps.
- I/O and readdir use separate slot maps backed by different bitmaps.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-bufmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-bufmap.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-bufmap.h

## Scope

This header declares the OrangeFS shared buffer-map interface.

## APIs Declared

- Bufmap lifecycle and sizing: `orangefs_bufmap_size_query()`, `orangefs_bufmap_initialize()`, `orangefs_bufmap_finalize()`, `orangefs_bufmap_run_down()`.
- Slot allocation: `orangefs_bufmap_get()`, `orangefs_bufmap_put()`, `orangefs_readdir_index_get()`, `orangefs_readdir_index_put()`.
- Data movement: `orangefs_bufmap_copy_from_iovec()`, `orangefs_bufmap_copy_to_iovec()`.

## Dependencies And Role

- Consumed by file I/O, readdir, and request-device code.
- Uses `struct ORANGEFS_dev_map_desc` from the OrangeFS device protocol headers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-bufmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-cache.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-cache.c

## Scope

This file implements the slab cache and tag allocation for OrangeFS kernel operations.

## APIs Covered

- Cache lifecycle: `op_cache_initialize()`, `op_cache_finalize()`.
- Operation allocation: `op_alloc()`, `op_release()`.
- Tag assignment: `orangefs_new_tag()`.
- Debug naming: `get_opname_string()`.

## Control Flow And Behavior

- The operation cache is created with a usercopy-safe region spanning tag through upcall data.
- Tags start at 100, increment under spinlock, and wrap from zero back to 100.
- `op_alloc()` zeroes the operation, initializes list/lock/completion, sets invalid initial upcall/downcall types, assigns tag/type, and captures current fsuid/fsgid into the upcall.
- `get_opname_string()` maps all known VFS op codes to stable debug strings.

## Risks And Invariants

- Operation objects are protocol objects copied to/from userspace, so cache usercopy bounds are part of the security contract.
- Tags identify downcalls; reuse is only safe after previous op lifetime ends.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-debug.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-debug.h

## Scope

This header defines OrangeFS kernel debug mask constants.

## APIs And Constants

- Defines `GOSSIP_NO_DEBUG` and subsystem masks for super, inode, file, dir, utils, wait, ACL, dcache, dev, name, bufmap, cache, debugfs, xattr, init, and sysfs.
- Defines `GOSSIP_MAX_NR` and `GOSSIP_MAX_DEBUG`.

## Dependencies And Role

- Kernel builds include Linux types; userspace-compatible inclusion falls back to standard integer types and `ARRAY_SIZE`.
- Masks are consumed by debug logging and debugfs keyword conversion.

## Risks And Invariants

- Mask values must remain collision-free because debugfs maps keywords to bits.
- `GOSSIP_MAX_DEBUG` assumes all active masks fit below `GOSSIP_MAX_NR`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-debugfs.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-debugfs.c

## Scope

This file implements OrangeFS debugfs support for kernel/client debug keyword help and runtime debug mask updates.

## APIs Covered

- Lifecycle: `orangefs_debugfs_init()`, `orangefs_debugfs_cleanup()`, `orangefs_prepare_debugfs_help_string()`.
- Debugfs file operations for `debug-help`, `kernel-debug`, and `client-debug`.
- Keyword conversion: mask-to-string and string-to-mask helpers for kernel and client masks.
- Device ioctl receivers: `orangefs_debugfs_new_client_mask()`, `orangefs_debugfs_new_client_string()`, `orangefs_debugfs_new_debug()`.

## Control Flow And Behavior

- Module init builds a debug-help string with known kernel keywords and placeholder client text, then creates `/sys/kernel/debug/orangefs`.
- Kernel debug mask is initialized from module parameter, normalized through keyword conversion, and protected from being overwritten by a zero client-provided mask if set at module load.
- Client keyword/mask data is learned later through device ioctls; the help string and `client-debug` file are rebuilt after the first client metadata arrives.
- Writes to `kernel-debug` parse keyword lists directly into `orangefs_gossip_debug_mask`.
- Writes to `client-debug` require the daemon to be running, convert keywords to two-mask client representation, and send an OrangeFS PARAM op to userspace.
- Special keywords `all` and `verbose` are treated as aggregate masks.

## Risks And Invariants

- `orangefs_debug_lock` protects debug string file data; `orangefs_help_file_lock` protects help string reads/rebuilds.
- Client keyword arrays are dynamically allocated from newline-delimited client metadata and reused for string/mask conversion.
- User-provided debug strings are length-capped and trimmed before parsing.
- Debugfs removal is recursive and frees the help string.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-debugfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-debugfs.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-debugfs.h

## Scope

This header declares OrangeFS debugfs entry points.

## APIs Declared

- `orangefs_debugfs_init()`, `orangefs_debugfs_cleanup()`.
- `orangefs_prepare_debugfs_help_string()`.
- Device ioctl hooks for client mask, client string, and debug mask updates.

## Dependencies And Role

- Used by module init and `/dev/pvfs2-req` ioctl dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-debugfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-dev-proto.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-dev-proto.h

## Scope

This header defines operation codes and constants shared by the OrangeFS kernel module and userspace client device protocol.

## APIs And Constants

- Defines `ORANGEFS_VFS_OP_*` operation types for file I/O, lookup, create, getattr, remove, mkdir, readdir, setattr, symlink, rename, statfs, truncate, mount/unmount, xattrs, params, perf counts, cancel, fsync, fskey, readdirplus, and features.
- Defines `ORANGEFS_FEATURE_READAHEAD`.
- Defines `ORANGEFS_MAX_DEBUG_STRING_LEN` and `ORANGEFS_MAX_DIRENT_COUNT_READDIR`.
- Includes both upcall and downcall protocol headers.

## Risks And Invariants

- Constants are userspace ABI and must stay 32/64-bit clean.
- Comments require miscellaneous constants to remain multiples of 8 for mixed-width compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-dev-proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-kernel.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-kernel.h

## Scope

This central OrangeFS kernel header declares subsystem data structures, global state, operation-state helpers, VFS operation exports, mount/device/cache interfaces, and utility macros.

## APIs And Structures

- Defines operation states and `struct orangefs_kernel_op_s` with tag, shared-memory slot state, upcall/downcall, completion, lock, attempts, and list node.
- Defines `struct orangefs_inode_s`, `struct orangefs_sb_info_s`, stats, cached xattr records, and write-range metadata.
- Provides `ORANGEFS_I()`, `ORANGEFS_SB()`, `orangefs_khandle_to_ino()`, root/handle match helpers, and `orangefs_set_timeout()`.
- Declares op cache, inode cache, waitqueue, superblock, file, inode, xattr, device, debug, and sysfs interfaces.
- Defines service operation flags and `get_interruptible_flag()`.

## Control Flow And Behavior

- `set_op_state_serviced()` marks an op serviced and completes its wait queue.
- `set_op_state_purged()` handles normal purged ops by completing waiters, while cancel ops are removed and released specially.
- `put_cancel()` frees a cancel op’s buffer slot and releases the op.
- `fill_default_sys_attrs()` fills owner/group/perms/time/mask for create-style upcalls from current fs credentials.

## Risks And Invariants

- Operation state bits coordinate request queue, in-progress hash, daemon restarts, cancellation, and waiting VFS callers.
- OrangeFS inode identity is fsid plus 128-bit handle; inode number is only a derived hash.
- `d_fsdata` stores dcache timeout as a cast jiffies value.
- Many globals are shared across files and require the documented spinlocks/mutexes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-mod.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-mod.c

## Scope

This file implements OrangeFS module lifecycle, module parameters, global request queues, filesystem registration, and in-progress operation purge.

## APIs Covered

- Module init/exit: `orangefs_init()`, `orangefs_exit()`.
- Global operation state: request mutex, in-progress hash table, request list, request-list lock, and request-list wait queue.
- `purge_inprogress_ops()`.

## Control Flow And Behavior

- Init normalizes negative timeouts, creates operation and inode caches, allocates in-progress hash buckets, initializes fsid key table, prepares debugfs help, initializes debugfs/sysfs/device layers, and registers filesystem type `pvfs2`.
- Error paths unwind in reverse order.
- Exit unregisters filesystem, removes debugfs/sysfs, finalizes fsid/device/cache state, asserts request and in-progress lists are empty, and frees hash storage.
- `purge_inprogress_ops()` walks all hash buckets and marks each operation purged so waiters can retry or fail after daemon shutdown.

## State And Dependencies

- Module parameters include hash table size, debug mask, operation timeout, and slot timeout.
- Global cache and dcache/getattr timeout defaults are exported for sysfs.
- Filesystem type uses `orangefs_init_fs_context()`, `orangefs_fs_param_spec`, and `orangefs_kill_sb()` from superblock code.

## Risks And Invariants

- Request structures must be empty on unload.
- Hash table size controls tag lookup distribution for downcalls.
- Device initialization must occur before normal mounted operation can be serviced.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-mod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-sysfs.c

## Scope

This file implements OrangeFS sysfs controls and counters under `/sys/fs/orangefs`.

## APIs Covered

- Attribute dispatch: `orangefs_attr_show()`, `orangefs_attr_store()`, `orangefs_sysfs_ops`.
- Local integer attributes: `sysfs_int_show()`, `sysfs_int_store()`.
- Daemon-backed attributes: `sysfs_service_op_show()`, `sysfs_service_op_store()`.
- Kobject lifecycle: `orangefs_sysfs_init()`, `orangefs_sysfs_exit()`.

## Control Flow And Behavior

- Top-level integer attributes expose and update kernel-side `op_timeout_secs`, `slot_timeout_secs`, cache timeout, dcache timeout, and getattr timeout.
- Stats kobject exposes kernel read/write counters as read-only values.
- Most cache, readahead, perf, and perf-counter attributes are implemented by sending PARAM or PERF_COUNT service operations to the userspace daemon.
- Readahead sysfs operations are rejected when `ORANGEFS_FEATURE_READAHEAD` is not negotiated.
- Store paths validate numeric ranges before posting PARAM requests; two-value `readahead_count_size` is parsed specially.
- `orangefs_sysfs_init()` creates the root `orangefs` kobject plus `acache`, `capcache`, `ccache`, `ncache`, `perf_counters`, and `stats` children with default attribute groups.

## State, Dependencies, And Invariants

- `pc` and `stats` kobjects reject stores.
- Daemon-backed attributes require `is_daemon_in_service()` to succeed.
- Kobject error paths unwind with `kobject_put()` for already-created objects.
- Release callbacks free each allocated kobject and clear its global pointer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-sysfs.h -->
# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-sysfs.h

## Scope

This header declares the OrangeFS sysfs lifecycle interface.

## APIs Declared

- `orangefs_sysfs_init()`.
- `orangefs_sysfs_exit()`.

## Dependencies And Role

- Included by module lifecycle code to create and remove `/sys/fs/orangefs` entries.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/orangefs/orangefs-sysfs.h -->