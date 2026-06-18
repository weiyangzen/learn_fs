# Group Research: group_998_linux_stable_sources_os_linux_linux_stable_fs_fuse_dir_c_sources_os__5224a33b6098

Scope: `Docs/research_subset_a.md` only. This grouped report covers the listed Linux stable FUSE files under `sources/os/linux/linux-stable/fs/fuse/`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/dir.c

## Purpose

`dir.c` implements FUSE VFS directory, dentry, inode operation, permission, lookup, symlink, getattr/statx, and setattr behavior. It translates Linux VFS operations into FUSE protocol requests while maintaining kernel-side dentry and attribute caches with server-provided timeouts.

## Main Responsibilities

- Maintains FUSE dentry private data, dentry validity timeouts, stale-entry invalidation, and optional periodic stale dentry cleanup.
- Implements lookup and dentry revalidation using `FUSE_LOOKUP`, including negative dentries, epoch invalidation, readdirplus hints, and automount submount entries.
- Implements directory and namespace mutations: create, tmpfile, mknod, mkdir, symlink, unlink, rmdir, rename, and link.
- Adds creation extensions for security context (`FUSE_SECURITY_CTX`) and supplementary parent-group information (`FUSE_CREATE_SUPP_GROUP`).
- Implements attribute retrieval through `FUSE_GETATTR` and optional `FUSE_STATX`, with local cache fallback when attributes remain valid.
- Implements permission checks for both kernel-side `default_permissions` mode and server-side `FUSE_ACCESS` mode.
- Implements symlink readlink caching/non-caching paths.
- Implements directory open/release/fsync/ioctl wrappers.
- Implements `SETATTR`, including truncate, open(O_TRUNC), writeback-cache time handling, killpriv, DAX layout breakage, and writepage exclusion.
- Installs FUSE inode/file operation tables for directories, common inodes, and symlinks.

## Dentry and Attribute Cache Model

FUSE maintains separate timeout state for dentries and inode attributes:
- Dentry timeout lives in `struct fuse_dentry`.
- Attribute timeout lives in `fuse_inode->i_time`.
- `fuse_time_to_jiffies()` converts protocol timeout fields to jiffies.
- `fuse_change_entry_timeout()` updates dentry validity after lookup/create replies.
- `fuse_invalidate_attr_mask()` marks selected statx fields stale.
- `fuse_invalidate_entry_cache()` marks a dentry stale without necessarily removing it.

The optional `inval_wq` module parameter enables a delayed workqueue that keeps an rb-tree of expiring dentries and disposes unused expired entries. `delete_stale` also toggles `DCACHE_OP_DELETE` so stale dentries are dropped more aggressively.

## Lookup and Revalidation

`fuse_dentry_revalidate()` is central:
- Rejects dentries older than the connection epoch.
- Rejects bad inodes.
- Refreshes expired positive dentries with `FUSE_LOOKUP`.
- Treats zero nodeid as `-ENOENT`.
- Detects nodeid/type/submount mismatches and asks VFS to invalidate.
- Refreshes inode attributes and dentry timeout when the same inode is confirmed.
- Uses `FUSE_I_INIT_RDPLUS` and `FUSE_I_ADVISE_RDPLUS` to adaptively encourage readdirplus after lookup/readdir interaction.

`fuse_lookup_name()` sends raw lookups and creates inodes with `fuse_iget()`. `fuse_lookup()` wraps it for VFS, handles negative results, prevents root aliases, splices aliases, and records the current connection epoch in `dentry->d_time`.

## Create and Namespace Operations

Creation helpers share common reply handling through `create_new_entry()`:
- Allocates a forget request before sending the operation.
- Sends operation-specific protocol input.
- Adds creation extension arguments when negotiated.
- Validates nodeid, file type, and attributes.
- Instantiates or splices the returned inode.
- Updates parent directory attributes/version.

