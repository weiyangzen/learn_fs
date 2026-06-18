# File Research: sources/block-storage/lvm2/libdm/libdm-deptree.c

## Purpose

`libdm-deptree.c` implements libdevmapper’s dependency-tree model and activation engine. It builds an in-memory graph of device-mapper devices and their dependencies, then uses it to create, preload, suspend, resume, rename, message, and remove mapped devices in dependency-safe order. It also builds target table lines for many DM target types.

## Supported Target Types

The file maps internal segment types to kernel target names for:
- `cache`
- `crypt`
- `error`
- `linear`
- `mirror`
- `snapshot`
- `snapshot-origin`
- `snapshot-merge`
- `striped`
- `zero`
- `writecache`
- `integrity`
- `thin-pool`
- `thin`
- `vdo`
- `raid` variants including raid0, raid1, raid10, raid4, raid5, and raid6 layouts.

Replicator targets are explicitly unsupported and return errors.

## Core Data Structures

- `struct seg_area`
  - Represents an underlying area/device plus offset for segment types that consume other block devices.
- `struct dm_thin_message` and `struct thin_message`
  - Represent queued thin-pool target messages and expected errno values.
- `struct load_segment`
  - Per-table-segment state. It stores the target type, size, device areas, and target-specific fields for snapshot, mirror, raid, cache, thin, VDO, writecache, integrity, and crypt targets.
- `struct load_properties`
  - Per-node activation/load state: read-only flag, major/minor, read-ahead, segment list, delayed resume flags, send-message flags, reload comparison flags, sibling reactivation flags, and related activation controls.
- `struct dm_tree_link`
  - Bidirectional edge wrapper for dependency lists.
- `struct dm_tree_node`
  - A graph node representing one device. It holds name, UUID, `dm_info`, dependency edges, udev flags, caller context, load properties, optional presuspend node, callback, and activation bookkeeping.
- `struct dm_tree`
  - Owns the memory pool, hash tables by dev_t and UUID, root pseudo-node, global activation options, cookie, debug buffer, and optional UUID suffix list.

## Tree and Node Management

- `dm_tree_create()` allocates a tree, root node, memory pool, and hash tables.
- `dm_tree_free()` destroys hash tables and pool.
- `dm_tree_set_cookie()` / `dm_tree_get_cookie()` set/read the shared udev cookie.
- `dm_tree_skip_lockfs()`, `dm_tree_use_no_flush_suspend()`, `dm_tree_retry_remove()` set activation flags.
- `_link_nodes()`, `_unlink_nodes()`, `_link_tree_nodes()` maintain bidirectional dependency edges and special root top/bottom-level links.
- `_create_dm_tree_node()` allocates a node and inserts it into dev and UUID hashes.
- `dm_tree_find_node()` and `dm_tree_find_node_by_uuid()` find existing nodes, with root special cases.
- `_find_dm_tree_node_by_uuid()` supports optional suffix matching and transition handling for missing default UUID prefixes.
- `dm_tree_next_child()` iterates either child dependencies or inverse parent edges.
- `dm_tree_node_num_children()` counts dependencies while treating root pseudo-links specially.
- Accessors expose node name, UUID, info, context, udev flags, read-ahead, callback, and size-change state.

## Discovery and Dependency Import

`_add_dev()` imports an existing kernel device into the tree:
- Calls `_deps()` for DM devices to run `DM_DEVICE_DEPS`.
- Creates a node if absent.
- Links it under the supplied parent.
- Recurses over dependency major/minor pairs.
- Marks implicit dependencies and applies restrictive udev flags to them.

`dm_tree_add_dev()` and `dm_tree_add_dev_with_udev_flags()` expose this import behavior.

New devices are added through `dm_tree_add_new_dev_with_udev_flags()` or `dm_tree_add_new_dev()`. These create a placeholder node when the UUID is absent from the tree, attach it to top and bottom root links until a table is supplied, store requested major/minor, read-only state, context, and udev flags, and optionally clear an inactive table.

## Activation and Deactivation

The activation engine is organized around dependency order and current kernel state.

