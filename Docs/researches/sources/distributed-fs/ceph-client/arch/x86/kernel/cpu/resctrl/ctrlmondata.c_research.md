# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/ctrlmondata.c

## Purpose

This file implements architecture-specific control update helpers for resctrl schemata writes and AMD I/O allocation enablement. It bridges generic staged resctrl configurations to x86 QOS MSR writes.

## Important APIs, Types, And Functions

Important APIs are `resctrl_arch_update_one()`, `resctrl_arch_update_domains()`, `resctrl_arch_get_config()`, `resctrl_arch_get_io_alloc_enabled()`, and `resctrl_arch_io_alloc_enable()`. It uses `struct rdt_hw_ctrl_domain`, `struct rdt_hw_resource`, `struct msr_param`, and staged config arrays from the generic resctrl layer.

## Control Flow

`resctrl_arch_update_one()` validates that the caller is executing on a CPU in the target domain, updates the cached `ctrl_val` entry, and writes a single MSR range through the resource's `msr_update()` callback. `resctrl_arch_update_domains()` walks all control domains under the CPU hotplug read lock, collects changed staged CDP/non-CDP config entries for one CLOSID, updates cached values, and sends `rdt_ctrl_update()` to one CPU in each domain. AMD SDCIAE enablement writes or clears bit 1 of `MSR_IA32_L3_QOS_EXT_CFG` on all CPUs in all control domains.

## State, Dependencies, And Integration

The persistent runtime state is the per-domain `ctrl_val[]` cache plus `rdt_hw_resource::sdciae_enabled`. It depends on CPU mask IPIs, MSR helpers, generic resctrl staging, and `internal.h` conversion helpers. It integrates with resctrl filesystem schemata writes and I/O allocation toggles.

## Risks And Test Signals

Incorrect index calculation can program the wrong CLOSID or CDP half. The CPU-mask assertions matter because domain lists can change during hotplug. SDCIAE must be updated on every CPU when hardware state is per-CPU. Test by writing schemata for CAT/MBA/SMBA, toggling I/O allocation on AMD systems with SDCIAE, hotplugging CPUs, and reading back config through resctrl's info and schema paths.
