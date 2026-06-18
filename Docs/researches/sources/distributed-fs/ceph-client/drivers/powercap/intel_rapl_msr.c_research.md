# sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_msr.c

Purpose: RAPL backend for MSR-based Intel, AMD, and Hygon platforms. It supplies MSR register maps, primitive bit layouts, platform defaults, CPU matching, and hotplug package creation for the common RAPL layer.

Important APIs/types/functions: `rapl_msr_probe()`, `rapl_msr_remove()`, `rapl_cpu_online()`, `rapl_cpu_down_prep()`, `rapl_msr_read_raw()`, `rapl_msr_write_raw()`, `rapl_check_unit_atom()`, `set_floor_freq_atom()`, and `rapl_compute_time_window_atom()`. Static `rapl_if_priv` instances describe Intel and AMD/Hygon register availability. `rpi_msr[]` maps RAPL primitives to MSR masks and shifts.

Control flow: module init registers a platform driver, matches the boot CPU against `rapl_ids`, and creates an `intel_rapl_msr` platform device with the selected defaults. Probe selects vendor-specific `rapl_if_priv`, installs raw read/write callbacks, attaches defaults and primitive descriptors, enables PL4 or MSR PMU support when requested by CPU defaults, registers the `intel-rapl` powercap control type, and installs a dynamic CPU hotplug state. CPU-online creates a common-layer package when the first CPU for that package/die appears; CPU-down removes the package when its cpumask becomes empty.

State and persistence: global `rapl_msr_priv` is the active backend descriptor and `rapl_msr_pmu` gates PMU registration. Per-package state lives in common RAPL structures. The write path uses `smp_call_function_single()` to update MSRs on the selected CPU with read-modify-write semantics; PMU reads can use direct `rdmsrq()` when already executing in the PMU context.

Dependencies/integration: depends on x86 CPU model tables, `asm/msr.h`, Intel family macros, IOSF MBI for Atom floor-frequency control, CPU hotplug, powercap, and common RAPL exported symbols. AMD/Hygon support is monitoring-oriented with package and core energy status registers.

Risks: CPU model defaults must match actual MSR layouts; PL4 and SPR Psys layout fixups require correct feature flags; Atom unit conversion differs from core CPUs; floor-frequency IOSF writes cache an original static value; CPU hotplug ordering must keep `lead_cpu` valid for MSR access; failed platform-device registration is logged but module init still succeeds.

Test signals: verify CPU model table coverage, module/device probe, powercap zones for each online package/die, hotplug add/remove, PL4 sysfs exposure on selected CPUs, PMU event exposure on PMU-capable defaults, AMD/Hygon energy reads, and Atom unit/time-window conversion on applicable systems.
