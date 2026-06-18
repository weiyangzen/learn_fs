# Group Research: group_697_linux_sources_os_linux_linux_fs_afs_yfsclient_c_sources_os_linux_lin_728acbfa278f

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/afs/yfsclient.c -->
# File Research: sources/os/linux/linux/fs/afs/yfsclient.c

## Summary
Implements YFS file-server client RPC stubs for the Linux AFS client. It marshals YFS requests, unmarshals replies, updates AFS operation status/callback state, and provides YFS variants of file, directory, lock, volume-status, and ACL operations.

## Main Responsibilities
- Encode/decode YFS XDR primitives, FIDs, store status records, timestamps, callbacks, volume status, and file status.
- Build and issue YFS RPC calls through `afs_alloc_flat_call()` and `afs_make_op_call()`.
- Deliver replies for fetch/store/status/mutation/lock/ACL operations.
- Handle server capability downgrade for `RemoveFile2` and extended rename operations.
- Support streaming data extraction for `YFS.FetchData64`.
- Support opaque ACL fetch/store operations.

## Key APIs
- `yfs_fs_fetch_data()`, `yfs_fs_store_data()`.
- `yfs_fs_create_file()`, `yfs_fs_make_dir()`, `yfs_fs_remove_file()`, `yfs_fs_remove_dir()`.
- `yfs_fs_link()`, `yfs_fs_symlink()`, `yfs_fs_rename()`, `yfs_fs_rename_replace()`, `yfs_fs_rename_noreplace()`, `yfs_fs_rename_exchange()`.
- `yfs_fs_setattr()`, `yfs_fs_fetch_status()`, `yfs_fs_inline_bulk_status()`.
- `yfs_fs_get_volume_status()`.
- `yfs_fs_set_lock()`, `yfs_fs_extend_lock()`, `yfs_fs_release_lock()`.
- `yfs_fs_fetch_opaque_acl()`, `yfs_fs_store_opaque_acl2()`, `yfs_free_opaque_acl()`.

## Important Behavior
YFS timestamps are 64-bit 100ns units and are converted to/from Linux `timespec64`, with special handling for negative values on 32-bit builds.

`YFS.FetchData64` is delivered as a multi-stage state machine: length, data into the netfs subrequest iterator, excess discard, then status/callback/volsync metadata. EOF is marked when transferred bytes reach the returned status size.

Create, mkdir, symlink, link, remove, rename, store, setattr, lock, and status calls use hand-computed request and reply sizes. `yfs_check_req()` warns if the encoded request length does not exactly match the allocated buffer.

`yfs_fs_remove_file()` first tries `YFS.RemoveFile2` unless the server is marked as lacking it. `yfs_done_fs_remove_file2()` sets `AFS_SERVER_FL_NO_RM2` and marks the operation for downgrade on unsupported-op aborts.

`yfs_fs_rename()` similarly prefers `YFS.Rename_Replace` unless the server is marked `AFS_SERVER_FL_NO_RENAME2`; the extended rename paths can return displaced target status.

## State and Lifetime
The file operates around `struct afs_operation`, `struct afs_call`, `struct afs_vnode_param`, status/callback records, and operation-specific embedded state. ACL fetch allocates `struct afs_acl` buffers into `op->yacl`; `yfs_free_opaque_acl()` owns cleanup.

## Risks
XDR sizes, padding, and decode order are manually maintained and must match the protocol exactly. The streaming fetch path mutates `call->iter`, `iov_len`, `remaining`, and netfs subrequest counters across delivery states. ACL lengths come from the server and drive allocations after rounding. Feature downgrade depends on correctly interpreting RX abort codes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/afs/yfsclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/aio.c -->
# File Research: sources/os/linux/linux/fs/aio.c

## Summary
Implements Linux native asynchronous I/O syscalls and their completion ring infrastructure. It manages AIO contexts, ring mmap setup, request accounting, cancellation, completion delivery, polling, fsync work, compat syscalls, and teardown.

