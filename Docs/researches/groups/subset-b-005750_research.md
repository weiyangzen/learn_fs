<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/ctrlmondata.c -->
# sources/distributed-fs/ceph-client/fs/resctrl/ctrlmondata.c

## Purpose
`ctrlmondata.c` implements the resctrl user-facing control and monitor data operations behind files such as `schemata`, `mba_MBps_event`, monitor event files, `io_alloc`, and `io_alloc_cbm`. It translates kernfs reads/writes into staged resctrl domain configuration, architecture counter reads, and optional I/O allocation cache partitioning.

## Important APIs, Types, And Functions
The local `struct rdt_parse_data` carries a CLOSID, current group mode, and value buffer into parser callbacks. `ctrlval_parser_t` abstracts schema-specific parsers. `bw_validate()` and `parse_bw()` validate memory bandwidth range controls, including MBA software-controller MBps mode. `cbm_validate()` and `parse_cbm()` validate cache bitmasks, enforce contiguous-mask rules when sparse masks are unsupported, enforce minimum bits, and reject overlap with exclusive or pseudo-locked allocations. `rdtgroup_schemata_write()` parses multiline `RESOURCE:id=value;...` updates and commits them via `resctrl_arch_update_domains()`. `rdtgroup_schemata_show()` formats current allocations, with special handling for pseudo-lock setup and pseudo-locked groups.

Monitoring entry points include `mon_event_read()`, which prepares `struct rmid_read` and dispatches `mon_event_count()` on an appropriate CPU or directly for `any_cpu` events, and `rdtgroup_mondata_show()`, which resolves `struct mon_data` from `kn->priv`, reads a domain or an SNC sum, and prints numeric, fixed-point, `Error`, `Unavailable`, or `Unassigned` output. `print_event_value()` formats fixed-point event values according to the architecture-provided binary fractional bit count.

I/O allocation support is exposed through `resctrl_io_alloc_show()`, `resctrl_io_alloc_write()`, `resctrl_io_alloc_cbm_show()`, and `resctrl_io_alloc_cbm_write()`. It reserves the highest usable CLOSID from `resctrl_io_alloc_closid()`, initializes its cache bitmask through `resctrl_io_alloc_init_cbm()`, and keeps CDP code/data peers in sync when CDP is enabled.

## Control Flow
For `schemata` writes, the function requires a trailing newline, locks the live rdtgroup, clears `last_cmd_status`, rejects pseudo-locked groups, clears staged configs, parses each resource line, and then commits staged configs for all non-MBA-SC resources. If the group is in `RDT_MODE_PSEUDO_LOCKSETUP`, a valid CBM initializes the pseudo-lock region and triggers `rdtgroup_pseudo_lock_create()`. All exits clear staged configs and unlock.

For monitor reads, `rdtgroup_mondata_show()` locks the group, gets the event metadata from kernfs private data, resolves a resource and domain, then calls `mon_event_read()`. SNC summing is expressed by a `NULL` domain header and a cacheinfo shared CPU map. `mon_event_read()` allocates architecture monitor context unless assignable MBM counters are active, chooses a housekeeping CPU for domain-scoped reads, uses `smp_call_on_cpu()` or `smp_call_function_any()` as needed, and frees the context.

For `io_alloc`, enabling validates hardware support and CLOSID availability, reserves a fixed CLOSID, initializes the CBM, and calls `resctrl_arch_io_alloc_enable()`. Disabling releases the fixed CLOSID after architecture state is changed off.

## State And Persistence
The file does not own persistent on-disk state. It mutates in-memory staged configs in `rdt_ctrl_domain::staged_config`, per-domain MBA-SC values in `mbps_val`, rdtgroup `mba_mbps_event`, pseudo-lock region fields, and architecture control registers through resctrl architecture hooks. User-visible failure text is accumulated in `last_cmd_status` through helpers from `rdtgroup.c`.

## Dependencies And Integration Points
It depends on `internal.h` definitions, global `resctrl_schema_all`, `rdtgroup_mutex`, group locking via `rdtgroup_kn_lock_live()`, CLOSID helpers, pseudo-lock helpers, and architecture APIs such as `resctrl_arch_update_domains()`, `resctrl_arch_rmid_read()`, `resctrl_arch_mon_ctx_alloc()`, CDP status helpers, and I/O allocation hooks. `rdtgroup.c` wires these callbacks into kernfs `rftype` definitions.

## Risks
Parser correctness is critical because bad validation can over-allocate cache ways, violate exclusive/pseudo-lock isolation, or leave stale staged configs. All functions assume `rdtgroup_mutex` and CPU hotplug locks are held where asserted; missing those locks would race domain lists or group deletion. Monitor reads must handle architecture-specific errors without exposing misleading counters. I/O allocation uses a fixed high CLOSID, so conflicts with existing groups and CDP-halved CLOSID ranges are important edge cases.

