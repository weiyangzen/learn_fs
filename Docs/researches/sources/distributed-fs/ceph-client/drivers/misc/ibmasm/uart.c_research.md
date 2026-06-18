# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/uart.c

## Purpose
`uart.c` optionally registers the IBM ASM service processor's Scout COM B UART as an 8250 serial port when the service processor allows OS ownership.

## Important APIs, Types, and Functions
Public functions are `ibmasm_register_uart()` and `ibmasm_unregister_uart()`. It uses `struct uart_8250_port`, serial 8250 registration helpers, UART scratch register `UART_SCR`, and low-level UART interrupt enable/disable helpers.

## Control Flow
Registration reads the UART scratch register at `SCOUT_COM_B_BASE`; zero means the service processor owns the UART, so the driver records `serial_line = -1` and returns. Otherwise it initializes a memory-mapped shared-IRQ 8250 port with a 3.6864 MHz clock, registers it, stores the line number, and enables UART interrupts. Unregister disables UART interrupts and unregisters the 8250 line if one was registered.

## State and Persistence
The only driver state is `sp->serial_line`. Hardware UART ownership and interrupt mask state persist in device registers while enabled.

## Dependencies and Integration Points
The file is compiled only with `CONFIG_SERIAL_8250`. It depends on serial core/8250 APIs and low-level interrupt helpers, and is called by module probe/remove.

## Risks and Edge Cases
The scratch-register ownership heuristic is hardware-specific. UART shares the service processor IRQ, so interrupt masking must coexist with SP message interrupts. Failure to register leaves interrupts disabled because enabling happens only after success.

## Test Signals
Build with and without 8250, test scratch zero and nonzero cases, successful serial registration, failed registration, IRQ sharing with service-processor interrupts, and remove after no registration.
