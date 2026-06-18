# sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.h` is the local register contract for the GRLIB APBUART serial driver. It defines the memory layout, firmware register property shape, status/control bits, and raw MMIO accessor macros used by `apbuart.c`. The source was read as a complete 65-line file.

## Important APIs, Types, and Functions

The header defines `UART_NR` as eight ports and declares the file-scope `grlib_apbuart_port_nr`. `struct grlib_apbuart_regs_map` models the four 32-bit APBUART registers: `data`, `status`, `ctrl`, and `scaler`. `struct amba_prom_registers` models the OF `reg` payload consumed by the driver. Macros define status flags (`UART_STATUS_DR`, `THE`, `BR`, `OE`, `PE`, `FE`, and `ERR`) and control flags (`RE`, `TE`, `RI`, `TI`, parity, flow control, loopback). Accessors such as `UART_GET_CHAR()`, `UART_PUT_CTRL()`, and `UART_PUT_SCAL()` use `__raw_readl()`/`__raw_writel()`.

## Control Flow

There is no executable control flow in the header. It shapes the driver's control flow by providing predicates `UART_RX_DATA()` and `UART_TX_READY()` and by mapping a `uart_port`'s `membase` into typed APBUART register pointers.

## State and Persistence Behavior

The header itself owns no runtime state except the unusual `static int grlib_apbuart_port_nr` definition, which becomes a private variable in each translation unit that includes it. In this tree it is included by `apbuart.c`, so it backs the driver's discovered port count for the module lifetime. Hardware state is represented by status/control/scaler registers only.

## Dependencies and Integration Points

It includes `<asm/io.h>` and assumes Linux integer types are available. It is tightly coupled to `apbuart.c`; moving it to a shared include context would require care because of the `static` variable definition.

## Risks and Edge Cases

The raw accessors impose no endian conversion or barriers beyond raw MMIO semantics. Incorrect struct layout would make every register access wrong. The APBBASE macros depend on `membase` being valid and mapped to at least `sizeof(struct grlib_apbuart_regs_map)`. The header-level `static int` is safe for single-user inclusion but would be surprising if included by multiple C files.

## Test Signals

Build coverage of `apbuart.c`, register read/write smoke tests on APBUART hardware, status/control bit toggling, scaler programming, and sparse/compile checks around the header's static variable are the relevant signals.
