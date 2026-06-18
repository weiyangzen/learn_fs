## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ingenic.c

Purpose: OF platform driver and early console support for Ingenic JZ/X-series SoC UARTs with 8250-like registers plus SoC-specific enable, modem, timeout, and FIFO behavior.

Important APIs, types, and functions: `struct ingenic_uart_config` supplies FIFO and TX load size per compatible. `struct ingenic_uart_data` stores module/baud clocks and the registered line. `OF_EARLYCON_DECLARE()` entries install early console setup variants; JZ4750 adjusts high oscillator clocks by `/2`. `ingenic_uart_serial_out()` forces `UART_FCR_UME`, mirrors RLSI to timeout interrupt enable, and toggles modem-control extension bits. `ingenic_uart_serial_in()` hides nonstandard bits. `ingenic_uart_probe()` maps registers, enables clocks, fills a `uart_8250_port`, and registers it.

Control flow: early console reads `/ext` clock-frequency from the flat DT, programs divisor/FIFO/MCR, and replaces console write with an Ingenic polling putc. Normal probe selects match data, maps MMIO, reads port properties, enables clocks, sets serial in/out hooks and FIFO capabilities, registers with serial8250, then stores the line for remove.

State and persistence: runtime state consists of two enabled clocks and the line number. Hardware state includes UART module enable, FIFO trigger state, and modem extension bits. No suspend/resume hooks are present here.

Dependencies and integration points: relies on OF matching, clock framework, earlycon infrastructure, serial8250 registration, and standard tty/console paths.

Risks: early console clock discovery assumes an `/ext` node and can misprogram baud if DT differs. `serial_in/out` masks nonstandard bits; future core changes reading those registers must preserve this abstraction. Test signals: earlycon on every compatible, baud correctness with 12/24 MHz ext clocks, modem-status interrupt behavior, FIFO sizes per SoC, and clock disable on remove.
