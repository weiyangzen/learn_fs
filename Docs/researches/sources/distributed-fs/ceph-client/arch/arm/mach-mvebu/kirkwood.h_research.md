<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.h

Purpose: Kirkwood physical register definition header shared by platform initialization and PM. It centralizes the CPU control, DDR operation, and memory power-control addresses.

Important APIs/types/functions: The exported constants are `DDR_OPERATION_BASE`, `MEMORY_PM_CTRL_PHYS`, and `CPU_CONTROL_PHYS`; there are no functions or types.

Control flow, state, and persistence: State is not stored here; consumers use these constants for `ioremap` or platform resources.

Dependencies and integration points: The exported constants are `DDR_OPERATION_BASE`, `MEMORY_PM_CTRL_PHYS`, and `CPU_CONTROL_PHYS`; there are no functions or types. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: The risk is stale SoC address data because the constants directly select hardware registers. Test users through cpufreq resource registration and Kirkwood standby/cpuidle paths.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 19 lines, 609 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/kirkwood.h -->
