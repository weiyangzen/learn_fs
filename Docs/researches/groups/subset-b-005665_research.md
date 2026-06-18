# subset-b-005665 Research

Grouped research for the source files in `subset-b-005665`. Each file section is marker-delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_parser.c -->
# sources/distributed-fs/ceph-client/fs/fs_parser.c

## Purpose
`fs_parser.c` is the VFS helper library for parsing filesystem mount/reconfigure parameters described by `struct fs_parameter_spec`. It matches incoming `struct fs_parameter` keys, handles negated flag forms such as `nofoo`, converts simple string/file/path values into typed `struct fs_parse_result` fields, and validates duplicate parameter descriptions under `CONFIG_VALIDATE_FS_PARSER`.

## Important APIs, Types, and Functions
- `lookup_constant()` searches a `constant_table` and is exported for filesystems with enum-like options.
- `__fs_parse()` is the central matcher/converter used by `fs_parse()` wrappers. It returns the matched option id, `-ENOPARAM`, or conversion errors.
- `fs_lookup_param()` turns a string/filename parameter into a `struct path`, optionally requiring a block device.
- `fs_param_is_bool/u32/s32/u64/enum/string/fd/file_or_string/uid/gid/blockdev()` are reusable conversion callbacks for parameter specs.
- `fs_validate_description()` checks duplicate parameter names with matching flag/value shape in validation builds.

## Control Flow
Parsing begins in `__fs_parse()`, which calls `fs_lookup_key()` to find an exact spec whose flag-ness matches the incoming value. For flag parameters, `fs_lookup_key()` also supports `no` prefixes when `fs_param_neg_with_no` is set and reports the result through `result->negated`. `__fs_parse()` warns on deprecated specs, then either sets `result->boolean` for flags or invokes the spec-provided conversion callback. The conversion helpers uniformly reject mismatched value types, honor `fs_param_can_be_empty` for empty strings, and populate a typed field in `struct fs_parse_result`.

## State and Persistence
The file has no persistent storage. It mutates only caller-owned `fs_parse_result`, `fs_parameter`, and output `struct path` objects. `fs_lookup_param()` temporarily converts kernel strings to `struct filename`, performs `filename_lookup()`, and returns a refcounted path that callers must release. UID/GID conversion is relative to `current_user_ns()`.

## Dependencies and Integration Points
This code integrates with `fs_context`, the new mount API, `namei` pathname lookup, user namespace ID conversion, and filesystem-specific parameter tables throughout `fs/`. It is directly exercised by `fsconfig()` paths in `fsopen.c` via `vfs_parse_fs_param()` and by many filesystem `->parse_param` implementations.

## Risks
The main risks are option table ambiguity, accidentally accepting an unexpected value shape, namespace-sensitive UID/GID rejection, and lifetime mistakes around returned paths. `fs_param_is_blockdev()` is a placeholder that returns success without conversion, so block-device users need `fs_lookup_param()` or higher-level validation. Negated flags are only supported for pure flag parameters, so specs that define both flag and value forms must be tested for intended precedence.

