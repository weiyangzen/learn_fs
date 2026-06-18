# Group Research: group_1231_netbsd_src_sources_os_bsd_netbsd_src_lib_librefuse_fuse_log_h_sourc_f497cc52c74b

Scope: `Docs/research_subset_a.md`, limited to the listed NetBSD `lib/librefuse` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse_log.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse_log.h

This public header declares the FUSE 3.7-style logging API exported by ReFUSE. It defines `enum fuse_log_level`, the `fuse_log_func_t` callback type, `fuse_set_log_func`, and printf-checked `fuse_log`.

Integration points: implemented by `refuse_log.c` and included by consumers through the broader FUSE headers. ABI risk is low, but callback signature and `va_list` lifetime are part of the public contract.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse_log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse_lowlevel.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse_lowlevel.h

This public header supplies a small subset of the FUSE low-level header surface, mainly `struct fuse_cmdline_opts`, `fuse_lowlevel_version`, and `fuse_cmdline_help`. The struct has explicit reserved space and a comment warning that size/layout changes break ABI compatibility.

Integration points: parsed and filled by `refuse_lowlevel.c` and used by setup wrappers in `refuse.c` and version adapters. Main risk is ABI drift from upstream FUSE command-line option structures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse_lowlevel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse_opt.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse_opt.h

This public option-parsing header defines FUSE option keys, `struct fuse_opt`, helper macros, the option callback type, and APIs for adding/copying/freeing/inserting args, composing `-o` option strings, parsing options, and matching templates.

Integration points: implemented by `refuse_opt.c`, consumed by command-line setup, mount compatibility wrappers, and librefuse's own `debug`/`fsname` options. Risks are template matching compatibility with libfuse and ownership rules for allocated argument vectors and `%s` destinations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/fuse_opt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse.c

This is the main ReFUSE implementation that maps high-level FUSE operations onto NetBSD puffs. It defines per-node state (`struct refusenode`), directory-buffer handling, FUSE context management, puffs vnode callbacks, setup/teardown, mount/unmount, loop, destroy, version/pkg helpers, and unsupported compatibility stubs.

The puffs callbacks translate lookup, getattr, setattr, readlink, mknod, mkdir, create, remove, rmdir, symlink, rename, link, open, close, read, write, readdir, reclaim, sync, statvfs, and unmount into `fuse_fs_*` calls. FUSE callbacks return negative errno-style results, while puffs expects positive errno values, so the file repeatedly negates or normalizes results. It also caches open `fuse_file_info` per puffs node and slurps complete directories into a puffs-formatted dirent buffer.

Setup parses FUSE command-line options, handles help/version, creates a `struct fuse`, initializes puffs operations, installs signal handlers, daemonizes through puffs, and mounts. Context handling uses pthread-specific storage when `MULTITHREADED_REFUSE` is enabled, otherwise a static context.

Risks: several comments mark incomplete areas, including proper multithreaded loop support, clean destruction/quiescence, `getgroups`, cache cleanup, and exact create/open semantics. Directory offset handling is acknowledged as unclear, fake inode allocation is not thread-safe, and close returns raw FUSE callback status rather than consistently converting negative errno in the same style as most other callbacks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/Makefile.inc

This make include adds the internal ReFUSE compatibility implementation files to `SRCS` and installs the internal compatibility headers through `INCS`. It includes buffer, channel, filesystem stacking, legacy, poll, session, and version-specific source/header files.

Integration points: pulled into the librefuse build from the parent makefile. Risk is build/export drift: adding a new compatibility version requires updating both `SRCS` and `INCS` consistently.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/buf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/buf.c

This file implements the FUSE 2.9 buffer-vector helpers. `fuse_buf_size` totals buffer sizes, and `fuse_buf_copy` copies between source and destination `fuse_bufvec`s while advancing vector indices and offsets.

Copy paths handle memory-to-memory with `memmove`, fd-to-memory with `read`/`pread`, memory-to-fd with `write`/`pwrite`, and fd-to-fd through a page-sized temporary heap buffer. EINTR is retried, partial success is returned rather than converted into failure, and `FUSE_BUF_FD_SEEK` selects positioned I/O.

Integration points: used by versioned `read_buf`/`write_buf` operation support from `fs.c`. Risks include ignored splice flags, short I/O behavior, unbounded `size_t` totals, and the fact that fd-to-fd cannot recover data already read but not written.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/buf.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/buf.h

