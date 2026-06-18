# Group Research: group_826_linux_sources_os_linux_linux_fs_resctrl_ctrlmondata_c_sources_os_lin_4702f66981c6

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/resctrl/ctrlmondata.c -->
# File Research: sources/os/linux/linux/fs/resctrl/ctrlmondata.c

## Purpose
Implements user-facing resctrl file handlers for control and monitor data: `schemata`, `mon_data/*` event files, `mba_MBps_event`, and `io_alloc`/`io_alloc_cbm`. It validates text written through kernfs, stages allocation changes, commits them through architecture hooks, and formats monitoring/control values back to userspace.

## Main Responsibilities
- Parse CAT/CDP cache bitmasks and MBA bandwidth values from `schemata`.
- Enforce sharing, exclusivity, and pseudo-locking overlap rules before committing CBMs.
- Display current schemata and pseudo-lock state.
- Read monitoring counters through `mon_event_read()` and print normal, unavailable, unassigned, error, or fixed-point values.
- Support MBA software-controller event selection.
- Support `io_alloc`, which reserves the highest CLOSID for I/O allocation and lets users configure its CBM.

## Key Types
- `struct rdt_parse_data`: carries `closid`, group mode, and current value text into parsers.
- `ctrlval_parser_t`: parser callback type used by `parse_line()`.
- `decplaces[]`: fixed-point decimal precision table for monitor events with binary fractional bits.

## Important Control Flow
- `rdtgroup_schemata_write()`:
  - Requires newline-terminated input.
  - Locks a live rdtgroup using `rdtgroup_kn_lock_live()`.
  - Rejects writes to already pseudo-locked groups.
  - Clears all staged configs, parses each `<resource>:<domain=value;...>` line, then calls `resctrl_arch_update_domains()` for non-MBA-SC resources.
  - If group is in `RDT_MODE_PSEUDO_LOCKSETUP`, calls `rdtgroup_pseudo_lock_create()` after staging one cache region.
- `parse_cbm()`:
  - Rejects duplicate domains, pseudo-lock hierarchy conflicts, invalid masks, overlap with pseudo-locked regions, overlap with exclusive groups, and illegal overlap for exclusive/pseudo-locksetup modes.
  - Stages the new CBM in `d->staged_config[s->conf_type]`.
- `parse_bw()`:
  - Validates MBA values with hardware limits/granularity unless MBA software controller is enabled.
  - In MBA-SC mode stores MBps target in `d->mbps_val[closid]` instead of staging MSR control values.
- `rdtgroup_mondata_show()`:
  - Resolves `struct mon_data` from `kn->priv`.
  - Handles normal domain reads and L3 SNC sum files.
  - Prints `Error`, `Unavailable`, `Unassigned`, integer values, or fixed-point values.
- `resctrl_io_alloc_write()`:
  - Parses a boolean enable value.
  - Reserves/frees the highest usable CLOSID.
  - Initializes CBMs for the reserved CLOSID and enables/disables architecture I/O allocation.
- `resctrl_io_alloc_cbm_write()`:
  - Parses `domain=mask` entries plus global `*=mask`.
  - Keeps CDP code/data peer CBMs synchronized for the I/O CLOSID.

## Dependencies and Integration
- Depends on `internal.h` for rdtgroup types, global schema list, last-command status helpers, monitor structures, and pseudo-locking declarations.
- Calls architecture hooks including `resctrl_arch_update_domains()`, `resctrl_arch_get_config()`, `resctrl_arch_io_alloc_enable()`, `resctrl_arch_mon_ctx_alloc/free()`, and monitor read hooks indirectly through `mon_event_count()`.
- Shares staged-domain workflow with `rdtgroup.c`.
- Integrates with `monitor.c` through `mon_event_count()` and MBM counter assignment state.

## Concurrency and Locking
- File writes and reads use `rdtgroup_kn_lock_live()` or explicit `cpus_read_lock()` plus `rdtgroup_mutex`.
- Domain-list walks assert CPU hotplug protection with `lockdep_assert_cpus_held()`.
- Monitor reads pick housekeeping CPUs where possible and use `smp_call_on_cpu()` or `smp_call_function_any()` depending on nohz/full and event constraints.