## Main Responsibilities
- Provide `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, and `io_pgetevents`.
- Allocate `kioctx` contexts and map userspace-visible completion rings.
- Maintain per-mm RCU-protected AIO context tables.
- Track global and per-context request limits.
- Submit read/write, vectored read/write, fsync/fdsync, and poll requests.
- Deliver completions into shared rings and optionally signal eventfds.
- Cancel active requests and destroy contexts on `io_destroy()` or `exit_aio()`.

## Key APIs
- Syscalls: `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, `io_pgetevents`, plus compat/time32 variants.
- Internal lifecycle: `ioctx_alloc()`, `kill_ioctx()`, `exit_aio()`, `lookup_ioctx()`.
- Request helpers: `aio_get_req()`, `iocb_put()`, `aio_complete()`, `aio_complete_rw()`.
- Operation handlers: `aio_read()`, `aio_write()`, `aio_fsync()`, `aio_poll()`.
- Exported helper: `kiocb_set_cancel_fn()`.

## Important Behavior
AIO rings are backed by an internal pseudo filesystem and an anonymous file mapped into the caller’s address space. The userspace handle is the mmap base address; lookup reads the ring id from userspace and verifies it against the current mm’s context table.

Ring slots are protected by a batched per-cpu `reqs_available` scheme. Completions update the kernel tail and userspace ring tail under `completion_lock`, then wake waiters whose `min_nr` is satisfied.

Request lifetime uses two references: one for the async completion path and one for synchronous submission cleanup. Context lifetime uses percpu refs for users and outstanding requests, with final freeing deferred through RCU work.

Poll AIO uses waitqueue entries, RCU protection for `wake_up_pollfree()`, cancellation callbacks, and optional workqueue completion when inline completion is unsafe.

## State and Synchronization
Uses `mm->ioctx_lock`, RCU, percpu refs, `ctx_lock`, `ring_lock`, `completion_lock`, waitqueues, hrtimers, workqueues, eventfd references, file references, and page migration hooks. Ring folio migration is serialized with `ring_lock`, `migrate_lock`, and `completion_lock`.

## Risks
This is concurrency-heavy legacy infrastructure. Correctness depends on precise ordering between userspace ring head/tail, completion writes, request-slot refill, context table removal, cancellation, poll waitqueue freeing, and RCU-delayed context free. The userspace ring head is intentionally trusted only after clamping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/aio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/anon_inodes.c -->
# File Research: sources/os/linux/linux/fs/anon_inodes.c

## Summary
Provides the anonymous-inode pseudo filesystem and helper APIs for kernel subsystems that need file descriptors without persistent filesystem objects.

## Main Responsibilities
- Mount `anon_inodefs` during early fs init.
- Maintain a singleton anonymous inode for normal anon-inode files.
- Allocate secure per-file anonymous inodes when LSM labeling or unique inode identity is needed.
- Create anonymous `struct file` objects and install them into file descriptors.
- Preserve legacy userspace `stat()` behavior for anon inodes.

## Key APIs
- `anon_inode_getfile()`, `anon_inode_getfile_fmode()`.
- `anon_inode_create_getfile()`.
- `anon_inode_getfd()`, `anon_inode_create_getfd()`.
- `anon_inode_make_secure_inode()`.
- `anon_inode_getattr()`, `anon_inode_setattr()`.

## Important Behavior
Normal anon-inode files share one inode, reducing memory and setup overhead. Secure/unique anon-inode creation allocates a fresh inode, clears `S_PRIVATE`, installs anon inode operations, and calls `security_inode_init_security_anon()`.

`anon_inode_getattr()` masks file-type bits from `st_mode` so legacy userspace tools continue to recognize `anon_inode` objects as before.

`__anon_inode_getfile()` pins the file-operations module owner before allocating the file and drops that reference on error.

## Risks
Callers choosing the singleton path share inode identity and security context. Callers needing LSM policy or distinct `fstat()` identity must use the create APIs. The `context_inode` passed to the LSM hook is not refcounted by this helper.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/anon_inodes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/attr.c -->
# File Research: sources/os/linux/linux/fs/attr.c