`fuse_create_open()` implements atomic create/open for `FUSE_CREATE` and `FUSE_TMPFILE`, allocating `struct fuse_file`, saving the open reply, instantiating the inode, and completing `finish_open()`. If the server lacks create support, `fuse_atomic_open()` falls back to mknod plus normal open.

Mutations invalidate or refresh local cache state carefully:
- `unlink`/`rmdir` update parent directory state, reduce link counts, invalidate entry cache, and invalidate ctime.
- `rename` updates ctime for moved entries, invalidates on interrupted/unknown outcomes, and supports `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT` when `FUSE_RENAME2` is available.
- `link` uses `FUSE_LINK`, falling back to `-EPERM` after `-ENOSYS`.

## Attributes, Statx, and Permission

`fuse_update_get_attr()` decides whether to call the server:
- Honors `AT_STATX_FORCE_SYNC` and `AT_STATX_DONT_SYNC`.
- Requests only FUSE-supported fields: basic stats and optionally btime.
- Uses `FUSE_STATX` when btime is requested and the server supports it.
- Falls back to cached `generic_fillattr()` and preserved FUSE fields when valid.

`fuse_permission()` enforces the FUSE access model:
- First checks `fuse_allow_current_process()` to prevent unauthorized callers from entering a user-controlled filesystem.
- In `default_permissions` mode, refreshes mode/uid/gid if stale and calls `generic_permission()`.
- In remote-check mode, sends `FUSE_ACCESS` for access/chdir checks.
- Always keeps local execute checks for regular files.

## Setattr and Truncation

`fuse_do_setattr()` is the main setattr implementation:
- Uses `setattr_prepare()`, with `ATTR_FORCE` when the server handles permissions.
- Converts VFS `iattr` into `fuse_setattr_in`, including idmapped uid/gid translation.
- Handles `ATTR_OPEN` with `atomic_o_trunc` as a local page-cache truncate.
- Blocks writepages during truncate with `FUSE_NOWRITE`.
- Marks size unstable with `FUSE_I_SIZE_UNSTABLE`.
- Breaks DAX layouts before truncating DAX inodes.
- Sends file-handle based setattr when available.
- Adds kill-suid/sgid flags for truncate/chown when `handle_killpriv_v2` is negotiated.
- Updates local inode attributes and page cache only after a successful server reply.

This path is sensitive because writeback-cache mode trusts local size/mtime/ctime more than server replies.

## Operation Tables

The file installs:
- `fuse_dir_inode_operations` for directories.
- `fuse_dir_operations` for directory files.
- `fuse_common_inode_operations` for regular and special inode metadata operations.
- `fuse_symlink_inode_operations` and `fuse_symlink_aops` for symlinks.

## Edge Cases and Risks

- Interrupted namespace operations may have completed in userspace, so the kernel invalidates affected dentries but cannot fully repair all race cases.
- Attribute cache invalidation must be field-specific because writeback cache keeps local size/time authoritative.
- `SETATTR` truncate paths coordinate inode locks, page-cache invalidation, writeback exclusion, and DAX layout breaking.
- Permission checks intentionally avoid entering the userspace server for callers the mounter could not ptrace.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/file.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/file.c

## Purpose

`file.c` implements FUSE regular-file operations: open/release, flush/fsync, buffered reads and writes, direct I/O, writeback, mmap, locking, lseek, poll, fallocate, splice, passthrough dispatch, DAX dispatch, and copy-file-range.

## Main Responsibilities

- Sends `FUSE_OPEN`/`FUSE_OPENDIR` and manages `struct fuse_file` handles.
- Sends delayed or synchronous `FUSE_RELEASE`/`FUSE_RELEASEDIR`.
- Implements `flush`, `fsync`, and writeback synchronization.
- Implements cached reads through iomap read helpers and FUSE read requests.
- Implements cached writes either through writeback-cache/iomap or immediate FUSE writes.
- Implements direct I/O with sync/async request splitting, page extraction, completion aggregation, and EOF/short-I/O handling.
- Implements writeback batching for dirty folios using iomap writeback callbacks.
- Supports DAX and passthrough dispatch where negotiated.
- Implements mmap behavior, including direct-I/O shared mmap restrictions.
- Implements POSIX locks, flock, bmap, lseek, poll notification, fallocate, and copy-file-range.