This header declares the FUSE buffer API added in FUSE 2.9. It defines buffer flags, copy flags, `struct fuse_buf`, `struct fuse_bufvec`, `FUSE_BUFVEC_INIT`, `fuse_buf_size`, and `fuse_buf_copy`.

The header explicitly notes NetBSD ignores splice-related flags because Linux `splice(2)` has no direct local equivalent. ABI sensitivity is around the public struct layouts and macro initializer compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/chan.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/chan.c

This file implements ReFUSE's internal emulation of the old FUSE channel API. A `struct fuse_chan` stores mountpoint, copied args, associated `struct fuse`, and a deferred-destroy flag. A global expandable vector stores channels by integer index so old APIs that return "fds" can return a small handle.

The API creates/destroys channels, stashes/peeks/takes/finds them, sets associated fuse state, and exposes mountpoint/args/fuse/destroy-pending accessors. Optional pthread locking protects the global storage.

Risks: the storage can leak by design if old callers destroy without later unmounting, and `realloc` failure after assigning `storage.vec` would lose the old vector pointer. Semantics are only an approximation of Linux FUSE channels.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/chan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/chan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/chan.h

This internal header declares the opaque `struct fuse_chan` and hidden channel-management helpers used by version compatibility code. It is guarded against direct inclusion except through `<fuse.h>`.

Integration points: used by `v11.c`, `v21.c`, `v25.c`, and `v26.c` to emulate pre-FUSE-3 mount-before-new flows. Risks are hidden ABI coupling and global channel lifetime semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/chan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/fs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/fs.c

This is the filesystem stacking compatibility layer. It wraps a versioned `struct fuse_operations_v*` table in `struct fuse_fs`, clones the operation table, stores its version and user data, and exposes version-neutral `fuse_fs_*` dispatchers.

Each dispatcher sets `fuse_get_context()->private_data` to the filesystem layer's user data, then switches on operation-table version. It adapts changed prototypes across FUSE 1.1, 2.1, 2.2, 2.3, 2.5, 2.6, 2.8, 2.9, 3.0, 3.4, 3.5, and 3.8 for getattr, rename, open/release, read/write, statfs, readdir/getdir, chmod/chown/truncate/utimens, xattrs, ioctl, init/destroy, and newer operations like copy_file_range and lseek.

Special cases match libfuse behavior where missing open/release/opendir/releasedir/statfs are treated as success. Readdir has nested shims to translate old `getdir` callbacks and FUSE 2.x fillers to the FUSE 3.0 filler shape. Statfs conversion handles old `fuse_statfs`, Linux `statfs`, and modern `statvfs`.

Risks: the large version switch matrix is easy to desynchronize. `dt_to_mode` maps `DT_DIR` to `S_IFCHR`, which appears wrong. Several late-operation switches omit version 21 in unsupported-version cases, so a FUSE 2.1 operation could fall into `UNKNOWN_VERSION` rather than returning `-ENOSYS`. Callback prototype and operation-table layout stability are the central correctness constraints.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/fs.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/fs.h

This internal header declares the opaque `struct fuse_fs` and all filesystem stacking dispatchers implemented by `fs.c`. It documents the default missing-operation behavior: most return `-ENOSYS`, while open/release/opendir/releasedir/statfs return success.

Integration points: consumed by `refuse.c` and compatibility wrappers to call operation tables without caring about the exact `struct fuse_operations` version. Risk is declaration/implementation drift across many versioned function names and callback signatures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/legacy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/legacy.c

This file implements the removed legacy `fuse_invalidate` API in terms of modern `fuse_invalidate_path`. It treats `-ENOENT` as non-error because there was no cache entry to invalidate.

Integration points: paired with `legacy.h` and `refuse.c`'s no-cache `fuse_invalidate_path` implementation. Risk is semantic mismatch: ReFUSE does not currently cache paths, so invalidation is effectively a compatibility no-op.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/legacy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/legacy.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/legacy.h

This compatibility header defines removed FUSE types and functions: old `struct fuse_statfs`, Linux-specific `struct statfs` used by FUSE 2.1-2.4, `fuse_dirh_t`, `FUSE_DEBUG`, `fuse_invalidate`, and `fuse_is_lib_option`.

Integration points: included by version headers and `fs.c` for old callback struct definitions and statfs translation. Risks are Linux/NetBSD type-layout assumptions and preserving old public API while not conflicting with native system headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/legacy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/poll.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/poll.c

