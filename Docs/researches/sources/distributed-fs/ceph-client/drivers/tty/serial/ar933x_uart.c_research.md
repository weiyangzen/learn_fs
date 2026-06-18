# sources/distributed-fs/ceph-client/drivers/tty/serial/ar933x_uart.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/ar933x_uart.c` is the platform serial driver for the Atheros/Qualcomm AR933x SoC UART. It exposes `ttyATH` ports, programs the AR933x fractional clock/step baud generator, supports GPIO-backed modem control, optional RS485 half-duplex RTS handling, console output, and console polling. The source was read as a complete 940-line file.

## Important APIs, Types, and Functions

`struct ar933x_uart_port` wraps `uart_port` with an interrupt-enable shadow `ier`, min/max baud limits, a UART clock, modem-control GPIOs, and an RTS GPIO descriptor. Register helpers are `ar933x_uart_read()`, `ar933x_uart_write()`, and read-modify-write variants. Serial-core ops are in `ar933x_uart_ops`, including TX/RX start/stop, termios, break, poll, and config/verify functions. Data movement is in `ar933x_uart_rx_chars()`, `ar933x_uart_tx_chars()`, and `ar933x_uart_interrupt()`. Probe/remove and module registration are in `ar933x_uart_probe()`, `ar933x_uart_remove()`, `ar933x_uart_init()`, and `ar933x_uart_exit()`.

## Control Flow

Probe obtains the line number from the OF `serial` alias or platform ID, validates it against `CONFIG_SERIAL_AR933X_NR_UARTS`, gets the IRQ, allocates the wrapper, gets/enables the `uart` clock, maps MMIO, fills `uart_port`, computes supported baud limits from hardware scale/step extremes, reads RS485 mode from firmware, initializes modem GPIOs, disables RS485 if no RTS GPIO exists, registers the console port pointer when configured, and adds the UART port.

Termios forces CS8 and one stop bit, supports none/even/odd parity only, clears mark/space parity, searches scale/step values for the closest baud, disables the interface while programming clock and parity, updates timeout and CREAD masking, enables host interrupts and ready overrides, then re-enables DCE mode. Startup requests the IRQ, enables host interrupt and ready override bits, and enables RX interrupts. IRQ handling first checks the host-interrupt latch, then locks the port, masks interrupt status by the shadow enable register, clears RX/TX interrupt bits, drains RX, and services TX; `uart_unlock_and_check_sysrq()` handles deferred sysrq.

RX drains up to 256 valid chars by reading `DATA_REG`, acknowledging each RX character by writing `RX_CSR`, and inserting normal chars unless CREAD masking is active. TX handles x_char and FIFO data while `DATA_TX_CSR` says space is available. When RS485 is enabled and data exists, it disables RX interrupts, drives RTS to the configured send polarity, transmits, waits for TX complete, flushes RX, reenables RX interrupts, and drives RTS to the after-send polarity.

## State and Persistence Behavior

State lives in the allocated port wrapper, shadow `ier`, clock enable state, GPIO descriptors, RS485 config in `uart_port.rs485`, and hardware registers. There is no file persistence. Console state is stored in a static array indexed by line and is populated at probe time. Remove unregisters the port and disables the clock.

## Dependencies and Integration Points

The driver depends on platform/OF APIs, clock APIs, serial core, TTY flip buffers, sysrq, GPIO modem-control helpers from `serial_mctrl_gpio.h`, AR933x register definitions from `<asm/mach-ath79/ar933x_uart.h>`, and optional console/poll configuration. It matches `qca,ar9330-uart`.

## Risks and Edge Cases

The baud search is brute force over scale values and depends on valid clock rate. TX-complete waits use fixed 60 ms polling timeouts, so wedged hardware can delay interrupt/console paths. RS485 depends on an RTS GPIO; firmware enabling RS485 without one is corrected by probe. RX has no parity/frame error classification in this driver. Console write disables interrupts and must restore interrupt enable state even during oops trylock paths.

## Test Signals

Relevant tests include OF alias numbering, clock failure and zero-rate handling, baud accuracy across min/max limits, RX/TX interrupt loopback, CREAD suppression, RS485 RTS polarity and RX flush behavior, modem GPIO get/set, console output under normal and oops paths, poll get/put, and removal clock balancing.