## Open and Release Lifecycle

`fuse_file_open()` allocates `struct fuse_file`, optionally sends `FUSE_OPEN` or `FUSE_OPENDIR`, records server file handle and `FOPEN_*` flags, and detects `-ENOSYS` no-open/no-opendir support. Regular files still allocate release argument storage even in no-open mode to avoid reclaim deadlocks with pending I/O.

`fuse_finish_open()` finalizes cache/passthrough I/O mode through `fuse_file_io_open()`, applies stream/nonseekable flags, and links writable files into `fi->write_files` when writeback cache is enabled.

`fuse_prepare_release()` removes the file from write and poll tracking, wakes poll waiters, prepares the release request, and optionally pins the inode until async release completion. `fuse_file_put()` sends release synchronously or in background after outstanding async I/O drops references.

## Flush and Fsync

`fuse_flush()` writes dirty inode data, checks mapping errors, sends `FUSE_FLUSH` unless unsupported or suppressed by `FOPEN_NOFLUSH`, and invalidates block count attributes in writeback-cache mode.

`fuse_fsync()`:
- Locks the inode.
- Calls `file_write_and_wait_range()`.
- Waits for queued/sent FUSE writepages via `fuse_sync_writes()`.
- Checks writeback errors directly.
- Syncs inode metadata.
- Sends `FUSE_FSYNC` unless unsupported.

Directory fsync in `dir.c` reuses `fuse_fsync_common()` with `FUSE_FSYNCDIR`.

## Cached Reads

Cached read uses iomap:
- `fuse_read_folio()` handles synchronous folio reads.
- `fuse_readahead()` batches folios and may issue async background reads if `async_read` is enabled.
- `fuse_send_readpages()` sends multi-folio `FUSE_READ` requests.
- `fuse_readpages_end()` completes folios and handles short reads.
- `fuse_short_read()` treats short reads as EOF unless writeback cache is enabled, where holes can be hidden by dirty local cache.

`fuse_cache_read_iter()` refreshes size on auto-invalidate mounts or reads beyond cached EOF, then delegates to `generic_file_read_iter()`.

## Cached Writes

There are two buffered write modes:
- With writeback cache and no killpriv conflict, `fuse_cache_write_iter()` uses `iomap_file_buffered_write()` for granular dirty tracking.
- Otherwise, `fuse_perform_write()` copies user data into cache folios and sends `FUSE_WRITE` immediately.

`fuse_write_update_attr()` increments attribute version, extends local i_size when needed, and invalidates size/mtime/ctime/block attributes.

Immediate writes use `fuse_fill_write_pages()` and `fuse_send_write_pages()`. They wait on folio writeback, copy data atomically from the iterator, send `FUSE_WRITE`, clear uptodate on error/short write, unlock the last locked folio when needed, and update position only for completed bytes.

## Direct I/O

`fuse_direct_io()` is the shared direct read/write engine:
- Splits I/O by `max_read`/`max_write` and `max_pages`.
- Extracts user pages with `iov_iter_extract_pages()` or uses kvec buffers directly when allowed.
- Handles vmalloc kernel I/O flushing/invalidation.
- Sends `FUSE_READ` or `FUSE_WRITE`.
- Supports async completion through `struct fuse_io_priv`.
- Reverts iov_iter on short or failed operations.
- Invalidates page cache around `FOPEN_DIRECT_IO` writes.

Direct writes use `fuse_dio_lock()`:
- Exclusive lock for append, past-EOF writes, non-parallel direct-write servers, or cached I/O mode.
- Shared lock for negotiated parallel direct writes, guarded by uncached I/O mode counters.

`fuse_direct_IO()` is the address-space direct-I/O hook and supports async DIO. It avoids async extending writes, truncates back after failed extending writes, and handles short-read truncation optimizations.

