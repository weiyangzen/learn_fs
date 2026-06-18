# sources/distributed-fs/ceph-client/drivers/tty/serial/max310x.c

## Purpose

`max310x.c` is a regmap-based SPI/I2C UART driver for MAX3107, MAX3108, MAX3109, and MAX14830 chips. It supports one to four UART ports per chip, FIFO batch I/O, threaded IRQ dispatch, clock/PLL setup, RS-485 mode, optional GPIO controller registration, and PM suspend/resume.

## Important APIs, Types, and Functions

Important types are `struct max310x_devtype`, `struct max310x_if_cfg`, `struct max310x_one`, and `struct max310x_port`. `max310x_ops` provides serial-core callbacks; `max310x_uart` is the shared `uart_driver`. Core functions include `max310x_detect()`, `max310x_set_ref_clk()`, `max310x_set_baud()`, `max310x_handle_rx()`, `max310x_handle_tx()`, `max310x_port_irq()`, `max310x_ist()`, `max310x_set_termios()`, `max310x_rs485_config()`, `max310x_probe()`, bus-specific SPI/I2C probe functions, and GPIO callbacks under `CONFIG_GPIOLIB`.

## Control Flow

Module init registers the UART driver, then SPI and/or I2C bus drivers. Bus probe creates per-port regmaps and calls common `max310x_probe()`. Common probe validates clocks, detects the chip by revision/default register, resets each port, waits for startup, programs mode registers, configures reference clock/PLL, allocates global line numbers, initializes serial-core ports and work items, registers each UART, powers ports down, optionally registers GPIOs, and requests a threaded IRQ. IRQ service dispatches global per-port IRQ state, handles CTS changes, drains RX FIFO, and schedules TX work on TX-empty. Termios writes LCR, status masks, hardware/software flow control, XON/XOFF chars, baud generator, and timeout.

## State and Persistence Behavior

Global line allocation uses `max310x_lines`. Per-chip state includes devtype, interface config, root regmap, clock, optional gpio chip, and flexible-array per-port state. Per-port state includes regmap, RX buffer, TX/modem/RS485 work items, serial-core state, and RS-485 configuration. Suspend iterates ports through `uart_suspend_port()` and powers them off; resume powers them on and calls `uart_resume_port()`.

## Dependencies and Integration Points

The file integrates with serial core, regmap, SPI, I2C, common clock framework, GPIO library, device properties, OF and bus ID tables, threaded IRQs, workqueues, and Linux RS-485 serial APIs. It uses noinc regmap operations for FIFO batch transfers.

## Risks and Edge Cases

The `max310x_uart_init()` error label for I2C failure unconditionally references the SPI unregister path, so build configurations with I2C but without SPI need scrutiny. Probe must unwind partially registered multiport chips correctly; line bits are set only after successful add. Regmap cache volatility/precious settings are critical for FIFO/status correctness. Clock detection chooses `xtal` based on absence of `clock-names = "osc"`, which is subtle. Batch RX optimization ignores detailed errors unless masks request them.

## Test Signals

SPI and I2C probe for all devtypes, multiport global IRQ dispatch, revision mismatch, PLL/clock stability failures, FIFO batch RX/TX at boundaries, hardware and software flow control, RS-485 delay validation, GPIO direction/get/set/config, suspend/resume across active ports, and module init error paths for SPI-only/I2C-only builds.
