# sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon-semihost.c

Purpose: semihosting-backed early console provider named `smh`, routing early printk output through architecture semihosting calls.

Important APIs/types/functions: `smh_write()` obtains `earlycon_device` from `console->data` and writes through `uart_console_write()` using `smh_putc`. `early_smh_setup()` installs the write callback. Registered by `EARLYCON_DECLARE(smh, early_smh_setup)`.

Control flow: generic earlycon calls setup after matching `smh`; setup assigns the write method. Subsequent early console writes are emitted one character at a time via semihosting.

State/persistence: no driver-private state beyond the generic earlycon device pointer.

Dependencies/integration: `asm/semihost.h`, generic console support, and earlycon registration.

Risks: semihosting may be slow or unavailable depending on monitor/debugger setup. No availability probe is performed here. Character output can be expensive for large logs.

Test signals: boot with `earlycon=smh` under semihosting, verify CR/LF handling via `uart_console_write()`, and confirm target behavior without semihosting.
