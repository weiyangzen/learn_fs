# Research: subset-b-009649

Grouped research for libfuse example and include files. Each section preserves the source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/notify_prune.c -->
# sources/user-network-fs/libfuse/example/notify_prune.c

## Purpose
`notify_prune.c` is a low-level FUSE example that exposes a single read-only file named `current_time`. The file content is a timestamp string, but the example intentionally uses very long entry and attribute timeouts plus `fi->keep_cache` to show that kernel-side dentry/inode/page-cache state can make content appear stale. A background thread calls `fuse_lowlevel_notify_prune()` for inode `FILE_INO` so the kernel prunes its cached node and sends `FORGET`; the server updates the timestamp only when lookup count falls to zero.

## Important APIs, Types, and Functions
The file uses `FUSE_USE_VERSION FUSE_MAKE_VERSION(3, 19)` and the low-level API from `fuse_lowlevel.h`. `struct fuse_lowlevel_ops tfs_oper` registers `init`, `destroy`, `lookup`, `getattr`, `readdir`, `open`, `read`, and `forget`. `struct options` is parsed with `fuse_opt_parse` for `--no-notify` and `--update-interval=%d`. `tfs_stat()` synthesizes root and file attributes. `update_fs()` fills global `file_contents` and `file_size`. `update_fs_loop()` is the notification thread and the direct integration point for `fuse_lowlevel_notify_prune()`.

## Control Flow
`main()` parses options and standard FUSE command-line flags, initializes file contents, creates and mounts a `fuse_session`, daemonizes, starts `update_fs_loop`, then runs either `fuse_session_loop` or `fuse_session_loop_mt` with a `fuse_loop_config`. Lookup of `/current_time` replies with long cache timeouts and increments `lookup_cnt`. Reads return the current global buffer through `reply_buf_limited()`. The background thread sleeps for the configured interval and, when notifications are enabled and the kernel has looked up the file, asks the kernel to prune `FILE_INO`. When the kernel later sends `forget`, `tfs_forget()` decrements `lookup_cnt` and refreshes the content at zero lookup count.

## State and Persistence
All filesystem state is process-local: `file_contents`, `file_size`, `lookup_cnt`, parsed options, and atomic `is_stop`. There is no persistent backing store. The example relies on kernel caches as observable state: entry/attr timeouts are set to `NO_TIMEOUT`, `open` sets `keep_cache`, and prune notifications force the kernel to drop awareness so a later lookup sees refreshed content. `lookup_cnt` is not protected by a mutex, so multi-threaded loops can race with the updater; this is acceptable for a small demonstration but important if reused.

## Dependencies and Integration Points
The program depends on libfuse low-level session APIs, pthreads, libc time formatting, and standard file-mode constants. It integrates with FUSE notification support through `fuse_lowlevel_notify_prune()` and tolerates `-ENOENT`, `-EBADF`, and `-ENODEV` during teardown. It also depends on FUSE sending `FORGET` requests after prune; without that behavior, `update_fs()` is not triggered by notification.

## Risks
The main correctness risk is unsynchronized access to `lookup_cnt`, `file_contents`, and `file_size` across the FUSE worker thread(s) and updater thread. The error message in `update_fs_loop()` incorrectly names `fuse_lowlevel_notify_store()` although it calls prune. `pthread_create` failure jumps to `err_out3` without unmounting first, so cleanup shape differs from the normal path. `update_interval` is not validated; zero causes a tight-ish loop with `sleep(0)`, and negative values are converted by `sleep`.

## Test Signals
Manual testing should mount with and without `--no-notify`, repeatedly `cat mnt/current_time`, and verify that the no-notify mode remains stale while notification mode changes after prune/forget cycles. Additional signals are lookup/forget balance under `-f -d`, successful unmount without aborting on expected notification errors, and behavior under both single-threaded and multi-threaded loops.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/notify_prune.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/notify_store_retrieve.c -->
# sources/user-network-fs/libfuse/example/notify_store_retrieve.c

## Purpose
`notify_store_retrieve.c` is a low-level FUSE example for actively pushing changed file data into the kernel page cache. It exposes one read-only `current_time` file whose userspace buffer changes periodically. Unlike invalidate/prune examples, the updater calls `fuse_lowlevel_notify_store()` to store the new bytes in the kernel and then `fuse_lowlevel_notify_retrieve()` to ask the kernel to send the stored bytes back for verification.

## Important APIs, Types, and Functions
The file uses `FUSE_USE_VERSION FUSE_MAKE_VERSION(3, 12)`, `struct fuse_lowlevel_ops`, and `struct fuse_bufvec`. `tfs_lookup()`, `tfs_forget()`, `tfs_getattr()`, `tfs_readdir()`, `tfs_open()`, and `tfs_read()` implement the single-file filesystem. `tfs_retrieve_reply()` is registered as `.retrieve_reply` and validates retrieved data with `fuse_buf_copy()`. `update_fs_loop()` performs `fuse_lowlevel_notify_store()` and `fuse_lowlevel_notify_retrieve()` while holding a mutex over lookup/open counters and the buffer setup.

## Control Flow
`main()` parses options, prepares the first timestamp, creates/mounts a low-level session, starts the updater thread, and enters the selected FUSE loop. Lookups reply with very long entry and attr timeouts; only after a successful reply does the code increment `lookup_cnt`. Opens set `keep_cache` and increment `open_cnt`. The updater refreshes `file_contents`, and if notifications are enabled and both `open_cnt` and `lookup_cnt` are positive, it stores the buffer in the kernel page cache and schedules a retrieve request using a duplicated expected string as cookie. On destroy, `is_umount` is set and the updater is joined.

## State and Persistence
State is in global process memory: current string, file size, lookup/open counts, mutex, `retrieve_status`, unmount flag, and updater TID. There is no disk persistence. The important external state is the kernel page cache, which receives stored bytes and later returns them through `retrieve_reply`. `retrieve_status` encodes whether data was stored but not yet validated (`1`) or validated (`2`); `main()` asserts that shutdown does not leave it stuck at `1`.

## Dependencies and Integration Points
This example integrates with FUSE notification APIs that require the kernel to know the node and usually require an open cached file to demonstrate effects. It uses pthreads for the producer thread and `fuse_bufvec` for zero-copy-ish buffer plumbing. It tolerates expected notification failures during unmount (`ENOENT`, `EBADF`, `ENODEV`) but otherwise aborts.

## Risks
`open_cnt` increments on open but is never decremented on release because no release handler exists; for a demo this keeps notification active, but a real server would leak open state. The assertion after `fuse_lowlevel_notify_retrieve()` contains `ret != -ENODEV`, likely intended to be `ret == -ENODEV`, so it does not symmetrically accept that teardown error. `retrieve_status` is written outside the mutex in `tfs_retrieve_reply()`, so it can race with shutdown assertions. `file_contents` is updated before taking `lock`, while reads access it without locking.

## Test Signals
Run with `--no-notify` and confirm repeated reads stay at the initially cached timestamp. Run without it and confirm reads advance once per update interval. Debug logs or breakpoints should show `retrieve_reply` setting `retrieve_status` to `2`. Teardown tests should unmount during active notification and confirm only expected kernel-side errors are accepted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/notify_store_retrieve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/null.c -->
# sources/user-network-fs/libfuse/example/null.c

