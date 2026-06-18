# sources/distributed-fs/ceph-client/drivers/w1/masters/w1-uart.c

## Purpose
UART-backed 1-Wire master driver using serdev. It synthesizes reset, write, and read timing by sending carefully chosen UART bytes at configured baud rates.

## Important APIs, Types, and Functions
`struct w1_uart_config` stores actual baud rate, extra delay, and transmit byte. `struct w1_uart_device` embeds `struct w1_bus_master`, serdev pointer, receive completion, receive mutex, and RX result fields. `w1_uart_set_config()` derives a transmit byte from timing limits and the actual baud rate returned by serdev. `w1_uart_serdev_tx_rx()` performs a single byte transmit and waits for one-byte receive. W1 callbacks are `w1_uart_reset_bus()` and `w1_uart_touch_bit()`.

## Control Flow
Probe allocates `w1_uart_device`, initializes completion/mutex, attaches serdev ops, opens the device, validates reset/write-0/write-1 timing configurations, disables flow control, and registers a W1 master. Reset uses 9600 bps by default; touch cycles use 115200 bps by default. Presence or read-zero is detected when the received byte differs from the transmitted byte. The receive callback stores a single byte or an error if serdev delivered an unexpected count, completes the waiter, and returns consumed bytes.

## State and Persistence
State is volatile: derived timing configs, one receive byte/error pair, and completion state. Device tree properties `reset-bps`, `write-0-bps`, and `write-1-bps` tune runtime configuration but no persistent data is written.

## Dependencies and Integration Points
Depends on serdev, OF compatible `w1-uart`, completion/mutex primitives, and the W1 core. It supplies `reset_bus` and `touch_bit`, which lets the W1 core use higher-level read/write/search helpers without bit-banging GPIO.

## Risks and Test Signals
Baud-rate rounding can invalidate 1-Wire timing; `w1_uart_set_config()` rejects out-of-range timing but hardware-specific UART behavior still matters. RX locking uses `mutex_trylock()` after completion, so unexpected asynchronous receive can force `-EIO`. Test by probing with configured baud overrides, confirming slave search, observing reset presence behavior, testing timeouts, and validating read/write cycles against known devices.