## Test Signals
Useful signals include fsconfig/mount tests for flags, `no`-prefixed flags, deprecated options, empty values, enum tables, invalid UID/GID mappings, path lookup failures, and block-device rejection. Validation builds should catch duplicate spec entries through `CONFIG_VALIDATE_FS_PARSER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_pin.c -->
# sources/distributed-fs/ceph-client/fs/fs_pin.c

## Purpose
`fs_pin.c` implements generic filesystem/mount pin lists and kill synchronization. Pins are attached to both a superblock and a mount so teardown code can locate callback-bearing objects that must be killed before the mount or group disappears.

## Important APIs, Types, and Functions
- `pin_insert()` adds an `fs_pin` to `s_pins` and `mnt_pins`.
- `pin_remove()` removes both hlist links and wakes waiters after marking the pin done.
- `pin_kill()` runs a pin's `kill()` callback exactly once, or waits uninterruptibly while another thread kills it.
- `mnt_pin_kill()` drains all pins on a `struct mount`.
- `group_pin_kill()` drains all pins from a superblock/group hlist.

## Control Flow
Insertion and removal are serialized by the global `pin_lock`. Killers repeatedly take an RCU read lock, sample the first hlist node with `READ_ONCE()`, and call `pin_kill()`. `pin_kill()` uses the pin waitqueue lock to transition `done` from unset to `-1` for the killer, calls the supplied callback outside RCU, or sleeps until `pin_remove()` sets `done` positive and wakes waiters.

## State and Persistence
State lives in `struct fs_pin`: two hlist links, a waitqueue, a `done` field, and a kill callback. There is no on-disk state. The object lifetime is externally owned, and waiters rely on the `done` protocol and RCU to avoid use-after-free while a kill callback is in progress.

## Dependencies and Integration Points
The file depends on VFS mount internals (`mount.h`), superblock pin lists, spinlocks, waitqueues, and RCU. It is an infrastructure primitive for code that pins mounts or superblocks until asynchronous cleanup can safely run.

## Risks
Correctness depends on the kill callback eventually calling `pin_remove()` or otherwise completing the state transition. A callback that sleeps indefinitely will block all drainers. The global lock is small-scope but serializes all pin list mutation. Kill paths use uninterruptible sleep, so deadlocks in callback teardown show up as stuck tasks.

## Test Signals
Stress mount teardown, namespace teardown, repeated concurrent killers, and callback paths that remove pins during drain. Lockdep/RCU diagnostics and hung-task detection are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_pin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_struct.c -->
# sources/distributed-fs/ceph-client/fs/fs_struct.c

## Purpose
`fs_struct.c` manages each task's filesystem view: root path, current working directory, umask, users count, and exec/unshare state. It supplies safe setters, cloning, unsharing, exit cleanup, and chroot reference updates across tasks.

## Important APIs, Types, and Functions
- `set_fs_root()` and `set_fs_pwd()` replace root/pwd with path refcounting under `fs->seq`.
- `chroot_fs_refs()` rewrites task `root`/`pwd` references from an old root to a new root.
- `free_fs_struct()`, `exit_fs()`, `copy_fs_struct()`, and `unshare_fs_struct()` own lifetime and copy-on-unshare behavior.
- `init_fs` is the initial boot-time `fs_struct`.

## Control Flow
Setters grab a reference on the new path, update the field under a seqlock writer section, then drop the old path. `chroot_fs_refs()` scans every process/thread under `tasklist_lock`, locks each task, replaces matching root/pwd paths under the target `fs_struct` seqlock, then balances old path references after the scan. `exit_fs()` clears `tsk->fs` and decrements `users`; the last user frees the structure. `copy_fs_struct()` snapshots root and pwd under the old seqlock and increments both path refs.

## State and Persistence
The state is entirely in-memory task state. Path objects are refcounted with `path_get()`/`path_put()`. `users` tracks sharing between threads or clone users. `seq` gives lockless path readers a consistency point.

## Dependencies and Integration Points
This code integrates with scheduler task locking, path refcounting, `tasklist_lock`, init task setup, chroot/pivot-root style operations, and clone/unshare/exit code. It is core VFS process state, not Ceph-specific despite residing in the source subset.

## Risks
The key risks are reference imbalance when replacing root/pwd, task iteration races, and seqlock misuse by readers. `chroot_fs_refs()` walks all tasks and can be expensive, but it is limited to rare namespace/root transitions. `exit_fs()` relies on taking task and fs locks in the established order.

## Test Signals
Regression signals include `chdir`, `chroot`, `pivot_root`, `unshare(CLONE_FS)`, thread sharing, exec, process exit under parallel cwd/root changes, path refcount leaks, and lockdep warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fs_struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fserror.c -->
# sources/distributed-fs/ceph-client/fs/fserror.c

## Purpose
`fserror.c` provides asynchronous filesystem error reporting. It lets filesystem and iomap code report metadata, shutdown, and I/O errors to a superblock callback and fsnotify without running arbitrary notification code in atomic or locked contexts.

## Important APIs, Types, and Functions
- `fserror_mount()` initializes `sb->s_pending_errors` with a bias.
- `fserror_unmount()` drops the bias and waits for pending reports to drain.
- `fserror_report()` allocates an event, records type/range/error/inode, and schedules work.
- `fserror_worker()` invokes `sb->s_op->report_error()` when present and emits `fsnotify(FS_ERROR, ...)`.
- `fserror_init()` initializes a mempool of `struct fserror_event`.

## Control Flow
Callers invoke `fserror_report()` with a negative errno and optional inode/range. The allocator increments `s_pending_errors` only if nonzero and `SB_ACTIVE` is still set. If allocation and optional `igrab()` succeed, work is queued. The worker builds a positive error number for userspace-facing `fs_error_report`, calls the filesystem callback, sends fsnotify, drops the inode, decrements the pending counter, and returns the event to the mempool. Unmount waits until the biased pending counter goes below one.

## State and Persistence
State is volatile: a global mempool and per-superblock pending counter. Events hold a superblock pointer, optional active inode ref, error metadata, and a work item. There is no persistent error journal in this file; delivery can be lost under allocation or inode ref failure and is logged rate-limited.

## Dependencies and Integration Points
It integrates with `fs/super.c` mount/unmount lifecycle, `super_operations::report_error`, fsnotify, iomap error reporters, ext4/btrfs callers, inode refcounting, and workqueues.

## Risks
The file is sensitive to teardown ordering: `SB_ACTIVE` and `s_pending_errors` checks must prevent reports from racing past unmount. Since the mempool is finite, extreme bursts can still lose reports. Callers must pass negative errors and matching inode/superblock pairs; violations only warn. `report_error` implementations must tolerate process-context asynchronous delivery.

## Test Signals
Tests should trigger file I/O errors, metadata errors, shutdown errors, unmount with queued reports, memory pressure allocation fallback, and fsnotify consumers. Signals include no use-after-free during unmount, rate-limited lost-report logs only under induced failure, and callback delivery ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fserror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fsopen.c -->
# sources/distributed-fs/ceph-client/fs/fsopen.c

## Purpose
`fsopen.c` implements the fd-based mount API entry points `fsopen(2)`, `fspick(2)`, and `fsconfig(2)`. It creates filesystem contexts, exposes their logs through anonymous fds, applies parameters, and transitions contexts through create/reconfigure phases.

## Important APIs, Types, and Functions
- `fscontext_fops` exposes `.read` for context log messages and `.release` for `put_fs_context()`.
- `fsopen()` creates a mount `fs_context` by filesystem type.
- `fspick()` creates a reconfiguration `fs_context` for an existing mount root.
- `fsconfig()` submits flags, strings, binary blobs, paths, fds, and create/reconfigure commands.
- `vfs_cmd_create()`, `vfs_cmd_reconfigure()`, and `vfs_fsconfig_locked()` enforce the context state machine.

## Control Flow
`fsopen()` validates mount permission and flags, resolves the filesystem type, allocates a mount context, puts it in `FS_CONTEXT_CREATE_PARAMS`, attaches a log, and returns an anonymous fd. `fspick()` performs a pathname lookup, requires the target dentry to be the mount root, builds a reconfigure context, and returns an fd. `fsconfig()` validates command-specific user arguments, copies the key/value into a `struct fs_parameter`, locks `fc->uapi_mutex`, and either parses the parameter or runs create/reconfigure. Create calls `vfs_get_tree()`, checks LSM mount permission, drops `s_umount`, and moves to `FS_CONTEXT_AWAITING_MOUNT`. Reconfigure checks `CAP_SYS_ADMIN` in the superblock user namespace, locks `s_umount`, calls `reconfigure_super()`, and cleans the context.

## State and Persistence
State is in `struct fs_context`: phase, log ring, root, fs type, uapi mutex, and parsed parameters. The anonymous fd owns a reference to the context. User-provided strings, blobs, filenames, and files are freed after parsing unless stolen by the filesystem or LSM.

## Dependencies and Integration Points
This code integrates with `fs_context` helpers, `anon_inode_getfd`, `vfs_get_tree`, `reconfigure_super`, LSM hooks, path lookup, mount capabilities, and the parameter parser in `fs_parser.c`. It is the main syscall bridge into filesystem-specific `init_fs_context` and `parse_param`.

## Risks
The main risks are state-machine bypass, user pointer copy limits, stolen-parameter ownership, and superblock lock handling. `fsconfig()` caps binary parameters at 1 MiB and strings/keys at 256 bytes, so compatibility depends on callers respecting those limits. Create paths must drop `s_umount` exactly once after `vfs_get_tree()` succeeds. Reconfiguration permission is checked in the target superblock user namespace, not only the caller namespace.

## Test Signals
Exercise fsopen/fspick/fsconfig success and failure phases, invalid command/value combinations, oversized strings/blobs, path-empty behavior, fd parameters, LSM denials, create-excl behavior, reconfigure permission failures, context log reads, and release cleanup after partial configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fsopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/Kconfig -->
# sources/distributed-fs/ceph-client/fs/fuse/Kconfig

## Purpose
This Kconfig file defines build-time feature switches for FUSE, CUSE, virtio-fs, DAX support, passthrough backing-file operations, and FUSE io_uring transport.

## Important Options
- `FUSE_FS` is the base tristate and selects POSIX ACL and iomap support.
- `CUSE` depends on `FUSE_FS` and builds character-device-in-userspace support.
- `VIRTIO_FS` depends on `FUSE_FS` and selects `VIRTIO`.
- `FUSE_DAX` depends on virtio-fs, FS_DAX, and DAX, and selects interval trees.
- `FUSE_PASSTHROUGH` depends on `FUSE_FS` and selects `FS_STACK`.
- `FUSE_IO_URING` depends on `FUSE_FS` and `IO_URING`.

## Control Flow
There is no runtime control flow. The configuration symbols gate object inclusion in the Makefile and compile-time code paths in the FUSE implementation.

## State and Persistence
Selections persist in the kernel build configuration. Runtime feature availability in FUSE connections is then negotiated or enabled by mount/init flags and module parameters.

## Dependencies and Integration Points
The options map directly to `fs/fuse/Makefile` object lists and conditional code in `dax.c`, `backing.c`, `dev_uring.c`, virtio-fs, and sysctl/control paths.

## Risks
Default-y booleans for DAX, passthrough, and io_uring can expose code paths when dependencies are enabled, so build matrices need to include both enabled and disabled variants. Dependency drift can create unresolved symbols or feature negotiation mismatches.

## Test Signals
Build FUSE as built-in and module, with CUSE/virtio-fs/DAX/passthrough/io_uring toggled independently where dependencies permit. Confirm disabled configurations compile out ioctl, DAX, and uring paths cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/Makefile -->
# sources/distributed-fs/ceph-client/fs/fuse/Makefile

## Purpose
The Makefile assembles the FUSE, CUSE, and virtio-fs kernel objects according to Kconfig selections.

## Important Build Rules
- `obj-$(CONFIG_FUSE_FS) += fuse.o`
- `obj-$(CONFIG_CUSE) += cuse.o`
- `obj-$(CONFIG_VIRTIO_FS) += virtiofs.o`
- `fuse-y` includes trace, device, directory, file, inode, control, xattr, ACL, readdir, ioctl, and iomode code.
- Conditional additions include `dax.o`, `passthrough.o backing.o`, `sysctl.o`, and `dev_uring.o`.
- `ccflags-y = -I$(src)` supports local trace event includes.

## Control Flow
No runtime flow exists. Build-time expansion determines which object files are linked into `fuse.o`, `cuse.o`, and `virtiofs.o`.

## State and Persistence
The file contributes only to build artifacts. It does not own runtime state.

## Dependencies and Integration Points
It mirrors `Kconfig` and must stay aligned with conditional declarations and `IS_ENABLED()` use in the source. `trace.o` is intentionally first to surface ftrace errors early.

## Risks
Missing conditional objects can cause unresolved references; extra objects can include dead features. Because `backing.o` is tied to `CONFIG_FUSE_PASSTHROUGH`, ioctls in `dev.c` must preserve `IS_ENABLED()` guards.

## Test Signals
Kernel builds under varied FUSE configs are the primary signal. Compile checks should cover `CONFIG_FUSE_FS=m/y`, `CONFIG_CUSE=m/y`, and combinations of DAX, passthrough, SYSCTL, and io_uring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/acl.c -->
# sources/distributed-fs/ceph-client/fs/fuse/acl.c

## Purpose
`acl.c` maps VFS POSIX ACL operations to FUSE xattr requests while preserving compatibility with older daemons that did not advertise `FUSE_POSIX_ACL`.

## Important APIs, Types, and Functions
- `__fuse_get_acl()` fetches ACL xattrs and converts them with `posix_acl_from_xattr()`.
- `fuse_no_acl()` rejects ACL interaction for unsupported daemons outside the initial user namespace.
- `fuse_get_acl()` is the dentry operation path.
- `fuse_get_inode_acl()` is the inode permission-check path and returns `NULL` when the daemon did not opt into kernel ACL checks.
- `fuse_set_acl()` serializes/removes ACL xattrs and invalidates cached ACLs/attributes when appropriate.

## Control Flow
ACL reads reject RCU mode, bad inodes, disabled getxattr, and unsupported ACL types. They allocate one page, issue `fuse_getxattr()`, and map empty, `-ENODATA`, and supported `-EOPNOTSUPP` cases to no ACL. Set operations validate support, convert ACLs to xattr bytes, apply `FUSE_SETXATTR_ACL_KILL_SGID` when the kernel ACL feature is active and the caller lacks group/capability privileges, then call `fuse_setxattr()` or `fuse_removexattr()`.

## State and Persistence
ACL data is persisted by the userspace daemon through xattrs. Kernel-side cached ACLs and inode attributes are invalidated after successful set/remove only for `fc->posix_acl` daemons.

## Dependencies and Integration Points
This file depends on `fuse_i.h`, POSIX ACL helpers, POSIX ACL xattr names, FUSE xattr operations, mount idmaps, and user namespace conversion through `fc->user_ns`.

## Risks
Backwards compatibility is subtle: daemons without `FUSE_POSIX_ACL` may still expose ACL xattrs but rely on userspace permission checks. The one-page read buffer means oversized ACL xattrs return `-E2BIG`. RCU ACL lookup is not supported and returns `-ECHILD`, so callers must retry in ref-walk context.

## Test Signals
Test ACL get/set/remove for daemons with and without `FUSE_POSIX_ACL`, user namespaces/idmapped mounts, large ACL xattrs, setgid stripping behavior, bad inode handling, and xattr-disabled fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/backing.c -->
# sources/distributed-fs/ceph-client/fs/fuse/backing.c

## Purpose
`backing.c` manages FUSE passthrough backing files registered by privileged userspace. It stores kernel `struct file` references in a per-connection IDR and returns integer backing IDs for direct-operation mapping.

## Important APIs, Types, and Functions
- `fuse_backing_files_init()` and `fuse_backing_files_free()` initialize and destroy `fc->backing_files_map`.
- `fuse_backing_open()` validates and registers a backing fd.
- `fuse_backing_close()` removes a backing id.
- `fuse_backing_lookup()` finds and refcounts a backing file under RCU.
- `fuse_backing_get()`/`fuse_backing_put()` manage `struct fuse_backing` lifetime.

## Control Flow
Open requires `fc->passthrough` and `CAP_SYS_ADMIN`, rejects flags/padding, obtains the raw fd, requires a regular non-directory file, checks stack depth against `fc->max_stack_depth`, allocates a `fuse_backing`, stores the file and prepared credentials, and allocates an IDR id starting at 1. Close performs the same feature/capability checks, removes the id under `fc->lock`, and drops the backing reference. Lookup uses RCU plus `refcount_inc_not_zero()` to return a stable object.

## State and Persistence
State is per-connection in an IDR. Each `fuse_backing` holds a file ref, credentials, refcount, and RCU lifetime. There is no disk state; persistence is the lifetime of the FUSE connection or until explicit close.

## Dependencies and Integration Points
This file is enabled by `CONFIG_FUSE_PASSTHROUGH`, called from `FUSE_DEV_IOC_BACKING_OPEN/CLOSE` in `dev.c`, and consumed by passthrough read/write/splice/mmap paths in other FUSE code. It integrates with `FS_STACK` stack-depth protection.

## Risks
The TODO notes CAP_SYS_ADMIN may be overly strict until backing files are visible to tools such as `lsof`. The stack-depth check prevents recursive stacking loops but relies on correct `max_stack_depth`. Prepared credentials must be released, and IDR removal must not race with lookup users, hence RCU freeing.

## Test Signals
Test ioctl registration/close, permission failures, non-regular fds, directory fds, stack-depth rejection, lookup while closing, connection teardown with live backings, and disabled `CONFIG_FUSE_PASSTHROUGH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/backing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/control.c -->
# sources/distributed-fs/ceph-client/fs/fuse/control.c

