# Group Research: group_1162_minix_sources_teaching_minix_minix_servers_vfs_stadir_c_sources_tea_6ca009cd3961

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/stadir.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/stadir.c

## Purpose
Implements VFS system calls for directory context changes and file system status queries: `fchdir`, `chdir`, `chroot`, `stat`, `fstat`, `lstat`, `statvfs1`, `fstatvfs1`, and `getvfsstat`.

## Main Entry Points
- `do_fchdir()` changes `fp->fp_wd` to an already-open file descriptor vnode.
- `do_chdir()` resolves a pathname and changes current working directory.
- `do_chroot()` resolves a pathname and changes root directory; requires `super_user`.
- `do_stat()`, `do_lstat()`, `do_fstat()` forward inode stat requests to the owning FS via `req_stat`.
- `update_statvfs()` refreshes a mount's cached `statvfs` fields from the file server.
- `do_statvfs()`, `do_fstatvfs()` expose mount statistics for a path or fd.
- `do_getvfsstat()` enumerates reportable mounted file systems.

## Control Flow and State
Path-based calls use `fetch_name` or `copy_path`, initialize `struct lookup`, set vmnt/vnode lock requirements, call `eat_path`, perform the operation, then unlock and `put_vnode`. `change_into()` validates that the target vnode is a searchable directory before replacing either `fp_wd` or `fp_rd`.

`fill_statvfs()` either refreshes statistics unless `ST_NOWAIT` is set or uses `vmp->m_stats`; then it overlays VFS-local metadata such as read-only state, fsid, mount path, mount source, and filesystem type before copying to userspace with `sys_datacopy_wrapper`.

## Dependencies
Depends on VFS pathname resolution (`path.h`), filp lookup (`file.h`), vnode/vmnt locks, FS request helpers such as `req_stat` and `req_statvfs`, and MINIX message fields in `job_m_in`.

## Concurrency and Locking
The file consistently takes `VMNT_READ` and `VNODE_READ` locks around resolved path targets. `do_getvfsstat()` intentionally avoids vmnt locking for `ST_NOWAIT` and relies on `VMNT_CANSTAT` to skip transient mounts; it locks only when it may query file servers.

## Risks and Notes
`do_getvfsstat()` skips mounts being mounted/unmounted and PFS. `fill_statvfs()` maps any refresh failure to `EIO`. `change_into()` correctly handles identity replacement by returning early when the target vnode is already the stored directory.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/stadir.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/table.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/table.c

## Purpose
Defines the VFS syscall dispatch table `call_vec`, mapping `VFS_*` call numbers to their implementing `do_*` routines.

## Main Data
- `CALL(n)` converts absolute VFS call numbers into zero-based indices relative to `VFS_BASE`.
- `call_vec[NR_VFS_CALLS]` is a designated-initializer array of function pointers.

## Coverage
The table includes core file operations (`read`, `write`, `open`, `close`), namespace calls (`link`, `unlink`, `rename`, `mkdir`, `rmdir`), metadata calls (`stat`, `fstat`, `lstat`, `chmod`, `chown`, `utimens`), mount/statvfs calls, VM/VFS coordination, driver mapping, and socket operations.

## Dependencies
Includes `fs.h`, MINIX call number headers, and VFS object headers so the function declarations and syscall constants are visible.

## Risks and Notes
This table is central dispatch glue: missing or mismatched call numbers would route syscalls incorrectly. `VFS_RMDIR` deliberately maps to `do_unlink`, implying the unlink implementation distinguishes file and directory removal by call/message context.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/table.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/threads.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/threads.h

## Purpose
Adapts MINIX `mthread` primitives to VFS-local thread, mutex, condition, and attribute names, and defines the per-worker state structure.

## Main Types and Macros
- Aliases `thread_t`, `mutex_t`, `cond_t`, `attr_t` to `mthread_*` types.
- Aliases mutex and condition operations to `mthread_*` functions.
- Defines `struct worker_thread`.

## Worker State
`struct worker_thread` stores:
- thread identity and event synchronization objects,
- current process context `w_fp`,
- input/output messages and saved error code,
- blocked sendrec storage for FS and driver communication,
- current task endpoint and device map pointer,
- `w_next` queue linkage used by the TLL locking queues.

## Dependencies
Includes `<minix/mthread.h>` and forward-declares `struct fproc`.

## Risks and Notes
`w_next` is shared by worker scheduling and TLL wait queues, so lock code assumes a worker is on at most one such queue at a time.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/threads.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/time.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/time.c

## Purpose
Implements `do_utimens`, covering timestamp updates for named paths and file descriptors.

## Main Entry Point
- `do_utimens()` handles `utimens`, `lutimens`, `utimensat` absolute/`AT_FDCWD` cases, and `futimens`.

