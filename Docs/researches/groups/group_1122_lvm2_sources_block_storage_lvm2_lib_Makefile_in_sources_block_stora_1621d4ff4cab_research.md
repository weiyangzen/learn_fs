# Group Research: group_1122_lvm2_sources_block_storage_lvm2_lib_Makefile_in_sources_block_stora_1621d4ff4cab

Scope: `Docs/research_subset_a.md` (`sources/block-storage/lvm2`).

This group covers the LVM2 library activation unit: the build inclusion point, public activation API, device-manager API, device-mapper tree builder, `/dev` symlink fallback handling, and target-area helper declaration.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/Makefile.in -->
# File Research: sources/block-storage/lvm2/lib/Makefile.in

## Role

This makefile defines the source list for `liblvm-internal.a`, the internal LVM2 library used by command and daemon code. It is the build aggregation point for metadata, devices, filters, reporting, segment types, and activation support.

## Build Behavior

- Always includes `activate/activate.c`, so the high-level activation API is compiled even when devmapper support is disabled. In that case `activate.c` provides stub implementations for many activation functions.
- Adds `activate/dev_manager.c` and `activate/fs.c` only when `@DEVMAPPER@` is `yes`; these are the real device-mapper backend and fallback `/dev/<vg>/<lv>` symlink implementation.
- Adds `lvmpolld/lvmpolld-client.c`, `locking/lvmlockd.c`, and `vdo/vdo.c` behind configure flags.
- Sets `LIB_NAME = liblvm-internal`, `LIB_STATIC = $(LIB_NAME).a`, and uses the shared LVM build template via `include $(top_builddir)/make.tmpl`.
- Populates `CFLOW_LIST` from `SOURCES`, enabling cflow dependency generation for the internal library.

## Dependency Context

The activation files in this group are part of the same static library as metadata manipulation, device discovery, filters, segment-type modules, locking, memory locking, reporting, and misc helpers. This explains the dense internal include graph in `activate.c` and `dev_manager.c`: activation is not an isolated frontend; it consumes committed/precommitted LV metadata and writes device-mapper tables from that metadata.

## Important Invariants

- `activate/activate.c` must remain unconditional because public activation APIs need linkable stubs without devmapper.
- `activate/dev_manager.c` and `activate/fs.c` must remain conditional on devmapper because they directly use libdevmapper task/tree and udev-cookie operations.
- Any new segment type that needs activation normally requires both a source entry elsewhere in this makefile and activation hooks through segment-type ops consumed by `dev_manager.c`.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/activate/activate.c -->
# File Research: sources/block-storage/lvm2/lib/activate/activate.c

## Role

`activate.c` is the high-level activation facade for LVM logical volumes. It exposes the API declared in `activate.h`, gates behavior on activation settings and configuration filters, delegates real device-mapper work to `dev_manager.c`, coordinates critical sections and udev cookie synchronization, and manages dmeventd monitoring.

## Major Responsibilities

- Module discovery: recursively collects device-mapper target module names needed by LV segments, origins, snapshots, and LV areas through `list_segment_modules()` and `list_lv_modules()`.
- Activation filters: evaluates `activation/volume_list`, `activation/auto_activation_volume_list`, and `activation/read_only_volume_list`, supporting `vg`, `vg/lv`, exact tags, and host-tag wildcard matching.
- Devmapper availability: when `DEVMAPPER_SUPPORT` is absent, provides stub functions that either no-op successfully for workflow functions or return inactive/unsupported status for query functions.
- Driver and target probing: wraps libdevmapper library/driver version calls, target version queries, sysfs module detection, `modules.builtin` scanning, and optional `modprobe`.
- LV info and status: resolves active DM devices, including layered forms such as `-real`, `-tpool`, `-vpool`, cache pool users, snapshot merge state, VDO pool status, and combined `lv_info_with_seg_status()` status extraction.
- Activation lifecycle: implements suspend, resume, activate, deactivate, preload, temporary activation, and convenience wrappers over committed metadata.
- Use checks: verifies open counts, sysfs holders, mounted filesystems, active components, active holders, and active sub-LVs before destructive operations.
- Event monitoring: recursively registers/unregisters dmeventd monitoring for snapshots, mirrors, pools, external origins, metadata LVs, AREA_LV dependencies, and segment types that implement monitor hooks.

## Key Public Entry Points