## Purpose
`control.c` implements the `fusectl` pseudo-filesystem that exposes live FUSE connection controls and counters under per-connection directories.

## Important APIs, Types, and Functions
- `fuse_ctl_add_conn()` creates a directory named by connection device id with `waiting`, `abort`, `max_background`, and `congestion_threshold` files.
- `fuse_ctl_remove_conn()` removes that directory and clears inode-private connection pointers.
- `fuse_conn_abort_write()` aborts a connection.
- `fuse_conn_waiting_read()` reports `fc->num_waiting`.
- limit readers/writers expose and adjust `max_background` and `congestion_threshold`.
- `fuse_ctl_init()`/`fuse_ctl_cleanup()` register and unregister the `fusectl` filesystem.

## Control Flow
Mounting `fusectl` creates a singleton superblock with `simple_fill_super()`, records it under `fuse_mutex`, and adds existing connections. Connection add/remove is also serialized by `fuse_mutex`. File operations acquire a temporary `fuse_conn` reference from inode private data, perform the read/write operation, and drop it. Writes to `max_background` update `fc->blocked` under `bg_lock` and wake blocked waiters when limits allow progress.

## State and Persistence
State is in the singleton `fuse_control_sb`, persistent dentries/inodes in the pseudo-filesystem, inode `i_private` pointers to `fuse_conn`, and live connection counters/limits. Values are not persistent across unmount or connection teardown.