## Purpose
`null.c` implements a single-file FUSE filesystem meant to be mounted on a regular file rather than a directory. Reads return zero-filled data up to a synthetic 4 GiB size, writes are discarded while reporting success, and truncate is accepted without changing size. The file also demonstrates the libfuse service API path for systemd socket activation.

## Important APIs, Types, and Functions
The high-level operation table `null_oper` registers `getattr`, `truncate`, `open`, `read`, and `write`. The service path uses `fuse_service_accept()`, `fuse_service_accepted()`, `fuse_service_append_args()`, `fuse_service_finish_file_requests()`, `fuse_service_expect_mount_format(S_IFREG)`, `fuse_service_main()`, `fuse_service_send_goodbye()`, and `fuse_service_exit()`. Non-service execution validates the mountpoint with `stat()` and calls `fuse_main()`.

## Control Flow
`main()` first tries to accept a FUSE service connection. If accepted, `null_service()` appends service-supplied arguments, finishes file requests, declares that the mount target should be a regular file, loosens mode to `0666`, runs `fuse_service_main`, sends goodbye, and exits through the service helper. If no service was accepted, it parses command-line options, requires a mountpoint, verifies that the mountpoint is a regular file, and calls `fuse_main`. Operations only accept path `/`; other paths return `ENOENT`.

## State and Persistence
The only mutable state is process-global `mode`, initially `0644` and changed to `0666` in service mode. File contents are not stored; reads synthesize zero bytes and writes discard input. Attribute times are generated from `time(NULL)` on each getattr. There is no persistence across process restarts.

## Dependencies and Integration Points
This example depends on high-level libfuse, `fuse_service.h`, standard libc, and a systemd socket/service pair when run in service mode. It expects service-managed mounts to target a file (`S_IFREG`) instead of a directory. Non-service mode depends on the caller providing an existing regular file mountpoint.

## Risks
`null_read()` only checks `offset >= 4GiB`; if `offset + size` exceeds 4 GiB it still returns the full requested size, so reads can report bytes beyond the advertised EOF. The Doxygen include line names `passthrough_fh.c`, probably a copy/paste mistake. Service mode changes permissions to world writable because dynamic users cannot predict ownership, which is correct for the example but unsuitable for sensitive data paths.

## Test Signals
Compile with `pkg-config fuse3`, create a regular file as mountpoint, mount, and verify `stat` reports a 4 GiB regular file. `dd if=<mountpoint>` should return zero bytes, and writes should report the written count without persisting data. Service-mode tests should use the matching socket/service unit and confirm `fuse_service_expect_mount_format(S_IFREG)` rejects directory mounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/null.socket.in -->
# sources/user-network-fs/libfuse/example/null.socket.in

## Purpose
`null.socket.in` is the systemd socket-activation unit template for the `null` sample FUSE service. It creates an accepting Unix sequential-packet socket in the configured FUSE service socket directory.

## Important APIs, Types, and Functions
This is a systemd unit, not C code. Key settings are `ListenSequentialPacket=@FUSE_SERVICE_SOCKET_DIR_RAW@/null`, `Accept=yes`, `SocketMode=@FUSE_SERVICE_SOCKET_PERMS@`, `RemoveOnStop=yes`, and `WantedBy=sockets.target`. The `@...@` tokens are build-time substitutions.

## Control Flow
When the socket unit starts, systemd listens at the generated path. Each accepted connection starts an instance of the paired `null@.service`, passing the accepted socket to the service process. `RemoveOnStop=yes` removes the socket path when the unit stops.

## State and Persistence
The runtime state is the systemd socket inode and accepted connections. There is no persistent state beyond the installed unit file. The socket path and mode are determined by configure-time substitutions and systemd's unit state.

## Dependencies and Integration Points
This file integrates with `null.c` through `fuse_service_accept()` and with `null@.service` through `Accept=yes` instance activation. It depends on systemd support for Unix sequential-packet sockets and on the libfuse service socket directory convention.

## Risks
Bad substitution values for socket directory or permissions can prevent mounting or expose the socket too broadly. Because `Accept=yes` creates per-connection service instances, the service template must be installed with the expected name and `ExecStart` must point to the compiled binary.

## Test Signals
After installation and `systemctl daemon-reload`, `systemctl start null.socket` should create the configured socket. A service-mode FUSE mount should cause an instance of `null@.service` to start, and stopping the socket should remove the socket path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/null.socket.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/null@.service -->
# sources/user-network-fs/libfuse/example/null@.service

## Purpose
`null@.service` is the systemd service template for running the `null` sample as a heavily sandboxed socket-activated FUSE server. It is intended to be paired with `null.socket.in`.

## Important APIs, Types, and Functions
Important service directives include `Type=exec`, `ExecStart=/path/to/null`, `DynamicUser=true`, `ProtectSystem=strict`, `PrivateTmp=true`, `PrivateDevices=true`, `PrivateUsers=true`, `PrivateNetwork=true`, `RestrictAddressFamilies=none`, `SystemCallFilter` allow/deny lists, empty `CapabilityBoundingSet`, `NoNewPrivileges=true`, `UMask=7777`, `DevicePolicy=closed`, and `OOMPolicy=continue`.

## Control Flow
For each accepted socket connection, systemd starts an instance of this template. The process runs the `null` binary, which detects service activation with `fuse_service_accept()`, requests/finishes service file handling, runs the FUSE main loop, sends goodbye, and exits. `CollectMode=inactive-or-failed` prevents failed units from accumulating.

## State and Persistence
State is managed by systemd: transient dynamic user identity, sandbox namespaces, logs to `/dev/ttyprintk`, and the unit lifecycle. No writable filesystem state is intentionally available because `ProtectSystem=strict`, `ProtectHome=true`, `UMask=7777`, and no capabilities constrain the process.

## Dependencies and Integration Points
The unit depends on a valid `ExecStart` path, systemd sandboxing features, `/dev/ttyprintk` for output, and the libfuse service protocol over the socket unit. The comments account for libfuse io_uring needing `mbind` and `sched_setaffinity`.

## Risks
The placeholder `ExecStart=/path/to/null` must be replaced. The syscall filter and namespace restrictions are intentionally strict and may break future libfuse behavior if it needs new syscalls or filesystem visibility. `StandardOutput=append:/dev/ttyprintk` depends on that device existing and being usable in the sandbox.

## Test Signals
`systemd-analyze verify null@.service` should pass after replacing `ExecStart`. Starting through `null.socket` should spawn instances under a dynamic user with no capabilities. Journal or ttyprintk output should show service startup and teardown, and syscall-filter failures should return `EL3RST`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/null@.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough.c -->
# sources/user-network-fs/libfuse/example/passthrough.c

## Purpose
`passthrough.c` is the simplest high-level FUSE passthrough example. It mirrors the host filesystem namespace visible from the process root by forwarding operations to libc/path-based syscalls. The comments explicitly note that performance is poor; the value is demonstrating high-level API callback coverage.

## Important APIs, Types, and Functions
`xmp_oper` registers high-level callbacks for attributes, access, readlink, directory listing, creation/removal, rename/link, chmod/chown/truncate, utimens, open/create, read/write, statfs, release, fsync, fallocate, xattrs, copy_file_range, lseek, and statx when available. `xmp_init()` configures `use_ino`, `parallel_direct_writes`, and cache timeouts. `passthrough_helpers.h` supplies `mknod_wrapper()` and `do_fallocate()`.

