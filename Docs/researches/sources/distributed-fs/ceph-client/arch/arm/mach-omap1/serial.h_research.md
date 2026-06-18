<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.h

## Purpose
Defines OMAP1 serial constants used by debug low-level code and UART platform setup, including scratch offset, register shifts, base baud values, and encoded UART IDs.

## Important APIs, Types, and Functions
Provides `OMAP_UART_INFO_OFS`, `OMAP_PORT_SHIFT`, `OMAP7XX_PORT_SHIFT`, `OMAP1510_BASE_BAUD`, `OMAP16XX_BASE_BAUD`, `OMAP1UART1/2/3`, and declaration `omap_serial_init()`.

## Control Flow
No runtime flow. Boot/decompress/debug code and `serial.c` consume the constants to locate and configure UARTs.

## State and Persistence Behavior
No state. The `OMAP_UART_INFO_OFS` describes a RAM scratch location used by debug/uncompress paths.

## Dependencies and Integration Points
Integrates with DEBUG_LL `uncompress.h` and `debug-macro.S`, plus OMAP1 8250 registration.

## Risks
The scratch offset must not overlap decompressor memory. Wrong base baud or register shift breaks early console and 8250 autoconfig.

## Test Signals
Build DEBUG_LL for UART1/2/3 and confirm early `printascii` output before paging and normal 8250 console after boot.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.h -->