## Summary
Implements generic VFS attribute-change validation and update helpers for chmod/chown/truncate/time changes.

## Main Responsibilities
- Decide when setuid/setgid bits should be dropped.
- Validate ownership, group, mode, timestamp, size, immutable, append-only, verity, and swapfile constraints.
- Copy simple attribute updates into inodes.
- Handle idmapped mount permission and mapping checks.
- Drive `notify_change()` security hooks, delegation breaking, filesystem `setattr`, and fsnotify.

## Key APIs
- `setattr_should_drop_sgid()`, `setattr_should_drop_suidgid()`.
- `setattr_prepare()`.
- `inode_newsize_ok()`.
- `setattr_copy()`.
- `may_setattr()`.
- `notify_change()`.

## Important Behavior
`setattr_prepare()` checks truncation limits first, then owner/group/mode/time permissions unless `ATTR_FORCE` is set. It can invoke `security_inode_killpriv()` for `ATTR_KILL_PRIV`.

`inode_newsize_ok()` rejects negative sizes, enforces `RLIMIT_FSIZE` and `s_maxbytes` on extension, sends `SIGXFSZ` when appropriate, and rejects truncation of in-use swapfiles.

`setattr_copy()` updates uid/gid/mode and timestamps but intentionally does not update inode size or mark the inode dirty. Multigrain timestamp inodes use `setattr_copy_mgtime()` to keep ctime ordering coherent.

`notify_change()` rejects chmod on symlinks, truncates requested timestamps to filesystem granularity, handles privilege and setid stripping, validates idmapped uid/gid mappings, runs LSM hooks, breaks delegations unless `ATTR_DELEG` is set, calls filesystem `->setattr` or `simple_setattr`, then sends fsnotify and post-setattr security notification.

## Risks
Callers must hold the inode `i_rwsem` exclusively for `notify_change()` and `setattr_copy()`. Attribute flags have subtle interactions, especially `ATTR_MODE` with `ATTR_KILL_SUID/SGID`, idmapped mounts, invalid uid/gid mappings, multigrain timestamps, and delegation retry handling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/Kconfig -->
# File Research: sources/os/linux/linux/fs/autofs/Kconfig

## Summary
Defines the kernel configuration option for autofs support.

## Main Contents
- `AUTOFS_FS`: tristate kernel automounter support for protocol versions 3, 4, and 5.

## Important Behavior
The help text describes autofs as a partially kernel-based automounter intended to reduce overhead for already-mounted paths, requires userspace automounter tools, and builds the module as `autofs` when selected as `M`.

## Risks
No runtime logic. The option enables a filesystem module with daemon coordination through control pipes and ioctls.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/Makefile -->
# File Research: sources/os/linux/linux/fs/autofs/Makefile

## Summary
Builds the autofs filesystem module.

## Main Contents
- `obj-$(CONFIG_AUTOFS_FS) += autofs4.o`.
- `autofs4-objs := init.o inode.o root.o symlink.o waitq.o expire.o dev-ioctl.o`.

## Important Behavior
The built object name remains `autofs4.o` while the module aliases and filesystem type expose `autofs`.

## Risks
No runtime logic. Build composition must stay in sync with exported symbols across the autofs source files.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/autofs_i.h -->
# File Research: sources/os/linux/linux/fs/autofs/autofs_i.h

## Summary
Internal autofs header defining shared state, flags, helpers, and cross-file declarations for the autofs filesystem.

## Main Contents
- `struct autofs_info`: per-dentry/inode state, active/expiring list nodes, requester uid/gid, expiry state, and counters.
- `struct autofs_wait_queue`: daemon wait token, path identity, requester credentials/pids, status, and wait counter.
- `struct autofs_sb_info`: per-superblock control pipe, daemon process group, protocol version, mount type, flags, wait queues, and active/expiring lists.
- Helpers for oz-mode detection, pipe validation/preparation, managed dentry flags, device/inode ids, and expiring-list management.
- Declarations for init, inode, root, symlink, waitq, expire, and misc-device ioctl code.

