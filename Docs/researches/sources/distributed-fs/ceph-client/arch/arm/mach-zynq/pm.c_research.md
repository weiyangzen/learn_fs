# sources/distributed-fs/ceph-client/arch/arm/mach-zynq/pm.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-zynq/pm.c` provides platform power-management code for Xilinx Zynq-7000 platform support. It consumes or advertises OF compatible strings `xlnx,zynq-ddrc-a05` to find syscon/MMIO nodes, match machine descriptors, or register CPU bring-up methods.

## Important APIs, Types, and Functions
Important functions and entry points are `zynq_pm_late_init`. Important structs/types referenced or defined are `device_node`. File-scope platform state and tables include `reg`. Preprocessor/register symbols defined here include `DDRC_CTRL_REG1_OFFS`, `DDRC_DRAM_PARAM_REG3_OFFS`, `DDRC_CLOCKSTOP_MASK`, `DDRC_SELFREFRESH_MASK`. Machine descriptors are none; OF compatible strings visible in the file are `xlnx,zynq-ddrc-a05`. Headers imported by the file include `linux/io.h`, `linux/of.h`, `linux/of_address.h`, `common.h`

## Control Flow
Power-management flow is entered from suspend, cpuidle, MCPM, or platform late-init hooks. The code maps controller registers, saves state needed across low-power entry, programs wake or reset vectors, disables caches/SCU where needed, and restores hardware state on resume before generic kernel execution continues.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as `reg`. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include `linux/io.h`, `linux/of.h`, `linux/of_address.h`, `common.h` plus platform integration with Zynq DT machine setup, SLCR syscon/regmap access, SCU mapping, SMP trampoline copying, CPU start/stop state, restart notifier, cpuidle registration, and DDR self-refresh suspend setup. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/boot/dts/xilinx/zynq-7000.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/pm.c`, `sources/distributed-fs/ceph-client/drivers/edac/synopsys_edac.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: SLCR unlock/write ordering errors, trampoline address or cache-flush mistakes, stale CPU state bits across hotplug, wrong OCM/DDR controller discovery, and suspend support depending on unavailable PM services. Additional file-specific risks: suspend paths can lose wake masks, resume addresses, or controller state; compatible-string changes can orphan existing board DTBs.

## Test Signals
ARCH_ZYNQ builds, Zynq DT boot, CPU1 online/offline/hotplug, restart behavior, cpuidle registration, suspend entry when enabled, and SLCR syscon compatible validation. Exercise suspend/resume, wake-source delivery, cpuidle state entry, and lockdep/RCU warnings around low-power transitions.
