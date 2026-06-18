# Group Research: group_755_linux_sources_os_linux_linux_fs_fs_dirent_c_sources_os_linux_linux_f_225f2782323e

Scope: `Docs/research_subset_a.md`, specifically `sources/os/linux/linux`.

This grouped report covers small-to-large Linux VFS and FUSE sources. I read every listed file completely and verified the listed line counts with `wc -l` (8,606 total lines).

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fs_dirent.c -->
# File Research: sources/os/linux/linux/fs/fs_dirent.c

## Purpose
This file provides small exported helpers for converting between Linux generic file-mode bits, filesystem on-disk file type values (`FT_*`), and userspace directory entry type values (`DT_*`). It centralizes mappings that many filesystem drivers need when filling directory entries or storing lightweight inode type metadata.

## Main Definitions
- `fs_dtype_by_ftype[FT_MAX]` maps on-disk `FT_*` constants to `DT_*` constants.
- `fs_ftype_by_dtype[DT_MAX]` maps `DT_*` directory entry type values back to `FT_*`; uninitialized entries default to `FT_UNKNOWN`.
- `fs_ftype_to_dtype(unsigned int filetype)` returns `DT_UNKNOWN` when the supplied filetype is out of range.
- `fs_umode_to_ftype(umode_t mode)` converts `S_DT(mode)` into an on-disk `FT_*` type.
- `fs_umode_to_dtype(umode_t mode)` composes the previous two helpers.

## Control Flow And Behavior
The implementation is table-driven and intentionally has no allocation or locking. Invalid on-disk file type numbers are clamped to `DT_UNKNOWN`, while invalid/unrecognized mode-derived directory types fall through the zero-initialized `fs_ftype_by_dtype` table as `FT_UNKNOWN`.

## Dependencies And Interfaces
The file depends on `<linux/fs_dirent.h>` for type constants and `S_DT()`, and exports all three helpers with `EXPORT_SYMBOL_GPL`. The consumers are expected to be filesystem implementations that need consistent directory entry type conversions.

## Concurrency And Safety
The tables are static constant data and are safe in any context. The kernel-doc comments explicitly state “Any context” for all helpers.

## Research Notes
This is foundational glue rather than policy code. Its main correctness property is that unsupported or impossible values degrade to unknown type instead of fabricating a specific type.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fs_dirent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fs_parser.c -->
# File Research: sources/os/linux/linux/fs/fs_parser.c

## Purpose
This file implements generic filesystem mount/reconfiguration parameter parsing for the modern `fs_context` mount API. Filesystems describe supported parameters with `struct fs_parameter_spec`; this parser matches keys, handles `no`-prefixed negation for flags, converts string values into typed parse results, and reports errors through the filesystem context log.

## Main Definitions
- `bool_names[]` accepts `0`, `1`, `false`, `no`, `true`, and `yes`.
- `lookup_constant()` and `__lookup_constant()` search simple name/value tables.
- `fs_lookup_key()` matches `struct fs_parameter` keys against a parameter description table and handles `fs_param_neg_with_no`.
- `__fs_parse()` is the central parser: match key, warn for deprecated parameters, convert values, and return the option id.
- `fs_lookup_param()` turns a string or filename parameter into a resolved `struct path`, with optional block-device validation.
- Type validators include `fs_param_is_bool`, `fs_param_is_u32`, `fs_param_is_s32`, `fs_param_is_u64`, `fs_param_is_enum`, `fs_param_is_string`, `fs_param_is_fd`, `fs_param_is_file_or_string`, `fs_param_is_uid`, `fs_param_is_gid`, and `fs_param_is_blockdev`.
- Under `CONFIG_VALIDATE_FS_PARSER`, `fs_validate_description()` detects duplicate parameter names of the same flag/non-flag kind.

## Control Flow And Behavior
`__fs_parse()` zeroes `result->uint_64`, finds a matching spec, emits a deprecation warning when needed, and then either handles a flag directly or calls the spec’s type conversion callback. Unknown keys return `-ENOPARAM`; mismatched or invalid values usually return `-EINVAL` through the `inval_plog()` logging path.

`fs_lookup_key()` distinguishes flags from value parameters, so the same name can exist once as a flag and once as a valued parameter. For flag input, it also recognizes `nofoo` as a negated form of `foo` only when the spec opted into `fs_param_neg_with_no`.

`fs_lookup_param()` accepts either `fs_value_is_string` or `fs_value_is_filename`. Strings are wrapped with `getname_kernel()` and looked up from `AT_FDCWD`; filename parameters preserve their provided `dirfd`. If `want_bdev` is true, the resolved path must be a block device or the function returns `-ENOTBLK`.

## Dependencies And Interfaces
This file is used by filesystem `fs_context` implementations and exported parser helpers. It depends on `fs_context`, `fs_parser`, name lookup, security/user namespace conversion, and internal VFS logging helpers.

## Concurrency And Safety
The parser itself is synchronous and does not keep global mutable state. Path lookup and user namespace ID conversion rely on standard VFS and namespace helpers. Empty values are rejected unless the spec has `fs_param_can_be_empty`.

