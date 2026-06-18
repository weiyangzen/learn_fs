# Group Research: group_1161_minix_sources_teaching_minix_minix_servers_vfs_mount_c_sources_teac_6685b5af492e

Scope: `Docs/research_subset_a.md`, source tree `sources/teaching/minix`.

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/mount.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/mount.c

Implements VFS mount and unmount lifecycle.

Key behavior:
- `do_mount` validates superuser privilege, copies mount label/device/path/type from the caller, resolves the filesystem endpoint through DS, translates the device path to a block device or allocates a `NONE_MAJOR` pseudo-device, then delegates to `mount_fs`.
- `mount_fs` allocates and locks a `vmnt`, rejects duplicate mounted devices, resolves non-root mountpoints, calls `req_mountpoint`, allocates a root vnode, sends `REQ_READSUPER`, fills statvfs cache, and attaches the mount.
- Root mounting is special: `have_root` allows initial ramdisk root and later boot-disk root replacement; all processes' root and working directories are replaced.
- `mount_pfs` mounts PipeFS as pseudo filesystem infrastructure for pipes and sockets.
- `unmount` refuses busy mounts by scanning vnode references and locks, cleans root references, sends `REQ_UNMOUNT`, frees pseudo-devices, marks the `vmnt` free, and reroutes block-special I/O to `ROOT_FS_E`.
- `update_bspec` scans live block-special vnodes for a device and updates `v_bfs_e`, optionally sending `REQ_NEW_DRIVER`.

Important dependencies:
- Path lookup through `lookup_init`, `eat_path`, and `name_to_dev`.
- Vnode/vmnt lifecycle through free-slot allocation, locks, reference counts, `put_vnode`, and `mark_vmnt_free`.
- Request layer through `req_readsuper`, `req_mountpoint`, `req_unmount`, and `req_newdriver`.
- Block-special serialization through `lock_bsf`.

Notable details:
- Pseudo devices are tracked by a static bitmap and allocated lazily.
- Non-root mounts briefly unlock the parent mount after `req_mountpoint` to avoid back-call deadlocks.
- `unmount_all(force)` repeatedly scans all mounts because dependent mounts must be peeled from leaves inward.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/open.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/open.c

Implements open, create, node creation, directory creation, seek, and close operations.

Key behavior:
- `do_open` rejects `O_CREAT` and calls `common_open`; `do_creat` requires `O_CREAT`, fetches pathname and mode, then calls `common_open`.
- `common_open` allocates an fd and filp, resolves or creates a vnode, installs the filp, applies `O_CLOEXEC`, enforces permissions, and dispatches by vnode type.
- Regular files may be truncated with `O_TRUNC`; directories are openable for read but not write.
- Character devices call `cdev_open`; block devices call `bdev_open`, compute `v_bfs_e` from mounted filesystems, and may notify the root FS of driver labels.
- FIFOs are mapped to PipeFS with `map_vnode`, forced to append mode, and opened through `pipe_open`; shared reader/writer filps may be reused.
- Sockets cannot be opened by path and return `EOPNOTSUPP`.

Creation helpers:
- `new_node` resolves the parent with `last_dir`, honors `O_EXCL` symlink behavior, creates regular files with `req_create`, and handles dangling symlinks by reading the link and recursively creating the target.
- `do_mknod` supports special nodes and FIFOs, restricting non-FIFO creation to superuser.
- `do_mkdir` resolves the parent and calls `req_mkdir`.

Seek/close:
- `actual_lseek` rejects pipes, computes `SEEK_SET/CUR/END`, checks overflow, updates filp position, and inhibits FS read-ahead when position changes.
- `close_fd` removes the fd before closing the filp, clears close-on-exec, and releases advisory locks owned by the process.

Notable detail:
- `common_open` installs the filp before lower-level device/FIFO open so cloning and suspended opens can refer to the fd.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/open.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/path.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/path.c

Central pathname resolution implementation. It bridges VFS vnode/vmnt state and file-server `REQ_LOOKUP` semantics.

