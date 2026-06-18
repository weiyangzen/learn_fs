# File Research: sources/block-storage/lvm2/libdm/ioctl/libdm-iface.c

Purpose: implements libdevmapper's low-level device-mapper ioctl interface, converting public `dm_task` requests into kernel `dm_ioctl` buffers and coordinating control-device setup, udev cookies, node operations, result unmarshalling, retries, and library lifecycle cleanup.

Read coverage: complete file read, 2,624 lines.

Key responsibilities:
- Defines the v4 device-mapper command table mapping `DM_DEVICE_*` task types to ioctl command numbers and minimum driver versions.
- Discovers kernel and device-mapper state through `uname`, `/proc/devices`, `/proc/misc`, static `/dev/mapper/control` minor handling, and cached DM major-number bitsets.
- Creates, validates, opens, optionally holds, and releases the `/dev/mapper/control` character device.
- Checks kernel driver compatibility, tracks the running dm driver version, and gates features such as cookies, inactive-table queries, precise timestamps, secure data, UUID changes, and IMA measurement.
- Owns `dm_task` destruction, target-list cleanup, secure zeroing of sensitive strings/ioctl buffers, target iteration, dependency/name/version/message result accessors, and `dm_info` extraction.
- Flattens task state into `struct dm_ioctl`, including persistent major/minor, name/UUID, target specs, messages, rename/new UUID payloads, geometry payloads, flags, event numbers, and minimum buffer sizing.
- Implements device list conversion into `struct dm_active_device` lists, preserving optional event numbers and UUIDs when supported by the kernel.
- Handles old-style create-with-table by chaining create, reload, resume and reverting the created device on failure.
- Supports identical-reload suppression by reading the existing live table, comparing type/start/length/params/read-only state, and recording the existing table size.
- Provides suspend validation that recursively checks DM dependencies to avoid trapping I/O between already-suspended devices.
- Executes ioctls with remove-on-`EBUSY` retry, buffer-full retry for variable-size result calls, post-ioctl error handling, timestamp capture, name/UUID unmangling, and udev completion fallback when the kernel did not generate a uevent.
- Performs userspace device-node operations after successful create/remove/rename/resume/mknodes operations when not relying entirely on udev.
- Implements library release/exit cleanup for control fd, timestamps, SELinux state, DM major bitset, memory pools, and debug memory accounting.
- Preserves ABI compatibility for older `dm_task_get_info` symbol versions.

Important entry points:
- `dm_task_run()`, `dm_ioctl_exec()`, `dm_task_destroy()`, `dm_check_version()`, `dm_cookie_supported()`, `dm_is_dm_major()`.
- Result accessors: `dm_task_get_info()`, `dm_task_get_deps()`, `dm_task_get_names()`, `dm_task_get_versions()`, `dm_task_get_message_response()`, `dm_task_get_device_list()`.
- Task mutators: `dm_task_set_ro()`, `dm_task_set_newuuid()`, `dm_task_set_message()`, `dm_task_set_sector()`, `dm_task_set_geometry()`, `dm_task_no_flush()`, `dm_task_secure_data()`, `dm_task_ima_measurement()`, `dm_task_retry_remove()`, `dm_task_query_inactive_table()`, `dm_task_set_record_timestamp()`.
- Lifecycle helpers: `dm_hold_control_dev()`, `dm_lib_release()`, `dm_lib_exit()`, `dm_task_update_nodes()`.

Dependencies:
- Includes internal libdm helpers from `dmlib.h`, `libdm-common.h`, `libdm-targets.h`, and kernel/user ABI definitions from `dm-ioctl.h`.
- Uses Linux-specific device number helpers, `/proc`, `/dev/mapper`, SELinux setup hooks, udev synchronization helpers, timestamp helpers, string mangling helpers, node-management helpers, and logging.
- The implementation is compiled differently when `DM_IOCTLS` is unavailable, providing a limited userspace-testing path.

Risk and edge cases:
- Several global caches and flags (`_control_fd`, version state, major bitset, ioctl buffer growth, timestamp object, warning counters) make behavior process-global and require careful lifecycle handling in long-running or multi-threaded callers.
- Control-node creation races are partially handled by rechecking `EEXIST`, but behavior still depends on `/proc`, udev, permissions, SELinux context setup, and kernel module autoloading.
- Buffer-full retry uses a global doubling factor and can grow from 16 KiB up to 1 GiB; callers should treat very large DM result sets as a memory-pressure path.
- Udev cookie logic intentionally disables udev rules when synchronization support exists but the caller did not provide a cookie; incorrect flag combinations can leave node creation to either udev or libdevmapper fallback unexpectedly.
- Secure data paths zero target params and ioctl buffers, but only for tasks marked secure before allocations are destroyed.
- Message logging sanitizes key-setting messages, but other target messages may still appear in debug logs.
- Identical-reload suppression trims trailing spaces from existing target params before comparison, so formatting differences can affect reload decisions.
