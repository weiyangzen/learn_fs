<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-generic.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-generic.c

## Purpose
Provides generic Device Tree machine descriptors for OMAP2/3/4/5, AM33xx, AM43xx, DRA7, TI81xx, and special N900 handling, wiring early init, IO mapping, timers, IRQs, restart, and machine init callbacks.

## Important APIs, Types, and Functions
Defines many `DT_MACHINE_START` descriptors, `omap_generic_init()`, `omap_init_time_of()`, optional `tick_broadcast()`, N900 ATAG helpers, and compatibility arrays.

## Control Flow
For each compatible family, the ARM machine descriptor calls reserve/map_io/init_early/init_irq/init_machine/init_late/init_time/restart callbacks appropriate for that SoC. `omap_generic_init()` applies pdata quirks and registers the SoC device. `omap_init_time_of()` initializes clocks and probes DT timers. N900 reserve saves ATAGs and system revision before normal OMAP reserve.

## State and Persistence Behavior
Machine descriptors are init data. Runtime state affected includes saved ATAGs for N900, `system_rev`, registered SoC device, clocks, timers, and pdata quirks.

## Dependencies and Integration Points
Depends on common OMAP init functions, DT compatible strings, irqchip init, timer probe, L2 cache secure write hooks, SMP ops, restart functions, and pdata quirks.

## Risks
Compatible-string ordering determines which machine descriptor matches. Wrong callbacks can select wrong IO map, restart, timer, or IRQ path. N900 preserves legacy userspace contracts via `/proc/atags` and board name.

## Test Signals
Boot DTBs for each compatible family and verify selected machine name, clock/timer init, irqchip, restart behavior, and SoC device registration. N900 tests should verify ATAG export and `system_rev`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/board-generic.c -->
