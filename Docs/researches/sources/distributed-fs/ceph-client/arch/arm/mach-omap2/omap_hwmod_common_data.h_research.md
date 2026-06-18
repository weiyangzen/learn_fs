# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_common_data.h

## Purpose
`omap_hwmod_common_data.h` declares shared OMAP2xxx hwmod objects, OCP interface descriptors, hwmod classes, and common display attributes for use by SoC-specific hwmod data files. It is a cross-file contract for older OMAP hwmod tables.

## Important APIs, Types, and Functions
The header declares common `struct omap_hwmod` instances for L3/L4 interconnect, MPU, timers, watchdog, UARTs, DSS blocks, GPIOs, McSPI, GPMC, RNG, SHAM, and AES. It also declares `struct omap_hwmod_ocp_if` links, classes such as `l3_hwmod_class`, `omap2_uart_class`, `omap2_dss_hwmod_class`, and `omap2xxx_gpio_hwmod_class`, plus `omap2_3_dss_dispc_dev_attr`.

## Control Flow
There is no runtime control flow in the header. Its declarations let per-SoC C files compose link arrays and reuse class descriptors. The eventual control flow happens when init code calls `omap_hwmod_register_links()` with arrays containing these declared objects.

## State and Persistence Behavior
The header owns no state. It binds compilation units to shared statically initialized descriptors whose runtime effects are PRCM and sysconfig register programming by the hwmod layer.

## Dependencies and Integration Points
It includes `omap_hwmod.h`, `common.h`, and `display.h`. Integration points are all OMAP2xxx hwmod files that need common bus, display, timer, serial, GPIO, crypto, and GPMC definitions.

## Risks
Changing declarations without matching definitions breaks builds. Renaming or removing shared hwmods can silently destabilize SoC link arrays or DT auxdata paths if only one platform is tested.

## Test Signals
Compile all OMAP2xxx/3xxx configurations that include hwmod support. Useful signals are no unresolved symbols, correct device registration for common modules, and successful display, timer, UART, GPIO, crypto, and GPMC probe on OMAP2-family boards.
