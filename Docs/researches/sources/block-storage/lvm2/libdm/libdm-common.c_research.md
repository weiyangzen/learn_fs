# File Research: sources/block-storage/lvm2/libdm/libdm-common.c

## Purpose

`libdm-common.c` implements shared libdevmapper runtime support: library initialization, logging hooks, `dm_task` construction and setters, name/UUID mangling, device-node fallback operations, SELinux labeling, mountinfo/sysfs helpers, and udev synchronization cookies. It is the central glue between higher-level device-mapper task building and the local `/dev`, `/sys`, `/proc/self/mountinfo`, and udev environment.

## Main Responsibilities

- Initializes global libdm behavior from environment:
  - `DM_DISABLE_UDEV` disables udev reliance and forces library-managed nodes.
  - `DM_DEFAULT_NAME_MANGLING_MODE` selects `none`, `auto`, or `hex` name mangling.
- Provides default logging and compatibility wrappers between old `dm_log_fn` and newer `dm_log_with_errno_fn`.
- Creates and configures `struct dm_task` objects with default uid/gid/mode/read-ahead/event/cookie fields.
- Converts device names and UUIDs between unmangled strings and udev-safe `\xNN` escaped strings.
- Manages direct fallback `/dev/mapper` node operations:
  - add block node or symlink in alternate dev dirs,
  - remove node,
  - rename node,
  - get/set read-ahead through sysfs or block ioctls.
- Defers node operations in a stack and flushes them through `update_devs()`, allowing udev to complete first when available.
- Reads mountinfo and sysfs to map major/minor to names and detect holders or mounted filesystems.
- Implements udev cookie synchronization with System V semaphores when built with `UDEV_SYNC_SUPPORT`.
- Provides no-op udev-cookie compatibility paths when udev sync support is not compiled in.

## Key State

- `_dm_dir`: device-mapper directory, default `/dev/mapper`.
- `_sysfs_dir`: sysfs root, default `/sys/`.
- `_default_uuid_prefix`: UUID prefix used by libdm/LVM, default `LVM-`.
- `_verbose`: default logger verbosity gate.
- `_suspended_dev_counter`: process-local counter updated on suspend/resume.
- `_name_mangling_mode`: active string mangling policy.
- `_udev_disabled`: set by `DM_DISABLE_UDEV`.
- `_node_ops` and `_count_node_ops`: deferred node-operation queue.
- Under `UDEV_SYNC_SUPPORT`:
  - `_semaphore_supported`,
  - `_udev_running`,
  - `_sync_with_udev`,
  - `_udev_checking`.

## Important Functions

- `dm_lib_init()` reads environment and initializes udev and mangling defaults.
- `dm_log_init()`, `dm_log_with_errno_init()`, `dm_log_init_verbose()`, `dm_log_is_non_default()` manage logging callbacks.
- `dm_task_create()` allocates and initializes a `dm_task`, also checking libdm/kernel compatibility via `dm_check_version()`.
- `mangle_string()` escapes non-whitelisted characters as `\xNN`.
- `unmangle_string()` decodes `\xNN` sequences and optionally enforces strict whitelisted input.
- `check_multiple_mangled_string_allowed()` rejects double-mangled strings in auto mode.
- `_dm_task_set_name()`, `_dm_task_set_name_from_path()`, `dm_task_set_name()` set names, resolving paths back to `/dev/mapper` names for existing devices.
- `dm_task_set_newname()` and `dm_task_set_uuid()` apply validation/mangling before storing task fields.
- `dm_task_add_target()` appends `struct target` entries to a task.
- `dm_prepare_selinux_context()`, `dm_set_selinux_context()`, `selinux_release()` wrap SELinux file context behavior.
- `_add_dev_node()`, `_rm_dev_node()`, `_rename_dev_node()` perform direct node operations.
- `add_dev_node()`, `rm_dev_node()`, `rename_dev_node()`, `set_dev_node_read_ahead()` stack node operations instead of executing immediately.
- `update_devs()` flushes stacked node operations.
- `dm_set_dev_dir()`, `dm_set_sysfs_dir()`, `dm_set_uuid_prefix()` change process-local roots/prefixes.
- `dm_mountinfo_read()` parses `/proc/self/mountinfo` and invokes a callback per mount line.
- `dm_device_get_name()` resolves kernel or DM names from sysfs.
- `dm_device_has_holders()` and `dm_device_has_mounted_fs()` detect active users of a block device.
- `dm_mknodes()` runs the kernel `DM_DEVICE_MKNODES` task.
- `dm_driver_version()` queries the device-mapper driver version.
- `dm_task_set_cookie()`, `dm_udev_create_cookie()`, `dm_udev_complete()`, `dm_udev_wait()`, `dm_udev_wait_immediate()` implement udev synchronization.