## Test Signals
Useful tests exercise valid and invalid `schemata` writes, duplicate domain entries, sparse and non-sparse CBMs, MBA min/max/granularity rounding, pseudo-lock setup rejection for MBA, `mba_MBps_event` selection when events are disabled, monitor reads with offline domains, SNC sum files, fixed-point formatting, and `io_alloc` enable/disable plus `io_alloc_cbm` wildcard and per-domain updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/ctrlmondata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/internal.h -->
# sources/distributed-fs/ceph-client/fs/resctrl/internal.h

## Purpose
`internal.h` is the private contract for the resctrl filesystem implementation. It defines the in-memory objects shared by `rdtgroup.c`, `ctrlmondata.c`, `monitor.c`, and optional pseudo-lock code, plus function prototypes and configuration-gated pseudo-lock stubs.

## Important APIs, Types, And Functions
`cpumask_any_housekeeping()` selects a CPU from a mask while preferring CPUs not in `nohz_full`, which matters for delayed work and counter reads. `struct rdt_fs_context` extends kernfs mount context with mount flags for L2/L3 CDP, MBA MBps mode, and debug files; `rdt_fc2context()` recovers it from `fs_context`.

Monitoring contracts include `struct mon_evt`, the global `mon_event_all[]`, `for_each_mon_event()`, and `MAX_BINARY_BITS`; `struct mon_data`, stored as kernfs private data for monitor event files; and `struct rmid_read`, the cross-CPU payload used by `mon_event_read()` and `mon_event_count()`.

Group contracts include `enum rdt_group_type`, `enum rdtgrp_mode`, `struct mongroup`, and `struct rdtgroup`. The header also defines `RDT_DELETED`, `RFTYPE_*` flags, `struct rftype`, `struct mbm_state`, and extern globals such as `resctrl_schema_all`, `rdt_all_groups`, `rdtgroup_mutex`, `rdtgroup_default`, `debugfs_resctrl`, and `mba_mbps_default_event`.

The prototypes declare the internal API surface for group locking, `last_cmd_status`, schemata I/O, monitor file show functions, RMID allocation, monitor initialization, delayed work handlers, MBA assignment controls, I/O allocation, CLOSID lookup, CDP peer mapping, and pseudo-lock operations.

## Control Flow
The header itself has no runtime control flow except inline helpers. Its main control role is to keep cross-file call paths explicit: `rdtgroup.c` owns filesystem lifecycle and locks, `ctrlmondata.c` owns control/monitor file operations, `monitor.c` owns RMID and event counting, and `pseudo_lock.c` is compiled in only when `CONFIG_RESCTRL_FS_PSEUDO_LOCK` is enabled.

## State And Persistence
All declared state is in-memory kernel state. `struct rdtgroup` tracks kernfs identity, CLOSID/RMID, CPU assignment, deletion status, type, mode, child monitor groups, MBA MBps event, and pseudo-lock region pointer. `struct mon_data` instances persist while the resctrl filesystem is mounted. `struct rmid_read` is transient per read or counter initialization.

## Dependencies And Integration Points
The header includes `linux/resctrl.h`, kernfs, fs context, and tick/nohz APIs. It binds resctrl filesystem code to architecture-facing functions declared elsewhere by `linux/resctrl.h`, and to kernel subsystems including kernfs, CPU hotplug, cpumasks, delayed work, debugfs, and optional pseudo-lock char-device support.

## Risks
Because this is the shared internal ABI, field semantics must stay synchronized across all implementation files. Misinterpreting `rdtgroup::type`, `mode`, `closid`, or `mon.rmid` changes task/CPU assignment and monitoring behavior. Locking expectations are not encoded in types; many users must already hold `rdtgroup_mutex` and sometimes `cpus_read_lock()`.

## Test Signals
Build coverage should include configurations with allocation only, monitoring only, assignable MBM counters, CDP, MBA MBps, and pseudo-lock enabled/disabled. Runtime tests should verify that all kernfs callbacks referenced by `struct rftype` compile and that pseudo-lock stubs return `-EOPNOTSUPP` or no-op behavior when the feature is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/monitor.c -->
# sources/distributed-fs/ceph-client/fs/resctrl/monitor.c

## Purpose
`monitor.c` implements resctrl monitoring: RMID allocation and reclamation, LLC occupancy limbo scanning, MBM counter overflow accounting, MBA software-controller feedback, monitor event registration, event filter configuration, and assignable MBM counter management.

