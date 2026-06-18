# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_early.c

## Purpose
Implements early console support for 8250/16550 UARTs before full serial driver discovery, supporting I/O port and MMIO access widths plus several OF earlycon compatible strings.

## Important APIs, types, and functions
- Register access: `serial8250_early_in()` and `serial8250_early_out()`.
- Console I/O: `serial_putc()`, `early_serial8250_write()`, and optional `early_serial8250_read()` under `CONFIG_CONSOLE_POLL`.
- Setup: `init_port()`, `early_serial8250_setup()`, `early_serial8250_rs2_setup()`, and optional `early_omap8250_setup()`.
- Declarations: `EARLYCON_DECLARE()` and `OF_EARLYCON_DECLARE()` for generic uart8250/ns16550 and SoC-specific compatible strings.

## Control flow
Early setup validates that an I/O base or membase exists. If a baud is supplied, it initializes 8n1, masks interrupts, disables FIFO, asserts DTR/RTS, and programs divisor from `uartclk`. If no baud is supplied, it assumes firmware initialized the UART and only masks interrupts. It then assigns console write and optional read callbacks.

Writes send chars through `uart_console_write()` and `serial_putc()`, which writes TX then busy-waits for TX empty. Poll reads drain RX while LSR data-ready is set.

## State and persistence behavior
State is in the boot-time `earlycon_device` and hardware UART registers. It does not allocate persistent driver state. Full 8250 console later matches/replaces earlycon through core console matching.

## Dependencies and integration points
Depends on earlycon framework, serial register definitions, MMIO/PIO accessors, OF earlycon matching, and optional console polling. `early_bcm2835aux_setup()` and other platform earlycon declarations build on this generic setup.

## Risks and edge cases
- Busy-wait TX can stall boot if hardware is misdescribed or not clocked.
- Access width/iotype must match hardware; wrong width can fault or write wrong registers.
- Initialization without a baud leaves firmware divisor/format intact, which is useful but can hide bad bootloader setup.

## Test signals
Boot with `earlycon=uart8250,io`, `mmio`, `mmio32`, and OF compatible forms, handoff to `ttyS` console, poll read when enabled, no-baud firmware-initialized console, and invalid base rejection.
