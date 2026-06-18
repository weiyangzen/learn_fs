# Group Research: group_939_linux_stable_sources_os_linux_linux_stable_fs_afs_yfsclient_c_source_0ba884e2f264

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/yfsclient.c -->
# File Research: sources/os/linux/linux-stable/fs/afs/yfsclient.c

## Purpose
Implements kAFS client-side YFS file-server RPC stubs. It builds YFS XDR requests, unmarshals replies, and connects YFS operations to the common `afs_operation` / `afs_call` machinery.

## Main Interfaces
- File data and metadata: `yfs_fs_fetch_data()`, `yfs_fs_store_data()`, `yfs_fs_fetch_status()`, `yfs_fs_setattr()`.
- Namespace operations: `yfs_fs_create_file()`, `yfs_fs_make_dir()`, `yfs_fs_remove_file()`, `yfs_fs_remove_dir()`, `yfs_fs_link()`, `yfs_fs_symlink()`.
- Rename variants: `yfs_fs_rename()`, `yfs_fs_rename_replace()`, `yfs_fs_rename_noreplace()`, `yfs_fs_rename_exchange()`.
- Volume and locking: `yfs_fs_get_volume_status()`, `yfs_fs_set_lock()`, `yfs_fs_extend_lock()`, `yfs_fs_release_lock()`.
- Bulk status and ACLs: `yfs_fs_inline_bulk_status()`, `yfs_fs_fetch_opaque_acl()`, `yfs_fs_store_opaque_acl2()`, `yfs_free_opaque_acl()`.

## Implementation Notes
The file is dominated by XDR helpers for YFS fids, strings, store status records, volume status, callbacks, volsync records, and 100ns YFS timestamp conversion. Reply delivery functions decode status/callback/volsync combinations into `afs_status_cb` and operation result fields.

Fetch-data delivery is a staged unmarshalling state machine: it extracts returned data length, transfers file data into the netfs subrequest iterator, discards excess server data if needed, then decodes status, callback, and volume sync metadata.

YFS optional operation support is probed by failure. `YFS.RemoveFile2` and `YFS.Rename_Replace` downgrade to older operations by setting server capability flags when the server returns unsupported-operation abort codes.

## Cross-File Relationships
Depends on AFS/YFS protocol structures from `afs_fs.h`, `xdr_fs.h`, and `protocol_yfs.h`, and on the AFS operation/call framework from `internal.h`. Status results feed common kAFS vnode, callback, volume sync, lock, and netfs paths.

## Risks / Review Notes
Request buffer sizing is manually matched to encoded fields and checked only after encoding by `yfs_check_req()`. Reply length/state sequencing is protocol-sensitive, especially for variable-length volume status strings and opaque ACL payloads. Rename and remove downgrade behavior is per-server state and affects later operation selection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/afs/yfsclient.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/aio.c -->
# File Research: sources/os/linux/linux-stable/fs/aio.c

