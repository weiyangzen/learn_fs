# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/monitor.c

## Purpose

This file implements x86 resctrl monitoring: RMID reads, MBM overflow correction, Sub-NUMA Cluster RMID translation, L3 monitoring capability setup, Intel MBM correction quirks, and AMD bandwidth-monitor event/counter assignment support.

## Important APIs, Types, And Functions

Cross-file APIs include `resctrl_arch_rmid_read()`, `resctrl_arch_reset_rmid()`, `resctrl_arch_reset_rmid_all()`, `arch_mon_domain_online()`, `rdt_get_l3_mon_config()`, `intel_rdt_mbm_apply_quirk()`, `resctrl_arch_mbm_cntr_assign_set()`, `resctrl_arch_mbm_cntr_assign_enabled()`, `resctrl_arch_config_cntr()`, and `resctrl_arch_mbm_cntr_assign_set_one()`. Important helpers include `logical_rmid_to_physical_rmid()`, `__rmid_read_phys()`, `get_corrected_val()`, `__cntr_id_read()`, and the MBM correction-factor table.

## Control Flow

Monitor reads program `MSR_IA32_QM_EVTSEL`, read `MSR_IA32_QM_CTR`, reject error/unavailable bits, and convert raw values to bytes. MBM events use per-RMID `arch_mbm_state` to accumulate wraparound deltas and optional Intel correction factors. SNC mode changes L3 monitor scope to node and maps logical RMIDs into physical RMID partitions. AET package resources delegate reads to `intel_aet_read_event()`. ABMC support toggles `MSR_IA32_L3_QOS_EXT_CFG`, assigns counters through `MSR_IA32_L3_QOS_ABMC_CFG`, and reads counters through extended event IDs.

## State, Dependencies, And Integration

State includes global `rdt_mon_capable`, SNC node count, correction-factor threshold/value, per-resource monitor scale/width, per-domain MBM arrays, and ABMC enable state. Dependencies include CPUID, MSR access, CPU model matching, topology NUMA/package helpers, generic resctrl monitor event APIs, and Intel AET.

## Risks And Test Signals

Wrong RMID width, scale, SNC translation, or MBM overflow handling yields misleading monitoring data. ABMC toggles are domain-wide and must reset state consistently. Intel correction factors are model/RMID-count dependent. Test by mounting resctrl, reading `mon_data` occupancy and MBM files under traffic, exercising SNC systems, toggling ABMC counter assignment, configuring BMEC event masks, and validating unavailable/error returns under invalid RMIDs.