## Control Flow
`main()` sets `umask(0)`, strips two example-specific options (`--plus` and `--readdir-zero-inodes`) into globals, and delegates to `fuse_main`. Each callback maps the FUSE path directly to a libc operation: `lstat`, `access`, `opendir/readdir`, `mknod_wrapper`, `mkdir`, `unlink`, `rename`, `open`, `pread`, `pwrite`, and so on. For reads, writes, fallocate, copy, and lseek, the code uses `fi->fh` if available and opens by path only when libfuse calls statelessly.

## State and Persistence
The filesystem persists by modifying the underlying filesystem directly; no separate metadata database exists. Runtime state is limited to `fill_dir_plus`, `readdir_zero_ino`, and file descriptors stored in `fi->fh`. `xmp_init()` disables entry/attribute/negative cache timeouts unless `auto_cache` is set, reducing stale hardlink metadata.

## Dependencies and Integration Points
The code depends on high-level libfuse and platform feature macros for `utimensat`, xattrs, `copy_file_range`, and `statx`. It integrates with kernel caching through `struct fuse_config`, with directory cache prefill through `FUSE_FILL_DIR_PLUS`, and with direct I/O write concurrency by setting `parallel_direct_writes` when direct I/O is active.

## Risks
Because operations are path-based, races between lookup and operation are expected, especially around rename/unlink and symlinks. The filesystem starts at process `/`, so mounting it exposes the daemon's whole namespace subject to permissions. `MAX_ARGS` silently caps processed arguments at ten. `xmp_readdir()` ignores `fstatat` errors in plus mode and may report partial attributes. It implements `rename` flags only by rejecting any nonzero flags.

## Test Signals
Smoke tests should mount in a temporary directory and compare common operations against the backing root: create/read/write/truncate/link/rename/unlink, xattr when built, `copy_file_range`, sparse-file `lseek`, and `statx`. `--plus` should trigger attribute-prefilled readdir, while `--readdir-zero-inodes` should report zero inode numbers from directory entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough_fh.c -->
# sources/user-network-fs/libfuse/example/passthrough_fh.c

## Purpose
`passthrough_fh.c` is a more capable high-level passthrough example that stores file and directory handles in `struct fuse_file_info`. It still mirrors paths through libc syscalls, but file data operations are primarily file-descriptor based, enabling better performance, `nullpath_ok`, buffer-based reads/writes, flush/fsync, and lock support.

## Important APIs, Types, and Functions
`xmp_init()` enables `use_ino`, `nullpath_ok`, `parallel_direct_writes`, and zero cache timeouts. `struct xmp_dirp` stores a `DIR *`, current entry, and offset for stateful readdir. The operation table includes `opendir`, `readdir`, `releasedir`, `read_buf`, `write_buf`, `flush`, `fsync`, optional POSIX locks via `ulockmgr`, BSD `flock`, optional xattrs, copy-file-range, lseek, and statx.

## Control Flow
`main()` delegates to `fuse_main`. `open` and `create` store real backing file descriptors in `fi->fh`; later read/write/truncate/chmod/chown/utimens/fsync/fallocate operations use that descriptor when available. `opendir` stores an allocated `xmp_dirp` as `fi->fh`, and `readdir` uses `seekdir/telldir` offsets to support continuation. `read_buf` and `write_buf` expose FD-backed `fuse_bufvec` structures so libfuse can transfer data efficiently.

## State and Persistence
Persistent state is the backing filesystem. Runtime state consists of open backing file descriptors and allocated directory stream handles. Cache state is intentionally short-lived because entry, attr, and negative timeouts are set to zero. File locks and flock calls are forwarded to the backing file descriptors.

## Dependencies and Integration Points
This example integrates with libfuse high-level `nullpath_ok`, file-handle semantics, `fuse_buf_copy()`, platform xattr APIs, optional `libulockmgr`, `flock(2)`, `copy_file_range`, and `statx`. It uses `passthrough_helpers.h` for fallocate portability. FreeBSD directory offsets are adjusted because `telldir()` may return zero.

## Risks
The implementation remains vulnerable to path races for operations that cannot use `fi->fh`, such as unlink, rename, link creation, and xattrs. Directory handle allocation must be balanced by `releasedir`; leaks occur if abnormal teardown bypasses release. `flush` uses `close(dup(fi->fh))`, which is correct for close-like flushing but can surprise readers expecting fsync semantics. `rename` still rejects all nonzero flags.

## Test Signals
Test with common POSIX file operations while holding files open across rename/unlink to verify descriptor-based behavior. Exercise `read_buf`/`write_buf` through large reads/writes, `flock`, optional `fcntl` locks if built with `libulockmgr`, xattrs, fallocate, copy-file-range, lseek data/hole, and readdir continuation across small buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough_fh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough_helpers.h -->
# sources/user-network-fs/libfuse/example/passthrough_helpers.h

## Purpose
`passthrough_helpers.h` provides small portability helpers shared by passthrough examples. It abstracts fallocate support across Linux/POSIX/FreeBSD-style APIs and centralizes creation of backing filesystem nodes for FUSE mknod-like operations.

## Important APIs, Types, and Functions
`do_fallocate(int fd, int mode, off_t offset, off_t length)` maps to `fallocate`, `posix_fallocate` for mode zero, or FreeBSD `fspacectl` for punch-hole keep-size mode `0x3`, returning negative errno-style errors. `mknod_wrapper(int dirfd, const char *path, const char *link, int mode, dev_t rdev)` chooses `openat`, `mkdirat`, `symlinkat`, `mkfifoat`, FreeBSD socket creation via `bindat`, or `mknodat`.

## Control Flow
Callers use `do_fallocate()` from FUSE fallocate handlers and pass its return value directly or after sign conversion depending on API style. Callers use `mknod_wrapper()` for regular files, directories, symlinks, FIFOs, sockets on FreeBSD, and device nodes. The helper relies on mode type bits to choose the syscall.

## State and Persistence
The header keeps no state. It changes persistent backing filesystem state by creating files/nodes or allocating/deallocating space. Errors are communicated via return values and `errno` depending on helper.

## Dependencies and Integration Points
It depends on compile-time feature macros `HAVE_FALLOCATE`, `HAVE_POSIX_FALLOCATE`, and `HAVE_FSPACECTL`, plus FreeBSD socket headers for socket-file creation. It is integrated by `passthrough.c`, `passthrough_fh.c`, `passthrough_ll.c`, and `passthrough_hp.cc`.

## Risks
Return-value conventions differ: `do_fallocate()` returns negative errno values, while `mknod_wrapper()` returns syscall-style `-1` with `errno`. Callers must not mix those conventions. The FreeBSD socket path checks `strlen(path)` against `sun_path`, but uses the relative path with `bindat`; portability depends on that platform API. `posix_fallocate` is used only for mode zero, so other modes return `EOPNOTSUPP`.

## Test Signals
Build passthrough examples under different feature macro configurations. Test regular file, directory, symlink, FIFO, and device creation where permitted. Test fallocate mode zero, unsupported modes, and punch-hole mode on FreeBSD with `HAVE_FSPACECTL`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough_hp.cc -->
# sources/user-network-fs/libfuse/example/passthrough_hp.cc