## Error Handling
- Writes consistently update `last_cmd_status` through `rdt_last_cmd_*()` before returning `-EINVAL`, `-ENOENT`, `-ENODEV`, or `-ENOSPC`.
- Monitoring counter read errors are intentionally translated to user-visible strings in event files.
- Staged configs are cleared on every exit path from schemata and I/O CBM writes.

## Research Notes
This file is the primary parser/formatter boundary for resctrl allocation control. The highest-risk behaviors are textual grammar compatibility, staged-config cleanup, pseudo-lock overlap checks, and interactions between MBA-SC, assignable MBM counters, and `io_alloc` CLOSID reservation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/resctrl/ctrlmondata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/resctrl/internal.h -->
# File Research: sources/os/linux/linux/fs/resctrl/internal.h

## Purpose
Private header for the Linux resctrl filesystem implementation. It defines shared in-kernel data structures, flags, helper prototypes, and pseudo-locking stubs used across `rdtgroup.c`, `ctrlmondata.c`, `monitor.c`, and `pseudo_lock.c`.

## Main Responsibilities
- Define resctrl filesystem context and kernfs-facing file descriptors.
- Define monitoring event metadata and per-file monitor private data.
- Define rdtgroup, mongroup, and RMID read state.
- Centralize rftype flags used to decide which files appear in which resctrl directories.
- Declare cross-file functions for schemata, monitor reads, MBA assignment controls, I/O allocation, CLOSID/RMID allocation, pseudo-locking, and file visibility.

## Key Types
- `struct rdt_fs_context`: mount option state for CDP, MBA MBps, and debug mode.
- `struct mon_evt`: monitor event descriptor, including event id, resource id, name, configuration mask, fixed-point formatting metadata, enable state, and architecture private data.
- `struct mon_data`: `kernfs_node->priv` payload for monitor event files; identifies resource, domain/cache id, event, and whether the file is a sum file.
- `struct rmid_read`: read request/result passed to `mon_event_count()` across local or remote CPU calls.
- `enum rdt_group_type`: distinguishes control groups from monitor-only groups.
- `enum rdtgrp_mode`: shareable, exclusive, pseudo-lock setup, and pseudo-locked group modes.
- `struct mongroup`: monitor-group state, parent relationship, child list, and RMID.
- `struct rdtgroup`: core resctrl group object with kernfs node, CLOSID, CPU mask, lifecycle flags, type, monitor state, mode, MBA event selection, and pseudo-lock region pointer.
- `struct rftype`: describes resctrl files, permissions, kernfs operations, visibility flags, show callback, and write callback.
- `struct mbm_state`: cached previous MBM bytes and computed bandwidth.

## Important Constants and Flags
- `CQM_LIMBOCHECK_INTERVAL`: RMID limbo scan period.
- `MAX_BINARY_BITS`: limit for fixed-point monitor-event fractional bits.
- `RDT_DELETED`: rdtgroup lifecycle flag used with `waitcount`.
- `RFTYPE_*`: visibility flags for top/info/base/control/monitor/cache/MB/debug/assignment/perf-package files.
- `RFTYPE_FLAGS_CPUS_LIST`: marks `cpus_list` formatting/parsing.

## Inline Helpers
- `cpumask_any_housekeeping()`: chooses a CPU from a mask, preferring non-`nohz_full` housekeeping CPUs and optionally excluding one CPU.
- `rdt_fc2context()`: converts `fs_context` to resctrl context.
- `rdt_kn_name()`: safely reads a kernfs node name under `rdtgroup_mutex`.

## Dependencies and Integration
- Includes `<linux/resctrl.h>`, kernfs, fs context, and tick/nohz support.
- Exposes `resctrl_schema_all`, `rdt_all_groups`, `rdtgroup_default`, `rdtgroup_mutex`, `max_name_width`, and `debugfs_resctrl`.
- Provides stubs for pseudo-locking when `CONFIG_RESCTRL_FS_PSEUDO_LOCK` is disabled, allowing the rest of resctrl to compile without feature guards at every call site.

## Research Notes
This header is the internal contract for the resctrl filesystem. Most correctness constraints in the implementation depend on these structures being consistently interpreted across allocation control, monitor accounting, mount lifecycle, and pseudo-locking.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/resctrl/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/resctrl/monitor.c -->
# File Research: sources/os/linux/linux/fs/resctrl/monitor.c