Key behavior:
- `advance` resolves a path from a starting vnode, allocates a temporary vnode, calls internal `lookup`, reuses an existing vnode if present, fills new vnode metadata otherwise, increments references, and downgrades locks when requested.
- `eat_path` chooses root or working directory for absolute vs relative paths.
- `last_dir` resolves all but the final component, returns the parent directory vnode, and rewrites `resolve->l_path` to the final component. It handles trailing slashes, symlinks, relative and absolute symlink restarts, and mountpoint crossings.
- Internal `lookup` sends `REQ_LOOKUP`, handles `EENTERMOUNT`, `ELEAVEMOUNT`, and `ESYMLINK`, rewrites remaining path text from `char_processed`, locks current mounts, and follows mount tree transitions.
- `lookup_init` initializes the shared mutable `struct lookup` contract.
- `get_name` scans directory entries with `req_getdents` to find a child's name.
- `canonical_path` resolves symlinks, climbs parent directories with `..`, crosses mount roots back to mounted-on vnodes, and builds an absolute path.
- `do_socketpath` lets UDS check or create on-disk socket path nodes on behalf of a blocked user process.

Important dependencies:
- Request wrappers: `req_lookup`, `req_rdlink`, `req_getdents`, `req_mknod`.
- Vnode/vmnt locking and reference management.
- Permission checks through `forbidden`.

Notable details:
- Path lookup mutates the caller-provided path buffer.
- VMNT read requests are initially taken as write locks and later downgraded.
- Symlink depth is bounded by `_POSIX_SYMLOOP_MAX`.
- `DO_POSIX_PATHNAME_RES` is disabled, so trailing slashes are stripped in historical Unix style.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/path.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/path.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/path.h

Defines the shared pathname lookup descriptor.

Key contents:
- `struct lookup` stores the mutable path buffer, VFS/FS lookup flags, desired `vmnt` and vnode lock modes, and output pointers for locked `vmnt`/vnode objects.
- Used by path, open, mount, protect, and socket-path code to standardize lookup intent and returned locks.
- Callers initialize it with `lookup_init` and set non-`TLL_NONE` lock modes before `advance`, `eat_path`, or `last_dir`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/path.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/pipe.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/pipe.c

Implements pipe creation, FIFO feasibility checks, suspension, revival, and signal interruption for blocked VFS calls.

Key behavior:
- `do_pipe2` combines modern and backward-compatible flags, calls `create_pipe`, and returns the fd pair.
- `create_pipe` locks PipeFS, allocates a vnode, gets two filps/fds, creates a PipeFS node with `REQ_NEWNODE`, fills vnode mapping fields, and assigns read/write filps.
- `map_vnode` maps named FIFOs to PipeFS by creating a temporary PipeFS node and storing `v_mapfs_e`, `v_mapinode_nr`, and map reference count.
- `pipe_check` decides whether pipe reads/writes can proceed, should suspend, fail with `EAGAIN/EPIPE`, or perform a partial write. It wakes opposite-side waiters through `release`.
- `suspend` records block state and updates `susp_count` for pipe open/I/O waits.
- `pipe_suspend` stores resumable read/write state in `fp_pipe`.
- `release` wakes blocked pipe open/read/write callers and notifies select waiters.
- `revive` marks pipe/flock waiters for main-loop revival or replies immediately for select/cdev/popen states.
- `unpause` handles signal interruption across pipe, flock, select, popen, cdev, and sdev blocking states.

Important dependencies:
- Pipe data I/O is later performed by `read.c` through mapped PipeFS requests.
- Select integration uses `select_callback`.
- Socket-driver blocking is delegated to `sdev_cancel` and `sdev_stop`.

Notable detail:
- Blocking writes larger than `PIPE_BUF` may partially write, then suspend for the remaining data.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/protect.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/protect.c

Implements protection-related syscalls and generic vnode access checks.

Key behavior:
- `do_chmod` handles path and fd variants, requires owner or superuser, rejects read-only filesystems, clears setgid for non-superusers outside the file's group, calls `req_chmod`, and updates cached mode.
- `do_chown` handles path and fd variants, rejects read-only filesystems, restricts non-superusers from giving away files or changing to arbitrary groups, calls `req_chown`, and updates cached uid/gid/mode.
- `do_umask` updates `fp_umask` and returns the complement of the old mask.
- `do_access` validates requested access bits, resolves the path, and checks permissions using real uid/gid semantics.
- `forbidden` computes owner/group/supplementary-group/other permission bits, gives superuser read/write plus directory search and conditional execute, and checks read-only mounts for writes.
- `read_only` tests `vp->v_vmnt` for `VMNT_READONLY`.