## Purpose
`passthrough_hp.cc` is a high-performance C++ low-level passthrough filesystem. It mirrors a specified source directory, maintains its own inode map keyed by backing `(st_ino, st_dev)`, supports optional cache disabling, writeback cache, kernel FUSE passthrough mode, splice control, SELinux create contexts, direct I/O, and multi-threaded operation. It is intended as a production-quality template rather than a minimal demo.

## Important APIs, Types, and Functions
Key types are `SrcId`, `Inode`, `InodeMap`, and global `Fs fs`. `Inode` stores backing `fd`, source IDs, generation, passthrough `backing_id`, open count, atomic lookup count, and a mutex. `Fs` stores global config, source path, root inode, cache/pass-through flags, and a mutex. Important operations include `sfs_init`, `do_lookup`, `sfs_lookup`, `mknod_symlink`, `sfs_unlink`, `forget_one`, `do_readdir`, `sfs_create`, `sfs_tmpfile`, `sfs_open`, `do_passthrough_open`, `sfs_release`, `do_read`, `do_write_buf`, xattr handlers, and `assign_operations`.

## Control Flow
`parse_options()` uses cxxopts to parse source, mountpoint, debug, cache, splice, passthrough, SELinux, thread, clone-fd, direct-io, and mount options. `main()` resolves and validates the source directory, raises the file descriptor limit, opens the root with `O_PATH`, creates a low-level session, sets signal/fail handlers, daemonizes early, mounts, starts a teardown watchdog, and runs a single- or multi-threaded loop. Lookups open children with `O_PATH|O_NOFOLLOW`, validate that they stay on the source device and avoid `FUSE_ROOT_ID`, then insert/reuse `Inode` objects in `fs.inodes`. File opens create real read/write fds from `/proc/self/fd` or FreeBSD path info and may install a shared kernel passthrough backing file.

## State and Persistence
Persistent state is the backing source tree. Runtime state is substantial: a global inode map, per-inode fds, generation counters for recycled inodes, open counts, lookup counts, cached passthrough backing IDs, directory handles, and global mount behavior. With normal caching, timeout is 86400 seconds and the source is assumed to change only through the FUSE mount; `--nocache` sets timeout zero and includes unlink logic to close last-link fds before unlink to handle inode-number reuse. SELinux fscreate labels are staged per worker thread and immediately cleared after create-like syscalls.

## Dependencies and Integration Points
The file depends on `fuse_lowlevel.h`, `fuse_daemonize.h`, cxxopts, pthread/libc syscalls, syslog, resource limits, `/proc/self/fd` on Linux or `F_KINFO` on FreeBSD, and optional xattr support. It integrates with feature negotiation through `FUSE_CAP_PASSTHROUGH`, `FUSE_CAP_WRITEBACK_CACHE`, `FUSE_CAP_FLOCK_LOCKS`, `FUSE_CAP_SECURITY_CTX`, splice caps, `FUSE_CAP_DIRECT_IO_ALLOW_MMAP`, and `FUSE_CAP_NO_EXPORT_SUPPORT`. It uses `fuse_passthrough_open/close`, `fuse_req_get_payload()` for io_uring payloads, and `fuse_session_start_teardown_watchdog()`.

## Risks
Pointer-valued inode IDs require the pointed `Inode` to remain valid while the kernel may reference it; this is managed by lookup counts, so negative counts or incorrect forget handling aborts. Holding one fd per known dentry can exhaust descriptors despite `maximize_fd_limit()`. Cached mode can return stale or dangerous results if the source tree is modified outside the FUSE mount, and the header warns of possible data loss. `do_lookup()` returns `ENOTSUP` for mountpoints but does not close `newfd` on that path, which is a leak signal. Passthrough and direct I/O choices interact: read/write handlers treat unexpected fallback in passthrough mode as `EIO`.

## Test Signals
Exercise both default cached mode and `--nocache` while modifying the source through and outside the mount. Run xfstests-style create/unlink/rename/hardlink/readdirplus/open-after-unlink tests, descriptor-pressure tests, passthrough-capability fallback tests, SELinux create-label tests, direct-io mmap tests, and io_uring payload reads. Verify unmount and forced teardown do not leave backing IDs or fds open.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough_hp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough_ll.c -->
# sources/user-network-fs/libfuse/example/passthrough_ll.c

## Purpose
`passthrough_ll.c` is a low-level C passthrough filesystem that mirrors a source directory, defaulting to `/`. It is more explicit than the high-level variants: it maintains an inode table, maps FUSE node IDs to `struct lo_inode *`, uses directory handles, supports configurable cache modes, writeback, flock, and optional xattrs.

## Important APIs, Types, and Functions
Core types are `struct lo_inode` and `struct lo_data`. `lo_inode` stores linked-list pointers, a backing `fd`, source inode/device IDs, and a mutex-protected refcount. `lo_data` stores global options, timeouts, cache mode, source path, and root inode. `lo_opts` parses `writeback`, `source=`, `flock`, `xattr`, `timeout=`, and `cache=` mount options. The operation table `lo_oper` registers low-level handlers for lookup, create, tmpfile, read/write buffers, metadata, directory operations, forget, xattrs, locks, copy, lseek, and statx.

## Control Flow
`main()` parses libfuse command-line options, parses custom options into `lo`, validates and opens the source directory with `O_PATH`, creates a low-level session, mounts it, daemonizes, and runs the selected loop. `lo_do_lookup()` opens a child relative to its parent fd, stats it, reuses an existing `lo_inode` by `(ino,dev)` if present, or creates a new linked-list entry. `lo_forget()` and `lo_forget_multi()` decrement refcounts and free inode records when no kernel lookups remain. File and directory operations mostly use `openat`, `fstatat(AT_EMPTY_PATH)`, `/proc/self/fd`, and FD-backed `fuse_bufvec`.

## State and Persistence
Persistent state is all backing filesystem content. Runtime state is the linked list of known inodes and their open `O_PATH` fds, root fd, directory stream handles, and per-open file fds in `fi->fh`. Cache timeout derives from `cache=never|auto|always` unless explicitly set. `cache=never` sets direct I/O, `cache=always` sets keep-cache, and normal cache uses a one-second timeout.

## Dependencies and Integration Points
This file depends on low-level libfuse, pthread mutexes, Linux `AT_EMPTY_PATH`, `/proc/self/fd`, xattr APIs, `flock`, and helper functions in `passthrough_helpers.h`. It negotiates `FUSE_CAP_WRITEBACK_CACHE` and `FUSE_CAP_FLOCK_LOCKS`. It integrates with readdirplus by performing lookups for directory entries and manually forgetting entries that do not fit into the response buffer.

## Risks
Pointer-valued inode IDs must match the lifetime of allocated `lo_inode` records; incorrect refcount/forget behavior would create use-after-free. `create_new_inode()` can return NULL, but `fill_entry_param_new_inode()` casts the result to an inode without checking, so memory pressure can produce an invalid zero inode path. Some operations use `/proc/self/fd`, making Linux semantics important despite limited portability. Writeback cache changes O_WRONLY to O_RDWR and strips O_APPEND, accepting append atomicity loss.