## Writeback

Writeback uses `struct fuse_writepage_args` and iomap writeback callbacks:
- `fuse_iomap_writeback_range()` batches contiguous dirty ranges until max pages, max bytes, or discontinuity.
- `fuse_writepages_send()` queues batches on `fi->queued_writes`.
- `fuse_flush_writepages()` sends queued batches only while no truncate/fsync write exclusion is active.
- `fuse_send_writepage()` submits background forced/nocreds write requests and respects current inode size crop.
- `fuse_writepage_end()` records mapping errors, invalidates modification attrs when not writeback-cache, decrements write counters, completes folio writeback, and frees resources.

`fuse_launder_folio()` writes one dirty folio and waits for writeback before reclaim/laundering.

## mmap and I/O Mode

`fuse_file_mmap()` dispatches:
- DAX mmap to `fuse_dax_mmap()`.
- Passthrough mmap to `fuse_passthrough_mmap()`.
- Direct-I/O mmap only when restrictions allow it.

For `FOPEN_DIRECT_IO`, shared mmap requires `FUSE_DIRECT_IO_ALLOW_MMAP`. The first shared mmap transitions the inode into cached I/O mode and waits out incompatible parallel direct writers.

`fuse_page_mkwrite()` updates file time, locks the folio, verifies mapping, and waits for prior writeback before allowing the page to be dirtied again.

## Locks, Poll, Lseek, and Other File Ops

- POSIX locks use `FUSE_GETLK`, `FUSE_SETLK`, and `FUSE_SETLKW`; fallback uses local locks if server lacks support.
- `flock` uses FUSE lock requests with `FUSE_LK_FLOCK`, or local fallback if unsupported.
- `fuse_lseek()` uses `FUSE_LSEEK` for `SEEK_DATA`/`SEEK_HOLE`, falling back to generic seek after refreshing size.
- Poll registers `struct fuse_file` in an rb-tree keyed by kernel handle and wakes waiters on `FUSE_NOTIFY_POLL`.
- `fuse_file_fallocate()` sends `FUSE_FALLOCATE`, coordinates writeback and DAX layout breakage, updates size, and truncates page cache for hole-punch/zero-range.
- `fuse_copy_file_range()` uses `FUSE_COPY_FILE_RANGE_64` with fallback to older `FUSE_COPY_FILE_RANGE`, then splice fallback for unsupported/exdev cases.

## Operation Tables

`fuse_file_operations` provides regular file VFS methods. `fuse_file_aops` provides folio read/readahead/writeback/dirty/invalidate/bmap/direct-I/O behavior.

`fuse_init_file_inode()` installs these operations and initializes writeback, direct-I/O, and optional DAX inode state.

## Edge Cases and Risks

- Release may be delayed until async I/O completes.
- Direct-I/O async completion must aggregate partial request results into the longest contiguous transferred prefix.
- Writeback cache changes which timestamps and sizes can be trusted from userspace replies.
- Mixing passthrough, cached I/O, direct I/O, shared mmap, and DAX requires careful mode transitions.
- Copy-file-range cache invalidation can lose unusual concurrent mmap writes to partial pages, as documented in-code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/fuse_dev_i.h -->
# File Research: sources/os/linux/linux-stable/fs/fuse/fuse_dev_i.h

## Purpose

`fuse_dev_i.h` is an internal header for FUSE device-side request transport. It declares request-ID conventions, `/dev/fuse` device helpers, copy-state tracking, and internal functions used by the FUSE device implementation.

## Main Responsibilities

- Defines request ID layout:
  - ordinary requests use even unique IDs,
  - interrupt requests use the low bit via `FUSE_INT_REQ_BIT`,
  - normal request IDs advance by `FUSE_REQ_ID_STEP`.
- Declares the global `fuse_dev_waitq` used for device/mount coordination.
- Defines `struct fuse_copy_state`, the state used when copying request payloads between kernel request buffers and userspace/device iterators or pipes.
- Provides safe inline accessors for `struct fuse_dev` from a file and for reading `fud->fc`.
- Declares request lookup, queue, interrupt, forget, copy, and timeout helpers implemented elsewhere.

