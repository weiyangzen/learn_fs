# sources/distributed-fs/ceph-client/arch/x86/boot/early_serial_console.c

Purpose: initializes early serial output for setup and compressed boot messages from `earlyprintk=` or `console=uart8250,io,...`.

Important APIs and state: exports `console_init()`. Helpers parse command-line options, probe an existing UART divisor, and program 8250-compatible UART registers. It writes global `early_serial_base` used by `tty.c`.

Control flow: `console_init()` first parses `earlyprintk`; if no serial base was established, it parses the last `console` option for `uart8250,io` or `uart,io`. `early_serial_init()` configures 8n1, disables interrupts/FIFO, asserts DTR/RTS, sets baud divisor, and stores the base port.

Dependencies and integration: depends on boot command-line parsing, `simple_strtoull()`, and port I/O callbacks, which TDX can override. `tty.c` mirrors output to this serial base.

Risks and test signals: malformed baud or port options fall back to defaults; `probe_baud()` can divide by zero if a UART reports a zero divisor. Test with `earlyprintk=serial,ttyS0,115200`, explicit hex ports, `console=uart8250,io,...`, and TDX port-I/O virtualization.
