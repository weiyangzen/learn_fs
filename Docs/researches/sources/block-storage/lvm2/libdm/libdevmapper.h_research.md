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
