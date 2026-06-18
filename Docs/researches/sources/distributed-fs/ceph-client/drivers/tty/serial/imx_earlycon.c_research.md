# sources/distributed-fs/ceph-client/drivers/tty/serial/imx_earlycon.c

## Purpose
`imx_earlycon.c` provides the minimal early console writer for i.MX21/i.MX6Q-compatible UARTs before the full `imx.c` serial driver is available. It lets early boot messages be emitted through Device Tree earlycon matching.

## Important APIs, types, and functions
`imx_uart_console_early_putchar()` busy-waits until `IMX21_UTS` no longer reports `UTS_TXFULL`, then writes one byte to `URTX0` with relaxed MMIO. `imx_uart_console_early_write()` delegates string output to `uart_console_write()`. `imx_console_early_setup()` validates `dev->port.membase` and installs the write callback. `OF_EARLYCON_DECLARE()` registers `fsl,imx6q-uart` and `fsl,imx21-uart`.

## Control flow
The earlycon framework matches a compatible string, builds an `earlycon_device`, and calls setup. Setup rejects missing MMIO and otherwise sets `dev->con->write`. Early console writes then flow through `uart_console_write()` to the polling putchar helper.

## State and persistence behavior
The file keeps no private persistent state. It uses only the earlycon-supplied `uart_port` and direct MMIO register state. It does not program baud, clocks, FIFO levels, or line control, so it assumes firmware or earlier boot code left the UART usable.

## Dependencies and integration points
Dependencies are early console infrastructure, serial core console helpers, Device Tree earlycon matching, and relaxed MMIO access. It integrates with the full i.MX UART driver by sharing compatible strings and register offsets for i.MX21-style controllers.

## Risks and test signals
Risks include unsupported i.MX1 UTS offset, an infinite polling loop if TX-full never clears, and lack of clock/register setup. Test boot-time `earlycon` on `fsl,imx6q-uart` and `fsl,imx21-uart`, missing `membase` failure, and continuity when the normal `ttymxc` console takes over.