## Research Notes
This is shared mount API infrastructure. Important semantic details are: flag negation is opt-in, unknown parameter behavior is controlled by higher-level description policy, UID/GID parsing validates against `current_user_ns()`, and fd parameters reject values larger than `INT_MAX`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fs_parser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fs_pin.c -->
# File Research: sources/os/linux/linux/fs/fs_pin.c

## Purpose
This file implements `fs_pin` list management and teardown. Pins are linked both to a mount and to a superblock/group list so that unmount and group shutdown paths can find and kill outstanding filesystem pins.

## Main Definitions
- Global `pin_lock` protects insertion/removal from the mount and superblock hlist nodes.
- `pin_insert()` links a pin into `m->mnt_sb->s_pins` and `real_mount(m)->mnt_pins`.
- `pin_remove()` unlinks the pin from both lists, marks it done, and wakes waiters.
- `pin_kill()` coordinates first-killer execution of `p->kill(p)` with concurrent waiters.
- `mnt_pin_kill()` repeatedly kills pins linked from one `struct mount`.
- `group_pin_kill()` repeatedly kills pins linked from a superblock/group hlist.

## Control Flow And Behavior
`pin_kill()` is designed to be called while holding RCU read lock around list lookup. If the pin pointer is null, it simply drops RCU. If `done` is zero, the caller transitions it to `-1`, drops locks/RCU, and invokes the pin’s `kill` callback. If another caller is already killing the pin (`done < 0`), the function waits on the pin waitqueue until `pin_remove()` marks completion with `done > 0`.

`mnt_pin_kill()` and `group_pin_kill()` loop until the corresponding hlist head is empty. Each iteration uses `READ_ONCE()` under RCU to fetch the first node and delegates the synchronization protocol to `pin_kill()`.

## Dependencies And Interfaces
The file depends on internal mount structures (`mount.h`) and `struct fs_pin` definitions from VFS internals. It is not exporting symbols here; it is internal VFS lifecycle code.

## Concurrency And Safety
The implementation combines a global spinlock for list structure mutations, per-pin waitqueue locking for state transitions, and RCU for safe lookup while teardown races with removal. The `done` field encodes active kill (`-1`) and completion (`1`).