## Important APIs, Types, And Functions
The private `struct rmid_entry` records a CLOSID/RMID pair, per-domain busy count, and free-list linkage. Global state includes `rmid_free_lru`, `rmid_ptrs`, `rmid_limbo_count`, `resctrl_rmid_realloc_threshold`, `resctrl_rmid_realloc_limit`, and optional `closid_num_dirty_rmid[]`.

RMID lifecycle functions include `setup_rmid_lru_list()`, `alloc_rmid()`, `free_rmid()`, `add_rmid_to_limbo()`, `__check_limbo()`, `has_busy_rmid()`, and `resctrl_find_cleanest_closid()`. Counter read paths include `__l3_mon_event_count()`, `__l3_mon_event_count_sum()`, `__mon_event_count()`, `mon_event_count()`, `mbm_update_one_event()`, `mbm_update()`, and `mbm_bw_count()`. Delayed work entry points are `cqm_handle_limbo()` and `mbm_handle_overflow()`, scheduled by `cqm_setup_limbo_handler()` and `mbm_setup_overflow_handler()`.

Event and assignment APIs include `mon_event_all[]`, `resctrl_enable_mon_event()`, `resctrl_is_mon_event_enabled()`, `resctrl_get_mon_evt_cfg()`, `event_filter_show/write()`, `resctrl_mbm_assign_mode_show/write()`, `resctrl_mbm_assign_on_mkdir_show/write()`, `resctrl_num_mbm_cntrs_show()`, `resctrl_available_mbm_cntrs_show()`, `mbm_L3_assignments_show/write()`, `rdtgroup_assign_cntrs()`, and `rdtgroup_unassign_cntrs()`.

## Control Flow
RMID freeing does not immediately return an RMID to users if LLC occupancy monitoring is enabled. `free_rmid()` adds the entry to each L3 monitor domain's busy bitmap and schedules limbo work. `__check_limbo()` reads occupancy for busy RMID indices and moves entries back to `rmid_free_lru` once all domains report occupancy below threshold or forced cleanup is requested.

Monitor reads arrive through `mon_event_count()`, which reads the parent group and then child monitor groups for control groups. L3 reads can target one domain or sum across SNC domains sharing a cache id. MBM overflow work iterates all groups and child monitor groups, updates total/local MBM state, optionally calls `update_mba_bw()` for MBA-SC feedback, and reschedules itself.

Assignable MBM counter mode switches through `resctrl_mbm_assign_mode_write()`. Enabling changes architecture mode, hides BMEC config files, seeds default event filters, enables assign-on-mkdir, clears domain counter assignments, and resets non-architectural RMID state. Per-group `mbm_L3_assignments_write()` parses event/domain assignment state and assigns or frees counters.

## State And Persistence
All state is volatile kernel memory. RMID free/limbo state persists across mounts until `resctrl_exit()` because delayed limbo work can outlive unmount. Per-domain `mbm_states[]` stores previous byte counts and calculated MBps. Assignable counters use `rdt_l3_mon_domain::cntr_cfg[]`. `mon_event_all[]` stores enabled/configurable flags, architecture private pointers, fixed-point metadata, and event filter bitmasks.

## Dependencies And Integration Points
The file is driven by architecture hooks for RMID index encoding/decoding, monitor context allocation, RMID/counter reads, event enablement, MBM counter assignment, and MBA control updates. It integrates with `rdtgroup.c` group lists and kernfs callbacks, `ctrlmondata.c` monitor read dispatch, CPU hotplug domain setup/teardown, delayed work, and `monitor_trace.h` tracepoints.

## Risks
RMID leaks are a central risk when limbo work is not scheduled, domains go offline, or forced cleanup misses busy entries. Counter reads are CPU-affine for some resources; running on the wrong CPU returns errors or stale data. Assignable MBM counter updates can partially succeed across domains before an allocation failure. MBA-SC feedback can over-throttle or under-throttle if MBM deltas are stale, reset, or summed incorrectly. The code relies heavily on `rdtgroup_mutex` and CPU hotplug serialization.

## Test Signals
Tests should cover RMID exhaustion versus `-EBUSY` limbo cases, threshold updates, domain offline forced limbo release, MBM overflow rescheduling on housekeeping CPUs, parent plus child monitor aggregation, SNC summed monitors, assignable counter mode transitions, event filter parsing, per-domain assignment syntax, and MBA-SC bandwidth adjustment behavior after MBM state resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/monitor_trace.h -->
# sources/distributed-fs/ceph-client/fs/resctrl/monitor_trace.h

## Purpose
`monitor_trace.h` defines the resctrl tracepoint used by LLC occupancy limbo scanning. It lets tracing users observe CLOSID/RMID occupancy values while the monitor code decides whether an RMID is clean enough for reallocation.

