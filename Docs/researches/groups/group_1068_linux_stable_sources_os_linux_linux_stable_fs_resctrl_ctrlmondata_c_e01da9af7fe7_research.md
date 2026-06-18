# Group Research: group_1068_linux_stable_sources_os_linux_linux_stable_fs_resctrl_ctrlmondata_c_e01da9af7fe7

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/ctrlmondata.c -->
# File Research: sources/os/linux/linux-stable/fs/resctrl/ctrlmondata.c

Implements resctrl user-facing data file handlers for allocation schemata, monitor data reads, MBA MBps event selection, and `io_alloc` controls.

Key responsibilities:
- Parses `schemata` writes by resource/domain pairs, validating MBA bandwidth values and cache CBMs against hardware limits, sparse-mask support, minimum CBM width, exclusive groups, and pseudo-locked regions.
- Stages per-domain updates in `staged_config`, then commits non-MBA-SC controls through `resctrl_arch_update_domains()`.
- Handles pseudo-lock setup by accepting one valid cache CBM, attaching resource/domain/CBM state to `rdtgrp->plr`, and invoking `rdtgroup_pseudo_lock_create()`.
- Shows schemata and allocation sizes for normal groups, pseudo-lock setup groups, and completed pseudo-locked groups.
- Reads monitor event files through `mon_event_read()`, including summed L3 SNC views, any-CPU events, architecture monitor contexts, and fixed-point formatting.
- Implements user selection of the MBA software-controller input event between `mbm_local_bytes` and `mbm_total_bytes`.
- Implements cache `io_alloc` enablement and CBM configuration using the highest available CLOSID, with CDP peer CBMs kept in sync.

Important dependencies:
- Uses `rdtgroup_kn_lock_live()`/`rdtgroup_kn_unlock()` to combine kernfs lifetime, `cpus_read_lock()`, and `rdtgroup_mutex`.
- Calls `rdtgroup_cbm_overlaps()`, pseudo-lock helpers, CLOSID helpers, and architecture hooks from the wider resctrl subsystem.
- Relies on `mon_event_all[]`, `struct mon_data`, and `struct rmid_read` from `internal.h`/`monitor.c`.

Notable invariants:
- User writes to newline-sensitive files require a trailing newline.
- Duplicate domain entries in a write are rejected.
- MBA software-controller writes update `mbps_val[]` targets instead of directly staging hardware controls.
- Pseudo-locked groups cannot have schemata modified in place.
- `io_alloc` reserves a fixed highest CLOSID and refuses enablement if that CLOSID is already used by a group.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/ctrlmondata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/resctrl/internal.h

Shared private header for the resctrl filesystem implementation.

Key definitions:
- `struct rdt_fs_context`: mount option state for CDP, MBA software controller, and debug mode.
- `struct mon_evt`, `struct mon_data`, and `struct rmid_read`: monitor event metadata, kernfs event-file private data, and cross-CPU monitor-read request state.
- `enum rdt_group_type` and `enum rdtgrp_mode`: distinguish control/monitor groups and shareable, exclusive, pseudo-lock setup, and pseudo-locked modes.
- `struct mongroup` and `struct rdtgroup`: core in-memory group state, including kernfs node, CLOSID, RMID, CPU mask, child monitor groups, mode, MBA event, and pseudo-lock region.
- `struct rftype`: central descriptor for each resctrl kernfs file, including visibility flags and callbacks.
- `struct mbm_state`: cached MBM bandwidth state for delta MBps calculations.

Shared APIs:
- Declares schemata, monitoring, CLOSID/RMID, pseudo-lock, file visibility, BMEC, MBM assignment, and `io_alloc` helpers used across `rdtgroup.c`, `ctrlmondata.c`, `monitor.c`, and `pseudo_lock.c`.
- Provides pseudo-lock stubs when `CONFIG_RESCTRL_FS_PSEUDO_LOCK` is disabled.
- Provides `cpumask_any_housekeeping()` to prefer non-`nohz_full` CPUs for monitor work and IPIs.

Notable invariants:
- Most declared helpers assume `rdtgroup_mutex` is held.
- Domain walks commonly require CPU hotplug protection.
- `MAX_BINARY_BITS` bounds fixed-point monitor event formatting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/monitor.c -->
# File Research: sources/os/linux/linux-stable/fs/resctrl/monitor.c

