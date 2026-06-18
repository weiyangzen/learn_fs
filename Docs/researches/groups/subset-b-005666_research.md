# subset-b-005666 FUSE client research

Grouped research for the FUSE client directory/file/inode core. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dir.c -->
# sources/distributed-fs/ceph-client/fs/fuse/dir.c

## Purpose
`dir.c` implements FUSE VFS directory and metadata operations: dentry validation, lookup, create/mkdir/mknod/symlink/tmpfile/link, unlink/rmdir/rename, permission checks, readlink, directory open/release/fsync/ioctl, getattr/statx, setattr/truncate, and inode-operation initialization for directories, common inodes, and symlinks. It is the main bridge between Linux namei/inode operations and userspace FUSE requests such as `FUSE_LOOKUP`, `FUSE_CREATE`, `FUSE_MKDIR`, `FUSE_RENAME2`, `FUSE_ACCESS`, `FUSE_GETATTR`, `FUSE_STATX`, and `FUSE_SETATTR`.

## Important APIs, Types, And Functions
The file defines `struct fuse_dentry`, an internal object attached to `dentry->d_fsdata` that stores the entry timeout and, when enabled, an RB-tree node used by the periodic stale-dentry invalidation worker. `fuse_dentry_operations` wires `.d_revalidate`, `.d_delete`, `.d_init`, `.d_release`, and `.d_automount` to FUSE-specific behavior.

Lookup and cache APIs include `fuse_time_to_jiffies()`, `fuse_change_entry_timeout()`, `fuse_invalidate_attr_mask()`, `fuse_invalidate_attr()`, `fuse_invalidate_entry_cache()`, `fuse_lookup_name()`, and `fuse_dentry_revalidate()`. Creation APIs are layered through `fuse_create_open()`, `fuse_atomic_open()`, `create_new_entry()`, `create_new_nondir()`, `fuse_mknod()`, `fuse_mkdir()`, `fuse_symlink()`, and `fuse_tmpfile()`. Metadata APIs include `fuse_do_statx()`, `fuse_do_getattr()`, `fuse_update_get_attr()`, `fuse_update_attributes()`, `iattr_to_fattr()`, `fuse_flush_times()`, `fuse_set_nowrite()`, `fuse_release_nowrite()`, and `fuse_do_setattr()`.

The exported or externally used hooks are `fuse_lookup_name()`, `fuse_invalidate_attr*()`, `fuse_invalidate_entry_cache()`, `fuse_update_attributes()`, `fuse_reverse_inval_entry()`, `fuse_allow_current_process()`, `fuse_flush_time_update()`, `fuse_update_ctime()`, `fuse_set_nowrite()`, `fuse_release_nowrite()`, `fuse_flush_times()`, `fuse_do_setattr()`, `fuse_init_common()`, `fuse_init_dir()`, and `fuse_init_symlink()`.

## Control Flow
Name lookup starts in `fuse_lookup()`, which locks the directory via `fuse_lock_inode()` unless `parallel_dirops` was negotiated, sends `FUSE_LOOKUP` through `fuse_lookup_name()`, converts the returned attributes into a Linux inode with `fuse_iget()`, then splices the dentry and stamps the current connection epoch and entry timeout. `fuse_dentry_revalidate()` is the fast/slow validity gate: it rejects dentries from older epochs, bad inodes, expired entries, explicit revalidation, exclusive lookup, or rename target lookups; for positive expired dentries it reissues `FUSE_LOOKUP`, queues a `FORGET` if the reply identifies a different object, refreshes attributes and ACL cache if the same object is confirmed, and returns invalid on errors or stale attributes.

Create paths build `struct fuse_args` around protocol-specific input structs. `fuse_atomic_open()` first resolves in-lookup dentries, then attempts `FUSE_CREATE` unless `no_create` is known, falling back to `mknod + open` on `-ENOSYS`. `fuse_create_open()` allocates a `fuse_file`, includes optional security-context and supplementary-group extension records, sends `FUSE_CREATE` or `FUSE_TMPFILE`, instantiates the inode, opens the VFS file with `finish_open()`, and invalidates or truncates page cache based on `FOPEN_KEEP_CACHE` and `atomic_o_trunc`.

Unlink, rmdir, and rename send the corresponding opcode, then update directory attributes and ctime/nlink state locally. Ambiguous errors such as `-EINTR` invalidate affected dentries because userspace may have completed the operation. `fuse_reverse_inval_entry()` is the server-notification path: it finds the parent inode, locates/removes the child dentry without permission checks, invalidates parent attributes, optionally deletes a matching non-mounted child inode, and handles `FUSE_EXPIRE_ONLY`.