## Key Types

`struct fuse_copy_state` tracks:
- Current request.
- I/O iterator.
- Pipe buffers and current pipe buffer.
- Current page, length, and offset.
- Direction (`write`), folio movement, io_uring mode, and ring-copy accounting.

`FUSE_DEV_FC_DISCONNECTED` is a sentinel stored in `fud->fc` after `/dev/fuse` is closed.

## Concurrency Notes

`fuse_dev_fc_get()` uses `smp_load_acquire()` and pairs with `xchg()`/`cmpxchg()` in device install/release paths. The comments document when lockless dereference is safe and where exceptions exist.

## Dependencies

This header depends on `struct fuse_conn`, `struct fuse_dev`, request queue structures, and the FUSE device implementation. It is included by `inode.c` and device-side code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/fuse_dev_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/fuse_i.h -->
# File Research: sources/os/linux/linux-stable/fs/fuse/fuse_i.h

## Purpose

`fuse_i.h` is the main internal FUSE header. It defines core FUSE kernel structures, connection feature state, request objects, inode/file private data, mount context data, helper functions, constants, and cross-file prototypes.

## Main Responsibilities

- Defines default request/page limits and global module parameters.
- Defines private inode, file, request, queue, device, mount, and connection structures.
- Defines FUSE inode state bits and request state bits.
- Defines request argument containers and page/folio descriptors.
- Declares helpers implemented across `dir.c`, `file.c`, `inode.c`, device code, DAX, ioctl, xattr, ACL, readdir, iomode, backing, and passthrough code.
- Provides inline accessors for FUSE mount/connection/inode/file state.
- Provides no-op or conditional declarations for optional DAX, passthrough, and sysctl functionality.

## Core Data Structures

`struct fuse_inode` extends Linux `struct inode` with:
- FUSE nodeid and lookup count.
- Pending forget message.
- Attribute timeout, invalid mask, original mode/ino, birth time, attribute version.
- Regular-file cache/writeback state: write file list, queued writes, write counter, page-cache I/O counter, wait queues.
- Directory readdir-cache state.
- Per-inode state bits and serialization locks.
- Optional DAX, submount, and passthrough state.

Important inode state bits include:
- `FUSE_I_ADVISE_RDPLUS`
- `FUSE_I_INIT_RDPLUS`
- `FUSE_I_SIZE_UNSTABLE`
- `FUSE_I_BAD`
- `FUSE_I_BTIME`
- `FUSE_I_CACHE_IO_MODE`
- `FUSE_I_EXCLUSIVE`

`struct fuse_file` stores:
- Mount pointer, server file handle, kernel handle, nodeid, refcount, and `FOPEN_*` flags.
- Writeback list entry.
- Readdir stream/cache position.
- Poll rb-tree node and wait queue.
- Cached/uncached I/O mode state.
- Optional passthrough file/cred.
- Flock marker.

`struct fuse_conn` is the connection-wide state holder:
- Global locks, refcount, epoch, user/group/userns/pidns.
- Request queues and device lists.
- Background request throttling.
- INIT/connected/aborted/error state.
- Negotiated feature bits.
- Capability fallback bits such as `no_open`, `no_fsync`, `no_lseek`, `no_statx`, etc.
- Attribute/evict version counters.
- DAX, passthrough, io_uring, timeout, poll, and syncfs state.
- List of `struct fuse_mount` objects sharing the connection.

`struct fuse_mount` binds a superblock to a shared `fuse_conn`, supporting submounts and shared connections.

## Request Model

`struct fuse_args` describes high-level request input/output arguments and page behavior flags:
- ordinary scalar args,
- page-backed input/output,
- variable-length output,
- zeroing/replacement behavior,
- background completion callback,
- credential/force/may-block behavior,
- vmalloc kvec invalidation support.