Important dependencies:
- Path lookup through `lookup_init` and `eat_path`.
- Request wrappers `req_chmod` and `req_chown`.
- User/group state from `fproc` and supplementary group helper `in_group`.

Notable detail:
- For `VFS_ACCESS`, both lookup credentials and `forbidden` use real uid/gid instead of effective uid/gid.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/protect.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/proto.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/proto.h

Global VFS prototype header.

Key contents:
- Includes `request.h`, `threads.h`, `tll.h`, and `type.h`.
- Forward declares major VFS structures to avoid circular includes.
- Declares cross-module entry points for device drivers, file descriptors, links, mount, open, path, pipe, protection, read/write, request wrappers, socket device layers, socket syscalls, stat/directory, locking, utilities, vmnt/vnode management, select, and worker threads.
- Defines endpoint validation convenience macros `okendpt` and `isokendpt`.

Relevant to this group:
- Exposes mount/unmount, open/close/lseek/mknod/mkdir, path lookup helpers, pipe suspend/revive helpers, permission checks, read/getdents/rw_pipe, all `req_*` wrappers, `sdev_*`, `smap_*`, socket syscalls, and select callbacks.
- Serves as the compact shared contract between syscall dispatch, worker scheduling, IPC request wrappers, and object lifecycle code.

Notable detail:
- `do_creat` is declared twice in the open section.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/read.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/read.c

Implements read path, shared read/write execution, getdents, pipe I/O, and block-special-file locking.

Key behavior:
- `do_read` validates reserved `cum_io` input and delegates to `do_read_write_peek`.
- `actual_read_write_peek` locks filp/vnode for read or write, checks access mode, handles zero-length I/O, and calls `read_write`.
- `read_write` dispatches by vnode type:
  - FIFOs use `rw_pipe`.
  - Character devices use asynchronous `cdev_io`.
  - Sockets use `sdev_readwrite`.
  - Block devices serialize with `lock_bsf` and call `req_breadwrite` or `req_bpeek`.
  - Regular files/directories call `req_readwrite` or `req_peek`, honoring `O_APPEND`.
- Writes update cached vnode size for regular files and directories.
- `EPIPE` on writes triggers SIGPIPE unless `O_NOSIGPIPE` is set.
- `do_getdents` validates the fd as a readable directory, calls `req_getdents`, and updates filp position.
- `rw_pipe` uses `pipe_check`, suspends when necessary, performs mapped PipeFS `req_readwrite`, updates cached pipe size, and handles partial blocking writes.

Block-special lock:
- `lock_bsf` suspends the worker if the mutex is busy.
- `unlock_bsf` releases it.
- `check_bsf_lock` verifies shutdown/unmount cleanup.

Notable details:
- Character device I/O may return `SUSPEND`; VFS optimistically advances filp position for async character operations.
- `PEEKING` is rejected for pipes, character devices, and sockets.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/request.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/request.c

Implements typed wrappers for VFS-to-filesystem server requests. Each wrapper builds a message, creates grants when needed, sends through `fs_sendrec`, revokes grants, and copies reply data into VFS structures.

Major request families:
- Data I/O: `req_readwrite`, `req_breadwrite`, `req_peek`, `req_bpeek`.
- Metadata: `req_chmod`, `req_chown`, `req_utime`, `req_stat`, `req_statvfs`.
- Namespace: `req_lookup`, `req_create`, `req_mkdir`, `req_mknod`, `req_link`, `req_rename`, `req_rmdir`, `req_unlink`, `req_slink`, `req_rdlink`.
- Mount/lifecycle: `req_readsuper`, `req_mountpoint`, `req_unmount`, `req_newdriver`, `req_flush`, `req_sync`, `req_putnode`, `req_newnode`, `req_inhibread`, `req_ftrunc`.

