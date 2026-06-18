<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.c

## Purpose
Initializes OMAP1 internal UARTs as 8250 platform ports, manages UART clocks and reset/autoconfiguration, and optionally reroutes UART RX pins to GPIO wake inputs during deep sleep.

## Important APIs, Types, and Functions
Defines `omap_serial_init()`, platform registration `arch_initcall omap_init()`, and under `CONFIG_OMAP_SERIAL_WAKE`, `omap_serial_wake_trigger()` plus `omap_serial_wakeup_init()`.

## Control Flow
Early serial init adjusts baud clocks for 15xx, ioremaps each UART, gets/enables its clock, programs clock rates, and resets UART registers for 8250 autoconfig. The later arch init registers the `serial8250` platform device. Wake support requests GPIO wake descriptors/IRQs and toggles mux entries between UART RX and GPIO before/after suspend.

## State and Persistence Behavior
Static clock pointers record which UARTs were initialized. `serial_platform_data[]` persists mapbase, membase, IRQ, and clock settings. Wake GPIO descriptors are acquired during wake init and IRQ wake is enabled.

## Dependencies and Integration Points
Depends on 8250 platform driver, clock names `uart1_ck`/`uart2_ck`/`uart3_ck`, mux entries, GPIO descriptors named `wakeup`, IRQ macros, and PM hooks in `pm.c`.

## Risks
UART2 pins can conflict with USB2 on Innovator-1510. Clock get failures are logged but port reset still proceeds if mapped. Wake muxing only supports OMAP16xx and assumes GPIO lookup tables are provided.

## Test Signals
Boot with early console and 8250 console on each UART, verify clock rates on 15xx/16xx, suspend/resume with serial wake enabled, and test USB2/UART2 pin-conflict board configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/serial.c -->