## Dependencies and Integration Points
This file integrates with FUSE connection registration, `simple_fill_super`, `get_tree_single`, `kill_anon_super`, `fuse_abort_conn()`, and global tunables `max_user_bgreq`/`max_user_congthresh`.

## Risks
The singleton superblock and borrowed dentry references require `fuse_mutex` discipline. Limit writes from unprivileged users are clamped by global limits; privileged writes can set up to 65535. Stale control files must clear `i_private` during removal to avoid use-after-free.

## Test Signals
Mount/unmount `fusectl`, create and destroy FUSE mounts while mounted, read counters, adjust limits as privileged and unprivileged users, abort a hung connection, and run lockdep during concurrent connection teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/cuse.c -->
# sources/distributed-fs/ceph-client/fs/fuse/cuse.c

## Purpose
`cuse.c` implements CUSE, a FUSE-based mechanism for userspace character devices. A daemon opens `/dev/cuse`, completes a `CUSE_INIT` handshake, and the kernel creates a character device whose operations are proxied through FUSE requests.

## Important APIs, Types, and Functions
- `struct cuse_conn` embeds a dummy `fuse_mount`, a `fuse_conn`, and the created `cdev`/`device`.
- Frontend ops `cuse_read_iter()`, `cuse_write_iter()`, `cuse_open()`, `cuse_release()`, and ioctl wrappers forward to FUSE direct I/O/open/release/ioctl helpers.
- `cuse_parse_one()` and `cuse_parse_devinfo()` parse NUL-packed init strings such as `DEVNAME=...`.
- `cuse_send_init()` sends the asynchronous `CUSE_INIT` request.
- `cuse_process_init_reply()` validates the daemon reply and creates/registers the chrdev.
- `cuse_channel_open()`/`cuse_channel_release()` own `/dev/cuse` server channel lifetime.