`struct fuse_req` is the queued request object with input/output headers, flags, wait queue, mount pointer, optional transport buffers, and creation time.

Request flags describe lifecycle and transport state:
- waiting, pending, sent, finished,
- background, force, reply,
- interrupted, aborted, locked,
- async and io_uring.

`struct fuse_io_priv` aggregates multi-request direct-I/O completion state.

## Queue and Device Model

`struct fuse_iqueue` is the input queue visible to the userspace server/device transport. It contains pending requests, interrupts, forgets, request counter, wait queue, fasync state, and transport-specific callbacks.

`struct fuse_pqueue` tracks processing requests in a hash table and I/O list.

`struct fuse_dev` represents one device instance with refcount, connection pointer, processing queue, and connection device-list entry.

## Feature Negotiation State

`struct fuse_conn` contains negotiated flags for:
- async read and async direct I/O,
- atomic open truncate,
- export support,
- writeback cache,
- parallel directory operations,
- killpriv v1/v2,
- symlink caching,
- big writes,
- auto/explicit invalidation,
- readdirplus,
- POSIX ACLs,
- submounts,
- syncfs,
- init-security/create supplementary groups,
- inode DAX,
- direct-I/O mmap relaxation,
- statx,
- passthrough,
- kvec page transport,
- link support,
- sync init,
- io_uring transport,
- request timeouts.

It also stores optimization fallback flags when operations return `-ENOSYS`.

## Important Inline Helpers

The header provides:
- `get_fuse_mount_super()`, `get_fuse_conn_super()`, `get_fuse_mount()`, `get_fuse_conn()`.
- `get_fuse_inode()` and `get_node_id()`.
- `invalid_nodeid()`.
- attribute/evict version readers.
- stale/bad inode helpers.
- DAX and passthrough helpers.
- `fuse_folios_alloc()` for paired folio/descriptor arrays.
- `fuse_set_zero_arg0()` for operations that need a placeholder first argument.

## Cross-Module Contract

This header ties together:
- `dir.c` for dentries, attributes, permissions, setattr, xattrs/ACLs.
- `file.c` for file I/O and writeback.
- `inode.c` for mount/superblock/inode lifecycle.
- `dev.c` and transport code for request queuing and completion.
- DAX, ioctl, readdir, passthrough, backing, sysctl, and control filesystem modules.

## Edge Cases and Risks

- The connection struct has many feature and fallback bits; code must distinguish negotiated capabilities from `-ENOSYS` runtime fallbacks.
- Inode fields share a union between regular-file and directory-specific cache state, so initialization must match inode type.
- Request argument flags control memory ownership, page pinning, vmalloc flushing, and completion behavior; incorrect combinations can corrupt data or leak refs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/fuse_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/fuse_trace.h -->
# File Research: sources/os/linux/linux-stable/fs/fuse/fuse_trace.h

## Purpose

`fuse_trace.h` defines FUSE tracepoints for request submission and completion. It provides symbolic opcode names and trace event layouts used by Linux ftrace/perf tooling.

## Main Responsibilities

