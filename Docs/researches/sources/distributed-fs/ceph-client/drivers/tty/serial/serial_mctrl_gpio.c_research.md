# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_mctrl_gpio.c

## Purpose
Reusable helper implementation for UART modem-control lines backed by GPIO descriptors. It lets low-level serial drivers set RTS/DTR, read CTS/DSR/DCD/RI, and receive GPIO IRQ notifications as serial-core modem-status changes.

## Important APIs, Types, And Functions
`struct mctrl_gpios` stores the owning `uart_port`, GPIO descriptors, IRQ numbers, previous modem-control state, and enable flag. Exported functions include `mctrl_gpio_set()`, `mctrl_gpio_get()`, `mctrl_gpio_get_outputs()`, `mctrl_gpio_to_gpiod()`, `mctrl_gpio_init_noauto()`, `mctrl_gpio_init()`, enable/disable modem-status IRQ helpers, and IRQ wake helpers. `mctrl_gpio_irq_handle()` maps GPIO edge changes to UART icount updates and `uart_handle_dcd_change()`/`uart_handle_cts_change()`.

## Control Flow
Initialization scans device properties named `cts-gpios`, `dsr-gpios`, `dcd-gpios`, `rng-gpios`, `rts-gpios`, and `dtr-gpios`. Input GPIOs are converted to IRQs with `IRQ_NOAUTOEN` and requested edge-both. `.enable_ms` calls `mctrl_gpio_enable_ms()`, snapshots current input state, and enables IRQs. IRQs update cached state under the UART port lock and wake `delta_msr_wait`.

## State And Persistence
State is devm-allocated and lasts for the device lifetime. Output GPIO states are hardware state; input cached state is `mctrl_prev`. There is no durable persistence.

## Dependencies And Integration Points
Depends on GPIOLIB, device properties, IRQ APIs, termios modem-control constants, and serial-core modem helpers. The paired header provides no-op stubs when `CONFIG_GPIOLIB` is disabled.

## Risks
Drivers must not also handle the same GPIO input line changes or duplicate events may occur. IRQ enable/disable tracks `mctrl_on`; imbalance would leave modem interrupts disabled or enabled unexpectedly. `gpiod_get_value()` assumes appropriate sleep context for these calls.

## Test Signals
Use GPIO-backed CTS/DCD/DSR/RI lines with edge injection, verify `TIOCMGET` state, test RTS/DTR output changes, enable/disable modem status repeatedly, suspend wake enable/disable paths, and build with GPIOLIB disabled to verify stubs.
