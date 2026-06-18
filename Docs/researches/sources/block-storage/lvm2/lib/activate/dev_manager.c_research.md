# File Research: sources/block-storage/lvm2/lib/activate/dev_manager.c

## Role

`dev_manager.c` is the low-level LVM2 device-mapper backend. It translates LV metadata graphs into libdevmapper dependency trees, creates/preloads/activates/suspends/deactivates DM devices, parses target status/table lines, manages udev flags and fallback symlinks, checks whether mapped devices are safe to scan, and provides target-specific runtime status helpers.

## Internal Model

`struct dev_manager` owns a memory pool, command context, target-state pointer, pvmove mirror count, flush-required state, activation/suspend mode flags, pending-delete and pvmove dependency tracking flags, and the VG name. Tree operations are represented by `action_t`: `PRELOAD`, `ACTIVATE`, `DEACTIVATE`, `SUSPEND`, `SUSPEND_WITH_LOCKFS`, and `CLEAN`.

`struct lv_layer` is attached as a DM tree node context to remember the LV, old DM name for rename detection, and whether a component LV is intentionally visible.

## Device-Mapper Task Layer

The central helper `_setup_task_run()` creates libdevmapper tasks, sets name/UUID/event/major-minor selectors, enables optional activation checks, controls open-count and flush behavior, handles inactive-table queries, and runs the task except for `DM_DEVICE_TARGET_MSG`, which requires caller-specific message setup. It is the common path for info, status, table, list, remove, message, and mknodes work.

Information helpers include:

- `_info_run()` for UUID/devno-based `DM_DEVICE_INFO` or `DM_DEVICE_STATUS`, including read-ahead and segment-status extraction.
- `_info()` for primary UUID, old suffix format, and pre-2.02 UUID compatibility probing.
- `dev_manager_info()` for public LV/layer lookup with dm device cache short-circuiting.
- `devno_dm_uuid()` and `dev_dm_uuid()` for DM UUID lookup.
- `dev_manager_get_dm_active_devices()` and `dev_manager_check_prefix_dm_major_minor()` for global device enumeration/checking.

## Status Parsing

`_get_segment_status_from_target_params()` validates the active DM target type against the expected segment type, handles snapshot-merge target compatibility, and fills `struct lv_seg_status` with parsed cache, raid, snapshot, thin, thin-pool, VDO pool, writecache, or integrity status. VDO status combines table/status parsing with a `stats` target message to obtain block usage counters.

Dedicated public status helpers exist for snapshots, mirrors/RAID percent, RAID status/messages, writecache messages, cache status, thin pool status, thin status and device IDs, VDO pool status, and VDO pool runtime size configuration.

## Device Usability Checks

`dm_device_is_usable()` rejects mapped devices according to caller policy:

- Empty target tables.
- Suspended devices when requested.
- LVM internal/reserved UUIDs, reserved LV names, private crypt devices, and Stratis devices.
- Blocked mirrors with failed components and blocking table options.
- Suspended snapshot components.
- Invalid snapshots.
- Frozen RAID devices.
- Thin devices whose pool is read-only or out of data space.
- Devices consisting only of `error` or `zero` targets when requested.

This function is part of the scanning safety boundary: it prevents LVM label/device scans from blocking on broken targets or recursively consuming private LVM devices.

## Tree Discovery and Construction

Existing device discovery builds partial trees with `_create_partial_dtree()` and `_add_lv_to_dtree()`. These functions add the public LV, private layers such as `real`, `cow`, `tpool`, `vpool`, cachevol `cdata`/`cmeta`, snapshots, origins, external origins, pool metadata, writecache/integrity devices, pvmove users, pending-delete users, and segment AREA_LV dependencies.

New tree construction is handled by `_add_new_lv_to_dtree()` and `_add_segment_to_dtree()`:

- Adds DM nodes with correct names, UUIDs, read-only flags, major/minor policy, clear-inactive-table behavior, context, and udev flags.
- Handles snapshot origins, COW devices, snapshot merge targets, external origins, thin pools, VDO pools, writecache origins, cache pools/cachevol subdevices, pending-delete error mappings, and pvmove dependency reloads.
- Delegates actual target-line construction to segment-type `add_target_line` ops via `_add_target_to_dtree()`.
- Adds pool metadata check callbacks for thin/cache where appropriate.
- Sets read-ahead based on explicit LV settings, stripe geometry, or calculated defaults.

`add_areas_line()` is the shared target-area builder used by segment types. It maps PV areas by block-device path and PE offset, maps LV areas by DM UUID and LE offset, handles RAID metadata/data pairs, represents missing RAID legs as null areas where valid, and creates error/zero filler devices for partial/degraded activation when policy permits.

## Udev and Symlink Handling

`_init_udev_fallback()` computes whether LVM should verify or perform fallback udev operations based on config, rule availability, environment-driven libdm behavior, and driver capability. `_get_udev_flags()` generates libdm udev flags for top-level devices, hidden layers, new thin pools, reserved names, snapshots, noscan LVs, temporary LVs, and disabled udev rules.

After activation, `_create_lv_symlinks()` walks tree children and creates, removes, or renames `/dev/<vg>/<lv>` links through `fs.c` when fallback is enabled. Deactivation uses `_remove_lv_symlinks()`. `_clean_tree()` tracks and removes unused non-top-level private nodes and pending-delete UUIDs.

## Tree Actions

`_tree_action()` is the main executor:

- Builds a partial tree and sets the current fs cookie on the root.
- For `PRELOAD` and `ACTIVATE`, adds required new nodes, preloads child tables, records whether flush is required due to size changes, activates children, and creates symlinks.
- For `SUSPEND` and `SUSPEND_WITH_LOCKFS`, applies no-flush and lockfs policy and suspends matching children.
- For `DEACTIVATE`, removes matching children and symlinks.
- For `CLEAN`, removes unused private nodes and pending-delete devices.

Public wrappers `dev_manager_activate()`, `dev_manager_preload()`, `dev_manager_deactivate()`, and `dev_manager_suspend()` configure state and call `_tree_action()`.

## Other Utilities

- `read_only_lv()` enforces read-only policy while keeping COW layers and RAID sub-LVs writable where required.
- `add_linear_area_to_dtree()` chooses a striped single-area target when the extent size is page-size compatible, otherwise falls back to linear.
- `dev_manager_device_uses_vg()` builds a dependency tree from a device and checks whether any child UUID belongs to the target VG.
- `get_crypt_table_offset()` parses the active `crypt` target table to return the payload offset in bytes for resize calculations.

## Risks and Invariants

- DM UUID construction and optional suffix handling must match `build_dm_uuid()` and historical compatibility rules; mismatches can hide active devices or remove the wrong private layer.
- Tree-building recursion must avoid loops and must distinguish public devices from layers, especially for origins, snapshots, thin pools, VDO pools, cachevols, pvmove, and pending delete.
- `dm->mem` ownership is used for returned status structs; callers must follow the API contract and destroy pools only when ownership has effectively been transferred.
- `dm_device_is_usable()` intentionally errs toward "not usable" or "uncertain" for safety; relaxing checks can cause blocked scans or accidental use of private LVM/crypt devices.
- Udev fallback state must be initialized before threaded or const deactivation paths, because later code reads it through the command context.
