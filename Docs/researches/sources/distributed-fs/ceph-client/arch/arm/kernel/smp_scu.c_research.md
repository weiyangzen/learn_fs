# sources/distributed-fs/ceph-client/arch/arm/kernel/smp_scu.c

Purpose: controls the ARM Snoop Control Unit used by older MPCore/Cortex-A SMP systems for coherency and CPU count discovery.

Important APIs/types/functions: helpers include `scu_enable`, `scu_get_core_count`, `scu_power_mode`, and DT mapping helpers when configured.

Control flow: enable maps or receives SCU base, invalidates SCU tags/filters as required, sets the enable bit, and returns core count from SCU config. Power-mode helper adjusts per-CPU SCU power state.

State and persistence: SCU MMIO registers persist hardware coherency and power settings.

Dependencies and integration: platform SMP prepare code, device tree address mapping, cache coherency, and secondary CPU boot.

Risks: enabling SCU at the wrong time or with wrong base breaks coherency; power-mode writes are platform-sensitive. Test signals include SMP boot on SCU systems, cache coherency stress, and CPU hotplug/power mode transitions.
