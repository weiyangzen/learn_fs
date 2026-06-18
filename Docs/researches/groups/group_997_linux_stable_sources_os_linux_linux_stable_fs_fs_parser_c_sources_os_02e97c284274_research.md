# Group Research: group_997_linux_stable_sources_os_linux_linux_stable_fs_fs_parser_c_sources_os_02e97c284274

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`, and every source listed in this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_parser.c -->
# File Research: sources/os/linux/linux-stable/fs/fs_parser.c

## Purpose
Implements the generic VFS filesystem-parameter parser used by the modern mount API. It maps textual or typed `fs_parameter` inputs to filesystem-specific option IDs and converted values.

## Key Interfaces
- `lookup_constant()` searches string-to-integer tables and is exported.
- `__fs_parse()` matches a parameter against an `fs_parameter_spec` table, handles flag negation via `no...`, warns on deprecated parameters, and dispatches type converters.
- `fs_lookup_param()` resolves string/filename parameters to `struct path`, optionally enforcing block-device input.
- Type parsers include bool, u32, s32, u64, enum, string, fd, file-or-string, uid, gid, and blockdev placeholder.
- `fs_validate_description()` optionally checks duplicate parser descriptors under `CONFIG_VALIDATE_FS_PARSER`.

## Design Notes
Flag parameters are represented by a `NULL` type callback, while value parameters call a converter function. Boolean parsing accepts `0/1`, `false/true`, and `no/yes`. UID/GID parsers convert numeric values through `current_user_ns()` and reject invalid mappings.

## Dependencies
Uses `fs_context`, `fs_parser`, VFS path lookup, current user namespace ID mapping, and per-context logging helpers from `internal.h`.

## Research Notes
The file is a central adapter between the syscall-facing mount configuration layer and filesystem-specific option tables. Error reporting is intentionally routed through mount context logging helpers so userspace can read structured diagnostics from the fscontext fd.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_parser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_pin.c -->
# File Research: sources/os/linux/linux-stable/fs/fs_pin.c

## Purpose
Provides infrastructure for pinning filesystem or mount resources and safely killing those pins during unmount or group teardown.

## Key Interfaces
- `pin_insert()` links a `struct fs_pin` into both superblock and mount pin lists.
- `pin_remove()` unlinks a pin, marks it done, and wakes waiters.
- `pin_kill()` coordinates one caller running the pin-specific kill callback while other contenders wait.
- `mnt_pin_kill()` drains all pins attached to a mount.
- `group_pin_kill()` drains all pins attached to a shared hlist, typically superblock-scoped.

## Design Notes
A global `pin_lock` protects list membership. Each pin also has its own waitqueue lock and `done` state:
- `0` means live.
- `-1` means kill in progress.
- positive means removed/completed.

`pin_kill()` is designed to be called while holding RCU read lock; it drops and reacquires RCU around blocking or callback paths.

## Dependencies
Uses VFS mount internals from `mount.h`, `struct fs_pin` from VFS internal headers, spinlocks, hlist operations, RCU, and wait queues.

## Research Notes
This is small but concurrency-sensitive teardown code. The important invariant is that list removal and waitqueue completion must make later drain loops stop without freeing memory while another killer is still waiting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_pin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_struct.c -->
# File Research: sources/os/linux/linux-stable/fs/fs_struct.c

## Purpose
Manages `struct fs_struct`, the per-task filesystem context containing root, current working directory, umask, sharing state, and seqlock protection.

## Key Interfaces
- `set_fs_root()` and `set_fs_pwd()` replace root or cwd path references safely.
- `chroot_fs_refs()` rewrites matching root/cwd references across all tasks when a chroot root is moved.
- `free_fs_struct()` drops path references and frees the object.
- `exit_fs()` detaches a task from its fs context and frees it if the last user exits.
- `copy_fs_struct()` clones root, pwd, umask, and seqlock state for unsharing.
- `unshare_fs_struct()` installs a private copy for the current task.
- `init_fs` defines the boot-time initial fs context.

## Design Notes
Path updates use `write_seqlock()` so lockless readers can retry on concurrent mutation. Task-level changes use `task_lock()`, `tasklist_lock`, and exclusive seqlock sections around shared-user counts.

## Dependencies
Relies on VFS path refcounting, task iteration, task locking, `fs_cachep`, seqlocks, and scheduler task structures.

## Research Notes
The main behavioral contract is correct path reference ownership while `fs_struct` may be shared across threads. `chroot_fs_refs()` deliberately counts replaced references and drops old paths after releasing the task list lock.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fs_struct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fserror.c -->
# File Research: sources/os/linux/linux-stable/fs/fserror.c

## Purpose
Implements generic filesystem error event reporting. Filesystems can report errors to superblock callbacks and fsnotify while keeping event delivery safe from atomic contexts.

## Key Interfaces
- `fserror_mount()` initializes `sb->s_pending_errors` with a bias reference.
- `fserror_unmount()` drops the bias and waits for queued error events to drain.
- `fserror_report()` allocates an event, validates inputs, optionally grabs an inode reference, and schedules worker delivery.
- `fserror_worker()` invokes `sb->s_op->report_error()` if present and sends an `FS_ERROR` fsnotify event.
- `fserror_init()` initializes a mempool for error events.

## Design Notes
Pending events are tracked with a superblock refcount so unmount can wait for asynchronous workers. Events are allocated from a mempool to improve reliability in error paths. Workqueue delivery avoids calling filesystem callbacks or fsnotify from atomic contexts or while locks are held.

## Dependencies
Uses `fsnotify`, superblock operations, inode refcounting, workqueues, mempools, and `linux/fserror.h`.

## Research Notes
Lost reports are ratelimited to the kernel log. The code assumes reported `error` values are negative and warns if inode and superblock do not belong together.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fserror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fsopen.c -->
# File Research: sources/os/linux/linux-stable/fs/fsopen.c

## Purpose
Implements the modern mount API syscalls for creating, configuring, reading diagnostics from, and applying filesystem contexts.

## Key Interfaces
- `fscontext_read()` returns one queued log message per read from an fscontext fd.
- `fscontext_release()` drops the held `fs_context`.
- `fsopen()` opens a filesystem type by name, creates a mount context, allocates a log, and returns an anonymous fd.
- `fspick()` picks an existing mount root for superblock reconfiguration.
- `fsconfig()` validates command/value combinations, imports user parameters, locks the context, and applies configuration or lifecycle commands.
- `vfs_cmd_create()` transitions a creation context through tree construction and mount security checks.
- `vfs_cmd_reconfigure()` locks the target superblock and calls `reconfigure_super()`.

## Design Notes
The fscontext fd is an anonymous inode whose private data owns the `fs_context`. `fc->uapi_mutex` serializes userspace operations. Context phases enforce legal ordering: parameter collection, creating, awaiting mount, reconfiguring, failed, and cleaned states.

## Dependencies
Uses `fs_context`, `fs_parser`, anonymous inodes, fd helpers, VFS path lookup, security hooks, mount internals, and `uapi/linux/mount.h`.

## Research Notes
`fsconfig()` supports flags, strings, binary blobs, paths, empty paths, and fd parameters. It carefully cleans imported user memory unless the filesystem or LSM steals ownership by nulling the parameter pointer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fsopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/fuse/Kconfig

## Purpose
Defines kernel configuration options for FUSE, CUSE, virtiofs, DAX, passthrough, and io_uring-based FUSE communication.

## Options
- `FUSE_FS`: main Filesystem in Userspace support; selects POSIX ACL and iomap support.
- `CUSE`: character devices in userspace; depends on `FUSE_FS`.
- `VIRTIO_FS`: host/guest filesystem sharing over virtio; depends on `FUSE_FS` and selects `VIRTIO`.
- `FUSE_DAX`: direct host memory access for virtiofs; depends on virtiofs, FS_DAX, and DAX; selects interval trees.
- `FUSE_PASSTHROUGH`: maps selected FUSE operations to backing files; selects `FS_STACK`.
- `FUSE_IO_URING`: enables FUSE request transport through io_uring; depends on `FUSE_FS` and `IO_URING`.

## Design Notes
The default-enabled booleans for DAX, passthrough, and io_uring expose optional acceleration paths when their dependencies are present.

## Dependencies
References documentation under `Documentation/filesystems/fuse/fuse.rst` and depends on broader VFS, virtio, DAX, and io_uring subsystems.

## Research Notes
This file establishes which companion objects in the FUSE Makefile participate in the build.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/fuse/Makefile

## Purpose
Builds the FUSE kernel objects and conditionally includes optional feature modules.

## Build Composition
- `obj-$(CONFIG_FUSE_FS) += fuse.o`
- `obj-$(CONFIG_CUSE) += cuse.o`
- `obj-$(CONFIG_VIRTIO_FS) += virtiofs.o`
- `fuse-y` starts with `trace.o` so ftrace errors surface early.
- Core FUSE objects include device, directory, file, inode, control, xattr, ACL, readdir, ioctl, and iomode support.
- Conditional objects:
  - `dax.o` for `CONFIG_FUSE_DAX`
  - `passthrough.o backing.o` for `CONFIG_FUSE_PASSTHROUGH`
  - `sysctl.o` for `CONFIG_SYSCTL`
  - `dev_uring.o` for `CONFIG_FUSE_IO_URING`
- `virtiofs-y := virtio_fs.o`

## Design Notes
The file keeps the main FUSE module as a composite object while CUSE and virtiofs are separate module targets.

## Dependencies
Uses kernel kbuild conventions and adds `ccflags-y = -I$(src)` for trace event headers.

## Research Notes
The grouped files map directly to these feature gates: ACL is always part of FUSE, backing is passthrough-only, DAX is DAX-only, and dev_uring is io_uring-only.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/acl.c

## Purpose
Implements POSIX ACL get/set support for FUSE in terms of xattr operations and FUSE connection capabilities.

## Key Interfaces
- `fuse_get_acl()` handles VFS dentry-based ACL retrieval.
- `fuse_get_inode_acl()` supports inode ACL checks, including RCU rejection with `-ECHILD`.
- `fuse_set_acl()` serializes ACLs to xattr format, sets or removes ACL xattrs, and invalidates cached ACL/attribute state when appropriate.

## Design Notes
`__fuse_get_acl()` reads `system.posix_acl_access` or `system.posix_acl_default` through `fuse_getxattr()` into a page-sized buffer and converts it with `posix_acl_from_xattr()`. The helper returns `NULL` for absent ACLs and maps `-ERANGE` to `-E2BIG`.

Backward compatibility is explicit: daemons without `FUSE_POSIX_ACL` can still expose ACL xattrs without kernel permission-check participation, especially outside `init_user_ns`.

## Dependencies
Uses FUSE xattr helpers, POSIX ACL conversion helpers, user namespace mapping, `forget_all_cached_acls()`, and `fuse_invalidate_attr()`.

## Research Notes
When setting ACLs under true POSIX ACL support, the code may request setgid stripping with `FUSE_SETXATTR_ACL_KILL_SGID` unless the caller is in the inode group or capable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/backing.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/backing.c

## Purpose
Manages FUSE passthrough backing-file registrations. A privileged FUSE daemon can map operations for specific FUSE files directly to kernel backing files.

## Key Interfaces
- `fuse_backing_get()` and `fuse_backing_put()` manage `struct fuse_backing` refcounts.
- `fuse_backing_files_init()` initializes the connection IDR.
- `fuse_backing_files_free()` frees all remaining backing mappings during connection cleanup.
- `fuse_backing_open()` validates a userspace fd and allocates a backing ID.
- `fuse_backing_close()` removes a backing ID and drops its reference.
- `fuse_backing_lookup()` performs RCU-safe ID lookup and ref acquisition.

## Design Notes
Backing IDs are allocated cyclically from an IDR starting at `1`; `0` is treated as invalid. Open requires `fc->passthrough` and `CAP_SYS_ADMIN`, rejects flags/padding, requires a regular non-directory file, and prevents stack-depth loops by comparing the backing superblock depth against `fc->max_stack_depth`.

## Dependencies
Uses `struct file`, raw fd lookup, credentials, IDR, RCU, FUSE connection locking, and optional `CONFIG_FUSE_PASSTHROUGH`.

## Research Notes
A FIXME notes xarray might be space inefficient. There is also a TODO to relax `CAP_SYS_ADMIN` once backing files are visible to tools such as `lsof`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/backing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/control.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/control.c

## Purpose
Implements the `fusectl` pseudo-filesystem exposing per-connection control and monitoring files.

## Key Interfaces
- `fuse_ctl_add_conn()` creates a directory named by connection device ID with files `waiting`, `abort`, `max_background`, and `congestion_threshold`.
- `fuse_ctl_remove_conn()` removes a connection directory.
- `fuse_conn_abort_write()` aborts a connection when userspace writes to `abort`.
- `fuse_conn_waiting_read()` reports pending request count.
- Limit read/write helpers expose and update `max_background` and `congestion_threshold`.
- `fuse_ctl_init()` and `fuse_ctl_cleanup()` register/unregister the `fusectl` filesystem.

## Design Notes
A single global `fuse_control_sb` exists while `fusectl` is mounted and is protected by `fuse_mutex`. Control dentries use persistent simplefs-style dentries and store `struct fuse_conn *` in `inode->i_private`. Accessors take a connection reference under `fuse_mutex`.

## Dependencies
Uses simple filesystem helpers, FUSE global connection list, `fuse_mutex`, VFS fs_context operations, capability checks, and FUSE background throttling fields.

## Research Notes
Non-privileged writes to limits are capped by global user limits, while privileged callers can set up to the 16-bit maximum. Updating `max_background` also recomputes blocked state and wakes blocked waiters if capacity opens.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/control.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/cuse.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/cuse.c

## Purpose
Implements CUSE, which lets a userspace server provide character devices through the FUSE request protocol.

## Key Interfaces
- Frontend device ops route `read_iter`, `write_iter`, `ioctl`, `poll`, `open`, and `release` through FUSE direct I/O and file operations.
- `cuse_channel_open()` opens `/dev/cuse`, allocates a `cuse_conn`, initializes an embedded FUSE connection, installs a FUSE device, and sends `CUSE_INIT`.
- `cuse_process_init_reply()` handles the daemon’s init reply, parses device metadata, reserves a character device number, creates the device, adds the cdev, and publishes it.
- `cuse_channel_release()` removes the device and releases the FUSE channel.
- Module init creates the `cuse` class and miscdevice.

## Design Notes
CUSE stores active connections in a hash table keyed by device number, protected by `cuse_lock`. Opening the created character device looks up the connection, takes a FUSE connection reference, and performs a FUSE open. The init info parser accepts packed NUL-separated key/value strings and currently requires `DEVNAME`.

## Dependencies
Uses FUSE device infrastructure, miscdevice, cdev, device model, user namespaces, direct I/O, ioctl support, and sysfs device attributes.

## Research Notes
The code explicitly disables `FUSE_DEV_IOC_CLONE` for CUSE. Device availability is announced only after the cdev and device are fully installed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/cuse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dax.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/dax.c

## Purpose
Implements FUSE/virtiofs DAX support, mapping host page-cache memory into the guest address space and bypassing the guest page cache for eligible files.

## Key Structures
- `fuse_dax_mapping`: one DAX window range with inode, interval-tree node, busy/free list links, window offset, length, writability, and refcount.
- `fuse_inode_dax`: per-inode interval tree protected by an rwsem.
- `fuse_conn_dax`: per-connection DAX device, free/busy range lists, reclaim worker, waitqueue, and range counters.

## Key Interfaces
- Mapping setup/removal: `fuse_setup_one_mapping()`, `fuse_send_removemapping()`, `dmap_removemapping_list()`.
- Iomap integration: `fuse_iomap_begin()`, `fuse_iomap_end()`, `fuse_iomap_ops`.
- I/O paths: `fuse_dax_read_iter()`, `fuse_dax_write_iter()`, `fuse_dax_mmap()`, fault handlers.
- Reclaim: inline reclaim, worker reclaim, layout breaking, writeback/invalidation, and busy/free pool management.
- Lifecycle: `fuse_dax_conn_alloc()`, `fuse_dax_conn_free()`, `fuse_dax_inode_alloc()`, `fuse_dax_inode_cleanup()`, `fuse_dax_cancel_work()`.

## Design Notes
DAX ranges default to 2 MiB. Per-inode mappings are indexed by file-offset range and point into the connection DAX window. Read-only mappings can be upgraded to writable. Refcounts prevent reclaim while iomap/fault users hold a mapping. Reclaim takes `mapping->invalidate_lock`, breaks DAX layouts, invalidates page cache ranges, sends `FUSE_REMOVEMAPPING`, and returns mappings to the free pool.

## Dependencies
Uses DAX, iomap, interval trees, folios/page cache invalidation, FUSE setup/removemapping protocol messages, delayed work, and virtiofs-provided `dax_device`.

## Research Notes
File-extending writes deliberately fall back to FUSE direct I/O because DAX write and on-disk size extension are not atomic here. Fault-path allocation returns `-EAGAIN` rather than performing inline reclaim while invalidate locks are held.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dev.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/dev.c

## Purpose
Implements `/dev/fuse`, the core kernel/userspace transport for FUSE requests, replies, notifications, abort handling, request lifetime, splice support, background throttling, and miscdevice registration.

## Key Areas
- Request lifecycle: allocation, initialization, unique ID assignment, refcounting, waiting, interruption, completion, and freeing.
- Queues: input queue `fuse_iqueue`, per-device processing queue `fuse_pqueue`, background queue, forget queue, interrupt queue, and io_uring integration hooks.
- Userspace read path: `fuse_dev_do_read()` dequeues interrupts, forgets, or normal requests and copies request headers/args to userspace.
- Userspace write path: `fuse_dev_do_write()` parses reply headers, routes notifications, finds processing requests, copies output args, and completes requests.
- Copy engine: `fuse_copy_state`, page/folio copying, pipe splice support, optional folio stealing for page replacement.
- Notifications: poll wakeup, inode/entry invalidation, delete, store, retrieve, resend, epoch increment, and prune.
- Teardown: `fuse_abort_conn()`, `fuse_wait_aborted()`, `fuse_dev_release()`, request draining, poll wakeups, io_uring abort coordination.
- Ioctls: clone, passthrough backing open/close, and sync init.

## Design Notes
Foreground requests wait on per-request waitqueues; background requests are throttled by `max_background` and `active_background`. Interrupts are sent as special synthetic requests. Forget messages can be batched for protocol minor >= 16. Request timeout scanning checks pending, background, processing, and io_uring queues and aborts on expiry.

## Dependencies
Uses miscdevice, VFS file operations, pipes/splice, page cache/folios, FUSE protocol definitions, tracepoints, io_uring hooks, passthrough backing support, and proc fdinfo.

## Research Notes
This is the central synchronization point for FUSE. Lock ordering is carefully managed between connection locks, queue locks, request waitqueue locks, and copy operations that can fault. `FR_LOCKED`, `FR_ABORTED`, `FR_SENT`, `FR_PENDING`, and related flags are the primary request-state contract.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dev_uring.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/dev_uring.c

## Purpose
Implements optional FUSE communication over io_uring, replacing the traditional split read/write `/dev/fuse` exchange with registered ring entries and `COMMIT_AND_FETCH` commands.

## Key Interfaces
- `fuse_uring_enabled()` reports the module parameter `enable_uring`.
- `fuse_uring_cmd()` handles io_uring passthrough commands: register and commit/fetch.
- `fuse_uring_register()` creates or finds the ring and queue, validates userspace iovecs, and registers a ring entry.
- `fuse_uring_commit_fetch()` commits the previous reply for a request and immediately fetches the next request into the same entry.
- `fuse_uring_queue_fuse_req()` queues foreground requests to a CPU-local ring queue.
- `fuse_uring_queue_bq_req()` queues background requests with per-queue dispatch.
- `fuse_uring_abort_end_requests()`, `fuse_uring_stop_queues()`, and async teardown handle abort/shutdown.
- `fuse_uring_request_expired()` extends timeout detection to io_uring queues.

## Design Notes
The ring has one queue per possible CPU. Each queue owns available entries, entries with assigned requests, commit entries, userspace entries, released entries, foreground request queue, background request queue, and a FUSE processing queue for commit lookup.

Ring entries move through explicit states: commit, available, assigned FUSE request, userspace, teardown, and released. Registration only marks the ring ready after all queues have at least one available entry, then switches `fiq->ops` to io_uring operations and wakes blocked request allocation.

## Dependencies
Uses `io_uring_cmd`, FUSE copy helpers from `dev.c`, FUSE request/queue primitives, per-CPU task CPU selection, user iovec import, and connection abort logic.

## Research Notes
Notifications and interrupt replies are not fully transported through io_uring yet; forget and interrupt ops still use legacy queue helpers. Teardown intentionally delays freeing entries because io_uring cancellation may still hold direct entry pointers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dev_uring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dev_uring_i.h -->
# File Research: sources/os/linux/linux-stable/fs/fuse/dev_uring_i.h

## Purpose
Defines private structures, states, declarations, and no-op fallbacks for the FUSE io_uring transport.

## Key Definitions
- `FUSE_URING_TEARDOWN_TIMEOUT` and `FUSE_URING_TEARDOWN_INTERVAL` control async teardown polling.
- `enum fuse_ring_req_state` defines entry lifecycle states: invalid, commit, available, assigned request, userspace, teardown, and released.
- `struct fuse_ring_ent` stores userspace header/payload pointers, owning queue, io_uring command, list node, state, and assigned FUSE request.
- `struct fuse_ring_queue` stores queue ID, lock, entry lists, request queues, embedded processing queue, active background count, and stopped flag.
- `struct fuse_ring` stores connection backpointer, queue count, max payload size, queue array, teardown/debug state, stop waitqueue, queue refcount, and readiness flag.

## Exported Internal API
When `CONFIG_FUSE_IO_URING` is enabled, it declares enablement, destruction, queue stop, abort completion, command handling, foreground/background queueing, pending removal, and timeout helpers. Inline helpers integrate abort and stopped-queue waiting with core `dev.c`.

## Fallback Behavior
When io_uring support is disabled, all helpers become no-ops or return false, preserving build-time compatibility for the core FUSE device code.

## Dependencies
Includes `fuse_i.h` and relies on structures defined by FUSE core plus io_uring command types when enabled.

## Research Notes
This header makes `dev.c` mostly feature-agnostic: core request allocation, timeout, abort, and wait paths can call io_uring hooks unconditionally while compilation removes them when disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/dev_uring_i.h -->