This file provides stubs for the FUSE poll notification API. `fuse_notify_poll` returns success and `fuse_pollhandle_destroy` does nothing.

The comment states ReFUSE does not implement `puffs_node_poll` and therefore will never invoke `fuse_operations.poll`. These functions exist only for API compatibility. Risk is that filesystems relying on real poll notification semantics will silently get no behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/poll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/poll.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/poll.h

This header declares the FUSE 2.8 polling API surface: opaque `struct fuse_pollhandle`, `fuse_notify_poll`, and `fuse_pollhandle_destroy`. It is inclusion-guarded for use through `<fuse.h>`.

Integration points: operation table headers from FUSE 2.8 onward include poll callback fields using this type. The declared API is mostly compatibility-only because `poll.c` does not implement real readiness notification.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/poll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/session.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/session.c

This file implements a minimal FUSE session API by treating `struct fuse_session *` as identical to `struct fuse *`. It returns the session pointer, exposes `puffs_getselectable(fuse->pu)` as the session fd, and forwards signal handler installation/removal to ReFUSE internals.

Integration points: used by FUSE 2.5+ signal/session-facing APIs. Risk is semantic mismatch: the fd is `/dev/puffs` selectable state, not a Linux `/dev/fuse` fd, so consumers must not assume Linux kernel protocol behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/session.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/session.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/session.h

This header declares the public session compatibility surface: opaque `struct fuse_session`, `fuse_get_session`, `fuse_session_fd`, `fuse_set_signal_handlers`, and `fuse_remove_signal_handlers`.

Integration points: implemented by `session.c` and used by FUSE 2.5/3.0 compatibility layers. The main risk is representing two conceptual objects, session and fuse, with one underlying pointer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/session.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v11.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v11.c

This file implements FUSE 1.1-era compatibility. It adapts `fuse_mount_v11` from a mountpoint plus NULL-terminated argv list into a `struct fuse_args`, then delegates to the FUSE 2.5 mount path. It also implements old unmount/destroy lifetime behavior through the global channel stash.

The unmount/destroy logic supports old callers that mount before creating `struct fuse`, destroy before unmounting, or unmount without ever creating. `fuse_new_v11` maps `FUSE_DEBUG` into options and delegates to `fuse_new_v21`; `fuse_loop_mt_v11` delegates to the common loop.

Risks: the old API allows lifetime orders that puffs does not naturally support, so this uses deferred destruction and can intentionally leak if a caller destroys but never unmounts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v11.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v11.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v11.h

This header defines FUSE 1.1 compatibility declarations. It provides the old `fuse_dirfil_t_v11` filler type, `struct fuse_operations_v11`, and prototypes for old mount, unmount, new, destroy, and multithreaded loop functions.

Integration points: consumed by `fs.c` for old operation-table dispatch and by `v11.c` for API symbols. Risk is exact historical struct layout: the operation table must match old binary expectations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v11.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v21.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v21.c

This file implements FUSE 2.1 compatibility. `fuse_mount_v21` converts a comma-separated option string into `struct fuse_args` and delegates to `fuse_mount_v25`. `fuse_new_v21` looks up the stashed channel by integer handle, inserts library options near the front of the saved argv, creates the common ReFUSE object, stores it in the channel, and finally mounts.

Integration points: bridges the old mount-before-new flow to the modern `__fuse_new` and `fuse_mount_v30` implementation. Risks are option-merging semantics and channel-index validity.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v21.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v21.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v21.h

This header defines the FUSE 2.1 operation table, which adds xattr callbacks and uses Linux `struct statfs` while still keeping old `getdir`, old open/read/write signatures, and old release/fsync shapes.

It also declares `fuse_mount_v21` and `fuse_new_v21`. Integration risk is operation-table layout compatibility across the transition from FUSE 1.x to early 2.x.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v21.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v22.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v22.c

This file implements FUSE 2.2 setup/teardown wrappers. `fuse_setup_v22` delegates to `fuse_setup_v26`, then returns a dummy fd because ReFUSE has no real channel fd to expose. `fuse_teardown_v22` ignores the dummy fd and mountpoint and delegates to common teardown.

Integration points: supports the older `fuse_setup` API shape while using common setup and puffs-backed mount lifecycle. Risk is callers that treat the returned fd as a real Linux FUSE device.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v22.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v22.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v22.h

