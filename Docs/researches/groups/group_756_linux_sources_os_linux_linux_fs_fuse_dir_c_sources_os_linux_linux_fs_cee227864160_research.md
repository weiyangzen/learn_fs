# Group Research: group_756_linux_sources_os_linux_linux_fs_fuse_dir_c_sources_os_linux_linux_fs_cee227864160

Scope: `Docs/research_subset_a.md`  
Files read completely: 6 files, 10,025 total lines.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/dir.c -->
# File Research: sources/os/linux/linux/fs/fuse/dir.c

Purpose: Implements FUSE VFS directory, dentry, symlink, permission, lookup, creation, removal, rename, getattr/statx, setattr, and directory file operations.

Key responsibilities:
- Maintains FUSE dentry timeout state through `struct fuse_dentry`, per-bucket rbtree tracking, `inval_wq`, and `fuse_dentry_tree_work()`.
- Implements dentry operations: `fuse_dentry_revalidate()`, `fuse_dentry_delete()`, `fuse_dentry_init()`, `fuse_dentry_release()`, and automount setup for FUSE submounts.
- Converts FUSE lookup replies into inodes via `fuse_lookup_name()` and `fuse_iget()`, with FORGET handling on error.
- Implements create paths: `FUSE_CREATE`, fallback `mknod`, `mkdir`, `symlink`, `tmpfile`, and `link`.
- Builds optional create extensions for LSM security context and supplementary group propagation.
- Handles unlink/rmdir/rename cache invalidation, local link count updates, ctime updates, and interrupted-operation uncertainty.
- Implements `getattr` via `FUSE_GETATTR` and optional `FUSE_STATX`, including btime caching and fallback when `STATX` is unsupported.
- Implements permission model split between kernel-side `default_permissions` and server-side `FUSE_ACCESS`.
- Implements `FUSE_SETATTR`, including truncate synchronization through `FUSE_NOWRITE`, writeback-cache handling, DAX layout breakage, suid/sgid kill flags, and local cmtime trust rules.
- Provides directory open/release/fsync/ioctl and symlink readlink/page-cache support.

Important data/control flow:
- Dentry timeout is separate from inode attribute timeout. Dentry expiry causes lookup revalidation; inode expiry causes getattr/statx refresh.
- `fc->epoch` invalidates all dentries after connection-wide events; `fuse_epoch_work()` shrinks dcache under `fc->killsb`.
- `fuse_lock_inode()` serializes lookup/readdir unless `FUSE_PARALLEL_DIROPS` was negotiated.
- Attribute freshness is guarded by `fi->attr_version`, `fi->inval_mask`, `fi->i_time`, and writeback-cache-specific cache masks.
- `fuse_do_setattr()` is shared by directory and file paths and is a critical consistency point for truncation, ctime/mtime, page-cache invalidation, and DAX faults.

External dependencies:
- Core FUSE definitions from `fuse_i.h`.
- VFS dentry/inode/file APIs, idmapped mount helpers, ACL/security hooks, and folio/page-cache helpers.
- Request transport through `fuse_simple_request()` and `fuse_simple_idmap_request()`.

Notable edge cases:
- Zero nodeid in lookup is treated as negative lookup with valid timeout.
- Revalidation invalidates if nodeid, generation, type, or submount-flag identity changes.
- Interrupted unlink/rename invalidates affected dentries because userspace may already have completed the operation.
- Sticky bit is hidden from VFS permission checks when `default_permissions` is disabled, preserving server-controlled semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/file.c -->
# File Research: sources/os/linux/linux/fs/fuse/file.c

Purpose: Implements FUSE regular-file operations, including open/release, cached reads/writes, writeback, direct IO, mmap, locks, poll, bmap, lseek, fallocate, splice, and copy_file_range.