## Purpose
Implements resctrl monitoring internals: RMID allocation and limbo recycling, CQM/LLC occupancy cleanup, MBM bandwidth accounting, MBA software-controller feedback, configurable MBM event filters, assignable MBM counters, and monitoring resource initialization/teardown.

## Main Responsibilities
- Maintain global RMID free/limbo state.
- Track dirty RMIDs until LLC occupancy falls below the reallocation threshold.
- Read L3 and package monitoring events and aggregate child monitor groups.
- Periodically refresh MBM counters and compute MBps.
- Adjust MBA throttling in software-controller mode.
- Manage assignable MBM hardware counters and event transaction filters.
- Initialize monitor event metadata and per-domain state.

## Key Types and State
- `struct rmid_entry`: tracks one CLOSID/RMID pair or RMID index, busy-domain count, and free-list membership.
- `rmid_free_lru`: LRU list of clean/free RMIDs.
- `closid_num_dirty_rmid`: per-CLOSID dirty RMID count for architectures where RMID depends on CLOSID.
- `rmid_limbo_count`: count of unused but dirty RMIDs.
- `rmid_ptrs`: indexed RMID entry table.
- `resctrl_rmid_realloc_threshold`: occupancy threshold below which RMID can be reused.
- `resctrl_rmid_realloc_limit`: maximum allowed threshold.
- `mon_event_all[]`: global table of supported monitor events, enabled/configured by architecture code.

## Important Control Flow
- RMID allocation:
  - `setup_rmid_lru_list()` allocates `rmid_ptrs`, initializes all entries as free, and reserves the default RMID.
  - `alloc_rmid()` gets a compatible free entry for a CLOSID.
  - `free_rmid()` either adds the entry to limbo if LLC occupancy monitoring is enabled or returns it directly to free LRU.
- Limbo recycling:
  - `add_rmid_to_limbo()` marks the RMID busy in every L3 monitor domain and schedules `cqm_limbo`.
  - `__check_limbo()` reads LLC occupancy for busy RMIDs and releases clean entries.
  - `cqm_handle_limbo()` repeats scans until no busy RMIDs remain.
- Counter reads:
  - `__l3_mon_event_count()` reads one L3 domain or resets counters on first initialization.
  - `__l3_mon_event_count_sum()` sums SNC domains sharing one L3 cache id.
  - `__mon_event_count()` dispatches by resource id.
  - `mon_event_count()` also adds child monitor-group counts for control groups.
- MBM/MBA:
  - `mbm_update_one_event()` reads MBM events and updates bandwidth state.
  - `mbm_handle_overflow()` periodically updates all groups and optionally calls `update_mba_bw()`.
  - `update_mba_bw()` compares measured bandwidth against user target and adjusts MBA MSR values by hardware granularity.
- Assignable counters:
  - `mbm_cntr_get/alloc/free()` manage per-domain counter slots.
  - `rdtgroup_assign_cntrs()` assigns default MBM counters for new groups when enabled.
  - `rdtgroup_unassign_cntrs()` releases counters on group deletion.
  - `mbm_L3_assignments_show/write()` exposes per-event/per-domain assignment state.
- Event filters:
  - `event_filter_show/write()` displays and updates memory transaction masks for configurable MBM events.
  - Changes are propagated to existing assigned counters through `resctrl_update_cntr_allrdtgrp()`.

## Dependencies and Integration
- Includes `monitor_trace.h` and defines tracepoints for RMID limbo occupancy reads.
- Called by `rdtgroup.c` for mount init, domain hotplug, group creation/deletion, and info-file handlers.
- Called by `ctrlmondata.c` indirectly through `mon_event_read()` and `mon_event_count()`.
- Relies on architecture hooks for RMID indexing, monitor context allocation, RMID/counter reads, counter resets, and counter configuration.

## Concurrency and Locking
- RMID, counter assignment, and group traversal require `rdtgroup_mutex`.
- Domain list traversal also requires CPU hotplug protection where noted.
- Delayed workers take `cpus_read_lock()` and `rdtgroup_mutex`.
- Work scheduling avoids nohz_full CPUs where possible via `cpumask_any_housekeeping()`.

