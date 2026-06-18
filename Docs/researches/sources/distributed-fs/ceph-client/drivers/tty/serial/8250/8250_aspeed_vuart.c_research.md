# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_aspeed_vuart.c

## Purpose
Implements the BMC-side Aspeed virtual UART, an 8250-like device that exposes a host LPC UART endpoint and lets BMC userspace configure host I/O address, SIRQ, and polarity.

## Important APIs, types, and functions
- `struct aspeed_vuart` stores device, 8250 line, unthrottle timer, and registered 8250 port pointer.
- Sysfs attributes: `lpc_address`, `sirq`, and `sirq_polarity`.
- Hardware control helpers: `aspeed_vuart_set_lpc_address()`, `aspeed_vuart_set_sirq()`, `aspeed_vuart_set_sirq_polarity()`, `aspeed_vuart_set_enabled()`, and `aspeed_vuart_set_host_tx_discard()`.
- UART callbacks: `aspeed_vuart_startup()`, `aspeed_vuart_shutdown()`, `aspeed_vuart_throttle()`, `aspeed_vuart_unthrottle()`, and custom `aspeed_vuart_handle_irq()`.
- Probe/remove: `aspeed_vuart_probe()` and `aspeed_vuart_remove()` with OF matches for AST2400/AST2500 VUART.

## Control flow
Probe allocates private data, creates sysfs controls, reads port properties and clock, sets optional current-speed divisor, installs custom startup/shutdown/throttle/IRQ callbacks, registers an 8250 port of type `PORT_ASPEED_VUART`, then configures optional SIRQ polarity sensing, LPC I/O address, SIRQ number/polarity, enables the VUART, and initially discards host TX until the tty is opened.

The IRQ handler reads IIR/LSR, checks flip-buffer space before draining RX, and if there is no space disables receive-related IER bits and arms a timer to retry unthrottle after `HZ/10`. If space exists, it reads up to the available space or 256 chars, pushes the flip buffer, services modem status, and sends TX chars when THRE is set. Startup enables host TX delivery after normal 8250 startup; shutdown discards host TX before normal shutdown.

## State and persistence behavior
Runtime state includes sysfs-programmed LPC address/SIRQ registers, enabled bit, host TX discard bit, receive interrupt throttle state in IER, and a retry timer. These hardware settings persist while the device is bound but are not stored across reboot.

## Dependencies and integration points
Depends on platform/OF resources, optional clocks, syscon/regmap for polarity auto-sensing, tty flip-buffer availability, and serial8250 registration/core IRQ helpers. It exposes policy knobs to BMC userspace through sysfs.

## Risks and edge cases
- Sysfs attributes directly mutate host-visible LPC/SIRQ registers; invalid policy can break host console discovery.
- RX throttling depends on flip-buffer space and timer retry; bad interactions can cause dropped host bytes or stuck receive interrupts.
- Error paths after `serial8250_register_8250_port()` should unregister the port; current later configuration failures jump only to sysfs removal, so line cleanup is a point to audit.
- `UART_BUG_TXRACE` and `UPF_NO_THRE_TEST` indicate hardware quirks that should not be removed casually.

## Test signals
OF probe with/without clock-frequency, sysfs read/write validation for address/SIRQ/polarity, host-side LPC console enumeration, RX stress that fills tty buffers and verifies throttle/unthrottle recovery, startup/shutdown host TX discard behavior, and removal cleanup including timer deletion and port unregister.