## Test Signals
Mount with `source=<tmpdir>` and run metadata, data, hardlink, readdirplus, create/tmpfile, xattr, flock, fallocate, copy-file-range, lseek, and statx tests. Vary `cache=never`, `cache=auto`, `cache=always`, `writeback`, and `no_writeback`. Use small readdir buffers to verify lookup count repair when entries do not fit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/passthrough_ll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/poll.c -->
# sources/user-network-fs/libfuse/example/poll.c

## Purpose
`poll.c` demonstrates high-level FUSE poll/select support for readiness changes generated outside kernel file writes. It exposes sixteen read-only files named `0` through `F`; a producer thread periodically adds bytes to their counters and notifies poll waiters.

## Important APIs, Types, and Functions
`fsel_oper` registers `destroy`, `getattr`, `readdir`, `open`, `release`, `read`, and `poll`. Global arrays track per-file counts and `struct fuse_pollhandle *` values. `fsel_poll()` records poll handles and sets readiness bits. `fsel_producer()` mutates counters and calls `fuse_notify_poll()` followed by `fuse_pollhandle_destroy()`.

## Control Flow
`main()` initializes the mutex and starts the producer thread before entering `fuse_main`. `open` maps paths `/0` to `/F` to a numeric file handle and allows only one open per file by `fsel_open_mask`; files are direct I/O and nonseekable. `read` consumes up to the requested size from the per-file count and fills the buffer with the file's hex character. `poll` records a handle when provided and immediately reports `POLLIN` when the count is nonzero. The producer wakes every 250 ms, increments selected file counters up to ten, and notifies any saved poll handle for files that became ready.

## State and Persistence
All state is in process memory: open mask, poll handles, counts, global `struct fuse *`, mutex, stop flag, and producer thread. Counts behave like small pipe buffers. There is no persistence after unmount. Poll handles are single-use references that must be destroyed by the filesystem once no longer needed.

## Dependencies and Integration Points
The file uses high-level libfuse, `fuse_get_context()` to obtain `struct fuse *`, `fuse_notify_poll()`, pthreads, and POSIX `poll` event constants. It is paired with `poll_client.c`, which opens all files and uses `select()`.

## Risks
`fsel_open_mask` is modified without the mutex, so concurrent opens/releases can race. Only one open per file is supported because the file index is used as `fi->fh`; broader use would need open-instance allocation. If a client closes without a later poll replacement, handle lifetime depends on the most recent destroy path. Producer comments say 500 ms but the interval is 250 ms.

## Test Signals
Run `poll` mounted in a directory, run `poll_client` from that mount, and observe readiness/read counts rotating across hex files. Confirm opening the same file twice returns `EBUSY`, writes fail with `EACCES`, reads consume counts, and unmount joins the producer thread cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/poll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/poll_client.c -->
# sources/user-network-fs/libfuse/example/poll_client.c

## Purpose
`poll_client.c` is a small userspace test client for `poll.c`. It opens the sixteen files `0` through `F`, waits for readiness with `select()`, reads ready files, and prints per-file read counts.

## Important APIs, Types, and Functions
The program uses `open`, `select`, `FD_SET`, `FD_ISSET`, and `read`. It has only `main()`, a `hex_map` of file names, an fd array, and a fixed read buffer.

## Control Flow
`main()` opens each hex-named file in the current directory, computes `nfds` from the last opened fd plus one, then performs sixteen select/read iterations. For each iteration, it builds a read fd set, blocks indefinitely in `select`, prints `_:` for not-ready files, and reads/prints the byte count for ready files.

## State and Persistence
State is limited to process-local file descriptors and the stack/static read buffer. It does not write data and leaves persistence entirely to the mounted FUSE example.

## Dependencies and Integration Points
It assumes the current working directory is the root of a mounted `poll.c` filesystem. It depends on POSIX `select` and file descriptors small enough for `fd_set`. It exercises FUSE poll readiness by reading every descriptor that select reports.

## Risks
The program never closes fds explicitly, relying on process exit. `nfds` is computed from the last fd rather than the maximum across all fds, which is usually fine because opens are sequential but not guaranteed by API. It uses `select`, so very high-numbered fds beyond `FD_SETSIZE` would be unsafe.

## Test Signals
When run against `poll.c`, output should show changing readiness across files and positive byte counts. Running outside the mount should fail on `open`. Repeated runs should confirm the server's one-open-per-file policy releases handles on process exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/poll_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/printcap.c -->
# sources/user-network-fs/libfuse/example/printcap.c

## Purpose
`printcap.c` is a minimal low-level filesystem that mounts a temporary FUSE session only long enough to print the negotiated protocol version and supported kernel/library capability flags, then exits.

## Important APIs, Types, and Functions
The `capabilities[]` table maps `FUSE_CAP_*` bit flags to names, including newer flags such as passthrough, io_uring, idmap, and security context. `print_capabilities()` calls `fuse_get_feature_flag()` for each entry. `pc_init()` prints protocol version and capabilities, then calls `fuse_session_exit(se)`. `pc_oper` only registers `.init`.

## Control Flow
`main()` creates a temporary directory under `/tmp`, prints libfuse version information, creates a low-level session, installs signal handlers, mounts at the temp directory, and enters `fuse_session_loop`. The init callback runs during session initialization, prints capability information, asks the session to exit, and the normal cleanup path unmounts, removes signal handlers, destroys the session, removes the temp directory, and frees args.

## State and Persistence
The only global mutable state is `struct fuse_session *se`. The temporary mountpoint directory exists only for the process duration and is removed before exit. There is no filesystem content beyond initialization.

## Dependencies and Integration Points
The program depends on low-level libfuse and the kernel FUSE protocol. It integrates with the feature negotiation helpers rather than reading `conn->capable` directly. The hardcoded capability table must be updated as new `FUSE_CAP_*` flags are added.

## Risks
The global session pointer must be assigned before init runs; current control flow satisfies that. If mount or cleanup fails, `rmdir` may leave the temporary directory. The table can silently omit newer capabilities, so the program is only as complete as the maintained list.

## Test Signals
Running the binary should print the libfuse version, low-level version, protocol version, and one line per supported capability, then exit successfully. Failure to create/mount the temporary directory should produce a nonzero exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/printcap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_hl.c -->
# sources/user-network-fs/libfuse/example/service_hl.c

## Purpose
`service_hl.c` is a high-level API example for a systemd-managed FUSE service. It exposes a single regular file backed by a caller-provided device or file, using the shared `single_file` helper for metadata/options and service-mediated file acquisition.

## Important APIs, Types, and Functions
`struct service_hl` stores the requested device path, `struct fuse_service *`, and debug flag. `service_hl_oper` combines helper callbacks (`single_file_hl_getattr`, `readdir`, `open`, `opendir`, `statfs`, `chmod`, `utimens`, `fsync`, `chown`, `truncate`, `statx`) with local `init`, `read`, and `write`. `service_hl_opt_proc()` delegates to `single_file_opt_proc()` and captures the first non-option as `hl.device`.

## Control Flow
`main()` accepts only service activation, appends service args, parses options, requires a device argument, requests and receives the backing file through `single_file_service_open()`, finishes service file requests, configures `single_file`, declares a directory mount format, and calls `fuse_service_main()`. Reads and writes verify the path/open file handle, enforce direct-I/O policy, clamp operations to the configured size, and call `single_file_pread()` or `single_file_pwrite()`.

