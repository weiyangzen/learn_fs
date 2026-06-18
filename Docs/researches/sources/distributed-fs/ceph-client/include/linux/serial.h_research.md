# sources/distributed-fs/ceph-client/include/linux/serial.h

Purpose: `serial.h` provides common UART constants and counters layered over UAPI serial headers.

Important APIs/types/functions: It includes UAPI serial and 8250 register definitions, defines `UART_IER_ALL_INTR`, `UART_LCR_WLEN(x)`, `UART_LSR_BOTH_EMPTY`, `uart_lsr_tx_empty()`, `UART_MSR_STATUS_BITS`, and `struct async_icount` counters for modem/input line interrupts and RX/TX/error accounting.

Control flow: Serial drivers test line status with `uart_lsr_tx_empty()`, set interrupt-enable masks, derive word-length bits, and update `async_icount` as UART interrupts and errors occur.

State and persistence behavior: The header owns no state. `async_icount` is embedded in serial ports and persists as runtime statistics exposed through serial ioctls or diagnostics.

Dependencies and integration points: It integrates with UART drivers, 8250-compatible register definitions, TTY serial core, modem-control handling, and userspace serial APIs.

Risks: Register bit definitions are hardware-facing; using the wrong mask can miss interrupts or report transmit-empty too early. Counter overflow is possible on long-lived ports but uses 32-bit UAPI-compatible fields.

Test signals: TX-empty detection, interrupt mask setup, modem status counters, RX/TX/error counter increments, UAPI serial ioctl compatibility, and different UART word-length settings.