`getattr` chooses between cached VFS data, `FUSE_GETATTR`, and `FUSE_STATX`. `fuse_update_get_attr()` considers request mask, `AT_STATX_FORCE_SYNC`, `AT_STATX_DONT_SYNC`, the inode invalidation mask, cache mask, and attribute timeout. `FUSE_STATX` is used for birth time when available, with `-ENOSYS` downgrading `fc->no_statx`. `setattr` validates via `setattr_prepare()`, converts idmapped `iattr` fields to FUSE protocol values, handles `O_TRUNC`/writeback/DAX locking, blocks concurrent writepage with `FUSE_NOWRITE`, sends `FUSE_SETATTR`, applies returned attributes while respecting local writeback-cache mtime/ctime/size, and truncates or invalidates page cache after releasing the nowrite bias to avoid launder deadlocks.

## State And Persistence Behavior
Entry and attribute caching are timeout based. Dentry timeouts live in `struct fuse_dentry::time`; inode attribute timeouts and invalid masks live in `struct fuse_inode::i_time` and `inval_mask`. The connection epoch invalidates all dentries after global server-side invalidation. Optional module parameter `inval_wq` enables a delayed workqueue that scans RB trees of dentries by expiration time and marks/disposes stale dentries.

Metadata changes use the per-connection `attr_version` counter and the inode-local `fi->attr_version` to reject stale replies and preserve local writeback-cache updates. Directory mutations call `fuse_dir_changed()` to invalidate attributes and bump the inode version. Truncation and size-changing paths set `FUSE_I_SIZE_UNSTABLE` while size is in transition. Writeback safety uses `fi->writectr` and the `FUSE_NOWRITE` negative bias so truncate/fsync/setattr can wait for in-flight writepages and queue new ones.

No persistent on-disk state is maintained by this file. Persistence is delegated to the userspace FUSE server through requests; the kernel state is cache, lifetime, and coherency metadata.

## Dependencies And Integration Points
This file depends heavily on `fuse_i.h` structures and helpers, the request path (`fuse_simple_request()`, `fuse_simple_idmap_request()`), inode construction in `inode.c` (`fuse_iget()`, `fuse_change_attributes()`), file open/release in `file.c`, ACL/xattr/fileattr/ioctl helpers, DAX helpers, Linux VFS dentry/inode/namei APIs, LSM initialization hooks, idmapped mount helpers, and page-cache APIs.

The operation tables integrate with the VFS: `fuse_dir_inode_operations`, `fuse_dir_operations`, `fuse_common_inode_operations`, `fuse_symlink_inode_operations`, and `fuse_symlink_aops`. `fuse_dentry_automount()` integrates FUSE submounts with `fs_context_for_submount()` and `fc_mount()`.

## Risks And Edge Cases
Correctness is sensitive to races between lookup replies, inode eviction, and server-side invalidations. Ambiguous request interruption is handled by cache invalidation, but comments acknowledge remaining dcache inconsistency if invalidation fails under active references. `fuse_do_setattr()` has multiple deadlock-sensitive regions around DAX layout breaks, page-cache invalidation locks, `FUSE_NOWRITE`, and folio laundering. Idmapped mount conversion and security xattr extension packing must preserve user namespace semantics. Server bugs returning invalid node IDs, root generation, wrong inode type, oversize attributes, or invalid statx data cause `-EIO` or mark inodes bad.

Permission behavior is security-sensitive because operations call into a user-controlled daemon. `fuse_allow_current_process()` restricts access to the mounter identity unless `allow_other` or the sysadmin bypass module parameter permits access. Local versus remote permission checking changes behavior depending on `default_permissions`, POSIX ACL negotiation, and `FUSE_ACCESS` support.

## Test Signals
Useful tests include lookup timeout and negative-dentry expiry, readdirplus advice after lookup, `atomic_open` fallback on `-ENOSYS`, LSM/security-context create extension coverage, supplementary-group extension coverage, rename flags including `RENAME_EXCHANGE` and `RENAME_WHITEOUT`, `FUSE_EXPIRE_ONLY` notifications, permission behavior with and without `allow_other`/`default_permissions`, statx birth-time fallback, interrupted unlink/rename invalidation, writeback-cache truncate/setattr ordering, DAX truncate layout break failures, symlink caching, and directory ioctl gating by protocol minor version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/file.c -->
# sources/distributed-fs/ceph-client/fs/fuse/file.c

