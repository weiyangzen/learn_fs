# sources/distributed-fs/ceph-client/drivers/tty/serial/mcf.c

## Purpose

`mcf.c` is the Freescale ColdFire internal UART serial driver. It registers platform-provided UARTs with serial core, handles classic ColdFire UART registers, supports console output, and exposes basic RS-485 automatic RTS behavior.

## Important APIs, Types, and Functions

`struct mcf_uart` wraps `uart_port` with a local modem-signal cache and interrupt-mask mirror. `mcf_uart_ops` provides serial-core callbacks. Key functions include `mcf_startup()`, `mcf_shutdown()`, `mcf_set_termios()`, `mcf_rx_chars()`, `mcf_tx_chars()`, `mcf_interrupt()`, `mcf_config_port()`, `mcf_config_rs485()`, `mcf_probe()`, and console helpers.

## Control Flow

Platform probe iterates platform data entries, initializes static `mcf_ports`, assigns MMIO/IRQ/clock/ops/RS485 hooks, and adds each port. `mcf_config_port()` sets type/FIFO size, masks interrupts, and requests the IRQ. Startup resets RX/TX, enables both directions, and enables RX-ready interrupts. TX start enables transmitter/RTS for RS-485 and sets TX-ready interrupt. IRQ handling reads masked status and dispatches RX/TX under the port lock. RX drains ready bytes, resets error status, updates counters, handles break/sysrq, and pushes flip data. TX uses `uart_port_tx()` and disables TX after completion in RS-485 mode to negate RTS automatically.

## State and Persistence Behavior

Static `mcf_ports[10]` persists all port objects. `pp->imr` mirrors the hardware interrupt mask and `pp->sigs` mirrors modem outputs. Board-specific DTR/DCD macros can persist external GPIO state. There is no runtime PM or register cache beyond serial-core termios reprogramming.

## Dependencies and Integration Points

The driver depends on ColdFire architecture headers (`asm/coldfire.h`, `asm/mcfsim.h`, `asm/mcfuart.h`, `asm/nettel.h`), platform data `struct mcf_platform_uart`, serial core, console core, and optional board GPIO macros for DTR/DCD.

## Risks and Edge Cases

A FIXME notes `read_status_mask` and `ignore_status_mask` are not initialized from termios, so RX error filtering may be incomplete. IRQs are requested in `config_port()` and never freed in `release_port()`, which is normal for fixed internal UARTs but limits reprobe assumptions. `mcf_remove()` tests `if (port)` on addresses of static array elements, so it attempts removal for all slots. Console output busy-waits with fixed loop counts.

## Test Signals

Platform data with multiple UARTs, RX parity/frame/break/overrun counters, RS-485 RTS behavior, termios character/parity/baud modes including M5272 fractional divider, console output, DTR/DCD board macro behavior, and repeated platform remove/probe if supported.