## Research Notes
The key invariant is single execution of a pin’s `kill` callback while allowing arbitrary concurrent unmount/group teardown callers to converge by waiting for `pin_remove()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fs_pin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fs_struct.c -->
# File Research: sources/os/linux/linux/fs/fs_struct.c

## Purpose
This file manages `struct fs_struct`, the per-task or shared process filesystem context containing root, current working directory, umask, and reference count. It handles setting root/pwd, chroot reference rewrites, copy/unshare, exit, and init state.

## Main Definitions
- `set_fs_root()` replaces `fs->root` with a referenced new path and drops the old path afterward.
- `set_fs_pwd()` does the same for `fs->pwd`.
- `replace_path()` updates a path if it exactly matches an old path.
- `chroot_fs_refs()` walks all processes/threads and rewrites matching `root` and `pwd` references from `old_root` to `new_root`.
- `free_fs_struct()` drops root and pwd paths and frees from `fs_cachep`.
- `exit_fs()` detaches the task from its fs context and frees it when the user count reaches zero.
- `copy_fs_struct()` allocates a private copy of an existing fs context.
- `unshare_fs_struct()` installs a copied fs context for `current`.
- `init_fs` provides the boot/init task filesystem context with default umask `0022`.

## Control Flow And Behavior
Root and pwd updates take a reference on the new path first, update under the fs seqlock, then release the old path after dropping the lock. Copying allocates from `fs_cachep`, initializes a new seqlock and metadata, then snapshots root and pwd under the old fs seqlock.

`chroot_fs_refs()` traverses the full task list under `tasklist_lock`, locks each task, and replaces `root` and `pwd` references that still point to `old_root`. It increments `new_root` once per replacement and later drops `old_root` the same number of times.

## Dependencies And Interfaces
The file uses scheduler task traversal, task locks, seqlocks, path reference helpers, and the global `fs_cachep`. `unshare_fs_struct()` is exported GPL for other kernel code.

## Concurrency And Safety
`fs_struct` fields are protected by `fs->seq`; task ownership is protected by `task_lock()`. The code carefully avoids dropping path references while holding the seqlock because `path_put()` can block.

## Research Notes
This file is central to namespace-like behavior at the task level. Its most important lifetime rule is that path references are acquired before publishing and released after unpublishing, preserving stable root/pwd paths for concurrent readers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fs_struct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fserror.c -->
# File Research: sources/os/linux/linux/fs/fserror.c

## Purpose
This file implements asynchronous filesystem error reporting from superblocks to filesystem-specific callbacks and to fsnotify/userspace. It allows errors discovered in contexts that may not sleep to be queued to process context while preserving inode references until reporting completes.

## Main Definitions
- `FSERROR_DEFAULT_EVENT_POOL_SIZE` sets the mempool baseline to 32 events.
- Global `fserror_events_pool` backs allocations for `struct fserror_event`.
- `fserror_mount()` initializes `sb->s_pending_errors` with a bias of one.
- `fserror_unmount()` drops the bias and waits for pending queued events to drain.
- `fserror_worker()` invokes optional `sb->s_op->report_error(event)` and emits an `FS_ERROR` fsnotify event.
- `fserror_report()` is the public reporting API and is exported GPL.
- `fserror_init()` initializes the mempool at `fs_initcall` time.

## Control Flow And Behavior
`fserror_report()` validates that `inode->i_sb` matches `sb` and that `error` is negative, allocates an event while incrementing `s_pending_errors`, fills event details, grabs an inode reference with `igrab()` when present, and schedules work. The worker converts the stored negative errno to a positive userspace error code for `fs_error_report`, calls filesystem-specific reporting if provided, sends an fsnotify event, drops the inode, and decrements the pending counter.

If allocation or inode grabbing fails, the code drops any pending reference and logs a rate-limited lost-report message.

## Dependencies And Interfaces
This file uses superblock fields, inode references, workqueues, mempools, fsnotify, and the `struct fserror_event` / `struct fs_error_report` API from `<linux/fserror.h>`.

## Concurrency And Safety
`s_pending_errors` is a refcount used as an unmount barrier. `refcount_inc_not_zero()` prevents queuing new reports after shutdown begins. The worker only reports while `SB_ACTIVE` is still set. Barriers are provided by refcount operations, as noted in the source comments.

## Research Notes
The design assumes filesystem errors are rare and favors process-context safety over immediate delivery. The unmount path blocks until queued reports drain, which prevents event memory and inode references from outliving the superblock teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fserror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fsopen.c -->
# File Research: sources/os/linux/linux/fs/fsopen.c

## Purpose
This file implements the fd-based mount API system calls `fsopen`, `fspick`, and `fsconfig`. It exposes filesystem contexts as anonymous-inode file descriptors, lets userspace read context log messages, set parameters, create mount trees, and reconfigure existing superblocks.

## Main Definitions
- `fscontext_fops` provides `.read` for log retrieval and `.release` for `put_fs_context()`.
- `fscontext_create_fd()` wraps an `fs_context` in an anonymous inode fd.
- `fscontext_alloc_log()` allocates the per-context log buffer.
- `SYSCALL_DEFINE2(fsopen)` opens a filesystem type for new mount configuration.
- `SYSCALL_DEFINE3(fspick)` selects an existing mount root for reconfiguration.
- `vfs_cmd_create()` transitions a creation context through tree creation and security checks.
- `vfs_cmd_reconfigure()` applies reconfiguration to an existing superblock.
- `SYSCALL_DEFINE5(fsconfig)` validates and imports one parameter/action from userspace.

## Control Flow And Behavior
`fsopen()` requires `may_mount()`, accepts only `FSOPEN_CLOEXEC`, resolves the filesystem type by name, creates a mount `fs_context`, moves it to `FS_CONTEXT_CREATE_PARAMS`, allocates logging, and returns an fd.

`fspick()` requires `may_mount()`, resolves a path with flags controlling symlink follow, automount, and empty path behavior, requires that the selected dentry is the mount root, creates a reconfiguration context, moves it to `FS_CONTEXT_RECONF_PARAMS`, allocates logging, and returns an fd.

`fsconfig()` validates the command-specific shape of `_key`, `_value`, and `aux`; imports strings, binary blobs, filenames, paths, or fds into a `struct fs_parameter`; locks `fc->uapi_mutex`; then calls `vfs_fsconfig_locked()`. Create/reconfigure commands drive phase transitions; ordinary set commands call `vfs_parse_fs_param()`. Imported values are cleaned up unless stolen by filesystem or LSM code.

## Dependencies And Interfaces
This file depends on `fs_context`, `fs_parser`, mount internals, anonymous inodes, name lookup, fd helpers, security hooks, and UAPI mount command constants.

## Concurrency And Safety
`fc->uapi_mutex` serializes userspace API operations against one context and protects log reads. Phase checks prevent reusing a context after creation/reconfiguration has progressed. `vfs_cmd_create()` releases `s_umount` after `vfs_get_tree()` succeeds because lower call chains acquired it.

## Research Notes
The file is the userspace entry point for the modern mount API. Important constraints include 256-byte limits for keys/strings, a 1 MiB binary parameter cap, exclusive phase states, and fd type checking against `fscontext_fops`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fsopen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/Kconfig -->
# File Research: sources/os/linux/linux/fs/fuse/Kconfig

## Purpose
This Kconfig file declares the build-time configuration options for FUSE, CUSE, virtiofs, virtiofs DAX, FUSE passthrough, and FUSE io_uring communication.

## Main Definitions
- `FUSE_FS`: tristate base support for Filesystem in Userspace; selects `FS_POSIX_ACL` and `FS_IOMAP`.
- `CUSE`: tristate Character device in Userspace support; depends on `FUSE_FS`.
- `VIRTIO_FS`: tristate virtio filesystem support; depends on `FUSE_FS` and selects `VIRTIO`.
- `FUSE_DAX`: bool virtiofs direct host memory access; default `y`; depends on `VIRTIO_FS`, `FS_DAX`, and `DAX`; selects `INTERVAL_TREE`.
- `FUSE_PASSTHROUGH`: bool passthrough operations; default `y`; depends on `FUSE_FS`; selects `FS_STACK`.
- `FUSE_IO_URING`: bool FUSE communication over io_uring; default `y`; depends on `FUSE_FS` and `IO_URING`.

## Behavior And Build Impact
The base `FUSE_FS` option enables the core userspace filesystem stack. CUSE and virtiofs are optional frontends/extensions. DAX, passthrough, and io_uring each conditionally include specialized implementation files through the Makefile.

## Dependencies And Interfaces
This file establishes compile-time feature gates used by `fs/fuse/Makefile` and by `#ifdef CONFIG_FUSE_*` sections in source files such as `dev.c`, `dax.c`, `backing.c`, and `dev_uring.c`.

