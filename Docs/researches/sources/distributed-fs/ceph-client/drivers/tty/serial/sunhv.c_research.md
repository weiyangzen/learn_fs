# sources/distributed-fs/ceph-client/drivers/tty/serial/sunhv.c

## Purpose
This driver exposes the SUN4V hypervisor console as a Linux UART named `ttyHV`. It uses SPARC hypervisor console calls instead of memory-mapped UART registers and provides both tty and console support.

## Important APIs, Types, And Functions
The driver switches between `bychar_ops` (`sun4v_con_putchar/getchar`) and `bywrite_ops` (`sun4v_con_write/read`) depending on hypervisor API support detected in `hv_probe()`. `sunhv_pops` implements `uart_ops` for serial core. `sunhv_console` is the console object. `sunhv_migrate_hvcons_irq()` exports IRQ affinity migration for CPU migration paths.

RX helpers handle hypervisor break and hangup values: `receive_chars_getchar()` and `receive_chars_read()` feed tty flip buffers, sysrq, DCD changes, and `sun_do_break()`. TX helpers drain the uart xmit FIFO by byte or page. Console write uses either per-character CRLF expansion or a page buffer filled by `fill_con_write_page()`.

## Control Flow
`sunhv_init()` only registers on hypervisor systems. `hv_probe()` validates IRQ availability, allocates a `uart_port`, optionally allocates one-page read/write buffers when the newer HV API is available, registers minors through `suncore`, matches the firmware console, adds the uart port, requests the IRQ, and stores driver data. Interrupts lock the port, receive pending console input, transmit pending tty bytes, then push flip buffers.

## State And Persistence
Global state includes `sunhv_port`, optional `con_write_page`/`con_read_page`, selected `sunhv_ops`, and `hung_up`. The allocated `uart_port` stores serial-core counters and masks. No state is persisted beyond driver lifetime.

## Dependencies And Integration Points
The driver depends on SPARC hypervisor APIs, IRQ/PROM/platform-device data, serial core, console core, sysrq, tty flip buffers, and `sunserial_register_minors()`/`sunserial_console_match()`. OF matching accepts `qcn` and `SUNW,sun4v-console` console nodes.

## Risks
The page-mode path depends on physically contiguous pages and correct `__pa()` usage. Console write loops can spin up to large retry limits if HV calls do not accept data. Hangup handling is global and single-port. `ignore_status_mask` is configured but receive paths largely rely on hypervisor status handling, so termios semantics are narrower than a hardware UART.

## Test Signals
Test on SUN4V guests with old and new HV console APIs, console output during oops/sysrq, tty read/write, break handling, hangup/DCD transition, IRQ migration, remove cleanup, and no-probe behavior on non-hypervisor systems.