Implements resctrl monitoring state, RMID allocation/reclaim, MBM bandwidth accounting, overflow and limbo workers, monitor event registration, and assignable MBM counter policy.

Key responsibilities:
- Maintains RMID free LRU and limbo state using `struct rmid_entry`; supports architectures where monitor identity depends on both CLOSID and RMID.
- Reclaims limbo RMIDs by reading LLC occupancy and freeing entries once occupancy drops below `resctrl_rmid_realloc_threshold`.
- Allocates RMIDs, frees them into limbo when occupancy monitoring is enabled, and finds a cleanest CLOSID for MPAM-like architectures.
- Reads L3 occupancy/MBM and PERF_PKG events; sums child monitor groups into parent control groups.
- Keeps per-RMID MBM state and computes MBps deltas on overflow intervals.
- Runs MBA software-controller feedback by comparing measured MBM bandwidth with user MBps targets and adjusting MBA throttle controls.
- Registers available monitor events in `mon_event_all[]`, with architecture enablement through `resctrl_enable_mon_event()`.
- Implements BMEC/event-filter display and writes for configurable MBM event transactions.
- Implements `mbm_assign_mode`, `mbm_assign_on_mkdir`, counter availability, and per-group `mbm_L3_assignments`.

Important workflows:
- `setup_rmid_lru_list()` allocates global RMID entries on mount and reserves the default RMID.
- `cqm_handle_limbo()` periodically scans dirty RMIDs for one L3 domain and reschedules while busy entries remain.
- `mbm_handle_overflow()` periodically updates MBM counters for all groups and child monitor groups, then optionally updates MBA software control.
- Assignable-counter mode clears software RMID state and hardware counter assignment state when toggled.
- Counter assignment writes use `e` and `_` states per event/domain, with `*` accepted for all domains.

Notable invariants:
- RMID and counter assignment state is protected by `rdtgroup_mutex`.
- Overflow and limbo work prefers housekeeping CPUs and migrates away from `nohz_full` CPUs.
- In MBM counter-assignment mode, unassigned counters are reported to userspace as `Unassigned`.
- Event configuration changes reset affected software MBM state so future bandwidth deltas do not mix incompatible counter definitions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/monitor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/monitor_trace.h -->
# File Research: sources/os/linux/linux-stable/fs/resctrl/monitor_trace.h

Defines the resctrl tracepoint header for monitor limbo accounting.

Key element:
- `TRACE_EVENT(mon_llc_occupancy_limbo)` records `ctrl_hw_id`, `mon_hw_id`, domain id, and LLC occupancy bytes while limbo RMIDs are checked.

Usage:
- Included by `monitor.c` with `CREATE_TRACE_POINTS`.
- Emitted from `__check_limbo()` after LLC occupancy reads.

Purpose:
- Provides observability into why RMIDs remain dirty or become reusable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/monitor_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/pseudo_lock.c -->
# File Research: sources/os/linux/linux-stable/fs/resctrl/pseudo_lock.c

Implements cache pseudo-locking support for resctrl control groups.

Key responsibilities:
- Converts an eligible empty control group into pseudo-lock setup mode, then into a pseudo-locked cache-resident memory region after a valid schemata write.
- Allocates and initializes `struct pseudo_lock_region`, computes region size from CBM/cache metadata, allocates backing kernel memory, and runs architecture pseudo-locking code on a CPU in the target cache domain.
- Prevents unsafe setup when the group is default, CDP is enabled, prefetch-disable support is absent, monitoring is active, tasks are assigned, or CPUs are assigned.
- Restricts and restores user access to `tasks`, `cpus`, `cpus_list`, and `mon_groups` during setup.
- Tracks pseudo-lock device minors and exposes each completed region as `/dev/pseudo_lock/<group>`.
- Creates optional debugfs measurement trigger for latency and cache residency measurements.
- Enforces character-device mmap constraints: target domain must still exist, current task affinity must be subset of the pseudo-locked domain CPUs, mapping must be shared, and bounds must fit the region.

Important cleanup:
- Removal relaxes PM QoS C-state constraints, removes debugfs files, destroys the device, releases the minor, frees the region, and frees CLOSID/RMID state as appropriate.
- Domain overlap helpers prevent new CBMs from overlapping existing pseudo-locked cache portions or cache hierarchy conflicts.