## Error Handling
- RMID allocation distinguishes `-EBUSY` dirty-RMID pressure from `-ENOSPC` exhaustion.
- Monitor context allocation failures are rate-limited warnings.
- Assignable counter read without assignment uses `-ENOENT`, later rendered as `Unassigned`.
- Event filter parsing reports invalid transaction names through `last_cmd_status`.

## Research Notes
This file is the resource-accounting core of resctrl monitoring. The important invariants are RMID lifecycle correctness, matching CLOSID/RMID indexing across architectures, delayed-work cancellation on hotplug/unmount, and consistency between assignable counter mode and legacy BMEC configuration files.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/resctrl/monitor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/resctrl/monitor_trace.h -->
# File Research: sources/os/linux/linux/fs/resctrl/monitor_trace.h

## Purpose
Defines the resctrl tracepoint used when checking dirty RMIDs in LLC occupancy limbo.

## Main Trace Event
- `mon_llc_occupancy_limbo`
  - Arguments: `ctrl_hw_id`, `mon_hw_id`, `domain_id`, `llc_occupancy_bytes`.
  - Emitted from `monitor.c::__check_limbo()` after a successful LLC occupancy read.
  - Helps diagnose why RMIDs remain dirty or become reusable.

## Integration
- `TRACE_SYSTEM` is `resctrl`.
- `TRACE_INCLUDE_PATH` is local directory and `TRACE_INCLUDE_FILE` is `monitor_trace`.
- Included by `monitor.c` after `#define CREATE_TRACE_POINTS`.

## Research Notes
This file is small but important for observability of RMID recycling. It does not alter behavior; it provides a stable trace schema for monitoring limbo occupancy decisions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/resctrl/monitor_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/resctrl/pseudo_lock.c -->
# File Research: sources/os/linux/linux/fs/resctrl/pseudo_lock.c

## Purpose
Implements resctrl cache pseudo-locking support. A resctrl group can be placed into pseudo-lock setup mode, configured with a CAT CBM, locked into cache by an architecture-specific thread, and exposed to userspace through a character device and debugfs measurement hook.

## Main Responsibilities
- Allocate and initialize pseudo-lock regions.
- Restrict group files while pseudo-lock setup is in progress.
- Validate that pseudo-locking is allowed for the group and platform.
- Prevent overlapping pseudo-locked regions in a cache hierarchy.
- Constrain CPU low-power states while a region is locked.
- Create/destroy pseudo-lock character devices.
- Provide NOMMU-style `mmap_prepare` mapping of the locked kernel buffer.
- Provide debugfs-triggered latency/residency measurements.

## Key State
- `pseudo_lock_major`: shared char-device major number.
- `pseudo_lock_minor_avail`: bitmap of available pseudo-lock minors.
- `pseudo_lock_class`: device class named `pseudo_lock`, with devnodes under `pseudo_lock/<group>`.
- `struct pseudo_lock_pm_req`: PM QoS request list entry used to constrain C-states for CPUs in the cache domain.

## Important Control Flow
- Setup entry:
  - `rdtgroup_locksetup_enter()` rejects default group, CDP-enabled systems, unsupported prefetch-disable platforms, existing monitoring, assigned tasks, or assigned CPUs.
  - Restricts `tasks`, `cpus`, `cpus_list`, and optionally `mon_groups`.
  - Allocates `rdtgrp->plr` and frees the group RMID because pseudo-lock groups cannot monitor.
- Setup exit:
  - `rdtgroup_locksetup_exit()` allocates a new RMID if monitoring is supported, restores file permissions, and frees the pseudo-lock region.
- Region creation:
  - `rdtgroup_pseudo_lock_create()` initializes region size/line size/CPU, allocates contiguous kernel memory, adds PM QoS constraints, runs `resctrl_arch_pseudo_lock_fn()` on the target CPU, allocates a minor, creates debugfs and device nodes, switches mode to `RDT_MODE_PSEUDO_LOCKED`, and frees the CLOSID.
- Region removal:
  - `rdtgroup_pseudo_lock_remove()` handles both setup and locked states, removing QoS constraints, debugfs, char device, minor allocation, CLOSID, and region memory.
- Mapping:
  - `pseudo_lock_dev_open()` finds a region by minor and increments rdtgroup waitcount.
  - `pseudo_lock_dev_mmap_prepare()` requires the caller affinity to be a subset of the cache-domain CPUs, requires shared mapping, validates offsets/lengths, zeroes the mapped bytes, and remaps the physical backing buffer.