## Control Flow
The function reads requested atime/mtime from `job_m_in.m_vfs_utimens`. If a name is present, it validates flags, chooses symlink-follow behavior, resolves the path with `eat_path`, and locks the vnode/vmnt for reading. If no name is present, it treats the request as fd-based and uses `get_filp`.

It checks ownership/superuser authorization, allows `UTIME_NOW`/`UTIME_NOW` touch through write permission, rejects read-only mounts, materializes `UTIME_NOW` with `clock_time`, preserves `UTIME_OMIT`, validates nanoseconds, and sends the final request to the file server through `req_utime`.

## Dependencies
Uses path resolution, filp lookup, vnode/vmnt locking, `forbidden`, `read_only`, `clock_time`, and FS request helper `req_utime`.

## Limitations
The header comment explicitly says relative `utimensat(fd, "some/path", ...)` is not implemented.

## Risks and Notes
The code carefully unlocks either the temporary path vnode/vmnt or the fd filp depending on call style. It supplies sensible seconds values for `UTIME_OMIT` to accommodate older file servers.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/time.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/tll.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/tll.c

## Purpose
Implements the VFS three-level lock used by vnode and vmnt objects.

## Lock Modes
- `TLL_READ`: shared read-only access.
- `TLL_READSER`: serialized read access with an owner, allowing concurrent read-only holders.
- `TLL_WRITE`: exclusive write access.
- `TLL_NONE`: unlocked.

## Main Operations
- `tll_init()` initializes lock state and queues.
- `tll_lock()` grants or queues requested access.
- `tll_unlock()` releases access and wakes queued owners.
- `tll_upgrade()` upgrades read-serialized to write-only after readers drain.
- `tll_downgrade()` downgrades write to read-serialized or read-serialized to read-only.
- `tll_islocked()`, `tll_locked_by_me()`, `tll_haspendinglock()` expose lock state.

## Queueing Model
There are two queues:
- `t_write` for write and read-only requests.
- `t_serial` for read-serialized requests.

The implementation is write-biased: if write requests are pending, new read/read-serialized requests queue instead of bypassing. Threads sleep and wake through `worker_wait()` and `worker_signal()`.

## Upgrade/Downgrade Behavior
`TLL_UPGR` marks a read-serialized owner waiting for read-only holders to leave before becoming write-only. `TLL_PEND` marks that a selected owner has been signaled but has not yet resumed and taken its mode. Downgrade can allow a queued read-serialized owner to proceed when no write queue exists.

## Dependencies
Relies on global `self`, `struct worker_thread`, worker wait/signal APIs, and assertions. It is included indirectly by vnode/vmnt lock wrappers.

## Risks and Notes
The lock is non-reentrant for owned modes and returns `EBUSY` when the same worker already owns it. Correctness depends on a worker not being enqueued twice and on `w_next` being reset when ownership changes.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/tll.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/tll.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/tll.h

## Purpose
Declares the three-level-lock types and structure used throughout VFS.

## Main Definitions
- `tll_access_t`: `TLL_NONE`, `TLL_READ`, `TLL_READSER`, `TLL_WRITE`.
- `tll_status_t`: default state, pending upgrade, and pending wake state.
- `tll_t`: current mode, owner, shared reader count, status flags, and two worker queues.

## Dependencies
References `struct worker_thread`, defined in `threads.h`.

## Risks and Notes
The comments describe `TLL_UPGR` as an upgrade marker; the structure comment also mentions pending state. The actual semantics are implemented in `tll.c`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/tll.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/type.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/type.h

## Purpose
Defines shared VFS support data types for file-server communication, cached mount statistics, service mapping, and socket IDs.

## Main Types
- `comm_t`: per-file-server request throttling state, including max/current outstanding requests and queued workers.
- `struct statvfs_cache`: compact cached subset of `struct statvfs`.
- `struct smap`: service map entry for driver endpoints and labels, with select bookkeeping.
- `sockid_t`: signed 32-bit socket identifier.

## Dependencies
Uses MINIX and system scalar types such as `endpoint_t`, `fsblkcnt_t`, `fsfilcnt_t`, `uint64_t`, and `LABEL_MAX`.

## Risks and Notes
The statvfs cache intentionally avoids embedding full `struct statvfs` to save memory per mount entry. The cache is populated by `update_statvfs()` in `stadir.c`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/type.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/utility.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/utility.c

## Purpose
Provides general VFS utilities for path copying, endpoint validation, supplementary group lookup, and safe userspace data copying.

## Main Entry Points
- `copy_path()` copies pathname data from path-style request messages.
- `fetch_name()` copies a pathname from userspace.
- `isokendpt_f()` validates endpoint-to-process table consistency.
- `in_group()` checks whether a group is in an `fproc` supplementary group list.
- `sys_datacopy_wrapper()` wraps kernel data copies with VM fault handling.