Important helpers:
- `_info_by_dev()` refreshes `DM_DEVICE_INFO`.
- `_check_device_not_in_use()` detects open devices using open count, sysfs holders, and mounted filesystem checks.
- `_node_has_closed_parents()` prevents deactivation when parent nodes remain open.
- `_create_remove_task()` and `_deactivate_node()` build/run remove tasks.
- `_node_clear_table()` clears inactive tables and removes orphaned incomplete dependencies.
- `_rename_node()` runs a rename task.
- `_resume_node()` runs resume, sets read-ahead, handles udev cookie, and decrements the suspended counter if resuming a previously suspended node.
- `_suspend_node()` runs suspend, honors skip-lockfs and no-flush options, increments the suspended counter, and refreshes info.

Public traversal functions:
- `dm_tree_deactivate_children()` recursively removes children matching a UUID prefix.
- `dm_tree_suspend_children()` suspends children once parents are suspended and may send thin-pool messages instead of suspending lower nodes.
- `dm_tree_activate_children()` activates children in dependency order, handles renames, resolves peer rename conflicts, resumes inactive/suspended nodes, sends post-resume messages, and optionally reactivates siblings.
- `dm_tree_preload_children()` recursively creates missing nodes, loads inactive tables, conditionally resumes extended devices, validates messages for newly-created nodes, handles immediate dev-node synchronization, invokes preload callbacks, and reverts created devices on failure.
- `dm_tree_children_use_uuid()` checks whether any child subtree belongs to a UUID prefix.

## Message Handling

Thin-pool and VDO targets require runtime messages:
- `_thin_pool_get_status()` reads and parses thin-pool status.
- `_thin_pool_node_message()` formats `create_snap`, `create_thin`, `delete`, `set_transaction_id`, `reserve_metadata_snap`, and `release_metadata_snap`.
- `_thin_pool_node_send_messages()` validates transaction IDs, checks failed/read-only/needs-check status, sends queued messages, and verifies transaction-id updates.
- `_vdo_get_status()` reads and parses VDO status.
- `_vdo_node_send_messages()` toggles compression and deduplication/index state when runtime status differs from requested target parameters.
- `_node_send_messages()` dispatches by the last load segment’s type.

## Table Emission

Segment emission converts `load_segment` objects into DM table target parameters:
- `_emit_areas_line()` formats underlying devices and offsets, with special handling for raid null areas.
- `_mirror_emit_segment_line()` emits mirror log parameters, region size, sync/error flags, clustered log UUIDs, and areas. It uses kernel version to choose legacy/current `block_on_error` vs `handle_errors` behavior and userspace clustered logs.
- `_raid_emit_segment_line()` emits raid target lines, including sync flags, rebuild/writemostly bitmaps, recovery rates, writebehind, region size, raid10 copies, reshape parameters, and metadata/data pairs. It checks target version because target parameter ordering differed between raid target versions.
- `_cache_emit_segment_line()` emits metadata/data/origin devices, block size, cache feature mode, metadata2 flag, policy name, migration threshold, and integer policy settings.
- `_writecache_emit_segment_line()` emits writecache device mode, origin/cache devices, block size, and optional settings.
- `_integrity_emit_segment_line()` emits integrity target settings and marks task data secure.
- `_vdo_emit_segment_line()` emits VDO V2/V4 table lines, including data device path, data size, IO/cache/era settings, compression/deduplication controls, and thread/discard parameters. It may read an existing VDO table or metadata logical size to correct virtual size upward.
- `_thin_pool_emit_segment_line()` emits metadata/data devices, block size, low-water mark, and feature flags.
- `_thin_emit_segment_line()` emits pool device, device ID, and optional external origin.
- `_emit_segment_line()` dispatches by segment type and calls `dm_task_add_target()`.
- `_emit_segment()` retries with larger parameter buffers up to `MAX_TARGET_PARAMSIZE`.
- `_load_node()` builds and runs a reload task, suppresses identical reloads, detects table size changes, and applies delayed-resume rules.

## Target Construction APIs

The file provides public functions to add target segments to a node:
- Snapshot:
  - `dm_tree_node_add_snapshot_origin_target()`
  - `dm_tree_node_add_snapshot_target()`
  - `dm_tree_node_add_snapshot_merge_target()`