- Measurements:
  - `pseudo_lock_measure_trigger()` accepts selector `1`, `2`, or `3`.
  - `pseudo_lock_measure_cycles()` runs architecture latency/L2/L3 residency measurement functions on a CPU in the locked domain.

## Dependencies and Integration
- Called from `rdtgroup.c` mode transitions, removal paths, and resctrl init/exit.
- Called from `ctrlmondata.c` schemata parsing/commit path when group mode is `RDT_MODE_PSEUDO_LOCKSETUP`.
- Uses architecture hooks for pseudo-lock execution, prefetch-disable detection, and measurements.
- Uses cacheinfo to derive cache line size and region size.

## Concurrency and Locking
- Uses `rdtgroup_mutex` for group lookup, state changes, and char-device open/release.
- Temporarily releases `rdtgroup_mutex` around debugfs/device creation to avoid lock ordering problems with mmap and filesystem locks.
- Uses `waitcount` and `RDT_DELETED` to keep rdtgroups alive while devices or kernfs operations hold references.

## Error Handling
- Writes descriptive `last_cmd_status` messages for unsupported platform state, allocation failure, invalid group state, device creation failure, and interrupted locking thread.
- Creation failure unwinds in reverse order: device/debugfs/minor, PM QoS, region data.
- If CPU/domain disappears, user-visible operations return `-ENODEV`.

## Research Notes
Pseudo-locking has strong cross-file coupling: `rdtgroup.c` controls mode and group lifetime, `ctrlmondata.c` supplies the validated CBM, and this file owns the locking/mapping/device mechanics. The main risks are teardown races, CPU hotplug, permission restoration, and deadlock avoidance around device/debugfs creation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/resctrl/pseudo_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/resctrl/rdtgroup.c -->
# File Research: sources/os/linux/linux/fs/resctrl/rdtgroup.c

## Purpose
Implements the resctrl filesystem: mount lifecycle, kernfs tree construction, resource group creation/removal/rename, CLOSID allocation, task/CPU assignment, mode changes, info files, monitor-data directories, CPU/domain hotplug handling, and top-level initialization/exit.

## Main Responsibilities
- Register and manage the `resctrl` filesystem.
- Build the root group, info directories, monitor directories, and per-group files.
- Track all rdtgroups and the global schema list.
- Allocate/free CLOSIDs for control groups.
- Move tasks and CPUs between control and monitor groups.
- Implement group modes: shareable, exclusive, pseudo-locksetup, pseudo-locked.
- Initialize default CAT/MBA allocations for new groups.
- Handle mount options: `cdp`, `cdpl2`, `mba_MBps`, and `debug`.
- Create/remove monitor event files for each domain and group.
- Handle CPU and domain online/offline callbacks.
- Coordinate teardown on unmount or fatal architecture exit.

## Key Global State
- `rdtgroup_mutex`: protects rdtgroup filesystem state.
- `rdt_root`: kernfs root.
- `rdtgroup_default`: root/default control group.
- `rdt_all_groups`: list of all control groups.
- `resctrl_schema_all`: active allocation schemas.
- `mon_data_kn_priv_list`: shared `struct mon_data` instances for monitor files.
- `resctrl_mounted`: single-mount guard.
- `kn_info`, `kn_mongrp`, `kn_mondata`: key root kernfs nodes.
- `max_name_width`: schemata display formatting width.
- `last_cmd_status`: last user-command status buffer.
- `debugfs_resctrl`: debugfs root for resctrl pseudo-lock measurement files.
- `mba_mbps_default_event`: default MBM event used by MBA software controller.

## Important Control Flow
- Mount:
  - `rdt_get_tree()` enforces single mount, sets up RMID LRU, root kernfs tree, mount options, schema list, CLOSID bitmap, base files, info files, monitor directories, pseudo-lock device support, and delayed MBM overflow workers.
  - Enables architecture allocation/monitoring after kernfs tree creation succeeds.
- Unmount:
  - `rdt_kill_sb()` disables mount context, resets architecture controls, tears down filesystem state, disables allocation/monitoring, clears `resctrl_mounted`, and kills kernfs superblock.