## Control Flow
`copy_path()` handles small embedded path buffers directly and delegates larger paths to `fetch_name()`. Both enforce maximum length and trailing NUL checks.

`sys_datacopy_wrapper()` first tries `sys_datacopy_try`. If it gets `EFAULT`, it asks VM to handle the target memory range via `vm_vfs_procctl_handlemem`, then retries the copy.

## Dependencies
Uses global request state (`job_m_in`, `who_e`, `err_code`), `fproc`, endpoint macros, VM/VFS procctl support, and MINIX data-copy calls.

## Risks and Notes
The wrapper assumes one endpoint is VFS/SELF and asserts that invariant after normalizing `VFS_PROC_NR` to `SELF`. Path functions return `EGENERIC` while setting `err_code`, matching surrounding VFS convention.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/utility.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/vmnt.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/vmnt.c

## Purpose
Manages the virtual mount table: initialization, allocation, lookup, lock wrappers, endpoint unmapping, and mount path refresh.

## Main Entry Points
- `init_vmnts()` clears all mount entries and initializes their TLL locks.
- `get_free_vmnt()` finds and resets a free mount table slot.
- `find_vmnt()` locates an in-use mount by FS endpoint.
- `mark_vmnt_free()` marks an entry unused.
- `lock_vmnt()`, `unlock_vmnt()`, `upgrade_vmnt_lock()`, `downgrade_vmnt_lock()` wrap TLL operations.
- `vmnt_unmap_by_endpt()` handles a file-server endpoint disappearing.
- `fetch_vmnt_paths()` refreshes canonical mount paths.

## State Management
`clear_vmnt()` resets endpoint/device, flags, mounted/root vnode pointers, label, and communication counters. A mount is considered free when `m_dev == NO_DEV`.

## Locking
`lock_vmnt()` maps `VMNT_EXCL` to an initial write lock and then upgrades. It rejects attempts by a file server to lock its own mount with `EDEADLK`. Lock-debug builds track read locks in `fp->fp_vmnt_rdlocks`.

## Endpoint Failure Handling
`vmnt_unmap_by_endpt()` marks a mount free, cancels FS communication, invalidates filps by endpoint, and releases the mount point vnode when the mount was successfully attached.

## Path Refresh
`fetch_vmnt_paths()` canonicalizes mount paths, skipping unused mounts and PFS. If canonicalization fails, it temporarily uses the mounted-on vnode as working directory and retries with the mount point basename.

## Risks and Notes
`fetch_vmnt_paths()` temporarily mutates `fp->fp_wd`; callers must assume process context is meaningful. `check_vmnt_locks()` panics if any vmnt remains locked or pending.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/vmnt.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/vmnt.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/vmnt.h

## Purpose
Declares the global virtual mount table and mount flags.

## Main Structure
`struct vmnt` stores:
- file-server endpoint and TLL lock,
- communication throttling state,
- device, mount flags, and FS capability flags,
- mounted-on vnode and root vnode,
- label, mount path, device/source path, filesystem type,
- cached statvfs fields.

## Flags
- `VMNT_READONLY`
- `VMNT_CALLBACK`
- `VMNT_MOUNTING`
- `VMNT_FORCEROOTBSF`
- `VMNT_CANSTAT`

## Lock Mapping
- `VMNT_READ` maps to `TLL_READ`.
- `VMNT_WRITE` maps to `TLL_READSER`.
- `VMNT_EXCL` maps to `TLL_WRITE`.

## Risks and Notes
`VMNT_CANSTAT` is important for `getvfsstat`, which can enumerate mounts without locking when `ST_NOWAIT` is used.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/vmnt.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/vnode.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/vnode.c

## Purpose
Manages VFS vnode table entries, including allocation, lookup, locking, duplication, reference release, and reference cleanup at underlying file servers.

## Main Entry Points
- `init_vnodes()` initializes the vnode table and locks.
- `get_free_vnode()` finds an unused, unlocked vnode slot.
- `find_vnode()` finds an active vnode by FS endpoint and inode number.
- `is_vnode_locked()` checks active or pending lock state.
- `lock_vnode()`, `unlock_vnode()`, `upgrade_vnode_lock()` wrap TLL.
- `dup_vnode()` increments VFS reference count.
- `put_vnode()` drops a vnode reference and sends `req_putnode` when the last VFS reference is gone.
- `vnode_clean_refs()` reduces accumulated FS-side references to one.

## Reference Model
`v_ref_count` tracks VFS users. `v_fs_count` tracks references held at the underlying file server. `put_vnode()` avoids sending a file-server put on every VFS ref decrement; it only sends when VFS refcount reaches zero, or trims excessive FS refs when `v_fs_count > 256`.

Mapped inode references are separately tracked with `v_mapfs_e`, `v_mapinode_nr`, and `v_mapfs_count`, and released from mapped FS when needed.