## Control Flow
Opening `/dev/cuse` allocates `cuse_conn`, initializes a FUSE connection using the opener's user namespace, installs a FUSE device, marks the connection initialized, sends `CUSE_INIT` in the background, and stores the device handle in the channel file. When the daemon replies, the callback checks protocol version, records limits and flags, parses `DEVNAME`, reserves a device number, allocates a `struct device` and `struct cdev`, checks name uniqueness under `cuse_lock`, registers both, inserts the connection into a hash table by dev_t, and emits a uevent. Opening the created char device looks up the connection, takes a ref, and calls `fuse_do_open()`. Channel release removes the connection from the table, unregisters device/cdev, and releases the FUSE device.

## State and Persistence
State is in the global `cuse_conntbl`, a global class, per-connection FUSE state, `cdev`, and `struct device`. It persists only while the server channel is open. `unrestricted_ioctl` is negotiated during initialization and affects ioctl forwarding flags.

## Dependencies and Integration Points
CUSE builds on `fuse_dev_operations`, `fuse_direct_io`, `fuse_do_open`, `fuse_sync_release`, `fuse_do_ioctl`, Linux cdev/device/misc subsystems, sysfs attributes, and module init/exit. It deliberately disables `FUSE_DEV_IOC_CLONE` for the CUSE channel.