- Files:
  - `res_common_files[]` is the central file table. It maps names, permissions, flags, show callbacks, and write callbacks for all info/base/control/monitor/debug files.
  - `rdtgroup_add_files()` filters this table by `RFTYPE_*` flags.
- CLOSIDs:
  - `closid_init()` computes the minimum CLOSID count across enabled schemas and reserves CLOSID 0 for the default group.
  - `closid_alloc()` optionally chooses the cleanest CLOSID when RMIDs depend on CLOSID.
  - `closid_free()`, `closid_allocated()`, and `closid_alloc_fixed()` manage the bitmap.
- CPU assignment:
  - `rdtgroup_cpus_write()` parses CPU masks/lists, rejects offline CPUs and pseudo-lock groups, then dispatches to control or monitor group handling.
  - Control groups return dropped CPUs to default and clear child monitor masks when parent membership changes.
  - Monitor groups can only use CPUs that belong to their parent control group.
- Task assignment:
  - `rdtgroup_tasks_write()` parses comma-separated PIDs.
  - Permission checks require root or task owner/saved owner.
  - Monitor groups cannot move tasks across control-group CLOSID boundaries.
  - Current tasks get immediate architecture state updates.
- Modes:
  - `rdtgroup_mode_write()` supports `shareable`, `exclusive`, and `pseudo-locksetup`; `pseudo-locked` is reached only after pseudo-lock creation.
  - Exclusive mode verifies no CBM overlap with other allocations.
  - Pseudo-locksetup delegates entry/exit to `pseudo_lock.c`.
- Info and monitor tree:
  - `rdtgroup_create_info_dir()` creates `info`, allocation resource dirs, and monitor resource dirs.
  - `mkdir_mondata_all()` creates per-group `mon_data` and per-domain event files.
  - SNC L3 systems create sum directories plus `mon_sub_*` domain directories.
- Group creation/removal:
  - `rdtgroup_mkdir_ctrl_mon()` creates top-level control+monitor groups, allocates CLOSID/RMID, initializes allocations, and adds `mon_groups`.
  - `rdtgroup_mkdir_mon()` creates monitor-only child groups under `mon_groups`.
  - `rdtgroup_rmdir_ctrl()` and `rdtgroup_rmdir_mon()` move tasks/CPUs back, update per-CPU defaults/MSRs, unassign counters, free RMIDs/CLOSIDs, and remove kernfs nodes.
  - `rdtgroup_rename()` supports moving monitor groups between parents when they are not monitoring CPUs.
- Domain/CPU hotplug:
  - `resctrl_online_ctrl_domain()` allocates MBA-SC per-domain state.
  - `resctrl_online_mon_domain()` allocates L3 monitor state, starts delayed workers, and creates monitor-data directories if mounted.
  - `resctrl_offline_mon_domain()` removes domain monitor directories, cancels delayed work, force-cleans busy RMIDs if needed, and frees domain monitor state.
  - `resctrl_online_cpu()` adds CPUs to default group; `resctrl_offline_cpu()` removes CPUs from groups and reschedules delayed work away from the offline CPU.

## Dependencies and Integration
- `ctrlmondata.c` supplies schemata, monitor-data display, MBA event, and I/O allocation file handlers referenced in `res_common_files[]`.
- `monitor.c` supplies RMID lifecycle, MBM assignment, monitor init/exit, and delayed work handlers.
- `pseudo_lock.c` supplies pseudo-lock mode entry/exit/create/remove and device lifecycle.
- Relies on architecture hooks for CDP, CLOSID/RMID scheduling state, control MSR updates, monitor capability, domain resources, and enable/disable operations.

## Concurrency and Lifetime
- Most operations use `rdtgroup_kn_lock_live()`/`rdtgroup_kn_unlock()` to combine kernfs active-reference handling, CPU hotplug protection, and `rdtgroup_mutex`.
- `waitcount` and `RDT_DELETED` protect rdtgroup memory while files/devices are still open.
- `rdtgroup_kn_get()` breaks kernfs active protection before taking global locks; `rdtgroup_kn_put()` restores it and frees deleted groups when references drain.

