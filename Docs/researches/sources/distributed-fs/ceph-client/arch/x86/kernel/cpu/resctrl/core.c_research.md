# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/core.c

## Purpose

This file is the x86 architecture backend for resctrl resource discovery, domain lifetime, CPU hotplug, default control programming, and boot-time option handling. It turns CPUID/MSR capabilities into `struct rdt_resource` instances for L3/L2 CAT, MBA/SMBA, L3 monitoring, and package telemetry, then registers them with the generic resctrl filesystem.

## Important APIs, Types, And Functions

Global state includes `rdt_resources_all[]`, `rdt_alloc_capable`, per-CPU `pqr_state`, `domain_list_lock`, and the CPU hotplug state `rdt_online`. Exported or cross-file functions include `resctrl_arch_get_resource()`, `resctrl_arch_system_num_rmid_idx()`, `resctrl_arch_get_num_closid()`, `rdt_ctrl_update()`, `resctrl_arch_pre_mount()`, `rdt_cpu_has()`, `resctrl_arch_is_evt_configurable()`, `resctrl_cpu_detect()`, and init/exit hooks. Hardware-specific helpers include CAT/MBA MSR writers, CPUID parsers, Haswell CAT probing, CDP setup, and Intel/AMD resource default initialization.

## Control Flow

`resctrl_arch_late_init()` initializes resource IDs, vendor defaults, quirks, allocation/monitoring resources, CPU hotplug callbacks, and generic `resctrl_init()`. `get_rdt_alloc_resources()` probes CAT/CDP/MBA/SMBA and configures MSR bases and CLOSID counts. `get_rdt_mon_resources()` enables monitoring events and calls `rdt_get_l3_mon_config()`. CPU hotplug callbacks add or remove control and monitor domains based on cache/node/package scopes, allocate per-domain control arrays and MBM state, update MSRs, and notify generic resctrl domain online/offline paths.

## State, Dependencies, And Integration

State is boot-lifetime kernel memory and per-domain dynamic allocations. Control-domain `ctrl_val[]` arrays mirror programmed CLOSID values. Monitor domains keep architecture-private MBM state. CPU hotplug mutations are protected by `domain_list_lock`, RCU list deletion, and cpus-read locking where required. Dependencies include CPUID, MSR accessors, topology/cacheinfo, CPU hotplug, Intel AET hooks, generic resctrl APIs, and x86 vendor/model quirks.

## Risks And Test Signals

Risk centers on incorrect resource enumeration, wrong MSR base/update callback, per-domain CPU mask handling, and hotplug lifetime. Haswell probing and Skylake/Broadwell MBM quirks are model-sensitive. CDP and AMD per-CPU config require updating the right CPU set. Test by booting on Intel and AMD systems with `rdt=` force-on/off options, mounting resctrl, verifying `info/` resource files, changing schemata, CPU hotplugging, enabling AET during mount, and checking that PQR_ASSOC resets on online/offline paths.