## Important APIs, Types, And Functions
The header sets `TRACE_SYSTEM resctrl` and declares `TRACE_EVENT(mon_llc_occupancy_limbo)`. The event takes `ctrl_hw_id`, `mon_hw_id`, `domain_id`, and `llc_occupancy_bytes`, stores them as trace fields, and prints them in a compact key/value format. `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` complete Linux tracepoint generation.

## Control Flow
There is no normal runtime logic in the header. Including it with `CREATE_TRACE_POINTS` in `monitor.c` instantiates the tracepoint. `__check_limbo()` calls `trace_mon_llc_occupancy_limbo()` after successful LLC occupancy reads for busy RMID entries.

## State And Persistence
The tracepoint stores no persistent resctrl state. It emits transient trace records into the kernel tracing infrastructure when enabled. The recorded identifiers reflect architecture-decoded CLOSID/RMID values and the current L3 monitor domain id.

## Dependencies And Integration Points
It depends on Linux tracepoint macros and is tightly coupled to `monitor.c` RMID limbo handling. User space can consume the event through ftrace, perf, or tracefs if tracing is configured.

## Risks
The event is diagnostic, so the main risk is semantic drift between field names and architecture behavior. On architectures where RMID depends on CLOSID, both IDs are meaningful; on x86 the CLOSID may be the empty/reserved value for RMID-only indexing. Excessive tracing during limbo scans can add overhead if enabled on systems with many RMIDs/domains.

## Test Signals
Build tests should ensure tracepoint generation succeeds with `CREATE_TRACE_POINTS`. Runtime validation can enable the event, force RMIDs into limbo, and confirm emitted records contain the expected domain id and occupancy bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/monitor_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/pseudo_lock.c -->
# sources/distributed-fs/ceph-client/fs/resctrl/pseudo_lock.c

## Purpose
`pseudo_lock.c` implements optional resctrl cache pseudo-locking. It converts a CAT allocation in a resource group into a cache-resident memory region exposed through a character device and debugfs measurement trigger, while preventing ordinary task/CPU assignment and conflicting cache allocations.

## Important APIs, Types, And Functions
Global device state includes `pseudo_lock_major`, the minor availability bitmap, and `pseudo_lock_class` with `pseudo_lock_devnode()`. Minor management uses `pseudo_lock_minor_get()` and `pseudo_lock_minor_release()`. `region_find_by_minor()` maps an opened device back to the owning `rdtgroup`.

Region setup functions include `pseudo_lock_init()`, `pseudo_lock_region_init()`, `pseudo_lock_region_alloc()`, `pseudo_lock_region_clear()`, and `pseudo_lock_free()`. C-state constraints use `struct pseudo_lock_pm_req`, `pseudo_lock_cstates_constrain()`, and `pseudo_lock_cstates_relax()`.

Mode transitions are handled through exported helpers `rdtgroup_locksetup_enter()`, `rdtgroup_locksetup_exit()`, `rdtgroup_pseudo_lock_create()`, and `rdtgroup_pseudo_lock_remove()`. Overlap checks are exposed as `rdtgroup_cbm_overlaps_pseudo_locked()` and `rdtgroup_pseudo_locked_in_hierarchy()`. Debug measurement uses `pseudo_lock_measure_cycles()` and `pseudo_lock_measure_trigger()`. Character device operations include `pseudo_lock_dev_open()`, `pseudo_lock_dev_release()`, `pseudo_lock_dev_mmap_prepare()`, and a rejected `mremap`.

## Control Flow
Entering locksetup rejects the default group, CDP-enabled systems, unsupported prefetch-disable platforms, existing monitor groups, assigned tasks, or assigned CPUs. It then restricts relevant kernfs files, allocates a pseudo-lock region object, and frees the group RMID because monitoring is not allowed.

When a valid cache schemata is written in locksetup mode, `rdtgroup_pseudo_lock_create()` allocates backing memory sized from the CBM, constrains C-states on CPUs in the cache domain, runs the architecture pseudo-lock thread on the selected CPU, allocates a minor, temporarily drops `rdtgroup_mutex` to create debugfs and device nodes, then rechecks deletion state. On success it marks the group pseudo-locked, frees the CLOSID, and makes CPU files read-only.

Device `mmap_prepare` requires the caller to be affined to the pseudo-locked domain CPUs, requires shared mapping, checks offset/length bounds, zeroes the mapped region slice, installs VM ops, and remaps physical pages. Removal tears down PM QoS, debugfs, device node, minor, CLOSID/RMID ownership, and region memory depending on the mode.

