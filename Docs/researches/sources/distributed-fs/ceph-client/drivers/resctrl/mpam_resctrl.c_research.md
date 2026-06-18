# sources/distributed-fs/ceph-client/drivers/resctrl/mpam_resctrl.c

## Purpose

This file maps Arm MPAM classes and components into the generic Linux resctrl filesystem architecture. It chooses MPAM resources that can represent L2/L3 cache allocation, memory bandwidth allocation, and L3 occupancy monitoring; initializes `struct rdt_resource` capabilities; translates resctrl CLOSID/RMID operations into MPAM PARTID/PMG values; manages resctrl domains during CPU hotplug; and tears resctrl down if MPAM is disabled.

## Important APIs, Types, And Functions

It implements the resctrl architecture hooks such as `resctrl_arch_alloc_capable()`, `resctrl_arch_mon_capable()`, `resctrl_arch_get_num_closid()`, `resctrl_arch_system_num_rmid_idx()`, `resctrl_arch_rmid_idx_encode()`, `resctrl_arch_rmid_idx_decode()`, `resctrl_arch_sched_in()`, `resctrl_arch_set_cpu_default_closid_rmid()`, `resctrl_arch_set_closid_rmid()`, `resctrl_arch_get_config()`, `resctrl_arch_update_one()`, `resctrl_arch_update_domains()`, `resctrl_arch_reset_all_ctrls()`, monitor context allocation/free, and `resctrl_arch_rmid_read()`.

MPAM-owned setup and hotplug functions are `mpam_resctrl_setup()`, `mpam_resctrl_exit()`, `mpam_resctrl_online_cpu()`, `mpam_resctrl_offline_cpu()`, and `mpam_resctrl_teardown_class()`. Resource selection helpers include `mpam_resctrl_pick_caches()`, `mpam_resctrl_pick_mba()`, `mpam_resctrl_pick_counters()`, `topology_matches_l3()`, and `traffic_matches_l3()`.

## Control Flow

`mpam_resctrl_setup()` waits for cacheinfo, initializes resctrl domain lists for all resource slots, selects MPAM classes for cache controls and MBA, initializes selected `rdt_resource` objects, selects monitoring counter classes, initializes monitoring, and then calls `resctrl_init()`. If neither allocation nor monitoring is available, setup returns `-EOPNOTSUPP`.

Resource selection is conservative. Cache allocation exposes only MPAM cache classes at level 2 or 3 with usable CPOR bitmaps, no more than 32 CBM bits, and affinity covering all possible CPUs. MBA uses MBW_MAX-capable classes whose topology and traffic shape match L3 expectations. Monitoring currently exposes CSU occupancy counters as L3 occupancy events and may fake an L3 resource when counters exist without L3 controls.

During CPU online, the bridge creates or updates control and monitor domains for each selected resource, using MPAM component affinity to choose domain membership and IDs. During CPU offline, it removes CPU bits, calls resctrl offline hooks, synchronizes RCU when a domain list entry is removed, and frees empty `mpam_resctrl_dom` objects.

Configuration updates convert resctrl CBM or MBA percentage values into `struct mpam_config` and call `mpam_apply_config()` for the correct PARTID. CDP emulation maps code/data to odd/even PARTIDs through `resctrl_get_config_index()`.

## State And Persistence

Static arrays `mpam_resctrl_controls[RDT_NUM_RESOURCES]` and `mpam_resctrl_counters[MPAM_MAX_EVENT + 1]` persist the chosen MPAM classes. `cdp_enabled`, per-resource `cdp_enabled`, `cacheinfo_ready`, and `resctrl_enabled` track bridge state. Domain lists live inside the `rdt_resource` objects and contain allocated `mpam_resctrl_dom` wrappers. Monitor context allocation uses IDA-backed CSU monitor allocation in the selected MPAM class; MBWU contexts currently use the sentinel `USE_PRE_ALLOCATED`.

Task and CPU default state is persistent in Arm MPAM task fields and `arm64_mpam_global_default`. CDP enable/disable relabels all tasks and updates all possible CPU defaults before syncing current CPU MPAM registers.

## Dependencies And Integration Points

The file depends on generic resctrl, cacheinfo, CPU hotplug, Arm MPAM task/register helpers, MPAM topology from `mpam_devices.c`, and `mpam_internal.h`. It assumes the generic resctrl model is L3-centered and adapts MPAM classes into that shape. It also depends on cacheinfo becoming ready at `device_initcall_sync()`.

## Risks And Edge Cases

Several resctrl hooks are stubs or unsupported: event configuration, RMID resets, counter assignment, IO allocation, and ABMC-style counter reading return no-op or errors. `resctrl_arch_rmid_read()` only accepts L3 occupancy events in this snapshot. The source contains a duplicated `tsk_closid >>= 1;` line in `resctrl_arch_match_rmid()`, which would incorrectly match tasks when CDP is enabled. CDP is warned as expert-only and rejected unless `CONFIG_EXPERT` allows it because repeated mounts can exhaust/out-range PARTIDs.

Topology inference is strict and may hide valid MPAM resources if cacheinfo, PPTT, NUMA, memory-side cache, or last-level-cache assumptions do not match resctrl's L3 model. Domain management must coordinate `domain_list_lock`, CPU hotplug locks, SRCU, and RCU list removal. Monitor allocation can sleep waiting for CSU monitor IDs.

## Test Signals

There is a conditional include for `test_mpam_resctrl.c`, though that file is outside this work item. Useful tests include class selection for L2/L3/MBA/CSU, MBA percent-to-fixed-point conversion, CDP enable/disable relabeling, CPU hotplug domain creation/removal, monitor context exhaustion and wakeup, occupancy reads through `mpam_msmon_read()`, and teardown when MPAM disable removes a class.
