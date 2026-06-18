# sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.h

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.h` provides internal platform header for Xilinx Zynq-7000 platform support. It is part of the board-support layer that bridges generic ARM kernel code to SoC-specific registers, firmware conventions, and Devicetree-described devices.

## Important APIs, Types, and Functions
Important functions and entry points are `zynq_core_pm_init`. Important structs/types referenced or defined are `smp_operations`. File-scope platform state and tables include none. Preprocessor/register symbols defined here include `__MACH_ZYNQ_COMMON_H__`. Machine descriptors are none; OF compatible strings visible in the file are none. Headers imported by the file include none

## Control Flow
Control flow is callback-oriented: generic ARM init, irqchip, clocksource, SMP, cpuidle, restart, or platform bus code calls the local functions `zynq_core_pm_init` when the matching machine, syscon, or CPU method is active.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as no named file-scope state detected. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include no C includes because this is Kconfig/Makefile data plus platform integration with Zynq DT machine setup, SLCR syscon/regmap access, SCU mapping, SMP trampoline copying, CPU start/stop state, restart notifier, cpuidle registration, and DDR self-refresh suspend setup. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/platsmp.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: SLCR unlock/write ordering errors, trampoline address or cache-flush mistakes, stale CPU state bits across hotplug, wrong OCM/DDR controller discovery, and suspend support depending on unavailable PM services. Additional file-specific risks: edits can desynchronize the platform code from generic ARM expectations and board DT data.

## Test Signals
ARCH_ZYNQ builds, Zynq DT boot, CPU1 online/offline/hotplug, restart behavior, cpuidle registration, suspend entry when enabled, and SLCR syscon compatible validation. Use DT boot smoke tests, earlycon logs, `dtbs_check` for matching board files, and probe logs for devices populated from the machine descriptor.