## Research Notes
The default-enabled bool options mean that when their dependencies are present, DAX, passthrough, and io_uring support are included unless disabled by the kernel configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/Makefile -->
# File Research: sources/os/linux/linux/fs/fuse/Makefile

## Purpose
This Makefile describes how the FUSE-related kernel objects are built and linked.

## Main Definitions
- Adds `-I$(src)` to `ccflags-y` for trace event include resolution.
- Builds `fuse.o` when `CONFIG_FUSE_FS` is enabled.
- Builds `cuse.o` when `CONFIG_CUSE` is enabled.
- Builds `virtiofs.o` when `CONFIG_VIRTIO_FS` is enabled.
- Places `trace.o` first in `fuse-y` so ftrace-related errors surface early.
- Core `fuse-y` includes `dev.o`, `dir.o`, `file.o`, `inode.o`, `control.o`, `xattr.o`, `acl.o`, `readdir.o`, `ioctl.o`, and `iomode.o`.
- Conditional objects include `dax.o`, `passthrough.o`, `backing.o`, `sysctl.o`, and `dev_uring.o`.
- `virtiofs-y` maps to `virtio_fs.o`.

## Research Notes
The build layout mirrors the Kconfig feature boundaries. The files in this batch cover several core and conditional objects: `dev.o`, `control.o`, `acl.o`, `backing.o`, `dax.o`, `dev_uring.o`, and `cuse.o`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/acl.c -->
# File Research: sources/os/linux/linux/fs/fuse/acl.c

## Purpose
This file implements POSIX ACL get/set support for FUSE in terms of extended attributes. It preserves compatibility with older FUSE daemons that handled ACL xattrs themselves without advertising `FUSE_POSIX_ACL`.

## Main Definitions
- `__fuse_get_acl()` fetches `system.posix_acl_access` or `system.posix_acl_default` with `fuse_getxattr()` and converts it with `posix_acl_from_xattr()`.
- `fuse_no_acl()` decides whether kernel POSIX ACL interaction should be refused for non-host user namespaces when the daemon lacks POSIX ACL support.
- `fuse_get_acl()` is the dentry-based VFS ACL getter.
- `fuse_get_inode_acl()` is an inode ACL getter used for permission checking, with RCU lookup handling.
- `fuse_set_acl()` serializes ACLs with `posix_acl_to_xattr()`, writes/removes xattrs, optionally requests setgid stripping, and invalidates ACL/attribute caches.

## Control Flow And Behavior
ACL get operations reject RCU mode with `-ECHILD`, reject bad inodes with `-EIO`, return `NULL` when xattr support is absent or the ACL xattr is absent, translate `-ERANGE` to `-E2BIG`, and otherwise propagate errors. ACL type selects the xattr name; unsupported types return `-EOPNOTSUPP`.

`fuse_set_acl()` rejects bad inodes, unsupported setxattr paths, and unsupported ACL types. For non-null ACLs it converts the ACL into xattr bytes, enforces `PAGE_SIZE` maximum, and may set `FUSE_SETXATTR_ACL_KILL_SGID` when the daemon supports POSIX ACLs and the caller lacks group/capability rights. Null ACL removes the xattr.

## Dependencies And Interfaces
The file uses `fuse_getxattr`, `fuse_setxattr`, `fuse_removexattr`, `forget_all_cached_acls`, and `fuse_invalidate_attr` from the FUSE/VFS xattr and cache layers. It also uses user namespace ACL conversion through `fc->user_ns`.

## Concurrency And Safety
The code does per-call allocation and does not manage global state. It respects RCU lookup constraints by returning `-ECHILD` when ACL lookup cannot sleep.

## Research Notes
The compatibility behavior is central: daemons without `FUSE_POSIX_ACL` retain old behavior, especially around VFS permission checking, ACL caching, and setgid stripping.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/backing.c -->
# File Research: sources/os/linux/linux/fs/fuse/backing.c

## Purpose
This file implements management of backing files for FUSE passthrough operations. It lets a privileged FUSE daemon register regular backing files, receive an integer backing id, look them up later, and close them.