## Risks
Initialization is asynchronous, so error paths must free folios, init args, device numbers, and partially registered devices. Device-name uniqueness is enforced only within the CUSE table. Channel close is authoritative and can remove the character device while opens race; the lookup/refcount path must handle `-ENODEV`. The server is responsible for write locking and sanity checks for char-device I/O.

## Test Signals
Exercise successful CUSE device creation, malformed init info, missing `DEVNAME`, duplicate names, explicit major/minor conflicts, server death during init, frontend read/write/ioctl/poll, sysfs `waiting`/`abort`, and module unload after devices are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/cuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dax.c -->
# sources/distributed-fs/ceph-client/fs/fuse/dax.c

## Purpose
`dax.c` implements FUSE/virtio-fs DAX mapping management. It maps file offsets to windows in a DAX device, serves read/write/mmap through iomap, and reclaims DAX windows by asking the userspace daemon to set up or remove mappings.

## Important APIs, Types, and Functions
- `struct fuse_dax_mapping` describes one DAX window range, its inode/file interval, writability, and in-use refcount.
- `struct fuse_inode_dax` holds an interval tree and semaphore per inode.
- `struct fuse_conn_dax` holds the DAX device, free/busy mapping lists, reclaim work, and waitqueue.
- `fuse_setup_one_mapping()` sends `FUSE_SETUPMAPPING`.
- `dmap_removemapping_list()`/`dmap_removemapping_one()` send `FUSE_REMOVEMAPPING`.
- `fuse_iomap_begin()`/`fuse_iomap_end()` implement iomap lookup/setup/refcount release.
- `fuse_dax_read_iter()`, `fuse_dax_write_iter()`, and `fuse_dax_mmap()` are data path entry points.
- `fuse_dax_conn_alloc/free()`, `fuse_dax_inode_alloc/init/cleanup()`, `fuse_dax_cancel_work()`, and `fuse_dax_check_alignment()` manage lifecycle.

## Control Flow
Connection allocation enumerates the DAX device size via `dax_direct_access()`, divides it into 2 MiB windows, and seeds a free list of `fuse_dax_mapping` objects. Iomap begin looks for an interval covering the requested file index; if found it fills an iomap and increments the mapping refcount, upgrading read-only mappings to writable by sending `FUSE_SETUPMAPPING` when necessary. If no mapping exists, it allocates a free range or reclaims one inline, sends `FUSE_SETUPMAPPING`, inserts the mapping into the inode interval tree and busy list, then returns an iomap. Iomap end decrements the temporary ref.

Reads and non-extending writes call `dax_iomap_rw()`. Extending writes fall back to FUSE direct I/O so data write and size growth are not split across DAX mapping semantics. Faults call `dax_iomap_fault()` under the mapping invalidate lock; if no free mapping is available in fault context, `-EAGAIN` causes wait/retry. Reclaim selects idle busy ranges, grabs the inode, breaks DAX layouts, writes back and invalidates page cache, removes the interval, sends `FUSE_REMOVEMAPPING`, and returns the range to the free list.

## State and Persistence
Mapping state is in memory only. The userspace daemon maintains the actual mapping behind `FUSE_SETUPMAPPING`/`FUSE_REMOVEMAPPING`; the kernel tracks file-index intervals and DAX window offsets. `S_DAX` and address-space ops are set per inode when connection mode and `FUSE_ATTR_DAX` allow it. Delayed reclaim is scheduled when free ranges drop below a 20 percent threshold.

## Dependencies and Integration Points
The file depends on virtio-fs DAX negotiation, `linux/dax.h`, iomap, interval trees, page-cache invalidation, inode eviction, FUSE request helpers, and daemon support for setup/removal opcodes. It is selected by `CONFIG_FUSE_DAX`.

## Risks
Lock ordering is delicate: reclaim takes mapping invalidate lock and inode DAX semaphore to serialize against faults/read/write, while fault context cannot do inline reclaim. Refcounts must prevent reclaim of mappings in active iomap use. Failed `FUSE_REMOVEMAPPING` is tolerated on disconnected connections but otherwise warns. Extending writes intentionally bypass DAX; missing this fallback can expose non-atomic size/data updates. Alignment negotiation must reject daemon map alignments larger than the fixed 2 MiB range size.

## Test Signals
Test DAX read/write/mmap faults, write upgrades, extending writes fallback, truncate/evict cleanup, mapping exhaustion and reclaim, memory pressure, daemon disconnect during removemapping, alignment negotiation, inode-mode toggling of `FUSE_ATTR_DAX`, and lockdep with concurrent mmap faults and reclaim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dev.c -->
# sources/distributed-fs/ceph-client/fs/fuse/dev.c

## Purpose
`dev.c` implements the classic `/dev/fuse` transport and much of the common FUSE request lifecycle. It allocates requests, queues foreground/background work, copies requests and replies between kernel and daemon via read/write/splice, handles notifications, aborts connections, exposes device ioctls, and registers the FUSE misc device.

