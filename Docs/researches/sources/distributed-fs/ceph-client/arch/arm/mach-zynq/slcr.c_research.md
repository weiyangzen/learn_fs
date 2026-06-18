# sources/distributed-fs/ceph-client/arch/arm/mach-zynq/slcr.c

## Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-zynq/slcr.c` provides reset, system-controller, or boot-vector support code for Xilinx Zynq-7000 platform support. It consumes or advertises OF compatible strings `xlnx,zynq-slcr` to find syscon/MMIO nodes, match machine descriptors, or register CPU bring-up methods.

## Important APIs, Types, and Functions
Important functions and entry points are `zynq_slcr_write`, `zynq_slcr_read`, `zynq_slcr_unlock`, `zynq_slcr_get_device_id`, `zynq_slcr_system_restart`, `zynq_slcr_cpu_start`, `zynq_slcr_cpu_stop`, `zynq_slcr_cpu_state_read`, `zynq_slcr_cpu_state_write`, `zynq_early_slcr_init`. Important structs/types referenced or defined are `regmap`, `notifier_block`, `device_node`. File-scope platform state and tables include `zynq_slcr_restart_nb`, `val`, `reboot`, `reg`, `state`. Preprocessor/register symbols defined here include `SLCR_UNLOCK_OFFSET`, `SLCR_PS_RST_CTRL_OFFSET`, `SLCR_A9_CPU_RST_CTRL_OFFSET`, `SLCR_REBOOT_STATUS_OFFSET`, `SLCR_PSS_IDCODE`, `SLCR_L2C_RAM`, `SLCR_UNLOCK_MAGIC`, `SLCR_A9_CPU_CLKSTOP`, `SLCR_A9_CPU_RST`, `SLCR_PSS_IDCODE_DEVICE_SHIFT`, `SLCR_PSS_IDCODE_DEVICE_MASK`. Machine descriptors are none; OF compatible strings visible in the file are `xlnx,zynq-slcr`. Headers imported by the file include `linux/io.h`, `linux/reboot.h`, `linux/mfd/syscon.h`, `linux/of_address.h`, `linux/regmap.h`, `common.h`

## Control Flow
Control flow is callback-oriented: generic ARM init, irqchip, clocksource, SMP, cpuidle, restart, or platform bus code calls the local functions `zynq_slcr_write`, `zynq_slcr_read`, `zynq_slcr_unlock`, `zynq_slcr_get_device_id`, `zynq_slcr_system_restart`, `zynq_slcr_cpu_start`, `zynq_slcr_cpu_stop`, `zynq_slcr_cpu_state_read`, `zynq_slcr_cpu_state_write`, `zynq_early_slcr_init` when the matching machine, syscon, or CPU method is active.

## State and Persistence Behavior
Persistent storage is not used. Runtime state is kept in file-scope mappings, flags, tables, or hardware registers such as `zynq_slcr_restart_nb`, `val`, `reboot`, `reg`, `state`. The durable contract is the DT ABI, Kconfig/Kbuild selection, and register programming sequence expected by firmware and the SoC; hardware register contents may persist across warm reset or low-power states even though the kernel does not write files.

## Dependencies and Integration Points
Dependencies include `linux/io.h`, `linux/reboot.h`, `linux/mfd/syscon.h`, `linux/of_address.h`, `linux/regmap.h`, `common.h` plus platform integration with Zynq DT machine setup, SLCR syscon/regmap access, SCU mapping, SMP trampoline copying, CPU start/stop state, restart notifier, cpuidle registration, and DDR self-refresh suspend setup. Cross-reference scans for visible symbols/compatibles found `sources/distributed-fs/ceph-client/arch/arm/boot/dts/xilinx/zynq-7000.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/common.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/platsmp.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-zynq/slcr.c`. The file depends on generic ARM infrastructure such as machine descriptors, irqchip, clocksource, SMP, cpuidle, PM, syscon/regmap, AMBA, OF address mapping, and Kbuild/Kconfig as applicable.

## Risks
Primary risks: SLCR unlock/write ordering errors, trampoline address or cache-flush mistakes, stale CPU state bits across hotplug, wrong OCM/DDR controller discovery, and suspend support depending on unavailable PM services. Additional file-specific risks: compatible-string changes can orphan existing board DTBs.

## Test Signals
ARCH_ZYNQ builds, Zynq DT boot, CPU1 online/offline/hotplug, restart behavior, cpuidle registration, suspend entry when enabled, and SLCR syscon compatible validation. Use DT boot smoke tests, earlycon logs, `dtbs_check` for matching board files, and probe logs for devices populated from the machine descriptor.