## Important Behavior
`autofs_oz_mode()` identifies the automount daemon process group or catatonic state. In oz mode the daemon can see/manipulate the raw autofs filesystem without triggering automount behavior.

Managed dentry helpers toggle `DCACHE_NEED_AUTOMOUNT` and `DCACHE_MANAGE_TRANSIT`, which tie autofs dentries into VFS path walking.

Pipe helpers require a writable FIFO, force packet mode through `O_DIRECT`, and clear `O_NONBLOCK`.

## Risks
Most autofs correctness depends on the flags in this header: `PENDING`, `WANT_EXPIRE`, `EXPIRING`, and per-dentry expire timeout state. The active and expiring lists are protected by `lookup_lock`; filesystem state flags use `fs_lock`; wait queues use `wq_mutex`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/autofs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/dev-ioctl.c -->
# File Research: sources/os/linux/linux/fs/autofs/dev-ioctl.c

## Summary
Implements `/dev/autofs`, a misc-device ioctl interface for controlling autofs mounts even when their mountpoints are covered by other mounts.

## Main Responsibilities
- Validate and copy `struct autofs_dev_ioctl` requests from userspace.
- Open/close ioctl file descriptors for specific autofs mounts.
- Release wait tokens as ready or failed.
- Reconnect catatonic mounts to a new daemon pipe.
- Put mounts into catatonic mode.
- Set global or per-dentry expire timeouts.
- Query requester uid/gid, protocol versions, expire candidates, umountability, and mountpoint status.

## Key APIs
- `autofs_dev_ioctl_init()`, `autofs_dev_ioctl_exit()`.
- ioctl handlers: version, protover, protosubver, openmount, closemount, ready, fail, setpipefd, catatonic, timeout, requester, expire, askumount, ismountpoint.

## Important Behavior
`copy_dev_ioctl()` copies a variable-sized control structure with an optional path tail, bounded by `PATH_MAX`. `validate_dev_ioctl()` checks interface version, path termination, and command-specific path requirements.

Most commands require `CAP_SYS_ADMIN`; version and ismountpoint are exceptions. Commands that operate on a mount validate the supplied fd points to `autofs_fs_type` and that the caller is oz-mode, except catatonic transition.

`setpipefd` only works when the mount is catatonic and refuses PID namespace changes. It prepares the new FIFO pipe, swaps daemon process group ownership, records the caller’s mount namespace id, and clears catatonic mode.

`ismountpoint` supports both fd-relative checks and path-only checks, returning mountpoint status plus encoded device and superblock magic.

## Risks
This file is a privileged control surface. Correctness depends on strict ioctl version/path validation, `array_index_nospec()` for table dispatch, mount fd type checks, oz-mode enforcement, and careful reconnect semantics for catatonic mounts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/dev-ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/expire.c -->
# File Research: sources/os/linux/linux/fs/autofs/expire.c

## Summary
Implements autofs expiration selection and synchronization for direct, indirect, tree, leaf, and forced expiration modes.

## Main Responsibilities
- Determine whether dentries are old enough and idle enough to expire.
- Check mount trees for busyness using dentry refcounts and `may_umount_tree()`.
- Traverse positive dentries safely under autofs lookup locking.
- Mark dentries as `WANT_EXPIRE` and `EXPIRING`.
- Coordinate with wait queues and daemon expiry notifications.
- Provide root ioctl and misc-device expire entry points.

## Key APIs
- `autofs_expire_wait()`.
- `autofs_expire_run()`.
- `autofs_do_expire_multi()`.
- `autofs_expire_multi()`.

## Important Behavior
Expiration eligibility uses `last_used + timeout` unless `AUTOFS_EXP_IMMEDIATE` is requested. Forced expiration bypasses normal busy checks and lets userspace handle busy mounts.

Direct mount expiration checks the root dentry and mount tree. Indirect expiration scans positive root children, supports per-dentry timeouts, and can expire either whole trees or leaves depending on flags.