- `set_activation()` / `activation()` control whether device-mapper interactions are attempted.
- `library_version()`, `driver_version()`, `target_version()`, `target_present_version()`, `target_present()`, and `module_present()` expose kernel/libdm capability checks.
- `lv_info()`, `lv_info_with_name_check()`, and `lv_info_with_seg_status()` are status-query APIs used by commands and reports.
- `lv_snapshot_status()`, `lv_raid_status()`, `lv_cache_status()`, `lv_thin_status()`, `lv_thin_pool_status()`, `lv_vdo_pool_status()`, and related percent/message helpers return target-specific runtime state.
- `lv_suspend_if_active()`, `lv_resume()`, `lv_resume_if_active()`, `lv_activate()`, `lv_activate_with_filter()`, `lv_deactivate()`, `lv_mknodes()`, and wrapper forms such as `activate_lv()` and `deactivate_lv()` drive LV lifecycle changes.
- `lv_component_is_active()`, `lv_holder_is_active()`, and `deactivate_lv_with_sub_lv()` protect stacked component relationships.

## Core Flow

Activation first applies filters and partial/degraded activation rules, rejects unknown or invalid RAID-visible sub-LV states, calculates read-ahead, creates a udev cookie, enters a critical section, and calls `dev_manager_activate()`. On success it registers event monitoring. Deactivation performs in-use checks for visible/virtual/merging LVs, unmonitors, enters a critical section, calls `dev_manager_deactivate()`, removes temporary missing RAID subdevices, and verifies that the public device disappeared.

Suspend is more complex because it may preload tables from precommitted metadata before suspending. It handles pvmove removal, detached hidden-to-visible LVs, removed snapshots, flush requirements, dmeventd unmonitoring, filesystem locking for snapshot and thin conversion cases, and critical-section management. Resume reactivates loaded tables, decrements the critical section, and restores monitoring.

## Special-Case Handling

- New thin pools may require querying the `-tpool` layer while reporting the public pool as inactive if only the layer exists.
- VDO volumes query the public VDO LV for info but the VDO pool layer for pool status.
- Snapshot origins and COW volumes redirect status queries depending on merge state.
- Visible LVs that still have private `-real` UUID devices can be detected through `_lv_info_real()` to handle historical RAID/mirror transitions.
- RAID messages are deliberately restricted at the high-level API to user-facing `check` and `repair` transitions from `idle`, even though the lower layer supports more dm-raid messages.

## Dependencies

This file depends on metadata helpers for LV classification and traversal, config-tree readers, locking/critical-section helpers, dmeventd APIs under `DMEVENTD`, libdevmapper task APIs, `dev_manager.h` for all device-tree work, and `fs.h` for udev cookie and node synchronization.

## Risks and Invariants

- Activation functions assume VG locks and committed/precommitted metadata are coherent; many internal failures are logged as `INTERNAL_ERROR`.
- Open-count checks must synchronize pending non-delete fs operations before trusting counts.
- Critical sections must be balanced around suspend/resume and activate/deactivate; `activation_release()` warns if activation is released while still in a critical section.
- Event monitoring recursion must avoid inappropriate unmonitoring of shared thin pools and must preserve snapshot-origin semantics.
- Without devmapper support, success-returning lifecycle stubs can let higher-level command logic proceed while no real kernel device work happens; callers rely on `activation()` and query results to distinguish that mode.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/activate/activate.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/activate/activate.h -->
# File Research: sources/block-storage/lvm2/lib/activate/activate.h

## Role

`activate.h` is the public internal header for LVM2 activation services. It defines common status structures, activation options, target/module name constants, and the function surface used by commands, metadata code, reports, polling, and segment types.

## Key Types

- `struct lvinfo` captures generic DM state: existence, suspension, open count, major/minor, read-only state, live/inactive table flags, and read-ahead.
- `lv_seg_status_type_t` identifies parsed runtime status classes: cache, raid, snapshot, thin, thin pool, VDO pool, writecache, integrity, unknown, or none.
- `struct lv_seg_status` carries a segment pointer and a union of parsed libdm target status structures or `struct lv_status_vdo`.
- `struct lv_with_info_and_seg_status` joins generic LV info with one segment status for reporting paths that can use a single ioctl when possible.
- `struct lv_activate_opts` is the activation option bundle: exclusivity, origin-only behavior, merge suppression, message sending, skip-in-use, revert/resume flags, read-only/noscan/temporary flags, and optional component LV context.
- `struct dev_usable_check_params` is a bitfield policy for determining if a mapped device is safe for scanning/use.

## API Surface

The header declares:

- Global activation controls and driver/target/module queries.
- DM UUID lookup by devno or `struct device`.
- LV lifecycle operations and user-facing wrappers.
- Runtime status and percent helpers for snapshots, mirrors, RAID, cache, thin, VDO, writecache, and integrity-adjacent paths.
- Active/open LV counting and active-component/holder detection.
- Activation filters, read-only filters, transient checks, target-type checks, and PV-uses-VG dependency checks.
- dmeventd registration helpers behind `DMEVENTD`.
- `add_linear_area_to_dtree()` for segment code that needs a linear/striped wrapper target.
- `fs_unlock()` is declared here rather than exposing `fs.h` broadly, keeping fs fallback internals mostly private to activation.

## Constants

The file centralizes device-mapper target names such as `cache`, `writecache`, `integrity`, `error`, `linear`, `mirror`, `raid`, `snapshot`, `snapshot-merge`, `thin`, `thin-pool`, `vdo`, and `zero`. It also defines kernel module names, including special handling for VDO as `kvdo` rather than a `dm-` prefixed module.

## Dependency and Ownership Notes

This header includes `metadata-exported.h`, so it is designed for broad internal use without exposing all activation-private implementation details. It intentionally references many opaque or externally defined types from metadata, libdm, dmeventd, and device code through declarations or included headers.

## Invariants

- Callers that receive target-specific status structs are often responsible for destroying the associated memory pool, as documented by implementation comments.
- `lv_activate_opts` fields are used by both high-level activation and low-level tree construction; adding fields must account for both layers.
- Target name constants must match kernel/libdm names and segment-type expectations, because they are used for capability checks, table/status parsing, and module loading.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/activate/activate.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/activate/dev_manager.c -->
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

<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/activate/dev_manager.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/activate/dev_manager.h -->
# File Research: sources/block-storage/lvm2/lib/activate/dev_manager.h

## Role

`dev_manager.h` declares the private activation backend API used primarily by `activate.c` and segment-type target builders. It hides `struct dev_manager` while exposing construction, destruction, LV status, lifecycle, node, dependency, and utility functions.

## API Groups

- Lifecycle: `dev_manager_create()`, `dev_manager_destroy()`, `dev_manager_release()`, and `dev_manager_exit()`.
- Generic device info: `dev_manager_info()` returns DM info/read-ahead and optional segment status for an LV/layer.
- Target statuses: snapshot percent/status, mirror percent, RAID status/message, writecache message, cache status, thin status/device ID/pool status, VDO status and VDO size config.
- Lifecycle actions: `dev_manager_preload()`, `dev_manager_suspend()`, `dev_manager_activate()`, `dev_manager_deactivate()`, and `dev_manager_transient()`.
- Node and dependency helpers: `dev_manager_mknodes()`, `dev_manager_device_uses_vg()`, `dev_manager_check_prefix_dm_major_minor()`, and `dev_manager_get_dm_active_devices()`.
- Utility helpers: `read_only_lv()` and `get_crypt_table_offset()`.

## Dependency Context

The header includes `metadata-exported.h` and forward-declares most participating structs, keeping the interface lighter than the implementation. The API is still tightly coupled to LVM metadata concepts such as logical volumes, volume groups, LV segments, activation options, and target status objects.

## Important Invariants

- A `dev_manager` is scoped to a command context and VG name and uses an internal dm pool; many returned status objects refer to that pool.
- `track_pvmove_deps` at construction changes tree recursion behavior for pvmove operations.
- `dev_manager_suspend()` receives both lockfs and flush policy from `activate.c`; callers should not bypass the higher-level suspend logic unless they can supply those correctly.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/activate/dev_manager.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/activate/fs.c -->
# File Research: sources/block-storage/lvm2/lib/activate/fs.c

## Role

`fs.c` implements activation-private filesystem fallback operations for LVM device nodes and symlinks. Its main job is to maintain `/dev/<vg>/<lv>` symlinks to `/dev/mapper/<dm-name>` when udev is unavailable, incomplete, or configured for verification/fallback, and to synchronize those operations with libdevmapper udev cookies.

## Core Behavior

- `_mk_dir()` creates the VG directory under the configured device directory with the device-directory umask and SELinux context preparation.
- `_rm_dir()` removes an empty VG directory after LV symlink removal.
- `_rm_blks()` removes legacy block devices in a VG directory when cleaning up LVM1 device artifacts.
- `_mk_link()` creates or repairs the LV symlink, removes obsolete LVM1 group files and LVM2 links when safe, checks udev-created links when requested, and falls back to direct `symlink()`.
- `_rm_link()` removes an LV symlink after verifying it is actually a symlink.
- `_do_fs_op()` applies add, delete, or rename operations.

## Operation Stacking