This header defines FUSE 2.2 compatibility. It introduces `fuse_dirfil_t_v22`, whose `getdir` filler includes an inode number, defines `struct fuse_operations_v22`, and declares setup/teardown functions with an fd output.

Integration points: `fs.c` uses the filler type for getdir-to-readdir shims. ABI risk centers on the callback table layout and the fake fd returned by `v22.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v22.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v23.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v23.h

This header defines FUSE 2.3 compatibility. It introduces `fuse_fill_dir_t_v23`, adds `opendir`, `readdir`, `releasedir`, `fsyncdir`, `init`, and `destroy` to the operation table, while retaining deprecated `getdir`.

Integration points: `fs.c` converts between this filler and FUSE 3.0 fillers. Risks are coexistence of `getdir` and `readdir` and the nullary `init(void)` prototype.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v23.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v25.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v25.c

This file implements FUSE 2.5 mount, parse, and new wrappers. `fuse_mount_v25` creates and stashes a channel and returns its integer index as a nominal fd. `fuse_parse_cmdline_v25` adapts modern parsed options into old mountpoint/multithreaded/foreground outputs.

`fuse_new_v25` checks whether the args passed to `fuse_new` differ from those passed to `fuse_mount`, warns if they do, then delegates to `fuse_new_v21`. Risk is that the old API expects two arg vectors to be identical, and ReFUSE can warn but cannot correctly merge conflicting vectors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v25.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v25.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v25.h

This header defines the FUSE 2.5 operation table. It switches statfs to `struct statvfs` and adds `access`, `create`, `ftruncate`, and `fgetattr`.

It declares FUSE 2.5 mount, command-line parse, and new functions. Integration risks are create/open semantics and fallback behavior when newer callbacks are absent.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v25.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v26.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v26.c

This file implements FUSE 2.6 compatibility, where `fuse_mount` returns `struct fuse_chan *` rather than an fd. It delegates mounting to the FUSE 2.5 channel stash, returns the channel pointer, and maps `fuse_new_v26` back to the channel's stash index.

It also adapts unmount, setup, and teardown. `fuse_unmount_v26` permits a NULL channel and warns if the supplied mountpoint differs from the channel's saved mountpoint.

Risks are the same channel-lifetime approximations as older versions, plus pointer/index round-tripping through global storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v26.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v26.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v26.h

This header defines the FUSE 2.6 operation table. It changes `init` to take `struct fuse_conn_info *` and adds `lock`, `utimens`, and `bmap`.

It declares mount/unmount/new/setup/teardown APIs using `struct fuse_chan *`. Risks are callback prototype changes and the compatibility layer's ability to preserve old mount lifecycle behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v26.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v28.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v28.h

This header defines the FUSE 2.8 operation table. It adds bitfield flags including `flag_nullpath_ok`, reserves the remaining bits, and adds `ioctl` with signed `int cmd` plus `poll`.

Integration points: `fs.c` dispatches FUSE 2.8 ioctl/poll and adapts ioctl to later unsigned command forms. Risks include bitfield layout portability and ioctl command type conversion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v28.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v29.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v29.h

This header defines the FUSE 2.9 operation table. It expands flags with `flag_nopath` and `flag_utime_omit_ok`, and adds `write_buf`, `read_buf`, `flock`, and `fallocate`.

Integration points: paired with `buf.h`/`buf.c` and `fs.c` dispatchers. Risks are correct handling of buffer-vector operations and preserving old flag bit layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v29.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v30.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v30.c

This file implements FUSE 3.0 wrapper symbols by delegating to the common ReFUSE internals. It maps mount, unmount, new, destroy, multithreaded loop, and command-line parsing to `__fuse_mount`, `__fuse_unmount`, `__fuse_new`, `__fuse_destroy`, `__fuse_loop_mt`, and `__fuse_parse_cmdline`.

`fuse_loop_mt_v30` constructs a `struct fuse_loop_config` with `clone_fd` and default `max_idle_threads`. Risk is limited because this is mostly pass-through, but real multithreaded loop behavior is not implemented underneath.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v30.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v30.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v30.h

This header defines FUSE 3.0 compatibility. It introduces the FUSE 3.0 `fuse_fill_dir_t_v30`, defines `struct fuse_operations_v30`, removes old `getdir`, `utime`, `ftruncate`, `fgetattr`, and flag fields, and changes callbacks such as getattr/chmod/chown/truncate/rename/readdir/init.

It also declares FUSE 3.0 mount, unmount, new, destroy, loop, and parse APIs. Risks are broad because FUSE 3.0 is a major prototype transition point.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v30.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v32.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v32.c

This file implements the FUSE 3.2 multithreaded loop entry point. It simply forwards `fuse_loop_mt_v32(fuse, config)` to `__fuse_loop_mt`.

Integration risk is that the common loop currently delegates to single-threaded `fuse_loop`, so the FUSE 3.2 API is present but not semantically multithreaded.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v32.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v32.h

This header declares the FUSE 3.2 multithreaded loop API taking `struct fuse_loop_config *`. It contains no operation-table changes.

Integration points: implemented by `v32.c` and backed by common loop internals. Risk is behavioral mismatch with true libfuse multithreaded operation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v34.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v34.h

This header defines the FUSE 3.4 operation table. It is mostly the FUSE 3.0 table plus `copy_file_range`.

Integration points: `fs.c` dispatches `copy_file_range` only for versions 3.4 and newer. Risk is preserving the exact callback order and ssize_t return semantics for partial copies and errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v34.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v35.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v35.h

This header defines the FUSE 3.5 operation table. Relative to 3.4, the notable change is `ioctl` using `unsigned int cmd`.

Integration points: `fs.c` has separate `fuse_fs_ioctl_v28` and `fuse_fs_ioctl_v35` paths to adapt signed and unsigned command prototypes. Risk is ioctl command truncation or sign differences when crossing compatibility versions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v35.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v38.h -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v38.h

This header defines the FUSE 3.8 operation table. It extends the 3.5 table with `lseek`.

Integration points: `fs.c` dispatches `fuse_fs_lseek` for version 38 and returns `-ENOSYS` for older versions. Risks are return-value interpretation because `off_t` is also used for successful offsets and negative errno values in FUSE convention.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse/v38.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_compat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_compat.c

This file preserves old unversioned librefuse ABI symbols. It defines a previous `struct fuse_cmdline_opts_rev0` and compatibility implementations for old `fuse_daemonize`, `fuse_main_real`, `fuse_mount`, `fuse_new`, `fuse_destroy`, `fuse_parse_cmdline`, `fuse_unmount`, and `fuse_unmount_compat22`.

Most symbols use `__warn_references` so linkers can warn callers that they are binding to compatibility symbols. The implementations delegate to modern versioned APIs, often FUSE 3.0 or 2.6 paths.

Risks: this intentionally preserves ABI but not always source API compatibility, especially the old incorrect `fuse_daemonize` prototype and old command-line option struct size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_log.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_log.c

This file implements the FUSE logging API. The default log function writes formatted output to `stderr` with `vfprintf`; `fuse_set_log_func` installs a caller callback or resets to default; `fuse_log` formats variadic input and calls the current callback.

When `MULTITHREADED_REFUSE` is enabled, a pthread mutex protects reads/writes of the global log function pointer. Risk is holding the mutex while invoking user-provided log callbacks, which serializes logging but could deadlock if callbacks call back into logging.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_lowlevel.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_lowlevel.c

This file implements command-line parsing support and help/version stubs for the low-level API. It defines option templates for help, version, debug, foreground, singlethread, and `fsname`, prints ReFUSE option help, parses a single mountpoint as a non-option, and adds a default `fsname=refuse:<program>` if none was provided.

`__fuse_parse_cmdline` always sets `singlethread = 1` because puffs does not currently support multithreaded operation. `fuse_lowlevel_version` is a placeholder that prints nothing.

Risks: command-line behavior is intentionally partial compared with libfuse, `-s` cannot be disabled in practice, and version output is unimplemented.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_lowlevel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_opt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_opt.c

This file implements FUSE option parsing and argument-vector manipulation. It supports deep-copying and freeing `struct fuse_args`, appending and inserting args, composing comma-separated `-o` option strings with optional escaping, matching templates with `=` or space separators, and parsing all argv entries into a filtered output vector.

The parser treats program name as kept, handles `--`, `-ofoo` and `-o foo`, parses comma-separated option lists with backslash escaping, supports templates like `foo=%s` and `-x %d`, writes parsed values into offsets, and calls optional processors for keep/discard/error decisions.

Risks: `%s` values are heap-allocated into caller-provided fields without freeing prior contents, nonliteral `sscanf` formats are used by design, and ownership swaps between input and output `fuse_args` must be handled exactly to avoid leaks or double frees.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librefuse/refuse_opt.c -->