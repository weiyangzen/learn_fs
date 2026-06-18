# sources/distributed-fs/ceph-client/drivers/tty/serial/bcm63xx_uart.c

Purpose: Broadcom BCM63xx integrated UART driver for up to two `ttyS` ports. It implements Linux serial-core `uart_ops`, a platform driver matched by `brcm,bcm6345-uart`, optional boot/early console support, and console-poll hooks.

Important APIs/types/functions: global `struct uart_port ports[BCM63XX_NR_UARTS]`; `bcm_uart_ops`; register helpers `bcm_uart_readl()`/`bcm_uart_writel()`; RX/TX interrupt helpers `bcm_uart_do_rx()` and `bcm_uart_do_tx()`; lifecycle callbacks `bcm_uart_startup()`, `bcm_uart_shutdown()`, `bcm_uart_set_termios()`, `bcm_uart_probe()`, `bcm_uart_remove()`; console functions `bcm_console_write()`, `bcm_console_setup()`, `bcm_early_write()`.

Control flow: module init registers the UART driver then the platform driver. Probe derives line number from DT aliases, maps MMIO, gets IRQ and clock, fills `uart_port`, and calls `uart_add_one_port()`. Startup disables and flushes the UART, configures FIFO thresholds/timeouts and modem edge reporting, requests IRQ, enables RX interrupts, and enables RX/TX/baud generation. The IRQ handler locks the port, dispatches RX, TX, and CTS/DCD changes, then unlocks with SysRq handling.

State/persistence: runtime state is the global port array, serial-core masks/counters/FIFOs, and hardware registers. `membase` marks an occupied slot. There is no disk persistence.

Dependencies/integration: platform/OF resources, common clock, serial core, TTY flip buffers, SysRq, console core, `linux/serial_bcm63xx.h`, `console_initcall()`, and `OF_EARLYCON_DECLARE`.

Risks: hardware flow control is noted as untested; `set_termios()` busy-waits for TX empty; FIFO error handling must preserve break/parity/frame semantics; console/oops locking is delicate; no runtime clock management beyond initial rate read.

Test signals: DT aliases for both ports, interrupt RX/TX, CTS/DCD changes, console and earlycon output, console-poll, baud/data/parity/stop changes, RX overrun/error injection, and remove/reprobe cleanup.