When LVM is in a prioritized section, `_fs_op()` queues operations in `_fs_ops` instead of executing them immediately. `_stack_fs_op()` coalesces conflicting add/delete/rename operations, especially when udev is expected to create or remove links. `_pop_fs_ops()` later executes and frees all queued operations.

The file tracks counts by operation type in `_count_fs_ops` and uses `_other_fs_ops()` to decide whether pending non-delete operations exist. `fs_has_non_delete_ops()` exposes that state to activation code so open-count checks can wait for device names to settle.

## Udev Cookie Handling

- `_fs_cookie` starts as `DM_COOKIE_AUTO_CREATE` and is shared with libdevmapper tree operations.
- `fs_ensure_cookie()` creates a udev cookie only when udev sync is enabled and no cookie is active.
- `fs_get_cookie()` and `fs_set_cookie()` transfer cookie state between `fs.c` and `dev_manager.c`.
- `fs_unlock()` waits for udev processing when no devices are suspended, resets the cookie, releases libdm resources, and flushes stacked fs operations.
- `fs_set_create()` records that activation created nodes, causing `fs_has_non_delete_ops()` to report pending create-like work.

## Public Functions

- `fs_add_lv()`, `fs_del_lv()`, `fs_del_lv_byname()`, and `fs_rename_lv()` are the device-link operations used by `dev_manager.c`.
- `fs_ensure_cookie()`, `fs_get_cookie()`, `fs_set_cookie()`, `fs_set_create()`, `fs_has_non_delete_ops()`, and `fs_unlock()` coordinate with activation and libdm.

## Risks and Invariants

- Direct link creation/removal is intentionally conservative: existing non-symlink/non-block files block creation, and non-symlinks are not removed as LV links.
- Udev fallback correctness depends on checking the device number of the udev-created symlink target against the DM target path.
- Queued operation coalescing must preserve final filesystem state across prioritized sections; rename handling is explicitly marked as imperfect.
- `fs_unlock()` skips syncing while devices are suspended, preventing device-name synchronization from racing suspended tables.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/activate/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/activate/fs.h -->
# File Research: sources/block-storage/lvm2/lib/activate/fs.h

## Role

`fs.h` is the private header for activation filesystem fallback operations. It is intended for the activation unit rather than broad library consumers.

## Declared Interface

- `fs_add_lv()` creates the VG directory and LV symlink for a logical volume.
- `fs_del_lv()` removes an LV symlink and possibly the empty VG directory.
- `fs_del_lv_byname()` removes an LV symlink by explicit device directory, VG name, LV name, and udev-check policy.
- `fs_rename_lv()` handles old-to-new LV symlink transitions, including cross-VG rename as delete plus add.
- `fs_ensure_cookie()`, `fs_get_cookie()`, and `fs_set_cookie()` manage the shared udev cookie.
- `fs_set_create()` and `fs_has_non_delete_ops()` expose pending create/non-delete state.
- `fs_unlock()` is intentionally not declared here anymore; the comment notes it moved to `activate.h` to keep this private header hidden.

## Dependency Context

The header includes `lib/metadata/metadata.h`, so the filesystem operations can accept full `struct logical_volume` pointers and derive VG, command context, device directory, and udev settings.

## Invariants

- This header should stay private to activation/backend code; public callers should use activation-level APIs.
- Cookie APIs must remain consistent with `dev_manager.c` tree cookie transfer.
- Link operations assume LV and VG names have already been validated by metadata layers.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/activate/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/activate/targets.h -->
# File Research: sources/block-storage/lvm2/lib/activate/targets.h

## Role

`targets.h` is a small bridge header for segment target-line construction. It forward-declares the activation/device-manager and libdm tree types needed by target builders and exposes `add_areas_line()`.

## Interface

`add_areas_line(struct dev_manager *dm, struct lv_segment *seg, struct dm_tree_node *node, uint32_t start_area, uint32_t areas)` adds a range of LV segment areas to an in-progress DM tree node target line.

The implementation in `dev_manager.c` handles PV-backed areas, LV-backed areas, RAID data/metadata pairs, unassigned RAID areas, partial/degraded activation filler devices, and error handling for incomplete non-RAID/non-integrity segments.

## Dependency Context

This header avoids including full metadata or libdm headers by forward-declaring `struct dev_manager`, `struct lv_segment`, and `struct dm_tree_node`. Segment-type implementation files can include it to call the area builder without depending on the full `dev_manager.c` internals.

## Invariants

- The function assumes the caller has already created a compatible target on `node`.
- Segment type, area count, and metadata-area layout must match the target being generated.
- Partial/degraded activation policy is read through `seg->lv->vg->cmd`, so target builders must pass real metadata-backed segments.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/activate/targets.h -->