Key responsibilities:
- Handles `FUSE_OPEN`/`FUSE_RELEASE` lifecycle through `fuse_file_open()`, `fuse_finish_open()`, `fuse_prepare_release()`, and refcounted `struct fuse_file`.
- Supports no-open/no-opendir server optimizations while still allocating release state when needed to avoid reclaim deadlocks.
- Implements flush and fsync semantics, including writeback synchronization, metadata sync, and server fallback when `FUSE_FLUSH` or `FUSE_FSYNC` is unsupported.
- Provides cached read path using iomap folio reads and readahead, issuing `FUSE_READ` requests and handling short-read EOF truncation.
- Provides cached write path using either iomap buffered write for writeback-cache mode or immediate FUSE write requests through `fuse_perform_write()`.
- Implements writeback with `struct fuse_writepage_args`, queued writepage requests, sync buckets for `syncfs`, and `FUSE_WRITE_CACHE`.
- Implements direct IO through `fuse_direct_io()`, packing user pages or kernel vectors into request pages/args and supporting async DIO.
- Enforces direct-write locking rules, including exclusive locking for append, writes past EOF, non-parallel servers, or cache-mode conflicts.
- Implements mmap behavior for DAX, passthrough, direct-IO shared mmap restrictions, cached mmap, and `page_mkwrite` writeback ordering.
- Implements POSIX locks, BSD flock mapping, `FUSE_BMAP`, `FUSE_LSEEK`, `FUSE_POLL`, `FUSE_FALLOCATE`, and `FUSE_COPY_FILE_RANGE(_64)`.
- Exposes `fuse_file_operations`, `fuse_file_aops`, and `fuse_init_file_inode()`.

Important data/control flow:
- `ff->open_flags` decides direct IO, keep-cache, stream/nonseekable, passthrough precedence, mmap behavior, and direct write concurrency.
- `fi->write_files` tracks open writable files needed for writeback and metadata flushes.
- `fi->queued_writes`, `fi->writectr`, and `FUSE_NOWRITE` coordinate truncate/fsync/writeback exclusion.
- Async direct IO uses `struct fuse_io_priv` refcounts, completion accounting, byte aggregation, and `ki_complete()`.
- `fuse_write_update_attr()` bumps attribute version, extends local size when needed, and invalidates modsize stats.

External dependencies:
- FUSE connection and request structures from `fuse_i.h`.
- DAX helpers, passthrough helpers, iomap buffered IO/writeback APIs, folio APIs, VFS locking and splice APIs.
- Server request transport via `fuse_simple_request()` and `fuse_simple_background()`.

Notable edge cases:
- `FOPEN_DIRECT_IO` overrides passthrough.
- Writeback-cache trusts local size/mtime/ctime more than server attributes.
- Async DIO cannot extend file size without blocking behavior.
- Copy file range falls back from 64-bit opcode to old opcode, then to splice fallback for unsupported/cross-device cases.
- Fallocate hole punch/zero range writes back and invalidates page cache to prevent stale data.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/fuse_dev_i.h -->
# File Research: sources/os/linux/linux/fs/fuse/fuse_dev_i.h

Purpose: Internal header for `/dev/fuse` request/copy plumbing and processing queue lookup helpers.

Key responsibilities:
- Defines request-id bit layout: ordinary requests use even IDs and interrupts use `FUSE_INT_REQ_BIT`.
- Declares `struct fuse_copy_state`, which tracks copying request data between kernel request buffers, user iovecs, pipe buffers, pages, and io_uring-specific state.
- Defines `FUSE_DEV_FC_DISCONNECTED` sentinel used after `/dev/fuse` release.
- Provides helpers to retrieve `struct fuse_dev` and safely load `fud->fc` with acquire ordering.
- Declares processing queue helpers: hash lookup, request find, request end, pending request removal, timeout checks.
- Declares copy helpers for args in/out and queueing FORGET/INTERRUPT messages to the device queue.

Important data/control flow:
- `fuse_dev_fc_get()` pairs with connection install/release atomic updates and is central to safe lockless device-to-connection access.
- `__fuse_get_dev()` returns NULL if the device is not attached to a connection.
- Copy state tracks whether data is moving to or from userspace, whether folios can be moved, and whether the path is io_uring-backed.

External dependencies:
- Struct definitions from `fuse_i.h` and device implementation files.
- Linux pipe, iov_iter, page, and waitqueue APIs.

Notable edge cases:
- `fud->fc` may be NULL, a valid connection, or the disconnected sentinel.
- Most readers can dereference `fud->fc` safely after acquire load, but release/install paths require special handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/fuse_dev_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/fuse_i.h -->
# File Research: sources/os/linux/linux/fs/fuse/fuse_i.h