## Error Handling
- User-facing failures are usually recorded in `last_cmd_status`.
- Mount has structured unwind labels for pseudo-lock, monitor-data, mon_groups, info, CLOSID, schema, mount context, and root teardown.
- Group creation carefully unwinds kernfs nodes, RMIDs, CLOSIDs, counters, and list membership.
- Teardown forcibly moves all tasks and CPUs back to default state.

## Research Notes
This is the central orchestrator for resctrl. Its correctness depends on consistent lock ordering, kernfs lifetime handling, architecture-hook behavior, and strict separation between control groups and monitor groups. It is also where feature visibility is decided, so adding a new resctrl file usually requires changes to `res_common_files[]` and feature flag initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/resctrl/rdtgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/romfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/romfs/Kconfig

## Purpose
Defines Kconfig options for Linux ROMFS support and its backing-store choices.

## Main Configuration
- `ROMFS_FS`
  - Tristate option: "ROM file system support".
  - Depends on `BLOCK || MTD`.
  - Builds module named `romfs` when selected as module.
  - Described as a small read-only filesystem for init/install media and other read-only storage.

## Backing Store Choice
The `choice` block is visible when `ROMFS_FS` is enabled:
- `ROMFS_BACKED_BY_BLOCK`
  - Block-device backed ROMFS.
  - Depends on `BLOCK`.
  - Uses page-cache/block buffering and does not support direct mapping.
- `ROMFS_BACKED_BY_MTD`
  - MTD-backed ROMFS.
  - Depends on built-in MTD or module-compatible MTD.
  - Supports direct MTD access and, under NOMMU, direct mapping when CPU-addressable.
- `ROMFS_BACKED_BY_BOTH`
  - Enables both block and MTD paths.
  - Depends on both block support and compatible MTD support.

## Derived Options
- `ROMFS_ON_BLOCK`
  - Internal bool.
  - Defaults to `y` for block or both.
  - Selects `BUFFER_HEAD`.
- `ROMFS_ON_MTD`
  - Internal bool.
  - Defaults to `y` for MTD or both.

