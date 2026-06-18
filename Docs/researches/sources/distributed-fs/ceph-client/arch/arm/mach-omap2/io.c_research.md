<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/io.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/io.c

## Purpose
`io.c` defines static IO mappings and early/late initialization flows for OMAP2/3/4/5, TI81xx, AM33xx/AM43xx, and DRA7. It maps interconnect windows, initializes clocks, hwmods, control base, SDRC/GPMC memory support, PRM/CM, powerdomains, and late PM/display-related platform state.

## Important APIs, Types, and Functions
Public mapping functions include `omap242x_map_io()`, `omap243x_map_io()`, `omap3_map_io()`, `ti81xx_map_io()`, `am33xx_map_io()`, `omap4_map_io()`, `omap5_map_io()`, and `dra7xx_map_io()`. Public init functions include `omap2420_init_early()`, `omap2430_init_early()`, `omap3430_init_early()`, `omap3630_init_early()`, `am35xx_init_early()`, `ti814x_init_early()`, `ti816x_init_early()`, `am33xx_init_early()`, `am43xx_init_early()`, `omap4430_init_early()`, `omap5_init_early()`, `dra7xx_init_early()`, corresponding late init helpers, and `omap_clk_init()`.

## Control Flow
Map functions call `iotable_init()` with SoC-specific `map_desc` arrays. Early init functions set TAP globals, initialize SoC revision/features, clock/PRM/CM/powerdomain infrastructure, control-module base, hwmods, and SoC-specific PM prerequisites. Late init paths typically perform GPMC/SDRC or control/device PM finalization. `omap_hwmod_init_postsetup()` optionally forces hwmods into a configured postsetup state.

## State and Persistence Behavior
The file establishes permanent static virtual mappings for early MMIO windows and boot-time global subsystem state. It does not write persistent storage, but it configures hardware modules and global framework state that remain active for the kernel lifetime.

## Dependencies and Integration Points
It depends on ARM `map_desc`/`iotable_init`, SoC address headers, clock init, PRM/CM, powerdomain/clockdomain, hwmod, control, SDRC, GPMC, PM, id, and device init helpers. It is integrated from machine descriptors and is upstream of almost every OMAP platform subsystem.

## Risks
Mapping size/base errors can cause early boot aborts or MMIO aliasing. Init ordering is fragile: SoC detection, clocks, PRM/CM, control base, hwmods, and PM must be initialized in the expected sequence. Multi-OMAP builds are especially sensitive to running the wrong SoC path.

## Test Signals
Boot each machine descriptor path with earlycon and dynamic debug enabled. Validate `/proc/iomem`, no early ioremap faults, correct SoC revision output, clock and hwmod registration, working interrupts/timers, and successful late init. Compile coverage should include all configured SoC families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/io.c -->