Purpose: Central internal FUSE header defining connection, inode, file, request, queue, mount, IO, DAX, passthrough, and helper interfaces used across the Linux FUSE implementation.

Key responsibilities:
- Defines constants for max pages, name limits, request timeout frequency, control dentries, and writeback exclusion bias.
- Defines `struct fuse_inode`, including nodeid/nlookup/FORGET state, attribute cache state, writeback state, readdir cache state, DAX/passthrough state, and submount lookup tracking.
- Defines inode state bits for readdirplus advice, bad inode state, btime cache, cache IO mode, size instability, and exclusive access.
- Defines `struct fuse_file`, including FUSE handle, kernel handle, open flags, readdir state, poll rbtree node, IO mode, passthrough file, and flock state.
- Defines request argument containers: `fuse_in_arg`, `fuse_arg`, `fuse_args`, `fuse_args_pages`, `fuse_io_args`, and release/open union storage.
- Defines async IO state in `struct fuse_io_priv`.
- Defines request flags and `struct fuse_req`, including headers, waitqueue, mount pointer, arg buffer, io_uring fields, and creation timestamp.
- Defines input and processing queues: `fuse_iqueue`, `fuse_iqueue_ops`, `fuse_pqueue`, and `fuse_dev`.
- Defines `struct fuse_conn`, the main negotiated connection state and capability bitmap, with background request accounting, mount list, device list, timeout state, DAX/passthrough/io_uring pointers, and sync bucket.
- Defines `struct fuse_mount`, allowing multiple superblocks/submounts to share one `fuse_conn`.
- Provides inline helpers for mount/connection/inode lookup, nodeid access, stale checks, bad inode marking, folio descriptor allocation, sync bucket decrement, and passthrough access.
- Declares cross-file APIs for lookup, forget, device lifecycle, request submission, inode operations, file IO, xattrs/ACLs, DAX, passthrough, ioctl, readdir, mount lifecycle, invalidation, and sysctl.

Important data/control flow:
- `fuse_conn` is the negotiated protocol and lifecycle anchor; `fuse_mount` maps it to each superblock.
- `fuse_inode` keeps kernel inode state aligned with userspace node identity and attribute invalidation.
- `fuse_file` holds per-open server file handle and kernel handle used by poll notifications.
- `fuse_args` is the uniform request descriptor used by all opcode implementations.
- Connection feature bits are set in `inode.c` after `FUSE_INIT` and consumed in `dir.c`, `file.c`, xattr, DAX, passthrough, and device code.

External dependencies:
- Linux VFS, folio/page-cache, waitqueue, workqueue, pid/user namespace, xattr, idr, DAX, io_uring, and FUSE UAPI headers.
- Companion implementation files in `fs/fuse`.

Notable edge cases:
- Many `no_*` fields are negative capability caches set after `-ENOSYS`.
- `FUSE_I_SIZE_UNSTABLE` blocks stale attribute application during truncate/extend races.
- `FUSE_NOWRITE` is a negative counter bias, not a boolean.
- Passthrough and DAX fields compile conditionally and have NULL inline fallbacks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/fuse_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/fuse_trace.h -->
# File Research: sources/os/linux/linux/fs/fuse/fuse_trace.h

Purpose: Defines FUSE tracepoints for request send and request completion.

Key responsibilities:
- Sets `TRACE_SYSTEM` to `fuse`.
- Defines the opcode symbolic table for FUSE and CUSE opcodes used by trace output.
- Emits `TRACE_DEFINE_ENUM()` entries for all listed opcodes.
- Defines `TRACE_EVENT(fuse_request_send)` with connection device id, unique request id, opcode, and input length.
- Defines `TRACE_EVENT(fuse_request_end)` with connection device id, unique request id, output length, and error code.
- Configures trace include path/file and includes `<trace/define_trace.h>`.

Important data/control flow:
- Tracepoints consume `struct fuse_req` fields from request headers and `req->fm->fc->dev`.
- Opcode names are generated from the same `OPCODES` macro table used for `__print_symbolic()`.