## Locking
Vnodes use TLL lock modes mapped in `vnode.h`. `put_vnode()` obtains `VNODE_OPCL`, upgrades to exclusive access when releasing the final reference, and asserts that a final put cannot happen while the current worker already owns the lock.

## Debugging
Lock-debug builds provide checks for locks still held by a process and verify the current worker is not left in vnode lock queues.

## Risks and Notes
`get_free_vnode()` only considers slots with zero refs and no lock/pending lock. `put_vnode()` panics on invalid reference counters and logs stack traces if `req_putnode` fails.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/vnode.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/vnode.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/vnode.h

## Purpose
Declares the global vnode table and vnode lock mode aliases.

## Main Structure
`struct vnode` stores:
- owning FS endpoint and optional mapped FS endpoint,
- inode numbers for original and mapped inode,
- mode, owner, group, size,
- VFS and FS reference counters,
- block-special-file endpoint/device information,
- containing device and special-device number,
- owning `struct vmnt`,
- per-vnode TLL lock.

## Lock Mapping
- `VNODE_NONE` maps to `TLL_NONE`.
- `VNODE_READ` maps to `TLL_READ`.
- `VNODE_OPCL` maps to `TLL_READSER`.
- `VNODE_WRITE` maps to `TLL_WRITE`.

## Risks and Notes
The distinction between `v_ref_count`, `v_fs_count`, and `v_mapfs_count` is central to avoiding excessive file-server calls while preserving reference accounting.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/vnode.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/worker.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/worker.c

## Purpose
Implements the VFS worker thread pool, request assignment, pending work handling, thread sleep/wake operations, blocked-send interruption, and special process-context switching for reboot.

## Main Entry Points
- `worker_init()` creates worker threads and synchronization state.
- `worker_cleanup()` shuts workers down for live update.
- `worker_idle()` reports whether no work is pending or busy.
- `worker_allow()` gates processing of new work during initialization.
- `worker_available()` reports free workers, including the spare.
- `worker_can_start()` checks whether normal work can be scheduled for a process.
- `worker_start()` schedules normal or postponed PM work.
- `worker_yield()` yields to workers from the main thread.
- `worker_wait()` and `worker_signal()` provide worker sleep/wake used by TLL.
- `worker_stop()` and `worker_stop_by_endpt()` interrupt blocked FS/driver communication.
- `worker_get()` finds a worker by thread ID.
- `worker_set_proc()` changes current worker process context for reboot-only code.

## Scheduling Model
Each `struct fproc` may have at most one normal job and one postponed PM job. `worker_start()` stores the message and function pointer or PM message, then activates a worker when available. If none can run, the process is marked `FP_PENDING`, and the global `pending` count is incremented.

The pool keeps one spare worker by default for deadlock resolution. Normal work requires at least two available workers unless `use_spare` is true. Callback-style work may use the spare.

## Worker Loop
`worker_main()` binds `self`, repeatedly obtains work, sets global `fp`, locks the process, executes normal work if present, executes postponed PM work if present, runs `thread_cleanup()`, unlocks the process, clears worker ownership, and decrements `busy`.

## Initialization and Cleanup
`worker_init()` configures stack size based on build mode, initializes events, creates `NR_WTHREADS`, and yields to let them sleep. `worker_cleanup()` requires all workers idle, wakes each with no assigned process to terminate, joins them, destroys synchronization objects, and zeroes the worker table.

## Blocking and Wakeup
`worker_sleep()` waits on the worker condition variable and restores `self`. `worker_suspend()` saves error state before a thread blocks; `worker_resume()` restores globals after wake. TLL locks use `worker_wait()`/`worker_signal()`.

## Failure Handling
`worker_stop()` turns blocked FS/driver sendrec storage into `EIO`, clears the blocked pointer, and wakes the worker. `worker_stop_by_endpt()` applies this to workers blocked on a dead endpoint.

## Risks and Notes
The global counters `pending` and `busy` are consistency-critical. `worker_start()` contains multiple panic checks for duplicate jobs or impossible pending/active combinations. `worker_set_proc()` explicitly violates normal threading rules and is restricted to reboot handling.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/worker.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/write.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/write.c

## Purpose
Provides the VFS write syscall entry point as a thin wrapper around shared read/write logic.

## Main Entry Point
- `do_write()` handles `write(fd, buffer, nbytes)`.

## Control Flow
The function rejects requests with nonzero `cum_io`, then delegates to `do_read_write_peek(WRITING, fd, buf, len)` using fields from `job_m_in.m_lc_vfs_readwrite`.

## Dependencies
Includes `fs.h`, `file.h`, and MINIX call numbers. The actual I/O behavior lives in shared read/write code outside this file.

## Risks and Notes
The `cum_io` guard mirrors `do_read()` behavior and prevents unsupported cumulative I/O state from entering the shared write path.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/write.c -->