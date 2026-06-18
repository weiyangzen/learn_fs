<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/devices.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/devices.c

Purpose: Early SPARC32 PROM device scan helpers for CPU node lookup and AUXIO/power discovery.

Important APIs and control flow: `cpu_mid_prop()` selects `cpu-id` on sun4d and `mid` otherwise. `__cpu_find_by()` iterates OF CPU nodes with comparison callbacks; `cpu_find_by_instance()` and `cpu_find_by_mid()` expose instance/MID searches, with sun4m MID truncation compatibility. `cpu_get_hwmid()` returns the full hardware MID. `device_scan()` prints the boot banner, initializes CPU0 clock tick on non-SMP by reading the first CPU node, then probes AUXIO and AUXIO power control.

State, dependencies, and risks: state updated includes `cpu_data(0).clock_tick` and global AUXIO mappings through called probes. Dependencies include PROM/OF CPU nodes, CPU model, `auxio_probe()`, `auxio_power_probe()`, and SMP conditionals. Risks include halting if no CPU node on non-SMP, sun4m MID truncation ambiguity, and relying on PROM property names. Test signals are boot on sun4m/sun4d, CPU instance/MID lookup for SMP bring-up, CPU clock reporting, and AUXIO/power probe side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/devices.c -->