External dependencies:
- Linux tracepoint infrastructure.
- FUSE request structure from surrounding compilation context.

Notable edge cases:
- The opcode table includes both ordinary FUSE operations and `CUSE_INIT`.
- Trace output is diagnostic only and does not affect request lifecycle.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/fuse_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/inode.c -->
# File Research: sources/os/linux/linux/fs/fuse/inode.c

Purpose: Implements FUSE inode allocation/lifecycle, attribute reconciliation, superblock/mount setup, mount option parsing, INIT negotiation, connection/device lifecycle integration, export support, syncfs/statfs, submounts, and module initialization/cleanup.

Key responsibilities:
- Defines module metadata and global state: inode slab cache, global connection list, `fuse_mutex`, `/dev/fuse` waitqueue, page/request limits, and background request limits.
- Allocates and frees `struct fuse_inode`, including FORGET request storage, DAX inode data, passthrough backing refs, locks, and invalidation state.
- Evicts inodes by truncating pages, sending FORGET for outstanding lookups, cleaning DAX/submount state, and bumping evict counter for non-deleted inodes.
- Applies FUSE attributes to inodes through `fuse_change_attributes_common()` and `fuse_change_attributes_i()`, respecting writeback-cache local size/mtime/ctime.
- Creates and looks up inodes with `fuse_iget()`, including stale inode detection, reused nodeid handling, and special un-hashed submount mountpoint inodes.
- Implements reverse invalidation for inode page/attribute cache and dentry entries.
- Implements `statfs`, `sync_fs`, writeback sync buckets, and superblock operations.
- Parses mount options: source, fd, rootmode, user/group IDs, default permissions, allow_other, max_read, blksize, and subtype.
- Initializes `fuse_conn`, request queues, background limits, pid/user namespaces, poll tree, attr/evict versions, max pages, and passthrough backing maps.
- Negotiates server capabilities in `process_init_reply()` after `FUSE_INIT`, setting feature bits for async read/DIO, locks, export, writeback cache, readdirplus, ACLs, DAX, passthrough, idmapped mounts, request timeout, io_uring, and more.
- Builds `FUSE_INIT` requests in `fuse_new_init()` and supports sync or background init.
- Allocates/installs/releases `struct fuse_dev` instances and their processing queues.
- Fills superblocks for normal FUSE, fuseblk, and submounts, including BDI setup, root inode creation, dentry operations, control filesystem registration, and device install.
- Implements NFS export file-handle encoding/lookup when export support is negotiated.
- Registers/unregisters `fuse` and `fuseblk` filesystem types, sysctl, `/dev/fuse`, sysfs mount point, fusectl, and dentry invalidation infrastructure.

Important data/control flow:
- `fuse_fill_super_common()` wires the mount context, connection, superblock, root inode, BDI, control fs entry, and optional device fd together.
- `fuse_send_init()` gates connection readiness; `process_init_reply()` sets `fc->conn_init` or `fc->conn_error`, then wakes blocked waiters.
- `fc->killsb` protects traversal of all mounts sharing a connection.
- `fc->curr_bucket` and `struct fuse_sync_bucket` allow `syncfs()` to wait for already-issued writeback without racing newer writes.
- Mount teardown removes the mount from `fc->mounts`; the last mount sends DESTROY if requested, aborts the connection, removes fusectl state, and drops the connection.

External dependencies:
- Core declarations in `fuse_i.h`, device declarations in `fuse_dev_i.h`, and io_uring declarations in `dev_uring_i.h`.
- Linux VFS fs_context, superblock, exportfs, BDI, DAX, namespace, module, sysfs, and block-device APIs.
- Other FUSE implementation files for device, control fs, DAX, passthrough, sysctl, request abort, and timeout behavior.

Notable edge cases:
- Mount fd must be a FUSE device opened in the same user namespace as the mount context.
- Reconfigure rejects changes except legacy remount option compatibility.
- `FUSE_ALLOW_IDMAP` is accepted only when `default_permissions` is active.
- Passthrough is rejected with writeback cache and invalid stack depth.
- For submounts, root inode state is duplicated from the mountpoint and lookup reference ownership is shared through `fuse_submount_lookup`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/inode.c -->