## Important APIs, Types, and Functions
- Request lifecycle: `fuse_get_req()`, `fuse_put_request()`, `fuse_send_one()`, `fuse_request_end()`, `__fuse_simple_request()`, and `fuse_simple_background()`.
- Queue ops: `fuse_dev_queue_forget()`, `fuse_dev_queue_interrupt()`, `fuse_dev_queue_req()`, and exported `fuse_dev_fiq_ops`.
- Copy helpers: `fuse_copy_init/finish()`, `fuse_copy_args()`, `fuse_copy_out_args()`, folio and splice helpers.
- Device paths: `fuse_dev_do_read()`, `fuse_dev_do_write()`, `fuse_dev_read/write()`, `splice_read/write()`, `poll()`, `fasync()`, and `release()`.
- Notifications: poll, inode/entry invalidation, delete, store, retrieve, resend, epoch increment, and prune.
- Teardown: `fuse_abort_conn()`, `fuse_wait_aborted()`, `fuse_dev_end_requests()`.
- Ioctls: clone, passthrough backing open/close, and sync init.

## Control Flow
Kernel FUSE operations allocate a `fuse_req`, fill credentials and headers, adjust for protocol compatibility, and queue through `fuse_iqueue_ops`. Foreground requests wait in `request_wait_answer()`, optionally sending `FUSE_INTERRUPT` on signal and removing pending requests on fatal signals when possible. Background requests are throttled by `max_background`, `num_background`, `active_background`, and `bg_queue`.

The daemon reads `/dev/fuse`; `fuse_dev_do_read()` waits for pending interrupts, forgets, or requests, copies headers and input args to userspace, then moves reply-expected requests into the per-device processing hash with `FR_SENT`. The daemon writes replies; `fuse_dev_do_write()` validates `fuse_out_header`, dispatches unsolicited notifications when `unique == 0`, finds processing requests by unique id, copies output args/pages, and ends the request. Splice paths use the same copy state but move through pipe buffers, including optional folio replacement.

Abort clears connection state, cancels timeout work, drains per-device IO/processing queues, pending queues, forget lists, background queues, and polls, wakes waiters, and delegates io_uring abort outside `fc->lock`. Releasing the last device aborts the connection.

## State and Persistence
State is in `fuse_conn`, `fuse_iqueue`, `fuse_pqueue`, `fuse_dev`, `fuse_req`, background counters, request flags, unique IDs, and the `fuse_request` kmem cache. No data is persisted directly here; the userspace daemon owns filesystem persistence. Page-cache mutations can occur through notify store/retrieve and reply page copying.

## Dependencies and Integration Points
This file integrates with the FUSE inode/file/dir layers, FUSE protocol headers, tracepoints, misc device registration, waitqueues, fasync, pipe/splice, page cache, io_uring transport hooks, passthrough backing-file management, and `fusectl` abort/limit controls.

## Risks
The risk surface is broad: request flag transitions must be atomic and ordered; copying must not fault while a request is locked; abort races with read/write/splice must not leak or double-end requests; background throttling must wake waiters correctly; notify handlers must validate sizes and names from userspace; resend is only safe for idempotent or duplicate-aware daemons. Timeout scanning checks list heads and can miss transient reordered cases, but should eventually catch stuck requests. Passthrough ioctls are feature-gated but share the same device interface.

## Test Signals
Signals include libfuse mount smoke tests, foreground and background operations, signal interruption, interrupt replies, large read buffers, SETXATTR too-large behavior, splice read/write, notify invalidation/store/retrieve/delete/resend/prune, abort from fusectl, daemon death, cloned devices, passthrough ioctls, io_uring-enabled fallback, timeout-induced abort, kmemleak/refcount checks, and lockdep under concurrent teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dev_uring.c -->
# sources/distributed-fs/ceph-client/fs/fuse/dev_uring.c

## Purpose
`dev_uring.c` implements an optional FUSE transport over `IORING_OP_URING_CMD`. It registers per-CPU userspace ring entries, switches the FUSE input queue to io_uring ops when all queues are ready, sends requests into registered header/payload buffers, commits replies, and coordinates abort/teardown.

## Important APIs, Types, and Functions
- `enable_uring` is a module parameter gating new io_uring use.
- `fuse_uring_enabled()` reports module-level enablement.
- Ring setup: `fuse_uring_create()`, `fuse_uring_create_queue()`, `fuse_uring_register()`, and `fuse_uring_do_register()`.
- Request transfer: `fuse_uring_queue_fuse_req()`, `fuse_uring_queue_bq_req()`, `fuse_uring_dispatch_ent()`, `fuse_uring_send_in_task()`, and `fuse_uring_send_next_to_ring()`.
- Reply path: `fuse_uring_commit_fetch()`, `fuse_uring_commit()`, `fuse_uring_copy_from_ring()`, and `fuse_uring_out_header_has_err()`.
- Teardown: `fuse_uring_abort_end_requests()`, `fuse_uring_stop_queues()`, `fuse_uring_entry_teardown()`, `fuse_uring_destruct()`, and cancellation handlers.
- Timeout integration: `fuse_uring_request_expired()`.