## State And Persistence
Pseudo-lock state is in memory and device/debugfs namespace entries. `rdtgroup::plr` points to a `pseudo_lock_region` that records schema, domain, CBM, size, line size, CPU, memory pointer, waitqueue, PM QoS requests, debugfs dir, and device minor. The pseudo-locked memory is allocated with `kzalloc()` and freed on group removal or failed setup.

## Dependencies And Integration Points
This file depends on CAT allocation state from `rdtgroup.c` and `ctrlmondata.c`, architecture pseudo-lock and measurement callbacks, PM QoS, CPU hotplug state, debugfs, char devices, NOMMU-style `mmap_prepare` APIs, kernfs permission helpers, CLOSID/RMID helpers, and cacheinfo.

## Risks
The code intentionally drops `rdtgroup_mutex` during debugfs/device creation to avoid lock inversions, so deletion races must be rechecked carefully. CPU affinity is a correctness requirement for mapped users; otherwise the user could evict the pseudo-locked cache lines. CLOSID/RMID ownership changes are asymmetric across setup, creation, exit, and removal, making leak tests important. Large regions are limited by `KMALLOC_MAX_SIZE`, and C-state QoS setup must unwind completely on partial failure.

## Test Signals
Tests should cover mode transitions into and out of locksetup, rejection with tasks/CPUs/monitor groups/CDP enabled, CBM overlap and hierarchy rejection, successful device creation/removal, mmap bounds and shared-only checks, affinity rejection, interrupted lock thread handling, debugfs measurement selectors, and CPU/domain offline behavior where `plr->d` becomes unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/pseudo_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/rdtgroup.c -->
# sources/distributed-fs/ceph-client/fs/resctrl/rdtgroup.c

## Purpose
`rdtgroup.c` is the resctrl filesystem integration hub. It registers and mounts the kernfs-based `resctrl` filesystem, creates all control/info/monitor files, manages resource and monitor groups, assigns tasks and CPUs to CLOSID/RMID pairs, handles mount options, domain hotplug, teardown, and delegates schemata, monitoring, assignable counter, I/O allocation, and pseudo-lock work to peer files.

## Important APIs, Types, And Functions
Global state includes `rdtgroup_mutex`, `rdt_root`, `rdtgroup_default`, `rdt_all_groups`, `resctrl_schema_all`, `mon_data_kn_priv_list`, mount flag `resctrl_mounted`, root kernfs nodes, `max_name_width`, `last_cmd_status`, `debugfs_resctrl`, `mba_mbps_default_event`, and `resctrl_debug`.

CLOSID management uses `closid_init()`, `closid_alloc()`, `closid_free()`, `closid_allocated()`, `closid_alloc_fixed()`, and `rdtgroup_mode_by_closid()`. Kernfs file dispatch is described by `struct rftype res_common_files[]`, `rdtgroup_add_files()`, `rdtgroup_file_write()`, and `rdtgroup_seqfile_show()`.

User operations include `rdtgroup_cpus_show/write()`, `rdtgroup_tasks_show/write()`, `rdtgroup_mode_show/write()`, `rdtgroup_size_show()`, info file show methods, MBM config show/write, and mount option parsing through `rdt_parse_param()`. Group lifecycle is handled by `rdtgroup_mkdir()`, `rdtgroup_mkdir_ctrl_mon()`, `rdtgroup_mkdir_mon()`, `rdtgroup_rmdir()`, `rdtgroup_rename()`, and helpers for mon_data directory creation/removal.

Filesystem lifecycle includes `rdt_init_fs_context()`, `rdt_get_tree()`, `rdt_kill_sb()`, `resctrl_init()`, and `resctrl_exit()`. Hotplug hooks include `resctrl_online_cpu()`, `resctrl_offline_cpu()`, `resctrl_online_ctrl_domain()`, `resctrl_offline_ctrl_domain()`, `resctrl_online_mon_domain()`, and `resctrl_offline_mon_domain()`.

## Control Flow
Mounting (`rdt_get_tree()`) serializes CPU hotplug and `rdtgroup_mutex`, rejects multiple mounts, prepares RMID LRU state, creates the root, enables mount context features such as CDP/MBA-SC/debug, builds schema entries, initializes CLOSID allocation, adds root files, creates `info`, `mon_groups`, and `mon_data`, initializes pseudo-lock device support, obtains the kernfs tree, enables architecture allocation/monitoring, sets `resctrl_mounted`, and starts MBM overflow work.

Creating a control group allocates a kernfs directory, a CLOSID, optionally an RMID and monitor files, initializes default CAT/MBA allocations across domains, adds it to `rdt_all_groups`, and creates its `mon_groups` directory. Creating a monitor group under `mon_groups` inherits the parent CLOSID, allocates its own RMID, creates monitor files, and links into the parent's child list.