## Purpose
`file.c` implements regular-file behavior for the FUSE client: open and release, flush/fsync, cached reads and writes, direct I/O, async direct I/O completion, writeback, mmap, file locking, block mapping, lseek, poll notifications, fallocate, copy-file-range, splice and passthrough dispatch, and regular-file inode initialization. It turns VFS file operations into FUSE requests while coordinating Linux page cache state with the userspace server.

## Important APIs, Types, And Functions
The central object is `struct fuse_file`, allocated by `fuse_file_alloc()` and opened by `fuse_file_open()`/`fuse_do_open()`. It carries the userspace file handle `fh`, kernel handle `kh`, open flags, readdir state, polling RB-tree node, waitqueue, passthrough state, and I/O mode. `fuse_file_put()`, `fuse_prepare_release()`, `fuse_file_release()`, `fuse_release_common()`, and `fuse_sync_release()` own release request preparation and deferred/synchronous lifetime management.

I/O request state is carried by `struct fuse_io_priv`, `struct fuse_io_args`, `struct fuse_args_pages`, and local `struct fuse_writepage_args`. Read helpers include `fuse_read_args_fill()`, `fuse_send_read()`, `fuse_do_readfolio()`, `fuse_send_readpages()`, `fuse_read_folio()`, `fuse_readahead()`, and `fuse_cache_read_iter()`. Write helpers include `fuse_write_args_fill()`, `fuse_send_write()`, `fuse_fill_write_pages()`, `fuse_perform_write()`, `fuse_cache_write_iter()`, `fuse_write_update_attr()`, and the writeback functions `fuse_writepages()`, `fuse_launder_folio()`, `fuse_flush_writepages()`, and `fuse_writepage_end()`.

Direct and async I/O are exposed through exported `fuse_direct_io()` and internal `fuse_direct_IO()`, `fuse_direct_read_iter()`, `fuse_direct_write_iter()`, `fuse_aio_complete()`, and `fuse_aio_complete_req()`. The operation tables are `fuse_file_operations` and `fuse_file_aops`, installed by `fuse_init_file_inode()`.

## Control Flow
Open starts at `fuse_open()`: it rejects bad inodes, runs `generic_file_open()`, handles `atomic_o_trunc` writeback/DAX locking, sends `FUSE_OPEN` via `fuse_do_open()`, completes local open state via `fuse_finish_open()`, and invalidates or truncates page cache based on `FOPEN_KEEP_CACHE` and truncation. `fuse_file_open()` optimizes `-ENOSYS` by marking `no_open`/`no_opendir` and defaulting to keep-cache semantics when the daemon has no open method.

Release starts from VFS `.release` or error paths. `fuse_prepare_release()` removes the file from write and poll tracking, wakes poll waiters, prepares a forced/nocreds `FUSE_RELEASE` or `FUSE_RELEASEDIR`, and optionally holds the inode until the request completes. `fuse_file_put()` delays release until all I/O references are gone, sends release synchronously for required paths or asynchronously in the background otherwise, and has a special no-open fast path.

Cached reads go through `fuse_cache_read_iter()` and page-cache `read_folio`/`readahead` callbacks. Reads may first refresh size when auto-invalidation is enabled or the read crosses EOF. Folio reads build FUSE page requests and mark folios complete through iomap helpers. Short reads are treated as EOF and can shrink local `i_size` when writeback cache is disabled.

Cached writes run `generic_write_checks()`, `kiocb_modified()`, then either direct-write fallback, iomap buffered write for writeback-cache cases, or FUSE page-copy writes via `fuse_perform_write()`. `fuse_perform_write()` copies user data into locked folios, sends `FUSE_WRITE`, handles short writes as `-EIO`, updates `i_size`, and invalidates modsize attributes.

Direct I/O pins/extracts user pages or uses kvec pointers, splits requests by `max_read`/`max_write` and `max_pages`, sends `FUSE_READ`/`FUSE_WRITE` synchronously or through `fuse_simple_background()`, and completes nonblocking kiocbs through `fuse_aio_complete()`. Direct writes use exclusive or shared inode locks depending on `FOPEN_PARALLEL_DIRECT_WRITES`, append, EOF extension, and page-cache I/O mode. Direct-I/O open flags force page-cache writeback/invalidation around the transfer.