## Main Definitions
- `fuse_backing_get()` safely increments a backing object refcount if nonzero.
- `fuse_backing_put()` frees the backing object when the refcount reaches zero.
- `fuse_backing_files_init()` initializes `fc->backing_files_map` as an IDR.
- `fuse_backing_id_alloc()` allocates cyclic ids starting at 1 under `fc->lock`.
- `fuse_backing_files_free()` destroys all registered backing files at connection teardown.
- `fuse_backing_open()` validates and registers a backing fd.
- `fuse_backing_close()` unregisters a backing id.
- `fuse_backing_lookup()` finds a backing object under RCU and returns a referenced pointer.

## Control Flow And Behavior
`fuse_backing_open()` requires passthrough support to be enabled on the connection and `CAP_SYS_ADMIN`. It rejects nonzero flags/padding, invalid fds, directories, non-regular files, and backing stack depth greater than or equal to `fc->max_stack_depth`. On success it stores the raw file pointer, prepares credentials, initializes the refcount, and inserts into the IDR.

`fuse_backing_close()` has the same capability/passthrough gate, rejects nonpositive ids, removes the object from the IDR, and drops the reference.

## Dependencies And Interfaces
The file depends on FUSE connection fields, Linux file references (`fget_raw`, `fput`), credentials (`prepare_creds`, `put_cred`), IDR, RCU, and stack-depth validation.

## Concurrency And Safety
The IDR map is protected by `fc->lock` for insert/remove. Lookup runs under RCU and uses `refcount_inc_not_zero()` to avoid resurrecting freed objects. Freeing uses `kfree_rcu()`.

## Research Notes
The TODO comments show security/observability concerns: `CAP_SYS_ADMIN` is required until backing files are visible to tools such as `lsof`, and an xarray may be reconsidered for space efficiency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/backing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/control.c -->
# File Research: sources/os/linux/linux/fs/fuse/control.c

## Purpose
This file implements the `fusectl` control filesystem. It exposes per-FUSE-connection control and status files under a single in-kernel pseudo filesystem, including abort, waiting request count, and background request throttling knobs.

## Main Definitions
- `fuse_control_sb` tracks the single mounted control superblock, protected by `fuse_mutex`.
- `fuse_ctl_file_conn_get()` obtains a referenced `fuse_conn` from a control file inode.
- Control file operations:
  - `abort`: write-only, aborts the connection.
  - `waiting`: read-only, reports `fc->num_waiting`.
  - `max_background`: read/write, controls `fc->max_background`.
  - `congestion_threshold`: read/write, controls `fc->congestion_threshold`.
- `fuse_ctl_add_dentry()` creates persistent dentries/inodes under the control fs.
- `fuse_ctl_add_conn()` creates a per-connection directory and files.
- `fuse_ctl_remove_conn()` removes a connection directory.
- `fuse_ctl_fill_super()` initializes the singleton superblock and populates existing connections.
- `fuse_ctl_fs_type` registers filesystem name `fusectl`.

## Control Flow And Behavior
When `fusectl` is mounted, `simple_fill_super()` creates the root and `fuse_ctl_fill_super()` records the superblock as the singleton. It then iterates `fuse_conn_list` and creates one directory per connection named by `fc->dev`. New connections can be added later through `fuse_ctl_add_conn()`.

Writes to limits parse unsigned values from userspace. Without `CAP_SYS_ADMIN`, requested limits are capped by global user limits (`max_user_bgreq` and `max_user_congthresh`). Updating `max_background` also updates `fc->blocked` and wakes blocked waiters when the connection becomes unblocked.

## Dependencies And Interfaces
This file uses simplefs helpers, VFS inode/dentry APIs, FUSE global connection lists, and module filesystem registration. It is wired into the FUSE module init/exit path through `fuse_ctl_init()` and `fuse_ctl_cleanup()`.

## Concurrency And Safety
`fuse_mutex` protects the singleton superblock and connection pointer lookup/removal. `fc->bg_lock` protects background throttling fields. `READ_ONCE`/`WRITE_ONCE` are used for limit reads/writes where appropriate.

## Research Notes
Each control inode stores `fc` in `i_private`; removal clears this pointer so later file operations can return as if the connection disappeared. The returned dentries from creation are borrowed references valid while `fuse_mutex` is held.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/control.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/cuse.c -->
# File Research: sources/os/linux/linux/fs/fuse/cuse.c

## Purpose
This file implements CUSE, Character device in Userspace. It lets a userspace daemon open `/dev/cuse`, complete a FUSE-like initialization handshake, and register a real character device whose file operations are forwarded to the daemon via the FUSE request machinery.

## Main Definitions
- `struct cuse_conn` embeds a dummy `fuse_mount`, a `fuse_conn`, and the registered `cdev`/`device`.
- `cuse_conntbl[64]` maps character device numbers to active CUSE connections under `cuse_lock`.
- Frontend file ops (`cuse_frontend_fops`) implement read, write, open, release, ioctl, compat ioctl, poll, and no-op llseek.
- `cuse_parse_one()` and `cuse_parse_devinfo()` parse packed init reply key/value data, currently requiring `DEVNAME`.
- `cuse_process_init_reply()` validates daemon init response, parses device info, reserves device number, creates the device, creates and registers the cdev, links the connection, and sends uevents.
- `cuse_channel_open()` creates a new CUSE connection when `/dev/cuse` is opened.
- `cuse_channel_release()` removes the connection and registered device when the daemon channel closes.
- Sysfs attributes `waiting` and `abort` expose status/control per CUSE device.