CPU writes move CPUs between groups while updating per-CPU defaults and hardware state. Task writes validate permissions, set task CLOSID/RMID, issue memory barriers, and update the running CPU if needed. Removing groups moves tasks and CPUs back to parent/default groups, unassigns counters, frees RMIDs/CLOSIDs, removes kernfs nodes, and uses `RDT_DELETED` plus `waitcount` to defer freeing if files are still active.

## State And Persistence
State is in-memory and tied to the mounted filesystem. `rdtgroup` objects persist while their kernfs nodes or active references exist. `resctrl_schema` entries represent current exposed control resources and CDP split state. `mon_data` private structures are shared across event files until unmount. Hardware state is persisted only in architecture registers and reset during unmount or `resctrl_exit()`.

## Dependencies And Integration Points
The file depends on kernfs, fs context, sysfs mount points, debugfs, task iteration, CPU hotplug locks, resctrl architecture hooks, `ctrlmondata.c` schemata and monitor callbacks, `monitor.c` RMID/MBM helpers, and optional pseudo-lock helpers. It is the file that wires those helpers into the visible resctrl file tree through `res_common_files`.

## Risks
The highest-risk areas are lifetime and locking: kernfs active protection is deliberately broken while holding references, group deletion can race open files, and CPU/domain hotplug can change masks and monitor directories. Incorrect CLOSID/RMID cleanup leaks scarce hardware IDs. Mount option rollback must undo CDP/MBA-SC/root/schema/CLOSID state in the correct order. Mode transitions must preserve exclusivity, pseudo-lock restrictions, and monitor assignment invariants. Task movement relies on barriers pairing with scheduler resctrl updates.

## Test Signals
Test signals include mount/unmount with all option combinations, duplicate mount rejection, CLOSID/RMID exhaustion, creation/removal/rename of ctrl and mon groups, task and CPU migration including permission failures, default group CPU retention, pseudo-lock mode transitions, mon_data directory updates on domain hotplug, MBM config file visibility changes, `last_cmd_status` text for invalid commands, and teardown after simulated architecture fatal exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/rdtgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/romfs/Kconfig

## Purpose
This Kconfig file declares ROMFS filesystem support and selects which backing stores are compiled: block devices, MTD devices, or both. It makes ROMFS available as a tiny read-only filesystem for initramfs/install media and other read-only media.

## Important Symbols
`ROMFS_FS` is the top-level tristate, dependent on `BLOCK || MTD`. The `choice` block selects one of `ROMFS_BACKED_BY_BLOCK`, `ROMFS_BACKED_BY_MTD`, or `ROMFS_BACKED_BY_BOTH`. Derived booleans `ROMFS_ON_BLOCK` and `ROMFS_ON_MTD` are set from that choice. `ROMFS_ON_BLOCK` selects `BUFFER_HEAD`, because block-backed storage uses buffer heads in `storage.c`.

## Control Flow
Kconfig control flow is declarative. Enabling `ROMFS_FS` opens the backing-store choice. Block support requires `BLOCK`; MTD support requires built-in MTD or module-compatible MTD when ROMFS is a module. The selected derived symbols control conditional compilation in `storage.c`, `internal.h`, and `Makefile`.

## State And Persistence
The file controls build-time configuration only. It does not manage runtime state or persistent filesystem data. Its choices determine which code paths exist in the built kernel/module.

## Dependencies And Integration Points
It integrates with the kernel build system, MTD, block layer, and buffer-head infrastructure. `Documentation/filesystems/romfs.rst` is referenced for format/user documentation. `Makefile` consumes `CONFIG_ROMFS_FS`, `CONFIG_ROMFS_ON_MTD`, and `CONFIG_MMU`.

## Risks
Misconfigured dependencies can build ROMFS without any backing store, which `storage.c` explicitly rejects with a preprocessor error. Module/built-in dependency rules for MTD are important because direct MTD access must be linkable. Choosing only block support disables NOMMU direct MTD mapping.

## Test Signals
Build matrix tests should cover `ROMFS_FS=n`, `m`, and `y`; block-only, MTD-only, and both; MMU and NOMMU; and module builds with MTD as built-in or module-compatible. Runtime smoke tests should mount block-backed and MTD-backed ROMFS images matching the selected configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/romfs/Makefile

## Purpose
The ROMFS Makefile connects Kconfig selections to the kernel build. It builds the `romfs` object when `CONFIG_ROMFS_FS` is enabled and conditionally includes NOMMU MTD mmap support.