Important behavior:
- User-buffer operations use magic grants and retry on `GRANT_FAULTED` by asking VM to handle memory with `vm_vfs_procctl_handlemem`, then repeating without `CPF_TRY`.
- VFS-local buffers use direct grants.
- `req_lookup` can pass supplemental group credentials through an extra grant and interprets `OK`, `EENTERMOUNT`, `ELEAVEMOUNT`, and `ESYMLINK` response shapes.
- `req_readsuper`, `req_create`, `req_newnode`, and `req_lookup` populate `node_details_t` or `lookup_res_t`.
- Some operations enforce non-`RES_64BIT` filesystem offset limits before sending requests.

Notable caveats:
- `req_getdents_actual` and `req_readwrite_actual` create grants before some 64-bit offset-limit checks; those early `EINVAL` paths return before revoking the grant.
- Grant allocation failures are treated as internal VFS invariants and often panic.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/request.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/request.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/request.h

Defines response structures shared by request wrappers and callers.

Key structures:
- `node_details_t`: filesystem endpoint, inode number, mode, size, uid, gid, and special-file device number.
- `lookup_res_t`: core vnode metadata plus `char_processed` and `symloop` fields used by path lookup after mount transitions or symlink expansion.

Usage:
- `node_details_t` is filled by creation, new-node, and read-super requests and copied into VFS vnode state.
- `lookup_res_t` is filled by `req_lookup` and consumed by `path.c` for multi-filesystem pathname traversal.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/request.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/sdev.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/sdev.c

Implements the lower VFS socket layer: communication with socket drivers and completion of long-lived socket operations.

Key behavior:
- `sdev_sendrec` sends short-lived socket-driver requests asynchronously, then blocks the current worker thread until the reply arrives.
- `sdev_suspend` records socket request state, grants, request type, and accept/recvmsg auxiliary state in `fp_sdev`, then suspends the process on `_SDEV`.
- `sdev_socket` creates sockets or socket pairs through a socket driver and converts driver-local socket IDs to VFS `dev_t` values.
- `sdev_bind`, `sdev_connect`, `sdev_accept`, `sdev_readwrite`, and `sdev_ioctl` send long-lived requests and suspend the process.
- `sdev_listen`, `sdev_shutdown`, option calls, address queries, and most closes use short-lived request/reply patterns.
- `sdev_close` may suspend only for user `close(2)`, where SO_LINGER can block; other close paths wait synchronously with a nonblocking close parameter.
- `sdev_select` initiates socket-driver select polling without suspending the process.

Reply handling:
- `sdev_reply` receives driver replies, routes select replies to `select_sdev_reply1/2`, wakes blocked worker threads for short-lived calls, resumes suspended processes for long-lived calls, and spawns a worker for successful accept replies.
- `sdev_finish` revokes grants and completes suspended calls by either `replycode` or upper-layer resume functions.
- `sdev_finish_accept` creates a VFS socket device identifier for accepted sockets and calls `resume_accept`.
- `sdev_cancel` sends cancel requests for signal-interrupted socket calls and handles the original reply.
- `sdev_stop` aborts calls when a socket driver dies.

Important dependencies:
- Socket-driver registration and device decoding are provided by `smap.c`.
- Upper socket syscall completion is delegated to `socket.c`.
- Select integration uses `select_sdev_reply1/2`.

Notable details:
- Accept success is special because creating the accepted fd may block, so it cannot be completed in the main VFS thread.
- Cancellation may still produce success or partial success; it is not treated as guaranteed failure.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/sdev.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/select.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/select.c

Implements `select(2)` over regular files, pipes/FIFOs, character devices, and socket devices.

Key behavior:
- `do_select` validates `nfds`, allocates a `selectentry`, copies fd sets, validates timeout, maps selected fds to filps and file types, issues readiness checks, returns immediately when ready/error/poll, or suspends with an optional timer.
- Regular files are always ready.
- Pipes are checked synchronously with `pipe_check`; blocking pipe select records wanted operations in `filp_pipe_select_ops`.
- Character and socket devices use asynchronous driver select requests through `cdev_select` and `sdev_select`.
- `select_filter` manages per-filp pending, busy, blocked, and update state.
- `copy_fdsets` copies only the user-requested fd-set size in and out.
- `select_cancel_all` and `select_cancel_filp` tear down per-call and per-filp selector state, marking in-flight driver queries stale when needed.
- `select_return` copies ready sets and revives the blocked process.
- `select_timeout_check` returns when timeout expires, or converts the request to nonblocking if async replies are still deferred.
- `select_unsuspend_by_endpt` cleans up selectors when a process or driver exits, marking affected fds readable/writable so later I/O reports errors.