## Control Flow And Behavior
The daemon opens `/dev/cuse`, which allocates `cuse_conn`, initializes its embedded FUSE connection, installs a FUSE device, marks it initialized, and sends an asynchronous `CUSE_INIT` request. The daemon replies with kernel ABI version, max read/write sizes, flags, device numbers, and packed device info. The reply handler registers the actual character device and makes it visible only after all registration is complete.

Opening the created character device looks up the connection by `dev_t`, takes a FUSE connection reference, and delegates open to `fuse_do_open()`. Reads and writes use `fuse_direct_io()` in CUSE mode, with writes intentionally leaving locking and checks to the server. Ioctls route to `fuse_do_ioctl()` and include unrestricted/compat flags as negotiated.

## Dependencies And Interfaces
CUSE depends on the FUSE core device path, miscdevice registration, char device APIs, device model/class APIs, sysfs attributes, and user namespace-aware FUSE connection initialization.

## Concurrency And Safety
`cuse_lock` protects registration, lookup, uniqueness checks, and removal from the connection table. The open path takes a FUSE connection reference so the connection remains alive while the character-device fd is active. Channel close removes the table entry first to stop new opens before unregistering device objects.

## Research Notes
CUSE is structurally a FUSE transport plus a char-device façade. Lifetime is daemon-channel driven: closing `/dev/cuse` removes the device and initiates FUSE device release.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/cuse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/dax.c -->
# File Research: sources/os/linux/linux/fs/fuse/dax.c

## Purpose
This file implements FUSE/virtiofs DAX direct host memory access. It maps file offsets into a shared DAX window using daemon-mediated `FUSE_SETUPMAPPING` and `FUSE_REMOVEMAPPING` requests, integrates with iomap/DAX read-write and mmap fault paths, and reclaims limited DAX window ranges.

## Main Definitions
- `FUSE_DAX_SHIFT` is 21, giving `FUSE_DAX_SZ` 2 MiB mapping ranges.
- `struct fuse_dax_mapping` describes one DAX window range mapped to an inode/file-offset interval.
- `struct fuse_inode_dax` stores each inode’s interval tree and lock.
- `struct fuse_conn_dax` stores the DAX device, global free/busy range lists, reclaim work, waitqueue, and counters.
- Mapping setup/removal functions include `fuse_setup_one_mapping()`, `fuse_send_removemapping()`, `dmap_removemapping_list()`, and `dmap_removemapping_one()`.
- Iomap operations are `fuse_iomap_begin()` and `fuse_iomap_end()`.
- Public I/O hooks include `fuse_dax_read_iter()`, `fuse_dax_write_iter()`, `fuse_dax_mmap()`, `fuse_dax_inode_init()`, `fuse_dax_inode_cleanup()`, and `fuse_dax_cancel_work()`.

## Control Flow And Behavior
The DAX connection initialization queries the DAX device size with `dax_direct_access()`, divides it into 2 MiB ranges, allocates one `fuse_dax_mapping` per range, and places all ranges on the free list. Per-inode DAX allocation initializes an interval tree guarded by an rwsem.

On iomap begin, the code looks for an existing mapping for the requested file offset. If it exists and write access is needed for a read-only mapping, it upgrades the mapping by sending another setup request. If no mapping exists and the offset is within EOF, it allocates or reclaims a free range, sends `FUSE_SETUPMAPPING`, inserts the mapping in the inode interval tree, adds it to the busy list, and returns an `IOMAP_MAPPED` DAX iomap. Reads beyond EOF return an `IOMAP_HOLE`.

Writes that extend file size avoid DAX iomap writes and instead use FUSE direct I/O so file data and size update do not become non-atomic. Non-extending reads/writes use `dax_iomap_rw()`. mmap faults use `dax_iomap_fault()` under `mapping->invalidate_lock` and retry with waitqueue sleeping when no DAX range is available.

Reclaim can happen inline or from delayed work. It avoids ranges with refcount greater than one, breaks DAX layouts, writes back and invalidates page cache, removes the interval-tree entry, sends `FUSE_REMOVEMAPPING`, and returns the mapping to the free pool. Inode eviction reclaims all mappings without taking normal inode DAX locks because reclaim lock ordering would otherwise trip lock validation.

## Dependencies And Interfaces
The file depends on DAX, iomap, interval trees, FUSE request helpers, address-space invalidation, page-fault accounting, and virtiofs/FUSE DAX negotiation fields. It is built only under `CONFIG_FUSE_DAX`.

## Concurrency And Safety
There are three main synchronization layers: `fcd->lock` for global free/busy lists, per-inode `fi->dax->sem` for interval tree changes and lookup stability, and `mapping->invalidate_lock` for page-cache/fault exclusion during reclaim. Mapping refcounts prevent reclaim while iomap users hold active references.

## Research Notes
The DAX window is a scarce cache of file mappings, not a permanent block mapping. The code is careful around fault-path restrictions: it returns `-EAGAIN` instead of doing inline reclaim when holding locks that reclaim would need to drop.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/dax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/dev.c -->
# File Research: sources/os/linux/linux/fs/fuse/dev.c

