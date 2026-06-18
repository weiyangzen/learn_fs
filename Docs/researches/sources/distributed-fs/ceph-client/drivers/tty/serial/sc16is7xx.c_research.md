# sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx.c

## Purpose
Core tty/serial implementation for NXP SC16IS7xx UART expanders. It is bus-neutral: SPI and I2C wrappers provide per-port regmaps and call `sc16is7xx_probe()`, while this file registers `ttySC*` UART ports, handles interrupts or polling, GPIO side functions, IrDA selection, hardware modem lines, RS-485 support, and clock/reset/power sequencing.

## Important APIs, Types, And Functions
Key state is split between `struct sc16is7xx_port` for chip-wide resources and `struct sc16is7xx_one` for each UART. `sc16is7xx_one` owns `struct uart_port`, a regmap, register mutex, kthread work items, cached modem state, RX buffer, pending config bits, and IrDA mode. `struct sc16is7xx_devtype` instances describe variant name, GPIO count, and UART count.

Exported APIs are `sc16is7xx_probe()`, `sc16is7xx_remove()`, `sc16is7xx_regcfg`, `sc16is7xx_dt_ids`, devtype symbols, `sc16is7xx_regmap_name()`, and `sc16is7xx_regmap_port_mask()`. UART operations are collected in `sc16is7xx_ops`: TX/RX control, modem control, termios, startup/shutdown, RS-485 config, break, PM, and port verification.

## Control Flow
Module init registers `sc16is7xx_uart`; bus wrappers later call `sc16is7xx_probe()`. Probe validates regmaps by reading LSR, obtains clock or `clock-frequency`, starts a FIFO-priority kthread worker, resets the chip, allocates line IDs, configures each channel with `uart_add_one_port()`, optionally configures IrDA, modem-control GPIO muxing, and gpiochip export, then installs a threaded IRQ. If no IRQ exists, delayed kthread polling repeatedly invokes the same interrupt service path.

The IRQ path loops over all UARTs and calls `sc16is7xx_port_irq()`. It reads IIR under the per-port register mutex, dispatches RX sources to FIFO reads and `uart_insert_char()`, TX empty to `sc16is7xx_handle_tx()`, modem sources to cached mctrl updates and serial-core notifications, and logs unexpected IDs with rate limiting. TX is deferred through `tx_work`; register changes that require sleeping regmap access are coalesced through `reg_work`.

## State And Persistence
Runtime state is in driver-private memory and hardware registers. There is no durable persistence. Line allocation uses a module-global IDA. Cached state includes `old_mctrl`, `old_lcr`, pending IER/MCR/RS485 config, and optional gpio valid masks. Regmap cache uses `REGCACHE_MAPLE`; volatile, precious, and no-increment callbacks protect FIFO and status registers.

## Dependencies And Integration Points
Depends on Linux serial core, tty flip buffers, regmap, clk, GPIO/descriptor APIs, kthread worker APIs, IRQ handling, device properties, and optional GPIOLIB. Device tree properties include `clock-frequency`, `irda-mode-ports`, `nxp,modem-control-line-ports`, reset GPIO, and RS-485 properties consumed by serial core.

## Risks
The chip has overlapping register banks selected by magic LCR values; the mutex and regcache bypass are critical because interrupts can otherwise read EFR as IIR. Polling mode can hide IRQ wiring problems and adds latency. FIFO level sanity checks handle bad TXLVL/RXLVL readings but indicate possible hardware or regmap issues. Cleanup paths must free IDA lines only after registration state is known. RS-485 only supports hardware RTS timing plus optional pre-send delay; post-send delay is rejected.

## Test Signals
Useful signals include successful `ttySC*` registration, IRQ or polling RX/TX loopback, termios changes across baud/parity/word/stop settings, CTS/DCD change propagation, RS-485 ioctl behavior including rejected post-send delay, gpiochip visibility for 75x/76x variants, reset GPIO and software-reset coverage, suspend power bit behavior, and stress tests around enhanced-register access while interrupts fire.