## Important Build Rules
`obj-$(CONFIG_ROMFS_FS) += romfs.o` builds ROMFS as built-in or module according to the top-level tristate. `romfs-y := storage.o super.o` always includes storage access and superblock/inode logic. When `CONFIG_MMU` is not `y`, `romfs-$(CONFIG_ROMFS_ON_MTD) += mmap-nommu.o` adds direct MTD mmap support for NOMMU systems.

## Control Flow
Build control is declarative. The composite `romfs.o` is formed from required objects and optional `mmap-nommu.o`. The conditional deliberately excludes NOMMU mmap code on MMU builds and excludes it when MTD backing is not enabled.

## State And Persistence
No runtime state is present. The file determines which object files are linked into the kernel or module.

## Dependencies And Integration Points
It consumes `CONFIG_ROMFS_FS`, `CONFIG_MMU`, and `CONFIG_ROMFS_ON_MTD` from Kconfig. It assumes `super.o` provides filesystem registration and `storage.o` provides backing-store reads, while `mmap-nommu.o` provides `romfs_ro_fops` only for the `!MMU && ROMFS_ON_MTD` case referenced by `internal.h`.

## Risks
The conditional must stay aligned with `internal.h`; otherwise `romfs_ro_fops` could be declared but not linked, or NOMMU MTD direct mapping support could be silently omitted. Build coverage across MMU/NOMMU and backing-store combinations is the main guard.

## Test Signals
Compile tests should verify block-only, MTD-only, both, MMU, and NOMMU combinations. A NOMMU plus MTD build should include `mmap-nommu.o`; ordinary MMU builds should not.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/romfs/internal.h

## Purpose
`internal.h` defines ROMFS-private inode metadata, helpers, and cross-file declarations for storage access and optional NOMMU MTD file operations.

## Important APIs, Types, And Functions
`struct romfs_inode_info` embeds `struct inode` and adds `i_metasize` for non-data bytes plus `i_dataoffset` from filesystem start. `romfs_maxsize()` interprets `sb->s_fs_info` as the maximum accessible filesystem size. `ROMFS_I()` converts a VFS inode to the ROMFS inode wrapper.

The header conditionally declares `extern const struct file_operations romfs_ro_fops` for `!CONFIG_MMU && CONFIG_ROMFS_ON_MTD`; otherwise it aliases `romfs_ro_fops` to `generic_ro_fops`. Storage APIs exported from `storage.c` are `romfs_dev_read()`, `romfs_dev_strnlen()`, and `romfs_dev_strcmp()`.

## Control Flow
The only control flow is preprocessor selection of file operations. NOMMU MTD builds use ROMFS-specific operations that can request direct MTD mappings. All other builds use generic read-only file operations.

## State And Persistence
ROMFS inode state lives in allocated inodes managed by `super.c`. `i_dataoffset` and `i_metasize` persist in memory for each inode after parsing on-disk metadata. Superblock `s_fs_info` carries image-size information consumed by storage bounds checks.

## Dependencies And Integration Points
The header includes `linux/romfs_fs.h` for format constants such as ROMFS limits. It integrates storage helpers with superblock/inode parsing and maps file operations to `mmap-nommu.c` when configured.

## Risks
`romfs_maxsize()` relies on `s_fs_info` being initialized to a valid size-compatible pointer value by mount code. Wrong `i_dataoffset` values can make storage and mmap code read or map the wrong image area. The file-operations conditional must match the Makefile conditional.

## Test Signals
Tests should verify inode wrapper conversion, max-size initialization during mount, correct use of generic file ops on MMU or non-MTD builds, and use of `romfs_ro_fops` on NOMMU MTD builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/mmap-nommu.c -->
# sources/distributed-fs/ceph-client/fs/romfs/mmap-nommu.c

## Purpose
`mmap-nommu.c` provides ROMFS read-only file operations for NOMMU systems backed by directly addressable MTD devices. It allows shared mappings to point through to the underlying MTD storage when the MTD driver supports it.

## Important APIs, Types, And Functions
`romfs_get_unmapped_area()` validates a requested mapping and delegates address selection to `mtd_get_unmapped_area()`. `romfs_mmap_prepare()` allows only NOMMU shared mappings and rejects unsupported private/copy mappings with `-ENOSYS`. `romfs_mmap_capabilities()` returns MTD mapping capabilities or `NOMMU_MAP_COPY` when no MTD exists. `romfs_ro_fops` combines generic read-only read/seek/splice operations with these NOMMU mmap hooks.

## Control Flow
Mapping starts with VFS/NOMMU asking `get_unmapped_area`. The function rejects non-MTD superblocks, mappings beyond inode EOF, nonzero requested addresses, lengths or page offsets beyond the MTD size, and offsets beyond MTD size after adding `ROMFS_I(inode)->i_dataoffset`. It clamps length to the remaining MTD size if needed, delegates to the MTD driver, and maps `-EOPNOTSUPP` to `-ENOSYS`.

