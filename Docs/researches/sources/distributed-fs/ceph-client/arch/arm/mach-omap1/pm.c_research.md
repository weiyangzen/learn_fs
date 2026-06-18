<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.c

## Purpose
Implements OMAP1 idle and suspend-to-RAM support, including dynamic idle sysfs control, wake-source masking, register save/restore, SRAM suspend function installation, and debugfs PM register reporting.

## Important APIs, Types, and Functions
Exports/defines `omap1_pm_idle()` and `omap1_pm_suspend()`. Kernel integration points include `platform_suspend_ops`, `arm_pm_idle`, sysfs `power/sleep_while_idle`, debugfs `pm_debug/omap_pm`, and `__initcall omap_pm_init()`.

## Control Flow
Idle disables FIQ, adjusts IDLECT masks for timers and DMA activity, either performs shallow WFI with temporary IDLECT writes or calls the SRAM suspend routine. Suspend enables serial wake muxing, disables IRQ/FIQ, saves MPUI/ARM/ULPD/DSP registers, stops DSP clocks, programs wake masks, disables watchdog, calls SRAM assembly, restores clocks/registers/masks, re-enables interrupts, and restores serial muxing. Init installs SRAM-copied suspend code, sets idle/suspend ops, requests wake IRQ, configures ULPD/IDLECT3, creates debugfs/sysfs, and muxes `LOW_PWR` on 16xx.

## State and Persistence Behavior
Static save arrays hold ARM, DSP, ULPD, and MPUI register snapshots. `enable_dyn_sleep` persists the sysfs idle policy, and `omap_sram_suspend` points at executable SRAM code. Hardware state includes interrupt masks, clock/idlect registers, DSP reset/clock state, watchdog mode, ULPD power control, and serial wake muxing.

## Dependencies and Integration Points
Depends on DMA activity checks, timer capability macros, `sleep.S` routines copied by `sram-init.c`, mux entries, serial wake helpers, interrupt numbers, clocksource timer helpers, suspend core, debugfs, and CPU predicates.

## Risks
Suspend touches many always-on and memory-controller registers with IRQs disabled; wrong save/restore ordering can hang resume. Dynamic idle is only enabled when 32k and DMTIMER support exist. Wake masks are board-generic and may miss board-specific wake sources.

## Test Signals
Run suspend/resume and idle tests on OMAP15xx and OMAP16xx with serial, GPIO/keypad, UART2, and peripheral wake. Validate `sleep_while_idle` accepts only 0/1, debugfs register snapshots update, and active DMA prevents deep idle.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm.c -->