## Purpose
Implements the legacy Linux native asynchronous I/O syscalls and their completion ring: `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, and `io_pgetevents` including compat/time32 variants.

## Main Components
- `struct kioctx`: per-AIO-context state, completion ring, refs, wait queue, active cancellation list, request counters, and mmap metadata.
- `struct aio_ring`: user-visible ring header plus `io_event` array.
- `struct aio_kiocb`: internal request wrapper for read/write, fsync, and poll operations.
- Private pseudo filesystem and ring file used to back mmaped ring pages.
- Sysctl state for global `aio-nr` and `aio-max-nr`.

## Important Behavior
`io_setup()` allocates a `kioctx`, creates and mmaps ring folios, installs the context in the current mm’s RCU-protected ioctx table, and charges the global AIO request quota. Context lifetime is split between `users` and `reqs` percpu refs: user refs protect lookup/submission, while request refs keep the context alive until all in-flight requests finish.

Ring overflow is avoided with `reqs_available`, batched through per-cpu counters. Completed events are written under `completion_lock`; userspace advances `ring->head`, while the kernel updates `tail`. `aio_read_events_ring()` copies events to userspace and advances the ring head under `ring_lock`.

`io_submit()` supports pread/pwrite, preadv/pwritev, fsync/fdatasync, and poll. Reads/writes use file `read_iter`/`write_iter`; fsync is punted to workqueue with captured creds; poll handles waitqueue lifetime, `POLLFREE`, cancellation, inline completion, and workqueue fallback.

## State And Synchronization
Uses `mm->ioctx_lock`, RCU lookup, percpu refs, `ctx_lock` for active requests/cancel, `ring_lock` for ring reads and migration coordination, `completion_lock` for event insertion, and wait queues for `io_getevents()`. Ring folio migration is supported with a private address-space operation and synchronized against teardown through `aio_inode_info::migrate_lock`.

## Risks / Review Notes
The ring protocol is intentionally shared with userspace, so head/tail ordering and barriers are critical. Poll cancellation and `POLLFREE` rely on waitqueue lock ordering plus RCU-delayed freeing. Error paths after partial request setup must balance eventfd refs, file refs, request slots, and percpu request refs exactly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/aio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/anon_inodes.c -->
# File Research: sources/os/linux/linux-stable/fs/anon_inodes.c

## Purpose
Provides the anonymous-inode filesystem and helper APIs used by kernel subsystems to create file objects or file descriptors that are not backed by ordinary filesystem paths.

## Main Interfaces
- `anon_inode_getfile()`, `anon_inode_getfile_fmode()`.
- `anon_inode_create_getfile()`.
- `anon_inode_getfd()`, `anon_inode_create_getfd()`.
- `anon_inode_make_secure_inode()`.
- `anon_inode_getattr()` and `anon_inode_setattr()` for anonymous inode stat behavior.

## Important Behavior
Most anonymous files share a singleton inode to avoid per-file inode overhead. Callers that need a unique inode or LSM security context use the `create` variants, which allocate a non-`S_PRIVATE` inode and call `security_inode_init_security_anon()`.

The custom `getattr` masks off file-type bits in `st_mode` to preserve historical userspace detection of `anon_inode`. File creation takes a module reference for `fops->owner`, allocates a pseudo file on the `anon_inodefs` mount, sets `private_data`, and exposes the file through `FD_ADD()` when an fd is requested.

## Cross-File Relationships
Backs common kernel APIs such as eventfd/epoll-like anonymous files and security-sensitive consumers needing `anon_inode_create_*`. It uses the VFS pseudo filesystem helpers and LSM anonymous-inode initialization hook.

## Risks / Review Notes
The shared singleton inode path intentionally skips per-object security initialization. Callers needing LSM policy or unique stat identity must choose the secure create path. Module owner refs and inode/file cleanup are paired in the common helper.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/anon_inodes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/attr.c -->
# File Research: sources/os/linux/linux-stable/fs/attr.c

## Purpose
Implements generic VFS attribute-change policy and helper logic for chmod/chown/truncate/timestamp updates.

## Main Interfaces
- `setattr_prepare()`.
- `setattr_copy()`.
- `setattr_should_drop_sgid()`, `setattr_should_drop_suidgid()`.
- `inode_newsize_ok()`.
- `may_setattr()`.
- `notify_change()`.

## Important Behavior
Permission checks are idmapped-mount aware. `chown_ok()` and `chgrp_ok()` compare current credentials and capabilities through VFS uid/gid mappings. `setattr_prepare()` validates truncate size, verity immutability, chown/chgrp/chmod permissions, timestamp-setting permissions, and `ATTR_KILL_PRIV`.

`inode_newsize_ok()` enforces negative-size rejection, `RLIMIT_FSIZE`, superblock maxbytes, SIGXFSZ delivery, and swapfile truncation denial. `setattr_copy()` updates uid/gid/mode and timestamps, with special multigrain timestamp handling through `setattr_copy_mgtime()`.

`notify_change()` is the central VFS path: it checks immutability/append restrictions, normalizes timestamps, handles killpriv and setid-bit removal, validates id mappings, calls LSM hooks, breaks delegations unless `ATTR_DELEG` is set, dispatches filesystem `->setattr` or `simple_setattr`, then emits fsnotify and post-setattr hooks.

## Cross-File Relationships
Used broadly by filesystem `->setattr` implementations and truncate/chmod/chown paths. It coordinates with LSM, fsnotify, delegation breaking, idmapped mounts, POSIX permissions, and simple filesystem helpers.

## Risks / Review Notes
`notify_change()` requires the target inode locked exclusively. Callers must handle `-EWOULDBLOCK` delegation retry correctly when using `delegated_inode`. Changes to idmapping or setid-bit rules have wide VFS security impact.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/autofs/Kconfig

## Purpose
Defines the `AUTOFS_FS` kernel configuration option for kernel automounter support.

## Main Contents
`AUTOFS_FS` is a tristate option named “Kernel automounter support (supports v3, v4 and v5)”. The help text explains that autofs works with userspace automounter tools, reduces overhead for already-mounted paths, and builds as module `autofs` when selected as `M`.

## Risks / Review Notes
This is configuration metadata only. It does not define dependencies beyond user guidance, but enabling it exposes the autofs filesystem and `/dev/autofs` control interface compiled from the accompanying sources.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/autofs/Makefile

## Purpose
Builds the autofs filesystem object when `CONFIG_AUTOFS_FS` is enabled.

## Main Contents
Defines `autofs4.o` as the module/built-in target and composes it from `init.o`, `inode.o`, `root.o`, `symlink.o`, `waitq.o`, `expire.o`, and `dev-ioctl.o`.

## Risks / Review Notes
The object name remains `autofs4.o` for historical reasons while the module and filesystem are presented as autofs. Any new source file must be added here to be included in the driver.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/autofs_i.h -->
# File Research: sources/os/linux/linux-stable/fs/autofs/autofs_i.h

## Purpose
Internal autofs header defining shared structures, flags, prototypes, and inline helpers for the autofs filesystem implementation.

## Main Contents
- `struct autofs_info`: per-dentry/inode state, active/expiring list links, expire state, last-used time, requester uid/gid, and per-dentry timeout.
- `struct autofs_sb_info`: per-superblock daemon pipe, protocol version, flags, mount namespace id, locks, active/expiring lists, and wait queues.
- Wait queue state in `struct autofs_wait_queue`.
- Superblock flags including catatonic, strict-expire, and ignore.
- Dentry managed-flag helpers for `DCACHE_NEED_AUTOMOUNT` and `DCACHE_MANAGE_TRANSIT`.
- Pipe validation/preparation helpers and shared prototypes.

## Important Behavior
`autofs_oz_mode()` identifies daemon/catatonic access, allowing the owner process group to see and mutate the raw autofs namespace without triggering automounts. The header centralizes expiring-list manipulation under `lookup_lock` and wraps pipe setup to require writable FIFO packet-mode pipes.

## Cross-File Relationships
Included by all autofs implementation files. `root.c` uses dentry and automount helpers, `waitq.c` uses wait queue structures, `expire.c` uses expire flags/lists, `inode.c` initializes superblock state, and `dev-ioctl.c` exposes control operations.

## Risks / Review Notes
`autofs_info` is RCU-freed and linked into active/expiring lists; users must respect locking and lifetime. `autofs_empty()` depends on the internal `count` convention used by namespace mutation code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/autofs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/dev-ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/autofs/dev-ioctl.c

## Purpose
Implements the `/dev/autofs` miscellaneous-device ioctl interface, allowing userspace daemons and tools to control autofs mounts even when mountpoints are covered by other mounts.

## Main Interfaces
Supports device ioctl commands for interface/protocol version, open/close mount fd, ready/fail wait completion, set pipe fd, catatonic mode, timeout management, requester uid/gid lookup, expire, ask-umount, and mountpoint checks.

## Important Behavior
The dispatcher copies a variable-sized `struct autofs_dev_ioctl` from userspace, validates version and path encoding, checks command range, gates most commands behind `CAP_SYS_ADMIN`, resolves an optional autofs mount fd, checks owner-daemon mode, and dispatches through a fixed function table with `array_index_nospec()`.

`openmount` finds the topmost autofs mount matching a path and device id and returns an O_CLOEXEC fd. `setpipefd` reconnects a catatonic mount to a new daemon pipe only within the same pid namespace. `timeout` supports both superblock-wide and per-dentry indirect mount timeouts. `ismountpoint` can operate with or without an autofs fd and returns mount status, device, and covering filesystem magic.

## Cross-File Relationships
Calls `autofs_wait_release()`, `autofs_catatonic_mode()`, `autofs_expire_wait()`, and `autofs_do_expire_multi()`. Relies on autofs mount type helpers, VFS path lookup/mount traversal, and miscdevice registration.

## Risks / Review Notes
The ioctl struct has embedded path data, so size and NUL-termination validation are security-sensitive. Reconnecting daemon pipes requires careful namespace and catatonic-state checks. Some commands intentionally work without an existing autofs fd, which makes path lookup behavior part of the ABI.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/dev-ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/expire.c -->
# File Research: sources/os/linux/linux-stable/fs/autofs/expire.c

## Purpose
Implements autofs expiry selection and execution for direct, indirect, tree, and leaf mount cases.

## Main Interfaces
- `autofs_expire_wait()`.
- `autofs_expire_run()`.
- `autofs_do_expire_multi()`.
- `autofs_expire_multi()`.
- Internal selection helpers for direct and indirect expiry.

## Important Behavior
Expiry candidates are rejected if pending, too young, busy, a protected autofs submount, or still referenced beyond expected autofs-held counts. The code distinguishes forced expiry, immediate expiry, leaf expiry, direct trigger mounts, tree mounts, symlinks, and indirect mount children.

Candidate selection marks `AUTOFS_INF_WANT_EXPIRE`, synchronizes RCU path walks, rechecks eligibility, then marks `AUTOFS_INF_EXPIRING` and initializes a completion. Completion paths clear both flags, update `last_used` to avoid rapid retry loops, and wake waiters.

`autofs_expire_run()` supports the older ioctl style that copies a single expire packet to userspace. `autofs_do_expire_multi()` sends synchronous daemon notifications via `autofs_wait()`.

## State And Synchronization
Uses `lookup_lock` for dentry traversal/list stability, `fs_lock` for autofs info flags, RCU synchronization before selecting expiring dentries, and completions to coordinate path walkers blocked on expiry.

## Risks / Review Notes
Correctness depends on dentry reference-count conventions and rechecking after RCU synchronization. Expiry behavior differs across direct, indirect, v4 pseudo-direct, and v5 trigger mount layouts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/expire.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/init.c -->
# File Research: sources/os/linux/linux-stable/fs/autofs/init.c

## Purpose
Defines module initialization/exit and the autofs filesystem type.

## Main Interfaces
- `autofs_fs_type`.
- `init_autofs_fs()`.
- `exit_autofs_fs()`.

## Important Behavior
Module init registers the `/dev/autofs` miscdevice first, then registers the `autofs` filesystem. If filesystem registration fails, it deregisters the miscdevice. Module exit reverses that by deregistering the miscdevice and unregistering the filesystem.

## Cross-File Relationships
Connects `autofs_init_fs_context()` from `inode.c`, `autofs_kill_sb()` from `inode.c`, mount parameters from `autofs_i.h`, and miscdevice setup from `dev-ioctl.c`.

## Risks / Review Notes
Initialization ordering matters because the device interface and filesystem registration are exposed independently. Failure handling currently cleans up the miscdevice if filesystem registration fails.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/autofs/inode.c

## Purpose
Implements autofs superblock setup, mount option parsing, inode allocation, teardown, and mount option display.

## Main Interfaces
- `autofs_init_fs_context()`.
- `autofs_get_inode()`.
- `autofs_new_ino()`, `autofs_clean_ino()`, `autofs_free_ino()`.
- `autofs_kill_sb()`.

## Important Behavior
Mount parsing accepts daemon pipe fd, uid/gid, owner process group, protocol min/max, mount type flags, strict-expire, and ignore. The pipe is opened during parse to avoid fd reuse races and is forced into packet-pipe mode.

`autofs_alloc_sbi()` initializes catatonic state, protocol defaults, locks, active/expiring lists, mount namespace id, and default indirect type. `autofs_validate_protocol()` negotiates protocol version/subversion. `autofs_fill_super()` creates the root inode/dentry, attaches root `autofs_info`, assigns daemon process group, marks trigger roots managed when needed, and leaves catatonic mode.

`autofs_kill_sb()` enters catatonic mode to release waiters and close the pipe, drops the daemon pgrp, kills the anonymous superblock, and RCU-frees `sbi`.

## Cross-File Relationships
Provides state consumed by `root.c`, `waitq.c`, `expire.c`, and `dev-ioctl.c`. Inode operation tables are defined in `root.c` and `symlink.c`.

## Risks / Review Notes
Several mount options affect ABI-visible protocol behavior. Error paths during `autofs_fill_super()` must avoid leaking `autofs_info`, pipe refs, and pgrp refs. `autofs_evict_inode()` frees symlink target storage from `i_private`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/root.c -->
# File Research: sources/os/linux/linux-stable/fs/autofs/root.c

## Purpose
Implements autofs dentry operations, directory inode operations, root ioctls, lookup behavior, and daemon-controlled namespace mutation.

## Main Interfaces
- Dentry ops: `autofs_d_automount()`, `autofs_d_manage()`, `autofs_dentry_release()`.
- Directory ops: `autofs_lookup()`, `autofs_dir_permission()`, `autofs_dir_symlink()`, `autofs_dir_unlink()`, `autofs_dir_mkdir()`, `autofs_dir_rmdir()`.
- Root ioctl dispatcher: `autofs_root_ioctl()` and compat wrapper.
- Exported helper: `is_autofs_dentry()`.

## Important Behavior
Non-daemon path walks trigger or wait for mounts through `autofs_wait()`. The owner daemon, detected by `autofs_oz_mode()`, can operate on the raw namespace without triggering mounts. `autofs_d_manage()` decides whether path walk should proceed, trigger automount, or stop with `-EISDIR` for already-satisfied rootless multi-mount/symlink cases.

`autofs_lookup()` reuses unhashed active dentries when possible, creates per-dentry `autofs_info`, and marks root children as automount triggers for indirect mounts. Directory creation and symlink creation are daemon-only namespace operations that turn active dentries into persistent dentries. Unlink/rmdir do not simply delete; they drop dentries and place them on the expiring list so walkers racing expiry can wait and retry.

Legacy root ioctls implement ready/fail, catatonic mode, protocol queries, timeout get/set, ask-umount, single expire, and multi-expire.

## State And Synchronization
Uses `lookup_lock` for active/expiring lists and dentry list manipulation, `fs_lock` for pending/expiring flags and requester state, and dentry locks for managed-flag updates. RCU walk paths return `-ECHILD` when blocking is required.

## Risks / Review Notes
Path-walk behavior is subtle because autofs dentries are both filesystem objects and mount triggers. The code must avoid false `ELOOP`, handle stale dentries after daemon replacement, and preserve expiring dentries long enough for waiters to resolve races.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/root.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/autofs/symlink.c

## Purpose
Implements autofs symlink inode operations.

## Main Interface
- `autofs_get_link()` via `autofs_symlink_inode_operations`.

## Important Behavior
`get_link` returns `-ECHILD` for RCU/pathwalk contexts without a dentry. For non-daemon accesses, it updates the associated `autofs_info::last_used` timestamp before returning the symlink target stored in `inode->i_private`.

## Cross-File Relationships
Symlink target strings are allocated in `autofs_dir_symlink()` and freed by `autofs_evict_inode()`. Last-used timestamps feed expiry decisions in `expire.c`.

## Risks / Review Notes
The symlink target is raw inode-private storage; lifetime is tied to inode eviction. RCU symlink resolution is not supported here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/waitq.c -->
# File Research: sources/os/linux/linux-stable/fs/autofs/waitq.c

## Purpose
Implements autofs daemon notification and wait-queue coordination for mount and expire requests.

## Main Interfaces
- `autofs_wait()`.
- `autofs_wait_release()`.
- `autofs_catatonic_mode()`.

## Important Behavior
`autofs_wait()` builds a request name, validates whether a wait should continue, reuses an existing wait for duplicate requests, or creates a new `autofs_wait_queue` with token, requester uid/gid, pid/tgid translated into the daemon pid namespace, and device/inode metadata. It then sends the appropriate protocol v4 or v5 packet to the daemon pipe and waits killably until userspace releases the token.

`autofs_notify_daemon()` formats missing/expire packets for protocol v4 or v5 and writes them to the packet pipe. Pipe write failure can release the wait with an error or force catatonic mode. `autofs_wait_release()` unlinks the wait by token, frees the saved name, records status, and wakes all waiters.

`autofs_catatonic_mode()` marks the mount unresponsive, releases all queued waits with `-ENOENT`, closes the daemon pipe, and resets pipe state.

## State And Synchronization
`wq_mutex` protects the wait queue list and daemon notification setup. `pipe_mutex` serializes writes. Wait entries use a `wait_ctr` convention to keep the object alive for both list ownership and sleeping tasks.

## Risks / Review Notes
The request name buffer stores an offset so the exact allocation can be freed after using a shifted `qstr.name`. Namespace translation failure rejects requests from unrelated pid namespaces. Catatonic mode is the central failure/shutdown escape path and must wake all blocked waiters.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/autofs/waitq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/backing-file.c -->
# File Research: sources/os/linux/linux-stable/fs/backing-file.c

## Purpose
Provides common helpers for stackable filesystems that operate on backing files while preserving the user-visible file/path relationship.

## Main Interfaces
- `backing_file_open()`.
- `backing_tmpfile_open()`.
- `backing_file_read_iter()`, `backing_file_write_iter()`.
- `backing_file_splice_read()`, `backing_file_splice_write()`.
- `backing_file_mmap()`.

## Important Behavior
Open helpers allocate an empty backing file with supplied credentials, store the user path from the upper file, and open a real lower path or tmpfile. Read/write helpers require `FMODE_BACKING`, run under `ctx->cred`, enforce direct-I/O capability, and call optional access/end-write callbacks on the upper/original file.

Asynchronous read/write uses `struct backing_aio`, cloning the caller kiocb onto the backing file and preserving the original kiocb for completion. Async write completion is queued to the superblock DIO completion workqueue to serialize mtime/size updates, then calls the original completion callback.

Splice and mmap paths similarly switch credentials and call VFS helpers. `backing_file_mmap()` swaps `vma->vm_file` to the backing file and calls `security_mmap_backing_file()` before `vfs_mmap()`.

## Cross-File Relationships
Used by stackable filesystems such as overlayfs. Integrates with VFS open/tmpfile/read/write/splice/mmap helpers, LSM mmap checks, file privilege removal, write accounting, and superblock DIO workqueues.

## Risks / Review Notes
Async backing I/O has tight lifetime coupling among original kiocb, cloned kiocb, file refs, and completion callbacks. Write paths remove privileges from the user-facing file before writing the backing file. Mmap changes `vma->vm_file`, so security checks must see both backing and user files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/backing-file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/bad_inode.c -->
# File Research: sources/os/linux/linux-stable/fs/bad_inode.c

## Purpose
Provides VFS stub operations for inodes that could not be read or became invalid due to I/O or remote filesystem errors.

## Main Interfaces
- `make_bad_inode()`.
- `is_bad_inode()`.
- `iget_failed()`.

## Important Behavior
`bad_inode_ops` implements common inode operations by returning `-EIO`, including create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, rename, permission, getattr, setattr, xattr listing, get_link, ACL, fiemap, update_time, atomic_open, tmpfile, and set_acl. `bad_file_ops` rejects open with `-EIO`.

`make_bad_inode()` removes the inode from the inode hash, resets it as a regular file with simple timestamps, installs bad inode/file operations, and clears xattr operation flags. `iget_failed()` marks an under-construction inode bad, unlocks it, and drops it.

## Cross-File Relationships
Called by filesystem inode lookup/read paths that fail after allocating an inode. VFS users can test with `is_bad_inode()`.

## Risks / Review Notes
The goal is fail-closed behavior: after marking bad, operations should consistently return `-EIO` rather than proceeding with partially initialized filesystem state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/bad_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/befs/Kconfig

## Purpose
Defines kernel configuration options for BeOS File System support.

## Main Contents
`BEFS_FS` is a tristate read-only BeFS driver option depending on `BLOCK` and selecting `BUFFER_HEAD` and `NLS`. Help text describes BeFS as BeOS’s native 64-bit filesystem with attributes and database-like indices, while noting this driver does not expose those advanced features.

`BEFS_DEBUG` is a boolean dependent on `BEFS_FS` that enables driver debug output when the debug mount option is used.

## Risks / Review Notes
This is configuration metadata only. The read-only status is explicitly part of the user-facing option text and should remain accurate if write support ever changes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/befs/Makefile

## Purpose
Builds the BeFS filesystem driver.

## Main Contents
Enables `befs.o` when `CONFIG_BEFS_FS` is set. Adds `-DDEBUG` to C flags when `CONFIG_BEFS_DEBUG` is enabled. Composes the driver from `datastream.o`, `btree.o`, `super.o`, `inode.o`, `debug.o`, `io.o`, and `linuxvfs.o`.

## Risks / Review Notes
This is build metadata. Any change to BeFS source layout or debug conditional compilation must be reflected here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/befs/Makefile -->