## Control Flow
Userspace submits register commands with SQE128 command payloads and two iovecs: one header area and one payload area. Registration creates the shared ring if needed, creates the queue for the requested CPU id, validates buffer sizes, allocates a `fuse_ring_ent`, marks the command cancelable, and puts the entry on the available list. Once every queue has an available entry, the code swaps `fiq->ops` to `fuse_io_uring_ops`, marks the ring ready, and wakes blocked request allocators.

Queued FUSE requests choose a queue based on `task_cpu(current)`, receive a classic FUSE unique id, and either bind to an available entry or wait in the queue's request list. Dispatch happens as io_uring task work so the daemon task context can access the registered user buffers. The send path copies the operation-specific input header to `op_in`, payload pages/args to the payload iovec, metadata to `ring_ent_in_out`, and `fuse_in_header` to `in_out`, then completes the uring command so userspace can process it.

Userspace replies with `FUSE_IO_URING_CMD_COMMIT_AND_FETCH` containing the commit id and queue id. The kernel finds the request in that queue's processing hash, transitions the entry to commit state, copies the out header and payload back into request args, ends the request, and immediately makes the same entry available/fetches the next request. This combined commit-and-fetch is required so queued kernel requests continue to flow.

## State and Persistence
State is in `fc->ring`, `struct fuse_ring`, per-queue lists, per-entry states (`FRRS_*`), queue background counters, per-queue processing hash, request `FR_URING` flags, and request backpointers to queues/entries. There is no persistent storage. Ring entries are moved to a released list instead of freed immediately to tolerate io_uring cancel races.

## Dependencies and Integration Points
This file depends on FUSE core request helpers in `dev.c`, `dev_uring_i.h`, FUSE UAPI io_uring structures in `include/uapi/linux/fuse.h`, `io_uring/cmd.h`, task-work completion, FUSE timeout scans, background request throttling, and classic FUSE ops for forget and interrupt requests. `fs/fuse/inode.c` negotiates `fc->io_uring`.

## Risks
The transport is concurrency-heavy. Queue readiness requires at least one registered entry per possible CPU, so CPU hotplug or missing queue registration can leave request allocation blocked while `fc->io_uring` is set. Entry state transitions must match list membership or teardown may leak entries. `IO_URING_F_CANCEL` can access entries directly, so released entries are intentionally retained until connection destruction. Notifications and interrupt replies are not fully supported through io_uring and fall back or reject. Background accounting is split between global `fc` counters and per-queue counters and must remain balanced on errors and abort. Unique mismatch or invalid out headers must end requests with errors without corrupting queues.

## Test Signals
Exercise register on all queues, invalid iovec/header/payload sizes, disabled module parameter, command without SQE128, commit/fetch success, wrong commit id, unique mismatch, daemon cancel/death, abort with in-userspace entries, background request flow, timeout detection, fallback forget/interrupt behavior, and lockdep/KASAN under concurrent request dispatch and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dev_uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dev_uring_i.h -->
# sources/distributed-fs/ceph-client/fs/fuse/dev_uring_i.h

## Purpose
`dev_uring_i.h` defines the private data structures and inline integration points for the optional FUSE io_uring transport.

## Important APIs, Types, and Functions
- `enum fuse_ring_req_state` enumerates entry lifecycle states from invalid through commit, available, assigned request, userspace, teardown, and released.
- `struct fuse_ring_ent` binds userspace header/payload buffers, a queue, an `io_uring_cmd`, list node, state, and assigned `fuse_req`.
- `struct fuse_ring_queue` owns per-CPU entry lists, request queues, background queues, a processing hash, active background count, lock, and stopped flag.
- `struct fuse_ring` owns the connection pointer, queue array, max payload size, stop waitqueue, async teardown work, queue refcount, and readiness.
- Prototypes connect `dev_uring.c` to FUSE core.
- Inline stubs preserve buildability when `CONFIG_FUSE_IO_URING` is disabled.

## Control Flow
When enabled, core FUSE code calls the declared helpers for readiness checks, request queueing, pending request removal, timeout scans, abort, stop waiting, and destruction. The inline `fuse_uring_abort()` checks for a ring and live queue refs, then ends queued requests and stops queues. `fuse_uring_wait_stopped_queues()` waits for all queue refs to reach zero. When disabled, all helpers become no-op or false-returning stubs.

## State and Persistence
The header defines in-memory state only. Queue refs intentionally outlive active entries until teardown releases all io_uring-visible objects. No state persists beyond connection destruction.

## Dependencies and Integration Points
It depends on `fuse_i.h`, `CONFIG_FUSE_IO_URING`, io_uring command types through the implementation, and FUSE core request fields such as `ring_queue` and `ring_entry`.

## Risks
The header encodes the locking and lifetime model used by `dev_uring.c`; misuse of entry states or queue locks can lead to stale direct pointers from cancel paths. Disabled stubs must match enabled semantics enough that core code can call them unconditionally without behavioral surprises.

## Test Signals
Compile both enabled and disabled configs, confirm abort/wait paths do not hang with no ring, and validate that queue refs reach zero after daemon cancellation or connection abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/fuse/dev_uring_i.h -->
