# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology.c

## Purpose

This file maintains early x86 CPU/APIC topology registration, CPU-number allocation, topology-domain bitmaps, logical ID queries, CPU hotplug APIC handling, and possible/present CPU mask initialization. It provides a unified topology view across package, die, tile, module, core, and SMT domains.

## Important APIs, Types, And Functions

Important globals are early per-CPU `x86_cpu_to_apicid`, `x86_cpu_to_acpiid`, `phys_cpu_present_map`, `cpuid_to_apicid[]`, domain `apic_maps[]`, and `topo_info`. Public APIs include `arch_match_cpu_phys_id()`, `topology_register_apic()`, `topology_register_boot_apic()`, `topology_get_logical_id()`, `topology_unit_count()`, `topology_get_primary_thread()`, ACPI hotplug helpers, `topology_apply_cmdline_limits_early()`, `topology_init_possible_cpus()`, and `topology_reset_possible_cpus_up()`.

## Control Flow

Firmware or guest enumeration registers APIC IDs early. The boot APIC reserves CPU0; later APICs receive stable CPU numbers unless limits reject them. Domain bitmaps store normalized APIC IDs at each topology level. BSP sanity checks detect crash-kernel scenarios and broken firmware enumeration to avoid INITing the real BSP. Possible CPU initialization computes maximum packages/nodes/dies/threads, applies command-line limits, assigns disabled hotplug CPUs, and populates present/possible masks.

## State, Dependencies, And Integration

State is mostly `__ro_after_init` or early per-CPU mappings, with hotplug updates for present APICs. Dependencies include APIC, ACPI/MPTABLE enumeration, Xen PV handling, NUMA, SMP masks, MSRs, and x86 topology parser output. It integrates with scheduler topology, CPU hotplug, perf/uncore topology users, and `/proc/cpuinfo`.

## Risks And Test Signals

Risks include APIC ID overflow, duplicate or out-of-order BSP enumeration, CPU-number exhaustion, disabled APIC handling, and incorrect domain shift assumptions. Test with maxcpus/nosmp/nolapic/possible_cpus options, Xen PV guests, ACPI CPU hotplug, kdump kernels, large APIC IDs, multi-die systems, and logical ID/unit count consumers.