Before final selection, dentries are marked `AUTOFS_INF_WANT_EXPIRE` and an RCU grace period is forced with `synchronize_rcu()`. The code then revalidates that the dentry is still eligible before setting `AUTOFS_INF_EXPIRING`.

`autofs_expire_wait()` blocks path walkers while an expire is pending or active, using `autofs_wait()` and `expire_complete`.

## Risks
Expiration is race-prone by design: path walking, daemon unlink/rmdir, mountpoint replacement, RCU walk, dentry refcounts, and umount checks all interact. The `WANT_EXPIRE` to `EXPIRING` transition and cleanup must clear flags and complete waiters on every path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/expire.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/init.c -->
# File Research: sources/os/linux/linux/fs/autofs/init.c

## Summary
Registers and unregisters the autofs filesystem and its misc-device ioctl interface.

## Main Responsibilities
- Define `autofs_fs_type`.
- Initialize `/dev/autofs` control device.
- Register the `autofs` filesystem.
- Unregister filesystem and misc device at module exit.

## Key APIs
- `init_autofs_fs()`.
- `exit_autofs_fs()`.
- `autofs_fs_type`.

## Important Behavior
The init path registers the misc device first, then the filesystem. If filesystem registration fails, the misc device is deregistered. Module aliases expose both filesystem and device names.

## Risks
Initialization ordering matters because the device ioctl path references `autofs_fs_type` and mount state. No complex runtime logic lives here.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/inode.c -->
# File Research: sources/os/linux/linux/fs/autofs/inode.c

## Summary
Handles autofs superblock setup, mount option parsing, inode allocation, and superblock teardown.

## Main Responsibilities
- Allocate and clean `autofs_info` objects.
- Allocate and initialize `autofs_sb_info`.
- Parse fs_context mount parameters including daemon pipe fd, uid/gid, pgrp, protocol versions, type, strict expire, and ignore.
- Validate daemon/kernel protocol compatibility.
- Fill the superblock root inode/dentry.
- Expose mount options through `show_options`.
- Tear down autofs state and enter catatonic mode on kill.

## Key APIs
- `autofs_init_fs_context()`.
- `autofs_get_inode()`.
- `autofs_kill_sb()`.
- `autofs_new_ino()`, `autofs_clean_ino()`, `autofs_free_ino()`.
- `autofs_param_specs`.

## Important Behavior
The pipe fd is opened during parameter parsing so it is resolved in the original syscall context. The pipe must be a writable FIFO and is forced into packet-pipe mode.

New superblocks start catatonic and become active only after root setup and daemon process group selection. Direct or offset trigger roots are marked managed so VFS path walk invokes autofs.

Protocol validation chooses the highest supported version within daemon-supplied min/max bounds and sets protocol subversions for v4/v5.

## Risks
`autofs_fill_super()` must release partially allocated root state on failures; one path after `autofs_get_inode()` failure returns without freeing the newly allocated `autofs_info`. Mount parsing and pipe ownership are sensitive because daemon communication depends on a valid writable packet FIFO.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/root.c -->
# File Research: sources/os/linux/linux/fs/autofs/root.c

## Summary
Implements autofs root/directory file operations, dentry operations, lookup, automount triggering, daemon-visible directory manipulation, and legacy root ioctls.

## Main Responsibilities
- Provide autofs root and directory `file_operations`.
- Provide autofs directory `inode_operations`.
- Provide dentry `d_automount`, `d_manage`, and `d_release`.
- Create active autofs dentries during lookup and reuse unhashed active dentries.
- Trigger daemon mount requests during path walk.
- Wait for pending expires and pending mounts.
- Allow daemon-only mkdir/symlink/unlink/rmdir operations.
- Support root-directory ioctls for wait release, protocol queries, timeout, askumount, and expire.

## Key APIs
- `autofs_d_automount()`, `autofs_d_manage()`.
- `autofs_lookup()`.
- `autofs_dir_mkdir()`, `autofs_dir_symlink()`, `autofs_dir_unlink()`, `autofs_dir_rmdir()`.
- `autofs_root_ioctl()`, `autofs_root_compat_ioctl()`.
- `is_autofs_dentry()`.