- Defines an `OPCODES` macro table mapping FUSE/CUSE opcode constants to printable names.
- Emits `TRACE_DEFINE_ENUM()` entries for each opcode.
- Reuses the opcode table for `__print_symbolic()`.
- Defines `fuse_request_send` trace event.
- Defines `fuse_request_end` trace event.
- Sets `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and includes `trace/define_trace.h`.

## Trace Events

`fuse_request_send` records:
- connection device id,
- request unique id,
- opcode,
- input header length,
- symbolic opcode name.

`fuse_request_end` records:
- connection device id,
- request unique id,
- output header length,
- request error code.

## Dependencies

The tracepoints consume `struct fuse_req` fields:
- `req->fm->fc->dev`
- `req->in.h.unique`
- `req->in.h.opcode`
- `req->in.h.len`
- `req->out.h.len`
- `req->out.h.error`

## Notes

The opcode table includes standard FUSE operations, newer operations such as `FUSE_TMPFILE` and `FUSE_STATX`, DAX mapping operations, syncfs, and `CUSE_INIT`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/fuse_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/inode.c

## Purpose

`inode.c` implements FUSE module initialization, filesystem registration, superblock setup, mount context parsing, connection setup/teardown, FUSE_INIT negotiation, inode allocation/eviction, attribute installation, export support, syncfs, submounts, and device association.

## Main Responsibilities

- Defines module metadata and module parameters.
- Manages global FUSE connection list and global mutex.
- Allocates and frees FUSE inode cache objects.
- Initializes and releases `struct fuse_conn`, `struct fuse_mount`, and `struct fuse_dev`.
- Implements FUSE inode attribute refresh and inode instantiation.
- Sends FORGET on inode eviction and submount lookup release.
- Implements reverse inode invalidation support.
- Implements superblock operations: alloc/free/evict inode, write inode, statfs, syncfs, show options, umount begin.
- Parses mount options for `fuse` and `fuseblk`.
- Negotiates protocol features with the userspace server through `FUSE_INIT`.
- Registers `fuse` and `fuseblk` filesystem types.
- Initializes `/dev/fuse`, fusectl, sysfs mount point, dentry invalidation work, and sysctls.

## Inode Allocation and Eviction

`fuse_alloc_inode()` allocates `struct fuse_inode` from `fuse_inode_cachep`, clears private fields, initializes locks, allocates a forget message, and optional DAX/passthrough state.

`fuse_evict_inode()`:
- Warns if dirty inode metadata remains.
- Breaks DAX layouts.
- Truncates pages and clears the inode.
- Sends `FORGET` for outstanding lookup references if the superblock is active.
- Releases submount lookup refs.
- Increments `evict_ctr` for non-deleted inodes to invalidate racing lookups.
- Checks that regular-file cache/writeback lists are empty.

## Attribute Handling

`fuse_change_attributes_common()` installs server attributes into the Linux inode while holding `fi->lock`:
- Clears invalid masks when safe.
- Advances attribute version.
- Updates mode, nlink, uid/gid, blocks, times, btime, block size, original mode/ino.
- Preserves sticky-bit semantics when the kernel is not doing default permissions.
- Clears `S_NOSEC` because server-side security metadata may have changed.

`fuse_change_attributes_i()` wraps this with writeback-cache handling:
- Trusts local size/mtime/ctime when writeback cache is active for regular files.
- Ignores stale attribute updates by comparing `attr_version`.
- Avoids applying size changes while `FUSE_I_SIZE_UNSTABLE` is set.
- Truncates or invalidates page cache when size or mtime indicates stale data.
- Applies DAX dont-cache flags.

`fuse_get_cache_mask()` captures the writeback-cache rule: local size, mtime, and ctime can be authoritative for regular files.

## Inode Lookup

`fuse_iget()` creates or finds inodes by FUSE nodeid:
- Handles auto-submount roots specially because their nodeids are not unique within the parent filesystem hash.
- Uses `iget5_locked()` for ordinary inodes.
- Marks stale reused-nodeid inodes bad.
- Initializes inode operation tables by file type.
- Increments `nlookup`.
- Applies attributes and unlocks new inodes.

`fuse_ilookup()` scans all mounts sharing a connection under `fc->killsb` to find a nodeid. It supports notifications and shared-connection submounts.

`fuse_reverse_inval_inode()` handles server-initiated invalidation by nodeid, invalidating attrs, ACLs, and optional page ranges.

## Mount and Superblock Setup

`fuse_parse_param()` handles modern fs_context parameters:
- `source`
- `fd`
- `rootmode`
- `user_id`
- `group_id`
- `default_permissions`
- `allow_other`
- `max_read`
- `blksize`
- `subtype`

It validates `/dev/fuse` file type and user namespace matching.

`fuse_fill_super_common()` initializes the superblock:
- Applies standard FUSE superblock defaults.
- Sets block size for `fuseblk` or page-sized blocks for normal FUSE.
- Allocates DAX connection state if requested.
- Initializes backing device info with strict dirty limits.
- Sets POSIX ACL support and mount options.
- Creates the root inode and root dentry.
- Adds the connection to fusectl and global list.
- Installs the device connection and wakes `/dev/fuse` waiters.

`fuse_get_tree()` creates a new connection/mount pair, supports `fuseblk`, normal nodev mounts, and reusing an already initialized FUSE device connection.

## Submounts

FUSE submounts share a `fuse_conn` but have distinct superblocks:
- `fuse_dentry_automount()` in `dir.c` creates a submount context.
- `fuse_get_tree_submount()` allocates a new `fuse_mount`, shares the parent connection, and creates a superblock rooted at the mountpoint inode.
- `fuse_fill_super_submount()` copies relevant superblock settings, duplicates the root inode, and shares submount lookup accounting so FORGET is delayed until all submount users are gone.

## FUSE_INIT Negotiation

`fuse_send_init()` creates and sends `FUSE_INIT`, synchronously or in background depending on `sync_init`.

`process_init_reply()` validates protocol version, processes background limits, and maps negotiated flags to connection behavior:
- async read/direct I/O,
- POSIX/flock locking,
- atomic truncate,
- export support,
- big writes and max pages,
- dont-mask,
- auto/explicit invalidation,
- readdirplus,
- writeback cache,
- parallel dirops,
- killpriv v1/v2,
- time granularity,
- POSIX ACL/default permissions,
- symlink caching,
- abort error behavior,
- DAX map alignment and inode DAX,
- extended setxattr,
- security context and supplementary group creation,
- direct-I/O mmap allowance,
- passthrough,
- no-export support,
- idmapped mounts,
- io_uring transport,
- request timeout.

It sets max readahead, minor version, max write, and connection initialized/error state.

## Syncfs and Writeback Buckets

When `sync_fs` is enabled:
- `fuse_sync_fs_writes()` switches the current writeback bucket and waits for all writes in the old bucket.
- `fuse_sync_fs()` then sends `FUSE_SYNCFS`, disabling the feature on `-ENOSYS`.

This ensures syncfs sees all FUSE writepages that were in flight before the sync boundary.

## Export Support

NFS/export helpers encode file handles as nodeid/generation pairs, optionally with parent. `fuse_get_dentry()` can reconstruct dentries by inode lookup or server lookup of `"."` when export support is negotiated. `FUSE_NO_EXPORT_SUPPORT` switches to encode-only export operations.

## Device and Connection Lifecycle

`fuse_conn_init()` initializes locks, queues, counters, feature defaults, namespace refs, request limits, random lock-owner scramble key, optional passthrough backing map, and mount list membership.

`fuse_conn_put()` tears down DAX, timeouts, epoch work, input queue ops, pid/user namespaces, sync bucket, backing files, io_uring, and final release via RCU.

`fuse_dev_alloc()`, `fuse_dev_install()`, `fuse_dev_alloc_install()`, and `fuse_dev_put()` allocate processing queues, attach devices to connections, and drop connection refs.

`fuse_conn_destroy()` optionally sends `FUSE_DESTROY`, aborts the connection, waits for abort completion, and removes fusectl/global-list entries.

## Module Initialization

`fuse_init()` performs full module startup:
- initializes global connection list,
- registers `fuse`/`fuseblk`,
- initializes `/dev/fuse`,
- creates sysfs `fs/fuse/connections`,
- initializes fusectl,
- initializes dentry invalidation trees,
- sanitizes background request limits.

`fuse_exit()` reverses those steps.

## Edge Cases and Risks

- Attribute updates must be versioned to avoid applying stale server replies after local changes.
- Eviction races with lookup/readdirplus are handled with `evict_ctr`.
- Mount fd namespace checks are security-critical.
- FUSE_INIT feature combinations matter; passthrough is rejected with writeback cache.
- Submount nodeids are intentionally excluded from the normal inode hash to avoid alias conflicts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/inode.c -->