Writeback uses iomap writepage callbacks. Dirty folios are grouped into `fuse_writepage_args`, associated with an open write file, optionally counted in the syncfs bucket, queued under `fi->queued_writes`, and submitted while `fi->writectr >= 0`. Completion decrements `writectr`, marks writeback done, records mapping errors, invalidates modification attributes when not using writeback cache, and wakes waiters.

The tail operations are protocol wrappers: `fuse_file_mmap()` dispatches DAX/passthrough/direct-io mmap policy and installs VM ops; locks use `FUSE_GETLK`/`FUSE_SETLK` or local fallback; `fuse_lseek()` uses server `FUSE_LSEEK` for hole/data with fallback; `fuse_file_poll()` registers `kh` in an RB tree for `FUSE_NOTIFY_POLL`; `fuse_file_fallocate()` writes back or invalidates relevant ranges around `FUSE_FALLOCATE`; `__fuse_copy_file_range()` flushes source/destination ranges, tries 64-bit then legacy copy op, truncates destination cache, and falls back to splice on unsupported cases.

## State And Persistence Behavior
Open-file state persists in `struct fuse_file` until the final I/O reference and release request complete. Writeback state persists in `struct fuse_inode` lists (`write_files`, `queued_writes`), `writectr`, `page_waitq`, `direct_io_waitq`, and `iocachectr`. Per-operation state is request-local and is freed on request completion.

The file does not store durable data itself. It preserves coherency between kernel page cache and the userspace daemon through writeback, flush, fsync, release, truncate, and invalidation ordering. It updates `attr_version`, `i_size`, and invalidation masks after successful writes, fallocate, direct I/O, and copy operations so later getattr/cache decisions see local changes.

## Dependencies And Integration Points
`file.c` depends on request construction and connection state from `fuse_i.h`, metadata helpers from `dir.c`/`inode.c`, DAX helpers, passthrough helpers, iomode helpers, ioctl helpers, Linux iomap/page-cache/direct-I/O APIs, VFS locking APIs, pipe splice APIs, file locking APIs, and background request scheduling. `fuse_sync_fs_writes()` in `inode.c` relies on writepage bucket accounting performed here.

## Risks And Edge Cases
Risk centers on cache coherency and lock ordering. Direct I/O must not race with writeback or cached mmap; the code uses inode locks, uncached I/O counters, page-cache invalidation, and `FUSE_I_CACHE_IO_MODE`, but EOF-extending async writes are forced into blocking mode. Writeback can deadlock with reclaim if open-file references or `FUSE_NOWRITE` ordering regress. `copy_file_range()` has a documented partial-page mmap race where modifications outside the copied byte range can be lost after cache truncation.

Short reads/writes, server replies larger than requested, stale size replies under writeback cache, `-ENOSYS` feature downgrades, passthrough/direct-I/O precedence, DAX layout breaks, and release paths that can run in server context are all sensitive edge cases. Poll tracking depends on stable `kh` uniqueness and removal during release.

## Test Signals
High-value coverage includes no-open/no-opendir fallback, `FOPEN_KEEP_CACHE` invalidation behavior, `O_TRUNC` with writeback cache and DAX, flush/fsync error propagation, short-read EOF size update, buffered write short-write failure, async direct I/O completion and short read truncation, parallel direct writes versus mmap/cache mode, writeback congestion and `FUSE_NOWRITE` queue draining, mmap policy for DAX/passthrough/direct-io, POSIX and flock fallback, `SEEK_HOLE`/`SEEK_DATA` fallback, poll notify wakeups, fallocate hole-punch/zero-range invalidation, and copy-file-range 64-bit/legacy/fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/fuse_dev_i.h -->
# sources/distributed-fs/ceph-client/fs/fuse/fuse_dev_i.h

## Purpose
`fuse_dev_i.h` is the internal interface between FUSE core code and the device/request-copy implementation. It defines request ID bit conventions, copy-state bookkeeping for moving request payloads between kernel buffers, userspace iovecs, pipes, and io_uring, and inline accessors for safely recovering the `fuse_dev` and `fuse_conn` behind a `/dev/fuse` file.

## Important APIs, Types, And Functions
`FUSE_INT_REQ_BIT` marks interrupt-request IDs as odd while ordinary requests use even IDs stepped by `FUSE_REQ_ID_STEP`. `struct fuse_copy_state` tracks the request being copied, the active `iov_iter`, pipe buffers, current page, length, offset, direction (`write`), folio moving, io_uring mode, and ring copied size. `FUSE_DEV_FC_DISCONNECTED` is a sentinel stored in `fud->fc` after `/dev/fuse` is closed.