## Purpose
This file implements the main `/dev/fuse` kernel/userspace transport. It allocates and queues FUSE requests, copies request/reply payloads between kernel structures and userspace buffers or pipes, handles interrupts, background throttling, notifications, aborts, device cloning, passthrough backing ioctls, and miscdevice registration.

## Main Definitions
- `fuse_req_cachep` caches `struct fuse_req`.
- `fuse_timeout_timer_freq` and `fuse_check_timeout()` implement request timeout detection across pending, background, processing, and io_uring queues.
- Request lifecycle helpers include `fuse_request_init()`, `fuse_request_alloc()`, `fuse_get_req()`, `fuse_put_request()`, `fuse_request_end()`, and `request_wait_answer()`.
- Queue helpers include `fuse_dev_queue_forget()`, `fuse_dev_queue_interrupt()`, `fuse_dev_queue_req()`, `flush_bg_queue()`, `fuse_request_queue_background()`, and `fuse_simple_background()`.
- Copy helpers include `fuse_copy_init()`, `fuse_copy_finish()`, `fuse_copy_fill()`, `fuse_copy_do()`, `fuse_copy_folio()`, `fuse_copy_folios()`, `fuse_copy_args()`, and folio splice/move helpers.
- `/dev/fuse` data paths are `fuse_dev_do_read()` and `fuse_dev_do_write()`, wrapped by read/write/splice file ops.
- Notification handlers cover poll wakeups, inode/entry invalidation, delete, store, retrieve, resend, epoch increment, and prune.
- Abort/release/ioctl paths include `fuse_abort_conn()`, `fuse_wait_aborted()`, `fuse_dev_release()`, `FUSE_DEV_IOC_CLONE`, `FUSE_DEV_IOC_BACKING_OPEN`, `FUSE_DEV_IOC_BACKING_CLOSE`, and `FUSE_DEV_IOC_SYNC_INIT`.

## Control Flow And Behavior
Kernel-side filesystem operations allocate `fuse_req` objects through `fuse_get_req()`, which waits for connection initialization, background availability, and io_uring readiness as needed. It assigns pid/uid/gid in the FUSE header, respecting idmapped mount support. Synchronous requests are queued, then wait for a reply; background requests go through a throttled background queue.

`fuse_dev_do_read()` is the daemon’s request-fetch path. It waits for pending work, prioritizes interrupts, interleaves forget requests with normal requests, rejects too-small daemon buffers, moves reply-expected requests to the processing hash table, sets `FR_SENT`, and copies headers/arguments to userspace.

`fuse_dev_do_write()` is the daemon’s reply/notification path. It reads a `fuse_out_header`, dispatches unsolicited notifications when `unique == 0`, validates reply errors, finds the matching request in the processing hash, copies output arguments into the waiting request, and completes it. Interrupt replies have special handling for `ENOSYS` and `EAGAIN`.

The notification subsystem lets daemons invalidate cached inode/entry state, push data into the page cache, retrieve cached data by sending a `FUSE_NOTIFY_REPLY`, request resending of processing requests, increment an epoch to invalidate dentries, and prune specific inode nodeids.

Abort disconnects the connection, stops timeout work, marks processing queues disconnected, completes all pending/processing requests with `-ECONNABORTED`, frees forgets, wakes all waiters/pollers, and then invokes io_uring abort handling outside `fc->lock` to avoid lock-order conflicts.

## Dependencies And Interfaces
This is the central FUSE core file. It depends on FUSE internal headers, tracepoints, miscdevice APIs, poll/fasync, splice and pipe APIs, folio/page-cache APIs, user iov iterators, idmapped mount helpers, passthrough backing support, and optional `CONFIG_FUSE_IO_URING`.

## Concurrency And Safety
Important locks include `fiq->lock` for input pending/interrupt/forget queues, `fpq->lock` for per-device processing queues, `fc->bg_lock` for background throttling, `fc->lock` for connection/device lists, request waitqueue locks for `FR_LOCKED`/`FR_ABORTED`, and `fc->killsb` for reverse notifications that touch inode/dentry state. Memory barriers pair interrupt delivery, initialization visibility, and abort wakeups.

## Research Notes
This file defines the classic FUSE protocol transport semantics. io_uring is integrated by replacing `fiq->ops->send_req` when a ring becomes ready, but forget and interrupt paths still use the classic device queue operations in this implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/dev_uring.c -->
# File Research: sources/os/linux/linux/fs/fuse/dev_uring.c

## Purpose
This file implements an optional io_uring command transport for FUSE requests. Instead of daemon `read(/dev/fuse)` and `write(/dev/fuse)`, userspace registers per-CPU ring entries with header and payload buffers, receives requests through io_uring command completions, and commits replies with `FUSE_IO_URING_CMD_COMMIT_AND_FETCH`.

