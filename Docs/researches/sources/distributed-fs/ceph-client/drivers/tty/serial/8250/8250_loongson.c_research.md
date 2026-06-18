## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_loongson.c

Purpose: OF platform driver for Loongson UARTs with optional fractional divisor support and inverted modem-control/status pins. It registers one fixed 16550A-style port with serial8250.

Important APIs, types, and functions: `struct loongson_uart_ddata` describes fractional divisor availability and MCR/MSR inversion masks. `struct loongson_uart_priv` stores line, clock, resource, reset control, and match data. `loongson_serial_in/out()` apply `serial_fixup()` around MMIO access. `loongson_frac_get_divisor()`/`set_divisor()` use `LOONGSON_UART_DLF` for an 8-bit fractional part. `loongson_uart_probe()` maps resources, reads properties/clock, deasserts reset, registers the port, and stores private state. PM callbacks suspend/resume the serial8250 line and clock around console rules.

Control flow: probe selects match data, installs accessors, optionally installs fractional divisor callbacks, reads UART properties, obtains a clock only if no `clock-frequency` was provided, deasserts reset, then registers. Remove unregisters and reasserts reset. Suspend/resume disable clocks unless the port is an active console with console suspend disabled.

State and persistence: runtime state is `line`, optional enabled clock, and reset deassertion. Hardware state includes DLF fractional divisor and inverted pin semantics. No persistent storage.

Dependencies and integration points: OF matching, reset framework, clock framework, serial8250, PM core, and console handling.

Risks: `loongson_serial_out()` shifts `offset` before passing it to `serial_fixup()`, so MCR writes may not match the unshifted `UART_MCR` case if `regshift` changes from zero in future; currently probe sets `regshift=0`. Clock pointer may remain NULL if `uartclk` came from properties, so suspend/resume clock handling relies on console branch not dereferencing an invalid clock path. Test signals: fractional baud accuracy on `ls2k1500`, inverted RTS/DTR/CTS/DSR behavior, reset assertion on remove, suspend/resume with and without console, and property-provided clock versus clock-provider path.