The inline helpers are `fuse_dev_fc_get()`, `fuse_file_to_fud()`, and `__fuse_get_dev()`. Function declarations expose the request and copy operations implemented elsewhere: `fuse_get_dev()`, `fuse_req_hash()`, `fuse_request_find()`, `fuse_dev_end_requests()`, `fuse_copy_init()`, `fuse_copy_finish()`, `fuse_copy_args()`, `fuse_copy_out_args()`, `fuse_dev_queue_forget()`, `fuse_dev_queue_interrupt()`, `fuse_remove_pending_req()`, and `fuse_request_expired()`.

## Control Flow
Callers that operate on a FUSE device file fetch `struct fuse_dev *` from `file->private_data`, then use `fuse_dev_fc_get()` to acquire-load the connection pointer. `__fuse_get_dev()` returns `NULL` if the device has not been installed on a connection, otherwise returns the device. The explicit comment identifies exceptions where the disconnected sentinel matters: `fuse_dev_put()` and `fuse_fill_super_common()` must distinguish an installed live connection from a released device.

Copy operations are declared around `struct fuse_copy_state`: initialize the copy direction and iterator, copy input/output args, finish pipe/vmap/user state, and queue protocol side requests such as forgets or interrupts into the input queue.

## State And Persistence Behavior
The header itself owns no storage except external `fuse_dev_waitq`. Its key persistent contract is the lifetime and memory-ordering model for `fud->fc`: assigned once during mount, valid until file release, then exchanged to `FUSE_DEV_FC_DISCONNECTED`. The acquire load pairs with installation/release stores so request-device users do not dereference a partially installed connection.

## Dependencies And Integration Points
This header depends on `linux/types.h` and forward declarations from `fuse_i.h`. It is included by device code and `inode.c`; `inode.c` uses the sentinel and helpers while installing or putting a `fuse_dev`. Request-copy functions integrate with the FUSE request queues, `/dev/fuse` read/write paths, pipe splice support, and io_uring support.

## Risks And Edge Cases
The most important risk is treating `FUSE_DEV_FC_DISCONNECTED` as a valid connection or assuming lockless access is safe in the documented exceptions. Incorrect request ID parity would break interrupt matching. Copy state is security-sensitive because it moves protocol payloads across kernel/userspace boundaries; wrong length, offset, page pin, or pipe handling can corrupt replies or leak data.

## Test Signals
Useful tests include mount/device install races, `/dev/fuse` close while requests are pending, interrupt request ID matching, forget and interrupt queueing, splice read/write copy paths, io_uring copy accounting, and ensuring callers reject uninstalled or disconnected devices without dereferencing the sentinel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/fuse_dev_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/fuse_i.h -->
# sources/distributed-fs/ceph-client/fs/fuse/fuse_i.h

## Purpose
`fuse_i.h` is the private core header for the FUSE client. It declares the main in-kernel objects (`fuse_conn`, `fuse_mount`, `fuse_inode`, `fuse_file`, request queues, request args, I/O state), feature flags and constants, inline accessors, and cross-file function prototypes. It is the contract binding directory, file, inode, device, ioctl, xattr, ACL, DAX, passthrough, io_uring, and control filesystem code.

## Important APIs, Types, And Functions
Constants define request/page limits, filename limits, control dentries, timeout cadence, `FUSE_NOWRITE`, direct-I/O flags, and statx invalidation masks. `struct fuse_inode` extends `struct inode` with FUSE nodeid, lookup count, FORGET allocation, attribute timeout and invalidation mask, original mode/ino, birth time, attr version, regular-file writeback state, directory readdir-cache state, state bits, serialization locks, optional DAX, submount lookup, passthrough backing, and cached block bits.

`struct fuse_file` stores the connection mount, open/release argument storage, kernel and userspace handles, nodeid, refcount, open flags, writeback linkage, readdir state, poll RB node and waitqueue, I/O mode, passthrough file/cred, and flock state. `struct fuse_args`, `struct fuse_args_pages`, `struct fuse_io_args`, `struct fuse_io_priv`, and `struct fuse_req` define the request construction and completion model. `struct fuse_iqueue`, `struct fuse_pqueue`, and `struct fuse_dev` define pending/processing queues and device instances.

