# Group Research: group_1138_lvm2_sources_block_storage_lvm2_libdm_ioctl_libdm_iface_c_sources_b_3e78c3faef8e

Scope: `Docs/research_subset_a.md`; source tree `sources/block-storage/lvm2` is included in subset A.

Read coverage: complete read of all listed files, 6,842 total source lines.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/ioctl/libdm-iface.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/ioctl/libdm-iface.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/ioctl/libdm-targets.h -->
# File Research: sources/block-storage/lvm2/libdm/ioctl/libdm-targets.h

Purpose: defines libdevmapper's internal ioctl/task data structures shared by the ioctl implementation and related low-level code.

Read coverage: complete file read, 99 lines.

Key contents:
- Declares `struct target`, the internal linked-list node for a table segment with start sector, length, target type, target parameters, and next pointer.
- Defines the full internal `struct dm_task`, including public task type, device name/UUID and mangled variants, target list, major/minor identity, permissions, read-ahead, ioctl result buffer, rename/message/geometry state, flags, udev cookie state, expected/ioctl errno, timestamp recording, and feature toggles.
- Defines `struct cmd_data`, mapping a public task type to a command name, ioctl number, and version triplet.
- Defines remove retry constants: `DM_IOCTL_RETRIES` and `DM_RETRY_USLEEP_DELAY`.
- Declares internal helpers `dm_ioctl_exec()`, `dm_check_version()`, and `dm_task_get_existing_table_size()`.

Dependencies:
- Includes the public `libdevmapper.h` API and standard integer/types headers.
- Forward-declares `struct dm_ioctl`, keeping the kernel ioctl ABI definition out of this internal header's public declarations.

Risk and edge cases:
- `struct dm_task` is an internal ownership hub; memory-management mistakes around moved target lists, `dmi.v4`, mangled strings, and secure data can produce leaks, double frees, or missed zeroing.
- The header exposes internals across libdm compilation units, so field changes require careful ABI/API separation from the public opaque `struct dm_task`.
- Retry constants directly shape remove latency: 25 retries at 200 ms can add about five seconds to busy-device removal attempts.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/ioctl/libdm-targets.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdevmapper.h -->
# File Research: sources/block-storage/lvm2/libdm/libdevmapper.h

Purpose: declares libdevmapper's public C API: direct device-mapper task/ioctl operations, target status parsers, dependency tree construction, dm-stats, target table builders, memory/data-structure utilities, reporting, config parsing, timestamps, udev synchronization, and miscellaneous string/file helpers.

Read coverage: complete file read, 4,107 lines.

Key API areas:
- Logging setup via modern errno-aware callbacks and deprecated legacy callbacks, plus suspended-device tracking.
- Direct task API for creating/destroying `dm_task`, setting name/UUID/major/minor/permissions/cookies/messages/geometry/read-ahead/flags, adding targets, running ioctls, and reading info/deps/names/versions/messages.
- Device-mapper status parsers for mirror, raid, cache, writecache, integrity, snapshot, thin-pool, thin, VDO status, and VDO stats.
- `dm_stats` API for creating/listing/populating/deleting/clearing statistics regions, precise timestamp and histogram support, program IDs, region/group/file-extent mapping, cursor walks, raw counters, derived metrics, and histogram formatting.
- Name/UUID mangling controls and direct mangled/unmangled accessors.
- Device and environment helpers for DM directory, sysfs directory, UUID prefixes, major detection, sysfs name lookup, holders, mounted filesystem checks, and `/proc/self/mountinfo` iteration.
- Dependency tree API for discovering, constructing, preloading, activating, suspending, and deactivating mapped-device trees.
- Target table builders for snapshot, error, zero, linear, striped, crypt, mirror, raid, cache, cachevol, writecache, integrity, VDO, replicator, thin-pool, thin, target areas, null areas, read-ahead, callbacks, and udev flags.
- Memory management wrappers, pool allocator/object builder, bitsets, hashes, intrusive lists, active-device list helpers, SELinux context helpers, string utilities, unit/size formatting, directory and stream helpers, asprintf wrappers, daemon lockfile checks, regex helpers, percent helpers, timestamps, report generation, report grouping, and config tree parse/write/query APIs.
- Udev cookie constants and synchronization functions, including rule-disabling flags, subsystem flag space, cookie creation/completion/wait, and immediate wait probing.

Important types and constants:
- Public task enum `DM_DEVICE_CREATE` through `DM_DEVICE_GET_TARGET_VERSION`.
- Public result structures: `dm_info`, `dm_deps`, `dm_names`, `dm_versions`, target-specific status structures, `dm_active_device`, config node/value/tree, report field/object/group structures, and target parameter structures.
- Target constants for cache, thin, VDO, mirror log flags, RAID bitmap sizing, read-ahead, percent fixed-point values, histogram formatting flags, and udev cookie flags.
- Opaque handles for `dm_task`, `dm_pool`, `dm_tree`, `dm_tree_node`, `dm_stats`, `dm_histogram`, `dm_report`, `dm_regex`, and `dm_hash_table`.

Dependencies:
- Publicly includes standard C/POSIX headers and Linux types when available.
- Serves as the central header consumed by libdevmapper users and by LVM2 internals building mapped-device tables and reporting.
- Many declarations are implemented across libdm submodules, not solely by `ioctl/libdm-iface.c`.

Risk and edge cases:
- The header is very broad; API consumers can mix low-level task calls, tree APIs, and udev synchronization incorrectly if they do not follow each subsystem's ordering rules.
- Several comments document ABI compatibility constraints, especially around structs extended over time and alternate versioned APIs such as RAID params v2 and thin-pool target v1.
- `dm_pool_free()` frees an object and all later allocations from the same pool, which is efficient but dangerous if callers expect ordinary `free()` semantics.
- Report and config APIs return many pool-owned or handle-owned pointers that become invalid after destroy, list, populate, bind, or parse lifecycle operations.
- dm-stats file mapping depends on regular files, local filesystems, FIEMAP support, stable extents, and device-mapper backing devices.
- Udev flags influence whether udev or libdevmapper manages nodes; using `DM_UDEV_DISABLE_LIBRARY_FALLBACK` assumes udev rules are correct.
- Some constants preserve historical behavior despite known mismatch with kernel formulas, notably `DM_THIN_MAX_METADATA_SIZE`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdevmapper.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdevmapper.pc.in -->
# File Research: sources/block-storage/lvm2/libdm/libdevmapper.pc.in

Purpose: provides the pkg-config template for consumers linking against libdevmapper.

Read coverage: complete file read, 12 lines.

Key contents:
- Defines install-time variables `prefix`, `exec_prefix`, `libdir`, and `includedir`.
- Publishes package metadata: `Name: devmapper`, description `device-mapper library`, and version placeholder `@DM_LIB_PATCHLEVEL@`.
- Exposes compile flags as `-I${includedir}`.
- Exposes public linker flags as `-L${libdir} -ldevmapper`.
- Lists private dependencies for static/private linking through `Requires.private: @SELINUX_PC@ @UDEV_PC@`.
- Lists private libraries `-lm @RT_LIBS@ @PTHREAD_LIBS@`.

Dependencies:
- Filled by the build system from configure/meson-style substitution variables before installation.
- Represents SELinux, udev, realtime, pthread, and math dependencies without forcing all of them into dynamic consumers' public link lines.

Risk and edge cases:
- Incorrect substitution of private dependency placeholders can break static linking or overexpose platform libraries.
- The `Cflags` line has a trailing space after `${includedir}`, harmless for pkg-config but worth preserving only if generated output compatibility expects it.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdevmapper.pc.in -->