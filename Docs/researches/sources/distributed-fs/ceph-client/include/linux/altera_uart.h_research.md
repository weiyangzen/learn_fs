<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/altera_uart.h -->
# sources/distributed-fs/ceph-client/include/linux/altera_uart.h

## Purpose
`altera_uart.h` declares platform data for Altera UART devices.

## Important APIs, types, and functions
`struct altera_uart_platform_uart` carries the physical MMIO base, IRQ, UART clock rate, and bus address shift/stride.

## Control flow
Platform setup passes the struct to the serial driver, which maps the UART, configures baud from `uartclk`, applies register stride from `bus_shift`, and uses the IRQ for interrupt-driven I/O.

## State and persistence behavior
The header stores no state. The platform data persists as device configuration during driver lifetime.

## Dependencies and integration points
It integrates board/platform descriptions with the Altera UART serial driver.

## Risks and test signals
Risks include incorrect clock causing baud errors, wrong bus shift corrupting register access, and IRQ/base mismatches. Test signals include probe, baud-rate validation, interrupt-driven RX/TX, and polling/console use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/altera_uart.h -->
