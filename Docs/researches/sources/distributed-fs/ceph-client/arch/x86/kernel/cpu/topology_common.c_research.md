# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_common.c

## Purpose
Builds the common x86 CPU topology model from CPUID/APIC data and initializes global topology metadata used by scheduler, CPU hotplug, cache, and package/die/core ID code.

## Important APIs, Types, And Functions
Exports `x86_topo_system` and `__amd_nodes_per_pkg`. `topology_set_dom()` updates one topology domain and propagates defaults upward. `get_topology_cpu_type()` and `get_topology_cpu_type_name()` classify Intel/AMD hybrid CPUs. `cpu_parse_topology()` validates per-CPU topology after APIC setup, and `cpu_init_topology()` seeds boot-time global domain shifts and sizes.

## Control Flow
`parse_topology()` starts with safe defaults, handles CPUID-less/Xen PV fake topology, reads CPUID leaf 1 initial APIC ID, then dispatches to AMD/Hygon, Intel extended topology, or legacy core parsing. The boot CPU path stores global domain shifts in `x86_topo_system`; later CPUs recompute and warn if domain shifts or APIC IDs disagree.

## State, Persistence, And Dependencies
State is boot-lifetime kernel state: `cpuinfo_x86.topo`, global topology shifts/sizes, APIC-to-logical IDs, AMD node counts, and exported masks. It depends on CPUID helpers, APIC access, SMP topology registration, and vendor-specific parsers in sibling CPU code.

## Integration Points
Feeds scheduler topology, CPU masks, sysfs topology, cache IDs, AMD node handling, and firmware bug diagnostics. Intel extended parsing is delegated to `cpu_parse_topology_ext()`, while AMD fixups are delegated to AMD topology helpers.

## Risks
Malformed firmware/APIC/CPUID data can cause wrong package/core/die IDs. Legacy parsing depends on core counts and HT bits matching CPUID leaf 1. Early mode uses initial APIC ID because APIC mapping is not yet ready.

## Test Signals
Boot logs should not show APIC mismatch or topology-domain shift firmware bugs. CPU hotplug should produce stable logical package/die/core IDs across all CPUs. Hybrid Intel/AMD systems should report expected CPU type names.
