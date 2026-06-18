# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/rdtgroup.c

## Purpose

This file contains x86 architecture hooks used by the generic resctrl group/filesystem layer. It synchronizes CLOSID/RMID state on CPUs, reads and writes configurable monitoring-event masks, toggles CDP, and resets all control MSRs for a resource.

## Important APIs, Types, And Functions

Exported hooks include `resctrl_arch_sync_cpu_closid_rmid()`, `resctrl_arch_mon_event_config_read()`, `resctrl_arch_mon_event_config_write()`, `rdt_domain_reconfigure_cdp()`, `resctrl_arch_set_cdp_enabled()`, `resctrl_arch_get_cdp_enabled()`, and `resctrl_arch_reset_all_ctrls()`. Static keys `rdt_enable_key`, `rdt_mon_enable_key`, and `rdt_alloc_enable_key` gate fast-path resctrl usage elsewhere.

## Control Flow

CPU sync updates per-CPU default CLOSID/RMID and calls `resctrl_arch_sched_in()` so the currently running task's effective state is applied safely. Monitor event configuration maps total/local MBM event IDs to `MSR_IA32_EVT_CFG_BASE` offsets. CDP toggling builds a CPU mask from control domains and writes L2/L3 QOS_CFG MSRs either once per domain or per CPU for AMD-style per-CPU config. Resetting controls fills each domain's cached values with defaults and programs the full CLOSID range.

## State, Dependencies, And Integration

State includes static keys, per-CPU `pqr_state`, `rdt_hw_resource::cdp_enabled`, cached domain control values, and hardware QOS MSRs. Dependencies are generic resctrl group logic, MSR writes, CPU masks, and hotplug read locking. It integrates directly with mount options, schemata resets, CDP enable/disable operations, and monitoring event configuration files.

## Risks And Test Signals

Risks include writing QOS_CFG on too few CPUs, races with CPU hotplug, invalid configurable event IDs, and stale cached control values after reset. Test CDP mount/remount flows, monitor event config writes, schemata reset, per-task scheduling changes, AMD per-CPU config hardware, and CPU hotplug while resctrl is mounted.
