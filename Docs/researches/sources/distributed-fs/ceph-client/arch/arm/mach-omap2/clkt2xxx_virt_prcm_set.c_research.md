<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_virt_prcm_set.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_virt_prcm_set.c

## Purpose
Implements the virtual OMAP2xxx `virt_prcm_set` clock used for legacy DVFS/cpufreq rate-set changes across MPU, DPLL, module dividers, and SDRC timing.

## Important APIs, Types, and Functions
Exports globals `curr_prcm_set` and `rate_table`, and defines `omap2xxx_clkt_vps_init()` for DT clock init. Clock ops include recalc, determine_rate, and set_rate helpers.

## Control Flow
Late init captures immutable `sys_ck` rate, checks bootloader-selected DPLL/core rate to choose `curr_prcm_set`, registers a synthetic `virt_prcm_set` clock parented by `mpu_ck`, and creates a `cpufreq_ck` clkdev alias. Rate determination scans `rate_table` for the highest allowed MPU rate no greater than requested, matching CPU mask and crystal. Set-rate picks the PRCM config, updates module dividers, switches SDRC to safe x2 timing, calls SRAM PRCM programming, reinitializes SDRC DLL state, and switches to final core source under IRQ disable.

## State and Persistence Behavior
Global state includes `cpu_mask`, `curr_prcm_set`, `rate_table`, and captured `sys_ck_rate`. Hardware state includes CM dividers, DPLL, SDRC refresh/DLL state, and IRQ-disabled transition window.

## Dependencies and Integration Points
Depends on clock framework, clkdev, cpufreq consumers, OMAP2xxx PRCM config tables, CM helpers, SDRC, SRAM PRCM programming, and CPU detection.

## Risks
If `sys_ck` lookup fails, rate matching can fail. `curr_prcm_set` and `rate_table` must be initialized by SoC clock data before use. Frequency changes are tightly coupled to memory timing and can hang if a table entry is wrong.

## Test Signals
Verify `cpufreq_ck` registration and rate changes on OMAP2420/2430 with different crystal rates. Test bootloader-rate detection, invalid requested rates, and memory/timer stability through transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/clkt2xxx_virt_prcm_set.c -->
