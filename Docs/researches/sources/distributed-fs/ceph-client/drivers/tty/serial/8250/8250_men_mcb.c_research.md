## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_men_mcb.c

Purpose: MCB bus driver for MEN Z025/Z057/Z125 8250 UART IP cores. It discovers how many UART channels are implemented and registers each channel with serial8250.

Important APIs, types, and functions: `struct serial_8250_men_mcb_data` stores port count, line numbers, and per-port offsets. `men_lookup_uartclk()` derives a board-specific clock from the MCB bus name. `read_uarts_available_from_register()` maps the global availability register at offset `0x40`. `read_serial_data()` decodes the upper nibble into channel offsets. `init_serial_data()` handles single-port Z125 versus multiport Z025/Z057. `serial_8250_men_mcb_probe()` loops over discovered offsets and registers each port.

Control flow: probe obtains the MCB memory resource, initializes serial metadata, stores driver data, and for each channel fills a `uart_8250_port` with I/O remap, shared IRQ, board-derived clock, and mapbase offset. Remove iterates stored lines and unregisters them.

State and persistence: line numbers and offsets are stored in devm data. Availability is read from hardware at probe time; no persistent software state is written.

Dependencies and integration points: MCB bus resource/IRQ APIs, MMIO mapping, serial8250, and board-name conventions for clock selection.

Risks: `read_serial_data()` switches on `(uarts_available & mask)` but the case constants are absolute masks for UART1-4; the default branch returns `-EINVAL` for absent ports, so sparse or zero bits can abort discovery. Clock derivation from string prefixes is fragile. Test signals: Z125 single-port, Z025/Z057 with 1-4 populated UARTs, sparse availability patterns, each known board name clock, IRQ sharing, and remove cleanup after partial registration failures.