## Behavior Details

Name mangling is intentionally conservative for udev integration, not for kernel DM itself. Allowed characters are alphanumeric plus `# + - . : = @ _`; other bytes become `\xNN`. Auto mode preserves already-mangled strings but rejects mixed mangled/unmangled content. Hex mode permits remangling all disallowed characters.

Path-based task names are treated as references to existing devices. `dm_task_set_name()` detects `/` and calls `_dm_task_set_name_from_path()`, which uses `stat()` and `_find_dm_name_of_device()` to translate an arbitrary block-device path back to a mapper name, then stores it without mangling.

Node operations are intentionally queued. The public node helpers push `NODE_ADD`, `NODE_DEL`, `NODE_RENAME`, and `NODE_READ_AHEAD` into `_node_ops`; `_stack_node_op()` coalesces conflicting operations. Deletes remove outstanding add/rename/read-ahead operations for the same device, adds can cancel a pending delete, and renames remove stale operations for the old name. `update_devs()` processes only operations not marked `rely_on_udev`.

Direct device-node creation handles several real-world races:
- Existing correct block node is accepted.
- Existing wrong node is unlinked.
- Dangling symlinks are removed.
- Alternative device directories may use symlinks to real `/dev/dm-N` nodes when cookies are supported.
- SELinux creation context is prepared before `mknod()` or `symlink()`.

Read-ahead prefers sysfs when major/minor are known and falls back to `BLKRAGET`/`BLKRASET`. Sysfs uses KiB while DM read-ahead uses sectors, so conversions multiply or round by two.

Mountinfo parsing unmangles octal escape sequences and contains a btrfs-specific correction path: if mountinfo reports `0:0` but includes `/dev/mapper/...`, it queries DM info for the true major/minor.

Udev synchronization uses a cookie whose high 16 bits must match `DM_COOKIE_MAGIC`. A System V semaphore is created at cookie allocation, incremented when assigned to a task, decremented by completion, waited to zero by `dm_udev_wait()`, then destroyed. If udev sync support is unavailable, cookie APIs degrade to zero-cookie success and `dm_udev_wait()` simply flushes stacked node operations.

## Dependencies and Interactions

- Uses `libdm/misc/dmlib.h` for memory, logging, string, list, and utility helpers.
- Uses `libdm/ioctl/libdm-targets.h` and `libdm/misc/dm-ioctl.h` for task and ioctl structures.
- Uses `libdm-common.h` for shared internal declarations.
- Calls lower-level ioctl/task helpers implemented elsewhere, including `dm_task_run()`, `dm_task_destroy()`, `dm_task_get_info()`, `dm_cookie_supported()`, and `dm_check_version()`.
- Optional SELinux code depends on `HAVE_SELINUX` and `HAVE_SELINUX_LABEL_H`.
- Optional udev sync depends on `UDEV_SYNC_SUPPORT` and `libudev`.

## Notable Edge Cases

- `dm_task_set_newname()` rejects empty names and names containing `/`.
- `mangle_string()` requires caller buffers at least `DM_NAME_LEN`, even when used for UUID-like strings.
- `_find_dm_name_of_device()` scans `_dm_dir`, so alternate dev directories affect path resolution.
- `dm_device_has_mounted_fs()` first checks mountinfo, then sysfs `/sys/fs/<fs>/<kernel_dev_name>`, with a TODO noting namespace implications.
- `_udev_wait()` supports an immediate/nonblocking mode by inspecting semaphore value before waiting.
- The non-udev build path still calls `update_devs()` in wait functions so direct fallback node operations are not lost.