Notable invariants:
- Pseudo-lock setup frees the group RMID because monitoring is not allowed.
- Completed pseudo-locked groups free their CLOSID because tasks/CPUs no longer use that CLOSID.
- mmap is deliberately non-seekable and rejects private copy-on-write mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/pseudo_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/rdtgroup.c -->
# File Research: sources/os/linux/linux-stable/fs/resctrl/rdtgroup.c

Main resctrl filesystem implementation. It owns global group state, kernfs file layout, mount/unmount, group creation/removal, CPU/task assignment, schema creation, info files, monitor-data directories, and CPU/domain hotplug integration.

Key responsibilities:
- Defines `rdtgroup_mutex`, `rdtgroup_default`, `rdt_all_groups`, `resctrl_schema_all`, mount state, info/monitor kernfs nodes, `last_cmd_status`, and debugfs root.
- Implements CLOSID allocation using a global bitmap, with cleanest-CLOSID selection when RMID state depends on CLOSID.
- Implements user-visible `last_cmd_status` accumulation for write errors.
- Provides kernfs operation wrappers for common resctrl files and `mon_data` event files.
- Handles `cpus`/`cpus_list` writes for control groups and monitor groups, moving CPUs between groups and updating architecture CLOSID/RMID state.
- Handles `tasks` writes and task migration with permission checks, CLOSID/RMID update ordering, and immediate update of current tasks through IPIs when needed.
- Provides `/proc` resctrl display when enabled.
- Provides info-file readers for CLOSIDs, RMIDs, monitor features, cache masks, bit usage, MBA properties, thread throttle mode, and threshold occupancy.
- Implements group modes and transitions between shareable, exclusive, pseudo-lock setup, and pseudo-locked, including CBM overlap tests.
- Implements MBM event configuration files and BMEC visibility controls.
- Defines `res_common_files[]`, the central table of resctrl files and callbacks.
- Builds the `info` tree and per-resource/monitor info directories based on resource capability flags.
- Parses mount options `cdp`, `cdpl2`, `mba_MBps`, and `debug`, then enables architecture context and builds schemas on mount.
- Sets up root, info, `mon_groups`, `mon_data`, pseudo-lock device class, and allocation/monitoring architecture state in `rdt_get_tree()`.
- Tears down groups, resets controls, releases pseudo-lock, and disables architecture state in `rdt_kill_sb()` and `resctrl_exit()`.

Group lifecycle:
- Control groups are created under root, receive a CLOSID, optional RMID, default CAT/MBA allocations, `mon_groups`, and `mon_data`.
- Monitor groups are created only under a parent `mon_groups` directory, share the parent CLOSID, receive their own RMID, and get `mon_data`.
- Removal moves tasks/CPUs back to parent/default groups, updates CPU defaults/MSRs, unassigns counters, frees RMID/CLOSID, removes kernfs nodes, and handles open references through `waitcount`/`RDT_DELETED`.
- Monitor groups can be renamed or reparented if they do not monitor CPUs.

Monitor-data layout:
- Creates `mon_data/mon_<resource>_<domain>` directories with one file per enabled event.
- For L3 SNC node scope, creates aggregate `mon_L3_<cacheid>` directories with subdomain directories.
- Reuses `struct mon_data` objects across identical event/domain/sum files.

Domain/CPU hotplug:
- Online control domains allocate MBA software-controller per-domain arrays when applicable.
- Online monitor domains allocate RMID busy bitmaps, MBM state arrays, assignable counter config, delayed work, and mon_data directories if mounted.
- Offline monitor domains remove mon_data directories, cancel work, force-free limbo RMIDs if needed, and destroy domain monitor state.
- CPU online adds the CPU to the default group; CPU offline removes it from current group/child masks and reschedules work off that CPU.

Notable invariants:
- resctrl can be mounted only once.
- Many operations require both `cpus_read_lock()` and `rdtgroup_mutex`.
- Schemata are generated after mount options because CDP changes visible resources and CLOSID counts.
- Default group always uses reserved CLOSID/RMID.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/rdtgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/romfs/Kconfig

Kconfig entries for ROMFS support.

