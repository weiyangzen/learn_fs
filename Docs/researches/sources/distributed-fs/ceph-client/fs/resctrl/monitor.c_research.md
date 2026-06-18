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
