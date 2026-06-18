# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_uniphier.c

## Purpose
Adapts Socionext UniPhier UART hardware to the 8250 core. The hardware is 8250-like but uses 32-bit MMIO, shared register words for CHAR/FCR and LCR/MCR, no SCR, and a divisor latch at a fixed offset without DLAB.

## Important APIs, Types, And Functions
`struct uniphier8250_priv` stores the registered line, clock, and `atomic_write_lock` used for read-modify-write access to shared 32-bit register words. `uniphier_serial_in()` and `uniphier_serial_out()` remap standard UART offsets and mask/shift byte lanes. `uniphier_serial_dl_read()` and `uniphier_serial_dl_write()` access `UNIPHIER_UART_DLR`. `uniphier_uart_probe()` maps MMIO, enables the clock, initializes the customized `uart_8250_port`, and registers it. Early console setup configures the port as MMIO32 and sets `device->baud = 0` to avoid touching the divisor.

## Control Flow
Probe gets the MMIO resource, maps it, allocates private state, gets/enables the clock, stores `uartclk`, initializes the shared-write spinlock, fills the port with mapbase/membase/mapsize and firmware properties, sets fixed `PORT_16550A`, `UPIO_MEM32`, `fifosize = 64`, `regshift = 2`, `UART_CAP_FIFO`, optional `UART_CAP_AFE` from `auto-flow-control`, custom serial and divisor callbacks, then calls `serial8250_register_8250_port()`. Remove unregisters and disables the clock. System suspend/resume delegates to 8250 and gates the clock unless the active console must remain powered.

## State And Persistence
Private state is per device and exists for the platform driver's lifetime. The lock protects non-atomic shared-register updates against concurrent console/interrupt accesses. Hardware register contents are volatile and reprogrammed by the 8250 core; no persistent storage is used.

## Dependencies And Integration Points
Depends on OF compatible `socionext,uniphier-uart`, common clocks, 8250 registration, firmware port property parsing, and earlycon. It integrates by overriding accessors while leaving most line discipline, interrupts, termios, console, and PM behavior to `8250_port.c`.

## Risks And Test Signals
The custom accessor path is sensitive to byte-lane shifts and shared-register read-modify-write races. Probe has an error path after `clk_prepare_enable()` where a failing `uart_read_port_properties()` returns without disabling the clock. Test signals include early console without divisor writes, normal console/tty operation, LCR/MCR/FCR/SCR behavior, hardware flow control from `auto-flow-control`, suspend/resume clock balance, and lockdep coverage under console plus interrupt traffic.