`mmap_prepare` is a second gate: only shared NOMMU VMA flags are accepted. Capabilities are reported directly from the MTD device, allowing the NOMMU core to decide whether direct mapping is possible.

## State And Persistence
The file owns no state. It reads inode size, superblock `s_mtd`, MTD size/capabilities, and ROMFS inode data offset. Mappings are runtime VMA state managed by the VM and MTD layers.

## Dependencies And Integration Points
It depends on NOMMU VM APIs, MTD superblock support, `mtd_get_unmapped_area()`, `mtd_mmap_capabilities()`, and ROMFS inode metadata from `internal.h`. It is compiled only for `!MMU && ROMFS_ON_MTD` and supplies the `romfs_ro_fops` declaration used by `super.c` through `internal.h`.

## Risks
Offset arithmetic must prevent mapping beyond EOF, image data, or MTD bounds. Since `offset += i_dataoffset`, malformed inode metadata could otherwise direct mappings outside file data. Rejecting nonzero `addr` is strict but avoids unsupported placement semantics. Returning copy capabilities for non-MTD fallback ensures reads still work, but direct mmap is unavailable.

## Test Signals
Tests should cover shared versus private mappings, mapping exactly at EOF boundaries, pgoff and len overflow-style edge cases, non-MTD fallback, MTD `-EOPNOTSUPP` translation, and correct physical offset including `i_dataoffset`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/mmap-nommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/storage.c -->
# sources/distributed-fs/ceph-client/fs/romfs/storage.c

## Purpose
`storage.c` provides ROMFS backing-store access helpers. It abstracts reads, bounded string length scans, and name comparisons over MTD-backed and block-backed ROMFS images while enforcing image-size limits.

## Important APIs, Types, And Functions
Public helpers are `romfs_dev_read()`, `romfs_dev_strnlen()`, and `romfs_dev_strcmp()`. MTD-specific implementations are `romfs_mtd_read()`, `romfs_mtd_strnlen()`, and `romfs_mtd_strcmp()`, built under `CONFIG_ROMFS_ON_MTD` and using `mtd_read()`. Block-specific implementations are `romfs_blk_read()`, `romfs_blk_strnlen()`, and `romfs_blk_strcmp()`, built under `CONFIG_ROMFS_ON_BLOCK` and using `sb_bread()`, `buffer_head`, `memcpy()`, `memchr()`, and `memcmp()`.

## Control Flow
All public helpers first check `romfs_maxsize(sb)` bounds. `romfs_dev_read()` rejects reads starting beyond the image or extending past the limit, then dispatches to MTD if `sb->s_mtd` is present, else block if `sb->s_bdev` is present. `romfs_dev_strnlen()` clamps `maxlen` to the image limit and dispatches similarly. `romfs_dev_strcmp()` rejects out-of-image positions, names longer than `ROMFS_MAXFN`, and comparisons without space for the trailing NUL.

MTD reads request exact byte counts and treat short reads as `-EIO`. MTD string operations scan up to 16 bytes at a time; compare reads up to 17 bytes to include the trailing NUL. Block reads split by `ROMBSIZE` block boundaries, reading each buffer head, copying or scanning the segment, and releasing the buffer. Block compare checks a terminator either inside the final block or at the first byte of the next block.

## State And Persistence
The file owns no mutable state. It reads from persistent ROMFS images through MTD or block devices and uses transient stack buffers or buffer heads. Superblock fields `s_mtd`, `s_bdev`, and `s_fs_info` determine the active backend and bounds.

## Dependencies And Integration Points
It depends on `internal.h`, `linux/mtd/super.h`, `linux/buffer_head.h`, ROMFS constants `ROMBSIZE`, `ROMBSBITS`, and `ROMFS_MAXFN`, plus mount code that initializes `s_mtd`, `s_bdev`, and max size. `super.c` uses these helpers to parse metadata, names, and file data from the image.

## Risks
Boundary checks are the primary correctness and security defense. Off-by-one errors around trailing NUL checks could accept prefix names or read past image end. MTD short reads and block read failures must become `-EIO`. Block compare uses `BUG_ON()` for an invariant that the terminator check at the next block only happens on a block boundary, so logic changes around segment sizing need care.

## Test Signals
Tests should cover reads spanning block boundaries, strings with terminator inside a block and at the next block, missing terminators, oversized names, image-end boundary reads, MTD short-read/error injection, block `sb_bread()` failure, and both backing-store configurations. Mount tests with malformed ROMFS metadata should confirm errors are returned rather than out-of-bounds access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/storage.c -->