Reply handling:
- `select_cdev_reply1` and `select_sdev_reply1` process initial poll replies and restart deferred filps.
- `select_cdev_reply2` and `select_sdev_reply2` process later readiness notifications.
- `select_reply2`, `filp_status`, and `restart_proc` propagate status to all waiting select calls that share a filp/device.
- `select_restart_filps` retries deferred character/socket polling after a busy device becomes free.

Notable details:
- The module intentionally uses minimal locking so driver replies can be processed without blocking.
- Per-call `selectentry` state and per-filp select state are separate, allowing multiple processes or fds to share one in-flight select query.
- `select_dump` provides runtime diagnostics for active select entries and underlying device state.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/select.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/smap.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/smap.c

Maintains socket-driver mappings.

Key behavior:
- `init_smap` initializes one-based socket map numbers and clears protocol-family mappings.
- `smap_map` registers or replaces a socket driver by label, endpoint, and supported domains. It validates domains, prevents conflicts, handles stateless restarts by unsuspending old endpoint users and invalidating existing socket filps, then updates `smap` and `pfmap`.
- `smap_unmap_by_endpt` deregisters a socket driver on exit and invalidates sockets before clearing mappings.
- `smap_endpt_up` handles socket-driver restart announcements by invalidating preexisting sockets.
- `make_smap_dev` encodes one-based smap number in the high 32 bits of `dev_t` and driver-local socket ID in the low 32 bits.
- `get_smap_by_dev`, `get_smap_by_endpt`, and `get_smap_by_domain` decode socket device numbers and look up drivers.

Important dependencies:
- Uses `invalidate_filp_by_sock_drv` and `unsuspend_by_endpt` for driver restarts/exits.
- Consumed by `sdev.c`, `socket.c`, and `select.c`.

Notable details:
- Socket `dev_t` values are in a logical namespace separate from block/character device numbers.
- Endpoint lookup is O(n), with a TODO noting it could be cached.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/smap.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/socket.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/socket.c

Implements the upper VFS socket syscall layer: BSD socket calls plus fd/filp/vnode/PipeFS object management.

Key behavior:
- `get_sock_flags` converts `SOCK_CLOEXEC`, `SOCK_NONBLOCK`, and `SOCK_NOSIGPIPE` into open flags.
- `check_sock_fds` performs cheap per-process fd availability checks before creating sockets.
- `make_sock_fd` creates the VFS representation for an open socket: locks PipeFS, allocates vnode and filp/fd, creates a PFS socket node with `REQ_NEWNODE`, fills `v_sdev`, installs the filp, and applies close-on-exec.
- `do_socket` checks domain support through `smap`, asks `sdev_socket` for a socket, wraps it in a VFS fd, and closes the driver socket on wrapping failure.
- `do_socketpair` does the same for two connected sockets, with cleanup for partial fd creation.
- `get_sock` validates a fd as a socket and returns its `dev_t` and filp flags.
- `do_bind`, `do_connect`, `do_listen`, `do_accept`, `do_sendto`, `do_recvfrom`, `do_sockmsg`, option calls, name queries, peer queries, and `do_shutdown` translate syscall messages into lower-layer `sdev_*` calls.

Resume functions:
- `resume_accept` handles failed accept, accepted-but-error, and accepted-success cases. On success it verifies the listening socket, inherits accepted-socket flags, creates the accepted fd with `make_sock_fd`, and replies with fd plus address length.
- `resume_recvfrom` replies with byte count plus address length for successful receives.
- `resume_recvmsg` rereads and rewrites the user `msghdr` to update control length, flags, and optional address length before replying.

Notable details:
- Generic file operations on sockets such as read, write, ioctl, and select bypass this file and go directly to `sdev.c`.
- `do_sockmsg` supports at most one iovec element; libc is expected to consolidate vectors.
- Accepted sockets inherit `O_CLOEXEC`, `O_NONBLOCK`, and `O_NOSIGPIPE` from the listening socket.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/socket.c -->