`struct fuse_conn` is the largest state object: it stores locking/refcounting, epoch work, users/namespaces, negotiated maxima, input and background queues, initialization/blocking state, connection feature bits, no-op fallbacks, cache policy, permissions, submount/syncfs/security/passthrough/io_uring flags, wait counters, active mounts/devices, attr/evict counters, timeout work, DAX state, backing maps, and writeback sync buckets. `struct fuse_mount` associates a potentially shared connection with one superblock.

Inline helpers include `get_fuse_mount*()`, `get_fuse_conn*()`, `get_fuse_inode()`, `get_node_id()`, `invalid_nodeid()`, `fuse_get_attr_version()`, `fuse_get_evict_ctr()`, stale/bad inode helpers, folio descriptor allocation/initialization, and `fuse_sync_bucket_dec()`.

## Control Flow
The header does not execute top-level logic but defines the data flow used by the implementation. VFS operations build `struct fuse_args` or `struct fuse_args_pages`, fill opcode/nodeid/input/output arrays, then send through simple or background request helpers. Inode and dentry code use connection feature flags negotiated during `FUSE_INIT` to select protocol operations, local fallback, cache invalidation policy, and permissions model. File code uses `fuse_file` and `fuse_inode` regular-file substate to coordinate open lifetime, cached I/O, direct I/O, writeback, mmap, and syncfs.

The queue model separates pending input (`fuse_iqueue`) from processing (`fuse_pqueue`) and background throttling (`fuse_conn` background fields). Device implementations attach `fuse_dev` instances to a connection and use the input queue ops for normal requests, forgets, and interrupts.

## State And Persistence Behavior
All persistent in-kernel FUSE state described by this subset is declared here. Lookup persistence is `nlookup` plus queued FORGET messages. Metadata persistence is timeout/invalidation/attribute-version state. File persistence is handle/refcount/open flag state. Connection persistence is negotiated capabilities, queue counters, mount/device membership, background congestion limits, timeout policy, and abort/disconnect state.

The header also encodes concurrency expectations: spinlocks protect queue and inode write fields, `killsb` protects mount-list superblock access, refcounts protect files/connections/backing files/submount lookups, and RCU protects connection release and sync buckets.

## Dependencies And Integration Points
`fuse_i.h` includes Linux FUSE UAPI, VFS, mount, wait, memory-management, backing-device, locking, poll, workqueue, xattr, pid/user namespace, and refcount headers. It declares integration points for `dir.c`, `file.c`, `inode.c`, device code, DAX, ioctl, iomode, xattr, ACL, readdir, control filesystem, sysctl, passthrough, and backing-file support.

## Risks And Edge Cases
Because this header is the shared ABI inside the module, layout and semantic changes have broad blast radius. Bitfields in `fuse_conn` are used as negotiated feature and negative-cache state; setting a `no_*` flag too early or too late changes externally visible behavior. The union in `fuse_inode` requires correct mode-specific initialization so regular-file writeback state and directory readdir-cache state are not confused. Request argument arrays have small fixed sizes, so extension insertion must respect bounds. Locking and lifetime comments are part of the correctness contract; violating them risks use-after-free, deadlock, lost FORGETs, or stale cache exposure.

## Test Signals
Test signals include compile coverage across config combinations (`CONFIG_FUSE_DAX`, `CONFIG_FUSE_PASSTHROUGH`, `CONFIG_FUSE_IO_URING`, `CONFIG_BLOCK`, `CONFIG_SYSCTL`), mount negotiation of every feature bit, inode mode initialization, connection abort and refcount release, queue state under background congestion, sync bucket accounting, request timeout behavior, FORGET accounting, passthrough/DAX disabled stubs, and idmapped mount permission combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/fuse_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/fuse_trace.h -->
# sources/distributed-fs/ceph-client/fs/fuse/fuse_trace.h

## Purpose
`fuse_trace.h` defines FUSE tracepoints for request submission and completion. It gives ftrace/perf/BPF users a stable view of connection device ID, request unique ID, opcode, request length, reply length, and reply error for the FUSE protocol operations listed in the local opcode table.

## Important APIs, Types, And Functions
The `OPCODES` macro lists symbolic names for protocol opcodes from `FUSE_LOOKUP` through `FUSE_STATX`, plus `CUSE_INIT`. The file expands that list first into `TRACE_DEFINE_ENUM()` declarations, then into the `__print_symbolic()` table used in trace output. Two `TRACE_EVENT`s are defined: `fuse_request_send` and `fuse_request_end`.