## Main Definitions
- Module parameter `enable_uring` gates initial use of the transport.
- `struct fuse_uring_pdu` stores the active `fuse_ring_ent` pointer inside an io_uring command PDU.
- `fuse_io_uring_ops` replaces the FUSE input queue `send_req` operation once the ring is ready.
- Ring setup functions: `fuse_uring_create()`, `fuse_uring_create_queue()`, `fuse_uring_register()`, and `fuse_uring_create_ring_ent()`.
- Request/entry state functions: `fuse_uring_ent_avail()`, `fuse_uring_add_req_to_ring_ent()`, `fuse_uring_send_next_to_ring()`, `fuse_uring_commit()`, and `fuse_uring_next_fuse_req()`.
- Teardown functions: `fuse_uring_abort_end_requests()`, `fuse_uring_stop_queues()`, `fuse_uring_entry_teardown()`, and async teardown work.
- Public entry point: `fuse_uring_cmd()`.

## Control Flow And Behavior
Userspace submits `FUSE_IO_URING_CMD_REGISTER` with a 128-byte SQE command containing a queue id and an iovec pair. The kernel creates the global ring and the target per-CPU queue if needed, validates the header/payload buffers, creates a `fuse_ring_ent`, marks the command cancelable, and places the entry on the available queue. When all queues have at least one available entry, the connection’s input queue ops switch to `fuse_io_uring_ops`, `ring->ready` becomes true, and blocked FUSE request allocators wake.

When a kernel request is queued over io_uring, it is assigned to the current task CPU’s queue. If an available entry exists, the request is bound to it and dispatched by completing task work in the ring task context so userspace buffer access permissions are correct. Otherwise the request waits on the queue’s request list. Background requests use a per-queue background list and `fuse_uring_flush_bg()` so each queue can make progress even under global background limits.

For replies, userspace submits `FUSE_IO_URING_CMD_COMMIT_AND_FETCH` with the committed request id. The kernel finds the request in the queue’s processing table, transitions the entry to commit state, copies the output header and payload from userspace buffers, completes the request, then immediately attempts to fetch and dispatch the next request on the same entry.

## Dependencies And Interfaces
The file depends on io_uring command APIs, FUSE request copy helpers from `dev.c`, FUSE processing queues, and the state structures declared in `dev_uring_i.h`. It is built under `CONFIG_FUSE_IO_URING`.

## Concurrency And Safety
Each `fuse_ring_queue` has a spinlock covering entry state transitions and queue lists. The connection lock protects ring creation and queue publication. `ring->queue_refs` tracks live entries through teardown; stopped queues prevent new assignments. Cancellation and teardown avoid immediate freeing of entries because io_uring cancellation can hold direct pointers into entries.

## Research Notes
Notifications and interrupt replies are not fully supported over the io_uring transport in this file; notifications are explicitly rejected in `fuse_uring_out_header_has_err()`, and the ops table keeps forget/interrupt on classic FUSE queue functions. The implementation emphasizes per-core affinity and commit-and-fetch batching to keep requests flowing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/dev_uring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fuse/dev_uring_i.h -->
# File Research: sources/os/linux/linux/fs/fuse/dev_uring_i.h

## Purpose
This internal header declares the FUSE io_uring transport data structures, state enum, public functions, and no-op stubs used when `CONFIG_FUSE_IO_URING` is disabled.

## Main Definitions
- `FUSE_URING_TEARDOWN_TIMEOUT` and `FUSE_URING_TEARDOWN_INTERVAL` control async teardown logging/retry timing.
- `enum fuse_ring_req_state` defines entry states:
  - `FRRS_INVALID`
  - `FRRS_COMMIT`
  - `FRRS_AVAILABLE`
  - `FRRS_FUSE_REQ`
  - `FRRS_USERSPACE`
  - `FRRS_TEARDOWN`
  - `FRRS_RELEASED`
- `struct fuse_ring_ent` stores userspace header/payload pointers, owning queue, io_uring command pointer, list node, state, and bound `fuse_req`.
- `struct fuse_ring_queue` stores queue id, lock, entry lists, pending/background request lists, a processing queue, active background count, and stopped flag.
- `struct fuse_ring` stores the parent `fuse_conn`, queue count, maximum payload size, queue array, stop diagnostics, waitqueue, async teardown work, queue refcount, and readiness flag.

## Interfaces
When enabled, the header declares:
- `fuse_uring_enabled()`
- `fuse_uring_destruct()`
- `fuse_uring_stop_queues()`
- `fuse_uring_abort_end_requests()`
- `fuse_uring_cmd()`
- `fuse_uring_queue_fuse_req()`
- `fuse_uring_queue_bq_req()`
- `fuse_uring_remove_pending_req()`
- `fuse_uring_request_expired()`

It also defines inline helpers:
- `fuse_uring_abort()` aborts requests and stops queues when live queue refs exist.
- `fuse_uring_wait_stopped_queues()` waits for queue refs to reach zero.
- `fuse_uring_ready()` tests connection ring readiness.

When disabled, the same helpers compile to no-ops or `false`, and pending request removal/request expiry return `false`.

## Research Notes
The header makes the rest of FUSE mostly compile-time agnostic to io_uring support. The state enum is the key to understanding `dev_uring.c`: entries transition from available, to assigned request, to userspace, to commit, and eventually back to available or into teardown/released states.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fuse/dev_uring_i.h -->