## Important Behavior
The automount daemon never triggers mounts; oz-mode path walks see the raw autofs filesystem. Non-daemon writers are denied by `autofs_dir_permission()`.

`autofs_d_automount()` waits for pending expires, sets `AUTOFS_INF_PENDING` when it must call the daemon, waits for `NFY_MOUNT`, then detects whether userspace replaced the dentry.

`autofs_d_manage()` can return `-EISDIR` to tell VFS that a managed dentry is not a mount trap after all, avoiding needless automount recursion for symlinks and non-empty directories.

Lookup creates `autofs_info`, attaches it to the dentry, and adds it to the active list. Root entries in indirect mounts are marked managed mount triggers.

Daemon unlink/rmdir uses `d_drop()` plus the expiring list rather than ordinary negative-dentry deletion, so path walkers can detect incomplete expiry and wait.

## Risks
The path-walk hooks are race-sensitive around RCU walk, expiring dentries, stale indirect mount dentries, rootless multi-mounts, and daemon replacement of directories with symlinks. Active/expiring list cleanup in `d_release` must match lookup and expire behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/root.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/symlink.c -->
# File Research: sources/os/linux/linux/fs/autofs/symlink.c

## Summary
Implements symlink inode operations for autofs dentries.

## Main Responsibilities
- Return the symlink target stored in `inode->i_private`.
- Update autofs last-used time for non-daemon access.

## Key APIs
- `autofs_symlink_inode_operations`.
- `autofs_get_link()`.

## Important Behavior
RCU link lookup without a dentry returns `-ECHILD`. Non-oz-mode access updates `ino->last_used`, which affects expiration eligibility.

## Risks
The symlink target lifetime is owned by the inode and freed from `autofs_evict_inode()`. Expiry behavior depends on `last_used` being updated on ordinary access.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/autofs/waitq.c -->
# File Research: sources/os/linux/linux/fs/autofs/waitq.c

## Summary
Implements autofs wait queues and daemon notification through the autofs control pipe.

## Main Responsibilities
- Enter catatonic mode and wake/fail all pending waits.
- Write mount/expire request packets to the daemon pipe.
- Deduplicate waits for the same path.
- Validate whether a wait is still needed after races.
- Sleep until daemon releases a wait token.
- Release wait tokens from root or device ioctls.

## Key APIs
- `autofs_wait()`.
- `autofs_wait_release()`.
- `autofs_catatonic_mode()`.

## Important Behavior
Each new wait gets a global nonzero token. Requests are keyed by a `qstr` derived from either the raw dentry path or a dummy direct-mount root name.

Protocol v4 and v5 use different packet formats. v5 packets include dev, ino, uid, gid, pid, and tgid translated into the daemon’s namespaces.

`autofs_notify_daemon()` drops `wq_mutex` while writing to the pipe. Write failures either release the specific wait for recoverable errors or put the mount into catatonic mode.

`validate_request()` handles important races: an existing wait, a completed mount while sleeping, an expire wait whose queue is not yet posted, and invalid negative dentries for direct/offset/non-root indirect cases.

After a successful mount wait, requester uid/gid are stored into the relevant `autofs_info` for daemon restart/reconnect use.

## Risks
Wait queue lifetime uses `wait_ctr` because both waiters and release paths can hold references. The code depends on `wq->name.name == NULL` as the wake condition. Pipe write error handling and catatonic transition must avoid lost wakeups and dangling pipe refs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/autofs/waitq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/backing-file.c -->
# File Research: sources/os/linux/linux/fs/backing-file.c

## Summary
Provides common helpers for stackable filesystems that operate on backing files while preserving the user-visible file/path context.

## Main Responsibilities
- Open backing files and tmpfiles with supplied credentials.
- Attach the user-facing path to backing file containers.
- Provide read/write/splice/mmap helpers under backing credentials.
- Support async backing I/O completion and position propagation.
- Remove privileges before backing writes.
- Call filesystem-provided access and write-end hooks.

