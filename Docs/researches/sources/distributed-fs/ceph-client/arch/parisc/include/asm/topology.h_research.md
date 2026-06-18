<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/topology.h

Source read size: 19 lines, 402 bytes.

Purpose: selects generic architecture topology support when configured and provides no-op topology hooks otherwise. Important APIs: `init_cpu_topology()`, `store_cpu_topology()`, and `reset_cpu_topology()` in non-generic builds, plus inclusion of `asm-generic/topology.h`. Control flow: boot CPU topology setup either delegates to `linux/arch_topology.h` or compiles to empty inline calls. State and persistence: no state here; topology state is owned by generic topology code when enabled. Dependencies and integration points: integrates with scheduler topology, CPU masks, and optional `arch/parisc/kernel/topology.c`. Risks: no-op fallback means scheduler and sysfs topology may be flat on builds without `CONFIG_GENERIC_ARCH_TOPOLOGY`. Test signals: boot logs, `/sys/devices/system/cpu` topology, scheduler domain debug output, SMP hotplug if supported, and build coverage with topology enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/topology.h -->
