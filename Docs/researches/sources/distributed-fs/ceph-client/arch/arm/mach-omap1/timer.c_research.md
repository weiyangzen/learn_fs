<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer.c

## Purpose
Registers OMAP16xx dual-mode timer platform devices and provides a low-level hook for selecting each timer input clock source.

## Important APIs, Types, and Functions
Defines `omap1_dm_timer_set_src()` and `arch_initcall omap1_dm_timer_init()` that creates eight `omap_timer` platform devices.

## Control Flow
Init exits unless CPU is OMAP16xx. It loops timer IDs 1-8, maps each ID to a base address and IRQ, allocates a platform device, adds MEM/IRQ resources, allocates DMTIMER platform data, sets `set_timer_src` and capability flags, attaches data, and registers the device. Clock-source selection updates two-bit fields in `MOD_CONF_CTRL_1` based on timer ID.

## State and Persistence Behavior
No global state after registration beyond platform devices and their copied platform data. Hardware state changes when clients call `set_timer_src`.

## Dependencies and Integration Points
Depends on DMTIMER platform data, `clocksource/timer-ti-dm.h`, OMAP16xx IRQ macros, `MOD_CONF_CTRL_1`, and platform bus.

## Risks
Partial failure stops registration and frees only the current pdev/pdata; already registered timers remain. Timer base/IRQ mapping must match OMAP16xx documentation.

## Test Signals
On OMAP16xx, verify eight `omap_timer` devices probe, each IRQ fires, and clock-source changes update `MOD_CONF_CTRL_1`. Non-16xx boot should skip registration cleanly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/timer.c -->