## Research Notes
This file controls which code paths in `storage.c` and `mmap-nommu.c` are compiled. The build requires at least one backing-store interface, enforced again by `storage.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/romfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/romfs/Makefile -->
# File Research: sources/os/linux/linux/fs/romfs/Makefile

## Purpose
Build rules for the Linux ROMFS filesystem module/built-in object.

## Build Behavior
- `obj-$(CONFIG_ROMFS_FS) += romfs.o`: builds ROMFS when configured.
- `romfs-y := storage.o super.o`: core ROMFS object always includes storage access and superblock/inode logic.
- `romfs-$(CONFIG_ROMFS_ON_MTD) += mmap-nommu.o` only when `CONFIG_MMU` is not `y`.

## Integration
The Makefile mirrors Kconfig:
- `storage.o` handles block and/or MTD reads according to `ROMFS_ON_BLOCK` and `ROMFS_ON_MTD`.
- `mmap-nommu.o` is included only for NOMMU MTD direct-map support.

## Research Notes
This is a minimal feature-gated build file. Direct mmap support is intentionally absent on MMU builds.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/romfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/romfs/internal.h -->
# File Research: sources/os/linux/linux/fs/romfs/internal.h

## Purpose
Private ROMFS header defining inode-private state, convenience helpers, and internal storage/mmap declarations.

## Key Types
- `struct romfs_inode_info`
  - Embeds `struct inode vfs_inode`.
  - `i_metasize`: size of non-data inode metadata.
  - `i_dataoffset`: byte offset of file data from filesystem start.

## Helpers
- `romfs_maxsize(sb)`: returns maximum image size from `sb->s_fs_info`.
- `ROMFS_I(inode)`: converts a VFS inode to `struct romfs_inode_info`.

## Declarations
- `romfs_ro_fops`
  - Uses NOMMU MTD-specific implementation when `!CONFIG_MMU && CONFIG_ROMFS_ON_MTD`.
  - Otherwise aliases to `generic_ro_fops`.
- Storage helpers from `storage.c`:
  - `romfs_dev_read()`
  - `romfs_dev_strnlen()`
  - `romfs_dev_strcmp()`

## Research Notes
This header is the narrow internal API between ROMFS superblock/inode code, storage access, and optional NOMMU MTD mmap support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/romfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/romfs/mmap-nommu.c -->
# File Research: sources/os/linux/linux/fs/romfs/mmap-nommu.c

## Purpose
Provides NOMMU direct-mapping support for ROMFS files stored on MTD devices.

## Main Responsibilities
- Determine whether a ROMFS file mapping can be directly mapped through the underlying MTD device.
- Validate mapping offsets and lengths against file size and MTD size.
- Expose file operations that support NOMMU mapping capabilities.

## Important Control Flow
- `romfs_get_unmapped_area()`:
  - Requires an MTD-backed superblock.
  - Rejects mappings beyond EOF, nonzero requested addresses, offsets beyond MTD size, and ranges outside the MTD.
  - Adds the ROMFS inode data offset to the file offset.
  - Delegates to `mtd_get_unmapped_area()`.
  - Translates `-EOPNOTSUPP` to `-ENOSYS`.
- `romfs_mmap_prepare()`:
  - Allows only NOMMU shared mappings.
  - Rejects private/copy mappings with `-ENOSYS`.
- `romfs_mmap_capabilities()`:
  - Returns `NOMMU_MAP_COPY` without MTD.
  - Otherwise delegates to `mtd_mmap_capabilities()`.

## Exported Object
- `const struct file_operations romfs_ro_fops`
  - Read-only file operations with llseek, read_iter, splice_read, mmap_prepare, get_unmapped_area, and mmap_capabilities.

## Dependencies and Integration
- Compiled only on NOMMU MTD ROMFS builds.
- Uses `ROMFS_I(inode)->i_dataoffset` from `internal.h`.
- Used by ROMFS regular files through `romfs_ro_fops`.

## Research Notes
The file is intentionally limited to direct mappings that the MTD layer can support safely. It prevents mappings outside the ROMFS file or backing MTD range.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/romfs/mmap-nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/romfs/storage.c -->
# File Research: sources/os/linux/linux/fs/romfs/storage.c

## Purpose
Implements low-level ROMFS image access for MTD and block-device backing stores. It provides bounded read, string length, and string compare helpers used by ROMFS metadata parsing.

## Main Responsibilities
- Read arbitrary byte ranges from a ROMFS image.
- Compute bounded NUL-terminated string lengths inside the image.
- Compare a supplied filename string against an image string and verify its terminating NUL.
- Dispatch to MTD or block-device implementations depending on superblock backing.

## MTD Path
Compiled under `CONFIG_ROMFS_ON_MTD`:
- `romfs_mtd_read()`
  - Calls `mtd_read()` and requires the exact requested length.
- `romfs_mtd_strnlen()`
  - Reads up to 16 bytes at a time and searches for NUL.
- `romfs_mtd_strcmp()`
  - Reads up to 17 bytes at a time to compare data plus trailing NUL.

## Block Path
Compiled under `CONFIG_ROMFS_ON_BLOCK`:
- `romfs_blk_read()`
  - Reads block-sized segments through `sb_bread()`, copies from buffer heads, and releases them.
- `romfs_blk_strnlen()`
  - Scans block segments for NUL using buffer heads.
- `romfs_blk_strcmp()`
  - Compares block segments and verifies trailing NUL either in the same block or first byte of the next block.

## Public Internal API
- `romfs_dev_read(sb, pos, buf, buflen)`
  - Bounds-checks against `romfs_maxsize(sb)`.
  - Dispatches to MTD when `sb->s_mtd` is present or block when `sb->s_bdev` is present.
- `romfs_dev_strnlen(sb, pos, maxlen)`
  - Bounds-checks and clamps max length to remaining image size.
- `romfs_dev_strcmp(sb, pos, str, size)`
  - Rejects names larger than `ROMFS_MAXFN`.
  - Requires room for trailing NUL.
  - Dispatches to matching backing store.

## Error Handling
- Returns `-EIO` for out-of-range image reads, missing backing store, failed block reads, short MTD reads, or insufficient room for required data.
- Returns `-ENAMETOOLONG` for filename compare sizes greater than `ROMFS_MAXFN`.
- String compare returns `1` for match, `0` for mismatch, and negative errno on read/bounds error.

## Research Notes
This file is the storage abstraction for ROMFS metadata and file reads. Its main invariants are strict image bounds, exact-length MTD reads, buffer-head release on every block path, and correct NUL verification across block boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/romfs/storage.c -->