- Simple:
  - `dm_tree_node_add_error_target()`
  - `dm_tree_node_add_zero_target()`
  - `dm_tree_node_add_linear_target()`
  - `dm_tree_node_add_striped_target()`
  - `dm_tree_node_add_crypt_target()`
- Mirror:
  - `dm_tree_node_add_mirror_target()`
  - `dm_tree_node_add_mirror_target_log()`
- Raid:
  - `dm_tree_node_add_raid_target()`
  - `dm_tree_node_add_raid_target_with_params()`
  - `dm_tree_node_add_raid_target_with_params_v2()`
- Cache:
  - `dm_tree_node_add_cache_target()`
  - `dm_tree_node_add_cachevol_target()`
- Writecache:
  - `dm_tree_node_add_writecache_target()`
- Integrity:
  - `dm_tree_node_add_integrity_target()`
- Thin:
  - `dm_tree_node_add_thin_pool_target()`
  - `dm_tree_node_add_thin_pool_target_v1()`
  - `dm_tree_node_add_thin_pool_message()`
  - `dm_tree_node_set_thin_pool_discard()`
  - `dm_tree_node_set_thin_pool_error_if_no_space()`
  - `dm_tree_node_set_thin_pool_read_only()`
  - `dm_tree_node_add_thin_target()`
  - `dm_tree_node_set_thin_external_origin()`
- Areas and callbacks:
  - `dm_tree_node_add_target_area()`
  - `dm_tree_node_add_null_area()`
  - `dm_tree_node_set_callback()`
- VDO:
  - `dm_tree_node_add_vdo_target()`

## Dependency Linking Rules

Most target add functions find dependency nodes by UUID and link them to the new target node. For physical paths, `dm_tree_node_add_target_area()` uses `stat()` and imports the block device by major/minor. Some targets also adjust activation properties:
- Snapshot origins get activation priority and may trigger sibling reactivation.
- Snapshot merge nodes manipulate priorities so snapshot-merge and merging snapshot resume in the right order.
- Mirror logs may require immediate dev-node creation for clustered logs.
- Thin-pool metadata/data nodes clear `delay_resume_if_new`.
- Thin external origins may delay resume if newly-created.
- Integrity nodes set `skip_reload_params_compare`.
- VDO versions below 4 require runtime messages.

## Validation and Edge Cases

- `_uuid_prefix_matches()` handles default UUID-prefix transitions.
- `_children_suspended()` ignores nodes outside the requested UUID prefix and presuspend exceptions.
- Deactivation skips or errors on open devices depending on level, retry settings, holders, and mounted filesystems.
- Concurrent external resume during suspend is treated as an abort condition.
- Rename conflicts can be resolvable if the conflicting sibling is also being renamed.
- `_load_node()` distinguishes grown, shrunk, unchanged, and zero-length tables and has special delayed-resume handling for thin-pool-on-raid resize scenarios.
- Thin-pool messages require sequential transaction IDs.
- Thin device IDs are bounded by `DM_THIN_MAX_DEVICE_ID`.
- Cache feature flags are validated; cleaner policy forces writethrough mode.
- Cache migration threshold is forced to at least `data_block_size * 8`.
- Thin metadata can be cropped to `DM_THIN_MAX_METADATA_SIZE`.
- Raid supports null areas only for raid segment types.
- Backward-compatible symbol versions are provided under `GNU_SYMVER` for `dm_tree_node_size_changed()` and old cache target feature masking.

## Dependencies and Interactions

- Uses `libdm-common.h` for device-node, UUID-prefix, suspended-counter, thin-status, and kernel-version helpers.
- Uses `dm_task_*` ioctl wrappers extensively for info, deps, create, remove, rename, suspend, resume, reload, clear, status, target messages, and target versions.
- Uses config-tree cloning for cache policy settings.
- Uses udev cookies through `dm_task_set_cookie()` and `dm_udev_wait()`.
- Uses sysfs/mount checks indirectly through `dm_device_has_holders()` and `dm_device_has_mounted_fs()` from `libdm-common.c`.