Key options:
- `ROMFS_FS`: tristate read-only ROM filesystem, dependent on `BLOCK || MTD`.
- `ROMFS_BACKED_BY_BLOCK`: block-device backed ROMFS, dependent on `BLOCK`.
- `ROMFS_BACKED_BY_MTD`: direct MTD backed ROMFS, dependent on built-in MTD or module-compatible MTD.
- `ROMFS_BACKED_BY_BOTH`: enables both block and MTD backing.
- `ROMFS_ON_BLOCK`: derived boolean selected by block or both backing; selects `BUFFER_HEAD`.
- `ROMFS_ON_MTD`: derived boolean selected by MTD or both backing.

Purpose:
- Lets small systems choose block, MTD, or both storage paths while keeping ROMFS read-only and compact.
- Documents that NOMMU direct mapping is possible for CPU-addressable MTD devices.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/romfs/Makefile

Build glue for the ROMFS filesystem.

Key behavior:
- Builds `romfs.o` when `CONFIG_ROMFS_FS` is enabled.
- Always includes `storage.o` and `super.o`.
- On NOMMU builds, includes `mmap-nommu.o` only when `CONFIG_ROMFS_ON_MTD` is enabled.

Purpose:
- Keeps direct MTD mmap support limited to NOMMU MTD-backed configurations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/romfs/internal.h

Private ROMFS header shared by storage, superblock, and NOMMU mmap code.

Key definitions:
- `struct romfs_inode_info`: embeds the VFS inode and stores metadata size plus file data offset from filesystem start.
- `romfs_maxsize(sb)`: returns filesystem image size stored in `sb->s_fs_info`.
- `ROMFS_I(inode)`: converts a VFS inode to ROMFS inode-private state.

File-operation selection:
- Exposes `romfs_ro_fops` from `mmap-nommu.c` only for NOMMU + MTD builds.
- Otherwise maps `romfs_ro_fops` to `generic_ro_fops`.

Storage API:
- Declares `romfs_dev_read()`, `romfs_dev_strnlen()`, and `romfs_dev_strcmp()` for backing-store independent reads and directory-name handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/mmap-nommu.c -->
# File Research: sources/os/linux/linux-stable/fs/romfs/mmap-nommu.c

NOMMU mmap support for ROMFS files stored directly on MTD devices.

Key responsibilities:
- `romfs_get_unmapped_area()` validates requested shared mapping bounds against file size and MTD size, adds the ROMFS file data offset, and delegates address selection to `mtd_get_unmapped_area()`.
- Converts unsupported MTD direct mapping from `-EOPNOTSUPP` to `-ENOSYS`.
- `romfs_mmap_prepare()` permits only NOMMU shared mappings.
- `romfs_mmap_capabilities()` returns MTD mmap capabilities when an MTD device exists, otherwise `NOMMU_MAP_COPY`.
- Defines read-only file operations using generic read/splice plus NOMMU mmap hooks.

Notable invariants:
- Direct mappings are only attempted for MTD-backed ROMFS.
- Nonzero requested addresses, out-of-file ranges, and out-of-MTD ranges are rejected.
- Private mappings are not supported by this direct NOMMU path.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/mmap-nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/storage.c -->
# File Research: sources/os/linux/linux-stable/fs/romfs/storage.c

Implements backing-store independent ROMFS storage access for MTD and block devices.

Key responsibilities:
- Provides `romfs_dev_read()` with common bounds checking against `romfs_maxsize(sb)`, then dispatches to MTD or block-device readers.
- Provides `romfs_dev_strnlen()` for bounded filename/string scans, clamping the max length to the filesystem image limit.
- Provides `romfs_dev_strcmp()` for comparing a non-NUL-terminated VFS name against a NUL-terminated ROMFS image string, enforcing `ROMFS_MAXFN`.
- Implements MTD reads through `mtd_read()`, requiring the returned byte count to match the requested length.
- Implements MTD string scanning/comparison in small 16/17-byte chunks.
- Implements block reads through `sb_bread()` and buffer-head copying at ROMFS block-size granularity.
- Implements block string scanning/comparison across block boundaries, including explicit verification of the trailing NUL.

Notable invariants:
- At least one of `CONFIG_ROMFS_ON_MTD` or `CONFIG_ROMFS_ON_BLOCK` must be enabled.
- Any access beyond the recorded filesystem image size returns `-EIO`.
- String comparison returns `1` for match, `0` for mismatch, or a negative errno for read/validation errors.
- The block string comparison requires the terminating NUL either within the final compared block or as the first byte of the next block.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/romfs/storage.c -->