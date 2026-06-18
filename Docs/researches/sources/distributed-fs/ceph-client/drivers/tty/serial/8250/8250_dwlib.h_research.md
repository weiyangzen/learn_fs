# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_dwlib.h

## Purpose
Declares the shared DesignWare 8250 port-data structure, exported helper prototypes, and endian-aware extended-register read/write helpers.

## Important APIs, types, and functions
- `struct dw8250_port_data` stores registered line, embedded `uart_8250_dma`, CPR override, DLF size, and hardware RS485 support flag.
- Prototypes: `dw8250_do_set_termios()` and `dw8250_setup_port()`.
- Inline helpers: `dw8250_readl_ext()` and `dw8250_writel_ext()` use big-endian accessors when `p->iotype == UPIO_MEM32BE`, otherwise little-endian `readl`/`writel`.

## Control flow
The main DesignWare driver embeds `dw8250_port_data` in its private data and passes it as `uart_port.private_data`. Extended register helpers are used by both the main driver and library to access non-8250 DesignWare registers.

## State and persistence behavior
The header defines state shape only. Runtime state is maintained by `8250_dw.c` and `8250_dwlib.c`.

## Dependencies and integration points
Depends on `linux/io.h`, `linux/types.h`, and internal `8250.h`. It is the private interface between DesignWare 8250 modules.

## Risks and edge cases
The extended register helpers assume extended registers are 32-bit and aligned at raw offsets, not shifted 8250 offsets. Incorrect `iotype` causes endian-swapped access.

## Test signals
Build coverage for little-endian and big-endian DesignWare ports, and runtime validation that extended register values read consistently with the selected iotype.