## State and Persistence
Service-local state is `hl` and the global `single_file` object from `single_file.c`. Persistent data lives in the opened backing file or block device. Metadata such as mode, timestamps, size, block count, and read-only/direct-I/O settings are held in memory and initialized by `single_file_configure()`.

## Dependencies and Integration Points
The file depends on high-level libfuse, `fuse_service.h`, pthread-aware single-file helpers, Linux filesystem headers for block/device metadata, and the matching systemd socket/service units. It integrates with the mount caller's environment by asking the service layer to provide the backing file rather than opening it directly inside the sandbox.

## Risks
The program refuses non-service execution, so running it directly exits early. Read/write return `ENOSYS` when direct I/O is requested but disallowed; clients must handle that. The backing file is opened with exclusive flags in the helper, which may fail under concurrent use. The high-level path checks depend on `fi->fh` being set by helper open/opendir callbacks.

## Test Signals
Install the matching socket/service units, start the socket, and mount with `mount -t fuse.service_hl <device> <mnt>`. Verify directory listing exposes the configured single file, reads/writes map to the backing file, read-only mode rejects writes, `size=` clamps I/O, `statx` reports configured metadata, and service teardown calls `single_file_close()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_hl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_hl.socket.in -->
# sources/user-network-fs/libfuse/example/service_hl.socket.in

## Purpose
`service_hl.socket.in` is the socket-activation template for the high-level `service_hl` FUSE service.

## Important APIs, Types, and Functions
Key unit settings are `ListenSequentialPacket=@FUSE_SERVICE_SOCKET_DIR_RAW@/service_hl`, `Accept=yes`, `SocketMode=@FUSE_SERVICE_SOCKET_PERMS@`, `RemoveOnStop=yes`, and `WantedBy=sockets.target`.

## Control Flow
Systemd listens on the generated sequential-packet socket. Each accepted connection starts a `service_hl@.service` instance. The service binary receives the socket and uses `fuse_service_accept()` to enter service mode.

## State and Persistence
The socket unit maintains runtime socket state only. Installed unit text is persistent, but mount sessions and accepted sockets are transient.

## Dependencies and Integration Points
The file must be installed with the paired `service_hl@.service` and the configured libfuse service socket directory. It integrates with mount requests for filesystem type `fuse.service_hl`.

## Risks
Incorrect build substitutions or permissions can make service mounts fail or make the service socket accessible to the wrong users. `Accept=yes` requires the template service name and binary path to match.

## Test Signals
`systemctl start service_hl.socket` should create the configured socket. A mount request should spawn `service_hl@...service`, and stopping the socket should remove the socket path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_hl.socket.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_hl@.service -->
# sources/user-network-fs/libfuse/example/service_hl@.service

## Purpose
`service_hl@.service` is the sandboxed systemd service template for the high-level single-file FUSE example.

## Important APIs, Types, and Functions
The service uses `Type=exec`, placeholder `ExecStart=/path/to/service_hl`, `DynamicUser=true`, strict filesystem/network/device/proc protections, syscall filters, no capabilities, `NoNewPrivileges=true`, `UMask=7777`, ttyprintk logging, and `OOMPolicy=continue`.

## Control Flow
Socket activation starts one instance per accepted service connection. The service binary accepts the service socket, requests its backing file/device from the mount caller, runs the high-level FUSE service loop, sends goodbye, and exits. `CollectMode=inactive-or-failed` avoids stale failed-unit accumulation.

## State and Persistence
Systemd manages dynamic identity, namespaces, resource limits, and logging. The unit intentionally provides little writable state; the FUSE service obtains its backing resource through the service protocol.

## Dependencies and Integration Points
The unit depends on replacing `ExecStart`, on systemd sandbox features, and on the paired socket unit. It is tuned for libfuse service operation and allows `mbind`/`sched_setaffinity` for libfuse io_uring behavior despite other syscall restrictions.

## Risks
The sandbox can block future libfuse or backing-file behavior if new syscalls or filesystem access are required. `UMask=7777` and no capabilities are deliberately restrictive. Logging to `/dev/ttyprintk` may not be available in all environments.

## Test Signals
Verify the unit with `systemd-analyze verify`, start through the socket, inspect `systemctl status` for dynamic-user sandboxing, and mount/unmount a high-level service filesystem. A syscall-filter violation should surface as `EL3RST`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_hl@.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_ll.c -->
# sources/user-network-fs/libfuse/example/service_ll.c

## Purpose
`service_ll.c` is the low-level API counterpart to `service_hl.c`. It demonstrates a systemd-managed FUSE service that exposes one file backed by a caller-provided device or file while using explicit low-level sessions and replies.

## Important APIs, Types, and Functions
`struct service_ll` stores `struct fuse_session *`, device path, `struct fuse_service *`, and debug flag. `service_ll_oper` combines low-level helper callbacks (`single_file_ll_lookup`, `getattr`, `setattr`, `readdir`, `open`, `statfs`, `statx`, `fsync`) with local `init`, `read`, and `write`. `service_ll_opt_proc()` delegates shared single-file options and captures the device argument.

## Control Flow
`main()` accepts service activation, appends args, parses service and FUSE command-line options, handles help/version, validates mountpoint and device, obtains the backing file through `single_file_service_open()`, finishes file requests, configures `single_file`, creates a low-level session, mounts via `fuse_service_session_mount()`, sends goodbye/releases the service object once mounted, and runs the chosen loop. `service_ll_read()` allocates a reply buffer, clamps reads, calls `single_file_pread()`, and replies with `fuse_reply_buf()`. `service_ll_write()` clamps writes, calls `single_file_pwrite()`, and replies with `fuse_reply_write()`.

## State and Persistence
Runtime state is the `ll` singleton, low-level session, loop config, and global `single_file`. Persistent data lives in the backing file/device. `service_ll_init()` sets `conn->time_gran = 1`; single-file metadata timeouts are zero in the helper.

## Dependencies and Integration Points
The file depends on low-level libfuse, `fuse_service.h`, and `single_file.c/h`. It integrates with systemd service activation, service-mediated file transfer, standard low-level session setup, and both single-threaded and multi-threaded FUSE loops.

## Risks
The low-level read path allocates `count` bytes after clamping; very large but valid reads can pressure memory. Direct I/O policy returns `ENOSYS` when disallowed. Error sign handling differs between helper functions and low-level replies, so the code carefully negates helper returns; regressions here would surface as wrong errno values. It sends goodbye/release before entering the loop once mounted, so later errors are ordinary session failures rather than service-handshake failures.

## Test Signals
Mount through `service_ll.socket`, read/write the single file, verify read-only, size, blocksize, direct-I/O, and sync options. Compare high-level and low-level behavior for metadata, statx, fsync, and error returns. Test single-thread and multi-thread options and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_ll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_ll.socket.in -->
# sources/user-network-fs/libfuse/example/service_ll.socket.in

## Purpose
`service_ll.socket.in` is the socket-activation template for the low-level `service_ll` FUSE service.

## Important APIs, Types, and Functions
It defines a systemd socket with `ListenSequentialPacket=@FUSE_SERVICE_SOCKET_DIR_RAW@/service_ll`, `Accept=yes`, `SocketMode=@FUSE_SERVICE_SOCKET_PERMS@`, `RemoveOnStop=yes`, and installation under `sockets.target`.

## Control Flow
Systemd listens on the configured socket and starts a new `service_ll@.service` instance for each accepted connection. The low-level service binary consumes the socket through `fuse_service_accept()`.

## State and Persistence
Runtime state is the socket file and active accepted connections. No filesystem or service state is persisted by the socket unit itself.

## Dependencies and Integration Points
The socket unit must match the service template and libfuse service socket directory. It is the entry point for `mount -t fuse.service_ll ...` style activation.

## Risks
Misconfigured socket path, mode, or missing paired template prevents service activation. Overly permissive socket mode can expose mount service entry points beyond intended users.

## Test Signals
Starting the socket should create the generated path; a mount request should activate `service_ll@.service`; stopping the socket should remove the path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_ll.socket.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_ll@.service -->
# sources/user-network-fs/libfuse/example/service_ll@.service

## Purpose
`service_ll@.service` is the sandboxed systemd template for the low-level single-file FUSE service.

## Important APIs, Types, and Functions
It has the same hardening profile as the high-level and null service templates: `Type=exec`, placeholder `ExecStart=/path/to/service_ll`, dynamic user, strict system/home/device/network/proc/kernel protections, syscall allow/deny filters, no capabilities, no new privileges, restrictive umask, ttyprintk logging, and OOM behavior set to continue.

## Control Flow
The paired socket starts an instance for each accepted connection. `service_ll` accepts the socket, negotiates resources, mounts a low-level FUSE session, releases the service handshake, and then handles FUSE requests until unmount.

## State and Persistence
The unit creates transient process, namespace, dynamic-user, and logging state. It intentionally avoids general writable state; backing data is provided through the FUSE service protocol instead of direct host access.

## Dependencies and Integration Points
It depends on systemd sandboxing and a corrected `ExecStart`. The syscall filter includes accommodations for libfuse io_uring. It integrates with `service_ll.socket.in` and `service_ll.c`.

## Risks
The placeholder binary path must be changed. Sandbox restrictions may need updates if libfuse, the C library, or deployment environment requires additional syscalls or devices. `RestrictFileSystems=` is empty, which intentionally leaves the directive present but not listing allowed filesystem types.

## Test Signals
`systemd-analyze verify` should pass after path substitution. Socket-activated mounting should run under the dynamic user with no capabilities. Kernel/syslog output should capture service diagnostics, and syscall filter hits should produce `EL3RST`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/service_ll@.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/single_file.c -->
# sources/user-network-fs/libfuse/example/single_file.c

## Purpose
`single_file.c` is shared implementation code for examples that expose one regular file backed by another file or block device. It supports both low-level and high-level FUSE operation handlers, common option parsing, metadata synthesis, statfs/statx, bounded reads/writes, timestamp updates, and service-mediated opening of backing resources.

## Important APIs, Types, and Functions
The global `struct single_file single_file` stores the backing fd, logical size, block count, mode, read-only/direct-IO/sync/block-device flags, blocksize, timestamps, and mutex. `SINGLE_FILE_INO` is `FUSE_ROOT_ID + 1`; `single_file_name` defaults to `single_file`. Important helpers include path/ino mapping functions, `dirbuf_add()`, `reply_buf_limited()`, `sf_stat()`, optional `sf_statx()`, `single_file_statfs()`, low-level handlers (`single_file_ll_*`), high-level handlers (`single_file_hl_*`), option functions, `single_file_service_open()`, I/O bounds checks, `single_file_pread/pwrite()`, `single_file_configure()`, and `single_file_close()`.

## Control Flow
Service examples parse options through `single_file_opt_proc()`, request/open a backing resource with `single_file_service_open()`, then call `single_file_configure()`. Configure stats the backing fd, derives block size and size from file or block-device ioctls, validates user-provided size/blocksize constraints, rounds size down to blocksize, computes block count, and initializes timestamps/name/mode. FUSE operations map root and single-file paths to fixed inode numbers, synthesize directory entries, reply with metadata, enforce read-only policy on open and metadata changes, clamp reads/writes to logical size, and call pread/pwrite loops on the backing fd.

## State and Persistence
The backing file/device contains persistent data. Metadata such as exposed name, mode bits, timestamps, read-only state, and logical size are process-local and reset on restart unless derived from the backing resource. `single_file_pwrite()` optionally `fsync`s when `sync` is set and updates mtime/ctime under the mutex. Attribute and entry timeouts are zero, favoring fresh metadata.

## Dependencies and Integration Points
The file includes both `fuse_lowlevel.h` and `fuse.h`, plus `fuse_service.h`. Linux block device integration uses `BLKSSZGET`, `BLKGETSIZE64`, and optional `statx` direct-I/O alignment fields. It is directly integrated by `service_hl.c` and `service_ll.c`, with compile-time macros enabling prototype visibility in `single_file.h`.

## Risks
`single_file_check_write()` compares and adjusts `size_t` counts against signed `isize`; invalid negative positions are not explicitly handled and rely on FUSE/kernel call patterns. `single_file_service_open()` retries read-only after permission failures and mutates `single_file.ro`; callers must expect downgrade. The code exposes immutable statx attributes for read-only mode but does not persist chmod/utimens to the backing file. `single_file_close()` closes `backing_fd` without checking whether it is valid.

## Test Signals
Unit-style tests should cover `parse_num_blocks()` suffixes, blocksize/size validation, read/write clamping at EOF, read-only write rejection, sync write fsync failures, stat/statx/statfs values, custom exposed filename, high-level and low-level directory listing, and service-open fallback from read-write to read-only. Integration tests should compare bytes in the exposed file against the backing file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/single_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/example/single_file.h -->
# sources/user-network-fs/libfuse/example/single_file.h

## Purpose
`single_file.h` declares the shared state, option keys, numeric helpers, and high-level/low-level operation helpers implemented by `single_file.c`. It lets service examples include only the API style they use through `USE_SINGLE_FILE_LL_API` and `USE_SINGLE_FILE_HL_API`.

## Important APIs, Types, and Functions
Inline helpers include `round_up`, `round_down`, `howmany`, `b_to_fsbt`, `b_to_fsb`, and `fsb_to_b`. `struct single_file` defines the backing fd, logical geometry, mode, flags, timestamps, and mutex. `enum single_file_opt_keys` and `SINGLE_FILE_OPT_KEYS` define FUSE option parser keys for `ro`, `rw`, `require_bdev`, `dio`, `nodio`, `sync`, `nosync`, `size=`, and `blocksize=`. The header declares service open/configure/close, pread/pwrite, bounds checks, and conditional low-level/high-level handlers.

## Control Flow
Including files define `USE_SINGLE_FILE_LL_API` or `USE_SINGLE_FILE_HL_API` before including this header, which exposes the matching callback prototypes. Runtime control flow is in `single_file.c`; this header shapes how service files build operation tables and parse options.

## State and Persistence
The header declares `extern struct single_file single_file`, a single global process state object. It does not persist anything by itself. Inline block conversion helpers read `single_file.blocksize`, so they depend on `single_file_configure()` having initialized block size before use.

## Dependencies and Integration Points
The declarations assume libfuse types such as `fuse_req_t`, `fuse_ino_t`, `struct fuse_file_info`, `fuse_fill_dir_t`, and `struct fuse_args` are visible from prior includes. It forward-declares `struct fuse_service` for service-mediated backing-file open. It is included by `single_file.c`, `service_hl.c`, and `service_ll.c`.

## Risks
Because inline helpers divide by `single_file.blocksize`, misuse before configuration can divide by zero. The conditional prototype blocks can hide needed declarations if callers forget the macro; the header emits only a preprocessor warning when neither API macro is defined. Global state makes multiple independent single-file instances in one process unsupported.

## Test Signals
Build both service examples to verify macro-gated prototypes match implementations. Exercise option parsing using `SINGLE_FILE_OPT_KEYS` and validate block conversion helpers after setting blocksize. Compile a file without API macros and confirm the warning appears.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/example/single_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/cuse_lowlevel.h -->
# sources/user-network-fs/libfuse/include/cuse_lowlevel.h

## Purpose
`cuse_lowlevel.h` declares the public low-level CUSE API for character devices in userspace. CUSE reuses FUSE low-level request/session machinery but presents a character-device operation surface rather than a filesystem tree.

## Important APIs, Types, and Functions
The header defaults `FUSE_USE_VERSION` to 29 if unset and includes `fuse_lowlevel.h`. `CUSE_UNRESTRICTED_IOCTL` is the only local flag. `struct cuse_info` contains desired device major/minor, device-info argument vector, and flags. `struct cuse_lowlevel_ops` contains callbacks for `init`, `init_done`, `destroy`, `open`, `read`, `write`, `flush`, `release`, `fsync`, `ioctl`, and `poll`; unlike FUSE low-level filesystem ops, these generally do not take inode numbers. Public constructors/runners are `cuse_lowlevel_new`, `cuse_lowlevel_setup`, `cuse_lowlevel_teardown`, and `cuse_lowlevel_main`.

## Control Flow
Applications fill `cuse_info` and `cuse_lowlevel_ops`, then call one of the setup/main helpers to create a `struct fuse_session` and enter normal FUSE session processing. The kernel routes character-device opens, reads, writes, ioctls, and poll events to the registered callbacks. `init_done` runs after initialization completes.

## State and Persistence
The header defines no state. Runtime state is held by the session created by the CUSE helpers and by application userdata. Device identity is controlled by major/minor and device info arguments; the actual character device lifetime is tied to setup/teardown.

## Dependencies and Integration Points
CUSE depends on low-level FUSE types (`fuse_req_t`, `struct fuse_file_info`, `struct fuse_conn_info`, `struct fuse_pollhandle`) and POSIX types for offsets and I/O vectors. It integrates with the same event-loop/session infrastructure used by low-level FUSE filesystems.

## Risks
The API is low-level: callback implementers must reply to requests correctly and manage unrestricted ioctl behavior carefully. If `CUSE_UNRESTRICTED_IOCTL` is set, ioctl argument handling can expose broader kernel/userspace ABI risk. Because the header defaults `FUSE_USE_VERSION`, including order can affect ABI selection if applications forget to define it explicitly.

## Test Signals
Compile a CUSE example such as `example/cusexmp.c`, create a device with specific dev info, and exercise open/read/write/ioctl/poll. ABI tests should include C++ inclusion through the `extern "C"` block and builds with explicit versus default `FUSE_USE_VERSION`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/cuse_lowlevel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse.h -->
# sources/user-network-fs/libfuse/include/fuse.h

## Purpose
`fuse.h` is the public high-level libfuse API header. It defines the path-oriented operation table, high-level configuration, context accessors, event-loop helpers, service-main wrapper for service mode, cache/poll helpers, and the stacking/module API used by FUSE filesystems.

## Important APIs, Types, and Functions
Important types include opaque `struct fuse`, `enum fuse_readdir_flags`, `enum fuse_fill_dir_flags`, `fuse_fill_dir_t`, `struct fuse_config`, `struct fuse_operations`, `struct fuse_context`, and opaque `struct fuse_fs`. `struct fuse_config` contains uid/gid/mode rewriting, entry/negative/attr timeouts, interrupt settings, inode remembering, hard-remove, inode reporting, direct I/O, kernel/auto cache, nullpath support, masks, no-rofd-flush, and `parallel_direct_writes`. `struct fuse_operations` defines callbacks from basic metadata and namespace operations through modern handlers such as `write_buf`, `read_buf`, `flock`, `fallocate`, `copy_file_range`, `lseek`, `statx`, and `syncfs`. Lifecycle helpers include `fuse_main`, `fuse_new`, `fuse_mount`, `fuse_unmount`, `fuse_loop`, `fuse_loop_mt`, `fuse_exit`, and `fuse_destroy`.

## Control Flow
Most high-level filesystems either call `fuse_main()` or manually call `fuse_new()`, `fuse_mount()`, and an event loop. `fuse_main()` parses options, installs signal handlers, creates the handle, registers operations, and runs the selected loop. During initialization, libfuse passes `struct fuse_conn_info` and mutable `struct fuse_config` to the filesystem's `init` callback; operation callbacks then receive paths and optional `struct fuse_file_info`. Filesystems return zero or negative errno values from callbacks. In FUSE 3.19 and newer, `fuse_service_main()` wraps service-mode startup from an accepted `struct fuse_service`.

## State and Persistence
The header defines API contracts rather than storing state. High-level runtime state lives in the opaque `struct fuse`, `struct fuse_fs` layers, operation private data, request contexts, and kernel caches controlled by `fuse_config`. Persistence is entirely filesystem-specific. Cache-related config fields are central because they decide how long kernel lookup, attribute, negative, and file-data state survive.

## Dependencies and Integration Points
`fuse.h` includes `fuse_common.h` and POSIX stat/statvfs/uio/time headers. It integrates high-level APIs with lower-level sessions through `fuse_get_session()`, with polling through `fuse_notify_poll()`, with cache invalidation through `fuse_invalidate_path()`, with cleanup of remembered inodes, and with stackable modules through `fuse_fs_*` wrappers and `FUSE_REGISTER_MODULE`.

## Risks
This header is ABI-sensitive; `struct fuse_config` explicitly warns that new options must be appended. Callback semantics contain many traps: `flush` is not `fsync`, `release` return values are ignored, writeback cache can cause reads on write-only opens and kernel-handled `O_APPEND`, `hard_remove` changes unlinked-open-file behavior, `parallel_direct_writes` can corrupt data if the filesystem lacks its own synchronization, and context pointers are valid only during the operation. Version-dependent `ioctl` signatures and `fuse_loop_mt` macros require matching `FUSE_USE_VERSION`.

## Test Signals
Header-level validation includes compiling representative high-level filesystems across supported `FUSE_USE_VERSION` values, exercising all optional callbacks through the `fuse_fs_*` wrapper API, checking C++ linkage, and verifying service-main availability at version 3.19+. Runtime tests should focus on cache options, readdir offsets/readdirplus, open/read/write/flush/release ordering, lock behavior, poll notifications, statx, copy-file-range, lseek, and syncfs behavior on fuseblk servers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libfuse/include/fuse.h -->