`fuse_request_send` records `connection`, `unique`, `opcode`, and input `len` from `req->fm->fc->dev` and `req->in.h`. `fuse_request_end` records `connection`, `unique`, output `len`, and protocol `error` from `req->out.h`.

## Control Flow
This header is consumed by the Linux tracepoint generation machinery. FUSE request code includes/emits the trace events around the lifecycle of a `struct fuse_req`: when a request is sent to userspace and when it completes. At runtime, tracepoint enablement controls whether the fast assignment and print formatting execute.

## State And Persistence Behavior
No FUSE runtime state is stored here. Trace records are ephemeral diagnostics emitted through the kernel tracing subsystem. The only persistent contract is the mapping between numeric opcodes and printable symbolic names compiled into the tracepoint format.

## Dependencies And Integration Points
The file includes `linux/tracepoint.h`, expects `struct fuse_req` fields from the including translation unit, sets `TRACE_SYSTEM` to `fuse`, and ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` for tracepoint generation. It integrates with request send/end instrumentation in the FUSE device/request implementation.

## Risks And Edge Cases
Trace output can mislead diagnostics if `OPCODES` is not kept in sync with UAPI opcode additions. The trace events dereference `req->fm->fc`, so instrumentation must only be used while the request still holds valid mount/connection references. High-volume tracing on busy FUSE mounts can create significant trace data and perturb timing, especially around request latency investigations.

## Test Signals
Useful checks include building with tracing enabled, verifying `format` files expose the expected fields, enabling `fuse:fuse_request_send` and `fuse:fuse_request_end` during simple filesystem operations, confirming symbolic opcode names print for newer operations such as `FUSE_STATX` and `FUSE_COPY_FILE_RANGE`, and confirming completion errors match userspace daemon replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/fuse_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/inode.c -->
# sources/distributed-fs/ceph-client/fs/fuse/inode.c

## Purpose
`inode.c` implements FUSE module, filesystem, mount, superblock, connection, inode, export, statfs, syncfs, and initialization-negotiation logic. It is the spine that creates `fuse_conn`/`fuse_mount`, parses mount options, installs `/dev/fuse` devices, negotiates protocol features through `FUSE_INIT`, creates and evicts FUSE inodes, handles submounts and NFS export file handles, and tears everything down at unmount/module exit.

## Important APIs, Types, And Functions
Allocation and inode lifecycle are handled by `fuse_alloc_inode()`, `fuse_free_inode()`, `fuse_evict_inode()`, `fuse_init_inode()`, `fuse_iget()`, `fuse_ilookup()`, `fuse_reverse_inval_inode()`, and `fuse_try_prune_one_inode()`. Attribute application is centralized in `fuse_change_attributes_common()`, `fuse_change_attributes_i()`, and `fuse_change_attributes()`, with `fuse_get_cache_mask()` preserving local writeback-cache size/mtime/ctime.

Mount and connection APIs include `fuse_conn_init()`, `fuse_conn_put()`, `fuse_conn_get()`, `fuse_mount_remove()`, `fuse_conn_destroy()`, `fuse_mount_destroy()`, `fuse_fill_super_common()`, `fuse_fill_super()`, `fuse_get_tree()`, and submount-specific `fuse_init_fs_context_submount()`/`fuse_fill_super_submount()`. Device helpers are `fuse_dev_alloc()`, `fuse_dev_install()`, `fuse_dev_alloc_install()`, and `fuse_dev_put()`.

Negotiation is built around `struct fuse_init_args`, `fuse_new_init()`, `fuse_send_init()`, `process_init_reply()`, `process_init_limits()`, and request-timeout setup. Filesystem registration and module lifecycle are handled by `fuse_fs_init()`, `fuse_fs_cleanup()`, `fuse_sysfs_init()`, `fuse_sysfs_cleanup()`, `fuse_init()`, and `fuse_exit()`.

## Control Flow
Mount setup begins with `fuse_init_fs_context()`, which allocates `struct fuse_fs_context` and installs parser ops. `fuse_parse_param()` validates `fd`, `rootmode`, `user_id`, `group_id`, `default_permissions`, `allow_other`, `max_read`, `blksize`, and subtype. `fuse_get_tree()` allocates a new connection and mount, initializes the connection with `/dev/fuse` input queue ops, and either reuses an existing initialized connection for an already-installed device or creates a new nodev/block superblock.

`fuse_fill_super_common()` applies superblock defaults, allocates the syncfs bucket, handles block size and DAX setup, creates a private backing device info, sets mount policy into `fuse_conn`, creates the root inode and dentry, adds the connection to fusectl/global lists, and installs the fuse device if present. `fuse_fill_super()` then sends `FUSE_INIT`.

`fuse_new_init()` advertises supported kernel features. `fuse_send_init()` sends the init request synchronously or in the background depending on `sync_init`. `process_init_reply()` validates protocol major version, processes background limits, interprets feature flags, sets capability bits and no-op fallbacks, configures DAX/passthrough/idmap/io_uring/request-timeout support, adjusts readahead/max write/max pages/name length/time granularity, marks the connection initialized or errored, and wakes waiters blocked on initialization.

Inode lookup flows through `fuse_iget()`: submount points may get unhashed automount inodes with shared `fuse_submount_lookup`; normal inodes use `iget5_locked()` keyed by nodeid, initialize operations by file type, reject stale reused nodeids by marking old inodes bad and retrying, increment `nlookup`, and apply attributes. Eviction truncates pages, clears the inode, queues `FORGET` for accumulated lookups, drops submount lookup references, bumps `evict_ctr` for non-deleted inodes, and asserts regular-file writeback state is clean.

Unmount removes mounts from `fc->mounts`; the last mount sends optional `FUSE_DESTROY`, aborts the connection, waits for abort completion, removes fusectl/global list state, and drops the connection. Module init registers inode caches, fuse/fuseblk filesystems, sysctl, device, sysfs, fusectl, and dentry invalidation; exit reverses those steps.

## State And Persistence Behavior
This file owns the long-lived kernel state for the FUSE client. The inode cache stores `struct fuse_inode`. `fuse_conn_list` and `fuse_mutex` track active connections and fusectl visibility. `fuse_conn` persists negotiated capabilities, queues, device/mount membership, user namespace credentials, request timeout work, syncfs bucket, attr/evict counters, and abort state until all references drop through RCU.

Lookup persistence is maintained through `fi->nlookup` and queued `FORGET` messages. Attribute persistence is timeout/version based; writeback cache causes local size/mtime/ctime to override server replies. Submount lookup state uses shared refcounts to prevent premature final FORGET for auto-submount roots. Syncfs persistence uses a generation bucket so syncfs can wait for writepages submitted before the sync boundary.

## Dependencies And Integration Points
`inode.c` integrates the rest of the FUSE subsystem: `fuse_i.h`, `fuse_dev_i.h`, `dev_uring_i.h`, device operations, dentry operations from `dir.c`, file initialization from `file.c`, xattr handlers, DAX, passthrough backing files, fusectl, sysctl, sysfs, exportfs, fs_context, block-device mounting, pid/user namespaces, and Linux superblock/inode/page-cache APIs.

It registers `fuse_fs_type` and `fuseblk_fs_type`, exposes module aliases, and implements `super_operations` and export operations. It also supplies `fuse_umount_begin()`, `fuse_statfs()`, and `fuse_sync_fs()` to the VFS.

## Risks And Edge Cases
Mount and init negotiation are security-sensitive: `/dev/fuse` must come from the same user namespace, idmapped mounts are only allowed with default permissions, passthrough is refused with writeback cache or invalid stack depth, and unprivileged background limits are capped. Feature-flag interpretation changes behavior across many files, so incorrect negotiation can silently select unsafe cache, permission, DAX, or passthrough modes.

Lifecycle races include device close during mount, reused nodeids, inode eviction racing with lookup/readdirplus replies, submount duplicate roots, abort while background requests are outstanding, and RCU release of connections/mounts/buckets. `fuse_change_attributes_common()` must avoid accepting stale replies across evictions and must not overwrite locally authoritative writeback-cache fields. Module cleanup must flush RCU inode frees before destroying the cache.

## Test Signals
Important tests include mount option validation, wrong user namespace fd rejection, normal fuse and fuseblk mount/unmount, initialized-device remount reuse, FUSE_INIT feature negotiation for each flag, sync and async init paths, background limit clamping for unprivileged users, request timeout setup, root inode creation, nodeid reuse stale-inode behavior, FORGET accounting on eviction, reverse inode invalidation, NFS export handle encode/decode, auto-submount creation and teardown, syncfs bucket waiting, forced unmount abort behavior, DAX/passthrough/idmap combinations, and module init/exit cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/inode.c -->