## Key APIs
- `backing_file_open()`, `backing_tmpfile_open()`.
- `backing_file_read_iter()`, `backing_file_write_iter()`.
- `backing_file_splice_read()`, `backing_file_splice_write()`.
- `backing_file_mmap()`.

## Important Behavior
Backing files must have `FMODE_BACKING`; helpers warn and fail otherwise. Synchronous kiocbs call normal VFS iter read/write helpers. Asynchronous reads/writes clone the original kiocb into `struct backing_aio`, hold the backing file, and propagate `ki_pos` back to the original kiocb on cleanup.

Async writes queue completion to the original file superblock’s `s_dio_done_wq` so mtime/size updates are serialized. Direct I/O is rejected if the backing file cannot support it.

Reads and mmap invoke `ctx->accessed` on the user file. Writes and splice writes call `file_remove_privs()` on the user-visible file before writing to the backing file and call `ctx->end_write` when present.

`backing_file_mmap()` temporarily swaps `vma->vm_file` to the backing file, runs `security_mmap_backing_file()`, and then calls `vfs_mmap()`.

## Risks
This layer bridges user-visible and real backing file state, so credential scoping, file refs, position propagation, direct-I/O capability checks, mmap security hooks, and async completion ordering are all important. Async write completion relies on `s_dio_done_wq` initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/backing-file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/bad_inode.c -->
# File Research: sources/os/linux/linux/fs/bad_inode.c

## Summary
Provides VFS stub operations for inodes that could not be read or constructed correctly, causing further operations to fail with `-EIO`.

## Main Responsibilities
- Define bad inode file and inode operations.
- Convert an inode into a bad inode after I/O/read failure.
- Test whether an inode is bad.
- Abort construction of a newly allocated inode.

## Key APIs
- `make_bad_inode()`.
- `is_bad_inode()`.
- `iget_failed()`.

## Important Behavior
`make_bad_inode()` removes the inode from the inode hash, sets it to a regular-file mode with simple timestamps, installs `bad_inode_ops` and `bad_file_ops`, and clears xattr operation flags.

Almost all inode operations return `-EIO`; lookup and directory creation return error pointers. `iget_failed()` marks the inode bad, unlocks it as a new inode, and drops it with `iput()`.

## Risks
This is deliberately blunt failure containment. Once an inode is marked bad, callers should expect normal filesystem operations to fail. `is_bad_inode()` identifies badness by pointer comparison against `bad_inode_ops`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/bad_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/Kconfig -->
# File Research: sources/os/linux/linux/fs/befs/Kconfig

## Summary
Defines configuration options for the Linux BeFS filesystem driver.

## Main Contents
- `BEFS_FS`: tristate read-only BeOS filesystem support.
- `BEFS_DEBUG`: optional debug support depending on `BEFS_FS`.

## Important Behavior
`BEFS_FS` depends on block-device support and selects `BUFFER_HEAD` and `NLS`. The help text notes the driver is read-only and does not expose BeFS attributes or database-like indices.

`BEFS_DEBUG` enables driver debugging output usable with the `debug` mount option.

## Risks
No runtime logic. Enabling debug changes compilation through the Makefile’s `-DDEBUG`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/befs/Makefile -->
# File Research: sources/os/linux/linux/fs/befs/Makefile

## Summary
Builds the BeFS filesystem driver.

## Main Contents
- `obj-$(CONFIG_BEFS_FS) += befs.o`.
- `ccflags-$(CONFIG_BEFS_DEBUG) += -DDEBUG`.
- `befs-objs := datastream.o btree.o super.o inode.o debug.o io.o linuxvfs.o`.

## Important Behavior
The Makefile links the BeFS driver from datastream, btree, superblock, inode, debug, I/O, and Linux VFS integration objects.

## Risks
No runtime logic. Build composition and debug flag selection must match the Kconfig options.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/befs/Makefile -->